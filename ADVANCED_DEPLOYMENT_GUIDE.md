# AI Employee Vault - Advanced Deployment Guide

## Overview

This guide details the advanced deployment capabilities of the AI Employee Vault system across all four phases: Bronze, Silver, Gold, and Platinum. Each phase builds upon the previous with increasingly sophisticated capabilities.

## Phase Deployment Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        PLATINUM PHASE                               │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐    │
│  │   CLOUD AGENT   │  │   LOCAL AGENT   │  │  VAULT SYNC     │    │
│  │  (24/7 Draft)   │  │ (Execution/Sync)│  │   (Git/Sync)    │    │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────────────┐
│                         GOLD PHASE                                  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐    │
│  │   ACCOUNTING    │  │   SOCIAL MEDIA  │  │   AUTOMATION    │    │
│  │    (Odoo)       │  │ (FB, IG, TWTR)  │  │  (Ralph Loop)   │    │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────────────┐
│                        SILVER PHASE                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐    │
│  │   WATCHERS      │  │   MCP SERVERS   │  │  APPROVAL WF    │    │
│  │ (Gmail, Social) │  │ (Email, Social) │  │ (Human-in-loop) │    │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────────────┐
│                       BRONZE PHASE                                  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐    │
│  │  FILESYSTEM     │  │  ORCHESTRATOR   │  │  VAULT STRUCTURE │    │
│  │   WATCHER       │  │                 │  │                 │    │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
```

## Silver Phase Deployment

### Features
- Enhanced Watcher System (Gmail, WhatsApp, LinkedIn)
- MCP Server Integration (Email, Social Media)
- Human-in-the-Loop Approval Workflow
- Automated Scheduling

### Deployment Configuration

#### Docker Compose for Silver Phase
```yaml
version: '3.8'

