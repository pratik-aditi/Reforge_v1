# UI Flows Schema

> Defines the structure for UI components and layouts (`ui-flows.xml`)

## Overview

The UI flows schema captures user interface components and navigation patterns extracted by `/reforge.extract ui`. It includes screen definitions, component hierarchies, event handlers, and navigation flows.

## Root Element

```xml
<ui-flows project-id="my-app" version="1.0.0" generated="2024-01-15T10:30:00Z">
  <screens>...</screens>
  <navigation>...</navigation>
</ui-flows>
```

### Attributes

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `project-id` | string | Yes | Reference to analysis project |
| `version` | string | Yes | Schema version |
| `generated` | dateTime | Yes | Extraction timestamp |

## Elements

### `<screens>`

Collection of discovered UI screens/pages.

```xml
<screens count="12">
  <screen>...</screen>
</screens>
```

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `count` | integer | Yes | Total screens discovered |

### `<screen>`

Individual screen or page definition.

```xml
<screen id="SCR-001" name="Order List" path="/orders">
  <layout rows="20" columns="80">
    <ascii>
+------------------------------------------+
|  [Logo]     Search: [________] [Search]  |
+------------------------------------------+
| Orders                          [+ New]  |
+------------------------------------------+
| ID  | Customer    | Total  | Status      |
|-----|-------------|--------|-------------|
| 001 | Acme Corp   | $500   | Pending     |
| 002 | Beta Inc    | $1200  | Shipped     |
+------------------------------------------+
| [<< Prev]              Page 1    [Next >>]|
+------------------------------------------+
    </ascii>
  </layout>
  <components count="8">
    <component>...</component>
  </components>
  <source file="src/views/OrderList.jsp" line-start="1" line-end="150"/>
</screen>
```

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string | Yes | Unique screen identifier |
| `name` | string | Yes | Human-readable screen name |
| `path` | string | No | URL path or route |

### `<layout>`

ASCII art representation of the screen layout.

```xml
<layout rows="20" columns="80">
  <ascii>...</ascii>
</layout>
```

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `rows` | integer | No | Layout height in rows |
| `columns` | integer | No | Layout width in columns |

### `<components>`

Collection of UI components on a screen.

```xml
<components count="5">
  <component>...</component>
</components>
```

### `<component>`

Individual UI component.

```xml
<component id="CMP-001" type="button" name="submitBtn" label="Submit Order" confidence="high">
  <position row="15" column="60" parent="orderForm"/>
  <events>
    <event type="click" handler="submitOrder" workflow-ref="WF-001"/>
  </events>
  <source file="src/views/OrderForm.jsp" line-start="45" line-end="48"/>
</component>
```

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string | Yes | Unique component identifier |
| `type` | ComponentTypeEnum | Yes | Type of UI component |
| `name` | string | No | Component name/ID in code |
| `label` | string | No | Display label |
| `confidence` | ConfidenceType | Yes | Extraction confidence |

#### ComponentTypeEnum

| Value | Description |
|-------|-------------|
| `button` | Clickable button |
| `input` | Text input field |
| `form` | Form container |
| `table` | Data table/grid |
| `label` | Text label |
| `link` | Hyperlink |
| `container` | Generic container/div |
| `dropdown` | Select/dropdown |
| `checkbox` | Checkbox input |
| `radio` | Radio button |
| `textarea` | Multi-line text |
| `image` | Image element |
| `menu` | Navigation menu |

### `<position>`

Component position within layout.

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `row` | integer | No | Row position |
| `column` | integer | No | Column position |
| `parent` | string | No | Parent component ID |

### `<events>`

Event handlers attached to a component.

```xml
<events>
  <event type="click" handler="submitOrder" workflow-ref="WF-001"/>
  <event type="change" handler="validateField"/>
</events>
```

### `<event>`

Individual event handler.

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `type` | string | Yes | Event type (click, change, submit, etc.) |
| `handler` | string | Yes | Handler function/method name |
| `workflow-ref` | string | No | Reference to triggered workflow |

