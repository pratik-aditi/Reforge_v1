# Implementation Plan: Source-Anchored Generation

**Branch**: `010-source-anchored-generation` | **Date**: 2026-02-20 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/010-source-anchored-generation/spec.md`

## Summary

Implement Source-Anchored Generation constraints for the `/reforge.generate` command, ensuring the generation phase treats extraction XML as the sole source of truth. This prevents fabricated identifiers, stale statistics, and unsourced claims -- addressing 7 of 13 verified errors from the TCOS-RUMO project.

The implementation is entirely prompt-template modifications: inserting new mandatory sections into `.reforge/commands/generate.md` and adding annotations to 5 template files. No compiled code, no runtime dependencies.

## Technical Context

**Language/Version**: Markdown prompt templates (no compiled code per Constitution Principle I)
**Primary Dependencies**: None -- LLM-native tools only (Read, Write, Glob, Grep)
**Storage**: Filesystem -- markdown files in `.reforge/commands/` and `.reforge/templates/`
**Testing**: Manual validation via 8 test cases defined in spec (run against TCOS-RUMO dataset)
**Target Platform**: Any AI coding assistant (agent-agnostic per Constitution Principle V)
**Project Type**: Single (prompt template framework)
**Performance Goals**: N/A (prompt templates, not runtime code)
**Constraints**: Must follow Constitution Principles I-VI; all constraints enforced by agent following prompt, not by tooling
**Scale/Scope**: 1 command file (1009 lines) + 5 template files modified; ~345 lines of new prompt content inserted

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Evidence |
|-----------|--------|----------|
| I. LLM-First Architecture | PASS | All changes are prompt template text. No compiled code, parsers, or runtime dependencies introduced. |
| II. Prompt Template Commands | PASS | Modifying existing command `.reforge/commands/generate.md`. New sections follow existing Step N pattern. |
| III. Structured Output (XML/Markdown) | PASS | Provenance annotations use HTML comments in generated output. Verification logs use structured comment blocks. All output remains XML/markdown. |
| IV. Installable via CLI Bootstrap | PASS | No new dependencies. Framework remains copy-installable. |
| V. Agent-Agnostic Design | PASS | All constraints use "the agent MUST" phrasing. No agent-specific features referenced. |
| VI. Extensibility via Tooling Layer | PASS | No optional tooling changes. Core workflow remains self-contained. |

**Gate Result**: ALL PASS. No violations. Proceeding to Phase 0.

## Project Structure

### Documentation (this feature)

```text
specs/010-source-anchored-generation/
├── plan.md              # This file
├── research.md          # Phase 0 output (insertion point analysis)
├── data-model.md        # Phase 1 output (section catalog)
├── quickstart.md        # Phase 1 output (usage guide)
└── tasks.md             # Phase 2 output (/speckit.tasks)
```

### Source Code (repository root)

```text
.reforge/
├── commands/
│   └── generate.md         # PRIMARY: Insert Step 0.6 + 9 new sections + update Selective Regeneration
└── templates/
    ├── sysml-block.md      # ANNOTATE: Add Source-Anchored Generation reference
    ├── uml-class.md        # ANNOTATE: Add Source-Anchored Generation reference
    ├── user-story.md       # ANNOTATE: Add Source-Anchored Generation reference
    ├── ascii-layout.md     # ANNOTATE: Add Source-Anchored Generation reference
    └── data-dictionary.md  # ANNOTATE: Add Source-Anchored Generation reference
