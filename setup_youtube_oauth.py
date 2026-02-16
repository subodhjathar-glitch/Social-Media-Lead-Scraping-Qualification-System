"""
Setup YouTube OAuth for automated comment posting.

This script guides you through:
1. Getting OAuth credentials from Google Cloud Console
2. Running OAuth flow to get access token
3. Storing credentials securely
"""

import os
import json
from pathlib import Path
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import pickle

# OAuth scopes required for posting YouTube comments
SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']

# Token storage location
TOKEN_FILE = 'youtube_token.pickle'
CREDENTIALS_FILE = 'client_secret.json'


def print_instructions():
    """Print instructions for getting OAuth credentials."""
    print("=" * 80)
    print("📹 YOUTUBE OAUTH SETUP")
    print("=" * 80)
    print("\nTo enable automatic YouTube posting, you need OAuth credentials.")
    print("\n📋 STEP-BY-STEP INSTRUCTIONS:\n")

    print("1. Go to Google Cloud Console:")
    print("   https://console.cloud.google.com/\n")

    print("2. Create a New Project (or select existing):")
    print("   - Click 'Select a project' at the top")
    print("   - Click 'NEW PROJECT'")
    print("   - Name it: 'Yogavani Lead System'")
    print("   - Click 'CREATE'\n")

    print("3. Enable YouTube Data API v3:")
    print("   - Go to: https://console.cloud.google.com/apis/library")
    print("   - Search for 'YouTube Data API v3'")
    print("   - Click on it and press 'ENABLE'\n")

    print("4. Create OAuth Consent Screen:")
    print("   - Go to: https://console.cloud.google.com/apis/credentials/consent")
    print("   - Select 'External' user type")
    print("   - Click 'CREATE'")
    print("   - Fill in:")
    print("     * App name: Yogavani Lead System")
    print("     * User support email: your-email@gmail.com")
    print("     * Developer contact: your-email@gmail.com")
    print("   - Click 'SAVE AND CONTINUE'")
    print("   - On Scopes page, click 'SAVE AND CONTINUE'")
    print("   - On Test users page, add your email, click 'SAVE AND CONTINUE'\n")

    print("5. Create OAuth 2.0 Credentials:")
    print("   - Go to: https://console.cloud.google.com/apis/credentials")
    print("   - Click '+ CREATE CREDENTIALS'")
    print("   - Select 'OAuth client ID'")
    print("   - Application type: 'Desktop app'")
    print("   - Name: 'Yogavani Desktop Client'")
    print("   - Click 'CREATE'\n")

    print("6. Download Credentials:")
    print("   - Click the download icon (⬇️) next to your OAuth client")
    print("   - Save the file as 'client_secret.json' in this directory:")
    print(f"   {os.getcwd()}\n")

    print("7. Run this script again after downloading client_secret.json\n")

    print("=" * 80)


def setup_oauth():
    """Run OAuth flow and save credentials."""

    # Check if client_secret.json exists
    if not Path(CREDENTIALS_FILE).exists():
        print("\n❌ ERROR: client_secret.json not found!\n")
        print_instructions()
        return False

    print("\n✅ Found client_secret.json")
    print("\n🔐 Starting OAuth flow...\n")
    print("A browser window will open for authentication.")
    print("Please:")
    print("  1. Sign in with the YouTube account you want to post from")
    print("  2. Click 'Continue' when warned about unverified app")
    print("  3. Select all checkboxes to grant permissions")
    print("  4. Click 'Continue'\n")

    input("Press ENTER when ready to start authentication...")

    try:
        # Run OAuth flow
        flow = InstalledAppFlow.from_client_secrets_file(
            CREDENTIALS_FILE,
            SCOPES,
            redirect_uri='http://localhost:8080/'
        )

        # This will open browser for authentication
        credentials = flow.run_local_server(
            port=8080,
            prompt='consent',
            success_message='Authentication successful! You can close this window.'
        )

        # Save credentials
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(credentials, token)

        print("\n" + "=" * 80)
        print("✅ SUCCESS! YouTube OAuth is now configured!")
        print("=" * 80)
        print(f"\nCredentials saved to: {TOKEN_FILE}")
        print("\n🚀 You can now post comments automatically from the dashboard!")
        print("\nNext steps:")
        print("  1. Restart the Streamlit dashboard")
        print("  2. Approve a reply")
        print("  3. It will automatically post to YouTube!")
        print("\n" + "=" * 80)

        return True

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print("\nTroubleshooting:")
        print("  - Make sure you have a web browser available")
        print("  - Check that client_secret.json is valid")
        print("  - Ensure you granted all permissions")
        print("  - Try running the script again")
        return False


def check_existing_credentials():
    """Check if OAuth is already set up."""
    if Path(TOKEN_FILE).exists():
        try:
            with open(TOKEN_FILE, 'rb') as token:
                credentials = pickle.load(token)

            # Check if credentials are valid
            if credentials and credentials.valid:
                print("\n✅ YouTube OAuth is already configured!")
                print(f"   Token file: {TOKEN_FILE}")
                print("\n🚀 You can post comments automatically.")

                # Show which account is authenticated
                print("\nTo re-authenticate with a different account:")
                print(f"  1. Delete {TOKEN_FILE}")
                print("  2. Run this script again")
                return True
            elif credentials and credentials.expired and credentials.refresh_token:
                # Try to refresh
                print("\n🔄 Token expired, attempting to refresh...")
                credentials.refresh(Request())

                with open(TOKEN_FILE, 'wb') as token:
                    pickle.dump(credentials, token)

                print("✅ Token refreshed successfully!")
                return True
        except Exception as e:
            print(f"\n⚠️ Existing token is invalid: {e}")
            print("Will set up new authentication...\n")

    return False


def main():
    """Main setup flow."""
    print("\n" + "=" * 80)
    print("🕉️ YOGAVANI YOUTUBE OAUTH SETUP")
    print("=" * 80)
    print("\nThis will enable automatic YouTube comment posting.\n")

    # Check if already configured
    if check_existing_credentials():
        response = input("\nDo you want to re-authenticate? (y/n): ").lower()
        if response != 'y':
            print("\nOAuth setup complete. Exiting.")
            return

        # Delete old token
        if Path(TOKEN_FILE).exists():
            os.remove(TOKEN_FILE)
            print("\n🗑️  Old token deleted.")

    # Check for client_secret.json
    if not Path(CREDENTIALS_FILE).exists():
        print_instructions()
        print("\n👉 After downloading client_secret.json, run this script again:")
        print(f"   python {__file__}\n")
        return

    # Run OAuth setup
    success = setup_oauth()

    if success:
        print("\n✨ Setup complete! Your dashboard can now post comments automatically.\n")
    else:
        print("\n❌ Setup failed. Please try again or check the instructions.\n")


if __name__ == "__main__":
    main()
