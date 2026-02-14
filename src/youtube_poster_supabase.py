"""
YouTube comment posting with OAuth authentication - Supabase version.

This module handles posting approved replies to YouTube comments.
"""

import time
from datetime import datetime
from typing import Dict, Optional
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from src.config import settings
from src.utils import setup_logger

logger = setup_logger(__name__)


class YouTubePoster:
    """Posts approved replies to YouTube comments."""

    # Safety limits
    MAX_REPLIES_PER_DAY = 20
    MIN_SECONDS_BETWEEN_REPLIES = 60  # 1 minute cooldown
    MAX_REPLY_LENGTH = 10000  # YouTube limit

    def __init__(self, supabase_client):
        """
        Initialize YouTube poster.

        Args:
            supabase_client: Supabase client instance
        """
        self.supabase = supabase_client
        self.youtube = None  # Will be initialized after OAuth
        self.replies_posted_today = 0
        self.last_post_time = None

    def initialize_youtube_client(self, credentials=None):
        """
        Initialize YouTube API client with OAuth credentials.

        Args:
            credentials: OAuth credentials object (from google-auth)

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if credentials:
                # Use OAuth credentials
                self.youtube = build('youtube', 'v3', credentials=credentials)
                logger.info("YouTube client initialized with OAuth")
            else:
                # Fallback to API key (read-only)
                self.youtube = build('youtube', 'v3', developerKey=settings.youtube_api_key)
                logger.warning("YouTube client initialized with API key (read-only mode)")

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

    def extract_comment_id(self, comment_url: str) -> Optional[str]:
        """
        Extract YouTube comment ID from comment URL.

        Args:
            comment_url: YouTube comment URL

        Returns:
            Comment ID or None if not found
        """
        try:
            # Format: https://www.youtube.com/watch?v=VIDEO_ID&lc=COMMENT_ID
            if 'lc=' in comment_url:
                comment_id = comment_url.split('lc=')[1].split('&')[0]
                return comment_id
            return None
        except Exception as e:
            logger.error(f"Error extracting comment ID: {e}")
            return None

    def post_comment_reply(self, comment_id: str, reply_text: str) -> Dict:
        """
        Post a reply to a YouTube comment.

        Args:
            comment_id: YouTube comment ID to reply to
            reply_text: Reply text to post

        Returns:
            Dictionary with status: 'success', 'failed', or 'no_oauth'
            and additional info (error message, comment data, etc.)
        """
        # Check if YouTube client is initialized
        if not self.youtube:
            return {
                'status': 'no_oauth',
                'error': 'YouTube client not initialized. Run OAuth setup first.'
            }

        # Check safety limits
        can_post, reason = self.can_post_reply()
        if not can_post:
            return {
                'status': 'failed',
                'error': reason
            }

        # Validate reply length
        if len(reply_text) > self.MAX_REPLY_LENGTH:
            logger.warning(f"Reply too long: {len(reply_text)} chars, truncating")
            reply_text = reply_text[:self.MAX_REPLY_LENGTH - 3] + "..."

        try:
            logger.info(f"Posting reply to comment {comment_id}")

            request_body = {
                'snippet': {
                    'parentId': comment_id,
                    'textOriginal': reply_text
                }
            }

            # Post comment
            response = self.youtube.comments().insert(
                part='snippet',
                body=request_body
            ).execute()

            # Update counters
            self.replies_posted_today += 1
            self.last_post_time = datetime.now()

            logger.info(f"✅ Reply posted successfully! ID: {response.get('id', 'unknown')}")

            return {
                'status': 'success',
                'comment_id': response.get('id'),
                'posted_at': datetime.now().isoformat()
            }

        except HttpError as e:
            error_msg = str(e)

            if e.resp.status == 403:
                if 'commentsDisabled' in error_msg:
                    error = "Comments are disabled on this video"
                elif 'insufficientPermissions' in error_msg or 'quotaExceeded' not in error_msg:
                    error = "OAuth authentication required to post comments"
                else:
                    error = f"Permission denied: {error_msg}"
            elif e.resp.status == 400:
                error = f"Bad request: {error_msg}"
            else:
                error = f"HTTP {e.resp.status}: {error_msg}"

            logger.error(f"❌ {error}")
            return {
                'status': 'failed',
                'error': error
            }

        except Exception as e:
            error = f"Unexpected error: {str(e)}"
            logger.error(f"❌ {error}")
            return {
                'status': 'failed',
                'error': error
            }

    def post_approved_reply_from_ui(self, reply_id: str, edited_reply_text: str) -> Dict:
        """
        Post a single approved reply from the UI.

        This is called when a teacher approves a reply in Streamlit.

        Args:
            reply_id: UUID of the pending_reply record
            edited_reply_text: The (possibly edited) reply text

        Returns:
            Dictionary with posting status and info
        """
        try:
            # Get the reply record
            reply = self.supabase.table('pending_replies')\
                .select('*, conversation_threads(*)')\
                .eq('id', reply_id)\
                .single()\
                .execute()

            if not reply.data:
                return {
                    'status': 'failed',
                    'error': 'Reply not found in database'
                }

            reply_data = reply.data
            thread = reply_data.get('conversation_threads', {})

            # Extract comment ID from URL
            comment_url = thread.get('comment_url', '')
            comment_id = self.extract_comment_id(comment_url)

            if not comment_id:
                return {
                    'status': 'failed',
                    'error': f'Could not extract comment ID from URL: {comment_url}'
                }

            # Post the reply
            result = self.post_comment_reply(comment_id, edited_reply_text)

            if result['status'] == 'success':
                # Update database - mark as posted
                self.supabase.table('pending_replies').update({
                    'approval_status': 'posted',
                    'posted_at': result['posted_at'],
                    'ai_generated_reply': edited_reply_text  # Save edited version
                }).eq('id', reply_id).execute()

                # Update conversation thread
                self.supabase.table('conversation_threads').update({
                    'last_reply_date': datetime.now().strftime('%Y-%m-%d'),
                    'conversation_stage': thread.get('conversation_stage', 0) + 1
                }).eq('id', thread.get('id')).execute()

                logger.info(f"✅ Reply {reply_id} posted and database updated")

            return result

        except Exception as e:
            logger.error(f"Error in post_approved_reply_from_ui: {e}")
            return {
                'status': 'failed',
                'error': str(e)
            }

    def batch_post_approved_replies(self) -> Dict:
        """
        Post all approved replies (batch operation).

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

        try:
            # Get all approved (but not yet posted) replies
            approved = self.supabase.table('pending_replies')\
                .select('*, conversation_threads(*)')\
                .eq('approval_status', 'approved')\
                .execute()

            if not approved.data:
                logger.info("No approved replies to post")
                return stats

            logger.info(f"Found {len(approved.data)} approved replies to post")

            for reply in approved.data:
                stats['attempted'] += 1

                try:
                    thread = reply.get('conversation_threads', {})
                    comment_url = thread.get('comment_url', '')
                    comment_id = self.extract_comment_id(comment_url)

                    if not comment_id:
                        stats['failed'] += 1
                        stats['errors'].append(f"No comment ID for {reply['lead_name']}")
                        continue

                    # Post reply
                    result = self.post_comment_reply(comment_id, reply['ai_generated_reply'])

                    if result['status'] == 'success':
                        # Update database
                        self.supabase.table('pending_replies').update({
                            'approval_status': 'posted',
                            'posted_at': result['posted_at']
                        }).eq('id', reply['id']).execute()

                        stats['posted'] += 1
                    else:
                        stats['failed'] += 1
                        stats['errors'].append(result.get('error', 'Unknown error'))

                    # Cooldown between posts
                    if stats['attempted'] < len(approved.data):
                        time.sleep(self.MIN_SECONDS_BETWEEN_REPLIES)

                except Exception as e:
                    stats['failed'] += 1
                    stats['errors'].append(str(e))
                    logger.error(f"Error posting reply {reply['id']}: {e}")

            logger.info(f"Batch posting complete: {stats['posted']}/{stats['attempted']} posted")

        except Exception as e:
            logger.error(f"Error in batch_post_approved_replies: {e}")
            stats['errors'].append(str(e))

        return stats
