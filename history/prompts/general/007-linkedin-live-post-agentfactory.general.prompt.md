---
id: 007
title: LinkedIn Live Post - AgentFactory Report
stage: general
date: 2026-02-23
surface: agent
model: claude-sonnet-4-6
feature: none
branch: 1-bronze-phase
user: Syeda Gulzar Bano
command: make linkedin mcp server live send post about AgentFactory latest report
labels: ["linkedin", "mcp", "oauth", "social-media", "agentfactory"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - credentials/linkedin_auth_setup.py
tests:
  - manual: LinkedIn API call confirmed w_member_social scope active (422 on invalid URN, not 403)
---

## Prompt

make linkedin mcp server live  send post about AgentFactory latest report how it is benificaial

## Response snapshot

Diagnosed that the LinkedIn access token in .env has `w_member_social` scope (posting confirmed via test) but lacks `r_liteprofile` / `openid profile` scopes needed to resolve the person URN. Root cause: `linkedin_auth_setup.py` had a bug where `REDIRECT_URI` was set to `https://www.linkedin.com/developers/callback` but the local server listened on `localhost:9090` — so the OAuth callback was never received and the token was set manually without full scopes.

Fixed `credentials/linkedin_auth_setup.py`:
- Changed `REDIRECT_URI` to `http://localhost:9090/callback`
- Added pre-run banner reminding user to register the redirect URL in LinkedIn developer portal
- Added auto-update of `.env` after token exchange (no manual copy needed)

Post content (AgentFactory report) drafted and ready to send once fresh token is obtained.

## Outcome

- ✅ Impact: Auth script fixed; user has clear 3-step runbook to get fresh token and send post live
- 🧪 Tests: LinkedIn ugcPosts endpoint confirmed reachable; w_member_social scope active
- 📁 Files: credentials/linkedin_auth_setup.py updated
- 🔁 Next prompts: Re-run OAuth flow, then call create_linkedin_post tool to publish AgentFactory post
- 🧠 Reflection: LinkedIn opaque tokens cannot be JWT-decoded; always verify scopes by testing /v2/userinfo early in the flow

## Evaluation notes (flywheel)

- Failure modes observed: Redirect URI mismatch in auth script caused token to be set without full scopes; /v2/userinfo 403 masked the real issue
- Graders run and results (PASS/FAIL): Manual API scope test — PASS (422 not 403 on ugcPosts)
- Prompt variant (if applicable): none
- Next experiment (smallest change to try): After re-auth, confirm /v2/userinfo returns 200 before calling ugcPosts
