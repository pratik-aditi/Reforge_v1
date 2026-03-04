# /reforge.status

Show analysis progress, coverage statistics, and pending items.

## Syntax

```
/reforge.status [--detailed] [--json]
```

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `--detailed` | No | Show file-level progress details |
| `--json` | No | Output status as JSON for tooling integration |

## What It Does

This command provides a read-only dashboard of the current analysis state. It reports:

- **Analysis progress** -- completed, in-progress, or not started, with file counts and timing
- **Extraction status** -- per-type completion with item counts and confidence breakdowns (high/medium/low)
- **Glossary status** -- version, entry count, and generation timestamp
- **Pending clarifications** -- count of items awaiting user input
- **Generated outputs** -- which documentation artifacts have been created
- **Project plan progress** -- if a plan exists, shows per-section completion percentages
- **Contextual next steps** -- recommendations based on current state

The `--detailed` flag adds file-level information: completed files, pending files, skipped files, and files with errors. The `--json` flag outputs the full status as structured JSON for tooling integration.

This command does not modify any files -- it is purely informational.

## Extraction Types Tracked

| Type | Status File |
|------|-------------|
| Business Rules | `extractions/business-rules.xml` |
| Database | `extractions/database.xml` |
| UI Flows | `extractions/ui-flows.xml` |
| Workflows | `extractions/workflows.xml` |
| Call Sites | `extractions/call-sites.xml` |
| Dependencies | `extractions/dependencies.xml` |
| Functional Requirements | `extractions/functional-requirements.xml` |
| Non-Functional | `extractions/non-functional-requirements.xml` |
| Architecture | `extractions/architecture.xml` |
| Issues | `extractions/issues.xml` |

## Output

Status is printed to the console. No files are created or modified.

## Example

=== "Claude Code"

    ```
    /reforge.status
    /reforge.status --detailed
    /reforge.status --json
    ```

=== "GitHub Copilot"

    ```
    @reforge.status
    @reforge.status --detailed
    @reforge.status --json
    ```

## Related Commands

- [`/reforge.plan`](plan.md) -- manage the project plan shown in status
- [`/reforge.analyze`](analyze.md) -- start or resume analysis
- [`/reforge.extract`](extract.md) -- run extractions shown as "Not Started"
- [`/reforge.clarify`](clarify.md) -- resolve pending clarifications
