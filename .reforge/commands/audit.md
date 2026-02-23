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

**Valid extraction types** (coverage scoping): `business-rules`, `database`, `ui-flows`, `workflows`
**Valid generation types** (coverage scoping): `user-stories`, `documentation`, `diagrams`
**Valid special types** (coverage scoping): `analysis` (checks analysis.xml for stale file entries)
**Valid audit modes** (standalone — not combinable with the above): `accuracy`, `consistency`, `full`

If the type is an audit mode (`accuracy`, `consistency`, `full`):
- These are standalone audit modes that run specialized workflows
- They are NOT combinable with extraction/generation/special types
- Route to the corresponding workflow section (see **Audit Mode Routing** below)
- Skip Steps 2-7 (those belong to the coverage audit workflow)

If the type is invalid:
```
Error: Unknown audit type '[type]'.
Valid types: analysis, business-rules, database, ui-flows, workflows, user-stories, documentation, diagrams, accuracy, consistency, full
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

### Audit Mode Routing

If the `[type]` argument is an audit mode, route to the corresponding workflow section. **Do not continue to Step 2** — Steps 2-7 are the coverage audit workflow only.

| Type Argument | Route To | Description |
|---------------|----------|-------------|
| `accuracy` | **Accuracy Audit Workflow** (below) | Verify extraction items against source codebase |
| `consistency` | **Consistency Audit Workflow** (below) | Check internal consistency of extraction corpus |
| `full` | **Full Audit Workflow** (below) | Run coverage + consistency + accuracy in sequence |
| _(any other valid type, or no type)_ | **Step 2** (continue below) | Default coverage audit workflow |

---

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

## Accuracy Audit Workflow

**Activated when**: `/reforge.audit accuracy` is invoked (routed from Audit Mode Routing above).

### Accuracy Step 1: Prerequisites

1. **Source codebase availability check**:
   - The agent MUST verify that `$SOURCE_ROOT` (the root directory of the source codebase being analyzed) is accessible
   - `$SOURCE_ROOT` is resolved from the project context established by `/reforge.init` (stored in `.reforge/memory/project-context.xml` or `.reforge/config.json`)
   - If the source root cannot be determined or accessed:
     ```
     Error: Source codebase not available. The accuracy audit requires access to the original source code.
       Expected source root: $SOURCE_ROOT

       Ensure the source codebase is accessible and /reforge.init has been run.
     ```
   - Abort the accuracy audit — do not proceed without source access

2. **Extraction corpus availability check**:
   - Verify `$EXTRACTIONS_DIR` exists and contains at least one extraction XML file
   - If no extraction files exist:
     ```
     Error: No extraction files found in $EXTRACTIONS_DIR.
       Run /reforge.extract first to create extractions before auditing accuracy.
     ```

3. **Set output variables**:
   - `$AUDIT_DIR` = `$PROJECT_OUTPUT_DIR/audit/`
   - Ensure `$AUDIT_DIR` directory exists (create if needed)

### Accuracy Step 2: Enumerate Extraction Items

The agent MUST read all extraction files and build a complete inventory of items to verify.

1. **Read all extraction files** from `$EXTRACTIONS_DIR`:
   - `business-rules.xml`, `database.xml`, `ui-flows.xml`, `workflows.xml`
   - Skip any extraction type that does not have a file present

2. **Collect items with IDs**:
   - For each extraction file, find all elements with an `id` attribute
   - Record for each item: `id`, `extraction-type` (derived from filename), element name, any `source` or `file` attributes, any `line` attributes

3. **Categorize by extraction type**:
   - Group items by their extraction type (business-rules, database, ui-flows, workflows)
   - Count totals per category

4. **Record totals**:
   - `$TOTAL_ITEMS` = total extraction items across all categories
   - `$ITEMS_BY_CATEGORY` = map of category → item count

### Accuracy Step 3: Determine Verification Scope (Sampling)

The agent MUST determine whether to verify all items or use statistical sampling.

1. **Check for full verification override**:
   - If `--full-verify` flag is present: verify ALL items (methodology = `census`)
   - If `$TOTAL_ITEMS` < 500: default to full verification (methodology = `census`)

2. **Determine sample size**:
   - If `--sample-size N` is provided: use N as absolute sample size (overrides `--sample-rate`)
   - If `--sample-rate R` is provided: sample size = ceil($TOTAL_ITEMS * R)
   - Otherwise: use default 20% rate → sample size = ceil($TOTAL_ITEMS * 0.20)

3. **Stratified sampling**:
   - For each category, compute stratum sample size proportional to its share of total items:
     - `stratum_sample = max(5, round(category_count / $TOTAL_ITEMS * $SAMPLE_SIZE))`
   - Minimum 5 items per stratum (if the stratum has >= 5 items; otherwise sample all)
   - Adjust final sample size if rounding causes total to differ from target

4. **Systematic Nth-item selection**:
   - Within each stratum, select every Nth item where N = floor(stratum_population / stratum_sample)
   - Starting from a random offset within [0, N)
   - This ensures uniform distribution across the stratum

5. **Record sampling metadata**:
   - `$METHODOLOGY` = `sampling` or `census`
   - `$SAMPLE_RATE`, `$SAMPLE_SIZE`, `$STRATA` details

### Accuracy Step 4: Multi-Check-Type Verification

For each item in the verification scope, the agent MUST apply the applicable check types using native tools (Grep, Read, Glob).

**Check Type Definitions** (FR-023):

1. **`identifier-exists`**: Word-boundary search for the item's identifier in the source codebase
   - Use Grep with pattern `\b<identifier>\b` across `$SOURCE_ROOT`
   - Pass: ≥1 word-boundary match found
   - Fail: 0 matches found
   - Record match count and file locations

2. **`term-exists`**: Search for the item's name/term in comments, strings, and documentation
   - Use Grep with the term (case-insensitive) across `$SOURCE_ROOT`
   - Scope: comments, string literals, documentation files
   - Pass: term found in relevant context
   - Fail: term not found anywhere

3. **`line-reference`**: Verify that the stated source file exists and has content at the stated line
   - Use Read to check the file exists and read the stated line number
   - Pass: file exists AND line number is within range AND has content
   - Fail: file missing OR line out of range OR line empty

4. **`content-match`**: Compare extracted code snippet against actual source content
   - Use Read to get actual content at the stated file/line location
   - Compare with whitespace-insensitive matching (normalize whitespace before comparison)
   - Pass: extracted snippet matches actual source content (after whitespace normalization)
   - Fail: content differs materially

5. **`expansion-match`**: Verify acronym expansion matches source context
   - Search for the acronym's stated expansion near occurrences of the acronym in source
   - Use Grep to find acronym occurrences, then Read surrounding context
   - Pass: expansion text found near an acronym occurrence
   - Fail: expansion not found near any occurrence

6. **`count-match`**: Recount elements and compare to stated count
   - Read the source file/element and count the relevant items
   - Pass: actual count matches stated count
   - Fail: counts differ

7. **`relationship-match`**: Verify stated relationship (calls, inherits, imports, etc.) exists
   - Search for evidence of the stated relationship in source code
   - Use Grep to find call sites, inheritance declarations, import statements
   - Pass: relationship evidence found
   - Fail: no evidence of stated relationship

**Check Type Selection Per Item Type**:

| Extraction Type | Always Apply | Apply When Available |
|----------------|-------------|---------------------|
| business-rules | `identifier-exists` | `line-reference`, `content-match`, `relationship-match` |
| database | `identifier-exists` | `line-reference`, `content-match`, `count-match` |
| ui-flows | `identifier-exists` | `line-reference`, `content-match` |
| workflows | `identifier-exists` | `line-reference`, `relationship-match` |
| *(acronyms/glossary)* | `identifier-exists`, `term-exists` | `expansion-match` |

The agent MUST apply at least `identifier-exists` for every item. Additional check types are applied when the item has the necessary attributes (e.g., `line-reference` only when the item has a `line` attribute and `source file` attribute).

### Accuracy Step 5: Verdict Classification

For each verified item, the agent MUST assign one of five canonical verdicts (FR-022):

| Verdict | Criteria |
|---------|----------|
| `confirmed` | All applicable checks passed; item verified in source |
| `plausible` | Partial match only (e.g., identifier found as substring but not word-boundary match, or found in comments but not code); not conclusively confirmed |
| `incorrect` | Found in source but with wrong value, wrong line, or wrong context |
| `fabricated` | No evidence of item in source codebase (all checks failed, 0 matches) |
| `skipped` | Check not applicable or could not be performed (e.g., binary file, inaccessible path) |

**Decision logic**:
- If ALL applicable checks pass → `confirmed`
- If identifier found ONLY as substring (no word-boundary match) → `plausible`
- If identifier found but content/line/relationship wrong → `incorrect`
- If identifier NOT found at all (0 matches of any kind) → `fabricated`
- If checks cannot be performed → `skipped`

### Accuracy Step 6: Score Computation

The agent MUST compute accuracy scores at multiple levels (FR-004).

1. **Overall accuracy score**:
   - `accuracy_score = (confirmed_count / verified_count) * 100`
   - `verified_count` excludes items with verdict `skipped`

2. **Per-category breakdown**:
   - For each extraction type: `category_accuracy = (category_confirmed / category_verified) * 100`

3. **Per-check-type breakdown**:
   - For each check type: `total`, `passed`, `failed`

4. **Confidence interval** (when methodology = `sampling`):
   - Use the Wald interval formula for 95% confidence:
     - `p = accuracy_score / 100`
     - `SE = sqrt(p * (1 - p) / n)` where n = verified_count
     - `margin_of_error = 1.96 * SE * 100` (in percentage points)
     - `lower = accuracy_score - margin_of_error`
     - `upper = accuracy_score + margin_of_error`

5. **Low-accuracy stratum flagging** (FR-008):
   - If any stratum has accuracy < 90%, flag it with a recommendation for full verification:
     ```
     Warning: Stratum '[category]' has accuracy [X]% (below 90% threshold).
     Recommend running: /reforge.audit accuracy --full-verify
     ```

### Accuracy Step 7: Generate accuracy-audit-report.xml

The agent MUST generate the accuracy audit report following the schema defined in `.reforge/schemas/accuracy-audit-report.md`.

Write the report to: `$AUDIT_DIR/accuracy-audit-report.xml`

The report MUST include:
- Root element `<accuracy-audit-report>` with all required attributes (project-id, version, generated, methodology, sample-rate, total-items, verified-items, accuracy-score)
- `<sampling-metadata>` section (when methodology = sampling): sample-rate, total-population, sample-size, confidence-level, confidence-interval, margin-of-error, per-stratum breakdown
- `<accuracy-summary>` section: overall stats, by-category breakdown, by-check-type breakdown
- `<verification-results>` section: individual item-level results with checks and correction hints
- `<recommendations>` section: actionable recommendations based on findings

### Accuracy Step 8: Generate accuracy-correction-plan.xml

The agent MUST generate a correction plan for items that need fixing (FR-005, FR-018, FR-019).

Write the correction plan to: `$AUDIT_DIR/accuracy-correction-plan.xml`

**Correction entries are generated for**:
- Items with verdict `fabricated` → correction type `fabricated`, action `delete <extraction-file> <item-id>`, severity `critical`
- Items with verdict `incorrect` → correction type `inaccurate`, action `/reforge.reanalyze <source-file>`, severity `high`

**Each correction entry MUST include**:
- `source-audit-type="accuracy"`
- `severity` attribute (critical for fabricated, high for incorrect)
- `<evidence>` child element with human-readable description of failed checks
- `category="extraction"` (since accuracy corrections target extraction items)

**Priority ordering** follows the extended correction plan schema: severity-based within category (critical → high → medium → low), fabricated items before inaccurate items.

### Accuracy Step 9: Display Results

The agent MUST display a human-readable summary:

```
=== Reforge Accuracy Audit Report ===
Project: [project-name]
Methodology: [sampling at X% | full verification]

