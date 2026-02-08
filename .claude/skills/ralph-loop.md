# Skill: ralph-loop

## Description
Continue multi-step task execution until complete using the Ralph Wiggum pattern.

## Phase
Gold (Autonomous Employee)

## Trigger
- Complex multi-step tasks
- Tasks requiring autonomous completion
- /ralph-loop command invocation

## Instructions

You are running in Ralph Wiggum autonomous mode. Follow these steps:

### 1. Understand Ralph Wiggum Pattern
The Ralph Wiggum pattern keeps Claude working until a task is truly complete:
- Claude works on task
- Claude tries to exit
- Stop hook checks: Is task done?
- NO → Re-inject prompt, continue working
- YES → Allow exit

### 2. Task State Tracking
Create/update state file at task start:
```markdown
# /In_Progress/[agent]/RALPH_[task_id].md
---
task_id: [unique_id]
started: [ISO_TIMESTAMP]
iteration: 1
max_iterations: 10
status: in_progress
---

## Task
[Original task description]

## Progress
- [x] Step completed
- [ ] Step pending

## Current Focus
[What Claude is working on now]
```

### 3. Completion Detection

#### Strategy 1: Promise-Based
Claude outputs when done:
```
<promise>TASK_COMPLETE</promise>
```
Stop hook detects this and allows exit.

#### Strategy 2: File Movement
Task is complete when:
- Task file moves from /Needs_Action to /Done
- State file shows all steps checked

### 4. Iteration Loop
For each iteration:
1. Read current state
2. Identify next uncompleted step
3. Execute the step
4. Update state file
5. Check if all steps complete
6. If not complete and under max_iterations, continue
7. If complete or max reached, exit

### 5. Error Handling
- Log each iteration attempt
- On error, increment retry counter
- After 3 retries on same step, escalate to human
- Never exceed max_iterations

### 6. Completion
When task is done:
1. Move task file to /Done
2. Update Dashboard
3. Log completion
4. Output completion signal

```json
{
  "timestamp": "[ISO]",
  "action_type": "ralph_loop_complete",
  "task_id": "[id]",
  "iterations": [count],
  "result": "success"
}
```

## Safety Rails
- Max 10 iterations by default
- Human escalation after 3 failures
- No sensitive actions without approval (even in loop)
- Full logging of each iteration

## Success Criteria
- Task completes end-to-end
- All steps executed in order
- Proper state tracking throughout
- Clean exit with completion signal
