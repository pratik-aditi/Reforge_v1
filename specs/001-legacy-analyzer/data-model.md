# Data Model: Reforge Legacy Analyzer Framework

**Branch**: `001-legacy-analyzer` | **Date**: 2025-01-13

## Overview

This document defines the data entities used by the Reforge framework. All entities are serialized as XML elements and stored in the output directory structure defined in the plan.

---

## Core Entities

### AnalysisProject

Represents a target codebase under analysis. Root entity for all analysis operations.

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string | Yes | Unique project identifier (derived from directory name) |
| `name` | string | Yes | Human-readable project name |
| `root-path` | string | Yes | Absolute path to codebase root |
| `created` | datetime | Yes | Analysis start timestamp |
| `updated` | datetime | Yes | Last modification timestamp |
| `status` | enum | Yes | `not-started`, `in-progress`, `completed`, `paused` |

**Relationships**:
- Has many `SourceFile`
- Has many `AnalysisCheckpoint`
- Has one `Configuration`

**XML Element**: `<project>`

---

### SourceFile

Individual source file with analysis metadata.

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `path` | string | Yes | Relative path from project root |
| `language` | string | Yes | Detected programming language |
| `file-type` | enum | Yes | `source`, `config`, `template`, `data`, `binary`, `unknown` |
| `size-bytes` | integer | Yes | File size in bytes |
| `line-count` | integer | No | Number of lines (null for binary) |
| `hash` | string | Yes | Content hash for change detection |
| `analysis-status` | enum | Yes | `pending`, `in-progress`, `completed`, `skipped`, `error` |
| `analyzed-at` | datetime | No | When analysis completed |

**Relationships**:
- Belongs to `AnalysisProject`
- Has many `BusinessRule`
- Has many `DatabaseInteraction`
- Has many `UIComponent`
- Has many `Workflow` (as entry point)

**XML Element**: `<file>`

---

### BusinessRule

Extracted business logic with full traceability.

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string | Yes | Unique rule identifier (e.g., `BR-001`) |
| `category` | string | Yes | Domain category (e.g., `pricing`, `validation`, `authorization`) |
| `description` | string | Yes | Human-readable rule description |
| `logic` | string | Yes | Extracted code or pseudo-code |
| `confidence` | enum | Yes | `high`, `medium`, `low` |

**Source Reference** (nested):
| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `file` | string | Yes | Source file path |
| `line-start` | integer | Yes | Starting line number |
| `line-end` | integer | Yes | Ending line number |
| `snippet` | string | No | Code snippet for context |

**Relationships**:
- Belongs to `SourceFile`
- References many `DataEntity`
- May generate `GeneratedUserStory`

**XML Element**: `<business-rule>`

---

### DatabaseInteraction

Captured SQL statement with execution context.

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string | Yes | Unique identifier (e.g., `SQL-001`) |
| `operation` | enum | Yes | `SELECT`, `INSERT`, `UPDATE`, `DELETE`, `DDL`, `CALL` |
| `sql` | string | Yes | Full SQL statement |
| `tables` | string[] | Yes | Tables referenced |
| `columns` | string[] | No | Columns referenced |
| `confidence` | enum | Yes | `high`, `medium`, `low` |

**Execution Context** (nested):
| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `method` | string | Yes | Calling method name |
| `class` | string | No | Containing class/module |
| `trigger` | string | No | What triggers this query |

**Source Reference** (nested): Same as BusinessRule

**Relationships**:
- Belongs to `SourceFile`
- References many `DataEntity`
- Part of `Workflow` steps

**XML Element**: `<database-interaction>`

---

### DataEntity

Inferred or extracted data model element.

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string | Yes | Unique identifier (e.g., `ENT-001`) |
| `name` | string | Yes | Entity/table name |
| `type` | enum | Yes | `table`, `view`, `entity`, `dto` |
| `source-type` | enum | Yes | `ddl`, `orm`, `inferred`, `config` |
| `confidence` | enum | Yes | `high`, `medium`, `low` |

