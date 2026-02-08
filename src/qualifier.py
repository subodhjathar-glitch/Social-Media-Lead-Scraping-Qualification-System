"""
AI-powered lead qualification using OpenAI GPT-4o-mini
"""

import json
from typing import Dict, List
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from src.config import settings
from src.utils import setup_logger

logger = setup_logger(__name__)


class LeadQualifier:
    """Qualifies leads using OpenAI's GPT-4o-mini model."""

    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key)

    def qualify(self, comment: str) -> Dict[str, str]:
        return {
            "intent": "unknown",
            "confidence": 0
        }
