"""Deterministic structural scanner for VB.NET.

Approach (see design/deterministic-source-layer/): a line-oriented state machine,
not regex over raw text and not Roslyn.

  * Raw regex is unsafe: `End Function` inside a string literal or comment would
    close a frame that was never opened.
  * Roslyn is rejected: it adds a .NET runtime dependency and generalizes to no
    other legacy language Reforge targets.

So each physical line is first reduced to code-only text (string literals and
comments removed, continuations joined), and only then matched against anchored
declaration patterns. VB.NET is line-structured, which makes this reliable and
cheap, and the same skeleton ports to other languages one module at a time.

Guarantees: same bytes in, same units out. No interpretation of meaning.
"""

from __future__ import annotations

import re
from pathlib import Path

from .models import StructuralMap, StructuralParseError, StructuralUnit

LANGUAGE = "vbnet"

# Modifiers that may precede a declaration keyword. Anchored matching against
# this set is what prevents `Dim f As Func(Of Integer)` being read as a Function.
_MODIFIERS = (
    "public|private|protected|friend|shared|static|partial|mustinherit|"
    "notinheritable|notoverridable|overridable|overrides|overloads|shadows|"
    "mustoverride|default|readonly|writeonly|withevents|async|iterator|"
    "narrowing|widening|custom|global"
)

_MOD_PREFIX = rf"(?:(?:{_MODIFIERS})\s+)*"

_RE_CONTAINER = re.compile(
    rf"^{_MOD_PREFIX}(?P<kw>namespace|class|module|interface|structure|enum)\s+"
    rf"(?P<name>\[?[A-Za-z_][A-Za-z0-9_]*\]?)",
    re.IGNORECASE,
)

_RE_MEMBER = re.compile(
    rf"^{_MOD_PREFIX}(?P<kw>sub|function|property|operator|event)\s+"
    rf"(?P<name>\[?[A-Za-z_][A-Za-z0-9_]*\]?)",
    re.IGNORECASE,
)

# Declarations that never open a body.
_RE_DECLARE = re.compile(rf"^{_MOD_PREFIX}(?:declare|delegate)\s+", re.IGNORECASE)
_RE_MUSTOVERRIDE = re.compile(rf"^{_MOD_PREFIX}mustoverride\s+", re.IGNORECASE)

# Unanchored name lookup for body-less forms, where the declaration keyword is
# preceded by words that are not modifiers (`Declare Function`, `Delegate Sub`).
_RE_DECLARED_NAME = re.compile(
    r"\b(?P<kw>sub|function|property|operator|event)\s+"
    r"(?P<name>\[?[A-Za-z_][A-Za-z0-9_]*\]?)",
    re.IGNORECASE,
)

_RE_END = re.compile(
    r"^end\s+(?P<kw>namespace|class|module|interface|structure|enum|sub|function|"
    r"property|operator|event|get|set|addhandler|removehandler|raiseevent)\b",
    re.IGNORECASE,
)

_RE_ACCESSOR = re.compile(
    r"^(?:public\s+|private\s+|protected\s+|friend\s+)?"
    r"(?P<kw>get|set|addhandler|removehandler|raiseevent)\b\s*(?:\(|$)",
    re.IGNORECASE,
)

_RE_REGION = re.compile(r"^#region\b", re.IGNORECASE)
# The region label lives inside a string literal, so it must be read from the
# raw line -- strip_noise has already removed it from the cleaned text.
_RE_REGION_NAME = re.compile(r'^\s*#region\b\s*"?(?P<name>[^"]*)"?', re.IGNORECASE)
_RE_END_REGION = re.compile(r"^#end\s+region\b", re.IGNORECASE)

_RE_CUSTOM_EVENT = re.compile(r"^custom\s+event\b", re.IGNORECASE)
_RE_ATTRIBUTE = re.compile(r"^<[^>]*>\s*")
_RE_REM = re.compile(r"(?i)(?<![\w.])REM(?=\s|$)")

_QUOTE = '"'
_APOSTROPHE = "'"


