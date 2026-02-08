"""Test script to verify environment setup and API connections."""

import os
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
        # Show where .env is loaded from (pydantic-settings uses current working directory)
        cwd = os.getcwd()
        env_path = os.path.abspath(os.path.join(cwd, ".env"))
        print(f"  .env path: {env_path}")
        if not os.path.isfile(env_path):
            print("  ✗ .env file not found at this path. Create it: cp .env.example .env")
            return False
        print("  ✓ .env file found")

        # Shell env vars override .env - check if placeholders are coming from the shell
        env_keys = [
            "YOUTUBE_API_KEY", "OPENAI_API_KEY", "AIRTABLE_TOKEN", "AIRTABLE_BASE_ID",
            "EMAIL_FROM", "EMAIL_TO", "EMAIL_PASSWORD"
        ]
        from_env = [k for k in env_keys if os.environ.get(k, "").strip()]
        if from_env:
            placeholder_like = [
                k for k in from_env
                if "your_" in (os.environ.get(k) or "") or "_here" in (os.environ.get(k) or "")
            ]
            if placeholder_like:
                print(f"  ⚠ Shell has placeholder values for: {', '.join(placeholder_like)}")
                print("    Unset them so .env is used: unset YOUTUBE_API_KEY OPENAI_API_KEY AIRTABLE_TOKEN AIRTABLE_BASE_ID EMAIL_FROM EMAIL_TO EMAIL_PASSWORD")
                print("    Then run this test again.")
                return False

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
            # Check .env file content for placeholder text (without printing secrets)
            try:
                with open(env_path, "r", encoding="utf-8") as f:
                    content = f.read()
                placeholders_in_file = []
                for line in content.splitlines():
                    line = line.strip()
                    if line.startswith("#") or "=" not in line:
                        continue
                    key, _, val = line.partition("=")
                    key, val = key.strip(), val.strip().strip('"').strip("'")
                    if not val or "your_" in val or "_here" in val:
                        placeholders_in_file.append(key)
                if placeholders_in_file:
                    print(f"  Your .env file still has placeholder values for: {', '.join(placeholders_in_file)}")
                    print("  Replace them with real keys and save the file.")
            except Exception:
                pass
            print("  Use one variable per line, no spaces around =, e.g.:")
            print("    YOUTUBE_API_KEY=your_actual_key")
            print("  Save the file and run this test again from the project directory.")
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
        err_str = str(e)
        print(f"  ✗ OpenAI API error: {e}")
        if "429" in err_str or "quota" in err_str.lower() or "insufficient_quota" in err_str:
            print("  → This is a quota/billing limit. Add a payment method or upgrade at:")
            print("    https://platform.openai.com/account/billing")
        else:
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
        err_str = str(e)
        print(f"  ✗ Airtable API error: {e}")
        if "404" in err_str or "NOT_FOUND" in err_str:
            print("  → 404 means the base or table wasn't found. Checking which bases your token can access...")
            try:
                import requests
                from src.config import settings
                r = requests.get(
                    "https://api.airtable.com/v0/meta/bases",
                    headers={"Authorization": f"Bearer {settings.airtable_token}"},
                    timeout=10,
                )
                if r.status_code == 200:
                    data = r.json()
                    bases = data.get("bases") or []
                    ids = [b.get("id") for b in bases if b.get("id")]
                    if ids:
                        print(f"    Your token can access base IDs: {', '.join(ids)}")
                        if settings.airtable_base_id not in ids:
                            print(f"    Your .env has AIRTABLE_BASE_ID={settings.airtable_base_id}")
                            print("    → That base is NOT in the list. In Airtable: Developer Hub → your token → add this base under Access.")
                        else:
                            print("    Your base ID is in the list → the table name may be wrong. Create a table named exactly 'Leads'.")
                    else:
                        print("    Your token has no bases in scope. Developer Hub → your token → add a base under Access.")
                else:
                    print("    1. Base ID: copy from Airtable URL (https://airtable.com/BASE_ID/...)")
                    print("    2. Table name: exactly 'Leads' (or set AIRTABLE_TABLE_NAME in .env)")
                    print("    3. Token: Developer Hub → your token → add this base under Access")
            except Exception:
                print("    1. Base ID: copy from Airtable URL (https://airtable.com/BASE_ID/...)")
                print("    2. Table name: exactly 'Leads' (or set AIRTABLE_TABLE_NAME in .env)")
                print("    3. Token: Developer Hub → your token → add this base under Access")
        else:
            print("  Check your AIRTABLE_TOKEN and AIRTABLE_BASE_ID in .env")
        return False


def test_email():
    """Test email configuration (without sending)."""
    print("\nTesting email configuration...")
    try:
        from src.config import settings

        print(f"  ✓ From: {settings.email_from}")
        print(f"  ✓ To: {settings.email_to}")
        print(f"  ✓ Recipients: {settings.email_recipients}")

        # Multiple addresses must be comma-separated in EMAIL_TO
        if "," not in settings.email_to and settings.email_to.count("@") > 1:
            print("  ⚠ For multiple recipients, use commas in EMAIL_TO, e.g.: a@x.com, b@y.com")

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
