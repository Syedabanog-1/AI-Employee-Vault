# AI Employee Vault - Cloud Deployment Guide

## Architecture Overview

```
                    ┌─────────────┐
                    │   GitHub    │
                    │  Actions    │
                    │   CI/CD     │
                    └──────┬──────┘
                           │ Build & Push
                           ▼
                    ┌─────────────┐
                    │   GitHub    │
                    │  Container  │
                    │  Registry   │
                    └──────┬──────┘
                           │ Pull Image
              ┌────────────┼────────────┐
              ▼            ▼            ▼
       ┌────────────┐ ┌─────────┐ ┌─────────┐
       │  AWS ECS   │ │Railway  │ │ Render  │
       │  Fargate   │ │  .app   │ │  .com   │
       └─────┬──────┘ └────┬────┘ └────┬────┘
             │              │           │
             ▼              ▼           ▼
    ┌──────────────────────────────────────┐
    │         AI Employee Vault            │
    │  ┌──────────┐  ┌──────────────────┐  │
    │  │Orchestr- │  │  Health Check    │  │
    │  │  ator    │  │  :8080/health    │  │
    │  └──────────┘  └──────────────────┘  │
    │  ┌──────────┐  ┌──────────────────┐  │
    │  │ Watcher  │  │   MCP Servers    │  │
    │  │ Service  │  │  (Email, Social) │  │
    │  └──────────┘  └──────────────────┘  │
    └──────────────────────────────────────┘
```

## Quick Start

### Option 1: Docker (Local)

```bash
# Build
docker build -t ai-employee-vault .

# Run
docker run -d \
  --name ai-employee \
  --env-file .env \
  -p 8080:8080 \
  ai-employee-vault

# Verify
curl http://localhost:8080/health
```

### Option 2: Docker Compose (Full Stack)

```bash
# Development
docker compose -f docker-compose.yml -f docker-compose.dev.yml up

# Production
docker compose up -d

# Check status
docker compose ps
curl http://localhost:8080/health
curl http://localhost:8080/metrics
```

### Option 3: AWS ECS (Production)

1. **Prerequisites:**
   - AWS CLI configured
   - GitHub Container Registry access
   - Secrets stored in AWS Secrets Manager

2. **Deploy CloudFormation stack:**
   ```bash
   aws cloudformation deploy \
     --template-file deploy/aws/cloudformation.yml \
     --stack-name ai-employee-vault-staging \
     --parameter-overrides \
       Environment=staging \
       VpcId=vpc-xxxxx \
       SubnetIds=subnet-aaa,subnet-bbb \
       ContainerImage=ghcr.io/OWNER/ai-employee-vault:latest \
     --capabilities CAPABILITY_IAM
   ```

3. **Verify:**
   ```bash
   aws cloudformation describe-stacks \
     --stack-name ai-employee-vault-staging \
     --query 'Stacks[0].Outputs'
   ```

### Option 4: Railway (Simple Cloud)

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

### Option 5: Render (Auto-Deploy)

1. Connect GitHub repository to Render
2. Render auto-detects `render.yaml`
3. Set environment variables in Render dashboard
4. Push to deploy

## CI/CD Pipeline

The GitHub Actions pipeline (`.github/workflows/ci-cd.yml`) runs:

| Stage | Trigger | Actions |
|-------|---------|---------|
| Lint | All pushes/PRs | Black format check, MyPy type check |
| Test | After lint | Pytest suite |
| Security | After lint | Trivy scan, TruffleHog secrets check |
| Build | After test+security | Docker multi-arch build, push to GHCR |
| Deploy Staging | Push to master | ECS update, health check |
| Deploy Production | Version tags (v*) | ECS update, health check, GitHub release |

### Required GitHub Secrets

| Secret | Description |
|--------|-------------|
| `AWS_ACCESS_KEY_ID` | AWS IAM access key |
| `AWS_SECRET_ACCESS_KEY` | AWS IAM secret key |

### Required GitHub Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `AWS_REGION` | AWS region | `us-east-1` |
| `STAGING_URL` | Staging ALB URL | `http://ai-employee-staging-xxx.us-east-1.elb.amazonaws.com` |
| `PRODUCTION_URL` | Production ALB URL | `http://ai-employee-prod-xxx.us-east-1.elb.amazonaws.com` |

## Health Endpoints

| Endpoint | Purpose | Response |
|----------|---------|----------|
| `GET /health` | Liveness probe | `{"status": "healthy", "uptime_seconds": ...}` |
| `GET /ready` | Readiness probe | `{"status": "ready", "checks": {...}}` |
| `GET /metrics` | Queue metrics | `{"queue_sizes": {"inbox": 0, ...}}` |

## Monitoring & Alerts

- **CloudWatch**: Container Insights enabled on ECS cluster
- **Log Aggregation**: Promtail collects from `/app/Logs/`
- **Alarms**: CPU > 80%, unhealthy targets trigger CloudWatch alarms
- **Auto-scaling**: 1-3 tasks, target 70% CPU utilization

## Security

- Non-root container user (`aiemployee`)
- Secrets via AWS Secrets Manager (not env vars)
- Nginx security headers (XSS, CSRF, content-type)
- Rate limiting on all endpoints
- TLS termination at ALB/Nginx layer
- Trivy + TruffleHog in CI pipeline
