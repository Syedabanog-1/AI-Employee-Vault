# AI Employee Vault - Platinum Phase

## Overview
The Platinum Phase implements a distributed AI employee system with clear separation of duties between Cloud and Local agents:

- **Cloud Agent**: Runs 24/7, handles draft creation and monitoring (no execution permissions)
- **Local Agent**: Handles sensitive operations requiring credentials (execution, payments, approvals)

## Features

### Cloud Agent Capabilities
- ✅ 24/7 operation for continuous monitoring
- ✅ Draft creation for emails, social posts, and Odoo entries
- ✅ Claim-by-move task management to prevent duplicate work
- ✅ Secure vault synchronization (excludes credentials)
- ✅ Health monitoring and auto-recovery
- ✅ Swagger UI API documentation

### Local Agent Capabilities
- ✅ Execution of approved actions via MCP servers
- ✅ Sensitive operations (payments, WhatsApp, credentials)
- ✅ Dashboard management (single-writer rule)
- ✅ Approval of cloud-generated drafts

## API Documentation

The Cloud Agent API includes comprehensive Swagger documentation:

- **Swagger UI**: `/docs` - Interactive API testing
- **ReDoc**: `/redoc` - Alternative API documentation
- **OpenAPI Schema**: `/openapi.json` - Raw API specification

### Key Endpoints

#### System Operations
- `GET /health` - Health check
- `GET /ready` - Readiness check
- `GET /api/status` - Full system status
- `GET /api/metrics` - Queue sizes and metrics
- `GET /api/config` - Runtime configuration

#### Queue Management
- `GET /api/queues` - List all queues
- `GET /api/queue/{name}` - Items in specific queue
- `POST /api/claim-task` - Claim a task (claim-by-move)

#### Task Operations
- `POST /api/inbox` - Submit new task
- `POST /api/draft-email` - Create email draft
- `POST /api/approve-action` - Approve an action (Local Agent)
- `POST /api/execute-action` - Execute approved action (Local Agent)

## Architecture

### Work Zone Specialization
```
Cloud Agent → Draft-only operations
  - Email monitoring and draft creation
  - Social media draft creation
  - Odoo entry draft creation
  - Never executes sensitive actions

Local Agent → Execution-only operations
  - Execute approved actions
  - Handle payments
  - Manage WhatsApp communications
  - Update Dashboard.md (single-writer rule)
```

### Claim-by-Move System
Prevents duplicate work between Cloud and Local agents:
1. Task appears in `/Needs_Action`
2. First agent to move file to `/In_Progress/<agent-id>/` claims ownership
3. Other agents skip already-claimed tasks

### Secure Vault Synchronization
- Git-based synchronization between Cloud and Local
- Credentials and sensitive files excluded from sync
- `.gitignore` includes `.env`, `*.session`, `credentials.json`, etc.

## Deployment

### Railway Deployment
The Cloud Agent can be deployed to Railway with Swagger UI:

```bash
# Deploy the Cloud Agent
railway up
```

### Environment Variables
- `VAULT_PATH` - Path to the vault directory
- `AGENT_TYPE` - Either "cloud" or "local"
- `DEV_MODE` - Development mode flag

## Security Model

### Cloud Agent Permissions
- ✅ Read all queues
- ✅ Create draft items
- ❌ Execute sensitive actions
- ❌ Access credentials
- ❌ Modify Dashboard.md

### Local Agent Permissions
- ✅ Read all queues
- ✅ Execute approved actions
- ✅ Access credentials
- ✅ Modify Dashboard.md
- ✅ Handle sensitive operations

## Getting Started

1. Deploy the Cloud Agent to Railway
2. Access the API documentation at `/docs`
3. Monitor the dashboard at `/`
4. The Local Agent runs on your local machine with full execution privileges

## Demo Scenario
1. Email arrives while Local agent is offline
2. Cloud Agent creates draft reply in `/Pending_Approval`
3. When Local agent returns online, user reviews and approves draft
4. Local Agent executes send via MCP and logs to `/Done`
5. Dashboard.md is updated following single-writer rule