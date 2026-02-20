# Quickstart: Project Plan Command

**Feature**: 008-project-plan

## What This Feature Does

Adds a `/reforge.plan` command that creates and manages a checklist-based project plan at `.reforge/memory/project-plan.md`. The plan tracks all extraction, audit, and generation work across the entire Reforge workflow. All existing commands get a new Step 0.7 that reads and updates the plan automatically.

## Implementation Summary

This feature consists of **two deliverables**:

1. **New command template**: `.reforge/commands/plan.md` — the `/reforge.plan` command
2. **Step 0.7 integration**: Add a standardized "Check/Update Project Plan" step to all 10 existing command templates

There is no compiled code, no new dependencies, no new schemas. The plan file is plain markdown with HTML comment tags for machine matching.

## Key Files

| File | Action | Purpose |
|------|--------|---------|
| `.reforge/commands/plan.md` | CREATE | New command template for `/reforge.plan` |
| `.reforge/commands/init.md` | MODIFY | Add Step 0.7 |
| `.reforge/commands/analyze.md` | MODIFY | Add Step 0.7 |
| `.reforge/commands/profile.md` | MODIFY | Add Step 0.7 |
| `.reforge/commands/extract.md` | MODIFY | Add Step 0.7 |
| `.reforge/commands/clarify.md` | MODIFY | Add Step 0.7 |
| `.reforge/commands/generate.md` | MODIFY | Add Step 0.7 |
| `.reforge/commands/status.md` | MODIFY | Add Step 0.7 + plan progress display |
| `.reforge/commands/reanalyze.md` | MODIFY | Add Step 0.7 |
| `.reforge/commands/audit.md` | MODIFY | Add Step 0.7 |
| `.reforge/commands/fix.md` | MODIFY | Add Step 0.7 |
| `.reforge/memory/constitution.md` | MODIFY | Add plan.md to framework architecture, update command workflow |
| `CLAUDE.md` | MODIFY | Add `/reforge.plan` to command listing |

## Plan File Format (Output Example)

```markdown
# Project Plan

**Project**: TCOS-RUMO
**Created**: 2026-02-20
**Last Updated**: 2026-02-20

## Setup

- [x] Initialize project context <!-- reforge:init --> *(completed: 2026-02-20)*
- [x] Analyze codebase <!-- reforge:analyze --> *(completed: 2026-02-20)*
- [ ] Generate extraction profile <!-- reforge:profile -->

## Business Rules

- [ ] Extract business rules <!-- reforge:extract:business-rules -->
- [ ] Clarify business rules extractions <!-- reforge:clarify:business-rules -->
- [ ] Audit business rules extractions <!-- reforge:audit:business-rules -->
- [ ] Fix business rules extraction issues <!-- reforge:fix:business-rules -->
- [ ] Generate business rules documentation <!-- reforge:generate:business-rules -->
- [ ] Audit business rules generated docs <!-- reforge:audit-generated:business-rules -->
- [ ] Fix business rules generated doc issues <!-- reforge:fix-generated:business-rules -->

## Database

- [ ] Extract database interactions <!-- reforge:extract:database -->
- [ ] Clarify database extractions <!-- reforge:clarify:database -->
- [ ] Audit database extractions <!-- reforge:audit:database -->
- [ ] Fix database extraction issues <!-- reforge:fix:database -->
- [ ] Generate database documentation <!-- reforge:generate:database -->
- [ ] Audit database generated docs <!-- reforge:audit-generated:database -->
- [ ] Fix database generated doc issues <!-- reforge:fix-generated:database -->

## Custom Tasks

- [ ] Review architecture with team lead <!-- reforge:custom:review-architecture -->
```

## Step 0.7 Pattern (Added to Each Command)

```markdown
### Step 0.7: Check/Update Project Plan

If `.reforge/memory/project-plan.md` exists, read it now.

**On command start:**
- Parse the plan file to count total items and completed items
- Display: "📋 Project Plan: X/Y items complete (Z%)"
- Identify items relevant to this command and display their status

**On command completion (success only):**
- Locate the plan item by searching for `<!-- reforge:<COMMAND_TAG> -->`
- If found and unchecked: change to `- [x]` and append ` *(completed: YYYY-MM-DD)*`
- If found and already checked: leave unchanged (idempotent)
- If tag not found: emit warning
- If file write fails: emit warning but do not fail the command

If `.reforge/memory/project-plan.md` does not exist, skip this step silently.
```

## Constitution Impact

- **Principle I (LLM-First)**: Compliant — plan.md is a prompt template, project-plan.md is LLM-generated markdown
- **Principle II (Prompt Templates)**: Compliant — command defined as `.reforge/commands/plan.md`
- **Principle III (Structured Output)**: Compliant — plan uses structured markdown with HTML comment tags for traceability
- **Principle IV (CLI Bootstrap)**: Compliant — plan.md deployed via framework copy, no new dependencies
- **Principle V (Agent-Agnostic)**: Compliant — uses "The agent" language throughout
- **Principle VI (Extensibility)**: Compliant — plan is optional; all commands work without it (FR-011)

Constitution version bump required: 1.3.0 → 1.4.0 (MINOR — new command added to framework)
