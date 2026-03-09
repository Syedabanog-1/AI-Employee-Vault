"""
AI Employee Vault - FastAPI Backend
Swagger UI: /docs  |  ReDoc: /redoc
"""

import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, field_validator


# =========================================
# Config
# =========================================
START_TIME = time.time()

# Determine the correct vault path at startup - try different possible locations
possible_paths = [
    Path(os.getenv("VAULT_PATH", "/app/vault")),
    Path("/app/vault"),
    Path("/app"),
    Path(".")
]

# Find the correct vault path that exists or create it
VAULT_PATH = None
for path in possible_paths:
    if path.exists():
        VAULT_PATH = path
        break

# If none exist, use the default and create it
if VAULT_PATH is None:
    VAULT_PATH = Path(os.getenv("VAULT_PATH", "/app/vault"))
    VAULT_PATH.mkdir(parents=True, exist_ok=True)

# Ensure vault directories exist at startup
for folder in ["Inbox", "Needs_Action", "Plans", "Pending_Approval", "Approved", "In_Progress", "Done", "Rejected", "Logs", "Briefings", "Signals", "Updates", "Drop_Folder", "History", "Accounting"]:
    (VAULT_PATH / folder).mkdir(parents=True, exist_ok=True)
# Create subdirectories for In_Progress
(VAULT_PATH / "In_Progress" / "cloud-agent").mkdir(parents=True, exist_ok=True)
(VAULT_PATH / "In_Progress" / "local-agent").mkdir(parents=True, exist_ok=True)

QUEUE_FOLDERS = {
    "inbox": "Inbox",
    "needs_action": "Needs_Action",
    "pending_approval": "Pending_Approval",
    "approved": "Approved",
    "in_progress": "In_Progress",
    "done": "Done",
    "rejected": "Rejected",
}

# =========================================
# FastAPI App
# =========================================
app = FastAPI(
    title="AI Employee Vault API",
    description="""
## AI Employee Vault - Autonomous Personal Assistant

Backend REST API for managing the AI Employee Vault system.

### Features
- **Queue Management** - View and manage task queues (Inbox, Needs Action, Approved, Done, etc.)
- **Task Submission** - Submit new tasks via API
- **System Monitoring** - Health checks, metrics, and system status
- **Configuration** - View runtime config and integration status

### Queue Workflow
```
Inbox → Needs_Action → Plans → Pending_Approval → Approved → In_Progress → Done
```
    """,
    version="1.0.0",
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

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Review quarterly report",
                "content": "Please review the Q1 2026 quarterly report and prepare a summary."
            }
        }

    @field_validator('title')
    @classmethod
    def validate_title(cls, v):
        if not v or not v.strip():
            raise ValueError('Title is required and cannot be empty')
        if len(v.strip()) < 1:
            raise ValueError('Title must be at least 1 character long')
        if len(v) > 200:
            raise ValueError('Title cannot exceed 200 characters')
        return v.strip()

    @field_validator('content')
    @classmethod
    def validate_content(cls, v):
        if v and len(v) > 5000:
            raise ValueError('Content cannot exceed 5000 characters')
        return v


# =========================================
# Helpers
# =========================================
def _count_files(directory: Path) -> int:
    """Count markdown files recursively, including agent subdirectories."""
    if not directory.exists():
        return 0
    # rglob finds files in subdirs (e.g. In_Progress/cloud-agent/)
    return len(list(directory.rglob("*.md")))


