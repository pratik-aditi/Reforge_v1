"""Tests for the oversized-member splitter (Layer 4).

The load-bearing property is that every cut lands on a safe control-structure
boundary. A cut inside an `If` produces a condition with no consequence, and
any rule extracted from that fragment is fiction.
"""

from __future__ import annotations

import pytest

from reforge_cli.scripts.segmentation import (
    INTEGRITY_DEGRADED,
    INTEGRITY_INTACT,
    STRATEGY_BLOCK_SPLIT,
    STRATEGY_BLOCK_SPLIT_DEEP,
    Budget,
    apply_splits,
    plan_segments,
    split_segment,
    top_level_boundaries,
    validate_plan,
)
from reforge_cli.scripts.structure import parse_vbnet

TIGHT = Budget(target_tokens=400, max_tokens=700, max_lines=60)


def monster(block_count: int, block_body: int, kind: str = "if") -> str:
    """A single method made of many complete top-level control structures."""
    body: list[str] = []
    for i in range(block_count):
        if kind == "if":
            body.append(f"            If value = {i} Then")
            body += [f"                Dim a{j} As Integer = {j}" for j in range(block_body)]
            body.append("            End If")
        elif kind == "select":
            body.append(f"            Select Case value + {i}")
            body.append("                Case 0")
            body += [f"                    Dim b{j} As Integer = {j}" for j in range(block_body)]
            body.append("                Case Else")
            body.append("                    Exit Select")
            body.append("            End Select")
        elif kind == "try":
            body.append("            Try")
            body += [f"                Dim c{j} As Integer = {j}" for j in range(block_body)]
            body.append("            Catch ex As Exception")
            body.append("                Throw")
            body.append("            Finally")
            body.append("                Reset()")
            body.append("            End Try")
        elif kind == "mixed":
            body.append(f"            For idx = 0 To {i}")
            body.append("                While idx > 0")
            body += [f"                    Dim d{j} As Integer = {j}" for j in range(block_body)]
            body.append("                End While")
            body.append("            Next")
            body.append("            Using res = Acquire()")
            body.append("                With res")
            body.append("                    .Touch()")
            body.append("                End With")
            body.append("            End Using")
    return "\n".join(
        ["Namespace Gen", "    Public Class Big", "        Public Sub Huge(value As Integer)"]
        + body
        + ["        End Sub", "    End Class", "End Namespace"]
    )


def planned(source: str, budget: Budget = TIGHT):
    smap = parse_vbnet(source, "Mon.vb")
    lines = source.splitlines()
    return smap, plan_segments(smap, lines, budget), lines


def is_block_edge(line: str) -> bool:
    head = line.strip().lower()
    return head.startswith(
        ("if ", "select case", "try", "for ", "for each", "do", "while ", "using ", "with ", "synclock")
    )


def assert_tiles(parent_start, parent_end, subs):
    assert subs[0].start_line == parent_start
    assert subs[-1].end_line == parent_end
    for previous, following in zip(subs, subs[1:]):
        assert following.start_line == previous.end_line + 1


# --- boundary discovery ----------------------------------------------------

def test_single_line_if_is_not_a_block():
    lines = [
        "Dim x As Integer = 1",
        "If x = 1 Then DoThing()",
        "Dim y As Integer = 2",
    ]
    assert top_level_boundaries(lines, 1, 3) == [1, 2, 3]


def test_block_if_suppresses_interior_boundaries():
    lines = [
        "Dim x As Integer = 1",
        "If x = 1 Then",
        "    DoThing()",
        "    DoOther()",
        "End If",
        "Dim y As Integer = 2",
    ]
    assert top_level_boundaries(lines, 1, 6) == [1, 2, 6]


def test_else_and_elseif_are_not_boundaries():
    lines = [
        "If x = 1 Then",
        "    A()",
        "ElseIf x = 2 Then",
        "    B()",
        "Else",
        "    C()",
        "End If",
        "Tail()",
    ]
    assert top_level_boundaries(lines, 1, 8) == [1, 8]


def test_catch_and_finally_are_not_boundaries():
    lines = [
        "Try",
        "    A()",
        "Catch ex As Exception",
        "    B()",
        "Finally",
        "    C()",
        "End Try",
        "Tail()",
    ]
    assert top_level_boundaries(lines, 1, 8) == [1, 8]


@pytest.mark.parametrize(
    "opener,closer",
    [
        ("Select Case v", "End Select"),
        ("For i = 1 To 10", "Next"),
        ("For Each item In list", "Next"),
        ("While active", "End While"),
        ("Do", "Loop"),
        ("Using res = Acquire()", "End Using"),
        ("With obj", "End With"),
        ("SyncLock gate", "End SyncLock"),
    ],
)
def test_each_control_structure_is_recognised(opener, closer):
    lines = ["Head()", opener, "    Inner()", closer, "Tail()"]
    assert top_level_boundaries(lines, 1, 5) == [1, 2, 5]


def test_nested_blocks_only_cut_at_top_level():
    lines = [
        "If a Then",
        "    For i = 1 To 3",
        "        While b",
        "            X()",
        "        End While",
        "    Next",
        "End If",
        "Tail()",
    ]
    assert top_level_boundaries(lines, 1, 8) == [1, 8]


# --- splitting -------------------------------------------------------------

