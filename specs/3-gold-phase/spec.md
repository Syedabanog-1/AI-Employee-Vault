# Feature Specification: Gold Phase - Autonomous AI Employee

**Feature Branch**: `3-gold-phase`
**Created**: 2026-02-07
**Status**: Draft
**Input**: User description: "Gold Phase - Autonomous Employee with cross-domain integration, Odoo accounting, CEO Briefing, multiple MCPs, Ralph Wiggum loop, error recovery, and Agent Skills"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Cross-Domain Task Processing (Priority: P1)

As a user, I want my AI Employee to handle tasks that span personal and business domains seamlessly.

**Why this priority**: Cross-domain integration is what makes Gold-tier autonomous.

**Independent Test**: Send a message requesting both an invoice (business) and a personal reminder, verify both are handled in one workflow.

**Acceptance Scenarios**:

1. **Given** a cross-domain request arrives, **When** Claude processes it, **Then** it creates plans for both domains
2. **Given** business and personal actions are needed, **When** executed, **Then** both complete and are logged separately
3. **Given** a domain-specific error occurs, **When** processing continues, **Then** the other domain is not affected

---

### User Story 2 - Odoo Accounting Integration (Priority: P1)

As a user, I want my AI Employee to track invoices, payments, and expenses through Odoo Community.

**Why this priority**: Financial visibility is core to business automation.

**Independent Test**: Create an invoice in Odoo via MCP, verify it appears in accounting summary.

**Acceptance Scenarios**:

1. **Given** Odoo is configured, **When** Claude creates an invoice draft, **Then** it appears in Odoo pending approval
2. **Given** a payment is recorded, **When** Claude reads Odoo, **Then** the transaction appears in /Accounting summaries
3. **Given** Odoo API fails, **When** Claude attempts accounting action, **Then** error is logged and user notified

---

### User Story 3 - Weekly CEO Briefing Generation (Priority: P1)

As a user, I want my AI Employee to generate a weekly "Monday Morning CEO Briefing" summarizing business performance.

**Why this priority**: Proactive reporting transforms AI from assistant to business partner.

**Independent Test**: Trigger CEO Briefing generation, verify /Briefings contains summary with revenue, bottlenecks, suggestions.

**Acceptance Scenarios**:

1. **Given** Sunday night arrives, **When** scheduled task runs, **Then** a CEO Briefing is generated in /Briefings
2. **Given** briefing is generated, **When** I read it, **Then** it includes revenue, completed tasks, bottlenecks, and suggestions
3. **Given** unusual spending is detected, **When** briefing is created, **Then** it includes cost optimization suggestions

---

### User Story 4 - Ralph Wiggum Autonomous Loop (Priority: P1)

As a user, I want Claude to continue working on multi-step tasks until complete, not stopping after each step.

**Why this priority**: Autonomous completion is the defining Gold-tier capability.

**Independent Test**: Start a multi-step task, verify Claude completes all steps without manual intervention.

**Acceptance Scenarios**:

1. **Given** a multi-step task is assigned, **When** Ralph loop is active, **Then** Claude continues until all steps complete
2. **Given** a step fails, **When** Ralph loop detects it, **Then** Claude retries or escalates appropriately
3. **Given** task file moves to /Done, **When** Ralph loop checks, **Then** it allows Claude to exit

---

### User Story 5 - WhatsApp Integration (Priority: P2)

As a user, I want my AI Employee to monitor WhatsApp for urgent messages and respond appropriately.

**Why this priority**: WhatsApp is a major communication channel for many businesses.

**Independent Test**: Send a WhatsApp message with keyword "invoice", verify task is created.

**Acceptance Scenarios**:

1. **Given** WhatsApp Watcher is running, **When** a message with keyword arrives, **Then** task file is created
2. **Given** a WhatsApp reply is approved, **When** executed via MCP, **Then** the reply is sent
3. **Given** WhatsApp session expires, **When** detected, **Then** system pauses and alerts user

---

### User Story 6 - Social Media Integration (Facebook, Instagram, Twitter) (Priority: P2)

As a user, I want my AI Employee to post to multiple social platforms and generate engagement summaries.

**Why this priority**: Multi-platform presence multiplies business reach.

**Independent Test**: Approve a cross-platform post, verify it appears on all configured platforms.

**Acceptance Scenarios**:

1. **Given** a social post is approved, **When** executed, **Then** it posts to Facebook, Instagram, and Twitter
2. **Given** posts are published, **When** engagement data is available, **Then** summary is generated
3. **Given** one platform fails, **When** others succeed, **Then** partial success is logged with details

---

### User Story 7 - Error Recovery and Graceful Degradation (Priority: P2)

As a user, I want my AI Employee to handle errors gracefully without crashing or losing work.

**Why this priority**: Reliability is essential for autonomous operation.

**Independent Test**: Simulate API failure, verify system continues operating and alerts user.

**Acceptance Scenarios**:

1. **Given** a transient error occurs, **When** system detects it, **Then** exponential backoff retry is used
2. **Given** authentication fails, **When** detected, **Then** operations pause and user is alerted
3. **Given** a component crashes, **When** watchdog detects it, **Then** it is restarted automatically

