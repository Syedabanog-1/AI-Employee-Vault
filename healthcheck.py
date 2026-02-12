"""
Health Check Endpoint for AI Employee Vault
Provides HTTP health check + system diagnostics for container orchestration.
"""

import json
import os
import sys
import time
from datetime import datetime, timezone
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path


# Track start time for uptime calculation
START_TIME = time.time()


class HealthCheckHandler(BaseHTTPRequestHandler):
    """HTTP handler for health check and readiness probes."""

    def do_GET(self):
        if self.path == "/health":
            self._handle_health()
        elif self.path == "/ready":
            self._handle_readiness()
        elif self.path == "/metrics":
            self._handle_metrics()
        else:
            self.send_response(404)
            self.end_headers()

    def _handle_health(self):
        """Liveness probe - is the process alive?"""
        response = {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "uptime_seconds": round(time.time() - START_TIME, 2),
            "version": os.getenv("APP_VERSION", "1.0.0"),
        }
        self._send_json(200, response)

    def _handle_readiness(self):
        """Readiness probe - is the app ready to serve?"""
        vault_path = Path(os.getenv("VAULT_PATH", "/app"))
        checks = {
            "vault_accessible": vault_path.exists(),
            "inbox_exists": (vault_path / "Inbox").exists(),
            "needs_action_exists": (vault_path / "Needs_Action").exists(),
            "orchestrator_config": Path("orchestrator.py").exists(),
        }
        all_ready = all(checks.values())
        response = {
            "status": "ready" if all_ready else "not_ready",
            "checks": checks,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self._send_json(200 if all_ready else 503, response)

    def _handle_metrics(self):
        """Basic metrics endpoint for monitoring."""
        vault_path = Path(os.getenv("VAULT_PATH", "/app"))
        metrics = {
            "uptime_seconds": round(time.time() - START_TIME, 2),
            "queue_sizes": {
                "inbox": _count_files(vault_path / "Inbox"),
                "needs_action": _count_files(vault_path / "Needs_Action"),
                "pending_approval": _count_files(vault_path / "Pending_Approval"),
                "approved": _count_files(vault_path / "Approved"),
                "in_progress": _count_files(vault_path / "In_Progress"),
                "done": _count_files(vault_path / "Done"),
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self._send_json(200, metrics)

    def _send_json(self, status_code, data):
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode())

    def log_message(self, format, *args):
        """Suppress default logging to reduce noise."""
        pass


def _count_files(directory: Path) -> int:
    """Count markdown files in a directory."""
    if not directory.exists():
        return 0
    return len(list(directory.glob("*.md")))


def run_health_server(port: int = 8080):
    """Start the health check HTTP server."""
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    print(f"Health check server running on port {port}")
    server.serve_forever()


if __name__ == "__main__":
    # When run directly, check health and exit with appropriate code
    vault_path = Path(os.getenv("VAULT_PATH", "/app"))
    if vault_path.exists() and Path("orchestrator.py").exists():
        sys.exit(0)
    sys.exit(1)
