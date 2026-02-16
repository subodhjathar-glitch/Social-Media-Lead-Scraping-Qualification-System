"""YouTube OAuth credential management."""

import os
import pickle
from pathlib import Path
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

TOKEN_FILE = 'youtube_token.pickle'


def get_youtube_credentials():
    """
    Get YouTube OAuth credentials.

    Returns:
        Credentials object or None if not configured
    """
    token_path = Path(TOKEN_FILE)

    if not token_path.exists():
        return None

    try:
        with open(token_path, 'rb') as token:
            credentials = pickle.load(token)

        # Check if credentials need refresh
        if credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())

            # Save refreshed credentials
            with open(token_path, 'wb') as token:
                pickle.dump(credentials, token)

        return credentials

    except Exception as e:
        print(f"Error loading YouTube credentials: {e}")
        return None


def get_youtube_client():
    """
    Get authenticated YouTube API client.

    Returns:
        YouTube API client or None if not configured
    """
    credentials = get_youtube_credentials()

    if not credentials:
        return None

    try:
        youtube = build('youtube', 'v3', credentials=credentials)
        return youtube
    except Exception as e:
        print(f"Error building YouTube client: {e}")
        return None


def is_oauth_configured():
    """
    Check if YouTube OAuth is configured.

    Returns:
        bool: True if OAuth is set up and valid
    """
    credentials = get_youtube_credentials()
    return credentials is not None and credentials.valid
