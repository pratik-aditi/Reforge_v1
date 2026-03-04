# Issues Schema

> Defines the structure for bugs and technical issues (`issues.xml`)

## Overview

The issues schema captures bugs/defects and technical debt/operational issues extracted by `/reforge.extract issues`. It uses two item types: `<bug>` for code defects/TODOs and `<issue>` for tech debt/operational concerns.

## Common Elements

This schema extends the [Common Extraction Schema](./common-schema.md), which defines shared structural elements used across all extraction types:

- **Root attributes**: `project-id`, `version`, `schema-version`, `generated`, `xmlns`
- **Metadata container**: `<metadata>` with `<total-count>`, `<confidence-distribution>`, `<extraction-timestamp>`
- **Source references**: Canonical `<source>` format with `file`, `line-start`, `line-end` attributes
- **Confidence vocabulary**: `high`, `medium`, `low` enumeration
- **ID patterns**: `BUG-{CATEGORY}-{SEQUENCE}` (bugs), `ISS-{CATEGORY}-{SEQUENCE}` (issues)

See `common-schema.md` for complete definitions. Elements defined there MUST NOT be redefined in this schema.

## Root Element

```xml
<issues xmlns="http://reforge.dev/schema/extraction"
        project-id="my-app" version="1.0.0"
        schema-version="1.0.0"
        generated="2024-01-15T10:30:00Z">
  <metadata>...</metadata>
  <bugs>...</bugs>
  <issues-list>...</issues-list>
</issues>
```

### Attributes

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `xmlns` | URI | Yes | Must be `http://reforge.dev/schema/extraction` |
| `project-id` | string | Yes | Reference to analysis project |
| `version` | string | Yes | Extraction version (semver) |
| `schema-version` | string | Yes | Common schema version (initial: `1.0.0`) |
| `generated` | dateTime | Yes | Extraction timestamp (ISO-8601) |

> Root attributes and `<metadata>` are defined by the [Common Extraction Schema](./common-schema.md). The `<metadata>` element is required as the first child of the root element. The metadata `<total-count>` equals the count of bugs plus the count of issues combined.

## Elements

### `<bugs>`

Container for bug/defect items.

```xml
<bugs count="5">
  <bug>...</bug>
</bugs>
```

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `count` | integer | Yes | Number of bug items in this container |

### `<bug>`

Individual code defect or TODO with impact assessment and source traceability.

```xml
<bug id="BUG-NULL-001" category="null-reference" severity="high" confidence="high">
  <title>Unchecked null return from findCustomer</title>
  <description>CustomerService.findCustomer can return null but caller does not check before accessing properties.</description>
  <detection-method>static-analysis</detection-method>
  <impact>NullPointerException at runtime when customer not found</impact>
  <source file="src/service/OrderService.java" line-start="45" line-end="48">
    <snippet>Customer customer = customerService.findCustomer(id);
String name = customer.getName(); // potential NPE</snippet>
  </source>
</bug>
```

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string | Yes | Unique bug identifier |
| `category` | string | Yes | Bug category |
| `severity` | string | Yes | Severity level (critical, high, medium, low) |
| `confidence` | ConfidenceType | Yes | Extraction confidence level |

### `<title>` (bug)

Short, descriptive title of the bug or defect.

### `<description>` (bug)

Full description of the defect explaining what is wrong and the conditions under which it occurs.

### `<detection-method>`

How the bug was identified during extraction.

| Value | Description |
|-------|-------------|
| `static-analysis` | Identified through code pattern analysis |
| `todo-comment` | Found via TODO/FIXME/HACK comment |
| `pattern-match` | Detected by known anti-pattern matching |
| `code-review` | Identified through manual code review |

### `<impact>`

Description of the runtime or operational impact if the bug is triggered.

### `<issues-list>`

Container for technical debt and operational issue items.

```xml
<issues-list count="8">
  <issue>...</issue>
</issues-list>
```

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `count` | integer | Yes | Number of issue items in this container |

### `<issue>`

Individual technical debt or operational concern with remediation guidance.

