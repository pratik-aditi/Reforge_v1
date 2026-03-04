# /reforge.audit

Audit extraction coverage and identify gaps against the analyzed codebase.

## Syntax

```
/reforge.audit [type] [--json]
```

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `type` | No | Specific artifact type to audit (see list below) |
| `--json` | No | Output audit results as JSON for tooling integration |

**Auditable types:** `analysis`, `business-rules`, `database`, `ui-flows`, `workflows`, `call-sites`, `dependencies`, `functional-requirements`, `non-functional`, `architecture`, `issues`, `user-stories`, `documentation`, `diagrams`

## What It Does

This command compares your analysis inventory against extraction and generation outputs to identify:

- **Coverage gaps** -- analyzed source files with no extraction references
- **Stale references** -- extractions pointing to files that no longer exist or have changed since extraction
- **Per-type coverage breakdown** -- how well each extraction type covers the codebase

The audit produces two outputs:

- **`audit-report.xml`** -- a read-only diagnostic with coverage statistics, gap listings, and stale reference details
- **`correction-plan.xml`** -- an actionable plan of corrections consumed by `/reforge.fix`

When run without a `type` argument, the audit covers all available extraction types. When a specific type is provided, only that type is audited.

## Prerequisites

- Completed analysis (`/reforge.analyze`)
- At least one extraction type completed (recommended for meaningful results)

## Output

Files are written to `reforge_output/<project>/audit/`:

| File | Description |
|------|-------------|
| `audit-report.xml` | Coverage statistics and gap analysis (read-only diagnostic) |
| `correction-plan.xml` | Actionable corrections for `/reforge.fix` |

## Example

=== "Claude Code"

    ```
    /reforge.audit
    /reforge.audit business-rules
    /reforge.audit --json
    ```

=== "GitHub Copilot"

    ```
    @reforge.audit
    @reforge.audit business-rules
    @reforge.audit --json
    ```

## Related Commands

- [`/reforge.fix`](fix.md) -- execute corrections from the audit
- [`/reforge.extract`](extract.md) -- fill coverage gaps identified by audit
- [`/reforge.reanalyze`](reanalyze.md) -- update stale analysis entries
- [`/reforge.status`](status.md) -- broader progress overview
