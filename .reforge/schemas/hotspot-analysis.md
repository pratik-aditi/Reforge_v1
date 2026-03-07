# Hotspot Analysis Schema

> Defines the structure for risk heatmap analysis (`hotspot-analysis.xml`)

## Overview

The hotspot analysis schema captures composite risk scores computed by `/reforge.hotspot` — combining complexity, dependency density, issue density, and business rule concentration into a ranked risk heatmap. It uses the [Common Extraction Schema](./common-schema.md) for shared structural elements.

## Common Elements

This schema extends the [Common Extraction Schema](./common-schema.md), which defines shared structural elements used across all extraction types:

- **Root attributes**: `project-id`, `version`, `schema-version`, `generated`, `xmlns`
- **Metadata container**: `<metadata>` with `<total-count>`, `<confidence-distribution>`, `<extraction-timestamp>`
- **Source references**: Canonical `<source>` format with `file`, `line-start`, `line-end` attributes
- **Confidence vocabulary**: `high`, `medium`, `low` enumeration
- **ID patterns**: `HOT-{CATEGORY}-{SEQUENCE}` (hotspot findings)

See `common-schema.md` for complete definitions. Elements defined there MUST NOT be redefined in this schema.

## Root Element

```xml
<hotspot-analysis xmlns="http://reforge.dev/schema/extraction"
        project-id="my-app" version="1.0.0"
        schema-version="1.0.0"
        generated="2024-01-15T10:30:00Z">
  <metadata>...</metadata>
  <scoring-weights>...</scoring-weights>
  <hotspots>...</hotspots>
</hotspot-analysis>
```

### Attributes

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `xmlns` | URI | Yes | Must be `http://reforge.dev/schema/extraction` |
| `project-id` | string | Yes | Reference to analysis project |
| `version` | string | Yes | Extraction version (semver) |
| `schema-version` | string | Yes | Common schema version (initial: `1.0.0`) |
| `generated` | dateTime | Yes | Analysis timestamp (ISO-8601) |

> Root attributes and `<metadata>` are defined by the [Common Extraction Schema](./common-schema.md). The `<metadata>` element is required as the first child of the root element. The metadata `<total-count>` equals the number of hotspot items.

## Elements

### `<scoring-weights>`

Documents the weights used to compute composite risk scores.

```xml
<scoring-weights>
  <weight factor="complexity" value="0.30"/>
  <weight factor="dependency" value="0.25"/>
  <weight factor="issue-density" value="0.25"/>
  <weight factor="business-rule-density" value="0.20"/>
</scoring-weights>
```

### `<weight>`

Individual scoring weight factor.

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `factor` | string | Yes | Factor name: `complexity`, `dependency`, `issue-density`, `business-rule-density` |
| `value` | decimal | Yes | Weight value (0.0-1.0). All weights must sum to 1.0 |

### `<hotspots>`

Container for ranked hotspot items.

```xml
<hotspots count="5" threshold="25">
  <hotspot>...</hotspot>
</hotspots>
```

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `count` | integer | Yes | Number of hotspot items in this container |
| `threshold` | integer | No | Minimum risk score threshold used for filtering (0-100) |

### `<hotspot>`

Individual hotspot with composite risk scoring and source traceability.

```xml
<hotspot id="HOT-SVC-001" name="OrderService" path="src/service/OrderService.java"
         risk-score="82" rank="1" confidence="high">
  <complexity-score value="90" cyclomatic="18" cognitive="12"/>
  <dependency-score value="75" afferent="8" efferent="12"/>
  <issue-density-score value="85" issue-count="7" lines-of-code="1200"/>
  <business-rule-count value="15"/>
  <rationale>High cyclomatic complexity (18) combined with high dependency fan-out (12) and dense issue concentration (7 issues in 1200 LOC) make this the highest-risk module for modernization.</rationale>
  <source file="src/service/OrderService.java" line-start="1" line-end="1200"/>
</hotspot>
```

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string | Yes | Unique hotspot identifier (`HOT-{CATEGORY}-{SEQUENCE}`) |
| `name` | string | Yes | Module or component name |
| `path` | string | Yes | Relative file or directory path |
| `risk-score` | integer | Yes | Composite risk score (0-100, higher = more risk) |
| `rank` | integer | Yes | Risk ranking (1 = highest risk) |
| `confidence` | ConfidenceType | Yes | Confidence in computed scores |

### `<complexity-score>`

Complexity contribution to the hotspot score.

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `value` | integer | Yes | Normalized complexity score (0-100) |
| `cyclomatic` | integer | No | Raw cyclomatic complexity value |
| `cognitive` | integer | No | Raw cognitive complexity value |

### `<dependency-score>`

