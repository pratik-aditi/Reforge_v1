# /reforge.audit

> Audit extraction coverage and identify gaps against the analyzed codebase

## Command Syntax

```
/reforge.audit [type] [--json]
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `type` | No | Specific artifact type to audit: `analysis`, `business-rules`, `database`, `ui-flows`, `workflows`, `user-stories`, `documentation`, `diagrams` |
| `--json` | No | Output audit results as JSON for tooling integration |

## Overview

This command compares your analysis inventory against extraction and generation outputs to identify:

1. Coverage gaps — analyzed files with no extraction references
2. Stale references — extractions pointing to files that no longer exist or have changed
3. Per-type coverage breakdown — how well each extraction type covers the codebase

The audit produces two outputs:
- **`audit-report.xml`** — Read-only diagnostic with coverage statistics
- **`correction-plan.xml`** — Actionable plan consumed by `/reforge.fix`

## Prerequisites

- Completed analysis (`$ANALYSIS_DIR/analysis.xml` must exist)
- At least one extraction type completed (recommended for meaningful results)

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
- Identify audit-related items and display their status

**On command completion (success only):**

Determine the audit target context from what was audited during execution:
- If the audit targeted files in `$PROJECT_OUTPUT_DIR/extractions/` → use tag `<!-- reforge:audit:<type> -->`
- If the audit targeted files in `$PROJECT_OUTPUT_DIR/generated/` → use tag `<!-- reforge:audit-generated:<type> -->`
- If both were processed → mark both tags

If a specific `[type]` argument was provided:
- Locate the plan item by searching for the appropriate tag (based on context above)
- If found and unchecked (`- [ ]`): change to `- [x]` and append ` *(completed: YYYY-MM-DD)*`
- If found and already checked (`- [x]`): leave unchanged (idempotent)
- If tag not found: emit warning — "⚠️ No plan item found for this audit operation. Run /reforge.plan to add it."

If no `[type]` argument was provided (full audit):
- Determine which types were audited during execution
- For each audited type, search for and mark the corresponding tag(s)
- Report how many plan items were updated

- If file write fails: emit warning — "⚠️ Could not update project plan." Continue without failing.
- Update the `**Last Updated**` metadata line to today's date

If `.reforge/memory/project-plan.md` does not exist, skip this step silently.
The project plan is optional — its absence MUST NOT affect command behavior.

### Step 1: Read Analysis Inventory

1. **Read `$ANALYSIS_DIR/analysis.xml`**:
   - Extract all file paths from `<file>` elements
   - For each file, note: `path`, `language`, `lines`, `components`, `hash` attributes

2. **Read exclusion patterns**:
   - Read `$CONFIG` (config.json)
   - Extract `analysis.exclusions` array (glob patterns)
   - Remove any files matching exclusion patterns from the audit scope

3. **Build analyzed file list**:
   - The final set of files after exclusions is the audit scope
   - Record `total-files` count for coverage calculation

### Step 1.5: Validate Type Argument

If a `[type]` argument is provided, validate it against known types:

**Valid extraction types**: `business-rules`, `database`, `ui-flows`, `workflows`
**Valid generation types**: `user-stories`, `documentation`, `diagrams`
**Valid special types**: `analysis` (checks analysis.xml for stale file entries)

If the type is invalid:
```
Error: Unknown audit type '[type]'.
Valid types: analysis, business-rules, database, ui-flows, workflows, user-stories, documentation, diagrams
```

If the type is a generation type (`user-stories`, `documentation`, `diagrams`):
- Check if the corresponding output exists in `$PROJECT_OUTPUT_DIR/generated/`
- If not found:
  ```
  Error: No [type] found. Run /reforge.generate [type] first.
    Expected: $PROJECT_OUTPUT_DIR/generated/[type]/
  ```

If the type is an extraction type (`business-rules`, `database`, `ui-flows`, `workflows`):
- Check if the corresponding extraction file exists in `$EXTRACTIONS_DIR`
- If not found:
  ```
  Error: No [type] extraction found. Run /reforge.extract [type] first.
    Expected: $EXTRACTIONS_DIR/[type].xml
  ```

### Step 2: Read Extraction References

For each extraction file in `$EXTRACTIONS_DIR`, extract source file references:

**When `[type]` argument is NOT provided (full audit):**

Read all extraction files that exist:
- `$EXTRACTIONS_DIR/business-rules.xml` — extract all `<source file="...">` attributes
- `$EXTRACTIONS_DIR/database.xml` — extract all `<source file="...">` attributes
- `$EXTRACTIONS_DIR/ui-flows.xml` — extract all `<source file="...">` attributes
- `$EXTRACTIONS_DIR/workflows.xml` — extract all `<source file="...">` attributes

**When `[type]` is an extraction type (e.g., `business-rules`):**

Read ONLY the specified extraction file:
- `$EXTRACTIONS_DIR/[type].xml` — extract all `<source file="...">` attributes
- Coverage will be scoped to this single type only

**When `[type]` is a generation type (e.g., `user-stories`):**

Validate generated artifacts exist in `$PROJECT_OUTPUT_DIR/generated/` and trace their references back to extraction items:
- Read generated output files
- For each generated item, check its source extraction references
- Identify extraction items not represented in the generated output

**When `[type]` is `analysis`:**

Check analysis.xml for stale file entries:
- For each `<file>` entry in analysis.xml, verify the file still exists on disk
- Report entries where the source file has been deleted or moved

For each extraction file read:
- Collect the set of unique file paths referenced by `<source file="...">` attributes
- Count total extraction items (e.g., `<rule>`, `<entity>`, `<screen>`, `<workflow>` elements)
- Track which extraction type references which files

**Build the referenced file set**: Union of all file paths referenced across selected extraction types.

### Step 3: Calculate Coverage

1. **Compute covered files**: Files in the analyzed file list that appear in the referenced file set (at least one extraction references them)

2. **Compute uncovered files**: Files in the analyzed file list that do NOT appear in the referenced file set

3. **Calculate coverage percentage**:
   ```
   coverage_percentage = (covered_files_count / total_files_count) * 100
   ```

4. **Per-type coverage**: For each extraction type, count how many unique files it references

### Step 4: Check Stale References

For each extraction source reference found in Step 2 (scoped to the selected type if `[type]` argument was provided):

1. **Check file still exists in analysis.xml**: Is the referenced file path present in the analyzed file list?
   - If NOT present: classify as `issue="missing"` — the file may have been deleted

2. **Check file exists on disk**: Use Read tool to verify the file path is accessible
   - If NOT accessible: classify as `issue="missing"`

3. **Record stale references**:
   - Extraction type
   - Item ID (e.g., BR-001, WF-012)
   - Referenced file path
   - Issue type: "missing" or "modified"

**When `[type]` is specified**: Only check references for the specified type, report per-type statistics only.

### Step 5: Generate Correction Plan

For each identified issue, create a correction item in `correction-plan.xml`:

**For uncovered files (gaps):**
- `type="gap"`
- `category="extraction"`
- `action="/reforge.extract <best-type> --files <file-path>"`
  - Determine best extraction type based on file language/components:
    - Java services, controllers → `business-rules`
    - Repository/DAO files, SQL → `database`
    - JSP, HTML, frontend files → `ui-flows`
    - Service orchestration, async → `workflows`
    - If unclear, use `business-rules` as default

**For stale references:**
- `type="stale"`
- `category="extraction"` (or `category="analysis"` if the file is missing from analysis.xml entirely)
- `action="/reforge.reanalyze <file-path>"` for stale files
- `action="/reforge.reanalyze <file-path> --force"` for missing files

**Priority assignment** (upstream before downstream):
1. Analysis corrections first (priority 1-N)
2. Extraction corrections next (priority N+1-M)
3. Generation corrections last (priority M+1-P)

Within each category:
- Stale references before gaps (fix broken things before adding new ones)
- Files with more lines/components first (higher-value files)

**Assign sequential IDs**: COR-001, COR-002, ...

**Write `correction-plan.xml`** to `$AUDIT_DIR`:

```xml
<correction-plan project-id="$PROJECT_NAME" version="1.0.0"
                 generated="<current-timestamp>"
                 source-audit="$AUDIT_DIR/audit-report.xml"
                 total-items="<count>" completed-items="0">
  <correction id="COR-001" priority="1" type="stale" category="extraction"
              extraction-type="business-rules" status="pending"
              action="/reforge.reanalyze src/old/LegacyPricing.java">
    <description>...</description>
    <affected-files>
      <file>src/old/LegacyPricing.java</file>
    </affected-files>
  </correction>
  <!-- ... more corrections ... -->
