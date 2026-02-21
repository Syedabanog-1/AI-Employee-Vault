"""
LinkedIn Watcher Implementation
Monitors LinkedIn for new messages/notifications and creates action files in Needs_Action folder.

SETUP:
1. Go to: https://www.linkedin.com/developers/
2. Create a new App
3. Request access to "Sign In with LinkedIn using OpenID Connect" + "Share on LinkedIn"
4. Under Auth tab, get your Client ID and Client Secret
5. Run the auth setup: python linkedin_auth_setup.py
6. Put the access token in your .env file:
     LINKEDIN_CLIENT_ID=your_client_id
     LINKEDIN_CLIENT_SECRET=your_client_secret
     LINKEDIN_ACCESS_TOKEN=your_access_token
7. Run: python linkedin_watcher.py
"""

import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from base_watcher import BaseWatcher

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class LinkedInWatcher(BaseWatcher):
    """
    LinkedIn Watcher using LinkedIn API v2.

    Monitors:
    - New connection requests
    - New messages
    - Post engagement (comments, likes)
    """

    def __init__(self, vault_path: str):
        super().__init__(vault_path, check_interval=300)  # Check every 5 minutes
        self.processed_ids = set()

        # Load credentials
        self.access_token = os.getenv('LINKEDIN_ACCESS_TOKEN', '')
        self.client_id = os.getenv('LINKEDIN_CLIENT_ID', '')
        self.client_secret = os.getenv('LINKEDIN_CLIENT_SECRET', '')

        self.api_base = 'https://api.linkedin.com/v2'
        self.person_id = None

        self._validate_credentials()

    def _validate_credentials(self):
        """Check if LinkedIn credentials are configured."""
        if not self.access_token or self.access_token == 'your_linkedin_access_token':
            self.logger.error(
                "LinkedIn access token not configured!\n\n"
                "SETUP STEPS:\n"
                "1. Go to https://www.linkedin.com/developers/\n"
                "2. Create a new App (or use existing)\n"
                "3. Under 'Products' tab, request:\n"
                "   - 'Sign In with LinkedIn using OpenID Connect'\n"
                "   - 'Share on LinkedIn' (for posting)\n"
                "4. Under 'Auth' tab:\n"
                "   - Copy 'Client ID' -> LINKEDIN_CLIENT_ID in .env\n"
                "   - Copy 'Client Secret' -> LINKEDIN_CLIENT_SECRET in .env\n"
                "5. Generate an access token:\n"
                "   Run: python linkedin_auth_setup.py\n"
                "6. Copy the token -> LINKEDIN_ACCESS_TOKEN in .env\n"
                "7. Re-run this watcher"
            )
            raise SystemExit(1)

        # Verify token by getting profile
        try:
            import requests
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'X-Restli-Protocol-Version': '2.0.0'
            }
            response = requests.get(
                f'{self.api_base}/userinfo',
                headers=headers,
                timeout=30
            )

            if response.status_code == 401:
                self.logger.error(
                    "LinkedIn access token is expired or invalid!\n"
                    "Re-run: python linkedin_auth_setup.py\n"
                    "Then update LINKEDIN_ACCESS_TOKEN in .env"
                )
                raise SystemExit(1)

            if response.status_code == 200:
                profile = response.json()
                self.person_id = profile.get('sub', '')
                name = profile.get('name', 'Unknown')
                self.logger.info(f"Authenticated as: {name} (ID: {self.person_id})")
            else:
                self.logger.warning(
                    f"Could not verify token (status {response.status_code}). "
                    "Continuing anyway..."
                )

        except ImportError:
            self.logger.error("requests package not installed! Run: pip install requests")
            raise SystemExit(1)
        except Exception as e:
            self.logger.warning(f"Token verification failed: {e}. Continuing...")

    def check_for_updates(self) -> list:
        """Check LinkedIn for new activity."""
        updates = []

        # Check for new posts/engagement on your content
        updates.extend(self._check_posts())

        return updates

    def _check_posts(self) -> list:
        """Check for engagement on your LinkedIn posts."""
        try:
            import requests
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'X-Restli-Protocol-Version': '2.0.0'
            }

            # Get recent posts
            response = requests.get(
                f'{self.api_base}/ugcPosts?q=authors&authors=List(urn%3Ali%3Aperson%3A{self.person_id})&count=5',
                headers=headers,
                timeout=30
            )

            if response.status_code != 200:
                self.logger.debug(f"Posts API returned {response.status_code}")
                return []

            posts = response.json().get('elements', [])
            new_items = []

            for post in posts:
                post_id = post.get('id', '')
                if post_id not in self.processed_ids:
                    new_items.append({
                        'type': 'post_activity',
                        'post_id': post_id,
                        'data': post
                    })

            return new_items

        except Exception as e:
            self.logger.error(f"Error checking posts: {e}")
            return []

    def create_action_file(self, item) -> Path:
        """Create a markdown action file for LinkedIn activity."""
        try:
            item_type = item.get('type', 'unknown')
            item_id = item.get('post_id', '') or item.get('message_id', '') or \
                       datetime.now().strftime('%Y%m%d%H%M%S')

            if item_type == 'post_activity':
                return self._create_post_action(item, item_id)
            else:
                return self._create_generic_action(item, item_id)

        except Exception as e:
            self.logger.error(f"Error creating action file: {e}")
            raise

    def _create_post_action(self, item, item_id) -> Path:
        """Create action file for post activity."""
        data = item.get('data', {})
        text = data.get('specificContent', {}).get(
            'com.linkedin.ugc.ShareContent', {}
        ).get('shareCommentary', {}).get('text', 'No content')

        content = f'''---
type: linkedin_post
post_id: {item_id}
received: {datetime.now().isoformat()}
priority: medium
status: pending
---


## LinkedIn Post Activity
**Post ID:** {item_id}
**Detected:** {datetime.now().strftime('%Y-%m-%d %H:%M')}

### Post Content Preview
{text[:500]}


## Suggested Actions
- [ ] Check post engagement (likes, comments)
- [ ] Respond to comments
- [ ] Share insights from engagement
'''
        self.needs_action.mkdir(parents=True, exist_ok=True)
        filepath = self.needs_action / f'LINKEDIN_{item_id[:20]}.md'
        filepath.write_text(content)
        self.processed_ids.add(item_id)
        self.logger.info(f'Created action file: {filepath.name}')
        return filepath

    def _create_generic_action(self, item, item_id) -> Path:
        """Create generic action file for LinkedIn activity."""
        content = f'''---
type: linkedin_activity
item_id: {item_id}
activity_type: {item.get('type', 'unknown')}
received: {datetime.now().isoformat()}
priority: medium
status: pending
---


## LinkedIn Activity
**Type:** {item.get('type', 'Unknown')}
**ID:** {item_id}
**Detected:** {datetime.now().strftime('%Y-%m-%d %H:%M')}


## Suggested Actions
- [ ] Review activity
- [ ] Take appropriate action
- [ ] Mark as handled
'''
        self.needs_action.mkdir(parents=True, exist_ok=True)
        filepath = self.needs_action / f'LINKEDIN_{item_id[:20]}.md'
        filepath.write_text(content)
        self.processed_ids.add(item_id)
        self.logger.info(f'Created action file: {filepath.name}')
        return filepath


def main():
    """Run the LinkedIn Watcher."""
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

    print("=" * 50)
    print("LinkedIn Watcher - AI Employee")
    print("=" * 50)
    print(f"Vault: {vault_path}")
    print("Checking every 5 minutes for new LinkedIn activity")
    print("Press Ctrl+C to stop")
    print("=" * 50)

    watcher = LinkedInWatcher(vault_path)
    watcher.run()


if __name__ == '__main__':
    main()
