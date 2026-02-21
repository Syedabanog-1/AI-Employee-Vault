---
id: 004
title: Run and Test MCP Servers
stage: general
date: 2026-02-21
surface: agent
model: claude-sonnet-4-6
feature: none
branch: 1-bronze-phase
user: Syeda Gulzar Bano
command: none
labels: ["mcp", "testing", "dry-run", "tweepy", "inputSchema", "fix"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - mcp-servers/whatsapp-mcp/server.py
  - mcp-servers/linkedin-mcp/server.py
  - mcp-servers/twitter-mcp/server.py
  - mcp-servers/facebook-mcp/server.py
  - mcp-servers/instagram-mcp/server.py
  - mcp-servers/calendar-mcp/server.py
  - mcp-servers/filesystem-mcp/server.py
tests:
  - DRY_RUN test all 5 social MCP servers (PASS)
  - stdio server start test all 5 servers (PASS - exit 124 = waiting for MCP input)
---

## Prompt

ok run

## Response snapshot

After the previous session (003) which implemented real API calls in all 5 social MCP servers, the user requested to run/test them.

**Issues found and fixed:**

1. **Missing dependency**: `tweepy` was not installed → `pip install tweepy` (v4.16.0 installed)

2. **MCP SDK compatibility** (CRITICAL): All 7 Python MCP server files used `input_schema=` (snake_case) but mcp SDK 1.24.0 requires `inputSchema=` (camelCase). Fixed 24 occurrences across 7 files using Python bulk replace.

**Test results:**

DRY_RUN test (all 5 passed):
- WhatsApp: PASS — `[DRY RUN] Would send: 'DRY_RUN test' to +923001234567`
- Facebook: PASS — `[DRY RUN] Would post to Facebook page 61588241532407`
- LinkedIn: PASS — `[DRY RUN] Would post to LinkedIn`
- Twitter: PASS — `[DRY RUN] Would tweet: 'DRY_RUN test tweet'`
- Instagram: PASS — `[DRY RUN] Would post to Instagram with caption`

stdio server start test (all 5 passed):
All servers started and blocked waiting for MCP input (exit code 124 = timeout = correct behavior)

**Credential check:**
All credentials loaded from .env:
- WhatsApp: 293ch token ✅
- LinkedIn: 350ch token ✅
- Twitter: all 5 keys ✅
- Facebook: 298ch token ✅
- Instagram: 202ch token + INSTAGRAM_ACCOUNT_ID 17ch ✅
- DRY_RUN = false (real API calls will go out when Claude Code calls these MCP tools)

## Outcome

- ✅ Impact: All 5 social MCP servers now pass DRY_RUN and stdio startup tests; ready for Claude Code integration
- 🧪 Tests: DRY_RUN + stdio start tests — all 5 PASSED
- 📁 Files: 7 files modified (24× input_schema→inputSchema fix)
- 🔁 Next prompts: Reload Claude Code to pick up MCP servers; test live API call on one platform; commit working watchers
- 🧠 Reflection: The `inputSchema` vs `input_schema` issue was a silent failure — servers imported fine but crashed at Tool() instantiation time, not at startup. Always verify SDK field names against the installed version.

## Evaluation notes (flywheel)

- Failure modes observed: `input_schema` → `inputSchema` is a breaking change in mcp SDK — no warning at import time, only fails when Tool() is constructed
- Graders run and results: DRY_RUN test PASS ×5, stdio start PASS ×5
- Prompt variant: "ok run" — minimal, action-oriented
- Next experiment: Run `claude mcp list` to confirm all servers are registered; then use a tool like `send_whatsapp_message` in a real Claude Code session
