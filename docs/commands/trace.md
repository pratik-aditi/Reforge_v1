---
tags:
  - commands
  - analysis
---

# /reforge.trace

End-to-end traceability matrix linking requirements, rules, code, UI, and stories.

## Syntax

=== "Claude Code"

    ```
    /reforge.trace [--from id] [--depth n] [--format html|xml] [--json]
    ```

=== "GitHub Copilot"

    ```
    @reforge.trace [--from id] [--depth n] [--format html|xml] [--json]
    ```

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `--from` | No | Start tracing from a specific item ID |
| `--depth` | No | Maximum traversal depth (default: unlimited) |
| `--format` | No | Output format: `html` or `xml` (default: `xml`) |
| `--json` | No | Output results as JSON for tooling integration |

## What It Does

Builds a full traceability matrix across all extraction artifacts, mapping the chain:

**Requirement → Business Rule → Source Code → UI Flow → User Story**

The matrix identifies:

- **Connected chains** -- complete traces from requirement through to deliverable
- **Orphaned items** -- extracted artifacts with no upstream or downstream connections
- **Partial traces** -- items connected in one direction but missing links elsewhere
- **Coverage density** -- how thoroughly each extraction type participates in traces

When `--from` is specified, the matrix is scoped to traces passing through that item. The `--depth` flag limits how many hops from the starting item are followed.

## Prerequisites

- Completed analysis (`/reforge.analyze`)
- At least two extraction types completed (e.g., business rules and UI flows)

## Output

Files are written to `reforge_output/<project>/derived/`:

| File | Description |
|------|-------------|
| `traceability-matrix.xml` | Full traceability chains with orphan and coverage analysis |

## Example

=== "Claude Code"

    ```
    /reforge.trace
    /reforge.trace --from BR-042
    /reforge.trace --depth 3 --format html
    ```

=== "GitHub Copilot"

    ```
    @reforge.trace
    @reforge.trace --from BR-042
    @reforge.trace --depth 3 --format html
    ```

## Related Commands

- [`/reforge.extract`](extract.md) -- produce the artifacts that feed the matrix
- [`/reforge.compare`](compare.md) -- diff extraction runs for regression detection
- [`/reforge.audit`](audit.md) -- audit extraction coverage gaps
