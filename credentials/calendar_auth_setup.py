"""
Google Calendar OAuth2 Setup Script
Run this ONCE to generate calendar_token.json for the Calendar MCP server.

Prerequisites:
1. client_secret.json already exists in this folder (same one used for Gmail)
2. Run: python calendar_auth_setup.py
3. A browser window will open — sign in with your Google account
4. calendar_token.json will be created automatically
"""

import os
import sys
from pathlib import Path

SCOPES = ['https://www.googleapis.com/auth/calendar']


def main():
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
    token_path = credentials_dir / 'calendar_token.json'

    if not client_secret_path.exists():
        print("=" * 60)
        print("ERROR: client_secret.json NOT FOUND!")
        print("=" * 60)
        print()
        print("Download it from Google Cloud Console:")
        print("1. Go to: https://console.cloud.google.com/")
        print("2. Select your project")
        print("3. APIs & Services > Credentials")
        print("4. Click your OAuth 2.0 Client ID > DOWNLOAD JSON")
        print(f"5. Save as: {client_secret_path}")
        sys.exit(1)

    creds = None
    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)

    if creds and creds.valid:
        print("calendar_token.json already exists and is valid!")
        print("Your Calendar MCP server should work. No action needed.")
        return

    if creds and creds.expired and creds.refresh_token:
        print("Token expired, refreshing...")
        try:
            creds.refresh(Request())
            print("Token refreshed successfully!")
        except Exception as e:
            print(f"Refresh failed: {e}")
            print("Running full auth flow...")
            creds = None

    if not creds:
        print("=" * 60)
        print("Starting Google Calendar OAuth2 Authentication")
        print("=" * 60)
        print()
        print("IMPORTANT: Make sure 'Google Calendar API' is enabled in your")
        print("Google Cloud Console project before proceeding.")
        print()
        print("A browser window will open shortly.")
        print("Please sign in and grant Calendar access.")
        print()

        flow = InstalledAppFlow.from_client_secrets_file(
            str(client_secret_path),
            SCOPES
        )
        creds = flow.run_local_server(port=0)
        print()
        print("Authentication successful!")

    with open(token_path, 'w') as token_file:
        token_file.write(creds.to_json())

    print(f"Token saved to: {token_path}")
    print()
    print("=" * 60)
    print("SETUP COMPLETE! Your Calendar MCP server can now authenticate.")
    print("=" * 60)
    print()
    print("Next step: Restart Claude Code so the calendar MCP server loads.")


if __name__ == '__main__':
    main()
