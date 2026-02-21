"""
Platinum Phase - Local Agent API
REST API for Local-based AI Employee with Swagger documentation
"""

import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel


# =========================================
# Config
# =========================================
START_TIME = time.time()
VAULT_PATH = Path(os.getenv("VAULT_PATH", "./vault"))
LOCAL_AGENT_ID = "local-agent"

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
    title="AI Employee Vault - Local Agent API",
    description="""
## AI Employee Vault - Local Agent (Platinum Phase)

Local-based AI Employee that handles execution of sensitive actions.
This agent follows the Platinum Phase specification with clear separation of duties:
- **Cloud Agent**: Draft-only operations (emails, social posts, Odoo entries)
- **Local Agent**: Execution of sensitive actions (sending, payments, approvals)

### Features
- **Action Execution**: Execute approved actions via MCP servers
- **Sensitive Operations**: Handle payments, WhatsApp, and other secure operations
- **Claim-by-Move**: Prevent duplicate work using /In_Progress/<agent>/ folders
- **Dashboard Management**: Single-writer rule for Dashboard.md
- **Security**: Full access to credentials and secure operations

### Work Zone Specialization
```
Cloud Agent → Draft-only (emails, social, Odoo entries)
Local Agent → Execution (sending, payments, approvals, WhatsApp)
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
                "title": "Process quarterly report",
                "content": "Please process the Q1 2026 quarterly report and execute required actions.",
                "priority": "high"
            }
        }


class ApprovalRequest(BaseModel):
    """Request approval for an action."""
    task_id: str
    action_type: str  # email, social, odoo, whatsapp, payment
    target_system: str  # email, twitter, facebook, odoo, whatsapp, etc.
    execution_details: str


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
    """Live HTML dashboard for Local Agent - auto-refreshes every 30s."""
    uptime = round(time.time() - START_TIME, 2)
    hours = int(uptime // 3600)
    minutes = int((uptime % 3600) // 60)

    queues = {k: _count_files(VAULT_PATH / v) for k, v in QUEUE_FOLDERS.items()}
    checks = {
        "Vault": VAULT_PATH.exists(),
        "Inbox": (VAULT_PATH / "Inbox").exists(),
        "In_Progress": (VAULT_PATH / "In_Progress").exists(),
        "Local_Agent_Config": Path(__file__).exists(),
        "Credentials_Access": (VAULT_PATH.parent / ".env").exists() if VAULT_PATH.parent / ".env" else True,
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
<title>AI Employee Vault - Local Agent</title>
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
  .agent-info {{ background:linear-gradient(45deg, #059669, #0d9488); padding:16px; border-radius:8px; 
                 margin-bottom:20px; text-align:center; }}
  .agent-name {{ font-size:1.2rem; font-weight:bold; color:white; }}
  .agent-role {{ color:#a7f3d0; font-size:0.9rem; }}
</style>
</head>
<body>
<div class="container">
  <div class="agent-info">
    <div class="agent-name">AI Employee - Local Agent</div>
    <div class="agent-role">Execution & Security (Platinum Phase)</div>
  </div>
  
  <h1>Local Agent Dashboard</h1>
  <p class="subtitle">Local AI Employee System - Execution Operations</p>

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
    <h2>Local Agent API</h2>
    <div class="endpoints">
      <a href="/api/status">/api/status <span class="badge badge-get">GET</span> - Full system status</a>
      <a href="/api/queues">/api/queues <span class="badge badge-get">GET</span> - All queues</a>
      <a href="/api/queue/inbox">/api/queue/inbox <span class="badge badge-get">GET</span> - Inbox items</a>
      <a href="/api/queue/done">/api/queue/done <span class="badge badge-get">GET</span> - Completed items</a>
      <a href="/api/metrics">/api/metrics <span class="badge badge-get">GET</span> - Metrics</a>
      <a href="/api/config">/api/config <span class="badge badge-get">GET</span> - Configuration</a>
      <a href="/api/logs">/api/logs <span class="badge badge-get">GET</span> - Recent logs</a>
      <a href="#">/api/approve-action <span class="badge badge-post">POST</span> - Approve an action</a>
      <a href="/api/execute-action <span class="badge badge-post">POST</span> - Execute an action</a>
    </div>
  </div>

  <div class="card">
    <h2>Health Probes</h2>
    <div class="endpoints">
      <a href="/health">/health <span class="badge badge-get">GET</span> - Liveness</a>
      <a href="/ready">/ready <span class="badge badge-get">GET</span> - Readiness</a>
    </div>
  </div>

  <p class="footer">v2.0.0-platinum &middot; Local Agent &middot; FastAPI + Swagger &middot; Auto-refreshes every 30s</p>
</div>
</body>
</html>"""
    return HTMLResponse(content=html)


