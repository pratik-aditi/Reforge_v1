# /reforge.compare

> Diff two extraction runs for regression detection

## Command Syntax

```
/reforge.compare <file1> <file2> [--type <extraction-type>] [--json]
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `file1` | Yes | Path to the first (baseline) extraction XML file |
| `file2` | Yes | Path to the second (current) extraction XML file |
| `--type` | No | Extraction type hint (auto-detected from root element if omitted) |
| `--json` | No | Output comparison as JSON instead of XML |

## Overview

This command compares two versions of any extraction XML file to detect regressions, additions, and modifications. It is useful for:

- Verifying that re-extraction produces consistent results
- Detecting regressions after code changes
- Comparing extractions before and after `/reforge.fix`
- Validating delta extraction results

The comparison report uses a simple inline structure (no separate schema required).

## Prerequisites

- Both `file1` and `file2` must exist and be valid extraction XML files
- Files should be the same extraction type (same root element)

---

## Workflow

### Step 0: Check Prerequisites

Run the prerequisites script to validate state and resolve paths:

```bash
reforge-scripts check-prerequisites --json
```

This returns JSON with resolved variables:
```json
{"PROJECT_NAME":"...","REPO_ROOT":"...","PROJECT_OUTPUT_DIR":"...","CONFIG":"...","ANALYSIS_STATUS":"...","AVAILABLE_EXTRACTIONS":[...],"CHECKPOINT":null,"CLARIFICATIONS_DIR":"..."}
```

Use `$PROJECT_OUTPUT_DIR` for all output paths in subsequent steps.

Assign subdirectory variables:
```
$AUDIT_DIR = $PROJECT_OUTPUT_DIR/audit
```

### Step 0.5: Load Project Context

If `.reforge/memory/project-context.md` exists, read it now. Use its contents as
supplemental guidance throughout this command's execution:
- **Technology Stack**: Informs extraction type detection
- **Domain Knowledge**: Provides context for change significance assessment
- **Analysis Guidelines**: Directs focus and exclusions beyond config.json
- **Custom Rules**: Additional rules to follow alongside the constitution

### Step 0.7: Check/Update Project Plan

If `.reforge/memory/project-plan.md` exists, read it now.

**On command start:**
- Parse the plan file to count total items and completed items
- Display: "📋 Project Plan: X/Y items complete (Z%)"
- Derive the plan tag: `<!-- reforge:compare -->`
- Identify the item with that tag and display its status

**On command completion (success only):**
- Locate the plan item by searching for `<!-- reforge:compare -->`
- If found and unchecked (`- [ ]`): change to `- [x]` and append ` *(completed: YYYY-MM-DD)*`
- If found and already checked (`- [x]`): leave unchanged (idempotent)
- If tag not found: emit warning -- "No plan item found for compare. Run /reforge.plan to add it."
- If file write fails: emit warning -- "Could not update project plan." Continue without failing.
- Update the `**Last Updated**` metadata line to today's date

If `.reforge/memory/project-plan.md` does not exist, skip this step silently.
The project plan is optional -- its absence MUST NOT affect command behavior.

### Step 1: Load Both Files

Read both extraction XML files using the Read tool:

1. Read `file1` (baseline) -- parse root element, metadata, and all items
2. Read `file2` (current) -- parse root element, metadata, and all items

Detect the extraction type from the root element name (e.g., `<business-rules>`, `<database>`, `<issues>`). If `--type` is provided, verify it matches.

If root elements differ between files:
- Report error: "Root elements do not match: `<{root1}>` vs `<{root2}>`. Cannot compare different extraction types."

### Step 2: Index Items by ID

For each file, build an index of items by their `id` attribute:

```
file1_items = { "BR-VAL-001": {content}, "BR-VAL-002": {content}, ... }
file2_items = { "BR-VAL-001": {content}, "BR-VAL-003": {content}, ... }
```

The item element name varies by extraction type (e.g., `<rule>`, `<interaction>`, `<bug>`, `<screen>`).

### Step 3: Identify Changes

Compare the two item indexes:

1. **Added items**: IDs in `file2` but not in `file1`
2. **Removed items**: IDs in `file1` but not in `file2`
3. **Modified items**: IDs in both files but with different content
4. **Unchanged items**: IDs in both files with identical content

For modified items, identify what changed:
- Attribute changes (confidence, severity, category)
- Content changes (description, source references, child elements)
- Source location changes (file path, line numbers)

### Step 4: Compute Statistics

Calculate change statistics:

```
total_baseline = count of items in file1
total_current = count of items in file2
added = count of items only in file2
removed = count of items only in file1
modified = count of items in both but changed
unchanged = count of items in both and identical
change_rate = (added + removed + modified) / max(total_baseline, 1) * 100
```

### Step 5: Generate Comparison Report

Write `$AUDIT_DIR/comparison-report.xml`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<comparison-report xmlns="http://reforge.dev/schema/extraction"
                   project-id="{project-id}"
                   generated="{timestamp}">

  <metadata>
    <extraction-type>{type}</extraction-type>
    <baseline-file>{file1-path}</baseline-file>
    <baseline-generated>{file1-timestamp}</baseline-generated>
    <baseline-count>{total-items-file1}</baseline-count>
    <current-file>{file2-path}</current-file>
    <current-generated>{file2-timestamp}</current-generated>
    <current-count>{total-items-file2}</current-count>
  </metadata>

  <statistics>
    <added>{count}</added>
    <removed>{count}</removed>
    <modified>{count}</modified>
    <unchanged>{count}</unchanged>
    <change-rate>{percent}%</change-rate>
  </statistics>

  <changes>
    <added-items count="{n}">
      <item id="BR-VAL-025">
        <summary>New email format validation rule</summary>
        <source file="src/service/ValidationService.java" line-start="180" line-end="195"/>
      </item>
    </added-items>

    <removed-items count="{n}">
      <item id="BR-VAL-010">
        <summary>Legacy phone validation removed</summary>
        <source file="src/service/ValidationService.java" line-start="90" line-end="105"/>
      </item>
    </removed-items>

    <modified-items count="{n}">
      <item id="BR-VAL-003">
        <summary>Validation threshold changed</summary>
        <diff attribute="description">
          <before>Order total must exceed $100</before>
          <after>Order total must exceed $150</after>
        </diff>
        <diff attribute="source.line-start">
          <before>45</before>
          <after>52</after>
        </diff>
      </item>
    </modified-items>
  </changes>

</comparison-report>
```