--- Accuracy Score ---
Overall: [X]% ([confirmed] of [verified] items confirmed)
[If sampling: 95% CI: [lower]% - [upper]% (±[margin]%)]

--- Accuracy by Category ---
| Category       | Verified | Confirmed | Fabricated | Accuracy |
|----------------|----------|-----------|------------|----------|
| Business Rules | [N]      | [N]       | [N]        | [X]%     |
| Database       | [N]      | [N]       | [N]        | [X]%     |
| UI Flows       | [N]      | [N]       | [N]        | [X]%     |
| Workflows      | [N]      | [N]       | [N]        | [X]%     |

--- Verdict Summary ---
Confirmed: [N] | Plausible: [N] | Incorrect: [N] | Fabricated: [N] | Skipped: [N]

--- Top Findings ---
[List up to 10 most significant findings — fabricated items first, then incorrect]

--- Correction Plan ---
Total corrections: [N]
  Fabricated (delete): [N]
  Inaccurate (re-analyze): [N]
Path: $AUDIT_DIR/accuracy-correction-plan.xml

--- Next Steps ---
→ Review accuracy report: $AUDIT_DIR/accuracy-audit-report.xml
→ Run /reforge.fix --plan $AUDIT_DIR/accuracy-correction-plan.xml to execute corrections
→ Run /reforge.audit consistency for internal consistency checks
→ Run /reforge.audit full for unified quality assessment
```

---

## Consistency Audit Workflow

**Activated when**: `/reforge.audit consistency` is invoked (routed from Audit Mode Routing above).

### Consistency Step 1: Prerequisites

1. **Extraction corpus availability check**:
   - Verify `$EXTRACTIONS_DIR` exists and contains at least one extraction XML file
   - If no extraction files exist:
     ```
     Error: No extraction files found in $EXTRACTIONS_DIR.
       Run /reforge.extract first to create extractions before auditing consistency.
     ```

2. **Set output variables**:
   - `$AUDIT_DIR` = `$PROJECT_OUTPUT_DIR/audit/`
   - `$GENERATED_DIR` = `$PROJECT_OUTPUT_DIR/generated/`
   - Ensure `$AUDIT_DIR` directory exists (create if needed)

3. **Initialize counters**:
   - `$TOTAL_CHECKS` = 0, `$PASSED_CHECKS` = 0, `$FAILED_CHECKS` = 0

### Consistency Step 1.5: Metrics Registry Recomputation (FR-015)

Before any scanning, the agent MUST recompute the metrics registry from current extraction data.
This ensures the audit always validates against the freshest canonical values, regardless of
whether a `metrics-registry.xml` file already exists from a prior generation run.

1. **Discover extraction files**:
   - Glob all XML files in each extraction category subdirectory under `$EXTRACTIONS_DIR`
     (same discovery procedure as `generate.md` Multi-File Extraction Discovery)
   - Also read `$ANALYSIS_DIR/analysis.xml` for codebase-level metrics

2. **Compute canonical metrics**:
   - For each extraction category, count elements using the actual element names present in XML
   - Assign deterministic metric IDs following the `MET-{CATEGORY}-{NAME}` pattern
   - Record per-file breakdowns for aggregate metrics
   - Compute derivation formulas showing per-file breakdown sums

3. **Handle missing or incomplete extraction data gracefully**:
   - If an extraction category has no files, skip the corresponding metrics
   - Report which metrics could not be computed (e.g., "Skipping MET-UI-SCREEN-COUNT: no
     ui-flows extraction files found")
   - Continue with available data — do NOT fail the audit due to missing extraction categories

4. **Write the registry**:
   - Write to `$PROJECT_OUTPUT_DIR/metrics-registry.xml` following the metrics-registry schema
     (`.reforge/schemas/metrics-registry.md`)
   - Include `<configuration>` section with default tolerance rules:
     - `approximately` / `~` / `about` / `roughly`: ±10%
     - `nearly`: ±5%
     - `over` / `more than`: gte direction (value must be at least the registry value)
     - `fewer than` / `under` / `less than`: lte direction (value must be at most the registry value)
   - Include `<scan-patterns>` section with patterns for common metric categories
   - Include empty `<exclusion-list>` on first creation (or preserve existing exclusions if
     a prior registry exists)

5. **Bootstrap detection**:
   - Set `$REGISTRY_IS_BOOTSTRAP` = true if no prior `metrics-registry.xml` existed before
     this step wrote one
   - This flag is used in Consistency Step 6.8 for bootstrap messaging

6. **Store registry path for subsequent steps**:
   - `$METRICS_REGISTRY` = `$PROJECT_OUTPUT_DIR/metrics-registry.xml`

### Consistency Step 2: Arithmetic Checks (FR-009)

The agent MUST compare stated metadata counts against actual element counts per extraction file. Zero tolerance for mismatches.

1. **For each extraction file** in `$EXTRACTIONS_DIR`:
   - Read the file and locate `<metadata>` element
   - If no `<metadata>` element or no `total-count` attribute exists:
     - Record as `no-metadata` — not a failure, skip this file's arithmetic check
   - If `total-count` attribute exists:
     - Count actual child elements (items with `id` attributes)
     - Compare stated count vs actual count
     - Record check result: `pass` if equal, `fail` if different
     - Increment `$TOTAL_CHECKS` and `$PASSED_CHECKS` or `$FAILED_CHECKS`

2. **Check confidence-distribution sums** (if present):
   - If the extraction file has a `<confidence-distribution>` element with count attributes
   - Sum all distribution counts
   - Compare against actual element count
   - Record check result

### Consistency Step 3: Cross-Reference Validation (FR-010)

The agent MUST verify that all cross-references resolve to existing targets.

1. **File references**:
   - Find all `<source file="...">` and `<cross-ref target="...">` attributes across extraction files
   - For each file reference, verify the target file exists on disk at `$SOURCE_ROOT`
   - Record check result per reference

2. **ID references**:
   - Find all internal ID references (elements referencing other element IDs within the corpus)
   - Verify each referenced ID exists in the extraction corpus
   - Record check result per reference

3. **Update counters**: Increment `$TOTAL_CHECKS`, `$PASSED_CHECKS`, `$FAILED_CHECKS`

### Consistency Step 4: Duplicate ID Detection (FR-011)

The agent MUST detect duplicate element IDs across extraction files.

1. **Collect all IDs**:
   - Read all extraction files and collect every `id` attribute with its file path and element location
   - Build a map: `id → list of (file, element-path)`

2. **Detect duplicates**:
   - For each ID that appears more than once:
     - **Within same file** → severity `critical`
     - **Within same category** (same extraction type, different implied locations) → severity `critical`
     - **Cross-category** (different extraction types) → severity `info`

3. **Record findings**: Each duplicate ID group is recorded (not counted as a check pass/fail — tracked separately as `$TOTAL_IDS_SCANNED` and `$DUPLICATES_FOUND`)

### Consistency Step 5: Freshness Checks (FR-012)

The agent MUST compare extraction timestamps against generated document timestamps and verify numeric claims.

1. **For each generated document** in `$GENERATED_DIR`:
   - Attempt to parse the document (markdown or HTML)
   - If unparseable: record as `skipped` with a note, increment `$TOTAL_CHECKS` (as skipped)

2. **Timestamp comparison**:
   - Extract `generated` timestamp from the generated document (if available)
   - Compare against the `generated` timestamp of the corresponding extraction file
   - If generated document is older than extraction: potential staleness

3. **Numeric claim verification**:
   - Search the generated document for numeric claims about extraction counts (e.g., "981 business rules", "245 database entities")
   - Compare each claimed number against the current actual count in the corresponding extraction XML
   - If values differ: record a `<discrepancy>` with `metric`, `generated-value`, `extraction-value`

4. **Update counters**: Increment `$TOTAL_CHECKS`, `$PASSED_CHECKS`, `$FAILED_CHECKS`

### Consistency Step 6: Cross-Document Discrepancy Detection (FR-013)

The agent MUST scan generated documents for numeric claims about the same metric cited with different values.

1. **Extract numeric claims**:
   - For each generated document in `$GENERATED_DIR`, find all numeric claims mentioning extraction-related metrics
   - Pattern match for phrases like: "[N] business rules", "[N] files analyzed", "total of [N]", etc.
   - Record: `metric name`, `value`, `file`, `location` (section/line)

2. **Cluster by metric**:
   - Group all claims by their metric name (normalized)
   - For each metric with 2+ occurrences: check if all values agree

3. **Record discrepancies**:
   - For each metric with conflicting values, create a discrepancy cluster
   - Generate a resolution recommendation (e.g., "Update documentation.md to use current value of X from extraction.xml")

4. **Update counters**: Each cross-document check counts toward `$TOTAL_CHECKS`

### Consistency Step 6.5: Metrics Registry Document Scanning (FR-016)

The agent MUST scan all generated documents against the authoritative metrics registry to detect
numeric claim discrepancies.

1. **Determine scan scope**:
   - Scan all files in `$GENERATED_DIR/` (recursively) matching configured file types from the
     registry's `<scan-file-types>` configuration (default: `.md`, `.html`, `.puml`, `.mmd`, `.svg`)
   - Also scan `$PROJECT_OUTPUT_DIR/diagrams/` (if present) — diagram source files may be stored
     separately from generated documents
   - Initialize: `$CLAIMS_SCANNED` = 0, `$DISCREPANCIES` = []
   - **Deduplication rule**: When HTML files contain inline SVG, a metric claim may appear in
     both the HTML parser's results and the SVG `<text>` content. The agent MUST detect each
     metric at a unique (file, line) location only once — do not double-count claims from
     embedded SVG within HTML reports

2. **For each file in scan scope**:
   - Read the file contents
   - Apply scan pattern descriptions from the registry's `<scan-patterns>` section to identify
     numeric claims. The agent reads the document and uses its language understanding to recognize
     phrases matching each pattern's `description` attribute (e.g., "Numeric value followed by
     'business rules'" matches "981 business rules" or "approximately 850 business rules")
   - For each identified numeric claim:
     a. Extract the numeric value and any qualifying language (approximately, ~, about, etc.)
     b. Match against registry metrics using the pattern's `metric-hint` and value proximity
     c. If a metric ID annotation is present (`<!-- metric: MET-XXX -->` in HTML/Markdown,
        `' metric: MET-XXX` in PlantUML, or `%% metric: MET-XXX` in Mermaid), use it as a
        direct match (confidence = `high`)
     d. If no annotation, match by pattern category and value proximity:
        - Pattern + unit/noun match → confidence `high`
        - Pattern match but ambiguous unit → confidence `medium`
        - Value-proximity only → confidence `low`
     e. Increment `$CLAIMS_SCANNED`

