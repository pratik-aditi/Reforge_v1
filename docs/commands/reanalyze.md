# /reforge.reanalyze

Re-analyze specific files or directories without full re-processing.

## Syntax

```
/reforge.reanalyze <path> [--type <extraction>] [--force]
```

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `path` | Yes | File or directory path to re-analyze (supports glob patterns) |
| `--type` | No | Limit to a specific extraction type: `analysis`, `business-rules`, `database`, `ui`, `workflows` |
| `--force` | No | Re-analyze even if file hash has not changed |

## What It Does

This command enables incremental re-analysis after code changes. Instead of re-running the full `/reforge.analyze` pipeline, it processes only the specified files:

1. **Change detection** -- compares file hashes against the stored analysis to identify modifications
2. **Backup** -- saves current state of affected XML entries before modification
3. **Re-analysis** -- re-reads file content, re-detects components, updates the analysis entry
4. **Re-extraction** -- updates extraction entries for changed files (all types or filtered by `--type`)
5. **Cross-reference repair** -- verifies and updates references between extraction types
6. **Stale output marking** -- flags generated documentation that may need regeneration

Without `--force`, unchanged files (same hash) are skipped. Use `--force` after clarifications or when you want to re-extract with updated guidance.

## Prerequisites

- Initial analysis must be completed (`/reforge.analyze`)
- Target files must be within the analyzed project root

## Output

- Updated `analysis.xml` entries for re-analyzed files
- Updated extraction XML files with re-extracted elements
- Backup of previous state in `.reforge/memory/backups/`

## Example

=== "Claude Code"

    ```
    /reforge.reanalyze src/service/OrderService.java
    /reforge.reanalyze src/service/ --type business-rules
    /reforge.reanalyze "src/**/*Service.java"
    /reforge.reanalyze src/model/Order.java --force
    ```

=== "GitHub Copilot"

    ```
    @reforge.reanalyze src/service/OrderService.java
    @reforge.reanalyze src/service/ --type business-rules
    @reforge.reanalyze "src/**/*Service.java"
    @reforge.reanalyze src/model/Order.java --force
    ```

## Related Commands

- [`/reforge.analyze`](analyze.md) -- full codebase analysis (run first)
- [`/reforge.audit`](audit.md) -- identifies stale references that need re-analysis
- [`/reforge.fix`](fix.md) -- dispatches to reanalyze for analysis corrections
- [`/reforge.status`](status.md) -- check current analysis state
