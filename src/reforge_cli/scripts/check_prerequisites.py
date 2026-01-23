"""Validate prerequisites for Reforge commands.

This module provides the same functionality as .reforge/scripts/bash/check-prerequisites.sh
but implemented in pure Python for cross-platform compatibility.

Usage from CLI: reforge check-prerequisites [--json] [--require-analysis] [--require-extraction <type>] [--include-checkpoint]
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from .common import (
    ReforgeError,
    get_project_name,
    get_project_output_dir,
    get_repo_root,
)


@dataclass
class PrerequisitesResult:
    """Result of prerequisites check."""

    project_name: str
    repo_root: Path
    project_output_dir: Path
    config: Path
    analysis_status: str
    available_extractions: list[str] = field(default_factory=list)
    checkpoint: Path | None = None
    clarifications_dir: Path | None = None

    def to_json(self) -> str:
        """Convert to JSON string matching bash script output format."""
        return json.dumps(
            {
                "PROJECT_NAME": self.project_name,
                "REPO_ROOT": str(self.repo_root),
                "PROJECT_OUTPUT_DIR": str(self.project_output_dir),
                "CONFIG": str(self.config),
                "ANALYSIS_STATUS": self.analysis_status,
                "AVAILABLE_EXTRACTIONS": self.available_extractions,
                "CHECKPOINT": str(self.checkpoint) if self.checkpoint else None,
                "CLARIFICATIONS_DIR": str(self.clarifications_dir)
                if self.clarifications_dir
                else None,
            }
        )


def check_prerequisites(
    require_analysis: bool = False,
    require_extraction: str | None = None,
    include_checkpoint: bool = False,
) -> PrerequisitesResult:
    """Validate prerequisites for Reforge commands.

    Checks for required analysis and extraction files.
    Matches behavior of bash check-prerequisites.sh script.

    Args:
        require_analysis: If True, raises error if analysis.xml doesn't exist.
        require_extraction: If set, raises error if specified extraction doesn't exist.
        include_checkpoint: If True, includes checkpoint path in result if it exists.

    Returns:
        PrerequisitesResult with validation results.

    Raises:
        ReforgeError: If required prerequisites are missing.
    """
    # Resolve paths
    repo_root = get_repo_root()
    config = repo_root / ".reforge" / "config.json"

    if not config.is_file():
        raise ReforgeError(f"config.json not found at {config}")

    project_name = get_project_name(repo_root)
    project_output_dir = get_project_output_dir(repo_root)
    clarifications_dir = repo_root / ".reforge" / "memory" / "clarifications"

    # Check analysis status
    analysis_file = project_output_dir / "analysis.xml"
    analysis_status = "completed" if analysis_file.is_file() else "not-found"

    if require_analysis and analysis_status == "not-found":
        raise ReforgeError(
            f"Analysis not found. Run /reforge.analyze first.\n  Expected: {analysis_file}"
        )

    # Check required extraction
    if require_extraction:
        extraction_file = project_output_dir / f"{require_extraction}.xml"
        if not extraction_file.is_file():
            raise ReforgeError(
                f"Extraction '{require_extraction}' not found. "
                f"Run /reforge.extract {require_extraction} first.\n"
                f"  Expected: {extraction_file}"
            )

    # List available extractions
    extraction_types = ["business-rules", "database", "ui-flows", "workflows"]
    available_extractions = [
        ext_type
        for ext_type in extraction_types
        if (project_output_dir / f"{ext_type}.xml").is_file()
    ]

    # Check for checkpoint
    checkpoint: Path | None = None
    if include_checkpoint:
        checkpoint_file = (
            repo_root / ".reforge" / "memory" / "checkpoints" / "analysis-checkpoint.xml"
        )
        if checkpoint_file.is_file():
            checkpoint = checkpoint_file

    return PrerequisitesResult(
        project_name=project_name,
        repo_root=repo_root,
        project_output_dir=project_output_dir,
        config=config,
        analysis_status=analysis_status,
        available_extractions=available_extractions,
        checkpoint=checkpoint,
        clarifications_dir=clarifications_dir,
    )
