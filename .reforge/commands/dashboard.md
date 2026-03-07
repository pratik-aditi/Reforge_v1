# /reforge.dashboard

> Generate an interactive HTML dashboard summarizing all extractions and quality metrics

## Command Syntax

```
/reforge.dashboard [--theme <light|dark>] [--sections <all|summary|extractions|quality|migration>]
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `--theme` | No | Visual theme: `light` (default) or `dark` |
| `--sections` | No | Sections to include: `all` (default), `summary`, `extractions`, `quality`, `migration` |

## Overview

This command generates a self-contained HTML dashboard that provides a visual overview of the entire Reforge analysis and extraction project. The dashboard consolidates data from all available extractions and derived artifacts into an interactive single-page view.

Key sections:
- **Project Overview**: Project name, analysis date, file inventory summary
- **Extraction Coverage**: Chart showing which extraction types have been completed and item counts
- **Confidence Distribution**: Breakdown of extraction confidence levels across all types
- **Hotspot Visualization**: Files with the highest extraction density (if hotspot data available)
- **Migration Readiness**: Overall readiness assessment (if tech-recommendation data available)
- **Quality Metrics**: Audit findings and coverage statistics (if audit data available)

## Prerequisites

- Analysis must be completed (`$ANALYSIS_DIR/analysis.xml` must exist)
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

Use `$PROJECT_OUTPUT_DIR` for all output paths in subsequent steps.

Assign subdirectory variables:
```
$ANALYSIS_DIR = $PROJECT_OUTPUT_DIR/analysis
$EXTRACTIONS_DIR = $PROJECT_OUTPUT_DIR/extractions
$GENERATED_DIR = $PROJECT_OUTPUT_DIR/generated
$DERIVED_DIR = $PROJECT_OUTPUT_DIR/derived
$AUDIT_DIR = $PROJECT_OUTPUT_DIR/audit
```

Create the output directory if it does not exist:
```
mkdir -p $GENERATED_DIR
```

### Step 0.5: Load Project Context

If `.reforge/memory/project-context.md` exists, read it now. Use its contents as
supplemental guidance throughout this command's execution:
- **Technology Stack**: Informs dashboard technology labels
- **Domain Knowledge**: Provides business context for section headings
- **Analysis Guidelines**: Directs focus and exclusions beyond config.json
- **Custom Rules**: Additional rules to follow alongside the constitution

### Step 0.7: Check/Update Project Plan

If `.reforge/memory/project-plan.md` exists, read it now.

**On command start:**
- Parse the plan file to count total items and completed items
- Display: "📋 Project Plan: X/Y items complete (Z%)"
- Search for `<!-- reforge:dashboard -->` tag and display its status

**On command completion (success only):**
- Locate the plan item by searching for `<!-- reforge:dashboard -->`
- If found and unchecked (`- [ ]`): change to `- [x]` and append ` *(completed: YYYY-MM-DD)*`
- If found and already checked (`- [x]`): leave unchanged (idempotent)
- If tag not found: emit warning — "⚠️ No plan item found for dashboard. Run /reforge.plan to add it."
- If file write fails: emit warning — "⚠️ Could not update project plan." Continue without failing.
- Update the `**Last Updated**` metadata line to today's date

If `.reforge/memory/project-plan.md` does not exist, skip this step silently.
The project plan is optional — its absence MUST NOT affect command behavior.

### Step 1: Inventory Available Artifacts

Scan the project output directory for all available data sources:

**Extraction files** (`$EXTRACTIONS_DIR/`):
- `business-rules.xml`, `database.xml`, `ui-flows.xml`, `workflows.xml`
- `call-sites.xml`, `dependencies.xml`, `functional-requirements.xml`
- `non-functional.xml`, `architecture.xml`, `issues.xml`
- `acronym-glossary.xml`

**Derived artifacts** (`$DERIVED_DIR/`):
- `cross-mappings/`, `features-requirements/`, `registries/`

**Audit data** (`$AUDIT_DIR/`):
- `audit-report.xml`, `correction-plan.xml`
- `consistency-audit-report.xml`

**Generated artifacts** (`$GENERATED_DIR/`):
- `tech-recommendation.xml`
- `reports/`

For each artifact found, record:
- File path and existence status
- Last modified timestamp
- Key metrics (item counts from `<metadata>/<total-count>`)

### Step 2: Compute Summary Statistics

For each available extraction file, parse and collect:
- Total item count from `<metadata>/<total-count>`
- Confidence distribution from `<metadata>/<confidence-distribution>`
- Extraction timestamp

Compute aggregate statistics:
- Total extracted items across all types
- Overall confidence distribution (sum of all types)
- Extraction coverage: (completed extraction types) / (total possible extraction types)
- Most recent extraction timestamp

### Step 3: Compute Section Data

**Project Overview Section**:
- Project name from config
- Analysis date from `analysis.xml` `generated` attribute
- Total files analyzed (count of `<file>` elements in analysis.xml)
- Total lines of code (sum of `lines` attributes)
- Languages detected (unique `language` attributes)

**Extraction Coverage Section**:
- For each extraction type: name, item count (or "Not extracted"), completion status
- Visual bar chart data (item counts as proportional widths)

**Confidence Distribution Section**:
- Aggregate high/medium/low counts across all extractions
- Per-type confidence breakdown

**Hotspot Visualization Section** (if data available):
- Files referenced by the most extraction items
- Cross-reference extraction source files to find highest-density files
- Top 10 files by extraction reference count

**Migration Readiness Section** (if `tech-recommendation.xml` exists):
- Recommendation count by priority
- Average recommendation score
- Categories covered

**Quality Metrics Section** (if audit data exists):
- Coverage percentage from audit report
- Gap count from correction plan
- Consistency findings (if consistency audit exists)

### Step 4: Generate Dashboard HTML

Generate `$GENERATED_DIR/dashboard.html` as a self-contained HTML file.

**CRITICAL**: The HTML MUST be completely self-contained:
- All CSS inline within `<style>` tags — no external stylesheets
- All JavaScript inline within `<script>` tags — no external scripts
- No CDN references or external dependencies
- Uses the Stephen Few design system from `.reforge/templates/html-report.md`

**Theme support**:
- `--theme light` (default): Use standard Stephen Few color palette
- `--theme dark`: Invert key CSS variables (`--ink: #e0e0e0`, `--bg: #1a1a1a`, etc.)

