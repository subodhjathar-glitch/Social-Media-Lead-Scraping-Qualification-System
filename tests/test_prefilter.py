"""Unit tests for the CommentPreFilter class."""

import pytest
from src.prefilter import CommentPreFilter


class TestCommentPreFilter:
    """Test cases for pre-filter functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.prefilter = CommentPreFilter()

    def test_should_skip_empty_comment(self):
        """Test that empty comments are skipped."""
        should_skip, reason = self.prefilter.should_skip("")
        assert should_skip is True
        assert reason == "empty"

        should_skip, reason = self.prefilter.should_skip("   ")
        assert should_skip is True
        assert reason == "empty"

    def test_should_skip_too_short(self):
        """Test that comments with < 4 words are skipped."""
        should_skip, reason = self.prefilter.should_skip("Great video")
        assert should_skip is True
        assert reason == "too_short"

        should_skip, reason = self.prefilter.should_skip("Amazing")
        assert should_skip is True
        assert reason == "too_short"

    def test_should_skip_emoji_only(self):
        """Test that emoji-only comments are skipped."""
        should_skip, reason = self.prefilter.should_skip("🙏🔥❤️")
        assert should_skip is True
        assert reason == "emoji_only"

        should_skip, reason = self.prefilter.should_skip("😊 😊 😊")
        assert should_skip is True
        assert reason == "emoji_only"

    def test_should_skip_praise_only(self):
        """Test that praise-only comments are skipped."""
        should_skip, reason = self.prefilter.should_skip("Namaskaram Sadhguru")
        assert should_skip is True
        assert reason == "praise_only"

        should_skip, reason = self.prefilter.should_skip("Amazing video thank you")
        assert should_skip is True
        assert reason == "praise_only"

        should_skip, reason = self.prefilter.should_skip("Love this so much")
        assert should_skip is True
        assert reason == "praise_only"

    def test_should_pass_meaningful_comment(self):
        """Test that meaningful comments pass the filter."""
        should_skip, reason = self.prefilter.should_skip("I have back pain. Can yoga help?")
        assert should_skip is False
        assert reason == "passed"

        should_skip, reason = self.prefilter.should_skip("How do I register for Inner Engineering?")
        assert should_skip is False
        assert reason == "passed"

        should_skip, reason = self.prefilter.should_skip("I'm struggling with anxiety and need help")
        assert should_skip is False
        assert reason == "passed"

    def test_should_pass_question_with_question_mark(self):
        """Test that questions are passed even without action verbs."""
        should_skip, reason = self.prefilter.should_skip("What is this program about?")
        assert should_skip is False
        assert reason == "passed"

    def test_should_pass_pain_keywords(self):
        """Test that comments with pain keywords pass the filter."""
        should_skip, reason = self.prefilter.should_skip("Amazing but I have pain")
        assert should_skip is False
        assert reason == "passed"

        should_skip, reason = self.prefilter.should_skip("Love this video anxiety is difficult")
        assert should_skip is False
        assert reason == "passed"

    def test_has_meaningful_verb(self):
        """Test meaningful verb detection."""
        assert self.prefilter._has_meaningful_verb("i want to learn meditation") is True
        assert self.prefilter._has_meaningful_verb("how can i help myself") is True
        assert self.prefilter._has_meaningful_verb("i am struggling with anxiety") is True
        assert self.prefilter._has_meaningful_verb("amazing beautiful video") is False

    def test_is_praise_only(self):
        """Test praise-only detection."""
        assert self.prefilter._is_praise_only("namaskaram sadhguru") is True
        assert self.prefilter._is_praise_only("amazing love this") is True
        assert self.prefilter._is_praise_only("watching from india") is True
        assert self.prefilter._is_praise_only("i want to learn") is False

    def test_filter_batch(self):
        """Test batch filtering."""
        comments = [
            {'text': 'Namaskaram 🙏'},
            {'text': 'I have back pain. Can yoga help?'},
            {'text': '😊😊😊'},
            {'text': 'Amazing'},
            {'text': 'How do I register for Inner Engineering?'}
        ]

        filtered, stats = self.prefilter.filter_batch(comments)

        assert stats['total'] == 5
        assert stats['passed'] == 2
        assert len(filtered) == 2
        assert filtered[0]['text'] == 'I have back pain. Can yoga help?'
        assert filtered[1]['text'] == 'How do I register for Inner Engineering?'

    def test_filter_batch_tracks_reasons(self):
        """Test that filter batch tracks skip reasons correctly."""
        comments = [
            {'text': ''},
            {'text': 'Short'},
            {'text': '🙏🙏🙏'},
            {'text': 'Namaskaram Sadhguru beautiful video'},
            {'text': 'I need help with anxiety and stress'}
        ]

        filtered, stats = self.prefilter.filter_batch(comments)

        assert stats['skipped_empty'] >= 1
        assert stats['skipped_too_short'] >= 1
        assert stats['skipped_emoji_only'] >= 1
        assert stats['skipped_praise_only'] >= 1
        assert stats['passed'] == 1
