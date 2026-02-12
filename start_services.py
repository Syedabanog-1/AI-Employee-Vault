"""
Service Starter for AI Employee Vault
Launches orchestrator + health check server in parallel.
"""

import os
import sys
import threading
import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
logger = logging.getLogger("start_services")


def start_health_server():
    """Start the health check HTTP server in a background thread."""
    from healthcheck import run_health_server

    port = int(os.getenv("HEALTH_PORT", "8080"))
    run_health_server(port)


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

    # Start health check server in background thread
    health_thread = threading.Thread(target=start_health_server, daemon=True)
    health_thread.start()
    logger.info("Health check server started")

    # Start orchestrator in main thread
    start_orchestrator()


if __name__ == "__main__":
    main()
