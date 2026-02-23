"""
Export YouTube OAuth token to JSON format for Streamlit Cloud.

Run this AFTER running setup_youtube_oauth.py locally.

Usage:
    python export_oauth_token.py

Then copy the output YOUTUBE_TOKEN_JSON value into:
  - Streamlit Cloud: App settings → Secrets
  - Local .env file
"""

import json
import pickle
from pathlib import Path

TOKEN_FILE = 'youtube_token.pickle'


def main():
    token_path = Path(TOKEN_FILE)

    if not token_path.exists():
        print(f"\n❌ '{TOKEN_FILE}' not found.")
        print("Run 'python setup_youtube_oauth.py' first to generate the token.\n")
        return

    try:
        with open(token_path, 'rb') as f:
            credentials = pickle.load(f)

        if credentials.expired and credentials.refresh_token:
            from google.auth.transport.requests import Request
            credentials.refresh(Request())
            print("✅ Token refreshed.\n")

        token_data = {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': list(credentials.scopes) if credentials.scopes else [],
        }

        token_json = json.dumps(token_data)

        print("=" * 70)
        print("✅ YouTube OAuth token exported successfully!")
        print("=" * 70)
        print("\nCopy the line below into Streamlit Cloud Secrets (or your .env):\n")
        print(f'YOUTUBE_TOKEN_JSON={token_json}')
        print("\n" + "=" * 70)
        print("\nIn Streamlit Cloud:")
        print("  App → Settings → Secrets → paste the line above → Save")
        print("\nIn .env file (local):")
        print("  Add the line to your .env file")
        print("\nAfter adding, restart your Streamlit app.\n")

    except Exception as e:
        print(f"\n❌ Error exporting token: {e}")
        print("Try re-running setup_youtube_oauth.py to generate a fresh token.\n")


if __name__ == "__main__":
    main()
