# Skill: error-recovery

## Description
Handle errors with retry logic, escalation, and graceful degradation.

## Phase
Gold (Autonomous Employee) - Used by all phases

## Trigger
- When any error occurs
- Called by other skills on failure
- System health checks

## Instructions

You are handling an error. Follow these steps:

### 1. Classify Error Type

| Category | Examples | Strategy |
|----------|----------|----------|
| Transient | Network timeout, rate limit, 503 | Exponential backoff retry |
| Authentication | Token expired, 401/403 | Pause + alert human |
| Logic | Bad input, parse error | Log + skip item |
| Data | Corrupted file, missing field | Quarantine + alert |
| System | Disk full, crash | Restart + alert |
| Payment | Any payment error | NEVER auto-retry |

### 2. Exponential Backoff (Transient Errors)
```python
delays = [1, 2, 4, 8, 16, 32, 60]  # seconds
max_retries = 3

for attempt in range(max_retries):
    try:
        execute_action()
        break
    except TransientError:
        if attempt < max_retries - 1:
            wait(delays[min(attempt, len(delays)-1)])
        else:
            escalate_to_human()
```

### 3. Authentication Errors
On auth failure:
1. Log the error with full context
2. Pause ALL operations for that service
3. Create alert in /Signals:
```markdown
# /Signals/AUTH_ERROR_[service].md
---
type: alert
severity: high
service: [gmail|linkedin|odoo|etc]
created: [timestamp]
---

## Authentication Error

Service [name] authentication failed.

**Error**: [error message]
**Action Required**: Re-authenticate or refresh token

## How to Fix
1. Check .env credentials
2. Refresh OAuth token if needed
3. Delete this file when resolved
```
4. Update Dashboard with alert

### 4. Data Errors
On corrupted/invalid data:
1. Move file to `/Signals/quarantine/`
2. Log error details
3. Continue with next item
4. Alert human for review

### 5. Payment Errors
SPECIAL RULES - NEVER auto-retry:
1. Log error immediately
2. Create high-priority alert
3. Require fresh human approval for retry
4. Never retry with same parameters

### 6. System Errors
On crash or system failure:
1. Watchdog detects via heartbeat
2. Attempt restart (max 3 times)
3. If restart fails, alert human
4. Log all restart attempts

### 7. Log All Errors
```json
{
  "timestamp": "[ISO]",
  "action_type": "error",
  "error_category": "[transient|auth|logic|data|system|payment]",
  "error_message": "[full error]",
  "context": {
    "action": "[what was being done]",
    "file": "[related file]",
    "retry_count": [N]
  },
  "resolution": "[retried|escalated|quarantined|skipped]"
}
```

### 8. Graceful Degradation
When component fails:
- Gmail down → Queue emails locally
- Odoo down → Skip accounting, continue other tasks
- LinkedIn down → Queue posts, retry later
- Claude unavailable → Watchers keep collecting

## Success Criteria
- Errors handled without system crash
- Appropriate escalation for serious errors
- Full error logging
- System continues operating where possible
