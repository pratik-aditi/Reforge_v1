---
tags:
  - commands
  - extraction
---

# /reforge.clarify

Interactively resolve ambiguities in extracted code elements.

## Syntax

```
/reforge.clarify [--id <item-id>] [--all] [--category <type>]
```

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `--id` | No | Resolve a specific clarification item by ID |
| `--all` | No | Process all pending clarifications sequentially |
| `--category` | No | Filter by category: `business-rules`, `database`, `ui`, `workflows` |

## What It Does

When the AI agent encounters unclear patterns during extraction -- magic numbers, ambiguous logic, missing context, dead code, dynamic SQL, or unclear event handlers -- it flags them as pending clarifications. This command walks through those items interactively.

For each clarification, the agent:

1. Presents the ambiguous code with surrounding context
2. Explains what is unclear and why it matters
3. Offers interpretation options (specify values, describe business rule, mark as legacy, identify external config, skip, or provide custom interpretation)
4. Records the user's decision
5. Updates the related extraction with improved confidence
6. Searches for similar patterns and applies the decision consistently

Clarifications are sorted by impact -- items affecting multiple workflows or business rules are presented first.

## Clarification Types

| Type | What It Catches |
|------|----------------|
| Magic Numbers | Undefined or unclear numeric constants |
| Ambiguous Logic | Code where intent is unclear |
| Missing Context | Code referencing external resources |
| Dead Code | Potentially unused or obsolete code |
| Dynamic SQL | SQL built from variables at runtime |
| Event Handlers | UI events with unclear triggers |

## Prerequisites

- At least one extraction must be completed
- Pending clarifications must exist

## Output

- Updated clarification files in `.reforge/memory/clarifications/`
- Updated extraction XML files with improved confidence levels

## Example

=== "Claude Code"

    ```
    /reforge.clarify
    /reforge.clarify --id CL-001
    /reforge.clarify --all --category business-rules
    ```

=== "GitHub Copilot"

    ```
    @reforge.clarify
    @reforge.clarify --id CL-001
    @reforge.clarify --all --category business-rules
    ```

## Related Commands

- [`/reforge.extract`](extract.md) -- creates clarification items during extraction
- [`/reforge.status`](status.md) -- shows pending clarification count
