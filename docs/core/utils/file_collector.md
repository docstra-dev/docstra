---
language: documenttype.markdown
source_file: /Users/jorgenosberg/development/docstra/docs/core/utils/file_collector.md
summary: 'File Collector

  ================'
title: file_collector

---

# File Collector
================

The `FileCollector` module is a utility class that collects files from a specified base path according to inclusion/exclusion rules.

## Overview
------------

The `FileCollector` class provides a flexible way to collect files based on various criteria, such as file extensions, directory inclusions, and exclusion patterns. It can be used to gather files for various purposes, such as data processing, backup, or archiving.

## Classes
---------

### FileCollector

#### Attributes

*   `base_path`: The base path from which to start the file collection.
*   `include_dirs`: A list of directories to include in the file collection.
*   `exclude_dirs`: A list of gitignore-style patterns for directories to exclude.
*   `exclude_files`: A list of gitignore-style patterns for files to exclude.
*   `file_extensions`: A list of file extensions to include.

#### Methods

*   `collect_files()`: Collects files from the base path according to the inclusion/exclusion rules.
*   `_walk_directory(dir_path)`: Recursively walks a directory and its subdirectories, filtering files based on the rules.
*   `_should_include_file(file_path, rel_file=None)`: Checks if a file should be included in the collection.
*   `_check_for_issues()`: Checks for potential issues with the file collection, such as excessive files or problematic patterns.

## Functions
------------

### collect_files(base_path, include_dirs, exclude_dirs, exclude_files, file_extensions, log_level)

Collects files from the specified base path according to the inclusion/exclusion rules.

#### Parameters

*   `base_path`: The base path from which to start the file collection.
*   `include_dirs`: A list of directories to include in the file collection.
*   `exclude_dirs`: A list of gitignore-style patterns for directories to exclude.
*   `exclude_files`: A list of gitignore-style patterns for files to exclude.
*   `file_extensions`: A list of file extensions to include.
*   `log_level`: The logging level.

#### Returns

A list of collected file paths as Path objects.

### _walk_directory(dir_path)

Recursively walks a directory and its subdirectories, filtering files based on the rules.

#### Parameters

*   `dir_path`: The path of the directory to walk.

#### Returns

A list of included file paths.

## Usage Examples
-----------------

```python
# Collect files from the current working directory
collected_files = collect_files()

# Collect files with specific extensions
collected_files = collect_files(
    base_path="/Users/jorgenosberg/development",
    include_dirs=["src", "tests"],
    exclude_dirs=["node_modules", "dist"],
    exclude_files=["*.tmp", "*.log"],
    file_extensions=[".py", ".txt"],
)

# Collect files with logging level set to DEBUG
collected_files = collect_files(
    base_path="/Users/jorgenosberg/development",
    include_dirs=["src", "tests"],
    exclude_dirs=["node_modules", "dist"],
    exclude_files=["*.tmp", "*.log"],
    file_extensions=[".py", ".txt"],
    log_level=logging.DEBUG,
)
```

## Important Dependencies
-------------------------

The `FileCollector` module depends on the following:

*   `pathlib`: A Python module for working with file paths and directories.
*   `logging`: A Python module for logging messages.

## Notes
------

*   The `FileCollector` class is designed to be flexible and customizable, allowing users to tailor the collection process to their specific needs.
*   The `_walk_directory` method uses a recursive approach to walk the directory tree, ensuring that all files are collected regardless of their depth.
*   The `_should_include_file` method checks if a file should be included based on the specified rules, taking into account file extensions and directory inclusions/exclusions.


## Source Code

