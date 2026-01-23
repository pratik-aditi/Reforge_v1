# Workflows Schema

> Defines the structure for process flows and execution paths (`workflows.xml`)

## Overview

The workflows schema captures business process flows extracted by `/reforge.extract workflows`. It documents execution paths, decision points, and cross-references to related components.

## Root Element

```xml
<workflows project-id="my-app" version="1.0.0"
           generated="2024-01-15T10:30:00Z" count="15">
  <workflow>...</workflow>
</workflows>
```

### Attributes

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `project-id` | string | Yes | Reference to analysis project |
| `version` | string | Yes | Schema version |
| `generated` | dateTime | Yes | Extraction timestamp |
| `count` | integer | Yes | Total workflows discovered |

## Elements

### `<workflow>`

Individual workflow definition.

```xml
<workflow id="WF-001" name="Order Submission"
          entry-point="OrderController.submit"
          trigger-type="ui-action" confidence="high">
  <description>Handles new order submission from checkout</description>
  <steps>...</steps>
  <source file="src/controller/OrderController.java" line-start="45" line-end="120"/>
  <related>
    <ui-component>CMP-011</ui-component>
    <business-rule>BR-001</business-rule>
    <database-interaction>DB-001</database-interaction>
  </related>
</workflow>
```

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string | Yes | Unique workflow identifier |
| `name` | string | Yes | Human-readable workflow name |
| `entry-point` | string | Yes | Starting method/function |
| `trigger-type` | TriggerTypeEnum | Yes | What initiates the workflow |
| `confidence` | ConfidenceType | Yes | Extraction confidence |

#### TriggerTypeEnum

| Value | Description |
|-------|-------------|
| `ui-action` | Triggered by user interaction |
| `api-call` | Triggered by API request |
| `scheduled` | Triggered by scheduler/cron |
| `message` | Triggered by message/event |
| `startup` | Triggered on application start |
| `event` | Triggered by domain event |

### `<description>`

Human-readable description of the workflow's purpose and behavior.

### `<steps>`

Ordered collection of workflow steps.

```xml
<steps>
  <step sequence="1" type="validation" method="validateOrder" class="OrderValidator">
    <description>Validate order data and business rules</description>
    <source file="src/validator/OrderValidator.java" line-start="25" line-end="45"/>
  </step>
  <step sequence="2" type="decision" condition="order.isValid()">
    <description>Check if order passed validation</description>
    <branches>
      <branch condition="true" label="Valid">
        <step sequence="1" type="data-access" sql-ref="DB-002">
          <description>Save order to database</description>
        </step>
      </branch>
      <branch condition="false" label="Invalid">
        <step sequence="1" type="notification">
          <description>Return validation errors</description>
        </step>
      </branch>
    </branches>
  </step>
</steps>
```

### `<step>`

Individual workflow step.

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `sequence` | integer | Yes | Step order (1-based) |
| `type` | StepTypeEnum | Yes | Type of step |
| `method` | string | No | Method name if applicable |
| `class` | string | No | Class name if applicable |
| `condition` | string | No | Condition expression |
| `sql-ref` | string | No | Reference to database interaction |
| `rule-ref` | string | No | Reference to business rule |

#### StepTypeEnum

| Value | Description |
|-------|-------------|
| `method-call` | Invokes a method/function |
| `decision` | Conditional branching point |
| `loop` | Iteration over collection |
| `data-access` | Database read/write |
| `external-call` | External service/API call |
| `validation` | Input/state validation |
| `transformation` | Data transformation |
| `notification` | Alert/message sending |

### `<branches>`

Conditional branches for decision steps.

```xml
<branches>
  <branch condition="status == 'approved'" label="Approved Path">
    <step>...</step>
  </branch>
  <branch condition="status == 'rejected'" label="Rejected Path">
    <step>...</step>
  </branch>
</branches>
```

### `<branch>`

Individual branch path.

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `condition` | string | Yes | Branch condition |
| `label` | string | No | Human-readable branch name |

### `<related>`

Cross-references to related extraction elements.

```xml
<related>
  <ui-component>CMP-001</ui-component>
  <ui-component>CMP-002</ui-component>
  <business-rule>BR-001</business-rule>
  <business-rule>BR-003</business-rule>
  <database-interaction>DB-001</database-interaction>
</related>
```

## Shared Types

### ConfidenceType

| Value | Description |
|-------|-------------|
| `high` | Workflow clearly traced through code |
| `medium` | Workflow identified but path may vary |
| `low` | Possible workflow, dynamic/reflection-based |

## Example Output

```xml
<?xml version="1.0" encoding="UTF-8"?>
<workflows xmlns="http://reforge.dev/schema/workflows"
           project-id="ecommerce-legacy" version="1.0.0"
           generated="2024-01-15T10:30:00Z" count="2">

  <workflow id="WF-001" name="Order Submission"
            entry-point="OrderController.submitOrder"
            trigger-type="ui-action" confidence="high">
    <description>Processes customer order submission from checkout page</description>
    <steps>
      <step sequence="1" type="validation" method="validate" class="OrderValidator">
        <description>Validate order data including items and customer info</description>
        <source file="src/validator/OrderValidator.java" line-start="20" line-end="45"/>
      </step>

      <step sequence="2" type="decision" condition="validationResult.isValid()">
        <description>Check validation result</description>
        <branches>
          <branch condition="true" label="Valid Order">
            <step sequence="1" type="method-call" method="calculateTotal" class="PricingService">
              <description>Calculate order total with discounts</description>
              <rule-ref>BR-001</rule-ref>
            </step>
            <step sequence="2" type="data-access" sql-ref="DB-002">
              <description>Persist order to database</description>
            </step>
            <step sequence="3" type="notification">
              <description>Send order confirmation email</description>
            </step>
          </branch>
          <branch condition="false" label="Invalid Order">
            <step sequence="1" type="notification">
              <description>Return validation errors to user</description>
            </step>
          </branch>
        </branches>
      </step>
    </steps>
    <source file="src/controller/OrderController.java" line-start="50" line-end="95"/>
    <related>
      <ui-component>CMP-011</ui-component>
      <business-rule>BR-001</business-rule>
      <business-rule>BR-002</business-rule>
      <database-interaction>DB-002</database-interaction>
    </related>
  </workflow>

  <workflow id="WF-002" name="Daily Inventory Sync"
            entry-point="InventoryJob.execute"
            trigger-type="scheduled" confidence="high">
    <description>Nightly job to sync inventory levels with warehouse system</description>
    <steps>
      <step sequence="1" type="external-call" method="fetchInventory">
        <description>Fetch current inventory from warehouse API</description>
      </step>
      <step sequence="2" type="loop" condition="foreach product in inventory">
        <description>Update each product's stock level</description>
        <step sequence="1" type="data-access" sql-ref="DB-010">
          <description>Update product stock in database</description>
        </step>
      </step>
      <step sequence="3" type="notification">
        <description>Send sync completion report</description>
      </step>
    </steps>
    <source file="src/job/InventoryJob.java" line-start="30" line-end="80"/>
    <related>
      <database-interaction>DB-010</database-interaction>
    </related>
  </workflow>

</workflows>
```

## Related Schemas

- [analysis.md](./analysis.md) — Codebase inventory
- [business-rules.md](./business-rules.md) — Rules referenced in steps
- [database.md](./database.md) — Data access steps
- [ui-flows.md](./ui-flows.md) — UI triggers workflows
- [user-stories.md](./user-stories.md) — Workflows trace to stories

## Contract Reference

Based on: `specs/001-legacy-analyzer/contracts/workflows.xsd`
