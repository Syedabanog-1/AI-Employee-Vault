# Skill: update-dashboard

## Description
Refresh Dashboard.md with current system status, pending tasks, and recent activity.

## Phase
Bronze (Foundation)

## Trigger
- After any task processing
- Manual invocation
- Scheduled refresh

## Instructions

You are updating the Dashboard. Follow these steps:

### 1. Gather Current State
- Count files in `/Needs_Action` (pending tasks)
- Count files in `/In_Progress` (active tasks)
- Count files in `/Pending_Approval` (awaiting human)
- Read recent entries from `/Logs`

### 2. Update System Status
Check status of each component:
- FileSystem Watcher: Check if process is running
- Gmail Watcher: Check if configured and running
- WhatsApp Watcher: Check if configured and running
- MCP Servers: Check configuration exists

### 3. Update Sections

#### Pending Tasks
List files from `/Needs_Action`:
```markdown
## Pending Tasks
- [FILENAME] - [TYPE] - [TIMESTAMP]
```

#### In Progress
List files from `/In_Progress`:
```markdown
## In Progress
- [FILENAME] - Claimed by [AGENT]
```

#### Recent Activity
Last 10 entries from logs:
```markdown
## Recent Activity
| Timestamp | Action | Result |
|-----------|--------|--------|
| ... | ... | ... |
```

#### Pending Approvals
List files from `/Pending_Approval`:
```markdown
## Pending Approvals
- [ACTION] - [DETAILS] - Move to /Approved to execute
```

### 4. Update Quick Stats
```markdown
## Quick Stats
- **Tasks Today**: [COUNT]
- **Tasks This Week**: [COUNT]
- **Pending Approvals**: [COUNT]
- **Errors (24h)**: [COUNT]
```

### 5. Set Timestamp
Update "Last Updated" at top of Dashboard.

## Success Criteria
- All sections reflect current state
- Timestamp is current
- No stale information displayed
