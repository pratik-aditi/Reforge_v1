# Functional Requirements Schema

> Defines the structure for extracted functional requirements (`functional-requirements.xml`)

## Overview

The functional requirements schema captures functional requirements extracted by `/reforge.extract functional-requirements`. Each requirement includes acceptance criteria and source traceability.

## Common Elements

This schema extends the [Common Extraction Schema](./common-schema.md), which defines shared structural elements used across all extraction types:

- **Root attributes**: `project-id`, `version`, `schema-version`, `generated`, `xmlns`
- **Metadata container**: `<metadata>` with `<total-count>`, `<confidence-distribution>`, `<extraction-timestamp>`
- **Source references**: Canonical `<source>` format with `file`, `line-start`, `line-end` attributes
- **Confidence vocabulary**: `high`, `medium`, `low` enumeration
- **ID patterns**: `FR-{CATEGORY}-{SEQUENCE}` format

See `common-schema.md` for complete definitions. Elements defined there MUST NOT be redefined in this schema.

## Root Element

```xml
<functional-requirements xmlns="http://reforge.dev/schema/extraction"
                         project-id="my-app" version="1.0.0"
                         schema-version="1.0.0"
                         generated="2024-01-15T10:30:00Z">
  <metadata>...</metadata>
  <requirement>...</requirement>
</functional-requirements>
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

### `<requirement>`

Individual functional requirement with acceptance criteria and source traceability.

```xml
<requirement id="FR-AUTH-001" category="authentication" priority="high" confidence="high">
  <title>User Login Authentication</title>
  <description>The system shall authenticate users via username and password before granting access to protected resources.</description>
  <acceptance-criteria>
    <criterion>Valid credentials grant access and create a session</criterion>
    <criterion>Invalid credentials display an error message</criterion>
    <criterion>Three failed attempts lock the account for 30 minutes</criterion>
  </acceptance-criteria>
  <source file="src/auth/LoginController.java" line-start="20" line-end="55">
    <snippet>public AuthResult authenticate(String username, String password) {</snippet>
  </source>
  <related-rules>
    <rule-ref id="BR-AUTH-001" relationship="implements"/>
  </related-rules>
  <related-workflows>
    <workflow-ref id="WF-AUTH-001"/>
  </related-workflows>
</requirement>
```

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string | Yes | Unique requirement identifier |
| `category` | string | Yes | Requirement category |
| `priority` | string | Yes | Priority level (high, medium, low) |
| `confidence` | ConfidenceType | Yes | Extraction confidence level |

### `<title>`

Short, descriptive title of the functional requirement. Written as a concise label for identification and reference.

### `<description>`

Full description of the requirement using "shall" language. Written in natural language to convey what the system must do.

### `<acceptance-criteria>`

List of testable conditions that define when the requirement is satisfied.

```xml
<acceptance-criteria>
  <criterion>Valid credentials grant access and create a session</criterion>
  <criterion>Invalid credentials display an error message</criterion>
</acceptance-criteria>
```

Each `<criterion>` is a plain string describing a single testable condition.

### `<source>`

Source code location where the requirement was identified. Uses the canonical format defined in the [Common Extraction Schema](./common-schema.md#source-references). The optional `<snippet>` child element contains the actual code implementing the requirement.

### `<related-rules>`

Optional cross-references to business rules that this requirement implements or depends on.

```xml
<related-rules>
  <rule-ref id="BR-AUTH-001" relationship="implements"/>
  <rule-ref id="BR-VAL-003" relationship="depends-on"/>
</related-rules>
```

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string | Yes | Referenced business rule ID |
| `relationship` | string | No | Relationship type (implements, depends-on, extends) |

### `<related-workflows>`

Optional cross-references to workflows associated with this requirement.

```xml
<related-workflows>
  <workflow-ref id="WF-AUTH-001"/>
</related-workflows>
```

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string | Yes | Referenced workflow ID |

## Common Categories

Functional requirements are typically categorized as:

| Category | Description | Examples |
|----------|-------------|----------|
| `AUTH` | Authentication | Login, logout, session management |
| `CRUD` | Data management | Create, read, update, delete operations |
| `RPT` | Reporting | Report generation, data export |
| `INT` | Integration | External system communication |
| `NAV` | Navigation | Page routing, menu structure |
| `VAL` | Validation | Input validation, data integrity checks |
| `NOTIF` | Notifications | Email alerts, in-app messages |

## Example Output

```xml
<?xml version="1.0" encoding="UTF-8"?>
<functional-requirements xmlns="http://reforge.dev/schema/extraction"
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

  <requirement id="FR-AUTH-001" category="authentication" priority="high" confidence="high">
    <title>User Login Authentication</title>
    <description>The system shall authenticate users via username and password before granting access to protected resources.</description>
    <acceptance-criteria>
      <criterion>Valid credentials grant access and create a session</criterion>
      <criterion>Invalid credentials display an error message</criterion>
      <criterion>Three failed attempts lock the account for 30 minutes</criterion>
    </acceptance-criteria>
    <source file="src/auth/LoginController.java" line-start="20" line-end="55">
      <snippet>public AuthResult authenticate(String username, String password) {</snippet>
    </source>
    <related-rules>
      <rule-ref id="BR-AUTH-001" relationship="implements"/>
    </related-rules>
    <related-workflows>
      <workflow-ref id="WF-AUTH-001"/>
    </related-workflows>
  </requirement>

  <requirement id="FR-CRUD-001" category="data-management" priority="high" confidence="high">
    <title>Order Creation</title>
    <description>The system shall allow authenticated users to create new orders with one or more line items and persist them to the database.</description>
    <acceptance-criteria>
      <criterion>Order is saved with a unique order number</criterion>
      <criterion>All line items are associated with the order</criterion>
      <criterion>Order total is calculated correctly</criterion>
      <criterion>Confirmation is displayed to the user</criterion>
    </acceptance-criteria>
    <source file="src/controller/OrderController.java" line-start="30" line-end="75">
      <snippet>public Order createOrder(OrderRequest request) {</snippet>
    </source>
    <related-rules>
      <rule-ref id="BR-VAL-001" relationship="depends-on"/>
    </related-rules>
  </requirement>

</functional-requirements>
```

## Related Schemas

- [Common Schema](./common-schema.md) — Shared elements (root attributes, metadata, source references, confidence)
- [business-rules.md](./business-rules.md) — Business rules implemented by requirements
- [workflows.md](./workflows.md) — Workflows associated with requirements