```documenttype.markdown
---
language: documenttype.python
source_file: /Users/jorgenosberg/development/docstra/docstra/core/utils/file_collector.py
summary: 'File Collector

  ================'
title: file_collector

---

**File Collector**
================

Overview
--------

The `FileCollector` class is a utility module for collecting files based on specific inclusion and exclusion criteria. It provides a flexible way to filter files according to various conditions, such as file extensions, directory patterns, and more.

Implementation Details
--------------------

The `FileCollector` class uses a combination of regular expressions and string matching to determine which files should be included or excluded. The class is designed to be highly customizable, allowing users to specify their own inclusion and exclusion criteria through various parameters.

**Attributes**
------------

*   `base_path`: The base path for the file collection.
*   `include_dirs`: A list of directories to specifically include.
*   `exclude_dirs`: A list of gitignore-style patterns for directories to exclude.
*   `exclude_files`: A list of gitignore-style patterns for files to exclude.
*   `file_extensions`: A list of file extensions to include.
*   `log_level`: The logging level.

**Methods**
------------

### `collect_files()`

Collects files based on the specified inclusion and exclusion criteria.

#### Parameters

*   `base_path`: The base path for the file collection.
*   `include_dirs`: A list of directories to specifically include.
*   `exclude_dirs`: A list of gitignore-style patterns for directories to exclude.
*   `exclude_files`: A list of gitignore-style patterns for files to exclude.
*   `file_extensions`: A list of file extensions to include.
*   `log_level`: The logging level.

#### Return Value

A list of collected file paths as `Path` objects.

### `_check_for_issues()`

Checks for potential issues with the file collection, such as very few files being included or directories containing excessive files.

#### Parameters

None.

#### Return Value

None.

**Usage Examples**
-----------------

```python
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO)

# Create a FileCollector instance
collector = FileCollector(
    base_path="/Users/jorgenosberg/development/docstra",
    include_dirs=["src", "tests"],
    exclude_dirs=["node_modules", ".git"],
    file_extensions=[".py", ".txt"],
    log_level=logging.INFO,
)

# Collect files
files = collector.collect_files()

# Print collected files
for file in files:
    print(file)
```

**Important Dependencies**
-------------------------

The `FileCollector` class uses the following dependencies:

*   `pathlib`: For working with file paths.
*   `logging`: For logging purposes.

**Notes and Limitations**
------------------------

*   The `FileCollector` class assumes that the base path is a valid directory. If the base path does not exist, the class will raise an error.
*   The `collect_files()` method uses regular expressions to match file names and directories. This can lead to false positives or false negatives if the patterns are too broad or too narrow.
*   The `_check_for_issues()` method checks for potential issues with the file collection, but it is not foolproof and may miss some cases.

**Class Documentation**
----------------------

```python
class FileCollector:
    """
    A utility class for collecting files based on specific inclusion and exclusion criteria.

    Attributes:
        base_path (str): The base path for the file collection.
        include_dirs (list[str]): A list of directories to specifically include.
        exclude_dirs (list[str]): A list of gitignore-style patterns for directories to exclude.
        exclude_files (list[str]): A list of gitignore-style patterns for files to exclude.
        file_extensions (list[str]): A list of file extensions to include.
        log_level (int): The logging level.

    Methods:
        collect_files(): Collects files based on the specified inclusion and exclusion criteria.
        _check_for_issues(): Checks for potential issues with the file collection.
    """

    def __init__(
        self,
        base_path: str,
        include_dirs: list[str] = None,
        exclude_dirs: list[str] = None,
        exclude_files: list[str] = None,
        file_extensions: list[str] = None,
        log_level: int = logging.INFO,
    ):
        """
        Initializes a FileCollector instance.

        Args:
            base_path (str): The base path for the file collection.
            include_dirs (list[str], optional): A list of directories to specifically include. Defaults to None.
            exclude_dirs (list[str], optional): A list of gitignore-style patterns for directories to exclude. Defaults to None.
            exclude_files (list[str], optional): A list of gitignore-style patterns for files to exclude. Defaults to None.
            file_extensions (list[str], optional): A list of file extensions to include. Defaults to None.
            log_level (int, optional): The logging level. Defaults to logging.INFO.
        """
        self.base_path = Path(base_path)
        self.include_dirs = include_dirs or []
        self.exclude_dirs = exclude_dirs or []
        self.exclude_files = exclude_files or []
        self.file_extensions = file_extensions or []
        self.log_level = log_level

    def collect_files(self):
        """
        Collects files based on the specified inclusion and exclusion criteria.

        Returns:
            list[Path]: A list of collected file paths as Path objects.
        """
        # Implementation details omitted for brevity
        pass

    def _check_for_issues(self):
        """
        Checks for potential issues with the file collection, such as very few files being included or directories containing excessive files.

        Returns:
            None
        """
        # Implementation details omitted for brevity
        pass
