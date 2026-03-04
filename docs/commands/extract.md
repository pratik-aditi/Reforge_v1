# /reforge.extract

Extract specific knowledge elements from the analyzed codebase.

## Syntax

```
/reforge.extract <type> [--files <pattern>] [--confidence <level>] [--subtype <subtype>]
```

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `type` | Yes | Extraction type (see tables below) |
| `--files` | No | Limit extraction to files matching a glob pattern |
| `--confidence` | No | Minimum confidence threshold: `high`, `medium`, `low` (default: all) |
| `--subtype` | No | For `architecture` type only: `design-patterns`, `integrations`, `infrastructure` |

## Extraction Types

### Core Types

| Type | What It Extracts |
|------|-----------------|
| `business-rules` | Conditional logic, validations, calculations, business constraints |
| `database` | SQL statements, data models, ORM mappings, entity relationships |
| `ui` | Screen layouts, components, navigation flows, form structures |
| `workflows` | Execution paths, state machines, event handlers, process flows |

### Extended Types

| Type | What It Extracts |
|------|-----------------|
| `call-sites` | Method/function call relationships with caller and callee source traceability |
| `dependencies` | Module dependency graphs -- imports, events, interfaces, inheritance |
| `functional-requirements` | Functional requirements with acceptance criteria derived from code behavior |
| `non-functional` | Non-functional requirements (SLAs, performance) and security findings (CWE) |
| `architecture` | Architectural components, integration points, and design patterns |
| `issues` | Bugs, defects, TODOs, technical debt, and operational issues |

## What It Does

The extract command reads the analysis inventory (`analysis.xml`), processes each relevant source file, and identifies elements matching the requested extraction type. Every extracted element includes:

- **Confidence level** (high, medium, low) indicating extraction certainty
- **Source location** with file path, line numbers, and code snippet
- **Unique identifier** for cross-referencing across extraction types
- **Category** classification within the extraction type

The command automatically loads the extraction profile (from `/reforge.profile`) for language-specific guidance and the project context (from `/reforge.init`) for domain awareness. Items flagged as ambiguous are saved as pending clarifications for `/reforge.clarify`.

!!! note
    The `architecture` type supports the `--subtype` flag to focus on specific aspects: `design-patterns` for recognized patterns, `integrations` for external system connections, or `infrastructure` for deployment and runtime components.

## Prerequisites

- Analysis must be completed (`/reforge.analyze`)

## Output

Extraction XML files are written to `reforge_output/<project>/extractions/`:

| Type | Output File |
|------|-------------|
| `business-rules` | `business-rules.xml` |
| `database` | `database.xml` |
| `ui` | `ui-flows.xml` |
| `workflows` | `workflows.xml` |
| `call-sites` | `call-sites.xml` |
| `dependencies` | `dependencies.xml` |
| `functional-requirements` | `functional-requirements.xml` |
| `non-functional` | `non-functional-requirements.xml` |
| `architecture` | `architecture.xml` |
| `issues` | `issues.xml` |

## Example

=== "Claude Code"

    ```
    /reforge.extract business-rules
    /reforge.extract database --files "src/**/*Repository.java"
    /reforge.extract architecture --subtype design-patterns
    /reforge.extract non-functional --confidence high
    ```

=== "GitHub Copilot"

    ```
    @reforge.extract business-rules
    @reforge.extract database --files "src/**/*Repository.java"
    @reforge.extract architecture --subtype design-patterns
    @reforge.extract non-functional --confidence high
    ```

## Related Commands

- [`/reforge.analyze`](analyze.md) -- must be run before extraction
- [`/reforge.profile`](profile.md) -- improves extraction accuracy with language-specific rules
- [`/reforge.clarify`](clarify.md) -- resolve ambiguities flagged during extraction
- [`/reforge.generate`](generate.md) -- generate documentation from extractions
- [`/reforge.audit`](audit.md) -- check extraction coverage
