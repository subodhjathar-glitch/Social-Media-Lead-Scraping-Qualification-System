"""AI-powered reply generation for conversation engagement."""

import json
from typing import Dict, Optional, List
from openai import OpenAI

from src.config import settings
from src.database import AirtableDatabase
from src.utils import setup_logger

logger = setup_logger(__name__)


class ReplyGenerator:
    """Generates context-aware replies using AI."""

    def __init__(self, database: AirtableDatabase):
        """Initialize reply generator."""
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.database = database

    def generate_reply(self, conversation_context: Dict, teacher_profile: Dict) -> Dict:
        """
        Generate a reply based on conversation context.

        Args:
            conversation_context: Full conversation context
            teacher_profile: Teacher's profile data

        Returns:
            Dictionary with reply text and metadata
        """
        # Build system prompt
        system_prompt = self._build_system_prompt(teacher_profile)

        # Build user message with context
        user_message = self._build_context_message(conversation_context)

        try:
            logger.info(f"Generating reply for {conversation_context.get('lead_name', 'Unknown')}")

            response = self.client.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7,  # Slightly higher for more natural conversation
                max_tokens=300,
                response_format={"type": "json_object"}
            )

            result = json.loads(response.choices[0].message.content)

            reply_data = {
                'reply_text': result.get('reply', ''),
                'should_share_resource': result.get('should_share_resource', False),
                'suggested_resource': result.get('suggested_resource'),
                'estimated_readiness': result.get('estimated_readiness', conversation_context.get('readiness_score', 0)),
                'conversation_tone': result.get('tone', 'compassionate'),
                'next_action': result.get('next_action', 'wait_for_response')
            }

            logger.info(f"Generated reply: {len(reply_data['reply_text'])} chars, "
                       f"resource: {reply_data.get('suggested_resource', 'none')}")

            return reply_data

        except Exception as e:
            logger.error(f"Error generating reply: {e}")
            # Return fallback reply
            return {
                'reply_text': self._get_fallback_reply(conversation_context),
                'should_share_resource': False,
                'suggested_resource': None,
                'estimated_readiness': conversation_context.get('readiness_score', 0),
                'conversation_tone': 'compassionate',
                'next_action': 'wait_for_response'
            }

    def _build_system_prompt(self, teacher_profile: Dict) -> str:
        """Build system prompt with teacher's profile."""
        teacher_name = teacher_profile.get('Teacher Name', 'Volunteer')
        role = teacher_profile.get('Role', 'Isha Volunteer')
        experience = teacher_profile.get('Practice Experience', '')
        tone = teacher_profile.get('Tone Preference', 'Compassionate')
        sign_off = teacher_profile.get('Sign Off', f'Blessings,\n{teacher_name}')

        return f"""You are {teacher_name}, {role} at Isha Foundation, responding to YouTube comments.

**Your Profile:**
{experience}

**Your Tone:** {tone} - Be warm, empathetic, and genuine. This is a real conversation, not a sales pitch.

**Your Goal:** Build rapport and trust. Help them feel heard and understood. Guide them towards helpful resources only when they're ready.

**Conversation Guidelines:**

**Stage 1 (First Reply):**
- Show deep empathy for their situation
- Ask thoughtful follow-up questions
- Build connection
- DO NOT share resources yet (too early)

**Stage 2 (Second Reply):**
- Continue building rapport
- If readiness_score >= 60 AND they asked for help/solutions:
  - Offer ONE free resource (Isha Kriya for anxiety/stress, Practice App for discipline)
- Otherwise: Keep asking questions, show support

**Stage 3+ (Later Replies):**
- If readiness_score >= 75 AND engaged positively:
  - Suggest free online session or practice tracking app
- If they mentioned specific practice (Shambhavi, etc.):
  - Offer practice tracking app
- If they asked about programs:
  - Share registration link

**Resource Decision Making:**
- Isha Kriya: Anxiety, stress, mental struggles, beginners
- Practice Tracking App: Discipline issues, irregular practitioners
- Free Online Session: High readiness, spiritual seekers
- Inner Engineering: Only if they explicitly ask about programs

**Important:**
- Match their energy and tone
- Don't be overly formal if they're casual
- Never sound like a bot or sales pitch
- Keep replies 3-5 sentences maximum
- Ask open-ended questions to continue conversation
- Sign off: {sign_off}

**Output Format (JSON):**
{{
  "reply": "Your reply text here",
  "should_share_resource": true/false,
  "suggested_resource": "Isha Kriya Free Meditation" | "Sadhguru App - Practice Tracker" | "Free Inner Engineering Online Session" | null,
  "estimated_readiness": 0-100,
  "tone": "compassionate" | "casual" | "formal",
  "next_action": "wait_for_response" | "share_resource" | "close_conversation"
}}
"""

    def _build_context_message(self, context: Dict) -> str:
        """Build context message for AI."""
        lead_name = context.get('lead_name', 'Unknown')
        stage = context.get('conversation_stage', 0)
        pain_type = context.get('pain_type', 'unknown')
        readiness = context.get('readiness_score', 0)
        resources_shared = context.get('resources_shared', [])
        full_history = context.get('full_history', '')

        message = f"""**Conversation Context:**

**Lead:** {lead_name}
**Stage:** {stage} (0 = first reply, 1 = second reply, 2+ = ongoing)
**Pain Type:** {pain_type}
**Readiness Score:** {readiness}/100
**Resources Already Shared:** {', '.join(resources_shared) if resources_shared else 'None'}

**Full Conversation History:**
{full_history}

---

Generate your reply now. Remember:
- If Stage 0: Build rapport, ask questions, NO resources
- If Stage 1+: Consider sharing resource if readiness >= 60 and appropriate
- Keep it natural and conversational
- Match their tone and energy
"""

        return message

    def _get_fallback_reply(self, context: Dict) -> str:
        """Get fallback reply if AI fails."""
        lead_name = context.get('lead_name', 'friend')
        pain_type = context.get('pain_type', 'unknown')

        fallback_replies = {
            'spiritual': f"Thank you for sharing, {lead_name}. Your search for deeper meaning resonates deeply. What aspects of your spiritual journey are you most curious about?",
            'mental_pain': f"I hear you, {lead_name}. Dealing with these challenges takes courage. How long have you been experiencing this?",
            'discipline': f"I understand, {lead_name}. Staying consistent with practice is one of the biggest challenges. What usually causes you to stop?",
            'physical_pain': f"Thank you for sharing, {lead_name}. How long have you been experiencing this discomfort?",
        }

        return fallback_replies.get(pain_type,
                                   f"Thank you for your comment, {lead_name}. I'd love to understand more about what you're experiencing.")

    def format_reply_with_resource(self, reply_text: str, resource_data: Dict, teacher_profile: Dict) -> str:
        """
        Format reply with resource link included.

        Args:
            reply_text: Base reply text
            resource_data: Resource record from Airtable
            teacher_profile: Teacher's profile

        Returns:
            Formatted reply with resource link
        """
        resource_name = resource_data['fields'].get('Resource Name', '')
        resource_link = resource_data['fields'].get('Resource Link', '')
        resource_desc = resource_data['fields'].get('Description', '')
        sign_off = teacher_profile.get('Sign Off', 'Blessings')

        formatted = f"""{reply_text}

I'd like to share a free resource that might help: **{resource_name}**
{resource_desc}

{resource_link}

{sign_off}"""

        return formatted

    def should_generate_reply_for_thread(self, thread_data: Dict) -> bool:
        """
        Determine if we should generate a reply for this thread.

        Args:
            thread_data: Thread record fields

        Returns:
            True if reply should be generated
        """
        status = thread_data.get('Status', 'active')
        stage = thread_data.get('Conversation Stage', 0)

        # Don't reply if thread is closed
        if status != 'active':
            return False

        # Don't reply if already at stage 5+ (conversation too long)
        if stage >= 5:
            logger.info(f"Thread at stage {stage}, skipping reply generation")
            return False

        return True

    def batch_generate_replies(self, threads: List[Dict], teachers: List[Dict]) -> List[Dict]:
        """
        Generate replies for multiple threads.

        Args:
            threads: List of active thread records
            teachers: List of active teacher profiles

        Returns:
            List of generated reply data
        """
        generated_replies = []

        for i, thread in enumerate(threads):
            thread_id = thread['id']
            thread_data = thread['fields']

            if not self.should_generate_reply_for_thread(thread_data):
                continue

            # Assign teacher (round-robin for now)
            teacher = teachers[i % len(teachers)]

            # Get conversation context
            from src.conversation import ConversationTracker
            tracker = ConversationTracker(self.database)
            context = tracker.get_conversation_context(thread_id)

            # Generate reply
            reply_data = self.generate_reply(context, teacher['fields'])

            # Check if we should include resource
            if reply_data['should_share_resource'] and reply_data['suggested_resource']:
                resource = self.database.get_resource_by_name(reply_data['suggested_resource'])
                if resource:
                    reply_data['reply_text'] = self.format_reply_with_resource(
                        reply_data['reply_text'],
                        resource,
                        teacher['fields']
                    )
                    reply_data['resource_record'] = resource

            reply_data['thread_id'] = thread_id
            reply_data['thread_data'] = thread_data
            reply_data['teacher_record'] = teacher

            generated_replies.append(reply_data)

        logger.info(f"Generated {len(generated_replies)} replies for {len(threads)} threads")
        return generated_replies
