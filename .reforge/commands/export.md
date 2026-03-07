# /reforge.export

> Export extraction artifacts to external project management formats

## Command Syntax

```
/reforge.export <format> [--type <artifact-type>] [--output <path>]
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `format` | Yes | Export format: `jira-csv`, `azure-devops`, `confluence`, `github-issues` |
| `--type` | No | Limit export to specific artifact type: `user-stories`, `business-rules`, `issues` (default: all available) |
| `--output` | No | Custom output path (defaults to `$PROJECT_OUTPUT_DIR/exports/`) |

## Overview

This command transforms Reforge extraction artifacts into formats consumable by external project management and documentation tools:

- **jira-csv**: CSV file importable via Jira's CSV importer with standard field mappings
- **azure-devops**: CSV file compatible with Azure DevOps work item import
- **confluence**: Markdown files formatted for Confluence wiki import
- **github-issues**: Markdown files structured as GitHub Issues (one file per item)

## Prerequisites

- At least one exportable artifact must exist:
  - `$GENERATED_DIR/user-stories/` (from `/reforge.generate user-stories`)
  - `$EXTRACTIONS_DIR/business-rules.xml` (from `/reforge.extract business-rules`)
  - `$EXTRACTIONS_DIR/issues.xml` (from `/reforge.extract issues`)

---

## Workflow

### Step 0: Check Prerequisites

Run the prerequisites script to validate state and resolve paths:

```bash
reforge-scripts check-prerequisites --json --require-analysis
```

This returns JSON with resolved variables:
```json
{"PROJECT_NAME":"...","REPO_ROOT":"...","PROJECT_OUTPUT_DIR":"...","CONFIG":"...","ANALYSIS_STATUS":"completed","AVAILABLE_EXTRACTIONS":[...],"CHECKPOINT":null,"CLARIFICATIONS_DIR":"..."}
```

Use `$PROJECT_OUTPUT_DIR` for all output paths in subsequent steps.

Assign subdirectory variables:
```
$EXTRACTIONS_DIR = $PROJECT_OUTPUT_DIR/extractions
$GENERATED_DIR = $PROJECT_OUTPUT_DIR/generated
$EXPORTS_DIR = $PROJECT_OUTPUT_DIR/exports
```

If `--output` is specified, use that path instead of `$EXPORTS_DIR`.

Create the output directory if it does not exist:
```
mkdir -p $EXPORTS_DIR
```

### Step 0.5: Load Project Context

If `.reforge/memory/project-context.md` exists, read it now. Use its contents as
supplemental guidance throughout this command's execution:
- **Technology Stack**: Informs field mappings and labels
- **Domain Knowledge**: Provides business context for story descriptions
- **Analysis Guidelines**: Directs focus and exclusions beyond config.json
- **Custom Rules**: Additional rules to follow alongside the constitution

### Step 0.7: Check/Update Project Plan

If `.reforge/memory/project-plan.md` exists, read it now.

**On command start:**
- Parse the plan file to count total items and completed items
- Display: "📋 Project Plan: X/Y items complete (Z%)"
- Search for `<!-- reforge:export -->` tag and display its status

**On command completion (success only):**
- Locate the plan item by searching for `<!-- reforge:export -->`
- If found and unchecked (`- [ ]`): change to `- [x]` and append ` *(completed: YYYY-MM-DD)*`
- If found and already checked (`- [x]`): leave unchanged (idempotent)
- If tag not found: emit warning — "⚠️ No plan item found for export. Run /reforge.plan to add it."
- If file write fails: emit warning — "⚠️ Could not update project plan." Continue without failing.
- Update the `**Last Updated**` metadata line to today's date

If `.reforge/memory/project-plan.md` does not exist, skip this step silently.
The project plan is optional — its absence MUST NOT affect command behavior.

### Step 1: Identify Available Source Artifacts

Scan for exportable artifacts:

1. **User Stories**: Check `$GENERATED_DIR/user-stories/` for markdown files
2. **Business Rules**: Check `$EXTRACTIONS_DIR/business-rules.xml`
3. **Issues**: Check `$EXTRACTIONS_DIR/issues.xml`

If `--type` is specified, validate the type and only load that artifact:
- Valid types: `user-stories`, `business-rules`, `issues`
- If the specified type is not available, emit error and stop

If no exportable artifacts are found:
```
Error: No exportable artifacts found. Run extraction or generation commands first.
  Checked: $GENERATED_DIR/user-stories/, $EXTRACTIONS_DIR/business-rules.xml, $EXTRACTIONS_DIR/issues.xml
