# Skill: create-plan

## Description
Analyze a task and create a Plan.md with objective, steps, and approval requirements.

## Phase
Silver (Functional Assistant)

## Trigger
- When processing tasks that require action
- Before any external action
- Complex multi-step tasks

## Instructions

You are creating an action plan. Follow these steps:

### 1. Analyze the Task
Read the task file and determine:
- What is being requested?
- What actions are needed?
- Are any sensitive actions required?
- What is the expected outcome?

### 2. Create Plan File
Create file in `/Plans/PLAN_[task_slug].md`:

```markdown
---
created: [ISO_TIMESTAMP]
task_source: [ORIGINAL_FILE]
status: awaiting_approval
approval_required: [yes/no]
---

# Plan: [OBJECTIVE]

## Objective
[Clear statement of what will be accomplished]

## Context
[Relevant background from the task]

## Steps
- [x] Analyze request
- [ ] [Step 1 description]
- [ ] [Step 2 description]
- [ ] [Step 3 description]
- [ ] Log completion

## Approval Required
[List any steps that need human approval]

## Expected Outcome
[What success looks like]

## Risks
[Any potential issues to be aware of]
```

### 3. Determine Approval Needs
Mark `approval_required: yes` if plan includes:
- Sending emails
- Posting to social media
- Making payments
- Contacting external parties
- Modifying business data

### 4. Update Dashboard
Add to Pending Tasks or In Progress as appropriate.

### 5. If Approval Needed
Create approval request file (see `request-approval` skill).

## Success Criteria
- Plan file created in /Plans
- All steps are clear and actionable
- Approval requirements identified
- Dashboard updated
