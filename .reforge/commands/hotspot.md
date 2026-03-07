# /reforge.hotspot

> Identify high-risk modules by computing composite scores from complexity, dependency density, issue density, and business rule concentration

## Command Syntax

```
/reforge.hotspot [--threshold <0-100>] [--top <n>] [--format html|xml] [--json]
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `--threshold` | No | Minimum composite risk score to include (0-100, default: 25) |
| `--top` | No | Limit output to top N hotspots (default: all above threshold) |
| `--format` | No | Output format: `xml` (default) or `html` (generates HTML report alongside XML) |
| `--json` | No | Output hotspot summary as JSON for tooling integration |

## Overview

This command computes a composite risk score for each module in the codebase by combining:

1. **Complexity Score** (weight: 0.30) — Cyclomatic and cognitive complexity
2. **Dependency Score** (weight: 0.25) — Afferent + efferent coupling density
3. **Issue Density Score** (weight: 0.25) — Issues per lines of code
4. **Business Rule Density** (weight: 0.20) — Concentration of business rules

Modules are ranked by composite risk score to produce a prioritized heatmap for modernization planning.

The hotspot command produces:
- **`hotspot-analysis.xml`** — Ranked risk analysis (schema: `.reforge/schemas/hotspot-analysis.md`)

## Prerequisites

- Completed analysis (`$ANALYSIS_DIR/analysis.xml` must exist)
- At least one extraction type completed (more extractions = more accurate scores)
- Recommended: dependencies, issues, call-sites, and business-rules extractions

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
$DERIVED_DIR = $PROJECT_OUTPUT_DIR/derived
```

