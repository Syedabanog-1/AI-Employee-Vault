---
id: "012"
title: Twitter Post 401 After Clean Env Dedup
stage: general
date: 2026-02-28
surface: agent
model: claude-sonnet-4-6
feature: none
branch: 1-bronze-phase
user: Syeda Gulzar Bano
command: create_twitter_post
labels: ["twitter","oauth","401","debugging","mcp"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - mcp-servers/twitter-mcp/server.py
  - .env
tests:
  - manual: tweepy.Client.create_tweet (live Twitter API v2)
  - manual: requests_oauthlib OAuth1 verify_credentials (v1.1)
---

## Prompt

Use the Twitter MCP server tool `create_twitter_post` to post the following tweet: "Excited to share my AI Employee Vault project! 🚀"

The .env file has been cleaned up — duplicate TWITTER_ACCESS_TOKEN and TWITTER_ACCESS_TOKEN_SECRET entries have been removed. The correct (new, regenerated) tokens are now the only ones present. Please attempt to post and return the full result including tweet ID or URL if successful, or the exact error message if it fails.

## Response snapshot

Attempted to post the tweet via both the tweepy v2 client (Twitter API v2 `create_tweet`) and a raw OAuth 1.0a request against the v1.1 `verify_credentials` endpoint.

First attempt returned: `503 Backend unavailable, connection timeout` (transient Twitter server error).

Retry (after 5s pause) returned: `401 Unauthorized` via tweepy.

Direct OAuth 1.0a test against v1.1 returned: `{"errors":[{"code":32,"message":"Could not authenticate you."}]}`

Credential inspection confirmed:
- All four OAuth 1.0a credentials loaded correctly from .env with no hidden whitespace or truncation.
- ACCESS_TOKEN: `2008909557792411648-Z1wkc0W5hv6efyd1tFJ32cZUkXatEl` (50 chars, correct format)
- ACCESS_TOKEN_SECRET: `Dwfqtww3LT9vfxoNL6F4gctg8XHa05RtDdXiljJEsGyB9` (45 chars)
- API_KEY: `H5Bp46ru8idQK2EIEBJRzR5LH` (25 chars)
- API_SECRET: `59LB8LbA1GF5JFzl8FDKH5EJya3faR9apwzFLJlAeB8eSwcoGt` (51 chars)

**Result: FAILED — 401 Unauthorized (Twitter error code 32)**

## Outcome

- Impact: Tweet was NOT posted. Twitter rejected the OAuth 1.0a credentials with error code 32 ("Could not authenticate you").
- Tests: Live API calls made; both v1.1 and v2 endpoints returned 401/403.
- Files: No files modified.
- Next prompts: Regenerate access token + secret from developer.twitter.com → Apps → Keys and Tokens. Ensure app has "Read and Write" permissions BEFORE generating the tokens. Then update .env and retry.
- Reflection: Error code 32 typically means: (1) tokens were generated before app permissions were set to Read+Write, (2) tokens have been revoked/invalidated, or (3) system clock skew on the signing machine.

## Evaluation notes (flywheel)

- Failure modes observed: Twitter API 401 code 32 despite visually clean credentials; transient 503 on first attempt.
- Graders run and results (PASS/FAIL): Live API test — FAIL
- Prompt variant (if applicable): N/A
- Next experiment: Regenerate access token and secret in Twitter Developer Portal with Read+Write permissions confirmed first; update .env; retry post.
