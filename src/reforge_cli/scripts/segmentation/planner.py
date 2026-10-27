"""Segment planner (Layer 3).

Turns a StructuralMap into bounded, contiguous extraction segments.

Policy, per reforge-update.txt:

  * A file that fits the budget is kept whole.
  * Otherwise, pack *complete adjacent members* until the budget is reached.
  * `every N lines -> split` is never the primary strategy. It appears only in
    the degraded fallback, when structural parsing failed outright.

Method integrity is preserved wherever possible: a member is either wholly
inside one segment, or it is oversized and tagged for Layer 4's block splitter.
This module never splits a member itself.

Coverage is the invariant that matters: the emitted segments tile the file from
line 1 to the final line with no gap and no overlap. Interstitial source --
imports, field declarations, class headers, comment banners between members --
is captured as its own atom rather than skipped, which is the step most
implementations get wrong.
"""

from __future__ import annotations

import re

from ..structure.models import StructuralMap, StructuralUnit
from .budget import Budget, estimate_lines_tokens
from .models import (
    STRATEGY_FALLBACK_WINDOW,
    STRATEGY_INTERSTITIAL,
    STRATEGY_MEMBER_PACK,
    STRATEGY_OVERSIZED_MEMBER,
    STRATEGY_WHOLE_FILE,
    CoverageError,
    Segment,
    SegmentPlan,
)

_SLUG_RE = re.compile(r"[^a-z0-9]+")

_CONTAINER_TYPES = ("namespace", "class", "module", "interface", "structure", "enum")


def _slug(file: str) -> str:
    stem = file.rsplit("/", 1)[-1].rsplit("\\", 1)[-1]
    stem = stem.rsplit(".", 1)[0]
    return _SLUG_RE.sub("-", stem.lower()).strip("-") or "file"


def _segment_id(file: str, start_line: int) -> str:
    """Stable identifier for a segment.

    Derived from the start line, not from an incrementing counter, so that
    inserting code in one part of a file does not renumber every segment after
    it. Layer 5 adds the file hash to the manifest for change detection.
    """
    return f"{_slug(file)}-{start_line:06d}"


def _outermost_members(smap: StructuralMap) -> list[StructuralUnit]:
    """Members that anchor segmentation.

    Body-less declarations (interface members, Declare, auto-properties) are
    excluded: they are single lines and belong with the surrounding
    interstitial source. Members nested inside another member are dropped so a
    range is never claimed twice.
    """
    candidates = [u for u in smap.leaves() if not u.body_less]
    result: list[StructuralUnit] = []
    for unit in candidates:
        if any(
            other.start_line <= unit.start_line and unit.end_line <= other.end_line
            for other in result
        ):
            continue
        result.append(unit)
    return result


def _atoms(smap: StructuralMap) -> list[tuple[int, int, StructuralUnit | None]]:
    """Tile the file into (start, end, member-or-None) spans.

    Guarantees by construction that the union of spans is exactly
    1..total_lines, with no gap and no overlap.
    """
    spans: list[tuple[int, int, StructuralUnit | None]] = []
    cursor = 1
    for member in _outermost_members(smap):
        if member.start_line > cursor:
            spans.append((cursor, member.start_line - 1, None))
        spans.append((member.start_line, member.end_line, member))
        cursor = member.end_line + 1
    if cursor <= smap.total_lines:
        spans.append((cursor, smap.total_lines, None))
    return spans


def _context_path(smap: StructuralMap, line: int) -> str:
    """Namespace -> class chain enclosing a line, for the task packet header."""
    enclosing = [
        u
        for u in smap.units
        if u.type in _CONTAINER_TYPES and u.start_line <= line <= u.end_line
    ]
    enclosing.sort(key=lambda u: (u.nesting_depth, u.start_line))
    return ".".join(u.name for u in enclosing)


def _members_in_range(smap: StructuralMap, start: int, end: int) -> list[str]:
    """Names of all members overlapping a range, including body-less ones."""
    names: list[str] = []
    for unit in smap.leaves():
        if unit.start_line <= end and unit.end_line >= start:
            if unit.name not in names:
                names.append(unit.name)
    return names


def _assert_contiguous(plan: SegmentPlan) -> None:
    """Light self-check. Layer 5 owns the full coverage validator.

    Known limit: this detects a missing start, a missing end, an overlap and a
    gap *between* segments. It cannot detect a member atom lost in the middle
    of a packed segment, because a segment takes its bounds from the first and
    last atom it holds -- the enclosing segment still covers those lines, so
    no source is lost, but the member would vanish from `members`. Closing that
    requires checking every structural member against the plan, which is
    Layer 5's job.
    """
    if plan.total_lines == 0:
        if plan.segments:
            raise CoverageError(f"{plan.file}: segments emitted for an empty file")
        return
    if not plan.segments:
        raise CoverageError(f"{plan.file}: no segments emitted for a non-empty file")
    if plan.segments[0].start_line != 1:
        raise CoverageError(
            f"{plan.file}: coverage starts at line {plan.segments[0].start_line}, not 1"
        )
    if plan.segments[-1].end_line != plan.total_lines:
        raise CoverageError(
            f"{plan.file}: coverage ends at line {plan.segments[-1].end_line}, "
            f"expected {plan.total_lines}"
        )
    for previous, following in zip(plan.segments, plan.segments[1:]):
        if following.start_line != previous.end_line + 1:
            raise CoverageError(
                f"{plan.file}: gap or overlap between {previous.segment_id} "
                f"(ends {previous.end_line}) and {following.segment_id} "
                f"(starts {following.start_line})"
            )
    if len({s.segment_id for s in plan.segments}) != len(plan.segments):
        raise CoverageError(f"{plan.file}: duplicate segment ids")


