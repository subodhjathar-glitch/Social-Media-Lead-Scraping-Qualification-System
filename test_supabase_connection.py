"""Test Supabase connection and diagnose issues."""

import os
from dotenv import load_dotenv
from supabase import create_client
import sys

# Load environment variables
load_dotenv()

def test_supabase():
    """Test Supabase connection and diagnose issues."""

    # Get credentials (prefer service_role_key for backend)
    url = os.getenv("SUPABASE_URL", "").strip().rstrip("/")
    key = (os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY") or "").strip()

    print("=" * 80)
    print("SUPABASE CONNECTION TEST")
    print("=" * 80)

    # Check if credentials are set
    print("\n1. Checking credentials...")
    if not url or not key:
        print("❌ FAILED: SUPABASE_URL or SUPABASE_KEY not set in .env")
        return False

    # Check if they're placeholder values
    if "your_" in url or "your_" in key or "supabase.co" not in url:
        print(f"❌ FAILED: Credentials appear to be placeholder values")
        print(f"   URL format check: {url[:30]}...")
        print(f"   Please set real Supabase credentials in .env file")
        return False

    print(f"✓ URL: {url[:30]}...")
    print(f"✓ Key: {key[:10]}...{key[-5:]}")

    # Test connection
    print("\n2. Testing connection...")
    try:
        client = create_client(url, key)
        print("✓ Supabase client created")
    except Exception as e:
        print(f"❌ FAILED: Could not create Supabase client: {e}")
        return False

    # Test database access
    print("\n3. Testing database access...")
    try:
        # Try to query the leads table
        response = client.table('leads').select('id').limit(1).execute()
        print(f"✓ Successfully queried 'leads' table")
        print(f"  Current lead count: {len(response.data)} (showing first result)")

        # Check if we can count all records
        count_response = client.table('leads').select('id', count='exact').limit(1).execute()
        total_count = count_response.count if hasattr(count_response, 'count') else 0
        print(f"  Total leads in database: {total_count}")

    except Exception as e:
        print(f"❌ FAILED: Could not access 'leads' table: {e}")
        print(f"\nPossible issues:")
        print(f"  1. Table 'leads' doesn't exist in your Supabase database")
        print(f"  2. RLS (Row Level Security) is blocking access")
        print(f"  3. API key doesn't have permissions")
        print(f"\nTo fix:")
        print(f"  1. Check your Supabase dashboard → SQL Editor")
        print(f"  2. Run the schema creation script to create tables")
        print(f"  3. If using RLS, either:")
        print(f"     - Disable RLS for service role key")
        print(f"     - Use SUPABASE_SERVICE_ROLE_KEY instead of SUPABASE_KEY")
        return False

    # Test write access
    print("\n4. Testing write access...")
    try:
        test_data = {
            'name': 'Test User',
            'platform': 'YouTube',
            'comment': 'Test comment for connection verification',
            'video_url': 'https://www.youtube.com/test',
            'comment_url': 'https://www.youtube.com/test',
            'intent': 'Low',
            'confidence': 100,
            'ai_reasoning': 'Test entry',
            'intent_type': 'low_intent',
            'pain_intensity': 0,
            'readiness_score': 0,
            'lead_hash': 'test_connection_hash_12345',
            'scraped_date': '2026-02-15'
        }

        # Try to insert
        insert_response = client.table('leads').insert(test_data).execute()

        if insert_response.data:
            print(f"✓ Successfully wrote test record to database")

            # Delete the test record
            test_id = insert_response.data[0]['id']
            client.table('leads').delete().eq('id', test_id).execute()
            print(f"✓ Successfully deleted test record")
        else:
            print(f"⚠ Write returned no data (might still have worked)")

    except Exception as e:
        print(f"❌ FAILED: Could not write to 'leads' table: {e}")
        print(f"\nPossible issues:")
        print(f"  1. RLS (Row Level Security) is blocking writes")
        print(f"  2. API key doesn't have write permissions")
        print(f"  3. Required fields are missing or have wrong types")
        print(f"\nTo fix:")
        print(f"  - Use SUPABASE_SERVICE_ROLE_KEY for full access (bypass RLS)")
        print(f"  - Or disable RLS on the 'leads' table in Supabase dashboard")
        return False

    print("\n" + "=" * 80)
    print("✅ ALL TESTS PASSED - Supabase is properly configured!")
    print("=" * 80)
    print("\nYour scraper should now save data to Supabase successfully.")
    return True

if __name__ == "__main__":
    success = test_supabase()
    sys.exit(0 if success else 1)
