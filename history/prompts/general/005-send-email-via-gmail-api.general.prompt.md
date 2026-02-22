---
id: "005"
title: Send Email via Gmail API
stage: general
date: 2026-02-22
surface: agent
model: claude-sonnet-4-6
feature: none
branch: 1-bronze-phase
user: Syeda Gulzar Bano
command: send email to syedagulzarbano@gmail.com
labels: ["gmail","email","oauth","send"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - credentials/gmail_auth_setup.py
  - credentials/gmail_token.json
tests:
  - Email sent successfully (Message ID: 19c8561b1125dcf4)
---

## Prompt

send email to syedagulzarbano@gmail.com
Subject Hi and Body How're You?

## Response snapshot

1. Identified that `gmail_token.json` had `gmail.readonly` scope only — cannot send.
2. User added `gmail.send` scope to `credentials/gmail_auth_setup.py` (SCOPES list).
3. Ran `python credentials/gmail_auth_setup.py` — OAuth browser flow completed, new token saved.
4. Sent email via Gmail API using `googleapiclient` with MIMEText:
   - To: syedagulzarbano@gmail.com
   - Subject: Hi
   - Body: How're You?
   - Message ID: 19c8561b1125dcf4

## Outcome

- ✅ Impact: Email delivered successfully to syedagulzarbano@gmail.com
- 🧪 Tests: Gmail API returned message ID confirming delivery
- 📁 Files: gmail_auth_setup.py (scope updated), gmail_token.json (refreshed)
- 🔁 Next prompts: Add Gmail send to MCP server, build draft-email approval flow
- 🧠 Reflection: Token scope must match intended action; readonly tokens silently block send operations

## Evaluation notes (flywheel)

- Failure modes observed: Token expired + wrong scope — required full re-auth
- Graders run and results (PASS/FAIL): Manual verification — PASS (message ID returned)
- Prompt variant (if applicable): none
- Next experiment (smallest change to try): Wrap Gmail send in a proper MCP tool so Claude can call it natively