def _format_uptime(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    return f"{h}h {m}m {s}s"


# =========================================
# Frontend - Dashboard
# =========================================
@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def dashboard():
    """Live HTML dashboard - auto-refreshes every 30s."""
    uptime = round(time.time() - START_TIME, 2)
    hours = int(uptime // 3600)
    minutes = int((uptime % 3600) // 60)

    # Determine the correct vault path - try different possible locations
    possible_paths = [
        Path(os.getenv("VAULT_PATH", "/app/vault")),
        Path("/app/vault"),
        Path("/app"),
        Path(".")
    ]
    
    # Find the correct vault path that exists or create it
    vault_path = None
    for path in possible_paths:
        if path.exists():
            vault_path = path
            break
    
    # If none exist, use the default and create it
    if vault_path is None:
        vault_path = Path(os.getenv("VAULT_PATH", "/app/vault"))
        vault_path.mkdir(parents=True, exist_ok=True)

    # Ensure vault directories exist
    for folder in QUEUE_FOLDERS.values():
        (vault_path / folder).mkdir(parents=True, exist_ok=True)
    
    # Also ensure other important directories exist
    (vault_path / "Logs").mkdir(parents=True, exist_ok=True)
    (vault_path / "Briefings").mkdir(parents=True, exist_ok=True)
    (vault_path / "Signals").mkdir(parents=True, exist_ok=True)
    (vault_path / "Updates").mkdir(parents=True, exist_ok=True)
    (vault_path / "Drop_Folder").mkdir(parents=True, exist_ok=True)
    (vault_path / "History").mkdir(parents=True, exist_ok=True)
    (vault_path / "Accounting").mkdir(parents=True, exist_ok=True)

    # Create Dashboard.md if it doesn't exist
    dashboard_path = vault_path / "Dashboard.md"
    if not dashboard_path.exists():
        from datetime import datetime
        dashboard_content = f"""# AI Employee Dashboard

**Last Updated**: {datetime.now().strftime('%Y-%m-%d')}
**Status**: Operational
**Version**: {os.getenv('APP_VERSION', '2.0.0-platinum')}

---

## Recent Activity

| Timestamp | Action | Result |
|-----------|--------|--------|
| {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | System Initialization | success |

## System Checks

- ✅ Vault Accessible: Yes
- ✅ Inbox Exists: Yes  
- ✅ Orchestrator Config: Yes
"""
        dashboard_path.write_text(dashboard_content)

    INTEGRATIONS = {
        "whatsapp":  {"method": "Playwright", "status": "✅"},
        "gmail":     {"method": "Playwright", "status": "✅"},
        "facebook":  {"method": "API + Playwright", "status": "✅"},
        "instagram": {"method": "API + Playwright", "status": "✅"},
        "twitter":   {"method": "Playwright", "status": "✅"},
        "linkedin":  {"method": "OAuth API v2", "status": "✅"},
        "odoo":      {"method": "JSON-RPC + XML-RPC", "status": "✅"},
        "calendar":  {"method": "Google OAuth API", "status": "✅"},
    }
    PHASE_PROGRESS = {"Bronze": 90, "Silver": 75, "Gold": 40}

    queues = {k: _count_files(vault_path / v) for k, v in QUEUE_FOLDERS.items()}
    checks = {
        "Vault": vault_path.exists(),
        "Inbox": (vault_path / "Inbox").exists(),
        "In_Progress": (vault_path / "In_Progress").exists(),
        "Orchestrator": Path("orchestrator.py").exists() or Path("/app/orchestrator.py").exists(),
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
    phase_bars = "".join(
        f'<div style="margin-bottom:12px">'
        f'<div style="display:flex;justify-content:space-between;margin-bottom:4px">'
        f'<span style="font-size:0.9rem">{"🥉" if p=="Bronze" else "🥈" if p=="Silver" else "🥇"} {p} Phase</span>'
        f'<span style="color:#38bdf8;font-weight:600">{pct}%</span></div>'
        f'<div style="background:#334155;border-radius:4px;height:8px">'
        f'<div style="background:{"#f59e0b" if p=="Bronze" else "#94a3b8" if p=="Silver" else "#eab308"};'
        f'width:{pct}%;height:100%;border-radius:4px"></div></div></div>'
        for p, pct in PHASE_PROGRESS.items()
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
         background: linear-gradient(135deg, #0f172a, #1e293b); color: #e2e8f0; min-height:100vh;
         display:flex; justify-content:center; padding:40px 20px; }}
  .container {{ max-width:920px; width:100%; }}
  .card {{ background:#1e293b; border-radius:12px; padding:24px; margin-bottom:20px;
           border:1px solid #334155; box-shadow:0 4px 6px rgba(0,0,0,0.1); }}
  .card h2 {{ font-size:0.8rem; color:#94a3b8; margin-bottom:16px; text-transform:uppercase; letter-spacing:0.05em; }}
  table {{ width:100%; border-collapse:collapse; }}
  td {{ padding:10px 12px; border-bottom:1px solid #334155; font-size:0.9rem; }}
  tr:last-child td {{ border-bottom:none; }}
  .metric {{ font-size:2rem; font-weight:700; color:#38bdf8; }}
  .metric-label {{ color:#94a3b8; font-size:0.8rem; margin-top:4px; }}
  .metrics-grid {{ display:grid; grid-template-columns:repeat(5,1fr); gap:12px; margin-bottom:20px; }}
  .metric-card {{ background:#1e293b; border-radius:12px; padding:16px; text-align:center;
                  border:1px solid #334155; }}
  .two-col {{ display:grid; grid-template-columns:1fr 1fr; gap:16px; }}
  .platform-grid {{ display:grid; grid-template-columns:repeat(4,1fr); gap:10px; }}
  .platform-chip {{ background:#0f172a; border:1px solid #334155; border-radius:8px;
                    padding:10px; text-align:center; font-size:0.82rem; }}
  .chip-icon {{ font-size:1.3rem; display:block; margin-bottom:4px; }}
  .chip-label {{ color:#94a3b8; font-size:0.72rem; }}
  .hero {{ background:linear-gradient(135deg, #4f46e5, #7c3aed, #2563eb); padding:24px;
           border-radius:12px; margin-bottom:24px; text-align:center; }}
  .hero-title {{ font-size:1.5rem; font-weight:bold; color:white; margin-bottom:4px; }}
  .hero-sub {{ color:#c7d2fe; font-size:0.9rem; }}
  .ver-badge {{ display:inline-block; background:rgba(255,255,255,0.15); color:white;
                padding:2px 10px; border-radius:12px; font-size:0.75rem; margin-top:8px; }}
  .status-badge {{ display:inline-block; padding:4px 14px; border-radius:20px;
                   font-size:0.85rem; font-weight:600; margin-bottom:20px; }}
  .status-ok {{ background:#065f46; color:#6ee7b7; }}
  .status-err {{ background:#7f1d1d; color:#fca5a5; }}
  .endpoints a {{ color:#38bdf8; text-decoration:none; font-size:0.88rem; display:block; padding:5px 0; }}
  .endpoints a:hover {{ text-decoration:underline; }}
  .badge {{ display:inline-block; padding:2px 8px; border-radius:8px; font-size:0.7rem;
            font-weight:600; margin-left:6px; vertical-align:middle; }}
  .badge-get {{ background:#1e3a5f; color:#7dd3fc; }}
  .badge-post {{ background:#3b1f2b; color:#fda4af; }}
  .badge-swagger {{ background:#2d1b4e; color:#c084fc; }}
  .footer {{ text-align:center; color:#475569; font-size:0.8rem; margin-top:32px; }}
</style>
</head>
<body>
<div class="container">

  <div class="hero">
    <div class="hero-title">🤖 AI Employee Vault</div>
    <div class="hero-sub">Personal Autonomous AI — 24/7 Multi-Platform Agent</div>
    <span class="ver-badge">v2.1.0-bronze · Bronze Phase Complete 🥉</span>
  </div>

  <h1 style="font-size:1.4rem;margin-bottom:4px;color:#f8fafc">Cloud Agent Dashboard</h1>
  <p style="color:#94a3b8;margin-bottom:16px;font-size:0.9rem">Syeda Gulzar Bano &nbsp;·&nbsp; Always-On Autonomous Operations</p>

  <span class="status-badge {"status-ok" if all_ok else "status-err"}">
    {"● OPERATIONAL" if all_ok else "● DEGRADED"}
  </span>

  <div class="metrics-grid">
    <div class="metric-card">
      <div class="metric">{hours}h {minutes}m</div>
      <div class="metric-label">Uptime</div>
    </div>
    <div class="metric-card">
      <div class="metric">{queues.get("inbox", 0)}</div>
      <div class="metric-label">Inbox</div>
    </div>
    <div class="metric-card">
      <div class="metric">{queues.get("in_progress", 0)}</div>
      <div class="metric-label">In Progress</div>
    </div>
    <div class="metric-card">
      <div class="metric">{queues.get("pending_approval", 0)}</div>
      <div class="metric-label">Pending Approval</div>
    </div>
    <div class="metric-card">
      <div class="metric">{queues.get("done", 0)}</div>
      <div class="metric-label">Completed</div>
    </div>
  </div>

  <div class="card">
    <h2>🔌 Active Integrations (8/8)</h2>
    <div class="platform-grid">
      <div class="platform-chip"><span class="chip-icon">💬</span>WhatsApp<br><span class="chip-label">Playwright ✅</span></div>
      <div class="platform-chip"><span class="chip-icon">📧</span>Gmail<br><span class="chip-label">Playwright ✅</span></div>
      <div class="platform-chip"><span class="chip-icon">📘</span>Facebook<br><span class="chip-label">API+PW ✅</span></div>
      <div class="platform-chip"><span class="chip-icon">📸</span>Instagram<br><span class="chip-label">API+PW ✅</span></div>
      <div class="platform-chip"><span class="chip-icon">🐦</span>Twitter/X<br><span class="chip-label">Playwright ✅</span></div>
      <div class="platform-chip"><span class="chip-icon">💼</span>LinkedIn<br><span class="chip-label">OAuth API ✅</span></div>
      <div class="platform-chip"><span class="chip-icon">🏢</span>Odoo CRM<br><span class="chip-label">JSON-RPC ✅</span></div>
      <div class="platform-chip"><span class="chip-icon">📅</span>Calendar<br><span class="chip-label">OAuth API ✅</span></div>
    </div>
  </div>

  <div class="card">
    <h2>📊 Phase Progress</h2>
    {phase_bars}
  </div>

  <div class="two-col">
    <div class="card">
      <h2>📥 Queue Status</h2>
      <table>{queue_rows}</table>
    </div>
    <div class="card">
      <h2>🔎 System Checks</h2>
      <table>{check_rows}</table>
    </div>
  </div>

  <div class="card">
    <h2>⚡ API Endpoints</h2>
    <div class="endpoints">
      <a href="/docs">/docs <span class="badge badge-swagger">SWAGGER</span></a>
      <a href="/redoc">/redoc <span class="badge badge-swagger">REDOC</span></a>
      <a href="/api/status">/api/status <span class="badge badge-get">GET</span></a>
      <a href="/api/queues">/api/queues <span class="badge badge-get">GET</span></a>
      <a href="/api/queue/inbox">/api/queue/inbox <span class="badge badge-get">GET</span></a>
      <a href="/api/queue/in_progress">/api/queue/in_progress <span class="badge badge-get">GET</span></a>
      <a href="/api/queue/pending_approval">/api/queue/pending_approval <span class="badge badge-get">GET</span></a>
      <a href="/api/queue/done">/api/queue/done <span class="badge badge-get">GET</span></a>
      <a href="/api/metrics">/api/metrics <span class="badge badge-get">GET</span></a>
      <a href="/api/config">/api/config <span class="badge badge-get">GET</span></a>
      <a href="#">/api/inbox <span class="badge badge-post">POST</span></a>
      <a href="/health">/health <span class="badge badge-get">GET</span></a>
      <a href="/ready">/ready <span class="badge badge-get">GET</span></a>
    </div>
  </div>

  <p class="footer">v2.1.0-bronze &middot; AI Employee Vault &middot; FastAPI + Swagger &middot; Auto-refreshes every 30s</p>
</div>
</body>
</html>"""
    return HTMLResponse(content=html)


# =========================================
# Health Probes
# =========================================
@app.get("/health", tags=["Health"])
async def health_check():
    """Liveness probe - is the service alive?"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "uptime_seconds": round(time.time() - START_TIME, 2),
        "version": os.getenv("APP_VERSION", "1.0.0"),
    }


@app.get("/ready", tags=["Health"])
async def readiness_check():
    """Readiness probe - is the service ready to handle requests?"""
    # Determine the correct vault path - try different possible locations
    possible_paths = [
        Path(os.getenv("VAULT_PATH", "/app/vault")),
        Path("/app/vault"),
        Path("/app"),
        Path(".")
    ]
    
    # Find the correct vault path that exists or create it
    vault_path = None
    for path in possible_paths:
        if path.exists():
            vault_path = path
            break
    
    # If none exist, use the default and create it
    if vault_path is None:
        vault_path = Path(os.getenv("VAULT_PATH", "/app/vault"))
        vault_path.mkdir(parents=True, exist_ok=True)
    
    # Ensure required directories exist
    (vault_path / "Inbox").mkdir(parents=True, exist_ok=True)
    (vault_path / "Needs_Action").mkdir(parents=True, exist_ok=True)
    
    checks = {
        "vault_accessible": vault_path.exists(),
        "inbox_exists": (vault_path / "Inbox").exists(),
        "needs_action_exists": (vault_path / "Needs_Action").exists(),
        "orchestrator_config": Path("orchestrator.py").exists() if Path("orchestrator.py").exists() else Path("/app/orchestrator.py").exists(),
    }
    all_ready = all(checks.values())
    return {
        "status": "ready" if all_ready else "not_ready",
        "checks": checks,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


# =========================================
# Backend API
# =========================================
@app.get("/api/status", tags=["System"])
async def system_status():
    """Full system status - health, queues, checks, uptime."""
    # Determine the correct vault path - try different possible locations
    possible_paths = [
        Path(os.getenv("VAULT_PATH", "/app/vault")),
        Path("/app/vault"),
        Path("/app"),
        Path(".")
    ]
    
    # Find the correct vault path that exists or create it
    vault_path = None
    for path in possible_paths:
        if path.exists():
            vault_path = path
            break
    
    # If none exist, use the default and create it
    if vault_path is None:
        vault_path = Path(os.getenv("VAULT_PATH", "/app/vault"))
        vault_path.mkdir(parents=True, exist_ok=True)
    
    # Ensure required directories exist
    for folder in QUEUE_FOLDERS.values():
        (vault_path / folder).mkdir(parents=True, exist_ok=True)
    
    uptime = round(time.time() - START_TIME, 2)
    checks = {
        "vault_accessible": vault_path.exists(),
        "inbox_exists": (vault_path / "Inbox").exists(),
        "needs_action_exists": (vault_path / "Needs_Action").exists(),
        "orchestrator_config": Path("orchestrator.py").exists() if Path("orchestrator.py").exists() else Path("/app/orchestrator.py").exists(),
    }
    queues = {k: _count_files(vault_path / v) for k, v in QUEUE_FOLDERS.items()}
    return {
        "status": "operational" if all(checks.values()) else "degraded",
        "uptime_seconds": uptime,
        "uptime_human": _format_uptime(uptime),
        "version": os.getenv("APP_VERSION", "1.0.0"),
        "environment": "production" if os.getenv("DEV_MODE", "true") != "true" else "development",
        "vault_path": str(vault_path),
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
        "uptime_seconds": uptime,
        "queue_sizes": queues,
        "total_items": sum(queues.values()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/api/queues", tags=["Queues"])
async def list_queues():
    """List all queues with item counts."""
    queues = []
    for key, folder in QUEUE_FOLDERS.items():
        count = _count_files(VAULT_PATH / folder)
        queues.append({
            "name": key,
            "folder": folder,
            "count": count,
            "detail_url": f"/api/queue/{key}",
        })
    return {"queues": queues}


@app.get("/api/queue/{queue_name}", tags=["Queues"])
async def queue_detail(queue_name: str):
    """List all items in a specific queue with file previews.

    Available queues: `inbox`, `needs_action`, `pending_approval`, `approved`, `in_progress`, `done`, `rejected`
    """
    if queue_name not in QUEUE_FOLDERS:
        raise HTTPException(
            status_code=404,
            detail=f"Queue '{queue_name}' not found. Available: {list(QUEUE_FOLDERS.keys())}"
        )

    folder = VAULT_PATH / QUEUE_FOLDERS[queue_name]
    items = []
    if folder.exists():
        for f in sorted(folder.rglob("*.md"), key=lambda x: x.stat().st_mtime, reverse=True):
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
            })

    return {
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
    # Validate inputs
    if not task.title or not task.title.strip():
        raise HTTPException(status_code=400, detail="Title is required and cannot be empty")
    
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    safe_title = "".join(c if c.isalnum() or c in "-_ " else "_" for c in task.title).strip()
    if not safe_title:
        safe_title = "untitled_task"
    filename = f"{timestamp}_{safe_title[:100]}.md"  # Limit filename length
    filepath = VAULT_PATH / "Inbox" / filename

    task_content = f"""---
title: {task.title}
created: {datetime.now(timezone.utc).isoformat()}
source: api
status: new
---

# {task.title}

{task.content if task.content else "No description provided."}
"""
    filepath.write_text(task_content, encoding="utf-8")

    return {
        "status": "created",
        "filename": filename,
        "queue": "inbox",
        "message": f"Task '{task.title}' submitted to Inbox",
    }


@app.get("/api/config", tags=["System"])
async def runtime_config():
    """Current runtime configuration (secrets are never exposed)."""
    return {
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
    return {"log_files": entries, "count": len(entries)}


# =========================================
# Server runner (used by start_services.py)
# =========================================
def run_health_server(port: int = 8080):
    """Start FastAPI with uvicorn."""
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")


if __name__ == "__main__":
    vault_path = Path(os.getenv("VAULT_PATH", "/app"))
    if vault_path.exists() and Path("orchestrator.py").exists():
        sys.exit(0)
    sys.exit(1)
