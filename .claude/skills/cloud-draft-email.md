# Skill: cloud-draft-email

## Description
Draft email replies without sending (Cloud agent only).

## Phase
Platinum (Cloud Agent)

## Trigger
- Email task claimed by Cloud agent
- 24/7 email processing

## Permissions
- CAN: Draft emails, create approval requests
- CANNOT: Send emails, access local credentials

## Instructions

You are the Cloud agent drafting an email. Follow these steps:

### 1. Verify You Are Cloud
This skill is ONLY for Cloud agent. If running locally, use `send-email` skill instead.

### 2. Read Email Task
Parse the email task from /In_Progress/cloud/:
- Original sender
- Subject
- Content/snippet
- Context

### 3. Analyze and Draft
Based on the email content:
- Understand the request
- Determine appropriate response
- Draft professional reply

### 4. Create Draft Approval Request
Write to `/Pending_Approval/EMAIL_DRAFT_[id].md`:

```markdown
---
type: approval_request
action: email_send
created: [ISO_TIMESTAMP]
drafted_by: cloud
status: pending_local_approval
---

# Email Draft: Re: [Original Subject]

## Original Email
**From**: [sender]
**Subject**: [subject]
**Received**: [timestamp]

> [Original email content]

## Draft Reply

**To**: [recipient]
**Subject**: Re: [subject]

---

[Your drafted reply here]

---

## For Local Agent

When you come online:
1. Review this draft
2. Edit if needed
3. Move to /Approved to send
4. Or move to /Rejected to discard

*Drafted by Cloud Agent at [timestamp]*
```

### 5. Write to Updates
Create `/Updates/EMAIL_DRAFTED_[id].md`:
```markdown
---
type: update
created: [ISO_TIMESTAMP]
agent: cloud
---

Email draft created for: [subject]
Approval file: /Pending_Approval/EMAIL_DRAFT_[id].md
```

### 6. Log Action
```json
{
  "timestamp": "[ISO]",
  "action_type": "email_draft",
  "agent": "cloud",
  "subject": "[subject]",
  "result": "draft_created",
  "awaiting": "local_approval"
}
```

### 7. Move Task
Move original task to /Done (draft complete, awaiting approval).

## Important
- NEVER call send_email MCP
- NEVER access GOOGLE_REFRESH_TOKEN
- Always mark as pending_local_approval

## Success Criteria
- Draft created in /Pending_Approval
- Update written to /Updates
- Action logged
- No email actually sent
