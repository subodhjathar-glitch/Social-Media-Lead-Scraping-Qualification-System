"""Conversation tracking and management for auto-reply system."""

from typing import Dict, List, Optional
from datetime import datetime

from src.database import AirtableDatabase
from src.utils import setup_logger

logger = setup_logger(__name__)


class ConversationTracker:
    """Tracks and manages conversation threads with leads."""

    def __init__(self, database: AirtableDatabase):
        """Initialize conversation tracker."""
        self.database = database

    def should_create_thread(self, lead_data: Dict) -> bool:
        """
        Determine if a lead should start a conversation thread.

        Args:
            lead_data: Qualified lead dictionary

        Returns:
            True if thread should be created, False otherwise
        """
        # Criteria for starting a conversation:
        # 1. High readiness score (>= 60)
        # 2. Not low_intent type
        # 3. Has meaningful pain signal

        readiness = lead_data.get('readiness_score', 0)
        intent_type = lead_data.get('intent_type', 'low_intent')
        pain_intensity = lead_data.get('pain_intensity', 0)

        if intent_type == 'low_intent':
            return False

        if readiness >= 60 or pain_intensity >= 5:
            return True

        # Special case: practice_aligned always gets a thread
        if intent_type == 'practice_aligned':
            return True

        return False

    def create_thread_for_lead(self, lead_record: Dict) -> Optional[Dict]:
        """
        Create a conversation thread for a qualified lead.

        Args:
            lead_record: Airtable lead record

        Returns:
            Created thread record or None
        """
        lead_id = lead_record['id']
        lead_data = lead_record['fields']

        # Check if thread already exists
        existing_thread = self.database.get_thread_by_lead(lead_id)
        if existing_thread:
            logger.info(f"Thread already exists for lead {lead_id}")
            return existing_thread

        # Create new thread
        logger.info(f"Creating conversation thread for lead: {lead_data.get('Name', 'Unknown')}")
        thread = self.database.create_conversation_thread(lead_id, lead_data)

        return thread

    def update_thread_with_reply(self, thread_id: str, our_reply: str,
                                 their_response: Optional[str] = None) -> bool:
        """
        Update conversation thread after we reply or they respond.

        Args:
            thread_id: Thread record ID
            our_reply: Our reply text
            their_response: Their response text (if they replied back)

        Returns:
            True if updated successfully
        """
        try:
            thread = self.database.threads_table.get(thread_id)
            fields = thread['fields']

            current_stage = fields.get('Conversation Stage', 0)
            current_history = fields.get('Full History', '')

            # Update history
            new_stage = current_stage + 1
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')

            new_history = current_history + f"\n\n[Stage {new_stage} - Our Reply - {timestamp}]\nUs: {our_reply}"

            if their_response:
                new_history += f"\n\n[Stage {new_stage + 1} - Their Response - {timestamp}]\nThem: {their_response}"
                new_stage += 1

            updates = {
                'Conversation Stage': new_stage,
                'Full History': new_history,
                'Last Reply Date': datetime.now().strftime('%Y-%m-%d')
            }

            return self.database.update_conversation_thread(thread_id, updates)

        except Exception as e:
            logger.error(f"Error updating thread with reply: {e}")
            return False

    def mark_resource_shared(self, thread_id: str, resource_name: str) -> bool:
        """
        Mark that a resource was shared in this conversation.

        Args:
            thread_id: Thread record ID
            resource_name: Name of resource shared

        Returns:
            True if updated successfully
        """
        try:
            thread = self.database.threads_table.get(thread_id)
            fields = thread['fields']

            current_resources = fields.get('Resources Shared', '')
            if current_resources:
                updated_resources = f"{current_resources}, {resource_name}"
            else:
                updated_resources = resource_name

            updates = {'Resources Shared': updated_resources}
            return self.database.update_conversation_thread(thread_id, updates)

        except Exception as e:
            logger.error(f"Error marking resource shared: {e}")
            return False

    def update_readiness_score(self, thread_id: str, new_score: int) -> bool:
        """
        Update readiness score based on conversation progress.

        Args:
            thread_id: Thread record ID
            new_score: New readiness score (0-100)

        Returns:
            True if updated successfully
        """
        updates = {'Readiness Score': new_score}
        return self.database.update_conversation_thread(thread_id, updates)

    def close_thread(self, thread_id: str, reason: str = 'completed') -> bool:
        """
        Close a conversation thread.

        Args:
            thread_id: Thread record ID
            reason: Reason for closing (completed/no_response/converted)

        Returns:
            True if updated successfully
        """
        updates = {
            'Status': reason,
            'Last Reply Date': datetime.now().strftime('%Y-%m-%d')
        }
        return self.database.update_conversation_thread(thread_id, updates)

    def get_conversation_context(self, thread_id: str) -> Dict:
        """
        Get full conversation context for AI reply generation.

        Args:
            thread_id: Thread record ID

        Returns:
            Dictionary with conversation context
        """
        try:
            thread = self.database.threads_table.get(thread_id)
            fields = thread['fields']

            # Get linked lead data
            lead_links = fields.get('Lead', [])
            lead_data = {}
            if lead_links:
                lead_record = self.database.table.get(lead_links[0])
                lead_data = lead_record['fields']

            context = {
                'thread_id': thread_id,
                'lead_name': fields.get('Comment Author', 'Unknown'),
                'original_comment': fields.get('Original Comment', ''),
                'conversation_stage': fields.get('Conversation Stage', 0),
                'full_history': fields.get('Full History', ''),
                'pain_type': fields.get('Pain Type', 'unknown'),
                'readiness_score': fields.get('Readiness Score', 0),
                'resources_shared': fields.get('Resources Shared', '').split(', ') if fields.get('Resources Shared') else [],
                'comment_url': fields.get('Comment URL', ''),
                'video_url': fields.get('Video URL', ''),
                'ai_context_summary': fields.get('AI Context Summary', ''),
                'lead_data': lead_data
            }

            return context

        except Exception as e:
            logger.error(f"Error getting conversation context: {e}")
            return {}

    def process_qualified_leads(self, qualified_leads: List[Dict]) -> List[Dict]:
        """
        Process qualified leads and create threads for eligible ones.

        Args:
            qualified_leads: List of qualified lead records from Airtable

        Returns:
            List of created thread records
        """
        created_threads = []

        for lead_record in qualified_leads:
            lead_data = lead_record['fields']

            if self.should_create_thread(lead_data):
                thread = self.create_thread_for_lead(lead_record)
                if thread:
                    created_threads.append(thread)
                    logger.info(f"Created thread for {lead_data.get('Name', 'Unknown')} "
                               f"(readiness: {lead_data.get('Readiness Score', 0)}%)")

        logger.info(f"Created {len(created_threads)} conversation threads from {len(qualified_leads)} leads")
        return created_threads
