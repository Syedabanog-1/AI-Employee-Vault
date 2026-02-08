# Implementation Plan: Bronze Phase - AI Employee Foundation

**Branch**: `1-bronze-phase` | **Date**: 2026-02-07 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/1-bronze-phase/spec.md`

## Summary

Build the foundation layer for the Personal AI Employee: an Obsidian vault with folder structure, core documents (Dashboard.md, Company_Handbook.md), a FileSystem Watcher to detect dropped files, and Claude Code integration to process tasks. All AI functionality will be packaged as reusable Agent Skills.

## Technical Context

**Language/Version**: Python 3.13+
**Primary Dependencies**: watchdog (filesystem monitoring), pathlib (file operations), json (logging)
**Storage**: Local filesystem (Obsidian vault - Markdown files)
**Testing**: Manual testing with file drops, pytest for unit tests
**Target Platform**: Windows 11 (primary), cross-platform compatible
**Project Type**: Single project - CLI scripts + Obsidian vault
**Performance Goals**: File detection within 5 seconds, task processing within 60 seconds
**Constraints**: Local-first, no external API calls in Bronze phase
**Scale/Scope**: Single user, ~100 tasks/day capacity

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Local-First & Privacy-First | ✅ PASS | All data stays in local vault |
| II. Human-in-the-Loop | ✅ PASS | Bronze has no sensitive actions (no HITL needed yet) |
| III. Watcher-Driven Perception | ✅ PASS | FileSystem Watcher creates task files |
| IV. Plan-Before-Act | ⚠️ N/A | Bronze processes simple tasks, planning in Silver |
| V. MCP-Based External Actions | ⚠️ N/A | No external actions in Bronze |
| VI. Graceful Degradation | ✅ PASS | Error handling in watcher and processing |
| VII. Audit Logging | ✅ PASS | All operations logged to /Logs |

**Gate Status**: ✅ PASSED - All applicable principles satisfied

## Project Structure

### Documentation (this feature)

```text
specs/1-bronze-phase/
├── spec.md              # Feature specification
├── plan.md              # This file
├── research.md          # Phase 0 research findings
├── data-model.md        # Entity definitions
├── quickstart.md        # Getting started guide
├── contracts/           # N/A for Bronze (no APIs)
└── checklists/
    └── requirements.md  # Quality checklist
```

### Source Code (repository root)

```text
AI_Employee_Vault_/
├── Dashboard.md                 # Real-time status (FR-002)
├── Company_Handbook.md          # AI behavior rules (FR-003)
├── Business_Goals.md            # Business objectives
├── Needs_Action/                # Incoming tasks (FR-001)
├── Done/                        # Completed tasks (FR-001)
├── Logs/                        # Audit logs (FR-009)
├── Inbox/                       # General inbox (FR-001)
├── Drop_Folder/                 # Watcher target (FR-001)
├── watchers/
│   ├── __init__.py
│   ├── base_watcher.py          # Base class (FR-004)
│   ├── filesystem_watcher.py    # File watcher (FR-004, FR-005)
│   └── orchestrator.py          # Process coordinator
├── .claude/
│   ├── skills/
│   │   ├── vault-init.md        # Skill 1 (FR-010)
│   │   ├── process-inbox.md     # Skill 2 (FR-006, FR-007, FR-008)
│   │   ├── update-dashboard.md  # Skill 3 (FR-007)
│   │   ├── summarize-file.md    # Skill 4
│   │   └── log-action.md        # Logging skill (FR-009)
│   └── mcp.json                 # MCP configuration
├── .env.example                 # Environment template
├── .gitignore                   # Security exclusions
└── requirements.txt             # Python dependencies

tests/
├── test_watcher.py              # Watcher unit tests
└── test_integration.py          # End-to-end tests
```

**Structure Decision**: Single project structure with watchers/ for Python scripts and .claude/skills/ for Agent Skills. Vault folders at root level for Obsidian compatibility.

## Complexity Tracking

> No violations - Bronze is intentionally simple per constitution tiered approach.

| Decision | Rationale | Alternative Rejected |
|----------|-----------|---------------------|
| Single watcher only | Bronze tier requirement | Multiple watchers (Silver) |
| No MCP servers | No external actions needed | Email MCP (Silver) |
| Manual Claude invocation | Keep simple for Bronze | Auto-trigger (Silver) |
