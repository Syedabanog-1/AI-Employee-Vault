"""
WhatsApp Watcher Implementation
Monitors WhatsApp for new messages using Meta WhatsApp Business Cloud API
and creates action files in Needs_Action folder.

SETUP:
1. Go to: https://developers.facebook.com/
2. Create a Meta Developer App (Business type)
3. Add "WhatsApp" product to your app
4. Get your Access Token, Phone Number ID, and Business Account ID
5. Put them in your .env file:
     WHATSAPP_ACCESS_TOKEN=your_token
     WHATSAPP_PHONE_NUMBER_ID=your_phone_id
     WHATSAPP_BUSINESS_ACCOUNT_ID=your_biz_id
6. Set up a Webhook (see setup_webhook_server() below)
7. Run: python whatsapp_watcher.py
"""

import os
import sys
import json
import logging
import time
import threading
from pathlib import Path
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from base_watcher import BaseWatcher

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class WhatsAppWatcher(BaseWatcher):
    """
    WhatsApp Watcher using Meta Cloud API webhooks.

    Two modes:
    1. WEBHOOK MODE (recommended): Receives real-time messages via webhook
    2. POLLING MODE (fallback): Periodically checks for messages via API
    """

    def __init__(self, vault_path: str, mode: str = "polling"):
        super().__init__(vault_path, check_interval=30)
        self.mode = mode
        self.processed_ids = set()

        # Load credentials from environment
        self.access_token = os.getenv('WHATSAPP_ACCESS_TOKEN', '')
        self.phone_number_id = os.getenv('WHATSAPP_PHONE_NUMBER_ID', '')
        self.business_account_id = os.getenv('WHATSAPP_BUSINESS_ACCOUNT_ID', '')
        self.webhook_verify_token = os.getenv('WHATSAPP_WEBHOOK_VERIFY_TOKEN', 'ai_employee_verify')

        # Keyword triggers - only create action files for messages with these
        self.keywords = ['urgent', 'asap', 'invoice', 'payment', 'help',
                         'order', 'quote', 'price', 'meeting', 'deadline']

        # Message queue (for webhook mode)
        self.message_queue = []

        self._validate_credentials()

    def _validate_credentials(self):
        """Check if credentials are properly configured."""
        missing = []
        if not self.access_token or self.access_token == 'your_meta_access_token':
            missing.append('WHATSAPP_ACCESS_TOKEN')
        if not self.phone_number_id or self.phone_number_id == 'your_phone_number_id':
            missing.append('WHATSAPP_PHONE_NUMBER_ID')
        if not self.business_account_id or self.business_account_id == 'your_business_account_id':
            missing.append('WHATSAPP_BUSINESS_ACCOUNT_ID')

        if missing:
            self.logger.error(
                "WhatsApp credentials not configured!\n"
                f"Missing: {', '.join(missing)}\n\n"
                "SETUP STEPS:\n"
                "1. Go to https://developers.facebook.com/\n"
                "2. Create a Business App > Add WhatsApp product\n"
                "3. In WhatsApp > API Setup:\n"
                "   - Copy 'Temporary access token' -> WHATSAPP_ACCESS_TOKEN\n"
                "   - Copy 'Phone number ID' -> WHATSAPP_PHONE_NUMBER_ID\n"
                "   - Copy 'WhatsApp Business Account ID' -> WHATSAPP_BUSINESS_ACCOUNT_ID\n"
                "4. Add these to your .env file\n"
                "5. Re-run this watcher"
            )
            raise SystemExit(1)

        self.logger.info("WhatsApp credentials validated successfully!")

    def check_for_updates(self) -> list:
        """
        Check for new WhatsApp messages.
        In webhook mode: drain the message queue.
        In polling mode: call the API to get recent messages.
        """
        if self.mode == "webhook":
            # Drain queued messages from webhook
            messages = list(self.message_queue)
            self.message_queue.clear()
            return messages

        # Polling mode - use conversations API
        try:
            import requests

            url = f"https://graph.facebook.com/v21.0/{self.business_account_id}/conversations"
            headers = {"Authorization": f"Bearer {self.access_token}"}

            response = requests.get(url, headers=headers, timeout=30)

            if response.status_code == 401:
                self.logger.error(
                    "Access token expired or invalid!\n"
                    "Go to https://developers.facebook.com/ > Your App > WhatsApp > API Setup\n"
                    "Generate a new temporary access token and update .env"
                )
                return []

            if response.status_code != 200:
                self.logger.error(f"API error {response.status_code}: {response.text}")
                return []

            data = response.json()
            conversations = data.get('data', [])

            new_messages = []
            for conv in conversations:
                conv_id = conv.get('id', '')
                if conv_id not in self.processed_ids:
                    new_messages.append(conv)

            if new_messages:
                self.logger.info(f"Found {len(new_messages)} new conversations")
            return new_messages

        except ImportError:
            self.logger.error("requests package not installed! Run: pip install requests")
            return []
        except Exception as e:
            self.logger.error(f"Error checking WhatsApp: {e}")
            return []

    def create_action_file(self, message) -> Path:
        """Create a markdown action file for the WhatsApp message."""
        try:
            # Handle webhook format vs polling format
            if isinstance(message, dict) and 'webhook_data' in message:
                return self._create_from_webhook(message)
            else:
                return self._create_from_polling(message)
        except Exception as e:
            self.logger.error(f"Error creating action file: {e}")
            raise

    def _create_from_webhook(self, message) -> Path:
        """Create action file from webhook data."""
        data = message['webhook_data']
        sender = data.get('from', 'Unknown')
        text = data.get('text', {}).get('body', 'No text')
        msg_id = data.get('id', datetime.now().strftime('%Y%m%d%H%M%S'))
        timestamp = data.get('timestamp', datetime.now().isoformat())

        content = f'''---
type: whatsapp
from: {sender}
message_id: {msg_id}
received: {datetime.now().isoformat()}
priority: {"high" if any(kw in text.lower() for kw in self.keywords) else "medium"}
status: pending
---


## WhatsApp Message
**From:** {sender}
**Time:** {timestamp}

{text}


## Suggested Actions
- [ ] Reply to sender
- [ ] Create task from request
- [ ] Forward to relevant person
'''
        self.needs_action.mkdir(parents=True, exist_ok=True)
        filepath = self.needs_action / f'WHATSAPP_{msg_id}.md'
        filepath.write_text(content)
        self.processed_ids.add(msg_id)
        self.logger.info(f'Created action file: {filepath.name}')
        return filepath

    def _create_from_polling(self, conversation) -> Path:
        """Create action file from polling data."""
        conv_id = conversation.get('id', datetime.now().strftime('%Y%m%d%H%M%S'))

        content = f'''---
type: whatsapp
conversation_id: {conv_id}
received: {datetime.now().isoformat()}
priority: medium
status: pending
---


## WhatsApp Conversation
**Conversation ID:** {conv_id}
**Updated:** {conversation.get('updated_time', 'Unknown')}

New activity detected in this conversation.


## Suggested Actions
- [ ] Review conversation
- [ ] Reply if needed
- [ ] Mark as handled
'''
        self.needs_action.mkdir(parents=True, exist_ok=True)
        filepath = self.needs_action / f'WHATSAPP_{conv_id}.md'
        filepath.write_text(content)
        self.processed_ids.add(conv_id)
        self.logger.info(f'Created action file: {filepath.name}')
        return filepath

    def handle_webhook_event(self, body: dict):
        """Process incoming webhook event from Meta."""
        try:
            entry = body.get('entry', [{}])[0]
            changes = entry.get('changes', [{}])[0]
            value = changes.get('value', {})
            messages = value.get('messages', [])

            for msg in messages:
                msg_id = msg.get('id', '')
                if msg_id not in self.processed_ids:
                    self.message_queue.append({'webhook_data': msg})
                    self.logger.info(f"Queued webhook message: {msg_id}")

        except (IndexError, KeyError) as e:
            self.logger.error(f"Error parsing webhook: {e}")

    def start_webhook_server(self, port: int = 8080):
        """Start local webhook server (use with ngrok for external access)."""
        watcher = self

        class WebhookHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                """Handle webhook verification from Meta."""
                query = parse_qs(urlparse(self.path).query)
                mode = query.get('hub.mode', [None])[0]
                token = query.get('hub.verify_token', [None])[0]
                challenge = query.get('hub.challenge', [None])[0]

                if mode == 'subscribe' and token == watcher.webhook_verify_token:
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(challenge.encode())
                else:
                    self.send_response(403)
                    self.end_headers()

            def do_POST(self):
                """Handle incoming webhook messages."""
                content_length = int(self.headers.get('Content-Length', 0))
                body = json.loads(self.rfile.read(content_length))
                watcher.handle_webhook_event(body)
                self.send_response(200)
                self.end_headers()

            def log_message(self, format, *args):
                pass  # Suppress default logging

        server = HTTPServer(('0.0.0.0', port), WebhookHandler)
        self.logger.info(f"Webhook server running on port {port}")
        self.logger.info("Use ngrok to expose: ngrok http {port}")
        server.serve_forever()


def main():
    """Run the WhatsApp Watcher."""
    try:
        from dotenv import load_dotenv
        env_path = Path(__file__).parent.parent / '.env'
        load_dotenv(env_path)
    except ImportError:
        pass

    vault_path = os.getenv(
        'VAULT_PATH',
        str(Path(__file__).parent.parent)
    )

    # Choose mode: "polling" or "webhook"
    mode = os.getenv('WHATSAPP_WATCHER_MODE', 'polling')

    print("=" * 50)
    print("WhatsApp Watcher - AI Employee")
    print("=" * 50)
    print(f"Vault: {vault_path}")
    print(f"Mode: {mode}")
    print("Press Ctrl+C to stop")
    print("=" * 50)

    watcher = WhatsAppWatcher(vault_path, mode=mode)

    if mode == "webhook":
        port = int(os.getenv('WHATSAPP_WEBHOOK_PORT', '8080'))
        # Run webhook server in background thread
        webhook_thread = threading.Thread(
            target=watcher.start_webhook_server,
            args=(port,),
            daemon=True
        )
        webhook_thread.start()

    watcher.run()


if __name__ == '__main__':
    main()
