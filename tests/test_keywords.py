"""Unit tests for the KeywordDetector class."""

import pytest
from src.keywords import KeywordDetector


class TestKeywordDetector:
    """Test cases for keyword detection functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.detector = KeywordDetector()

    def test_detect_physical_pain(self):
        """Test detection of physical pain keywords."""
        result = self.detector.detect_signals("I have severe back pain")
        assert result['has_physical_pain'] is True
        assert 'back pain' in result['keywords_found']
        assert result['preliminary_intent'] == 'physical_pain'

    def test_detect_mental_pain(self):
        """Test detection of mental/emotional pain keywords."""
        result = self.detector.detect_signals("I'm struggling with anxiety and depression")
        assert result['has_mental_pain'] is True
        assert 'anxiety' in result['keywords_found']
        assert result['preliminary_intent'] == 'mental_pain'

    def test_detect_discipline_issues(self):
        """Test detection of discipline struggle keywords."""
        result = self.detector.detect_signals("I stopped practicing Shambhavi 6 months ago")
        assert result['has_discipline_issue'] is True
        assert 'stopped' in result['keywords_found']
        assert result['preliminary_intent'] == 'discipline'

    def test_detect_spiritual_longing(self):
        """Test detection of spiritual longing keywords."""
        result = self.detector.detect_signals("I'm seeking purpose and transformation in life")
        assert result['has_spiritual_longing'] is True
        assert 'purpose' in result['keywords_found']
        assert 'transformation' in result['keywords_found']
        assert result['preliminary_intent'] == 'spiritual'

    def test_detect_practice_mentions(self):
        """Test detection of practice mentions."""
        result = self.detector.detect_signals("Will Shambhavi Mahamudra help with anxiety?")
        assert 'shambhavi' in result['practice_mentions']
        assert result['has_mental_pain'] is True
        assert result['preliminary_intent'] == 'practice_aligned'

        result = self.detector.detect_signals("I do Angamardana every morning")
        assert 'angamardana' in result['practice_mentions']

    def test_detect_multiple_pain_types(self):
        """Test detection when multiple pain types are present."""
        result = self.detector.detect_signals(
            "I have back pain and anxiety. Stopped doing yoga."
        )
        assert result['has_physical_pain'] is True
        assert result['has_mental_pain'] is True
        assert result['has_discipline_issue'] is True
        # Should prioritize mental pain over physical
        assert result['preliminary_intent'] == 'mental_pain'

    def test_practice_aligned_priority(self):
        """Test that practice mentions get highest priority."""
        result = self.detector.detect_signals(
            "Will Shambhavi help with my anxiety and depression?"
        )
        assert result['preliminary_intent'] == 'practice_aligned'
        assert 'shambhavi' in result['practice_mentions']
        assert result['has_mental_pain'] is True

    def test_spiritual_priority_over_physical(self):
        """Test that spiritual longing is prioritized over physical pain."""
        result = self.detector.detect_signals(
            "I have back pain but more importantly seeking life purpose"
        )
        assert result['has_physical_pain'] is True
        assert result['has_spiritual_longing'] is True
        assert result['preliminary_intent'] == 'spiritual'

    def test_preliminary_pain_score(self):
        """Test preliminary pain scoring."""
        # Spiritual longing = 4 points
        result = self.detector.detect_signals("Seeking transformation and awakening")
        assert result['preliminary_pain_score'] == 4

        # Mental pain = 3 points
        result = self.detector.detect_signals("I have anxiety")
        assert result['preliminary_pain_score'] == 3

        # Discipline = 2 points
        result = self.detector.detect_signals("I stopped practicing")
        assert result['preliminary_pain_score'] == 2

        # Physical pain = 1 point
        result = self.detector.detect_signals("I have back pain")
        assert result['preliminary_pain_score'] == 1

        # Multiple types (capped at 10)
        result = self.detector.detect_signals(
            "Seeking purpose, have anxiety, stopped practicing, back hurts"
        )
        assert result['preliminary_pain_score'] == 10  # 4+3+2+1 = 10

    def test_case_insensitive_detection(self):
        """Test that detection is case-insensitive."""
        result1 = self.detector.detect_signals("I have ANXIETY")
        result2 = self.detector.detect_signals("I have anxiety")
        result3 = self.detector.detect_signals("I have Anxiety")

        assert result1['has_mental_pain'] is True
        assert result2['has_mental_pain'] is True
        assert result3['has_mental_pain'] is True

    def test_misspelled_practice_names(self):
        """Test detection of common practice name misspellings."""
        result = self.detector.detect_signals("Does Sambhavi help?")  # misspelled
        assert 'sambhavi' in result['practice_mentions']

    def test_empty_text(self):
        """Test handling of empty text."""
        result = self.detector.detect_signals("")
        assert result['has_physical_pain'] is False
        assert result['has_mental_pain'] is False
        assert result['has_spiritual_longing'] is False
        assert result['practice_mentions'] == []
        assert result['preliminary_pain_score'] == 0

    def test_low_intent_comment(self):
        """Test that generic comments return low_intent."""
        result = self.detector.detect_signals("Namaskaram Sadhguru")
        assert result['preliminary_intent'] == 'low_intent'
        assert result['preliminary_pain_score'] == 0

    def test_detect_batch(self):
        """Test batch keyword detection."""
        comments = [
            {'text': 'I have anxiety'},
            {'text': 'Will Shambhavi help?'},
            {'text': 'Namaskaram'}
        ]

        result = self.detector.detect_batch(comments)

        assert len(result) == 3
        assert result[0]['keyword_detection']['has_mental_pain'] is True
        assert result[1]['keyword_detection']['practice_mentions'] == ['shambhavi']
        assert result[2]['keyword_detection']['preliminary_intent'] == 'low_intent'
