# Contract: Step 0.7 Integration Pattern

**Feature**: 008-project-plan

## Overview

Every Reforge command template receives a standardized "Step 0.7: Check/Update Project Plan" section. This step is inserted after Step 0.6 (Load Extraction Profile) or after Step 0.5 (Load Project Context) for commands that don't have Step 0.6.

## Insertion Points

| Command | Insert After | Tag(s) to Match |
|---------|-------------|-----------------|
| `init.md` | Step 7 (Write Project Context) — completion update at end | `reforge:init` |
| `analyze.md` | Step 0.5 (Load Project Context) | `reforge:analyze` |
| `profile.md` | Step 0.5 (Load Project Context) | `reforge:profile` |
| `extract.md` | Step 0.6 (Load Extraction Profile) | `reforge:extract:<type>` (from command argument) |
| `clarify.md` | Step 0.5 (Load Project Context) | `reforge:clarify:<type>` (from `--category` argument, or skip if no category) |
| `generate.md` | Step 0.5 (Load Project Context) | `reforge:generate:<type>` (from `--scope` argument, or all types with available extractions) |
| `status.md` | Step 0.5 (Load Project Context) | None — read-only (display plan progress in status report) |
| `reanalyze.md` | Step 0.5 (Load Project Context) | `reforge:analyze` (same artifact as analyze) |
| `audit.md` | Step 0.5 (Load Project Context) | `reforge:audit:<type>` when auditing extractions; `reforge:audit-generated:<type>` when auditing generated output (determined by audit target — see Special Cases) |
| `fix.md` | Step 0.5 (Load Project Context) | `reforge:fix:<type>` when fixing extractions; `reforge:fix-generated:<type>` when fixing generated output (determined by fix target — see Special Cases) |

## Standard Template

The following markdown block is added to each command template, with `<COMMAND_TAG>` replaced per the table above:

```markdown
### Step 0.7: Check/Update Project Plan

If `.reforge/memory/project-plan.md` exists, read it now.

**On command start:**
- Parse the plan file to count total items and completed items
- Display: "📋 Project Plan: X/Y items complete (Z%)"
- Identify items relevant to this command and display their status

**On command completion (success only):**
- Locate the plan item by searching for `<!-- COMMAND_TAG -->`
- If found and unchecked (`- [ ]`): change to `- [x]` and append ` *(completed: YYYY-MM-DD)*`
- If found and already checked (`- [x]`): leave unchanged (idempotent)
- If tag not found: emit warning — "⚠️ No plan item found for this operation. Run /reforge.plan to add it."
- If file write fails: emit warning — "⚠️ Could not update project plan." Continue without failing.
- Update the `**Last Updated**` metadata line to today's date

If `.reforge/memory/project-plan.md` does not exist, skip this step silently.
The project plan is optional — its absence MUST NOT affect command behavior.
```

## Special Cases

### init.md

The init command does not have Step 0.5/0.6 (it creates the project context, not loads it). Step 0.7 for init should be placed as a final step after writing project-context.md, checking for and updating `<!-- reforge:init -->`.

### status.md

The status command does NOT mark any item complete. Instead, its Step 0.7 is read-only:

```markdown
### Step 0.7: Check/Update Project Plan

If `.reforge/memory/project-plan.md` exists, read it now.

**Include in status report:**
- Display plan progress: "📋 Project Plan: X/Y items complete (Z%)"
- Per-section breakdown: Setup (X/3), <Type> (X/7) for each workflow group
- List next unchecked items as "Suggested next steps"

If `.reforge/memory/project-plan.md` does not exist, include in status report:
"No project plan found. Run /reforge.plan to create one."
```

### Commands with multi-type marking (audit, fix, generate without scope)

When a command operates on all types (no specific type argument), Step 0.7 on completion should:

1. Determine which types were processed during command execution
2. For each processed type, search for and mark the corresponding tag
3. Report how many plan items were updated

### clarify without --category

The clarify command without a category operates on all pending clarifications across types. Since clarification is interactive and may partially cover a type, Step 0.7 should NOT auto-mark clarify items. The agent or user should manually assess whether a type's clarifications are fully resolved before marking.

### audit.md and fix.md: Extraction vs. Generated Output

The audit and fix commands can operate on either extraction output or generated output. Step 0.7 must determine which context applies and mark the correct tag:

**Detection heuristic** (the agent determines context from what it operated on):
- If the audit/fix targeted files in `$PROJECT_OUTPUT_DIR/extractions/` → use `reforge:audit:<type>` or `reforge:fix:<type>`
- If the audit/fix targeted files in `$PROJECT_OUTPUT_DIR/generated/` → use `reforge:audit-generated:<type>` or `reforge:fix-generated:<type>`
- If both were processed in a single run → mark both tags

This requires no new command flags — the agent infers context from the audit report or correction plan it produced during execution.
