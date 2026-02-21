"""
Platinum Phase - Cloud Agent API
REST API for Cloud-based AI Employee with Swagger documentation
"""

import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel


# =========================================
# Config
# =========================================
START_TIME = time.time()
VAULT_PATH = Path(os.getenv("VAULT_PATH", "/app/vault"))
CLOUD_AGENT_ID = "cloud-agent"

QUEUE_FOLDERS = {
    "inbox": "Inbox",
    "needs_action": "Needs_Action",
    "pending_approval": "Pending_Approval",
    "approved": "Approved",
    "in_progress": "In_Progress",
    "done": "Done",
    "rejected": "Rejected",
    "updates": "Updates",
}

# =========================================
# FastAPI App
# =========================================
app = FastAPI(
    title="AI Employee Vault - Cloud Agent API",
    description="""
## AI Employee Vault - Cloud Agent (Platinum Phase)

Cloud-based AI Employee that operates 24/7, handling draft creation and monitoring.
This agent follows the Platinum Phase specification with clear separation of duties:
- **Cloud Agent**: Draft-only operations (emails, social posts, Odoo entries)
- **Local Agent**: Execution of sensitive actions (sending, payments, approvals)

### Features
- **Draft Creation**: Create draft emails, social posts, and Odoo entries
- **24/7 Monitoring**: Continuous monitoring of incoming tasks
- **Claim-by-Move**: Prevent duplicate work using /In_Progress/<agent>/ folders
- **Vault Sync**: Secure synchronization with local vault (excludes credentials)
- **Health Monitoring**: Self-monitoring and auto-recovery

### Work Zone Specialization
```
Cloud Agent → Drafts only (emails, social, Odoo entries)
Local Agent → Execution only (sending, payments, approvals)
```
    """,
    version="2.0.0-platinum",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================
# Pydantic Models
# =========================================
class TaskSubmit(BaseModel):
    """Submit a new task to the Inbox."""
    title: str
    content: Optional[str] = ""
    priority: str = "normal"  # normal, high, urgent

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Review quarterly report",
                "content": "Please review the Q1 2026 quarterly report and prepare a summary.",
                "priority": "normal"
            }
        }


class ApprovalRequest(BaseModel):
    """Request approval for a draft action."""
    task_id: str
    action_type: str  # email, social, odoo, etc.
    draft_content: str
    target_system: str  # email, twitter, facebook, odoo, etc.


# =========================================
# Helpers
# =========================================
def _count_files(directory: Path) -> int:
    if not directory.exists():
        return 0
    return len(list(directory.glob("*.md")))


