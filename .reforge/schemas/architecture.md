# Architecture Schema

> Defines the structure for architectural components, integrations, and design patterns (`architecture.xml`)

## Overview

The architecture schema captures architectural elements extracted by `/reforge.extract architecture`. It supports optional `--subtype` routing: `design-patterns`, `integrations`, `infrastructure`. The schema contains three item containers: `<components>`, `<integrations>`, and `<patterns>`. When `--subtype` is specified, only the corresponding container is populated; otherwise all three are extracted.

## Common Elements

This schema extends the [Common Extraction Schema](./common-schema.md), which defines shared structural elements used across all extraction types:

- **Root attributes**: `project-id`, `version`, `schema-version`, `generated`, `xmlns`
- **Metadata container**: `<metadata>` with `<total-count>`, `<confidence-distribution>`, `<extraction-timestamp>`
- **Source references**: Canonical `<source>` format with `file`, `line-start`, `line-end` attributes
- **Confidence vocabulary**: `high`, `medium`, `low` enumeration
- **ID patterns**: `ARCH-{CATEGORY}-{SEQUENCE}` (components), `INT-{CATEGORY}-{SEQUENCE}` (integrations), `DP-{CATEGORY}-{SEQUENCE}` (patterns)

See `common-schema.md` for complete definitions. Elements defined there MUST NOT be redefined in this schema.

## Root Element

```xml
<architecture xmlns="http://reforge.dev/schema/extraction"
              project-id="my-app" version="1.0.0"
              schema-version="1.0.0"
              generated="2024-01-15T10:30:00Z">
  <metadata>...</metadata>
  <components>...</components>
  <integrations>...</integrations>
  <patterns>...</patterns>
</architecture>
```

### Attributes

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `xmlns` | URI | Yes | Must be `http://reforge.dev/schema/extraction` |
| `project-id` | string | Yes | Reference to analysis project |
| `version` | string | Yes | Extraction version (semver) |
| `schema-version` | string | Yes | Common schema version (initial: `1.0.0`) |
| `generated` | dateTime | Yes | Extraction timestamp (ISO-8601) |

> Root attributes and `<metadata>` are defined by the [Common Extraction Schema](./common-schema.md). The `<metadata>` element is required as the first child of the root element. The metadata `<total-count>` equals the count of components plus integrations plus patterns combined.

## Elements

### `<components>`

Container for architectural component items.

```xml
<components count="10">
  <component>...</component>
</components>
```

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `count` | integer | Yes | Number of component items in this container |

### `<component>`

Individual architectural component with layer classification and responsibilities.

```xml
<component id="ARCH-WEB-001" name="Order API" layer="presentation" confidence="high">
  <description>REST API layer handling order CRUD operations</description>
  <technology>Spring MVC</technology>
  <responsibilities>
    <responsibility>Handle HTTP requests for order operations</responsibility>
    <responsibility>Input validation and response formatting</responsibility>
  </responsibilities>
  <source file="src/controller/OrderController.java" line-start="1" line-end="150"/>
</component>
```

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string | Yes | Unique component identifier |
| `name` | string | Yes | Human-readable component name |
| `layer` | string | Yes | Architectural layer classification |
| `confidence` | ConfidenceType | Yes | Extraction confidence level |

#### Layer Values

| Value | Description |
|-------|-------------|
| `presentation` | UI and API endpoints |
| `business` | Business logic and services |
| `data` | Data access and persistence |
| `integration` | External system adapters |
| `infrastructure` | Cross-cutting infrastructure |

### `<description>` (component)

Human-readable description of the component's purpose and scope.

### `<technology>`

Primary technology or framework used by the component (e.g., `Spring MVC`, `React`, `Hibernate`).

### `<responsibilities>`

List of responsibilities assigned to the component.

```xml
<responsibilities>
  <responsibility>Handle HTTP requests for order operations</responsibility>
  <responsibility>Input validation and response formatting</responsibility>
</responsibilities>
```

