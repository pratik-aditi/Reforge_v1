# /reforge.plan

Create and manage a project plan for the Reforge extraction workflow.

## Syntax

```
/reforge.plan [arguments] [--status]
```

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `arguments` | No | Natural language describing items to add (e.g., `"add database extraction and UML diagrams"`) |
| `--status` | No | Display progress summary without modifying the plan |

## What It Does

This command creates and manages a checklist-based project plan at `.reforge/memory/project-plan.md`. The plan tracks all extraction, audit, and generation work using markdown checkboxes with inline HTML comment tags for machine matching.

The plan organizes work into a **Setup section** (init, analyze, profile), **Workflow groups** with a 7-step pipeline per extraction type (extract, clarify, audit extractions, fix extractions, generate, audit generated, fix generated), and an optional **Custom Tasks** section for items outside the extraction pipeline.

All other Reforge commands check for this plan on startup and auto-mark their corresponding checkboxes on successful completion.

## Behavioral Modes

The command operates in one of four modes based on context:

| Condition | Mode |
|-----------|------|
| `--status` flag present | **Status** -- display progress, do not modify |
| No existing plan | **Create** -- gather input, generate plan |
| Existing plan + arguments | **Add** -- append new items |
| Existing plan, no arguments | **Interactive Review** -- show status, offer to add |

In **Create** mode, the command reads `analysis.xml` and `extraction-profile.md` (if available) to suggest extraction types based on evidence found in your codebase.

## Output

- `.reforge/memory/project-plan.md` -- the checklist-based project plan

## Example

=== "Claude Code"

    ```
    /reforge.plan
    /reforge.plan "add database extraction and UML diagrams"
    /reforge.plan --status
    ```

=== "GitHub Copilot"

    ```
    @reforge.plan
    @reforge.plan "add database extraction and UML diagrams"
    @reforge.plan --status
    ```

## Related Commands

- [`/reforge.init`](init.md) -- initialize project context (tracked by plan)
- [`/reforge.status`](status.md) -- broader progress report including plan status
