# Feature Specification: Platinum Phase - Always-On Cloud + Local Executive

**Feature Branch**: `4-platinum-phase`
**Created**: 2026-02-07
**Status**: Draft
**Input**: User description: "Platinum Phase - Distributed AI workforce with Cloud+Local split, 24/7 watchers, claim-by-move delegation, secure vault sync, and Agent Skills"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Cloud Agent Drafts While User is Offline (Priority: P1)

As a user, I want my Cloud AI Employee to draft replies and create plans 24/7, even when I'm offline, storing them for my review.

**Why this priority**: 24/7 operation is the core Platinum differentiator.

**Independent Test**: Shut down local machine, send email, verify Cloud creates draft in /Pending_Approval when Local comes online.

**Acceptance Scenarios**:

1. **Given** Local is offline, **When** email arrives, **Then** Cloud drafts reply and creates approval file
2. **Given** Cloud creates draft, **When** Local comes online, **Then** user sees pending approval in vault
3. **Given** Cloud is working, **When** it completes a draft, **Then** it writes to /Updates (not Dashboard.md)

---

### User Story 2 - Local Agent Executes Approved Actions (Priority: P1)

As a user, I want my Local AI Employee to be the only one that can execute sensitive actions after I approve them.

**Why this priority**: Security - sensitive actions must remain local.

**Independent Test**: Approve an email send on local machine, verify Local agent executes it via MCP.

**Acceptance Scenarios**:

1. **Given** an approval file exists, **When** Local detects it, **Then** Local executes the action via MCP
2. **Given** Local executes action, **When** complete, **Then** Dashboard.md is updated (single-writer rule)
3. **Given** Cloud attempts to execute, **When** action is sensitive, **Then** execution is blocked (Cloud draft-only)

---

### User Story 3 - Claim-by-Move Task Ownership (Priority: P1)

As a user, I want the system to prevent duplicate work when both Cloud and Local are running.

**Why this priority**: Coordination prevents wasted effort and conflicts.

**Independent Test**: Start both agents, drop file in /Needs_Action, verify only one agent claims it.

**Acceptance Scenarios**:

1. **Given** task appears in /Needs_Action, **When** Cloud claims it, **Then** file moves to /In_Progress/cloud/
2. **Given** Cloud claimed a task, **When** Local checks, **Then** Local ignores the task
3. **Given** Local claimed a task, **When** Cloud checks, **Then** Cloud ignores the task

---

### User Story 4 - Secure Vault Synchronization (Priority: P1)

As a user, I want my vault to sync between Cloud and Local, but sensitive credentials must never sync.

**Why this priority**: Security - credentials must never leave local machine.

**Independent Test**: Verify .env and session files are excluded from sync; verify markdown files sync.

**Acceptance Scenarios**:

1. **Given** Cloud creates a file, **When** sync runs, **Then** file appears in Local vault
2. **Given** .env exists locally, **When** sync runs, **Then** .env is NOT uploaded to Cloud
3. **Given** WhatsApp session exists locally, **When** sync runs, **Then** session files are NOT uploaded

---

### User Story 5 - Domain Work-Zone Specialization (Priority: P2)

As a user, I want clear ownership of which agent handles which types of work.

**Why this priority**: Clear boundaries prevent confusion and improve reliability.

**Independent Test**: Verify Cloud only handles email/social drafts; verify Local handles WhatsApp/payments.

**Acceptance Scenarios**:

1. **Given** email arrives, **When** Cloud processes, **Then** Cloud creates draft (not send)
2. **Given** WhatsApp message arrives, **When** detected, **Then** only Local can process (Cloud skips)
3. **Given** payment action needed, **When** approved, **Then** only Local executes (never Cloud)

---

### User Story 6 - Cloud Odoo Integration (Draft Only) (Priority: P2)

As a user, I want Cloud to read Odoo and prepare accounting drafts, but Local approves posting.

**Why this priority**: Financial actions require human oversight.

**Independent Test**: Cloud creates invoice draft in Odoo, user approves, Local posts it.

**Acceptance Scenarios**:

1. **Given** invoice request arrives, **When** Cloud processes, **Then** Cloud creates draft invoice in Odoo
2. **Given** draft invoice exists, **When** user approves, **Then** Local posts the invoice
3. **Given** payment needed, **When** requested, **Then** Cloud cannot execute (Local only)

---

### User Story 7 - Health Monitoring and Auto-Recovery (Priority: P2)

As a user, I want the Cloud system to monitor its own health and recover from failures.

**Why this priority**: 24/7 operation requires robust self-healing.

**Independent Test**: Kill a Cloud watcher process, verify it restarts within 60 seconds.

**Acceptance Scenarios**:

1. **Given** Cloud watcher crashes, **When** health monitor detects, **Then** watcher is restarted
2. **Given** Cloud orchestrator crashes, **When** systemd detects, **Then** orchestrator is restarted
3. **Given** recovery attempt fails, **When** max retries exceeded, **Then** alert is sent to user

---

### Edge Cases

