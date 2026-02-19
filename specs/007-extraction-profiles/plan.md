# Implementation Plan: Extraction Profiles Command

**Branch**: `007-extraction-profiles` | **Date**: 2026-02-19 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/007-extraction-profiles/spec.md`

## Summary

Create a new `/reforge.profile` command that generates language-specific and architecture-specific extraction guidance stored in `.reforge/memory/extraction-profile.md`. The extract command loads this profile during initialization. The hardcoded "Language-Specific Extraction Rules" section is removed from extract.md entirely. The profile command supports interactive declaration, auto-discovery of languages via file extension scanning, and update mode. All changes are prompt template modifications — no compiled code, no new dependencies.

## Technical Context

**Language/Version**: Markdown (prompt templates — no compiled code per Constitution Principle I)
**Primary Dependencies**: None (LLM-native tools only: Read, Write, Glob, Grep)
**Storage**: N/A (file-based markdown prompt template)
**Testing**: Manual validation via grep verification of text presence + acceptance criteria
**Target Platform**: Any AI coding assistant (agent-agnostic per Constitution Principle V)
**Project Type**: single (framework file modification)
**Performance Goals**: N/A (prompt template, not runtime code)
**Constraints**: New command file (`.reforge/commands/profile.md`) + modification to `extract.md`; must use agent-agnostic language; auto-discovery uses the file extension mapping already established in `analyze.md`
**Scale/Scope**: 1 new file created (`profile.md` ~200-300 lines), 1 file modified (`extract.md` — remove ~23 lines, add ~10 lines for profile loading), 1 output file generated at runtime (`extraction-profile.md`)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Evidence |
|-----------|--------|----------|
| I. LLM-First Architecture | PASS | Profile command uses Glob for auto-discovery and the LLM generates all profile content; no compiled code, no external parsers |
| II. Prompt Template Commands | PASS | New command defined as `.reforge/commands/profile.md`; follows `/reforge.profile` naming pattern; self-contained with clear inputs, steps, and outputs |
| III. Structured Output (XML/Markdown) | PASS | Profile output is structured markdown stored in `.reforge/memory/extraction-profile.md`; not extraction output so XML schema not required |
| IV. Installable via CLI Bootstrap | PASS | No new dependencies; `profile.md` ships with framework files under `.reforge/commands/` |
| V. Agent-Agnostic Design | PASS | Command uses "the agent MUST" language; tools referenced (Read, Glob, Grep, Write) are common agent tool patterns |
| VI. Extensibility via Tooling Layer | PASS | No new tooling required; all profile generation is prompt-based within the command template |

**Gate Result**: ALL PASS — proceed to Phase 0.

## Project Structure

### Documentation (this feature)

```text
specs/007-extraction-profiles/
├── plan.md              # This file
├── research.md          # Phase 0 output: extraction patterns, profile structure
├── data-model.md        # Phase 1 output: profile file structure and sections
├── quickstart.md        # Phase 1 output: verification and validation guide
├── checklists/
│   └── requirements.md  # Spec quality checklist (already created)
└── tasks.md             # Phase 2 output (created by /speckit.tasks)
```

### Source Code (repository root)

```text
.reforge/
├── commands/
│   ├── profile.md       # NEW — /reforge.profile command template
│   └── extract.md       # MODIFIED — remove Language-Specific section, add profile loading
└── memory/
    └── extraction-profile.md  # GENERATED AT RUNTIME — by /reforge.profile command
```

**Structure Decision**: Two framework files affected. One new command template created (`profile.md`), one existing command modified (`extract.md`). The runtime-generated profile (`extraction-profile.md`) is not shipped with the framework — it is created per-project when the user runs `/reforge.profile`.

## Implementation Strategy

### Modification Map

| Order | File | Operation | Requirement | Description |
|-------|------|-----------|-------------|-------------|
| 1 | `.reforge/commands/profile.md` | CREATE | FR-001 through FR-005, FR-008, FR-009, FR-010, FR-011, FR-012, FR-014 | New command template: interactive workflow, auto-discovery, profile generation |
| 2 | `.reforge/commands/extract.md` | MODIFY (remove) | FR-013 | Remove "Language-Specific Extraction Rules" section (lines 979-1001 + separator) |
| 3 | `.reforge/commands/extract.md` | MODIFY (insert) | FR-006, FR-007 | Add Step 0.6 to load extraction-profile.md after existing Step 0.5 |

### Profile Command Structure (profile.md)

The command template follows the established Reforge command pattern (see `init.md` for reference):

1. **Command Syntax** — `/reforge.profile [--update]`
2. **Step 0: Check Prerequisites** — Verify `.reforge/memory/` directory exists
3. **Step 0.5: Load Project Context** — Standard pattern, pre-populate from project-context.md
4. **Step 1: Check Existing Profile** — If exists and no `--update`, ask replace/update
5. **Step 2: Gather Languages** — Interactive declaration OR auto-discovery via Glob
6. **Step 3: Gather Architecture** — Interactive declaration of architectural patterns
7. **Step 4: Gather Custom Notes** — Free-form extraction guidance from user
8. **Step 5: Generate Profile** — Write structured markdown to `.reforge/memory/extraction-profile.md`
9. **Step 6: Confirm** — Display summary, suggest running `/reforge.extract`

### Auto-Discovery Strategy (Step 2)

When the user doesn't specify languages, the command scans the codebase using the file extension mapping from `analyze.md` (lines 323-359). The agent runs Glob patterns for common extensions, tallies results, and presents discovered languages for user confirmation.

### Extract.md Modification Strategy

**Remove** (lines 979-1002): The entire "Language-Specific Extraction Rules" section including its `---` separator.

**Add** (after existing Step 0.5, around line 77): A new "Step 0.6: Load Extraction Profile" block following the established Step 0.5 pattern:
- Check if `.reforge/memory/extraction-profile.md` exists
- If present: read and apply language-specific, architecture-specific, and custom extraction guidance
- If absent: log a suggestion to run `/reforge.profile` for better results

### Agent-Agnostic Language Compliance

All text in `profile.md` and inserted text in `extract.md` must:
- Use "the agent" or "you" — not "Claude", "Copilot", etc.
- Reference common tool patterns: "Read tool", "Glob", "Grep", "Write tool"
- Not reference MCP servers, agent-specific features, or proprietary capabilities

### Verification Approach

After all modifications, verify success criteria:
1. `profile.md` exists in `.reforge/commands/`
2. `grep "Language-Specific Extraction Rules" .reforge/commands/extract.md` returns 0 results
3. `grep "extraction-profile.md" .reforge/commands/extract.md` returns match (loading directive)
4. `grep "Step 0.6" .reforge/commands/extract.md` returns match (or "Load Extraction Profile")
5. `grep -c "Claude\|Copilot" .reforge/commands/profile.md` returns 0
6. Profile command contains auto-discovery step using Glob
7. Profile command contains `--update` flag handling

## Complexity Tracking

No constitution violations. No complexity justifications needed.
