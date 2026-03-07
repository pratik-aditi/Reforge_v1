# Codebase Metrics Schema

> Defines the structure for quantitative codebase metrics (`codebase-metrics.xml`)

## Overview

The codebase metrics schema captures quantitative measurements computed by `/reforge.metrics` — complexity scores, coupling and cohesion metrics, tech debt ratios, and lines-of-code counts per module. It uses the [Common Extraction Schema](./common-schema.md) for shared structural elements.

**Note**: This schema does NOT have an XSD. Metrics are derived computations, not direct extractions, and their structure may vary by project.

## Common Elements

This schema extends the [Common Extraction Schema](./common-schema.md), which defines shared structural elements used across all extraction types:

- **Root attributes**: `project-id`, `version`, `schema-version`, `generated`, `xmlns`
- **Metadata container**: `<metadata>` with `<total-count>`, `<confidence-distribution>`, `<extraction-timestamp>`
- **Source references**: Canonical `<source>` format with `file`, `line-start`, `line-end` attributes
- **Confidence vocabulary**: `high`, `medium`, `low` enumeration

See `common-schema.md` for complete definitions. Elements defined there MUST NOT be redefined in this schema.

## Root Element

```xml
<codebase-metrics xmlns="http://reforge.dev/schema/extraction"
        project-id="my-app" version="1.0.0"
        schema-version="1.0.0"
        generated="2024-01-15T10:30:00Z">
  <metadata>...</metadata>
  <project-summary>...</project-summary>
  <module-metrics>...</module-metrics>
</codebase-metrics>
```

### Attributes

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `xmlns` | URI | Yes | Must be `http://reforge.dev/schema/extraction` |
| `project-id` | string | Yes | Reference to analysis project |
| `version` | string | Yes | Extraction version (semver) |
| `schema-version` | string | Yes | Common schema version (initial: `1.0.0`) |
| `generated` | dateTime | Yes | Metrics computation timestamp (ISO-8601) |

> Root attributes and `<metadata>` are defined by the [Common Extraction Schema](./common-schema.md). The `<metadata>` element is required as the first child of the root element. The metadata `<total-count>` equals the number of modules analyzed.

## Elements

### `<project-summary>`

Aggregate project-level metrics.

```xml
<project-summary total-modules="12" total-loc="45000" avg-complexity="6.2"
                 avg-coupling="0.35" avg-cohesion="0.72" avg-tech-debt-ratio="0.15"/>
```

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `total-modules` | integer | Yes | Total number of modules analyzed |
| `total-loc` | integer | Yes | Total lines of code across all modules |
| `avg-complexity` | decimal | Yes | Average cyclomatic complexity across modules |
| `avg-coupling` | decimal | Yes | Average coupling score (0.0-1.0) |
| `avg-cohesion` | decimal | Yes | Average cohesion score (0.0-1.0) |
| `avg-tech-debt-ratio` | decimal | Yes | Average tech debt ratio across modules |

### `<module-metrics>`

Container for per-module metric items.

```xml
<module-metrics count="12">
  <module>...</module>
</module-metrics>
```

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `count` | integer | Yes | Number of module items in this container |

### `<module>`

Individual module metrics with source traceability.

```xml
<module name="OrderService" path="src/service/" confidence="high">
  <complexity cyclomatic="12" cognitive="8" max-nesting="4"/>
  <coupling afferent="5" efferent="8" instability="0.62"/>
  <cohesion score="0.75" type="functional"/>
  <tech-debt-ratio value="0.18" issue-count="3" effort-hours="24"/>
  <lines-of-code total="1200" code="950" comment="150" blank="100"/>
  <source file="src/service/OrderService.java" line-start="1" line-end="1200"/>
</module>
```

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | string | Yes | Module or component name |
| `path` | string | Yes | Relative directory path of the module |
| `confidence` | ConfidenceType | Yes | Confidence in computed metrics |

### `<complexity>`