- What happens when vault sync conflicts occur? Last-write-wins with conflict file created.
- What happens when Cloud and Local both claim same file simultaneously? First mover wins, second backs off.
- What happens when Cloud is unreachable for extended period? Local operates independently, sync catches up later.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Cloud Agent MUST run 24/7 on cloud VM (Oracle/AWS/etc.)
- **FR-002**: Cloud Agent MUST only draft, never send/post/pay
- **FR-003**: Local Agent MUST own all execution of sensitive actions
- **FR-004**: Local Agent MUST own Dashboard.md updates (single-writer rule)
- **FR-005**: Cloud MUST write updates to /Updates folder, not Dashboard.md
- **FR-006**: Claim-by-move MUST be enforced: first to move to /In_Progress/<agent>/ owns task
- **FR-007**: Vault sync MUST exclude: .env, tokens, session files, banking credentials
- **FR-008**: Vault sync MUST use Git (recommended) or Syncthing
- **FR-009**: Cloud MUST NOT store or access WhatsApp sessions
- **FR-010**: Cloud MUST NOT store or access banking credentials
- **FR-011**: Cloud Odoo integration MUST be draft-only
- **FR-012**: Local MUST approve and execute Odoo invoice/payment posting
- **FR-013**: Health monitoring MUST restart crashed components within 60 seconds
- **FR-014**: Health monitoring MUST alert user after 3 failed restart attempts
- **FR-015**: HTTPS MUST be used for all Cloud communications
- **FR-016**: Backups MUST be configured for Cloud Odoo data
- **FR-017**: All AI functionality MUST be implemented as Agent Skills

### Key Entities

- **Cloud Agent**: AI Employee running 24/7 on cloud VM, draft-only permissions
- **Local Agent**: AI Employee running on user's machine, full execution permissions
- **Work Zone**: Domain of responsibility (email, social, WhatsApp, payments, etc.)
- **Claim File**: Task file moved to /In_Progress/<agent>/ indicating ownership
- **Sync Exclude List**: Files/patterns that must not sync (.env, sessions, credentials)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Cloud Agent achieves 99% uptime over 30-day period
- **SC-002**: Email drafts created within 5 minutes of arrival, 24/7
- **SC-003**: Zero sensitive actions executed by Cloud Agent
- **SC-004**: Zero credential files synced to Cloud
- **SC-005**: Claim conflicts resolved correctly in 100% of cases
- **SC-006**: Crashed components restart within 60 seconds
- **SC-007**: Vault sync completes within 5 minutes of changes
- **SC-008**: Local approval to execution completes within 30 seconds

## Agent Skills Required

### Cloud Agent Skills

#### Skill 1: cloud-draft-email
**Purpose**: Draft email replies without sending
**Trigger**: When email task is claimed by Cloud

#### Skill 2: cloud-draft-social
**Purpose**: Draft social media posts without posting
**Trigger**: When social task is claimed by Cloud

#### Skill 3: cloud-odoo-draft
**Purpose**: Create draft invoices/entries in Odoo
**Trigger**: When accounting task is claimed by Cloud

#### Skill 4: cloud-write-update
**Purpose**: Write status update to /Updates folder
**Trigger**: After completing any draft work

#### Skill 5: cloud-health-check
**Purpose**: Monitor Cloud components and trigger restarts
**Trigger**: Scheduled every 60 seconds

### Local Agent Skills

#### Skill 6: local-execute-approved
**Purpose**: Execute approved actions via MCP
**Trigger**: When files appear in /Approved

#### Skill 7: local-merge-updates
**Purpose**: Merge /Updates into Dashboard.md
**Trigger**: When sync brings new files from Cloud

#### Skill 8: local-whatsapp
**Purpose**: Monitor and respond to WhatsApp (Local only)
**Trigger**: When WhatsApp message detected

#### Skill 9: local-payments
**Purpose**: Execute payment actions (Local only)
**Trigger**: When payment is approved

### Shared Skills

#### Skill 10: claim-task
**Purpose**: Move task to /In_Progress/<agent>/ to claim ownership
**Trigger**: When processing task from /Needs_Action

#### Skill 11: check-claimed
**Purpose**: Verify task is not already claimed by other agent
**Trigger**: Before claiming any task

#### Skill 12: sync-vault
**Purpose**: Trigger vault synchronization (Git push/pull)
**Trigger**: After completing work or on schedule

## MCP Servers Required

### Cloud MCP Servers

- **Email MCP (draft-only)**: draft_email, search_emails (NO send)
- **Social MCPs (draft-only)**: draft_post (NO publish)
- **Odoo MCP (draft-only)**: get_data, create_draft (NO post)

### Local MCP Servers

- **Email MCP (full)**: send_email, draft_email, search_emails
- **Social MCPs (full)**: create_post, publish_post
- **Odoo MCP (full)**: get_data, create_draft, post_invoice, record_payment
- **WhatsApp MCP (Local only)**: get_messages, send_message
- **Browser MCP (Local only)**: navigate, click, fill (for payments)

## Deployment Requirements

### Cloud VM
- Provider: Oracle Cloud Free Tier (or AWS/Azure/GCP)
- OS: Ubuntu 22.04 LTS
- Resources: 2 vCPU, 4GB RAM minimum
- HTTPS via Let's Encrypt
- Systemd for process management
- Daily automated backups

### Vault Sync
- Method: Git (recommended) or Syncthing
- .gitignore MUST include: .env, *.session, credentials.json, banking/
- Conflict resolution: last-write-wins with .conflict files

## Assumptions

- Gold Phase is fully operational
- Cloud VM is provisioned and accessible
- Git or Syncthing is configured for vault sync
- User understands Cloud vs Local permission boundaries
- Odoo is deployed on Cloud VM with HTTPS
