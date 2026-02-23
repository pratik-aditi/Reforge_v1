# Implementation Plan: Content Accuracy Audit

**Branch**: `011-content-accuracy-audit` | **Date**: 2026-02-22 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/011-content-accuracy-audit/spec.md`

## Summary

Extend the `/reforge.audit` command with three new audit modes — accuracy verification, consistency checking, and unified full-audit — to detect fabricated content, arithmetic errors, broken cross-references, and stale generated output. This addresses 6 of the 13 verified errors from the TCOS-RUMO project that the existing coverage audit cannot detect.

The implementation is entirely prompt-template and schema modifications: extending `.reforge/commands/audit.md` with new workflow sections, creating 3 new schema definition files, updating the correction plan schema, and adding a minimal deletion action to `.reforge/commands/fix.md`. No compiled code, no runtime dependencies.

## Technical Context

**Language/Version**: Markdown prompt templates (no compiled code per Constitution Principle I)
**Primary Dependencies**: None — LLM-native tools only (Read, Write, Glob, Grep)
**Storage**: XML files for audit reports and correction plans; structured markdown for command templates and schema definitions
**Testing**: Manual validation via 8 success criteria defined in spec (run against TCOS-RUMO dataset)
**Target Platform**: Any AI coding assistant (agent-agnostic per Constitution Principle V)
**Project Type**: Single (prompt template framework)
**Performance Goals**: N/A (prompt templates, not runtime code)
**Constraints**: Must follow Constitution Principles I-VI; all verification logic executed by agent following prompt instructions, not by tooling
**Scale/Scope**: 1 command file updated (~500 lines added), 1 command file minimally updated (~30 lines), 3 new schema files created (~150 lines each), 1 schema file updated (~80 lines added)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Evidence |
|-----------|--------|----------|
| I. LLM-First Architecture | PASS | All changes are prompt template text and schema definitions. No compiled code, parsers, or runtime dependencies. Verification logic (word-boundary search, element counting, cross-reference validation) uses agent-native tools (Grep, Read, Glob). |
| II. Prompt Template Commands | PASS | Extending existing command `.reforge/commands/audit.md`. New workflow sections follow existing Step N pattern. No new command files created (fix.md is an existing command receiving a minor update). |
| III. Structured Output (XML/Markdown) | PASS | Three new XML report schemas with defined structure. All output includes source references. Schema definitions documented in `.reforge/schemas/`. |
| IV. Installable via CLI Bootstrap | PASS | No new dependencies. New schema files are plain markdown. Framework remains copy-installable. |
| V. Agent-Agnostic Design | PASS | All new prompt text uses "the agent MUST" phrasing. No agent-specific features referenced. Verification methodology uses only common tool patterns (file read, glob, grep). |
| VI. Extensibility via Tooling Layer | PASS | No optional tooling changes. Core workflow remains self-contained. Statistical sampling is agent-implemented via prompt instructions. |

**Gate Result**: ALL PASS. No violations. Proceeding to Phase 0.

## Project Structure

### Documentation (this feature)

```text
specs/011-content-accuracy-audit/
├── plan.md              # This file
├── spec.md              # Feature specification (with clarifications)
├── research.md          # Phase 0 output (methodology decisions)
├── data-model.md        # Phase 1 output (XML schema entity catalog)
├── quickstart.md        # Phase 1 output (usage guide)
└── tasks.md             # Phase 2 output (/speckit.tasks - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
.reforge/
├── commands/
│   ├── audit.md          # PRIMARY: Extend with routing + accuracy + consistency + full workflows
│   └── fix.md            # MINOR: Add deletion action dispatch for fabricated corrections
└── schemas/
    ├── accuracy-audit-report.md     # NEW: Accuracy audit report schema
    ├── consistency-audit-report.md  # NEW: Consistency audit report schema
    ├── full-audit-report.md         # NEW: Full audit report schema
    └── correction-plan.md           # UPDATE: Add new types, categories, attributes
