# Feature Specification: Silver Phase - Functional AI Assistant

**Feature Branch**: `2-silver-phase`
**Created**: 2026-02-07
**Status**: Draft
**Input**: User description: "Silver Phase - Functional Assistant with 2+ Watchers, Planning workflow, MCP integration, Human-in-the-Loop approval, and Agent Skills"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Gmail Watcher Captures Emails (Priority: P1)

As a user, I want a Gmail Watcher that monitors my inbox for important/unread emails and creates task files in /Needs_Action.

**Why this priority**: Second perception channel expands AI's awareness.

**Independent Test**: Send an important email to monitored account, verify EMAIL_*.md file appears in /Needs_Action within 2 minutes.

**Acceptance Scenarios**:

1. **Given** Gmail Watcher is running, **When** an important unread email arrives, **Then** a task file is created in /Needs_Action
2. **Given** an email is captured, **When** the task file is created, **Then** it includes sender, subject, snippet, and timestamp in YAML frontmatter
3. **Given** Gmail Watcher is running, **When** a non-important email arrives, **Then** no task file is created (filtered out)

---

### User Story 2 - Claude Creates Plans Before Acting (Priority: P1)

As a user, I want Claude to create a Plan.md file in /Plans before taking any action, so I can review the strategy.

**Why this priority**: Planning is the key differentiator from Bronze - thinking before acting.

**Independent Test**: Place a task requiring action in /Needs_Action, verify Claude creates a Plan.md in /Plans with steps.

**Acceptance Scenarios**:

1. **Given** a task file exists, **When** Claude analyzes it, **Then** a Plan.md is created in /Plans with objective and steps
2. **Given** a plan requires approval, **When** Claude creates it, **Then** the plan includes "approval_required: yes" in frontmatter
3. **Given** multiple tasks exist, **When** Claude processes them, **Then** separate plans are created for each

---

### User Story 3 - Human-in-the-Loop Approval Workflow (Priority: P1)

As a user, I want sensitive actions to require my explicit approval by moving files between folders.

**Why this priority**: HITL is core to safe autonomous operation.

**Independent Test**: Claude creates approval request, user moves file to /Approved, action executes.

**Acceptance Scenarios**:

1. **Given** an action requires approval, **When** Claude prepares it, **Then** a file is created in /Pending_Approval with action details
2. **Given** user moves file to /Approved, **When** Orchestrator detects it, **Then** the action is executed
3. **Given** user moves file to /Rejected, **When** Orchestrator detects it, **Then** the action is cancelled and logged

---

### User Story 4 - Email MCP Server Sends Emails (Priority: P1)

As a user, I want Claude to send emails through an MCP server after I approve the action.

**Why this priority**: First external action capability - the AI's "hands".

**Independent Test**: Approve an email send, verify email is sent and action is logged.

**Acceptance Scenarios**:

1. **Given** an email action is approved, **When** MCP executes, **Then** the email is sent to the recipient
2. **Given** MCP sends an email, **When** complete, **Then** the action is logged to /Logs with timestamp and result
3. **Given** email send fails, **When** MCP reports error, **Then** the error is logged and user is notified via Dashboard

---

### User Story 5 - Audit Logging (Priority: P2)

As a user, I want all actions logged to JSON files for audit and debugging.

**Why this priority**: Logging enables accountability and troubleshooting.

**Independent Test**: Perform various actions, verify /Logs/YYYY-MM-DD.json contains all entries.

**Acceptance Scenarios**:

1. **Given** any action is taken, **When** it completes, **Then** an entry is added to today's log file
2. **Given** a log entry is created, **When** I read it, **Then** it includes timestamp, action_type, status, and approval info
3. **Given** multiple actions occur, **When** I review logs, **Then** I can trace the complete workflow

---

### User Story 6 - LinkedIn Auto-Posting (Priority: P2)

As a user, I want Claude to automatically post business updates to LinkedIn after my approval.

**Why this priority**: Social media automation generates business value.

**Independent Test**: Approve a LinkedIn post, verify it appears on LinkedIn profile.

**Acceptance Scenarios**:

