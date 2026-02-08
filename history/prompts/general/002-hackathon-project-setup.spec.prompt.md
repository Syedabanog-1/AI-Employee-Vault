---
id: 002
title: Hackathon 0 Project Complete Setup
stage: spec
date: 2026-02-07
surface: agent
model: claude-opus-4-5-20251101
feature: all-phases
branch: master
user: syeda-gulzar-bano
command: /sp.specify (all phases)
labels: ["hackathon", "ai-employee", "bronze", "silver", "gold", "platinum", "setup"]
links:
  spec: specs/1-bronze-phase/spec.md, specs/2-silver-phase/spec.md, specs/3-gold-phase/spec.md, specs/4-platinum-phase/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
  - specs/1-bronze-phase/spec.md
  - specs/1-bronze-phase/checklists/requirements.md
  - specs/2-silver-phase/spec.md
  - specs/2-silver-phase/checklists/requirements.md
  - specs/3-gold-phase/spec.md
  - specs/3-gold-phase/checklists/requirements.md
  - specs/4-platinum-phase/spec.md
  - specs/4-platinum-phase/checklists/requirements.md
  - Dashboard.md
  - Company_Handbook.md
  - Business_Goals.md
  - .claude/mcp.json
  - .env.example
  - .gitignore
  - requirements.txt
  - watchers/base_watcher.py
  - watchers/filesystem_watcher.py
  - watchers/gmail_watcher.py
  - watchers/orchestrator.py
  - .claude/skills/vault-init.md
  - .claude/skills/process-inbox.md
  - .claude/skills/update-dashboard.md
  - .claude/skills/create-plan.md
  - .claude/skills/request-approval.md
  - .claude/skills/execute-approved.md
  - .claude/skills/send-email.md
  - .claude/skills/post-linkedin.md
  - .claude/skills/generate-ceo-briefing.md
  - .claude/skills/ralph-loop.md
  - .claude/skills/odoo-sync.md
  - .claude/skills/log-action.md
  - .claude/skills/claim-task.md
  - .claude/skills/cloud-draft-email.md
  - .claude/skills/local-merge-updates.md
  - .claude/skills/error-recovery.md
tests:
  - N/A (specifications only)
---

## Prompt

Build app by following Hackathon 0 documents for Personal AI Employee. Create specifications for all phases (Bronze, Silver, Gold, Platinum) with Agent Skills, MCP server configurations, watcher scripts, and complete vault structure.

## Response snapshot

Created complete Personal AI Employee Hackathon 0 project structure:

### Constitution (v1.0.0)
- 7 core principles: Local-First, HITL, Watcher-Driven, Plan-Before-Act, MCP-Based Actions, Graceful Degradation, Audit Logging

### Phase Specifications
1. **Bronze Phase**: 4 user stories, 10 functional requirements, 4 Agent Skills
2. **Silver Phase**: 6 user stories, 13 functional requirements, 7 Agent Skills, 2 MCP Servers
3. **Gold Phase**: 7 user stories, 17 functional requirements, 9 Agent Skills, 5 MCP Servers
4. **Platinum Phase**: 7 user stories, 17 functional requirements, 12 Agent Skills (Cloud/Local split)

### Vault Structure
Created all required folders: Needs_Action, Done, Logs, Plans, Pending_Approval, Approved, Rejected, Accounting, Briefings, Updates, In_Progress/cloud, In_Progress/local, Signals

### Core Documents
- Dashboard.md - Real-time status
- Company_Handbook.md - AI behavior rules
- Business_Goals.md - Business objectives

### Agent Skills (16 total)
Bronze: vault-init, process-inbox, update-dashboard, log-action
Silver: create-plan, request-approval, execute-approved, send-email, post-linkedin
Gold: generate-ceo-briefing, ralph-loop, odoo-sync, error-recovery
Platinum: claim-task, cloud-draft-email, local-merge-updates

### Watcher Scripts
- base_watcher.py - Template class
- filesystem_watcher.py - Bronze phase
- gmail_watcher.py - Silver phase
- orchestrator.py - Master controller

### Configuration
- .claude/mcp.json - MCP server configs (9 servers)
- .env.example - Environment template
- .gitignore - Security exclusions
- requirements.txt - Python dependencies

## Outcome

- Impact: Complete hackathon project foundation created
- Tests: N/A (specifications phase)
- Files: 35+ files created
- Next prompts: /sp.plan for each phase, then /sp.tasks, then /sp.implement
- Reflection: Comprehensive setup enables rapid implementation

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment: Begin /sp.plan for Bronze phase