3. **Classify each matched claim**:
   - **consistent**: Document value exactly matches registry value (and no qualifier present)
   - **approximate-match**: Qualifier present and value is within the tolerance range
   - **mismatch**: No qualifier and value differs from registry, OR qualifier present but value
     is outside tolerance range
   - **unregistered**: Numeric claim matches a scan pattern but no corresponding metric exists
     in the registry
   - **ambiguous**: Multiple candidate metrics match with similar confidence — report all
     candidates with confidence indicators (FR-020)

4. **For ambiguous matches**:
   - Report all candidate metric matches with their confidence levels
   - Set discrepancy action to `investigate`
   - The agent MUST NOT arbitrarily choose one candidate — ambiguity requires human review

### Consistency Step 6.6: Tolerance Application (FR-012, FR-013)

The agent MUST apply tolerance rules when qualifying language is present.

1. **Detect qualifying language**:
   - When a numeric claim is accompanied by qualifying language (approximately, ~, about,
     roughly, nearly, over, fewer than, more than, less than, under), the agent MUST
     identify the qualifier and look up the corresponding tolerance rule

2. **Apply tolerance rules**:
   - Read tolerance configuration from `$METRICS_REGISTRY` `<configuration>/<tolerance-defaults>`
   - If the matched metric has a per-metric `<tolerance>` override, use it instead of the default
   - For percentage-based tolerance (`percent` attribute):
     - Compute allowed range: `[registry_value * (1 - percent/100), registry_value * (1 + percent/100)]`
     - If document value falls within range → classify as `approximate-match`
     - If outside range → classify as `mismatch` (warning severity)
   - For direction-based tolerance (`direction` attribute):
     - `gte`: Document value must be >= registry value
     - `lte`: Document value must be <= registry value
   - Values without any qualifying language MUST require exact match (FR-013)

