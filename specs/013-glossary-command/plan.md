# Implementation Plan: Glossary Command

**Branch**: `013-glossary-command` | **Date**: 2026-02-23 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/013-glossary-command/spec.md`

## Summary

Implement `/reforge.glossary` — a 4-phase acronym extraction and verification pipeline delivered as markdown prompt templates. A parent orchestrator template dispatches to per-phase templates that guide the agent through pattern extraction, WebSearch-based external verification, source code audit via word-boundary grep, and an independent self-audit. The final glossary persists to memory for cross-command consumption. Team orchestration is an optional enhancement with mandatory sequential fallback per Constitution Principle V.

## Technical Context

**Language/Version**: Markdown prompt templates (no compiled code per Constitution Principle I)
**Primary Dependencies**: None — LLM-native tools only (Read, Write, Glob, Grep, WebSearch)
**Storage**: XML files for glossary output; JSON for memory lookup and checkpoints; markdown for templates
**Testing**: Manual validation via sample legacy codebases
**Target Platform**: Any AI coding assistant (agent-agnostic per Constitution Principle V)
**Project Type**: Prompt template framework (no compiled source code)
**Performance Goals**: <15 min/phase for 500-file codebase at default team size (3 agents)
**Constraints**: Agent-agnostic, zero dependencies, LLM-native tools only, common-schema extension
**Scale/Scope**: Codebases up to 500 source files, team size 1-6 agents, English-language acronyms only

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. LLM-First Architecture | PASS | All analysis via LLM using Read/Grep/Glob/Write/WebSearch. No compiled code, no external parsers. |
| II. Prompt Template Commands | PASS | Command defined as markdown files in `.reforge/commands/`. Parent orchestrator + 4 per-phase templates. |
| III. Structured Output (XML/Markdown) | PASS | Glossary XML extends common-schema. Schemas documented in `.reforge/schemas/glossary.md`. Source references included. |
| IV. Installable via CLI Bootstrap | PASS | Only adds markdown template files and a schema definition. No runtime dependencies. |
| V. Agent-Agnostic Design | PASS (conditional) | Team orchestration expressed as optional enhancement with sequential fallback. Templates use "the agent" not specific agent names. Core workflow uses only Read/Write/Glob/Grep/WebSearch. **Note**: WebSearch is not in Constitution V's explicit tool list ("file read, file write, glob, grep, directory listing") but is a common agent capability; Phase 2 is skippable via `--skip-external` ensuring no hard dependency on WebSearch. See R-001 in research.md. |
| VI. Extensibility via Tooling Layer | PASS | Team orchestration is an optional layer that enhances but never replaces the core sequential workflow. |

**Principle V Mitigation**: The spec lists TeamCreate/Task/SendMessage as dependencies. In implementation, these are reframed as optional capabilities. The core template describes sequential zone-by-zone processing that works on any agent. A clearly marked optional section provides parallel instructions for agents with team orchestration support. Output is identical regardless of execution path. See Complexity Tracking below.

### Post-Design Re-Check

| Principle | Status | Notes |
|-----------|--------|-------|
| I. LLM-First | PASS | Data model uses XML/JSON — no compiled validators |
| II. Prompt Templates | PASS | 5 template files (1 orchestrator + 4 phases) + 1 schema |
| III. Structured Output | PASS | Common-schema extension with source traceability |
| IV. Installable | PASS | Only markdown files added |
| V. Agent-Agnostic | PASS | Sequential fallback confirmed in quickstart.md; WebSearch optional via `--skip-external` |
| VI. Extensibility | PASS | Optional team enhancement documented |

## Project Structure

### Documentation (this feature)

```text
specs/013-glossary-command/
├── spec.md              # Feature specification
├── plan.md              # This file
├── research.md          # Phase 0: Research decisions (8 items)
├── data-model.md        # Phase 1: Entity definitions
├── quickstart.md        # Phase 1: Usage guide and file map
└── tasks.md             # Phase 2 output (created by /speckit.tasks)
```

### Source Code (repository root)

```text
.reforge/
├── commands/
│   ├── glossary.md              # Parent orchestrator (flag routing, checkpoints, dispatch)
│   ├── glossary-phase-1.md      # Phase 1: Pattern Extraction
│   ├── glossary-phase-2.md      # Phase 2: External Verification (WebSearch)
│   ├── glossary-phase-3.md      # Phase 3: Source Code Audit (word-boundary grep)
│   └── glossary-phase-4.md      # Phase 4: Self-Audit
├── schemas/
│   └── glossary.md              # Glossary XML schema definition (extends common-schema)
├── memory/
│   ├── glossary.json            # Persistent lookup (created at runtime)
│   └── checkpoints/
│       └── glossary-checkpoint.json  # Resume state (created/cleaned at runtime)
└── config.json                  # (no changes — existing config sufficient)

reforge_output/<project-name>/
├── extractions/
│   └── acronym-glossary.xml     # Glossary extraction output (created at runtime)
└── audit/
    └── glossary-audit-report.xml # Phase 3-4 audit findings (created at runtime)
```

**Structure Decision**: No new directories required beyond existing `.reforge/commands/` and `.reforge/schemas/`. Runtime output follows existing `reforge_output/` conventions. The `.reforge/memory/checkpoints/` subdirectory may need creation if it doesn't exist (handled by the orchestrator template).

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| 5 template files (1 orchestrator + 4 phases) instead of 1 | Each phase has fundamentally different tool requirements (Read/Glob, WebSearch, Grep, Read/Grep). Separation enables `--phase N` routing and keeps each template focused and maintainable. | Single monolithic template would exceed ~1000 lines, mix unrelated concerns, and make per-phase execution awkward with large conditional blocks. |
| Optional agent-specific team orchestration section | Parallel processing provides 40-70% time savings for capable agents on large codebases. | Removing parallelism entirely penalizes capable agents. The sequential fallback ensures all agents produce identical results. |
