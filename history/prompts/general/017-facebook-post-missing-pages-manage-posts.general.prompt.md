---
id: "017"
title: Facebook Post Missing pages_manage_posts Permission
stage: general
date: 2026-02-28
surface: agent
model: claude-sonnet-4-6
feature: none
branch: 1-bronze-phase
user: Syeda Gulzar Bano
command: create_facebook_page_post
labels: ["facebook", "mcp", "oauth", "permissions", "api-error"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - mcp-servers/facebook-mcp/server.py
  - .env
tests:
  - Direct Facebook Graph API POST to /{page_id}/feed via python requests
  - Token debug via /debug_token endpoint
---

## Prompt

Use the Facebook MCP server tool `create_facebook_page_post` to post the following message: "Excited to share my AI Employee Vault project! 🚀"

The FACEBOOK_ACCESS_TOKEN in .env has been updated with a fresh token. Please attempt to post and return the full result including post ID or URL if successful, or the exact error message if it fails.

## Response snapshot

Executed the `create_facebook_page_post` logic using the credentials in `.env` (Page ID: `982053108328381`, token starting `EAA8vHlZBPcNEBQZBI3YRAKQicROsU...`).

**Result: FAILED — HTTP 403 OAuthException**

Exact error from Facebook Graph API v18.0:
```
(#200) If posting to a group, requires app being installed in the group, and
  either publish_to_groups permission with user token, or both pages_read_engagement
  and pages_manage_posts permission with page token; If posting to a page, requires
  both pages_read_engagement and pages_manage_posts as an admin with sufficient
  administrative permission
```

Token debug analysis:
- Token is VALID (is_valid: true), expires at 1772283600 (not expired)
- Type: USER token (not a Page token)
- `pages_read_engagement` IS present in scopes
- `pages_manage_posts` IS MISSING from scopes — this is the root cause
- Page `982053108328381` is in granular scopes for pages_read_engagement and pages_messaging, but NOT pages_manage_posts

## Outcome

- Impact: Facebook post attempt failed. Token lacks the `pages_manage_posts` permission required to publish to the page.
- Tests: Direct API call confirmed 403 error; debug_token call confirmed missing scope.
- Files: No files modified. Read `.env` and `mcp-servers/facebook-mcp/server.py` for diagnosis.
- Next prompts: Re-authorize the Facebook token including the `pages_manage_posts` scope; then also obtain a **Page Access Token** (not user token) for posting.
- Reflection: The token is fresh and valid, but was generated without the `pages_manage_posts` scope. The fix requires going through Facebook App's OAuth flow again and explicitly requesting this permission.

## Evaluation notes (flywheel)

- Failure modes observed: Missing OAuth scope (`pages_manage_posts`) on user token; token type is USER not PAGE — page tokens are generally preferred for page management actions.
- Graders run and results (PASS/FAIL): API call FAIL (403), token debug PASS (confirmed valid token, identified missing scope)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Re-run OAuth with `pages_manage_posts` added to requested scopes; exchange user token for a page-specific access token for page `982053108328381`
