# Implementation Plan: Project Plan Command

**Branch**: `008-project-plan` | **Date**: 2026-02-20 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/008-project-plan/spec.md`

## Summary

Add a `/reforge.plan` command that creates and manages a workflow-oriented project plan file at `.reforge/memory/project-plan.md`. The plan uses markdown checkboxes with inline HTML comment tags for machine matching, enabling all 10 existing Reforge commands to auto-update their corresponding checkboxes via a new standardized Step 0.7 pattern. Each workflow group follows a 7-step pipeline: extract → clarify → audit → fix → generate → audit generated → fix generated.

## Technical Context

**Language/Version**: Markdown prompt templates (no compiled code per Constitution Principle I)
**Primary Dependencies**: None — LLM-native tools only (Read, Write, Glob, Grep)
**Storage**: Filesystem — `.reforge/memory/project-plan.md` (structured markdown)
**Testing**: Manual validation via sample legacy codebases
**Target Platform**: Any AI agent environment (Claude Code, GitHub Copilot, etc.)
**Project Type**: Prompt template framework (no source code directories)
**Performance Goals**: Plan creation under 5 minutes of interactive input (SC-001)
**Constraints**: Zero dependencies, agent-agnostic language, LLM-first architecture
**Scale/Scope**: 1 new command template + 10 existing templates modified + 1 constitution update

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Evidence |
|-----------|--------|----------|
| I. LLM-First Architecture | ✅ PASS | `plan.md` is a prompt template; `project-plan.md` is generated/read/written by the LLM using native tools. No compiled code, no parsers. |
| II. Prompt Template Commands | ✅ PASS | Command defined as `.reforge/commands/plan.md`. Self-contained with clear inputs, steps, and outputs. Follows `/reforge.<action>` naming. |
| III. Structured Output (XML/Markdown) | ✅ PASS | Plan file is structured markdown with HTML comment tags for machine traceability. Human-readable and LLM-parseable. |
| IV. Installable via CLI Bootstrap | ✅ PASS | `plan.md` deployed via framework file copy (same as all other commands). No new runtime dependencies. |
| V. Agent-Agnostic Design | ✅ PASS | All prompt templates use "The agent MUST..." language. No agent-specific features required. |
| VI. Extensibility via Tooling Layer | ✅ PASS | Plan is optional — all commands work without it (FR-011). Optional tooling could add plan visualization without replacing core workflow. |

**Gate result**: PASS — No violations. Proceed to Phase 0.

## Project Structure

### Documentation (this feature)

```text
specs/008-project-plan/
├── plan.md              # This file
├── spec.md              # Feature specification
├── research.md          # Phase 0 output: design decisions
├── data-model.md        # Phase 1 output: entity model
├── quickstart.md        # Phase 1 output: implementation summary
└── contracts/           # Phase 1 output: interface contracts
    ├── plan-command-interface.md   # /reforge.plan command contract
    ├── plan-file-format.md        # project-plan.md format spec
    └── step-07-integration.md     # Step 0.7 pattern for all commands
```

### Source Code (repository root)

```text
.reforge/
├── commands/
│   ├── plan.md          # CREATE: /reforge.plan command template
│   ├── init.md          # MODIFY: Add Step 0.7
│   ├── analyze.md       # MODIFY: Add Step 0.7
│   ├── profile.md       # MODIFY: Add Step 0.7
│   ├── extract.md       # MODIFY: Add Step 0.7
│   ├── clarify.md       # MODIFY: Add Step 0.7
│   ├── generate.md      # MODIFY: Add Step 0.7
│   ├── status.md        # MODIFY: Add Step 0.7 (read-only variant + plan progress display)
│   ├── reanalyze.md     # MODIFY: Add Step 0.7
│   ├── audit.md         # MODIFY: Add Step 0.7
│   └── fix.md           # MODIFY: Add Step 0.7
├── memory/
│   ├── constitution.md  # MODIFY: Add plan.md to architecture, update command workflow
│   └── project-plan.md  # OUTPUT: Generated at runtime by /reforge.plan
└── config.json          # NO CHANGE
```

**Structure Decision**: No new directories created. The plan command template goes in the existing `.reforge/commands/` directory. The plan output file goes in the existing `.reforge/memory/` directory. This follows the established pattern exactly.

## Complexity Tracking

> No Constitution Check violations to justify. All principles pass cleanly.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| (none) | — | — |

## Post-Design Constitution Re-Check

| Principle | Status | Post-Design Notes |
|-----------|--------|-------------------|
| I. LLM-First | ✅ PASS | Plan file parsing uses string search (Grep/Read), plan writing uses Write. No external tools. |
| II. Prompt Templates | ✅ PASS | `plan.md` follows exact same structure as existing commands (syntax, arguments, overview, workflow sections). |
| III. Structured Output | ✅ PASS | HTML comment tags (`<!-- reforge:command:type -->`) provide machine-readable traceability within human-readable markdown. |
| IV. CLI Bootstrap | ✅ PASS | Only adds `plan.md` to the commands directory — deployed identically to all other commands. |
| V. Agent-Agnostic | ✅ PASS | Step 0.7 pattern uses "The agent" language. Tag matching is simple string search available in any agent. |
| VI. Extensibility | ✅ PASS | Plan is explicitly optional (FR-011). Step 0.7 silently skips when no plan exists. |

**Post-design gate result**: PASS — Design is fully constitutional.
