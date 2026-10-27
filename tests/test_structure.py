"""Tests for the deterministic structural scanner (Layer 2).

These assert syntactic facts only -- line ranges, nesting, determinism. Nothing
here depends on what the sample code means.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from reforge_cli.scripts.structure import (
    StructuralParseError,
    parse_vbnet,
    parse_vbnet_file,
    strip_noise,
)

FIXTURE = Path(__file__).parent / "fixtures" / "vbnet" / "Sample.vb"


@pytest.fixture(scope="module")
def sample():
    return parse_vbnet_file(FIXTURE)


def unit(smap, name, parent=None):
    """Look up one unit. Names are only unique within a scope, so `parent`
    disambiguates members that an interface and its implementor share."""
    matches = [
        u for u in smap.units if u.name == name and (parent is None or u.parent == parent)
    ]
    assert matches, f"unit {name!r} (parent={parent!r}) not found"
    assert len(matches) == 1, f"unit {name!r} found {len(matches)} times"
    return matches[0]


# --- strip_noise -----------------------------------------------------------

@pytest.mark.parametrize(
    "line,expected",
    [
        ("Dim x As Integer ' comment", "Dim x As Integer"),
        ('Dim s = "End Class"', 'Dim s = ""'),
        ('Dim s = "a ""quoted"" b" : x = 1', 'Dim s = "" : x = 1'),
        ("REM whole line", ""),
        ("x = 1 : REM trailing", "x = 1 :"),
        ("Dim remainder As Integer", "Dim remainder As Integer"),
        ('Dim s = "it' + "'" + 's"', 'Dim s = ""'),
        ("", ""),
    ],
)
def test_strip_noise(line, expected):
    assert strip_noise(line) == expected


# --- structural discovery --------------------------------------------------

def test_containers_discovered(sample):
    assert unit(sample, "Dispatch").type == "namespace"
    assert unit(sample, "Track").type == "class"
    assert unit(sample, "Helpers").type == "module"
    assert unit(sample, "ITrackSource").type == "interface"
    assert unit(sample, "StateOfOnBoard").type == "enum"


def test_ranges_are_valid_and_in_file(sample):
    for u in sample.units:
        assert 1 <= u.start_line <= u.end_line <= sample.total_lines, u


def test_nesting_and_parentage(sample):
    assert unit(sample, "Track").parent == "Dispatch"
    assert unit(sample, "Refresh", "Track").parent == "Track"
    assert unit(sample, "Describe").parent == "Helpers"
    assert unit(sample, "Dispatch").nesting_depth == 0
    assert unit(sample, "Track").nesting_depth == 1
    assert unit(sample, "Refresh", "Track").nesting_depth == 2


def test_enum_range_covers_all_members(sample):
    enum = unit(sample, "StateOfOnBoard")
    text = FIXTURE.read_text().splitlines()[enum.start_line - 1 : enum.end_line]
    body = "\n".join(text)
    for member in ("Inactive", "Active", "InactiveLoggedOn"):
        assert member in body


def test_string_literals_do_not_create_structure(sample):
    # The trap field embeds "End Class", "Public Function Fake()" and "#Region".
    assert not [u for u in sample.units if u.name == "Fake"]
    assert unit(sample, "Track").end_line > unit(sample, "Refresh", "Track").end_line


def test_auto_property_is_body_less(sample):
    label = unit(sample, "Label", "Track")
    assert label.body_less is True
    assert label.start_line == label.end_line


def test_block_property_spans_accessors(sample):
    prop = unit(sample, "Id", "Track")
    assert prop.body_less is False
    assert prop.line_count > 5


def test_declare_and_mustoverride_are_body_less(sample):
    assert unit(sample, "GetTickCount").body_less is True
    assert unit(sample, "AbstractOp").body_less is True
    assert unit(sample, "Changed").body_less is True


def test_interface_members_are_body_less(sample):
    get_id_decls = [u for u in sample.units if u.name == "GetId"]
    assert len(get_id_decls) == 2
    in_interface = [u for u in get_id_decls if u.parent == "ITrackSource"][0]
    in_class = [u for u in get_id_decls if u.parent == "Track"][0]
    assert in_interface.body_less is True
    assert in_class.body_less is False


def test_line_continuation_joined(sample):
    # TrackTrainIDOn's signature spans two physical lines; the unit must start
    # at the first of them.
    method = unit(sample, "TrackTrainIDOn", "Track")
    first = FIXTURE.read_text().splitlines()[method.start_line - 1]
    assert "TrackTrainIDOn" in first
    assert method.line_count > 5


def test_regions_tracked_and_excluded_from_leaves(sample):
    regions = [u for u in sample.units if u.type == "region"]
    assert {r.name for r in regions} == {"Fields", "Members"}
    assert all(r.end_line > r.start_line for r in regions)
    assert all(leaf.type != "region" for leaf in sample.leaves())


def test_leaves_are_ordered_members_only(sample):
    leaves = sample.leaves()
    assert leaves == sorted(leaves, key=lambda u: (u.start_line, u.end_line))
    assert all(u.type in ("sub", "function", "property", "operator", "event") for u in leaves)
    assert {"Refresh", "TrackTrainIDOn", "Describe"} <= {u.name for u in leaves}


# --- determinism -----------------------------------------------------------

def test_parsing_is_deterministic():
    source = FIXTURE.read_text()
    first = parse_vbnet(source, "Sample.vb").to_dict()
    second = parse_vbnet(source, "Sample.vb").to_dict()
    assert first == second


def test_crlf_and_lf_agree():
    source = FIXTURE.read_text()
    lf = parse_vbnet(source.replace("\r\n", "\n"), "Sample.vb").to_dict()
    crlf = parse_vbnet(source.replace("\r\n", "\n").replace("\n", "\r\n"), "Sample.vb").to_dict()
    assert lf == crlf


# --- failure signals the fallback -----------------------------------------

def test_unterminated_construct_raises():
    with pytest.raises(StructuralParseError) as exc:
        parse_vbnet("Public Class Orphan\n    Public Sub A()\n    End Sub\n", "x.vb")
    assert "unterminated" in str(exc.value)


def test_mismatched_end_raises():
    with pytest.raises(StructuralParseError) as exc:
        parse_vbnet("Public Class A\n    Public Sub B()\n    End Function\nEnd Class\n", "x.vb")
    assert "does not match" in str(exc.value)


def test_stray_end_raises():
    with pytest.raises(StructuralParseError):
        parse_vbnet("End Class\n", "x.vb")


def test_unterminated_region_is_tolerated():
    smap = parse_vbnet('#Region "R"\nPublic Class A\nEnd Class\n', "x.vb")
    region = [u for u in smap.units if u.type == "region"][0]
    assert region.end_line == smap.total_lines


def test_empty_source():
    smap = parse_vbnet("", "empty.vb")
    assert smap.units == []
    assert smap.total_lines == 0
