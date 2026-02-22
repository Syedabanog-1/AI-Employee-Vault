"""
LinkedIn OAuth2 Setup Script
Run this ONCE to generate an access token for the LinkedIn Watcher.

Prerequisites:
1. Create a LinkedIn Developer App at https://www.linkedin.com/developers/
2. Under Products, request "Sign In with LinkedIn using OpenID Connect"
3. Under Auth tab, add redirect URL: https://www.linkedin.com/developers/callback
4. Copy Client ID and Client Secret into your .env file
5. Run this script: python linkedin_auth_setup.py
"""

import os
import sys
import webbrowser
import json
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

# Load .env
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent / '.env'
    load_dotenv(env_path)
except ImportError:
    pass


CLIENT_ID = os.getenv('LINKEDIN_CLIENT_ID', '') 
CLIENT_SECRET = os.getenv('LINKEDIN_CLIENT_SECRET', '')
REDIRECT_URI = 'https://www.linkedin.com/developers/callback'
SCOPES = 'openid profile email w_member_social'
TOKEN_FILE = Path(__file__).parent / 'linkedin_token.json'


def main():
    if not CLIENT_ID or CLIENT_ID == 'your_linkedin_client_id':
        print("=" * 60)
        print("ERROR: LINKEDIN_CLIENT_ID not set!")
        print("=" * 60)
        print()
        print("Steps to fix:")
        print("1. Go to https://www.linkedin.com/developers/")
        print("2. Create an App (or use existing)")
        print("3. Go to 'Auth' tab")
        print("4. Copy 'Client ID' and 'Client Secret'")
        print("5. Add to your .env file:")
        print("   LINKEDIN_CLIENT_ID=your_actual_client_id")
        print("   LINKEDIN_CLIENT_SECRET=your_actual_client_secret")
        print("6. IMPORTANT: Under 'Auth' > 'OAuth 2.0 settings':")
        print(f"   Add redirect URL: {REDIRECT_URI}")
        print()
        print("Then re-run this script.")
        sys.exit(1)

    if not CLIENT_SECRET or CLIENT_SECRET == 'your_linkedin_client_secret':
        print("ERROR: LINKEDIN_CLIENT_SECRET not set in .env!")
        sys.exit(1)

    print("=" * 60)
    print("LinkedIn OAuth2 Authentication")
    print("=" * 60)
    print()
    print("A browser window will open. Sign in with your LinkedIn account.")
    print()

    # Build auth URL
    auth_url = (
        f"https://www.linkedin.com/oauth/v2/authorization?"
        f"response_type=code&"
        f"client_id={CLIENT_ID}&"
        f"redirect_uri={REDIRECT_URI}&"
        f"scope={SCOPES}"
    )

    # Variable to store the auth code
    auth_code = [None]

    class CallbackHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            query = parse_qs(urlparse(self.path).query)
            code = query.get('code', [None])[0]
            error = query.get('error', [None])[0]

            if error:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(f"Error: {error}".encode())
                return

            if code:
                auth_code[0] = code
                self.send_response(200)
                self.send_header('Content-Type', 'text/html')
                self.end_headers()
                self.wfile.write(
                    b"<h1>Success!</h1>"
                    b"<p>LinkedIn authentication complete. You can close this window.</p>"
                )
            else:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"No code received")

        def log_message(self, format, *args):
            pass

    # Start callback server
    server = HTTPServer(('localhost', 9090), CallbackHandler)

    # Open browser
    webbrowser.open(auth_url)
    print("Waiting for authentication...")

    # Handle one request (the callback)
    server.handle_request()
    server.server_close()

    if not auth_code[0]:
        print("ERROR: No authorization code received!")
        sys.exit(1)

    print("Authorization code received! Exchanging for access token...")

    # Exchange code for token
    try:
        import requests
    except ImportError:
        print("ERROR: requests package required! Run: pip install requests")
        sys.exit(1)

    token_response = requests.post(
        'https://www.linkedin.com/oauth/v2/accessToken',
        data={
            'grant_type': 'authorization_code',
            'code': auth_code[0],
            'redirect_uri': REDIRECT_URI,
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET
        },
        timeout=30
    )

    if token_response.status_code != 200:
        print(f"ERROR: Token exchange failed: {token_response.text}")
        sys.exit(1)

    token_data = token_response.json()
    access_token = token_data.get('access_token', '')
    expires_in = token_data.get('expires_in', 0)

    # Save token
    with open(TOKEN_FILE, 'w') as f:
        json.dump(token_data, f, indent=2)

    print()
    print("=" * 60)
    print("AUTHENTICATION SUCCESSFUL!")
    print("=" * 60)
    print()
    print(f"Access Token (first 20 chars): {access_token[:20]}...")
    print(f"Expires in: {expires_in // 86400} days")
    print(f"Token saved to: {TOKEN_FILE}")
    print()
    print("NOW: Copy this token to your .env file:")
    print(f"  LINKEDIN_ACCESS_TOKEN={access_token}")
    print()
    print("Your LinkedIn Watcher should now work!")


if __name__ == '__main__':
    main()
