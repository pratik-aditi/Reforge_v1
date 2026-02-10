# Implementation Plan: GitHub Copilot Slash Command Support

**Branch**: `005-copilot-support` | **Date**: 2026-02-09 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/005-copilot-support/spec.md`

## Summary

Add a `--copilot` flag to the Reforge CLI that installs Copilot-specific agent files (`.github/agents/reforge.*.agent.md`), companion prompt files (`.github/prompts/reforge.*.prompt.md`), and VS Code workspace settings (`.vscode/settings.json`) — mirroring the spec-kit pattern. The implementation extends the existing `--claude` installation pipeline with parallel Copilot generation functions, sharing the same `.reforge/` framework files.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: Typer (CLI framework), Rich (console output)
**Storage**: Filesystem (markdown files, JSON config)
**Testing**: pytest with Typer CliRunner (141 existing tests in `tests/test_scripts.py`)
**Target Platform**: macOS, Linux, Windows (cross-platform CLI)
**Project Type**: Single Python package
**Performance Goals**: N/A (CLI tool, single invocation)
**Constraints**: Zero runtime dependencies for the framework itself; CLI is the optional tooling layer
**Scale/Scope**: 9 command templates to generate agent/prompt files for

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. LLM-First Architecture | PASS | No new parsers or runtime dependencies. Copilot agents load the same prompt templates |
| II. Prompt Template Commands | PASS | Commands remain in `.reforge/commands/`. Agent files are wrappers that reference them |
| III. Structured Output | N/A | This feature generates installation files, not analysis output |
| IV. Installable via CLI Bootstrap | PASS | `reforge --copilot <path>` is the bootstrap command |
| V. Agent-Agnostic Design | PASS | Prompt templates remain agent-agnostic. Agent-specific files are generated wrappers only |
| VI. Extensibility via Tooling Layer | PASS | CLI installation is the optional tooling layer; core workflow still functions without it |

All gates pass. No violations requiring justification.

## Project Structure

### Documentation (this feature)

```text
specs/005-copilot-support/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
└── tasks.md             # Phase 2 output (/speckit.tasks command)
```

### Source Code (repository root)

```text
src/reforge_cli/
├── __init__.py          # CLI entry point — add --copilot flag, copilot install/update/remove functions
└── scripts/
    └── __init__.py      # No changes needed (reforge-scripts works agent-agnostically)

tests/
└── test_scripts.py      # Add Copilot install/update/remove test classes
```

**Structure Decision**: Single-project layout. All changes are in `src/reforge_cli/__init__.py` (CLI entry point) and `tests/test_scripts.py` (test suite). No new modules needed — the Copilot generation functions follow the same pattern as the existing Claude wrapper generation.

## Design Decisions

### D1: Copilot Agent File Format

Generated `.agent.md` files follow FR-007 requirements:
- **YAML frontmatter with `description` field** — extracted from command template's first `>` blockquote line
- Body contains a Load-and-Execute instruction pointing to `.reforge/commands/<name>.md`

Example `reforge.analyze.agent.md`:
```markdown
---
description: Scan and inventory a legacy codebase
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Execution

Load and execute the full command template at `.reforge/commands/analyze.md`.
Follow all steps defined in that file exactly as written, passing through any
arguments provided above.
```

### D2: Prompt File Format

Minimal YAML-only files following spec-kit convention:
```markdown
---
agent: reforge.analyze
---
```

### D3: VS Code Settings Structure

Following spec-kit's `vscode-settings.json` pattern:
```json
{
    "chat.promptFilesRecommendations": {
        "reforge.analyze": true,
        "reforge.extract": true,
        ...
    },
    "chat.tools.terminal.autoApprove": {
        "reforge-scripts ": true
    }
}
```

### D4: Installation Detection

- `--copilot --update` detects existing installation by checking for `.github/agents/reforge.*.agent.md` files (per clarification session)
- `--copilot` fresh install checks for `.reforge/` directory existence (shared guard)

### D5: Removal Strategy

- `--remove` is a full uninstall: removes `.reforge/`, Claude wrappers, Copilot agents/prompts, VS Code settings entries, and gitignore entries (per clarification session)
- Non-Reforge files in `.github/`, `.vscode/`, `.claude/` are preserved

### D6: Code Organization

New functions added to `__init__.py` following existing patterns:

| Function | Purpose | Mirrors |
|----------|---------|---------|
| `generate_copilot_agents()` | Create `.github/agents/reforge.*.agent.md` | `generate_wrappers()` |
| `generate_copilot_prompts()` | Create `.github/prompts/reforge.*.prompt.md` | N/A (new) |
| `merge_vscode_settings()` | Create/merge `.vscode/settings.json` | `merge_settings()` |

The existing `do_install()`, `do_update()`, `do_remove()` functions will be extended with a `mode` parameter (or the `cli()` callback will dispatch to mode-specific logic) to call the appropriate generation functions.

## Complexity Tracking

No violations to justify. All changes follow existing patterns.
