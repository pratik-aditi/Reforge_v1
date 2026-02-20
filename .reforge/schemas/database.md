# Database Schema

> Defines the structure for database interactions and data model (`database.xml`)

## Overview

The database schema captures data model entities and database interactions extracted by `/reforge.extract database`. It includes table/entity definitions, relationships, and SQL operations found in the codebase.

## Common Elements

This schema extends the [Common Extraction Schema](./common-schema.md), which defines shared structural elements used across all extraction types:

- **Root attributes**: `project-id`, `version`, `schema-version`, `generated`, `xmlns`
- **Metadata container**: `<metadata>` with `<total-count>`, `<confidence-distribution>`, `<extraction-timestamp>`
- **Source references**: Canonical `<source>` format with `file`, `line-start`, `line-end` attributes
- **Confidence vocabulary**: `high`, `medium`, `low` enumeration
- **ID patterns**: `DB-{CATEGORY}-{SEQUENCE}` (interactions), `E-{CATEGORY}-{SEQUENCE}` (entities)

See `common-schema.md` for complete definitions. Elements defined there MUST NOT be redefined in this schema.

## Root Element

```xml
<database xmlns="http://reforge.dev/schema/extraction"
          project-id="my-app" version="1.0.0"
          schema-version="1.0.0"
          generated="2024-01-15T10:30:00Z">
  <metadata>...</metadata>
  <data-model>...</data-model>
  <interactions>...</interactions>
</database>
```

### Attributes

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `xmlns` | URI | Yes | Must be `http://reforge.dev/schema/extraction` |
| `project-id` | string | Yes | Reference to analysis project |
| `version` | string | Yes | Extraction version (semver) |
| `schema-version` | string | Yes | Common schema version (initial: `1.0.0`) |
| `generated` | dateTime | Yes | Extraction timestamp (ISO-8601) |

> Root attributes and `<metadata>` are defined by the [Common Extraction Schema](./common-schema.md). The `<metadata>` element is required as the first child of the root element.

## Elements

### `<data-model>`

Contains discovered entities and their relationships.

```xml
<data-model entity-count="15">
  <entity>...</entity>
  <relationship>...</relationship>
</data-model>
```

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `entity-count` | integer | Yes | Total entities discovered |

### `<entity>`

A data entity (table, view, ORM class, or DTO).

```xml
<entity id="E-001" name="orders" type="table" source-type="ddl" confidence="high">
  <column name="id" data-type="bigint" nullable="false" primary-key="true"/>
  <column name="customer_id" data-type="bigint" nullable="false" foreign-key="customers.id"/>
  <column name="total" data-type="decimal(10,2)" nullable="false"/>
  <column name="status" data-type="varchar(20)" nullable="false"/>
  <column name="created_at" data-type="timestamp" nullable="false"/>
  <source file="db/schema.sql" line-start="25" line-end="35"/>
</entity>
```

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string | Yes | Unique entity identifier |
| `name` | string | Yes | Entity/table name |
| `type` | EntityTypeEnum | Yes | Type of entity |
| `source-type` | SourceTypeEnum | Yes | How entity was discovered |
| `confidence` | ConfidenceType | Yes | Discovery confidence |

#### EntityTypeEnum

| Value | Description |
|-------|-------------|
| `table` | Database table |
| `view` | Database view |
| `entity` | ORM entity class |
| `dto` | Data transfer object |

#### SourceTypeEnum

| Value | Description |
|-------|-------------|
| `ddl` | From DDL/SQL schema files |
| `orm` | From ORM annotations/mappings |
| `inferred` | Inferred from queries |
| `config` | From configuration files |

### `<column>`

Column definition within an entity.

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | string | Yes | Column name |
| `data-type` | string | Yes | Data type (SQL or language type) |
| `nullable` | boolean | No | Whether NULL is allowed |
| `primary-key` | boolean | No | Is primary key |
| `foreign-key` | string | No | Foreign key reference (table.column) |

### `<relationship>`

Relationship between entities.

```xml
<relationship from-entity="orders" from-column="customer_id"
              to-entity="customers" to-column="id" type="many-to-one"/>
```

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `from-entity` | string | Yes | Source entity name |
| `from-column` | string | Yes | Source column |
| `to-entity` | string | Yes | Target entity name |
| `to-column` | string | Yes | Target column |
| `type` | RelationshipTypeEnum | Yes | Relationship cardinality |

