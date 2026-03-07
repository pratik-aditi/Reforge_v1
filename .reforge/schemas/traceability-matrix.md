# Traceability Matrix Schema

> Defines the structure for end-to-end traceability chains (`traceability-matrix.xml`)

## Overview

The traceability matrix schema captures cross-extraction traceability chains produced by `/reforge.trace`. It links items across extraction types to provide end-to-end traceability: requirement to rule to code to UI to user story. It also identifies orphaned items that lack connections to other artifacts.

## Common Elements

This schema extends the [Common Extraction Schema](./common-schema.md), which defines shared structural elements used across all extraction types:

- **Root attributes**: `project-id`, `version`, `schema-version`, `generated`, `xmlns`
- **Metadata container**: `<metadata>` with `<total-count>`, `<confidence-distribution>`, `<extraction-timestamp>`
- **Source references**: Canonical `<source>` format with `file`, `line-start`, `line-end` attributes
- **Confidence vocabulary**: `high`, `medium`, `low` enumeration
- **ID patterns**: `TRACE-{CATEGORY}-{SEQUENCE}`

See `common-schema.md` for complete definitions. Elements defined there MUST NOT be redefined in this schema.

## Root Element

```xml
<traceability-matrix xmlns="http://reforge.dev/schema/extraction"
                     project-id="my-app" version="1.0.0"
                     schema-version="1.0.0"
                     generated="2024-01-15T10:30:00Z">
  <metadata>...</metadata>
  <summary>...</summary>
  <traces>...</traces>
  <orphans>...</orphans>
</traceability-matrix>
```

### Attributes

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `xmlns` | URI | Yes | Must be `http://reforge.dev/schema/extraction` |
| `project-id` | string | Yes | Reference to analysis project |
| `version` | string | Yes | Extraction version (semver) |
| `schema-version` | string | Yes | Common schema version (initial: `1.0.0`) |
| `generated` | dateTime | Yes | Extraction timestamp (ISO-8601) |

> Root attributes and `<metadata>` are defined by the [Common Extraction Schema](./common-schema.md). The `<metadata>` element is required as the first child of the root element. The metadata `<total-count>` equals the count of all trace chains.

## Elements

### `<summary>`

Aggregate statistics for the traceability matrix.

```xml
<summary>
  <total-traces>45</total-traces>
  <total-links>182</total-links>
  <total-orphans>12</total-orphans>
  <coverage>
    <type name="functional-requirement" total="30" traced="28" percent="93"/>
    <type name="business-rule" total="85" traced="72" percent="85"/>
    <type name="ui-flow" total="22" traced="20" percent="91"/>
    <type name="workflow" total="15" traced="14" percent="93"/>
    <type name="user-story" total="40" traced="35" percent="88"/>
  </coverage>
</summary>
```

### `<traces>`

Container for trace chains.

```xml
<traces count="45">
  <trace>...</trace>
</traces>
```

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `count` | integer | Yes | Number of trace chains in this container |

### `<trace>`

Individual traceability chain linking items across extraction types.

```xml
<trace id="TRACE-AUTH-001" confidence="high">
  <description>Authentication login flow from requirement through implementation to UI</description>
  <chain>
    <link type="functional-requirement" ref-id="FR-AUTH-001"
          label="User must authenticate with username and password"/>
    <link type="business-rule" ref-id="BR-AUTH-001"
          label="Password must meet complexity requirements"/>
    <link type="business-rule" ref-id="BR-AUTH-002"
          label="Account locks after 5 failed attempts"/>
    <link type="code" ref-id="CALL-SVC-012"
          label="AuthService.authenticate()"/>
    <link type="ui-flow" ref-id="SCR-LOGIN-001"
          label="Login screen with username/password fields"/>
    <link type="user-story" ref-id="US-AUTH-001"
          label="As a user I can log in with my credentials"/>
  </chain>
</trace>
```

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string | Yes | Unique trace identifier (`TRACE-{CATEGORY}-{SEQUENCE}`) |
| `confidence` | ConfidenceType | Yes | Confidence in the completeness of the trace chain |

### `<description>`

Summary of what this trace chain represents end-to-end.

### `<chain>`

Ordered sequence of linked items forming the trace.

### `<link>`

Individual link in a trace chain, pointing to an item in another extraction.

```xml
<link type="business-rule" ref-id="BR-VAL-001"
      label="Order total must exceed minimum threshold"/>
```

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `type` | string | Yes | The extraction type of the linked item |
| `ref-id` | string | Yes | ID of the referenced item in its extraction |
| `label` | string | No | Human-readable summary of the linked item |

