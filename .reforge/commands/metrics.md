# /reforge.metrics

> Compute quantitative codebase metrics — complexity, coupling, cohesion, and tech debt ratio per module

## Command Syntax

```
/reforge.metrics [--scope <module|project>] [--format html|xml] [--json]
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `--scope` | No | Scope of metrics computation: `module` (per-module breakdown, default) or `project` (aggregate only) |
| `--format` | No | Output format: `xml` (default) or `html` (generates HTML report alongside XML) |
| `--json` | No | Output metrics summary as JSON for tooling integration |

## Overview

This command computes quantitative metrics from extraction data:

- **Complexity** — Cyclomatic and cognitive complexity per module
- **Coupling** — Afferent (incoming) and efferent (outgoing) dependency counts, instability ratio
- **Cohesion** — Functional cohesion score based on internal method relationships
- **Tech Debt Ratio** — Ratio of remediation cost to development cost, derived from issue counts
- **Lines of Code** — LOC breakdown (code, comments, blanks) per module

The metrics command produces:
- **`codebase-metrics.xml`** — Structured metrics (schema: `.reforge/schemas/codebase-metrics.md`)

## Prerequisites

- Completed analysis (`$ANALYSIS_DIR/analysis.xml` must exist)
- At least one of: dependencies extraction, issues extraction, or call-sites extraction (recommended for meaningful results)

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
- Identify metrics-related items and display their status

**On command completion (success only):**
- Locate the plan item by searching for `<!-- reforge:metrics -->`
- If found and unchecked (`- [ ]`): change to `- [x]` and append ` *(completed: YYYY-MM-DD)*`
- If found and already checked (`- [x]`): leave unchanged (idempotent)
- If tag not found: emit warning — "⚠️ No plan item found for this metrics operation. Run /reforge.plan to add it."
- If file write fails: emit warning — "⚠️ Could not update project plan." Continue without failing.
- Update the `**Last Updated**` metadata line to today's date

If `.reforge/memory/project-plan.md` does not exist, skip this step silently.
The project plan is optional — its absence MUST NOT affect command behavior.

### Step 1: Load Analysis Inventory

Read `$ANALYSIS_DIR/analysis.xml` to get:
- List of source files with `path`, `language`, `lines`, `components` attributes
- Module/directory structure of the codebase
- Component locations (classes, methods, functions)

**Determine module boundaries**:
- Use top-level directories under the source root as module boundaries
- If project context specifies module structure, use that instead
- Each module is a unit for metrics computation

### Step 2: Load Extraction Data

Read available extraction files that contribute to metrics:

1. **`$EXTRACTIONS_DIR/dependencies.xml`** (if exists):
   - Extract `<dependency>` items with `source-module` and `target-module`
   - Used for coupling computation

2. **`$EXTRACTIONS_DIR/issues.xml`** (if exists):
   - Extract `<bug>` and `<issue>` items with source file references
   - Used for tech debt ratio computation

3. **`$EXTRACTIONS_DIR/call-sites.xml`** (if exists):
   - Extract `<call-site>` items with caller/callee relationships
   - Used for cohesion computation

4. **`$EXTRACTIONS_DIR/business-rules.xml`** (if exists):
   - Extract `<rule>` items with source file references
   - Used for complexity weighting

If none of these extraction files exist:
```
Warning: No extraction data available for metrics computation.
  Metrics will be computed from analysis.xml only (LOC and basic complexity).
  Run /reforge.extract dependencies, issues, or call-sites for richer metrics.
