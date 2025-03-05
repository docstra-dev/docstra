import os
import time
import threading
import logging
import queue
from typing import List, Optional, Callable
from pathlib import Path

from watchdog.observers import Observer
from watchdog.events import (
    PatternMatchingEventHandler,
)

logger = logging.getLogger(__name__)


class DocstraEventHandler(PatternMatchingEventHandler):
    """Custom event handler for file system changes with debounce support."""

    def __init__(
        self,
        patterns=None,
        ignore_patterns=None,
        ignore_directories=True,
        case_sensitive=False,
        callback=None,
        debounce_seconds=1.0,
        working_dir=None,
    ):
        """Initialize the event handler.

        Args:
            patterns: List of file patterns to watch
            ignore_patterns: List of patterns to ignore
            ignore_directories: Whether to ignore directory events
            case_sensitive: Whether patterns are case sensitive
            callback: Function to call with (added, modified, deleted) file lists
            debounce_seconds: Time to wait for batching similar events
            working_dir: Base directory for generating relative paths
        """
        super().__init__(
            patterns=patterns,
            ignore_patterns=ignore_patterns,
            ignore_directories=ignore_directories,
            case_sensitive=case_sensitive,
        )
        self.callback = callback
        self.debounce_seconds = debounce_seconds
        self.working_dir = working_dir

        # Event queues for collecting batched events
        self.event_queue = queue.Queue()
        self.added_files = set()
        self.modified_files = set()
        self.deleted_files = set()

        # Timer for debouncing
        self.last_event_time = 0
        self.debounce_timer = None
        self.lock = threading.RLock()

    def on_created(self, event):
        """Handle file creation events."""
        if not event.is_directory:
            self._queue_event("added", event.src_path)

    def on_modified(self, event):
        """Handle file modification events."""
        if not event.is_directory:
            self._queue_event("modified", event.src_path)

    def on_deleted(self, event):
        """Handle file deletion events."""
        if not event.is_directory:
            self._queue_event("deleted", event.src_path)

    def on_moved(self, event):
        """Handle file moved/renamed events."""
        if not event.is_directory:
            self._queue_event("deleted", event.src_path)
            self._queue_event("added", event.dest_path)

    def _queue_event(self, event_type, file_path):
        """Queue event with debouncing."""
        with self.lock:
            now = time.time()
            self.last_event_time = now

            # Add event to appropriate set
            if event_type == "added":
                self.added_files.add(file_path)
                self.deleted_files.discard(file_path)  # In case of quick delete/add
            elif event_type == "modified":
                # If a file was just added, don't mark it as modified
                if file_path not in self.added_files:
                    self.modified_files.add(file_path)
            elif event_type == "deleted":
                self.deleted_files.add(file_path)
                self.added_files.discard(file_path)
                self.modified_files.discard(file_path)

            # Set or reset debounce timer
            if self.debounce_timer:
                self.debounce_timer.cancel()

            self.debounce_timer = threading.Timer(
                self.debounce_seconds, self._process_events
            )
            self.debounce_timer.daemon = True
            self.debounce_timer.start()

    def _process_events(self):
        """Process all batched events after debounce period."""
        with self.lock:
            if not (self.added_files or self.modified_files or self.deleted_files):
                return

            # Convert to lists for callback
            added_files = list(self.added_files)
            modified_files = list(self.modified_files)
            deleted_files = list(self.deleted_files)

            # Clear sets for next batch
            self.added_files.clear()
            self.modified_files.clear()
            self.deleted_files.clear()

            # Call callback with batched events
            if self.callback:
                try:
                    self.callback(added_files, modified_files, deleted_files)
                except Exception as e:
                    logger.error(
                        f"Error in file change callback: {str(e)}", exc_info=True
                    )