def strip_noise(line: str) -> str:
    """Reduce a physical line to code-only text.

    Removes double-quoted string literals (a doubled quote is the VB escape),
    apostrophe comments, and REM comments. Returns the stripped remainder.
    """
    out: list[str] = []
    i = 0
    n = len(line)
    while i < n:
        ch = line[i]
        if ch == _QUOTE:
            # Consume the literal; a doubled quote stays inside it.
            i += 1
            while i < n:
                if line[i] == _QUOTE:
                    if i + 1 < n and line[i + 1] == _QUOTE:
                        i += 2
                        continue
                    i += 1
                    break
                i += 1
            out.append('""')
            continue
        if ch == _APOSTROPHE:
            break
        out.append(ch)
        i += 1
    code = "".join(out)
    # REM comment, only when it stands as its own token.
    code = _RE_REM.split(code, maxsplit=1)[0]
    return code.strip()


def _logical_lines(lines: list[str]) -> list[tuple[int, str]]:
    """Join underscore continuations into logical lines.

    Returns (first_physical_line_number, cleaned_text) per logical line.
    Lines that reduce to nothing are dropped.
    """
    result: list[tuple[int, str]] = []
    buffer = ""
    start = 0
    for idx, raw in enumerate(lines, start=1):
        cleaned = strip_noise(raw)
        if not buffer:
            start = idx
        if cleaned.endswith("_") and (len(cleaned) == 1 or cleaned[-2].isspace()):
            buffer += cleaned[:-1].rstrip() + " "
            continue
        text = (buffer + cleaned).strip()
        buffer = ""
        if text:
            result.append((start, text))
    if buffer.strip():
        result.append((start, buffer.strip()))
    return result


# A multiline lambda (`Task.Run(Sub() ... End Sub)`) opens a body that the
# member patterns never see: the keyword is in expression position and carries
# no name. Its `End Sub` would otherwise pop the enclosing class frame.
_RE_LAMBDA = re.compile(r"\b(?P<kw>sub|function)\s*\(", re.IGNORECASE)
_RE_LAMBDA_AS = re.compile(r"^as\s+\S+$", re.IGNORECASE)


def _lambda_opens(text: str) -> list[str]:
    """Kinds of multiline lambdas opened on this logical line.

    A lambda is multiline only when nothing follows its parameter list, so
    single-line forms (`Sub() DoIt()`, `Function(x) x + 1`) are not counted.
    """
    opens: list[str] = []
    for match in _RE_LAMBDA.finditer(text):
        cursor = match.end() - 1
        depth = 0
        while cursor < len(text):
            if text[cursor] == "(":
                depth += 1
            elif text[cursor] == ")":
                depth -= 1
                if depth == 0:
                    break
            cursor += 1
        else:
            continue
        rest = text[cursor + 1 :].strip()
        kw = match.group("kw").lower()
        if not rest or (kw == "function" and _RE_LAMBDA_AS.match(rest)):
            opens.append(kw)
    return opens


def _clean_name(name: str) -> str:
    return name.strip().strip("[]")


def _is_block_property(logical: list[tuple[int, str]], index: int) -> bool:
    """Decide deterministically whether a Property declaration opens a body.

    An auto-implemented property has no `End Property`; a block property is
    followed by a Get/Set accessor. The rule is bounded lookahead to the next
    significant logical line.
    """
    for _, text in logical[index + 1 :]:
        stripped = _RE_ATTRIBUTE.sub("", text)
        if not stripped:
            continue
        return bool(_RE_ACCESSOR.match(stripped))
    return False


