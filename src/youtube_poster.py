"""YouTube comment posting with OAuth authentication."""

import time
from datetime import datetime
from typing import Dict, Optional, List
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from src.config import settings
from src.database import AirtableDatabase
from src.utils import setup_logger

logger = setup_logger(__name__)


class YouTubePoster:
    """Posts approved replies to YouTube comments."""

    # Safety limits
    MAX_REPLIES_PER_DAY = 20
    MIN_SECONDS_BETWEEN_REPLIES = 60  # 1 minute cooldown
    MAX_REPLY_LENGTH = 10000  # YouTube limit

    def __init__(self, database: AirtableDatabase):
        """Initialize YouTube poster."""
        self.database = database
        self.youtube = None  # Will be initialized after OAuth
        self.replies_posted_today = 0
        self.last_post_time = None

    def initialize_youtube_client(self):
        """
        Initialize YouTube API client with OAuth.

        NOTE: This requires OAuth setup which will be done separately.
        For now, this is a placeholder that uses the regular API key.
        """
        try:
            # TODO: Replace with OAuth credentials after setup
            self.youtube = build('youtube', 'v3', developerKey=settings.youtube_api_key)
            logger.info("YouTube client initialized (using API key - OAuth pending)")
            return True
        except Exception as e:
            logger.error(f"Error initializing YouTube client: {e}")
            return False

    def can_post_reply(self) -> tuple[bool, str]:
        """
        Check if we can post a reply (safety limits).

        Returns:
            Tuple of (can_post: bool, reason: str)
        """
        # Check daily limit
        if self.replies_posted_today >= self.MAX_REPLIES_PER_DAY:
            return False, f"Daily limit reached ({self.MAX_REPLIES_PER_DAY} replies)"

        # Check cooldown
        if self.last_post_time:
            seconds_since_last = (datetime.now() - self.last_post_time).total_seconds()
            if seconds_since_last < self.MIN_SECONDS_BETWEEN_REPLIES:
                wait_time = int(self.MIN_SECONDS_BETWEEN_REPLIES - seconds_since_last)
                return False, f"Cooldown active ({wait_time}s remaining)"

        return True, "OK"

    def post_comment_reply(self, comment_id: str, reply_text: str) -> Optional[Dict]:
        """
        Post a reply to a YouTube comment.

        Args:
            comment_id: YouTube comment ID to reply to
            reply_text: Reply text to post

        Returns:
            Posted comment data or None if failed
        """
        # Check safety limits
        can_post, reason = self.can_post_reply()
        if not can_post:
            logger.warning(f"Cannot post reply: {reason}")
            return None

        # Validate reply length
        if len(reply_text) > self.MAX_REPLY_LENGTH:
            logger.error(f"Reply too long: {len(reply_text)} chars (max {self.MAX_REPLY_LENGTH})")
            reply_text = reply_text[:self.MAX_REPLY_LENGTH - 3] + "..."

        try:
            logger.info(f"Posting reply to comment {comment_id}")

            # NOTE: This will fail with API key - needs OAuth
            # Keeping code structure ready for OAuth implementation
            request_body = {
                'snippet': {
                    'parentId': comment_id,
                    'textOriginal': reply_text
                }
            }

            # This requires OAuth - will fail with API key
            response = self.youtube.comments().insert(
                part='snippet',
                body=request_body
            ).execute()

            # Update counters
            self.replies_posted_today += 1
            self.last_post_time = datetime.now()

            logger.info(f"Reply posted successfully! ID: {response.get('id', 'unknown')}")
            return response

        except HttpError as e:
            if e.resp.status == 403:
                if 'commentsDisabled' in str(e):
                    logger.error("Comments are disabled on this video")
                elif 'insufficientPermissions' in str(e):
                    logger.error("OAuth authentication required to post comments")
                else:
                    logger.error(f"Permission error: {e}")
            else:
                logger.error(f"HTTP error posting reply: {e}")
            return None

        except Exception as e:
            logger.error(f"Error posting reply: {e}")
            return None

    def post_approved_replies(self) -> Dict:
        """
        Post all approved replies to YouTube.

        Returns:
            Dictionary with posting statistics
        """
        stats = {
            'attempted': 0,
            'posted': 0,
            'failed': 0,
            'skipped': 0,
            'errors': []
        }

        # Get approved replies
        approved_replies = self.database.get_approved_replies()

        if not approved_replies:
            logger.info("No approved replies to post")
            return stats

        logger.info(f"Found {len(approved_replies)} approved replies")

        for reply_record in approved_replies:
            reply_id = reply_record['id']
            reply_fields = reply_record['fields']
            stats['attempted'] += 1

            try:
                # Get thread data to find comment URL
                thread_links = reply_fields.get('Thread', [])
                if not thread_links:
                    logger.error(f"No thread linked to reply {reply_id}")
                    stats['failed'] += 1
                    continue

                thread = self.database.threads_table.get(thread_links[0])
                thread_fields = thread['fields']

                # Extract comment ID from comment URL
                comment_url = thread_fields.get('Comment URL', '')
                comment_id = self._extract_comment_id(comment_url)

                if not comment_id:
                    logger.error(f"Cannot extract comment ID from URL: {comment_url}")
                    stats['failed'] += 1
                    continue

                # Get reply text
                reply_text = reply_fields.get('AI Generated Reply', '')

                # Post reply
                posted_comment = self.post_comment_reply(comment_id, reply_text)

                if posted_comment:
                    # Update Airtable - mark as posted
                    self.database.update_pending_reply(reply_id, {
                        'Approval Status': 'posted',
                        'Posted At': datetime.now().isoformat()
                    })

                    # Update conversation thread
                    from src.conversation import ConversationTracker
                    tracker = ConversationTracker(self.database)
                    tracker.update_thread_with_reply(thread_links[0], reply_text)

                    stats['posted'] += 1
                    logger.info(f"Posted reply {reply_id}")

                else:
                    stats['failed'] += 1
                    error_msg = "Failed to post (check OAuth setup)"
                    stats['errors'].append(error_msg)

                    # Mark as failed in Airtable
                    self.database.update_pending_reply(reply_id, {
                        'Your Notes': error_msg
                    })

                # Wait between posts (cooldown)
                if stats['attempted'] < len(approved_replies):
                    time.sleep(self.MIN_SECONDS_BETWEEN_REPLIES)

            except Exception as e:
                logger.error(f"Error processing reply {reply_id}: {e}")
                stats['failed'] += 1
                stats['errors'].append(str(e))

        logger.info(f"Posting complete: {stats['posted']}/{stats['attempted']} posted, "
                   f"{stats['failed']} failed, {stats['skipped']} skipped")

        return stats

    def _extract_comment_id(self, comment_url: str) -> Optional[str]:
        """Extract YouTube comment ID from comment URL."""
        try:
            # Format: https://www.youtube.com/watch?v=VIDEO_ID&lc=COMMENT_ID
            if 'lc=' in comment_url:
                comment_id = comment_url.split('lc=')[1].split('&')[0]
                return comment_id
            return None
        except Exception as e:
            logger.error(f"Error extracting comment ID: {e}")
            return None