3. **Record tolerance application**:
   - For each claim where tolerance was applied, record the qualifier, tolerance percentage,
     computed range, and whether the value fell within range

### Consistency Step 6.7: Exclusion List Application (FR-019)

The agent MUST check the exclusion list before reporting unregistered metrics.

1. **Load exclusion list**:
   - Read `<exclusion-list>` from `$METRICS_REGISTRY` `<configuration>`
   - Build a list of excluded pattern texts

2. **For each unregistered numeric claim** (from Step 6.5):
   - Check if the claim's text matches any exclusion pattern
   - If matched: suppress the claim — do not report as a discrepancy
   - Record the suppression in `$EXCLUSIONS_APPLIED` for the audit report

3. **Report new unregistered metrics**:
   - Unregistered claims NOT matching any exclusion pattern are reported as `info`-severity
     discrepancies with action `register-or-ignore`
   - These represent numeric claims that may be legitimate metrics not yet tracked by the
     registry, or incidental numbers (page counts, section numbers, etc.)

### Consistency Step 6.8: Metrics Discrepancy Report Generation (FR-016)

The agent MUST generate the `<metrics-registry-checks>` section of the consistency audit report.

1. **Build discrepancy list**:
   - From Step 6.5 results, collect all claims classified as `mismatch`, `unregistered`
     (non-excluded), or `ambiguous`
   - Assign severity:
     - `critical`: Exact value mismatch (no qualifier, values differ)
     - `warning`: Approximate value outside tolerance range
     - `info`: Unregistered metric (not in exclusion list)
   - Assign unique IDs: `DIS-001`, `DIS-002`, ...
   - Assign actions:
     - `critical` mismatch → `regenerate`
     - `warning` mismatch → `review`
     - `info` unregistered → `register-or-ignore`
     - ambiguous → `investigate`

