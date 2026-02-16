"""Verify that data is properly stored in Supabase."""

from src.database import SupabaseDatabase
from src.utils import setup_logger

logger = setup_logger(__name__)


def verify_data():
    """Verify Supabase has data."""

    db = SupabaseDatabase()

    if not db.is_available:
        logger.error("❌ Supabase is not available")
        return False

    logger.info("✓ Connected to Supabase")

    # Get total lead count
    try:
        response = db.client.table('leads').select('id', count='exact').limit(1).execute()
        total_leads = response.count if hasattr(response, 'count') else len(response.data)

        logger.info(f"✅ Total leads in Supabase: {total_leads}")

        # Get recent leads
        recent = db.get_recent_leads(hours=24)
        logger.info(f"✅ Leads from last 24 hours: {len(recent)}")

        # Show sample
        if recent:
            sample = recent[0]
            logger.info(f"\nSample lead:")
            logger.info(f"  Name: {sample.get('name')}")
            logger.info(f"  Intent: {sample.get('intent')}")
            logger.info(f"  Intent Type: {sample.get('intent_type')}")
            logger.info(f"  Readiness: {sample.get('readiness_score')}%")
            logger.info(f"  Comment: {sample.get('comment', '')[:80]}...")

        return True

    except Exception as e:
        logger.error(f"❌ Error querying Supabase: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


if __name__ == "__main__":
    import sys
    success = verify_data()
    sys.exit(0 if success else 1)