**Column** (nested, multiple):
| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | string | Yes | Column/field name |
| `data-type` | string | Yes | Data type |
| `nullable` | boolean | No | Whether nullable |
| `primary-key` | boolean | No | Whether primary key |
| `foreign-key` | string | No | Referenced entity.column |

**Relationships**:
- Referenced by `BusinessRule`
- Referenced by `DatabaseInteraction`
- Has many relationships to other `DataEntity`

**XML Element**: `<data-entity>`

---

### UIComponent

Extracted UI element with interaction mapping.

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string | Yes | Unique identifier (e.g., `UI-001`) |
| `screen` | string | Yes | Parent screen/page name |
| `type` | enum | Yes | `button`, `input`, `form`, `table`, `label`, `link`, `container` |
| `name` | string | No | Component name/label |
| `confidence` | enum | Yes | `high`, `medium`, `low` |

**Layout Position** (nested):
| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `row` | integer | No | Grid row position |
| `column` | integer | No | Grid column position |
| `parent` | string | No | Parent component ID |

**Event Handler** (nested, multiple):
| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `event` | string | Yes | Event type (e.g., `click`, `submit`) |
| `handler` | string | Yes | Handler method reference |
| `workflow-ref` | string | No | Associated workflow ID |

**Source Reference** (nested): Same as BusinessRule

**Relationships**:
- Belongs to `SourceFile`
- Triggers `Workflow`
- Part of screen layout

**XML Element**: `<ui-component>`

---

### Workflow

Traced execution path from entry point.

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string | Yes | Unique identifier (e.g., `WF-001`) |
| `name` | string | Yes | Workflow name/description |
| `entry-point` | string | Yes | Starting method/handler |
| `trigger-type` | enum | Yes | `ui-action`, `api-call`, `scheduled`, `message`, `startup` |
| `confidence` | enum | Yes | `high`, `medium`, `low` |

**Step** (nested, multiple, ordered):
| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `sequence` | integer | Yes | Step order (1-based) |
| `type` | enum | Yes | `method-call`, `decision`, `loop`, `data-access`, `external-call` |
| `description` | string | Yes | What this step does |
| `method` | string | No | Method being called |
| `condition` | string | No | Branch condition (for decisions) |
| `sql-ref` | string | No | Referenced DatabaseInteraction ID |
| `branches` | Step[] | No | Child branches (for decisions) |

**Source Reference** (nested): Same as BusinessRule

**Relationships**:
- Triggered by `UIComponent`
- Contains `DatabaseInteraction` references
- References `BusinessRule` logic
- Generates `GeneratedUserStory`

**XML Element**: `<workflow>`

---

### GeneratedUserStory

Modernization backlog item derived from extractions.

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string | Yes | Unique identifier (e.g., `US-001`) |
| `title` | string | Yes | Story title |
| `actor` | string | Yes | User role/persona |
| `action` | string | Yes | What the user wants to do |
| `value` | string | Yes | Why they want to do it |
| `priority` | enum | Yes | `critical`, `high`, `medium`, `low` |

**Acceptance Criterion** (nested, multiple):
| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string | Yes | Criterion identifier (e.g., `AC-001`) |
| `description` | string | Yes | Testable criterion |
| `source-ref` | string | No | Source extraction that informed this |

**Traceability** (nested):
| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `business-rules` | string[] | No | Referenced BusinessRule IDs |
| `workflows` | string[] | No | Referenced Workflow IDs |
| `ui-components` | string[] | No | Referenced UIComponent IDs |
| `database-ops` | string[] | No | Referenced DatabaseInteraction IDs |

**XML Element**: `<user-story>`

---

### ClarificationItem

Ambiguous code element pending user resolution.

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string | Yes | Unique identifier (e.g., `CLR-001`) |
| `type` | enum | Yes | `business-logic`, `data-type`, `naming`, `relationship`, `behavior` |
| `question` | string | Yes | What needs clarification |
| `context` | string | Yes | Code context showing ambiguity |
| `status` | enum | Yes | `pending`, `resolved`, `deferred` |
| `options` | string[] | No | Possible interpretations |
| `resolution` | string | No | User's decision |
| `resolved-at` | datetime | No | When resolved |

