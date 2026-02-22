"""
Gmail OAuth2 Setup Script
Run this ONCE to generate gmail_token.json for the Gmail Watcher.

Prerequisites:
1. Download client_secret.json from Google Cloud Console
2. Place it in this same folder (credentials/)
3. Run: python gmail_auth_setup.py
4. A browser window will open - sign in with your Google account
5. gmail_token.json will be created automatically
"""

import os
import sys
from pathlib import Path

# The scopes your Gmail Watcher needs

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.send']

def main():
    # Check for required packages
    try:
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.oauth2.credentials import Credentials
        from google.auth.transport.requests import Request
    except ImportError:
        print("ERROR: Required packages not installed!")
        print("Run this command first:")
        print("  pip install google-auth google-auth-oauthlib google-api-python-client")
        sys.exit(1)

    credentials_dir = Path(__file__).parent
    client_secret_path = credentials_dir / 'client_secret.json'
    token_path = credentials_dir / 'gmail_token.json'

    # Step 1: Check if client_secret.json exists
    if not client_secret_path.exists():
        print("=" * 60)
        print("ERROR: client_secret.json NOT FOUND!")
        print("=" * 60)
        print()
        print("You need to download it from Google Cloud Console:")
        print()
        print("1. Go to: https://console.cloud.google.com/")
        print("2. Select your project")
        print("3. Go to 'APIs & Services' > 'Credentials'")
        print("4. Click on your OAuth 2.0 Client ID")
        print("5. Click 'DOWNLOAD JSON'")
        print(f"6. Save the file as: {client_secret_path}")
        print()
        print("Then re-run this script.")
        sys.exit(1)

    # Step 2: Check if token already exists and is valid
    creds = None
    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)

    if creds and creds.valid:
        print("gmail_token.json already exists and is valid!")
        print("Your Gmail Watcher should work. No action needed.")
        return

    # Step 3: Refresh if expired
    if creds and creds.expired and creds.refresh_token:
        print("Token expired, refreshing...")
        try:
            creds.refresh(Request())
            print("Token refreshed successfully!")
        except Exception as e:
            print(f"Refresh failed: {e}")
            print("Running full auth flow...")
            creds = None

    # Step 4: Run full OAuth flow if needed
    if not creds:
        print("=" * 60)
        print("Starting Gmail OAuth2 Authentication")
        print("=" * 60)
        print()
        print("A browser window will open shortly.")
        print("Please sign in with your Google account and grant access.")
        print()

        flow = InstalledAppFlow.from_client_secrets_file(
            str(client_secret_path),
            SCOPES
        )
        creds = flow.run_local_server(port=0)
        print()
        print("Authentication successful!")

    # Step 5: Save the token
    with open(token_path, 'w') as token_file:
        token_file.write(creds.to_json())

    print(f"Token saved to: {token_path}")
    print()
    print("=" * 60)
    print("SETUP COMPLETE! Your Gmail Watcher can now authenticate.")
    print("=" * 60)


if __name__ == '__main__':
    main()
