---
tags:
  - commands
  - analysis
---

# /reforge.dead-code

Detect unreachable code via call-site and dependency graph analysis.

## Syntax

=== "Claude Code"

    ```
    /reforge.dead-code [--scope module|project] [--include-tests] [--format html|xml] [--json]
    ```

=== "GitHub Copilot"

    ```
    @reforge.dead-code [--scope module|project] [--include-tests] [--format html|xml] [--json]
    ```

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `--scope` | No | Granularity: `module` (default) or `project` for cross-module analysis |
| `--include-tests` | No | Include test files in the dead code scan (excluded by default) |
| `--format` | No | Output format: `xml` (default) or `html` for a styled report |
| `--json` | No | Output dead code results as JSON for tooling integration |

## What It Does

This command cross-references call-site and dependency extractions to identify code with no inbound references. It detects:

- **Dead methods** -- functions and methods never called from any other code
- **Dead classes** -- classes never instantiated or referenced
- **Dead files** -- source files with no inbound dependencies
- **Dead variables** -- module-level variables never read
- **Dead imports** -- imported symbols never used

The analysis builds a reachability graph from known entry points (main methods, route handlers, event listeners) and flags anything not reachable. Results include confidence scores reflecting the completeness of the call-site data.

Use `--include-tests` to scan test files as well -- by default, test files are excluded since test-only references do not indicate production usage.

## Prerequisites

- Completed analysis (`/reforge.analyze`)
- Call-sites extraction completed (`/reforge.extract call-sites`)
- Dependencies extraction completed (`/reforge.extract dependencies`)

## Output

Files are written to `reforge_output/<project>/derived/`:

| File | Description |
|------|-------------|
| `dead-code-report.xml` | Dead code inventory with categories, locations, and confidence scores |

## Example

=== "Claude Code"

    ```
    /reforge.dead-code
    /reforge.dead-code --scope project
    /reforge.dead-code --include-tests
    /reforge.dead-code --format html
    /reforge.dead-code --json
    ```

=== "GitHub Copilot"

    ```
    @reforge.dead-code
    @reforge.dead-code --scope project
    @reforge.dead-code --include-tests
    @reforge.dead-code --format html
    @reforge.dead-code --json
    ```

## Related Commands

- [`/reforge.extract`](extract.md) -- produce call-sites and dependencies extractions
- [`/reforge.metrics`](metrics.md) -- quantitative metrics including tech debt from dead code
- [`/reforge.audit`](audit.md) -- verify extraction coverage completeness
