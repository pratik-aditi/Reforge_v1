# Deterministic Layer — Integration Point (Layer 1 Deliverable)

> Answers the Layer 1 question: *where can the deterministic source layer be
> inserted with minimum disruption?*

## Answer

**One new shared section in `.reforge/commands/extract.md`, plus a rewrite of the
four lines at `extract.md:143` (the "read it in sections" clause).**

Everything else is additive: new Python modules, a new CLI subcommand, new output
files. No existing module is modified.

## Minimum edit set

Ordered by how late they can be deferred. Items 1–2 are new files only.

| # | Target | Kind | Layer | Deferrable to |
|---|--------|------|-------|---------------|
| 1 | `src/reforge_cli/scripts/structure/` | **new files** | 2 | — |
| 2 | `src/reforge_cli/scripts/segmentation/` | **new files** | 3–5 | — |
| 3 | `tests/fixtures/vbnet/`, `tests/test_structure.py` | **new files** | 2 | — |
| 4 | `.reforge/config.json` | **additive key** `segmentation` | 4 | Layer 4 |
| 5 | `src/reforge_cli/scripts/__init__.py` | 2 added exports | 5 | Layer 5 |
| 6 | `src/reforge_cli/__init__.py` | 1 added `@scripts.command("segment-source")` | 5 | Layer 5 |
| 7 | `.reforge/commands/extract.md` | replace 143; add shared section | 6 | Layer 6 |
| 8 | `.reforge/memory/constitution.md` | clarify Principle I | — | **decision needed** |

Items 5 and 6 were not in the two-file edit budget agreed earlier. They are
unavoidable for CLI exposure — a Typer subcommand must be registered — but both are
pure additions (one import line, one decorated function) and **neither is needed for
Layer 2**, which ships as an importable library with tests.

## Why `extract.md:143` is the right seam

```
3. If a file is too large to read in one pass, read it in sections and process each section
```

This one clause *is* the current segmentation policy, it is the only place boundary
authority is granted to the LLM, and it has no other behavioural dependencies.
Replacing it transfers that authority to deterministic code without disturbing the
pattern catalogue (Step 2), the anti-hallucination mandate (Step 2.5), or the
validation chain (Steps 5.5/5.6) — all of which continue to apply unchanged, per
segment instead of per file.

## Structural obstacle (decide before Layer 6)

Per `current-extraction-flow.md` §4, `extract.md` has no shared preamble: Steps 0–0.8
sit under the business-rules heading, and each of the four types restarts at its own
`Step 1`. Two options:

- **Option A — narrow.** Add one shared `## Deterministic Source Segmentation`
  section before `## Extraction Types` (line ~44), and in each of the four `Step 1`
  blocks add a single cross-reference line. Five small, reviewable edits.
- **Option B — structural.** Promote Steps 0–0.8 into a shared preamble, then insert
  once. Cleaner result, but a large diff in a 1,637-line prompt.

**Recommendation: Option A.** It is the smaller diff and matches the standing
guardrail. Option B is a separate refactor to propose on its own merits.

## Two corrections to the plan in `reforge-update.txt`

1. **No sub-agents exist.** Layer 6 must introduce orchestration, not connect to it.
   This makes Layer 6 materially larger than the source document implies and it
   should be re-scoped before work starts.
2. **No working resume exists.** `extract.md` never calls `checkpoint`, and the
   checkpoint schema is file-granular (`total-files`, `processed-files`,
   `current-file`). The success criterion *"one failed segment does not require
   rereading the entire huge source file"* therefore requires a new segment-granular
   checkpoint type — new work, not a modification, and best treated as its own item.

## Open decision carried forward

**Symbol digest (Caveat 2 — option A vs B), still unanswered.** Layer 1 resolves the
urgency: Layer 2 records every declaration as a structural unit regardless, so the
digest is *derivable from Layer 2 output with no rework*. The decision is not needed
until Layer 6 builds task packets, and nothing built before then forecloses it.

## Constitution conflict (your call, unactioned)

Constitution Principle I states "no compiled code / LLM-native tools only". Python
helpers already exist (§6 of the flow document), so the principle is already read as
*"no compiled analysis"* rather than *"no code"*. Recommended clarification —
**not applied**, flagged only:

> Deterministic mechanics (path resolution, checkpointing, validation, source
> segmentation) may be implemented as pure-stdlib Python helpers. All semantic
> interpretation of source code remains with the LLM.
