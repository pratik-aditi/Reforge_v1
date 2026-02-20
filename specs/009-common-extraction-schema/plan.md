# Implementation Plan: Common Extraction Schema

**Branch**: `009-common-extraction-schema` | **Date**: 2026-02-20 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/009-common-extraction-schema/spec.md`

## Summary

Define a common extraction schema that standardizes the structural contract (root attributes, metadata, source references, confidence vocabulary, ID patterns) shared across all four extraction types. Deliver as both markdown (`common-schema.md`) and XSD (`common-schema.xsd`), update all type-specific schemas to reference the common schema, and add a validation gate to the extract command template.

## Technical Context

**Language/Version**: Markdown prompt templates + XSD 1.0 (no compiled code per Constitution Principle I)
**Primary Dependencies**: None — LLM-native tools only (Read, Write, Glob, Grep)
**Storage**: XML files for extraction output; markdown for schema definitions; XSD for formal schema
**Testing**: Manual validation — LLM agent reads schema definition and verifies extraction output structure
**Target Platform**: Any capable AI coding assistant (agent-agnostic per Constitution Principle V)
**Project Type**: Single — framework of prompt templates and schemas
**Performance Goals**: N/A — schema definition feature, no runtime execution
**Constraints**: Zero dependencies (Constitution I), agent-agnostic (Constitution V), all files under `.reforge/`
**Scale/Scope**: 4 extraction types, ~12 files to create or modify

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Evidence |
|-----------|--------|----------|
| I. LLM-First Architecture | ✅ PASS | All deliverables are markdown + XSD files. Validation gate uses agent's native Read tool to check output against schema — no external XML validators. |
| II. Prompt Template Commands | ✅ PASS | Extract command template (`.reforge/commands/extract.md`) updated with validation gate section. No new commands created. |
| III. Structured Output | ✅ PASS | This feature directly strengthens Principle III by standardizing XML output structure across all extraction types. |
| IV. Installable via CLI Bootstrap | ✅ PASS | New files placed under `.reforge/schemas/` — part of the installable framework directory. |
| V. Agent-Agnostic Design | ✅ PASS | Schema definitions use "the agent" language. No agent-specific tool references. Markdown schema is universally readable. |
| VI. Extensibility via Tooling Layer | ✅ PASS | XSD files serve as optional formal schema for potential future tooling validation. Core workflow uses markdown schema read by agent. |

**Gate result**: ALL PASS — proceed to Phase 0.

### Post-Phase 1 Re-Check

| Principle | Status | Notes |
|-----------|--------|-------|
| I. LLM-First | ✅ PASS | Validation gate reads `common-schema.md` via Read tool. No compiled validators. |
| II. Prompt Templates | ✅ PASS | Extract command template gets new Step 5.6 — still a markdown prompt template. |
| III. Structured Output | ✅ PASS | Common schema strengthens structured output with standardized metadata, source refs. |
| IV. CLI Bootstrap | ✅ PASS | `common-schema.md` and `common-schema.xsd` added to `.reforge/schemas/` — installed by bootstrap. |
| V. Agent-Agnostic | ✅ PASS | Contract uses "the agent" language throughout. Markdown is universally readable. |
| VI. Extensibility | ✅ PASS | XSD layer is optional enhancement. Core validation uses markdown schema. |

**Post-design gate result**: ALL PASS — no violations introduced by design artifacts.

## Project Structure

### Documentation (this feature)

```text
specs/009-common-extraction-schema/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── common-schema-contract.md
└── tasks.md             # Phase 2 output (/speckit.tasks)
```

### Source Code (repository root)

```text
.reforge/
├── schemas/
│   ├── common-schema.md        # NEW — authoritative common schema definition
│   ├── business-rules.md       # MODIFIED — link to common-schema.md, remove shared element definitions
│   ├── database.md             # MODIFIED — link to common-schema.md, remove shared element definitions
│   ├── ui-flows.md             # MODIFIED — link to common-schema.md, remove shared element definitions
│   ├── workflows.md            # MODIFIED — link to common-schema.md, remove shared element definitions
│   └── xsd/
│       ├── common-schema.xsd   # NEW — shared XSD types (ConfidenceType, SourceReferenceType, MetadataType)
│       ├── business-rules.xsd  # MODIFIED — xs:include common-schema.xsd, remove duplicate types
│       ├── database.xsd        # MODIFIED — xs:include common-schema.xsd, remove duplicate types
│       ├── ui-flows.xsd        # MODIFIED — xs:include common-schema.xsd, remove duplicate types
│       └── workflows.xsd       # MODIFIED — xs:include common-schema.xsd, remove duplicate types
├── commands/
│   └── extract.md              # MODIFIED — add validation gate section referencing common schema
└── memory/
    └── (no changes)
```

**Structure Decision**: No new directories created. All files go into existing `.reforge/schemas/` and `.reforge/schemas/xsd/` directories. One new file per layer (markdown + XSD) plus modifications to 9 existing files.

## Complexity Tracking

> No constitution violations. Table not needed.