```

### Step 3: Compute Complexity Per Module

For each module:

1. **Cyclomatic complexity**: Count decision points from analysis components
   - `if`, `else if`, `case`, `catch`, `&&`, `||`, `?:` patterns
   - Sum across all files in the module
   - Normalize: total decision points + 1

2. **Cognitive complexity**: Weight by nesting depth
   - Each nesting level adds a multiplier
   - Recursive calls add extra weight

3. **Max nesting depth**: Deepest nesting level in the module

4. **Assign confidence**:
   - `high`: Source code was read and analyzed directly
   - `medium`: Estimated from analysis.xml metadata
   - `low`: Inferred from limited data

### Step 4: Compute Coupling Per Module

For each module (requires dependencies extraction):

1. **Afferent coupling (Ca)**: Count modules that depend on this module
   - From `dependencies.xml`: count `<dependency>` items where this module is the target

2. **Efferent coupling (Ce)**: Count modules this module depends on
   - From `dependencies.xml`: count `<dependency>` items where this module is the source

3. **Instability (I)**: `Ce / (Ca + Ce)`
   - Range: 0.0 (maximally stable) to 1.0 (maximally unstable)
   - If `Ca + Ce = 0`, instability = 0.0

If dependencies extraction is not available:
- Set coupling values to 0 with `confidence="low"`
- Note in output: "Coupling metrics estimated — run /reforge.extract dependencies for accurate values"

### Step 5: Compute Cohesion Per Module

For each module (requires call-sites extraction):

1. **Method connectivity**: Analyze internal call relationships
   - From `call-sites.xml`: count calls between methods within the same module
   - Compute: internal calls / total possible internal call pairs

2. **Cohesion score**: 0.0 (coincidental) to 1.0 (functional)

3. **Cohesion type classification**:
   - `functional` (0.8-1.0): Methods work together on a single task
   - `sequential` (0.6-0.8): Output of one method feeds into another
   - `communicational` (0.4-0.6): Methods operate on the same data
   - `procedural` (0.2-0.4): Methods follow a specific execution order
   - `temporal` (0.1-0.2): Methods are related by timing
   - `logical` (0.05-0.1): Methods are categorically similar
   - `coincidental` (0.0-0.05): No meaningful relationship

If call-sites extraction is not available:
- Estimate cohesion from file count and component count in the module
- Set `confidence="low"`

### Step 6: Compute Tech Debt Ratio Per Module

For each module (requires issues extraction):

1. **Issue count**: Count bugs + issues from `issues.xml` referencing files in this module

2. **Effort estimation**:
   - `low` effort issues: 4 hours
   - `medium` effort issues: 20 hours
   - `high` effort issues: 60 hours
   - Sum total remediation hours

3. **Development cost estimate**: LOC / 10 hours (approximate)

4. **Tech debt ratio**: remediation hours / development hours
   - Values > 1.0 indicate remediation cost exceeds original development cost

If issues extraction is not available:
- Set tech debt ratio to 0.0 with `confidence="low"`

### Step 7: Compute Lines of Code Per Module

For each module:

1. **Read each file** in the module (or use analysis.xml `lines` attribute)
2. **Classify lines**: code, comment, blank
3. **Sum** across all files in the module

### Step 8: Generate Codebase Metrics File

Write the metrics to `$DERIVED_DIR/codebase-metrics.xml` following the schema defined in `.reforge/schemas/codebase-metrics.md`.

The file MUST include:
- Root element `<codebase-metrics>` with all required common attributes
- `<metadata>` with module count as `total-count`
- `<project-summary>` with aggregate metrics
- `<module-metrics>` with per-module breakdown (unless `--scope project`)

### Step 9: Display Results

Display a human-readable summary:

```
=== Reforge Codebase Metrics ===
Project: [project-name]
Modules: [N]

--- Project Summary ---
Total LOC: [N]
Avg Complexity: [N]
Avg Coupling: [N]
Avg Cohesion: [N]
Avg Tech Debt Ratio: [N]

--- Module Rankings (by complexity) ---
| Rank | Module            | Complexity | Coupling | Cohesion | Debt Ratio |
|------|-------------------|------------|----------|----------|------------|
| 1    | OrderService      | 18         | 0.62     | 0.75     | 0.18       |
| 2    | PaymentGateway    | 12         | 0.67     | 0.65     | 0.14       |
| 3    | CustomerRepo      | 8          | 0.33     | 0.80     | 0.08       |

--- Next Steps ---
-> Review metrics: $DERIVED_DIR/codebase-metrics.xml
-> Run /reforge.hotspot for risk-based prioritization
-> Run /reforge.validate to check extraction integrity
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
  Computing basic metrics from analysis.xml only (LOC and estimated complexity).
  For comprehensive metrics, run /reforge.extract with: dependencies, issues, call-sites
```

Continue with available data — do not abort.

### Empty Modules

If a module contains no source files:

```
Warning: Module '[name]' has no source files. Skipping.
```

Continue processing remaining modules.

---

## Examples

### Full Metrics Computation

```
User: /reforge.metrics

Agent:
=== Reforge Codebase Metrics ===
Project: legacy-ecommerce
Modules: 8

--- Project Summary ---
Total LOC: 45,000
Avg Complexity: 8.5
Avg Coupling: 0.45
Avg Cohesion: 0.68
Avg Tech Debt Ratio: 0.12

--- Module Rankings (by complexity) ---
| Rank | Module            | Complexity | Coupling | Cohesion | Debt Ratio |
|------|-------------------|------------|----------|----------|------------|
| 1    | OrderService      | 18         | 0.62     | 0.75     | 0.18       |
| 2    | PaymentGateway    | 12         | 0.67     | 0.65     | 0.14       |
| 3    | CustomerRepo      | 8          | 0.33     | 0.80     | 0.08       |
| 4    | InventoryManager  | 7          | 0.50     | 0.72     | 0.10       |
| 5    | AuthService       | 6          | 0.40     | 0.85     | 0.05       |

Output: reforge_output/legacy-ecommerce/derived/codebase-metrics.xml

--- Next Steps ---
-> Run /reforge.hotspot for risk-based prioritization
-> Run /reforge.validate to check extraction integrity
```

### Project-Scope Only

```
User: /reforge.metrics --scope project

Agent:
=== Reforge Codebase Metrics ===
Project: legacy-ecommerce

--- Project Summary ---
Total LOC: 45,000
Total Modules: 8
Avg Complexity: 8.5
Avg Coupling: 0.45
Avg Cohesion: 0.68
Avg Tech Debt Ratio: 0.12

Output: reforge_output/legacy-ecommerce/derived/codebase-metrics.xml
```
