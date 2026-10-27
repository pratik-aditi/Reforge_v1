"""Data model for bounded extraction segments (Layer 3).

A Segment is a contiguous, inclusive line range of one source file, large
enough to be meaningful and small enough that no part of it sits in the
positionally-disadvantaged middle of a model's context.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

#: How a segment's boundaries were chosen.
STRATEGY_WHOLE_FILE = "whole-file"
STRATEGY_MEMBER_PACK = "member-pack"
STRATEGY_INTERSTITIAL = "interstitial"
STRATEGY_OVERSIZED_MEMBER = "oversized-member"
STRATEGY_BLOCK_SPLIT = "block-split"
STRATEGY_BLOCK_SPLIT_DEEP = "block-split-deep"
STRATEGY_FALLBACK_WINDOW = "fallback-window"

STRATEGIES = (
    STRATEGY_WHOLE_FILE,
    STRATEGY_MEMBER_PACK,
    STRATEGY_INTERSTITIAL,
    STRATEGY_OVERSIZED_MEMBER,
    STRATEGY_BLOCK_SPLIT,
    STRATEGY_BLOCK_SPLIT_DEEP,
    STRATEGY_FALLBACK_WINDOW,
)

#: A subsegment cut at a safe control-structure boundary keeps full integrity.
#: One cut at an arbitrary line does not, and must be reported as such.
INTEGRITY_INTACT = "intact"
INTEGRITY_DEGRADED = "degraded"


class CoverageError(Exception):
    """Raised when a segment plan does not account for every source line.

    This is a hard failure, never a warning. A manifest that silently drops
    lines is worse than no manifest, because everything downstream trusts it.
    """


@dataclass
class Segment:
    """One bounded unit of source handed to exactly one extraction agent."""

    segment_id: str
    file: str
    start_line: int
    end_line: int
    strategy: str
    members: list[str] = field(default_factory=list)
    est_tokens: int = 0
    #: True when this segment exceeds budget on its own and must be subdivided
    #: by Layer 4's block splitter before it can be dispatched.
    needs_split: bool = False
    #: Lines this segment deliberately repeats from its predecessor. Overlap is
    #: never implicit: the validator rejects any overlap not declared here.
    overlap_previous: int = 0
    #: Namespace -> class -> member chain for the task packet header.
    context_path: str = ""
    #: Set on subsegments of a member that was too large to stand alone, so an
    #: agent knows it is seeing part of a method rather than the whole of one.
    parent_member: str = ""
    subsegment_index: int = 0
    subsegment_count: int = 0
    #: INTEGRITY_INTACT unless the cut had to fall at an arbitrary line.
    integrity: str = INTEGRITY_INTACT

    @property
    def line_count(self) -> int:
        return self.end_line - self.start_line + 1

    def to_dict(self) -> dict[str, Any]:
        return {
            "segment_id": self.segment_id,
            "start_line": self.start_line,
            "end_line": self.end_line,
            "line_count": self.line_count,
            "strategy": self.strategy,
            "est_tokens": self.est_tokens,
            "needs_split": self.needs_split,
            "overlap_previous": self.overlap_previous,
            "context_path": self.context_path,
            "parent_member": self.parent_member,
            "subsegment_index": self.subsegment_index,
            "subsegment_count": self.subsegment_count,
            "integrity": self.integrity,
            "members": list(self.members),
        }


@dataclass
class SegmentPlan:
    """All segments for one file, in source order."""

    file: str
    total_lines: int
    segments: list[Segment] = field(default_factory=list)
    language: str = ""
    #: Set when structural parsing failed and token windows were used instead.
    degraded: bool = False
    degraded_reason: str = ""

    @property
    def oversized(self) -> list[Segment]:
        return [s for s in self.segments if s.needs_split]

    def to_dict(self) -> dict[str, Any]:
        return {
            "file": self.file,
            "language": self.language,
            "total_lines": self.total_lines,
            "segment_count": len(self.segments),
            "degraded": self.degraded,
            "degraded_reason": self.degraded_reason,
            "segments": [s.to_dict() for s in self.segments],
        }
