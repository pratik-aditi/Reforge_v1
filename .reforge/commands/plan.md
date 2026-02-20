# /reforge.plan

> Create and manage a project plan for the Reforge extraction workflow

## Command Syntax

```
/reforge.plan [arguments] [--status]
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `arguments` | No | Natural language describing items to add (e.g., `"add database extraction and UML diagrams"`) |
| `--status` | No | Display progress summary without modifying the plan |

## Overview

This command creates and manages a checklist-based project plan at
`.reforge/memory/project-plan.md`. The plan tracks all extraction, audit, and
generation work across the entire Reforge workflow using markdown checkboxes
with inline HTML comment tags for machine matching.

The plan file organizes work into:

- **Setup section**: Project initialization, codebase analysis, extraction profile
- **Workflow groups**: One section per extraction type (e.g., Business Rules,
  Database), each containing a 7-step pipeline: extract → clarify → audit
  extractions → fix extractions → generate → audit generated → fix generated
- **Custom Tasks**: Optional section for user-defined items that don't fit the
  extraction pipeline

All other Reforge commands check for this plan on startup (Step 0.7) and
auto-mark their corresponding checkboxes on successful completion.

## Behavioral Modes

The command operates in one of four modes based on context:

| Condition | Mode |
|-----------|------|
| `--status` flag present | **Mode 4: Status** — display progress, do not modify |
| No existing plan, no `--status` | **Mode 1: Create** — gather input, generate plan |
| Existing plan + arguments provided | **Mode 2: Add** — append new items to existing plan |
| Existing plan + no arguments + no `--status` | **Mode 3: Interactive Review** — show status, offer to add |

---

## Workflow

### Step 0: Check Prerequisites

Verify that the `.reforge/memory/` directory exists. If it does not exist:
- Check if `.reforge/` exists at all
- If `.reforge/` is missing, instruct the user to run `/reforge.init` first
- If `.reforge/` exists but `memory/` does not, create the `memory/` subdirectory

### Step 0.5: Load Project Context

If `.reforge/memory/project-context.md` exists, read it now. Use its contents to:
- **Pre-populate project name**: Extract the project name from the Project
  Identity section for the plan metadata header
- **Technology awareness**: Note declared languages, frameworks, and databases
  for suggestion logic in Create mode

If `project-context.md` does not exist, proceed without pre-population. Note to
the user that running `/reforge.init` first provides better defaults.

### Step 1: Determine Behavioral Mode

1. **Check for `--status` flag**: If present, proceed to **Mode 4: Status**
2. **Check for existing plan**: Read `.reforge/memory/project-plan.md`
   - If the file does not exist: proceed to **Mode 1: Create**
   - If the file exists AND arguments are provided: proceed to **Mode 2: Add**
   - If the file exists AND no arguments: proceed to **Mode 3: Interactive Review**

---

## Mode 1: Create New Plan

### Step 2: Load Available Context for Suggestions

Read available context files to generate intelligent suggestions. These are all
optional — the command works without any of them.

#### 2a. Analysis-Based Suggestions

If `$PROJECT_OUTPUT_DIR/analysis/analysis.xml` exists, read it to suggest
extraction types. The agent MUST scan the analysis inventory and suggest
extraction types based on evidence:

| Evidence Found | Suggested Extraction Type |
|----------------|--------------------------|
| `.sql` files, stored procedures, database DDL | `database` |
| ORM annotations/configurations (Entity Framework, Hibernate, Django models) | `database` |
| Form files, JSP/ASPX/HTML/JSX/TSX/Vue templates | `ui` |
| Service classes, controllers, business logic files | `business-rules` |
| Batch jobs, schedulers, workflow orchestrators, message handlers | `workflows` |
| API endpoint definitions, REST controllers | `business-rules` and `workflows` |

If analysis.xml does not exist, skip analysis-based suggestions and note:
"Run `/reforge.analyze` to enable analysis-based plan suggestions."

#### 2b. Profile-Based Suggestions

If `.reforge/memory/extraction-profile.md` exists, read it to suggest targeted
sub-tasks. The agent MUST incorporate the extraction profile's insights:

- **Language-specific extractions**: If the profile declares architecture
  patterns (e.g., WCF, CQRS), suggest extraction focus areas specific to those
  patterns
- **Architecture-specific targets**: If the profile declares layered
  architecture, suggest extracting from each layer's typical locations
- **Framework patterns**: If the profile lists framework-specific patterns, note
  these as relevant extraction targets

If the profile does not exist, skip profile-based suggestions and note:
"Run `/reforge.profile` to enable language/architecture-specific plan suggestions."

### Step 3: Interactive Gathering

Ask the user to declare their intended extraction scope. Present analysis-based
and profile-based suggestions (from Step 2) as defaults the user can accept,
modify, or extend.

**Prompt 1 — Extraction Types:**

"What extraction types do you want to include in this project plan?

[If suggestions available from analysis/profile:]
Based on your project analysis, the agent suggests:
- <suggested type 1> (reason: <evidence>)
- <suggested type 2> (reason: <evidence>)
...

Standard extraction types: `business-rules`, `database`, `ui`, `workflows`

You can also declare custom extraction types (e.g., `security`,
`performance-metrics`, `api-contracts`). Custom extraction types will get the
full 7-step pipeline.

Enter the types to include (comma-separated), or 'all' for all standard types:"

**Prompt 2 — Custom Tasks:**

"Do you have any additional tasks to include in the plan that are not part of
the extraction pipeline?

Examples:
- 'Review architecture with team lead'
- 'Set up CI/CD for generated documentation'
- 'Validate extracted rules with domain experts'

Enter custom tasks (one per line, press enter twice to finish), or 'skip' to
skip:"

### Step 4: Generate Plan File

Write `.reforge/memory/project-plan.md` using the following structure:

#### Metadata Header

```markdown
# Project Plan

