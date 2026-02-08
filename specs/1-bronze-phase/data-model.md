# Data Model: Bronze Phase - AI Employee Foundation

**Date**: 2026-02-07
**Feature**: Bronze Phase

## Entities

### 1. Task File

**Description**: A markdown file representing a work item for the AI Employee to process.

**Location**: `/Needs_Action/` (pending) → `/Done/` (completed)

**Naming Convention**: `{TYPE}_{identifier}.md`
- Examples: `FILE_invoice.pdf.md`, `FILE_report.docx.md`

**Schema**:
```yaml
---
# Required fields
type: string          # file_drop | email | message | task
status: string        # pending | processing | done | error
timestamp: datetime   # ISO-8601 when created

# Optional fields
source: string        # Which watcher or manual
priority: string      # low | normal | high | urgent
original_name: string # Original filename (for file drops)
size_bytes: integer   # File size
file_type: string     # document | image | data | etc.
error: string         # Error message if status=error
processed_at: datetime # When processing completed
---

## Content

[Human-readable description of the task]

## Suggested Actions

- [ ] Action item 1
- [ ] Action item 2

## Notes

[Space for additional notes]
```

**Validation Rules**:
- `type` must be one of: file_drop, email, message, task
- `status` must be one of: pending, processing, done, error
- `timestamp` must be valid ISO-8601 datetime
- File must have `.md` extension

**State Transitions**:
```
pending → processing → done
pending → processing → error
pending → done (simple tasks)
```

---

### 2. Dashboard

**Description**: Real-time status document showing system state.

**Location**: `/Dashboard.md` (root of vault)

**Schema**:
```markdown
# AI Employee Dashboard

**Last Updated**: {ISO datetime}
**Status**: {Initialized | Active | Error | Offline}

---

## System Status

| Component | Status | Last Check |
|-----------|--------|------------|
| FileSystem Watcher | {status} | {datetime} |

---

## Pending Tasks

{List of files in /Needs_Action}

---

## In Progress

{List of files being processed}

---

## Recent Activity

| Timestamp | Action | Result |
|-----------|--------|--------|
| {datetime} | {action} | {Success|Failure} |

---

## Alerts

{Any error messages or warnings}

---

## Quick Stats

- **Tasks Today**: {count}
- **Tasks This Week**: {count}
- **Errors (24h)**: {count}
```

**Update Triggers**:
- Task created → Add to Pending Tasks
- Task processed → Add to Recent Activity, remove from Pending
- Error occurs → Add to Alerts
- Manual refresh → Update all sections

---

### 3. Company Handbook

**Description**: Rules document defining AI behavior constraints.

**Location**: `/Company_Handbook.md` (root of vault)

**Schema**:
```markdown
# Company Handbook - AI Employee Rules

**Version**: {semver}
**Last Updated**: {date}

---

## Core Rules (Non-Negotiable)

{List of absolute rules}

---

## Action Categories

### Auto-Approved Actions
{Actions AI can take without asking}

### Requires Human Approval
{Actions that need approval}

### Never Allowed
{Actions AI must never take}

---

## Response Templates

{Standard response formats}

---

## Escalation Rules

{When and how to escalate to human}
```

**Validation Rules**:
- Must have Core Rules section
- Must have Action Categories section
- Version must follow semver

---

### 4. Log Entry

**Description**: JSON record of an action or event.

**Location**: `/Logs/YYYY-MM-DD.json`

**Schema**:
```json
{
  "timestamp": "ISO-8601 datetime (required)",
  "action_type": "string (required)",
  "actor": "string (required)",
  "target": "string (optional)",
  "parameters": "object (optional)",
  "result": "success | failure | partial (required)",
  "error": "string (optional, if result != success)",
  "duration_ms": "integer (optional)",
  "related_files": ["array of paths (optional)"]
}
```

**Action Types (Bronze)**:
- `system_start` - System initialized
- `system_stop` - System stopped
- `task_created` - New task file created
- `task_processed` - Task was processed
- `task_completed` - Task moved to Done
- `dashboard_updated` - Dashboard refreshed
- `error` - Error occurred

**Validation Rules**:
- File must be valid JSON array
- Each entry must have timestamp, action_type, actor, result
- Timestamp must be ISO-8601

---

### 5. Agent Skill

**Description**: Reusable Claude Code skill definition.

**Location**: `/.claude/skills/{skill-name}.md`

**Schema**:
```markdown
# Skill: {name}

## Description
{What this skill does}

## Phase
{Bronze | Silver | Gold | Platinum}

## Trigger
{When to invoke this skill}

## Instructions

{Step-by-step instructions for Claude}

## Success Criteria
{How to verify the skill worked}
```

**Bronze Phase Skills**:
| Skill | Purpose |
|-------|---------|
| vault-init | Initialize/verify vault structure |
| process-inbox | Process files in /Needs_Action |
| update-dashboard | Refresh Dashboard.md |
| summarize-file | Generate summary for task |
| log-action | Write to daily log file |

---

## Relationships

```
┌─────────────────┐
│  Drop_Folder    │
│  (source)       │
└────────┬────────┘
         │ creates
         ▼
┌─────────────────┐      ┌─────────────────┐
│  Task File      │─────▶│  Log Entry      │
│  (Needs_Action) │      │  (Logs/)        │
└────────┬────────┘      └─────────────────┘
         │ processed
         ▼
┌─────────────────┐      ┌─────────────────┐
│  Task File      │─────▶│  Dashboard      │
│  (Done/)        │      │  (updated)      │
└─────────────────┘      └─────────────────┘
```

## File Naming Conventions

| Entity | Pattern | Example |
|--------|---------|---------|
| Task File | `{TYPE}_{identifier}.md` | `FILE_invoice.pdf.md` |
| Log File | `YYYY-MM-DD.json` | `2026-02-07.json` |
| Skill | `{skill-name}.md` | `process-inbox.md` |
