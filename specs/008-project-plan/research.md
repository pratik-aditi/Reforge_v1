# Research: Project Plan Command

**Feature**: 008-project-plan
**Date**: 2026-02-20

## Research Questions

### R1: Tag Naming Convention for All Plan Items

**Decision**: Use `<!-- reforge:<command>[:<type>] -->` with compound command names for the audit/fix-generated phase.

**Rationale**: The tag must be unique per plan item and parseable by any command's Step 0.7 implementation. Setup items have no type qualifier; workflow group items include the extraction type. The 7-step pipeline introduces two audit/fix cycles (one for extractions, one for generated output), requiring disambiguation.

**Tag Convention**:

| Pipeline Step | Tag Pattern | Example |
|---------------|-------------|---------|
| Init | `<!-- reforge:init -->` | `- [ ] Initialize project context <!-- reforge:init -->` |
| Analyze | `<!-- reforge:analyze -->` | `- [ ] Analyze codebase <!-- reforge:analyze -->` |
| Profile | `<!-- reforge:profile -->` | `- [ ] Generate extraction profile <!-- reforge:profile -->` |
| Extract | `<!-- reforge:extract:<type> -->` | `<!-- reforge:extract:business-rules -->` |
| Clarify | `<!-- reforge:clarify:<type> -->` | `<!-- reforge:clarify:business-rules -->` |
| Audit (extractions) | `<!-- reforge:audit:<type> -->` | `<!-- reforge:audit:business-rules -->` |
| Fix (extractions) | `<!-- reforge:fix:<type> -->` | `<!-- reforge:fix:business-rules -->` |
| Generate | `<!-- reforge:generate:<type> -->` | `<!-- reforge:generate:business-rules -->` |
| Audit (generated) | `<!-- reforge:audit-generated:<type> -->` | `<!-- reforge:audit-generated:business-rules -->` |
| Fix (generated) | `<!-- reforge:fix-generated:<type> -->` | `<!-- reforge:fix-generated:business-rules -->` |
| Custom | `<!-- reforge:custom:<slug> -->` | `<!-- reforge:custom:review-architecture -->` |

**Alternatives considered**:
- Three-part tags (`<!-- reforge:audit:business-rules:generated -->`) — rejected because it changes the established `<command>:<type>` pattern and complicates parsing
- Numeric IDs (`<!-- reforge:item-042 -->`) — rejected because they lose semantic meaning and require a lookup table

---

### R2: Command-to-Plan-Item Mapping for Multi-Target Commands

**Decision**: Commands that operate on a specific extraction type mark the corresponding workflow group item. Commands that operate across all types mark multiple items.

**Rationale**: Most Reforge commands already accept a type argument (extract takes `business-rules`, audit takes `business-rules`, generate takes `--scope business-rules`). The Step 0.7 implementation can derive the tag from the command name + type argument. Commands that don't target a specific type need special handling.

**Mapping Rules**:

| Command | Plan Item Resolution |
|---------|---------------------|
| `/reforge.init` | Mark `<!-- reforge:init -->` |
| `/reforge.analyze` | Mark `<!-- reforge:analyze -->` |
| `/reforge.profile` | Mark `<!-- reforge:profile -->` |
| `/reforge.extract <type>` | Mark `<!-- reforge:extract:<type> -->` |
| `/reforge.clarify --category <type>` | Mark `<!-- reforge:clarify:<type> -->` |
| `/reforge.clarify` (no category) | Do not auto-mark any clarify items (user marks manually or agent infers from session) |
| `/reforge.audit <type>` | Mark `<!-- reforge:audit:<type> -->` |
| `/reforge.audit` (no type, full audit) | Mark all `<!-- reforge:audit:<type> -->` items for types that were audited |
| `/reforge.fix --type <type>` | Mark `<!-- reforge:fix:<type> -->` |
| `/reforge.fix` (no type) | Mark all `<!-- reforge:fix:<type> -->` items for types that were fixed |
| `/reforge.generate <format> --scope <type>` | Mark `<!-- reforge:generate:<type> -->` |
| `/reforge.generate <format>` (no scope) | Mark all `<!-- reforge:generate:<type> -->` items for types whose extractions contributed to the output |
| `/reforge.reanalyze` | Mark `<!-- reforge:analyze -->` if not already checked (re-analysis refreshes the same artifact) |
| `/reforge.status` | No item to mark — reads plan and includes progress in its report |

**Alternatives considered**:
- Always require explicit type for plan marking — rejected because full-scope commands (audit all, fix all) should mark everything they touch
- Single generic audit/fix/generate checkboxes — rejected because per-type tracking is more granular and useful

---

### R3: Step 0.7 Standardized Pattern

**Decision**: Two-phase pattern (read on start, write on completion) matching the structure of Step 0.5 and Step 0.6. Each command template gets the same boilerplate with command-specific tag derivation.

