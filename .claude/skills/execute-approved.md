# Skill: execute-approved

## Description
Execute actions from approved requests using appropriate MCP servers.

## Phase
Silver (Functional Assistant)

## Trigger
- When file appears in /Approved folder
- Orchestrator detection
- Manual invocation with file path

## Instructions

You are executing an approved action. Follow these steps:

### 1. Read Approval File
Parse the approved request from `/Approved/[filename].md`:
- Extract action type
- Extract all parameters
- Verify not expired

### 2. Validate Approval
Check:
- File is in /Approved (not /Pending_Approval)
- Request has not expired
- All required parameters present

### 3. Execute via MCP
Based on action type, call appropriate MCP:

#### For Email (send-email skill)
```
MCP: gmail
Action: send_email
Params: to, subject, body, attachments
```

#### For Social Post (post-linkedin, post-facebook, etc.)
```
MCP: linkedin/facebook/twitter/instagram
Action: create_post
Params: content, media, hashtags
```

#### For Payment (Platinum - local only)
```
MCP: browser or bank-api
Action: execute_payment
Params: amount, recipient, reference
```

### 4. Handle Result

#### On Success:
- Log to `/Logs/YYYY-MM-DD.json`
- Update Dashboard Recent Activity
- Move approval file to /Done
- Move related plan to /Done

#### On Failure:
- Log error with full details
- Update Dashboard with alert
- Keep approval file for retry
- Notify user via Signals

### 5. Log Action
```json
{
  "timestamp": "[ISO]",
  "action_type": "[type]",
  "approval_file": "[filename]",
  "result": "success|failure",
  "details": "[execution details]",
  "approved_by": "human"
}
```

## Success Criteria
- Action executes successfully
- Full audit trail in logs
- Dashboard updated
- Files moved to /Done
