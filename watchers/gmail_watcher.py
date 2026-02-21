"""
Gmail Watcher Implementation
Monitors Gmail for new important emails and creates action files in Needs_Action folder.

SETUP (one-time):
1. Place client_secret.json in ../credentials/
2. Run: python ../credentials/gmail_auth_setup.py
3. This creates gmail_token.json automatically
4. Then run this watcher: python gmail_watcher.py
"""

import os
import sys
import logging
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from base_watcher import BaseWatcher

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class GmailWatcher(BaseWatcher):
    def __init__(self, vault_path: str, credentials_dir: str = None):
        super().__init__(vault_path, check_interval=120)  # Check every 2 minutes

        # Resolve credentials directory
        if credentials_dir:
            self.credentials_dir = Path(credentials_dir)
        else:
            self.credentials_dir = Path(__file__).parent.parent / 'credentials'

        self.token_path = self.credentials_dir / 'gmail_token.json'
        self.client_secret_path = self.credentials_dir / 'client_secret.json'
        self.processed_ids = set()
        self.service = None

        # Initialize Gmail service
        self._init_service()

    def _init_service(self):
        """Initialize Gmail API service with proper auth handling."""
        try:
            from google.oauth2.credentials import Credentials
            from google.auth.transport.requests import Request
            from googleapiclient.discovery import build
        except ImportError:
            self.logger.error(
                "Required packages not installed! Run:\n"
                "  pip install google-auth google-auth-oauthlib google-api-python-client"
            )
            raise SystemExit(1)

        SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

        # Check if token file exists
        if not self.token_path.exists():
            self.logger.error(
                f"gmail_token.json not found at: {self.token_path}\n"
                f"You must run the auth setup first:\n"
                f"  cd {self.credentials_dir}\n"
                f"  python gmail_auth_setup.py"
            )
            raise SystemExit(1)

        # Load credentials from token
        creds = Credentials.from_authorized_user_file(
            str(self.token_path), SCOPES
        )

        # Refresh if expired
        if creds.expired and creds.refresh_token:
            self.logger.info("Token expired, refreshing...")
            try:
                creds.refresh(Request())
                # Save refreshed token
                with open(self.token_path, 'w') as f:
                    f.write(creds.to_json())
                self.logger.info("Token refreshed and saved.")
            except Exception as e:
                self.logger.error(
                    f"Token refresh failed: {e}\n"
                    f"Re-run auth setup:\n"
                    f"  cd {self.credentials_dir}\n"
                    f"  python gmail_auth_setup.py"
                )
                raise SystemExit(1)

        if not creds.valid:
            self.logger.error(
                "Credentials are not valid. Re-run auth setup:\n"
                f"  cd {self.credentials_dir}\n"
                f"  python gmail_auth_setup.py"
            )
            raise SystemExit(1)

        # Build Gmail service
        self.service = build('gmail', 'v1', credentials=creds)
        self.logger.info("Gmail API service initialized successfully!")

    def check_for_updates(self) -> list:
        """Check for new important/unread emails"""
        try:
            results = self.service.users().messages().list(
                userId='me', q='is:unread is:important'
            ).execute()
            messages = results.get('messages', [])
            new_messages = [m for m in messages if m['id'] not in self.processed_ids]
            if new_messages:
                self.logger.info(f"Found {len(new_messages)} new unread important emails")
            return new_messages
        except Exception as e:
            self.logger.error(f'Error checking Gmail: {e}')
            return []

    def create_action_file(self, message) -> Path:
        """Create a markdown file for the new email in Needs_Action folder"""
        try:
            msg = self.service.users().messages().get(
                userId='me', id=message['id']
            ).execute()

            # Extract headers
            headers = {h['name']: h['value'] for h in msg['payload']['headers']}

            content = f'''---
type: email
from: {headers.get('From', 'Unknown')}
subject: {headers.get('Subject', 'No Subject')}
received: {datetime.now().isoformat()}
priority: high
status: pending
---


## Email Content
{msg.get('snippet', '')}


## Suggested Actions
- [ ] Reply to sender
- [ ] Forward to relevant party
- [ ] Archive after processing
'''
            # Ensure Needs_Action folder exists
            self.needs_action.mkdir(parents=True, exist_ok=True)

            filepath = self.needs_action / f'EMAIL_{message["id"]}.md'
            filepath.write_text(content)
            self.processed_ids.add(message['id'])
            self.logger.info(f'Created action file: {filepath.name}')
            return filepath
        except Exception as e:
            self.logger.error(f'Error creating action file: {e}')
            raise


def main():
    """Run the Gmail Watcher."""
    # Load environment variables
    try:
        from dotenv import load_dotenv
        env_path = Path(__file__).parent.parent / '.env'
        load_dotenv(env_path)
    except ImportError:
        pass  # dotenv is optional

    vault_path = os.getenv(
        'VAULT_PATH',
        str(Path(__file__).parent.parent)
    )

    print("=" * 50)
    print("Gmail Watcher - AI Employee")
    print("=" * 50)
    print(f"Vault: {vault_path}")
    print("Checking every 2 minutes for new important emails")
    print("Press Ctrl+C to stop")
    print("=" * 50)

    watcher = GmailWatcher(vault_path)
    watcher.run()


if __name__ == '__main__':
    main()
