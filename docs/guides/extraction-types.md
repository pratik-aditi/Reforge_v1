---
tags:
  - guides
  - extraction
---

# Extraction Types

Reforge supports 10 extraction types organized into two tiers: 4 core types that cover the most common modernization needs, and 6 extended types for deeper analysis.

## Command Syntax

=== "Claude Code"

    ```
    /reforge.extract <type> [--files <pattern>] [--confidence <level>]
    ```

=== "GitHub Copilot"

    ```
    @reforge.extract <type> [--files <pattern>] [--confidence <level>]
    ```

| Option | Description |
|--------|-------------|
| `--files <pattern>` | Limit extraction to files matching the glob pattern |
| `--confidence <level>` | Minimum confidence threshold: `high`, `medium`, or `low` |
| `--subtype <name>` | For `architecture` type only (see below) |

---

## Core Types

### `business-rules`

Extracts conditional logic, validation rules, calculations, and business constraints from source code.

**Use cases**: Understanding pricing logic, authorization rules, data validation, domain-specific calculations that must be preserved during modernization.

**Key output fields**:

| Field | Description |
|-------|-------------|
| `<rule>` | Individual business rule element |
| `<category>` | Rule classification (validation, calculation, authorization, etc.) |
| `<condition>` | The conditional expression or guard clause |
| `<action>` | What happens when the condition is met |
| `<source-ref>` | File path and line number reference |
| `<confidence>` | `high`, `medium`, or `low` |
| `<code-snippet>` | Source code excerpt (when `includeSnippets` is enabled) |

---

### `database`

Extracts SQL queries, data models, ORM mappings, schema definitions, and entity relationships.

**Use cases**: Building a data dictionary, mapping table relationships, cataloging all database interactions for migration planning.

**Key output fields**:

| Field | Description |
|-------|-------------|
| `<entity>` | Database table or model definition |
| `<column>` | Column name, type, constraints, and foreign keys |
| `<query>` | SQL statement with operation type (SELECT, INSERT, UPDATE, DELETE) |
| `<relationship>` | Foreign key or ORM-defined relationship between entities |
| `<source-ref>` | File path and line number reference |

---

### `ui`

Extracts screen layouts, UI components, navigation flows, and form structures.

**Use cases**: Inventorying all screens for a UI redesign, mapping navigation flows, documenting form fields and their validation rules.

**Key output fields**:

| Field | Description |
|-------|-------------|
| `<screen>` | Screen or page definition |
| `<component>` | UI component (button, form, table, etc.) |
| `<navigation>` | Navigation link or route between screens |
| `<form>` | Form definition with field types and validation |
| `<event>` | User interaction event handler |
| `<source-ref>` | File path and line number reference |

---

### `workflows`

Extracts execution paths, state machines, event handlers, and process flows.

**Use cases**: Documenting order processing pipelines, approval chains, background job sequences, and multi-step business processes.

**Key output fields**:

| Field | Description |
|-------|-------------|
| `<workflow>` | Top-level workflow definition |
| `<step>` | Individual step in the workflow sequence |
| `<trigger>` | What initiates the workflow (HTTP request, event, schedule, etc.) |
| `<decision>` | Branch point with conditions |
| `<transition>` | Connection between steps with condition |
| `<source-ref>` | File path and line number reference |

---

## Extended Types

### `call-sites`

Extracts method and function call relationships, mapping callers to callees with source traceability.

**Use cases**: Understanding call chains for impact analysis, identifying heavily-used utility functions, mapping entry points through the codebase.

**Key output fields**:

| Field | Description |
|-------|-------------|
| `<call-site>` | Individual call relationship |
| `<caller>` | The calling function/method with file and line |
| `<callee>` | The called function/method with file and line |
| `<call-type>` | Direct, virtual, static, callback, etc. |
| `<arguments>` | Argument types or names passed |

---

### `dependencies`

Extracts module dependency graphs including imports, event subscriptions, interface implementations, and inheritance hierarchies.

**Use cases**: Mapping module coupling for decomposition planning, identifying circular dependencies, understanding event-driven communication patterns.

**Key output fields**:

