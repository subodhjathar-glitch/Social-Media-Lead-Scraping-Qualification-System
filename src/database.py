"""Airtable database operations for lead storage."""

from datetime import datetime, timedelta
from typing import List, Dict, Optional
from pyairtable import Api
from pyairtable.formulas import match
from tenacity import retry, stop_after_attempt, wait_exponential

from src.config import settings
from src.utils import setup_logger, generate_lead_hash

logger = setup_logger(__name__)


class AirtableDatabase:
    """Manages lead storage in Airtable."""

    def __init__(self):
        """Initialize Airtable API client."""
        self.api = Api(settings.airtable_token)
        self.table = self.api.table(
            settings.airtable_base_id,
            settings.airtable_table_name
        )

    def check_duplicate(self, lead_hash: str) -> bool:
        """
        Check if a lead with this hash already exists.

        Args:
            lead_hash: SHA-256 hash of the lead

        Returns:
            True if duplicate exists, False otherwise
        """
        try:
            formula = match({"Lead Hash": lead_hash})
            records = self.table.all(formula=formula)

            if records:
                logger.info(f"Duplicate found for hash: {lead_hash}")
                return True
            return False

        except Exception as e:
            logger.error(f"Error checking duplicate: {e}")
            # On error, assume not duplicate to avoid losing leads
            return False

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    def create_lead(self, lead_data: Dict) -> Optional[Dict]:
        """
        Create a single lead in Airtable.

        Args:
            lead_data: Lead dictionary with all required fields

        Returns:
            Created record or None on failure
        """
        try:
            # Map lead data to Airtable fields
            fields = {
                'Name': lead_data.get('author', 'Unknown'),
                'Platform': 'YouTube',
                'Comment': lead_data.get('text', ''),
                'Video URL': lead_data.get('video_url', ''),
                'Comment URL': lead_data.get('comment_url', ''),
                'Intent': lead_data.get('intent', 'Low'),
                'Confidence': lead_data.get('confidence', 0),
                'AI Reasoning': lead_data.get('reasoning', ''),
                'Lead Hash': lead_data.get('hash', ''),
                'Scraped Date': datetime.now().strftime('%Y-%m-%d')
            }

            record = self.table.create(fields)
            logger.info(f"Created lead: {fields['Name']} ({fields['Intent']})")
            return record

        except Exception as e:
            logger.error(f"Error creating lead: {e}")
            logger.error(f"Lead data: {lead_data}")
            return None

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    def batch_create_leads(self, leads: List[Dict]) -> List[Dict]:
        """
        Create multiple leads in Airtable (batch operation).

        Args:
            leads: List of lead dictionaries

        Returns:
            List of created records
        """
        if not leads:
            return []

        created_records = []

        # Process in batches of 10 (Airtable API limit)
        batch_size = 10
        for i in range(0, len(leads), batch_size):
            batch = leads[i:i + batch_size]

            try:
                # Map each lead to Airtable fields
                records_to_create = []
                for lead in batch:
                    fields = {
                        'Name': lead.get('author', 'Unknown'),
                        'Platform': 'YouTube',
                        'Comment': lead.get('text', ''),
                        'Video URL': lead.get('video_url', ''),
                        'Comment URL': lead.get('comment_url', ''),
                        'Intent': lead.get('intent', 'Low'),
                        'Confidence': lead.get('confidence', 0),
                        'AI Reasoning': lead.get('reasoning', ''),
                        'Lead Hash': lead.get('hash', ''),
                        'Scraped Date': datetime.now().strftime('%Y-%m-%d')
                    }
                    records_to_create.append(fields)

                # Batch create
                records = self.table.batch_create(records_to_create)
                created_records.extend(records)

                logger.info(f"Created batch of {len(records)} leads")

            except Exception as e:
                logger.error(f"Error creating batch: {e}")
                # Try creating individually as fallback
                logger.info("Attempting individual creation as fallback")
                for lead in batch:
                    record = self.create_lead(lead)
                    if record:
                        created_records.append(record)

        logger.info(f"Total leads created: {len(created_records)}")
        return created_records

    def get_recent_leads(self, hours: int = 24) -> List[Dict]:
        """
        Get leads created in the last N hours.

        Args:
            hours: Number of hours to look back

        Returns:
            List of lead records
        """
        try:
            cutoff_date = (datetime.now() - timedelta(hours=hours)).strftime('%Y-%m-%d')

            # Fetch all records created on or after cutoff date
            formula = f"IS_AFTER({{Scraped Date}}, '{cutoff_date}')"
            records = self.table.all(formula=formula, sort=['Scraped Date'])

            logger.info(f"Found {len(records)} leads from last {hours} hours")
            return records

        except Exception as e:
            logger.error(f"Error fetching recent leads: {e}")
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
