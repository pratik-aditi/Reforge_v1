"""Oversized-member splitter (Layer 4).

Some legacy methods exceed any sane budget on their own -- `TrackTrainIDOn` in
Track.vb runs 1,253 lines. They cannot be packed and they cannot be skipped, so
they must be subdivided.

The rule from reforge-update.txt: **only split at safe structural boundaries.**
Cutting mid-`If` hands an agent a condition with no consequence, or a branch
with no condition, and any rule it extracts from that is fiction.

So the splitter re-scans the member body tracking control-structure depth and
cuts only where depth returns to zero -- between complete top-level statements:

    If / End If            For / Next            Using / End Using
    Select Case / End      While / End While     With / End With
    Try / Catch / End Try  Do / Loop             SyncLock / End SyncLock

When a single depth-0 block is itself over budget, the splitter recurses one
level deeper and cuts at depth-1 boundaries (`block-split-deep`). Only when
even that fails does it fall back to an arbitrary line cut, and that subsegment
is marked `integrity="degraded"` so the damage is visible in the manifest
rather than silent.

Coverage is preserved at every level: subsegments tile the parent's range
exactly, with no gap and no overlap.
"""

from __future__ import annotations

import re

from ..structure.vbnet import strip_noise
from .budget import Budget, estimate_lines_tokens
from .planner import _segment_id
from .models import (
    INTEGRITY_DEGRADED,
    INTEGRITY_INTACT,
    STRATEGY_BLOCK_SPLIT,
    STRATEGY_BLOCK_SPLIT_DEEP,
    Segment,
    SegmentPlan,
)

# Block openers. `If` is handled separately: the single-line form
# (`If x Then DoThing()`) opens nothing.
_OPENERS = (
    (re.compile(r"^select\s+case\b", re.IGNORECASE), "select"),
    (re.compile(r"^try\b", re.IGNORECASE), "try"),
    (re.compile(r"^for\s+each\b", re.IGNORECASE), "for"),
    (re.compile(r"^for\b", re.IGNORECASE), "for"),
    (re.compile(r"^do\b", re.IGNORECASE), "do"),
    (re.compile(r"^while\b", re.IGNORECASE), "while"),
    (re.compile(r"^using\b", re.IGNORECASE), "using"),
    (re.compile(r"^with\b", re.IGNORECASE), "with"),
    (re.compile(r"^synclock\b", re.IGNORECASE), "synclock"),
)

_CLOSERS = (
    (re.compile(r"^end\s+if\b", re.IGNORECASE), "if"),
    (re.compile(r"^end\s+select\b", re.IGNORECASE), "select"),
    (re.compile(r"^end\s+try\b", re.IGNORECASE), "try"),
    (re.compile(r"^end\s+while\b", re.IGNORECASE), "while"),
    (re.compile(r"^wend\b", re.IGNORECASE), "while"),
    (re.compile(r"^end\s+using\b", re.IGNORECASE), "using"),
    (re.compile(r"^end\s+with\b", re.IGNORECASE), "with"),
    (re.compile(r"^end\s+synclock\b", re.IGNORECASE), "synclock"),
    (re.compile(r"^next\b", re.IGNORECASE), "for"),
    (re.compile(r"^loop\b", re.IGNORECASE), "do"),
)

_RE_IF = re.compile(r"^if\b", re.IGNORECASE)
_RE_IF_THEN_TRAILING = re.compile(r"\bthen\b(?P<rest>.*)$", re.IGNORECASE)
_RE_ELSEIF = re.compile(r"^else\s*if\b", re.IGNORECASE)

# Continuation keywords: they sit inside an open block and are never cut points.
_RE_CONTINUATION = re.compile(
    r"^(else|elseif|case|catch|finally)\b", re.IGNORECASE
)


def _opens_block(text: str) -> str | None:
    """Return the block kind this line opens, or None."""
    if _RE_ELSEIF.match(text):
        return None
    if _RE_IF.match(text):
        match = _RE_IF_THEN_TRAILING.search(text)
        if match is None:
            # `If ... ` continued onto the next logical line; treat as a block.
            return "if"
        # `If x Then DoThing()` is a complete statement and opens nothing.
        return None if match.group("rest").strip() else "if"
    for pattern, kind in _OPENERS:
        if pattern.match(text):
            return kind
    return None


def _closes_block(text: str) -> str | None:
    for pattern, kind in _CLOSERS:
        if pattern.match(text):
            return kind
    return None


def top_level_boundaries(
    lines: list[str], start_line: int, end_line: int, level: int = 0
) -> list[int]:
    """Lines at which a cut is safe inside an inclusive range.

    Returns the start lines of complete statements sitting at nesting `level`.
    `start_line` is always included. A line is a boundary only when the control
    structure depth is exactly `level` and no block is mid-flight.
    """
    boundaries: list[int] = []
    depth = 0
    stack: list[str] = []
    pending_depth_zero = True
    continuing = False

    for lineno in range(start_line, end_line + 1):
        text = strip_noise(lines[lineno - 1])
        if not text:
            continue

        # A line continued from the previous one is part of the same statement.
        # Cutting between them would sever a statement mid-expression, which is
        # exactly what this function exists to prevent.
        was_continuing = continuing
        continuing = text.endswith("_") and (len(text) == 1 or text[-2].isspace())
        if was_continuing:
            continue

        closing = _closes_block(text)
        if closing is not None:
            if stack:
                stack.pop()
                depth = len(stack)
            pending_depth_zero = depth <= level
            continue

        if _RE_CONTINUATION.match(text) and not _RE_ELSEIF.match(text):
            pending_depth_zero = False
            continue
        if _RE_ELSEIF.match(text):
            pending_depth_zero = False
            continue

        if depth <= level and pending_depth_zero:
            boundaries.append(lineno)

        opening = _opens_block(text)
        if opening is not None:
            stack.append(opening)
            depth = len(stack)
            pending_depth_zero = False
        else:
            pending_depth_zero = depth <= level

    if not boundaries or boundaries[0] != start_line:
        boundaries.insert(0, start_line)
    return boundaries