def plan_segments(
    smap: StructuralMap,
    lines: list[str],
    budget: Budget | None = None,
) -> SegmentPlan:
    """Build a segment plan for one structurally-parsed file."""
    budget = budget or Budget()
    plan = SegmentPlan(
        file=smap.file, total_lines=smap.total_lines, language=smap.language
    )

    if smap.total_lines == 0:
        return plan

    whole_tokens = estimate_lines_tokens(lines, 1, smap.total_lines)
    if not budget.exceeds(whole_tokens, smap.total_lines):
        plan.segments.append(
            Segment(
                segment_id=_segment_id(smap.file, 1),
                file=smap.file,
                start_line=1,
                end_line=smap.total_lines,
                strategy=STRATEGY_WHOLE_FILE,
                members=_members_in_range(smap, 1, smap.total_lines),
                est_tokens=whole_tokens,
                context_path=_context_path(smap, 1),
            )
        )
        _assert_contiguous(plan)
        return plan

    pending: list[tuple[int, int, StructuralUnit | None]] = []
    pending_tokens = 0

    def flush() -> None:
        nonlocal pending, pending_tokens
        if not pending:
            return
        start = pending[0][0]
        end = pending[-1][1]
        has_member = any(unit is not None for _, _, unit in pending)
        plan.segments.append(
            Segment(
                segment_id=_segment_id(smap.file, start),
                file=smap.file,
                start_line=start,
                end_line=end,
                strategy=STRATEGY_MEMBER_PACK if has_member else STRATEGY_INTERSTITIAL,
                members=_members_in_range(smap, start, end),
                est_tokens=pending_tokens,
                context_path=_context_path(smap, start),
            )
        )
        pending = []
        pending_tokens = 0

    for start, end, unit in _atoms(smap):
        tokens = estimate_lines_tokens(lines, start, end)
        line_count = end - start + 1

        if budget.exceeds(tokens, line_count):
            # Too large to stand alone. Emit it as its own segment and let
            # Layer 4 subdivide it at safe control-structure boundaries. The
            # planner never cuts into a member itself.
            flush()
            plan.segments.append(
                Segment(
                    segment_id=_segment_id(smap.file, start),
                    file=smap.file,
                    start_line=start,
                    end_line=end,
                    strategy=(
                        STRATEGY_OVERSIZED_MEMBER
                        if unit is not None
                        else STRATEGY_INTERSTITIAL
                    ),
                    members=_members_in_range(smap, start, end),
                    est_tokens=tokens,
                    needs_split=True,
                    context_path=_context_path(smap, start),
                )
            )
            continue

        would_be_tokens = pending_tokens + tokens
        would_be_lines = (end - pending[0][0] + 1) if pending else line_count
        if pending and (
            would_be_tokens > budget.target_tokens
            or would_be_lines > budget.max_lines
        ):
            flush()

        pending.append((start, end, unit))
        pending_tokens += tokens

    flush()
    _assert_contiguous(plan)
    return plan


def plan_token_windows(
    file: str,
    lines: list[str],
    budget: Budget | None = None,
    reason: str = "",
    overlap_lines: int = 0,
) -> SegmentPlan:
    """Degraded fallback for files that cannot be parsed structurally.

    Deterministic fixed-token windows. Coverage is still guaranteed: the
    windows tile the file end to end. Overlap, when requested, is recorded by
    extending each window backwards, so the union still covers every line.
    """
    budget = budget or Budget()
    plan = SegmentPlan(
        file=file,
        total_lines=len(lines),
        degraded=True,
        degraded_reason=reason or "structural parse failed",
    )
    if not lines:
        return plan

    total = len(lines)
    cursor = 1
    while cursor <= total:
        end = cursor
        tokens = 0
        while end <= total:
            line_tokens = estimate_lines_tokens(lines, end, end)
            if end > cursor and (
                tokens + line_tokens > budget.target_tokens
                or (end - cursor + 1) > budget.max_lines
            ):
                end -= 1
                break
            tokens += line_tokens
            end += 1
        end = min(end, total)
        start = cursor if not plan.segments else max(1, cursor - overlap_lines)
        plan.segments.append(
            Segment(
                segment_id=_segment_id(file, cursor),
                file=file,
                start_line=start,
                end_line=end,
                strategy=STRATEGY_FALLBACK_WINDOW,
                est_tokens=estimate_lines_tokens(lines, start, end),
                overlap_previous=cursor - start,
                context_path="",
            )
        )
        cursor = end + 1
    return plan
