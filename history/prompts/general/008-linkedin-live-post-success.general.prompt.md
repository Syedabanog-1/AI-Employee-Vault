---
id: 008
title: LinkedIn Post Live - AgentFactory Report
stage: general
date: 2026-02-23
surface: agent
model: claude-sonnet-4-6
feature: none
branch: 1-bronze-phase
user: Syeda Gulzar Bano
command: make linkedin mcp server live send post about AgentFactory report
labels: ["linkedin", "oauth", "live-post", "agentfactory", "oidc"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - credentials/linkedin_auth_setup.py
  - .env
  - credentials/linkedin_token.json
tests:
  - live: POST urn:li:share:7431647570596347906 published successfully (HTTP 201)
---

## Prompt

make linkedin mcp server live send post about AgentFactory latest report how it is beneficial

## Response snapshot

Long debugging session resolving LinkedIn OAuth scope issues. Root cause: LinkedIn Token Generator issues non-OIDC tokens even when openid/profile scopes selected. Fixed by:
1. Updated `credentials/linkedin_auth_setup.py` to use `http://localhost:9090/callback` (localhost redirect)
2. Added "Sign In with LinkedIn using OpenID Connect" product to SyedaApp after app verification
3. Used full OAuth authorization code flow (not Token Generator) to get proper OIDC token
4. Retrieved person URN `urn:li:person:73e07l_ZKq` via `/v2/userinfo`
5. Posted AgentFactory report successfully (HTTP 201)

Post ID: urn:li:share:7431647570596347906
Posted as: Gulzar Bano Syeda

## Outcome

- ✅ Impact: AgentFactory report post published live on LinkedIn
- 🧪 Tests: HTTP 201 from ugcPosts API, post visible at profile activity
- 📁 Files: credentials/linkedin_auth_setup.py, .env, credentials/linkedin_token.json
- 🔁 Next prompts: Token valid 59 days; re-run auth script to refresh
- 🧠 Reflection: LinkedIn Token Generator does NOT produce OIDC-compatible tokens; always use full OAuth code flow for openid+profile scopes

## Evaluation notes (flywheel)

- Failure modes observed: Token Generator produces invalid tokens for OIDC endpoints; client secret mismatch (multiple apps confused user); SyedaApp2 created under wrong account
- Graders run and results (PASS/FAIL): Live API post — PASS (HTTP 201)
- Prompt variant (if applicable): none
- Next experiment (smallest change to try): Update linkedin-mcp server.py to use full OAuth flow instead of relying on manually-pasted tokens
