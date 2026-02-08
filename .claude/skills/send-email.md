# Skill: send-email

## Description
Send email via Gmail MCP server after approval.

## Phase
Silver (Functional Assistant)

## Trigger
- After email action is approved
- Called by execute-approved skill

## Instructions

You are sending an email. Follow these steps:

### 1. Verify Approval
Confirm the email send has been approved:
- Check file exists in /Approved
- Verify action type is email_send
- Extract all email parameters

### 2. Prepare Email
Gather parameters:
- `to`: Recipient email address
- `subject`: Email subject line
- `body`: Email body (can be HTML or plain text)
- `cc`: (optional) CC recipients
- `bcc`: (optional) BCC recipients
- `attachments`: (optional) File paths

### 3. Call Gmail MCP
```
Server: gmail
Tool: send_email
Parameters:
  to: [recipient]
  subject: [subject]
  body: [body]
  cc: [cc_list]
  bcc: [bcc_list]
  attachments: [file_paths]
```

### 4. Handle Response

#### On Success:
```json
{
  "timestamp": "[ISO]",
  "action_type": "email_send",
  "to": "[recipient]",
  "subject": "[subject]",
  "result": "success",
  "message_id": "[gmail_message_id]"
}
```

#### On Failure:
```json
{
  "timestamp": "[ISO]",
  "action_type": "email_send",
  "to": "[recipient]",
  "subject": "[subject]",
  "result": "failure",
  "error": "[error_message]"
}
```

### 5. Update Dashboard
Add to Recent Activity:
```
| [TIMESTAMP] | Email sent to [recipient] | Success |
```

### 6. Cleanup
- Move approval file to /Done
- Move related plan to /Done
- Update any related task files

## Error Handling
- If Gmail API fails, log error and alert user
- Do NOT retry automatically for auth errors
- Retry once for transient network errors

## Success Criteria
- Email delivered successfully
- Full audit trail logged
- Dashboard updated
- Files moved to /Done
