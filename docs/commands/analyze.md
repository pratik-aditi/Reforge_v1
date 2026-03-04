---
tags:
  - commands
  - planning
---

# /reforge.analyze

Scan and inventory a legacy codebase for analysis and documentation.

## Syntax

```
/reforge.analyze [path] [--resume] [--force]
```

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `path` | No | Target directory to analyze (defaults to current working directory) |
| `--resume` | No | Resume from last checkpoint if available |
| `--force` | No | Force full re-analysis, ignoring checkpoints |

## What It Does

This command performs the initial inventory and analysis of a legacy codebase. It scans all files in the target directory, detects programming languages and frameworks, identifies module boundaries and components, and creates a structured XML inventory.

The analysis workflow:

1. Discovers all files respecting exclusion patterns from `config.json`
2. Categorizes files by type (source, config, template, data, binary)
3. Detects languages by file extension and content analysis
4. Identifies components (classes, interfaces, methods, imports, exports)
5. Detects frameworks from dependency files, import patterns, and configuration
6. Generates an XML inventory with per-file component listings

The command supports **checkpointing** -- large analyses can be interrupted and resumed with `--resume`. Checkpoints are saved every 50 files or 10% of progress. Binary files are inventoried (path, size, extension) but their content is not read.

## Prerequisites

- `.reforge/` directory structure must exist
- Configuration set in `.reforge/config.json`

!!! tip
    Run `/reforge.init` and `/reforge.profile` before analyzing for best results.

## Output

- `reforge_output/<project>/analysis/analysis.xml` -- structured codebase inventory

## Example

=== "Claude Code"

    ```
    /reforge.analyze
    /reforge.analyze ./src --resume
    /reforge.analyze --force
    ```

=== "GitHub Copilot"

    ```
    @reforge.analyze
    @reforge.analyze ./src --resume
    @reforge.analyze --force
    ```

## Related Commands

- [`/reforge.init`](init.md) -- set up project context before analysis
- [`/reforge.extract`](extract.md) -- extract knowledge from the analyzed codebase
- [`/reforge.reanalyze`](reanalyze.md) -- incrementally re-process specific files
- [`/reforge.status`](status.md) -- check analysis progress