class FileWatcher:
    """Watches a directory for file changes using Watchdog for native FS events."""

    def __init__(
        self,
        directory: str,
        file_extensions: List[str] = None,
        ignored_dirs: List[str] = None,
        debounce_seconds: float = 1.0,
        callback: Optional[Callable[[List[str], List[str], List[str]], None]] = None,
    ):
        """Initialize the file watcher.

        Args:
            directory: Root directory to watch
            file_extensions: List of file extensions to watch (e.g., ['.py', '.js'])
            ignored_dirs: List of directories to ignore (e.g., ['.git', 'node_modules'])
            debounce_seconds: Time in seconds to wait for batching similar events
            callback: Function to call when changes are detected with
                    (added, modified, deleted) file lists as arguments
        """
        self.directory = Path(directory).resolve()
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
        self.ignored_dirs = ignored_dirs or [
            ".git",
            "node_modules",
            "venv",
            ".venv",
            "__pycache__",
            "build",
            "dist",
        ]
        self.debounce_seconds = debounce_seconds
        self.callback = callback

        # Set up observer
        self.observer = None
        self.running = False

        # Patterns for event handler
        self.patterns = [f"*{ext}" for ext in self.file_extensions]
        self.ignore_patterns = [f"*/{d}/*" for d in self.ignored_dirs]

        # Set up event handler
        self.event_handler = DocstraEventHandler(
            patterns=self.patterns,
            ignore_patterns=self.ignore_patterns,
            ignore_directories=True,
            case_sensitive=False,
            callback=self._handle_batch_events,
            debounce_seconds=debounce_seconds,
            working_dir=self.directory,
        )

    def _handle_batch_events(self, added_files, modified_files, deleted_files):
        """Handle batched events and pass to the callback."""
        # Filter any remaining ignored directories that pattern matching missed
        filtered_added = self._filter_ignored_paths(added_files)
        filtered_modified = self._filter_ignored_paths(modified_files)
        filtered_deleted = self._filter_ignored_paths(deleted_files)

        # Call the callback with filtered files
        if self.callback and (filtered_added or filtered_modified or filtered_deleted):
            try:
                self.callback(filtered_added, filtered_modified, filtered_deleted)
            except Exception as e:
                logger.error(f"Error in file watcher callback: {str(e)}", exc_info=True)

    def _filter_ignored_paths(self, file_paths):
        """Filter out paths in ignored directories."""
        result = []
        for path in file_paths:
            # Convert to relative path for easier filtering
            rel_path = Path(path).relative_to(self.directory)
            # Check if path is in an ignored directory
            if not any(
                ignored_dir in rel_path.split(os.sep)
                for ignored_dir in self.ignored_dirs
            ):
                result.append(path)
        return result

    def start(self):
        """Start watching for file changes."""
        if self.running:
            return

        # Create observer
        self.observer = Observer()
        self.observer.schedule(self.event_handler, self.directory, recursive=True)
        self.observer.start()
        self.running = True

        logger.info(f"Started watchdog file watcher in {self.directory}")

    def stop(self):
        """Stop watching for file changes."""
        if self.observer and self.observer.is_alive():
            self.observer.stop()
            self.observer.join(timeout=5.0)
            self.running = False
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
            # Get file extensions from config if available
            extensions = getattr(
                self.config,
                "included_extensions",
                [
                    ".py",
                    ".js",
                    ".ts",
                    ".java",
                    ".kt",
                    ".cs",
                    ".go",
                    ".rs",
                    ".cpp",
                    ".c",
                    ".h",
                    ".hpp",
                ],
            )

            # Get excluded patterns from config if available
            excluded_dirs = getattr(
                self.config,
                "excluded_patterns",
                [
                    ".git",
                    "node_modules",
                    "venv",
                    ".venv",
                    "build",
                    "dist",
                    "__pycache__",
                    ".pytest_cache",
                ],
            )

            # Get debounce interval from config
            check_interval = getattr(self.config, "check_interval", 1.0)

            self.file_watcher = FileWatcher(
                directory=self.working_dir,
                file_extensions=extensions,
                ignored_dirs=excluded_dirs,
                debounce_seconds=check_interval,
                callback=self._handle_file_changes,
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
            # Use parallel processing for multiple files
            self._process_files_for_indexing(
                added_paths + modified_paths, parallel=True
            )

        # Remove deleted files
        if deleted_files:
            rel_paths = [Path(f).relative_to(self.working_dir) for f in deleted_files]
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
