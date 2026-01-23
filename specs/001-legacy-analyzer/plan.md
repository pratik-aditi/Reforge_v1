# Implementation Plan: Reforge Legacy Analyzer Framework

**Branch**: `001-legacy-analyzer` | **Date**: 2025-01-13 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-legacy-analyzer/spec.md`

## Summary

Reforge is an LLM-driven framework for legacy codebase analysis that enables AI agents to inventory, analyze, and document legacy applications without external parsers or compiled code. The framework consists entirely of prompt templates, XML schemas, and configuration files—following the SpecKit pattern. Users invoke slash commands (`/reforge.analyze`, `/reforge.extract`, `/reforge.generate`) to scan codebases, extract business rules/database/UI/workflows with source traceability, and generate documentation including modernization user stories.

## Technical Context

**Language/Version**: Markdown prompt templates (no compiled language)
**Primary Dependencies**: None - LLM-native tools only (Read, Write, Glob, Grep)
**Storage**: XML files for analysis output, structured markdown for documentation
**Testing**: Manual validation via sample legacy codebases; idempotency checks
**Target Platform**: Any AI coding assistant with file read/write capabilities
**Project Type**: Single project - prompt template framework
**Performance Goals**: 1000-file codebase inventory in <2 hours; resume within 30 seconds
**Constraints**: Zero external dependencies; agent-agnostic design; all analysis via LLM
**Scale/Scope**: Target codebases up to 10,000+ files; outputs may span multiple XML files

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Evidence |
|-----------|--------|----------|
| **I. LLM-First Architecture** | ✅ PASS | FR-016 mandates "operate entirely through AI agent native tools with no external parsers or compiled code" |
| **II. Prompt Template Commands** | ✅ PASS | FR-017 requires "slash command prompt templates following the SpecKit pattern"; constitution defines commands in `.reforge/commands/` |
| **III. Structured Output (XML/Markdown)** | ✅ PASS | FR-007 requires "structured XML files with defined schemas"; FR-008/FR-009 specify markdown/UML generation; FR-019/FR-020 define storage locations |
| **IV. Installable via CLI Bootstrap** | ✅ PASS | Constitution specifies `specify init <project> --template reforge`; all files under `.reforge/` directory |
| **V. Agent-Agnostic Design** | ✅ PASS | FR-016 uses only common tool patterns (Read, Write, Glob, Grep); no agent-specific features required |
| **VI. Extensibility via Tooling Layer** | ✅ PASS | Optional tools separated in `.reforge/tools/`; core workflow functions without them |

**Gate Status**: ✅ ALL PRINCIPLES SATISFIED - Proceed to Phase 0

## Project Structure

### Documentation (this feature)

```text
specs/001-legacy-analyzer/
├── plan.md              # This file
├── spec.md              # Feature specification
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (XML schemas)
│   ├── analysis.xsd
│   ├── business-rules.xsd
│   ├── database.xsd
│   ├── ui-flows.xsd
│   ├── workflows.xsd
│   └── user-stories.xsd
├── checklists/          # Validation checklists
│   └── requirements.md
└── tasks.md             # Phase 2 output (/speckit.tasks)
```

### Source Code (repository root)

```text
.reforge/
├── commands/              # Slash command prompt templates
│   ├── analyze.md         # /reforge.analyze - Codebase inventory
│   ├── extract.md         # /reforge.extract [type] - Extract elements
│   ├── generate.md        # /reforge.generate [format] - Generate docs
│   ├── clarify.md         # /reforge.clarify - Resolve ambiguities
│   ├── status.md          # /reforge.status - Progress reporting
│   └── reanalyze.md       # /reforge.reanalyze - Incremental re-analysis
├── schemas/               # XML schema documentation (human-readable)
│   ├── analysis.md
│   ├── business-rules.md
│   ├── database.md
│   ├── ui-flows.md
│   ├── workflows.md
│   └── user-stories.md
├── templates/             # Output templates for generation
│   ├── user-story.md
│   ├── data-dictionary.md
│   ├── uml-class.md
│   ├── sysml-block.md
│   └── ascii-layout.md
├── memory/                # Project-specific state
│   ├── constitution.md    # Framework principles
│   ├── checkpoints/       # Analysis checkpoint XML files
│   ├── clarifications/    # Stored clarification decisions
│   └── logs/              # Analysis transparency logs
├── config.json            # Framework configuration
└── README.md              # Framework documentation

reforge_output/            # Analysis outputs (per-project)
└── <project-name>/
    ├── analysis.xml       # Main codebase inventory
    ├── business-rules.xml # Extracted business rules
    ├── database.xml       # Database interactions
    ├── ui-flows.xml       # UI component definitions
    ├── workflows.xml      # Process flows
    └── generated/         # Generated documentation
        ├── user-stories.md
        ├── user-stories.json
        ├── data-dictionary.md
        └── diagrams/
```

**Structure Decision**: Single project structure using prompt templates only. The `.reforge/` directory contains all framework files (commands, schemas, templates, memory). Analysis outputs go to `reforge_output/<project-name>/` following the SpecKit pattern where specs go to `specs/<feature>/`.

## Complexity Tracking

> No violations requiring justification. All constitutional principles are satisfied by the design.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| *None* | — | — |
