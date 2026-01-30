# /reforge.extract

> Extract specific elements from analyzed codebase

## Command Syntax

```
/reforge.extract <type> [--files <pattern>] [--confidence <level>]
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `type` | Yes | Extraction type: `business-rules`, `database`, `ui`, `workflows` |
| `--files` | No | Limit extraction to files matching pattern |
| `--confidence` | No | Minimum confidence threshold: `high`, `medium`, `low` (default: all) |

## Overview

This command extracts specific types of information from the analyzed codebase:

- **business-rules**: Conditional logic, validations, calculations, business constraints
- **database**: SQL statements, data model, entity relationships
- **ui**: Screen definitions, components, layouts, navigation
- **workflows**: Execution paths, process flows, decision trees

## Prerequisites

- Analysis must be completed (`/reforge.analyze`)
- `$ANALYSIS_DIR/analysis.xml` must exist (where `$ANALYSIS_DIR = $PROJECT_OUTPUT_DIR/analysis`)

---

## Extraction Types

---

# Business Rules Extraction

## Command

```
/reforge.extract business-rules
```

## Workflow

### Step 0: Check Prerequisites

Run the prerequisites script to validate state and resolve paths:

```bash
reforge-scripts check-prerequisites --json --require-analysis
```

This returns JSON with resolved variables:
```json
{"PROJECT_NAME":"...","REPO_ROOT":"...","PROJECT_OUTPUT_DIR":"...","CONFIG":"...","ANALYSIS_STATUS":"completed","AVAILABLE_EXTRACTIONS":[...],"CHECKPOINT":null,"CLARIFICATIONS_DIR":"..."}
```

Use `$PROJECT_OUTPUT_DIR` for all output paths in subsequent steps.

Assign subdirectory variables:
```
$ANALYSIS_DIR = $PROJECT_OUTPUT_DIR/analysis
$EXTRACTIONS_DIR = $PROJECT_OUTPUT_DIR/extractions
```

### Step 0.5: Load Project Context

If `.reforge/memory/project-context.md` exists, read it now. Use its contents as
supplemental guidance throughout this command's execution:
- **Technology Stack**: Informs language/framework detection and pattern recognition
- **Domain Knowledge**: Provides business context for naming and categorization
- **Analysis Guidelines**: Directs focus and exclusions beyond config.json
- **Custom Rules**: Additional rules to follow alongside the constitution

### Step 1: Load Analysis

Read `$ANALYSIS_DIR/analysis.xml` to get:
- List of source files to process
- Language information for each file
- Component locations (classes, methods)

### Step 2: Scan for Business Logic Patterns

For each source file, identify:

#### Conditional Logic Patterns

```
IF/ELSE patterns:
  if (condition) { action }
  condition ? trueResult : falseResult
  when/case expressions

SWITCH patterns:
  switch (value) { case X: ... }
  match expressions
  pattern matching

GUARD patterns:
  if (!valid) throw/return
  assert statements
  require/ensure contracts
```

#### Validation Patterns

```
Input validation:
  if (input == null) throw ...
  if (input.isEmpty()) ...
  regex.match(input)

Range validation:
  if (value < MIN || value > MAX) ...
  value.between(min, max)

Format validation:
  isValidEmail(email)
  isValidPhone(phone)
  parseDate(date)
```

#### Calculation Patterns

```
Business calculations:
  total = subtotal + tax
  discount = price * discountRate
  interest = principal * rate * time

Aggregations:
  sum(), average(), count()
  groupBy, having
```

#### Constraint Patterns

```
Business constraints:
  if (inventory < orderQuantity) ...
  if (user.age < 18) ...
  if (!authorized) ...

State constraints:
  if (order.status != PENDING) ...
  if (account.isClosed()) ...
