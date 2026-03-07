---
tags:
  - commands
  - modernization
---

# /reforge.recommend

Technology stack recommendations based on architecture analysis and project requirements.

## Syntax

=== "Claude Code"

    ```
    /reforge.recommend [--focus backend|frontend|data|infra] [--constraints text] [--format html|xml] [--json]
    ```

=== "GitHub Copilot"

    ```
    @reforge.recommend [--focus backend|frontend|data|infra] [--constraints text] [--format html|xml] [--json]
    ```

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `--focus` | No | Limit recommendations to a specific technology layer |
| `--constraints` | No | Free-text constraints (e.g., "must support on-prem", "team knows Java") |
| `--format` | No | Output format: `html` or `xml` (default: `xml`) |
| `--json` | No | Output results as JSON for tooling integration |

## What It Does

Generates scored technology stack recommendations by analyzing the current architecture, non-functional requirements, and known issues. Each recommendation includes:

- **Current technology assessment** -- what is in use today and its strengths/weaknesses
- **Proposed replacement** -- candidate technology with scored rationale across fitness criteria
- **Migration effort and risk** -- estimated complexity, team skill gap, and transition risk

Recommendations are grouped by technology layer (backend, frontend, data, infrastructure) and ranked by composite fitness score. When `--constraints` is provided, scoring is adjusted to reflect organizational or technical limitations.

## Prerequisites

- Architecture extraction required (`/reforge.extract architecture`)
- Non-functional requirements and issues extractions recommended for deeper analysis

## Output

Files are written to `reforge_output/<project>/generated/`:

| File | Description |
|------|-------------|
| `tech-recommendation.xml` | Scored recommendations with rationale and migration assessment |

## Example

=== "Claude Code"

    ```
    /reforge.recommend
    /reforge.recommend --focus backend
    /reforge.recommend --constraints "team knows Python, must run on AWS" --format html
    ```

=== "GitHub Copilot"

    ```
    @reforge.recommend
    @reforge.recommend --focus backend
    @reforge.recommend --constraints "team knows Python, must run on AWS" --format html
    ```

## Related Commands

- [`/reforge.migrate`](migrate.md) -- generate a phased migration playbook from recommendations
- [`/reforge.estimate`](estimate.md) -- estimate effort for recommended changes
- [`/reforge.analyze`](analyze.md) -- inventory the codebase that feeds recommendations
