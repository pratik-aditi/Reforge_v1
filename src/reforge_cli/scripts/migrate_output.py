"""Migrate flat output structure to categorized subdirectories.

This module provides the same functionality as .reforge/scripts/bash/migrate-output.sh
but implemented in pure Python for cross-platform compatibility.

Usage from CLI: reforge migrate-output [--json] [target-path]
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from .common import (
    ensure_dir,
    get_project_output_dir,
    get_repo_root,
)


@dataclass
class MigrationResult:
    """Result of output structure migration."""

    migrated: bool
    moved_files: int
    project_output_dir: Path
    moves: list[tuple[str, str]] = field(default_factory=list)

    def to_json(self) -> str:
        """Convert to JSON string matching bash script output format."""
        return json.dumps(
            {
                "MIGRATED": self.migrated,
                "MOVED_FILES": self.moved_files,
                "PROJECT_OUTPUT_DIR": str(self.project_output_dir),
            }
        )


def _move_if_exists(
    src: Path,
    dest_dir: Path,
    moves: list[tuple[str, str]],
) -> bool:
    """Move a file to destination directory if it exists.

    Args:
        src: Source file path.
        dest_dir: Destination directory path.
        moves: List to append move info to.

    Returns:
        True if file was moved, False otherwise.
    """
    if src.is_file():
        ensure_dir(dest_dir)
        dest = dest_dir / src.name
        src.rename(dest)
        moves.append((src.name, str(dest_dir.name) + "/"))
        return True
    return False


def _move_glob_if_exists(
    directory: Path,
    pattern: str,
    dest_dir: Path,
    moves: list[tuple[str, str]],
) -> int:
    """Move files matching glob pattern to destination directory.

    Args:
        directory: Directory to search in.
        pattern: Glob pattern to match.
        dest_dir: Destination directory path.
        moves: List to append move info to.

    Returns:
        Number of files moved.
    """
    count = 0
    for file_path in directory.glob(pattern):
        if file_path.is_file():
            ensure_dir(dest_dir)
            dest = dest_dir / file_path.name
            file_path.rename(dest)
            moves.append((file_path.name, str(dest_dir.name) + "/"))
            count += 1
    return count


def migrate_output(
    target_path: Path | None = None,
    output_dir_override: Path | None = None,
) -> MigrationResult:
    """Migrate flat output structure to categorized subdirectories.

    Migrates legacy flat structure to new categorized structure:
    - analysis.xml -> analysis/analysis.xml
    - business-rules.xml, etc. -> extractions/
    - cross-mappings.xml, etc. -> derived/
    - *-registry.md -> derived/registries/
    - diagram sources -> diagrams/sources/
    - rendered diagrams -> diagrams/rendered/

    Args:
        target_path: Optional target directory for repository root resolution.
        output_dir_override: Optional explicit output directory path.

    Returns:
        MigrationResult with migration details.
    """
    # Resolve project output directory
    if output_dir_override:
        project_output_dir = output_dir_override
    elif target_path:
        repo_root = get_repo_root(target_path)
        project_output_dir = get_project_output_dir(repo_root)
    else:
        repo_root = get_repo_root()
        project_output_dir = get_project_output_dir(repo_root)

    moves: list[tuple[str, str]] = []
    moved_files = 0

    # Move analysis.xml -> analysis/
    if _move_if_exists(
        project_output_dir / "analysis.xml",
        project_output_dir / "analysis",
        moves,
    ):
        moved_files += 1

    # Move extraction XMLs -> extractions/
    extractions_dir = project_output_dir / "extractions"
    for ext_type in ["business-rules", "database", "ui-flows", "workflows"]:
        if _move_if_exists(
            project_output_dir / f"{ext_type}.xml",
            extractions_dir,
            moves,
        ):
            moved_files += 1

    # Move derived artifacts -> derived/
    derived_dir = project_output_dir / "derived"
    for derived_file in ["cross-mappings.xml", "features-requirements.xml"]:
        if _move_if_exists(
            project_output_dir / derived_file,
            derived_dir,
            moves,
        ):
            moved_files += 1

    # Move registry files -> derived/registries/
    registries_dir = project_output_dir / "derived" / "registries"
    moved_files += _move_glob_if_exists(
        project_output_dir,
        "*-registry.md",
        registries_dir,
        moves,
    )

    # Move user-stories.xml from root -> generated/
    if _move_if_exists(
        project_output_dir / "user-stories.xml",
        project_output_dir / "generated",
        moves,
    ):
        moved_files += 1

    # Move diagram sources from generated/diagrams/ -> diagrams/sources/
    old_diagrams_dir = project_output_dir / "generated" / "diagrams"
    if old_diagrams_dir.is_dir():
        diagrams_sources = project_output_dir / "diagrams" / "sources"
        diagrams_rendered = project_output_dir / "diagrams" / "rendered"

        # Move source files
        moved_files += _move_glob_if_exists(
            old_diagrams_dir,
            "*.puml",
            diagrams_sources,
            moves,
        )
        moved_files += _move_glob_if_exists(
            old_diagrams_dir,
            "*.mmd",
            diagrams_sources,
            moves,
        )

        # Move rendered diagrams
        moved_files += _move_glob_if_exists(
            old_diagrams_dir,
            "*.png",
            diagrams_rendered,
            moves,
        )
        moved_files += _move_glob_if_exists(
            old_diagrams_dir,
            "*.svg",
            diagrams_rendered,
            moves,
        )

        # Remove empty generated/diagrams/ if now empty
        try:
            if old_diagrams_dir.is_dir() and not any(old_diagrams_dir.iterdir()):
                old_diagrams_dir.rmdir()
        except OSError:
            pass  # Directory not empty or other error, ignore

    return MigrationResult(
        migrated=True,
        moved_files=moved_files,
        project_output_dir=project_output_dir,
        moves=moves,
    )
