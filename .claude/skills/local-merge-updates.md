# Skill: local-merge-updates

## Description
Merge Cloud agent updates from /Updates into Dashboard.md (Local agent only).

## Phase
Platinum (Local Agent)

## Trigger
- When sync brings new files from Cloud
- On local agent startup
- Scheduled merge check

## Permissions
- Local agent OWNS Dashboard.md (single-writer rule)
- Cloud writes to /Updates, never to Dashboard

## Instructions

You are the Local agent merging updates. Follow these steps:

### 1. Check /Updates Folder
List all files in `/Updates/`:
- Files are created by Cloud agent
- Each contains status update information

### 2. Process Each Update
For each file in /Updates:

#### Read Update Content
```yaml
---
type: update
created: [timestamp]
agent: cloud
---

[Update content]
```

#### Extract Information
- What action was taken
- What's pending
- Any alerts or issues

### 3. Update Dashboard.md

#### Add to Recent Activity
```markdown
| [Update timestamp] | [Cloud: action description] | [Status] |
```

#### Update Pending Approvals
If update mentions pending approval:
```markdown
## Pending Approvals
- [NEW] [Action] - Created by Cloud - Review needed
```

#### Update System Status
If update mentions component status:
```markdown
| Cloud Agent | Active | [Last update time] |
```

### 4. Archive Processed Updates
Move processed update files:
```
From: /Updates/[filename]
To: /Updates/archive/[filename]
```

### 5. Log Merge
```json
{
  "timestamp": "[ISO]",
  "action_type": "merge_updates",
  "agent": "local",
  "updates_processed": [count],
  "result": "success"
}
```

### 6. Check Pending Approvals
After merge, review /Pending_Approval for items needing attention:
- List items drafted by Cloud
- Highlight urgent items

## Single-Writer Rule
- ONLY Local agent writes to Dashboard.md
- Cloud NEVER directly modifies Dashboard.md
- This prevents sync conflicts

## Success Criteria
- All updates processed
- Dashboard.md reflects current state
- Updates archived
- No merge conflicts
