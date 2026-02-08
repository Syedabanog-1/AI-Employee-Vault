"""
Gmail Watcher Implementation
Monitors Gmail for new important emails and creates action files in Needs_Action folder.
"""

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from base_watcher import BaseWatcher
from datetime import datetime
import logging
from pathlib import Path


class GmailWatcher(BaseWatcher):
    def __init__(self, vault_path: str, credentials_path: str):
        super().__init__(vault_path, check_interval=120)  # Check every 2 minutes
        self.credentials_path = Path(credentials_path)
        self.creds = Credentials.from_authorized_user_file(str(self.credentials_path))
        self.service = build('gmail', 'v1', credentials=self.creds)
        self.processed_ids = set()
        
    def check_for_updates(self) -> list:
        """Check for new important/unread emails"""
        try:
            results = self.service.users().messages().list(
                userId='me', q='is:unread is:important'
            ).execute()
            messages = results.get('messages', [])
            return [m for m in messages if m['id'] not in self.processed_ids]
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
            filepath = self.needs_action / f'EMAIL_{message["id"]}.md'
            filepath.write_text(content)
            self.processed_ids.add(message['id'])
            self.logger.info(f'Created action file: {filepath}')
            return filepath
        except Exception as e:
            self.logger.error(f'Error creating action file: {e}')
            raise