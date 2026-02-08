# Skill: request-approval

## Description
Create an approval request file in /Pending_Approval for sensitive actions.

## Phase
Silver (Functional Assistant)

## Trigger
- Before any sensitive action
- When plan indicates approval_required: yes
- Payment, email, social media actions

## Instructions

You are requesting human approval. Follow these steps:

### 1. Identify Action Details
Gather all information about the pending action:
- Action type (email, payment, post, etc.)
- Target (recipient, account, platform)
- Content (message, amount, post text)
- Context (why this action is needed)

### 2. Create Approval File
Create file in `/Pending_Approval/[ACTION_TYPE]_[identifier]_[date].md`:

```markdown
---
type: approval_request
action: [email_send | payment | social_post | etc]
created: [ISO_TIMESTAMP]
expires: [ISO_TIMESTAMP + 24h]
status: pending
plan_ref: [/Plans/PLAN_xxx.md if applicable]
---

# Approval Request: [Brief Description]

## Action Details

**Type**: [Action type]
**Target**: [Recipient/Platform]
**Created**: [Timestamp]
**Expires**: [Timestamp]

## Content Preview

[Show exactly what will be sent/posted/paid]

---

## For Email:
**To**: [recipient@email.com]
**Subject**: [Email subject]
**Body**:
> [Email body text]

---

## For Payment:
**Amount**: $[amount]
**To**: [Recipient name]
**Account**: [Last 4 digits]
**Reference**: [Invoice/reason]

---

## For Social Post:
**Platform**: [LinkedIn/Facebook/Twitter/Instagram]
**Content**:
> [Post text]

**Hashtags**: [#tags]

---

## How to Respond

### To Approve
Move this file to `/Approved` folder.

### To Reject
Move this file to `/Rejected` folder.

### To Modify
Edit this file with changes, then move to `/Approved`.

---

*This request expires in 24 hours. After expiration, a new request must be created.*
```

### 3. Update Dashboard
Add entry to Pending Approvals section.

### 4. Wait
Do NOT proceed with the action. The system will detect when file is moved to /Approved.

## Success Criteria
- Approval file created with all details
- Dashboard shows pending approval
- No action taken until approved
