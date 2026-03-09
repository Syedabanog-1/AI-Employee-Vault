---
id: "021"
title: Odoo Get Contacts and Post Message
stage: general
date: 2026-02-28
surface: agent
model: claude-sonnet-4-6
feature: none
branch: 1-bronze-phase
user: Syeda Gulzar Bano
command: odoo_get_contacts + odoo_post_message
labels: ["odoo","mcp","contacts","message","chatter"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - mcp-servers/odoo-mcp/server.py
tests:
  - manual: odoo_get_contacts returned 1 contact successfully
  - manual: odoo_post_message returned success=true with message_id 104
---

## Prompt

Use the Odoo MCP server tools to:
1. First call `odoo_get_contacts` to get the list of contacts
2. Take the first contact from the result
3. Then call `odoo_post_message` to post the message "hi there today" on that first contact's record

Return the full result including contact name, record ID, and whether the message was posted successfully.

## Response snapshot

### Step 1 — odoo_get_contacts

```json
{
  "success": true,
  "count": 1,
  "contacts": [
    {
      "id": 8,
      "name": "Syeda Gulzar Bano",
      "email": "gulzar_bano@yahoo.com",
      "phone": false,
      "is_company": false
    }
  ]
}
```

First contact selected: **Syeda Gulzar Bano** (ID=8)

### Step 2 — odoo_post_message

```json
{
  "success": true,
  "message_id": 104,
  "model": "res.partner",
  "record_id": 8,
  "body": "hi there today",
  "timestamp": "2026-02-28T16:59:18.952300"
}
```

## Outcome

- Impact: Message "hi there today" successfully posted to Syeda Gulzar Bano's chatter on Odoo (res.partner ID=8); message_id=104
- Tests: Manual — both API calls returned success=true
- Files: mcp-servers/odoo-mcp/server.py (read-only, no edits)
- Next prompts: Test posting to a different model (e.g. sale.order); verify message visible in Odoo UI
- Reflection: The Odoo MCP server correctly chains XML-RPC (auth + contacts) with JSON-RPC session (message post). Single contact in DB is the owner account.

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): manual smoke test PASS
- Prompt variant (if applicable): none
- Next experiment: post a public message (note=false) and verify in Odoo chatter
