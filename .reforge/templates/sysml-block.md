# SysML Block Diagram Template

> Template for generating SysML block definition diagrams (BDD) for system architecture visualization

## Overview

SysML Block Definition Diagrams are used to show system structure, including:
- Major system components (blocks)
- Component properties and operations
- Relationships between components
- Data flows and interfaces

## Template Variables

| Variable | Source | Description |
|----------|--------|-------------|
| `{{project.name}}` | Analysis | Project name |
| `{{modules}}` | Analysis | System modules/components |
| `{{workflows}}` | Workflow extraction | Process flows |
| `{{interfaces}}` | Inferred | Module interfaces |

## PlantUML SysML Template

```plantuml
@startuml {{project.name}}-bdd
!include <sysml/common>

title {{project.name}} - Block Definition Diagram

{{#each modules}}
block "{{this.name}}" as {{this.id}} <<block>> {
  {{#each this.properties}}
  part {{this.name}} : {{this.type}}
  {{/each}}
  {{#each this.operations}}
  op {{this.name}}({{this.params}}) : {{this.return_type}}
  {{/each}}
}

{{/each}}

' Compositions
{{#each compositions}}
{{this.parent}} *-- {{this.child}} : contains
{{/each}}

' Associations
{{#each associations}}
{{this.from}} --> {{this.to}} : {{this.label}}
{{/each}}

' Flow ports
{{#each interfaces}}
{{this.block}} : port {{this.name}} : {{this.type}}
{{/each}}

@enduml
```

## Mermaid Block Diagram Template

Since Mermaid doesn't have native SysML support, we use a block diagram approximation:

```mermaid
block-beta
    columns 3

{{#each modules}}
    {{this.id}}["{{this.name}}"]
{{/each}}

{{#each compositions}}
    {{this.parent}} --> {{this.child}}
{{/each}}
```

## SysML Notation Reference

### Block Stereotypes

| Stereotype | Symbol | Description |
|------------|--------|-------------|
| `<<block>>` | Standard block | System component |
| `<<constraint>>` | Constraint block | Rules/constraints |
| `<<interface>>` | Interface | External interface |
| `<<valueType>>` | Value type | Data type definition |

### Relationship Types

| Type | Notation | Description |
|------|----------|-------------|
| Composition | `*--` | Strong containment |
| Association | `-->` | Reference relationship |
| Generalization | `<\|--` | Inheritance |
| Dependency | `..>` | Uses relationship |

### Ports and Flows

| Element | Description |
|---------|-------------|
| Flow port | Data/control flow interface |
| Standard port | Service interface |
| Item flow | Data flowing between ports |

## Example Output

### System Context

```plantuml
@startuml ecommerce-bdd
!theme plain
skinparam linetype ortho

title E-Commerce System - Block Definition Diagram

package "E-Commerce System" <<block>> {

  block "Order Management" as OM <<block>> {
    part orderProcessor : OrderProcessor
    part discountEngine : DiscountEngine
    --
    op createOrder(items) : Order
    op calculateTotal(order) : Decimal
  }

  block "Customer Management" as CM <<block>> {
    part customerRepo : CustomerRepository
    part authService : AuthService
    --
    op authenticate(creds) : Token
    op getCustomer(id) : Customer
  }

  block "Inventory Management" as IM <<block>> {
    part stockManager : StockManager
    part warehouseSync : WarehouseSync
    --
    op checkStock(product) : Integer
    op reserveStock(items) : Boolean
  }

  block "Payment Processing" as PP <<block>> {
    part paymentGateway : PaymentGateway
    part refundHandler : RefundHandler
    --
    op processPayment(order) : Result
    op refund(order) : Result
  }

  block "Notification Service" as NS <<block>> {
    part emailSender : EmailSender
    part smsSender : SMSSender
    --
    op sendOrderConfirmation(order) : void
    op sendShipmentUpdate(order) : void
  }
}

' Internal flows
OM --> CM : validates customer
OM --> IM : reserves inventory
OM --> PP : processes payment
OM --> NS : triggers notifications
PP --> NS : payment notifications

' External interfaces
cloud "Payment Provider" as ext_pay
cloud "Warehouse System" as ext_wh
cloud "Email Service" as ext_email

PP --> ext_pay : <<interface>>
IM --> ext_wh : <<interface>>
NS --> ext_email : <<interface>>

@enduml
```

### Module Detail

```plantuml
@startuml order-management-detail
!theme plain

title Order Management - Internal Block Diagram

block "Order Management" <<block>> {

  block "Order Processor" <<block>> {
    port orderIn : Order
    port orderOut : ProcessedOrder
    --
    op validateOrder()
    op applyDiscounts()
    op calculateTax()
  }

  block "Discount Engine" <<block>> {
    port orderTotal : Decimal
    port discount : Decimal
    --
    op evaluateRules()
  }

  block "Order Repository" <<block>> {
    port query : OrderQuery
    port result : Order[]
    --
    op save()
    op findById()
  }
}

"Order Processor" --> "Discount Engine" : requests discount
"Order Processor" --> "Order Repository" : persists

@enduml
```

## Generation Guidelines

When generating SysML diagrams:

1. **Identify system boundaries** - What's in scope vs external
2. **Map workflows to blocks** - Each major workflow may indicate a block
3. **Extract operations** - Entry points from workflows become block operations
4. **Identify data flows** - Database interactions show data movement
5. **Map external calls** - These become interface blocks
6. **Group by domain** - Related blocks should be packaged together

### Source-Anchored Generation (Mandatory)

All generated SysML diagrams MUST comply with the Source-Anchored Generation constraints
defined in Step 0.6 of `.reforge/commands/generate.md`. Key obligations:

1. Extraction XML is the sole source of truth for all diagram content
2. All identifiers (block names, operation names, port names) MUST be copied verbatim from extraction XML
3. All statistics (block counts, operation counts) MUST be computed with visible derivation formulas
4. `[DATA GAP]` markers MUST replace any content not supported by extraction data
5. Provenance annotations MUST cite extraction source files and element counts
6. The Content Validation Checklist MUST be completed before finalizing any diagram output
7. The agent MUST NOT read source code files directly — all source context comes from extraction XML

## Mapping from Reforge Extractions

| Reforge Element | SysML Element |
|-----------------|---------------|
| Analysis module | Block |
| Workflow entry point | Block operation |
| Database entity | Part (value type) |
| External API call | Interface block |
| Business rule | Constraint block |
| UI screen | Port (user interface) |
