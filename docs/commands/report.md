---
tags:
  - commands
  - reporting
---

# /reforge.report

Generate progress and status reports for stakeholder communication.

## Syntax

=== "Claude Code"

    ```
    /reforge.report [--type milestone|status|executive] [--period YYYY-MM-DD:YYYY-MM-DD] [--format html|md]
    ```

=== "GitHub Copilot"

    ```
    @reforge.report [--type milestone|status|executive] [--period YYYY-MM-DD:YYYY-MM-DD] [--format html|md]
    ```

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `--type` | No | Report type (default: `status`) |
| `--period` | No | Date range for the report (default: project start to today) |
| `--format` | No | Output format: `html` or `md` (default: `md`) |

**Report types:**

| Type | Description |
|------|-------------|
| `milestone` | Progress against the project plan with phase completion percentages |
| `status` | Current state snapshot: what is done, in progress, and remaining |
| `executive` | Stakeholder summary with overall readiness score, key risks, and recommendations |

## What It Does

Generates a structured report by aggregating data from analysis, extractions, audits, and derived artifacts. Each report type serves a different audience:

- **Milestone** -- tracks completion against `/reforge.plan` phases, highlights blockers and schedule risk
- **Status** -- summarizes current extraction coverage, recent activity, and next steps
- **Executive** -- provides a high-level readiness assessment with risk indicators and decision points

When `--period` is specified, metrics and activity are scoped to that date range.

## Prerequisites

- Completed analysis (`/reforge.analyze`)

## Output

Files are written to `reforge_output/<project>/generated/reports/`:

| File | Description |
|------|-------------|
| `report-YYYY-MM-DD.html` or `.md` | Generated report in the requested format |

## Example

=== "Claude Code"

    ```
    /reforge.report
    /reforge.report --type executive --format html
    /reforge.report --type milestone --period 2026-01-01:2026-03-06
    ```

=== "GitHub Copilot"

    ```
    @reforge.report
    @reforge.report --type executive --format html
    @reforge.report --type milestone --period 2026-01-01:2026-03-06
    ```

## Related Commands

- [`/reforge.dashboard`](dashboard.md) -- interactive HTML dashboard
- [`/reforge.status`](status.md) -- quick text-based progress check
- [`/reforge.export`](export.md) -- export artifacts to external tools