```

### Step 3: Extract Rule Details

For each identified pattern:

1. **Capture the rule logic:**
   - Extract the condition expression
   - Extract the action/consequence
   - Identify any else/default cases

2. **Determine confidence level:**
   - **High**: Clear business logic with descriptive names
   - **Medium**: Logic is clear but naming is generic
   - **Low**: Complex or unclear pattern, may need clarification

3. **Assign category:**
   - `validation`: Input/data validation rules
   - `pricing`: Price calculations, discounts
   - `authorization`: Access control, permissions
   - `calculation`: Business formulas, aggregations
   - `workflow`: State transitions, process rules
   - `notification`: Alert conditions, triggers
   - `constraint`: Business limits, restrictions

4. **Capture source reference:**
   - File path (relative)
   - Starting line number
   - Ending line number
   - Code snippet (if config allows)

5. **Identify related entities:**
   - Domain objects referenced
   - Database tables implied
   - Other rules that interact

### Step 4: Group Related Rules

- Group rules by domain entity (Order, Customer, Product, etc.)
- Identify rule dependencies and relationships
- Link rules that override or extend each other

### Step 5: Generate Output

Write to `$EXTRACTIONS_DIR/business-rules.xml`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<business-rules xmlns="http://reforge.dev/schema/business-rules"
                project-id="[project]" version="1.0.0"
                generated="[timestamp]" count="[total]">

  <rule id="BR-001" category="pricing" confidence="high">
    <description>Apply 10% discount for orders over $100</description>
    <logic>IF order.total > 100 THEN order.discount = order.total * 0.10</logic>
    <source file="src/service/PricingService.java" line-start="45" line-end="52">
      <snippet>if (order.getTotal().compareTo(new BigDecimal("100")) > 0) {
    order.setDiscount(order.getTotal().multiply(DISCOUNT_RATE));
}</snippet>
    </source>
    <entities>
      <entity>Order</entity>
    </entities>
    <related-rules>
      <rule-ref id="BR-002" relationship="overrides"/>
    </related-rules>
  </rule>

  <rule id="BR-002" category="validation" confidence="high">
    <description>Order must have at least one item</description>
    <logic>order.items.count MUST BE >= 1</logic>
    <source file="src/model/Order.java" line-start="78" line-end="82">
      <snippet>if (items == null || items.isEmpty()) {
    throw new ValidationException("Order must contain items");
}</snippet>
    </source>
    <entities>
      <entity>Order</entity>
      <entity>OrderItem</entity>
    </entities>
  </rule>

  <!-- More rules... -->

</business-rules>
```

### Step 6: Report Results

```
Business Rules Extraction Complete!

Output: $EXTRACTIONS_DIR/business-rules.xml

Summary:
- Total rules: 156
- By category:
  - Validation: 45
  - Pricing: 23
  - Authorization: 18
  - Calculation: 35
  - Workflow: 20
  - Constraint: 15
- Confidence levels:
  - High: 98 (63%)
  - Medium: 45 (29%)
  - Low: 13 (8%)

Low confidence items (may need clarification):
- BR-045: Unclear discount logic (src/pricing/Discount.java:78)
- BR-089: Magic number in validation (src/validate/OrderValidator.java:156)
...

Run /reforge.clarify to resolve ambiguous extractions.
```

---

# Database Extraction

## Command

```
/reforge.extract database
```

## Workflow

### Step 1: Load Analysis

Read `$ANALYSIS_DIR/analysis.xml` to identify:
- SQL files (.sql)
- Configuration files (persistence.xml, hibernate.cfg.xml)
- ORM entity files
- Source files with embedded SQL

### Step 2: Detect Data Model Sources

#### DDL Files

Look for SQL files containing:
```sql
CREATE TABLE ...
CREATE VIEW ...
ALTER TABLE ...
CREATE INDEX ...
```

#### ORM Configurations

**JPA/Hibernate:**
```java
@Entity
@Table(name = "...")
@Column(...)
@JoinColumn(...)
@ManyToOne, @OneToMany, @ManyToMany
```

**Entity Framework (.NET):**
```csharp
[Table("...")]
[Column("...")]
[ForeignKey("...")]
```

**Django:**
```python
class Model(models.Model):
    field = models.CharField(...)
    foreign = models.ForeignKey(...)
```

**ActiveRecord (Rails):**
```ruby
belongs_to :...
has_many :...
has_one :...
```

### Step 3: Extract Data Entities

For each discovered entity:

1. **Capture entity details:**
   - Name (table/class name)
   - Type: table, view, entity, dto
   - Source type: ddl, orm, inferred, config

2. **Extract columns:**
   - Column name
   - Data type
   - Nullable flag
   - Primary key flag
   - Foreign key reference

3. **Identify relationships:**
   - From entity and column
   - To entity and column
   - Relationship type: one-to-one, one-to-many, many-to-many

