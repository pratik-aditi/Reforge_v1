"""Tests for the coverage validator and segment manifest (Layer 5).

Every check in the validator is a hard failure, so each one gets a test that
proves it actually fires. A validator that cannot fail is decoration.
"""

from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

import pytest

from reforge_cli.scripts.segmentation import (
    Budget,
    CoverageError,
    Segment,
    assert_valid,
    build_manifest,
    config_hash,
    file_hash,
    is_stale,
    load_manifest,
    manifest_path,
    plan_segments,
    plan_token_windows,
    validate_plan,
    write_manifest,
)
from reforge_cli.scripts.structure import parse_vbnet

FIXTURE = Path(__file__).parent / "fixtures" / "vbnet" / "Sample.vb"
BUDGET = Budget(target_tokens=1500, max_tokens=2500, max_lines=400)


def synthetic(method_count: int, body_lines: int) -> str:
    out = ["Namespace Gen", "    Public Class Big"]
    for i in range(method_count):
        out.append(f"        Public Sub Method{i:03d}()")
        for j in range(body_lines):
            out.append(f"            Dim v{j} As Integer = {j} + {i}")
        out.append("        End Sub")
    out += ["    End Class", "End Namespace"]
    return "\n".join(out)


def built(source: str, budget: Budget = BUDGET):
    smap = parse_vbnet(source, "Sample.vb")
    return smap, plan_segments(smap, source.splitlines(), budget)


# --- the happy path --------------------------------------------------------

def test_valid_plan_passes():
    smap, plan = built(synthetic(40, 15))
    report = validate_plan(plan, smap)
    assert report.ok, report.errors
    assert report.coverage_pct == 100.0
    assert report.members_assigned == report.members_total > 0


def test_whole_file_plan_passes():
    source = FIXTURE.read_text()
    smap, plan = built(source)
    assert validate_plan(plan, smap).ok


def test_empty_file_passes():
    smap, plan = built("")
    report = validate_plan(plan, smap)
    assert report.ok
    assert report.coverage_pct == 100.0


# --- each failure mode actually fires -------------------------------------

def test_missing_start_is_detected():
    smap, plan = built(synthetic(20, 15))
    plan.segments = plan.segments[1:]
    errors = validate_plan(plan, smap).errors
    assert any("not 1" in e for e in errors)


def test_missing_end_is_detected():
    smap, plan = built(synthetic(20, 15))
    plan.segments = plan.segments[:-1]
    errors = validate_plan(plan, smap).errors
    assert any("end of source not covered" in e for e in errors)


def test_interior_gap_is_detected():
    smap, plan = built(synthetic(20, 15))
    assert len(plan.segments) >= 3
    del plan.segments[1]
    errors = validate_plan(plan, smap).errors
    assert any("silent gap" in e for e in errors)


def test_undeclared_overlap_is_rejected():
    smap, plan = built(synthetic(20, 15))
    plan.segments[1].start_line -= 3  # overlap without declaring it
    errors = validate_plan(plan, smap).errors
    assert any("undeclared overlap" in e for e in errors)


def test_declared_overlap_is_accepted():
    smap, plan = built(synthetic(20, 15))
    # Overlap extends the start backwards; the id keeps anchoring to the first
    # exclusively-owned line, so it must not change.
    plan.segments[1].start_line -= 3
    plan.segments[1].overlap_previous = 3
    report = validate_plan(plan, smap)
    assert report.ok, report.errors
    assert report.declared_overlap_lines == 3


def test_out_of_order_segments_are_detected():
    smap, plan = built(synthetic(20, 15))
    plan.segments[0], plan.segments[1] = plan.segments[1], plan.segments[0]
    assert any("source order" in e for e in validate_plan(plan, smap).errors)


def test_duplicate_ids_are_detected():
    smap, plan = built(synthetic(20, 15))
    plan.segments[1].segment_id = plan.segments[0].segment_id
    assert any("duplicate segment id" in e for e in validate_plan(plan, smap).errors)


def test_id_not_derived_from_anchor_is_detected():
    smap, plan = built(synthetic(20, 15))
    plan.segments[0].segment_id = "hand-written-id"
    errors = validate_plan(plan, smap).errors
    assert any("not derived from its anchor line" in e for e in errors)


def test_overlap_does_not_change_segment_identity():
    """Changing the overlap setting must not renumber segments."""
    lines = [f"line {i}" for i in range(1, 301)]
    budget = Budget(target_tokens=300, max_tokens=600, max_lines=50)
    plain = plan_token_windows("Weird.vb", lines, budget)
    lapped = plan_token_windows("Weird.vb", lines, budget, overlap_lines=5)
    assert [s.segment_id for s in plain.segments] == [
        s.segment_id for s in lapped.segments
    ]


