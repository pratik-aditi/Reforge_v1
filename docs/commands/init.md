---
tags:
  - commands
  - planning
---

# /reforge.init

Initialize project context with domain knowledge to guide all subsequent analysis.

## Syntax

```
/reforge.init [--update]
```

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `--update` | No | Update existing project context (re-run questions) |

## What It Does

This interactive command collects information about your project that guides all subsequent Reforge analysis. It walks through a series of prompts to gather:

- **Project identity** -- name, description, root path to analyze
- **Technology stack** -- languages, frameworks, build system, databases
- **Domain knowledge** -- business concepts and terminology
- **Analysis guidelines** -- focus areas, known patterns, directories to prioritize or ignore
- **Custom rules** -- architectural patterns, naming conventions, known technical debt

The gathered information is written to `.reforge/memory/project-context.md` and referenced by every other command as supplemental context. It also updates `.reforge/config.json` with the project name, description, and root path.

!!! tip
    Run this command before `/reforge.analyze` for best results. Domain knowledge and technology context significantly improve extraction accuracy.

## Output

- `.reforge/memory/project-context.md` -- structured project context file
- `.reforge/config.json` -- updated with project identity fields

## Example

=== "Claude Code"

    ```
    /reforge.init
    /reforge.init --update
    ```

=== "GitHub Copilot"

    ```
    @reforge.init
    @reforge.init --update
    ```

## Related Commands

- [`/reforge.profile`](profile.md) -- generate language-specific extraction profile (run after init)
- [`/reforge.analyze`](analyze.md) -- scan and inventory the codebase (run after init)
