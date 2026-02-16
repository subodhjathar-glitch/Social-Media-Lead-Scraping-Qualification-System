"""Check current workflow and database state."""

from src.database import SupabaseDatabase
from src.utils import setup_logger

logger = setup_logger(__name__)

def check_workflow():
    """Check what's in the database."""

    db = SupabaseDatabase()

    if not db.is_available:
        logger.error("Supabase not available")
        return

    print("\n" + "=" * 80)
    print("WORKFLOW STATUS CHECK")
    print("=" * 80)

    # Check leads
    try:
        leads = db.client.table('leads').select('id', count='exact').limit(1).execute()
        print(f"\n✅ Leads table: {leads.count} records")
    except Exception as e:
        print(f"\n❌ Leads table: Error - {e}")

    # Check conversation_threads
    try:
        threads = db.client.table('conversation_threads').select('id', count='exact').limit(1).execute()
        print(f"✅ Conversation Threads: {threads.count} records")
    except Exception as e:
        print(f"❌ Conversation Threads: Error - {e}")

    # Check pending_replies
    try:
        replies = db.client.table('pending_replies').select('id', count='exact').limit(1).execute()
        print(f"✅ Pending Replies: {replies.count} records")
    except Exception as e:
        print(f"❌ Pending Replies: Error - {e}")

    # Check teacher_profiles
    try:
        teachers = db.client.table('teacher_profiles').select('id', count='exact').limit(1).execute()
        print(f"✅ Teacher Profiles: {teachers.count} records")
    except Exception as e:
        print(f"❌ Teacher Profiles: Error - {e}")

    # Check resources
    try:
        resources = db.client.table('resources').select('id', count='exact').limit(1).execute()
        print(f"✅ Resources: {resources.count} records")
    except Exception as e:
        print(f"❌ Resources: Error - {e}")

    print("\n" + "=" * 80)
    print("WORKFLOW GAP ANALYSIS")
    print("=" * 80)

    print("\nCurrent workflow (main.py):")
    print("  1. ✅ Scrape YouTube comments")
    print("  2. ✅ Qualify leads with AI")
    print("  3. ✅ Store in 'leads' table")
    print("  4. ❌ Create conversation threads - MISSING!")
    print("  5. ❌ Generate AI replies - MISSING!")
    print("  6. ❌ Store in 'pending_replies' - MISSING!")

    print("\nWhat's missing:")
    print("  - After storing leads, system should create conversation threads")
    print("  - Then generate initial AI replies for qualified leads")
    print("  - Then store replies in pending_replies for teacher approval")
    print("  - Teacher approves in dashboard")
    print("  - System posts to YouTube")

    print("\n" + "=" * 80)

if __name__ == "__main__":
    check_workflow()
