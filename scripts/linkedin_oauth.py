#!/usr/bin/env python3
"""
LinkedIn OAuth 2.0 Token Generator — Two-step usage:

  Step 1 — Get the auth URL (opens browser):
      python scripts/linkedin_oauth.py

  Step 2 — Exchange the code for a token (after browser redirect):
      python scripts/linkedin_oauth.py --code AQXxxx...

Scopes: openid profile email w_member_social w_organization_social
"""

import os
import sys
import webbrowser
import urllib.parse
import requests
from pathlib import Path

try:
    from dotenv import load_dotenv, set_key
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "python-dotenv"])
    from dotenv import load_dotenv, set_key

ENV_FILE      = Path(__file__).parent.parent / ".env"
load_dotenv(ENV_FILE)

CLIENT_ID     = os.getenv("LINKEDIN_CLIENT_ID", "")
CLIENT_SECRET = os.getenv("LINKEDIN_CLIENT_SECRET", "")
REDIRECT_URI  = "https://www.linkedin.com/developers/tools/oauth/redirect"
SCOPES        = ["w_member_social", "r_liteprofile", "r_basicprofile"]
AUTH_URL      = "https://www.linkedin.com/oauth/v2/authorization"
TOKEN_URL     = "https://www.linkedin.com/oauth/v2/accessToken"


def step1_open_browser():
    """Print the auth URL and open it in the browser."""
    params = {
        "response_type": "code",
        "client_id":     CLIENT_ID,
        "redirect_uri":  REDIRECT_URI,
        "scope":         " ".join(SCOPES),
        "state":         "ai_employee_vault",
    }
    url = f"{AUTH_URL}?{urllib.parse.urlencode(params)}"

    print("=" * 65)
    print("  LinkedIn OAuth — Step 1: Authorize")
    print("=" * 65)
    print(f"  Scopes : {' '.join(SCOPES)}")
    print()
    print("  Opening browser... Approve the permissions on LinkedIn.")
    print("  After approval you'll land on a page titled:")
    print("  'OAuth 2.0 Redirect URL'")
    print()
    print("  Copy the 'code' value from that page, then run:")
    print(f"  python scripts/linkedin_oauth.py --code <PASTE_CODE_HERE>")
    print()
    print(f"  Auth URL:\n  {url}")
    webbrowser.open(url)


def step2_exchange_code(code: str):
    """Exchange auth code for access token and save to .env."""
    print("Exchanging auth code for access token...")
    resp = requests.post(
        TOKEN_URL,
        data={
            "grant_type":    "authorization_code",
            "code":          code,
            "redirect_uri":  REDIRECT_URI,
            "client_id":     CLIENT_ID,
            "client_secret": CLIENT_SECRET,
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=30,
    )

    if resp.status_code != 200:
        print(f"\nERROR {resp.status_code}: {resp.text}")
        sys.exit(1)

    data          = resp.json()
    access_token  = data.get("access_token", "")
    expires_in    = data.get("expires_in", 0)
    refresh_token = data.get("refresh_token", "")

    if not access_token:
        print(f"ERROR: No access_token in response: {data}")
        sys.exit(1)

    set_key(str(ENV_FILE), "LINKEDIN_ACCESS_TOKEN", access_token)
    set_key(str(ENV_FILE), "LINKEDIN_REDIRECT_URI",  REDIRECT_URI)
    if refresh_token:
        set_key(str(ENV_FILE), "LINKEDIN_REFRESH_TOKEN", refresh_token)

    days = int(expires_in) // 86400
    print(f"\nToken saved!  Expires in ~{days} days ({expires_in}s)")
    print(f"File: {ENV_FILE.name}")
    print("  LINKEDIN_ACCESS_TOKEN  ✅")
    if refresh_token:
        print("  LINKEDIN_REFRESH_TOKEN ✅")
    print("\nAll done! You can now post to LinkedIn.")


if __name__ == "__main__":
    if not CLIENT_ID or not CLIENT_SECRET:
        print("ERROR: LINKEDIN_CLIENT_ID / LINKEDIN_CLIENT_SECRET not set in .env")
        sys.exit(1)

    # Parse --code argument
    args = sys.argv[1:]
    code_value = None
    if "--code" in args:
        idx = args.index("--code")
        if idx + 1 < len(args):
            code_value = args[idx + 1]

    if code_value:
        step2_exchange_code(code_value)
    else:
        step1_open_browser()