</correction-plan>
```

See `.reforge/schemas/correction-plan.md` for full schema documentation.

### Step 6: Generate Audit Report

Assemble `audit-report.xml` with all coverage statistics.

**Scope attribute**: Set to `"all"` for full audit, or the specific type name for targeted audit (e.g., `"business-rules"`).

**When type is specified**: The `coverage-by-type` section includes only the audited type, and coverage percentage reflects only that type's coverage.

```xml
<audit-report project-id="$PROJECT_NAME" version="1.0.0"
              generated="<current-timestamp>"
              scope="all"
              total-files="<count>" covered-files="<count>"
              uncovered-files-count="<count>"
              coverage-percentage="<percentage>"
              stale-references-count="<count>">
  <coverage-by-type>
    <type-coverage type="business-rules" files-referenced="<N>" total-items="<N>" stale-items="<N>"/>
    <type-coverage type="database" files-referenced="<N>" total-items="<N>" stale-items="<N>"/>
    <type-coverage type="ui-flows" files-referenced="<N>" total-items="<N>" stale-items="<N>"/>
    <type-coverage type="workflows" files-referenced="<N>" total-items="<N>" stale-items="<N>"/>
  </coverage-by-type>
  <uncovered-files>
    <file path="..." language="..." lines="..." components="..."/>
    <!-- ... -->
  </uncovered-files>
  <stale-references>
    <stale-ref extraction-type="..." item-id="..." referenced-file="..." issue="missing|modified"/>
    <!-- ... -->
  </stale-references>
  <summary>Coverage: X% (Y of Z files covered). N uncovered files. M stale references.</summary>
