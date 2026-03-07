# /reforge.validate

> Validate extraction XML files for XSD conformance, ID uniqueness, cross-reference integrity, and confidence sum correctness

## Command Syntax

```
/reforge.validate [--type <type>] [--fix] [--json]
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `--type` | No | Limit validation to a specific extraction type: `business-rules`, `database`, `ui-flows`, `workflows`, `call-sites`, `dependencies`, `functional-requirements`, `non-functional`, `architecture`, `issues` |
| `--fix` | No | Auto-fix correctable issues (confidence sum mismatches, duplicate IDs) |
| `--json` | No | Output validation results as JSON for tooling integration |

## Overview

This command performs structural validation of all extraction XML files:

1. **XSD Conformance** — Validates each extraction XML against its corresponding XSD
2. **ID Uniqueness** — Checks for duplicate IDs within each extraction file
3. **Cross-Reference Integrity** — Verifies that IDs referenced across files actually exist
4. **Confidence Sum Checks** — Validates that `high + medium + low` equals `total-count` in metadata

The validation produces:
- **`validation-report.xml`** — Structured report with all findings (schema: `.reforge/schemas/validation-report.md`)

## Prerequisites

- Completed analysis (`$ANALYSIS_DIR/analysis.xml` must exist)
- At least one extraction type completed

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

Use `$PROJECT_OUTPUT_DIR`, `$PROJECT_NAME` throughout subsequent steps.

Assign subdirectory variables:
```
$ANALYSIS_DIR = $PROJECT_OUTPUT_DIR/analysis
$EXTRACTIONS_DIR = $PROJECT_OUTPUT_DIR/extractions
$AUDIT_DIR = $PROJECT_OUTPUT_DIR/audit
$XSD_DIR = .reforge/schemas/xsd
```

Create the audit output directory if it does not exist:
```
mkdir -p $AUDIT_DIR
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
- Identify validate-related items and display their status

**On command completion (success only):**
- Locate the plan item by searching for `<!-- reforge:validate -->`
- If found and unchecked (`- [ ]`): change to `- [x]` and append ` *(completed: YYYY-MM-DD)*`
- If found and already checked (`- [x]`): leave unchanged (idempotent)
- If tag not found: emit warning — "⚠️ No plan item found for this validation operation. Run /reforge.plan to add it."
- If file write fails: emit warning — "⚠️ Could not update project plan." Continue without failing.
- Update the `**Last Updated**` metadata line to today's date

If `.reforge/memory/project-plan.md` does not exist, skip this step silently.
The project plan is optional — its absence MUST NOT affect command behavior.

### Step 1: Discover Extraction Files

1. **Scan `$EXTRACTIONS_DIR`** for all XML files
2. If `--type` is specified, filter to only the matching extraction file (`$EXTRACTIONS_DIR/<type>.xml`)
3. If no extraction files found:
   ```
   Error: No extraction files found in $EXTRACTIONS_DIR.
     Run /reforge.extract first to create extractions before validating.
   ```

4. **Build the XSD mapping** — for each extraction file, locate its corresponding XSD:

| Extraction File | XSD File |
|----------------|----------|
| `business-rules.xml` | `$XSD_DIR/business-rules.xsd` |
| `database.xml` | `$XSD_DIR/database.xsd` |
| `ui-flows.xml` | `$XSD_DIR/ui-flows.xsd` |
| `workflows.xml` | `$XSD_DIR/workflows.xsd` |
| `call-sites.xml` | `$XSD_DIR/call-sites.xsd` |
| `dependencies.xml` | `$XSD_DIR/dependencies.xsd` |
| `functional-requirements.xml` | `$XSD_DIR/functional-requirements.xsd` |
| `non-functional.xml` | `$XSD_DIR/non-functional.xsd` |
| `architecture.xml` | `$XSD_DIR/architecture.xsd` |
| `issues.xml` | `$XSD_DIR/issues.xsd` |

If an XSD file does not exist for an extraction type, skip XSD validation for that file and note it:
```
Warning: No XSD found for [type]. Skipping XSD conformance check.
```

