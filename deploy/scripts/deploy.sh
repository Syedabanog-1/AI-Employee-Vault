#!/bin/bash
###############################################
# AI Employee Vault - Deployment Script
# Usage: ./deploy/scripts/deploy.sh [staging|production]
###############################################

set -euo pipefail

ENVIRONMENT="${1:-staging}"
REGION="${AWS_REGION:-us-east-1}"
REGISTRY="ghcr.io"
IMAGE_NAME="${GITHUB_REPOSITORY:-ai-employee-vault}"
TAG="${GITHUB_SHA:-latest}"

echo "=========================================="
echo "AI Employee Vault - Deployment"
echo "=========================================="
echo "Environment: ${ENVIRONMENT}"
echo "Region:      ${REGION}"
echo "Image:       ${REGISTRY}/${IMAGE_NAME}:${TAG}"
echo "=========================================="

# Validate environment
if [[ "${ENVIRONMENT}" != "staging" && "${ENVIRONMENT}" != "production" ]]; then
    echo "ERROR: Environment must be 'staging' or 'production'"
    exit 1
fi

# Production requires confirmation
if [[ "${ENVIRONMENT}" == "production" ]]; then
    echo ""
    echo "WARNING: You are deploying to PRODUCTION!"
    read -p "Type 'yes' to confirm: " CONFIRM
    if [[ "${CONFIRM}" != "yes" ]]; then
        echo "Deployment cancelled."
        exit 0
    fi
fi

CLUSTER="ai-employee-${ENVIRONMENT}"
SERVICE="ai-employee-orchestrator"

echo ""
echo "[1/4] Updating ECS service..."
aws ecs update-service \
    --cluster "${CLUSTER}" \
    --service "${SERVICE}" \
    --force-new-deployment \
    --region "${REGION}" \
    --output text \
    --query 'service.serviceName'

echo "[2/4] Waiting for deployment to stabilize..."
aws ecs wait services-stable \
    --cluster "${CLUSTER}" \
    --services "${SERVICE}" \
    --region "${REGION}"

echo "[3/4] Running health check..."
ALB_DNS=$(aws elbv2 describe-load-balancers \
    --names "ai-employee-${ENVIRONMENT}" \
    --region "${REGION}" \
    --query 'LoadBalancers[0].DNSName' \
    --output text 2>/dev/null || echo "")

if [[ -n "${ALB_DNS}" ]]; then
    for i in {1..10}; do
        STATUS=$(curl -s -o /dev/null -w "%{http_code}" "http://${ALB_DNS}/health" || true)
        if [[ "${STATUS}" == "200" ]]; then
            echo "Health check PASSED"
            break
        fi
        echo "  Attempt ${i}/10 - Status: ${STATUS}"
        sleep 10
    done
else
    echo "  Could not determine ALB DNS - skipping health check"
fi

echo "[4/4] Deployment summary..."
echo ""
echo "=========================================="
echo "Deployment complete!"
echo "=========================================="
echo "Cluster:     ${CLUSTER}"
echo "Service:     ${SERVICE}"
if [[ -n "${ALB_DNS}" ]]; then
    echo "Health:      http://${ALB_DNS}/health"
    echo "Metrics:     http://${ALB_DNS}/metrics"
fi
echo "=========================================="
