"""Data model for deterministic structural discovery.

A StructuralUnit is a purely syntactic fact about a source file: what kind of
construct it is, what it is called, and the exact line range it occupies. It
carries no interpretation of what the code means -- that remains with the LLM.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

# Unit kinds, in the order declared by reforge-update.txt.
CONTAINER_KINDS = ("namespace", "class", "module", "interface", "structure", "enum")
MEMBER_KINDS = ("sub", "function", "property", "operator", "event")
REGION_KIND = "region"

#: Kinds that hold extractable statements. Used by the segment planner (Layer 3)
#: to select leaf units for packing.
LEAF_KINDS = MEMBER_KINDS


class StructuralParseError(Exception):
    """Raised when a file cannot be parsed deterministically.

    Triggers the Layer 6 fallback to deterministic token windows. Carries the
    line number so the fallback can be reported precisely.
    """

    def __init__(self, message: str, file: str = "", line: int = 0) -> None:
        self.file = file
        self.line = line
        location = f"{file}:{line}: " if file else ""
        super().__init__(f"{location}{message}")


@dataclass
class StructuralUnit:
    """One syntactic construct with an exact, inclusive line range."""

    type: str
    name: str
    file: str
    start_line: int
    end_line: int
    parent: str | None = None
    nesting_depth: int = 0
    signature_line: str = ""
    #: True when the construct has no body (interface member, MustOverride,
    #: Declare, Delegate, auto-implemented property). Such units occupy a
    #: single line and are never split.
    body_less: bool = False

    @property
    def line_count(self) -> int:
        return self.end_line - self.start_line + 1

    def to_dict(self) -> dict[str, Any]:
        """Serialize in the field order used by the segment manifest."""
        return {
            "type": self.type,
            "name": self.name,
            "file": self.file,
            "start_line": self.start_line,
            "end_line": self.end_line,
            "parent": self.parent,
            "nesting_depth": self.nesting_depth,
            "signature_line": self.signature_line,
            "body_less": self.body_less,
        }


@dataclass
class StructuralMap:
    """All structural units discovered in one file, plus file-level facts."""

    file: str
    total_lines: int
    units: list[StructuralUnit] = field(default_factory=list)
    language: str = ""

    def leaves(self) -> list[StructuralUnit]:
        """Member-level units, ordered by position.

        These are what Layer 3 packs into segments. Containers are excluded to
        avoid double-counting their nested members.
        """
        return sorted(
            (u for u in self.units if u.type in LEAF_KINDS),
            key=lambda u: (u.start_line, u.end_line),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "file": self.file,
            "language": self.language,
            "total_lines": self.total_lines,
            "unit_count": len(self.units),
            "units": [u.to_dict() for u in self.units],
        }
