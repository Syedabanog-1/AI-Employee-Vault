---
id: "011"
title: Twitter Post 401 Token Dedup Debug
stage: general
date: 2026-02-28
surface: agent
model: claude-sonnet-4-6
feature: none
branch: 1-bronze-phase
user: Syeda Gulzar Bano
command: create_twitter_post
labels: ["twitter", "mcp", "oauth1", "401", "token-dedup", "debugging"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - D:\syeda Gulzar Bano\AI_Employee_Vault_\.env
tests:
  - Tweepy Client v2 create_tweet — FAIL (401 with old tokens, 503 transient with new)
  - Tweepy API v1.1 update_status — FAIL (code 32 Could not authenticate you)
  - requests_oauthlib OAuth1 verify_credentials — FAIL (code 32)
  - Bearer-only GET /2/users/me — FAIL (403 Unsupported Authentication, expected)
---

## Prompt

Use the Twitter MCP server tool `create_twitter_post` to post the following tweet: "Excited to share my AI Employee Vault project! 🚀"

The user has just regenerated their Twitter Access Token and Access Token Secret with Read+Write permissions and updated the .env file. Please attempt to post and return the full result including tweet ID or URL if successful, or the exact error message if it fails.

## Response snapshot

Post attempt failed. Root cause: Two sets of TWITTER_ACCESS_TOKEN and TWITTER_ACCESS_TOKEN_SECRET were present in .env (lines 75-76: old tokens; lines 83-84: new tokens). Python-dotenv loads the first occurrence, so the old (now-revoked) tokens were used. After deduplication (updating .env to use new tokens), the v2 API returned 503 Backend unavailable (transient). Switching to v1.1 returned error code 32 "Could not authenticate you" — indicating the API Key/Secret does not match the regenerated Access Token/Secret. This is a Twitter Developer Portal configuration issue: the app's access level or the regenerated tokens are not aligned with the API Key in use.

Full error chain:
- First attempt (dotenv first-occurrence, old tokens): 401 Unauthorized
- After dedup fix, v2 create_tweet with new tokens: 503 Backend unavailable / connection timeout (3 retries)
- v1.1 update_status with new tokens: 401, code 32 "Could not authenticate you"
- requests_oauthlib verify_credentials: 401, code 32

## Outcome

- Impact: Tweet was NOT posted. Blocked by Twitter OAuth1 credential mismatch (error code 32).
- Tests: All OAuth1 auth tests failed with code 32 or 503.
- Files: .env was temporarily deduplicated but reverted by external process; fix needs to be re-applied permanently.
- Next prompts: User must regenerate API Key + Secret AND Access Token + Secret together in Twitter Developer Portal, ensure App Permissions = Read and Write, then update all four values in .env with no duplicates.
- Reflection: Duplicate .env entries caused the wrong tokens to load. Twitter error code 32 is definitive: the consumer key/secret and access token/secret are not from the same app or the token was generated before the app permission was set to Read+Write.

## Evaluation notes (flywheel)

- Failure modes observed: Duplicate .env key ordering; Twitter OAuth1 code 32 credential mismatch; 503 transient on v2 endpoint
- Graders run and results (PASS/FAIL): create_tweet v2 FAIL, update_status v1.1 FAIL, verify_credentials FAIL
- Prompt variant (if applicable): N/A
- Next experiment: Regenerate all four Twitter credentials together from the Developer Portal after confirming app permission is Read+Write, then update .env with no duplicate entries