#### RelationshipTypeEnum

| Value | Description |
|-------|-------------|
| `one-to-one` | 1:1 relationship |
| `one-to-many` | 1:N relationship |
| `many-to-many` | M:N relationship |

### `<interactions>`

Collection of database operations found in code.

```xml
<interactions count="45">
  <interaction>...</interaction>
</interactions>
```

### `<interaction>`

Individual database operation.

```xml
<interaction id="DB-001" operation="SELECT" confidence="high">
  <sql>SELECT o.*, c.name FROM orders o JOIN customers c ON o.customer_id = c.id WHERE o.status = ?</sql>
  <tables>
    <table>orders</table>
    <table>customers</table>
  </tables>
  <columns>
    <column>orders.*</column>
    <column>customers.name</column>
  </columns>
  <context method="findOrdersWithCustomer" class="OrderRepository"/>
  <source file="src/repository/OrderRepository.java" line-start="45" line-end="52">
    <snippet>@Query("SELECT o.*, c.name FROM orders o...")</snippet>
  </source>
</interaction>
```

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string | Yes | Unique interaction identifier |
| `operation` | OperationType | Yes | SQL operation type |
| `confidence` | ConfidenceType | Yes | Extraction confidence |

#### OperationType

| Value | Description |
|-------|-------------|
| `SELECT` | Read operation |
| `INSERT` | Create operation |
| `UPDATE` | Update operation |
| `DELETE` | Delete operation |
| `DDL` | Schema modification |
| `CALL` | Stored procedure call |

### `<context>`

Execution context for the interaction.

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `method` | string | Yes | Method name |
| `class` | string | No | Class name |
| `trigger` | string | No | What triggers this operation |

## Example Output

```xml
<?xml version="1.0" encoding="UTF-8"?>
<database xmlns="http://reforge.dev/schema/extraction"
          project-id="ecommerce-legacy" version="1.0.0"
          schema-version="1.0.0"
          generated="2024-01-15T10:30:00Z">

  <metadata>
    <total-count>3</total-count>
    <confidence-distribution>
      <high>3</high>
      <medium>0</medium>
      <low>0</low>
    </confidence-distribution>
    <extraction-timestamp>2024-01-15T10:30:00Z</extraction-timestamp>
  </metadata>

  <data-model entity-count="2">
    <entity id="E-001" name="orders" type="table" source-type="ddl" confidence="high">
      <column name="id" data-type="bigint" nullable="false" primary-key="true"/>
      <column name="customer_id" data-type="bigint" nullable="false" foreign-key="customers.id"/>
      <column name="total" data-type="decimal(10,2)" nullable="false"/>
      <source file="db/schema.sql" line-start="10" line-end="20"/>
    </entity>

    <entity id="E-002" name="customers" type="table" source-type="ddl" confidence="high">
      <column name="id" data-type="bigint" nullable="false" primary-key="true"/>
      <column name="name" data-type="varchar(100)" nullable="false"/>
      <column name="email" data-type="varchar(255)" nullable="false"/>
      <source file="db/schema.sql" line-start="1" line-end="8"/>
    </entity>

    <relationship from-entity="orders" from-column="customer_id"
                  to-entity="customers" to-column="id" type="many-to-one"/>
  </data-model>

  <interactions count="1">
    <interaction id="DB-001" operation="SELECT" confidence="high">
      <sql>SELECT * FROM orders WHERE customer_id = ?</sql>
      <tables>
        <table>orders</table>
      </tables>
      <context method="findByCustomerId" class="OrderRepository"/>
      <source file="src/repository/OrderRepository.java" line-start="25" line-end="30"/>
    </interaction>
  </interactions>

</database>
```

## Related Schemas

- [Common Schema](./common-schema.md) — Shared elements (root attributes, metadata, source references, confidence)
- [analysis.md](./analysis.md) — Codebase inventory
- [business-rules.md](./business-rules.md) — Rules often reference entities
- [workflows.md](./workflows.md) — Workflows include data access steps

## Contract Reference

Based on: `specs/001-legacy-analyzer/contracts/database.xsd`