</audit-report>
```

Write to `$AUDIT_DIR/audit-report.xml`.

See `.reforge/schemas/audit-report.md` for full schema documentation.

### Step 7: Display Results

Display human-readable audit results:

```
=== Reforge Audit Report ===
Project: [project-name]

--- Coverage ---
Overall: [X]% ([Y] of [Z] files covered)

--- Coverage by Type ---
| Type           | Files Referenced | Items | Stale |
|----------------|-----------------|-------|-------|
| Business Rules | [N]             | [N]   | [N]   |
| Database       | [N]             | [N]   | [N]   |
| UI Flows       | [N]             | [N]   | [N]   |
| Workflows      | [N]             | [N]   | [N]   |

--- Uncovered Files ([count]) ---
[If count > 0:]
  [path] ([language], [lines] lines)
  [path] ([language], [lines] lines)
  ...
[If count > 20, show first 20 and note "... and N more"]

--- Stale References ([count]) ---
[If count > 0:]
  [extraction-type] [item-id]: [referenced-file] ([issue])
  ...

--- Correction Plan ---
Total corrections: [N]
  By priority: [analysis: X] [extraction: Y] [generation: Z]
  By type: [gaps: X] [stale: Y]

--- Next Steps ---
→ Review correction plan: $AUDIT_DIR/correction-plan.xml
→ Run /reforge.fix to execute corrections
→ Run /reforge.fix --interactive for step-by-step approval
```

**If 100% coverage and no stale references:**
```
=== Reforge Audit Report ===
Project: [project-name]

--- Coverage ---
Overall: 100% ([Z] of [Z] files covered)
Stale references: 0

✓ All files have extraction coverage. No corrections needed.

--- Next Steps ---
→ Run /reforge.generate to create documentation from extractions
→ Run /reforge.status for full project overview
```

**When `[type]` is specified**, adjust the report header and coverage to be type-specific:

```
=== Reforge Audit Report ===
Project: [project-name]
Scope: [type] only

--- [Type] Coverage ---
[Type] coverage: [X]% ([Y] of [Z] files have [type] references)

--- Uncovered Files ([count]) ---
  [Files with no [type] extraction references]
  ...

