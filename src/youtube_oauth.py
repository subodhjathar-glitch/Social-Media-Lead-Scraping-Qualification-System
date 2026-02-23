"""YouTube OAuth credential management.

Supports two credential sources (tried in order):
1. YOUTUBE_TOKEN_JSON environment variable — JSON string of credentials dict.
   Use this on Streamlit Cloud / any cloud deployment.
2. Local youtube_token.pickle file — for local development.

After running setup_youtube_oauth.py locally, run export_oauth_token.py to get
the JSON string to paste into Streamlit Cloud secrets as YOUTUBE_TOKEN_JSON.
"""

import json
import os
import pickle
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

TOKEN_FILE = 'youtube_token.pickle'


def _credentials_from_dict(token_data: dict) -> Credentials:
    """Reconstruct a Credentials object from a plain dict."""
    return Credentials(
        token=token_data.get('token'),
        refresh_token=token_data.get('refresh_token'),
        token_uri=token_data.get('token_uri', 'https://oauth2.googleapis.com/token'),
        client_id=token_data.get('client_id'),
        client_secret=token_data.get('client_secret'),
        scopes=token_data.get('scopes'),
    )


def get_youtube_credentials():
    """
    Get YouTube OAuth credentials.

    Tries YOUTUBE_TOKEN_JSON env var first (cloud deployment),
    then falls back to local youtube_token.pickle (local dev).

    Returns:
        Credentials object or None if not configured.
    """
    # ── Option 1: env var (Streamlit Cloud / GitHub Actions) ──────────────────
    token_json = os.getenv("YOUTUBE_TOKEN_JSON")
    if token_json:
        try:
            token_data = json.loads(token_json)
            credentials = _credentials_from_dict(token_data)

            if credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
                # Note: updated token can't be written back to env var at runtime.
                # The refresh_token remains valid so the next refresh will work too.

            return credentials
        except Exception as e:
            print(f"Error loading YouTube credentials from YOUTUBE_TOKEN_JSON: {e}")

    # ── Option 2: local pickle file (local development) ───────────────────────
    token_path = Path(TOKEN_FILE)
    if token_path.exists():
        try:
            with open(token_path, 'rb') as token:
                credentials = pickle.load(token)

            if credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
                with open(token_path, 'wb') as token:
                    pickle.dump(credentials, token)

            return credentials
        except Exception as e:
            print(f"Error loading YouTube credentials from file: {e}")

    return None


def get_youtube_client():
    """
    Get authenticated YouTube API client.

    Returns:
        YouTube API client or None if not configured.
    """
    credentials = get_youtube_credentials()
    if not credentials:
        return None
    try:
        return build('youtube', 'v3', credentials=credentials)
    except Exception as e:
        print(f"Error building YouTube client: {e}")
        return None


def is_oauth_configured() -> bool:
    """
    Check if YouTube OAuth is configured and credentials are valid.

    Returns:
        bool: True if OAuth is set up and credentials are valid.
    """
    credentials = get_youtube_credentials()
    return credentials is not None and credentials.valid