1. **Given** a LinkedIn post is drafted, **When** I approve it, **Then** it is posted via LinkedIn MCP
2. **Given** a post is scheduled, **When** the schedule time arrives, **Then** an approval request is created
3. **Given** posting fails, **When** MCP reports error, **Then** the error is logged and I am notified

---

### Edge Cases

- What happens when Gmail API token expires? System should alert user and pause Gmail watching.
- What happens when MCP server crashes? Orchestrator should restart it and retry pending actions.
- What happens when approval file is corrupted? System should quarantine and alert.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST support 2+ Watchers running concurrently (FileSystem + Gmail minimum)
- **FR-002**: Gmail Watcher MUST use OAuth2 for authentication
- **FR-003**: Gmail Watcher MUST filter for important/unread emails only
- **FR-004**: System MUST create /Plans folder for strategy documents
- **FR-005**: Claude MUST create Plan.md before any non-trivial action
- **FR-006**: Plans MUST include objective, steps with checkboxes, and approval requirements
- **FR-007**: System MUST create /Pending_Approval, /Approved, /Rejected folders
- **FR-008**: Sensitive actions MUST wait for file movement to /Approved before executing
- **FR-009**: Email MCP server MUST support send, draft, and search operations
- **FR-010**: All MCP actions MUST be logged to /Logs/YYYY-MM-DD.json
- **FR-011**: LinkedIn MCP server MUST support post creation
- **FR-012**: All AI functionality MUST be implemented as Agent Skills
- **FR-013**: Basic scheduling MUST be supported via cron or Task Scheduler

### Key Entities

- **Plan**: Strategy document with objective, steps, approval status, and expected outcomes
- **Approval Request**: File in /Pending_Approval containing action details awaiting human decision
- **MCP Server**: External action executor exposing capabilities via Model Context Protocol
- **Audit Log**: JSON file containing timestamped records of all actions and decisions
- **Agent Skill**: Reusable Claude Code skill for specific AI functionality

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Gmail Watcher captures important emails within 2 minutes of arrival
- **SC-002**: Claude creates plans for 100% of tasks requiring action
- **SC-003**: Zero sensitive actions execute without explicit user approval
- **SC-004**: Email send success rate exceeds 95% for approved actions
- **SC-005**: All actions are logged within 5 seconds of completion
- **SC-006**: LinkedIn posts publish within 30 seconds of approval
- **SC-007**: System handles 50+ tasks per day without performance degradation

## Agent Skills Required

### Skill 1: gmail-watcher-control
**Purpose**: Start, stop, and check status of Gmail Watcher
**Trigger**: Manual invocation or system startup

### Skill 2: create-plan
**Purpose**: Analyze a task and create a Plan.md with steps
**Trigger**: When processing tasks from /Needs_Action

### Skill 3: request-approval
**Purpose**: Create approval request file in /Pending_Approval
**Trigger**: Before any sensitive action

### Skill 4: execute-approved
**Purpose**: Execute actions from /Approved folder via MCP
**Trigger**: When files appear in /Approved

### Skill 5: send-email
**Purpose**: Send email via Email MCP server
**Trigger**: After email action is approved

### Skill 6: post-linkedin
**Purpose**: Post to LinkedIn via LinkedIn MCP server
**Trigger**: After LinkedIn post is approved

### Skill 7: log-action
**Purpose**: Write action record to daily log file
**Trigger**: After any action completes

## MCP Servers Required

### Email MCP
- **Operations**: send_email, draft_email, search_emails
- **Authentication**: Google OAuth2
- **Configuration**: GMAIL_CLIENT_ID, GMAIL_CLIENT_SECRET, GMAIL_REFRESH_TOKEN

### LinkedIn MCP
- **Operations**: create_post, get_profile
- **Authentication**: LinkedIn OAuth2
- **Configuration**: LINKEDIN_CLIENT_ID, LINKEDIN_CLIENT_SECRET, LINKEDIN_ACCESS_TOKEN

## Assumptions

- Bronze Phase is fully operational
- User has Gmail account with API access enabled
- User has LinkedIn account with API access enabled
- OAuth2 credentials are properly configured in .env
- cron (Linux/Mac) or Task Scheduler (Windows) is available for scheduling
