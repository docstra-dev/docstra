"""Path utilities for the Docstra CLI."""

import os
from pathlib import Path
from typing import List, Optional


def get_docstra_dir(working_dir: str) -> Path:
    """Get the Docstra config directory.
    
    Args:
        working_dir: Base working directory
        
    Returns:
        Path to the .docstra directory
    """
    return Path(working_dir) / ".docstra"


def ensure_docstra_dir(working_dir: str) -> Path:
    """Ensure the Docstra directory exists.
    
    Args:
        working_dir: Base working directory
        
    Returns:
        Path to the created .docstra directory
    """
    docstra_dir = get_docstra_dir(working_dir)
    docstra_dir.mkdir(exist_ok=True, parents=True)
    return docstra_dir


def get_config_path(working_dir: str) -> Path:
    """Get the path to the config file.
    
    This checks for configuration in two locations:
    1. .docstra/config.json (preferred)
    2. docstra.json in the root directory (legacy support)
    
    Args:
        working_dir: Base working directory
        
    Returns:
        Path to the config file (either .docstra folder or root)
    """
    # First check for .docstra/config.json
    dotconfig_path = get_docstra_dir(working_dir) / "config.json"
    if dotconfig_path.exists():
        return dotconfig_path
        
    # Fall back to root config (legacy support)
    return Path(working_dir) / "docstra.json"


def resolve_relative_path(base_dir: str, file_path: str) -> str:
    """Resolve a file path that might be relative or absolute.
    
    Args:
        base_dir: Base directory for relative paths
        file_path: Path to resolve
        
    Returns:
        Resolved file path
    """
    if os.path.isabs(file_path):
        return file_path
    return os.path.normpath(os.path.join(base_dir, file_path))


def is_docstra_initialized(working_dir: str) -> bool:
    """Check if Docstra is initialized in the directory.
    
    Docstra is considered initialized if either:
    1. A .docstra/config.json file exists (preferred approach)
    2. A docstra.json file exists in the working directory (legacy support)
    
    Args:
        working_dir: Directory to check
        
    Returns:
        True if initialized, False otherwise
    """
    # Check for .docstra/config.json
    dotconfig_path = get_docstra_dir(working_dir) / "config.json"
    if dotconfig_path.exists():
        return True
        
    # Check for legacy root config
    root_config = Path(working_dir) / "docstra.json"
    return root_config.exists()


def suggest_file_paths(partial_path: str, working_dir: str) -> List[str]:
    """Suggest file paths based on partial input.
    
    Args:
        partial_path: Partial path to match
        working_dir: Base directory for search
        
    Returns:
        List of matching file paths
    """
    base_dir = Path(working_dir)
    
    # Handle absolute paths
    if os.path.isabs(partial_path):
        dir_part = os.path.dirname(partial_path)
        file_part = os.path.basename(partial_path)
        
        try:
            if os.path.isdir(dir_part):
                return [os.path.join(dir_part, f) 
                        for f in os.listdir(dir_part) 
                        if f.startswith(file_part)]
        except:
            return []
    
    # Handle relative paths
    dir_part = os.path.dirname(partial_path)
    file_part = os.path.basename(partial_path)
    
    search_dir = base_dir / dir_part if dir_part else base_dir
    
    try:
        if search_dir.exists() and search_dir.is_dir():
            return [os.path.join(dir_part, f) if dir_part else f
                    for f in os.listdir(search_dir)
                    if f.startswith(file_part)]
    except:
        return []
        
    return []