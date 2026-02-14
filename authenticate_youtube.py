"""
YouTube OAuth Authentication Script

Run this ONCE to authenticate your YouTube account.
It will save credentials to 'youtube_token.pickle' for future use.

Usage:
    python authenticate_youtube.py

Requirements:
    1. client_secret.json (download from Google Cloud Console)
    2. pip install google-auth google-auth-oauthlib google-auth-httplib2
"""

import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# Scopes required for posting comments
SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']


def authenticate():
    """Authenticate and save credentials."""
    print("=" * 60)
    print("YouTube OAuth Authentication")
    print("=" * 60)
    print()

    creds = None

    # Check if client_secret.json exists
    if not os.path.exists('client_secret.json'):
        print("❌ ERROR: client_secret.json not found!")
        print()
        print("Please follow these steps:")
        print("1. Go to: https://console.cloud.google.com/apis/credentials")
        print("2. Create OAuth 2.0 Client ID (Desktop app)")
        print("3. Download as client_secret.json")
        print("4. Place in project root directory")
        print()
        print("📖 Full guide: docs/YOUTUBE_OAUTH_SETUP.md")
        return None

    # Check if token already exists
    if os.path.exists('youtube_token.pickle'):
        print("🔍 Found existing token...")
        with open('youtube_token.pickle', 'rb') as token:
            creds = pickle.load(token)
        print("✅ Loaded existing credentials")

    # If credentials are invalid or don't exist, authenticate
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("🔄 Refreshing expired token...")
            try:
                creds.refresh(Request())
                print("✅ Token refreshed successfully")
            except Exception as e:
                print(f"❌ Token refresh failed: {e}")
                print("Starting fresh authentication...")
                creds = None

        if not creds:
            print("🔐 Starting OAuth flow...")
            print()
            print("📌 A browser window will open shortly.")
            print("📌 Sign in with your YouTube account.")
            print("📌 Review and accept the permissions.")
            print()

            try:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'client_secret.json', SCOPES)
                creds = flow.run_local_server(port=0)
                print("✅ Authentication successful!")
            except Exception as e:
                print(f"❌ Authentication failed: {e}")
                return None

        # Save credentials for future use
        with open('youtube_token.pickle', 'wb') as token:
            pickle.dump(creds, token)
            print("💾 Credentials saved to youtube_token.pickle")

    print()
    print("=" * 60)
    print("✅ AUTHENTICATION COMPLETE")
    print("=" * 60)
    print()
    print("You can now:")
    print("- Post YouTube comments via the API")
    print("- Use auto-posting in the Streamlit app")
    print("- Reply to leads automatically")
    print()
    print("⚠️  IMPORTANT: Keep these files secret:")
    print("   - client_secret.json")
    print("   - youtube_token.pickle")
    print()
    print("Add them to .gitignore to prevent accidental commits!")
    print()

    return creds


if __name__ == '__main__':
    try:
        creds = authenticate()
        if creds:
            print("🎉 Setup complete! You're ready to post comments.")
        else:
            print("❌ Setup failed. Check the error messages above.")
    except KeyboardInterrupt:
        print("\n\n⚠️  Authentication cancelled by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("Please check the error and try again.")