def test_range_beyond_end_of_file_is_detected():
    smap, plan = built(synthetic(20, 15))
    plan.segments[-1].end_line += 50
    assert any("exceeds file length" in e for e in validate_plan(plan, smap).errors)


def test_inverted_range_is_detected():
    smap, plan = built(synthetic(20, 15))
    plan.segments[0] = replace(plan.segments[0], start_line=10, end_line=2)
    assert any("inverted range" in e for e in validate_plan(plan, smap).errors)


def test_member_missing_from_member_list_is_detected():
    """The check that contiguity alone cannot make -- see Layer 3 notes."""
    smap, plan = built(synthetic(20, 15))
    dropped = plan.segments[1].members.pop()
    errors = validate_plan(plan, smap).errors
    assert any(dropped in e and "missing from its member list" in e for e in errors)


def test_member_in_no_segment_is_detected():
    smap, plan = built(synthetic(20, 15))
    # Shrink the plan so the final members fall outside every segment, then
    # restore end coverage with a segment that lists nothing.
    plan.segments = plan.segments[:1]
    plan.segments[0].end_line = plan.total_lines
    plan.segments[0].members = []
    errors = validate_plan(plan, smap).errors
    assert any("missing from its member list" in e or "is in no segment" in e for e in errors)


def test_assert_valid_raises():
    smap, plan = built(synthetic(20, 15))
    plan.segments = plan.segments[1:]
    with pytest.raises(CoverageError):
        assert_valid(plan, smap)


def test_validator_without_structural_map_skips_member_checks():
    lines = [f"line {i}" for i in range(1, 301)]
    plan = plan_token_windows("Weird.vb", lines, Budget(target_tokens=300, max_tokens=600, max_lines=50))
    report = validate_plan(plan)
    assert report.ok, report.errors
    assert report.members_total == 0


def test_fallback_overlap_is_declared_and_accepted():
    lines = [f"line {i}" for i in range(1, 301)]
    plan = plan_token_windows(
        "Weird.vb",
        lines,
        Budget(target_tokens=300, max_tokens=600, max_lines=50),
        overlap_lines=5,
    )
    report = validate_plan(plan)
    assert report.ok, report.errors
    assert report.declared_overlap_lines > 0


# --- manifest --------------------------------------------------------------

def test_manifest_contains_identity_and_segments():
    source = synthetic(40, 15)
    smap, plan = built(source)
    manifest = build_manifest(plan, source.encode(), BUDGET, smap)
    assert manifest["file_hash"] == file_hash(source.encode())
    assert manifest["config_hash"] == config_hash(BUDGET)
    assert manifest["generator_version"]
    assert manifest["total_lines"] == plan.total_lines
    assert len(manifest["segments"]) == len(plan.segments)
    assert manifest["coverage"]["ok"] is True


def test_manifest_refuses_to_build_from_an_invalid_plan():
    source = synthetic(20, 15)
    smap, plan = built(source)
    plan.segments = plan.segments[1:]
    with pytest.raises(CoverageError):
        build_manifest(plan, source.encode(), BUDGET, smap)


def test_manifest_is_byte_identical_across_runs(tmp_path):
    source = synthetic(40, 15)
    outputs = []
    for name in ("a.json", "b.json"):
        smap, plan = built(source)
        manifest = build_manifest(plan, source.encode(), BUDGET, smap)
        outputs.append(write_manifest(manifest, tmp_path / name).read_bytes())
    assert outputs[0] == outputs[1]


def test_manifest_roundtrips(tmp_path):
    source = synthetic(40, 15)
    smap, plan = built(source)
    manifest = build_manifest(plan, source.encode(), BUDGET, smap)
    path = write_manifest(manifest, tmp_path / "m.json")
    assert load_manifest(path) == manifest
    assert json.loads(path.read_text())["file"] == "Sample.vb"


def test_staleness_detects_changed_source_and_config():
    source = synthetic(40, 15)
    smap, plan = built(source)
    manifest = build_manifest(plan, source.encode(), BUDGET, smap)
    assert is_stale(manifest, source.encode(), BUDGET) is False
    assert is_stale(manifest, (source + "\n' edit").encode(), BUDGET) is True
    assert is_stale(manifest, source.encode(), Budget(target_tokens=99, max_tokens=99)) is True


def test_manifest_path_layout(tmp_path):
    path = manifest_path(tmp_path, "src/legacy/Track.vb")
    assert path.parent.name == "segments"
    assert path.name == "Track.vb.segments.json"