```

**Structure Decision**: No new files or directories created in the framework. All changes are edits to 6 existing files. The `contracts/` directory is not applicable (no API endpoints -- this is a prompt template feature).

## Change Map

### File: `.reforge/commands/generate.md` (1009 lines)

All insertions are additive. No existing content is removed or reordered.

| Change | Location | Type | Approx Size |
|--------|----------|------|-------------|
| Step 0.6: Source-Anchored Generation Constraints | After line 75 (after Step 0.5, before Step 0.7) | INSERT new section | ~60 lines |
| Template Placeholder Specification | After line 128 (within Markdown Generation section) | INSERT subsection | ~25 lines |
| Canonical Metrics Computation | Before line 975 (before Selective Regeneration) | INSERT new section | ~35 lines |
| Multi-File Extraction Discovery | After Canonical Metrics | INSERT new section | ~20 lines |
| Content Validation Checklist | After Multi-File Discovery | INSERT new section | ~30 lines |
| Extraction Freshness & Gap Reporting | After Content Validation | INSERT new section | ~15 lines |
| Diagram Verification Protocol | After Freshness & Gap Reporting | INSERT new section | ~35 lines |
| Cross-Extraction Consistency Check | After Diagram Verification | INSERT new section | ~25 lines |
| Output Provenance Annotations | After Cross-Extraction Consistency | INSERT new section | ~15 lines |
| HTML Report Generation | After Provenance Annotations | INSERT new section | ~30 lines |
| Selective Regeneration update | Append to existing section (line 975+) | APPEND 2 items | ~5 lines |

**Total**: ~295 lines of new content inserted into generate.md.

### Files: `.reforge/templates/*.md` (5 files)

Each template receives an identical annotation block (~10 lines) inserted after their existing "Generation Guidelines" / "Notes for Agent" / "Story Generation Rules" section.

| Template File | Insert After Section |
|---------------|---------------------|
| `sysml-block.md` | "Generation Guidelines" |
| `uml-class.md` | "Generation Notes" |
| `user-story.md` | "Story Generation Rules" |
| `ascii-layout.md` | "Generation Guidelines" |
| `data-dictionary.md` | "Notes for Agent" |

**Total per file**: ~10 lines. **Total across all templates**: ~50 lines.

## Implementation Phases

### Phase A: Core Constraints (Step 0.6)

Insert the Source-Anchored Generation Constraints section into generate.md as Step 0.6. This is the foundation -- all other sections reference these constraints.

**Content**: 7 constraints covering single source of truth, no embellishment, no training-data contamination, verbatim identifiers, computed totals, source code boundary, and when-in-doubt-omit.

**Depends on**: Nothing. This is the first change.

### Phase B: Verification Sections

Insert the mandatory verification and validation sections before the Selective Regeneration section. These sections define the operational procedures that enforce Step 0.6 constraints.

**Sections** (in order):
1. Canonical Metrics Computation
2. Multi-File Extraction Discovery
3. Content Validation Checklist (10 items)
4. Extraction Freshness & Gap Reporting
5. Diagram Verification Protocol (6 steps)
6. Cross-Extraction Consistency Check
7. Output Provenance Annotations

**Ordering rationale**: Sections ordered to align with implementation priority (P1 → P2 → P3), so earlier stories' sections appear first in the document and serve as stable insertion anchors for later stories.

**Depends on**: Phase A (constraints must exist for sections to reference).

### Phase C: Generation-Type Sections

Insert the HTML Report Generation section and Template Placeholder Specification.

**Sections**:
1. HTML Report Generation (new generation sub-command guidance)
2. Template Placeholder Specification (typed placeholders with source/derivation)

**Depends on**: Phase A (both reference Step 0.6 constraints).

### Phase D: Selective Regeneration Update

Append 2 new rules to the existing Selective Regeneration section:
1. Re-verify regenerated sections against Content Validation Checklist
2. Recompute canonical metrics table before regenerating

**Depends on**: Phase B (references Content Validation Checklist and canonical metrics).

### Phase E: Template Annotations

Add a Source-Anchored Generation reference block to all 5 template files. Each block is identical and references the constraints in generate.md Step 0.6.

**Depends on**: Phase A (annotations reference Step 0.6 by name).

## Complexity Tracking

> No Constitution violations. No complexity justifications needed.

## Post-Phase 1 Constitution Re-Check

| Principle | Status | Evidence |
|-----------|--------|----------|
| I. LLM-First Architecture | PASS | All changes remain markdown prompt text. Zero compiled code. |
| II. Prompt Template Commands | PASS | generate.md remains a valid command template with clear inputs/steps/outputs. |
| III. Structured Output | PASS | Provenance annotations and verification logs are structured formats. |
| IV. Installable via CLI | PASS | No new dependencies. |
| V. Agent-Agnostic | PASS | All new text uses "the agent MUST" phrasing. Verified no agent-specific references. |
| VI. Extensibility | PASS | No optional tooling introduced. |

**Gate Result**: ALL PASS after design.
