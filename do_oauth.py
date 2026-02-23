"""
YouTube OAuth setup — WSL-compatible.
Starts a local HTTP server, writes the auth URL to url.txt, waits for callback.
"""
import json
import os
import pickle
import secrets
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

import requests

# Load client secrets
with open('client_secret.json') as f:
    cs = json.load(f)['installed']

CLIENT_ID = cs['client_id']
CLIENT_SECRET = cs['client_secret']
AUTH_URI = cs['auth_uri']
TOKEN_URI = cs['token_uri']
SCOPE = 'https://www.googleapis.com/auth/youtube.force-ssl'
REDIRECT_URI = 'http://localhost:8081/'
STATE = secrets.token_urlsafe(16)

auth_code = None
server_done = threading.Event()


class CallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global auth_code
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        if 'code' in params:
            auth_code = params['code'][0]
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.wfile.write(b'<h2>Authentication successful! You can close this tab.</h2>')
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b'<h2>Error: no code received</h2>')
        server_done.set()

    def log_message(self, format, *args):
        pass  # suppress request logs


def build_auth_url():
    params = (
        f"response_type=code"
        f"&client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&scope={SCOPE}"
        f"&state={STATE}"
        f"&access_type=offline"
        f"&prompt=consent"
    )
    return f"{AUTH_URI}?{params}"


def exchange_code(code):
    resp = requests.post(TOKEN_URI, data={
        'code': code,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'redirect_uri': REDIRECT_URI,
        'grant_type': 'authorization_code',
    })
    resp.raise_for_status()
    return resp.json()


def main():
    # Start server
    server = HTTPServer(('0.0.0.0', 8081), CallbackHandler)
    t = threading.Thread(target=server.serve_forever)
    t.daemon = True
    t.start()

    auth_url = build_auth_url()

    # Write URL to file so it can be read even if stdout is buffered
    with open('oauth_url.txt', 'w') as f:
        f.write(auth_url + '\n')

    print()
    print('=' * 72)
    print('OPEN THIS URL IN YOUR WINDOWS BROWSER:')
    print()
    print(auth_url)
    print()
    print('(Also saved to oauth_url.txt in case the above is cut off)')
    print('=' * 72)
    print()
    print('Waiting for you to authenticate...')
    sys.stdout.flush()

    # Wait for callback (up to 5 minutes)
    server_done.wait(timeout=300)
    server.shutdown()

    if not auth_code:
        print('Timed out or no code received.')
        sys.exit(1)

    print('Got authorization code. Exchanging for token...')
    token_data = exchange_code(auth_code)

    if 'access_token' not in token_data:
        print('Error:', token_data)
        sys.exit(1)

    # Save as pickle (matching existing format)
    from google.oauth2.credentials import Credentials
    credentials = Credentials(
        token=token_data['access_token'],
        refresh_token=token_data.get('refresh_token'),
        token_uri=TOKEN_URI,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        scopes=[SCOPE],
    )

    with open('youtube_token.pickle', 'wb') as f:
        pickle.dump(credentials, f)

    # Also export JSON immediately
    token_json = json.dumps({
        'token': token_data['access_token'],
        'refresh_token': token_data.get('refresh_token'),
        'token_uri': TOKEN_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'scopes': [SCOPE],
    })

    with open('youtube_token.json', 'w') as f:
        f.write(token_json)

    print()
    print('=' * 72)
    print('SUCCESS! Token saved to youtube_token.pickle and youtube_token.json')
    print()
    print('YOUTUBE_TOKEN_JSON value for Streamlit Cloud Secrets:')
    print()
    print(f'YOUTUBE_TOKEN_JSON={token_json}')
    print()
    print('Add the above line to Streamlit Cloud -> App -> Settings -> Secrets')
    print('=' * 72)


if __name__ == '__main__':
    main()
