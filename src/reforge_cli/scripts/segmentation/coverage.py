"""Coverage validator (Layer 5).

Enforces the mandatory invariant from reforge-update.txt:

    Source line 1 -> final source line. NO SILENT GAP.

Every check here is a hard failure, never a warning. A manifest that silently
drops source is worse than no manifest at all, because everything downstream
trusts it: if a range is missing from the plan, no agent ever reads it, nothing
is ever extracted from it, and no output will look wrong.

The member-assignment check is the one that matters most. Contiguity alone
cannot see a member lost inside a packed segment -- the enclosing segment still
covers those lines, so coverage looks intact while the member quietly vanishes
from the task packets. Checking every structural member against the plan is
what closes that hole.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ..structure.models import StructuralMap
from .models import CoverageError, SegmentPlan


@dataclass
class CoverageReport:
    """Outcome of validating one segment plan."""

    file: str
    total_lines: int
    segment_count: int
    covered_lines: int
    declared_overlap_lines: int
    members_total: int
    members_assigned: int
    errors: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors

    @property
    def coverage_pct(self) -> float:
        if self.total_lines == 0:
            return 100.0
        return round(100.0 * self.covered_lines / self.total_lines, 4)

    def to_dict(self) -> dict[str, Any]:
        return {
            "file": self.file,
            "ok": self.ok,
            "total_lines": self.total_lines,
            "segment_count": self.segment_count,
            "covered_lines": self.covered_lines,
            "coverage_pct": self.coverage_pct,
            "declared_overlap_lines": self.declared_overlap_lines,
            "members_total": self.members_total,
            "members_assigned": self.members_assigned,
            "errors": list(self.errors),
        }

    def raise_if_failed(self) -> CoverageReport:
        if self.errors:
            joined = "\n  - ".join(self.errors)
            raise CoverageError(f"{self.file}: coverage validation failed\n  - {joined}")
        return self


def validate_plan(
    plan: SegmentPlan,
    smap: StructuralMap | None = None,
) -> CoverageReport:
    """Validate a segment plan. Returns a report; never raises on its own.

    Pass the StructuralMap to enable the member-assignment and ordering checks.
    Without it only the line-level checks run, which is the correct behaviour
    for a degraded fallback plan where no structure was discoverable.
    """
    errors: list[str] = []
    segments = plan.segments
    ordered = sorted(segments, key=lambda s: (s.start_line, s.end_line))

    # --- ordering ---------------------------------------------------------
    if segments != ordered:
        errors.append("segments are not in source order")

    # --- identifiers ------------------------------------------------------
    ids = [s.segment_id for s in segments]
    duplicates = sorted({i for i in ids if ids.count(i) > 1})
    if duplicates:
        errors.append(f"duplicate segment ids: {', '.join(duplicates)}")
    for segment in segments:
        if not segment.segment_id:
            errors.append(f"segment at line {segment.start_line} has no id")
        # Identity anchors to the first line the segment owns exclusively, not
        # to its overlap-extended start. Otherwise changing the overlap setting
        # would renumber every segment -- precisely what start-line-derived ids
        # exist to prevent.
        anchor = segment.start_line + segment.overlap_previous
        if not segment.segment_id.endswith(f"{anchor:06d}"):
            errors.append(
                f"{segment.segment_id}: id is not derived from its anchor line "
                f"({anchor})"
            )

    # --- well-formed ranges ----------------------------------------------
    for segment in segments:
        if segment.start_line < 1:
            errors.append(f"{segment.segment_id}: start line {segment.start_line} < 1")
        if segment.end_line > plan.total_lines:
            errors.append(
                f"{segment.segment_id}: end line {segment.end_line} exceeds file "
                f"length {plan.total_lines}"
            )
        if segment.start_line > segment.end_line:
            errors.append(f"{segment.segment_id}: inverted range")

    # --- empty file -------------------------------------------------------
    if plan.total_lines == 0:
        if segments:
            errors.append("segments emitted for an empty file")
        return CoverageReport(
            file=plan.file,
            total_lines=0,
            segment_count=len(segments),
            covered_lines=0,
            declared_overlap_lines=0,
            members_total=0,
            members_assigned=0,
            errors=errors,
        )

    if not segments:
        errors.append("no segments emitted for a non-empty file")
        return CoverageReport(
            file=plan.file,
            total_lines=plan.total_lines,
            segment_count=0,
            covered_lines=0,
            declared_overlap_lines=0,
            members_total=len(smap.leaves()) if smap else 0,
            members_assigned=0,
            errors=errors,
        )

    # --- boundaries -------------------------------------------------------
    if ordered[0].start_line != 1:
        errors.append(
            f"coverage starts at line {ordered[0].start_line}, not 1 "
            "(beginning of source not covered)"
        )
    last_line = max(s.end_line for s in segments)
    if last_line != plan.total_lines:
        errors.append(
            f"coverage ends at line {last_line}, expected {plan.total_lines} "
            "(end of source not covered)"
        )

    # --- gaps and undeclared overlap -------------------------------------
    declared_overlap = 0
    for previous, following in zip(ordered, ordered[1:]):
        expected = previous.end_line + 1
        if following.start_line > expected:
            errors.append(
                f"silent gap: lines {expected}-{following.start_line - 1} "
                f"between {previous.segment_id} and {following.segment_id}"
            )
        elif following.start_line < expected:
            actual = expected - following.start_line
            if following.overlap_previous != actual:
                errors.append(
                    f"{following.segment_id}: undeclared overlap of {actual} line(s) "
                    f"with {previous.segment_id} (declared {following.overlap_previous})"
                )
            else:
                declared_overlap += actual

    covered: set[int] = set()
    for segment in segments:
        covered |= set(range(max(1, segment.start_line), segment.end_line + 1))
    missing = set(range(1, plan.total_lines + 1)) - covered
    if missing:
        errors.append(f"{len(missing)} source line(s) not covered by any segment")

    # --- structural checks ------------------------------------------------
    members_total = 0
    members_assigned = 0
    if smap is not None:
        leaves = smap.leaves()
        members_total = len(leaves)
        listed = {name for s in segments for name in s.members}
        for member in leaves:
            holders = [
                s
                for s in segments
                if s.start_line <= member.end_line and s.end_line >= member.start_line
            ]
            if not holders:
                errors.append(
                    f"member '{member.name}' (lines {member.start_line}-"
                    f"{member.end_line}) is in no segment"
                )
                continue
            if member.name not in listed:
                errors.append(
                    f"member '{member.name}' is covered by "
                    f"{holders[0].segment_id} but missing from its member list"
                )
                continue
            members_assigned += 1

    return CoverageReport(
        file=plan.file,
        total_lines=plan.total_lines,
        segment_count=len(segments),
        covered_lines=len(covered),
        declared_overlap_lines=declared_overlap,
        members_total=members_total,
        members_assigned=members_assigned,
        errors=errors,
    )


def assert_valid(plan: SegmentPlan, smap: StructuralMap | None = None) -> CoverageReport:
    """Validate and raise CoverageError on any failure."""
    return validate_plan(plan, smap).raise_if_failed()
