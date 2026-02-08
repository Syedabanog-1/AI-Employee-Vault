# Feature Specification: Bronze Phase - AI Employee Foundation

**Feature Branch**: `1-bronze-phase`
**Created**: 2026-02-07
**Status**: Draft
**Input**: User description: "Bronze Phase - Foundation tier for Personal AI Employee with Obsidian vault, FileSystem Watcher, Claude Code integration, and Agent Skills"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Initialize AI Employee Vault (Priority: P1)

As a user, I want to set up my Obsidian vault with the required folder structure and core documents so that my AI Employee has a foundation to operate from.

**Why this priority**: This is the absolute foundation - nothing else works without the vault structure.

**Independent Test**: Open Obsidian, verify all folders exist, Dashboard.md and Company_Handbook.md are readable and properly formatted.

**Acceptance Scenarios**:

1. **Given** a fresh installation, **When** I open the vault in Obsidian, **Then** I see Dashboard.md as the main view with status sections
2. **Given** the vault is initialized, **When** I check the folder structure, **Then** /Needs_Action, /Done, /Logs, and /Inbox folders exist
3. **Given** Company_Handbook.md exists, **When** I read it, **Then** I see rules for AI behavior clearly defined

---

### User Story 2 - FileSystem Watcher Detects New Files (Priority: P1)

As a user, I want a Python watcher script that monitors a Drop_Folder and automatically creates task files in /Needs_Action when new files are dropped.

**Why this priority**: The Watcher is the AI's "eyes" - core perception capability.

**Independent Test**: Drop a file into Drop_Folder, verify a corresponding .md file appears in /Needs_Action within 5 seconds.

**Acceptance Scenarios**:

1. **Given** the watcher is running, **When** I drop "invoice.pdf" into Drop_Folder, **Then** a file "FILE_invoice.pdf.md" appears in /Needs_Action
2. **Given** a file is detected, **When** the watcher creates the task file, **Then** it includes YAML frontmatter with type, status, and timestamp
3. **Given** the watcher is running, **When** I drop multiple files, **Then** each gets a separate task file

---

### User Story 3 - Claude Code Processes Tasks (Priority: P1)

As a user, I want Claude Code to read files from /Needs_Action, process them, update Dashboard.md, and move completed files to /Done.

**Why this priority**: This is the AI "brain" actually doing work - core reasoning capability.

**Independent Test**: Place a task file in /Needs_Action, run Claude with the process prompt, verify Dashboard.md is updated and file moves to /Done.

**Acceptance Scenarios**:

1. **Given** a task file in /Needs_Action, **When** Claude processes it, **Then** Dashboard.md shows the task in Recent Activity
2. **Given** Claude has processed a task, **When** processing completes, **Then** the task file is moved to /Done
3. **Given** multiple task files exist, **When** Claude runs, **Then** all are processed in order and logged

---

### User Story 4 - Agent Skills for AI Functionality (Priority: P2)

As a user, I want all AI functionality packaged as reusable Agent Skills so I can easily invoke specific behaviors.

**Why this priority**: Skills make the AI modular and maintainable.

**Independent Test**: Run a skill command and verify it executes the expected behavior.

**Acceptance Scenarios**:

1. **Given** the vault-init skill exists, **When** I invoke it, **Then** the vault structure is created/verified
2. **Given** the process-inbox skill exists, **When** I invoke it, **Then** Claude processes all /Needs_Action files
3. **Given** the update-dashboard skill exists, **When** I invoke it, **Then** Dashboard.md is refreshed with current status

---

### Edge Cases

- What happens when Drop_Folder doesn't exist? Watcher should create it or fail gracefully with clear error.
- What happens when /Needs_Action has corrupted files? Claude should log error and skip, not crash.
- What happens when Dashboard.md is locked by Obsidian? System should retry or queue the update.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST create vault folder structure: /Needs_Action, /Done, /Logs, /Inbox, Drop_Folder
- **FR-002**: System MUST create Dashboard.md with sections: Pending Tasks, Recent Activity, System Status
- **FR-003**: System MUST create Company_Handbook.md with AI behavior rules
- **FR-004**: FileSystem Watcher MUST detect new files in Drop_Folder within 5 seconds
- **FR-005**: Watcher MUST create .md task files with YAML frontmatter (type, status, timestamp)
- **FR-006**: Claude MUST read and process all files in /Needs_Action
- **FR-007**: Claude MUST update Dashboard.md after processing each task
- **FR-008**: Claude MUST move processed files from /Needs_Action to /Done
- **FR-009**: System MUST log all operations to /Logs with timestamps
- **FR-010**: All AI functionality MUST be implemented as Agent Skills

### Key Entities

- **Task File**: Markdown file with YAML frontmatter representing work item (type, status, timestamp, source)
- **Dashboard**: Real-time status document showing pending tasks, recent activity, system health
- **Company Handbook**: Rules document defining AI behavior constraints and guidelines
- **Agent Skill**: Reusable Claude Code skill file defining specific AI capability

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Vault initialization completes in under 30 seconds
- **SC-002**: FileSystem Watcher detects and creates task files within 5 seconds of file drop
- **SC-003**: Claude processes a task file and updates Dashboard within 60 seconds
- **SC-004**: 100% of dropped files result in corresponding task files
- **SC-005**: 100% of processed tasks appear in Dashboard.md Recent Activity
- **SC-006**: Zero data loss - all original files preserved in /Done after processing
- **SC-007**: System remains stable for 24 hours of continuous watcher operation

## Agent Skills Required

### Skill 1: vault-init
**Purpose**: Initialize or verify vault folder structure and core documents
**Trigger**: Manual invocation or first-run detection

### Skill 2: process-inbox
**Purpose**: Process all files in /Needs_Action, update Dashboard, move to /Done
**Trigger**: Manual or scheduled invocation

### Skill 3: update-dashboard
**Purpose**: Refresh Dashboard.md with current system status
**Trigger**: After any task processing or manual invocation

### Skill 4: summarize-file
**Purpose**: Read a file and generate a summary for the task record
**Trigger**: Called by process-inbox for each task

## Assumptions

- User has Python 3.13+ installed for watcher scripts
- User has Claude Code CLI installed and configured
- User has Obsidian installed and can open the vault
- Watchdog Python library will be used for filesystem monitoring
- Windows is the primary platform (paths use Windows conventions)
