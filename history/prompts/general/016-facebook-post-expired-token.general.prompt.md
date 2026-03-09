---
id: "016"
title: Facebook Post via MCP - Expired Token
stage: general
date: 2026-02-28
surface: agent
model: claude-sonnet-4-6
feature: none
branch: 1-bronze-phase
user: Syeda Gulzar Bano
command: create_facebook_page_post
labels: ["facebook","mcp","token-expired","social-media"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - mcp-servers/facebook-mcp/server.py
tests:
  - Live Facebook Graph API POST to /feed endpoint
---

## Prompt

Use the Facebook MCP server tool to post the following message to the Facebook page: "Excited to share my AI Employee Vault project! 🚀"

The Facebook MCP server should have a tool like `create_facebook_post` or `post_to_facebook`. Please use it to post and return the full result including post ID or URL if successful, or the exact error message if it fails.

## Response snapshot

Invoked the `create_facebook_page_post` tool logic from `mcp-servers/facebook-mcp/server.py` directly against the Facebook Graph API v18.0.

- Page ID targeted: `982053108328381`
- DRY_RUN: false (live call made)
- HTTP Status: 400
- Facebook API Error Code: 190 (OAuthException, subcode 463)
- Error Message: "Error validating access token: Session has expired on Friday, 27-Feb-26 09:00:00 PST. The current time is Saturday, 28-Feb-26 03:20:04 PST."

The FACEBOOK_ACCESS_TOKEN stored in `.env` expired on 2026-02-27 09:00 PST. A new Page access token must be generated from the Facebook Developer console (Meta for Developers) and updated in `.env`.

## Outcome

- Impact: Facebook post was NOT published. Token needs to be refreshed.
- Tests: Live API call made — HTTP 400 with OAuthException returned.
- Files: mcp-servers/facebook-mcp/server.py (read, not modified)
- Next prompts: Refresh FACEBOOK_ACCESS_TOKEN in .env and retry the post.
- Reflection: Facebook Page access tokens expire after ~60 days (or sooner for short-lived tokens). Consider using a long-lived Page access token obtained via the Graph API token exchange.

## Evaluation notes (flywheel)

- Failure modes observed: Expired OAuth token (OAuthException code 190, subcode 463)
- Graders run and results (PASS/FAIL): API call FAIL — token expired
- Prompt variant (if applicable): none
- Next experiment: Generate a new long-lived Page access token from Meta for Developers and update FACEBOOK_ACCESS_TOKEN in .env
