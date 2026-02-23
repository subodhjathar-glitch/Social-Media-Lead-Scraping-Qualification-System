"""
Setup YouTube OAuth for automated comment posting.

Run this script from the project directory:
    .venv/bin/python setup_youtube_oauth.py

A browser window will open. Sign in and grant access.
After completion, run export_oauth_token.py to get the key for Streamlit Cloud.
"""

import json
import os
import pickle
import sys
import webbrowser
from pathlib import Path

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
TOKEN_FILE = 'youtube_token.pickle'
CREDENTIALS_FILE = 'client_secret.json'


def setup_oauth():
    """Run OAuth flow and save credentials."""

    if not Path(CREDENTIALS_FILE).exists():
        print("\n❌ client_secret.json not found.")
        print("Download it from Google Cloud Console -> APIs & Credentials -> OAuth 2.0 Client IDs")
        print("Save as client_secret.json in this project directory.\n")
        return False

    print("\n✅ Found client_secret.json")
    print("\n🔐 Starting OAuth flow — a browser window will open.\n")
    print("Sign in with the Google account that manages the YouTube channel.")
    print("Click 'Continue' if warned about unverified app, then grant all permissions.\n")
    sys.stdout.flush()

    try:
        # WSL: try to use Windows browser
        if 'microsoft' in os.uname().release.lower() or 'wsl' in os.uname().release.lower():
            # Try common Windows browser paths
            for browser_path in [
                '/mnt/c/Program Files/Google/Chrome/Application/chrome.exe',
                '/mnt/c/Program Files (x86)/Google/Chrome/Application/chrome.exe',
                '/mnt/c/Program Files/Microsoft/Edge/Application/msedge.exe',
            ]:
                if os.path.exists(browser_path):
                    webbrowser.register('windows-browser',
                                        None,
                                        webbrowser.BackgroundBrowser(browser_path))
                    webbrowser.get('windows-browser')
                    break

        flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
        credentials = flow.run_local_server(
            port=8080,
            prompt='consent',
            success_message='Authentication successful! You can close this window.',
            open_browser=True,
        )

        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(credentials, token)

        print("\n" + "=" * 60)
        print("✅ SUCCESS! Token saved to youtube_token.pickle")
        print("=" * 60)
        print("\nNext: run this to get the key for Streamlit Cloud:")
        print("   .venv/bin/python export_oauth_token.py\n")

        return True

    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nIf browser didn't open, try running the script directly")
        print("in your terminal (outside Claude Code):\n")
        print("   cd ~/Social-Media-Lead-Scraping-Qualification-System")
        print("   .venv/bin/python setup_youtube_oauth.py\n")
        return False


def main():
    print("\n" + "=" * 60)
    print("YOGAVANI — YouTube OAuth Setup")
    print("=" * 60)

    # Delete expired token if it exists
    if Path(TOKEN_FILE).exists():
        try:
            with open(TOKEN_FILE, 'rb') as token:
                credentials = pickle.load(token)
            if credentials and credentials.valid:
                print("\n✅ Token already valid — no setup needed!")
                print("Run export_oauth_token.py to export it.\n")
                return
            elif credentials and credentials.expired and credentials.refresh_token:
                print("\n🔄 Attempting to refresh existing token...")
                try:
                    credentials.refresh(Request())
                    with open(TOKEN_FILE, 'wb') as token:
                        pickle.dump(credentials, token)
                    print("✅ Token refreshed successfully!")
                    print("Run export_oauth_token.py to export it.\n")
                    return
                except Exception:
                    print("⚠️  Token cannot be refreshed (expired/revoked). Re-authenticating...\n")
        except Exception:
            pass
        os.remove(TOKEN_FILE)

    setup_oauth()


if __name__ == "__main__":
    main()