**Project**: <project-name>
**Created**: YYYY-MM-DD
**Last Updated**: YYYY-MM-DD
```

- `Project`: From `project-context.md` Project Identity section, or
  `config.json` `project.name`, or "Unnamed Project" if neither available
- `Created`: Today's date
- `Last Updated`: Today's date

#### Setup Section (always present)

```markdown
## Setup

- [ ] Initialize project context <!-- reforge:init -->
- [ ] Analyze codebase <!-- reforge:analyze -->
- [ ] Generate extraction profile <!-- reforge:profile -->
```

If any of these commands have already been run (detected by checking for their
output files — `project-context.md` for init, `analysis.xml` for analyze,
`extraction-profile.md` for profile), pre-mark them as complete:

```markdown
- [x] Initialize project context <!-- reforge:init --> *(completed: YYYY-MM-DD)*
```

#### Workflow Group Sections (one per declared extraction type)

For each extraction type the user declared, create a section with the full
7-step pipeline:

```markdown
## <Extraction Type Display Name>

- [ ] Extract <type> <!-- reforge:extract:<slug> -->
- [ ] Clarify <type> extractions <!-- reforge:clarify:<slug> -->
- [ ] Audit <type> extractions <!-- reforge:audit:<slug> -->
- [ ] Fix <type> extraction issues <!-- reforge:fix:<slug> -->
- [ ] Generate <type> documentation <!-- reforge:generate:<slug> -->
- [ ] Audit <type> generated docs <!-- reforge:audit-generated:<slug> -->
- [ ] Fix <type> generated doc issues <!-- reforge:fix-generated:<slug> -->
```

Where `<slug>` is the lowercased, hyphenated form of the type name.

**Standard type display names and slugs**:

| Display Name | Slug |
|--------------|------|
| Business Rules | `business-rules` |
| Database | `database` |
| UI Flows | `ui` |
| Workflows | `workflows` |

**User-defined types**: Use the user's declared name as the display name. Derive
the slug by lowercasing, replacing spaces with hyphens, and removing special
characters (e.g., "API Contracts" → `api-contracts`).

#### Custom Tasks Section (only if user declared custom tasks)

```markdown
## Custom Tasks

- [ ] <task description> <!-- reforge:custom:<slug> -->
```

Where `<slug>` is derived by lowercasing and hyphenating the task description's
key phrase (e.g., "Review architecture with team lead" →
`review-architecture-with-team-lead`).

### Step 5: Confirm Plan Creation

Display a summary of the created plan:

```
Project plan created at .reforge/memory/project-plan.md

Summary:
- Setup items: 3 (X pre-completed)
- Workflow groups: N (extraction types: <list>)
- Items per group: 7 (full pipeline)
- Custom tasks: M
- Total items: <total>

