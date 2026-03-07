# /reforge.estimate

> Generate three-point effort estimates per module with complexity multipliers

## Command Syntax

```
/reforge.estimate [--scope <module|project>] [--method <three-point|analogous>] [--format html|xml] [--json]
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `--scope` | No | Estimation scope: `module` (per-module detail, default), `project` (aggregate only) |
| `--method` | No | Estimation method: `three-point` (PERT, default), `analogous` (comparison-based) |
| `--format` | No | Output format: `xml` (default), `html` (standalone report) |
| `--json` | No | Output summary as JSON to stdout (for scripting) |

## Overview

This command generates effort estimates for migrating or modernizing each module in the analyzed codebase. It combines data from multiple extraction sources to produce three-point estimates (optimistic, most-likely, pessimistic) with complexity multipliers derived from dependency graphs, issue density, and architectural coupling.

**Estimation methodology**:
- **Three-point (PERT)**: Expected = (O + 4M + P) / 6, where O=optimistic, M=most-likely, P=pessimistic
- **Analogous**: Comparison with similar modules already estimated (requires at least one baseline)

## Prerequisites

- Analysis must be completed (`/reforge.analyze`)
- Architecture extraction recommended (`/reforge.extract architecture`)
- Dependencies extraction recommended (`/reforge.extract dependencies`)
- Issues extraction recommended (`/reforge.extract issues`)

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
$GENERATED_DIR = $PROJECT_OUTPUT_DIR/generated
```

### Step 0.5: Load Project Context

If `.reforge/memory/project-context.md` exists, read it now. Use its contents as
supplemental guidance throughout this command's execution:
- **Technology Stack**: Informs complexity assessment and platform-specific multipliers
- **Domain Knowledge**: Provides business context for effort estimation
- **Analysis Guidelines**: Directs focus and exclusions beyond config.json
- **Custom Rules**: Additional rules to follow alongside the constitution

### Step 0.7: Check/Update Project Plan

If `.reforge/memory/project-plan.md` exists, read it now.

**On command start:**
- Parse the plan file to count total items and completed items
- Display: "📋 Project Plan: X/Y items complete (Z%)"
- Search for `<!-- reforge:estimate -->` and display its status

**On command completion (success only):**
- Locate the plan item by searching for `<!-- reforge:estimate -->`
- If found and unchecked (`- [ ]`): change to `- [x]` and append ` *(completed: YYYY-MM-DD)*`
- If found and already checked (`- [x]`): leave unchanged (idempotent)
- If tag not found: emit warning -- "No plan item found for estimate. Run /reforge.plan to add it."
- If file write fails: emit warning -- "Could not update project plan." Continue without failing.
- Update the `**Last Updated**` metadata line to today's date

If `.reforge/memory/project-plan.md` does not exist, skip this step silently.
The project plan is optional -- its absence MUST NOT affect command behavior.

### Step 1: Load Input Data

Read available extraction files to build the estimation context:

**Required:**
- `$ANALYSIS_DIR/analysis.xml` -- Module inventory and file list

**Recommended (use if available):**
- `$EXTRACTIONS_DIR/architecture.xml` -- Module boundaries, component types, integration points
- `$EXTRACTIONS_DIR/dependencies.xml` -- Dependency graph, coupling metrics
- `$EXTRACTIONS_DIR/issues.xml` -- Bug count, technical debt density per module

If recommended extractions are missing, warn the user and proceed with reduced accuracy:

```
Warning: Missing recommended extractions for accurate estimation:
  - architecture.xml (not found) -- module boundaries will be inferred from analysis
  - dependencies.xml (not found) -- coupling assessment will be limited
  - issues.xml (not found) -- risk factors will be conservative defaults

Consider running: /reforge.extract architecture dependencies issues
Proceeding with available data...
```

### Step 2: Inventory Modules

From the analysis and architecture data, build a module inventory:

1. **Identify modules**: Use architecture extraction if available (preferred), otherwise infer from analysis.xml directory/package structure
2. **For each module, gather**:
   - File count and total lines of code
   - Language(s) used
   - Component types (services, repositories, controllers, etc.)
   - Public API surface area (if architecture extraction available)

### Step 3: Assess Complexity Per Module

For each module, compute complexity factors:

1. **Dependency complexity**:
   - Count internal dependencies (from dependencies.xml or inferred)
   - Count external/third-party dependencies
   - Assess coupling depth (transitive dependency chains)

2. **Issue density**:
   - Count bugs and issues per module (from issues.xml)
   - Weight by severity (critical=4, high=3, medium=2, low=1)
   - Normalize by lines of code

3. **Structural complexity**:
   - File count and code volume
   - Number of integration points
   - Presence of anti-patterns or technical debt indicators

