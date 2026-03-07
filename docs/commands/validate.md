---
tags:
  - commands
  - validation
---

# /reforge.validate

Validate extraction XML for structural conformance, ID integrity, and data consistency.

## Syntax

=== "Claude Code"

    ```
    /reforge.validate [--type <type>] [--fix] [--json]
    ```

=== "GitHub Copilot"

    ```
    @reforge.validate [--type <type>] [--fix] [--json]
    ```

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `--type` | No | Specific extraction type to validate (e.g., `business-rules`, `database`) |
| `--fix` | No | Automatically correct fixable validation errors in-place |
| `--json` | No | Output validation results as JSON for tooling integration |

## What It Does

This command performs four validation checks against extraction XML files:

- **XSD conformance** -- verifies each extraction file matches its formal schema definition
- **ID uniqueness** -- ensures no duplicate IDs exist within or across extraction files
- **Cross-reference integrity** -- confirms all `ref` and `source-ref` attributes point to valid targets
- **Confidence sum correctness** -- validates that confidence scores are within valid ranges and sum correctly where required

When run without `--type`, all extraction types are validated. When a specific type is provided, only that type is checked.

The `--fix` flag attempts to auto-correct simple issues such as malformed IDs or out-of-range confidence values. Structural errors that cannot be auto-corrected are reported for manual resolution.

## Prerequisites

- Completed analysis (`/reforge.analyze`)
- At least one extraction type completed

## Output

Files are written to `reforge_output/<project>/audit/`:

| File | Description |
|------|-------------|
| `validation-report.xml` | Detailed validation results with error locations and severity |

## Example

=== "Claude Code"

    ```
    /reforge.validate
    /reforge.validate --type business-rules
    /reforge.validate --fix
    /reforge.validate --json
    ```

=== "GitHub Copilot"

    ```
    @reforge.validate
    @reforge.validate --type business-rules
    @reforge.validate --fix
    @reforge.validate --json
    ```

## Related Commands

- [`/reforge.audit`](audit.md) -- coverage gap analysis across extractions
- [`/reforge.fix`](fix.md) -- execute corrections from audit or validation
- [`/reforge.extract`](extract.md) -- produce extraction files to validate
