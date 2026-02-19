# Implementation Plan: Extract Verification Gates

**Branch**: `006-extract-verification-gates` | **Date**: 2026-02-19 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/006-extract-verification-gates/spec.md`

## Summary

Add anti-hallucination verification gates to `.reforge/commands/extract.md` at three stages (pre-extraction, during-extraction, post-extraction) to prevent LLM fabrication of identifiers, types, protocols, and references. All changes are prompt template modifications — no compiled code, no new dependencies, no new tooling. The implementation inserts, appends, and replaces specific markdown sections in the existing extract.md file per the insertion map in SPEC-001.

## Technical Context

**Language/Version**: Markdown (prompt templates — no compiled code per Constitution Principle I)
**Primary Dependencies**: None (LLM-native tools only: Read, Write, Glob, Grep)
**Storage**: N/A (file-based markdown prompt template)
**Testing**: Manual validation via grep verification of text presence in extract.md + acceptance criteria from SPEC-001
**Target Platform**: Any AI coding assistant (agent-agnostic per Constitution Principle V)
**Project Type**: single (framework file modification)
**Performance Goals**: N/A (prompt template, not runtime code)
**Constraints**: All modifications must be to `.reforge/commands/extract.md` only; must use agent-agnostic language ("the agent MUST", not agent-specific names)
**Scale/Scope**: Single file (~841 lines current), 13 operations (14 atomic ops — Op 1 is a combined REPLACE+APPEND), 6 new sections created, 6 existing sections modified

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Evidence |
|-----------|--------|----------|
| I. LLM-First Architecture | PASS | All verification gates are prompt-based instructions for the AI agent; no compiled code, no external parsers, no runtime dependencies added |
| II. Prompt Template Commands | PASS | Modifying existing command template (`.reforge/commands/extract.md`); no new commands created; command remains self-contained |
| III. Structured Output (XML/Markdown) | PASS | Output format (XML with source references) unchanged; verification gates ensure output accuracy, not format changes |
| IV. Installable via CLI Bootstrap | PASS | No new dependencies; modified extract.md ships with framework as before |
| V. Agent-Agnostic Design | PASS | SPEC-001 uses "the LLM MUST" language; tools referenced (Read, Glob, Grep) are common agent tool patterns per Principle V rules |
| VI. Extensibility via Tooling Layer | PASS | No new tooling required; all verification is prompt-based within the command template |

**Gate Result**: ALL PASS — proceed to Phase 0.

## Project Structure

### Documentation (this feature)

```text
specs/006-extract-verification-gates/
├── plan.md              # This file
├── research.md          # Phase 0 output: line number verification, insertion strategy
├── data-model.md        # Phase 1 output: section map and modification catalog
├── quickstart.md        # Phase 1 output: verification and validation guide
├── checklists/
│   └── requirements.md  # Spec quality checklist (already created)
└── tasks.md             # Phase 2 output (created by /speckit.tasks)
```

### Source Code (repository root)

```text
.reforge/
└── commands/
    └── extract.md       # TARGET FILE — all modifications go here
```

**Structure Decision**: No new files or directories created in the framework. All changes are edits to the single existing file `.reforge/commands/extract.md`. The implementation consists of 13 operations (8 insertions, 3 appends, 2 replacements; Op 1 combines REPLACE+APPEND as a single sequenced operation) applied in dependency order.

## Implementation Strategy

### Modification Sequence

Operations must be applied **bottom-to-top** within the file to preserve line number accuracy for subsequent operations. The sequence:

| Order | Operation | Location (line) | Type | Requirement | FR |
|-------|-----------|-----------------|------|-------------|-----|
| 1 | Replace "Optional Validation" with "Required Validation" + XSD limitation note | 815-817 + after 824 | REPLACE + APPEND | REQ-EXT-003, REQ-EXT-012 | FR-013, FR-014 |
| 2 | Insert "Language-Specific Extraction Rules" section | After 812 | INSERT | REQ-EXT-009 | FR-011 |
| 3 | Append snippet fidelity requirements to Source References | After 797 | APPEND | REQ-EXT-007 | FR-008 |
| 4 | Append file existence gate to Source References | After 797 | APPEND | REQ-EXT-004 | FR-006 |
| 5 | Replace Confidence Levels table | 785-789 | REPLACE | REQ-EXT-008 | FR-009 |
| 6 | Insert method name accuracy in Workflow Step 2 | After 683 | INSERT | REQ-EXT-006 | FR-007 |
| 7 | Insert "Step 5.5: Post-Extraction Verification" | Between 236 and 238 | INSERT | REQ-EXT-003 | FR-004, FR-005 |
| 8 | Insert aggregation accuracy requirements in Step 5 | After 195 | INSERT | REQ-EXT-011 | FR-012 |
| 9 | Insert "Step 3a: Technical Mechanism Accuracy" | After 182 (adjusted from 186) | INSERT | REQ-EXT-005 | FR-010 |
| 10 | Insert type preservation text in Step 3 | After 160 | INSERT | REQ-EXT-002 part 2 | FR-003 |
| 11 | Insert "Step 2.5: Verbatim Extraction Rules" | After 151, before Step 3 | INSERT | REQ-EXT-001 | FR-001, FR-015 |
| 12 | Insert "Enumeration and Constant Patterns" | After 151 (before Step 2.5) | INSERT | REQ-EXT-002 | FR-003 |
| 13 | Append read-before-describe mandate to Step 1 | After 84 | APPEND | REQ-EXT-010 | FR-002 |

**Note**: Operation 9 uses adjusted line 182 instead of SPEC-001's line 186 per research findings (4-line drift).

### Agent-Agnostic Language Compliance

SPEC-001 text uses "the LLM MUST" phrasing. During implementation, verify all inserted text:
- Uses "the agent" or "you" (addressing the executing agent) — not "Claude", "Copilot", etc.
- References common tool patterns: "Read tool", "Glob", "Grep" (allowed per Principle V)
- Does not reference MCP servers, agent-specific features, or proprietary capabilities

### Verification Approach

After all modifications, verify success criteria by grepping the modified extract.md:
1. `grep -c "verbatim"` — must return >= 3
2. `grep "Prohibited patterns"` — must exist
3. `grep "Step 2.5"` — must exist (Verbatim Extraction Rules)
4. `grep "Step 5.5"` — must exist (Post-Extraction Verification)
5. `grep "Required Validation"` — must exist (replaces "Optional Validation")
6. `grep "Optional Validation"` — must return 0 results
7. `grep "Language-Specific Extraction Rules"` — must exist
8. `grep "verified against source code"` — must exist in confidence table

## Complexity Tracking

No constitution violations. No complexity justifications needed.
