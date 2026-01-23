"""Shared utilities for Reforge scripts - path resolution and config parsing.

This module provides the same functionality as .reforge/scripts/bash/common.sh
but implemented in pure Python for cross-platform compatibility.
"""

from __future__ import annotations

import json
from pathlib import Path


class ReforgeError(Exception):
    """Base exception for Reforge script errors."""

    pass


def get_repo_root(start_dir: Path | None = None) -> Path:
    """Find repository root by walking up directory tree.

    Looks for .reforge/ directory first, then .git/ as fallback.
    Matches behavior of bash get_repo_root() function.

    Args:
        start_dir: Starting directory for search. Defaults to current working directory.

    Returns:
        Path to repository root.

    Raises:
        ReforgeError: If no repository root marker found.
    """
    current = (start_dir or Path.cwd()).resolve()

    while current != current.parent:  # Stop at filesystem root
        if (current / ".reforge").is_dir():
            return current
        if (current / ".git").is_dir():
            return current
        current = current.parent

    # Check root itself
    if (current / ".reforge").is_dir() or (current / ".git").is_dir():
        return current

    raise ReforgeError(
        "Could not find repository root (.reforge/ or .git/ marker)"
    )


def get_config_value(key_path: str, config_file: Path) -> str | None:
    """Get a value from config.json using dotted key path.

    Supports paths like "project.name" or "output.directory".
    Matches behavior of bash get_config_value() function.

    Args:
        key_path: Dotted path to config value (e.g., "project.name").
        config_file: Path to config.json file.

    Returns:
        Config value as string, or None if not found.
    """
    if not config_file.is_file():
        return None

    try:
        data = json.loads(config_file.read_text())
    except (json.JSONDecodeError, OSError):
        return None

    keys = key_path.split(".")
    current = data

    for key in keys:
        if not isinstance(current, dict) or key not in current:
            return None
        current = current[key]

    # Return as string (matching bash behavior which always outputs strings)
    if current is None:
        return None
    return str(current)


def get_project_name(repo_root: Path) -> str:
    """Get project name from config or fall back to directory name.

    Matches behavior of bash get_project_name() function.

    Args:
        repo_root: Path to repository root.

    Returns:
        Project name string.
    """
    config_file = repo_root / ".reforge" / "config.json"
    name = get_config_value("project.name", config_file)

    if not name:
        name = repo_root.name

    return name


def get_output_dir(repo_root: Path) -> str:
    """Get configured output directory or default.

    Matches behavior of bash get_output_dir() function.

    Args:
        repo_root: Path to repository root.

    Returns:
        Output directory name (relative path string).
    """
    config_file = repo_root / ".reforge" / "config.json"
    output_dir = get_config_value("output.directory", config_file)

    if not output_dir:
        output_dir = "reforge_output"

    return output_dir


def get_project_output_dir(repo_root: Path) -> Path:
    """Get full path to project output directory.

    Combines repo_root, output_dir, and project_name.
    Matches behavior of bash get_project_output_dir() function.

    Args:
        repo_root: Path to repository root.

    Returns:
        Full path to project output directory.
    """
    output_dir = get_output_dir(repo_root)
    project_name = get_project_name(repo_root)

    return repo_root / output_dir / project_name


def ensure_dir(path: Path) -> None:
    """Create directory and parents if they don't exist.

    Matches behavior of bash ensure_dir() function.

    Args:
        path: Directory path to create.
    """
    path.mkdir(parents=True, exist_ok=True)


def check_file(file_path: Path, label: str | None = None) -> bool:
    """Check if file exists.

    Args:
        file_path: Path to check.
        label: Optional label for reporting.

    Returns:
        True if file exists, False otherwise.
    """
    return file_path.is_file()


def check_dir(dir_path: Path, label: str | None = None) -> bool:
    """Check if directory exists.

    Args:
        dir_path: Path to check.
        label: Optional label for reporting.

    Returns:
        True if directory exists, False otherwise.
    """
    return dir_path.is_dir()
