---
id: "009"
title: Twitter Post AI Employee Vault
stage: general
date: 2026-02-28
surface: agent
model: claude-sonnet-4-6
feature: none
branch: 1-bronze-phase
user: Syeda Gulzar Bano
command: create_twitter_post
labels: ["twitter","mcp","social-media","403-forbidden","api-permissions"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - mcp-servers/twitter-mcp/server.py
tests:
  - Manual API call via tweepy.Client.create_tweet (v2)
  - Manual API call via tweepy.API.update_status (v1.1)
---

## Prompt

Use the Twitter MCP server tool to post the following tweet: "Excited to share my AI Employee Vault project! 🚀"

The Twitter MCP server should have a tool like `post_tweet` or `create_tweet`. Please use it to post this tweet and return the result (tweet ID, URL, or any confirmation details).

## Response snapshot

Investigated `mcp-servers/twitter-mcp/server.py` — the relevant tool is `create_twitter_post`. Credentials were verified as fully loaded from `.env` (DRY_RUN=False, all 5 keys present). User `SGulzarBano` was confirmed authenticated via `client.get_me()`. However, both the Twitter API v2 (`client.create_tweet`) and v1.1 (`api.update_status`) returned errors:

- v2: `403 Forbidden` — "Your client app is not configured with the appropriate oauth1 app permissions for this endpoint."
- v1.1: `403 Forbidden` — error code 453 — "You currently have access to a subset of X API V2 endpoints and limited v1.1 endpoints only."

The tweet was NOT posted. The root cause is that the Twitter Developer App is on the **Free tier**, which does not allow posting tweets (write access). Only reading and limited OAuth/media endpoints are available.

## Outcome

- Impact: Tweet was not posted due to Twitter Developer App being on the Free tier (error code 453). Authentication and credentials are correct — the blocker is the API access level.
- Tests: Two approaches tested — Tweepy v2 Client and v1.1 API — both returned 403.
- Files: No files modified.
- Next prompts: Upgrade Twitter Developer App to Basic tier ($100/month) at https://developer.x.com/en/portal/product, then regenerate access tokens with Read+Write permission, update .env, and retry.
- Reflection: Twitter's free tier is severely restricted since the 2023 API changes. Posting tweets (write access) requires a paid plan.

## Evaluation notes (flywheel)

- Failure modes observed: Twitter Free tier does not allow tweet creation (write operations). Both API v2 and v1.1 blocked with 403/453. Credentials are valid but app permissions insufficient.
- Graders run and results (PASS/FAIL): Authentication check PASS (get_me returned SGulzarBano). Tweet post FAIL (403).
- Prompt variant (if applicable): N/A
- Next experiment: Upgrade app to Basic tier at developer.x.com, regenerate tokens with Read+Write scope, update TWITTER_ACCESS_TOKEN and TWITTER_ACCESS_TOKEN_SECRET in .env, then retry create_twitter_post.
