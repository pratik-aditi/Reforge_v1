# Implementation Plan: XSD Validation Tooling

**Branch**: `004-xsd-validation-tooling` | **Date**: 2026-01-29 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/004-xsd-validation-tooling/spec.md`

## Summary

Add optional XSD validation tooling to Reforge that:
1. Deploys XSD schemas from `specs/*/contracts/` to `.reforge/schemas/xsd/` during install/update
2. Provides a `reforge-scripts validate-xml` CLI command that invokes `xmllint` for validation
3. Returns structured, LLM-parseable error output for self-correction workflows

This is an **optional tooling enhancement** per Constitution Principle VI — core workflow remains functional without it.

## Technical Context

**Language/Version**: Python 3.11 (extending existing reforge-cli package)
**Primary Dependencies**: typer, rich (existing); xmllint from libxml2 (external, optional)
**Storage**: XSD files deployed to `.reforge/schemas/xsd/`; no database
**Testing**: pytest (existing test infrastructure)
**Target Platform**: macOS, Linux, WSL (cross-platform bash/Python)
**Project Type**: Single CLI package (existing structure)
**Performance Goals**: <5 seconds validation for files <1MB
**Constraints**: Must work without xmllint (graceful error with install guidance)
**Scale/Scope**: 8 XSD schemas currently; validation of individual XML files

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. LLM-First Architecture | ✅ PASS | Validation is optional tooling; core LLM workflow unchanged |
| II. Prompt Template Commands | ✅ PASS | No new slash commands required; validation is helper script |
| III. Structured Output | ✅ PASS | Structured error format designed for LLM parsing |
| IV. Installable via CLI Bootstrap | ✅ PASS | XSD deployment integrated into existing install/update |
| V. Agent-Agnostic Design | ✅ PASS | Bash/Python script callable by any agent |
| VI. Extensibility via Tooling Layer | ✅ PASS | Explicitly optional tooling that enhances but doesn't replace |

**Gate Result**: ✅ PASSED — No violations

## Project Structure

### Documentation (this feature)

```text
specs/004-xsd-validation-tooling/
├── spec.md              # Feature specification
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output (validation result structure)
├── quickstart.md        # Phase 1 output (validation usage guide)
└── tasks.md             # Phase 2 output (/speckit.tasks command)
```

### Source Code (repository root)

```text
src/reforge_cli/
├── __init__.py          # Main CLI (modify: add validate-xml command)
└── scripts/
    ├── __init__.py      # Script exports (modify: add validation)
    ├── common.py        # Shared utilities (existing)
    └── validation.py    # NEW: XSD validation logic

.reforge/
├── schemas/
│   ├── *.md             # Existing markdown schemas
│   └── xsd/             # NEW: XSD schema files (deployed on install)
│       ├── analysis.xsd
│       ├── business-rules.xsd
│       ├── database.xsd
│       ├── ui-flows.xsd
│       ├── workflows.xsd
│       ├── user-stories.xsd
│       ├── audit-report.xsd
│       └── correction-plan.xsd

tests/
├── test_scripts.py      # Existing (modify: add validation tests)
└── fixtures/
    └── validation/      # NEW: Test XML files
        ├── valid-analysis.xml
        └── invalid-analysis.xml
```

**Structure Decision**: Extend existing `src/reforge_cli/scripts/` module with new `validation.py`. XSD files deployed to `.reforge/schemas/xsd/` subdirectory to keep separate from markdown schemas.

## Complexity Tracking

> No violations requiring justification — feature aligns with Constitution Principle VI.

| Aspect | Assessment |
|--------|------------|
| New code volume | ~200 lines Python (validation.py) |
| Dependencies | None new (xmllint is external/optional) |
| Integration points | 2 (install/update, new CLI command) |
| Risk | Low — isolated optional tooling |