```

**Structure Decision**: No new directories created. All changes are edits to 2 existing files and creation of 3 new schema definition files in the existing `.reforge/schemas/` directory. No `contracts/` directory needed — the XML schema definitions in `.reforge/schemas/` serve as the contracts for this prompt template project.

## Change Map

### File: `.reforge/commands/audit.md` (697 lines → ~1200 lines)

All existing content (Steps 0-7) remains untouched. New content is inserted at specific points:

| Change | Location | Type | Approx Size |
|--------|----------|------|-------------|
| Extended type argument validation | Step 1.5 (line ~123) | MODIFY | +15 lines |
| Audit mode routing section | After Step 1.5 | INSERT | ~30 lines |
| Accuracy Audit Workflow | After Step 7 (line ~396) | INSERT new section | ~200 lines |
| Consistency Audit Workflow | After Accuracy Workflow | INSERT new section | ~150 lines |
| Full Audit Workflow | After Consistency Workflow | INSERT new section | ~80 lines |
| Accuracy display results | Within Accuracy Workflow | INSERT | ~40 lines |
| Consistency display results | Within Consistency Workflow | INSERT | ~30 lines |
| Full audit display results | Within Full Workflow | INSERT | ~40 lines |

**Total**: ~500 lines of new content. ~15 lines of modified content.

### File: `.reforge/commands/fix.md` (640 lines → ~670 lines)

| Change | Location | Type | Approx Size |
|--------|----------|------|-------------|
| Deletion action dispatch | Step 3c (line ~196) | INSERT case | ~20 lines |
| Deletion verification | Step 4 (line ~229) | INSERT case | ~10 lines |

**Total**: ~30 lines of new content.

### File: `.reforge/schemas/correction-plan.md` (233 lines → ~315 lines)

| Change | Location | Type | Approx Size |
|--------|----------|------|-------------|
| New CorrectionType values | After line 67 | INSERT rows | ~15 lines |
| New CategoryType values | After line 74 | INSERT rows | ~10 lines |
| New attributes (source-audit-type, severity) | After line 59 | INSERT rows | ~10 lines |
| New `<evidence>` child element | After `<affected-files>` | INSERT section | ~25 lines |
| Updated priority order | Line 107 | MODIFY | ~5 lines |
| New example (fabricated correction) | After line 183 | INSERT example | ~20 lines |

**Total**: ~80 lines of new/modified content.

### New Files: `.reforge/schemas/accuracy-audit-report.md`, `consistency-audit-report.md`, `full-audit-report.md`

Each follows the pattern of the existing `audit-report.md` schema: overview, root element, attributes table, child elements, examples.

| File | Approx Size |
|------|-------------|
| `accuracy-audit-report.md` | ~180 lines |
| `consistency-audit-report.md` | ~150 lines |
| `full-audit-report.md` | ~100 lines |

## Implementation Phases

### Phase A: Schema Definitions (foundation)

Create the 3 new schema definition files and update the correction plan schema. These define the output contracts that the command workflows will produce.

**Deliverables**:
1. `.reforge/schemas/accuracy-audit-report.md` — Based on data-model.md Accuracy Audit Report section
2. `.reforge/schemas/consistency-audit-report.md` — Based on data-model.md Consistency Audit Report section
3. `.reforge/schemas/full-audit-report.md` — Based on data-model.md Full Audit Report section
4. `.reforge/schemas/correction-plan.md` — Extended with new types, categories, attributes, evidence element

**Depends on**: Nothing. Schemas are the foundation.

### Phase B: Audit Command — Routing & Type Validation

Extend the existing audit.md Step 1.5 to recognize `accuracy`, `consistency`, and `full` as valid type values. Add a routing section that dispatches to the appropriate workflow.

**Deliverables**:
1. Updated Step 1.5 type validation to include new values
2. New routing section after Step 1.5

**Depends on**: Phase A (routing references schema file paths for output).

### Phase C: Accuracy Audit Workflow

Insert the full accuracy audit workflow into audit.md. This is the largest single addition.

**Content**:
1. Prerequisites check (source codebase availability)
2. Extraction item enumeration across all extraction files
3. Statistical sampling logic (stratified, 20% default, --full-verify override)
4. Multi-check-type verification methodology (7 check types)
5. Verdict classification (5 verdict values)
6. Accuracy score computation
7. Report generation (`accuracy-audit-report.xml`)
8. Correction plan generation (`accuracy-correction-plan.xml`)
9. Display results

**Depends on**: Phase A (schemas), Phase B (routing).

### Phase D: Consistency Audit Workflow

Insert the consistency audit workflow into audit.md.

**Content**:
1. Arithmetic checks (metadata count vs actual element count)
2. Cross-reference validation (file references, ID references)
3. Duplicate ID detection (within-file, within-category, cross-category)
4. Freshness checks (generated vs extraction timestamps, numeric claims)
5. Cross-document discrepancy detection
6. Consistency score computation
7. Report generation (`consistency-audit-report.xml`)
8. Correction plan generation (`consistency-correction-plan.xml`)
9. Display results

**Depends on**: Phase A (schemas), Phase B (routing).

### Phase E: Full Audit Workflow

Insert the full audit workflow that orchestrates coverage + consistency + accuracy in sequence and produces the unified report.

**Content**:
1. Sequential execution: coverage audit → consistency audit → accuracy audit
2. Score collection from individual reports
3. Composite score computation (coverage*0.25 + consistency*0.35 + accuracy*0.40)
4. Quality rating mapping
5. Correction plan merging with source-audit-type tagging
6. Unified report generation (`full-audit-report.xml`)
7. Display results with composite score and rating

**Depends on**: Phase C (accuracy workflow), Phase D (consistency workflow).

### Phase F: Fix Command Update

Add the deletion action dispatch to fix.md for `fabricated` correction types.

**Content**:
1. New dispatch case in Step 3c for deletion actions
2. Agent instructions: read extraction XML, locate element by ID, remove it, update metadata count
3. New verification case in Step 4 for deletion (confirm element no longer present)

**Depends on**: Phase A (correction plan schema defines the new correction types).

## Complexity Tracking

> No Constitution violations. No complexity justifications needed.

## Post-Phase 1 Constitution Re-Check

| Principle | Status | Evidence |
|-----------|--------|----------|
| I. LLM-First Architecture | PASS | All changes remain markdown prompt text and schema definitions. Zero compiled code. Verification methodology (Grep word-boundary search, Read line verification, element counting) uses only LLM-native tools. |
| II. Prompt Template Commands | PASS | audit.md remains a valid command template with clear inputs/steps/outputs. New sections follow existing patterns. fix.md update adds a dispatch case following existing patterns. |
| III. Structured Output | PASS | Three new XML schema definitions with full attribute/element specifications. All reports include source references and traceability. |
| IV. Installable via CLI | PASS | No new dependencies. Three new `.md` files in existing directory. |
| V. Agent-Agnostic | PASS | All new text uses "the agent MUST" phrasing. Verified no agent-specific references in any new content. |
| VI. Extensibility | PASS | No optional tooling introduced. All verification is agent-implemented via prompt instructions. |

**Gate Result**: ALL PASS after design.
