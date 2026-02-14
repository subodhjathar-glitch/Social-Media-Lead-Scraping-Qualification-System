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

    SYSTEM_PROMPT = """You are a pain-based lead qualification specialist for Isha Foundation's transformation programs.

Analyze YouTube comments to identify people experiencing challenges that Isha practices address.

## PAIN SIGNAL CATEGORIES (PRIORITY ORDER)

**SPIRITUAL LONGING** (HIGHEST PRIORITY - Isha's core focus)
Keywords: purpose, transformation, awakening, meaning, lost, empty, disconnected, seeking, enlightenment, self-realization
Example: "I feel something is missing in life", "What is my purpose?", "Feeling spiritually disconnected"
**Scoring:** Automatically boost readiness_score by +20 for spiritual signals

**MENTAL/EMOTIONAL PAIN** (HIGH PRIORITY)
Keywords: anxiety, depression, stress, confusion, anger, overthinking, restless mind, mental chaos
Example: "I'm struggling with anxiety", "My mind is always racing", "Feeling emotionally lost"
**Scoring:** Significant readiness indicator

**DISCIPLINE** (MEDIUM-HIGH PRIORITY - Re-engagement opportunity)
Keywords: quit, stopped practicing, can't stay consistent, lost motivation, irregular
Example: "I learned Shambhavi but stopped", "How to stay disciplined?"
**Scoring:** HIGH VALUE for practice tracking and community engagement

**PHYSICAL PAIN** (LOWER PRIORITY - Not primary focus)
Keywords: back pain, knee pain, stiffness, fatigue, posture
Example: "I have back pain", "My knee hurts"
**Scoring:** Acknowledge but lower in priority queue

**PRACTICE ALIGNMENT** (Mentions practices - CRITICAL)
Practices: Angamardana, Surya Kriya, Shambhavi, Yogasanas, Sadhguru, Isha
Example: "Will Shambhavi help my anxiety?" → TOP LEAD

## SCORING

**pain_intensity (0-10):**
- 0-3: Mild curiosity
- 4-6: Clear struggle
- 7-8: Significant pain
- 9-10: Critical pain

**readiness_score (0-100):**
- 0-30: Passive observer
- 31-60: Curious
- 61-85: Ready to try
- 86-100: Highly motivated

## OUTPUT FORMAT

Return ONLY valid JSON:
{
  "intent_type": "physical_pain" | "mental_pain" | "discipline" | "spiritual" | "practice_aligned" | "low_intent",
  "pain_intensity": 0-10,
  "readiness_score": 0-100,
  "practice_mention": "practice_name" or null,
  "confidence": 0-100,
  "reasoning": "1-2 sentence explanation"
}

## EXAMPLES

"I have severe back pain. Can yoga help?" →
{
  "intent_type": "physical_pain",
  "pain_intensity": 8,
  "readiness_score": 70,
  "practice_mention": null,
  "confidence": 90,
  "reasoning": "Clear physical pain (severe back) with openness to yoga solution."
}

"I learned Shambhavi but stopped for 6 months. How to restart?" →
{
  "intent_type": "discipline",
  "pain_intensity": 6,
  "readiness_score": 80,
  "practice_mention": "Shambhavi",
  "confidence": 95,
  "reasoning": "Past practitioner struggling with consistency - high value for re-engagement."
}

"Namaskaram 🙏" →
{
  "intent_type": "low_intent",
  "pain_intensity": 0,
  "readiness_score": 10,
  "practice_mention": null,
  "confidence": 100,
  "reasoning": "Generic greeting with no transformation intent."
}
"""

    def __init__(self):
        """Initialize OpenAI client."""
        self.client = OpenAI(api_key=settings.openai_api_key)

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
            comment: Comment dictionary with 'text' field and optional 'keyword_detection' field

        Returns:
            Dictionary with intent_type, pain_intensity, readiness_score, practice_mention, confidence, and reasoning
        """
        try:
            logger.info(f"Qualifying comment from {comment.get('author', 'Unknown')}")

            # Prepare the user message with keyword context
            user_message = f"Comment: {comment['text']}"

            # Add keyword detection context if available
            if 'keyword_detection' in comment:
                kw = comment['keyword_detection']
                context_parts = []

                if kw.get('keywords_found'):
                    context_parts.append(f"Keywords detected: {', '.join(kw['keywords_found'][:5])}")
                if kw.get('practice_mentions'):
                    context_parts.append(f"Practices mentioned: {', '.join(kw['practice_mentions'])}")
                if kw.get('preliminary_pain_score', 0) > 0:
                    context_parts.append(f"Preliminary pain score: {kw['preliminary_pain_score']}/10")

                if context_parts:
                    user_message += f"\n\nContext: {'; '.join(context_parts)}"

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
            intent_type = result.get('intent_type', 'low_intent')
            valid_intents = ['physical_pain', 'mental_pain', 'discipline', 'spiritual', 'practice_aligned', 'low_intent']
            if intent_type not in valid_intents:
                logger.warning(f"Invalid intent_type '{intent_type}', defaulting to 'low_intent'")
                intent_type = 'low_intent'

            pain_intensity = int(result.get('pain_intensity', 0))
            pain_intensity = max(0, min(10, pain_intensity))  # Clamp to 0-10

            readiness_score = int(result.get('readiness_score', 0))
            readiness_score = max(0, min(100, readiness_score))  # Clamp to 0-100

            practice_mention = result.get('practice_mention')
            if practice_mention and not isinstance(practice_mention, str):
                practice_mention = str(practice_mention) if practice_mention else None

            confidence = int(result.get('confidence', 0))
            confidence = max(0, min(100, confidence))  # Clamp to 0-100

            reasoning = result.get('reasoning', 'No reasoning provided')

            qualification = {
                'intent_type': intent_type,
                'pain_intensity': pain_intensity,
                'readiness_score': readiness_score,
                'practice_mention': practice_mention,
                'confidence': confidence,
                'reasoning': reasoning
            }

            # Map intent_type to legacy 'intent' field for backward compatibility
            legacy_intent = self._map_to_legacy_intent(intent_type, readiness_score)
            qualification['intent'] = legacy_intent

            logger.info(f"Qualified as {intent_type} (pain: {pain_intensity}/10, readiness: {readiness_score}%)")
            return qualification

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse OpenAI response as JSON: {e}")
            return self._error_result('Error: Invalid JSON response from AI')
        except Exception as e:
            logger.error(f"Error qualifying lead: {e}")
            return self._error_result(f'Error during qualification: {str(e)}')

    def _map_to_legacy_intent(self, intent_type: str, readiness_score: int) -> str:
        """Map new intent_type to legacy High/Medium/Low format for backward compatibility."""
        if intent_type == 'practice_aligned' or (intent_type == 'spiritual' and readiness_score >= 70):
            return 'High'
        elif intent_type in ['spiritual', 'mental_pain', 'discipline'] or readiness_score >= 50:
            return 'Medium'
        else:
            return 'Low'

    def _error_result(self, error_msg: str) -> Dict:
        """Return error result with new format."""
        return {
            'intent_type': 'low_intent',
            'pain_intensity': 0,
            'readiness_score': 0,
            'practice_mention': None,
            'confidence': 0,
            'reasoning': error_msg,
            'intent': 'Low'  # Legacy field
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

        # New format statistics
        spiritual_count = sum(1 for c in qualified_comments if c.get('intent_type') == 'spiritual')
        mental_count = sum(1 for c in qualified_comments if c.get('intent_type') == 'mental_pain')
        discipline_count = sum(1 for c in qualified_comments if c.get('intent_type') == 'discipline')
        practice_count = sum(1 for c in qualified_comments if c.get('intent_type') == 'practice_aligned')

        logger.info(f"Qualification complete: High={high_count}, Medium={medium_count}, Low={low_count}")
        logger.info(f"  By type: Spiritual={spiritual_count}, Mental={mental_count}, Discipline={discipline_count}, Practice-aligned={practice_count}")

        return qualified_comments
