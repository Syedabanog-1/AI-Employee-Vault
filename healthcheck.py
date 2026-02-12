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
        if self.path == "/" or self.path == "":
            self._handle_dashboard()
        elif self.path == "/health":
            self._handle_health()
        elif self.path == "/ready":
            self._handle_readiness()
        elif self.path == "/metrics":
            self._handle_metrics()
        else:
            self.send_response(404)
            self.end_headers()

    def _handle_dashboard(self):
        """Root path - HTML dashboard with live system status."""
        vault_path = Path(os.getenv("VAULT_PATH", "/app"))
        uptime = round(time.time() - START_TIME, 2)
        hours = int(uptime // 3600)
        minutes = int((uptime % 3600) // 60)
        seconds = int(uptime % 60)

        queues = {
            "Inbox": _count_files(vault_path / "Inbox"),
            "Needs Action": _count_files(vault_path / "Needs_Action"),
            "Pending Approval": _count_files(vault_path / "Pending_Approval"),
            "Approved": _count_files(vault_path / "Approved"),
            "In Progress": _count_files(vault_path / "In_Progress"),
            "Done": _count_files(vault_path / "Done"),
        }

        checks = {
            "Vault": vault_path.exists(),
            "Inbox": (vault_path / "Inbox").exists(),
            "Orchestrator": Path("orchestrator.py").exists(),
        }
        all_ok = all(checks.values())

        queue_rows = "".join(
            f'<tr><td>{name}</td><td style="text-align:center;font-weight:bold">{count}</td></tr>'
            for name, count in queues.items()
        )
        check_rows = "".join(
            f'<tr><td>{name}</td><td style="text-align:center">'
            f'{"&#9989;" if ok else "&#10060;"}</td></tr>'
            for name, ok in checks.items()
        )

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta http-equiv="refresh" content="30">
<title>AI Employee Vault</title>
<style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
         background: #0f172a; color: #e2e8f0; min-height:100vh;
         display:flex; justify-content:center; padding:40px 20px; }}
  .container {{ max-width:720px; width:100%; }}
  h1 {{ font-size:1.8rem; margin-bottom:4px; color:#f8fafc; }}
  .subtitle {{ color:#94a3b8; margin-bottom:32px; font-size:0.95rem; }}
  .status-badge {{ display:inline-block; padding:4px 14px; border-radius:20px;
                   font-size:0.85rem; font-weight:600; margin-bottom:24px; }}
  .status-ok {{ background:#065f46; color:#6ee7b7; }}
  .status-err {{ background:#7f1d1d; color:#fca5a5; }}
  .card {{ background:#1e293b; border-radius:12px; padding:24px; margin-bottom:20px;
           border:1px solid #334155; }}
  .card h2 {{ font-size:1.1rem; color:#94a3b8; margin-bottom:16px; text-transform:uppercase;
              letter-spacing:0.05em; font-size:0.8rem; }}
  table {{ width:100%; border-collapse:collapse; }}
  td {{ padding:10px 12px; border-bottom:1px solid #334155; font-size:0.95rem; }}
  tr:last-child td {{ border-bottom:none; }}
  .metric {{ font-size:2rem; font-weight:700; color:#38bdf8; }}
  .metric-label {{ color:#94a3b8; font-size:0.85rem; }}
  .metrics-grid {{ display:grid; grid-template-columns:repeat(3,1fr); gap:16px; margin-bottom:20px; }}
  .metric-card {{ background:#1e293b; border-radius:12px; padding:20px; text-align:center;
                  border:1px solid #334155; }}
  .endpoints {{ margin-top:8px; }}
  .endpoints a {{ color:#38bdf8; text-decoration:none; margin-right:16px; font-size:0.9rem; }}
  .endpoints a:hover {{ text-decoration:underline; }}
  .footer {{ text-align:center; color:#475569; font-size:0.8rem; margin-top:32px; }}
</style>
</head>
<body>
<div class="container">
  <h1>AI Employee Vault</h1>
  <p class="subtitle">Autonomous Personal Assistant System</p>

  <span class="status-badge {"status-ok" if all_ok else "status-err"}">
    {"OPERATIONAL" if all_ok else "DEGRADED"}
  </span>

  <div class="metrics-grid">
    <div class="metric-card">
      <div class="metric">{hours}h {minutes}m</div>
      <div class="metric-label">Uptime</div>
    </div>
    <div class="metric-card">
      <div class="metric">{sum(queues.values())}</div>
      <div class="metric-label">Total Items</div>
    </div>
    <div class="metric-card">
      <div class="metric">{queues["Done"]}</div>
      <div class="metric-label">Completed</div>
    </div>
  </div>

  <div class="card">
    <h2>Queue Status</h2>
    <table>{queue_rows}</table>
  </div>

  <div class="card">
    <h2>System Checks</h2>
    <table>{check_rows}</table>
  </div>

  <div class="card">
    <h2>API Endpoints</h2>
    <div class="endpoints">
      <a href="/health">/health</a>
      <a href="/ready">/ready</a>
      <a href="/metrics">/metrics</a>
    </div>
  </div>

  <p class="footer">v{os.getenv("APP_VERSION", "1.0.0")} &middot; Auto-refreshes every 30s &middot; {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")}</p>
</div>
</body>
</html>"""

        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode())

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
