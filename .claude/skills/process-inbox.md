# Skill: process-inbox

## Description
Process all files in /Needs_Action folder, summarize them, update Dashboard, and move to /Done.

## Phase
Bronze (Foundation)

## Trigger
- Manual invocation
- Scheduled task
- Watcher notification

## Instructions

You are processing the inbox. Follow these steps:

### 1. Read /Needs_Action
List all files in the `/Needs_Action` folder.

### 2. For Each File
a. Read the file content
b. Parse YAML frontmatter if present
c. Determine the task type (email, file, message, etc.)
d. Generate a brief summary

### 3. Process Based on Type

#### For Simple Tasks (Bronze)
- Summarize the content
- Update Dashboard.md Recent Activity
- Move file to /Done

#### For Action-Required Tasks (Silver+)
- Create a Plan.md in /Plans
- If sensitive action needed, create approval request
- Do NOT execute until approved

### 4. Update Dashboard
Add entry to Recent Activity:
```markdown
| [TIMESTAMP] | Processed: [FILENAME] | [RESULT] |
```

### 5. Move to Done
Move the processed file from `/Needs_Action` to `/Done`

### 6. Log Action
Write to `/Logs/YYYY-MM-DD.json`:
```json
{
  "timestamp": "[ISO_TIMESTAMP]",
  "action_type": "process_task",
  "file": "[FILENAME]",
  "result": "success",
  "summary": "[BRIEF_SUMMARY]"
}
```

## Success Criteria
- All files in /Needs_Action are processed
- Dashboard.md is updated
- Files are moved to /Done
- Actions are logged