Create the derived output directory if it does not exist:
```
mkdir -p $DERIVED_DIR
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
- Identify hotspot-related items and display their status

**On command completion (success only):**
- Locate the plan item by searching for `<!-- reforge:hotspot -->`
- If found and unchecked (`- [ ]`): change to `- [x]` and append ` *(completed: YYYY-MM-DD)*`
- If found and already checked (`- [x]`): leave unchanged (idempotent)
- If tag not found: emit warning — "⚠️ No plan item found for this hotspot operation. Run /reforge.plan to add it."
- If file write fails: emit warning — "⚠️ Could not update project plan." Continue without failing.
- Update the `**Last Updated**` metadata line to today's date

If `.reforge/memory/project-plan.md` does not exist, skip this step silently.
The project plan is optional — its absence MUST NOT affect command behavior.

### Step 1: Load Analysis Inventory

Read `$ANALYSIS_DIR/analysis.xml` to get:
- List of source files with `path`, `language`, `lines`, `components` attributes
- Module/directory structure of the codebase

**Determine module boundaries**:
- Use top-level directories under the source root as module boundaries
- If project context specifies module structure, use that instead
- Each module is a unit for hotspot scoring

### Step 2: Load Extraction Data

Read all available extraction files that contribute to scoring:

1. **`$EXTRACTIONS_DIR/dependencies.xml`** (if exists):
   - Extract dependency relationships for coupling scores
   - Map each dependency to its source and target modules

2. **`$EXTRACTIONS_DIR/issues.xml`** (if exists):
   - Extract bugs and issues with source file references
   - Count issues per module

3. **`$EXTRACTIONS_DIR/call-sites.xml`** (if exists):
   - Extract call relationships for complexity/coupling analysis
   - Map calls to modules

4. **`$EXTRACTIONS_DIR/business-rules.xml`** (if exists):
   - Extract business rules with source file references
   - Count business rules per module

5. **`$DERIVED_DIR/codebase-metrics.xml`** (if exists):
   - Use pre-computed metrics if available (from `/reforge.metrics`)
   - Avoids recomputation of complexity, coupling, cohesion

Track which data sources are available — missing sources reduce scoring accuracy.

### Step 3: Compute Complexity Scores

For each module:

1. **If `codebase-metrics.xml` is available**: Use pre-computed cyclomatic and cognitive complexity
2. **Otherwise**: Estimate from analysis.xml component counts and file complexity indicators

3. **Normalize to 0-100 scale**:
   - Find the maximum complexity across all modules
   - Score = (module_complexity / max_complexity) * 100
   - If all modules have equal complexity, all score 50

### Step 4: Compute Dependency Scores

For each module:

1. **Count total dependencies**: afferent (incoming) + efferent (outgoing)
2. **Normalize to 0-100 scale**:
   - Find the maximum total dependency count across all modules
   - Score = (module_dependencies / max_dependencies) * 100

If dependency data is not available:
- Use file count and import patterns from analysis.xml as proxy
- Set `confidence="low"` for affected scores

### Step 5: Compute Issue Density Scores

For each module:

1. **Count issues**: bugs + technical debt issues from `issues.xml`
2. **Compute density**: issues / lines_of_code * 1000 (issues per KLOC)
3. **Normalize to 0-100 scale**:
   - Find the maximum density across all modules
   - Score = (module_density / max_density) * 100

If issues data is not available:
- Set issue density score to 0 with `confidence="low"`

### Step 6: Count Business Rules Per Module

For each module:

1. **Count business rules**: rules from `business-rules.xml` referencing files in this module
2. **Record raw count** — not normalized (used as a weighting factor)

If business-rules data is not available:
- Set count to 0 with `confidence="low"`

### Step 7: Compute Composite Risk Scores

For each module:

1. **Apply scoring weights**:
   ```
   risk_score = (complexity_score * 0.30) +
                (dependency_score * 0.25) +
                (issue_density_score * 0.25) +
                (business_rule_score * 0.20)
   ```

   Where `business_rule_score` is normalized: `(module_br_count / max_br_count) * 100`

2. **Round** to nearest integer (0-100)

3. **Assign confidence**:
   - `high`: 3+ data sources available
   - `medium`: 2 data sources available
   - `low`: 1 or fewer data sources available

4. **Apply threshold**: Exclude modules with `risk_score < threshold` (default: 25)

5. **Rank**: Sort by `risk_score` descending, assign `rank` starting from 1

6. **Apply `--top` limit**: If specified, keep only the top N results

### Step 8: Generate Rationale

For each hotspot, generate a human-readable rationale explaining:
- Which factors contributed most to the risk score
- Specific metrics that stand out (e.g., "cyclomatic complexity of 18 is 3x the project average")
- Modernization implications (e.g., "high afferent coupling means changes will ripple to 12 dependents")

### Step 9: Assign Hotspot Categories

Classify each hotspot using categories based on its architectural role:

| Category | Description | Detection |
|----------|-------------|-----------|
| `SVC` | Service layer | Path contains `service/`, `svc/`, class names ending in `Service` |
| `CTL` | Controller layer | Path contains `controller/`, `handler/`, `api/` |
| `DAL` | Data access layer | Path contains `repository/`, `dao/`, `data/`, `model/` |
| `MDL` | Model layer | Path contains `model/`, `entity/`, `domain/` |
| `UTL` | Utility | Path contains `util/`, `helper/`, `common/` |
| `CFG` | Configuration | Path contains `config/`, `setup/`, `bootstrap/` |
| `INT` | Integration | Path contains `integration/`, `gateway/`, `client/` |

If no category can be determined, use the first 3 characters of the module name (uppercased).

### Step 10: Generate Hotspot Analysis File

Write the analysis to `$DERIVED_DIR/hotspot-analysis.xml` following the schema defined in `.reforge/schemas/hotspot-analysis.md`.

The file MUST include:
- Root element `<hotspot-analysis>` with all required common attributes
- `<metadata>` with hotspot count as `total-count`
- `<scoring-weights>` documenting the weight configuration
- `<hotspots>` with ranked hotspot items including all sub-scores and rationale

### Step 11: Display Results

Display a human-readable summary:

```
=== Reforge Hotspot Analysis ===
Project: [project-name]
Threshold: [N] | Hotspots found: [N]

--- Risk Heatmap ---
| Rank | Module             | Risk | Complexity | Dependency | Issues | BRs | Confidence |
|------|--------------------|------|------------|------------|--------|-----|------------|
| 1    | OrderService       | 82   | 90         | 75         | 85     | 15  | high       |
| 2    | CustomerRepository | 65   | 60         | 80         | 55     | 8   | high       |
| 3    | PaymentGateway     | 58   | 45         | 60         | 70     | 4   | medium     |