**Section filtering**:
- If `--sections` is specified and not `all`, only include the requested sections
- Always include the header and footer regardless of section filter

**Dashboard layout**:
- Use CSS Grid for responsive card-based layout
- Summary cards at top with key metrics (total files, total items, coverage %, confidence %)
- Data tables for extraction details
- Horizontal bar charts using CSS `width` percentages (no JavaScript charting libraries)
- Conditional sections: only render sections that have data

**Interactive features** (inline JavaScript only):
- Collapsible sections with toggle buttons
- Sort-by-column on data tables
- Filter/search within tables

### Step 5: Write Output

Write the dashboard to `$GENERATED_DIR/dashboard.html`.

Display summary:
```
Dashboard generated: $GENERATED_DIR/dashboard.html
  Sections: [list of included sections]
  Extraction types: X/Y available
  Total items: N across all extractions
```

---

## Error Handling

| Condition | Action |
|-----------|--------|
| Analysis not completed | Error: "Analysis required. Run `/reforge.analyze` first." |
| No extractions available | Warning: "No extractions found. Dashboard will show analysis summary only." Generate with analysis data only. |
| Invalid `--theme` value | Error: "Invalid theme. Valid options: light, dark" |
| Invalid `--sections` value | Error: "Invalid section. Valid options: all, summary, extractions, quality, migration" |
| Extraction file parse error | Warning: "Could not parse [file]. Skipping." Continue with available data. |

---

## Examples

### Default Dashboard

```
/reforge.dashboard
```

Produces `generated/dashboard.html` with all sections using the light theme.

### Dark Theme with Quality Focus

```
/reforge.dashboard --theme dark --sections quality
```

Produces a dark-themed dashboard showing only quality metrics.

### Summary Only

```
/reforge.dashboard --sections summary
```

Produces a minimal dashboard with project overview and extraction coverage cards.