Each `<responsibility>` is a plain string describing a single responsibility.

### `<integrations>`

Container for integration point items.

```xml
<integrations count="5">
  <integration>...</integration>
</integrations>
```

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `count` | integer | Yes | Number of integration items in this container |

### `<integration>`

Individual external integration point with protocol and connectivity details.

```xml
<integration id="INT-API-001" name="Payment Gateway" protocol="REST" confidence="high">
  <description>External payment processing via Stripe API</description>
  <endpoint>https://api.stripe.com/v1/charges</endpoint>
  <direction>outbound</direction>
  <data-format>JSON</data-format>
  <authentication>API key</authentication>
  <source file="src/service/PaymentService.java" line-start="40" line-end="65">
    <snippet>restTemplate.postForObject(STRIPE_URL, chargeRequest, ChargeResponse.class);</snippet>
  </source>
</integration>
```

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string | Yes | Unique integration identifier |
| `name` | string | Yes | Human-readable integration name |
| `protocol` | string | Yes | Communication protocol |
| `confidence` | ConfidenceType | Yes | Extraction confidence level |

#### Protocol Values

| Value | Description |
|-------|-------------|
| `REST` | RESTful HTTP API |
| `SOAP` | SOAP web service |
| `gRPC` | gRPC remote procedure call |
| `JDBC` | Java database connectivity |
| `JMS` | Java message service |
| `file` | File-based integration |
| `custom` | Custom or proprietary protocol |

### `<description>` (integration)

Human-readable description of the integration purpose and target system.

### `<endpoint>`

URL or connection string for the external system.

### `<direction>`

Direction of data flow in the integration.

| Value | Description |
|-------|-------------|
| `inbound` | Receiving data from external system |
| `outbound` | Sending data to external system |
| `bidirectional` | Two-way data exchange |

### `<data-format>`

Data serialization format used (e.g., `JSON`, `XML`, `Protobuf`, `CSV`).

### `<authentication>`

Optional authentication mechanism used (e.g., `API key`, `OAuth2`, `Basic`, `mTLS`).

### `<patterns>`

Container for design pattern items.

```xml
<patterns count="8">
  <pattern>...</pattern>
</patterns>
```

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `count` | integer | Yes | Number of pattern items in this container |

### `<pattern>`

Individual design pattern occurrence with implementation details.

```xml
<pattern id="DP-SING-001" name="Service Locator" pattern-type="creational" confidence="high">
  <description>Centralized registry for service instances used throughout the application</description>
  <implementation-notes>Uses static HashMap to store service references, initialized at startup</implementation-notes>
  <affected-components>
    <component-ref id="ARCH-WEB-001"/>
  </affected-components>
  <source file="src/core/ServiceLocator.java" line-start="1" line-end="45">
    <snippet>public class ServiceLocator { private static Map&lt;Class, Object&gt; services = new HashMap&lt;&gt;();</snippet>
  </source>
</pattern>
```

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string | Yes | Unique pattern identifier |
| `name` | string | Yes | Design pattern name |
| `pattern-type` | string | Yes | Pattern classification |
| `confidence` | ConfidenceType | Yes | Extraction confidence level |

#### Pattern Type Values

| Value | Description |
|-------|-------------|
| `creational` | Object creation patterns |
| `structural` | Object composition patterns |
| `behavioral` | Object interaction patterns |
| `architectural` | System-level patterns |
| `concurrency` | Multi-threading patterns |

### `<description>` (pattern)

Human-readable description of how the pattern is used in the codebase.

### `<implementation-notes>`

Details about the specific implementation of the pattern, including any deviations from the canonical form.

### `<affected-components>`

List of architectural components that participate in or are affected by this pattern.

```xml
<affected-components>
  <component-ref id="ARCH-WEB-001"/>
  <component-ref id="ARCH-SVC-002"/>
</affected-components>
```

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string | Yes | Referenced component ID |

### `<source>`

