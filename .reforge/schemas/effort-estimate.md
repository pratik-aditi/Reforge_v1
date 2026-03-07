# Effort Estimate Schema

> Defines the structure for three-point effort estimation output (`effort-estimate.xml`)

## Overview

The effort estimate schema captures per-module effort estimates produced by `/reforge.estimate`. It uses three-point estimation (optimistic, most-likely, pessimistic) with complexity multipliers and risk factors to produce weighted expected effort values.

## Common Elements

This schema extends the [Common Extraction Schema](./common-schema.md), which defines shared structural elements used across all extraction types:

- **Root attributes**: `project-id`, `version`, `schema-version`, `generated`, `xmlns`
- **Metadata container**: `<metadata>` with `<total-count>`, `<confidence-distribution>`, `<extraction-timestamp>`
- **Source references**: Canonical `<source>` format with `file`, `line-start`, `line-end` attributes
- **Confidence vocabulary**: `high`, `medium`, `low` enumeration
- **ID patterns**: `EST-{CATEGORY}-{SEQUENCE}`

See `common-schema.md` for complete definitions. Elements defined there MUST NOT be redefined in this schema.

## Root Element

```xml
<effort-estimate xmlns="http://reforge.dev/schema/extraction"
                 project-id="my-app" version="1.0.0"
                 schema-version="1.0.0"
                 generated="2024-01-15T10:30:00Z">
  <metadata>...</metadata>
  <estimates>...</estimates>
  <summary>...</summary>
</effort-estimate>
```

### Attributes

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `xmlns` | URI | Yes | Must be `http://reforge.dev/schema/extraction` |
| `project-id` | string | Yes | Reference to analysis project |
| `version` | string | Yes | Extraction version (semver) |
| `schema-version` | string | Yes | Common schema version (initial: `1.0.0`) |
| `generated` | dateTime | Yes | Extraction timestamp (ISO-8601) |

> Root attributes and `<metadata>` are defined by the [Common Extraction Schema](./common-schema.md). The `<metadata>` element is required as the first child of the root element. The metadata `<total-count>` equals the count of estimate items.

## Elements

### `<estimates>`

Container for per-module effort estimate items.

```xml
<estimates count="12">
  <estimate>...</estimate>
</estimates>
```

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `count` | integer | Yes | Number of estimate items in this container |

### `<estimate>`

Individual module effort estimate with three-point values and complexity assessment.

```xml
<estimate id="EST-SVC-001" module="OrderService" confidence="high">
  <description>Order processing service with payment integration</description>
  <optimistic unit="person-days">5</optimistic>
  <most-likely unit="person-days">10</most-likely>
  <pessimistic unit="person-days">20</pessimistic>
  <expected unit="person-days">10.8</expected>
  <complexity-multiplier value="1.3" rationale="High coupling with 4 external integrations"/>
  <risk-factors>
    <risk-factor severity="high">Payment gateway API migration required</risk-factor>
    <risk-factor severity="medium">No existing test coverage</risk-factor>
  </risk-factors>
  <dependencies-count internal="3" external="2"/>
  <source file="src/service/OrderService.java" line-start="1" line-end="450"/>
</estimate>
```

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string | Yes | Unique estimate identifier (`EST-{CATEGORY}-{SEQUENCE}`) |
| `module` | string | Yes | Module or component name being estimated |
| `confidence` | ConfidenceType | Yes | Estimation confidence level |

### `<description>`

Brief description of the module's purpose and scope relevant to the estimate.

### `<optimistic>`

Best-case effort estimate assuming no complications.

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `unit` | string | Yes | Effort unit: `person-hours`, `person-days`, `person-weeks` |

### `<most-likely>`

Most probable effort estimate based on typical conditions.

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `unit` | string | Yes | Effort unit (must match `<optimistic>`) |

### `<pessimistic>`

Worst-case effort estimate accounting for complications and unknowns.

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `unit` | string | Yes | Effort unit (must match `<optimistic>`) |

### `<expected>`

Weighted average using PERT formula: `(O + 4*M + P) / 6`. Computed by the agent at generation time.

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `unit` | string | Yes | Effort unit (must match `<optimistic>`) |

### `<complexity-multiplier>`

Multiplier applied to the expected effort based on module complexity factors.

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `value` | decimal | Yes | Multiplier value (e.g., `1.0` = baseline, `1.5` = 50% more complex) |
| `rationale` | string | Yes | Explanation for the chosen multiplier |