### `<link>` Type Values

| Value | Description | Typical ID Prefix |
|-------|-------------|-------------------|
| `functional-requirement` | Functional requirement | `FR-` |
| `business-rule` | Business rule | `BR-` |
| `code` | Source code element (call-site, method) | `CALL-`, `DEP-` |
| `ui-flow` | UI screen or component | `SCR-`, `CMP-` |
| `workflow` | Process workflow | `WF-` |
| `user-story` | Generated user story | `US-` |
| `database` | Database interaction or entity | `DB-`, `E-` |
| `non-functional` | Non-functional requirement | `NFR-`, `SEC-` |
| `architecture` | Architectural component | `ARCH-`, `INT-` |

### `<orphans>`

Container for items that have no trace connections.

```xml
<orphans count="12">
  <orphan type="business-rule" ref-id="BR-CALC-015"
          label="Legacy commission calculation"
          reason="No functional requirement or user story references this rule"/>
  <orphan type="functional-requirement" ref-id="FR-RPT-003"
          label="Generate monthly compliance report"
          reason="No implementing code or UI found for this requirement"/>
</orphans>
```

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `count` | integer | Yes | Number of orphaned items |

### `<orphan>`

An extraction item with no connections to other artifacts.

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `type` | string | Yes | The extraction type of the orphaned item |
| `ref-id` | string | Yes | ID of the orphaned item |
| `label` | string | No | Human-readable summary |
| `reason` | string | Yes | Why this item is considered orphaned |

## Common Categories

| Category | Description | Examples |
|----------|-------------|----------|
| `AUTH` | Authentication traces | Login, session, credentials |
| `AUTHZ` | Authorization traces | Permissions, roles, access |
| `ORDER` | Order processing traces | Cart, checkout, payment |
| `USER` | User management traces | Registration, profile |
| `RPT` | Reporting traces | Reports, dashboards |
| `DATA` | Data management traces | CRUD operations |
| `INTEG` | Integration traces | API, external systems |

## Example Output

```xml
<?xml version="1.0" encoding="UTF-8"?>
<traceability-matrix xmlns="http://reforge.dev/schema/extraction"
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

  <summary>
    <total-traces>2</total-traces>
    <total-links>9</total-links>
    <total-orphans>1</total-orphans>
    <coverage>
      <type name="functional-requirement" total="10" traced="9" percent="90"/>
      <type name="business-rule" total="25" traced="22" percent="88"/>
    </coverage>
  </summary>

  <traces count="2">
    <trace id="TRACE-AUTH-001" confidence="high">
      <description>User login authentication flow from requirement to UI</description>
      <chain>
        <link type="functional-requirement" ref-id="FR-AUTH-001"
              label="User must authenticate with username and password"/>
        <link type="business-rule" ref-id="BR-AUTH-001"
              label="Password must meet complexity requirements"/>
        <link type="code" ref-id="CALL-SVC-012"
              label="AuthService.authenticate()"/>
        <link type="ui-flow" ref-id="SCR-LOGIN-001"
              label="Login screen"/>
        <link type="user-story" ref-id="US-AUTH-001"
              label="As a user I can log in"/>
      </chain>
    </trace>

    <trace id="TRACE-ORDER-001" confidence="medium">
      <description>Order placement flow from requirement through checkout</description>
      <chain>
        <link type="functional-requirement" ref-id="FR-ORD-001"
              label="User can place an order from their cart"/>
        <link type="business-rule" ref-id="BR-VAL-005"
              label="Order total must exceed minimum threshold"/>
        <link type="code" ref-id="CALL-SVC-025"
              label="OrderService.placeOrder()"/>
        <link type="ui-flow" ref-id="SCR-CHECKOUT-001"
              label="Checkout page"/>
      </chain>
    </trace>
  </traces>

  <orphans count="1">
    <orphan type="business-rule" ref-id="BR-CALC-015"
            label="Legacy commission calculation"
            reason="No functional requirement or user story references this rule"/>
  </orphans>

</traceability-matrix>
```

## Related Schemas

- [Common Schema](./common-schema.md) — Shared elements (root attributes, metadata, source references, confidence)
- [functional-requirements.md](./functional-requirements.md) — Functional requirements linked in traces
- [business-rules.md](./business-rules.md) — Business rules linked in traces
- [call-sites.md](./call-sites.md) — Code call-sites linked in traces
- [ui-flows.md](./ui-flows.md) — UI screens and components linked in traces
- [workflows.md](./workflows.md) — Workflows linked in traces
