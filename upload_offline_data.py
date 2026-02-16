"""Upload offline saved leads to Supabase."""

import json
import sys
from pathlib import Path
from src.database import SupabaseDatabase
from src.utils import setup_logger

logger = setup_logger(__name__)


def upload_offline_leads(json_file: str):
    """Upload leads from JSON file to Supabase."""

    # Load the JSON file
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            leads = json.load(f)
        logger.info(f"Loaded {len(leads)} leads from {json_file}")
    except Exception as e:
        logger.error(f"Error loading JSON file: {e}")
        return False

    # Initialize database
    db = SupabaseDatabase()

    if not db.is_available:
        logger.error("Supabase is not available. Cannot upload data.")
        return False

    logger.info(f"✓ Supabase connection established")

    # Transform leads to match expected format
    processed_leads = []
    for lead in leads:
        # The data is already in the right format from _save_leads_locally
        # Just need to map it properly
        processed_lead = {
            'author': lead.get('name', 'Unknown'),
            'text': lead.get('comment', ''),
            'video_url': lead.get('video_url', ''),
            'comment_url': lead.get('comment_url', ''),
            'intent': lead.get('intent', 'Low'),
            'confidence': lead.get('confidence', 0),
            'reasoning': lead.get('ai_reasoning', ''),
            'intent_type': lead.get('intent_type', 'low_intent'),
            'pain_intensity': lead.get('pain_intensity', 0),
            'readiness_score': lead.get('readiness_score', 0),
            'practice_mention': lead.get('practice_mention'),
            'language': lead.get('language'),
            'prefilter_status': lead.get('prefilter_status', 'unknown'),
            'hash': lead.get('lead_hash', '')
        }
        processed_leads.append(processed_lead)

    # Upload in batch
    try:
        logger.info(f"Uploading {len(processed_leads)} leads to Supabase...")
        created_records = db.batch_create_leads(processed_leads)
        logger.info(f"✅ Successfully uploaded {len(created_records)} leads to Supabase!")
        return True
    except Exception as e:
        logger.error(f"Error uploading leads: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        # Find the latest offline file
        data_dir = Path("data")
        offline_files = list(data_dir.glob("leads_offline_*.json"))

        if not offline_files:
            print("No offline lead files found in data/ directory")
            sys.exit(1)

        # Get the most recent file
        latest_file = max(offline_files, key=lambda p: p.stat().st_mtime)
        print(f"Found offline data file: {latest_file}")
        json_file = str(latest_file)
    else:
        json_file = sys.argv[1]

    success = upload_offline_leads(json_file)
    sys.exit(0 if success else 1)
