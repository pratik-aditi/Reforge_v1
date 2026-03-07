---
tags:
  - commands
  - reporting
---

# /reforge.export

Export extraction artifacts to external project management formats.

## Syntax

=== "Claude Code"

    ```
    /reforge.export <format> [--type user-stories|business-rules|issues] [--output path]
    ```

=== "GitHub Copilot"

    ```
    @reforge.export <format> [--type user-stories|business-rules|issues] [--output path]
    ```

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `format` | Yes | Target format: `jira-csv`, `azure-devops`, `confluence`, `github-issues` |
| `--type` | No | Specific artifact type to export (default: all available) |
| `--output` | No | Custom output path (default: `reforge_output/<project>/exports/`) |

**Supported formats:**

| Format | Description |
|--------|-------------|
| `jira-csv` | CSV importable into Jira with summary, description, type, and priority fields |
| `azure-devops` | JSON work items compatible with Azure DevOps import |
| `confluence` | Confluence wiki markup for documentation publishing |
| `github-issues` | JSON array of issues for GitHub CLI or API import |

## What It Does

Transforms Reforge extraction artifacts into formats consumable by external project management and documentation tools. Each export maps extracted fields (title, description, source references, confidence, priority) to the target platform's schema.

When `--type` is omitted, all exportable artifact types are included in the output.

## Prerequisites

- At least one exportable artifact generated (user stories, business rules, or issues)

## Output

Files are written to `reforge_output/<project>/exports/`:

| File | Description |
|------|-------------|
| `<format>-export.*` | Exported artifacts in the requested format |

## Example

=== "Claude Code"

    ```
    /reforge.export jira-csv
    /reforge.export github-issues --type user-stories
    /reforge.export confluence --type business-rules --output ./my-exports/
    ```

=== "GitHub Copilot"

    ```
    @reforge.export jira-csv
    @reforge.export github-issues --type user-stories
    @reforge.export confluence --type business-rules --output ./my-exports/
    ```

## Related Commands

- [`/reforge.generate`](generate.md) -- generate the artifacts that feed exports
- [`/reforge.dashboard`](dashboard.md) -- visual summary of all extractions
- [`/reforge.report`](report.md) -- generate progress reports
