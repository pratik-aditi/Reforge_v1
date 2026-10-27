"""Tests for the segment planner (Layer 3).

The load-bearing assertions are the coverage ones: every line of every file is
claimed by exactly one segment. Everything else is packing quality.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from reforge_cli.scripts.segmentation import (
    STRATEGY_FALLBACK_WINDOW,
    STRATEGY_MEMBER_PACK,
    STRATEGY_OVERSIZED_MEMBER,
    STRATEGY_WHOLE_FILE,
    Budget,
    CoverageError,
    estimate_tokens,
    plan_segments,
    plan_token_windows,
)
from reforge_cli.scripts.structure import parse_vbnet

FIXTURE = Path(__file__).parent / "fixtures" / "vbnet" / "Sample.vb"


def build(source: str, budget: Budget | None = None):
    smap = parse_vbnet(source, "Sample.vb")
    return plan_segments(smap, source.splitlines(), budget)


def synthetic(method_count: int, body_lines: int) -> str:
    """A VB.NET file with predictable, controllable member sizes."""
    out = ["Namespace Gen", "    Public Class Big"]
    for i in range(method_count):
        out.append(f"        Public Sub Method{i:03d}()")
        for j in range(body_lines):
            out.append(f"            Dim v{j} As Integer = {j} + {i}")
        out.append("        End Sub")
    out.append("    End Class")
    out.append("End Namespace")
    return "\n".join(out)


def assert_full_coverage(plan):
    """The mandatory invariant: line 1 to the final line, no silent gap."""
    assert plan.segments, "no segments"
    assert plan.segments[0].start_line == 1
    assert plan.segments[-1].end_line == plan.total_lines
    covered = set()
    for segment in plan.segments:
        assert segment.start_line <= segment.end_line
        span = set(range(segment.start_line, segment.end_line + 1))
        assert not (covered & span), f"overlap at {segment.segment_id}"
        covered |= span
    assert covered == set(range(1, plan.total_lines + 1))


# --- token estimation ------------------------------------------------------

def test_estimate_tokens_is_monotonic_and_deterministic():
    assert estimate_tokens("") == 0
    small, large = "x" * 100, "x" * 1000
    assert estimate_tokens(small) < estimate_tokens(large)
    assert estimate_tokens(large) == estimate_tokens(large)


def test_budget_rejects_inconsistent_limits():
    with pytest.raises(ValueError):
        Budget(target_tokens=9000, max_tokens=100)
    with pytest.raises(ValueError):
        Budget(target_tokens=0)


# --- small file: keep whole ------------------------------------------------

def test_small_file_kept_whole():
    source = FIXTURE.read_text()
    plan = build(source)
    assert len(plan.segments) == 1
    assert plan.segments[0].strategy == STRATEGY_WHOLE_FILE
    assert_full_coverage(plan)


def test_empty_file_yields_no_segments():
    plan = build("")
    assert plan.segments == []
    assert plan.total_lines == 0


# --- large file: member packing -------------------------------------------

def test_large_file_is_packed_into_many_segments():
    source = synthetic(method_count=60, body_lines=20)
    plan = build(source, Budget(target_tokens=1500, max_tokens=2500, max_lines=400))
    assert len(plan.segments) > 3
    assert_full_coverage(plan)
    assert any(s.strategy == STRATEGY_MEMBER_PACK for s in plan.segments)


def test_members_are_never_split_when_they_fit():
    source = synthetic(method_count=40, body_lines=15)
    budget = Budget(target_tokens=1500, max_tokens=2500, max_lines=400)
    smap = parse_vbnet(source, "Sample.vb")
    plan = plan_segments(smap, source.splitlines(), budget)
    for member in smap.leaves():
        holders = [
            s
            for s in plan.segments
            if s.start_line <= member.start_line and member.end_line <= s.end_line
        ]
        assert len(holders) == 1, f"{member.name} is not wholly inside one segment"


def test_every_member_is_assigned_to_a_segment():
    source = synthetic(method_count=40, body_lines=15)
    budget = Budget(target_tokens=1500, max_tokens=2500, max_lines=400)
    smap = parse_vbnet(source, "Sample.vb")
    plan = plan_segments(smap, source.splitlines(), budget)
    assigned = {name for s in plan.segments for name in s.members}
    for member in smap.leaves():
        assert member.name in assigned


def test_segments_respect_the_max_budget():
    source = synthetic(method_count=60, body_lines=20)
    budget = Budget(target_tokens=1500, max_tokens=2500, max_lines=400)
    plan = build(source, budget)
    for segment in plan.segments:
        if segment.needs_split:
            continue
        assert segment.est_tokens <= budget.max_tokens
        assert segment.line_count <= budget.max_lines


def test_interstitial_source_is_captured():
    # Namespace/class headers precede the first member and must be covered.
    source = synthetic(method_count=30, body_lines=20)
    plan = build(source, Budget(target_tokens=1200, max_tokens=2000, max_lines=300))
    assert plan.segments[0].start_line == 1
    assert_full_coverage(plan)


# --- oversized members -----------------------------------------------------

def test_oversized_member_is_tagged_not_split():
    source = synthetic(method_count=3, body_lines=400)
    budget = Budget(target_tokens=1000, max_tokens=1500, max_lines=200)
    plan = build(source, budget)
    oversized = plan.oversized
    assert oversized, "expected at least one oversized member"
    assert any(s.strategy == STRATEGY_OVERSIZED_MEMBER for s in oversized)
    assert_full_coverage(plan)
    # Layer 3 tags; Layer 4 splits. The member is still intact here.
    for segment in oversized:
        assert segment.needs_split is True


def test_context_path_is_recorded():
    source = synthetic(method_count=30, body_lines=20)
    plan = build(source, Budget(target_tokens=1200, max_tokens=2000, max_lines=300))
    mid = plan.segments[len(plan.segments) // 2]
    assert "Gen" in mid.context_path


# --- identifiers and determinism ------------------------------------------

def test_segment_ids_are_unique_and_start_line_derived():
    source = synthetic(method_count=40, body_lines=15)
    plan = build(source, Budget(target_tokens=1500, max_tokens=2500, max_lines=400))
    ids = [s.segment_id for s in plan.segments]
    assert len(ids) == len(set(ids))
    for segment in plan.segments:
        assert segment.segment_id.endswith(f"{segment.start_line:06d}")


def test_planning_is_deterministic():
    source = synthetic(method_count=40, body_lines=15)
    budget = Budget(target_tokens=1500, max_tokens=2500, max_lines=400)
    assert build(source, budget).to_dict() == build(source, budget).to_dict()


def test_trailing_edit_does_not_renumber_earlier_segments():
    """IDs come from start lines, not a counter, so appending a method must
    leave the identifiers of earlier segments untouched."""
    budget = Budget(target_tokens=1500, max_tokens=2500, max_lines=400)
    before = build(synthetic(method_count=40, body_lines=15), budget)
    after = build(synthetic(method_count=41, body_lines=15), budget)
    shared = min(len(before.segments), len(after.segments)) - 1
    assert [s.segment_id for s in before.segments[:shared]] == [
        s.segment_id for s in after.segments[:shared]
    ]


# --- fallback --------------------------------------------------------------

def test_fallback_windows_cover_everything():
    lines = [f"line {i}" for i in range(1, 501)]
    plan = plan_token_windows(
        "Weird.vb", lines, Budget(target_tokens=300, max_tokens=600, max_lines=50)
    )
    assert plan.degraded is True
    assert plan.degraded_reason
    assert all(s.strategy == STRATEGY_FALLBACK_WINDOW for s in plan.segments)
    covered = set()
    for segment in plan.segments:
        covered |= set(range(segment.start_line, segment.end_line + 1))
    assert covered == set(range(1, 501))


def test_fallback_overlap_still_covers_everything():
    lines = [f"line {i}" for i in range(1, 501)]
    plan = plan_token_windows(
        "Weird.vb",
        lines,
        Budget(target_tokens=300, max_tokens=600, max_lines=50),
        overlap_lines=5,
    )
    covered = set()
    for segment in plan.segments:
        covered |= set(range(segment.start_line, segment.end_line + 1))
    assert covered == set(range(1, 501))


def test_fallback_on_empty_file():
    plan = plan_token_windows("Weird.vb", [])
    assert plan.segments == []


# --- the coverage invariant is enforced, not advisory ---------------------

TIGHT = Budget(target_tokens=200, max_tokens=400, max_lines=40)


def _plan_with_atoms(monkeypatch, drop):
    """Run the planner with a deliberately broken atom tiling."""
    from reforge_cli.scripts.segmentation import planner

    source = synthetic(method_count=10, body_lines=10)
    smap = parse_vbnet(source, "Sample.vb")
    original = planner._atoms
    monkeypatch.setattr(planner, "_atoms", lambda m: drop(original(m)))
    return planner.plan_segments(smap, source.splitlines(), TIGHT)


def test_coverage_error_when_the_start_is_missing(monkeypatch):
    with pytest.raises(CoverageError, match="not 1"):
        _plan_with_atoms(monkeypatch, lambda spans: spans[1:])


def test_coverage_error_when_the_end_is_missing(monkeypatch):
    with pytest.raises(CoverageError, match="expected"):
        _plan_with_atoms(monkeypatch, lambda spans: spans[:-1])


def test_interior_atom_loss_cannot_lose_lines(monkeypatch):
    """A dropped interior atom is absorbed by the surrounding segment.

    Packing takes a segment's bounds from the first and last atom it holds, so
    a missing atom in the middle cannot open a line gap -- the enclosing
    segment still covers those lines. Coverage therefore holds, but contiguity
    alone cannot *detect* the loss: the member would silently be dropped from
    the segment's `members` list while its source is still handed to an agent.

    Catching that needs the member-assignment check, which belongs to Layer 5's
    full validator. This test pins the current guarantee so the gap in it stays
    visible.
    """
    plan = _plan_with_atoms(monkeypatch, lambda spans: spans[:1] + spans[2:])
    assert_full_coverage(plan)