2. **Build scan summaries**:
   - Per-file summary: for each scanned file, record claims found, discrepancies, and status
   - Per-metric summary: for each registry metric, record occurrences found, consistent count,
     discrepant count, and status

3. **Build exclusions applied**:
   - Record each exclusion pattern that matched, the number of suppressed matches, and
     affected files

4. **Bootstrap messaging**:
   - If `$REGISTRY_IS_BOOTSTRAP` is true (from Step 1.5), include a note in the report:
     "This is a bootstrap/migration scan. No prior metrics registry existed. Discrepancies
     represent the pre-registry state of generated documents and can be resolved incrementally
     via /reforge.fix."

### Consistency Step 6.9: Metrics Correction Item Generation (FR-016)

The agent MUST generate correction items for metrics discrepancies.

1. **For critical and warning discrepancies** (from Step 6.8):
   - Generate correction items using type `metric-mismatch`
   - Set category to `metrics-consistency`
   - Set `source-audit-type="consistency"`
   - Set severity matching the discrepancy severity
   - Set action to `/reforge.generate <doc-type> --refresh-metrics` for the affected document
   - Include `<evidence>` with the specific metric ID, registry value, document value, and
     file/line location

2. **For non-excluded unregistered metrics** (info severity):
   - Generate correction items using type `unregistered-metric`
   - Set category to `metrics-consistency`
   - Set `source-audit-type="consistency"`
   - Set severity to `info`
   - Set action to `register-or-exclude <file> line <N>`
   - Include `<evidence>` describing the unregistered claim

