"""
AI Employee Vault - Web Server
Serves dashboard (frontend) + REST API (backend) + health probes.
"""

import json
import os
import sys
import time
import urllib.parse
from datetime import datetime, timezone
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path


START_TIME = time.time()
VAULT_PATH = Path(os.getenv("VAULT_PATH", "/app"))

QUEUE_FOLDERS = {
    "inbox": "Inbox",
    "needs_action": "Needs_Action",
    "pending_approval": "Pending_Approval",
    "approved": "Approved",
    "in_progress": "In_Progress",
    "done": "Done",
    "rejected": "Rejected",
}


class VaultAPIHandler(BaseHTTPRequestHandler):
    """Handles frontend dashboard + backend REST API."""

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path.rstrip("/") or "/"

        # --- Frontend ---
        if path == "/":
            self._handle_dashboard()

        # --- Health probes ---
        elif path == "/health":
            self._handle_health()
        elif path == "/ready":
            self._handle_readiness()

        # --- Backend API ---
        elif path == "/api":
            self._handle_api_index()
        elif path == "/api/status":
            self._handle_api_status()
        elif path == "/api/metrics":
            self._handle_api_metrics()
        elif path == "/api/queues":
            self._handle_api_queues()
        elif path.startswith("/api/queue/"):
            queue_name = path.split("/api/queue/")[1]
            self._handle_api_queue_detail(queue_name)
        elif path == "/api/config":
            self._handle_api_config()
        elif path == "/api/logs":
            self._handle_api_logs()

        # Legacy endpoint
        elif path == "/metrics":
            self._handle_api_metrics()

        else:
            self._send_json(404, {"error": "Not found", "path": path})

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path.rstrip("/")

        if path == "/api/inbox":
            self._handle_api_submit_task()
        else:
            self._send_json(404, {"error": "Not found", "path": path})

    # =========================================
    # Backend API Endpoints
    # =========================================

    def _handle_api_index(self):
        """GET /api - List all available backend API endpoints."""
        base = f"https://{self.headers.get('Host', 'localhost')}"
        response = {
            "service": "AI Employee Vault API",
            "version": os.getenv("APP_VERSION", "1.0.0"),
            "endpoints": {
                "GET /api": "This index - list all endpoints",
                "GET /api/status": "Full system status (health + queues + checks)",
                "GET /api/metrics": "Queue sizes and uptime metrics",
                "GET /api/queues": "All queue names and item counts",
                "GET /api/queue/{name}": "List items in a specific queue (inbox, needs_action, pending_approval, approved, in_progress, done, rejected)",
                "GET /api/config": "Current runtime configuration",
                "GET /api/logs": "Recent system log entries",
                "POST /api/inbox": "Submit a new task to Inbox (JSON body: {title, content})",
                "GET /health": "Liveness probe",
                "GET /ready": "Readiness probe",
            },
            "links": {
                "dashboard": f"{base}/",
                "status": f"{base}/api/status",
                "queues": f"{base}/api/queues",
            },
        }
        self._send_json(200, response)

    def _handle_api_status(self):
        """GET /api/status - Full system status."""
        uptime = round(time.time() - START_TIME, 2)
        checks = {
            "vault_accessible": VAULT_PATH.exists(),
            "inbox_exists": (VAULT_PATH / "Inbox").exists(),
            "needs_action_exists": (VAULT_PATH / "Needs_Action").exists(),
            "orchestrator_config": Path("orchestrator.py").exists(),
        }
        queues = {k: _count_files(VAULT_PATH / v) for k, v in QUEUE_FOLDERS.items()}

        response = {
            "status": "operational" if all(checks.values()) else "degraded",
            "uptime_seconds": uptime,
            "uptime_human": _format_uptime(uptime),
            "version": os.getenv("APP_VERSION", "1.0.0"),
            "environment": "production" if os.getenv("DEV_MODE", "true") != "true" else "development",
            "vault_path": str(VAULT_PATH),
            "system_checks": checks,
            "queues": queues,
            "total_items": sum(queues.values()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self._send_json(200, response)

    def _handle_api_metrics(self):
        """GET /api/metrics - Queue sizes and uptime."""
        uptime = round(time.time() - START_TIME, 2)
        queues = {k: _count_files(VAULT_PATH / v) for k, v in QUEUE_FOLDERS.items()}
        response = {
            "uptime_seconds": uptime,
            "queue_sizes": queues,
            "total_items": sum(queues.values()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self._send_json(200, response)

    def _handle_api_queues(self):
        """GET /api/queues - All queue names and counts."""
        queues = []
        for key, folder in QUEUE_FOLDERS.items():
            path = VAULT_PATH / folder
            count = _count_files(path)
            queues.append({
                "name": key,
                "folder": folder,
                "count": count,
                "detail_url": f"/api/queue/{key}",
            })
        self._send_json(200, {"queues": queues})

    def _handle_api_queue_detail(self, queue_name):
        """GET /api/queue/{name} - List items in a specific queue."""
        if queue_name not in QUEUE_FOLDERS:
            self._send_json(404, {
                "error": f"Queue '{queue_name}' not found",
                "available_queues": list(QUEUE_FOLDERS.keys()),
            })
            return

        folder = VAULT_PATH / QUEUE_FOLDERS[queue_name]
        items = []
        if folder.exists():
            for f in sorted(folder.glob("*.md"), key=lambda x: x.stat().st_mtime, reverse=True):
                stat = f.stat()
                # Read first 200 chars as preview
                try:
                    preview = f.read_text(encoding="utf-8")[:200]
                except Exception:
                    preview = "(unable to read)"
                items.append({
                    "filename": f.name,
                    "size_bytes": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
                    "created": datetime.fromtimestamp(stat.st_ctime, tz=timezone.utc).isoformat(),
                    "preview": preview,
                })

        self._send_json(200, {
            "queue": queue_name,
            "folder": QUEUE_FOLDERS[queue_name],
            "count": len(items),
            "items": items,
        })

    def _handle_api_config(self):
        """GET /api/config - Runtime configuration (no secrets)."""
        response = {
            "vault_path": str(VAULT_PATH),
            "dev_mode": os.getenv("DEV_MODE", "true"),
            "dry_run": os.getenv("DRY_RUN", "true"),
            "environment": os.getenv("ENVIRONMENT", "development"),
            "version": os.getenv("APP_VERSION", "1.0.0"),
            "port": os.getenv("PORT", os.getenv("HEALTH_PORT", "8080")),
            "integrations": {
                "google": bool(os.getenv("GOOGLE_CLIENT_ID")),
                "twitter": bool(os.getenv("TWITTER_API_KEY")),
                "facebook": bool(os.getenv("FACEBOOK_ACCESS_TOKEN")),
                "linkedin": bool(os.getenv("LINKEDIN_ACCESS_TOKEN")),
                "instagram": bool(os.getenv("INSTAGRAM_ACCESS_TOKEN")),
                "whatsapp": bool(os.getenv("WHATSAPP_ACCESS_TOKEN")),
                "odoo": bool(os.getenv("ODOO_URL")),
            },
        }
        self._send_json(200, response)

    def _handle_api_logs(self):
        """GET /api/logs - Recent log entries."""
        logs_dir = VAULT_PATH / "Logs"
        entries = []
        if logs_dir.exists():
            # Find most recent log files
            log_files = sorted(logs_dir.rglob("*.log"), key=lambda x: x.stat().st_mtime, reverse=True)[:3]
            for lf in log_files:
                try:
                    lines = lf.read_text(encoding="utf-8").strip().split("\n")
                    # Last 20 lines
                    entries.append({
                        "file": str(lf.relative_to(VAULT_PATH)),
                        "recent_lines": lines[-20:],
                    })
                except Exception:
                    pass

        self._send_json(200, {"log_files": entries, "count": len(entries)})

    def _handle_api_submit_task(self):
        """POST /api/inbox - Submit a new task to Inbox."""
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            if content_length == 0:
                self._send_json(400, {"error": "Empty request body. Send JSON: {title, content}"})
                return

            body = self.rfile.read(content_length).decode("utf-8")
            data = json.loads(body)

            title = data.get("title", "").strip()
            content = data.get("content", "").strip()

            if not title:
                self._send_json(400, {"error": "Missing 'title' field"})
                return

            # Create task file in Inbox
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            safe_title = "".join(c if c.isalnum() or c in "-_ " else "" for c in title).strip().replace(" ", "_")
            filename = f"{timestamp}_{safe_title}.md"
            filepath = VAULT_PATH / "Inbox" / filename

            task_content = f"""---
title: {title}
created: {datetime.now(timezone.utc).isoformat()}
source: api
status: new
---

# {title}

{content if content else "No description provided."}
"""
            filepath.write_text(task_content, encoding="utf-8")

            self._send_json(201, {
                "status": "created",
                "filename": filename,
                "queue": "inbox",
                "message": f"Task '{title}' submitted to Inbox",
            })

        except json.JSONDecodeError:
            self._send_json(400, {"error": "Invalid JSON body"})
        except Exception as e:
            self._send_json(500, {"error": str(e)})

    # =========================================
    # Health Probes
    # =========================================

    def _handle_health(self):
        response = {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "uptime_seconds": round(time.time() - START_TIME, 2),
            "version": os.getenv("APP_VERSION", "1.0.0"),
        }
        self._send_json(200, response)

    def _handle_readiness(self):
        checks = {
            "vault_accessible": VAULT_PATH.exists(),
            "inbox_exists": (VAULT_PATH / "Inbox").exists(),
            "needs_action_exists": (VAULT_PATH / "Needs_Action").exists(),
            "orchestrator_config": Path("orchestrator.py").exists(),
        }
        all_ready = all(checks.values())
        response = {
            "status": "ready" if all_ready else "not_ready",
            "checks": checks,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self._send_json(200 if all_ready else 503, response)

    # =========================================
    # Frontend Dashboard
    # =========================================

    def _handle_dashboard(self):
        uptime = round(time.time() - START_TIME, 2)
        hours = int(uptime // 3600)
        minutes = int((uptime % 3600) // 60)

        queues = {k: _count_files(VAULT_PATH / v) for k, v in QUEUE_FOLDERS.items()}
        checks = {
            "Vault": VAULT_PATH.exists(),
            "Inbox": (VAULT_PATH / "Inbox").exists(),
            "Orchestrator": Path("orchestrator.py").exists(),
        }
        all_ok = all(checks.values())

        queue_rows = "".join(
            f'<tr><td>{QUEUE_FOLDERS[k]}</td><td style="text-align:center;font-weight:bold">{v}</td></tr>'
            for k, v in queues.items()
        )
        check_rows = "".join(
            f'<tr><td>{name}</td><td style="text-align:center">'
            f'{"&#9989;" if ok else "&#10060;"}</td></tr>'
            for name, ok in checks.items()
        )

        base = f"https://{self.headers.get('Host', 'localhost')}"

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
  .container {{ max-width:780px; width:100%; }}
  h1 {{ font-size:1.8rem; margin-bottom:4px; color:#f8fafc; }}
  .subtitle {{ color:#94a3b8; margin-bottom:32px; font-size:0.95rem; }}
  .status-badge {{ display:inline-block; padding:4px 14px; border-radius:20px;
                   font-size:0.85rem; font-weight:600; margin-bottom:24px; }}
  .status-ok {{ background:#065f46; color:#6ee7b7; }}
  .status-err {{ background:#7f1d1d; color:#fca5a5; }}
  .card {{ background:#1e293b; border-radius:12px; padding:24px; margin-bottom:20px;
           border:1px solid #334155; }}
  .card h2 {{ font-size:0.8rem; color:#94a3b8; margin-bottom:16px; text-transform:uppercase;
              letter-spacing:0.05em; }}
  table {{ width:100%; border-collapse:collapse; }}
  td {{ padding:10px 12px; border-bottom:1px solid #334155; font-size:0.95rem; }}
  tr:last-child td {{ border-bottom:none; }}
  .metric {{ font-size:2rem; font-weight:700; color:#38bdf8; }}
  .metric-label {{ color:#94a3b8; font-size:0.85rem; }}
  .metrics-grid {{ display:grid; grid-template-columns:repeat(3,1fr); gap:16px; margin-bottom:20px; }}
  .metric-card {{ background:#1e293b; border-radius:12px; padding:20px; text-align:center;
                  border:1px solid #334155; }}
  .endpoints a {{ color:#38bdf8; text-decoration:none; font-size:0.9rem; display:block;
                  padding:6px 0; }}
  .endpoints a:hover {{ text-decoration:underline; }}
  .badge {{ display:inline-block; padding:2px 8px; border-radius:8px; font-size:0.7rem;
            font-weight:600; margin-left:8px; vertical-align:middle; }}
  .badge-get {{ background:#1e3a5f; color:#7dd3fc; }}
  .badge-post {{ background:#3b1f2b; color:#fda4af; }}
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
      <div class="metric">{queues.get("done", 0)}</div>
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
    <h2>Backend API</h2>
    <div class="endpoints">
      <a href="/api">/api <span class="badge badge-get">GET</span> - All endpoints index</a>
      <a href="/api/status">/api/status <span class="badge badge-get">GET</span> - Full system status</a>
      <a href="/api/queues">/api/queues <span class="badge badge-get">GET</span> - All queues</a>
      <a href="/api/queue/inbox">/api/queue/inbox <span class="badge badge-get">GET</span> - Inbox items</a>
      <a href="/api/queue/done">/api/queue/done <span class="badge badge-get">GET</span> - Completed items</a>
      <a href="/api/metrics">/api/metrics <span class="badge badge-get">GET</span> - Metrics</a>
      <a href="/api/config">/api/config <span class="badge badge-get">GET</span> - Configuration</a>
      <a href="/api/logs">/api/logs <span class="badge badge-get">GET</span> - Recent logs</a>
      <a href="#">/api/inbox <span class="badge badge-post">POST</span> - Submit task</a>
    </div>
  </div>

  <div class="card">
    <h2>Health Probes</h2>
    <div class="endpoints">
      <a href="/health">/health <span class="badge badge-get">GET</span> - Liveness</a>
      <a href="/ready">/ready <span class="badge badge-get">GET</span> - Readiness</a>
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

    # =========================================
    # Helpers
    # =========================================

    def _send_json(self, status_code, data):
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode())

    def log_message(self, format, *args):
        pass


def _count_files(directory: Path) -> int:
    if not directory.exists():
        return 0
    return len(list(directory.glob("*.md")))


def _format_uptime(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    return f"{h}h {m}m {s}s"


def run_health_server(port: int = 8080):
    server = HTTPServer(("0.0.0.0", port), VaultAPIHandler)
    print(f"Health check server running on port {port}")
    server.serve_forever()


if __name__ == "__main__":
    vault_path = Path(os.getenv("VAULT_PATH", "/app"))
    if vault_path.exists() and Path("orchestrator.py").exists():
        sys.exit(0)
    sys.exit(1)