```xml
<issue id="ISS-DEBT-001" category="technical-debt" severity="medium" confidence="high">
  <title>Deprecated API usage in PaymentService</title>
  <description>Uses deprecated Stripe v1 API that will be removed in 2025.</description>
  <issue-type>deprecation</issue-type>
  <effort-estimate>medium</effort-estimate>
  <recommendation>Migrate to Stripe v3 API with updated payment intent flow.</recommendation>
  <source file="src/service/PaymentService.java" line-start="1" line-end="120"/>
</issue>
```

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string | Yes | Unique issue identifier |
| `category` | string | Yes | Issue category |
| `severity` | string | Yes | Severity level (critical, high, medium, low) |
| `confidence` | ConfidenceType | Yes | Extraction confidence level |

### `<title>` (issue)

Short, descriptive title of the technical debt or operational issue.

### `<description>` (issue)

Full description of the issue explaining the concern and its context.

### `<issue-type>`

Classification of the type of technical issue.

| Value | Description |
|-------|-------------|
| `deprecation` | Use of deprecated APIs, libraries, or patterns |
| `dead-code` | Unreachable or unused code |
| `duplication` | Duplicated logic across multiple locations |
| `complexity` | Excessive cyclomatic or cognitive complexity |
| `missing-tests` | Insufficient or absent test coverage |
| `hardcoded-config` | Configuration values embedded in source code |
| `anti-pattern` | Known anti-pattern implementation |

### `<effort-estimate>`

Estimated effort to resolve the issue.

| Value | Description |
|-------|-------------|
| `low` | Less than a day of effort |
| `medium` | One to five days of effort |
| `high` | More than five days of effort |

### `<recommendation>`

Suggested approach or strategy for resolving the issue.

### `<source>`

Source code location where the item was identified. Uses the canonical format defined in the [Common Extraction Schema](./common-schema.md#source-references). The optional `<snippet>` child element contains the relevant code.

## Common Categories

### Bug Categories

| Category | Description | Examples |
|----------|-------------|----------|
| `NULL` | Null references | Unchecked nulls, missing null guards |
| `RACE` | Race conditions | Thread-unsafe shared state |
| `LEAK` | Resource leaks | Unclosed connections, streams |
| `BOUND` | Bounds errors | Array index, off-by-one errors |
| `TYPE` | Type errors | Unsafe casts, type mismatches |
| `LOGIC` | Logic errors | Incorrect conditions, wrong operators |

### Issue Categories

| Category | Description | Examples |
|----------|-------------|----------|
| `DEBT` | Technical debt | Deprecated APIs, legacy patterns |
| `DEAD` | Dead code | Unused methods, unreachable branches |
| `DUP` | Duplication | Copy-pasted logic, redundant implementations |
| `CMPLX` | Complexity | High cyclomatic complexity, deep nesting |
| `TEST` | Missing tests | Untested critical paths, low coverage |
| `CFG` | Hardcoded config | Embedded URLs, magic numbers |

## Example Output

```xml
<?xml version="1.0" encoding="UTF-8"?>
<issues xmlns="http://reforge.dev/schema/extraction"
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

  <bugs count="1">
    <bug id="BUG-NULL-001" category="null-reference" severity="high" confidence="high">
      <title>Unchecked null return from findCustomer</title>
      <description>CustomerService.findCustomer can return null but caller does not check before accessing properties.</description>
      <detection-method>static-analysis</detection-method>
      <impact>NullPointerException at runtime when customer not found</impact>
      <source file="src/service/OrderService.java" line-start="45" line-end="48">
        <snippet>Customer customer = customerService.findCustomer(id);
String name = customer.getName(); // potential NPE</snippet>
      </source>
    </bug>
  </bugs>

  <issues-list count="1">
    <issue id="ISS-DEBT-001" category="technical-debt" severity="medium" confidence="high">
      <title>Deprecated API usage in PaymentService</title>
      <description>Uses deprecated Stripe v1 API that will be removed in 2025.</description>
      <issue-type>deprecation</issue-type>
      <effort-estimate>medium</effort-estimate>
      <recommendation>Migrate to Stripe v3 API with updated payment intent flow.</recommendation>
      <source file="src/service/PaymentService.java" line-start="1" line-end="120"/>
    </issue>
  </issues-list>

</issues>
```

## Related Schemas

- [Common Schema](./common-schema.md) — Shared elements (root attributes, metadata, source references, confidence)
- [non-functional.md](./non-functional.md) — Security findings related to code issues
- [architecture.md](./architecture.md) — Architectural components affected by issues