3. **Update counters**:
   - Each discrepancy (critical or warning) counts as a failed check
   - Each consistent claim counts as a passed check
   - Increment `$TOTAL_CHECKS`, `$PASSED_CHECKS`, `$FAILED_CHECKS` accordingly

### Consistency Step 7: Score Computation

The agent MUST compute the consistency score (FR-014).

1. **Overall consistency score**:
   - `consistency_score = ($PASSED_CHECKS / $TOTAL_CHECKS) * 100`

2. **Per-category breakdown**:
   - arithmetic: passed/total for arithmetic checks
   - cross-reference: passed/total for cross-reference checks
   - freshness: passed/total for freshness checks
   - cross-document: discrepancies count
   - metrics-consistency: claims scanned, discrepancies by severity (critical/warning/info)

### Consistency Step 8: Generate consistency-audit-report.xml

The agent MUST generate the consistency audit report following the schema defined in `.reforge/schemas/consistency-audit-report.md`.

Write the report to: `$AUDIT_DIR/consistency-audit-report.xml`

The report MUST include:
- Root element `<consistency-audit-report>` with all required attributes (project-id, version, generated, total-checks, passed-checks, failed-checks, consistency-score)
- `<arithmetic-checks>` section with individual check results
- `<cross-reference-checks>` section with individual check results
- `<duplicate-id-checks>` section with duplicate groups and severity
- `<freshness-checks>` section with individual check results and discrepancies
- `<cross-document-checks>` section with discrepancy clusters and recommendations
- `<metrics-registry-checks>` section (from Step 6.8) with:
  - Summary attributes: total-claims-scanned, total-discrepancies, critical-count, warning-count, info-count, files-scanned, registry-version
  - `<discrepancy>` elements for each detected mismatch with full attributes (id, severity, metric-id, registry-value, document-value, file, line, context, confidence, action, pattern-id, qualifier, tolerance-percent)
  - `<scan-summary>` with per-file and per-metric verification summaries
  - `<exclusions-applied>` section documenting suppressed patterns