@pytest.mark.parametrize("kind", ["if", "select", "try", "mixed"])
def test_split_cuts_only_at_safe_boundaries(kind):
    source = monster(12, 8, kind)
    smap, plan, lines = planned(source)
    oversized = [s for s in plan.segments if s.needs_split]
    assert oversized, "fixture did not produce an oversized member"

    subs = split_segment(oversized[0], lines, TIGHT)
    assert len(subs) > 1
    assert_tiles(oversized[0].start_line, oversized[0].end_line, subs)

    for sub in subs[1:]:
        if sub.integrity == INTEGRITY_DEGRADED:
            continue
        first = lines[sub.start_line - 1]
        # Every intact cut begins a complete statement, never a continuation.
        assert not first.strip().lower().startswith(
            ("else", "elseif", "case ", "catch", "finally", "end ", "next", "loop")
        )


def test_subsegments_carry_parent_and_index():
    source = monster(12, 8)
    smap, plan, lines = planned(source)
    oversized = [s for s in plan.segments if s.needs_split][0]
    subs = split_segment(oversized, lines, TIGHT)
    assert all(s.parent_member == "Huge" for s in subs)
    assert [s.subsegment_index for s in subs] == list(range(1, len(subs) + 1))
    assert all(s.subsegment_count == len(subs) for s in subs)
    assert all(s.strategy in (STRATEGY_BLOCK_SPLIT, STRATEGY_BLOCK_SPLIT_DEEP) for s in subs)


def test_subsegments_clear_needs_split():
    source = monster(12, 8)
    smap, plan, lines = planned(source)
    oversized = [s for s in plan.segments if s.needs_split][0]
    assert all(not s.needs_split for s in split_segment(oversized, lines, TIGHT))


def test_non_oversized_segment_is_returned_unchanged():
    source = monster(2, 2)
    smap, plan, lines = planned(source, Budget())
    segment = plan.segments[0]
    assert split_segment(segment, lines, Budget()) == [segment]


def test_a_single_huge_block_is_deep_split_not_degraded():
    """A 400-line If still has safe depth-1 statement boundaries inside it."""
    body = ["            If value = 1 Then"]
    body += [f"                Dim a{j} As Integer = {j}" for j in range(400)]
    body.append("            End If")
    source = "
".join(
        ["Namespace Gen", "    Public Class Big", "        Public Sub Huge(value As Integer)"]
        + body
        + ["        End Sub", "    End Class", "End Namespace"]
    )
    smap, plan, lines = planned(source)
    oversized = [s for s in plan.segments if s.needs_split][0]
    subs = split_segment(oversized, lines, TIGHT)
    assert len(subs) > 1
    assert any(s.strategy == STRATEGY_BLOCK_SPLIT_DEEP for s in subs)
    assert all(s.integrity == INTEGRITY_INTACT for s in subs)
    assert_tiles(oversized.start_line, oversized.end_line, subs)


def test_continued_statement_is_never_cut():
    """A statement spanning `_` continuations has no interior cut point."""
    lines = [
        "Dim total As Integer = 0 + _",
        "    1 + _",
        "    2 + _",
        "    3",
        "Tail()",
    ]
    assert top_level_boundaries(lines, 1, 5) == [1, 5]


def test_unsplittable_statement_degrades_visibly():
    """One statement longer than the budget cannot be cut safely at all."""
    body = ["            Dim total As Integer = 0 + _"]
    body += ["                1 + _" for _ in range(398)]
    body.append("                1")
    source = "
".join(
        ["Namespace Gen", "    Public Class Big", "        Public Sub Huge(value As Integer)"]
        + body
        + ["        End Sub", "    End Class", "End Namespace"]
    )
    smap, plan, lines = planned(source)
    oversized = [s for s in plan.segments if s.needs_split][0]
    subs = split_segment(oversized, lines, TIGHT)
    assert len(subs) > 1
    assert any(s.integrity == INTEGRITY_DEGRADED for s in subs)
    assert_tiles(oversized.start_line, oversized.end_line, subs)


def test_deep_split_used_before_degrading():
    """Nested blocks let the splitter recurse rather than cut arbitrarily."""
    body = ["            If value = 1 Then"]
    for i in range(14):
        body.append(f"                If value = {i} Then")
        body += [f"                    Dim a{j} As Integer = {j}" for j in range(8)]
        body.append("                End If")
    body.append("            End If")
    source = "\n".join(
        ["Namespace Gen", "    Public Class Big", "        Public Sub Huge(value As Integer)"]
        + body
        + ["        End Sub", "    End Class", "End Namespace"]
    )
    smap, plan, lines = planned(source)
    oversized = [s for s in plan.segments if s.needs_split][0]
    subs = split_segment(oversized, lines, TIGHT)
    assert any(s.strategy == STRATEGY_BLOCK_SPLIT_DEEP for s in subs)
    assert any(s.integrity == INTEGRITY_INTACT for s in subs)


# --- integration with the plan and validator ------------------------------

def test_apply_splits_keeps_the_plan_valid():
    source = monster(14, 8)
    smap, plan, lines = planned(source)
    assert plan.oversized
    apply_splits(plan, lines, TIGHT)
    assert not plan.oversized
    report = validate_plan(plan, smap)
    assert report.ok, report.errors
    assert report.coverage_pct == 100.0


def test_split_respects_the_budget_where_it_can():
    source = monster(20, 6)
    smap, plan, lines = planned(source)
    apply_splits(plan, lines, TIGHT)
    for segment in plan.segments:
        if segment.integrity == INTEGRITY_DEGRADED:
            continue
        assert segment.line_count <= TIGHT.max_lines


def test_splitting_is_deterministic():
    source = monster(14, 8)
    first = planned(source)
    second = planned(source)
    apply_splits(first[1], first[2], TIGHT)
    apply_splits(second[1], second[2], TIGHT)
    assert first[1].to_dict() == second[1].to_dict()
