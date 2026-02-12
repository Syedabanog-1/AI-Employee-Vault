# ============================================
# AI Employee Vault - Dockerfile
# Optimized for Railway / Cloud deployment (Supports Platinum Phase)
# ============================================

FROM python:3.12-slim

LABEL maintainer="AI Employee Vault"
LABEL version="2.0.0-platinum"

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
    openssh-client \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies (now includes platinum phase requirements)
COPY requirements.deploy.txt ./
RUN pip install --no-cache-dir -r requirements.deploy.txt

# Install platinum phase dependencies if they exist
COPY Platinum_Phase/requirements.txt /tmp/platinum-requirements.txt || echo "No platinum requirements found"
RUN if [ -f /tmp/platinum-requirements.txt ]; then pip install --no-cache-dir -r /tmp/platinum-requirements.txt; fi

# Copy application code
COPY . .

# Create vault directory structure
RUN mkdir -p \
    Inbox Needs_Action Plans Pending_Approval \
    Approved In_Progress Done Rejected \
    Logs Accounting Briefings Signals \
    Drop_Folder History Updates \
    In_Progress/cloud-agent \
    In_Progress/local-agent

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

EXPOSE ${PORT}

# Default to starting the bronze/gold phase services
# For platinum phase, use: python Platinum_Phase/cloud_agent/start_cloud_agent.py
CMD ["python", "start_services.py"]
