# /reforge.report

> Generate progress and status reports for the Reforge analysis project

## Command Syntax

```
/reforge.report [--type <milestone|status|executive>] [--period <date-range>] [--format html|md]
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `--type` | No | Report type: `milestone` (progress against plan), `status` (current state snapshot), `executive` (high-level stakeholder summary). Default: `status` |
| `--period` | No | Date range for the report: `YYYY-MM-DD:YYYY-MM-DD` (default: project start to today) |
| `--format` | No | Output format: `html` (default, self-contained) or `md` (markdown) |

## Overview

This command generates reports that summarize the current state and progress of the Reforge analysis project. Three report types are available:

- **milestone**: Tracks progress against the project plan, showing completed and remaining items with timeline
- **status**: Current state snapshot with extraction statistics, audit findings, and quality metrics
- **executive**: High-level summary for stakeholders with key findings, risks, and readiness assessment

## Prerequisites

- Analysis must be completed (`$ANALYSIS_DIR/analysis.xml` must exist)

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
$AUDIT_DIR = $PROJECT_OUTPUT_DIR/audit
$DERIVED_DIR = $PROJECT_OUTPUT_DIR/derived
$REPORTS_DIR = $GENERATED_DIR/reports
```

Create the output directory if it does not exist:
```
mkdir -p $REPORTS_DIR
```

### Step 0.5: Load Project Context

If `.reforge/memory/project-context.md` exists, read it now. Use its contents as
supplemental guidance throughout this command's execution:
- **Technology Stack**: Informs technology-related report sections
- **Domain Knowledge**: Provides business context for executive summaries
- **Analysis Guidelines**: Directs focus and exclusions beyond config.json
- **Custom Rules**: Additional rules to follow alongside the constitution

### Step 0.7: Check/Update Project Plan

If `.reforge/memory/project-plan.md` exists, read it now.

**On command start:**
- Parse the plan file to count total items and completed items
- Display: "📋 Project Plan: X/Y items complete (Z%)"
- Search for `<!-- reforge:report -->` tag and display its status

**On command completion (success only):**
- Locate the plan item by searching for `<!-- reforge:report -->`
- If found and unchecked (`- [ ]`): change to `- [x]` and append ` *(completed: YYYY-MM-DD)*`
- If found and already checked (`- [x]`): leave unchanged (idempotent)
- If tag not found: emit warning — "⚠️ No plan item found for report. Run /reforge.plan to add it."
- If file write fails: emit warning — "⚠️ Could not update project plan." Continue without failing.
- Update the `**Last Updated**` metadata line to today's date

If `.reforge/memory/project-plan.md` does not exist, skip this step silently.
The project plan is optional — its absence MUST NOT affect command behavior.

### Step 1: Gather Project Data

Collect data from all available sources:

**Analysis data** (`$ANALYSIS_DIR/analysis.xml`):
- Total files analyzed, lines of code, languages
- Analysis timestamp

**Extraction metadata** (for each file in `$EXTRACTIONS_DIR/`):
- Extraction type, item count, confidence distribution
- Extraction timestamp

**Audit data** (if available in `$AUDIT_DIR/`):
- Coverage percentages from `audit-report.xml`
- Gap counts from `correction-plan.xml`
- Consistency findings from `consistency-audit-report.xml`

**Project plan** (if available in `.reforge/memory/project-plan.md`):
- Total plan items and completion count
- Per-item completion dates
- Remaining items

**Derived artifacts** (if available in `$DERIVED_DIR/`):
- Cross-mapping availability
- Feature-requirement mapping status
- Registry generation status

### Step 2: Apply Period Filter

If `--period` is specified:
- Parse the date range `YYYY-MM-DD:YYYY-MM-DD`
- Filter extraction and audit timestamps to items within the range
- For milestone reports, show only plan items completed within the period

If not specified:
- Use the analysis timestamp as the start date
- Use today's date as the end date

### Step 3: Generate Report Content

Route to the appropriate report type:

#### Milestone Report (`--type milestone`)

