---
id: "013"
title: Twitter Post 401 Fresh Token Attempt
stage: general
date: 2026-02-28
surface: agent
model: claude-sonnet-4-6
feature: none
branch: 1-bronze-phase
user: Syeda Gulzar Bano
command: create_twitter_post
labels: ["twitter","mcp","oauth","401","debugging"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - mcp-servers/twitter-mcp/server.py
tests:
  - Manual: tweepy.Client.create_tweet (DRY_RUN=false)
  - Manual: requests OAuth1 POST /2/tweets
  - Manual: requests OAuth1 GET /2/users/me
  - Manual: Bearer token GET /2/users/me
---

## Prompt

Use the Twitter MCP server tool `create_twitter_post` to post the following tweet: "Excited to share my AI Employee Vault project! 🚀"

The .env file has been updated with fresh Access Token and Access Token Secret regenerated after setting app permissions to Read+Write. Please attempt to post and return the full result including tweet ID or URL if successful, or the exact error message if it fails.

## Response snapshot

Tweet attempt failed with HTTP 401 Unauthorized at every authentication layer tested:

- `tweepy.Client.create_tweet()` → `401 Unauthorized / Unauthorized`
- `requests OAuth1 GET /2/users/me` → `401 {"title":"Unauthorized","status":401,"detail":"Unauthorized"}`
- `requests OAuth1 POST /2/tweets` → `401 {"title":"Unauthorized","status":401,"detail":"Unauthorized"}`
- `Bearer token GET /2/users/me` → `403 Unsupported Authentication` (expected — v2 user context cannot use app-only bearer for /users/me without user auth)

Credentials confirmed present in .env:
- TWITTER_API_KEY: len=25
- TWITTER_API_SECRET: len=50
- TWITTER_ACCESS_TOKEN: len=50 (starts with `2008909557792411648-`)
- TWITTER_ACCESS_TOKEN_SECRET: len=45
- TWITTER_BEARER_TOKEN: len=117
- DRY_RUN: false

## Outcome

- Impact: Tweet was NOT posted. 401 Unauthorized on all OAuth 1.0a user context calls.
- Tests: All manual auth tests returned 401
- Files: No files modified — diagnostic read-only run
- Next prompts: Regenerate Access Token + Secret once more in developer.twitter.com portal (Apps > Keys and Tokens > Regenerate), ensure the app has "Read and Write" permissions SAVED before regenerating, then retry
- Reflection: The 401 on even GET /users/me (read) confirms the token pair is invalid — most likely the tokens were regenerated BEFORE the permission change was fully saved, or the wrong app's tokens are in .env

## Evaluation notes (flywheel)

- Failure modes observed: OAuth1 Access Token / Secret mismatch with API Key / Secret — tokens regenerated before permission save propagated, or tokens belong to a different app
- Graders run and results (PASS/FAIL): Manual auth probe — FAIL
- Prompt variant (if applicable): none
- Next experiment: In developer portal — confirm app permission is "Read and Write", Save, then Regenerate Access Token and Secret, copy both fresh values, update .env, and retry
