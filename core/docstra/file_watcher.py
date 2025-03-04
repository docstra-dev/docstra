import os
import time
import threading
import logging
from typing import List, Set, Dict, Optional, Callable
from pathlib import Path

logger = logging.getLogger(__name__)


class FileWatcher:
    """Watches a directory for file changes and triggers reindexing."""

    def __init__(
        self,
        directory: str,
        file_extensions: List[str] = None,
        ignored_dirs: List[str] = None,
        check_interval: float = 5.0,
        callback: Optional[Callable[[List[str], List[str], List[str]], None]] = None,
    ):
        """Initialize the file watcher.

        Args:
            directory: Root directory to watch
            file_extensions: List of file extensions to watch (e.g., ['.py', '.js'])
            ignored_dirs: List of directories to ignore (e.g., ['.git', 'node_modules'])
            check_interval: Interval in seconds between checks
            callback: Function to call when changes are detected with
                     (added, modified, deleted) file lists as arguments
        """
        self.directory = os.path.abspath(directory)
        self.file_extensions = file_extensions or [
            ".py",
            ".js",
            ".ts",
            ".java",
            ".cpp",
            ".c",
            ".go",
            ".rs",
        ]
        self.ignored_dirs = set(
            ignored_dirs
            or [".git", "node_modules", "venv", ".venv", "__pycache__", "build", "dist"]
        )
        self.check_interval = check_interval
        self.callback = callback

        # File tracking
        self.file_mtimes: Dict[str, float] = {}
        self.running = False
        self.watch_thread = None

        # Initial scan
        self._scan_files()

    def _scan_files(self) -> Dict[str, float]:
        """Scan the directory for files and record their modification times.

        Returns:
            Dictionary of file paths to modification times
        """
        current_files = {}

        for root, dirs, files in os.walk(self.directory):
            # Skip ignored directories
            dirs[:] = [
                d for d in dirs if d not in self.ignored_dirs and not d.startswith(".")
            ]

            for file in files:
                # Check file extension
                if any(file.endswith(ext) for ext in self.file_extensions):
                    file_path = os.path.join(root, file)
                    try:
                        mtime = os.path.getmtime(file_path)
                        current_files[file_path] = mtime
                    except OSError:
                        # Skip files that can't be accessed
                        pass

        return current_files

    def _check_for_changes(self):
        """Check for changes in the watched files."""
        current_files = self._scan_files()

        # Find new and modified files
        added_files = []
        modified_files = []

        for file_path, mtime in current_files.items():
            if file_path not in self.file_mtimes:
                added_files.append(file_path)
            elif mtime > self.file_mtimes[file_path]:
                modified_files.append(file_path)

        # Find deleted files
        deleted_files = [f for f in self.file_mtimes if f not in current_files]

        # Update file mtimes
        self.file_mtimes = current_files

        # If changes detected and callback provided, call it
        if (added_files or modified_files or deleted_files) and self.callback:
            try:
                self.callback(added_files, modified_files, deleted_files)
            except Exception as e:
                logger.error(f"Error in file change callback: {str(e)}", exc_info=True)

        return added_files, modified_files, deleted_files

    def _watch_loop(self):
        """Main watch loop that periodically checks for changes."""
        while self.running:
            try:
                self._check_for_changes()
            except Exception as e:
                logger.error(
                    f"Error checking for file changes: {str(e)}", exc_info=True
                )

            # Sleep until next check
            time.sleep(self.check_interval)

    def start(self):
        """Start watching for file changes."""
        if self.running:
            return

        self.running = True
        self.watch_thread = threading.Thread(target=self._watch_loop, daemon=True)
        self.watch_thread.start()

        logger.info(f"Started file watcher in {self.directory}")

    def stop(self):
        """Stop watching for file changes."""
        self.running = False

        if self.watch_thread and self.watch_thread.is_alive():
            self.watch_thread.join(timeout=1.0)

        logger.info("Stopped file watcher")

    def __enter__(self):
        """Start watcher when used as a context manager."""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Stop watcher when exiting context manager."""
        self.stop()


# Integration with DocstraService
def integrate_file_watcher(service_class):
    """Integrate file watcher with DocstraService."""

    # Store original init method
    original_init = service_class.__init__

    # Define new init method
    def new_init(self, *args, **kwargs):
        # Call original init
        original_init(self, *args, **kwargs)

        # Extract auto_index parameter or default to True
        auto_index = kwargs.pop("auto_index", True)

        # Create file watcher if auto_index is enabled
        if auto_index:
            self.file_watcher = FileWatcher(
                directory=self.working_dir, callback=self._handle_file_changes
            )
            self.file_watcher.start()

    # Define file change handler method
    def handle_file_changes(self, added_files, modified_files, deleted_files):
        """Handle file changes detected by the watcher."""
        if not (added_files or modified_files or deleted_files):
            return

        self.logger.info(
            f"Changes detected: {len(added_files)} added, "
            f"{len(modified_files)} modified, "
            f"{len(deleted_files)} deleted"
        )

        # Process just the changed files instead of full reindex
        added_paths = [Path(f) for f in added_files]
        modified_paths = [Path(f) for f in modified_files]

        # Process new and modified files
        if added_paths or modified_paths:
            self._process_files_for_indexing(added_paths + modified_paths)

        # Remove deleted files
        if deleted_files:
            rel_paths = [os.path.relpath(f, self.working_dir) for f in deleted_files]
            self._remove_files_from_index(rel_paths)

    # Define cleanup method override
    original_cleanup = getattr(service_class, "cleanup", lambda self: None)

    def new_cleanup(self):
        """Extended cleanup method that stops the file watcher."""
        # Stop file watcher if it exists
        if hasattr(self, "file_watcher"):
            self.file_watcher.stop()

        # Call original cleanup
        original_cleanup(self)

    # Attach new methods to the class
    service_class.__init__ = new_init
    service_class._handle_file_changes = handle_file_changes
    service_class.cleanup = new_cleanup

    return service_class