services:
  # Silver Phase Orchestrator with enhanced capabilities
  silver-orchestrator:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: ai-employee-silver-orchestrator
    restart: unless-stopped
    env_file:
      - .env
    environment:
      - VAULT_PATH=/app
      - DEV_MODE=false
      - HEALTH_PORT=8080
      - APP_VERSION=1.0.0-silver
      - ENABLE_GMAIL_WATCHER=true
      - ENABLE_SOCIAL_WATCHERS=true
    ports:
      - "8080:8080"
    volumes:
      - vault-data:/app/Inbox
      - vault-data:/app/Needs_Action
      - vault-data:/app/Plans
      - vault-data:/app/Pending_Approval
      - vault-data:/app/Approved
      - vault-data:/app/In_Progress
      - vault-data:/app/Done
      - vault-data:/app/Logs
      - vault-data:/app/Briefings
      - vault-data:/app/Signals
    healthcheck:
      test: ["CMD", "python", "healthcheck.py"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 15s
    networks:
      - ai-employee-net

  # Silver Phase Email MCP Server
  email-mcp:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: ai-employee-email-mcp
    restart: unless-stopped
    env_file:
      - .env
    environment:
      - SERVICE=email-mcp
      - APP_VERSION=1.0.0-silver
    command: ["python", "mcp-servers/email-mcp/server.py"]
    depends_on:
      silver-orchestrator:
        condition: service_healthy
    networks:
      - ai-employee-net

  # Silver Phase Social Media MCP Server
  social-mcp:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: ai-employee-social-mcp
    restart: unless-stopped
    env_file:
      - .env
    environment:
      - SERVICE=social-mcp
      - APP_VERSION=1.0.0-silver
    command: ["python", "mcp-servers/social-mcp/server.py"]
    depends_on:
      silver-orchestrator:
        condition: service_healthy
    networks:
      - ai-employee-net

  # Gmail Watcher Service
  gmail-watcher:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: ai-employee-gmail-watcher
    restart: unless-stopped
    env_file:
      - .env
    environment:
      - VAULT_PATH=/app
      - APP_VERSION=1.0.0-silver
    command: ["python", "watchers/gmail_watcher.py"]
    depends_on:
      silver-orchestrator:
        condition: service_healthy
    networks:
      - ai-employee-net

networks:
  ai-employee-net:
    driver: bridge

volumes:
  vault-data:
    driver: local
```

### Silver Phase Environment Variables
```bash
# Silver Phase Specific Variables
ENABLE_GMAIL_WATCHER=true
ENABLE_SOCIAL_WATCHERS=true
GMAIL_POLL_INTERVAL=30
SOCIAL_POST_SCHEDULE="0 9,13,17 * * *"  # Daily at 9am, 1pm, 5pm
APPROVAL_REQUIRED_FOR=["email", "social_post", "payment"]
```

## Gold Phase Deployment

### Features
- Full Cross-Domain Integration (Personal + Business)
- Odoo Accounting System Integration
- Multi-Platform Social Media (Facebook, Instagram, Twitter)
- CEO Briefing Generation
- Ralph Wiggum Loop for Persistent Tasks

### Deployment Configuration

#### Docker Compose for Gold Phase
```yaml
version: '3.8'

services:
  # Gold Phase Orchestrator with advanced capabilities
  gold-orchestrator:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: ai-employee-gold-orchestrator
    restart: unless-stopped
    env_file:
      - .env
    environment:
      - VAULT_PATH=/app
      - DEV_MODE=false
      - HEALTH_PORT=8080
      - APP_VERSION=1.0.0-gold
      - ENABLE_ACCOUNTING_INTEGRATION=true
      - ENABLE_SOCIAL_PLATFORMS=true
      - ENABLE_RALPH_LOOP=true
      - ENABLE_CELE_BRIEFING=true
    ports:
      - "8080:8080"
    volumes:
      - vault-data:/app/Inbox
      - vault-data:/app/Needs_Action
      - vault-data:/app/Plans
      - vault-data:/app/Pending_Approval
      - vault-data:/app/Approved
      - vault-data:/app/In_Progress
      - vault-data:/app/Done
      - vault-data:/app/Logs
      - vault-data:/app/Briefings
      - vault-data:/app/Signals
      - vault-data:/app/Accounting
    healthcheck:
      test: ["CMD", "python", "healthcheck.py"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 15s
    networks:
      - ai-employee-net
      - accounting-net

  # Gold Phase Odoo MCP Server
  odoo-mcp:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: ai-employee-odoo-mcp
    restart: unless-stopped
    env_file:
      - .env
    environment:
      - SERVICE=odoo-mcp
      - APP_VERSION=1.0.0-gold
    command: ["python", "mcp-servers/odoo-mcp/server.py"]
    depends_on:
      gold-orchestrator:
        condition: service_healthy
    networks:
      - ai-employee-net
      - accounting-net

  # Gold Phase Social Media MCP Server (Multi-Platform)
  social-mcp:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: ai-employee-social-mcp
    restart: unless-stopped
    env_file:
      - .env
    environment:
      - SERVICE=social-mcp
      - APP_VERSION=1.0.0-gold
    command: ["python", "mcp-servers/social-mcp/server.py"]
    depends_on:
      gold-orchestrator:
        condition: service_healthy
    networks:
      - ai-employee-net

  # Gold Phase Browser MCP Server (for complex web automation)
  browser-mcp:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: ai-employee-browser-mcp
    restart: unless-stopped
    env_file:
      - .env
    environment:
      - SERVICE=browser-mcp
      - APP_VERSION=1.0.0-gold
    command: ["python", "mcp-servers/browser-mcp/server.py"]
    depends_on:
      gold-orchestrator:
        condition: service_healthy
    networks:
      - ai-employee-net

  # Gold Phase Payment MCP Server
  payment-mcp:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: ai-employee-payment-mcp
    restart: unless-stopped
    env_file:
      - .env
    environment:
      - SERVICE=payment-mcp
      - APP_VERSION=1.0.0-gold
    command: ["python", "mcp-servers/payment-mcp/server.py"]
    depends_on:
      gold-orchestrator:
        condition: service_healthy
    networks:
      - ai-employee-net

  # Odoo Community Edition (Self-Hosted)
  odoo:
    image: odoo:19.0
    container_name: odoo-community
    restart: unless-stopped
    environment:
      - HOST=db
      - USER=odoo
      - PASSWORD=odoo
    ports:
      - "8069:8069"
    volumes:
      - odoo-data:/var/lib/odoo
      - ./config:/etc/odoo
    depends_on:
      - db
    networks:
      - accounting-net

  # PostgreSQL for Odoo
  db:
    image: postgres:15
    container_name: odoo-db
    restart: unless-stopped
    environment:
      - POSTGRES_DB=postgres
      - POSTGRES_USER=odoo
      - POSTGRES_PASSWORD=odoo
    volumes:
      - db-data:/var/lib/postgresql/data
    networks:
      - accounting-net

networks:
  ai-employee-net:
    driver: bridge
  accounting-net:
    driver: bridge

volumes:
  vault-data:
    driver: local
  odoo-data:
    driver: local
  db-data:
    driver: local
```

### Gold Phase Environment Variables
```bash
# Gold Phase Specific Variables
ENABLE_ACCOUNTING_INTEGRATION=true
ODOO_URL=http://odoo:8069
ODOO_DB_NAME=ai_employee_vault
ODOO_USERNAME=admin
ODOO_PASSWORD=password
ENABLE_SOCIAL_PLATFORMS=true
FACEBOOK_PAGE_ID=your_page_id
INSTAGRAM_ACCOUNT_ID=your_account_id
TWITTER_API_KEY=your_key
ENABLE_RALPH_LOOP=true
RALPH_LOOP_INTERVAL=300  # 5 minutes
ENABLE_CELE_BRIEFING=true
CEO_BRIEFING_SCHEDULE="0 8 * * 1"  # Every Monday at 8am
```

## Platinum Phase Deployment

### Features
- 24/7 Cloud Operation with Local Specialization
- Work-Zone Specialization (Cloud: Draft, Local: Execution)
- Claim-by-Move Task Management
- Secure Vault Synchronization
- Production-Ready Infrastructure

### Deployment Configuration

#### Platinum Phase Docker Compose
```yaml
version: '3.8'

services:
  # Platinum Phase Cloud Agent (24/7 Operation)
  cloud-agent:
    build:
      context: .
      dockerfile: Platinum_Phase/Dockerfile.cloud
    container_name: ai-employee-cloud-agent
    restart: unless-stopped
    env_file:
      - .env
    environment:
      - VAULT_PATH=/app/vault
      - DEV_MODE=false
      - HEALTH_PORT=8080
      - APP_VERSION=2.0.0-platinum
      - AGENT_TYPE=cloud
      - AGENT_ROLE=cloud-draft
      - SYNC_ENABLED=true
      - CLAIM_BY_MOVE_ENABLED=true
    ports:
      - "8080:8080"
    volumes:
      - vault-data:/app/vault
      - cloud-logs:/app/vault/Logs
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 15s
    networks:
      - ai-employee-net
    deploy:
      resources:
        limits:
          cpus: "1.0"
          memory: 1024M
        reservations:
          cpus: "0.5"
          memory: 512M

  # Platinum Phase Local Agent (Execution & Sync)
  local-agent:
    build:
      context: .
      dockerfile: Platinum_Phase/Dockerfile.local
    container_name: ai-employee-local-agent
    restart: unless-stopped
    env_file:
      - .env
    environment:
      - VAULT_PATH=/app/vault
      - DEV_MODE=false
      - HEALTH_PORT=8081
      - APP_VERSION=2.0.0-platinum
      - AGENT_TYPE=local
      - AGENT_ROLE=local-execution
      - SYNC_ENABLED=true
      - CLAIM_BY_MOVE_ENABLED=true
    ports:
      - "8081:8081"
    volumes:
      - vault-data:/app/vault
      - local-logs:/app/vault/Logs
      - /var/run/docker.sock:/var/run/docker.sock  # For local execution
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8081/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 15s
    networks:
      - ai-employee-net
    deploy:
      resources:
        limits:
          cpus: "1.0"
          memory: 1024M
        reservations:
          cpus: "0.5"
          memory: 512M

  # Platinum Phase Vault Sync Service
  vault-sync:
    build:
      context: .
      dockerfile: Platinum_Phase/Dockerfile.sync
    container_name: ai-employee-vault-sync
    restart: unless-stopped
    env_file:
      - .env
    environment:
      - VAULT_PATH=/app/vault
      - SYNC_METHOD=git
      - SYNC_INTERVAL=60
      - GIT_REMOTE_URL=https://github.com/your-org/ai-employee-vault.git
    volumes:
      - vault-data:/app/vault
      - git-credentials:/root/.ssh
    networks:
      - ai-employee-net
    deploy:
      resources:
        limits:
          cpus: "0.25"
          memory: 256M

  # Platinum Phase Load Balancer (Nginx)
  load-balancer:
    image: nginx:alpine
    container_name: ai-employee-load-balancer
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./deploy/nginx/platinum.conf:/etc/nginx/nginx.conf:ro
      - nginx-certs:/etc/nginx/certs
    depends_on:
      - cloud-agent
      - local-agent
    networks:
      - ai-employee-net
    deploy:
      resources:
        limits:
          cpus: "0.25"
          memory: 64M

  # Platinum Phase Monitoring Stack
  prometheus:
    image: prom/prometheus:latest
    container_name: ai-employee-prometheus
    restart: unless-stopped
    ports:
      - "9090:9090"
    volumes:
      - ./deploy/prometheus/config.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus-data:/prometheus
    networks:
      - ai-employee-net
    deploy:
      resources:
        limits:
          cpus: "0.5"
          memory: 512M

  grafana:
    image: grafana/grafana-enterprise:latest
    container_name: ai-employee-grafana
    restart: unless-stopped
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana-data:/var/lib/grafana
    depends_on:
      - prometheus
    networks:
      - ai-employee-net
    deploy:
      resources:
        limits:
          cpus: "0.5"
          memory: 512M

networks:
  ai-employee-net:
    driver: bridge

volumes:
  vault-data:
    driver: local
  cloud-logs:
    driver: local
  local-logs:
    driver: local
  git-credentials:
    driver: local
  nginx-certs:
    driver: local
  prometheus-data:
    driver: local
  grafana-data:
    driver: local
```

### Platinum Phase Environment Variables
```bash
# Platinum Phase Specific Variables
AGENT_TYPE=cloud
AGENT_ROLE=cloud-draft
SYNC_ENABLED=true
SYNC_METHOD=git
SYNC_INTERVAL=60
CLAIM_BY_MOVE_ENABLED=true
VAULT_SYNC_PATH=/app/vault
GIT_REMOTE_URL=https://github.com/your-org/ai-employee-vault.git
CLOUD_AGENT_URL=https://cloud.yourdomain.com
LOCAL_AGENT_URL=https://local.yourdomain.com
VAULT_SYNC_EXCLUDE=[".env", "*.token", "*.session", "secrets/", "private/"]
SECURITY_AUDIT_ENABLED=true
AUDIT_LOG_RETENTION_DAYS=90
```

## Deployment Commands

### Silver Phase Deployment
```bash
# Deploy Silver Phase
docker-compose -f docker-compose.silver.yml up -d

# Verify Silver Phase
curl http://localhost:8080/health
curl http://localhost:8080/api/status
```

### Gold Phase Deployment
```bash
# Deploy Gold Phase
docker-compose -f docker-compose.gold.yml up -d

# Verify Gold Phase
curl http://localhost:8080/health
curl http://localhost:8080/api/status
curl http://localhost:8069/web  # Odoo interface
```

### Platinum Phase Deployment
```bash
# Deploy Platinum Phase (Cloud Agent)
railway up --service cloud-agent

# Deploy Platinum Phase (Local Agent)
docker-compose -f docker-compose.platinum.yml up -d local-agent

# Verify Platinum Phase
curl https://your-cloud-agent.railway.app/health
curl http://localhost:8081/health
```

## Advanced Monitoring & Observability

### Health Endpoints
| Endpoint | Purpose | Response |
|----------|---------|----------|
| `GET /health` | Liveness probe | `{"status": "healthy", "uptime_seconds": ..., "phase": "platinum"}` |
| `GET /ready` | Readiness probe | `{"status": "ready", "checks": {...}, "phase": "platinum"}` |
| `GET /metrics` | Queue metrics | `{"queue_sizes": {"inbox": 0, ...}, "phase": "platinum"}` |
| `GET /api/status` | Full system status | Complete system overview |

### Platinum Phase Specific Endpoints
| Endpoint | Purpose | Response |
|----------|---------|----------|
| `GET /api/claim-task` | Claim a task via move | `{"task_id": "...", "claimed_by": "cloud-agent"}` |
| `GET /api/sync-status` | Vault sync status | `{"sync_status": "up-to-date", "last_sync": "..."}` |
| `GET /api/agent-status` | Agent coordination | `{"cloud_online": true, "local_online": false}` |

## Security Considerations

### Platinum Phase Security Architecture
- **Secret Isolation**: Cloud never stores WhatsApp sessions, banking credentials, or payment tokens
- **Claim-by-Move**: Prevents duplicate work with atomic file operations
- **Sync Exclusion**: Sensitive files never synchronized (configured in `.gitignore`)
- **Role Separation**: Cloud (draft-only) vs Local (execution-only)

### Network Security
- Service mesh with isolated networks for different concerns
- Load balancer with SSL termination
- Internal service communication only
- Firewall rules restricting external access

## Scaling Recommendations

### Silver Phase
- Single instance sufficient for personal use
- Horizontal scaling not typically needed

### Gold Phase
- Single instance for small-medium businesses
- Consider separate DB instance for high volume
- MCP servers can be scaled independently

### Platinum Phase
- Cloud Agent: Auto-scaling based on workload
- Local Agent: Single instance (by design)
- Vault Sync: Single instance with failover
- Monitoring: Dedicated instances for production

## Troubleshooting

### Common Issues
1. **Vault Sync Conflicts**: Use git merge strategies or manual resolution
2. **Claim-by-Move Race Conditions**: Increase sync intervals or implement distributed locks
3. **Agent Communication Failures**: Check network connectivity and sync status

### Diagnostic Commands
```bash
# Check all services
docker-compose ps

# Monitor logs
docker-compose logs -f

# Check vault sync status
docker exec vault-sync git status

# Verify agent coordination
curl http://localhost:8080/api/agent-status
```

## Upgrade Path

### From Silver to Gold
1. Deploy Odoo Community Edition
2. Update environment variables for accounting integration
3. Enable social media platforms
4. Configure CEO briefing schedule

### From Gold to Platinum
1. Deploy Cloud Agent to Railway/Cloud Provider
2. Set up vault synchronization (Git)
3. Configure claim-by-move system
4. Establish work-zone specialization
5. Test demo scenario (email → draft → approval → execution)

## Production Checklist

### Pre-Deployment
- [ ] Environment variables properly configured
- [ ] SSL certificates installed
- [ ] Backup procedures tested
- [ ] Monitoring alerts configured
- [ ] Security audit completed

### Post-Deployment
- [ ] Health endpoints verified
- [ ] Load testing performed
- [ ] Failover procedures tested
- [ ] Documentation updated
- [ ] Team trained on operations