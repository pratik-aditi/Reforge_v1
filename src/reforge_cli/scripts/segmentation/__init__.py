"""Deterministic segment planning (Layer 3).

Decides WHERE the boundaries of each extraction task fall. Never decides what
the bounded source means.
"""

from .budget import (
    CHARS_PER_TOKEN,
    DEFAULT_MAX_LINES,
    DEFAULT_MAX_TOKENS,
    DEFAULT_TARGET_TOKENS,
    Budget,
    estimate_lines_tokens,
    estimate_tokens,
)
from .models import (
    INTEGRITY_DEGRADED,
    INTEGRITY_INTACT,
    STRATEGIES,
    STRATEGY_BLOCK_SPLIT,
    STRATEGY_BLOCK_SPLIT_DEEP,
    STRATEGY_FALLBACK_WINDOW,
    STRATEGY_INTERSTITIAL,
    STRATEGY_MEMBER_PACK,
    STRATEGY_OVERSIZED_MEMBER,
    STRATEGY_WHOLE_FILE,
    CoverageError,
    Segment,
    SegmentPlan,
)
from .coverage import CoverageReport, assert_valid, validate_plan
from .manifest import (
    GENERATOR_VERSION,
    MANIFEST_SCHEMA_VERSION,
    build_manifest,
    config_hash,
    file_hash,
    is_stale,
    load_manifest,
    manifest_path,
    write_manifest,
)
from .planner import plan_segments, plan_token_windows
from .splitter import apply_splits, split_segment, top_level_boundaries

__all__ = [
    "INTEGRITY_DEGRADED",
    "INTEGRITY_INTACT",
    "STRATEGY_BLOCK_SPLIT",
    "STRATEGY_BLOCK_SPLIT_DEEP",
    "apply_splits",
    "split_segment",
    "top_level_boundaries",
    "CoverageReport",
    "assert_valid",
    "validate_plan",
    "GENERATOR_VERSION",
    "MANIFEST_SCHEMA_VERSION",
    "build_manifest",
    "config_hash",
    "file_hash",
    "is_stale",
    "load_manifest",
    "manifest_path",
    "write_manifest",
    "CHARS_PER_TOKEN",
    "DEFAULT_MAX_LINES",
    "DEFAULT_MAX_TOKENS",
    "DEFAULT_TARGET_TOKENS",
    "Budget",
    "estimate_lines_tokens",
    "estimate_tokens",
    "STRATEGIES",
    "STRATEGY_FALLBACK_WINDOW",
    "STRATEGY_INTERSTITIAL",
    "STRATEGY_MEMBER_PACK",
    "STRATEGY_OVERSIZED_MEMBER",
    "STRATEGY_WHOLE_FILE",
    "CoverageError",
    "Segment",
    "SegmentPlan",
    "plan_segments",
    "plan_token_windows",
]
