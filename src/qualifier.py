"""AI-powered lead qualification using OpenAI GPT-4o-mini."""

import json
from typing import Dict, List
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from src.config import settings
from src.utils import setup_logger

logger = setup_logger(__name__)


class LeadQualifier:
    """Qualifies leads using OpenAI's GPT-4o-mini model."""

    SYSTEM_PROMPT = """You are a lead qualification specialist for Inner Engineering programs offered by Isha Foundation (founded by Sadhguru).

Your task is to analyze YouTube comments and classify the commenter's intent to enroll in Inner Engineering programs.

Intent Criteria:

HIGH (80-100 confidence):
- Explicit questions about registration, enrollment, or how to join programs
- Direct requests for program details, dates, locations, or pricing
- Clear statements of intent to participate or learn specific practices
- Questions about program prerequisites or eligibility
- Requests for contact information or next steps
Examples: "How do I register for Inner Engineering?", "Where can I sign up?", "What are the program dates?"

MEDIUM (40-79 confidence):
- Strong spiritual interest and seeking guidance
- Thoughtful questions about meditation, yoga, or spiritual practices
- Expressions of life challenges that programs could address
- Positive engagement with Sadhguru's teachings
- Questions about specific practices or techniques
- Personal sharing showing readiness for transformation
Examples: "I want to learn meditation", "How can I find inner peace?", "This resonates with me deeply"

LOW (0-39 confidence):
- Generic praise or gratitude ("Thank you Sadhguru")
- Casual comments without depth
- Off-topic discussions
- Spam or promotional content
- Simple emoji reactions
- Questions unrelated to personal growth or programs
Examples: "Amazing!", "Love this", "First!", "Namaskaram"

Output Format:
Return ONLY valid JSON with this exact structure:
{
  "intent": "High" | "Medium" | "Low",
  "confidence": <number 0-100>,
  "reasoning": "<brief 1-2 sentence explanation>"
}

Be conservative with High ratings - only assign if there's clear enrollment intent.
Be generous with Medium ratings for genuine spiritual seekers.
"""

    def __init__(self):
        """Initialize OpenAI client."""
        self.client = OpenAI()


    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((Exception,)),
        reraise=True
    )
    def qualify_lead(self, comment: Dict) -> Dict:
        """
        Qualify a single lead using OpenAI.

        Args:
            comment: Comment dictionary with 'text' field

        Returns:
            Dictionary with intent, confidence, and reasoning
        """
        try:
            logger.info(f"Qualifying comment from {comment.get('author', 'Unknown')}")

            # Prepare the user message
            user_message = f"Comment: {comment['text']}"

            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": user_message}
                ],
                temperature=settings.openai_temperature,
                max_tokens=settings.openai_max_tokens,
                response_format={"type": "json_object"}
            )

            # Parse the response
            result = json.loads(response.choices[0].message.content)

            # Validate and normalize the response
            intent = result.get('intent', 'Low').capitalize()
            if intent not in ['High', 'Medium', 'Low']:
                logger.warning(f"Invalid intent '{intent}', defaulting to 'Low'")
                intent = 'Low'

            confidence = int(result.get('confidence', 0))
            confidence = max(0, min(100, confidence))  # Clamp to 0-100

            reasoning = result.get('reasoning', 'No reasoning provided')

            qualification = {
                'intent': intent,
                'confidence': confidence,
                'reasoning': reasoning
            }

            logger.info(f"Qualified as {intent} ({confidence}%)")
            return qualification

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse OpenAI response as JSON: {e}")
            return {
                'intent': 'Low',
                'confidence': 0,
                'reasoning': 'Error: Invalid JSON response from AI'
            }
        except Exception as e:
            logger.error(f"Error qualifying lead: {e}")
            # Return a low intent on error to avoid losing the lead
            return {
                'intent': 'Low',
                'confidence': 0,
                'reasoning': f'Error during qualification: {str(e)}'
            }

    def qualify_batch(self, comments: List[Dict]) -> List[Dict]:
        """
        Qualify multiple comments.

        Args:
            comments: List of comment dictionaries

        Returns:
            List of comments with qualification added
        """
        qualified_comments = []

        logger.info(f"Starting batch qualification of {len(comments)} comments")

        for i, comment in enumerate(comments, 1):
            logger.info(f"Processing comment {i}/{len(comments)}")

            qualification = self.qualify_lead(comment)

            # Merge qualification into comment
            qualified_comment = {**comment, **qualification}
            qualified_comments.append(qualified_comment)

        # Log summary statistics
        high_count = sum(1 for c in qualified_comments if c['intent'] == 'High')
        medium_count = sum(1 for c in qualified_comments if c['intent'] == 'Medium')
        low_count = sum(1 for c in qualified_comments if c['intent'] == 'Low')

        logger.info(f"Qualification complete: High={high_count}, Medium={medium_count}, Low={low_count}")

        return qualified_comments