### Step 2: XSD Conformance Validation

For each extraction file with a corresponding XSD:

1. **Read the extraction XML file**
2. **Read the corresponding XSD file** (and `common-schema.xsd`)
3. **Validate structure**:
   - Root element name matches expected element for the extraction type
   - All required attributes present (`project-id`, `version`, `schema-version`, `generated`)
   - `xmlns` attribute is `http://reforge.dev/schema/extraction`
   - `<metadata>` is present as first child element
   - All required child elements present per the XSD
   - Attribute types match XSD definitions (e.g., `confidence` values are `high`, `medium`, or `low`)
4. **Record results**: For each file, record `pass` or `fail` with specific error details

### Step 3: ID Uniqueness Check

For each extraction file:

1. **Extract all `id` attributes** from extraction items (e.g., `<rule id="BR-VAL-001">`, `<bug id="BUG-NULL-001">`)
2. **Check for duplicates** within the file scope
3. **Validate ID format**: Each ID must match `{PREFIX}-{CATEGORY}-{SEQUENCE}` pattern
4. **Record results**: For each file scope, record pass/fail with duplicate details

If `--fix` is specified and duplicates are found:
- Rename duplicate IDs by appending a disambiguating suffix (e.g., `BR-VAL-001` becomes `BR-VAL-001a`)
- Write the corrected file back to `$EXTRACTIONS_DIR`
- Record the fix in the validation report

### Step 4: Cross-Reference Integrity Check

Scan all extraction files for cross-references between extraction items:

1. **Identify cross-reference patterns**:
   - `ref="BR-VAL-001"` or similar ID references pointing to items in other files
   - `<related-rule>`, `<related-workflow>`, `<depends-on>` elements
   - Any attribute or element containing a value matching the `{PREFIX}-{CATEGORY}-{SEQUENCE}` pattern that references a different extraction type prefix

2. **For each cross-reference found**:
   - Determine the target file based on the ID prefix (e.g., `BR-*` maps to `business-rules.xml`)
   - Check if the target ID exists in the target file
   - Record `valid` or `broken` status

3. **Record results**: Total cross-references checked, passed, and failed with details

### Step 5: Confidence Sum Validation

For each extraction file:

1. **Read the `<metadata>` element**:
   - Extract `<total-count>` value
   - Extract `<confidence-distribution>` values: `<high>`, `<medium>`, `<low>`

2. **Compute sum**: `high + medium + low`

3. **Compare**: Sum must equal `total-count`

4. **Record results**: For each file, record pass/fail with actual values

If `--fix` is specified and a mismatch is found:
- Count actual items in the file by their `confidence` attributes
- Update `<total-count>` and `<confidence-distribution>` to match actual counts
- Write the corrected file back to `$EXTRACTIONS_DIR`
- Record the fix in the validation report

### Step 6: Generate Validation Report

Write the validation report to `$AUDIT_DIR/validation-report.xml` following the schema defined in `.reforge/schemas/validation-report.md`.

The report MUST include:
- Root element `<validation-report>` with all required common attributes
- `<metadata>` with total finding count
- `<xsd-validation>` section with per-file results
- `<id-uniqueness>` section with per-scope results
- `<cross-references>` section with per-reference results
- `<confidence-checks>` section with per-file sum results
- `<summary>` with aggregate pass/fail counts by category

### Step 7: Display Results

Display a human-readable summary:

```
=== Reforge Validation Report ===
Project: [project-name]

--- XSD Conformance ---
| File                   | Schema              | Status |
|------------------------|---------------------|--------|
| business-rules.xml     | business-rules.xsd  | PASS   |
| database.xml           | database.xsd        | PASS   |
| issues.xml             | issues.xsd          | FAIL   |

--- ID Uniqueness ---
| File                   | IDs Checked | Status |
|------------------------|-------------|--------|
| business-rules.xml     | 156         | PASS   |
| workflows.xml          | 23          | FAIL   |

--- Cross-References ---
Checked: 45 | Valid: 43 | Broken: 2

--- Confidence Sums ---
| File                   | Total | Sum | Status |
|------------------------|-------|-----|--------|
| business-rules.xml     | 156   | 156 | PASS   |
| database.xml           | 89    | 85  | FAIL   |

--- Summary ---
Status: FAIL
Total checks: 57 | Passed: 53 | Failed: 4

--- Next Steps ---
-> Review report: $AUDIT_DIR/validation-report.xml
-> Run /reforge.validate --fix to auto-correct fixable issues
-> Run /reforge.audit accuracy for content verification
```

