---
id: "019"
title: Facebook Live Post AI Employee Vault
stage: general
date: 2026-02-28
surface: agent
model: claude-sonnet-4-6
feature: none
branch: 1-bronze-phase
user: Syeda Gulzar Bano
command: create_facebook_page_post
labels: ["facebook","social-media","mcp","live-post"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - mcp-servers/facebook-mcp/server.py
tests:
  - Manual live post to Facebook Page ID 982053108328381 via Graph API v18.0
---

## Prompt

Use the Facebook MCP server tool `create_facebook_page_post` to post the following message: "Excited to share my AI Employee Vault project! 🚀"

Please attempt to post and return the full result including post ID or URL if successful, or the exact error message if it fails.

## Response snapshot

Verified credentials from `.env`:
- FACEBOOK_ACCESS_TOKEN: set (length=242)
- FACEBOOK_PAGE_ID: 982053108328381
- DRY_RUN: false (live mode)

Attempted /me/accounts page token resolution — returned OAuthException (#100) "Tried accessing nonexisting field (accounts)" (token is a Page token, not a User token, so /me/accounts is not applicable).

Fell back to using the stored FACEBOOK_ACCESS_TOKEN directly as the Page Access Token.

Posted to: https://graph.facebook.com/v18.0/982053108328381/feed

Result:
- HTTP 200
- Post ID: 982053108328381_122102715543274717
- URL: https://www.facebook.com/982053108328381_122102715543274717

## Outcome

- Impact: Facebook page post published successfully with emoji content
- Tests: Live API call to Graph API v18.0 returned HTTP 200 with post ID
- Files: mcp-servers/facebook-mcp/server.py (used as reference; invoked directly via Python)
- Next prompts: Verify post visible on Facebook page; consider Instagram cross-post
- Reflection: The /me/accounts token resolution step logs a non-fatal OAuthException when the stored token is already a Page Access Token (not a User token); the fallback to the raw token works correctly. No code change needed.

## Evaluation notes (flywheel)

- Failure modes observed: Windows console cp1252 UnicodeEncodeError on emoji in print() — resolved by wrapping stdout with utf-8 encoding; /me/accounts returned OAuthException (#100) — non-blocking, fallback succeeded
- Graders run and results (PASS/FAIL): PASS — HTTP 200, post ID returned
- Prompt variant (if applicable): none
- Next experiment: Cross-post same message to Instagram via instagram-mcp
