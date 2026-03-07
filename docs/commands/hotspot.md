---
tags:
  - commands
  - quality
---

# /reforge.hotspot

Generate a risk heatmap with composite scores across the codebase.

## Syntax

=== "Claude Code"

    ```
    /reforge.hotspot [--threshold 0-100] [--top n] [--format html|xml] [--json]
    ```

=== "GitHub Copilot"

    ```
    @reforge.hotspot [--threshold 0-100] [--top n] [--format html|xml] [--json]
    ```

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `--threshold` | No | Minimum risk score (0--100) to include in results (default: 0) |
| `--top` | No | Limit output to the top *n* highest-risk modules |
| `--format` | No | Output format: `xml` (default) or `html` for a styled heatmap |
| `--json` | No | Output hotspot data as JSON for tooling integration |

## What It Does

This command produces a risk heatmap by computing a composite score for each module from four dimensions:

- **Complexity** -- cyclomatic and cognitive complexity density
- **Dependency density** -- number of inbound and outbound dependencies
- **Issue density** -- concentration of known issues and defects
- **Business rule concentration** -- density of business logic that increases change risk

Each module receives a normalized 0--100 risk score. Higher scores indicate modules that are harder to maintain, more likely to introduce defects, and should be prioritized for modernization.

Use `--threshold` to filter out low-risk modules or `--top` to focus on the riskiest areas.

## Prerequisites

- Completed analysis (`/reforge.analyze`)
- Dependencies, issues, call-sites, and business-rules extractions recommended for accurate scoring

## Output

Files are written to `reforge_output/<project>/derived/`:

| File | Description |
|------|-------------|
| `hotspot-analysis.xml` | Risk scores and contributing factors per module |

## Example

=== "Claude Code"

    ```
    /reforge.hotspot
    /reforge.hotspot --threshold 60
    /reforge.hotspot --top 10
    /reforge.hotspot --format html
    /reforge.hotspot --json
    ```

=== "GitHub Copilot"

    ```
    @reforge.hotspot
    @reforge.hotspot --threshold 60
    @reforge.hotspot --top 10
    @reforge.hotspot --format html
    @reforge.hotspot --json
    ```

## Related Commands

- [`/reforge.metrics`](metrics.md) -- quantitative metrics feeding the hotspot scores
- [`/reforge.estimate`](estimate.md) -- effort estimates informed by hotspot risk
- [`/reforge.migrate`](migrate.md) -- migration planning prioritized by risk