---

## Error Handling

### No Extraction Files

If no extraction files exist in `$EXTRACTIONS_DIR`:

```
Error: No extraction files found in $EXTRACTIONS_DIR.
  Run /reforge.extract first to create extractions before validating.
```

### Invalid Type Argument

If `--type` specifies an unknown extraction type:

```
Error: Unknown extraction type '[type]'.
Valid types: business-rules, database, ui-flows, workflows, call-sites, dependencies, functional-requirements, non-functional, architecture, issues
```

### Missing XSD

If an XSD file does not exist for a given extraction type:

```
Warning: No XSD found for [type] at $XSD_DIR/[type].xsd.
  Skipping XSD conformance check for this type.
```

Continue processing remaining validation checks — do not abort.

### File Read Errors

If an extraction file cannot be read:

```
Warning: Cannot read [file-path]
  Skipping validation for this file.
```

Continue processing remaining files — do not abort on individual file errors.

---

## Examples

### Full Validation with Issues

```
User: /reforge.validate

Agent:
=== Reforge Validation Report ===
Project: legacy-ecommerce

--- XSD Conformance ---
| File                   | Schema              | Status |
|------------------------|---------------------|--------|
| business-rules.xml     | business-rules.xsd  | PASS   |
| database.xml           | database.xsd        | PASS   |
| workflows.xml          | workflows.xsd       | PASS   |
| issues.xml             | issues.xsd          | FAIL   |

--- ID Uniqueness ---
| File                   | IDs Checked | Status |
|------------------------|-------------|--------|
| business-rules.xml     | 156         | PASS   |
| database.xml           | 89          | PASS   |
| workflows.xml          | 23          | FAIL   |
| issues.xml             | 13          | PASS   |

--- Cross-References ---
Checked: 45 | Valid: 43 | Broken: 2

--- Confidence Sums ---
| File                   | Total | Sum | Status |
|------------------------|-------|-----|--------|
| business-rules.xml     | 156   | 156 | PASS   |
| database.xml           | 89    | 85  | FAIL   |
| workflows.xml          | 23    | 23  | PASS   |
| issues.xml             | 13    | 13  | PASS   |

--- Summary ---
Status: FAIL
Total checks: 57 | Passed: 53 | Failed: 4

--- Next Steps ---
-> Review report: reforge_output/legacy-ecommerce/audit/validation-report.xml
-> Run /reforge.validate --fix to auto-correct fixable issues
-> Run /reforge.audit accuracy for content verification
```

### Clean Validation

```
User: /reforge.validate

Agent:
=== Reforge Validation Report ===
Project: legacy-ecommerce

--- Summary ---
Status: PASS
Total checks: 57 | Passed: 57 | Failed: 0

All extraction files pass structural validation.

--- Next Steps ---
-> Run /reforge.audit accuracy for content verification
-> Run /reforge.generate to create documentation from extractions
```

### Type-Scoped Validation with Fix

```
User: /reforge.validate --type database --fix

Agent:
=== Reforge Validation Report ===
Project: legacy-ecommerce
Scope: database

--- XSD Conformance ---
database.xml: PASS

--- ID Uniqueness ---
database.xml: PASS (89 IDs checked)

--- Confidence Sums ---
database.xml: FAIL -> FIXED
  Was: total-count=89, sum=85 (difference: 4)
  Now: total-count=89, high=52, medium=32, low=5, sum=89

--- Summary ---
Status: PASS (after fixes)
Fixes applied: 1

--- Next Steps ---
-> Review report: reforge_output/legacy-ecommerce/audit/validation-report.xml
```