def _pack_boundaries(
    lines: list[str],
    start_line: int,
    end_line: int,
    boundaries: list[int],
    budget: Budget,
) -> list[tuple[int, int]]:
    """Group boundary-delimited blocks into budget-sized ranges."""
    blocks: list[tuple[int, int]] = []
    for index, boundary in enumerate(boundaries):
        stop = boundaries[index + 1] - 1 if index + 1 < len(boundaries) else end_line
        if boundary <= stop:
            blocks.append((boundary, stop))
    if not blocks:
        return [(start_line, end_line)]

    packed: list[tuple[int, int]] = []
    current_start = blocks[0][0]
    current_end = blocks[0][1]
    for block_start, block_end in blocks[1:]:
        candidate_tokens = estimate_lines_tokens(lines, current_start, block_end)
        candidate_lines = block_end - current_start + 1
        if candidate_tokens > budget.target_tokens or candidate_lines > budget.max_lines:
            packed.append((current_start, current_end))
            current_start, current_end = block_start, block_end
        else:
            current_end = block_end
    packed.append((current_start, current_end))
    return packed


def _line_windows(
    start_line: int, end_line: int, max_lines: int
) -> list[tuple[int, int]]:
    """Last-resort even cuts, used only when no safe boundary helps."""
    windows: list[tuple[int, int]] = []
    cursor = start_line
    while cursor <= end_line:
        stop = min(cursor + max_lines - 1, end_line)
        windows.append((cursor, stop))
        cursor = stop + 1
    return windows


def split_segment(
    segment: Segment,
    lines: list[str],
    budget: Budget | None = None,
) -> list[Segment]:
    """Subdivide one oversized segment at safe boundaries.

    Returns subsegments tiling the original range exactly. A segment that is
    not oversized is returned unchanged, as a single-item list.
    """
    budget = budget or Budget()
    if not segment.needs_split:
        return [segment]

    start, end = segment.start_line, segment.end_line

    # The signature and the closing `End` line belong to the member, not to any
    # inner block; scanning them would unbalance the depth counter.
    body_start = min(start + 1, end)
    body_end = max(end - 1, body_start)

    ranges = _pack_boundaries(
        lines, body_start, body_end,
        top_level_boundaries(lines, body_start, body_end, level=0),
        budget,
    )

    # Any range still over budget gets one deeper pass, then line windows.
    refined: list[tuple[int, int, str, str]] = []
    for range_start, range_end in ranges:
        tokens = estimate_lines_tokens(lines, range_start, range_end)
        line_count = range_end - range_start + 1
        if not budget.exceeds(tokens, line_count):
            refined.append((range_start, range_end, STRATEGY_BLOCK_SPLIT, INTEGRITY_INTACT))
            continue

        deeper = _pack_boundaries(
            lines, range_start, range_end,
            top_level_boundaries(lines, range_start, range_end, level=1),
            budget,
        )
        if len(deeper) > 1:
            for deep_start, deep_end in deeper:
                deep_tokens = estimate_lines_tokens(lines, deep_start, deep_end)
                deep_lines = deep_end - deep_start + 1
                if budget.exceeds(deep_tokens, deep_lines):
                    refined.extend(
                        (window_start, window_end, STRATEGY_BLOCK_SPLIT_DEEP, INTEGRITY_DEGRADED)
                        for window_start, window_end in _line_windows(
                            deep_start, deep_end, budget.max_lines
                        )
                    )
                else:
                    refined.append(
                        (deep_start, deep_end, STRATEGY_BLOCK_SPLIT_DEEP, INTEGRITY_INTACT)
                    )
        else:
            refined.extend(
                (window_start, window_end, STRATEGY_BLOCK_SPLIT_DEEP, INTEGRITY_DEGRADED)
                for window_start, window_end in _line_windows(
                    range_start, range_end, budget.max_lines
                )
            )

    # Re-attach the signature line to the first subsegment and the closing line
    # to the last, so the parent's range is tiled exactly.
    if not refined:
        refined = [(start, end, STRATEGY_BLOCK_SPLIT, INTEGRITY_DEGRADED)]
    first = refined[0]
    refined[0] = (start, first[1], first[2], first[3])
    last = refined[-1]
    refined[-1] = (last[0], end, last[2], last[3])

    parent = segment.parent_member or (segment.members[0] if segment.members else "")
    total = len(refined)
    out: list[Segment] = []
    for index, (sub_start, sub_end, strategy, integrity) in enumerate(refined, start=1):
        out.append(
            Segment(
                # Anchored to its own start line, like every other segment, so
                # the manifest's identity rule stays uniform.
                segment_id=_segment_id(segment.file, sub_start),
                file=segment.file,
                start_line=sub_start,
                end_line=sub_end,
                strategy=strategy,
                members=list(segment.members),
                est_tokens=estimate_lines_tokens(lines, sub_start, sub_end),
                needs_split=False,
                context_path=segment.context_path,
                parent_member=parent,
                subsegment_index=index,
                subsegment_count=total,
                integrity=integrity,
            )
        )
    return out


def apply_splits(
    plan: SegmentPlan,
    lines: list[str],
    budget: Budget | None = None,
) -> SegmentPlan:
    """Replace every oversized segment in a plan with its subsegments."""
    budget = budget or Budget()
    expanded: list[Segment] = []
    for segment in plan.segments:
        expanded.extend(split_segment(segment, lines, budget))
    plan.segments = expanded
    return plan
