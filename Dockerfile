# ============================================
# AI Employee Vault - Dockerfile
# Optimized for Railway / Cloud deployment
# ============================================

FROM python:3.12-slim

LABEL maintainer="AI Employee Vault"
LABEL version="1.0.0"

# Prevent Python from writing .pyc and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PORT=8080 \
    VAULT_PATH=/app

# Install minimal system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies (slim set - no playwright/dev tools)
COPY requirements.deploy.txt ./
RUN pip install --no-cache-dir -r requirements.deploy.txt

# Copy application code
COPY orchestrator.py start_services.py healthcheck.py ./
COPY watchers/ ./watchers/
COPY mcp-servers/ ./mcp-servers/
COPY Company_Handbook.md Business_Goals.md Dashboard.md ./
COPY mcp-config.json ./

# Create vault directory structure
RUN mkdir -p \
    Inbox Needs_Action Plans Pending_Approval \
    Approved In_Progress Done Rejected \
    Logs Accounting Briefings Signals \
    Drop_Folder History

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

EXPOSE ${PORT}

CMD ["python", "start_services.py"]