Source code location where the item was identified. Uses the canonical format defined in the [Common Extraction Schema](./common-schema.md#source-references). The optional `<snippet>` child element contains the relevant code.

## Common Categories

### Component Categories

| Category | Description | Examples |
|----------|-------------|----------|
| `WEB` | Web tier | Controllers, REST endpoints, servlets |
| `SVC` | Service tier | Business services, domain logic |
| `DAO` | Data access | Repositories, DAOs, mappers |
| `MSG` | Messaging | Message producers, consumers, brokers |
| `CACHE` | Caching | Cache managers, cache layers |
| `SEC` | Security | Auth filters, security interceptors |

### Integration Categories

| Category | Description | Examples |
|----------|-------------|----------|
| `API` | External APIs | REST clients, SOAP consumers |
| `DB` | Databases | JDBC connections, ORM configurations |
| `MSG` | Message queues | JMS, RabbitMQ, Kafka connections |
| `FILE` | File systems | FTP, SFTP, local file I/O |
| `LDAP` | Directory services | LDAP, Active Directory |

### Pattern Categories

| Category | Description | Examples |
|----------|-------------|----------|
| `SING` | Singleton | Single-instance services |
| `FACT` | Factory | Object creation factories |
| `OBS` | Observer | Event listeners, pub/sub |
| `MVC` | Model-View-Controller | MVC framework usage |
| `REP` | Repository | Data access abstraction |
| `STRAT` | Strategy | Interchangeable algorithms |

## Example Output

```xml
<?xml version="1.0" encoding="UTF-8"?>
<architecture xmlns="http://reforge.dev/schema/extraction"
              project-id="ecommerce-legacy" version="1.0.0"
              schema-version="1.0.0"
              generated="2024-01-15T10:30:00Z">

  <metadata>
    <total-count>3</total-count>
    <confidence-distribution>
      <high>3</high>
      <medium>0</medium>
      <low>0</low>
    </confidence-distribution>
    <extraction-timestamp>2024-01-15T10:30:00Z</extraction-timestamp>
  </metadata>

  <components count="1">
    <component id="ARCH-WEB-001" name="Order API" layer="presentation" confidence="high">
      <description>REST API layer handling order CRUD operations</description>
      <technology>Spring MVC</technology>
      <responsibilities>
        <responsibility>Handle HTTP requests for order operations</responsibility>
        <responsibility>Input validation and response formatting</responsibility>
      </responsibilities>
      <source file="src/controller/OrderController.java" line-start="1" line-end="150"/>
    </component>
  </components>

  <integrations count="1">
    <integration id="INT-API-001" name="Payment Gateway" protocol="REST" confidence="high">
      <description>External payment processing via Stripe API</description>
      <endpoint>https://api.stripe.com/v1/charges</endpoint>
      <direction>outbound</direction>
      <data-format>JSON</data-format>
      <authentication>API key</authentication>
      <source file="src/service/PaymentService.java" line-start="40" line-end="65">
        <snippet>restTemplate.postForObject(STRIPE_URL, chargeRequest, ChargeResponse.class);</snippet>
      </source>
    </integration>
  </integrations>

  <patterns count="1">
    <pattern id="DP-SING-001" name="Service Locator" pattern-type="creational" confidence="high">
      <description>Centralized registry for service instances used throughout the application</description>
      <implementation-notes>Uses static HashMap to store service references, initialized at startup</implementation-notes>
      <affected-components>
        <component-ref id="ARCH-WEB-001"/>
      </affected-components>
      <source file="src/core/ServiceLocator.java" line-start="1" line-end="45">
        <snippet>public class ServiceLocator { private static Map&lt;Class, Object&gt; services = new HashMap&lt;&gt;();</snippet>
      </source>
    </pattern>
  </patterns>

</architecture>
```

## Related Schemas

- [Common Schema](./common-schema.md) — Shared elements (root attributes, metadata, source references, confidence)
- [dependencies.md](./dependencies.md) — Module dependencies between architectural components
- [call-sites.md](./call-sites.md) — Method calls across architectural boundaries
