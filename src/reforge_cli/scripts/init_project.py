"""Initialize project output structure.

This module provides the same functionality as .reforge/scripts/bash/init-project.sh
but implemented in pure Python for cross-platform compatibility.

Usage from CLI: reforge init-project [--json] [--name <name>] [target-path]
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from .common import (
    ReforgeError,
    ensure_dir,
    get_config_value,
    get_output_dir,
    get_project_name,
    get_repo_root,
)


@dataclass
class InitResult:
    """Result of project initialization."""

    project_name: str
    output_dir: str
    project_output_dir: Path
    config: Path
    repo_root: Path

    def to_json(self) -> str:
        """Convert to JSON string matching bash script output format."""
        return json.dumps(
            {
                "PROJECT_NAME": self.project_name,
                "OUTPUT_DIR": self.output_dir,
                "PROJECT_OUTPUT_DIR": str(self.project_output_dir),
                "CONFIG": str(self.config),
                "REPO_ROOT": str(self.repo_root),
            }
        )


def init_project(
    target_path: Path | None = None,
    project_name_override: str | None = None,
) -> InitResult:
    """Initialize project output structure.

    Creates necessary directories and resolves project paths.
    Matches behavior of bash init-project.sh script.

    Args:
        target_path: Optional target directory. Defaults to current working directory.
        project_name_override: Optional project name to use instead of config/directory name.

    Returns:
        InitResult with resolved paths and project info.

    Raises:
        ReforgeError: If config.json not found.
    """
    # Resolve repository root
    if target_path:
        repo_root = get_repo_root(target_path)
    else:
        repo_root = get_repo_root()

    config = repo_root / ".reforge" / "config.json"

    if not config.is_file():
        raise ReforgeError(f"config.json not found at {config}")

    # Resolve project name
    if project_name_override:
        project_name = project_name_override
    else:
        project_name = get_project_name(repo_root)

    # Set project name in config.json if currently empty
    current_name = get_config_value("project.name", config)
    if not current_name and project_name:
        _update_config_project_name(config, project_name)

    # Resolve output paths
    output_dir = get_output_dir(repo_root)
    project_output_dir = repo_root / output_dir / project_name

    # Create directory structure
    ensure_dir(project_output_dir / "generated" / "diagrams")
    ensure_dir(repo_root / ".reforge" / "memory" / "history")
    ensure_dir(repo_root / ".reforge" / "memory" / "backups")
    ensure_dir(repo_root / ".reforge" / "memory" / "checkpoints")
    ensure_dir(repo_root / ".reforge" / "memory" / "clarifications")
    ensure_dir(repo_root / ".reforge" / "memory" / "logs")

    return InitResult(
        project_name=project_name,
        output_dir=output_dir,
        project_output_dir=project_output_dir,
        config=config,
        repo_root=repo_root,
    )


def _update_config_project_name(config: Path, project_name: str) -> None:
    """Update config.json with project name if empty.

    Args:
        config: Path to config.json file.
        project_name: Project name to set.
    """
    try:
        data = json.loads(config.read_text())
        if "project" in data and data["project"].get("name") == "":
            data["project"]["name"] = project_name
            config.write_text(json.dumps(data, indent=2) + "\n")
    except (json.JSONDecodeError, OSError, KeyError):
        # If we can't update, that's fine - config stays as-is
        pass