--- Stale References ([count]) ---
  [Only stale references for this type]
  ...

--- Correction Plan ---
Total corrections: [N] (scoped to [type])
  By type: [gaps: X] [stale: Y]

--- Next Steps ---
→ Run /reforge.fix --type [type] to execute [type]-specific corrections
→ Run /reforge.audit for full coverage report
```

### Correction Plan Display

After the audit report, display a correction plan summary:

```
--- Correction Plan Summary ---
[N] corrections identified:

Priority 1 (Analysis):
  [count] items — Fix analysis inventory first
Priority 2 (Extraction):
  [count] items — [gaps] gaps + [stale] stale references
Priority 3 (Generation):
  [count] items — Regenerate downstream artifacts

Run /reforge.fix to execute all corrections in dependency order.
Run /reforge.fix --interactive to review each correction before execution.
```

### JSON Output

When `--json` flag is provided, output structured JSON instead of human-readable text:

```json
{
  "project": {
    "name": "[project-name]",
    "root": "[root-path]"
  },
  "audit": {
    "scope": "all",
    "generated": "[timestamp]",
    "coverage": {
      "total_files": 1247,
      "covered_files": 1100,
      "uncovered_files": 147,
      "percentage": 88.2
    },
    "stale_references_count": 5,
    "coverage_by_type": {
      "business-rules": {
        "files_referenced": 450,
        "total_items": 156,
        "stale_items": 2
      },
      "database": {
        "files_referenced": 200,
        "total_items": 89,
        "stale_items": 0
      },
      "ui-flows": {
        "files_referenced": 150,
        "total_items": 45,
        "stale_items": 1
      },
      "workflows": {
        "files_referenced": 300,
        "total_items": 23,
        "stale_items": 2
      }
    },
    "uncovered_files": [
      {"path": "src/utils/StringHelper.java", "language": "java", "lines": 45},
      {"path": "src/config/AppConfig.java", "language": "java", "lines": 120}
    ],
    "stale_references": [
      {"extraction_type": "business-rules", "item_id": "BR-045", "file": "src/old/LegacyService.java", "issue": "missing"},
      {"extraction_type": "workflows", "item_id": "WF-012", "file": "src/service/OrderService.java", "issue": "modified"}
    ]
  },
  "correction_plan": {
    "total_items": 15,
    "by_category": {
      "analysis": 2,
      "extraction": 12,
      "generation": 1
    },
    "by_type": {
      "gap": 10,
      "stale": 5
    },
    "path": "reforge_output/[project]/audit/correction-plan.xml"
  }
}
```

---

## Error Handling

### Missing Analysis

If analysis.xml does not exist (caught by prerequisites script):

```
Error: Analysis not found. Run /reforge.analyze first.
  Expected: $ANALYSIS_DIR/analysis.xml

The audit command requires a completed analysis to compare against.
Run /reforge.analyze to inventory your codebase first.
```

### Missing Extractions

If no extraction files exist, warn but continue with partial audit:

```
Warning: No extraction outputs found.
  The audit will report 0% coverage.
  Run /reforge.extract <type> to create extractions first.

Proceeding with stale reference check only...
```

### File Access Errors

If a referenced file cannot be read during stale reference checking:

```
Warning: Cannot access [file-path]
  Marking as stale reference (issue: missing)
```

Continue processing remaining files — do not abort on individual file errors.

### Empty Analysis

If analysis.xml exists but contains no file entries:

```
Warning: Analysis contains no file entries.
  Coverage: N/A (0 files in scope)

  This may indicate:
  - All files matched exclusion patterns
  - Analysis was interrupted before processing files

  Run /reforge.analyze to re-inventory the codebase.
```

---

## Examples

### Full Audit with Coverage Gaps

```
User: /reforge.audit

Agent:
=== Reforge Audit Report ===
Project: legacy-ecommerce

--- Coverage ---
Overall: 88.2% (1100 of 1247 files covered)

--- Coverage by Type ---
| Type           | Files Referenced | Items | Stale |
|----------------|-----------------|-------|-------|
| Business Rules | 450             | 156   | 2     |
| Database       | 200             | 89    | 0     |
| UI Flows       | 150             | 45    | 1     |
| Workflows      | 300             | 23    | 2     |

