"""Unit tests for language detection utility."""

import pytest
from src.utils import detect_language


class TestLanguageDetection:
    """Test cases for language detection functionality."""

    def test_detect_english(self):
        """Test English language detection."""
        lang = detect_language("I have back pain and need help")
        assert lang == 'en'

        lang = detect_language("How do I register for the program?")
        assert lang == 'en'

    def test_detect_hindi(self):
        """Test Hindi language detection."""
        lang = detect_language("मुझे मदद चाहिए")
        assert lang == 'hi'

    def test_detect_marathi(self):
        """Test Marathi language detection."""
        lang = detect_language("मला मदत हवी आहे")
        assert lang == 'mr'

    def test_unsupported_language(self):
        """Test that unsupported languages return None."""
        # French
        lang = detect_language("J'ai besoin d'aide")
        assert lang is None

        # Spanish
        lang = detect_language("Necesito ayuda")
        assert lang is None

    def test_empty_text(self):
        """Test handling of empty text."""
        lang = detect_language("")
        assert lang is None

        lang = detect_language("   ")
        assert lang is None

    def test_very_short_text(self):
        """Test handling of very short text (may fail detection)."""
        lang = detect_language("Hi")
        # May return 'en' or None depending on langdetect behavior
        assert lang in ['en', None]
