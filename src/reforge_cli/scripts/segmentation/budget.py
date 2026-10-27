"""Token budget primitives (Layer 3 subset).

Layer 4 owns the full budget controller and will extend this module with
config-driven limits read from `.reforge/config.json`. Until then the defaults
live here as constants so the planner has something to size against, and
nothing outside this package is modified.

Budgeting is token-primary and line-secondary, per reforge-update.txt. The line
limit is a guard rail that caps a pathological segment; it never drives packing.
"""

from __future__ import annotations

from dataclasses import dataclass

#: Characters per token for source code, used by `estimate_tokens`.
#:
#: Deliberately a crude ratio rather than a real tokenizer: adding a tokenizer
#: would mean a new runtime dependency, and the planner only needs a *stable,
#: monotonic* size signal, not an exact count. Determinism matters here far more
#: than accuracy -- the same bytes must always produce the same segments.
#:
#: 3.2 is a conservative starting point for VB.NET (indentation-heavy, verbose
#: keywords). Layer 4 should calibrate it against a real tokenizer on the
#: benchmark files and pin the measured value here.
CHARS_PER_TOKEN = 3.2

#: Preferred segment size. Packing closes a segment once the next atom would
#: push it past this.
DEFAULT_TARGET_TOKENS = 6000

#: Hard ceiling. An atom that exceeds this on its own is oversized and is handed
#: to Layer 4's block splitter.
DEFAULT_MAX_TOKENS = 9000

#: Guard rail only.
DEFAULT_MAX_LINES = 1200


def estimate_tokens(text: str) -> int:
    """Estimate the token count of a block of source text.

    Deterministic by construction: a pure function of the input bytes.
    """
    if not text:
        return 0
    return max(1, int(len(text) / CHARS_PER_TOKEN))


def estimate_lines_tokens(lines: list[str], start_line: int, end_line: int) -> int:
    """Estimate tokens for an inclusive, 1-based line range."""
    if start_line > end_line:
        return 0
    chunk = lines[start_line - 1 : end_line]
    return estimate_tokens("\n".join(chunk))


@dataclass(frozen=True)
class Budget:
    """Size limits for one segmentation run."""

    target_tokens: int = DEFAULT_TARGET_TOKENS
    max_tokens: int = DEFAULT_MAX_TOKENS
    max_lines: int = DEFAULT_MAX_LINES

    def __post_init__(self) -> None:
        if self.target_tokens <= 0 or self.max_tokens <= 0 or self.max_lines <= 0:
            raise ValueError("budget limits must be positive")
        if self.target_tokens > self.max_tokens:
            raise ValueError("target_tokens must not exceed max_tokens")

    def exceeds(self, tokens: int, lines: int) -> bool:
        """True when a block is too large to stand as one segment."""
        return tokens > self.max_tokens or lines > self.max_lines
