# Dependencies Schema

> Defines the structure for module dependency graphs (`dependencies.xml`)

## Overview

The dependencies schema captures module-level dependency relationships extracted by `/reforge.extract dependencies`. It documents imports, event subscriptions, interface implementations, and other coupling mechanisms.

## Common Elements

This schema extends the [Common Extraction Schema](./common-schema.md), which defines shared structural elements used across all extraction types:

- **Root attributes**: `project-id`, `version`, `schema-version`, `generated`, `xmlns`
- **Metadata container**: `<metadata>` with `<total-count>`, `<confidence-distribution>`, `<extraction-timestamp>`
- **Source references**: Canonical `<source>` format with `file`, `line-start`, `line-end` attributes
- **Confidence vocabulary**: `high`, `medium`, `low` enumeration
- **ID patterns**: `DEP-{CATEGORY}-{SEQUENCE}` format

See `common-schema.md` for complete definitions. Elements defined there MUST NOT be redefined in this schema.

## Root Element

```xml
<dependencies xmlns="http://reforge.dev/schema/extraction"
              project-id="my-app" version="1.0.0"
              schema-version="1.0.0"
              generated="2024-01-15T10:30:00Z">
  <metadata>...</metadata>
  <dep-ref>...</dep-ref>
</dependencies>
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

### `<dep-ref>`

Individual module dependency relationship with source traceability.

```xml
<dep-ref id="DEP-IMP-001" dependency-type="import" confidence="high">
  <from-module>com.app.controller.OrderController</from-module>
  <to-module>com.app.service.PricingService</to-module>
  <coupling>tight</coupling>
  <direction>unidirectional</direction>
  <source file="src/controller/OrderController.java" line-start="3" line-end="3">
    <snippet>import com.app.service.PricingService;</snippet>
  </source>
</dep-ref>
```

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string | Yes | Unique dependency identifier |
| `dependency-type` | string | Yes | Type of dependency relationship |
| `confidence` | ConfidenceType | Yes | Extraction confidence level |

### `<from-module>`

Fully qualified name of the module that depends on another. The dependent (consumer) side of the relationship.

### `<to-module>`

Fully qualified name of the module being depended upon. The dependency (provider) side of the relationship.

### `<coupling>`

Degree of coupling between the modules.

| Value | Description |
|-------|-------------|
| `tight` | Direct compile-time dependency |
| `loose` | Interface or abstraction-mediated dependency |
| `runtime` | Runtime-only dependency (reflection, config, etc.) |

### `<direction>`

Directionality of the dependency relationship.

| Value | Description |
|-------|-------------|
| `unidirectional` | One-way dependency (A depends on B) |
| `bidirectional` | Mutual dependency (A and B depend on each other) |
| `circular` | Part of a circular dependency chain |

### `<source>`

Source code location where the dependency was identified. Uses the canonical format defined in the [Common Extraction Schema](./common-schema.md#source-references). The optional `<snippet>` child element contains the actual code establishing the dependency.

### Dependency Type Values

| Value | Description |
|-------|-------------|
| `import` | Explicit import or include statement |
| `event` | Event subscription or publication |
| `interface` | Interface implementation or contract |
| `inheritance` | Class inheritance relationship |
| `injection` | Dependency injection (constructor, field, or method) |
| `reflection` | Reflective access or dynamic loading |
| `config` | Configuration-driven dependency |

## Common Categories

Dependencies are typically categorized as:

| Category | Description | Examples |
|----------|-------------|----------|
| `IMP` | Imports | Package imports, includes, requires |
| `EVT` | Events | Event subscriptions, message listeners |
| `IFC` | Interfaces | Interface implementations, contracts |
| `INH` | Inheritance | Class extends, mixin usage |
| `INJ` | Dependency injection | Constructor injection, field injection |
| `CFG` | Configuration | Config-driven wiring, property references |

## Example Output

```xml
<?xml version="1.0" encoding="UTF-8"?>
<dependencies xmlns="http://reforge.dev/schema/extraction"
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

  <dep-ref id="DEP-IMP-001" dependency-type="import" confidence="high">
    <from-module>com.app.controller.OrderController</from-module>
    <to-module>com.app.service.PricingService</to-module>
    <coupling>tight</coupling>
    <direction>unidirectional</direction>
    <source file="src/controller/OrderController.java" line-start="3" line-end="3">
      <snippet>import com.app.service.PricingService;</snippet>
    </source>
  </dep-ref>

  <dep-ref id="DEP-EVT-001" dependency-type="event" confidence="high">
    <from-module>com.app.service.OrderService</from-module>
    <to-module>com.app.listener.InventoryListener</to-module>
    <coupling>loose</coupling>
    <direction>unidirectional</direction>
    <source file="src/service/OrderService.java" line-start="67" line-end="67">
      <snippet>eventBus.publish(new OrderCompletedEvent(order));</snippet>
    </source>
  </dep-ref>

</dependencies>
```

## Related Schemas

- [Common Schema](./common-schema.md) — Shared elements (root attributes, metadata, source references, confidence)
- [call-sites.md](./call-sites.md) — Call sites contribute to dependency relationships
- [architecture.md](./architecture.md) — Architectural components linked by dependencies
