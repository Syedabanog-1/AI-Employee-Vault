---
id: "020"
title: Facebook Post AI Employee Vault Launch
stage: general
date: 2026-02-28
surface: agent
model: claude-sonnet-4-6
feature: none
branch: 1-bronze-phase
user: Syeda Gulzar Bano
command: create_facebook_page_post
labels: ["facebook", "mcp", "social-post", "bronze-phase"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - mcp-servers/facebook-mcp/server.py
tests:
  - Live Facebook Graph API post call (status 200, post ID returned)
---

## Prompt

Use the Facebook MCP server tool `create_facebook_page_post` to post the following message: "Excited to share my AI Employee Vault project! 🚀"

Please attempt to post and return the full result including post ID or URL if successful, or the exact error message if it fails.

## Response snapshot

The Facebook MCP server tool `create_facebook_page_post` was invoked with:
- message: "Excited to share my AI Employee Vault project! 🚀"
- page_id: 982053108328381
- DRY_RUN: false

The `/me/accounts` token resolution returned a 400 error (nonexisting field — expected for page tokens already in env), so the existing FACEBOOK_ACCESS_TOKEN was used directly as the page token.

POST to `https://graph.facebook.com/v18.0/982053108328381/feed` succeeded:

Result:
- success: true
- post_id: 982053108328381_122102715789274717
- page_id: 982053108328381
- url: https://www.facebook.com/982053108328381_122102715789274717
- timestamp: 2026-02-28

## Outcome

- Impact: Facebook page post published live with post ID 982053108328381_122102715789274717
- Tests: Live API call returned HTTP 200 with valid post ID
- Files: mcp-servers/facebook-mcp/server.py (invoked, no changes)
- Next prompts: Verify post visibility on Facebook page; consider posting to Instagram or Odoo next
- Reflection: Token resolution via /me/accounts returns 400 for page access tokens used directly; fallback to raw token works correctly

## Evaluation notes (flywheel)

- Failure modes observed: /me/accounts 400 (OAuthException code 100) — non-blocking, fallback used
- Graders run and results (PASS/FAIL): Live post PASS (HTTP 200, post ID present)
- Prompt variant (if applicable): none
- Next experiment: Test with a link attachment or image in the Facebook post
