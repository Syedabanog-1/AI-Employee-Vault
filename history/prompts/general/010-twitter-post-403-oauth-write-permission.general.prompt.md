---
id: "010"
title: Twitter Post AI Employee Vault 403 OAuth Write Permission
stage: general
date: 2026-02-28
surface: agent
model: claude-sonnet-4-6
feature: none
branch: 1-bronze-phase
user: Syeda Gulzar Bano
command: create_twitter_post
labels: ["twitter","mcp","oauth","403","debugging"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - mcp-servers/twitter-mcp/server.py
tests:
  - "manual: tweepy client.get_me() read auth check -- PASS"
  - "manual: client.create_tweet() -- FAIL 403 (read-only tokens)"
---

## Prompt

Use the Twitter MCP server tool to post the following tweet: "Excited to share my AI Employee Vault project! 🚀"

The Twitter MCP server should have a tool like `post_tweet`, `create_tweet`, or `create_twitter_post`. Please use it to post this tweet and return the result (tweet ID, URL, or any confirmation details).

## Response snapshot

Invoked `create_twitter_post` from `mcp-servers/twitter-mcp/server.py` with text "Excited to share my AI Employee Vault project! 🚀".

- Authentication check: PASS — authenticated as @SGulzarBano (tweepy get_me() succeeded)
- Tweet post: FAIL — 403 Forbidden: "Your client app is not configured with the appropriate oauth1 app permissions for this endpoint."
- Root cause: Access tokens were generated when the Twitter Developer App had Read-only permissions. Write access requires regenerating tokens after enabling Read+Write in the app settings.

Fix steps:
1. Twitter Developer Portal -> App -> Edit -> App permissions -> Read and Write
2. Keys and tokens -> Access Token and Secret -> Regenerate
3. Update TWITTER_ACCESS_TOKEN and TWITTER_ACCESS_TOKEN_SECRET in .env

## Outcome

- Impact: Tweet was NOT posted due to read-only OAuth token scope mismatch
- Tests: get_me() read check PASS; create_tweet() FAIL 403
- Files: mcp-servers/twitter-mcp/server.py (no changes needed — server code is correct)
- Next prompts: Re-run after regenerating tokens with Read+Write scope
- Reflection: Token scope is fixed at generation time; changing app permissions does not upgrade existing tokens

## Evaluation notes (flywheel)

- Failure modes observed: OAuth1 token generated with read-only scope blocks write endpoints even with valid credentials
- Graders run and results (PASS/FAIL): read auth PASS, write auth FAIL
- Prompt variant (if applicable): null
- Next experiment: Regenerate access tokens with Read+Write scope in Twitter Dev Portal, then retry create_twitter_post