**Rationale**: Consistency with existing Step 0.5/0.6 patterns ensures predictable behavior. The pattern must handle: plan exists, plan missing, tag found, tag not found, already checked, write failure.

**Standardized Step 0.7 Template**:

```markdown
### Step 0.7: Check/Update Project Plan

If `.reforge/memory/project-plan.md` exists, read it now.

**On command start:**
- Parse the plan file to count total items and completed items
- Display: "📋 Project Plan: X/Y items complete (Z%)"
- Identify items relevant to this command and display their status

**On command completion (success only):**
- Locate the plan item by searching for `<!-- reforge:<COMMAND_TAG> -->`
- If found and unchecked (`- [ ]`): change to `- [x]` and append ` *(completed: YYYY-MM-DD)*`
- If found and already checked (`- [x]`): leave unchanged (idempotent)
- If tag not found: emit warning — "⚠️ No plan item found for <operation>. Run /reforge.plan to add it."
- If file write fails: emit warning — "⚠️ Could not update project plan. Plan may be out of sync." Continue without failing.

If `.reforge/memory/project-plan.md` does not exist, skip this step silently.
The project plan is optional — its absence MUST NOT affect command behavior.
```

**Alternatives considered**:
- Read-only pattern (only display, never write) — rejected because auto-update is the primary value proposition
- Write-only pattern (update without displaying status) — rejected because showing plan context on start helps the user understand where they are in the workflow

---

### R4: Plan File Markdown Structure

**Decision**: YAML-style metadata header, followed by Setup section, then Workflow Group sections, then optional Custom Tasks.

**Rationale**: YAML frontmatter is widely supported by markdown renderers. Workflow groups use H2 headings for visual separation. Each group's 7 steps are an ordered checklist under the group heading.

**Plan File Template**:

```markdown
# Project Plan

**Project**: <project-name>
**Created**: YYYY-MM-DD
**Last Updated**: YYYY-MM-DD

## Setup

- [ ] Initialize project context <!-- reforge:init -->
- [ ] Analyze codebase <!-- reforge:analyze -->
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
...

## Custom Tasks

- [ ] <user-defined task> <!-- reforge:custom:<slug> -->
```

**Alternatives considered**:
- JSON or XML plan format — rejected per Constitution Principle III (markdown is human-editable and human-readable)
- YAML frontmatter with `---` delimiters — considered but plain metadata lines are simpler and don't require YAML parsing; consistent with project-context.md format

---

### R5: Duplicate Detection for Plan Add Mode

**Decision**: Match by tag pattern, not by display text. When adding items, check if `<!-- reforge:<command>:<type> -->` already exists in the file.

**Rationale**: Since users can edit display text freely (per clarification Q2), duplicate detection must use the machine-readable tag. This is a simple Grep/string-contains check.

**Algorithm**:
1. Parse the requested addition to determine command + type
2. Search plan file for `<!-- reforge:<command>:<type> -->`
3. If found: inform user the item already exists, show its current status (checked/unchecked), offer to skip
4. If not found: append to the appropriate section

**Alternatives considered**:
- Allow duplicates — rejected because it would create ambiguity when Step 0.7 tries to mark completion
- Replace existing — rejected because it could destroy completion timestamps

---

### R6: Generate Command Plan Integration

**Decision**: The `/reforge.generate` command's plan items use extraction-type-based tags (`<!-- reforge:generate:<type> -->`), not artifact-format tags.

**Rationale**: The plan is organized by workflow group (extraction type), not by output format. When a user plans "Business Rules" work, the generate step means "generate documentation FROM business rules." The generate command already accepts a `--scope <type>` flag to limit scope. Without `--scope`, the generate command should mark generate items for all extraction types that contributed to the output.

This means `/reforge.generate user-stories` (which draws from ALL extraction types) would mark `<!-- reforge:generate:business-rules -->`, `<!-- reforge:generate:database -->`, etc. for each type that had available extractions.

**Alternatives considered**:
- Artifact-format tags (`<!-- reforge:generate:user-stories -->`) — rejected because it breaks the workflow-group structure where each group tracks its own pipeline
- Single generic generate tag — rejected because it loses per-type granularity

---

### R7: Commands Without Step 0.5 — Init and Plan

**Decision**: `/reforge.init` and `/reforge.plan` get a simplified Step 0.7 that only writes (no read-on-start display for init since it's the first command; plan manages its own file directly).

**Rationale**:
- `/reforge.init` is typically the very first command run. A plan likely doesn't exist yet. If it does, init should still mark its checkbox.
- `/reforge.plan` IS the plan management command — it reads and writes the plan file as its primary function, not as a side-effect step. Step 0.7 is redundant for it. Instead, the plan command should update its own metadata (Last Updated timestamp) on every run.

**Alternatives considered**:
- Give /reforge.plan a Step 0.7 that marks a "Plan created" checkbox — rejected as circular (the plan command creates the plan file it would mark)
