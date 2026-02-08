"""Test script to verify environment setup and API connections."""

import sys
from datetime import datetime

def test_imports():
    """Test that all required packages can be imported."""
    print("Testing imports...")
    try:
        import googleapiclient
        print("  ✓ google-api-python-client")
    except ImportError:
        print("  ✗ google-api-python-client - run: pip install -r requirements.txt")
        return False

    try:
        import openai
        print("  ✓ openai")
    except ImportError:
        print("  ✗ openai - run: pip install -r requirements.txt")
        return False

    try:
        import pyairtable
        print("  ✓ pyairtable")
    except ImportError:
        print("  ✗ pyairtable - run: pip install -r requirements.txt")
        return False

    try:
        from pydantic_settings import BaseSettings
        print("  ✓ pydantic-settings")
    except ImportError:
        print("  ✗ pydantic-settings - run: pip install -r requirements.txt")
        return False

    try:
        import dotenv
        print("  ✓ python-dotenv")
    except ImportError:
        print("  ✗ python-dotenv - run: pip install -r requirements.txt")
        return False

    return True


def test_config():
    """Test that configuration can be loaded."""
    print("\nTesting configuration...")
    try:
        from src.config import settings

        # Check required fields
        required = [
            'youtube_api_key',
            'openai_api_key',
            'airtable_token',
            'airtable_base_id',
            'email_from',
            'email_to',
            'email_password'
        ]

        missing = []
        for field in required:
            value = getattr(settings, field, None)
            if not value or 'your_' in str(value) or '_here' in str(value):
                missing.append(field)
                print(f"  ✗ {field.upper()} - not configured")
            else:
                print(f"  ✓ {field.upper()}")

        if missing:
            print(f"\n  Missing or invalid configuration: {', '.join(missing)}")
            print("  Please edit your .env file with valid API keys")
            return False

        return True

    except Exception as e:
        print(f"  ✗ Error loading config: {e}")
        return False


def test_youtube_api():
    """Test YouTube API connection."""
    print("\nTesting YouTube API connection...")
    try:
        from googleapiclient.discovery import build
        from src.config import settings

        youtube = build('youtube', 'v3', developerKey=settings.youtube_api_key)

        # Simple API test - search for a single channel
        response = youtube.search().list(
            part='snippet',
            q='test',
            type='channel',
            maxResults=1
        ).execute()

        print("  ✓ YouTube API connection successful")
        return True

    except Exception as e:
        print(f"  ✗ YouTube API error: {e}")
        print("  Check your YOUTUBE_API_KEY in .env")
        return False


def test_openai_api():
    """Test OpenAI API connection."""
    print("\nTesting OpenAI API connection...")
    try:
        from openai import OpenAI
        from src.config import settings

        client = OpenAI(api_key=settings.openai_api_key)

        # Simple API test
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Say 'test'"}],
            max_tokens=5
        )

        print("  ✓ OpenAI API connection successful")
        return True

    except Exception as e:
        print(f"  ✗ OpenAI API error: {e}")
        print("  Check your OPENAI_API_KEY in .env")
        return False


def test_airtable_api():
    """Test Airtable API connection."""
    print("\nTesting Airtable API connection...")
    try:
        from pyairtable import Api
        from src.config import settings

        api = Api(settings.airtable_token)
        table = api.table(settings.airtable_base_id, settings.airtable_table_name)

        # Try to fetch records (even if empty)
        records = table.all(max_records=1)

        print("  ✓ Airtable API connection successful")
        print(f"  ✓ Base ID: {settings.airtable_base_id}")
        print(f"  ✓ Table: {settings.airtable_table_name}")
        return True

    except Exception as e:
        print(f"  ✗ Airtable API error: {e}")
        print("  Check your AIRTABLE_TOKEN and AIRTABLE_BASE_ID in .env")
        print("  Also verify the 'Leads' table exists in your Airtable base")
        return False


def test_email():
    """Test email configuration (without sending)."""
    print("\nTesting email configuration...")
    try:
        from src.config import settings

        print(f"  ✓ From: {settings.email_from}")
        print(f"  ✓ To: {settings.email_to}")
        print(f"  ✓ Recipients: {settings.email_recipients}")

        if 'your_' in settings.email_password or '_here' in settings.email_password:
            print("  ✗ EMAIL_PASSWORD not configured")
            return False

        print("  ✓ Email configuration looks valid")
        print("  Note: Email sending will be tested during actual run")
        return True

    except Exception as e:
        print(f"  ✗ Email config error: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("Lead Scraper - Environment Setup Test")
    print("=" * 60)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    results = {
        "Imports": test_imports(),
        "Configuration": test_config(),
        "YouTube API": test_youtube_api(),
        "OpenAI API": test_openai_api(),
        "Airtable API": test_airtable_api(),
        "Email Config": test_email(),
    }

    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)

    all_passed = True
    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{test_name:20s} {status}")
        if not passed:
            all_passed = False

    print("=" * 60)

    if all_passed:
        print("\n✓ All tests passed! You're ready to run the scraper.")
        print("\nNext step: python -m src.main")
        sys.exit(0)
    else:
        print("\n✗ Some tests failed. Please fix the issues above.")
        print("\nCommon fixes:")
        print("1. Edit .env file with valid API keys")
        print("2. Verify Airtable base and table exist")
        print("3. Enable required APIs in Google Cloud Console")
        sys.exit(1)


if __name__ == "__main__":
    main()
