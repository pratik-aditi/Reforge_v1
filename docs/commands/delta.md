---
tags:
  - commands
  - analysis
---

# /reforge.delta

Incrementally re-extract only files that have changed since a prior run.

## Syntax

=== "Claude Code"

    ```
    /reforge.delta [--since <commit|date>] [--type <extraction-type>] [--json]
    ```

=== "GitHub Copilot"

    ```
    @reforge.delta [--since <commit|date>] [--type <extraction-type>] [--json]
    ```

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `--since` | No | Git commit hash or date to diff against (default: last extraction timestamp) |
| `--type` | No | Specific extraction type to re-extract for changed files |
| `--json` | No | Output delta results as JSON for tooling integration |

## What It Does

This command uses `git diff` to identify source files that have changed since a given point in time, then selectively re-extracts only those files. This avoids a full re-analysis when only a subset of the codebase has been modified.

The delta workflow:

1. **Diff detection** -- identifies added, modified, and deleted files since the `--since` reference
2. **Impact analysis** -- maps changed files to affected extraction types
3. **Selective re-extraction** -- re-runs extraction only for impacted files and types
4. **Delta report** -- documents what changed, what was re-extracted, and what was removed

When `--type` is specified, only that extraction type is re-processed for changed files. Without it, all applicable extraction types are updated.

## Prerequisites

- Completed analysis (`/reforge.analyze`)
- At least one extraction type completed
- Git repository with commit history

## Output

Files are written to `reforge_output/<project>/audit/`:

| File | Description |
|------|-------------|
| `delta-report.xml` | Changed files, re-extraction summary, and removed references |

## Example

=== "Claude Code"

    ```
    /reforge.delta
    /reforge.delta --since abc1234
    /reforge.delta --since 2025-01-15
    /reforge.delta --type business-rules
    /reforge.delta --json
    ```

=== "GitHub Copilot"

    ```
    @reforge.delta
    @reforge.delta --since abc1234
    @reforge.delta --since 2025-01-15
    @reforge.delta --type business-rules
    @reforge.delta --json
    ```

## Related Commands

- [`/reforge.extract`](extract.md) -- full extraction for all files
- [`/reforge.reanalyze`](reanalyze.md) -- re-analyze specific paths without git diffing
- [`/reforge.audit`](audit.md) -- verify coverage after incremental updates
- [`/reforge.compare`](compare.md) -- diff two extraction runs for regression detection