Next steps:
- Run /reforge.plan --status to view progress at any time
- Run /reforge.plan "add <type>" to add more extraction types later
- Run /reforge.analyze to begin codebase analysis (if not already done)
```

---

## Mode 2: Add Items to Existing Plan

### Step 2: Parse Arguments

Parse the user's text arguments to determine what to add. The agent MUST
classify each requested item:

**Classification rule**:
- If the item uses extraction-related language ("extract", "extraction",
  "audit", "generate", or is a known extraction type name like
  "business-rules", "database", "ui", "workflows"), classify it as a
  **workflow group** item → create a full 7-step pipeline section
- If the item describes a non-extraction task (e.g., "review architecture with
  team", "set up CI/CD"), classify it as a **custom task** → add a single item
  to the Custom Tasks section

### Step 3: Check for Duplicates

For each new item to add, check if its tag already exists in the plan file:

1. For workflow groups: search for `<!-- reforge:extract:<slug> -->` in the plan
2. For custom tasks: search for `<!-- reforge:custom:<slug> -->` in the plan

If a duplicate is found:
- Inform the user: "The item '<name>' already exists in the plan. Current
  status: [checked/unchecked]."
- Offer to skip the duplicate
- Do NOT add duplicate tags — tag uniqueness is mandatory

### Step 4: Insert New Items

Read the existing plan file content. Insert new items in the appropriate
location:

**For workflow groups**:
- Insert the new section BEFORE the Custom Tasks section (if present) and AFTER
  existing workflow group sections
- Preserve all existing content, including completion status and timestamps

**For custom tasks**:
- If a Custom Tasks section exists, append new items to it
- If no Custom Tasks section exists, create one at the end of the file

**Update metadata**: Set `**Last Updated**` to today's date.

Write the updated plan file.

### Step 5: Confirm Addition

Display what was added:

```
Plan updated at .reforge/memory/project-plan.md

Added:
- Workflow group: <type> (7 pipeline items)
- Custom task: <description>
...

Skipped (duplicates):
- <name> (already exists, status: [checked/unchecked])

Updated total: <new total> items
```

---

## Mode 3: Interactive Review

### Step 2: Display Current Status

Read the plan file and display per-section progress:

```
📋 Project Plan Status

Setup: X/3 complete
<Type 1>: X/7 complete
<Type 2>: X/7 complete
...
Custom Tasks: X/N complete (if present)

Overall: X/Y items complete (Z%)
```

### Step 3: Prompt for Action

Ask the user:

"What would you like to do?
1. **Add new items** — declare additional extraction types or custom tasks
2. **Review the plan** — display the full plan with current status
3. **Exit** — no changes"

- If user chooses 1: proceed as Mode 2 with interactive gathering — ask for
  items interactively rather than from arguments
- If user chooses 2: display the full plan file content, then suggest next
  unchecked items as "Suggested next steps"
- If user chooses 3: exit without changes

---

## Mode 4: Status Summary

### Step 2: Read and Parse Plan

Read `.reforge/memory/project-plan.md`. If the file does not exist:

```
No project plan found. Run /reforge.plan to create one.
```

### Step 3: Calculate Progress

Count completed and total items per section:
- Count all lines matching `- [ ]` or `- [x]` pattern
- Group by H2 section headings (`## <Section Name>`)

### Step 4: Display Summary

```
📋 Project Plan: X/Y items complete (Z%)

Setup: X/3
<Type 1>: X/7
<Type 2>: X/7
...
Custom Tasks: X/N (if present)
```

If less than 100% complete, show next unchecked items:

```
Next unchecked items:
- <first unchecked item description>
- <second unchecked item description>
- <third unchecked item description>
```

If 100% complete:

```
🎉 All plan items are complete!

Suggested next steps:
- Review all generated documentation for accuracy
- Share extraction results with stakeholders
- Archive the project plan
```

Do NOT modify the plan file in this mode.

---

## Edge Cases

- **Duplicate items in Add mode**: Detect by searching for the tag pattern
  `<!-- reforge:<command>:<type> -->`. Inform user and offer to skip.
- **Invalid markdown in plan file**: Attempt best-effort parsing. Preserve any
  manual additions the user made. Warn about unrecoverable formatting issues.
- **Custom extraction types** (e.g., "extract performance-metrics"): Accept as
  a workflow group with the full 7-step pipeline. The extract/audit/fix/generate
  commands will attempt to process them; if a command cannot handle a custom
  type, it skips the plan update for that item.
- **Non-extraction custom tasks** (e.g., "review architecture with
  stakeholders"): Add to the Custom Tasks section as a single checklist item.
- **Analysis changes after plan creation** (e.g., user runs `/reforge.reanalyze`
  adding new files): The plan remains as-is. The user can run `/reforge.plan`
  again to get updated suggestions for new items.
- **Running before init/analyze**: Allowed — produces a plan based solely on
  user declarations with a note suggesting those commands for richer suggestions.

---

## Error Handling

| Condition | Behavior |
|-----------|----------|
| `.reforge/memory/` does not exist | Instruct user to run `/reforge.init` first or create the directory |
| Plan file corrupted/invalid markdown | Attempt best-effort parsing; preserve what can be read; warn user |
| Duplicate item requested in Add mode | Inform user, show existing item status, offer to skip |
| No analysis/profile available for suggestions | Proceed with manual-only input, note suggestion availability |
| User declares unsupported extraction type | Accept as workflow group with full 7-step pipeline |
| `--status` with no plan file | Display "No project plan found. Run /reforge.plan to create one." |