### Consistency Step 9: Generate consistency-correction-plan.xml

The agent MUST generate a correction plan for consistency issues (FR-014, FR-018, FR-019).

Write the correction plan to: `$AUDIT_DIR/consistency-correction-plan.xml`

**Correction entries are generated for**:
- Arithmetic mismatches → correction type `arithmetic` or `inconsistent`, category `metadata`, action `update-metadata <file> <attribute>`
- Broken cross-references → correction type `broken-ref`, category `extraction`, action depends on reference type
- Duplicate IDs (critical severity only) → correction type `duplicate-id`, category `extraction`
- Stale generated documents → correction type `stale`, category `generation`, action `/reforge.generate <type>`
- Cross-document discrepancies → correction type `inconsistent`, category `cross-document`
- Metrics registry mismatches (from Step 6.9) → correction type `metric-mismatch`, category `metrics-consistency`, action `/reforge.generate <doc-type> --refresh-metrics`
- Unregistered metrics (from Step 6.9) → correction type `unregistered-metric`, category `metrics-consistency`, action `register-or-exclude <file> line <N>`

**Each correction entry MUST include**:
- `source-audit-type="consistency"`
- `severity` attribute
- `<evidence>` child element describing the specific check failure

**Priority ordering**: metadata corrections before cross-document corrections before metrics-consistency corrections before generation corrections (per extended correction plan schema).

### Consistency Step 10: Display Results

The agent MUST display a human-readable summary:

```
=== Reforge Consistency Audit Report ===
Project: [project-name]

--- Consistency Score ---
Overall: [X]% ([passed] of [total] checks passed)

--- Checks by Category ---
| Category           | Total | Passed | Failed | Score   |
|--------------------|-------|--------|--------|---------|
| Arithmetic         | [N]   | [N]    | [N]    | [X]%    |
| Cross-Reference    | [N]   | [N]    | [N]    | [X]%    |
| Duplicate IDs      | [N] scanned | [N] duplicates found    ||
| Freshness          | [N]   | [N]    | [N]    | [X]%    |
| Cross-Document     | [N] checked | [N] discrepancies       ||
| Metrics Consistency| [N] claims | [N] discrepancies       ||

--- Metrics Consistency ---
Claims scanned: [N] across [N] files
Registry metrics: [N] (registry version: [version])
Discrepancies: [critical] critical, [warning] warning, [info] info

[If critical discrepancies > 0:]
Critical mismatches:
  | File | Line | Metric | Expected | Actual |
  |------|------|--------|----------|--------|
  | [file] | [line] | [MET-XXX] | [registry-value] | [document-value] |
  ...

[If bootstrap scan:]
ℹ️ Bootstrap scan: No prior metrics registry existed. This is a migration scan.
Discrepancies represent the pre-registry state of existing generated documents
and can be resolved incrementally:
  → Run /reforge.fix to apply corrections from the correction plan
  → Or run /reforge.generate <type> --refresh-metrics to regenerate specific documents
  → Existing documents without corrections will continue to work but may contain stale values

--- Top Findings ---
[List up to 10 most significant findings — metric mismatches first, then arithmetic/cross-ref failures]

--- Correction Plan ---
Total corrections: [N]
  By category: [metadata: N] [extraction: N] [cross-document: N] [metrics-consistency: N] [generation: N]
Path: $AUDIT_DIR/consistency-correction-plan.xml

--- Next Steps ---
→ Review consistency report: $AUDIT_DIR/consistency-audit-report.xml
→ Run /reforge.fix --plan $AUDIT_DIR/consistency-correction-plan.xml to execute corrections
→ Run /reforge.audit accuracy for source verification
→ Run /reforge.audit full for unified quality assessment
```

---

## Full Audit Workflow

**Activated when**: `/reforge.audit full` is invoked (routed from Audit Mode Routing above).

### Full Step 1: Sequential Execution

The agent MUST run all three audit types in sequence (FR-015):

1. **Run Coverage Audit** (Steps 0-7 above):
   - Execute the standard coverage audit workflow
   - Collect `$COVERAGE_SCORE` from the generated `audit-report.xml`
   - **IMPORTANT**: Read the coverage audit's `correction-plan.xml` into memory before it can be overwritten by the merge step

