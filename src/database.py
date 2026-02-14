"""Supabase database operations for lead storage and management."""

from datetime import datetime, timedelta
from typing import List, Dict, Optional
from supabase import create_client, Client
from tenacity import retry, stop_after_attempt, wait_exponential

from src.config import settings
from src.utils import setup_logger, generate_lead_hash

logger = setup_logger(__name__)


class SupabaseDatabase:
    """Manages lead storage and operations in Supabase (PostgreSQL)."""

    def __init__(self):
        """Initialize Supabase client with fallback for network issues."""
        self.client: Optional[Client] = None
        self.is_available = False

        try:
            url = (settings.supabase_url or "").strip().rstrip("/")
            key = (settings.supabase_key or "").strip()

            if not url or not key or "your_" in url or "your_" in key or "supabase.co" not in url:
                logger.warning(
                    "Supabase credentials not configured. System will work in offline mode. "
                    "To enable Supabase: Set SUPABASE_URL and SUPABASE_KEY in .env"
                )
                self.is_available = False
                return

            # Test connection with timeout
            self.client = create_client(url, key)

            # Simple connectivity test
            try:
                # Try a simple query with timeout
                import socket
                socket.setdefaulttimeout(5)
                self.client.table('leads').select('id').limit(1).execute()
                self.is_available = True
                logger.info("✓ Supabase client initialized and connected successfully")
            except Exception as conn_error:
                logger.warning(
                    f"Supabase configured but unreachable: {conn_error}. "
                    f"System will work in offline mode. Data will be saved locally."
                )
                self.is_available = False
                self.client = None

        except ValueError as ve:
            logger.warning(f"Supabase configuration issue: {ve}")
            self.is_available = False
        except Exception as e:
            logger.warning(
                f"Could not initialize Supabase: {e}. "
                f"System will work in offline mode."
            )
            self.is_available = False
            self.client = None

    # ===== LEADS METHODS =====

    def check_duplicate(self, lead_hash: str) -> bool:
        """
        Check if a lead with this hash already exists.

        Args:
            lead_hash: SHA-256 hash of the lead

        Returns:
            True if duplicate exists, False otherwise
        """
        if not self.is_available or not self.client:
            # In offline mode, assume no duplicates
            return False

        try:
            response = self.client.table('leads').select('id').eq('lead_hash', lead_hash).execute()

            if response.data:
                logger.info(f"Duplicate found for hash: {lead_hash}")
                return True
            return False

        except Exception as e:
            logger.warning(f"Error checking duplicate (Supabase unavailable): {e}")
            return False

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    def create_lead(self, lead_data: Dict) -> Optional[Dict]:
        """
        Create a single lead in Supabase.

        Args:
            lead_data: Lead dictionary with all required fields

        Returns:
            Created record or None on failure
        """
        try:
            # Map lead data to database fields
            data = {
                'name': lead_data.get('author', 'Unknown'),
                'platform': 'YouTube',
                'comment': lead_data.get('text', ''),
                'video_url': lead_data.get('video_url', ''),
                'comment_url': lead_data.get('comment_url', ''),
                'intent': lead_data.get('intent', 'Low'),
                'confidence': lead_data.get('confidence', 0),
                'ai_reasoning': lead_data.get('reasoning', ''),
                'intent_type': lead_data.get('intent_type', 'low_intent'),
                'pain_intensity': lead_data.get('pain_intensity', 0),
                'readiness_score': lead_data.get('readiness_score', 0),
                'practice_mention': lead_data.get('practice_mention'),
                'language': lead_data.get('language'),
                'prefilter_status': lead_data.get('prefilter_status', 'unknown'),
                'lead_hash': lead_data.get('hash', ''),
                'scraped_date': datetime.now().strftime('%Y-%m-%d')
            }

            response = self.client.table('leads').insert(data).execute()

            if response.data:
                logger.info(f"Created lead: {data['name']} ({data['intent']})")
                return response.data[0]
            return None

        except Exception as e:
            logger.error(f"Error creating lead: {e}")
            return None

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    def batch_create_leads(self, leads: List[Dict]) -> List[Dict]:
        """
        Create multiple leads in Supabase (batch operation).
        Falls back to local JSON storage if Supabase is unavailable.

        Args:
            leads: List of lead dictionaries

        Returns:
            List of created records
        """
        if not leads:
            return []

        # If Supabase is not available, save locally
        if not self.is_available or not self.client:
            return self._save_leads_locally(leads)

        created_records = []

        # Process in batches (Supabase can handle larger batches than Airtable)
        batch_size = 100
        for i in range(0, len(leads), batch_size):
            batch = leads[i:i + batch_size]

            try:
                # Map each lead to database fields
                data_list = []
                for lead in batch:
                    data = {
                        'name': lead.get('author', 'Unknown'),
                        'platform': 'YouTube',
                        'comment': lead.get('text', ''),
                        'video_url': lead.get('video_url', ''),
                        'comment_url': lead.get('comment_url', ''),
                        'intent': lead.get('intent', 'Low'),
                        'confidence': lead.get('confidence', 0),
                        'ai_reasoning': lead.get('reasoning', ''),
                        'intent_type': lead.get('intent_type', 'low_intent'),
                        'pain_intensity': lead.get('pain_intensity', 0),
                        'readiness_score': lead.get('readiness_score', 0),
                        'practice_mention': lead.get('practice_mention'),
                        'language': lead.get('language'),
                        'prefilter_status': lead.get('prefilter_status', 'unknown'),
                        'lead_hash': lead.get('hash', ''),
                        'scraped_date': datetime.now().strftime('%Y-%m-%d')
                    }
                    data_list.append(data)

                # Batch insert
                response = self.client.table('leads').insert(data_list).execute()

                if response.data:
                    created_records.extend(response.data)
                    logger.info(f"Created batch of {len(response.data)} leads in Supabase")

            except Exception as e:
                logger.warning(f"Supabase batch insert failed: {e}. Saving locally instead.")
                # Save this batch locally
                self._save_leads_locally(batch)

        if not created_records and leads:
            # All batches failed, save everything locally
            logger.warning("All Supabase operations failed. Saving all leads locally.")
            return self._save_leads_locally(leads)

        logger.info(f"Total leads created in Supabase: {len(created_records)}")
        return created_records

    def _save_leads_locally(self, leads: List[Dict]) -> List[Dict]:
        """Save leads to local JSON file as fallback."""
        import json
        import os
        from pathlib import Path

        try:
            # Create data directory if it doesn't exist
            data_dir = Path("data")
            data_dir.mkdir(exist_ok=True)

            # Generate filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = data_dir / f"leads_offline_{timestamp}.json"

            # Prepare data for saving
            data_to_save = []
            for lead in leads:
                data = {
                    'name': lead.get('author', 'Unknown'),
                    'platform': 'YouTube',
                    'comment': lead.get('text', ''),
                    'video_url': lead.get('video_url', ''),
                    'comment_url': lead.get('comment_url', ''),
                    'intent': lead.get('intent', 'Low'),
                    'confidence': lead.get('confidence', 0),
                    'ai_reasoning': lead.get('reasoning', ''),
                    'intent_type': lead.get('intent_type', 'low_intent'),
                    'pain_intensity': lead.get('pain_intensity', 0),
                    'readiness_score': lead.get('readiness_score', 0),
                    'practice_mention': lead.get('practice_mention'),
                    'language': lead.get('language'),
                    'prefilter_status': lead.get('prefilter_status', 'unknown'),
                    'lead_hash': lead.get('hash', ''),
                    'scraped_date': datetime.now().strftime('%Y-%m-%d'),
                    'saved_at': datetime.now().isoformat()
                }
                data_to_save.append(data)

            # Save to JSON file
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data_to_save, f, indent=2, ensure_ascii=False)

            logger.info(f"✓ Saved {len(leads)} leads locally to: {filename}")
            logger.info(f"  When Supabase is available, you can import this file")

            return data_to_save

        except Exception as e:
            logger.error(f"Error saving leads locally: {e}")
            return []

    def get_recent_leads(self, hours: int = 24) -> List[Dict]:
        """
        Get leads created in the last N hours.

        Args:
            hours: Number of hours to look back

        Returns:
            List of lead records
        """
        if not self.is_available or not self.client:
            logger.info("Supabase unavailable. Cannot fetch recent leads.")
            return []

        try:
            cutoff_date = (datetime.now() - timedelta(hours=hours)).strftime('%Y-%m-%d')

            response = self.client.table('leads')\
                .select('*')\
                .gte('scraped_date', cutoff_date)\
                .order('created_at', desc=True)\
                .execute()

            logger.info(f"Found {len(response.data)} leads from last {hours} hours")
            return response.data

        except Exception as e:
            logger.warning(f"Error fetching recent leads (Supabase unavailable): {e}")
            return []

    def process_comments(self, comments: List[Dict]) -> tuple[List[Dict], List[Dict]]:
        """
        Process comments: check for duplicates and add hash.

        Args:
            comments: List of qualified comment dictionaries

        Returns:
            Tuple of (unique_comments, duplicate_comments)
        """
        unique_comments = []
        duplicate_comments = []

        logger.info(f"Processing {len(comments)} comments for duplicates")

        for comment in comments:
            # Generate hash
            lead_hash = generate_lead_hash(
                comment.get('author', ''),
                'youtube',
                comment.get('text', '')
            )
            comment['hash'] = lead_hash

            # Check if duplicate
            if self.check_duplicate(lead_hash):
                duplicate_comments.append(comment)
            else:
                unique_comments.append(comment)

        logger.info(f"Unique: {len(unique_comments)}, Duplicates: {len(duplicate_comments)}")
        return unique_comments, duplicate_comments

    # ===== TEACHER PROFILES METHODS =====

    def get_active_teachers(self) -> List[Dict]:
        """Get all active teachers for reply assignment."""
        try:
            response = self.client.table('teacher_profiles')\
                .select('*')\
                .eq('active', True)\
                .execute()

            logger.info(f"Found {len(response.data)} active teachers")
            return response.data
        except Exception as e:
            logger.error(f"Error fetching active teachers: {e}")
            return []

    def get_teacher_by_email(self, email: str) -> Optional[Dict]:
        """Get teacher profile by email."""
        try:
            response = self.client.table('teacher_profiles')\
                .select('*')\
                .eq('email', email)\
                .execute()

            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error fetching teacher by email: {e}")
            return None

    # ===== CONVERSATION THREADS METHODS =====

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    def create_conversation_thread(self, lead_id: str, lead_data: Dict) -> Optional[Dict]:
        """
        Create a new conversation thread.

        Args:
            lead_id: UUID of the lead
            lead_data: Lead data dictionary

        Returns:
            Created thread record or None
        """
        try:
            data = {
                'lead_id': lead_id,
                'comment_author': lead_data.get('name', lead_data.get('author', 'Unknown')),
                'original_comment': lead_data.get('comment', lead_data.get('text', '')),
                'comment_url': lead_data.get('comment_url', ''),
                'video_url': lead_data.get('video_url', ''),
                'conversation_stage': 0,
                'full_history': f"[Stage 0 - Original Comment]\n{lead_data.get('name', 'Unknown')}: {lead_data.get('comment', lead_data.get('text', ''))}",
                'ai_context_summary': f"Lead expressed {lead_data.get('intent_type', 'interest')}. Pain intensity: {lead_data.get('pain_intensity', 0)}/10",
                'status': 'active',
                'pain_type': lead_data.get('intent_type', 'low_intent'),
                'readiness_score': lead_data.get('readiness_score', 0),
                'resources_shared': ''
            }

            response = self.client.table('conversation_threads').insert(data).execute()

            if response.data:
                logger.info(f"Created conversation thread for {lead_data.get('name', 'Unknown')}")
                return response.data[0]
            return None

        except Exception as e:
            logger.error(f"Error creating conversation thread: {e}")
            return None

    def get_thread_by_lead(self, lead_id: str) -> Optional[Dict]:
        """Get conversation thread by lead ID."""
        try:
            response = self.client.table('conversation_threads')\
                .select('*')\
                .eq('lead_id', lead_id)\
                .execute()

            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error fetching thread by lead: {e}")
            return None

    def update_conversation_thread(self, thread_id: str, updates: Dict) -> bool:
        """Update conversation thread fields."""
        try:
            response = self.client.table('conversation_threads')\
                .update(updates)\
                .eq('id', thread_id)\
                .execute()

            logger.info(f"Updated conversation thread {thread_id}")
            return True
        except Exception as e:
            logger.error(f"Error updating conversation thread: {e}")
            return False

    def get_active_threads(self) -> List[Dict]:
        """Get all active conversation threads."""
        try:
            response = self.client.table('conversation_threads')\
                .select('*')\
                .eq('status', 'active')\
                .execute()

            logger.info(f"Found {len(response.data)} active threads")
            return response.data
        except Exception as e:
            logger.error(f"Error fetching active threads: {e}")
            return []

    def get_thread_by_id(self, thread_id: str) -> Optional[Dict]:
        """Get thread by ID."""
        try:
            response = self.client.table('conversation_threads')\
                .select('*')\
                .eq('id', thread_id)\
                .single()\
                .execute()

            return response.data
        except Exception as e:
            logger.error(f"Error fetching thread: {e}")
            return None

    # ===== PENDING REPLIES METHODS =====

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    def create_pending_reply(self, thread_id: str, thread_data: Dict,
                            generated_reply: str, teacher_id: str) -> Optional[Dict]:
        """
        Create a pending reply for teacher approval.

        Args:
            thread_id: UUID of the thread
            thread_data: Thread data dictionary
            generated_reply: AI-generated reply text
            teacher_id: Assigned teacher's UUID

        Returns:
            Created reply record or None
        """
        try:
            data = {
                'thread_id': thread_id,
                'lead_name': thread_data.get('comment_author', 'Unknown'),
                'their_last_message': thread_data.get('original_comment', ''),
                'ai_generated_reply': generated_reply,
                'approval_status': 'pending',
                'assigned_teacher_id': teacher_id,
                'generated_at': datetime.now().isoformat()
            }

            response = self.client.table('pending_replies').insert(data).execute()

            if response.data:
                logger.info(f"Created pending reply for thread {thread_id}")
                return response.data[0]
            return None

        except Exception as e:
            logger.error(f"Error creating pending reply: {e}")
            return None

    def get_pending_replies(self, teacher_email: Optional[str] = None) -> List[Dict]:
        """Get pending replies, optionally filtered by teacher."""
        try:
            query = self.client.table('pending_replies')\
                .select('*')\
                .eq('approval_status', 'pending')

            response = query.execute()

            logger.info(f"Found {len(response.data)} pending replies")
            return response.data
        except Exception as e:
            logger.error(f"Error fetching pending replies: {e}")
            return []

    def update_pending_reply(self, reply_id: str, updates: Dict) -> bool:
        """Update pending reply fields."""
        try:
            response = self.client.table('pending_replies')\
                .update(updates)\
                .eq('id', reply_id)\
                .execute()

            logger.info(f"Updated pending reply {reply_id}")
            return True
        except Exception as e:
            logger.error(f"Error updating pending reply: {e}")
            return False

    def get_approved_replies(self) -> List[Dict]:
        """Get all approved replies ready to post."""
        try:
            response = self.client.table('pending_replies')\
                .select('*')\
                .eq('approval_status', 'approved')\
                .execute()

            logger.info(f"Found {len(response.data)} approved replies")
            return response.data
        except Exception as e:
            logger.error(f"Error fetching approved replies: {e}")
            return []

    # ===== RESOURCES METHODS =====

    def get_active_resources(self) -> List[Dict]:
        """Get all active resources."""
        try:
            response = self.client.table('resources')\
                .select('*')\
                .eq('active', True)\
                .execute()

            logger.info(f"Found {len(response.data)} active resources")
            return response.data
        except Exception as e:
            logger.error(f"Error fetching active resources: {e}")
            return []

    def get_resource_by_name(self, resource_name: str) -> Optional[Dict]:
        """Get resource by name."""
        try:
            response = self.client.table('resources')\
                .select('*')\
                .eq('resource_name', resource_name)\
                .execute()

            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error fetching resource by name: {e}")
            return None

    def get_resources_for_pain_type(self, pain_type: str, readiness_score: int) -> List[Dict]:
        """
        Get appropriate resources based on pain type and readiness score.

        Args:
            pain_type: Type of pain (spiritual, mental_pain, etc.)
            readiness_score: Lead's readiness score (0-100)

        Returns:
            List of matching resources
        """
        try:
            response = self.client.table('resources')\
                .select('*')\
                .eq('active', True)\
                .contains('pain_types', [pain_type])\
                .lte('minimum_readiness_score', readiness_score)\
                .execute()

            # Also get resources with 'general' pain type
            general_response = self.client.table('resources')\
                .select('*')\
                .eq('active', True)\
                .contains('pain_types', ['general'])\
                .lte('minimum_readiness_score', readiness_score)\
                .execute()

            matching = response.data + general_response.data

            logger.info(f"Found {len(matching)} matching resources for {pain_type}")
            return matching

        except Exception as e:
            logger.error(f"Error fetching resources for pain type: {e}")
            return []

    def increment_resource_share_count(self, resource_id: str) -> bool:
        """Increment the times shared counter for a resource."""
        try:
            # Get current count
            response = self.client.table('resources')\
                .select('times_shared')\
                .eq('id', resource_id)\
                .single()\
                .execute()

            if response.data:
                current_count = response.data.get('times_shared', 0)
                # Update count
                self.client.table('resources')\
                    .update({'times_shared': current_count + 1})\
                    .eq('id', resource_id)\
                    .execute()
                return True
            return False
        except Exception as e:
            logger.error(f"Error incrementing resource share count: {e}")
            return False


# Alias for backward compatibility
AirtableDatabase = SupabaseDatabase