### `<navigation>`

Screen-to-screen navigation flows.

```xml
<navigation>
  <flow from-screen="SCR-001" to-screen="SCR-002" trigger="click:newOrderBtn"/>
  <flow from-screen="SCR-002" to-screen="SCR-003" trigger="submit" condition="validation.passed"/>
</navigation>
```

### `<flow>`

Individual navigation path.

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `from-screen` | string | Yes | Source screen ID |
| `to-screen` | string | Yes | Destination screen ID |
| `trigger` | string | No | What triggers navigation |
| `condition` | string | No | Conditional navigation logic |

## Shared Types

### ConfidenceType

| Value | Description |
|-------|-------------|
| `high` | Component clearly identified |
| `medium` | Component detected but may need verification |
| `low` | Possible component, requires human review |

## ASCII Layout Conventions

ASCII layouts use consistent symbols:

| Symbol | Meaning |
|--------|---------|
| `+---+` | Border corners and edges |
| `\|` | Vertical borders |
| `[Button]` | Buttons |
| `[____]` | Input fields |
| `(o)` | Radio buttons |
| `[x]` | Checkboxes |
| `v` | Dropdown indicator |

## Example Output

```xml
<?xml version="1.0" encoding="UTF-8"?>
<ui-flows xmlns="http://reforge.dev/schema/ui-flows"
          project-id="ecommerce-legacy" version="1.0.0"
          generated="2024-01-15T10:30:00Z">

  <screens count="2">
    <screen id="SCR-001" name="Order List" path="/orders">
      <layout rows="15" columns="60">
        <ascii>
+----------------------------------------------------------+
| Orders                                    [+ New Order]  |
+----------------------------------------------------------+
| ID   | Customer      | Total    | Actions               |
|------|---------------|----------|------------------------|
| #001 | Acme Corp     | $500.00  | [View] [Edit]         |
| #002 | Beta Inc      | $1,200   | [View] [Edit]         |
+----------------------------------------------------------+
        </ascii>
      </layout>
      <components count="3">
        <component id="CMP-001" type="button" name="newOrderBtn"
                   label="+ New Order" confidence="high">
          <events>
            <event type="click" handler="navigateToNewOrder"/>
          </events>
          <source file="src/views/orders/list.jsp" line-start="15" line-end="17"/>
        </component>
        <component id="CMP-002" type="table" name="ordersTable" confidence="high">
          <source file="src/views/orders/list.jsp" line-start="20" line-end="45"/>
        </component>
      </components>
      <source file="src/views/orders/list.jsp" line-start="1" line-end="60"/>
    </screen>

    <screen id="SCR-002" name="New Order Form" path="/orders/new">
      <components count="5">
        <component id="CMP-010" type="form" name="orderForm" confidence="high">
          <source file="src/views/orders/new.jsp" line-start="10" line-end="80"/>
        </component>
        <component id="CMP-011" type="button" name="submitBtn"
                   label="Submit" confidence="high">
          <position parent="orderForm"/>
          <events>
            <event type="click" handler="submitOrder" workflow-ref="WF-001"/>
          </events>
          <source file="src/views/orders/new.jsp" line-start="75" line-end="77"/>
        </component>
      </components>
      <source file="src/views/orders/new.jsp" line-start="1" line-end="85"/>
    </screen>
  </screens>

  <navigation>
    <flow from-screen="SCR-001" to-screen="SCR-002" trigger="click:newOrderBtn"/>
    <flow from-screen="SCR-002" to-screen="SCR-001" trigger="submit" condition="success"/>
  </navigation>

</ui-flows>
```

## Related Schemas

- [analysis.md](./analysis.md) — Codebase inventory
- [workflows.md](./workflows.md) — UI triggers workflows
- [business-rules.md](./business-rules.md) — UI validation rules

## Contract Reference

Based on: `specs/001-legacy-analyzer/contracts/ui-flows.xsd`
