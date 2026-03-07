# /reforge.delta

> Git diff-based incremental extraction -- only re-extract changed files

## Command Syntax

```
/reforge.delta [--since <commit|date>] [--type <extraction-type>] [--json]
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `--since` | No | Git commit SHA or date to diff against (default: last extraction timestamp) |
| `--type` | No | Limit re-extraction to specific type: `business-rules`, `database`, `ui`, `workflows`, `call-sites`, `dependencies`, `functional-requirements`, `non-functional`, `architecture`, `issues` |
| `--json` | No | Output delta report as JSON instead of XML |

## Overview

This command performs incremental extraction by:
1. Identifying files changed since a given commit or date via `git diff`
2. Cross-referencing changed files with existing extractions
3. Re-extracting only items from affected files
4. Generating a delta report showing what changed

This is significantly faster than full re-extraction for codebases with frequent changes.

**Note**: This command uses the `Bash` tool for `git diff` operations. All other operations use standard LLM-native tools (Read, Write, Glob, Grep).

## Prerequisites

- Analysis must be completed (`/reforge.analyze`)
- At least one extraction must exist in `$EXTRACTIONS_DIR/`
- Repository must be a git repository
- `$ANALYSIS_DIR/analysis.xml` must exist

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
$ANALYSIS_DIR = $PROJECT_OUTPUT_DIR/analysis
$EXTRACTIONS_DIR = $PROJECT_OUTPUT_DIR/extractions
$AUDIT_DIR = $PROJECT_OUTPUT_DIR/audit
$DERIVED_DIR = $PROJECT_OUTPUT_DIR/derived
```

### Step 0.5: Load Project Context

If `.reforge/memory/project-context.md` exists, read it now. Use its contents as
supplemental guidance throughout this command's execution:
- **Technology Stack**: Informs language/framework detection and pattern recognition
- **Domain Knowledge**: Provides business context for naming and categorization
- **Analysis Guidelines**: Directs focus and exclusions beyond config.json
- **Custom Rules**: Additional rules to follow alongside the constitution

### Step 0.7: Check/Update Project Plan

If `.reforge/memory/project-plan.md` exists, read it now.

**On command start:**
- Parse the plan file to count total items and completed items
- Display: "📋 Project Plan: X/Y items complete (Z%)"
- Derive the plan tag: `<!-- reforge:delta -->`
- Identify the item with that tag and display its status

**On command completion (success only):**
- Locate the plan item by searching for `<!-- reforge:delta -->`
- If found and unchecked (`- [ ]`): change to `- [x]` and append ` *(completed: YYYY-MM-DD)*`
- If found and already checked (`- [x]`): leave unchanged (idempotent)
- If tag not found: emit warning -- "No plan item found for delta. Run /reforge.plan to add it."
- If file write fails: emit warning -- "Could not update project plan." Continue without failing.
- Update the `**Last Updated**` metadata line to today's date

If `.reforge/memory/project-plan.md` does not exist, skip this step silently.
The project plan is optional -- its absence MUST NOT affect command behavior.

### Step 1: Determine Diff Baseline

Determine the baseline for the git diff:

1. **If `--since` provided**: Use the specified commit SHA or date
2. **If not provided**: Read the `generated` timestamp from the most recent extraction XML and use that as the baseline date

```bash
# Using commit SHA
git diff --name-only <commit-sha> HEAD

# Using date
git diff --name-only $(git rev-list -1 --before="<date>" HEAD) HEAD

# If no baseline found, diff against the last 7 days
git diff --name-only HEAD~7d HEAD
```

Store the list of changed files as `$CHANGED_FILES`.

### Step 2: Filter Changed Files

Cross-reference `$CHANGED_FILES` with the analysis inventory:

1. Read `$ANALYSIS_DIR/analysis.xml` to get the analyzed file inventory
2. Intersect `$CHANGED_FILES` with analyzed files (exclude files not in the analysis)
3. If `--type` is specified, further filter to files relevant to that extraction type