def parse_vbnet(source: str, file: str) -> StructuralMap:
    """Parse VB.NET source into a StructuralMap.

    Raises:
        StructuralParseError: on an unbalanced or mismatched block structure.
            Callers treat this as the signal to fall back to token windows.
    """
    lines = source.splitlines()
    total_lines = len(lines)
    logical = _logical_lines(lines)

    units: list[StructuralUnit] = []
    stack: list[tuple[str, StructuralUnit | None]] = []

    def enclosing_emitted() -> StructuralUnit | None:
        for kind, unit in reversed(stack):
            if unit is not None and kind != "region":
                return unit
        return None

    def parent_name() -> str | None:
        enclosing = enclosing_emitted()
        return enclosing.name if enclosing is not None else None

    def inside_interface() -> bool:
        for kind, _ in reversed(stack):
            if kind in ("class", "module", "structure", "sub", "function", "property"):
                return False
            if kind == "interface":
                return True
        return False

    def depth() -> int:
        return sum(1 for kind, unit in stack if unit is not None and kind != "region")

    def close_open_regions(at_line: int) -> None:
        while stack and stack[-1][0] == "region":
            _, open_region = stack.pop()
            if open_region is not None:
                open_region.end_line = at_line

    for index, (lineno, text) in enumerate(logical):
        if _RE_END_REGION.match(text):
            if not stack or stack[-1][0] != "region":
                raise StructuralParseError("#End Region without #Region", file, lineno)
            _, unit = stack.pop()
            if unit is not None:
                unit.end_line = lineno
            continue

        if _RE_REGION.match(text):
            raw = lines[lineno - 1] if lineno - 1 < len(lines) else text
            label = _RE_REGION_NAME.match(raw)
            unit = StructuralUnit(
                type="region",
                name=_clean_name(label.group("name")) if label else "",
                file=file,
                start_line=lineno,
                end_line=lineno,
                parent=parent_name(),
                nesting_depth=depth(),
                signature_line=raw.strip(),
            )
            if not unit.name:
                unit.name = "(unnamed)"
            units.append(unit)
            stack.append(("region", unit))
            continue

        end = _RE_END.match(text)
        if end:
            kw = end.group("kw").lower()
            # An unterminated #Region must not desynchronize the real stack.
            close_open_regions(lineno)
            if not stack:
                raise StructuralParseError(f"'End {kw}' without opener", file, lineno)
            kind, unit = stack.pop()
            if kind != kw:
                raise StructuralParseError(
                    f"'End {kw}' does not match open '{kind}'", file, lineno
                )
            if unit is not None:
                unit.end_line = lineno
            continue

        if _RE_DECLARE.match(text) or _RE_MUSTOVERRIDE.match(text):
            match = _RE_DECLARED_NAME.search(text)
            if match:
                units.append(
                    StructuralUnit(
                        type=match.group("kw").lower(),
                        name=_clean_name(match.group("name")),
                        file=file,
                        start_line=lineno,
                        end_line=lineno,
                        parent=parent_name(),
                        nesting_depth=depth(),
                        signature_line=text,
                        body_less=True,
                    )
                )
            continue

        container = _RE_CONTAINER.match(text)
        if container:
            kw = container.group("kw").lower()
            unit = StructuralUnit(
                type=kw,
                name=_clean_name(container.group("name")),
                file=file,
                start_line=lineno,
                end_line=lineno,
                parent=parent_name(),
                nesting_depth=depth(),
                signature_line=text,
            )
            units.append(unit)
            stack.append((kw, unit))
            continue

        accessor = _RE_ACCESSOR.match(text)
        if accessor and stack and stack[-1][0] in ("property", "event"):
            stack.append((accessor.group("kw").lower(), None))
            continue

        member = _RE_MEMBER.match(text)
        if member:
            kw = member.group("kw").lower()
            # A plain `Event Foo As EventHandler` has no body; only a
            # `Custom Event` opens one.
            if kw == "event":
                body_less = not _RE_CUSTOM_EVENT.match(text)
            elif kw == "property":
                body_less = not _is_block_property(logical, index)
            else:
                body_less = inside_interface()

            unit = StructuralUnit(
                type=kw,
                name=_clean_name(member.group("name")),
                file=file,
                start_line=lineno,
                end_line=lineno,
                parent=parent_name(),
                nesting_depth=depth(),
                signature_line=text,
                body_less=body_less,
            )
            units.append(unit)
            if not body_less:
                stack.append((kw, unit))
            continue

        for kind in _lambda_opens(text):
            stack.append((kind, None))

    # Tolerate an unterminated region (common in legacy files); never tolerate
    # an unterminated construct, which would mean the line ranges are wrong.
    close_open_regions(total_lines)
    if stack:
        kind, unit = stack[-1]
        name = unit.name if unit is not None else kind
        line = unit.start_line if unit is not None else 0
        raise StructuralParseError(f"unterminated '{kind} {name}'", file, line)

    units.sort(key=lambda u: (u.start_line, u.nesting_depth))
    return StructuralMap(
        file=file, total_lines=total_lines, units=units, language=LANGUAGE
    )


def parse_vbnet_file(path: str | Path) -> StructuralMap:
    """Parse a VB.NET file from disk, tolerating legacy encodings."""
    p = Path(path)
    data = p.read_bytes()
    try:
        source = data.decode("utf-8-sig")
    except UnicodeDecodeError:
        source = data.decode("cp1252", errors="replace")
    return parse_vbnet(source, p.name)
