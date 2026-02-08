# Platinum Phase Specification

**Phase**: Platinum  
**Target**: Always-On Cloud + Local Executive  
**Estimated Time**: 60+ hours

## Objectives
- Deploy AI Employee on Cloud 24/7 with local specialization
- Implement cloud-local synchronization
- Create production-ready infrastructure with monitoring

## Requirements
- All Gold requirements plus:
- Run the AI Employee on Cloud 24/7 (always-on watchers + orchestrator + health monitoring). You can deploy a Cloud VM (Oracle/AWS/etc.) - Oracle Cloud Free VMs can be used for this (subject to limits/availability).
- Work-Zone Specialization (domain ownership):
  - Cloud owns: Email triage + draft replies + social post drafts/scheduling (draft-only; requires Local approval before send/post)
  - Local owns: approvals, WhatsApp session, payments/banking, and final "send/post" actions
- Delegation via Synced Vault (Phase 1)
  - Agents communicate by writing files into:
    - /Needs_Action/<domain>/, /Plans/<domain>/, /Pending_Approval/<domain>/
  - Prevent double-work using:
    - /In_Progress/<agent>/ claim-by-move rule
    - single-writer rule for Dashboard.md (Local)
  - Cloud writes updates to /Updates/ (or /Signals/), and Local merges them into Dashboard.md.
- For Vault sync (Phase 1) use Git (recommended) or Syncthing.
- Claim-by-move rule: first agent to move an item from /Needs_Action to /In_Progress/<agent>/ owns it; other agents must ignore it.
- Security rule: Vault sync includes only markdown/state. Secrets never sync (.env, tokens, WhatsApp sessions, banking creds). So Cloud never stores or uses WhatsApp sessions, banking credentials, or payment tokens.
- Deploy Odoo Community on a Cloud VM (24/7) with HTTPS, backups, and health monitoring; integrate Cloud Agent with Odoo via MCP for draft-only accounting actions and Local approval for posting invoices/payments.
- Optional A2A Upgrade (Phase 2): Replace some file handoffs with direct A2A messages later, while keeping the vault as the audit record
- Platinum demo (minimum passing gate): Email arrives while Local is offline → Cloud drafts reply + writes approval file → when Local returns, user approves → Local executes send via MCP → logs → moves task to /Done.

## Components to Specify
1. **Cloud Infrastructure**
   - Cloud VM deployment (Oracle/AWS/other)
   - 24/7 operation capabilities
   - Health monitoring and alerting
   - Auto-scaling configurations

2. **Work-Zone Specialization**
   - Cloud agent responsibilities: email triage, draft replies, social post drafts
   - Local agent responsibilities: approvals, WhatsApp, payments, final actions
   - Clear division of duties and responsibilities
   - Handoff protocols between agents

3. **Vault Synchronization**
   - Git-based synchronization (primary) or Syncthing (alternative)
   - Conflict resolution mechanisms
   - Data consistency protocols
   - Secure transmission of state data

4. **Claim-by-Move System**
   - /In_Progress/<agent>/ folder structure
   - Task ownership protocols
   - Double-work prevention mechanisms
   - Coordination between cloud and local agents

5. **Security Architecture**
   - Secret isolation (never synced)
   - Secure credential management
   - Encrypted communication channels
   - Access control mechanisms

6. **Production Monitoring**
   - Health checks and monitoring
   - Performance metrics
   - Error tracking and alerting
   - Backup and disaster recovery

7. **Advanced MCP Integration**
   - Draft-only operations on cloud
   - Approval-required operations on local
   - Coordinated action execution
   - Audit trail maintenance

## Constraints
- Maintain strict separation of sensitive data
- Ensure secure communication between cloud and local agents
- Implement robust error handling for network interruptions
- Maintain audit trails across distributed system
- Ensure data consistency despite potential conflicts
- Minimize latency in cross-agent communication

## Success Criteria
- Cloud agent operating 24/7 reliably
- Local-cloud synchronization working seamlessly
- Claim-by-move system preventing double-work
- Security protocols protecting sensitive data
- Demo scenario working (email arrival → draft → approval → execution)
- Production monitoring and alerting operational
- Distributed system maintaining consistency