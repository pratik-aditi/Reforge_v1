---
tags:
  - commands
  - analysis
---

# /reforge.compare

Diff two extraction runs for regression detection.

## Syntax

=== "Claude Code"

    ```
    /reforge.compare <file1> <file2> [--type extraction-type] [--json]
    ```

=== "GitHub Copilot"

    ```
    @reforge.compare <file1> <file2> [--type extraction-type] [--json]
    ```

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `file1` | Yes | Path to the first extraction XML file |
| `file2` | Yes | Path to the second extraction XML file |
| `--type` | No | Extraction type for schema-aware comparison |
| `--json` | No | Output results as JSON for tooling integration |

## What It Does

Compares any two extraction XML files of the same type and produces a detailed diff report identifying:

- **Added items** -- new extractions present only in the second file
- **Removed items** -- extractions present in the first file but missing from the second
- **Modified items** -- extractions that exist in both but have changed content, confidence, or source references

This is useful for detecting regressions after re-extraction, verifying that fixes from `/reforge.fix` were applied correctly, or tracking how extractions evolve across iterations.

## Prerequisites

- Two extraction XML files of the same type (e.g., two versions of `business-rules.xml`)

## Output

Files are written to `reforge_output/<project>/audit/`:

| File | Description |
|------|-------------|
| `comparison-report.xml` | Itemized diff with added, removed, and modified entries |

## Example

=== "Claude Code"

    ```
    /reforge.compare extractions/business-rules-v1.xml extractions/business-rules-v2.xml
    /reforge.compare extractions/database-v1.xml extractions/database-v2.xml --type database
    ```

=== "GitHub Copilot"

    ```
    @reforge.compare extractions/business-rules-v1.xml extractions/business-rules-v2.xml
    @reforge.compare extractions/database-v1.xml extractions/database-v2.xml --type database
    ```

## Related Commands

- [`/reforge.delta`](delta.md) -- incremental extraction based on git diffs
- [`/reforge.audit`](audit.md) -- audit extraction coverage
- [`/reforge.extract`](extract.md) -- produce extraction artifacts to compare
