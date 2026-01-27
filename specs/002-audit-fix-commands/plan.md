# Implementation Plan: Audit and Fix Commands

**Branch**: `002-audit-fix-commands` | **Date**: 2026-01-23 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-audit-fix-commands/spec.md`

## Summary

Add two new reforge commands (`/reforge.audit` and `/reforge.fix`) that enable users to verify extraction coverage completeness and automatically execute corrections. The audit command performs file-level metadata comparison between analysis.xml and extraction outputs, produces a structured correction plan, and the fix command orchestrates existing reforge commands to resolve identified gaps.

## Technical Context

**Language/Version**: Markdown prompt templates (no compiled code per Constitution Principle I)
**Primary Dependencies**: None (LLM-native tools only: Read, Write, Glob, Grep)
**Storage**: XML files for audit report and correction plan; structured markdown for command templates
**Testing**: Manual validation via sample legacy codebases with known coverage gaps
**Target Platform**: Any AI coding assistant (agent-agnostic per Constitution Principle V)
**Project Type**: Single (framework of prompt templates and schemas)
**Performance Goals**: N/A (metadata comparison is inherently fast for LLM file operations)
**Constraints**: Must use only LLM-native tools; no external parsers or runtime dependencies
**Scale/Scope**: Supports codebases with 1000+ files in analysis.xml

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Evidence |
|-----------|--------|----------|
| I. LLM-First Architecture | PASS | Commands instruct the LLM to perform metadata comparison using Read/Grep on existing XML files. No external tooling. |
| II. Prompt Template Commands | PASS | Two new command files (`audit.md`, `fix.md`) in `.reforge/commands/` following existing patterns. |
| III. Structured Output (XML/Markdown) | PASS | Audit report and correction plan stored as XML with defined schemas in `.reforge/schemas/`. |
| IV. Installable via CLI Bootstrap | PASS | New files are markdown/schemas copied alongside existing framework files. |
| V. Agent-Agnostic Design | PASS | Commands use only common tool patterns (Read, Write, Glob, Grep). No agent-specific references. |
| VI. Extensibility via Tooling Layer | PASS | No new required tooling. Core workflow functions with LLM tools only. |

**Gate result**: ALL PASS — no violations.

## Project Structure

### Documentation (this feature)

```text
specs/002-audit-fix-commands/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (XML schema definitions)
└── tasks.md             # Phase 2 output (/speckit.tasks command)
```

### Source Code (repository root)

```text
.reforge/
├── commands/
│   ├── audit.md         # NEW: /reforge.audit command template
│   └── fix.md           # NEW: /reforge.fix command template
├── schemas/
│   ├── audit-report.md  # NEW: Audit report XML schema
│   └── correction-plan.md # NEW: Correction plan XML schema
└── scripts/bash/
    └── check-prerequisites.sh  # EXISTING: May need --require-audit flag support
```

**Structure Decision**: This feature adds 4 new files to the existing `.reforge/` framework structure. No new directories are needed — the audit output files (`audit-report.xml`, `correction-plan.xml`) are stored in `reforge_output/<project>/audit/` at runtime.

## Complexity Tracking

> No constitution violations to justify.