```

### Step 2: Parse Source Artifacts

For each available artifact type, extract the data needed for export:

**User Stories** — parse markdown files for:
- Story ID, title, description
- Acceptance criteria
- Priority and effort estimates
- Source references (extraction IDs)

**Business Rules** — parse XML for:
- Rule ID, name, description
- Category, confidence, source file references
- Conditions, actions, exceptions

**Issues** — parse XML for:
- Bug/issue ID, title, description
- Severity, category, detection method
- Impact, recommendation, effort estimate
- Source file references

### Step 3: Transform to Target Format

Apply format-specific field mappings:

#### Jira CSV Format

Output: `$EXPORTS_DIR/jira-import.csv`

| Source Field | Jira Field | Notes |
|-------------|------------|-------|
| ID | `External ID` | Preserves Reforge ID for traceability |
| Title | `Summary` | Required field |
| Description | `Description` | Full description with source references |
| Priority (severity) | `Priority` | Map: critical=Highest, high=High, medium=Medium, low=Low |
| Category | `Labels` | Comma-separated labels |
| Effort estimate | `Story Points` | Map: low=1, medium=3, high=8 |
| Acceptance criteria | `Description` | Appended to description as checklist |
| Type | `Issue Type` | user-story=Story, business-rule=Task, bug=Bug, issue=Task |

CSV header:
```csv
Issue Type,Summary,Description,Priority,Labels,Story Points,External ID
```

#### Azure DevOps Format

Output: `$EXPORTS_DIR/azure-devops-import.csv`

| Source Field | Azure DevOps Field | Notes |
|-------------|-------------------|-------|
| ID | `ID` | External reference |
| Title | `Title` | Required field |
| Description | `Description` | HTML-formatted description |
| Priority (severity) | `Priority` | Map: critical=1, high=2, medium=3, low=4 |
| Category | `Tags` | Semicolon-separated tags |
| Effort estimate | `Effort` | Map: low=1, medium=3, high=8 |
| Type | `Work Item Type` | user-story=User Story, business-rule=Task, bug=Bug, issue=Task |

CSV header:
```csv
Work Item Type,Title,Description,Priority,Tags,Effort,ID
```

#### Confluence Format

Output: `$EXPORTS_DIR/confluence/` (one markdown file per artifact type)

Structure each file as a Confluence-compatible wiki page:
- Use Confluence storage format headings
- Include expandable sections for details
- Add status macros for severity/priority
- Create tables for structured data
- Link related items via anchor references

Files produced:
- `confluence/user-stories.md` — User story catalog
- `confluence/business-rules.md` — Business rules reference
- `confluence/issues.md` — Issues and technical debt register

#### GitHub Issues Format

Output: `$EXPORTS_DIR/github-issues/` (one markdown file per item)

Each file follows GitHub Issue template format:
- Filename: `{id}.md` (e.g., `BUG-NULL-001.md`)
- YAML front matter with labels and assignees
- Markdown body with description, source references, and acceptance criteria

```markdown
---
title: "Unchecked null return from findCustomer"
labels: ["bug", "null-reference", "severity:high"]
---

## Description

CustomerService.findCustomer can return null but caller does not check before accessing properties.

## Impact

NullPointerException at runtime when customer not found

## Source

- `src/service/OrderService.java` (lines 45-48)

## Recommendation

Add null check before accessing customer properties.
```

### Step 4: Write Export Files

Write all export files to the target directory.

Display summary:
```
Export complete: [format]
  Source artifacts: [list of artifact types exported]
  Items exported: N
  Output: $EXPORTS_DIR/[files]
```

---

## Error Handling

| Condition | Action |
|-----------|--------|
| Invalid format argument | Error: "Unknown export format '[format]'. Valid formats: jira-csv, azure-devops, confluence, github-issues" |
| Invalid `--type` argument | Error: "Unknown artifact type '[type]'. Valid types: user-stories, business-rules, issues" |
| No exportable artifacts | Error: "No exportable artifacts found. Run extraction or generation commands first." |
| Specified `--type` not available | Error: "Artifact type '[type]' not found. Run the corresponding extraction/generation command first." |
| XML parse error | Warning: "Could not parse [file]. Skipping." Continue with other artifacts. |
| Output directory not writable | Error: "Cannot write to output directory: [path]" |

---

## Examples

### Export All to Jira

```
/reforge.export jira-csv
```

Produces `exports/jira-import.csv` containing all available user stories, business rules, and issues.

### Export Issues to GitHub

```
/reforge.export github-issues --type issues
```

Produces `exports/github-issues/BUG-NULL-001.md`, `exports/github-issues/ISS-DEBT-001.md`, etc.

### Export User Stories to Azure DevOps

```
/reforge.export azure-devops --type user-stories --output ./backlog/
```

Produces `./backlog/azure-devops-import.csv` containing user stories only.

### Export to Confluence

```
/reforge.export confluence
```

Produces `exports/confluence/user-stories.md`, `exports/confluence/business-rules.md`, `exports/confluence/issues.md`.
