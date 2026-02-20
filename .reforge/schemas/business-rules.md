# Business Rules Schema

> Defines the structure for extracted business rules (`business-rules.xml`)

## Overview

The business rules schema captures business logic extracted by `/reforge.extract business-rules`. Each rule includes its description, implementation logic, and source traceability.

## Common Elements

This schema extends the [Common Extraction Schema](./common-schema.md), which defines shared structural elements used across all extraction types:

- **Root attributes**: `project-id`, `version`, `schema-version`, `generated`, `xmlns`
- **Metadata container**: `<metadata>` with `<total-count>`, `<confidence-distribution>`, `<extraction-timestamp>`
- **Source references**: Canonical `<source>` format with `file`, `line-start`, `line-end` attributes
- **Confidence vocabulary**: `high`, `medium`, `low` enumeration
- **ID patterns**: `BR-{CATEGORY}-{SEQUENCE}` format

See `common-schema.md` for complete definitions. Elements defined there MUST NOT be redefined in this schema.

## Root Element

```xml
<business-rules xmlns="http://reforge.dev/schema/extraction"
                project-id="my-app" version="1.0.0"
                schema-version="1.0.0"
                generated="2024-01-15T10:30:00Z">
  <metadata>...</metadata>
  <rule>...</rule>
</business-rules>
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

### `<rule>`

Individual business rule with full traceability.

```xml
<rule id="BR-001" category="pricing" confidence="high">
  <description>Discount applies when order total exceeds $100</description>
  <logic>IF order.total > 100 THEN discount = order.total * 0.10</logic>
  <source file="src/PricingService.java" line-start="45" line-end="52">
    <snippet>if (order.getTotal() > 100) { discount = order.getTotal() * 0.10; }</snippet>
  </source>
  <entities>
    <entity>Order</entity>
    <entity>Discount</entity>
  </entities>
  <related-rules>
    <rule-ref id="BR-002" relationship="overrides"/>
  </related-rules>
</rule>
```

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string | Yes | Unique rule identifier |
| `category` | string | Yes | Rule category (validation, pricing, etc.) |
| `confidence` | ConfidenceType | Yes | Extraction confidence level |

### `<description>`

Human-readable description of what the rule does. Written in natural language to convey business intent.

### `<logic>`

Pseudo-code or structured representation of the rule logic. Uses a consistent format like:
- `IF <condition> THEN <action>`
- `WHEN <trigger> DO <action>`
- `<entity>.<property> MUST BE <constraint>`

### `<source>`

Source code location where the rule was extracted from. Uses the canonical format defined in the [Common Extraction Schema](./common-schema.md#source-references). The optional `<snippet>` child element contains the actual code implementing the rule.

### `<entities>`

Domain entities referenced by this rule.

```xml
<entities>
  <entity>Order</entity>
  <entity>Customer</entity>
</entities>
```

### `<related-rules>`

Cross-references to other rules.

```xml
<related-rules>
  <rule-ref id="BR-002" relationship="overrides"/>
  <rule-ref id="BR-003" relationship="depends-on"/>
</related-rules>
```

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string | Yes | Referenced rule ID |
| `relationship` | string | No | Relationship type (overrides, depends-on, extends) |

## Common Categories

Business rules are typically categorized as:

| Category | Description | Examples |
|----------|-------------|----------|
| `validation` | Input validation rules | Required fields, format checks |
| `pricing` | Pricing and discount rules | Bulk discounts, promotions |
| `authorization` | Access control rules | Role permissions, ownership |
| `calculation` | Computed values | Tax calculation, totals |
| `workflow` | State transitions | Order status changes |
| `notification` | Alert triggers | Email conditions, warnings |
| `constraint` | Business constraints | Inventory limits, date ranges |

## Example Output

```xml
<?xml version="1.0" encoding="UTF-8"?>
<business-rules xmlns="http://reforge.dev/schema/extraction"
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

  <rule id="BR-001" category="pricing" confidence="high">
    <description>Apply 10% discount for orders over $100</description>
    <logic>IF order.total > 100 THEN order.discount = order.total * 0.10</logic>
    <source file="src/service/PricingService.java" line-start="45" line-end="52">
      <snippet>if (order.getTotal().compareTo(DISCOUNT_THRESHOLD) > 0) {
    order.setDiscount(order.getTotal().multiply(DISCOUNT_RATE));
}</snippet>
    </source>
    <entities>
      <entity>Order</entity>
    </entities>
  </rule>

  <rule id="BR-002" category="validation" confidence="high">
    <description>Order must have at least one line item</description>
    <logic>order.items.count MUST BE >= 1</logic>
    <source file="src/model/Order.java" line-start="78" line-end="82">
      <snippet>if (items == null || items.isEmpty()) {
    throw new ValidationException("Order must have items");
}</snippet>
    </source>
    <entities>
      <entity>Order</entity>
      <entity>OrderItem</entity>
    </entities>
    <related-rules>
      <rule-ref id="BR-001" relationship="depends-on"/>
    </related-rules>
  </rule>

</business-rules>
```

## Related Schemas

- [Common Schema](./common-schema.md) — Shared elements (root attributes, metadata, source references, confidence)
- [analysis.md](./analysis.md) — Codebase inventory
- [database.md](./database.md) — Database interactions
- [workflows.md](./workflows.md) — Rules often trigger workflows

## Contract Reference

Based on: `specs/001-legacy-analyzer/contracts/business-rules.xsd`
