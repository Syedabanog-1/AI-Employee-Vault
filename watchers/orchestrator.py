"""
Orchestrator - The Master Controller for AI Employee.
Part of Personal AI Employee Hackathon 0 - Silver/Gold/Platinum Phases.

The Orchestrator coordinates all watchers, triggers Claude processing,
handles approvals, and manages the overall workflow.
"""

import os
import sys
import json
import time
import subprocess
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict
import schedule

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('Orchestrator')


class Orchestrator:
    """
    Master controller that coordinates the AI Employee system.

    Responsibilities:
    - Monitor folders for new tasks
    - Trigger Claude processing
    - Handle approval workflow
    - Manage watcher processes
    - Schedule recurring tasks
    """

    def __init__(self, vault_path: str, dry_run: bool = None):
        """
        Initialize the Orchestrator.

        Args:
            vault_path: Path to the Obsidian vault
            dry_run: If True, log actions but don't execute
        """
        self.vault_path = Path(vault_path)
        self.dry_run = dry_run if dry_run is not None else \
            os.getenv('DRY_RUN', 'false').lower() == 'true'

        # Folder paths
        self.needs_action = self.vault_path / 'Needs_Action'
        self.plans = self.vault_path / 'Plans'
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.approved = self.vault_path / 'Approved'
        self.rejected = self.vault_path / 'Rejected'
        self.done = self.vault_path / 'Done'
        self.logs_path = self.vault_path / 'Logs'

        # Ensure folders exist
        for folder in [self.needs_action, self.plans, self.pending_approval,
                       self.approved, self.rejected, self.done, self.logs_path]:
            folder.mkdir(parents=True, exist_ok=True)

        # Watcher processes
        self.watcher_processes: Dict[str, subprocess.Popen] = {}

        logger.info(f"Orchestrator initialized")
        logger.info(f"Vault: {self.vault_path}")
        logger.info(f"Dry run: {self.dry_run}")

    def log_action(self, action_type: str, details: dict):
        """Write to daily log file."""
        log_file = self.logs_path / f"{datetime.now().strftime('%Y-%m-%d')}.json"

        entry = {
            "timestamp": datetime.now().isoformat(),
            "action_type": action_type,
            "actor": "orchestrator",
            "details": details
        }

        if self.dry_run:
            logger.info(f"[DRY RUN] Would log: {json.dumps(entry)}")
            return

        if log_file.exists():
            with open(log_file, 'r') as f:
                logs = json.load(f)
        else:
            logs = []

        logs.append(entry)

        with open(log_file, 'w') as f:
            json.dump(logs, f, indent=2)

    # =========================================
    # Watcher Management
    # =========================================

    def start_watcher(self, name: str, script_path: str, args: List[str] = None):
        """
        Start a watcher process.

        Args:
            name: Unique name for the watcher
            script_path: Path to the watcher script
            args: Additional command line arguments
        """
        if name in self.watcher_processes:
            logger.warning(f"Watcher {name} already running")
            return

        cmd = [sys.executable, script_path]
        if args:
            cmd.extend(args)

        logger.info(f"Starting watcher: {name}")

        if self.dry_run:
            logger.info(f"[DRY RUN] Would start: {' '.join(cmd)}")
            return

        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        self.watcher_processes[name] = process

        self.log_action("watcher_started", {"name": name, "pid": process.pid})

    def stop_watcher(self, name: str):
        """Stop a watcher process."""
        if name not in self.watcher_processes:
            logger.warning(f"Watcher {name} not running")
            return

        process = self.watcher_processes[name]
        process.terminate()
        process.wait(timeout=10)

        del self.watcher_processes[name]
        logger.info(f"Stopped watcher: {name}")

        self.log_action("watcher_stopped", {"name": name})

    def check_watchers(self):
        """Check if watchers are still running, restart if needed."""
        for name, process in list(self.watcher_processes.items()):
            if process.poll() is not None:
                logger.warning(f"Watcher {name} died, restarting...")
                # TODO: Implement restart logic
                self.log_action("watcher_crashed", {"name": name})

    # =========================================
    # Task Processing
    # =========================================

    def check_needs_action(self) -> List[Path]:
        """Get list of files in /Needs_Action."""
        return list(self.needs_action.glob('*.md'))

    def trigger_claude_processing(self, task_file: Path):
        """
        Trigger Claude to process a task file.

        Args:
            task_file: Path to the task file
        """
        logger.info(f"Triggering Claude for: {task_file.name}")

        if self.dry_run:
            logger.info(f"[DRY RUN] Would trigger Claude")
            return

        # TODO: Implement Claude Code invocation
        # This would use subprocess to call Claude Code
        # with appropriate prompt

        self.log_action("claude_triggered", {"task": str(task_file)})

    # =========================================
    # Approval Workflow
    # =========================================

    def check_approved(self) -> List[Path]:
        """Get list of files in /Approved."""
        return list(self.approved.glob('*.md'))

    def execute_approved_action(self, approval_file: Path):
        """
        Execute an approved action.

        Args:
            approval_file: Path to the approved action file
        """
        logger.info(f"Executing approved action: {approval_file.name}")

        if self.dry_run:
            logger.info(f"[DRY RUN] Would execute action")
            return

        # Read approval file to get action details
        content = approval_file.read_text()

        # TODO: Parse action type and call appropriate MCP
        # This would use Claude Code or direct MCP calls

        # Move to done after execution
        dest = self.done / approval_file.name
        approval_file.rename(dest)

        self.log_action("action_executed", {
            "file": approval_file.name,
            "result": "success"
        })

    # =========================================
    # Scheduled Tasks
    # =========================================

    def setup_schedules(self):
        """Set up scheduled tasks."""

        # Daily dashboard update
        schedule.every().day.at("08:00").do(self.daily_briefing)

        # Weekly CEO briefing (Sunday night)
        schedule.every().sunday.at("22:00").do(self.weekly_ceo_briefing)

        # Health check every minute
        schedule.every(1).minutes.do(self.check_watchers)

        logger.info("Schedules configured")

    def daily_briefing(self):
        """Generate daily briefing."""
        logger.info("Generating daily briefing...")
        self.log_action("daily_briefing", {"status": "generated"})

    def weekly_ceo_briefing(self):
        """Generate weekly CEO briefing (Gold phase)."""
        logger.info("Generating CEO briefing...")
        # TODO: Implement CEO briefing generation
        self.log_action("ceo_briefing", {"status": "generated"})

    # =========================================
    # Main Loop
    # =========================================

    def run(self):
        """Main orchestrator loop."""
        logger.info("Starting Orchestrator main loop...")

        self.setup_schedules()

        while True:
            try:
                # Run scheduled tasks
                schedule.run_pending()

                # Check for new tasks
                tasks = self.check_needs_action()
                for task in tasks:
                    self.trigger_claude_processing(task)

                # Check for approved actions
                approved = self.check_approved()
                for action in approved:
                    self.execute_approved_action(action)

                # Check watcher health
                self.check_watchers()

                time.sleep(30)  # Main loop interval

            except KeyboardInterrupt:
                logger.info("Shutting down...")
                break
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                self.log_action("error", {"error": str(e)})
                time.sleep(60)  # Wait before retrying

        # Cleanup
        for name in list(self.watcher_processes.keys()):
            self.stop_watcher(name)


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description='AI Employee Orchestrator'
    )
    parser.add_argument(
        '--vault',
        default=os.getenv('VAULT_PATH', r'D:\syeda Gulzar Bano\AI_Employee_Vault_'),
        help='Path to Obsidian vault'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Log actions without executing'
    )

    args = parser.parse_args()

    orchestrator = Orchestrator(
        vault_path=args.vault,
        dry_run=args.dry_run
    )

    print("=" * 50)
    print("AI Employee Orchestrator")
    print("=" * 50)
    print(f"Vault: {orchestrator.vault_path}")
    print(f"Dry run: {orchestrator.dry_run}")
    print("Press Ctrl+C to stop")
    print("=" * 50)

    orchestrator.run()


if __name__ == "__main__":
    main()
