---
id: "015"
title: Twitter Post 402 No Credits
stage: general
date: 2026-02-28
surface: agent
model: claude-sonnet-4-6
feature: none
branch: 1-bronze-phase
user: Syeda Gulzar Bano
command: create_twitter_post
labels: ["twitter","mcp","402","api-credits","tweepy"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - mcp-servers/twitter-mcp/server.py
tests:
  - Manual: python tweepy create_tweet call executed live
---

## Prompt

Use the Twitter MCP server tool `create_twitter_post` to post the following tweet: "Excited to share my AI Employee Vault project! 🚀"

All 4 Twitter credentials have been freshly regenerated (API Key, API Secret, Access Token, Access Token Secret are all new values). The .env file has been updated. Please attempt to post and return the full result including tweet ID or URL if successful, or the exact error message if it fails.

## Response snapshot

All 5 Twitter env vars confirmed SET (API Key, API Secret, Access Token, Access Token Secret, Bearer Token). DRY_RUN=false.

Tweepy client built and `client.create_tweet()` called live against Twitter API v2.

**Result:**

```
ERROR: HTTPException: 402 Payment Required
Your enrolled account [2024823953982885888] does not have any credits to fulfill this request.
```

Tweet was NOT posted. No tweet ID or URL returned.

## Outcome

- Impact: Tweet failed — Twitter API v2 free tier account (ID 2024823953982885888) has exhausted its monthly write credits (25 tweets/month on Free tier), or requires a paid plan to use the `POST /2/tweets` endpoint.
- Tests: Live Tweepy `create_tweet` call executed; API returned HTTP 402.
- Files: No files modified; mcp-servers/twitter-mcp/server.py read and verified correct.
- Next prompts: Upgrade Twitter developer account to Basic ($100/month) or Pro tier to restore write access, then retry; or wait for monthly credit reset.
- Reflection: Credentials are correct and fully loaded — this is a billing/quota issue on the Twitter Developer Platform, not an auth or code issue.

## Evaluation notes (flywheel)

- Failure modes observed: 402 Payment Required — account has no remaining API write credits for this billing cycle.
- Graders run and results (PASS/FAIL): N/A — external API quota issue.
- Prompt variant (if applicable): null
- Next experiment: Upgrade developer plan at developer.twitter.com, then retest `create_tweet` with same credentials.
