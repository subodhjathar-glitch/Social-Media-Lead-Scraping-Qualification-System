"""Pre-filter module to reduce AI qualification costs by 70-90%."""

import re
from typing import Tuple
from src.utils import setup_logger

logger = setup_logger(__name__)


class CommentPreFilter:
    """Pre-filters comments to reject low-quality content before expensive AI calls."""

    # Regex patterns
    EMOJI_ONLY_PATTERN = re.compile(r'^[\U0001F000-\U0001F9FF\s\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\U00002702-\U000027B0\U000024C2-\U0001F251]+$')

    # Praise-only words (generic positive comments with no action intent)
    PRAISE_ONLY_WORDS = {
        'namaskaram', 'amazing', 'thank', 'thanks', 'love', 'loved',
        'great', 'wow', 'nice', 'good', 'beautiful', 'powerful',
        'first', 'om', 'namaste', 'jai', 'bless', 'blessed',
        'fantastic', 'awesome', 'excellent', 'wonderful', 'perfect',
        'watching', 'watching from', 'from', 'india', 'pakistan',
        'nepal', 'bangladesh', 'country', 'city', 'state'
    }

    # Action verbs that indicate meaningful engagement
    ACTION_VERBS = {
        'want', 'need', 'help', 'how', 'can', 'will', 'should',
        'would', 'could', 'may', 'might', 'struggling', 'struggle',
        'feeling', 'feel', 'felt', 'experiencing', 'experience',
        'suffering', 'suffer', 'dealing', 'deal', 'seeking', 'seek',
        'looking', 'look', 'trying', 'try', 'learning', 'learn',
        'doing', 'do', 'practicing', 'practice', 'practise',
        'stopped', 'stop', 'quit', 'started', 'start', 'begin',
        'register', 'enroll', 'join', 'sign', 'signup',
        'pain', 'hurt', 'ache', 'anxiety', 'depression', 'stress',
        'confused', 'lost', 'empty', 'seeking', 'transformation'
    }

    def should_skip(self, text: str) -> Tuple[bool, str]:
        """
        Determine if a comment should be skipped (not sent to AI).

        Args:
            text: Comment text to evaluate

        Returns:
            Tuple of (should_skip: bool, reason: str)
        """
        if not text or not text.strip():
            return True, "empty"

        text_clean = text.strip()
        text_lower = text_clean.lower()

        # Filter 1: Too short (< 4 words)
        words = text_clean.split()
        if len(words) < 4:
            return True, "too_short"

        # Filter 2: Only emojis and punctuation
        if self.EMOJI_ONLY_PATTERN.match(text_clean):
            return True, "emoji_only"

        # Filter 3: Only praise words (no action verbs)
        if self._is_praise_only(text_lower):
            return True, "praise_only"

        # Filter 4: No meaningful content (check for action verbs)
        if not self._has_meaningful_verb(text_lower):
            # Additional check: if it has question mark or pain keywords, keep it
            if '?' not in text_clean and not self._has_pain_keywords(text_lower):
                return True, "no_meaningful_content"

        # Passed all filters
        return False, "passed"

    def _is_praise_only(self, text_lower: str) -> bool:
        """Check if text contains only praise words and common filler words."""
        words = set(re.findall(r'\b\w+\b', text_lower))

        # Remove very common filler words
        filler_words = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been',
                       'this', 'that', 'these', 'those', 'so', 'very', 'much',
                       'from', 'to', 'in', 'on', 'at', 'for', 'with', 'by'}

        meaningful_words = words - filler_words

        # If all meaningful words are praise words, it's praise-only
        if meaningful_words and meaningful_words.issubset(self.PRAISE_ONLY_WORDS):
            return True

        return False

    def _has_meaningful_verb(self, text_lower: str) -> bool:
        """Check if text contains action verbs indicating engagement."""
        words = set(re.findall(r'\b\w+\b', text_lower))
        return bool(words & self.ACTION_VERBS)

    def _has_pain_keywords(self, text_lower: str) -> bool:
        """Quick check for pain-related keywords that should bypass filters."""
        pain_keywords = {
            'pain', 'hurt', 'ache', 'anxiety', 'depression', 'stress',
            'suffering', 'struggle', 'problem', 'issue', 'difficulty',
            'lost', 'confused', 'empty', 'purpose', 'meaning'
        }
        words = set(re.findall(r'\b\w+\b', text_lower))
        return bool(words & pain_keywords)

    def filter_batch(self, comments: list) -> Tuple[list, dict]:
        """
        Filter a batch of comments.

        Args:
            comments: List of comment dictionaries with 'text' field

        Returns:
            Tuple of (filtered_comments: list, stats: dict)
        """
        filtered = []
        stats = {
            'total': len(comments),
            'passed': 0,
            'skipped_too_short': 0,
            'skipped_emoji_only': 0,
            'skipped_praise_only': 0,
            'skipped_no_content': 0,
            'skipped_no_meaningful_content': 0,
            'skipped_empty': 0
        }

        for comment in comments:
            should_skip, reason = self.should_skip(comment.get('text', ''))

            if should_skip:
                # Track skip reason (ensure key exists for any reason)
                key = f'skipped_{reason}'
                stats[key] = stats.get(key, 0) + 1
                # Add pre-filter status to comment for tracking
                comment['prefilter_status'] = f'skipped_{reason}'
                logger.debug(f"Skipped comment ({reason}): {comment.get('text', '')[:50]}...")
            else:
                stats['passed'] += 1
                comment['prefilter_status'] = 'passed'
                filtered.append(comment)

        logger.info(f"Pre-filter results: {stats['passed']}/{stats['total']} passed ({stats['passed']/stats['total']*100:.1f}%)")
        logger.info(f"  Skipped - too_short: {stats.get('skipped_too_short', 0)}, emoji_only: {stats.get('skipped_emoji_only', 0)}, "
                   f"praise_only: {stats.get('skipped_praise_only', 0)}, no_meaningful_content: {stats.get('skipped_no_meaningful_content', 0)}, empty: {stats.get('skipped_empty', 0)}")

        return filtered, stats
