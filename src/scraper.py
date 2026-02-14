"""YouTube scraper for extracting comments from Sadhguru-related content."""

import json
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from src.config import settings
from src.utils import setup_logger

logger = setup_logger(__name__)


def _http_error_reason(e: HttpError) -> str:
    """Extract reason from YouTube API 403/error response for clearer logging."""
    try:
        if getattr(e, 'content', None):
            body = json.loads(e.content.decode('utf-8'))
            err = body.get('error', {})
            for item in err.get('errors', [{}]):
                if item.get('reason'):
                    return item['reason']
            return err.get('message', str(e))
    except Exception:
        pass
    return str(e)


class YouTubeScraper:
    """Scrapes YouTube comments from Sadhguru-related channels."""

    def __init__(self):
        """Initialize YouTube API client and quota tracker."""
        self.youtube = build('youtube', 'v3', developerKey=settings.youtube_api_key)
        self.quota_used = 0
        self.quota_limit = settings.youtube_quota_limit
        self.channel_id_cache = {}  # Cache for channel handle -> ID mappings

    def _increment_quota(self, cost: int) -> bool:
        """
        Increment quota usage and check if limit is reached.

        Args:
            cost: Quota cost of the operation

        Returns:
            True if within limit, False if limit exceeded
        """
        self.quota_used += cost
        logger.info(f"Quota used: {self.quota_used}/{self.quota_limit}")

        if self.quota_used >= self.quota_limit:
            logger.warning(f"Approaching quota limit ({self.quota_used}/{self.quota_limit}). Stopping.")
            return False
        return True

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((HttpError,)),
        reraise=True
    )
    def discover_channels(self, search_terms: List[str]) -> List[Dict]:
        """
        Discover Sadhguru-related YouTube channels.

        Args:
            search_terms: List of search queries

        Returns:
            List of channel dictionaries with id, title, and subscriber count
        """
        channels = []
        seen_channel_ids = set()

        for term in search_terms:
            if not self._increment_quota(100):  # search.list costs 100 units
                break

            try:
                logger.info(f"Searching for channels: '{term}'")
                response = self.youtube.search().list(
                    part='snippet',
                    q=term,
                    type='channel',
                    maxResults=5,
                    order='relevance'
                ).execute()

                for item in response.get('items', []):
                    channel_id = item['id']['channelId']

                    if channel_id in seen_channel_ids:
                        continue

                    # Get channel statistics to check subscriber count
                    if not self._increment_quota(1):  # channels.list costs 1 unit
                        break

                    channel_response = self.youtube.channels().list(
                        part='statistics,snippet',
                        id=channel_id
                    ).execute()

                    if channel_response.get('items'):
                        channel_data = channel_response['items'][0]
                        stats = channel_data['statistics']
                        subscriber_count = int(stats.get('subscriberCount', 0))

                        if subscriber_count >= settings.min_subscriber_count:
                            channels.append({
                                'id': channel_id,
                                'title': channel_data['snippet']['title'],
                                'subscribers': subscriber_count
                            })
                            seen_channel_ids.add(channel_id)
                            logger.info(f"Found channel: {channel_data['snippet']['title']} ({subscriber_count:,} subscribers)")

            except HttpError as e:
                if e.resp.status == 403:
                    logger.error("Quota exceeded. Stopping channel discovery.")
                    break
                elif e.resp.status in [500, 503]:
                    logger.warning(f"Server error during channel search: {e}. Retrying...")
                    raise
                else:
                    logger.error(f"Error searching for '{term}': {e}")
                    continue

        logger.info(f"Discovered {len(channels)} channels")
        return channels

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((HttpError,)),
        reraise=True
    )
    def get_recent_videos(self, channel_id: str, days_back: int) -> List[Dict]:
        """
        Get recent videos from a channel.

        Args:
            channel_id: YouTube channel ID
            days_back: Number of days to look back

        Returns:
            List of video dictionaries with id, title, and published date
        """
        videos = []
        published_after = (datetime.utcnow() - timedelta(days=days_back)).isoformat() + 'Z'

        try:
            if not self._increment_quota(100):  # search.list costs 100 units
                return videos

            logger.info(f"Fetching videos from channel {channel_id} (last {days_back} days)")
            response = self.youtube.search().list(
                part='snippet',
                channelId=channel_id,
                type='video',
                order='date',
                publishedAfter=published_after,
                maxResults=settings.max_videos_per_channel
            ).execute()

            for item in response.get('items', []):
                videos.append({
                    'id': item['id']['videoId'],
                    'title': item['snippet']['title'],
                    'published': item['snippet']['publishedAt'],
                    'url': f"https://www.youtube.com/watch?v={item['id']['videoId']}"
                })

            logger.info(f"Found {len(videos)} recent videos")

        except HttpError as e:
            if e.resp.status == 403:
                reason = _http_error_reason(e)
                logger.error("Video fetch 403: %s. (If quotaExceeded: check Google Cloud Console → APIs → YouTube Data API v3 → Quotas; default 10,000 units/day.)", reason)
            elif e.resp.status in [500, 503]:
                logger.warning(f"Server error fetching videos: {e}. Retrying...")
                raise
            else:
                logger.error(f"Error fetching videos from channel {channel_id}: {e}")

        return videos

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((HttpError,)),
        reraise=True
    )
    def get_video_comments(self, video_id: str, max_results: int) -> List[Dict]:
        """
        Extract comments from a video.

        Args:
            video_id: YouTube video ID
            max_results: Maximum number of comments to fetch

        Returns:
            List of comment dictionaries
        """
        comments = []

        try:
            if not self._increment_quota(1):  # commentThreads.list costs 1 unit
                return comments

            logger.info(f"Fetching comments from video {video_id}")
            response = self.youtube.commentThreads().list(
                part='snippet',
                videoId=video_id,
                maxResults=min(max_results, 100),  # API max is 100 per request
                order='relevance',
                textFormat='plainText'
            ).execute()

            for item in response.get('items', []):
                comment = item['snippet']['topLevelComment']['snippet']
                comment_id = item['snippet']['topLevelComment']['id']

                comments.append({
                    'id': comment_id,
                    'author': comment['authorDisplayName'],
                    'text': comment['textDisplay'],
                    'likes': comment['likeCount'],
                    'published': comment['publishedAt'],
                    'video_id': video_id,
                    'video_url': f"https://www.youtube.com/watch?v={video_id}",
                    'comment_url': self.build_comment_url(video_id, comment_id)
                })

            logger.info(f"Fetched {len(comments)} comments from video {video_id}")

        except HttpError as e:
            if e.resp.status == 403:
                if 'commentsDisabled' in str(e):
                    logger.info(f"Comments disabled for video {video_id}")
                else:
                    reason = _http_error_reason(e)
                    logger.error("Comment fetch 403: %s", reason)
            elif e.resp.status in [500, 503]:
                logger.warning(f"Server error fetching comments: {e}. Retrying...")
                raise
            else:
                logger.error(f"Error fetching comments from video {video_id}: {e}")

        return comments

    @staticmethod
    def build_comment_url(video_id: str, comment_id: str) -> str:
        """
        Build a direct URL to a specific comment.

        Args:
            video_id: YouTube video ID
            comment_id: Comment ID

        Returns:
            Direct URL to the comment
        """
        return f"https://www.youtube.com/watch?v={video_id}&lc={comment_id}"

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((HttpError,)),
        reraise=True
    )
    def get_channel_id_from_handle(self, handle: str) -> Optional[str]:
        """
        Convert a channel handle (@username) to channel ID.

        Args:
            handle: Channel handle (e.g., '@sadhguru')

        Returns:
            Channel ID or None if not found
        """
        # Check cache first
        if handle in self.channel_id_cache:
            logger.debug(f"Using cached channel ID for {handle}")
            return self.channel_id_cache[handle]

        # Remove @ prefix if present
        handle_clean = handle.lstrip('@')

        try:
            logger.info(f"Looking up channel ID for handle: {handle}")

            # Use search API to resolve handle -> channel ID (forHandle not in this client version)
            if not self._increment_quota(100):  # search.list costs 100 units
                return None

            response = self.youtube.search().list(
                part='snippet',
                q=handle_clean,
                type='channel',
                maxResults=1
            ).execute()

            if response.get('items'):
                channel_id = response['items'][0]['id']['channelId']
                logger.info(f"Found channel ID via search: {channel_id}")

                # Cache the result
                self.channel_id_cache[handle] = channel_id
                return channel_id

            logger.warning(f"Channel not found: {handle}")
            return None

        except HttpError as e:
            if e.resp.status == 403:
                reason = _http_error_reason(e)
                logger.error("Channel lookup 403: %s. (If quotaExceeded: daily quota 10,000 units may be exhausted.)", reason)
            else:
                logger.error(f"Error looking up channel {handle}: {e}")
            return None

    def scrape_all_v2(self) -> List[Dict]:
        """
        Main orchestration method using hardcoded channels (no search).

        Returns:
            List of all scraped comments
        """
        all_comments = []

        logger.info("Starting YouTube scrape (v2 - hardcoded channels)...")
        logger.info(f"Target channels: {len(settings.target_channels_list)}")
        logger.info(f"Days back: {settings.days_back}")
        logger.info(f"Max videos per channel: {settings.max_videos_per_channel}")
        logger.info(f"Max comments per video: {settings.max_comments_per_video}")

        # Process each hardcoded channel
        for i, handle in enumerate(settings.target_channels_list, 1):
            if self.quota_used >= self.quota_limit:
                logger.warning("Quota limit reached. Stopping scrape.")
                break

            logger.info(f"Processing channel {i}/{len(settings.target_channels_list)}: {handle}")

            # Get channel ID from handle
            channel_id = self.get_channel_id_from_handle(handle)

            if not channel_id:
                logger.warning(f"Skipping {handle} - could not resolve channel ID")
                continue

            # Get recent videos
            videos = self.get_recent_videos(channel_id, settings.days_back)

            if not videos:
                logger.info(f"No recent videos found for {handle}")
                continue

            # Get comments from each video
            for video in videos:
                if self.quota_used >= self.quota_limit:
                    break

                comments = self.get_video_comments(
                    video['id'],
                    settings.max_comments_per_video
                )

                # Add channel and video metadata to each comment
                for comment in comments:
                    comment['channel_id'] = channel_id
                    comment['channel_handle'] = handle
                    comment['video_title'] = video['title']

                all_comments.extend(comments)

            logger.info(f"Channel {handle}: collected {len([c for c in all_comments if c.get('channel_handle') == handle])} comments")

        logger.info(f"Scrape complete. Total comments: {len(all_comments)}")
        logger.info(f"Final quota used: {self.quota_used}/{self.quota_limit}")

        return all_comments

    def scrape_all(self) -> List[Dict]:
        """
        Main orchestration method to scrape all comments.

        Returns:
            List of all scraped comments
        """
        all_comments = []

        logger.info("Starting YouTube scrape...")
        logger.info(f"Search terms: {settings.search_terms_list}")
        logger.info(f"Days back: {settings.days_back}")
        logger.info(f"Max videos per channel: {settings.max_videos_per_channel}")
        logger.info(f"Max comments per video: {settings.max_comments_per_video}")

        # Discover channels
        channels = self.discover_channels(settings.search_terms_list)

        if not channels:
            logger.warning("No channels discovered. Exiting.")
            return all_comments

        # Process each channel
        for channel in channels:
            if self.quota_used >= self.quota_limit:
                logger.warning("Quota limit reached. Stopping scrape.")
                break

            # Get recent videos
            videos = self.get_recent_videos(channel['id'], settings.days_back)

            # Get comments from each video
            for video in videos:
                if self.quota_used >= self.quota_limit:
                    break

                comments = self.get_video_comments(
                    video['id'],
                    settings.max_comments_per_video
                )

                # Add channel and video metadata to each comment
                for comment in comments:
                    comment['channel_id'] = channel['id']
                    comment['channel_title'] = channel['title']
                    comment['video_title'] = video['title']

                all_comments.extend(comments)

        logger.info(f"Scrape complete. Total comments: {len(all_comments)}")
        logger.info(f"Final quota used: {self.quota_used}/{self.quota_limit}")

        return all_comments