```


## Source Code

```documenttype.python
import re
import logging
from pathlib import Path
from typing import List, Optional, Pattern, Union


class GitIgnorePattern:
    """A single gitignore pattern with matching functionality."""

    def __init__(self, pattern: str):
        """Initialize a gitignore pattern.

        Args:
            pattern: The gitignore pattern string
        """
        self.original_pattern = pattern
        self.pattern = self._parse_pattern(pattern)

        # Extract pattern properties
        self.is_negated = pattern.startswith("!")
        self.is_dir_only = pattern.endswith("/")
        self.is_absolute = (
            pattern.startswith("/") or "/" in pattern[:-1]
            if pattern.endswith("/")
            else "/" in pattern
        )

        # Convert to regex for faster matching
        self.regex = self._pattern_to_regex(self.pattern)

    def _parse_pattern(self, pattern: str) -> str:
        """Parse the raw gitignore pattern.

        Args:
            pattern: The raw pattern

        Returns:
            Processed pattern
        """
        # Handle negation
        if pattern.startswith("!"):
            pattern = pattern[1:]

        # Remove trailing spaces unless escaped
        if pattern.endswith(" ") and not pattern.endswith("\\ "):
            pattern = pattern.rstrip()

        # Handle escaped characters
        pattern = self._unescape_pattern(pattern)

        return pattern

    def _unescape_pattern(self, pattern: str) -> str:
        """Unescape special characters in the pattern.

        Args:
            pattern: Pattern string

        Returns:
            Unescaped pattern
        """
        # Replace \# with # and \! with ! etc.
        result = ""
        i = 0
        while i < len(pattern):
            if pattern[i] == "\\" and i + 1 < len(pattern):
                result += pattern[i + 1]
                i += 2
            else:
                result += pattern[i]
                i += 1
        return result

    def _pattern_to_regex(self, pattern: str) -> Pattern:
        """Convert a gitignore pattern to a regex pattern.

        Args:
            pattern: The gitignore pattern

        Returns:
            Compiled regex pattern
        """
        # Handle patterns without slashes - these should match at any level
        if "/" not in pattern:
            # For a pattern without slashes, it should match the pattern anywhere in the path
            # But must match full path components
            if pattern.endswith("/"):
                # Directory only, remove trailing slash
                pattern = pattern[:-1]
                regex = f"(^|/)({re.escape(pattern)})(/|$)"
            else:
                # File or directory
                regex = f"(^|/)({re.escape(pattern)})(/|$)"

            return re.compile(regex)

        # For patterns with slashes, standard processing follows:

        # Start at beginning of string or after a slash
        if pattern.startswith("/"):
            regex = "^"
            pattern = pattern[1:]
        else:
            regex = "(^|/)"

        # Remove trailing slash if present
        if pattern.endswith("/"):
            pattern = pattern[:-1]
            dir_only = True
        else:
            dir_only = False

        # Process the pattern
        i = 0
        while i < len(pattern):
            c = pattern[i]

            if c == "*":
                if i + 1 < len(pattern) and pattern[i + 1] == "*":
                    # Handle ** pattern (match anything including slashes)
                    if i + 2 < len(pattern) and pattern[i + 2] == "/":
                        # **/ matches zero or more directories
                        regex += "(.*/)??"
                        i += 3
                    else:
                        # ** by itself matches anything
                        regex += ".*"
                        i += 2
                else:
                    # Single * matches anything except slash
                    regex += "[^/]*"
                    i += 1
            elif c == "?":
                # ? matches any character except slash
                regex += "[^/]"
                i += 1
            elif c == "[":
                # Character class
                j = i
                while j < len(pattern) and pattern[j] != "]":
                    j += 1

                if j < len(pattern):
                    # Found closing bracket
                    char_class = pattern[i : j + 1]
                    regex += char_class
                    i = j + 1
                else:
                    # No closing bracket, treat as literal
                    regex += "\\["
                    i += 1
            elif c == "\\":
                # Escaped character
                if i + 1 < len(pattern):
                    regex += re.escape(pattern[i + 1])
                    i += 2
                else:
                    regex += "\\\\"
                    i += 1
            else:
                # Regular character
                regex += re.escape(c)
                i += 1

        # Match to end of string or before a slash
        if dir_only:
            regex += "/?$"
        else:
            regex += "(/|$)"

        return re.compile(regex)

    def matches(self, path: str, is_dir: bool = False) -> bool:
        """Check if the pattern matches a path.

        Args:
            path: Path to check
            is_dir: Whether the path is a directory

        Returns:
            True if the pattern matches, False otherwise
        """
        # Directory-only patterns only match directories
        if self.is_dir_only and not is_dir:
            return False

        # Check against regex
        return bool(self.regex.search(path))


