"""
Service Starter for AI Employee Vault
Launches orchestrator + FastAPI web server in parallel.
"""

import os
import sys
import threading
import logging
import uvicorn
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
logger = logging.getLogger("start_services")


def start_web_server():
    """Start the FastAPI web server with Swagger docs."""
    from healthcheck import app
    
    # Railway injects PORT env var; fall back to HEALTH_PORT or 8080
    port = int(os.getenv("PORT", os.getenv("HEALTH_PORT", "8080")))
    
    # Run the FastAPI app with uvicorn
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")


def start_orchestrator():
    """Start the main orchestrator."""
    from orchestrator import ClaudeOrchestrator

    vault_path = os.getenv("VAULT_PATH", ".")
    orchestrator = ClaudeOrchestrator(vault_path)
    orchestrator.run()


def main():
    logger.info("Starting AI Employee Vault services...")
    logger.info(f"Environment: {'production' if not os.getenv('DEV_MODE', 'true') == 'true' else 'development'}")
    logger.info(f"Vault path: {os.getenv('VAULT_PATH', '.')}")

    # Start orchestrator in background thread
    orchestrator_thread = threading.Thread(target=start_orchestrator, daemon=True)
    orchestrator_thread.start()
    logger.info("Orchestrator started in background")

    # Start web server in main thread (this will block)
    logger.info("Starting web server with Swagger docs...")
    start_web_server()


if __name__ == "__main__":
    main()