4. **Capture source reference:**
   - File path
   - Line numbers

5. **Assign confidence:**
   - **High**: Explicit DDL or ORM annotation
   - **Medium**: Inferred from naming conventions
   - **Low**: Guessed from query patterns

### Step 4: Scan for SQL Interactions

For each source file, find SQL patterns:

#### Direct SQL Strings

```java
// Java
String sql = "SELECT * FROM orders WHERE status = ?";
connection.prepareStatement("INSERT INTO orders ...");

// Python
cursor.execute("SELECT * FROM orders")
```

#### Query Annotations/Methods

```java
// JPA
@Query("SELECT o FROM Order o WHERE o.status = :status")

// MyBatis
<select id="findOrders">SELECT * FROM orders</select>

// Django ORM
Order.objects.filter(status='pending')
```

### Step 5: Extract Database Interactions

For each SQL statement:

1. **Parse operation type:**
   - SELECT, INSERT, UPDATE, DELETE, DDL, CALL

2. **Identify tables and columns:**
   - Parse SQL for table references
   - Extract column names used

3. **Capture execution context:**
   - Method name
   - Class name
   - Trigger/caller

4. **Capture source reference:**
   - File path
   - Line numbers
   - Code snippet

5. **Assign confidence:**
   - **High**: Static SQL clearly visible
   - **Medium**: Dynamic SQL with known patterns
   - **Low**: Complex dynamic SQL

### Step 6: Generate Output

Write to `$EXTRACTIONS_DIR/database.xml`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<database xmlns="http://reforge.dev/schema/database"
          project-id="[project]" version="1.0.0"
          generated="[timestamp]">

  <data-model entity-count="15">
    <entity id="E-001" name="orders" type="table"
            source-type="ddl" confidence="high">
      <column name="id" data-type="bigint" nullable="false" primary-key="true"/>
      <column name="customer_id" data-type="bigint" nullable="false"
              foreign-key="customers.id"/>
      <column name="total" data-type="decimal(10,2)" nullable="false"/>
      <column name="status" data-type="varchar(20)" nullable="false"/>
      <column name="created_at" data-type="timestamp" nullable="false"/>
      <source file="db/schema.sql" line-start="10" line-end="20"/>
    </entity>

    <entity id="E-002" name="customers" type="table"
            source-type="ddl" confidence="high">
      <column name="id" data-type="bigint" nullable="false" primary-key="true"/>
      <column name="name" data-type="varchar(100)" nullable="false"/>
      <column name="email" data-type="varchar(255)" nullable="false"/>
      <source file="db/schema.sql" line-start="1" line-end="8"/>
    </entity>

    <relationship from-entity="orders" from-column="customer_id"
                  to-entity="customers" to-column="id" type="many-to-one"/>
  </data-model>

  <interactions count="45">
    <interaction id="DB-001" operation="SELECT" confidence="high">
      <sql>SELECT * FROM orders WHERE customer_id = ?</sql>
      <tables>
        <table>orders</table>
      </tables>
      <columns>
        <column>*</column>
      </columns>
      <context method="findByCustomerId" class="OrderRepository"/>
      <source file="src/repository/OrderRepository.java" line-start="25" line-end="30">
        <snippet>@Query("SELECT * FROM orders WHERE customer_id = :customerId")</snippet>
      </source>
    </interaction>

    <!-- More interactions... -->
  </interactions>

</database>
```

### Step 7: Report Results

```
Database Extraction Complete!

Output: $EXTRACTIONS_DIR/database.xml

Data Model Summary:
- Entities: 15 (12 tables, 3 views)
- Relationships: 18
- Source types: DDL (10), ORM (4), Inferred (1)

SQL Interactions Summary:
- Total: 89
- By operation:
  - SELECT: 45
  - INSERT: 18
  - UPDATE: 15
  - DELETE: 8
  - DDL: 3

Confidence levels:
- High: 72 (81%)
- Medium: 15 (17%)
- Low: 2 (2%)