### Step 6: Report Results

```
Comparison Complete!

Extraction type: business-rules
Baseline: file1 (generated 2024-01-10, 85 items)
Current:  file2 (generated 2024-01-15, 88 items)

Output: $AUDIT_DIR/comparison-report.xml

Changes:
  Added:     5 items
  Removed:   2 items
  Modified:  8 items
  Unchanged: 75 items

Change rate: 17.6%

Notable changes:
  - BR-VAL-003: Validation threshold changed ($100 -> $150)
  - BR-AUTH-002: Confidence upgraded (medium -> high)
  - 5 new validation rules added in ValidationService.java

No regressions detected (no items lost confidence or gained severity).
```

---

## Error Handling

| Error | Response |
|-------|----------|
| `file1` not found | Report error: "Baseline file not found: {path}" |
| `file2` not found | Report error: "Current file not found: {path}" |
| Root elements differ | Report error: "Cannot compare different extraction types." |
| Invalid XML | Report error: "File is not valid XML: {path}. Check file integrity." |
| No items found in file | Warn: "No items found in {path}. File may be empty or use unexpected structure." |
| `--type` mismatch | Warn: "Specified type does not match detected type. Using detected type." |

---

## Examples

### Compare two business rules extractions

```
/reforge.compare reforge_output/myapp/extractions/business-rules-v1.xml reforge_output/myapp/extractions/business-rules.xml
```

### Compare with type hint

```
/reforge.compare backup/database.xml reforge_output/myapp/extractions/database.xml --type database
```

### JSON output for scripting

```
/reforge.compare file1.xml file2.xml --json
```
