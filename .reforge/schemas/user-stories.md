# User Stories Schema

> Defines the structure for generated modernization user stories (`user-stories.xml`)

## Overview

The user stories schema captures generated user stories created by `/reforge.generate user-stories`. Stories are derived from extracted business rules, workflows, and UI components, with full traceability back to source artifacts.

## Root Element

```xml
<user-stories project-id="my-app" version="1.0.0"
              generated="2024-01-15T10:30:00Z"
              epic-count="5" story-count="25">
  <epic>...</epic>
  <story>...</story>
</user-stories>
```

### Attributes

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `project-id` | string | Yes | Reference to analysis project |
| `version` | string | Yes | Schema version |
| `generated` | dateTime | Yes | Generation timestamp |
| `epic-count` | integer | Yes | Total epics generated |
| `story-count` | integer | Yes | Total stories generated |

## Elements

### `<epic>`

Groups related user stories into a larger feature area.

```xml
<epic id="EPIC-001" title="Order Management" priority="high">
  <description>All functionality related to creating, viewing, and managing customer orders</description>
  <stories>
    <story-ref>US-001</story-ref>
    <story-ref>US-002</story-ref>
    <story-ref>US-003</story-ref>
  </stories>
  <traceability>
    <workflow id="WF-001" confidence="high"/>
    <workflow id="WF-002" confidence="high"/>
    <ui-component id="SCR-001" confidence="high"/>
  </traceability>
</epic>
```

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string | Yes | Unique epic identifier |
| `title` | string | Yes | Epic title |
| `priority` | PriorityType | Yes | Business priority |

### `<story>`

Individual user story in standard format.

```xml
<story id="US-001" title="Submit New Order" priority="high"
       epic-ref="EPIC-001" story-points="5">
  <as-a>Customer</as-a>
  <i-want>to submit a new order with my selected items</i-want>
  <so-that>I can purchase products from the store</so-that>

  <acceptance-criteria>
    <criterion id="AC-001" source-ref="BR-001">
      <given>I have items in my cart totaling over $100</given>
      <when>I submit the order</when>
      <then>a 10% discount should be applied to my total</then>
    </criterion>
    <criterion id="AC-002" source-ref="BR-002">
      <given>I have an empty cart</given>
      <when>I try to submit an order</when>
      <then>I should see an error message requiring at least one item</then>
    </criterion>
  </acceptance-criteria>

  <traceability>
    <business-rule id="BR-001" confidence="high"/>
    <business-rule id="BR-002" confidence="high"/>
    <workflow id="WF-001" confidence="high"/>
    <ui-component id="CMP-011" confidence="high"/>
    <database-op id="DB-002" confidence="high"/>
  </traceability>

  <notes>Original system uses synchronous order processing; consider async for modernization</notes>
</story>
```

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string | Yes | Unique story identifier |
| `title` | string | Yes | Story title |
| `priority` | PriorityType | Yes | Business priority |
| `epic-ref` | string | No | Parent epic reference |
| `story-points` | integer | No | Estimated complexity |

### Story Components

#### `<as-a>`
The user role or persona.

#### `<i-want>`
The desired action or capability.

#### `<so-that>`
The business value or outcome.

### `<acceptance-criteria>`

Collection of testable criteria.

```xml
<acceptance-criteria>
  <criterion>...</criterion>
</acceptance-criteria>
```

### `<criterion>`

Individual acceptance criterion in Given-When-Then format.

```xml
<criterion id="AC-001" source-ref="BR-001">
  <given>a precondition or context</given>
  <when>an action is performed</when>
  <then>an expected outcome occurs</then>
</criterion>
```

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string | Yes | Unique criterion identifier |
| `source-ref` | string | No | Reference to source artifact (rule, workflow) |

### `<traceability>`

Links story back to extracted artifacts.

```xml
<traceability>
  <business-rule id="BR-001" confidence="high"/>
  <workflow id="WF-001" confidence="high"/>
  <ui-component id="CMP-011" confidence="medium"/>
  <database-op id="DB-002" confidence="high"/>
</traceability>
```

Each element type:

| Element | Description |
|---------|-------------|
| `<business-rule>` | Reference to extracted business rule |
| `<workflow>` | Reference to extracted workflow |
| `<ui-component>` | Reference to UI component |
| `<database-op>` | Reference to database interaction |

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string | Yes | Referenced artifact ID |
| `confidence` | string | No | Traceability confidence |

### `<notes>`

Optional free-form notes about modernization considerations, technical debt, or implementation hints.

## Type Definitions

### PriorityType

| Value | Description |
|-------|-------------|
| `critical` | Must-have for go-live |
| `high` | Important for initial release |
| `medium` | Desired for initial release |
| `low` | Can be deferred |

## Example Output

```xml
<?xml version="1.0" encoding="UTF-8"?>
<user-stories xmlns="http://reforge.dev/schema/user-stories"
              project-id="ecommerce-legacy" version="1.0.0"
              generated="2024-01-15T10:30:00Z"
              epic-count="1" story-count="2">

  <epic id="EPIC-001" title="Order Management" priority="high">
    <description>Core order creation and management functionality</description>
    <stories>
      <story-ref>US-001</story-ref>
      <story-ref>US-002</story-ref>
    </stories>
    <traceability>
      <workflow id="WF-001" confidence="high"/>
      <ui-component id="SCR-001" confidence="high"/>
      <ui-component id="SCR-002" confidence="high"/>
    </traceability>
  </epic>

  <story id="US-001" title="Create New Order" priority="high"
         epic-ref="EPIC-001" story-points="5">
    <as-a>Customer</as-a>
    <i-want>to submit a new order with my selected products</i-want>
    <so-that>I can purchase items and have them delivered</so-that>

    <acceptance-criteria>
      <criterion id="AC-001" source-ref="BR-001">
        <given>I have a cart with items totaling over $100</given>
        <when>I complete checkout</when>
        <then>a 10% discount is automatically applied</then>
      </criterion>
      <criterion id="AC-002" source-ref="BR-002">
        <given>I have an empty shopping cart</given>
        <when>I attempt to checkout</when>
        <then>I see an error requiring at least one item</then>
      </criterion>
      <criterion id="AC-003">
        <given>I have completed a valid order</given>
        <when>the order is submitted</when>
        <then>I receive an order confirmation email</then>
      </criterion>
    </acceptance-criteria>

    <traceability>
      <business-rule id="BR-001" confidence="high"/>
      <business-rule id="BR-002" confidence="high"/>
      <workflow id="WF-001" confidence="high"/>
      <ui-component id="CMP-011" confidence="high"/>
      <database-op id="DB-002" confidence="high"/>
    </traceability>

    <notes>Legacy uses synchronous processing. Modern implementation should use async order queue.</notes>
  </story>

  <story id="US-002" title="View Order History" priority="medium"
         epic-ref="EPIC-001" story-points="3">
    <as-a>Customer</as-a>
    <i-want>to view my past orders</i-want>
    <so-that>I can track deliveries and reorder products</so-that>

    <acceptance-criteria>
      <criterion id="AC-004">
        <given>I am logged in as a customer</given>
        <when>I navigate to my order history</when>
        <then>I see a list of all my past orders with status</then>
      </criterion>
      <criterion id="AC-005">
        <given>I am viewing my order history</given>
        <when>I click on an order</when>
        <then>I see the full order details including items and tracking</then>
      </criterion>
    </acceptance-criteria>

    <traceability>
      <ui-component id="SCR-001" confidence="high"/>
      <database-op id="DB-001" confidence="high"/>
    </traceability>
  </story>

</user-stories>
```

## Output Formats

The `/reforge.generate user-stories` command can produce multiple output formats:

| Format | File | Description |
|--------|------|-------------|
| Markdown | `user-stories.md` | Human-readable documentation |
| JSON | `user-stories.json` | Machine-readable for import tools |
| CSV | `user-stories.csv` | Spreadsheet-compatible |

## Related Schemas

- [business-rules.md](./business-rules.md) — Source for acceptance criteria
- [workflows.md](./workflows.md) — Source for user journeys
- [ui-flows.md](./ui-flows.md) — Source for screen-based stories
- [database.md](./database.md) — Data-related stories

## Contract Reference

Based on: `specs/001-legacy-analyzer/contracts/user-stories.xsd`