Display:
```
Delta Analysis:
  Changed files (git): N
  Analyzed files affected: M
  Extraction types to update: [list]
```

If no analyzed files are affected, report "No extraction-relevant changes detected" and exit successfully.

### Step 3: Identify Affected Extraction Items

For each extraction file in `$EXTRACTIONS_DIR/`:

1. Read the extraction XML
2. Find all items whose `<source file="...">` references any file in the filtered changed set
3. Record each affected item's ID, type, and source location

If `--type` is specified, only examine the specified extraction file.

### Step 4: Re-Extract Affected Items

For each affected file:

1. **Read the current file** using the Read tool (CRITICAL: must read in this session)
2. Re-extract items following the same patterns as `/reforge.extract` for the relevant type
3. Compare new extractions against existing items:
   - **Modified**: Item exists but content changed
   - **Removed**: Item no longer present in source
   - **Added**: New item found in changed file

### Step 5: Update Extraction Files

For each affected extraction type:

1. Read the existing extraction XML
2. Replace modified items with updated versions
3. Remove items that no longer exist
4. Add newly discovered items
5. Update the `<metadata>` counts and `generated` timestamp
6. Write the updated extraction XML

### Step 6: Generate Delta Report

Write `$AUDIT_DIR/delta-report.xml`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<delta-report xmlns="http://reforge.dev/schema/extraction"
              project-id="{project-id}" version="1.0.0"
              schema-version="1.0.0"
              generated="{timestamp}">
  <metadata>
    <baseline>{commit-sha-or-date}</baseline>
    <files-changed>{count}</files-changed>
    <files-affected>{count}</files-affected>
    <items-added>{count}</items-added>
    <items-modified>{count}</items-modified>
    <items-removed>{count}</items-removed>
  </metadata>

  <changes>
    <change type="modified" extraction-type="business-rules"
            item-id="BR-VAL-003" action="updated">
      <file>src/service/ValidationService.java</file>
      <summary>Validation threshold changed from 100 to 150</summary>
    </change>
    <change type="added" extraction-type="business-rules"
            item-id="BR-VAL-025" action="new">
      <file>src/service/ValidationService.java</file>
      <summary>New email format validation rule added</summary>
    </change>
    <change type="removed" extraction-type="database"
            item-id="DB-SEL-012" action="deleted">
      <file>src/repository/OrderRepository.java</file>
      <summary>Query removed during refactoring</summary>
    </change>
  </changes>
</delta-report>
```

### Step 7: Report Results

```
Delta Extraction Complete!

Baseline: {commit-sha or date}
Files changed: N (M relevant to extractions)

Changes:
  Added:    A items
  Modified: B items
  Removed:  C items

Updated extractions:
  - business-rules.xml (3 changes)
  - database.xml (1 change)

Delta report: $AUDIT_DIR/delta-report.xml

Run /reforge.audit to validate extraction coverage.
```

---

## Error Handling

| Error | Response |
|-------|----------|
| Not a git repository | Report error: "This command requires a git repository. Initialize with `git init` or clone the repo." |
| No extractions found | Report error: "No existing extractions found. Run `/reforge.extract` first before using delta." |
| `analysis.xml` not found | Report error, suggest `/reforge.analyze` |
| Git diff fails | Report error with git error message, suggest checking git status |
| `--since` commit not found | Report error: "Commit not found. Verify the commit SHA or use a date format (YYYY-MM-DD)." |
| No changed files | Report: "No changes detected since baseline. Extractions are up to date." Exit successfully. |
| File read error during re-extraction | Log warning, skip file, continue with remaining files |

---

## Examples

### Incremental update since last extraction

```
/reforge.delta
```

### Changes since specific commit

```
/reforge.delta --since abc1234
```

### Only update business rules since a date

```
/reforge.delta --since 2024-01-01 --type business-rules
```