--- Top Hotspot Detail ---
#1 OrderService (risk: 82/100)
   High cyclomatic complexity (18) combined with high dependency fan-out (12)
   and dense issue concentration (7 issues in 1200 LOC).

--- Data Sources ---
Available: analysis, dependencies, issues, call-sites, business-rules
Missing: none

--- Next Steps ---
-> Review analysis: $DERIVED_DIR/hotspot-analysis.xml
-> Run /reforge.metrics for detailed module metrics
-> Focus modernization efforts on top-ranked hotspots
```

---

## Error Handling

### No Analysis

If `$ANALYSIS_DIR/analysis.xml` does not exist:

```
Error: No analysis found. Run /reforge.analyze first.
  Expected: $ANALYSIS_DIR/analysis.xml
```

### No Extraction Data

If no extraction files exist:

```
Warning: No extraction data available.
  Hotspot analysis requires at least one extraction for meaningful results.
  Computing basic scores from analysis.xml only (file size and component counts).
  For accurate scoring, run /reforge.extract with: dependencies, issues, call-sites, business-rules
```

Continue with available data — do not abort.

### Invalid Threshold

If `--threshold` value is outside 0-100 range:

```
Error: Threshold must be between 0 and 100. Got: [value]
```

### No Hotspots Found

If no modules meet the threshold:

```
=== Reforge Hotspot Analysis ===
Project: [project-name]
Threshold: [N]

No modules exceed the risk threshold of [N].
Consider lowering the threshold: /reforge.hotspot --threshold [lower-value]
```

---

## Examples

### Default Hotspot Analysis

```
User: /reforge.hotspot

Agent:
=== Reforge Hotspot Analysis ===
Project: legacy-ecommerce
Threshold: 25 | Hotspots found: 5

--- Risk Heatmap ---
| Rank | Module             | Risk | Complexity | Dependency | Issues | BRs | Confidence |
|------|--------------------|------|------------|------------|--------|-----|------------|
| 1    | OrderService       | 82   | 90         | 75         | 85     | 15  | high       |
| 2    | CustomerRepository | 65   | 60         | 80         | 55     | 8   | high       |
| 3    | PaymentGateway     | 58   | 45         | 60         | 70     | 4   | medium     |
| 4    | InventoryManager   | 42   | 50         | 35         | 40     | 6   | high       |
| 5    | ReportGenerator    | 30   | 35         | 20         | 30     | 3   | high       |

Output: reforge_output/legacy-ecommerce/derived/hotspot-analysis.xml

--- Next Steps ---
-> Run /reforge.metrics for detailed module metrics
-> Focus modernization efforts on top-ranked hotspots
```

### Top 3 with High Threshold

```
User: /reforge.hotspot --threshold 50 --top 3

Agent:
=== Reforge Hotspot Analysis ===
Project: legacy-ecommerce
Threshold: 50 | Top: 3 | Hotspots found: 3

--- Risk Heatmap ---
| Rank | Module             | Risk | Complexity | Dependency | Issues | BRs | Confidence |
|------|--------------------|------|------------|------------|--------|-----|------------|
| 1    | OrderService       | 82   | 90         | 75         | 85     | 15  | high       |
| 2    | CustomerRepository | 65   | 60         | 80         | 55     | 8   | high       |
| 3    | PaymentGateway     | 58   | 45         | 60         | 70     | 4   | medium     |

--- Top Hotspot Detail ---
#1 OrderService (risk: 82/100)
   High cyclomatic complexity (18) combined with high dependency fan-out (12)
   and dense issue concentration (7 issues in 1200 LOC) make this the
   highest-risk module for modernization.

#2 CustomerRepository (risk: 65/100)
   High afferent coupling (12 dependents) creates significant change ripple
   risk. Contains 8 embedded business rules that should be extracted to
   service layer.

#3 PaymentGateway (risk: 58/100)
   External integration point with deprecated API usage (5 issues). High
   efferent coupling to payment provider libraries increases migration risk.

Output: reforge_output/legacy-ecommerce/derived/hotspot-analysis.xml
```
