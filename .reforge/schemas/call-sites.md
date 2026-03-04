# Call Sites Schema

> Defines the structure for extracted method/function call relationships (`call-sites.xml`)

## Overview

The call sites schema captures method/function call relationships extracted by `/reforge.extract call-sites`. Each call includes caller and callee information with dual source references for traceability.

## Common Elements

This schema extends the [Common Extraction Schema](./common-schema.md), which defines shared structural elements used across all extraction types:

- **Root attributes**: `project-id`, `version`, `schema-version`, `generated`, `xmlns`
- **Metadata container**: `<metadata>` with `<total-count>`, `<confidence-distribution>`, `<extraction-timestamp>`
- **Source references**: Canonical `<source>` format with `file`, `line-start`, `line-end` attributes
- **Confidence vocabulary**: `high`, `medium`, `low` enumeration
- **ID patterns**: `CALL-{CATEGORY}-{SEQUENCE}` format

See `common-schema.md` for complete definitions. Elements defined there MUST NOT be redefined in this schema.

## Root Element

```xml
<call-sites xmlns="http://reforge.dev/schema/extraction"
            project-id="my-app" version="1.0.0"
            schema-version="1.0.0"
            generated="2024-01-15T10:30:00Z">
  <metadata>...</metadata>
  <call>...</call>
</call-sites>
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

### `<call>`

Individual method/function call relationship with dual source traceability.

```xml
<call id="CALL-SVC-001" confidence="high">
  <caller method="submitOrder" class="OrderController" module="web">
    <caller-source file="src/controller/OrderController.java" line-start="45" line-end="45">
      <snippet>pricingService.calculateTotal(order);</snippet>
    </caller-source>
  </caller>
  <callee method="calculateTotal" class="PricingService" module="services">
    <callee-source file="src/service/PricingService.java" line-start="20" line-end="35">
      <snippet>public BigDecimal calculateTotal(Order order) {</snippet>
    </callee-source>
  </callee>
  <call-type>direct</call-type>
  <parameters>
    <parameter name="order" type="Order"/>
  </parameters>
  <return-type>BigDecimal</return-type>
</call>
```

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string | Yes | Unique call identifier |
| `confidence` | ConfidenceType | Yes | Extraction confidence level |

### `<caller>`

The method or function initiating the call.

```xml
<caller method="submitOrder" class="OrderController" module="web">
  <caller-source file="src/controller/OrderController.java" line-start="45" line-end="45">
    <snippet>pricingService.calculateTotal(order);</snippet>
  </caller-source>
</caller>
```

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `method` | string | Yes | Method or function name |
| `class` | string | Yes | Containing class or module name |
| `module` | string | Yes | Logical module or package |

The `<caller-source>` child element uses the canonical `SourceReferenceType` format defined in the [Common Extraction Schema](./common-schema.md#source-references).

### `<callee>`

The method or function being called.

```xml
<callee method="calculateTotal" class="PricingService" module="services">
  <callee-source file="src/service/PricingService.java" line-start="20" line-end="35">
    <snippet>public BigDecimal calculateTotal(Order order) {</snippet>
  </callee-source>
</callee>
```

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `method` | string | Yes | Method or function name |
| `class` | string | Yes | Containing class or module name |
| `module` | string | Yes | Logical module or package |

The `<callee-source>` child element uses the canonical `SourceReferenceType` format defined in the [Common Extraction Schema](./common-schema.md#source-references).

### `<call-type>`

Classification of the call mechanism.

| Value | Description |
|-------|-------------|
| `direct` | Direct method invocation |
| `virtual` | Virtual/polymorphic dispatch |
| `interface` | Call through interface reference |
| `event` | Event-driven invocation |
| `callback` | Callback or listener pattern |
| `reflection` | Reflective invocation |

### `<parameters>`

Optional list of parameters passed in the call.

```xml
<parameters>
  <parameter name="order" type="Order"/>
  <parameter name="applyDiscount" type="boolean"/>
</parameters>
```

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | string | Yes | Parameter name |
| `type` | string | Yes | Parameter type |

### `<return-type>`

Optional return type of the called method. Plain string value (e.g., `BigDecimal`, `void`, `List<Order>`).

## Common Categories

Call sites are typically categorized as:

| Category | Description | Examples |
|----------|-------------|----------|
| `SVC` | Service calls | Service-to-service invocations |
| `DAO` | Data access calls | Repository or DAO method calls |
| `CTL` | Controller calls | Controller-to-service dispatches |
| `UTL` | Utility calls | Helper and utility method calls |
| `EXT` | External/API calls | Third-party or external API calls |
| `EVT` | Event dispatches | Event publishing and listener invocations |

## Example Output

```xml
<?xml version="1.0" encoding="UTF-8"?>
<call-sites xmlns="http://reforge.dev/schema/extraction"
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

  <call id="CALL-SVC-001" confidence="high">
    <caller method="submitOrder" class="OrderController" module="web">
      <caller-source file="src/controller/OrderController.java" line-start="45" line-end="45">
        <snippet>pricingService.calculateTotal(order);</snippet>
      </caller-source>
    </caller>
    <callee method="calculateTotal" class="PricingService" module="services">
      <callee-source file="src/service/PricingService.java" line-start="20" line-end="35">
        <snippet>public BigDecimal calculateTotal(Order order) {</snippet>
      </callee-source>
    </callee>
    <call-type>direct</call-type>
    <parameters>
      <parameter name="order" type="Order"/>
    </parameters>
    <return-type>BigDecimal</return-type>
  </call>

  <call id="CALL-DAO-001" confidence="high">
    <caller method="calculateTotal" class="PricingService" module="services">
      <caller-source file="src/service/PricingService.java" line-start="28" line-end="28">
        <snippet>List&lt;PriceRule&gt; rules = priceRuleRepository.findActiveRules();</snippet>
      </caller-source>
    </caller>
    <callee method="findActiveRules" class="PriceRuleRepository" module="data">
      <callee-source file="src/repository/PriceRuleRepository.java" line-start="15" line-end="25">
        <snippet>public List&lt;PriceRule&gt; findActiveRules() {</snippet>
      </callee-source>
    </callee>
    <call-type>interface</call-type>
    <return-type>List&lt;PriceRule&gt;</return-type>
  </call>

</call-sites>
```

## Related Schemas

- [Common Schema](./common-schema.md) — Shared elements (root attributes, metadata, source references, confidence)
- [business-rules.md](./business-rules.md) — Business rules referenced by call sites
- [workflows.md](./workflows.md) — Calls often form workflow steps
- [dependencies.md](./dependencies.md) — Call sites contribute to dependency graphs