Run /reforge.generate data-dictionary to create documentation.
```

---

# UI Extraction

## Command

```
/reforge.extract ui
```

## Workflow

### Step 1: Load Analysis

Identify UI template files:
- HTML, JSP, ASPX, PHP templates
- React JSX/TSX components
- Vue single-file components
- Angular templates

### Step 2: Scan for Screens

For each UI file:

1. **Identify as screen/page:**
   - Has route definition
   - Contains full page structure
   - Is a primary component

2. **Extract screen metadata:**
   - Screen name (from filename or component)
   - URL path if available
   - Associated controller/component

### Step 3: Extract Components

For each screen, identify components:

| Component Type | Detection Pattern |
|----------------|-------------------|
| `button` | `<button>`, `<input type="submit">`, click handlers |
| `input` | `<input type="text">`, form fields |
| `form` | `<form>`, form containers |
| `table` | `<table>`, data grids |
| `label` | `<label>`, display text |
| `link` | `<a>`, navigation links |
| `container` | `<div>`, `<section>`, layout containers |
| `dropdown` | `<select>`, dropdown menus |
| `checkbox` | `<input type="checkbox">` |
| `radio` | `<input type="radio">` |
| `textarea` | `<textarea>` |
| `image` | `<img>`, images |
| `menu` | `<nav>`, navigation menus |

### Step 4: Map Event Handlers

For interactive components:

1. **Find event bindings:**
   - `onclick`, `onsubmit`, `onchange`
   - `@click`, `v-on:click` (Vue)
   - `(click)`, `(submit)` (Angular)
   - `onClick`, `onSubmit` (React)

2. **Trace to handler:**
   - Method name
   - Parameters
   - Target action (navigation, API call, state change)

3. **Cross-reference to workflows:**
   - If handler triggers a workflow, link to workflow extraction

### Step 5: Generate Layout

Create ASCII representation of screen layout:

1. **Analyze DOM structure:**
   - Identify major layout regions (header, sidebar, main, footer)
   - Determine component positioning

2. **Generate ASCII art:**
   - Use symbols from `.reforge/templates/ascii-layout.md`
   - Position components spatially
   - Label interactive elements

### Step 6: Extract Navigation

Identify screen-to-screen flows:

1. **Find navigation triggers:**
   - Link hrefs
   - Router navigations
   - Form action URLs
   - Programmatic redirects

2. **Map flows:**
   - Source screen
   - Target screen
   - Trigger (button, link, form)
   - Conditions (if any)

### Step 7: Generate Output

Write to `$EXTRACTIONS_DIR/ui-flows.xml`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<ui-flows xmlns="http://reforge.dev/schema/ui-flows"
          project-id="[project]" version="1.0.0"
          generated="[timestamp]">

  <screens count="12">
    <screen id="SCR-001" name="Order List" path="/orders">
      <layout rows="20" columns="60">
        <ascii>
+----------------------------------------------------------+
| [Logo]     Search: [___________] [Search]   [Cart (3)]   |
+----------------------------------------------------------+
| Orders                                    [+ New Order]  |
+----------------------------------------------------------+
| ID   | Customer      | Total    | Actions               |
|------|---------------|----------|------------------------|
| #001 | Acme Corp     | $500.00  | [View] [Edit]         |
+----------------------------------------------------------+
        </ascii>
      </layout>
      <components count="6">
        <component id="CMP-001" type="button" name="newOrderBtn"
                   label="+ New Order" confidence="high">
          <position row="3" column="50"/>
          <events>
            <event type="click" handler="navigateToNewOrder"/>
          </events>
          <source file="webapp/orders/list.jsp" line-start="15" line-end="17"/>
        </component>
        <!-- More components... -->
      </components>
      <source file="webapp/orders/list.jsp" line-start="1" line-end="100"/>
    </screen>
  </screens>

  <navigation>
    <flow from-screen="SCR-001" to-screen="SCR-002"
          trigger="click:newOrderBtn"/>
    <flow from-screen="SCR-002" to-screen="SCR-001"
          trigger="submit" condition="success"/>
  </navigation>

</ui-flows>
```

---

# Workflow Extraction

## Command

```
/reforge.extract workflows
```

## Workflow

### Step 1: Identify Entry Points

Find workflow starting points:

| Entry Type | Detection Pattern |
|------------|-------------------|
| `ui-action` | Button handlers, form submits |
| `api-call` | REST endpoints, controller methods |
| `scheduled` | @Scheduled, cron jobs, timers |
| `message` | Message listeners, event handlers |
| `startup` | @PostConstruct, initialization |
| `event` | Domain event handlers |

