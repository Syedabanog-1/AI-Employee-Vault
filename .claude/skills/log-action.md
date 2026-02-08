# Skill: log-action

## Description
Write action record to daily log file for audit trail.

## Phase
Bronze (Foundation) - Used by all phases

## Trigger
- After any action completes
- Called by other skills
- System events

## Instructions

You are logging an action. Follow these steps:

### 1. Determine Log File
Path: `/Logs/YYYY-MM-DD.json`
Create if doesn't exist (as JSON array).

### 2. Create Log Entry
Standard log entry format:
```json
{
  "timestamp": "[ISO_8601_TIMESTAMP]",
  "action_type": "[action_type]",
  "actor": "[claude_code|watcher|orchestrator|human]",
  "target": "[target_identifier]",
  "parameters": {
    "key": "value"
  },
  "approval_status": "[auto|approved|rejected|n/a]",
  "approved_by": "[human|auto|n/a]",
  "result": "[success|failure|partial]",
  "error": "[error_message_if_failed]",
  "duration_ms": [milliseconds],
  "related_files": [
    "/path/to/file1.md",
    "/path/to/file2.md"
  ]
}
```

### 3. Action Types
Common action types:
- `task_created` - New task file created
- `task_processed` - Task was processed
- `task_completed` - Task moved to Done
- `plan_created` - Plan file created
- `approval_requested` - Approval file created
- `approval_granted` - File moved to Approved
- `approval_rejected` - File moved to Rejected
- `email_send` - Email sent
- `social_post` - Social media post
- `payment_execute` - Payment made
- `odoo_sync` - Odoo data synced
- `ceo_briefing` - Briefing generated
- `error` - Error occurred
- `system_start` - System started
- `system_stop` - System stopped

### 4. Append to Log
Read existing log file, parse JSON array, append new entry, write back.

If file doesn't exist:
```json
[
  {
    "timestamp": "...",
    ...
  }
]
```

### 5. Verify Write
Confirm log was written successfully.

## Log Retention
- Logs retained for minimum 90 days
- Old logs can be archived to /Logs/archive/

## Query Patterns
To find specific logs:
- By date: Read `/Logs/YYYY-MM-DD.json`
- By action: Filter by `action_type`
- By result: Filter by `result`

## Success Criteria
- Log entry written to correct date file
- All required fields populated
- Valid JSON format maintained
- Entry queryable for audits