2. **Run Consistency Audit** (Consistency Steps 1-10 above):
   - Execute the full consistency audit workflow (includes metrics registry checks from Steps 1.5, 6.5-6.9)
   - Collect `$CONSISTENCY_SCORE` from the generated `consistency-audit-report.xml`
   - Note: the consistency score now incorporates metrics registry scan results — metric claim discrepancies count as failed checks

3. **Run Accuracy Audit** (Accuracy Steps 1-9 above):
   - Execute the full accuracy audit workflow
   - Collect `$ACCURACY_SCORE` from the generated `accuracy-audit-report.xml`

### Full Step 2: Composite Score and Quality Rating

The agent MUST compute the composite quality score and map it to a rating (FR-016, FR-017).

1. **Composite score computation**:
   - `composite_score = ($COVERAGE_SCORE * 0.25) + ($CONSISTENCY_SCORE * 0.35) + ($ACCURACY_SCORE * 0.40)`

2. **Quality rating mapping**:

   | Rating | Score Range | Action Recommendation |
   |--------|------------|----------------------|
   | Excellent | >= 98% | Ready for downstream consumption |
   | Good | 95 - 97.9% | Minor corrections recommended before use |
   | Acceptable | 90 - 94.9% | Review corrections; address critical items before use |
   | Poor | 80 - 89.9% | Significant corrections required; re-extract affected areas |
   | Critical | < 80% | Major quality issues; consider full re-extraction |

3. **Dimension highlights**:
   - For each dimension (coverage, consistency, accuracy), extract the single most significant finding

### Full Step 3: Merge Correction Plans

The agent MUST merge all individual correction plans into a unified plan (FR-015, FR-019).

1. **Read all correction plans**:
   - Coverage: `$AUDIT_DIR/correction-plan.xml` (read from memory — captured in Full Step 1)
   - Consistency: `$AUDIT_DIR/consistency-correction-plan.xml`
   - Accuracy: `$AUDIT_DIR/accuracy-correction-plan.xml`

2. **Merge entries**:
   - Combine all `<correction>` entries into a single list
   - Ensure each entry has `source-audit-type` set (add `source-audit-type="coverage"` to coverage entries if not present)
   - Re-number `id` attributes sequentially (COR-001, COR-002, ...)

3. **Re-prioritize**:
   - Sort by category priority order: `analysis` → `extraction` → `metadata` → `cross-document` → `metrics-consistency` → `generation`
   - Within each category, sort by severity: `critical` → `high` → `medium` → `low`
   - Within same severity: fabricated before inaccurate, metric-mismatch before unregistered-metric, stale before gaps
   - Assign `priority` attributes sequentially (1, 2, 3, ...)

4. **Write merged plan**:
   - Write to `$AUDIT_DIR/correction-plan.xml` (overwrites the coverage-only version)
   - Update `total-items` count on root element
   - Set `source-audit` to `$AUDIT_DIR/full-audit-report.xml`

### Full Step 4: Generate full-audit-report.xml

The agent MUST generate the full audit report following the schema defined in `.reforge/schemas/full-audit-report.md`.

Write the report to: `$AUDIT_DIR/full-audit-report.xml`

The report MUST include:
- Root element `<full-audit-report>` with all required attributes (project-id, version, generated, composite-score, quality-rating)
- `<dimension-scores>` section with individual dimension scores, weights, and weighted contributions
- `<quality-assessment>` section with rating, action recommendation, and dimension highlights
- `<correction-summary>` section with total corrections, by-source breakdown, and merged plan path

### Full Step 5: Display Results

The agent MUST display a human-readable summary:

```
=== Reforge Full Audit Report ===
Project: [project-name]

--- Quality Rating ---
[Rating]: [composite_score]%
[Action recommendation]

--- Dimension Scores ---
| Dimension   | Score  | Weight | Contribution |
|-------------|--------|--------|-------------|
| Coverage    | [X]%   | 0.25   | [X]         |
| Consistency | [X]%   | 0.35   | [X]         |
| Accuracy    | [X]%   | 0.40   | [X]         |
| **Composite** | **[X]%** |      |             |

--- Key Findings ---
  Coverage: [highlight]
  Consistency: [highlight]
  Accuracy: [highlight]

--- Correction Plan Summary ---
Total corrections: [N]
  By source: [coverage: N] [consistency: N] [accuracy: N]
Path: $AUDIT_DIR/correction-plan.xml

--- Reports Generated ---
  Coverage:    $AUDIT_DIR/audit-report.xml
  Consistency: $AUDIT_DIR/consistency-audit-report.xml
  Accuracy:    $AUDIT_DIR/accuracy-audit-report.xml
  Full:        $AUDIT_DIR/full-audit-report.xml
  Corrections: $AUDIT_DIR/correction-plan.xml (merged)

--- Next Steps ---
→ Review full report: $AUDIT_DIR/full-audit-report.xml
→ Run /reforge.fix to execute merged correction plan
→ Run /reforge.fix --interactive for step-by-step correction approval
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
