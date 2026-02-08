# Skill: vault-init

## Description
Initialize or verify the AI Employee vault folder structure and core documents.

## Phase
Bronze (Foundation)

## Trigger
- Manual invocation
- First-run detection
- System health check

## Instructions

You are initializing the AI Employee vault. Follow these steps:

### 1. Verify Folder Structure
Check that these folders exist, create if missing:
- `/Needs_Action` - Incoming tasks
- `/Done` - Completed tasks
- `/Logs` - Audit logs
- `/Inbox` - General inbox
- `/Drop_Folder` - File drop zone for watcher
- `/Plans` - Strategy documents (Silver+)
- `/Pending_Approval` - Awaiting human approval (Silver+)
- `/Approved` - Human-approved actions (Silver+)
- `/Rejected` - Human-rejected actions (Silver+)
- `/Accounting` - Financial data (Gold+)
- `/Briefings` - CEO reports (Gold+)
- `/Updates` - Cloud agent updates (Platinum)
- `/In_Progress/cloud` - Cloud claimed tasks (Platinum)
- `/In_Progress/local` - Local claimed tasks (Platinum)

### 2. Verify Core Documents
Check that these files exist:
- `Dashboard.md` - Real-time status
- `Company_Handbook.md` - AI behavior rules
- `Business_Goals.md` - Business objectives

### 3. Report Status
Update Dashboard.md with initialization status:
```markdown
| Timestamp | Action | Result |
|-----------|--------|--------|
| [NOW] | Vault structure verified | Success |
```

### 4. Output
Return a summary of:
- Folders verified/created
- Documents verified/created
- Any issues found

## Success Criteria
- All required folders exist
- All core documents are readable
- Dashboard.md is updated with status
