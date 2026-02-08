<!--
SYNC IMPACT REPORT
==================
Version Change: 0.0.0 → 1.0.0 (MAJOR - Initial constitution)
Modified Principles: N/A (new document)
Added Sections:
  - Core Principles (7 principles)
  - Security & Privacy Requirements
  - Development Workflow
  - Governance
Removed Sections: N/A
Templates Requiring Updates:
  - .specify/templates/plan-template.md (Constitution Check alignment) - pending
  - .specify/templates/spec-template.md - OK (no changes needed)
  - .specify/templates/tasks-template.md - OK (no changes needed)
Follow-up TODOs: None
-->

# Personal AI Employee Constitution

## Core Principles

### I. Local-First & Privacy-First

All sensitive data (credentials, banking info, WhatsApp sessions, personal communications) MUST remain on the local machine. The Obsidian vault serves as the single source of truth for state and memory. Cloud components (Platinum tier) are permitted only for draft operations and MUST NOT store, process, or transmit sensitive credentials.

**Rationale**: Privacy and security are non-negotiable for an autonomous system handling personal and business affairs.

### II. Human-in-the-Loop (HITL) for Sensitive Actions

The AI Employee MUST NOT execute irreversible or high-risk actions without explicit human approval. Approval requests MUST be written to `/Pending_Approval/` and the system MUST wait for file movement to `/Approved/` before proceeding. High-risk actions include: payments over $50, emails to new contacts, social media posts, and any action modifying external systems.

**Rationale**: Humans remain accountable for all actions taken by their AI Employee.

### III. Watcher-Driven Perception

The system MUST use lightweight Python sentinel scripts (Watchers) to monitor external sources (Gmail, WhatsApp, filesystem). Watchers create markdown files in `/Needs_Action/` with structured YAML frontmatter. Claude Code MUST NOT poll external APIs directly; it reads only from the vault.

**Rationale**: Separation of concerns enables reliability, testability, and graceful degradation.

### IV. Plan-Before-Act Workflow

For any non-trivial task, Claude MUST create a Plan.md in `/Plans/` before taking action. Plans MUST include: objective, ordered steps with checkboxes, approval requirements, and expected outcomes. The Ralph Wiggum loop enables multi-step autonomous execution only after planning is complete.

**Rationale**: Planning prevents errors, enables human oversight, and creates audit trails.

### V. MCP-Based External Actions

All external actions (sending emails, posting to social media, browser automation) MUST be executed through Model Context Protocol (MCP) servers. Each MCP server MUST support `--dry-run` mode for development. Actions MUST be logged to `/Logs/YYYY-MM-DD.json` with timestamp, action type, approval status, and result.

**Rationale**: Standardized action interface enables testing, auditing, and safe deployment.

### VI. Graceful Degradation & Error Recovery

The system MUST handle failures gracefully: transient errors use exponential backoff retry; authentication failures pause operations and alert human; payment errors MUST NOT auto-retry; crashed watchers MUST be restarted by the orchestrator. All errors MUST be logged and surfaced in Dashboard.md.

**Rationale**: Autonomous systems will fail; recovery strategies maintain service continuity.

### VII. Audit Logging & Observability

Every action, decision, and state change MUST be logged. Dashboard.md provides real-time status. Logs MUST be retained for minimum 90 days. CEO Briefings (Gold+) aggregate weekly activity for human review. The system MUST support forensic reconstruction of any action sequence.

**Rationale**: Accountability and debugging require comprehensive audit trails.

## Security & Privacy Requirements

### Credential Management

- Credentials MUST be stored in environment variables or OS-level secrets managers
- `.env` files MUST be added to `.gitignore` immediately upon creation
- Credentials MUST be rotated monthly and after any suspected breach
- Vault sync (Platinum) MUST exclude: `.env`, tokens, session files, banking credentials

### Sandboxing & Isolation

- `DEV_MODE` environment variable MUST disable all real external actions
- All action scripts MUST support `--dry-run` flag
- Rate limiting MUST be enforced: max 10 emails/hour, max 3 payments/hour
- Test/sandbox accounts MUST be used during development

### Permission Boundaries

| Action Category | Auto-Approve Threshold | Always Require Approval |
|-----------------|------------------------|-------------------------|
| Email replies | To known contacts only | New contacts, bulk sends |
| Payments | < $50 recurring to known payees | New payees, > $100 |
| Social media | Scheduled posts (pre-approved) | Replies, DMs, new posts |
| File operations | Create, read within vault | Delete, move outside vault |

## Development Workflow

### Tiered Implementation

The system MUST be built in progressive tiers:

1. **Bronze**: Foundation (Dashboard, Handbook, 1 Watcher, folder structure)
2. **Silver**: Assistant (2+ Watchers, Plans, 1 MCP, HITL approval, logging)
3. **Gold**: Autonomous Employee (Odoo, CEO Briefing, multiple MCPs, Ralph Wiggum loop)
4. **Platinum**: Distributed (Cloud+Local split, claim-by-move, 24/7 operation)

Each tier MUST be fully functional before advancing to the next.

### Folder Structure Convention

All vault folders MUST follow this naming pattern:
- `/Needs_Action/` - Incoming items requiring processing
- `/Plans/` - Strategy documents before execution
- `/Pending_Approval/` - Items awaiting human approval
- `/Approved/` - Human-approved actions ready for execution
- `/Rejected/` - Human-rejected actions (archived)
- `/In_Progress/<agent>/` - Items currently being processed (claim-by-move)
- `/Done/` - Completed items (archived)
- `/Logs/` - JSON audit logs
- `/Accounting/` - Financial data (Gold+)
- `/Briefings/` - CEO reports (Gold+)

### Testing Requirements

- Watchers MUST be tested with mock data before connecting to real APIs
- MCP servers MUST pass `--dry-run` tests before live operation
- Integration tests MUST verify folder workflow: Needs_Action -> Done
- Error recovery MUST be tested by simulating failures

## Governance

### Constitution Authority

This constitution supersedes all other development practices and guidelines for this project. Any proposed change to the constitution requires:

1. Written proposal documenting the change and rationale
2. Impact assessment on existing tiers and components
3. Migration plan for affected artifacts
4. Version increment following semantic versioning

### Compliance Verification

All pull requests and code reviews MUST verify:
- [ ] HITL gates are in place for sensitive actions
- [ ] Credentials are not hardcoded or committed
- [ ] Audit logging is implemented for all actions
- [ ] Error handling includes graceful degradation
- [ ] Folder conventions are followed

### Amendment Procedure

- **MAJOR** version: Changes that remove or redefine core principles
- **MINOR** version: New principles or sections added
- **PATCH** version: Clarifications and non-semantic refinements

**Version**: 1.0.0 | **Ratified**: 2026-02-07 | **Last Amended**: 2026-02-07
