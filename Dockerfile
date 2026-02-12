# ============================================
# AI Employee Vault - Multi-Stage Dockerfile
# ============================================
# Stage 1: Node.js dependencies for MCP servers
# Stage 2: Python application with all services
# ============================================

# --- Stage 1: Build Node.js MCP servers ---
FROM node:20-alpine AS node-builder

WORKDIR /app/mcp-servers/email-mcp
COPY mcp-servers/email-mcp/package*.json ./
RUN npm ci --production

# --- Stage 2: Python application ---
FROM python:3.13-slim AS production

# System metadata
LABEL maintainer="AI Employee Vault"
LABEL version="1.0.0"
LABEL description="AI Employee Vault - Autonomous Personal Assistant"

# Prevent Python from writing .pyc files and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    nodejs \
    npm \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN groupadd -r aiemployee && useradd -r -g aiemployee -m -s /bin/bash aiemployee

# Set working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy Node.js dependencies from builder stage
COPY --from=node-builder /app/mcp-servers/email-mcp/node_modules /app/mcp-servers/email-mcp/node_modules

# Copy application code
COPY . .

# Create vault directory structure
RUN mkdir -p \
    Inbox Needs_Action Plans Pending_Approval \
    Approved In_Progress Done Rejected \
    Logs Accounting Briefings Signals \
    Drop_Folder History

# Set permissions
RUN chown -R aiemployee:aiemployee /app

# Switch to non-root user
USER aiemployee

# Health check endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python healthcheck.py || exit 1

# Expose health check port
EXPOSE 8080

# Default command - start orchestrator with health endpoint
CMD ["python", "start_services.py"]
