---
id: 004
title: LinkedIn Post Test - The Seventh Sky
stage: general
date: 2026-02-22
surface: agent
model: claude-sonnet-4-6
feature: none
branch: 1-bronze-phase
user: Syeda Gulzar Bano
command: post this message on linkedin post
labels: ["linkedin", "social-media", "mcp", "oauth", "debugging"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - (none modified)
tests:
  - (none)
---

## Prompt

post this message on linkedin post * This is test message  "The seventh Sky"* use linkedin mcp server

## Response snapshot

Attempted to post to LinkedIn via MCP server. Diagnosed ACCESS_DENIED 403 errors on all endpoints (me, userinfo, ugcPosts). Root cause: LINKEDIN_ACCESS_TOKEN was generated without required OAuth scopes (r_liteprofile, w_member_social, w_organization_social). LinkedIn API also now requires LinkedIn-Version header. Provided fix instructions: regenerate OAuth token with proper scopes via LinkedIn Developer Portal.

## Outcome

- Impact: Blocked — LinkedIn access token missing required OAuth scopes; post was not sent
- Tests: none run
- Files: no files modified
- Next prompts: Regenerate LinkedIn OAuth token with scopes r_liteprofile, w_member_social, w_organization_social, then retry post
- Reflection: LinkedIn OAuth scope requirements must be validated before attempting posts; token generation flow needs to be documented or scripted to avoid repeated 403 errors

## Evaluation notes (flywheel)

- Failure modes observed: ACCESS_DENIED 403 on all LinkedIn API endpoints due to missing OAuth scopes; LinkedIn-Version header not included in requests
- Graders run and results (PASS/FAIL): FAIL — post not delivered
- Prompt variant (if applicable): none
- Next experiment: Regenerate token with correct scopes and retest posting with LinkedIn-Version header set to 2025-01-01 or later