def _format_uptime(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    return f"{h}h {m}m {s}s"


def _claim_task(task_file: Path, agent_id: str) -> Optional[Path]:
    """Atomically move task to agent's in-progress folder to claim ownership."""
    agent_progress_folder = VAULT_PATH / "In_Progress" / agent_id
    agent_progress_folder.mkdir(exist_ok=True)
    
    claimed_task = agent_progress_folder / task_file.name
    
    try:
        task_file.rename(claimed_task)
        return claimed_task
    except FileNotFoundError:
        # Task was already claimed by another agent
        return None


# =========================================
# Frontend - Dashboard
# =========================================
@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def dashboard():
    """Live HTML dashboard for Cloud Agent - auto-refreshes every 30s."""
    uptime = round(time.time() - START_TIME, 2)
    hours = int(uptime // 3600)
    minutes = int((uptime % 3600) // 60)

    queues = {k: _count_files(VAULT_PATH / v) for k, v in QUEUE_FOLDERS.items()}
    checks = {
        "Vault": VAULT_PATH.exists(),
        "Inbox": (VAULT_PATH / "Inbox").exists(),
        "In_Progress": (VAULT_PATH / "In_Progress").exists(),
        "Cloud_Agent_Config": Path(__file__).exists(),
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

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta http-equiv="refresh" content="30">
<title>AI Employee Vault - Cloud Agent</title>
<style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
         background: linear-gradient(135deg, #0f172a, #1e293b); color: #e2e8f0; min-height:100vh;
         display:flex; justify-content:center; padding:40px 20px; }}
  .container {{ max-width:800px; width:100%; }}
  h1 {{ font-size:1.8rem; margin-bottom:4px; color:#f8fafc; }}
  .subtitle {{ color:#94a3b8; margin-bottom:32px; font-size:0.95rem; }}
  .status-badge {{ display:inline-block; padding:4px 14px; border-radius:20px;
                   font-size:0.85rem; font-weight:600; margin-bottom:24px; }}
  .status-ok {{ background:#065f46; color:#6ee7b7; }}
  .status-err {{ background:#7f1d1d; color:#fca5a5; }}
  .card {{ background:#1e293b; border-radius:12px; padding:24px; margin-bottom:20px;
           border:1px solid #334155; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
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
  .badge-swagger {{ background:#2d1b4e; color:#c084fc; }}
  .footer {{ text-align:center; color:#475569; font-size:0.8rem; margin-top:32px; }}
  .agent-info {{ background:linear-gradient(45deg, #4f46e5, #7c3aed); padding:16px; border-radius:8px; 
                 margin-bottom:20px; text-align:center; }}
  .agent-name {{ font-size:1.2rem; font-weight:bold; color:white; }}
  .agent-role {{ color:#c7d2fe; font-size:0.9rem; }}
</style>
</head>
<body>
<div class="container">
  <div class="agent-info">
    <div class="agent-name">AI Employee - Cloud Agent</div>
    <div class="agent-role">24/7 Draft Creation & Monitoring (Platinum Phase)</div>
  </div>
  
  <h1>Cloud Agent Dashboard</h1>
  <p class="subtitle">Always-On AI Employee System - Draft Operations Only</p>

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
    <h2>Swagger UI & Docs</h2>
    <div class="endpoints">
      <a href="/docs">/docs <span class="badge badge-swagger">SWAGGER</span> - Interactive API Testing</a>
      <a href="/redoc">/redoc <span class="badge badge-swagger">REDOC</span> - API Documentation</a>
      <a href="/openapi.json">/openapi.json <span class="badge badge-get">GET</span> - OpenAPI Schema</a>
    </div>
  </div>

  <div class="card">
    <h2>Cloud Agent API</h2>
    <div class="endpoints">
      <a href="/api/status">/api/status <span class="badge badge-get">GET</span> - Full system status</a>
      <a href="/api/queues">/api/queues <span class="badge badge-get">GET</span> - All queues</a>
      <a href="/api/queue/inbox">/api/queue/inbox <span class="badge badge-get">GET</span> - Inbox items</a>
      <a href="/api/queue/done">/api/queue/done <span class="badge badge-get">GET</span> - Completed items</a>
      <a href="/api/metrics">/api/metrics <span class="badge badge-get">GET</span> - Metrics</a>
      <a href="/api/config">/api/config <span class="badge badge-get">GET</span> - Configuration</a>
      <a href="/api/logs">/api/logs <span class="badge badge-get">GET</span> - Recent logs</a>
      <a href="#">/api/inbox <span class="badge badge-post">POST</span> - Submit task</a>
      <a href="/api/claim-task">/api/claim-task <span class="badge badge-post">POST</span> - Claim a task</a>
      <a href="/api/draft-email">/api/draft-email <span class="badge badge-post">POST</span> - Draft an email</a>
    </div>
  </div>

  <div class="card">
    <h2>Health Probes</h2>
    <div class="endpoints">
      <a href="/health">/health <span class="badge badge-get">GET</span> - Liveness</a>
      <a href="/ready">/ready <span class="badge badge-get">GET</span> - Readiness</a>
    </div>
  </div>

  <p class="footer">v2.0.0-platinum &middot; Cloud Agent &middot; FastAPI + Swagger &middot; Auto-refreshes every 30s</p>
</div>
</body>
</html>"""
    return HTMLResponse(content=html)


# =========================================
# Health Probes
# =========================================
@app.get("/health", tags=["Health"])
async def health_check():
    """Liveness probe - is the Cloud Agent service alive?"""
    return {
        "status": "healthy",
        "agent": "cloud",
        "role": "draft-only",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "uptime_seconds": round(time.time() - START_TIME, 2),
        "version": os.getenv("APP_VERSION", "2.0.0-platinum"),
    }


@app.get("/ready", tags=["Health"])
async def readiness_check():
    """Readiness probe - is the Cloud Agent ready to handle requests?"""
    checks = {
        "vault_accessible": VAULT_PATH.exists(),
        "inbox_exists": (VAULT_PATH / "Inbox").exists(),
        "in_progress_exists": (VAULT_PATH / "In_Progress").exists(),
        "cloud_agent_config": Path(__file__).exists(),
        "agent_id": CLOUD_AGENT_ID,
    }
    all_ready = all(checks.values())
    return {
        "status": "ready" if all_ready else "not_ready",
        "agent": "cloud",
        "checks": checks,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


# =========================================
# Backend API
# =========================================
@app.get("/api/status", tags=["System"])
async def system_status():
    """Full system status - health, queues, checks, uptime."""
    uptime = round(time.time() - START_TIME, 2)
    checks = {
        "vault_accessible": VAULT_PATH.exists(),
        "inbox_exists": (VAULT_PATH / "Inbox").exists(),
        "in_progress_exists": (VAULT_PATH / "In_Progress").exists(),
        "cloud_agent_config": Path(__file__).exists(),
    }
    queues = {k: _count_files(VAULT_PATH / v) for k, v in QUEUE_FOLDERS.items()}
    return {
        "status": "operational" if all(checks.values()) else "degraded",
        "agent": "cloud",
        "role": "draft-only",
        "uptime_seconds": uptime,
        "uptime_human": _format_uptime(uptime),
        "version": os.getenv("APP_VERSION", "2.0.0-platinum"),
        "environment": "production" if os.getenv("DEV_MODE", "true") != "true" else "development",
        "vault_path": str(VAULT_PATH),
        "system_checks": checks,
        "queues": queues,
        "total_items": sum(queues.values()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/api/metrics", tags=["System"])
async def metrics():
    """Queue sizes and uptime metrics."""
    uptime = round(time.time() - START_TIME, 2)
    queues = {k: _count_files(VAULT_PATH / v) for k, v in QUEUE_FOLDERS.items()}
    return {
        "agent": "cloud",
        "uptime_seconds": uptime,
        "queue_sizes": queues,
        "total_items": sum(queues.values()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/api/queues", tags=["Queues"])
async def list_queues():
    """List all queues with item counts."""
    queues_info = []
    for key, folder in QUEUE_FOLDERS.items():
        count = _count_files(VAULT_PATH / folder)
        queues_info.append({
            "name": key,
            "folder": folder,
            "count": count,
            "detail_url": f"/api/queue/{key}",
            "agent_access": "read" if key in ["inbox", "needs_action", "pending_approval"] else "limited"
        })
    return {"agent": "cloud", "queues": queues_info}


@app.get("/api/queue/{queue_name}", tags=["Queues"])
async def queue_detail(queue_name: str):
    """List all items in a specific queue with file previews.

    Cloud Agent can view all queues but can only modify draft-related ones.
    """
    if queue_name not in QUEUE_FOLDERS:
        raise HTTPException(
            status_code=404,
            detail=f"Queue '{queue_name}' not found. Available: {list(QUEUE_FOLDERS.keys())}"
        )

    folder = VAULT_PATH / QUEUE_FOLDERS[queue_name]
    items = []
    if folder.exists():
        for f in sorted(folder.glob("*.md"), key=lambda x: x.stat().st_mtime, reverse=True):
            stat = f.stat()
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
                "agent_permission": "read" if queue_name in ["inbox", "needs_action", "pending_approval"] else "view_only"
            })

    return {
        "agent": "cloud",
        "queue": queue_name,
        "folder": QUEUE_FOLDERS[queue_name],
        "count": len(items),
        "items": items,
    }


@app.post("/api/inbox", tags=["Tasks"], status_code=201)
async def submit_task(task: TaskSubmit):
    """Submit a new task to the Inbox queue.

    The task will be created as a markdown file in the Inbox folder
    and picked up by the orchestrator for processing.
    """
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    safe_title = "".join(c if c.isalnum() or c in "-_ " else "" for c in task.title).strip().replace(" ", "_")
    filename = f"{timestamp}_{safe_title}.md"
    filepath = VAULT_PATH / "Inbox" / filename

    task_content = f"""---
title: {task.title}
created: {datetime.now(timezone.utc).isoformat()}
source: cloud-api
status: new
priority: {task.priority}
agent: cloud
---

# {task.title}

{task.content if task.content else "No description provided."}

## Task Details
- **Submitted by**: Cloud Agent API
- **Priority**: {task.priority}
- **Agent Role**: draft-creation
"""
    filepath.write_text(task_content, encoding="utf-8")

    return {
        "status": "created",
        "agent": "cloud",
        "filename": filename,
        "queue": "inbox",
        "message": f"Task '{task.title}' submitted to Inbox",
    }


@app.post("/api/claim-task", tags=["Tasks"], status_code=200)
async def claim_task_api(queue_name: str, filename: str):
    """Claim a task using the claim-by-move mechanism.
    
    Moves the task file to /In_Progress/cloud-agent/ to establish ownership.
    Prevents duplicate work between Cloud and Local agents.
    """
    if queue_name not in QUEUE_FOLDERS:
        raise HTTPException(
            status_code=404,
            detail=f"Queue '{queue_name}' not found. Available: {list(QUEUE_FOLDERS.keys())}"
        )
        
    source_folder = VAULT_PATH / QUEUE_FOLDERS[queue_name]
    task_file = source_folder / filename
    
    if not task_file.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Task file '{filename}' not found in queue '{queue_name}'"
        )
    
    # Attempt to claim the task (atomically move to In_Progress/<agent>/)
    claimed_task = _claim_task(task_file, CLOUD_AGENT_ID)
    
    if claimed_task:
        return {
            "status": "claimed",
            "agent": "cloud",
            "original_queue": queue_name,
            "claimed_file": str(claimed_task.relative_to(VAULT_PATH)),
            "message": f"Task '{filename}' claimed by Cloud Agent"
        }
    else:
        return {
            "status": "already_claimed",
            "agent": "cloud",
            "message": f"Task '{filename}' was already claimed by another agent"
        }


@app.post("/api/draft-email", tags=["Draft Operations"], status_code=201)
async def draft_email(background_tasks: BackgroundTasks, subject: str, body: str, recipient: str):
    """Create a draft email in the Pending_Approval queue.
    
    Cloud Agent creates drafts but never sends them - Local Agent must approve and send.
    """
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    filename = f"draft_email_{timestamp}_{recipient.replace('@', '_at_').replace('.', '_dot_')}.md"
    filepath = VAULT_PATH / "Pending_Approval" / filename

    draft_content = f"""---
type: email_draft
created: {datetime.now(timezone.utc).isoformat()}
source: cloud-agent
status: pending_approval
agent: cloud
target: email
recipient: {recipient}
subject: {subject}
---

# Email Draft

**To**: {recipient}
**Subject**: {subject}

{body}

## Approval Required
This email draft requires local approval before sending.
Action: approve-send-email
"""
    filepath.write_text(draft_content, encoding="utf-8")

    return {
        "status": "draft_created",
        "agent": "cloud",
        "filename": filename,
        "queue": "pending_approval",
        "message": f"Email draft for '{recipient}' created and placed in Pending Approval",
        "draft_file": str(filepath.relative_to(VAULT_PATH))
    }


@app.get("/api/config", tags=["System"])
async def runtime_config():
    """Current runtime configuration (secrets are never exposed)."""
    return {
        "agent": "cloud",
        "role": "draft-only",
        "vault_path": str(VAULT_PATH),
        "agent_id": CLOUD_AGENT_ID,
        "dev_mode": os.getenv("DEV_MODE", "true"),
        "environment": os.getenv("ENVIRONMENT", "development"),
        "version": os.getenv("APP_VERSION", "2.0.0-platinum"),
        "port": os.getenv("PORT", os.getenv("HEALTH_PORT", "8080")),
        "permissions": {
            "can_create_drafts": True,
            "can_execute_actions": False,
            "can_modify_dashboard": False,
            "can_access_credentials": False
        },
        "integrations": {
            "email_monitoring": True,  # Can monitor, not send
            "social_monitoring": True,  # Can monitor, not post
            "odoo_monitoring": True,  # Can monitor, not execute
            "whatsapp_access": False,  # Cloud never accesses WhatsApp
            "payment_processing": False,  # Cloud never processes payments
        },
    }


@app.get("/api/logs", tags=["System"])
async def recent_logs():
    """Recent system log entries from the Logs directory."""
    logs_dir = VAULT_PATH / "Logs"
    entries = []
    if logs_dir.exists():
        log_files = sorted(logs_dir.rglob("*.log"), key=lambda x: x.stat().st_mtime, reverse=True)[:3]
        for lf in log_files:
            try:
                lines = lf.read_text(encoding="utf-8").strip().split("\n")
                entries.append({
                    "file": str(lf.relative_to(VAULT_PATH)),
                    "recent_lines": lines[-20:],
                })
            except Exception:
                pass
    return {"agent": "cloud", "log_files": entries, "count": len(entries)}


# =========================================
# Server runner
# =========================================
def run_cloud_agent_api(port: int = 8080):
    """Start Cloud Agent API with uvicorn."""
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8080"))
    run_cloud_agent_api(port)