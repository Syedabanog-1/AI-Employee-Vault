---
id: "022"
title: Add Playwright MCP Server
stage: general
date: 2026-03-09
surface: agent
model: claude-sonnet-4-6
feature: none
branch: 1-bronze-phase
user: Syeda Gulzar Bano
command: configure and connect playwright mcp server in this app
labels: ["mcp","playwright","browser-automation","configuration"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .claude/mcp.json
tests:
  - none
---

## Prompt

configure and connect playwright mcp server in this app

## Response snapshot

Added `playwright` entry to `.claude/mcp.json` using `@playwright/mcp@latest` via `npx`. No env vars required. User instructed to restart Claude Code to activate the server. Available tools after restart: `browser_navigate`, `browser_click`, `browser_screenshot`, `browser_fill`, etc.

## Outcome

- ✅ Impact: Playwright MCP server registered in `.claude/mcp.json`; headless browser automation now available after Claude Code restart
- 🧪 Tests: none — no code tests applicable for config-only change
- 📁 Files: `.claude/mcp.json` (1 entry added)
- 🔁 Next prompts: restart Claude Code, then test with `browser_navigate` to a URL
- 🧠 Reflection: Simple config addition; `@playwright/mcp` is the official Microsoft package with no required secrets

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): n/a
- Prompt variant (if applicable): n/a
- Next experiment (smallest change to try): test browser_screenshot after restart