# =========================================
# Health Probes
# =========================================
@app.get("/health", tags=["Health"])
async def health_check():
    """Liveness probe - is the Local Agent service alive?"""
    return {
        "status": "healthy",
        "agent": "local",
        "role": "execution",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "uptime_seconds": round(time.time() - START_TIME, 2),
        "version": os.getenv("APP_VERSION", "2.0.0-platinum"),
    }


@app.get("/ready", tags=["Health"])
async def readiness_check():
    """Readiness probe - is the Local Agent ready to handle requests?"""
    checks = {
        "vault_accessible": VAULT_PATH.exists(),
        "inbox_exists": (VAULT_PATH / "Inbox").exists(),
        "in_progress_exists": (VAULT_PATH / "In_Progress").exists(),
        "local_agent_config": Path(__file__).exists(),
        "credentials_available": (VAULT_PATH.parent / ".env").exists() if VAULT_PATH.parent / ".env" else True,
        "agent_id": LOCAL_AGENT_ID,
    }
    all_ready = all(checks.values())
    return {
        "status": "ready" if all_ready else "not_ready",
        "agent": "local",
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
        "local_agent_config": Path(__file__).exists(),
        "credentials_available": (VAULT_PATH.parent / ".env").exists() if VAULT_PATH.parent / ".env" else True,
    }
    queues = {k: _count_files(VAULT_PATH / v) for k, v in QUEUE_FOLDERS.items()}
    return {
        "status": "operational" if all(checks.values()) else "degraded",
        "agent": "local",
        "role": "execution",
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
        "agent": "local",
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
            "agent_access": "full" if key in ["inbox", "needs_action", "pending_approval", "approved", "done"] else "read"
        })
    return {"agent": "local", "queues": queues_info}


