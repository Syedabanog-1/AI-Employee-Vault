# Skill: claim-task

## Description
Claim ownership of a task by moving it to /In_Progress/<agent>/ folder.

## Phase
Platinum (Distributed)

## Trigger
- When processing task from /Needs_Action
- Before starting work on any task
- Called by Cloud or Local agent

## Instructions

You are claiming a task. Follow these steps:

### 1. Identify Agent
Determine which agent you are:
- `cloud` - Running on cloud VM
- `local` - Running on user's local machine

### 2. Check If Already Claimed
Before claiming, verify task is not already claimed:
```
Check: /In_Progress/cloud/[filename]
Check: /In_Progress/local/[filename]
```

If file exists in either location → Task is claimed, SKIP IT.

### 3. Claim the Task
Move file atomically:
```
From: /Needs_Action/[filename]
To: /In_Progress/[agent]/[filename]
```

### 4. First Mover Wins
If two agents try to claim simultaneously:
- Only one move will succeed
- Check after move that file is in YOUR /In_Progress
- If not, another agent claimed it → Back off

### 5. Update State
Add claim metadata to the file:
```yaml
---
claimed_by: [agent]
claimed_at: [ISO_TIMESTAMP]
original_location: /Needs_Action/[filename]
---
```

### 6. Log Claim
```json
{
  "timestamp": "[ISO]",
  "action_type": "task_claimed",
  "agent": "[cloud|local]",
  "task": "[filename]",
  "result": "success"
}
```

### 7. Proceed with Work
Now you own this task. Process it according to your agent's permissions.

## Conflict Resolution
- First mover wins (file system atomic move)
- Losing agent must ignore the task
- No retry on conflict - move to next task
- Log all claim attempts for debugging

## Agent Permissions After Claim

| Agent | Can Draft | Can Execute | Can Approve |
|-------|-----------|-------------|-------------|
| Cloud | Yes | NO | NO |
| Local | Yes | Yes | Yes |

## Success Criteria
- Task moved to correct /In_Progress folder
- Claim metadata added
- No duplicate claims
- Log entry created
