"""
Orchestrator Script
Manages Claude Code interactions, monitors folders, and coordinates the AI Employee system.
"""

import os
import sys
import time
import logging
import subprocess
import threading
from pathlib import Path
from datetime import datetime, timedelta
import json
import schedule
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class ClaudeOrchestrator:
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.done = self.vault_path / 'Done'
        self.approved = self.vault_path / 'Approved'
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.plans = self.vault_path / 'Plans'
        self.logs = self.vault_path / 'Logs'
        self.signals = self.vault_path / 'Signals'

        # Set up logging
        self.setup_logging()

        # Initialize folder monitoring
        self.approved_observer = Observer()
        self.approved_handler = ApprovedFileHandler(self)

    def setup_logging(self):
        """Set up logging for the orchestrator"""
        log_dir = self.logs / datetime.now().strftime('%Y-%m')
        log_dir.mkdir(exist_ok=True)

        log_file = log_dir / f"{datetime.now().strftime('%d')}.log"

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)

    def process_needs_action(self):
        """Process all files in the Needs_Action folder"""
        self.logger.info("Checking Needs_Action folder for new items...")

        action_files = list(self.needs_action.glob('*.md'))
        if not action_files:
            self.logger.info("No new items in Needs_Action folder")
            return

        for action_file in action_files:
            self.logger.info(f"Processing action file: {action_file.name}")

            # Move file to In_Progress to prevent duplicate processing
            in_progress_dir = self.vault_path / 'In_Progress'
            in_progress_dir.mkdir(exist_ok=True)
            in_progress_file = in_progress_dir / action_file.name

            try:
                action_file.rename(in_progress_file)

                # Create a plan for Claude to process
                self.create_plan_for_claude(in_progress_file)

                # Call Claude to process the plan
                self.run_claude_on_plan(in_progress_file)

                # Move to Done when complete
                done_file = self.done / in_progress_file.name
                in_progress_file.rename(done_file)

                self.logger.info(f"Completed processing: {done_file.name}")

            except Exception as e:
                self.logger.error(f"Error processing {action_file.name}: {e}")
                # Move to error handling if needed

    def create_plan_for_claude(self, action_file: Path):
        """Create a plan file that Claude will use to process the action"""
        # Read the action file
        content = action_file.read_text()

        # Create a plan based on the action
        plan_content = f"""# Plan for Processing {action_file.name}

## Original Action File
{content}

## Processing Steps
1. Analyze the request in the original file
2. Apply Company_Handbook.md rules
3. Follow appropriate procedures
4. Create any necessary output files
5. Update Dashboard.md with status
6. Move original file to Done when complete

## Context Files Available
- Company_Handbook.md - Rules and guidelines
- Business_Goals.md - Business objectives
- Dashboard.md - Current status
- Any files in the vault
"""

        plan_file = self.plans / f"PLAN_{action_file.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        plan_file.write_text(plan_content)
        self.logger.info(f"Created plan file: {plan_file.name}")

    def run_claude_on_plan(self, action_file: Path):
        """Execute Claude Code to process the plan"""
        try:
            # This would typically call Claude Code with the appropriate prompt
            # For now, we'll simulate the process
            self.logger.info(f"Simulating Claude processing of {action_file.name}")

            # In a real implementation, this would call Claude with:
            # claude --message "Please process the plan in Plans/..." --attach ...

            # Update dashboard to reflect activity
            self.update_dashboard(f"Processed {action_file.name}", "success")

        except Exception as e:
            self.logger.error(f"Error running Claude on {action_file.name}: {e}")
            self.update_dashboard(f"Failed to process {action_file.name}", "error")

    def monitor_approved_folder(self):
        """Monitor the Approved folder for files that need action"""
        self.approved_handler = ApprovedFileHandler(self)
        self.approved_observer.schedule(
            self.approved_handler,
            str(self.approved),
            recursive=False
        )
        self.approved_observer.start()
        self.logger.info("Started monitoring Approved folder")

    def process_approved_file(self, approved_file: Path):
        """Process a file that has been approved for action"""
        self.logger.info(f"Processing approved file: {approved_file.name}")

        # In a real implementation, this would execute the approved action
        # using the appropriate MCP server based on the file content

        # For now, we'll just log the action and move the file
        self.execute_approved_action(approved_file)

    def execute_approved_action(self, approved_file: Path):
        """Execute the action described in the approved file"""
        content = approved_file.read_text()

        # Parse the file to determine what action to take
        # This would typically involve calling an MCP server
        self.logger.info(f"Executing action from: {approved_file.name}")

        # Move to history after execution
        history_dir = self.vault_path / 'History'
        history_dir.mkdir(exist_ok=True)
        history_file = history_dir / f"DONE_{approved_file.name}"
        approved_file.rename(history_file)

        self.update_dashboard(f"Executed approved action: {approved_file.name}", "success")

    def update_dashboard(self, action: str, result: str):
        """Update the Dashboard.md file with the latest activity"""
        dashboard_path = self.vault_path / 'Dashboard.md'

        if dashboard_path.exists():
            content = dashboard_path.read_text()
        else:
            content = "# AI Employee Dashboard\n\n**Last Updated**: 2026-02-07\n**Status**: Initialized\n\n---\n\n## Recent Activity\n\n| Timestamp | Action | Result |\n|-----------|--------|--------|\n"

        # Find the recent activity table and add a new row
        lines = content.split('\n')
        new_lines = []
        inserted = False

        for line in lines:
            new_lines.append(line)
            if '| Timestamp | Action | Result |' in line and not inserted:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                new_lines.append(f"| {timestamp} | {action} | {result} |")
                inserted = True

        # If we didn't find the table, append to the end
        if not inserted:
            new_lines.extend([
                "",
                "## Recent Activity",
                "",
                "| Timestamp | Action | Result |",
                "|-----------|--------|--------|",
                f"| {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | {action} | {result} |"
            ])

        # Update the last updated timestamp
        final_content = '\n'.join(new_lines)
        final_content = final_content.replace(
            '**Last Updated**: 2026-02-07',
            f'**Last Updated**: {datetime.now().strftime("%Y-%m-%d")}'
        )

        dashboard_path.write_text(final_content)

    def start_regular_tasks(self):
        """Schedule regular tasks like the CEO briefing"""
        # Schedule weekly CEO briefing (Sunday night/Monday morning)
        schedule.every().sunday.at("23:00").do(self.generate_ceo_briefing)

        # Schedule daily status checks
        schedule.every().hour.do(self.process_needs_action)

        self.logger.info("Scheduled regular tasks")

    def generate_ceo_briefing(self):
        """Generate the weekly CEO briefing"""
        self.logger.info("Generating CEO briefing...")

        briefing_date = datetime.now().strftime('%Y-%m-%d')
        briefing_path = self.vault_path / 'Briefings' / f'{briefing_date}_Monday_Briefing.md'
        briefing_path.parent.mkdir(exist_ok=True)

        # Read business goals and recent activity
        goals_path = self.vault_path / 'Business_Goals.md'
        goals_content = goals_path.read_text() if goals_path.exists() else "No business goals defined"

        # Create briefing content
        briefing_content = f"""---
generated: {datetime.now().isoformat()}
period: {(datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')} to {briefing_date}
---

# Monday Morning CEO Briefing - {briefing_date}

## Executive Summary
Weekly business review and insights generated by AI Employee.

## Revenue Overview
- **This Week**: TBD
- **MTD**: TBD
- **Trend**: TBD

## Completed Tasks
<!-- List tasks from Done folder -->
- [Sample] Task completed during the week

## Bottlenecks
<!-- Identify delays or issues -->
- [Sample] No major bottlenecks identified

## Proactive Suggestions

### Cost Optimization
<!-- Flag unusual expenses -->
- [Sample] No cost optimization opportunities identified

### Upcoming Deadlines
<!-- List upcoming deadlines -->
- [Sample] No immediate deadlines

---
*Generated by AI Employee v0.1*
"""

        briefing_path.write_text(briefing_content)
        self.logger.info(f"Generated CEO briefing: {briefing_path}")

    def run(self):
        """Main run loop for the orchestrator"""
        self.logger.info("Starting Claude Orchestrator...")

        # Start monitoring folders
        self.monitor_approved_folder()

        # Schedule regular tasks
        self.start_regular_tasks()

        # Main loop
        try:
            while True:
                # Process any pending actions
                self.process_needs_action()

                # Run scheduled tasks
                schedule.run_pending()

                # Sleep to prevent excessive CPU usage
                time.sleep(30)  # Check every 30 seconds

        except KeyboardInterrupt:
            self.logger.info("Orchestrator stopped by user")
        finally:
            self.approved_observer.stop()
            self.approved_observer.join()


class ApprovedFileHandler(FileSystemEventHandler):
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator

    def on_created(self, event):
        if event.is_directory:
            return
        if event.src_path.endswith('.md'):
            approved_file = Path(event.src_path)
            self.orchestrator.process_approved_file(approved_file)

    def on_moved(self, event):
        if event.is_directory:
            return
        if event.dest_path.endswith('.md'):
            approved_file = Path(event.dest_path)
            self.orchestrator.process_approved_file(approved_file)


if __name__ == "__main__":
    # Get vault path from command line or use default
    vault_path = sys.argv[1] if len(sys.argv) > 1 else "."

    orchestrator = ClaudeOrchestrator(vault_path)
    orchestrator.run()