---

### Edge Cases

- What happens when Odoo is unreachable for 24+ hours? System should queue actions and retry when available.
- What happens when Ralph loop hits max iterations? Should exit gracefully and report incomplete status.
- What happens when CEO Briefing has no data? Should generate minimal report noting low activity.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST support cross-domain task processing (Personal + Business)
- **FR-002**: Odoo MCP MUST connect via JSON-RPC API (Odoo 19+)
- **FR-003**: Odoo integration MUST support: read invoices, create draft invoices, read payments, read expenses
- **FR-004**: System MUST create /Accounting folder for financial summaries
- **FR-005**: System MUST create /Briefings folder for CEO reports
- **FR-006**: CEO Briefing MUST be generated weekly (Sunday night by default)
- **FR-007**: CEO Briefing MUST include: revenue summary, completed tasks, bottlenecks, cost suggestions
- **FR-008**: Ralph Wiggum loop MUST continue until task moves to /Done or max iterations reached
- **FR-009**: Ralph Wiggum MUST support promise-based and file-movement completion strategies
- **FR-010**: WhatsApp MCP MUST support message monitoring and sending
- **FR-011**: Facebook MCP MUST support post creation
- **FR-012**: Instagram MCP MUST support post creation
- **FR-013**: Twitter/X MCP MUST support tweet creation
- **FR-014**: System MUST implement exponential backoff retry for transient errors
- **FR-015**: System MUST implement watchdog process to restart crashed components
- **FR-016**: All errors MUST be logged with full context for debugging
- **FR-017**: All AI functionality MUST be implemented as Agent Skills

### Key Entities

- **CEO Briefing**: Weekly summary document with revenue, tasks, bottlenecks, and suggestions
- **Accounting Summary**: Financial overview from Odoo data (invoices, payments, expenses)
- **Ralph Loop State**: Tracking file for multi-step task progress and iteration count
- **Watchdog**: Process monitor that restarts crashed watchers and services
- **Social Post**: Content to be published across multiple platforms

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Cross-domain tasks complete end-to-end without manual intervention
- **SC-002**: Odoo data syncs within 5 minutes of changes
- **SC-003**: CEO Briefing generates automatically every Sunday by midnight
- **SC-004**: Ralph loop completes 90% of multi-step tasks without hitting max iterations
- **SC-005**: Social posts publish to all platforms within 2 minutes of approval
- **SC-006**: System recovers from transient errors within 5 minutes
- **SC-007**: Crashed components restart within 60 seconds
- **SC-008**: Zero data loss during error recovery scenarios

## Agent Skills Required

### Skill 1: process-cross-domain
**Purpose**: Handle tasks spanning personal and business domains
**Trigger**: When task involves multiple domains

### Skill 2: odoo-sync
**Purpose**: Sync data with Odoo accounting system
**Trigger**: Scheduled or after financial transactions

### Skill 3: generate-ceo-briefing
**Purpose**: Create weekly CEO Briefing document
**Trigger**: Sunday night scheduled task

### Skill 4: ralph-loop
**Purpose**: Continue multi-step task execution until complete
**Trigger**: When assigned complex tasks

### Skill 5: whatsapp-monitor
**Purpose**: Monitor WhatsApp for messages with keywords
**Trigger**: Continuous background operation

### Skill 6: post-social-all
**Purpose**: Post content to all configured social platforms
**Trigger**: After social post approval

### Skill 7: error-recovery
**Purpose**: Handle errors with retry logic and escalation
**Trigger**: When errors occur during any operation

### Skill 8: watchdog-check
**Purpose**: Monitor and restart crashed components
**Trigger**: Continuous background operation

### Skill 9: audit-subscriptions
**Purpose**: Analyze recurring transactions and suggest optimizations
**Trigger**: Part of CEO Briefing generation

## MCP Servers Required

### Odoo MCP
- **Operations**: get_invoices, create_draft_invoice, get_payments, get_expenses
- **Authentication**: Odoo JSON-RPC with API key
- **Configuration**: ODOO_URL, ODOO_DB, ODOO_USER, ODOO_API_KEY

### WhatsApp MCP
- **Operations**: get_messages, send_message
- **Authentication**: Meta Cloud API or local session
- **Configuration**: WHATSAPP_ACCESS_TOKEN, WHATSAPP_PHONE_NUMBER_ID

### Facebook MCP
- **Operations**: create_post, get_page_insights
- **Authentication**: Facebook Graph API
- **Configuration**: FB_PAGE_ID, FB_ACCESS_TOKEN

### Instagram MCP
- **Operations**: create_post, get_insights
- **Authentication**: Instagram Graph API
- **Configuration**: IG_ACCOUNT_ID, IG_ACCESS_TOKEN

### Twitter MCP
- **Operations**: create_tweet, get_engagement
- **Authentication**: Twitter API v2
- **Configuration**: TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN

## Assumptions

- Silver Phase is fully operational
- Odoo Community Edition 19+ is installed (local or VM)
- Social media accounts have API access configured
- Ralph Wiggum hook is properly configured in Claude Code
- Watchdog process has permission to restart services
