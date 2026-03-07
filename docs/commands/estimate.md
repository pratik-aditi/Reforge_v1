---
tags:
  - commands
  - modernization
---

# /reforge.estimate

Generate three-point effort estimates per module with complexity multipliers.

## Syntax

=== "Claude Code"

    ```
    /reforge.estimate [--scope module|project] [--method three-point|analogous] [--format html|xml] [--json]
    ```

=== "GitHub Copilot"

    ```
    @reforge.estimate [--scope module|project] [--method three-point|analogous] [--format html|xml] [--json]
    ```

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `--scope` | No | Granularity: `module` (default) for per-module estimates or `project` for aggregate |
| `--method` | No | Estimation method: `three-point` (default, PERT) or `analogous` for comparison-based |
| `--format` | No | Output format: `xml` (default) or `html` for a styled report |
| `--json` | No | Output estimates as JSON for tooling integration |

## What It Does

This command produces effort estimates for modernizing each module using the PERT three-point estimation technique:

- **Optimistic** -- best-case effort assuming no complications
- **Most likely** -- expected effort under normal conditions
- **Pessimistic** -- worst-case effort accounting for risks and unknowns

Estimates are adjusted by complexity multipliers derived from codebase metrics such as cyclomatic complexity, coupling density, and issue concentration. The `analogous` method uses comparison with similarly-sized modules when historical data is available.

Project-scope estimates aggregate module estimates and include a contingency buffer based on overall risk profile.

## Prerequisites

- Completed analysis (`/reforge.analyze`)
- Architecture, dependencies, and issues extractions recommended for accurate multipliers

## Output

Files are written to `reforge_output/<project>/generated/`:

| File | Description |
|------|-------------|
| `effort-estimate.xml` | Per-module and aggregate effort estimates with confidence ranges |

## Example

=== "Claude Code"

    ```
    /reforge.estimate
    /reforge.estimate --scope project
    /reforge.estimate --method analogous
    /reforge.estimate --format html
    /reforge.estimate --json
    ```

=== "GitHub Copilot"

    ```
    @reforge.estimate
    @reforge.estimate --scope project
    @reforge.estimate --method analogous
    @reforge.estimate --format html
    @reforge.estimate --json
    ```

## Related Commands

- [`/reforge.migrate`](migrate.md) -- migration playbook informed by effort estimates
- [`/reforge.hotspot`](hotspot.md) -- risk scores that influence complexity multipliers
- [`/reforge.metrics`](metrics.md) -- quantitative metrics used in estimation
