# Data Dictionary Template

> Template for generating data dictionary documentation from database extractions

## Template Variables

| Variable | Source | Description |
|----------|--------|-------------|
| `{{project.id}}` | Analysis | Project identifier |
| `{{project.name}}` | Analysis | Project name |
| `{{generated}}` | System | Generation timestamp |
| `{{entities}}` | Database extraction | Array of data entities |
| `{{relationships}}` | Database extraction | Array of relationships |

## Entity Variables

| Variable | Source | Description |
|----------|--------|-------------|
| `{{entity.id}}` | Extraction | Entity identifier |
| `{{entity.name}}` | Extraction | Table/entity name |
| `{{entity.type}}` | Extraction | table/view/entity/dto |
| `{{entity.source_type}}` | Extraction | ddl/orm/inferred/config |
| `{{entity.confidence}}` | Extraction | high/medium/low |
| `{{entity.columns}}` | Extraction | Array of columns |
| `{{entity.source}}` | Extraction | Source reference |

## Markdown Output Template

```markdown
# Data Dictionary: {{project.name}}

> Generated: {{generated}}
> Source: `/reforge.extract database`

## Overview

| Metric | Value |
|--------|-------|
| Total Entities | {{entities.length}} |
| Total Relationships | {{relationships.length}} |
| Discovery Sources | DDL, ORM, Inferred |

---

## Entities

{{#each entities}}
### {{this.name}}

| Property | Value |
|----------|-------|
| ID | `{{this.id}}` |
| Type | {{this.type}} |
| Source | {{this.source_type}} |
| Confidence | {{this.confidence}} |
| Location | `{{this.source.file}}:{{this.source.line_start}}-{{this.source.line_end}}` |

#### Columns

| Column | Type | Nullable | PK | FK |
|--------|------|----------|----|----|
{{#each this.columns}}
| `{{this.name}}` | {{this.data_type}} | {{#if this.nullable}}Yes{{else}}No{{/if}} | {{#if this.primary_key}}✓{{else}}{{/if}} | {{#if this.foreign_key}}`{{this.foreign_key}}`{{else}}{{/if}} |
{{/each}}

---

{{/each}}

## Relationships

| From | → | To | Type |
|------|---|-----|------|
{{#each relationships}}
| `{{this.from_entity}}.{{this.from_column}}` | → | `{{this.to_entity}}.{{this.to_column}}` | {{this.type}} |
{{/each}}

## Entity Relationship Diagram

See `diagrams/erd.plantuml` or `diagrams/erd.mermaid` for visual representation.
```

## Column Documentation Format

Each column should include:

### Standard Fields

| Field | Description |
|-------|-------------|
| Name | Column identifier |
| Type | SQL data type or language type |
| Nullable | Whether NULL values allowed |
| Primary Key | Is part of primary key |
| Foreign Key | References another table.column |

### Extended Documentation (when available)

| Field | Description |
|-------|-------------|
| Description | Human-readable description |
| Default | Default value if any |
| Constraints | CHECK constraints, UNIQUE |
| Index | Part of an index |
| Sample Values | Example data |

## Relationship Types

| Type | Symbol | Description |
|------|--------|-------------|
| one-to-one | 1:1 | Single record maps to single record |
| one-to-many | 1:N | Single record maps to multiple records |
| many-to-many | M:N | Multiple records map to multiple records |

## Example Output

```markdown
# Data Dictionary: E-Commerce Legacy

> Generated: 2024-01-15T10:30:00Z
> Source: `/reforge.extract database`

## Overview

| Metric | Value |
|--------|-------|
| Total Entities | 5 |
| Total Relationships | 4 |
| Discovery Sources | DDL, ORM |

---

## Entities

### orders

| Property | Value |
|----------|-------|
| ID | `E-001` |
| Type | table |
| Source | ddl |
| Confidence | high |
| Location | `db/schema.sql:10-25` |

#### Columns

| Column | Type | Nullable | PK | FK |
|--------|------|----------|----|----|
| `id` | bigint | No | ✓ |  |
| `customer_id` | bigint | No |  | `customers.id` |
| `total` | decimal(10,2) | No |  |  |
| `status` | varchar(20) | No |  |  |
| `created_at` | timestamp | No |  |  |

---

### customers

| Property | Value |
|----------|-------|
| ID | `E-002` |
| Type | table |
| Source | ddl |
| Confidence | high |
| Location | `db/schema.sql:1-8` |

#### Columns

| Column | Type | Nullable | PK | FK |
|--------|------|----------|----|----|
| `id` | bigint | No | ✓ |  |
| `name` | varchar(100) | No |  |  |
| `email` | varchar(255) | No |  |  |

---

## Relationships

| From | → | To | Type |
|------|---|-----|------|
| `orders.customer_id` | → | `customers.id` | many-to-one |
| `order_items.order_id` | → | `orders.id` | many-to-one |
| `order_items.product_id` | → | `products.id` | many-to-one |

## Entity Relationship Diagram

See `diagrams/erd.plantuml` for visual representation.
```

## Notes for Agent

When generating data dictionaries:

1. **Group related entities** - Place related tables near each other
2. **Highlight foreign keys** - These define the relationship structure
3. **Note inferred entities** - Flag entities discovered from queries vs DDL
4. **Include sample queries** - Reference common interactions involving each entity
5. **Cross-reference business rules** - Note which rules reference which entities