| Field | Description |
|-------|-------------|
| `<dependency>` | Individual dependency relationship |
| `<source-module>` | The dependent module |
| `<target-module>` | The dependency target |
| `<dependency-type>` | Import, event, interface, inheritance, etc. |
| `<strength>` | Coupling strength indicator |

---

### `functional-requirements`

Derives functional requirements with acceptance criteria from observed code behavior.

**Use cases**: Generating a requirements backlog from legacy code, creating acceptance tests, validating that modernized code preserves all existing functionality.

**Key output fields**:

| Field | Description |
|-------|-------------|
| `<requirement>` | Individual functional requirement |
| `<title>` | Short requirement title |
| `<description>` | Detailed requirement description |
| `<acceptance-criteria>` | Testable criteria derived from code behavior |
| `<priority>` | Derived priority level |
| `<source-ref>` | Source file and line references |

---

### `non-functional`

Extracts non-functional requirements (SLAs, performance characteristics) and security findings with CWE classification.

**Use cases**: Documenting performance constraints, identifying security vulnerabilities, cataloging SLA-related code for operational handoff.

**Key output fields**:

| Field | Description |
|-------|-------------|
| `<requirement>` | Non-functional requirement or security finding |
| `<category>` | Performance, security, reliability, scalability, etc. |
| `<cwe-id>` | CWE identifier for security findings (when applicable) |
| `<severity>` | Impact severity level |
| `<constraint>` | The specific constraint or threshold |
| `<source-ref>` | Source file and line references |

---

### `architecture`

Extracts architectural components, integration points, and design patterns. Supports focused extraction via `--subtype`.

**Use cases**: Documenting the overall system architecture, cataloging third-party integrations, identifying design patterns for modernization decisions.

**Subtypes**:

| Subtype | Focus |
|---------|-------|
| `design-patterns` | Recognized design patterns (factory, observer, repository, etc.) |
| `integrations` | External system integration points (APIs, message queues, file transfers) |
| `infrastructure` | Infrastructure concerns (caching, logging, configuration, health checks) |

=== "Claude Code"

    ```
    /reforge.extract architecture
    /reforge.extract architecture --subtype design-patterns
    /reforge.extract architecture --subtype integrations
    /reforge.extract architecture --subtype infrastructure
    ```

=== "GitHub Copilot"

    ```
    @reforge.extract architecture
    @reforge.extract architecture --subtype design-patterns
    @reforge.extract architecture --subtype integrations
    @reforge.extract architecture --subtype infrastructure
    ```

**Key output fields**:

| Field | Description |
|-------|-------------|
| `<component>` | Architectural component definition |
| `<layer>` | Architectural layer (presentation, business, data, infrastructure) |
| `<pattern>` | Identified design pattern |
| `<integration>` | External system integration point |
| `<technology>` | Technology or framework used |
| `<source-ref>` | Source file and line references |

---

### `issues`

Extracts bugs, defects, TODOs, technical debt markers, and operational issues found in the codebase.

**Use cases**: Building a technical debt backlog, cataloging known bugs before modernization, identifying operational risks in legacy code.

**Key output fields**:

| Field | Description |
|-------|-------------|
| `<issue>` | Individual issue or defect |
| `<issue-type>` | Bug, TODO, technical-debt, operational, etc. |
| `<severity>` | Critical, high, medium, low |
| `<description>` | Issue description |
| `<remediation>` | Suggested fix or resolution approach |
| `<source-ref>` | Source file and line references |

---

## Common Output Structure

All extraction types share a common XML structure defined by the [common extraction schema](https://reforge.dev/schema/extraction). Every extraction file includes:

- **Root attributes**: `project-id`, `version`, `schema-version`, `generated` timestamp
- **Metadata block**: `total-count`, `confidence-distribution` (high/medium/low counts), `extraction-timestamp`
- **Source references**: Every extracted item includes `<source-ref>` with file path, line start, line end, and optional code snippet

!!! info "Confidence levels"
    Each extracted item is assigned a confidence level:

    - **High** -- The pattern is unambiguous and well-supported by code evidence
    - **Medium** -- The pattern is likely correct but involves some interpretation
    - **Low** -- The pattern is possible but based on limited evidence or ambiguous code

    Use the `--confidence` flag or the `extraction.confidenceThreshold` config setting to filter items below a threshold.