4. **Compute complexity multiplier**:
   - Base: `1.0` (simple, well-isolated module)
   - Add `+0.1` per internal dependency above 2
   - Add `+0.2` per external dependency
   - Add `+0.1` per high/critical issue
   - Add `+0.2` for legacy framework usage
   - Cap at `2.5` maximum multiplier
   - Document rationale for each multiplier

### Step 4: Compute Three-Point Estimates

For each module, estimate effort:

1. **Optimistic (O)**: Best case -- clean migration with no surprises
   - Base on lines of code and component type
   - Assume good test coverage and clear interfaces

2. **Most-Likely (M)**: Expected case -- typical complications
   - Apply typical rework factor (20-30%)
   - Account for testing and integration time

3. **Pessimistic (P)**: Worst case -- significant complications
   - Account for hidden dependencies, undocumented behavior
   - Include time for investigation and workarounds

4. **Expected (E)**: PERT weighted average
   - `E = (O + 4*M + P) / 6`

5. **Identify risk factors**: Specific risks that could push toward pessimistic estimate

### Step 5: Generate Effort Estimate

Write the effort estimate to `$GENERATED_DIR/effort-estimate.xml` following the
[effort-estimate schema](../schemas/effort-estimate.md).

**Schema compliance**:
- Root element: `<effort-estimate>` with common root attributes
- Include `<metadata>` as first child with total count and confidence distribution
- Each `<estimate>` item has `id`, `module`, and `confidence` attributes
- All effort values use consistent `unit` attribute
- `<expected>` value must equal `(O + 4*M + P) / 6` (verified computation)
- `<summary>` totals must be computed by summing individual estimates

**Validation rules**:
- `optimistic <= most-likely <= pessimistic` for every estimate
- `expected` must match PERT formula result (within rounding tolerance)
- `complexity-multiplier` value must be between `0.5` and `2.5`
- All `unit` attributes within an estimate must be consistent
- `<summary>/<total-effort>` must equal sum of all individual `<expected>` values

### Step 6: Report Results

```
Effort Estimation Complete!

Output: $GENERATED_DIR/effort-estimate.xml

Estimation Summary:
- Modules estimated: 12
- Methodology: Three-point (PERT) with complexity multipliers
- Effort unit: person-days

Total Effort:
- Optimistic:  85 person-days
- Most Likely: 145 person-days
- Expected:    152 person-days (PERT weighted)
- Pessimistic: 240 person-days

By Confidence:
- High:   120 person-days (8 modules)
- Medium:  27 person-days (3 modules)
- Low:      5 person-days (1 module)

Top Risk Factors:
1. Payment gateway API migration (OrderService) -- severity: high
2. No test coverage (ReportingModule) -- severity: high
3. Legacy stored procedures (CustomerRepository) -- severity: medium

Run /reforge.migrate to generate a phased migration playbook.
```

---

## Error Handling

### Missing Analysis

If analysis.xml does not exist (caught by prerequisites script):

```
Error: Analysis not found. Run /reforge.analyze first.
  Expected: $ANALYSIS_DIR/analysis.xml

The estimate command requires a completed analysis to inventory modules.
Run /reforge.analyze to inventory your codebase first.
```

### Missing Extractions

If no extraction files are found, warn but proceed with limited data:

```
Warning: No extraction outputs found.
  Estimates will be based on analysis.xml only (reduced accuracy).
  Run /reforge.extract architecture dependencies issues for better estimates.

Proceeding with analysis-only estimation...
```

### Empty Analysis

If analysis.xml exists but contains no file entries:

```
Warning: Analysis contains no file entries.
  No modules to estimate.

  This may indicate:
  - All files matched exclusion patterns
  - Analysis was interrupted before processing files

  Run /reforge.analyze to re-inventory the codebase.
```

### Invalid Estimate Values

If computed values violate constraints (e.g., optimistic > most-likely):

```
Warning: Estimate constraint violation for [module-name]:
  optimistic (15) > most-likely (12)
  Adjusting most-likely to match optimistic value.
```

---

## Examples

### Basic Usage

```
/reforge.estimate
```

Generates per-module three-point estimates using all available extraction data.

### Project-Level Summary Only

```
/reforge.estimate --scope project
```

Generates aggregate estimates without per-module breakdown.

### JSON Output for Scripting

```
/reforge.estimate --json
```

Outputs summary as JSON to stdout in addition to the XML file:

```json
{
  "total_modules": 12,
  "total_effort_expected": 152,
  "unit": "person-days",
  "methodology": "three-point-pert",
  "by_confidence": {
    "high": 120,
    "medium": 27,
    "low": 5
  }
}
```
