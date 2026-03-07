---
tags:
  - commands
  - reporting
---

# /reforge.dashboard

Interactive HTML dashboard summarizing all extractions and quality metrics.

## Syntax

=== "Claude Code"

    ```
    /reforge.dashboard [--theme light|dark] [--sections all|summary|extractions|quality|migration]
    ```

=== "GitHub Copilot"

    ```
    @reforge.dashboard [--theme light|dark] [--sections all|summary|extractions|quality|migration]
    ```

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `--theme` | No | Color theme (default: `light`) |
| `--sections` | No | Sections to include (default: `all`). Comma-separate multiple values. |

## What It Does

Generates a self-contained HTML dashboard with inline CSS and JavaScript -- no external dependencies. The dashboard provides a visual summary of the entire Reforge workflow in one page.

**Dashboard sections:**

- **Project Overview** -- project name, tech stack, analysis timestamp, overall progress
- **Extraction Coverage** -- per-type completion status with file coverage percentages
- **Confidence Distribution** -- bar charts showing confidence levels across extractions
- **Hotspot Visualization** -- risk heatmap highlighting high-complexity areas
- **Migration Readiness** -- readiness scoring and phase progress from migration playbook
- **Quality Metrics** -- complexity, coupling, cohesion, and tech debt indicators

The layout uses CSS Grid with summary cards, collapsible sections, and sortable tables. All data is pulled from existing extraction and derived artifacts.

## Prerequisites

- Completed analysis (`/reforge.analyze`)
- At least one extraction type recommended for meaningful content

## Output

Files are written to `reforge_output/<project>/generated/`:

| File | Description |
|------|-------------|
| `dashboard.html` | Self-contained interactive HTML dashboard |

## Example

=== "Claude Code"

    ```
    /reforge.dashboard
    /reforge.dashboard --theme dark
    /reforge.dashboard --sections summary,extractions,quality
    ```

=== "GitHub Copilot"

    ```
    @reforge.dashboard
    @reforge.dashboard --theme dark
    @reforge.dashboard --sections summary,extractions,quality
    ```

## Related Commands

- [`/reforge.status`](status.md) -- text-based progress overview
- [`/reforge.report`](report.md) -- generate milestone and status reports
- [`/reforge.metrics`](metrics.md) -- quantitative codebase metrics