@app.get("/api/queue/{queue_name}", tags=["Queues"])
async def queue_detail(queue_name: str):
    """List all items in a specific queue with file previews.

    Local Agent has full access to all queues for execution operations.
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
                "agent_permission": "full_access"
            })

    return {
        "agent": "local",
        "queue": queue_name,
        "folder": QUEUE_FOLDERS[queue_name],
        "count": len(items),
        "items": items,
    }


@app.post("/api/approve-action", tags=["Execution"], status_code=200)
async def approve_action(request: ApprovalRequest):
    """Approve an action that was drafted by the Cloud Agent.
    
    Moves the task to the Approved queue for execution.
    """
    # Look for the draft file in Pending_Approval
    pending_path = VAULT_PATH / "Pending_Approval"
    draft_files = list(pending_path.glob(f"*{request.task_id}*.md"))
    
    if not draft_files:
        raise HTTPException(
            status_code=404,
            detail=f"No draft found with ID containing '{request.task_id}'"
        )
    
    draft_file = draft_files[0]  # Take the first match
    
    # Move to Approved queue
    approved_path = VAULT_PATH / "Approved"
    approved_file = approved_path / draft_file.name
    
    try:
        draft_file.rename(approved_file)
        
        # Update the file to mark it as approved
        content = approved_file.read_text(encoding="utf-8")
        approved_content = content.replace("status: pending_approval", "status: approved") + f"\n\n## Approved by Local Agent\nApproved at: {datetime.now(timezone.utc).isoformat()}\n"
        approved_file.write_text(approved_content, encoding="utf-8")
        
        return {
            "status": "approved",
            "agent": "local",
            "task_id": request.task_id,
            "action_type": request.action_type,
            "target_system": request.target_system,
            "message": f"Action '{request.task_id}' approved and moved to Approved queue"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error approving action: {str(e)}"
        )


@app.post("/api/execute-action", tags=["Execution"], status_code=200)
async def execute_action(task_id: str, action_type: str):
    """Execute an approved action via MCP servers.
    
    This is where the Local Agent performs sensitive operations like
    sending emails, posting to social media, processing payments, etc.
    """
    # Look for the approved file
    approved_path = VAULT_PATH / "Approved"
    approved_files = list(approved_path.glob(f"*{task_id}*.md"))
    
    if not approved_files:
        raise HTTPException(
            status_code=404,
            detail=f"No approved task found with ID containing '{task_id}'"
        )
    
    approved_file = approved_files[0]  # Take the first match
    
    # In a real implementation, this would call the appropriate MCP server
    # For now, we'll simulate the execution
    try:
        # Simulate execution via MCP
        execution_result = f"SIMULATED_EXECUTION: {action_type} action executed for task {task_id}"
        
        # Move to Done queue after execution
        done_path = VAULT_PATH / "Done"
        done_file = done_path / approved_file.name
        
        approved_file.rename(done_file)
        
        # Update the file to mark it as executed
        content = done_file.read_text(encoding="utf-8")
        executed_content = content + f"\n\n## Executed by Local Agent\nExecution result: {execution_result}\nExecuted at: {datetime.now(timezone.utc).isoformat()}\n"
        done_file.write_text(executed_content, encoding="utf-8")
        
        # Update Dashboard.md with execution info (single-writer rule)
        dashboard_path = VAULT_PATH / "Dashboard.md"
        if dashboard_path.exists():
            dashboard_content = dashboard_path.read_text(encoding="utf-8")
        else:
            dashboard_content = f"# AI Employee Dashboard\n\n**Last Updated**: {datetime.now().strftime('%Y-%m-%d')}\n**Status**: Initialized\n\n---\n\n"
        
        # Add execution log to dashboard
        execution_log = f"\n\n## Execution Log - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n- Executed {action_type} action: {task_id}\n- Result: {execution_result}\n"
        updated_dashboard = dashboard_content + execution_log
        dashboard_path.write_text(updated_dashboard, encoding="utf-8")
        
        return {
            "status": "executed",
            "agent": "local",
            "task_id": task_id,
            "action_type": action_type,
            "execution_result": execution_result,
            "message": f"Action '{task_id}' executed successfully and moved to Done"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error executing action: {str(e)}"
        )


@app.get("/api/config", tags=["System"])
async def runtime_config():
    """Current runtime configuration (includes credential status)."""
    return {
        "agent": "local",
        "role": "execution",
        "vault_path": str(VAULT_PATH),
        "agent_id": LOCAL_AGENT_ID,
        "dev_mode": os.getenv("DEV_MODE", "true"),
        "environment": os.getenv("ENVIRONMENT", "development"),
        "version": os.getenv("APP_VERSION", "2.0.0-platinum"),
        "port": os.getenv("PORT", os.getenv("HEALTH_PORT", "8080")),
        "permissions": {
            "can_create_drafts": True,
            "can_execute_actions": True,
            "can_modify_dashboard": True,
            "can_access_credentials": True
        },
        "credentials_available": (VAULT_PATH.parent / ".env").exists() if VAULT_PATH.parent / ".env" else True,
        "integrations": {
            "email_sending": True,  # Can send (unlike Cloud)
            "social_posting": True,  # Can post (unlike Cloud)
            "odoo_execution": True,  # Can execute (unlike Cloud)
            "whatsapp_access": True,  # Local only access
            "payment_processing": True,  # Local only processing
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
    return {"agent": "local", "log_files": entries, "count": len(entries)}


# =========================================
# Server runner
# =========================================
def run_local_agent_api(port: int = 8081):
    """Start Local Agent API with uvicorn."""
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8081"))
    run_local_agent_api(port)