Sections:
1. **Project Progress Summary**: X/Y plan items complete (Z%)
2. **Completed Items**: Table of completed plan items with completion dates
3. **Remaining Items**: Table of uncompleted plan items
4. **Timeline**: Visual timeline showing completion progression
5. **Blockers and Risks**: Items marked as blocked or overdue

Data sources: Project plan (primary), extraction timestamps (secondary)

#### Status Report (`--type status`)

Sections:
1. **Project Overview**: Name, analysis date, codebase size
2. **Extraction Status**: Table of all extraction types with status (completed/pending), item counts, confidence
3. **Quality Summary**: Audit coverage %, gap count, consistency score (if available)
4. **Recent Activity**: Extractions or audits completed within the last 7 days
5. **Next Steps**: Recommended actions based on current state (uncompleted extractions, unresolved audit gaps)

Data sources: All available artifacts

#### Executive Report (`--type executive`)

Sections:
1. **Executive Summary**: 2-3 paragraph overview of project state and key findings
2. **Key Metrics**: High-level numbers in card format (files analyzed, rules extracted, issues found, coverage %)
3. **Risk Assessment**: High-severity issues and technical debt summary
4. **Migration Readiness**: Overall readiness score based on extraction completeness and audit results
5. **Recommendations**: Top 3-5 prioritized next steps

Readiness score calculation:
- Analysis complete: 10 points
- Each core extraction type (business-rules, database, ui, workflows): 10 points each (40 total)
- Extended extractions (call-sites, dependencies, functional-requirements, non-functional, architecture, issues): 5 points each (30 total)
- Audit completed: 10 points
- Audit coverage >80%: 10 points

Score interpretation:
- 90-100: Ready for modernization planning
- 70-89: Most analysis complete, minor gaps remain
- 50-69: Significant analysis remaining
- <50: Early stage, major work needed

Data sources: All available artifacts, emphasis on high-level metrics

### Step 4: Generate Output

**HTML format** (default):

Generate `$REPORTS_DIR/report-YYYY-MM-DD.html` as a self-contained HTML file.

**CRITICAL**: The HTML MUST be completely self-contained:
- All CSS inline within `<style>` tags — no external stylesheets
- All JavaScript inline within `<script>` tags — no external scripts
- No CDN references or external dependencies
- Uses the Stephen Few design system from `.reforge/templates/html-report.md`

Include a print-friendly stylesheet via `@media print` rules.

**Markdown format**:

Generate `$REPORTS_DIR/report-YYYY-MM-DD.md` as structured markdown.

### Step 5: Write Output

Write the report to the target path.

Display summary:
```
Report generated: $REPORTS_DIR/report-YYYY-MM-DD.[html|md]
  Type: [milestone|status|executive]
  Period: [start-date] to [end-date]
  Data sources: [list of available artifacts used]
```

---

## Error Handling

| Condition | Action |
|-----------|--------|
| Analysis not completed | Error: "Analysis required. Run `/reforge.analyze` first." |
| Invalid `--type` value | Error: "Invalid report type. Valid options: milestone, status, executive" |
| Invalid `--period` format | Error: "Invalid period format. Use YYYY-MM-DD:YYYY-MM-DD" |
| Invalid `--format` value | Error: "Invalid format. Valid options: html, md" |
| Project plan missing (milestone report) | Warning: "Project plan not found. Milestone report will show extraction timeline only." |
| No extractions available | Warning: "No extractions found. Report will show analysis summary only." |

---

## Examples

### Default Status Report

```
/reforge.report
```

Produces `generated/reports/report-2024-01-15.html` with a status snapshot.

### Executive Summary

```
/reforge.report --type executive
```

Produces `generated/reports/report-2024-01-15.html` with high-level stakeholder summary.

### Milestone Report for Date Range

```
/reforge.report --type milestone --period 2024-01-01:2024-01-15
```

Produces `generated/reports/report-2024-01-15.html` showing progress within the specified period.

### Markdown Status Report

```
/reforge.report --type status --format md
```

Produces `generated/reports/report-2024-01-15.md` as structured markdown.
