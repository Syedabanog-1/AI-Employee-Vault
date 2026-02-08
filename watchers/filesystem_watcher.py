"""
File System Watcher Implementation
Monitors the Drop_Folder for new files and creates action files in Needs_Action folder.
"""

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pathlib import Path
import shutil
import logging
import time
from datetime import datetime


class DropFolderHandler(FileSystemEventHandler):
    def __init__(self, vault_path: str):
        self.needs_action = Path(vault_path) / 'Needs_Action'
        self.logger = logging.getLogger(self.__class__.__name__)
        
    def on_created(self, event):
        if event.is_directory:
            return
        source = Path(event.src_path)
        dest = self.needs_action / f'FILE_{source.name}'
        try:
            shutil.copy2(source, dest)
            self.create_metadata(source, dest)
            self.logger.info(f'Copied file to action queue: {dest}')
        except Exception as e:
            self.logger.error(f'Error processing file {source}: {e}')
        
    def create_metadata(self, source: Path, dest: Path):
        """Create metadata file with information about the dropped file"""
        meta_path = dest.with_suffix('.md')
        meta_content = f'''---
type: file_drop
original_name: {source.name}
size: {source.stat().st_size}
created: {datetime.now().isoformat()}
priority: medium
status: pending
---


## File Information
- Original Location: {source}
- Size: {source.stat().st_size} bytes
- Extension: {source.suffix}
- Created: {datetime.fromtimestamp(source.stat().st_ctime)}
- Modified: {datetime.fromtimestamp(source.stat().st_mtime)}


## Suggested Actions
- [ ] Review file content
- [ ] Determine appropriate processing
- [ ] Move to appropriate folder when processed
'''
        meta_path.write_text(meta_content)


class FileSystemWatcher:
    def __init__(self, vault_path: str, drop_folder_path: str = None):
        self.vault_path = Path(vault_path)
        self.drop_folder = Path(drop_folder_path) if drop_folder_path else self.vault_path / 'Drop_Folder'
        self.handler = DropFolderHandler(vault_path)
        self.observer = Observer()
        self.logger = logging.getLogger(self.__class__.__name__)
        
    def run(self):
        """Start watching the drop folder for new files"""
        self.observer.schedule(self.handler, str(self.drop_folder), recursive=False)
        self.observer.start()
        self.logger.info(f'Starting FileSystemWatcher on {self.drop_folder}')
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.observer.stop()
            self.logger.info('FileSystemWatcher stopped by user')
        
        self.observer.join()