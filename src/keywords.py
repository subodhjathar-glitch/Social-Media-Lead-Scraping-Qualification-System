"""Keyword detection module for fast pain signal pattern matching."""

import re
from typing import Dict, List, Set
from src.utils import setup_logger

logger = setup_logger(__name__)


class KeywordDetector:
    """Detects pain signals and practice mentions using regex-based pattern matching."""

    # Pain keyword sets (case-insensitive)
    PHYSICAL_PAIN = {
        'back pain', 'backpain', 'knee pain', 'kneepain', 'neck pain', 'neckpain',
        'stiffness', 'stiff', 'fatigue', 'tired', 'exhausted', 'obesity', 'obese',
        'thyroid', 'spine', 'spinal', 'posture', 'chronic pain', 'body pain',
        'flexibility', 'flexible', 'injury', 'injured', 'sore', 'ache', 'aching'
    }

    MENTAL_PAIN = {
        'anxiety', 'anxious', 'depression', 'depressed', 'stress', 'stressed',
        'confusion', 'confused', 'anger', 'angry', 'overthinking', 'overthink',
        'restless', 'restlessness', 'mental chaos', 'worry', 'worried', 'fear',
        'fearful', 'panic', 'panicking', 'overwhelm', 'overwhelmed', 'mental health',
        'emotional', 'emotions', 'mood', 'sad', 'sadness', 'lonely', 'loneliness'
    }

    DISCIPLINE = {
        'quit', 'quitting', 'stopped', 'stop practicing', 'cant stay consistent',
        'can\'t stay consistent', 'lost motivation', 'losing motivation', 'discipline',
        'undisciplined', 'irregular', 'inconsistent', 'struggle to practice',
        'struggling to practice', 'gave up', 'giving up', 'difficult to continue',
        'hard to continue', 'not practicing', 'stopped doing'
    }

    SPIRITUAL = {
        'purpose', 'life purpose', 'transformation', 'transform', 'awakening',
        'awaken', 'inner peace', 'peace', 'self-realization', 'self realization',
        'enlightenment', 'enlightened', 'meaning', 'meaningful', 'meaningless',
        'seeking', 'searching', 'lost', 'empty', 'emptiness', 'disconnected',
        'connection', 'consciousness', 'awareness', 'spiritual', 'spirituality',
        'soul', 'divine', 'truth', 'liberation', 'moksha', 'bliss', 'joy'
    }

    PRACTICES = {
        'angamardana', 'surya kriya', 'surya shakti', 'yogasanas', 'yoga asanas',
        'shambhavi', 'shambhavi mahamudra', 'shakti chalana kriya', 'hatha yoga',
        'sadhguru', 'isha foundation', 'isha', 'adiyogi', 'inner engineering',
        'isha kriya', 'yogic practices', 'meditation', 'dhyanalinga', 'bhuta shuddhi',
        'sambhavi', 'shambavy'  # Common misspellings
    }

    def __init__(self):
        """Initialize keyword detector with compiled regex patterns."""
        self.physical_pattern = self._compile_pattern(self.PHYSICAL_PAIN)
        self.mental_pattern = self._compile_pattern(self.MENTAL_PAIN)
        self.discipline_pattern = self._compile_pattern(self.DISCIPLINE)
        self.spiritual_pattern = self._compile_pattern(self.SPIRITUAL)
        self.practices_pattern = self._compile_pattern(self.PRACTICES)

    def _compile_pattern(self, keywords: Set[str]) -> re.Pattern:
        """
        Compile a regex pattern from a set of keywords.

        Args:
            keywords: Set of keyword phrases

        Returns:
            Compiled regex pattern
        """
        # Sort by length (longest first) to match multi-word phrases first
        sorted_keywords = sorted(keywords, key=len, reverse=True)
        # Escape special regex characters and join with OR
        pattern = '|'.join(re.escape(kw) for kw in sorted_keywords)
        return re.compile(pattern, re.IGNORECASE)

    def detect_signals(self, text: str) -> Dict:
        """
        Detect pain signals and practice mentions in text.

        Args:
            text: Comment text to analyze

        Returns:
            Dictionary with detected patterns and preliminary scoring
        """
        if not text or not text.strip():
            return self._empty_result()

        text_lower = text.lower()

        # Find matches for each category
        physical_matches = self.physical_pattern.findall(text_lower)
        mental_matches = self.mental_pattern.findall(text_lower)
        discipline_matches = self.discipline_pattern.findall(text_lower)
        spiritual_matches = self.spiritual_pattern.findall(text_lower)
        practice_matches = self.practices_pattern.findall(text_lower)

        # Calculate preliminary pain score (0-10)
        # Scoring logic: each category contributes to overall pain score
        pain_score = 0
        if spiritual_matches:
            pain_score += 4  # Highest priority - spiritual longing
        if mental_matches:
            pain_score += 3  # High priority - mental/emotional pain
        if discipline_matches:
            pain_score += 2  # Medium priority - discipline struggles
        if physical_matches:
            pain_score += 1  # Lower priority - physical pain

        # Cap at 10
        pain_score = min(10, pain_score)

        # Determine primary intent type
        intent_type = self._determine_intent_type(
            physical_matches, mental_matches, discipline_matches,
            spiritual_matches, practice_matches
        )

        result = {
            'has_physical_pain': bool(physical_matches),
            'has_mental_pain': bool(mental_matches),
            'has_discipline_issue': bool(discipline_matches),
            'has_spiritual_longing': bool(spiritual_matches),
            'practice_mentions': list(set(practice_matches)),  # Deduplicate
            'keywords_found': self._get_all_keywords(
                physical_matches, mental_matches, discipline_matches,
                spiritual_matches, practice_matches
            ),
            'preliminary_pain_score': pain_score,
            'preliminary_intent': intent_type
        }

        if result['keywords_found']:
            logger.debug(f"Keywords detected: {result['keywords_found'][:3]}...")

        return result

    def _determine_intent_type(self, physical: List, mental: List,
                               discipline: List, spiritual: List,
                               practice: List) -> str:
        """Determine primary intent type based on detected keywords."""
        # Priority order: practice_aligned > spiritual > mental > discipline > physical

        if practice and (spiritual or mental or discipline):
            return 'practice_aligned'
        elif spiritual:
            return 'spiritual'
        elif mental:
            return 'mental_pain'
        elif discipline:
            return 'discipline'
        elif physical:
            return 'physical_pain'
        else:
            return 'low_intent'

    def _get_all_keywords(self, physical: List, mental: List,
                         discipline: List, spiritual: List,
                         practice: List) -> List[str]:
        """Combine all detected keywords into a single list."""
        all_keywords = []
        all_keywords.extend(physical)
        all_keywords.extend(mental)
        all_keywords.extend(discipline)
        all_keywords.extend(spiritual)
        all_keywords.extend(practice)
        return list(set(all_keywords))  # Deduplicate

    def _empty_result(self) -> Dict:
        """Return empty result dictionary."""
        return {
            'has_physical_pain': False,
            'has_mental_pain': False,
            'has_discipline_issue': False,
            'has_spiritual_longing': False,
            'practice_mentions': [],
            'keywords_found': [],
            'preliminary_pain_score': 0,
            'preliminary_intent': 'low_intent'
        }

    def detect_batch(self, comments: List[Dict]) -> List[Dict]:
        """
        Detect keywords for a batch of comments.

        Args:
            comments: List of comment dictionaries with 'text' field

        Returns:
            List of comments with keyword detection results added
        """
        logger.info(f"Running keyword detection on {len(comments)} comments")

        for comment in comments:
            detection_result = self.detect_signals(comment.get('text', ''))
            # Merge detection results into comment
            comment['keyword_detection'] = detection_result

        # Log summary statistics
        practice_count = sum(1 for c in comments if c['keyword_detection']['practice_mentions'])
        spiritual_count = sum(1 for c in comments if c['keyword_detection']['has_spiritual_longing'])
        mental_count = sum(1 for c in comments if c['keyword_detection']['has_mental_pain'])

        logger.info(f"Keyword detection complete: Practice mentions={practice_count}, "
                   f"Spiritual={spiritual_count}, Mental={mental_count}")

        return comments