--- Uncovered Files (147) ---
  src/utils/StringHelper.java (java, 45 lines)
  src/config/AppConfig.java (java, 120 lines)
  src/legacy/OldPaymentGateway.java (java, 340 lines)
  ... and 144 more

--- Stale References (5) ---
  business-rules BR-045: src/old/LegacyPricing.java (missing)
  business-rules BR-089: src/validate/OrderValidator.java (modified)
  ui-flows UI-023: webapp/old/checkout.jsp (missing)
  workflows WF-012: src/service/OrderService.java (modified)
  workflows WF-018: src/batch/NightlyJob.java (modified)

--- Correction Plan ---
Total corrections: 152
  By priority: [extraction: 152]
  By type: [gaps: 147] [stale: 5]

--- Next Steps ---
→ Review correction plan: reforge_output/legacy-ecommerce/audit/correction-plan.xml
→ Run /reforge.fix to execute corrections
→ Run /reforge.fix --interactive for step-by-step approval
```

### Full Audit with 100% Coverage

```
User: /reforge.audit

Agent:
=== Reforge Audit Report ===
Project: legacy-ecommerce

--- Coverage ---
Overall: 100% (500 of 500 files covered)
Stale references: 0

✓ All files have extraction coverage. No corrections needed.

--- Next Steps ---
→ Run /reforge.generate to create documentation from extractions
→ Run /reforge.status for full project overview
```

### Audit with Stale References Only

```
User: /reforge.audit

Agent:
=== Reforge Audit Report ===
Project: legacy-ecommerce

--- Coverage ---
Overall: 100% (500 of 500 files covered)

--- Stale References (3) ---
  business-rules BR-045: src/old/LegacyPricing.java (missing)
  workflows WF-012: src/service/OrderService.java (modified)
  workflows WF-018: src/batch/NightlyJob.java (modified)

--- Correction Plan ---
Total corrections: 3
  By priority: [extraction: 3]
  By type: [stale: 3]

--- Next Steps ---
→ Review correction plan: reforge_output/legacy-ecommerce/audit/correction-plan.xml
→ Run /reforge.fix to execute corrections
```

### Targeted Audit — Business Rules

```
User: /reforge.audit business-rules

Agent:
=== Reforge Audit Report ===
Project: legacy-ecommerce
Scope: business-rules only

--- Business Rules Coverage ---
Business rules coverage: 60.0% (300 of 500 files have business-rules references)

--- Uncovered Files (200) ---
  src/service/PaymentService.java (java, 250 lines)
  src/service/ShippingService.java (java, 180 lines)
  src/util/ValidationHelper.java (java, 95 lines)
  ... and 197 more

--- Stale References (2) ---
  business-rules BR-045: src/old/LegacyPricing.java (missing)
  business-rules BR-089: src/validate/OrderValidator.java (modified)

--- Correction Plan ---
Total corrections: 202 (scoped to business-rules)
  By type: [gaps: 200] [stale: 2]

--- Next Steps ---
→ Run /reforge.fix --type business-rules to execute business-rules corrections
→ Run /reforge.audit for full coverage report
```

### Targeted Audit — User Stories

```
User: /reforge.audit user-stories

Agent:
=== Reforge Audit Report ===
Project: legacy-ecommerce
Scope: user-stories only

--- User Stories Coverage ---
User stories coverage: 85.0% (128 of 150 extraction items represented in user stories)

--- Unrepresented Extraction Items (22) ---
  BR-120: Loyalty points calculation (src/service/LoyaltyService.java)
  WF-015: Nightly batch reconciliation (src/batch/ReconcileJob.java)
  DB-045: Archive table interactions (src/repository/ArchiveRepository.java)
  ... and 19 more

--- Next Steps ---
→ Run /reforge.generate user-stories to regenerate with full coverage
```

### Targeted Audit — Invalid Type

```
User: /reforge.audit diagrams

Agent:
Error: No diagrams found. Run /reforge.generate diagrams first.
  Expected: reforge_output/legacy-ecommerce/generated/diagrams/
```
