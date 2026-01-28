"""Checkpoint CRUD for analysis/extraction state.

This module provides the same functionality as .reforge/scripts/bash/manage-checkpoint.sh
but implemented in pure Python for cross-platform compatibility.

Usage from CLI: reforge manage-checkpoint <read|create|delete> [--json] [--type analysis|extraction]
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

from .common import ensure_dir, get_repo_root


@dataclass
class CheckpointStatus:
    """Result of reading a checkpoint."""

    exists: bool
    checkpoint_type: str
    total_files: int = 0
    processed_files: int = 0
    current_file: str = ""
    started_at: str = ""
    elapsed_seconds: int = 0
    percentage: int = 0

    def to_json(self) -> str:
        """Convert to JSON string matching bash script output format."""
        return json.dumps(
            {
                "EXISTS": self.exists,
                "TYPE": self.checkpoint_type,
                "TOTAL_FILES": self.total_files,
                "PROCESSED_FILES": self.processed_files,
                "CURRENT_FILE": self.current_file,
                "STARTED_AT": self.started_at,
                "ELAPSED_SECONDS": self.elapsed_seconds,
                "PERCENTAGE": self.percentage,
            }
        )


@dataclass
class CheckpointPath:
    """Result of creating a checkpoint (returns path info)."""

    checkpoint_file: Path
    checkpoint_dir: Path

    def to_json(self) -> str:
        """Convert to JSON string matching bash script output format."""
        return json.dumps(
            {
                "CHECKPOINT_FILE": str(self.checkpoint_file),
                "CHECKPOINT_DIR": str(self.checkpoint_dir),
            }
        )


@dataclass
class CheckpointDeleted:
    """Result of deleting a checkpoint."""

    deleted: bool
    file: Path

    def to_json(self) -> str:
        """Convert to JSON string matching bash script output format."""
        return json.dumps(
            {
                "DELETED": self.deleted,
                "FILE": str(self.file),
            }
        )


def _extract_xml_value(content: str, tag: str) -> str:
    """Extract value from XML tag.

    Args:
        content: XML content to search.
        tag: Tag name to extract value from.

    Returns:
        Tag value or empty string if not found.
    """
    pattern = rf"<{tag}>([^<]*)</{tag}>"
    match = re.search(pattern, content)
    return match.group(1) if match else ""


def read_checkpoint(checkpoint_type: str = "analysis") -> CheckpointStatus:
    """Read checkpoint status.

    Args:
        checkpoint_type: Type of checkpoint ("analysis" or "extraction").

    Returns:
        CheckpointStatus with current checkpoint state.
    """
    repo_root = get_repo_root()
    checkpoint_dir = repo_root / ".reforge" / "memory" / "checkpoints"
    checkpoint_file = checkpoint_dir / f"{checkpoint_type}-checkpoint.xml"

    if not checkpoint_file.is_file():
        return CheckpointStatus(
            exists=False,
            checkpoint_type=checkpoint_type,
        )

    content = checkpoint_file.read_text()

    # Parse XML values
    total_files_str = _extract_xml_value(content, "total-files")
    processed_files_str = _extract_xml_value(content, "processed-files")
    elapsed_seconds_str = _extract_xml_value(content, "elapsed-seconds")

    total_files = int(total_files_str) if total_files_str.isdigit() else 0
    processed_files = int(processed_files_str) if processed_files_str.isdigit() else 0
    elapsed_seconds = int(elapsed_seconds_str) if elapsed_seconds_str.isdigit() else 0

    # Calculate percentage
    percentage = (processed_files * 100 // total_files) if total_files > 0 else 0

    return CheckpointStatus(
        exists=True,
        checkpoint_type=checkpoint_type,
        total_files=total_files,
        processed_files=processed_files,
        current_file=_extract_xml_value(content, "current-file"),
        started_at=_extract_xml_value(content, "started-at"),
        elapsed_seconds=elapsed_seconds,
        percentage=percentage,
    )


def create_checkpoint(checkpoint_type: str = "analysis") -> CheckpointPath:
    """Create checkpoint path (ensures directory exists).

    The actual checkpoint content is written by the agent.
    This function just ensures the directory exists and returns the path.

    Args:
        checkpoint_type: Type of checkpoint ("analysis" or "extraction").

    Returns:
        CheckpointPath with file and directory paths.
    """
    repo_root = get_repo_root()
    checkpoint_dir = repo_root / ".reforge" / "memory" / "checkpoints"
    ensure_dir(checkpoint_dir)

    checkpoint_file = checkpoint_dir / f"{checkpoint_type}-checkpoint.xml"

    return CheckpointPath(
        checkpoint_file=checkpoint_file,
        checkpoint_dir=checkpoint_dir,
    )


def delete_checkpoint(checkpoint_type: str = "analysis") -> CheckpointDeleted:
    """Delete a checkpoint file.

    Args:
        checkpoint_type: Type of checkpoint ("analysis" or "extraction").

    Returns:
        CheckpointDeleted with deletion result.
    """
    repo_root = get_repo_root()
    checkpoint_dir = repo_root / ".reforge" / "memory" / "checkpoints"
    checkpoint_file = checkpoint_dir / f"{checkpoint_type}-checkpoint.xml"

    if checkpoint_file.is_file():
        checkpoint_file.unlink()
        return CheckpointDeleted(deleted=True, file=checkpoint_file)
    else:
        return CheckpointDeleted(deleted=False, file=checkpoint_file)
