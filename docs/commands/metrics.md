---
tags:
  - commands
  - quality
---

# /reforge.metrics

Compute quantitative codebase metrics per module and project-wide.

## Syntax

=== "Claude Code"

    ```
    /reforge.metrics [--scope module|project] [--format html|xml] [--json]
    ```

=== "GitHub Copilot"

    ```
    @reforge.metrics [--scope module|project] [--format html|xml] [--json]
    ```

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `--scope` | No | Granularity of metrics: `module` (default) or `project` for aggregate view |
| `--format` | No | Output format: `xml` (default) or `html` for a styled report |
| `--json` | No | Output metrics as JSON for tooling integration |

## What It Does

This command analyzes the codebase and produces quantitative metrics including:

- **Complexity** -- cyclomatic and cognitive complexity scores per module
- **Coupling** -- afferent and efferent coupling between modules
- **Cohesion** -- functional cohesion assessment within modules
- **Tech debt ratio** -- estimated remediation effort relative to module size

Metrics are computed from the analysis inventory and enriched when optional extractions are available. The `module` scope produces per-module breakdowns; `project` scope produces aggregate summaries with distribution statistics.

## Prerequisites

- Completed analysis (`/reforge.analyze`)
- Dependencies, issues, and call-sites extractions recommended for richer metrics

## Output

Files are written to `reforge_output/<project>/derived/`:

| File | Description |
|------|-------------|
| `codebase-metrics.xml` | Quantitative metrics with per-module and aggregate scores |

## Example

=== "Claude Code"

    ```
    /reforge.metrics
    /reforge.metrics --scope project
    /reforge.metrics --format html
    /reforge.metrics --json
    ```

=== "GitHub Copilot"

    ```
    @reforge.metrics
    @reforge.metrics --scope project
    @reforge.metrics --format html
    @reforge.metrics --json
    ```

## Related Commands

- [`/reforge.hotspot`](hotspot.md) -- risk heatmap built on top of metrics
- [`/reforge.validate`](validate.md) -- verify extraction data feeding metrics
- [`/reforge.analyze`](analyze.md) -- produce the analysis inventory used by metrics