class GitIgnoreMatcher:
    """Matcher for multiple gitignore patterns."""

    def __init__(self, patterns: List[str]):
        """Initialize with a list of patterns.

        Args:
            patterns: List of gitignore pattern strings
        """
        self.patterns = []

        # Parse each pattern
        for pattern in patterns:
            # Skip blank lines and comments
            pattern = pattern.strip()
            if not pattern or pattern.startswith("#"):
                continue

            self.patterns.append(GitIgnorePattern(pattern))

    def matches(self, path: str, is_dir: bool = False) -> bool:
        """Check if any pattern matches the path.

        Args:
            path: Path to check
            is_dir: Whether the path is a directory

        Returns:
            True if the path should be excluded, False otherwise
        """
        excluded = False

        # Check each pattern in order
        for pattern in self.patterns:
            if pattern.matches(path, is_dir):
                if pattern.is_negated:
                    # Negated pattern - include the file
                    excluded = False
                else:
                    # Regular pattern - exclude the file
                    excluded = True

        return excluded


class FileCollector:
    """Utility for collecting files with inclusion/exclusion rules using gitignore patterns."""

    def __init__(
        self,
        base_path: Union[str, Path],
        include_dirs: Optional[List[str]] = None,
        exclude_dirs: Optional[List[str]] = None,
        exclude_files: Optional[List[str]] = None,
        file_extensions: Optional[List[str]] = None,
        log_level: int = logging.INFO,
    ):
        """Initialize the file collector.

        Args:
            base_path: Base path for file collection
            include_dirs: List of directories to specifically include
            exclude_dirs: List of gitignore-style patterns for directories to exclude
            exclude_files: List of gitignore-style patterns for files to exclude
            file_extensions: List of file extensions to include
            log_level: Logging level
        """
        self.base_path = Path(base_path).resolve()
        self.include_dirs = include_dirs or []
        self.file_extensions = file_extensions or []

        # Set up logging
        self.logger = logging.getLogger("docstra.file_collector")
        self.logger.setLevel(log_level)

        # Add console handler if none exists
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            handler.setLevel(log_level)
            formatter = logging.Formatter("%(levelname)s - %(message)s")
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

        # Create matchers for directory and file exclusions
        self.dir_matcher = GitIgnoreMatcher(exclude_dirs or [])
        self.file_matcher = GitIgnoreMatcher(exclude_files or [])

        # Statistics
        self.stats = {
            "visited_dirs": 0,
            "visited_files": 0,
            "included_files": 0,
            "excluded_dirs": 0,
            "excluded_files": 0,
            "dir_counts": {},  # Directory -> count of included files
        }

    @staticmethod
    def default_code_file_extensions() -> List[str]:
        """Get the default list of code file extensions.

        Returns:
            List of common code file extensions
        """
        return [
            # Common languages
            ".py",  # Python
            ".js",  # JavaScript
            ".ts",  # TypeScript
            ".java",  # Java
            ".go",  # Go
            ".rs",  # Rust
            ".c",  # C
            ".cpp",  # C++
            ".cc",  # C++ alternative
            ".h",  # C/C++ header
            ".hpp",  # C++ header
            ".cs",  # C#
            ".rb",  # Ruby
            ".php",  # PHP
            ".swift",  # Swift
            ".kt",  # Kotlin
            # Additional languages
            ".r",  # R
            ".jl",  # Julia
            ".scala",  # Scala
            ".fs",  # F#
            ".fsx",  # F# script
            ".pl",  # Perl
            ".pm",  # Perl module
            ".sh",  # Shell script
            ".bash",  # Bash script
            ".zsh",  # Zsh script
            ".ps1",  # PowerShell
            ".groovy",  # Groovy
            ".lua",  # Lua
            ".m",  # Objective-C / MATLAB
            ".mm",  # Objective-C++
            ".clj",  # Clojure
            ".erl",  # Erlang
            ".ex",  # Elixir
            ".exs",  # Elixir script
            ".elm",  # Elm
            ".hs",  # Haskell
            ".dart",  # Dart
            ".d",  # D language
            ".vb",  # Visual Basic
            ".sql",  # SQL
            # Web development
            ".jsx",  # React JSX
            ".tsx",  # React TSX
            ".html",  # HTML
            ".htm",  # HTML alternative
            ".css",  # CSS
            ".scss",  # SCSS
            ".sass",  # Sass
            ".less",  # Less
            ".vue",  # Vue
            ".svelte",  # Svelte
            # Configuration and data formats
            ".json",  # JSON
            ".yaml",  # YAML
            ".yml",  # YAML alternative
            ".xml",  # XML
            ".toml",  # TOML
            ".ini",  # INI configuration
            ".proto",  # Protocol Buffers
            # Documentation
            ".md",  # Markdown
            ".rst",  # reStructuredText
        ]

    def collect_files(self) -> List[Path]:
        """Collect files according to inclusion/exclusion rules.

        Returns:
            List of collected file paths
        """
        self.logger.info(f"Starting file collection from {self.base_path}")
        self.logger.debug(f"Include dirs: {self.include_dirs}")
        self.logger.debug(f"File extensions: {self.file_extensions}")

        # Reset statistics
        self.stats = {
            "visited_dirs": 0,
            "visited_files": 0,
            "included_files": 0,
            "excluded_dirs": 0,
            "excluded_files": 0,
            "dir_counts": {},
        }

        collected_files = []

        # Handle single file case
        if self.base_path.is_file():
            self.stats["visited_files"] += 1
            if self._should_include_file(self.base_path):
                collected_files.append(self.base_path)
                self.stats["included_files"] += 1
            else:
                self.stats["excluded_files"] += 1

            self._log_statistics()
            return collected_files

        # Recursively walk the directory tree
        for file_path in self._walk_directory(self.base_path):
            collected_files.append(file_path)

        # Log statistics and potential issues
        self._log_statistics()

        return collected_files

    def _walk_directory(self, dir_path: Path) -> List[Path]:
        """Walk a directory recursively, filtering files according to rules.

        Args:
            dir_path: Directory path to walk

        Returns:
            List of included file paths
        """
        self.stats["visited_dirs"] += 1
        included_files = []

        try:
            # Get all directories and files in the current directory
            dirs = []
            files = []

            for path in dir_path.iterdir():
                if path.is_dir():
                    dirs.append(path)
                elif path.is_file():
                    files.append(path)

            # Process each file in the current directory
            for file_path in files:
                self.stats["visited_files"] += 1
                rel_file = str(file_path.relative_to(self.base_path))

                if self._should_include_file(file_path, rel_file):
                    included_files.append(file_path)
                    self.stats["included_files"] += 1

                    # Update directory count
                    rel_dir = str(file_path.parent.relative_to(self.base_path)) or "."
                    self.stats["dir_counts"][rel_dir] = (
                        self.stats["dir_counts"].get(rel_dir, 0) + 1
                    )
                else:
                    self.stats["excluded_files"] += 1

            # Recursively process subdirectories
            for subdir in dirs:
                rel_dir = str(subdir.relative_to(self.base_path))

                if not self._should_exclude_directory(rel_dir):
                    included_files.extend(self._walk_directory(subdir))
                else:
                    self.logger.debug(f"Excluding directory: {rel_dir}")
                    self.stats["excluded_dirs"] += 1

        except (PermissionError, OSError) as e:
            self.logger.warning(f"Error accessing {dir_path}: {e}")

        return included_files

    def _should_exclude_directory(self, rel_dir: str) -> bool:
        """Check if a directory should be excluded.

        Args:
            rel_dir: Relative directory path from base_path

        Returns:
            True if the directory should be excluded, False otherwise
        """
        # Always include specified directories
        if self.include_dirs:
            for include_dir in self.include_dirs:
                include_path = Path(include_dir)
                rel_path = Path(rel_dir)

                # Check if this directory is included or is a subdirectory of an included directory
                if rel_path == include_path or any(
                    parent == include_path for parent in rel_path.parents
                ):
                    return False

        # Check gitignore patterns
        if self.dir_matcher.matches(rel_dir, is_dir=True):
            return True

        # If include_dirs is specified, exclude directories not explicitly included
        if self.include_dirs:
            for include_dir in self.include_dirs:
                include_path = Path(include_dir)
                rel_path = Path(rel_dir)

                if rel_path == include_path or any(
                    parent == include_path for parent in rel_path.parents
                ):
                    return False
            return True  # Exclude if not in include_dirs

        return False

    def _should_include_file(
        self, file_path: Path, rel_file: Optional[str] = None
    ) -> bool:
        """Check if a file should be included.

        Args:
            file_path: Path to the file
            rel_file: Optional relative path from base_path

        Returns:
            True if the file should be included, False otherwise
        """
        # Get relative path if not provided
        if rel_file is None:
            rel_file = str(file_path.relative_to(self.base_path))

        # Check file extension
        if self.file_extensions:
            if file_path.suffix.lower() not in self.file_extensions:
                return False

        # Check gitignore patterns
        if self.file_matcher.matches(rel_file, is_dir=False):
            return False

        # If we've made it here, include the file
        return True

    def _log_statistics(self) -> None:
        """Log collection statistics and potential issues."""
        self.logger.info(
            f"Visited {self.stats['visited_dirs']} directories and {self.stats['visited_files']} files"
        )
        self.logger.info(
            f"Collected {self.stats['included_files']} files, excluded {self.stats['excluded_files']} files and {self.stats['excluded_dirs']} directories"
        )

        # Log top directories with most files
        if self.stats["dir_counts"]:
            self.logger.info("Top directories with most collected files:")
            for dir_path, count in sorted(
                self.stats["dir_counts"].items(), key=lambda x: x[1], reverse=True
            )[:10]:
                self.logger.info(f"  {dir_path}: {count} files")

        # Check for potential issues
        self._check_for_issues()

    def _check_for_issues(self) -> None:
        """Check for potential issues with the file collection."""
        if self.stats["included_files"] < 5 and self.stats["visited_files"] > 0:
            self.logger.warning(
                "Very few files were included. Check your exclusion patterns or file extensions."
            )

        if self.stats["included_files"] > 5000:
            self.logger.warning(
                f"Unusually large number of files collected ({self.stats['included_files']}). This might impact performance."
            )

        # Check for directories with excessive files
        for dir_path, count in self.stats["dir_counts"].items():
            if count > 500:
                self.logger.warning(
                    f"Directory '{dir_path}' contains {count} files. Consider excluding this directory if it's not needed."
                )

        # Check for potential patterns that should have been excluded
        problem_patterns = [
            "node_modules",
            "dist",
            "build",
            "__pycache__",
            ".git",
            "venv",
        ]
        for pattern in problem_patterns:
            # Check if any directories with this pattern have files
            matching_dirs = [d for d in self.stats["dir_counts"] if pattern in d]
            if matching_dirs:
                total_files = sum(self.stats["dir_counts"][d] for d in matching_dirs)
                self.logger.warning(
                    f"Found {total_files} files in {len(matching_dirs)} '{pattern}' directories. Consider adding exclusion pattern."
                )


def collect_files(
    base_path: Union[str, Path],
    include_dirs: Optional[List[str]] = None,
    exclude_dirs: Optional[List[str]] = None,
    exclude_files: Optional[List[str]] = None,
    file_extensions: Optional[List[str]] = None,
    log_level: int = logging.INFO,
) -> List[Path]:
    """Collect files according to inclusion/exclusion rules.

    Args:
        base_path: Base path for file collection
        include_dirs: List of directories to specifically include
        exclude_dirs: List of gitignore-style patterns for directories to exclude
        exclude_files: List of gitignore-style patterns for files to exclude
        file_extensions: List of file extensions to include
        log_level: Logging level

    Returns:
        List of collected file paths as Path objects
    """
    collector = FileCollector(
        base_path=base_path,
        include_dirs=include_dirs,
        exclude_dirs=exclude_dirs,
        exclude_files=exclude_files,
        file_extensions=file_extensions,
        log_level=log_level,
    )
    return collector.collect_files()

```

```
