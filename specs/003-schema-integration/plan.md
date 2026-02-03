# Implementation Plan: Schema Integration for Reforge Workflow

**Branch**: `003-schema-integration` | **Date**: 2026-01-29 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-schema-integration/spec.md`

## Summary

Ensure schema consistency across the Reforge framework by verifying markdown schemas in `.reforge/schemas/` are complete, command templates explicitly reference their output schemas, and XSD contract traceability is maintained. This is a documentation/template quality improvement with no runtime dependencies.

## Technical Context

**Language/Version**: Markdown (documentation only - no compiled code per Constitution Principle I)
**Primary Dependencies**: None (LLM-native tools only: Read, Write, Glob, Grep)
**Storage**: N/A (file-based markdown and XML schemas)
**Testing**: Manual validation via schema-to-output comparison
**Target Platform**: Any AI coding assistant (agent-agnostic per Constitution Principle V)
**Project Type**: Documentation/template improvement
**Performance Goals**: N/A (one-time documentation task)
**Constraints**: Must comply with Constitution principles I-VI; no runtime dependencies
**Scale/Scope**: 10 markdown schema files, 9 command templates, 8 XSD contracts

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Evidence |
|-----------|--------|----------|
| **I. LLM-First Architecture** | ✅ PASS | No compiled code, parsers, or runtime tools. All work uses LLM-native file operations (Read, Write, Glob) |
| **II. Prompt Template Commands** | ✅ PASS | Updates existing command templates in `.reforge/commands/`; follows `/reforge.<action>` naming |
| **III. Structured Output (XML/Markdown)** | ✅ PASS | Enhances schema documentation in `.reforge/schemas/`; maintains XML+Markdown structured output |
| **IV. Installable via CLI Bootstrap** | ✅ PASS | No new dependencies introduced; schema files are markdown, copied during install |
| **V. Agent-Agnostic Design** | ✅ PASS | Schema documentation uses "The agent MUST..." phrasing; no agent-specific features |
| **VI. Extensibility via Tooling Layer** | ✅ PASS | XSD contracts remain optional development artifacts; core workflow uses markdown schemas only |

**GATE RESULT**: ✅ ALL PRINCIPLES SATISFIED - Proceed to Phase 0

## Project Structure

### Documentation (this feature)

```text
specs/003-schema-integration/
├── plan.md              # This file
├── research.md          # Phase 0 output - schema gap analysis
├── data-model.md        # Phase 1 output - entity relationships
├── quickstart.md        # Phase 1 output - implementation guide
└── contracts/           # N/A - no new API contracts for this feature
```

### Source Code (repository root)

```text
.reforge/
├── commands/           # Target: Add schema references to command templates
│   ├── extract.md      # References business-rules, database, ui-flows, workflows schemas
│   ├── generate.md     # References user-stories schema
│   ├── audit.md        # References audit-report schema
│   └── fix.md          # References correction-plan schema
├── schemas/            # Target: Ensure completeness and XSD traceability
│   ├── analysis.md
│   ├── business-rules.md
│   ├── database.md
│   ├── ui-flows.md
│   ├── workflows.md
│   ├── user-stories.md
│   ├── cross-mappings.md
│   ├── features-requirements.md
│   ├── audit-report.md
│   └── correction-plan.md
└── memory/
    └── constitution.md # Reference for compliance validation
```

**Structure Decision**: No new directories needed. This feature updates existing files in `.reforge/commands/` and `.reforge/schemas/`.

## Complexity Tracking

> No violations. This feature is purely documentation/template enhancement with zero runtime complexity.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| *None* | N/A | N/A |

---

## Post-Design Constitution Re-Check

*Re-evaluated after Phase 1 design artifacts completed.*

| Principle | Status | Post-Design Evidence |
|-----------|--------|---------------------|
| **I. LLM-First Architecture** | ✅ PASS | Design adds markdown documentation only; no parsers or runtime tools |
| **II. Prompt Template Commands** | ✅ PASS | Updates maintain command template format in `.reforge/commands/` |
| **III. Structured Output (XML/Markdown)** | ✅ PASS | Schema files remain structured markdown with XML examples |
| **IV. Installable via CLI Bootstrap** | ✅ PASS | All changes are markdown files deployable via copy |
| **V. Agent-Agnostic Design** | ✅ PASS | No agent-specific references introduced |
| **VI. Extensibility via Tooling Layer** | ✅ PASS | XSD contracts remain in development specs (not deployed) |

**POST-DESIGN GATE**: ✅ ALL PRINCIPLES SATISFIED - Ready for `/speckit.tasks`

---

## Generated Artifacts

| Artifact | Path | Status |
|----------|------|--------|
| Implementation Plan | `specs/003-schema-integration/plan.md` | ✅ Complete |
| Research | `specs/003-schema-integration/research.md` | ✅ Complete |
| Data Model | `specs/003-schema-integration/data-model.md` | ✅ Complete |
| Quickstart Guide | `specs/003-schema-integration/quickstart.md` | ✅ Complete |
| Contracts | N/A (no new APIs) | N/A |

## Files to Modify (Implementation)

| File | Change | Priority |
|------|--------|----------|
| `.reforge/schemas/audit-report.md` | Add Contract Reference section | 1 |
| `.reforge/schemas/correction-plan.md` | Add Contract Reference section | 1 |
| `.reforge/schemas/cross-mappings.md` | Add Schema Notes section | 2 |
| `.reforge/schemas/features-requirements.md` | Add Schema Notes section | 2 |
| `.reforge/commands/fix.md` | Add Output Schema References section | 3 |
