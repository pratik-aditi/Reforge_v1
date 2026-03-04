---
tags:
  - commands
  - generation
---

# /reforge.generate

Generate documentation and artifacts from extracted metadata.

## Syntax

```
/reforge.generate <format> [--output <path>] [--scope <type>]
```

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `format` | Yes | Output format (see table below) |
| `--output` | No | Custom output path (defaults to standard output directory) |
| `--scope` | No | Limit to a specific extraction type (e.g., `business-rules`, `database`) |

## Output Formats

| Format | Output | Notes |
|--------|--------|-------|
| `html` | Self-contained HTML reports with Stephen Few design system, inline SVG diagrams, interactive lightbox, and cross-document navigation | **Recommended** |
| `markdown` | Comprehensive human-readable documentation | |
| `user-stories` | Modernization backlog items with acceptance criteria (MD, JSON, CSV) | |
| `data-dictionary` | Database entity and column documentation | Requires `database` extraction |
| `uml` | Class diagrams in PlantUML/Mermaid notation | Requires `database` extraction |
| `sysml` | System architecture block diagrams | |
| `cross-mappings` | Traceability matrix: features to requirements to rules to workflows to UI to source | |
| `features` | Feature catalog with functional/non-functional requirements derived from extractions | |
| `registries` | Consolidated summary tables of extracted rules, endpoints, events, etc. | |

## What It Does

The generate command reads extraction XML files and transforms them into human-readable documentation. All generated content is strictly **source-anchored** -- every identifier, statistic, and relationship traces back to a specific element in the extraction XML. The agent does not embellish, paraphrase, or inject knowledge from its training data.

The `html` format produces standalone HTML files that work offline with no external dependencies. They include a Stephen Few-inspired design system, inline SVG diagrams rendered from PlantUML, interactive diagram lightbox, cross-document navigation, and print-friendly styling. For large extraction types, HTML output is automatically split into multiple pages.

Generated artifacts are written to `reforge_output/<project>/generated/` (documentation), `reforge_output/<project>/derived/` (cross-mappings, features, registries), or `reforge_output/<project>/diagrams/` (UML, SysML).

## Prerequisites

- At least one extraction must be completed

## Output

| Format | Output Location |
|--------|----------------|
| `html` | `generated/html/` |
| `markdown` | `generated/markdown/` |
| `user-stories` | `generated/user-stories/` |
| `data-dictionary` | `generated/data-dictionary/` |
| `uml` | `diagrams/sources/` and `diagrams/rendered/` |
| `sysml` | `diagrams/sources/` and `diagrams/rendered/` |
| `cross-mappings` | `derived/cross-mappings/` |
| `features` | `derived/features-requirements/` |
| `registries` | `derived/registries/` |

All paths are relative to `reforge_output/<project>/`.

## Example

=== "Claude Code"

    ```
    /reforge.generate html
    /reforge.generate markdown --scope business-rules
    /reforge.generate user-stories
    /reforge.generate data-dictionary
    /reforge.generate cross-mappings
    ```

=== "GitHub Copilot"

    ```
    @reforge.generate html
    @reforge.generate markdown --scope business-rules
    @reforge.generate user-stories
    @reforge.generate data-dictionary
    @reforge.generate cross-mappings
    ```

## Related Commands

- [`/reforge.extract`](extract.md) -- must be run before generation
- [`/reforge.audit`](audit.md) -- verify generation coverage
- [`/reforge.status`](status.md) -- check which artifacts have been generated
