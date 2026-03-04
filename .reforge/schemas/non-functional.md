# Non-Functional Requirements Schema

> Defines the structure for non-functional requirements and security findings (`non-functional-requirements.xml`)

## Overview

The non-functional requirements schema captures NFRs/SLAs and security findings extracted by `/reforge.extract non-functional`. It uses dual containers: `<requirements>` for non-functional requirements and `<findings>` for security/CWE items.

## Common Elements

This schema extends the [Common Extraction Schema](./common-schema.md), which defines shared structural elements used across all extraction types:

- **Root attributes**: `project-id`, `version`, `schema-version`, `generated`, `xmlns`
- **Metadata container**: `<metadata>` with `<total-count>`, `<confidence-distribution>`, `<extraction-timestamp>`
- **Source references**: Canonical `<source>` format with `file`, `line-start`, `line-end` attributes
- **Confidence vocabulary**: `high`, `medium`, `low` enumeration
- **ID patterns**: `NFR-{CATEGORY}-{SEQUENCE}` (requirements), `SEC-{CATEGORY}-{SEQUENCE}` (security findings)

See `common-schema.md` for complete definitions. Elements defined there MUST NOT be redefined in this schema.

## Root Element

```xml
<non-functional-requirements xmlns="http://reforge.dev/schema/extraction"
                              project-id="my-app" version="1.0.0"
                              schema-version="1.0.0"
                              generated="2024-01-15T10:30:00Z">
  <metadata>...</metadata>
  <requirements>...</requirements>
  <findings>...</findings>
</non-functional-requirements>
```

### Attributes

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `xmlns` | URI | Yes | Must be `http://reforge.dev/schema/extraction` |
| `project-id` | string | Yes | Reference to analysis project |
| `version` | string | Yes | Extraction version (semver) |
| `schema-version` | string | Yes | Common schema version (initial: `1.0.0`) |
| `generated` | dateTime | Yes | Extraction timestamp (ISO-8601) |

> Root attributes and `<metadata>` are defined by the [Common Extraction Schema](./common-schema.md). The `<metadata>` element is required as the first child of the root element. The metadata `<total-count>` equals the count of requirements plus the count of findings combined.

## Elements

### `<requirements>`

Container for non-functional requirement items.

```xml
<requirements count="5">
  <requirement>...</requirement>
</requirements>
```

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `count` | integer | Yes | Number of requirement items in this container |

### `<requirement>`

Individual non-functional requirement with metric thresholds and source traceability.

```xml
<requirement id="NFR-PERF-001" category="performance" confidence="high">
  <title>API Response Time SLA</title>
  <description>All API endpoints shall respond within 200ms at the 95th percentile under normal load.</description>
  <metric name="p95-response-time" threshold="200ms" unit="milliseconds"/>
  <source file="src/config/PerformanceConfig.java" line-start="15" line-end="20">
    <snippet>@Timeout(value = 200, unit = TimeUnit.MILLISECONDS)</snippet>
  </source>
</requirement>
```

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string | Yes | Unique requirement identifier |
| `category` | string | Yes | Requirement category |
| `confidence` | ConfidenceType | Yes | Extraction confidence level |

### `<title>` (requirement)

Short, descriptive title of the non-functional requirement.

### `<description>` (requirement)

Full description of the NFR using "shall" language. Written in natural language to convey the quality attribute or constraint.

### `<metric>`

Optional measurable threshold associated with the requirement.

```xml
<metric name="p95-response-time" threshold="200ms" unit="milliseconds"/>
```

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | string | Yes | Metric identifier |
| `threshold` | string | Yes | Target threshold value |
| `unit` | string | Yes | Unit of measurement |

### `<findings>`

Container for security finding items.

```xml
<findings count="3">
  <finding>...</finding>
</findings>
```

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `count` | integer | Yes | Number of finding items in this container |

### `<finding>`

Individual security or compliance finding with remediation guidance.