### Step 2: Trace Execution Path

For each entry point:

1. **Start at entry method**
2. **Follow method calls:**
   - Record each method invocation
   - Track parameters passed
   - Note return values used

3. **Handle decision points:**
   - If/else branches → create branch nodes
   - Switch statements → create case nodes
   - Try/catch → note exception paths

4. **Handle loops:**
   - For/while loops → note iteration context
   - Foreach → note collection being iterated

5. **Identify data access:**
   - Database reads/writes
   - File operations
   - External API calls

6. **Link to other extractions:**
   - Reference business rules applied
   - Reference database interactions
   - Reference UI component triggers

### Step 3: Generate Step Sequence

For each workflow step:

| Step Type | Description |
|-----------|-------------|
| `method-call` | Invokes another method |
| `decision` | Conditional branch point |
| `loop` | Iteration over collection |
| `data-access` | Database operation |
| `external-call` | External service call |
| `validation` | Input/state validation |
| `transformation` | Data transformation |
| `notification` | Alert/message sending |

### Step 4: Generate Output

Write to `$EXTRACTIONS_DIR/workflows.xml`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<workflows xmlns="http://reforge.dev/schema/workflows"
           project-id="[project]" version="1.0.0"
           generated="[timestamp]" count="23">

  <workflow id="WF-001" name="Order Submission"
            entry-point="OrderController.submitOrder"
            trigger-type="ui-action" confidence="high">
    <description>Handles new order submission from checkout</description>
    <steps>
      <step sequence="1" type="validation"
            method="validate" class="OrderValidator">
        <description>Validate order data</description>
        <source file="src/validator/OrderValidator.java"
                line-start="20" line-end="45"/>
      </step>

      <step sequence="2" type="decision"
            condition="validationResult.isValid()">
        <description>Check validation result</description>
        <branches>
          <branch condition="true" label="Valid">
            <step sequence="1" type="method-call"
                  method="calculateTotal" class="PricingService">
              <description>Calculate order total with discounts</description>
              <rule-ref>BR-001</rule-ref>
            </step>
            <step sequence="2" type="data-access" sql-ref="DB-002">
              <description>Save order to database</description>
            </step>
            <step sequence="3" type="notification">
              <description>Send confirmation email</description>
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
    <source file="src/controller/OrderController.java"
            line-start="50" line-end="95"/>
    <related>
      <ui-component>CMP-011</ui-component>
      <business-rule>BR-001</business-rule>
      <business-rule>BR-002</business-rule>
      <database-interaction>DB-002</database-interaction>
    </related>
  </workflow>

</workflows>
```

---

## Common Elements

### Confidence Levels

| Level | Criteria |
|-------|----------|
| `high` | Clear pattern, descriptive naming, straightforward logic |
| `medium` | Pattern identified but naming is generic or logic has some complexity |
| `low` | Unclear pattern, magic numbers, complex/obfuscated logic |

### Source References

All extractions include:
- `file`: Relative path to source file
- `line-start`: Starting line number
- `line-end`: Ending line number
- `snippet` (optional): Actual code snippet

### Error Handling

If extraction encounters issues:
- Log the error to `.reforge/memory/logs/`
- Continue processing other files
- Report errors in summary

### Clarification Items

When confidence is low:
- Create clarification entry in `.reforge/memory/clarifications/`
- Include context and suggested interpretations
- User can resolve via `/reforge.clarify`

---

## Optional Validation

After generating extraction output, you can validate the XML against its XSD schema using:

```bash
reforge-scripts validate-xml $EXTRACTIONS_DIR/business-rules.xml business-rules
reforge-scripts validate-xml $EXTRACTIONS_DIR/database.xml database
reforge-scripts validate-xml $EXTRACTIONS_DIR/ui-flows.xml ui-flows
reforge-scripts validate-xml $EXTRACTIONS_DIR/workflows.xml workflows
```

If validation fails, the output will show structured errors with line numbers and fix suggestions. Correct any issues before proceeding.

To list all available schema types:
```bash
reforge-scripts validate-xml --list-schemas
```

---

## Output Schema References

- Business Rules: `.reforge/schemas/business-rules.md`
- Database: `.reforge/schemas/database.md`
- UI Flows: `.reforge/schemas/ui-flows.md`
- Workflows: `.reforge/schemas/workflows.md`