Complexity metrics for a module.

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `cyclomatic` | integer | Yes | Cyclomatic complexity (decision points + 1) |
| `cognitive` | integer | No | Cognitive complexity (nesting-weighted) |
| `max-nesting` | integer | No | Maximum nesting depth in the module |

### `<coupling>`

Coupling metrics for a module.

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `afferent` | integer | Yes | Number of modules that depend on this module |
| `efferent` | integer | Yes | Number of modules this module depends on |
| `instability` | decimal | Yes | Instability ratio: efferent / (afferent + efferent). Range 0.0-1.0 |

### `<cohesion>`

Cohesion metrics for a module.

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `score` | decimal | Yes | Cohesion score (0.0-1.0, higher is better) |
| `type` | string | No | Cohesion type: `functional`, `sequential`, `communicational`, `procedural`, `temporal`, `logical`, `coincidental` |

### `<tech-debt-ratio>`

Technical debt metrics for a module.

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `value` | decimal | Yes | Tech debt ratio (remediation cost / development cost). Range 0.0-1.0+ |
| `issue-count` | integer | Yes | Number of issues contributing to tech debt |
| `effort-hours` | integer | No | Estimated hours to remediate tech debt |

### `<lines-of-code>`

Line count breakdown for a module.

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `total` | integer | Yes | Total lines in the module |
| `code` | integer | Yes | Lines of executable code |
| `comment` | integer | Yes | Lines of comments |
| `blank` | integer | Yes | Blank lines |

### `<source>`

Source code location for the module. Uses the canonical format defined in the [Common Extraction Schema](./common-schema.md#source-references).

## Example Output

```xml
<?xml version="1.0" encoding="UTF-8"?>
<codebase-metrics xmlns="http://reforge.dev/schema/extraction"
        project-id="ecommerce-legacy" version="1.0.0"
        schema-version="1.0.0"
        generated="2024-01-15T10:30:00Z">

  <metadata>
    <total-count>2</total-count>
    <confidence-distribution>
      <high>2</high>
      <medium>0</medium>
      <low>0</low>
    </confidence-distribution>
    <extraction-timestamp>2024-01-15T10:30:00Z</extraction-timestamp>
  </metadata>

  <project-summary total-modules="2" total-loc="2100" avg-complexity="10.0"
                   avg-coupling="0.55" avg-cohesion="0.70" avg-tech-debt-ratio="0.16"/>

  <module-metrics count="2">
    <module name="OrderService" path="src/service/" confidence="high">
      <complexity cyclomatic="12" cognitive="8" max-nesting="4"/>
      <coupling afferent="5" efferent="8" instability="0.62"/>
      <cohesion score="0.75" type="functional"/>
      <tech-debt-ratio value="0.18" issue-count="3" effort-hours="24"/>
      <lines-of-code total="1200" code="950" comment="150" blank="100"/>
      <source file="src/service/OrderService.java" line-start="1" line-end="1200"/>
    </module>
    <module name="PaymentGateway" path="src/payment/" confidence="high">
      <complexity cyclomatic="8" cognitive="5" max-nesting="3"/>
      <coupling afferent="3" efferent="6" instability="0.67"/>
      <cohesion score="0.65" type="communicational"/>
      <tech-debt-ratio value="0.14" issue-count="2" effort-hours="16"/>
      <lines-of-code total="900" code="720" comment="100" blank="80"/>
      <source file="src/payment/PaymentGateway.java" line-start="1" line-end="900"/>
    </module>
  </module-metrics>

</codebase-metrics>
```

## Related Schemas

- [Common Schema](./common-schema.md) — Shared elements (root attributes, metadata, source references, confidence)
- [issues.md](./issues.md) — Issues feeding into tech debt ratio computation
- [dependencies.md](./dependencies.md) — Dependency data feeding into coupling metrics
- [call-sites.md](./call-sites.md) — Call relationships feeding into cohesion metrics
