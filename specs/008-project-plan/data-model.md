# Data Model: Project Plan Command

**Feature**: 008-project-plan
**Date**: 2026-02-20

## Entities

### ProjectPlan

The markdown file at `.reforge/memory/project-plan.md`.

| Field | Type | Description |
|-------|------|-------------|
| project_name | string | From config.json or project-context.md |
| created_date | date (YYYY-MM-DD) | When the plan was first created |
| last_updated | date (YYYY-MM-DD) | Updated on every modification |
| sections | Section[] | Ordered list of plan sections |

**Lifecycle**: Created → Updated (add items, mark completions) → All Complete

### Section

A named group of plan items. Three section types exist.

| Field | Type | Description |
|-------|------|-------------|
| name | string | Section heading (e.g., "Setup", "Business Rules", "Custom Tasks") |
| type | enum | `setup`, `workflow_group`, `custom` |
| items | PlanItem[] | Ordered list of checklist items |

**Section types**:
- `setup`: Fixed section containing init, analyze, profile items
- `workflow_group`: One per extraction type, containing the 7-step pipeline
- `custom`: Optional section for user-defined tasks

### PlanItem

A single checkbox entry in the plan.

| Field | Type | Description |
|-------|------|-------------|
| description | string | Human-readable task description (editable by user) |
| tag | string | Machine-readable identifier: `reforge:<command>[:<type>]` |
| completed | boolean | Whether the checkbox is checked |
| completed_date | date or null | YYYY-MM-DD when completed, null if pending |

**Uncompleted format**: `- [ ] <description> <!-- reforge:<command>[:<type>] -->`
**Completed format**: `- [x] <description> <!-- reforge:<command>[:<type>] --> *(completed: YYYY-MM-DD)*`

**Identity**: Each PlanItem is uniquely identified by its `tag`. No two items in the same plan file may share a tag.

### Tag

The machine-readable identifier embedded as an HTML comment.

| Component | Required | Description |
|-----------|----------|-------------|
| prefix | yes | Always `reforge` |
| command | yes | The Reforge command verb (e.g., `init`, `extract`, `audit`, `audit-generated`, `fix-generated`, `custom`) |
| type | conditional | Extraction type slug (e.g., `business-rules`, `database`). Required for workflow group items and custom items. Omitted for setup items. |

**Pattern**: `<!-- reforge:<command>[:<type>] -->`

**Valid tag examples**:
- `<!-- reforge:init -->`
- `<!-- reforge:extract:business-rules -->`
- `<!-- reforge:audit-generated:ui -->`
- `<!-- reforge:custom:review-architecture -->`

## Relationships

```
ProjectPlan
  ├── Section (setup, 1)
  │     ├── PlanItem (init)
  │     ├── PlanItem (analyze)
  │     └── PlanItem (profile)
  ├── Section (workflow_group, 0..N)
  │     ├── PlanItem (extract:<type>)
  │     ├── PlanItem (clarify:<type>)
  │     ├── PlanItem (audit:<type>)
  │     ├── PlanItem (fix:<type>)
  │     ├── PlanItem (generate:<type>)
  │     ├── PlanItem (audit-generated:<type>)
  │     └── PlanItem (fix-generated:<type>)
  └── Section (custom, 0..1)
        └── PlanItem (custom:<slug>, 0..N)
```

## State Transitions

### PlanItem States

```
[ ] (pending) ──── command completes successfully ───→ [x] (completed)
                                                         + *(completed: YYYY-MM-DD)*
```

Items move in one direction only: pending → completed. There is no uncomplete operation via commands (users may manually edit the file to uncheck).

### ProjectPlan Lifecycle

```
Does not exist ──── /reforge.plan ───→ Created (with items)
                                          │
                            /reforge.plan "add ..." ───→ Updated (new items appended)
                                          │
                        command completion (Step 0.7) ──→ Updated (item checked)
                                          │
                           all items checked ──→ Complete (100%)
```

## Command Tag Derivation Rules

Each command derives its plan tag(s) from its arguments:

| Command Invocation | Derived Tag(s) |
|--------------------|----------------|
| `/reforge.init` | `reforge:init` |
| `/reforge.analyze` | `reforge:analyze` |
| `/reforge.profile` | `reforge:profile` |
| `/reforge.extract business-rules` | `reforge:extract:business-rules` |
| `/reforge.clarify --category business-rules` | `reforge:clarify:business-rules` |
| `/reforge.clarify` (no category) | None — skip plan update |
| `/reforge.audit business-rules` (extractions) | `reforge:audit:business-rules` |
| `/reforge.audit business-rules` (generated output) | `reforge:audit-generated:business-rules` |
| `/reforge.audit` (all types) | `reforge:audit:<type>` and/or `reforge:audit-generated:<type>` for each audited type, based on target |
| `/reforge.fix --type business-rules` (extractions) | `reforge:fix:business-rules` |
| `/reforge.fix --type business-rules` (generated output) | `reforge:fix-generated:business-rules` |
| `/reforge.fix` (all types) | `reforge:fix:<type>` and/or `reforge:fix-generated:<type>` for each fixed type, based on target |
| `/reforge.generate <format> --scope business-rules` | `reforge:generate:business-rules` |
| `/reforge.generate <format>` (no scope) | `reforge:generate:<type>` for each type with available extractions |
| `/reforge.reanalyze` | `reforge:analyze` (same artifact) |
| `/reforge.status` | None — reads plan for display only |
| `/reforge.plan` | N/A — manages the plan file directly |

## Extraction Type Slugs

Standard extraction types and their plan slugs:

| Extraction Type | Slug | Workflow Group Heading |
|-----------------|------|-----------------------|
| Business Rules | `business-rules` | `## Business Rules` |
| Database | `database` | `## Database` |
| UI Flows | `ui` | `## UI Flows` |
| Workflows | `workflows` | `## Workflows` |
| (user-defined) | `<user-slug>` | `## <User Title>` |

User-defined extraction types are accepted as-is. The slug is derived by lowercasing and hyphenating the user's declared type name.

**Classification rule**: If the user declares an item as an extraction type (e.g., "add performance-metrics extraction"), it gets a full workflow group with the 7-step pipeline. If the user declares a non-extraction task (e.g., "add review architecture with team"), it goes in the Custom Tasks section as a single item. The `/reforge.plan` command infers classification from the user's phrasing — extraction-related language ("extract", "audit", "generate") triggers a workflow group; other language triggers a custom task.

## Validation Rules

1. **Tag uniqueness**: No two PlanItems may share the same tag within a plan file
2. **Section ordering**: Setup section always first, Custom Tasks always last, workflow groups in between (user-declared order)
3. **Completion integrity**: A `- [x]` item MUST have a `*(completed: YYYY-MM-DD)*` suffix
4. **Metadata currency**: `Last Updated` MUST reflect the most recent modification date
5. **Markdown validity**: Plan file MUST be valid markdown renderable by any standard parser
