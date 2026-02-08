# Research: Bronze Phase - AI Employee Foundation

**Date**: 2026-02-07
**Feature**: Bronze Phase
**Status**: Complete

## Research Tasks Completed

### 1. FileSystem Monitoring Library

**Decision**: Use `watchdog` library for filesystem monitoring

**Rationale**:
- Industry standard for Python filesystem monitoring
- Cross-platform support (Windows, macOS, Linux)
- Event-driven architecture (efficient, not polling)
- Well-maintained with active community
- Simple API with Observer pattern

**Alternatives Considered**:
| Library | Pros | Cons | Decision |
|---------|------|------|----------|
| watchdog | Cross-platform, mature, event-driven | Requires dependency | ✅ Selected |
| os.scandir polling | No dependencies | Inefficient, polling-based | ❌ Rejected |
| pyinotify | Linux-native, efficient | Linux-only | ❌ Rejected |
| Windows API direct | Native Windows | Windows-only, complex | ❌ Rejected |

**Implementation Notes**:
```python
# Core pattern
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class Handler(FileSystemEventHandler):
    def on_created(self, event):
        # Handle new file
        pass

observer = Observer()
observer.schedule(handler, path, recursive=False)
observer.start()
```

### 2. YAML Frontmatter Format

**Decision**: Use standard YAML frontmatter with `---` delimiters

**Rationale**:
- Obsidian-native format
- Human-readable
- Easy to parse with Python's `yaml` library
- Compatible with other markdown tools

**Standard Fields for Task Files**:
```yaml
---
type: file_drop | email | message | task
status: pending | processing | done | error
timestamp: ISO-8601 datetime
source: watcher name or manual
priority: low | normal | high | urgent
---
```

### 3. Logging Format

**Decision**: JSON Lines format in daily log files

**Rationale**:
- Machine-parseable
- Human-readable
- Easy to query and aggregate
- Standard format for audit trails

**Log Entry Schema**:
```json
{
  "timestamp": "2026-02-07T10:30:00.000Z",
  "action_type": "task_created",
  "actor": "filesystem_watcher",
  "target": "/Needs_Action/FILE_invoice.pdf.md",
  "result": "success",
  "details": {}
}
```

### 4. Claude Code Skill Format

**Decision**: Markdown files with structured sections

**Rationale**:
- Claude Code native format
- Human-readable documentation
- Can include code examples
- Versioned with git

**Skill File Structure**:
```markdown
# Skill: [name]

## Description
[What this skill does]

## Phase
[Which hackathon phase]

## Trigger
[When to invoke]

## Instructions
[Step-by-step for Claude]

## Success Criteria
[How to verify success]
```

### 5. Error Handling Strategy

**Decision**: Log-and-continue with graceful degradation

**Rationale**:
- Watcher should never crash on single file error
- Errors logged for debugging
- Dashboard shows error state
- Human can intervene when needed

**Error Categories**:
| Error Type | Response |
|------------|----------|
| File read error | Log, skip file, continue |
| File write error | Retry once, then log and alert |
| Watcher crash | Watchdog restarts (Silver+) |
| Invalid frontmatter | Log warning, process anyway |

### 6. Windows Path Handling

**Decision**: Use `pathlib.Path` for all file operations

**Rationale**:
- Cross-platform path handling
- Proper Windows backslash support
- Object-oriented API
- Built into Python standard library

**Best Practices**:
```python
from pathlib import Path

# Always use Path objects
vault = Path(r"D:\syeda Gulzar Bano\AI_Employee_Vault_")
needs_action = vault / "Needs_Action"

# Use forward slashes in code, Path handles conversion
task_file = needs_action / f"FILE_{filename}.md"
```

## Dependencies Finalized

### Required (Bronze)
```
watchdog>=3.0.0      # Filesystem monitoring
pyyaml>=6.0          # YAML parsing (for frontmatter)
python-dotenv>=1.0.0 # Environment variables
```

### Development
```
pytest>=7.0.0        # Testing
black>=23.0.0        # Code formatting
```

## Open Questions Resolved

| Question | Resolution |
|----------|------------|
| How to handle file locks? | Use retry with exponential backoff |
| How to handle large files? | Create task file immediately, process metadata only |
| How to handle duplicate drops? | Check if task file exists, skip if so |
| How to handle special characters in filenames? | Sanitize for markdown compatibility |

## Next Steps

1. Implement `filesystem_watcher.py` using watchdog
2. Create task file template with YAML frontmatter
3. Implement logging to `/Logs/YYYY-MM-DD.json`
4. Create Agent Skills for Claude Code
5. Test end-to-end workflow
