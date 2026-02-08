"""
AI Employee Watchers Package
Part of Personal AI Employee Hackathon 0

This package contains watcher scripts that monitor external sources
and create task files in the vault for Claude to process.

Watchers:
- FileSystemWatcher: Monitors Drop_Folder for new files (Bronze)
- GmailWatcher: Monitors Gmail for important emails (Silver)
- Orchestrator: Coordinates all watchers and triggers (Silver+)
"""

from .base_watcher import BaseWatcher

__all__ = ['BaseWatcher']
__version__ = '1.0.0'