Dependency contribution to the hotspot score.

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `value` | integer | Yes | Normalized dependency score (0-100) |
| `afferent` | integer | No | Number of incoming dependencies |
| `efferent` | integer | No | Number of outgoing dependencies |

### `<issue-density-score>`

Issue density contribution to the hotspot score.

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `value` | integer | Yes | Normalized issue density score (0-100) |
| `issue-count` | integer | No | Number of issues in this module |
| `lines-of-code` | integer | No | Lines of code in this module |

### `<business-rule-count>`

Count of business rules associated with this module.

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `value` | integer | Yes | Number of business rules in this module |

### `<rationale>`

Human-readable explanation of why this module is flagged as a hotspot.

### `<source>`

Source code location for the hotspot. Uses the canonical format defined in the [Common Extraction Schema](./common-schema.md#source-references).

## Hotspot Categories

| Category | Description | Examples |
|----------|-------------|----------|
| `SVC` | Service layer | Core business services, orchestrators |
| `CTL` | Controller layer | Request handlers, API endpoints |
| `DAL` | Data access layer | Repositories, DAOs, data mappers |
| `MDL` | Model layer | Domain models, entities |
| `UTL` | Utility | Shared utilities, helpers |
| `CFG` | Configuration | Config classes, bootstrapping |
| `INT` | Integration | External system integrations |

## Example Output

```xml
<?xml version="1.0" encoding="UTF-8"?>
<hotspot-analysis xmlns="http://reforge.dev/schema/extraction"
        project-id="ecommerce-legacy" version="1.0.0"
        schema-version="1.0.0"
        generated="2024-01-15T10:30:00Z">

  <metadata>
    <total-count>3</total-count>
    <confidence-distribution>
      <high>2</high>
      <medium>1</medium>
      <low>0</low>
    </confidence-distribution>
    <extraction-timestamp>2024-01-15T10:30:00Z</extraction-timestamp>
  </metadata>

  <scoring-weights>
    <weight factor="complexity" value="0.30"/>
    <weight factor="dependency" value="0.25"/>
    <weight factor="issue-density" value="0.25"/>
    <weight factor="business-rule-density" value="0.20"/>
  </scoring-weights>

  <hotspots count="3" threshold="25">
    <hotspot id="HOT-SVC-001" name="OrderService" path="src/service/OrderService.java"
             risk-score="82" rank="1" confidence="high">
      <complexity-score value="90" cyclomatic="18" cognitive="12"/>
      <dependency-score value="75" afferent="8" efferent="12"/>
      <issue-density-score value="85" issue-count="7" lines-of-code="1200"/>
      <business-rule-count value="15"/>
      <rationale>High cyclomatic complexity (18) combined with high dependency fan-out (12) and dense issue concentration (7 issues in 1200 LOC) make this the highest-risk module for modernization.</rationale>
      <source file="src/service/OrderService.java" line-start="1" line-end="1200"/>
    </hotspot>

    <hotspot id="HOT-DAL-001" name="CustomerRepository" path="src/repository/CustomerRepository.java"
             risk-score="65" rank="2" confidence="high">
      <complexity-score value="60" cyclomatic="10" cognitive="7"/>
      <dependency-score value="80" afferent="12" efferent="4"/>
      <issue-density-score value="55" issue-count="4" lines-of-code="800"/>
      <business-rule-count value="8"/>
      <rationale>High afferent coupling (12 dependents) creates significant change ripple risk. Contains 8 embedded business rules that should be extracted to service layer.</rationale>
      <source file="src/repository/CustomerRepository.java" line-start="1" line-end="800"/>
    </hotspot>

    <hotspot id="HOT-INT-001" name="PaymentGateway" path="src/integration/PaymentGateway.java"
             risk-score="58" rank="3" confidence="medium">
      <complexity-score value="45" cyclomatic="7" cognitive="5"/>
      <dependency-score value="60" afferent="6" efferent="9"/>
      <issue-density-score value="70" issue-count="5" lines-of-code="600"/>
      <business-rule-count value="4"/>
      <rationale>External integration point with deprecated API usage (5 issues). High efferent coupling to payment provider libraries increases migration risk.</rationale>
      <source file="src/integration/PaymentGateway.java" line-start="1" line-end="600"/>
    </hotspot>
  </hotspots>

</hotspot-analysis>
```

## Related Schemas

- [Common Schema](./common-schema.md) — Shared elements (root attributes, metadata, source references, confidence)
- [issues.md](./issues.md) — Issue data feeding into issue density scores
- [dependencies.md](./dependencies.md) — Dependency data feeding into dependency scores
- [business-rules.md](./business-rules.md) — Business rule counts per module
- [call-sites.md](./call-sites.md) — Call relationships informing coupling analysis
