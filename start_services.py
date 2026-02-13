"""
Service Starter for AI Employee Vault
Launches orchestrator + FastAPI web server in parallel.
Supports both legacy mode and Platinum Phase Cloud Agent mode.
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


def start_cloud_agent_api():
    """Start the Platinum Phase Cloud Agent API."""
    from Platinum_Phase.cloud_agent.api import run_cloud_agent_api
    
    # Railway injects PORT env var; fall back to HEALTH_PORT or 8080
    port = int(os.getenv("PORT", os.getenv("HEALTH_PORT", "8080")))
    
    # Run the Cloud Agent API with uvicorn
    run_cloud_agent_api(port)


def start_orchestrator():
    """Start the main orchestrator."""
    from orchestrator import ClaudeOrchestrator

    vault_path = os.getenv("VAULT_PATH", ".")
    orchestrator = ClaudeOrchestrator(vault_path)
    orchestrator.run()


def start_cloud_orchestrator():
    """Start the Cloud Agent orchestrator that monitors for tasks."""
    import time
    from pathlib import Path
    from datetime import datetime
    
    vault_path = Path(os.getenv("VAULT_PATH", "/app/vault"))
    inbox_path = vault_path / "Inbox"
    needs_action_path = vault_path / "Needs_Action"
    
    logger.info(f"Cloud Agent Orchestrator started, monitoring: {vault_path}")
    
    # Create required directories if they don't exist
    for dir_name in ["Inbox", "Needs_Action", "Pending_Approval", "In_Progress", "Done", "Logs", "Updates"]:
        (vault_path / dir_name).mkdir(exist_ok=True)
    
    # Create In_Progress/cloud-agent directory for claim-by-move
    (vault_path / "In_Progress" / "cloud-agent").mkdir(exist_ok=True)
    
    try:
        while True:
            # Process any new items in the Inbox
            inbox_files = list(inbox_path.glob('*.md')) if inbox_path.exists() else []
            
            for inbox_file in inbox_files:
                logger.info(f"Cloud Agent found new task: {inbox_file.name}")
                
                # Move to Needs_Action for processing
                needs_action_file = needs_action_path / inbox_file.name
                
                try:
                    inbox_file.rename(needs_action_file)
                    logger.info(f"Cloud Agent moved {inbox_file.name} to Needs_Action")
                    
                    # Here would be the actual processing logic
                    # For now, we'll just log the action
                    
                except Exception as e:
                    logger.error(f"Cloud Agent error processing {inbox_file.name}: {e}")
            
            # Sleep to prevent excessive CPU usage
            time.sleep(30)  # Check every 30 seconds
            
    except KeyboardInterrupt:
        logger.info("Cloud Agent Orchestrator stopped by user")


def main():
    logger.info("Starting AI Employee Vault services...")
    logger.info(f"Environment: {'production' if not os.getenv('DEV_MODE', 'true') == 'true' else 'development'}")
    logger.info(f"Vault path: {os.getenv('VAULT_PATH', '.')}")

    agent_type = os.getenv("AGENT_TYPE", "legacy")  # Default to legacy for backward compatibility
    
    if agent_type.lower() == "cloud":
        logger.info("Starting in Platinum Phase Cloud Agent mode...")
        
        # Start Cloud Agent orchestrator in background thread
        orchestrator_thread = threading.Thread(target=start_cloud_orchestrator, daemon=True)
        orchestrator_thread.start()
        logger.info("Cloud Agent Orchestrator started in background")

        # Start Cloud Agent API in main thread (this will block)
        logger.info("Starting Cloud Agent API with Swagger docs...")
        start_cloud_agent_api()
    else:
        logger.info("Starting in legacy mode...")
        
        # Start orchestrator in background thread
        orchestrator_thread = threading.Thread(target=start_orchestrator, daemon=True)
        orchestrator_thread.start()
        logger.info("Orchestrator started in background")

        # Start web server in main thread (this will block)
        logger.info("Starting web server with Swagger docs...")
        start_web_server()


if __name__ == "__main__":
    main()