### `<risk-factors>`

Container for risk factors that affect the estimate.

### `<risk-factor>`

Individual risk factor that may impact effort.

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `severity` | string | Yes | Risk severity: `high`, `medium`, `low` |

### `<dependencies-count>`

Count of module dependencies affecting estimation complexity.

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `internal` | integer | Yes | Number of internal module dependencies |
| `external` | integer | Yes | Number of external/third-party dependencies |

### `<source>`

Source code location of the module being estimated. Uses the canonical format defined in the [Common Extraction Schema](./common-schema.md#source-references).

### `<summary>`

Aggregated estimation summary for the entire project.

```xml
<summary>
  <total-effort unit="person-days">185.4</total-effort>
  <total-modules>12</total-modules>
  <methodology>Three-point (PERT) estimation with complexity multipliers derived from dependency count, issue density, and coupling analysis</methodology>
  <effort-by-confidence>
    <high unit="person-days">120.0</high>
    <medium unit="person-days">50.4</medium>
    <low unit="person-days">15.0</low>
  </effort-by-confidence>
</summary>
```

| Element | Type | Required | Description |
|---------|------|----------|-------------|
| `total-effort` | decimal | Yes | Sum of all expected efforts (with `unit` attribute) |
| `total-modules` | integer | Yes | Count of modules estimated |
| `methodology` | string | Yes | Description of estimation methodology used |
| `effort-by-confidence` | container | Yes | Effort breakdown by confidence level |

## Example Output

```xml
<?xml version="1.0" encoding="UTF-8"?>
<effort-estimate xmlns="http://reforge.dev/schema/extraction"
                 project-id="ecommerce-legacy" version="1.0.0"
                 schema-version="1.0.0"
                 generated="2024-01-15T10:30:00Z">

  <metadata>
    <total-count>2</total-count>
    <confidence-distribution>
      <high>1</high>
      <medium>1</medium>
      <low>0</low>
    </confidence-distribution>
    <extraction-timestamp>2024-01-15T10:30:00Z</extraction-timestamp>
  </metadata>

  <estimates count="2">
    <estimate id="EST-SVC-001" module="OrderService" confidence="high">
      <description>Order processing service with payment integration and inventory management</description>
      <optimistic unit="person-days">5</optimistic>
      <most-likely unit="person-days">10</most-likely>
      <pessimistic unit="person-days">20</pessimistic>
      <expected unit="person-days">10.8</expected>
      <complexity-multiplier value="1.3" rationale="High coupling with 4 external integrations"/>
      <risk-factors>
        <risk-factor severity="high">Payment gateway API migration required</risk-factor>
        <risk-factor severity="medium">No existing test coverage</risk-factor>
      </risk-factors>
      <dependencies-count internal="3" external="2"/>
      <source file="src/service/OrderService.java" line-start="1" line-end="450"/>
    </estimate>

    <estimate id="EST-REPO-001" module="CustomerRepository" confidence="medium">
      <description>Customer data access layer with legacy SQL queries</description>
      <optimistic unit="person-days">3</optimistic>
      <most-likely unit="person-days">6</most-likely>
      <pessimistic unit="person-days">12</pessimistic>
      <expected unit="person-days">6.5</expected>
      <complexity-multiplier value="1.1" rationale="Moderate complexity with well-defined interfaces"/>
      <risk-factors>
        <risk-factor severity="medium">Legacy stored procedures require manual review</risk-factor>
      </risk-factors>
      <dependencies-count internal="2" external="1"/>
      <source file="src/repository/CustomerRepository.java" line-start="1" line-end="200"/>
    </estimate>
  </estimates>

  <summary>
    <total-effort unit="person-days">17.3</total-effort>
    <total-modules>2</total-modules>
    <methodology>Three-point (PERT) estimation with complexity multipliers derived from dependency count, issue density, and coupling analysis</methodology>
    <effort-by-confidence>
      <high unit="person-days">10.8</high>
      <medium unit="person-days">6.5</medium>
      <low unit="person-days">0</low>
    </effort-by-confidence>
  </summary>

</effort-estimate>
```

## Related Schemas

- [Common Schema](./common-schema.md) — Shared elements (root attributes, metadata, source references, confidence)
- [architecture.md](./architecture.md) — Architectural components informing module boundaries
- [dependencies.md](./dependencies.md) — Dependency graphs used for complexity assessment
- [issues.md](./issues.md) — Issues and technical debt affecting risk factors
