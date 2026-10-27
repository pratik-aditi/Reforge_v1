"""Segment manifest (Layer 5).

The manifest is the deterministic contract between the source layer and the
extraction agents. It records what source exists, how it was divided, and
enough identity to prove a later run is looking at the same bytes.

Reproducibility rests on three hashes:

  * ``file_hash``   -- sha256 of the source bytes. Change the file, change the
    manifest. This is also what lets `/reforge.delta` invalidate only the files
    that actually moved.
  * ``config_hash`` -- the budget that produced the plan. The same file under a
    different budget is a different segmentation, and must not be mistaken for
    a cache hit.
  * ``generator_version`` -- bumped when the planner's behaviour changes, so an
    old manifest is never silently reused against new packing rules.

Same bytes + same config + same generator => byte-identical manifest.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from ..structure.models import StructuralMap
from .budget import Budget
from .coverage import CoverageReport, validate_plan
from .models import CoverageError, SegmentPlan

#: Bump when planning or splitting behaviour changes in a way that would
#: produce different segments for unchanged input.
GENERATOR_VERSION = "1.0.0"

MANIFEST_SCHEMA_VERSION = "1.0.0"


def file_hash(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def config_hash(budget: Budget) -> str:
    payload = json.dumps(
        {
            "target_tokens": budget.target_tokens,
            "max_tokens": budget.max_tokens,
            "max_lines": budget.max_lines,
        },
        sort_keys=True,
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def build_manifest(
    plan: SegmentPlan,
    source: bytes,
    budget: Budget,
    smap: StructuralMap | None = None,
    validate: bool = True,
) -> dict[str, Any]:
    """Build the manifest for one planned file.

    Validation is on by default and raises CoverageError. Writing a manifest
    that has not been proven to cover its source would defeat the purpose of
    having one.
    """
    report: CoverageReport | None = None
    if validate:
        report = validate_plan(plan, smap).raise_if_failed()

    manifest: dict[str, Any] = {
        "schema_version": MANIFEST_SCHEMA_VERSION,
        "generator_version": GENERATOR_VERSION,
        "file": plan.file,
        "file_hash": file_hash(source),
        "config_hash": config_hash(budget),
        "language": plan.language,
        "total_lines": plan.total_lines,
        "degraded": plan.degraded,
        "degraded_reason": plan.degraded_reason,
        "budget": {
            "target_tokens": budget.target_tokens,
            "max_tokens": budget.max_tokens,
            "max_lines": budget.max_lines,
        },
        "segments": [segment.to_dict() for segment in plan.segments],
    }
    if report is not None:
        manifest["coverage"] = report.to_dict()
    return manifest


def write_manifest(manifest: dict[str, Any], path: str | Path) -> Path:
    """Write a manifest as canonical JSON.

    Keys are sorted and separators fixed so two runs over identical input
    produce byte-identical files -- diffable, and safe to hash.
    """
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(manifest, indent=2, sort_keys=True, separators=(",", ": "))
    target.write_text(text + "\n", encoding="utf-8")
    return target


def load_manifest(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def is_stale(
    manifest: dict[str, Any],
    source: bytes,
    budget: Budget,
) -> bool:
    """True when a stored manifest must not be reused for this input."""
    return (
        manifest.get("file_hash") != file_hash(source)
        or manifest.get("config_hash") != config_hash(budget)
        or manifest.get("generator_version") != GENERATOR_VERSION
    )


def manifest_path(output_dir: str | Path, file: str) -> Path:
    """Location of a file's manifest inside the analysis output directory."""
    stem = Path(file).name
    return Path(output_dir) / "segments" / f"{stem}.segments.json"


__all__ = [
    "GENERATOR_VERSION",
    "MANIFEST_SCHEMA_VERSION",
    "CoverageError",
    "build_manifest",
    "config_hash",
    "file_hash",
    "is_stale",
    "load_manifest",
    "manifest_path",
    "write_manifest",
]