```xml
<finding id="SEC-CWE-001" category="injection" severity="critical" confidence="high">
  <title>SQL Injection in Search Query</title>
  <description>User input concatenated directly into SQL query without parameterization.</description>
  <cwe-id>CWE-89</cwe-id>
  <affected-component>SearchRepository.findByName</affected-component>
  <remediation>Use parameterized queries or prepared statements.</remediation>
  <source file="src/repository/SearchRepository.java" line-start="30" line-end="35">
    <snippet>String sql = "SELECT * FROM items WHERE name = '" + name + "'";</snippet>
  </source>
</finding>
```

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string | Yes | Unique finding identifier |
| `category` | string | Yes | Finding category |
| `severity` | string | Yes | Severity level (critical, high, medium, low) |
| `confidence` | ConfidenceType | Yes | Extraction confidence level |

### `<title>` (finding)

Short, descriptive title of the security finding.

### `<description>` (finding)

Full description of the finding explaining the vulnerability or issue.

### `<cwe-id>`

Optional Common Weakness Enumeration identifier (e.g., `CWE-89`, `CWE-79`).

### `<affected-component>`

The specific component, class, or method affected by the finding.

### `<remediation>`

Recommended fix or mitigation strategy for the finding.

### `<source>`

Source code location where the item was identified. Uses the canonical format defined in the [Common Extraction Schema](./common-schema.md#source-references). The optional `<snippet>` child element contains the relevant code.

## Common Categories

### Requirement Categories

| Category | Description | Examples |
|----------|-------------|----------|
| `PERF` | Performance | Response times, throughput, latency |
| `SCAL` | Scalability | Load capacity, horizontal scaling |
| `AVAIL` | Availability | Uptime SLAs, failover, redundancy |
| `SEC` | Security | Encryption, access control policies |
| `MAINT` | Maintainability | Code quality, modularity constraints |
| `COMPAT` | Compatibility | Browser support, API versioning |

### Finding Categories

| Category | Description | Examples |
|----------|-------------|----------|
| `INJ` | Injection | SQL injection, command injection |
| `XSS` | Cross-site scripting | Reflected XSS, stored XSS |
| `AUTH` | Authentication | Weak passwords, missing MFA |
| `CRYPTO` | Cryptography | Weak algorithms, hardcoded keys |
| `CONFIG` | Misconfiguration | Debug mode enabled, default credentials |
| `EXPOSED` | Information exposure | Stack traces, verbose errors |

## Example Output

```xml
<?xml version="1.0" encoding="UTF-8"?>
<non-functional-requirements xmlns="http://reforge.dev/schema/extraction"
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

  <requirements count="1">
    <requirement id="NFR-PERF-001" category="performance" confidence="high">
      <title>API Response Time SLA</title>
      <description>All API endpoints shall respond within 200ms at the 95th percentile under normal load.</description>
      <metric name="p95-response-time" threshold="200ms" unit="milliseconds"/>
      <source file="src/config/PerformanceConfig.java" line-start="15" line-end="20">
        <snippet>@Timeout(value = 200, unit = TimeUnit.MILLISECONDS)</snippet>
      </source>
    </requirement>
  </requirements>

  <findings count="1">
    <finding id="SEC-INJ-001" category="injection" severity="critical" confidence="high">
      <title>SQL Injection in Search Query</title>
      <description>User input concatenated directly into SQL query without parameterization.</description>
      <cwe-id>CWE-89</cwe-id>
      <affected-component>SearchRepository.findByName</affected-component>
      <remediation>Use parameterized queries or prepared statements.</remediation>
      <source file="src/repository/SearchRepository.java" line-start="30" line-end="35">
        <snippet>String sql = "SELECT * FROM items WHERE name = '" + name + "'";</snippet>
      </source>
    </finding>
  </findings>

</non-functional-requirements>
```

## Related Schemas

- [Common Schema](./common-schema.md) — Shared elements (root attributes, metadata, source references, confidence)
- [architecture.md](./architecture.md) — Architectural components subject to NFRs
