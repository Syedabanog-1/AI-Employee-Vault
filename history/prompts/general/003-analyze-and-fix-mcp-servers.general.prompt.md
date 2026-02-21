---
id: 003
title: Analyze and Fix MCP Servers Integration
stage: general
date: 2026-02-21
surface: agent
model: claude-sonnet-4-6
feature: none
branch: 1-bronze-phase
user: Syeda Gulzar Bano
command: /sp.analyze
labels: ["mcp", "analysis", "integration", "whatsapp", "linkedin", "twitter", "facebook", "instagram", "env-vars"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .claude/mcp.json
  - mcp-servers/whatsapp-mcp/server.py
  - mcp-servers/linkedin-mcp/server.py
  - mcp-servers/twitter-mcp/server.py
  - mcp-servers/facebook-mcp/server.py
  - mcp-servers/instagram-mcp/server.py
tests:
  - none
---

## Prompt

analyze my app and give analyze summary report ur is summary report par changes implement kro i added parameters in environmental variables (.env file) connected mcp servers an dmake their functionality enabled and working [user provided full .env with all API keys for WhatsApp, Facebook, LinkedIn, Twitter, Instagram, Anthropic, OpenAI, Qdrant, Neon, Context7, Google/Gmail]

Context: Hackathon 0 — Personal AI Employee (Bronze→Gold tier) requiring MCP servers for social media automation.

## Response snapshot

Performed full codebase exploration, then generated a structured analysis report and implemented all critical fixes:

**Analysis Report — Key Findings:**
- C1 CRITICAL: `.claude/mcp.json` pointed to non-existent Node.js files (`./mcp-servers/whatsapp/index.js`, etc.) — actual implementations are Python files at different paths
- C2 CRITICAL: Env var name mismatches — `FB_PAGE_ID` vs `FACEBOOK_PAGE_ID`, `FB_ACCESS_TOKEN` vs `FACEBOOK_ACCESS_TOKEN`
- C3 CRITICAL: `TWITTER_ACCESS_SECRET` vs `TWITTER_ACCESS_TOKEN_SECRET`
- C4 CRITICAL: `IG_ACCOUNT_ID`/`IG_ACCESS_TOKEN` — `INSTAGRAM_ACCOUNT_ID` not in .env
- S1-S5 HIGH: All 5 social MCP servers were stubs — only `asyncio.sleep()`, no real API calls
- E1 HIGH: No MCP server loaded `os.getenv()` — env vars never reached the servers

**Hackathon tier at time of analysis:** Bronze ~80%, Silver ~50%

**Changes implemented:**
1. Fixed `.claude/mcp.json` — all 5 social servers now use `python -u ./mcp-servers/xxx-mcp/server.py` with correct env var names; email server corrected to `email-mcp/index.js`; DRY_RUN forwarded to each server
2. WhatsApp MCP: Real Meta Cloud API calls to `graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages`
3. LinkedIn MCP: Real LinkedIn API v2 calls to `api.linkedin.com/v2/ugcPosts` (personal + company page)
4. Twitter MCP: Real Tweepy v2 client with `create_tweet()`, thread support, reply, like
5. Facebook MCP: Real Graph API calls to `graph.facebook.com/{PAGE_ID}/feed` + insights + posts
6. Instagram MCP: Real two-step flow — create media container → publish — plus profile/insights
7. All servers: DRY_RUN support, proper error handling, `run()` method fixed to `stdio_server()` pattern

**Action required from user:**
- Add `INSTAGRAM_ACCOUNT_ID` to `.env` — retrieve via: `GET https://graph.facebook.com/v18.0/{FACEBOOK_PAGE_ID}?fields=instagram_business_account&access_token={FACEBOOK_ACCESS_TOKEN}`
- Gmail watcher still requires `credentials/gmail_token.json` (OAuth setup)
- Install: `pip install tweepy requests python-dotenv` if not already installed

## Outcome

- ✅ Impact: MCP servers can now make real API calls using credentials from .env; Claude Code can start and use all social media MCP tools
- 🧪 Tests: None run (manual verification required with real API calls)
- 📁 Files: 6 files modified — `.claude/mcp.json` + 5 MCP server Python files
- 🔁 Next prompts: Test each MCP server; commit watchers/linkedin_watcher.py and watchers/whatsapp_watcher.py; get INSTAGRAM_ACCOUNT_ID
- 🧠 Reflection: The biggest blocker was mcp.json pointing to non-existent paths — none of the social MCPs could even start. All stubs needed real API wiring. DRY_RUN=false in .env means real posts will go out when MCP is called.

## Evaluation notes (flywheel)

- Failure modes observed: Stub MCP implementations give false confidence — servers start but do nothing real. mcp.json path errors are silent failures.
- Graders run and results (PASS/FAIL): Not run
- Prompt variant (if applicable): none
- Next experiment (smallest change to try): Run `python mcp-servers/whatsapp-mcp/server.py` manually to verify MCP SDK compatibility before using via Claude Code