**Source Reference** (nested): Same as BusinessRule

**Relationships**:
- Associated with `SourceFile`
- May affect `BusinessRule`, `Workflow`, etc.

**XML Element**: `<clarification>`

---

### AnalysisCheckpoint

Progress state for resumable analysis.

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string | Yes | Checkpoint identifier |
| `project-id` | string | Yes | Associated project |
| `created` | datetime | Yes | Checkpoint timestamp |
| `phase` | enum | Yes | `inventory`, `extraction`, `generation` |
| `total-files` | integer | Yes | Total files in project |
| `completed-files` | integer | Yes | Files fully analyzed |
| `pending-files` | integer | Yes | Files remaining |
| `current-file` | string | No | File in progress |
| `current-position` | string | No | Position in current file |

**Extraction Status** (nested):
| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `type` | string | Yes | Extraction type |
| `status` | enum | Yes | `not-started`, `in-progress`, `completed` |
| `count` | integer | No | Items extracted |

**XML Element**: `<checkpoint>`

---

### AnalysisLog

Transparency record for debugging and audit.

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `timestamp` | datetime | Yes | When logged |
| `file` | string | Yes | File being analyzed |
| `action` | enum | Yes | `analyze`, `extract`, `generate`, `clarify` |
| `duration-ms` | integer | No | Operation duration |

**Decision** (nested, multiple):
| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `type` | string | Yes | Decision category |
| `value` | string | Yes | Decision made |
| `confidence` | enum | No | Confidence level |

**Reasoning** (nested):
| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `text` | string | Yes | LLM reasoning explanation |

**XML Element**: `<log-entry>`

---

## Entity Relationships Diagram

```
┌─────────────────┐
│ AnalysisProject │
└────────┬────────┘
         │ has many
         ▼
┌─────────────────┐      generates      ┌───────────────────┐
│   SourceFile    │─────────────────────▶│ GeneratedUserStory│
└────────┬────────┘                      └───────────────────┘
         │ extracts                               ▲
         ├──────────────────┬──────────────┬─────┴─────┐
         ▼                  ▼              ▼           │
┌─────────────────┐ ┌───────────────┐ ┌──────────┐    │
│  BusinessRule   │ │DatabaseInter- │ │UIComponent│    │
│                 │ │action         │ │          │    │
└────────┬────────┘ └───────┬───────┘ └────┬─────┘    │
         │                  │              │          │
         │ references       │ references   │ triggers │
         ▼                  ▼              ▼          │
┌─────────────────┐                 ┌──────────┐     │
│   DataEntity    │◀────────────────│ Workflow │─────┘
└─────────────────┘                 └──────────┘

Supporting Entities:
┌─────────────────┐  ┌───────────────────┐  ┌─────────────┐
│ClarificationItem│  │AnalysisCheckpoint │  │ AnalysisLog │
└─────────────────┘  └───────────────────┘  └─────────────┘
```

---

## State Transitions

### SourceFile.analysis-status

```
pending ──▶ in-progress ──▶ completed
    │            │
    │            └──▶ error
    │
    └──▶ skipped (via exclusion pattern)
```

### ClarificationItem.status

```
pending ──▶ resolved (user answered)
    │
    └──▶ deferred (user chose to skip)
```

### AnalysisProject.status

```
not-started ──▶ in-progress ──▶ completed
                    │
                    └──▶ paused (checkpoint saved)
                            │
                            └──▶ in-progress (resumed)
```

---

## Validation Rules

1. **SourceFile.path** must be unique within project
2. **BusinessRule.id** must be unique across all extractions
3. **Workflow.step.sequence** must be consecutive starting at 1
4. **GeneratedUserStory** must have at least one traceability link
5. **DataEntity** relationships must reference existing entities
6. **AnalysisCheckpoint.completed-files + pending-files = total-files**
7. **Confidence** levels must be one of: `high`, `medium`, `low`
