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

### Step 0.6: Load Extraction Profile

If `.reforge/memory/extraction-profile.md` exists, read it now. Use its contents as
language-specific and architecture-specific guidance throughout this extraction:
- **Language Rules**: Apply language-specific extraction rules (type quirks, operator
  differences, naming conventions, common pitfalls) when extracting from code in those languages
- **Architecture Guidance**: Use architecture-specific patterns to locate business rules,
  data access, workflows, and integration points in the expected locations
- **Framework Patterns**: Apply framework-specific extraction guidance when relevant
- **Custom Notes**: Follow project-specific extraction guidance provided by the user

If no extraction profile exists, proceed without language-specific guidance. Consider
suggesting that the user run `/reforge.profile` for improved extraction accuracy.

### Step 0.7: Check/Update Project Plan

If `.reforge/memory/project-plan.md` exists, read it now.

**On command start:**
- Parse the plan file to count total items and completed items
- Display: "📋 Project Plan: X/Y items complete (Z%)"
- Derive the plan tag from the extraction type argument: `<!-- reforge:extract:<type> -->` (e.g., `<!-- reforge:extract:business-rules -->`)
- Identify the item with that tag and display its status

**On command completion (success only):**
- Locate the plan item by searching for `<!-- reforge:extract:<type> -->`
- If found and unchecked (`- [ ]`): change to `- [x]` and append ` *(completed: YYYY-MM-DD)*`
- If found and already checked (`- [x]`): leave unchanged (idempotent)
- If tag not found: emit warning — "⚠️ No plan item found for this extraction type. Run /reforge.plan to add it."
- If file write fails: emit warning — "⚠️ Could not update project plan." Continue without failing.
- Update the `**Last Updated**` metadata line to today's date

If `.reforge/memory/project-plan.md` does not exist, skip this step silently.
The project plan is optional — its absence MUST NOT affect command behavior.

### Step 1: Load Analysis

Read `$ANALYSIS_DIR/analysis.xml` to get:
- List of source files to process
- Language information for each file
- Component locations (classes, methods)

**CRITICAL**: For every file you extract from, you MUST:
1. Read the file using the Read tool IN THIS SESSION before writing any extraction from it
2. Do NOT extract from memory of previous sessions or from analysis.xml metadata alone
3. If a file is too large to read in one pass, read it in sections and process each section
4. Track which files you have actually read -- only reference files read in this session

The analysis.xml inventory tells you WHICH files to examine. You must still READ each file to extract accurate content from it.

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

#### Enumeration and Constant Patterns

```
Enum declarations:
  enum StatusType { Active, Inactive, Suspended }
  Public Enum StateOfOnBoard As Integer
  public class StatusCodes : Enumeration<String>
  Public Class PTCStatus : Inherits Enumeration(Of String, PTCStatus)

Named constant sets:
  const MAX_RETRIES = 3
  Public Const TIMEOUT_MS As Integer = 5000
  static readonly string[] VALID_STATES = { ... }

State machine definitions:
  States: New -> InProgress -> Completed -> Archived
  Transitions: Submit(), Approve(), Reject()
```

**CRITICAL for enums**: When extracting enumeration types:
1. Read the ENTIRE enum/class declaration from source, not just a summary
2. Copy EVERY member name exactly as declared (spelling, casing, underscores)
3. Record the underlying type from the declaration:
   - Standard enum: note `As Integer`, `As String`, `: int`, etc.
   - Custom base class: note the full inheritance (e.g., `Inherits Enumeration(Of String, PTCStatus)`)
   - If type is ambiguous, read the base class source to determine value type
4. Copy any assigned values (numeric or string) exactly as written in source
5. Do NOT infer member names from usage context or descriptive comments
6. If the enum has more than 20 members, extract ALL of them -- do not summarize
7. Record the total member count (verified by counting in source)

### Step 2.5: Verbatim Extraction Rules

**CRITICAL ANTI-HALLUCINATION MANDATE**: When extracting any of the following, you MUST copy the EXACT text from source code as shown by the Read tool. Do NOT paraphrase, infer, or reconstruct names from memory:

- **Identifiers**: Class names, method names, property names, field names, variable names
- **Enum members**: Copy every member name character-for-character from the source declaration
- **Constant values**: Copy literal values (strings, numbers) exactly as declared
- **Type annotations**: Copy generic type parameters, base classes, and interface names exactly
- **File names**: Use the exact filename from the filesystem; do not guess filenames
- **String literals**: Copy protocol strings, format strings, and message templates verbatim
- **Boolean operators**: Copy the exact operator (`OrElse`, `AndAlso`, `&&`, `||`, `Or`, `And`) -- do not paraphrase to "AND"/"OR"

**Verification requirement**: After writing any identifier into the extraction output, re-read the source file to confirm the identifier exists at the claimed location. If you cannot verify an identifier, mark it with `confidence="low"` and add a `<clarification>` note explaining what could not be verified.

**Prohibited patterns**:
- Do NOT generate enum member names from description context (e.g., don't infer "InactiveLoggedOn" from knowing there's an inactive logged-on state)
- Do NOT assume integer values for string-typed enums or vice versa
- Do NOT reconstruct method names from behavioral descriptions (e.g., don't write "DisableJointControlTracks" when the actual method is "EnableJointControlTracks(False)")
- Do NOT fabricate file names by analogy (e.g., don't write "SrmManager.vb" when the actual file is "Srm.vb")
- Do NOT paraphrase boolean logic: if the code says `OrElse`, write `OrElse`, not "OR"

### Step 3: Extract Rule Details

For each identified pattern:

1. **Capture the rule logic:**
   - Extract the condition expression
   - Extract the action/consequence
   - Identify any else/default cases
   - **Preserve data types**: When the rule references a typed value (enum, constant, collection),
     record the actual declared type from source code, not an inferred type.
     Example: If source declares `Public Class PTCStatus : Inherits Enumeration(Of String)`,
     record it as a string enumeration, NOT as an integer enum.
   - **Include type declarations in snippets**: When a rule depends on a specific type,
     include the type declaration in the `<snippet>` or reference it in a `<related-rules>` entry.

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

#### 3a. Technical Mechanism Accuracy

When extracting rules or workflows that involve:

- **Authentication/crypto**: Describe the EXACT mechanism implemented in code, not a textbook definition. If code shows HMAC signing on the client side with a hardcoded key, describe it as "client-side HMAC signing with hardcoded key", NOT as "challenge-response authentication". Include:
  - Key source (hardcoded, derived, negotiated)
  - Signed data (what exact bytes/strings are signed)
  - Verification point (where and how signature is checked)
  - Protocol sequence from actual code flow
- **Communication protocols**: Describe the actual framing, encoding, and transport observed in code. Copy protocol constants (SOH, EOT, STX markers) verbatim from source.
- **External integrations**: Describe the actual API calls, message formats, and endpoints found in code, not assumed standard patterns.
- **Security findings**: Every security-related extraction MUST include:
  - The exact source file and line number
  - A verbatim code snippet proving the claim
  - Do NOT fabricate which functions are called in which files -- verify by reading the file

**Self-check rule**: When you find yourself writing a description that sounds like a textbook definition rather than a code-specific implementation detail, STOP and re-read the source code. The extraction must describe WHAT THE CODE DOES, not what the technology generally does.

### Step 4: Group Related Rules

- Group rules by domain entity (Order, Customer, Product, etc.)
- Identify rule dependencies and relationships
- Link rules that override or extend each other

### Step 5: Generate Output

Write to `$EXTRACTIONS_DIR/business-rules.xml`:

**Aggregation accuracy requirements**:
- The `count` attribute on the root element MUST equal the actual number of child elements. Count them explicitly; do not estimate.
- When extracting an enum with N members, verify by counting members in the source declaration. Do not derive count from the highest index value.
- When referencing totals across multiple files, re-count at output time. Do not carry forward counts from earlier analysis steps.
- If the extraction reports category breakdowns (e.g., "Validation: 45, Pricing: 23"), the subcategory counts MUST sum to the total count.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<business-rules xmlns="http://reforge.dev/schema/extraction"
                project-id="[project]" version="1.0.0"
                schema-version="1.0.0"
                generated="[timestamp]">

  <metadata>
    <total-count>[total]</total-count>
    <confidence-distribution>
      <high>[high-count]</high>
      <medium>[medium-count]</medium>
      <low>[low-count]</low>
    </confidence-distribution>
    <extraction-timestamp>[timestamp]</extraction-timestamp>
  </metadata>

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

### Step 5.5: Post-Extraction Verification

Before finalizing output, perform these MANDATORY verification checks:

#### A. Source File Existence
For every `<source file="...">` reference in the output:
1. Confirm the file exists at the specified path using Glob or Read
2. If the file does not exist, REMOVE the extraction item or mark confidence="low"
3. Do NOT reference files you have not actually read during this extraction session

#### B. Identifier Sampling Verification
Select a random sample of at least 20% of extraction items (minimum 5 items, or all items if fewer than 5 exist). For each sampled item:
1. Re-read the source file at the stated line numbers using the Read tool
2. Verify every identifier (class, method, enum member, constant) exists at the stated location
3. Verify any `<snippet>` content matches the source code at those lines
4. If any identifier is not found, search the entire file for it
5. If still not found, the identifier may be fabricated -- remove it, correct it, or flag as confidence="low"

#### C. Line Number Accuracy
For each sampled item:
1. Verify `line-start` and `line-end` are within the file's actual line count
2. Verify the code at those lines matches the extracted content
3. If line numbers are off by more than 5 lines, re-locate and update them

#### D. Enum/Constant Full Verification
For ALL enum and constant extractions (not just the 20% sample):
1. Re-read the source declaration
2. Compare every extracted member name against the source character-by-character
3. Verify the declared type matches the extraction
4. Verify the member count matches

#### E. Cross-Reference Consistency
For every `<rule-ref>`, `<sql-ref>`, or `<workflow-ref>`:
1. Confirm the referenced ID exists in the appropriate extraction file
2. If the referenced extraction does not yet exist, note it as "pending verification"

**If verification reveals errors**: Correct them in the extraction XML before proceeding to Step 5.6. Do NOT finalize output with known inaccuracies.

### Step 5.6: Schema Compliance Validation

After post-extraction verification, validate the output XML against the common extraction schema before writing the final file.

#### Setup

Read `.reforge/schemas/common-schema.md` to load the authoritative shared element definitions. All extraction output — regardless of type — MUST conform to this schema.

#### Validation Checks

Perform each check against the extraction output XML:

| # | Check | Rule |
|---|-------|------|
| 1 | **Required root attributes** | Root element MUST have all five attributes: `project-id`, `version`, `schema-version`, `generated`, `xmlns` |
| 2 | **Namespace** | `xmlns` MUST equal `http://reforge.dev/schema/extraction` |
| 3 | **Metadata present** | `<metadata>` MUST be the first child of the root element, containing `<total-count>`, `<confidence-distribution>` (with `<high>`, `<medium>`, `<low>` children), and `<extraction-timestamp>` |
| 4 | **Confidence sum** | `high + medium + low` in `<confidence-distribution>` MUST equal `<total-count>` |
| 5 | **Source reference format** | All `<source>` elements MUST use attributes `file`, `line-start`, `line-end` (canonical format). No legacy formats (`line="..."`, `lines="..."`, `<LineNumber>`) |
| 6 | **Schema version** | `schema-version` MUST be valid semver (`MAJOR.MINOR.PATCH`) |

#### Auto-Correction Rules

When a check fails and auto-correction is possible, apply the correction silently and log it for the Step 6 report:

| Violation | Auto-Correction |
|-----------|-----------------|
| Missing `schema-version` attribute | Add `schema-version="1.0.0"` to root element |
| Missing `xmlns` attribute | Add `xmlns="http://reforge.dev/schema/extraction"` to root element |
| Missing `<metadata>` element | Generate `<metadata>` from extracted item counts — compute `total-count`, tally items by confidence level for `<confidence-distribution>`, set `<extraction-timestamp>` to current ISO-8601 timestamp |
| Legacy source reference format (`line="145-160"`) | Normalize to `line-start="145" line-end="160"` |
| Legacy source reference format (`lines="45,46,47"`) | Normalize to `line-start="45" line-end="47"` |
| Legacy source reference format (`<LineNumber>45</LineNumber>`) | Normalize to `line-start="45" line-end="45"` |
| Missing `generated` attribute | Add `generated="{current-ISO-8601-timestamp}"` to root element |
| Confidence sum mismatch | Recount items by confidence level and update `<confidence-distribution>` and `<total-count>` |

#### SCHEMA-WARNING Behavior

When a violation is detected and auto-correction is **not possible** (e.g., `project-id` is empty and cannot be inferred, or structural issues prevent safe correction):

1. Insert an XML comment at the violation point:
   ```xml
   <!-- SCHEMA-WARNING: [description of violation] -->
   ```
2. **Continue writing the file** — do NOT abort the extraction
3. Include the warning count and details in the Step 6 report summary

Example:
```xml
<business-rules xmlns="http://reforge.dev/schema/extraction"
    project-id=""
    version="1.0.0"
    schema-version="1.0.0"
    generated="2025-01-15T10:30:00Z">
  <!-- SCHEMA-WARNING: project-id is empty — cannot infer value -->
  <metadata>
    ...
  </metadata>
  ...
</business-rules>
```

#### Legacy File Handling (FR-014)

When processing existing extraction files that lack a `schema-version` attribute:
- Emit warning: "Legacy extraction file detected (no schema-version). Output may use inconsistent element names."
- Attempt best-effort parsing with known legacy patterns
- Never crash on legacy files — degrade gracefully with warnings

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

Schema Compliance (Step 5.6):
- Validation checks: 6/6 passed
- Auto-corrections applied: 0
- SCHEMA-WARNING count: 0
- Schema version: 1.0.0

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
<database xmlns="http://reforge.dev/schema/extraction"
          project-id="[project]" version="1.0.0"
          schema-version="1.0.0"
          generated="[timestamp]">

  <metadata>
    <total-count>[entity-count + interaction-count]</total-count>
    <confidence-distribution>
      <high>[high-count]</high>
      <medium>[medium-count]</medium>
      <low>[low-count]</low>
    </confidence-distribution>
    <extraction-timestamp>[timestamp]</extraction-timestamp>
  </metadata>

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
<ui-flows xmlns="http://reforge.dev/schema/extraction"
          project-id="[project]" version="1.0.0"
          schema-version="1.0.0"
          generated="[timestamp]">

  <metadata>
    <total-count>[screen-count + component-count]</total-count>
    <confidence-distribution>
      <high>[high-count]</high>
      <medium>[medium-count]</medium>
      <low>[low-count]</low>
    </confidence-distribution>
    <extraction-timestamp>[timestamp]</extraction-timestamp>
  </metadata>

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
   - **Copy method names EXACTLY as they appear in source**: use `EnableJointControlTracks(False)`,
     NOT a paraphrased `DisableJointControlTracks`. The actual code identifier matters for
     downstream consumers who need to find the method in the codebase.
   - **Include actual parameters when they affect semantics**: If a boolean parameter like
     `False` or `True` changes the method's behavior, include it in the extraction
     (e.g., `EnableJointControlTracks(False)` not just `EnableJointControlTracks`).
   - **Verify method existence**: Before writing a method reference, use Grep to confirm
     the method name exists in the codebase. If grep returns 0 results, the name may be
     fabricated -- re-read the source to find the actual method name.
   - **Record the call site**: Note the exact file and line where the method is called,
     not just the method's definition location.

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
<workflows xmlns="http://reforge.dev/schema/extraction"
           project-id="[project]" version="1.0.0"
           schema-version="1.0.0"
           generated="[timestamp]">

  <metadata>
    <total-count>23</total-count>
    <confidence-distribution>
      <high>[high-count]</high>
      <medium>[medium-count]</medium>
      <low>[low-count]</low>
    </confidence-distribution>
    <extraction-timestamp>[timestamp]</extraction-timestamp>
  </metadata>

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

> Shared structural elements (root attributes, metadata, source references, confidence vocabulary, ID patterns) are defined in [common-schema.md](../schemas/common-schema.md). All extraction output MUST conform to the common schema. See that file for the authoritative specification.

### Confidence Levels

| Level | Criteria |
|-------|----------|
| `high` | Pattern clearly identified AND all identifiers verified against source code via Read/Grep AND snippets match source verbatim AND file references confirmed to exist |
| `medium` | Pattern identified but some identifiers could not be re-verified, OR logic has complexity that may cause misinterpretation, OR source file was read but specific lines could not be reconfirmed |
| `low` | Pattern inferred from context, OR identifiers reconstructed from memory rather than copied from source, OR source file could not be re-read for verification, OR extraction based on partial file reading |

**IMPORTANT**: Confidence reflects VERIFICATION STATUS, not just pattern clarity. An extraction with clear business logic but unverified identifiers MUST be rated `medium` or `low`, never `high`. The question is not "does this look right?" but "did I verify this against source code?"

### Source References

All extractions MUST use the canonical source reference format defined in [common-schema.md](../schemas/common-schema.md):

```xml
<source file="{relative-path}" line-start="{integer}" line-end="{integer}">
  <snippet>{optional-code-snippet}</snippet>
</source>
```

- `file`: Relative path to source file (no leading `/`)
- `line-start`: Starting line number (positive integer)
- `line-end`: Ending line number (≥ `line-start`)
- `snippet` (optional): Verbatim code snippet

Legacy formats (`line="145-160"`, `lines="45,46,47"`, `<LineNumber>`) MUST be normalized to `line-start`/`line-end` attributes.

**File existence requirement**: Before writing any `file` attribute value:
1. Use Glob to confirm the file exists at the stated path
2. If the exact path is not found, search for the filename in the project tree
3. Use the actual discovered path, not a guessed or recalled path
4. NEVER reference a file you have not opened and read during this extraction session

**Common fabrication patterns to avoid**:
- Adding "Manager", "Service", "Helper", "Base", or "Factory" suffixes to filenames
- Changing file extensions (e.g., ".cs" vs actual ".vb")
- Guessing subdirectory paths from module names
- Referencing files from a different project or module
- Using a class name as a filename without verifying (class `SrmManager` may live in `Srm.vb`)

**Snippet fidelity requirements**:
- Snippets MUST be verbatim copies of source code from the Read tool output
- Do NOT reformat, simplify, or "clean up" code in snippets
- Do NOT add or remove comments; whitespace normalization is acceptable
- Do NOT translate between programming languages in snippets
- Do NOT substitute equivalent expressions (e.g., don't change `OrElse` to `||`)
- If a code block is too long for a snippet, use the first and last relevant lines
  with `<!-- ... N lines omitted ... -->` to indicate omission, preserving exact code at boundaries
- Every snippet MUST be verifiable by reading the source file at the stated line numbers

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


## Required Validation

After generating extraction output, you MUST perform structural, content, and schema compliance validation:

### Structural Validation (XSD)

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

### Content Validation (Post-Extraction Verification)
Execute the verification checks from Step 5.5 above. At minimum:
1. Spot-check at least 20% of source file references by re-reading the files
2. Verify ALL enum/constant extractions have verbatim member names
3. Confirm ALL snippet content matches source code at stated line numbers
4. Report verification results in the extraction summary (Step 6)

If content verification reveals errors, correct them before finalizing the extraction output.

**Important limitation**: XSD validation checks structural correctness only (elements, attributes, types). It does NOT verify content accuracy. A structurally valid extraction may still contain:
- File paths that don't exist
- Line numbers outside the file's range
- Fabricated identifiers, enum members, or method names
- Paraphrased snippets that don't match source code

Content accuracy verification (Step 5.5) is REQUIRED, not optional.

### Schema Compliance Validation (Common Schema)

Execute the schema compliance checks from Step 5.6 above. This validates structural conformance to the common extraction schema (`.reforge/schemas/common-schema.md`):

1. All required root attributes present (`project-id`, `version`, `schema-version`, `generated`, `xmlns`)
2. Namespace is `http://reforge.dev/schema/extraction`
3. `<metadata>` element present with all required children
4. Confidence distribution sums to total count
5. All `<source>` elements use canonical `line-start`/`line-end` format
6. `schema-version` is valid semver

**Relationship to other validations**: Schema compliance (Step 5.6) checks structural conformance to the common schema — ensuring consistent root attributes, metadata, source references, and namespace across all extraction types. XSD validation checks formal type correctness against type-specific schemas. Content validation (Step 5.5) verifies accuracy of extracted data against the source code. All three are required.

---

## Output Schema References

- **Common Schema**: `.reforge/schemas/common-schema.md` (shared elements: root attributes, metadata, source references, confidence vocabulary, ID patterns)
- Business Rules: `.reforge/schemas/business-rules.md`
- Database: `.reforge/schemas/database.md`
- UI Flows: `.reforge/schemas/ui-flows.md`
- Workflows: `.reforge/schemas/workflows.md`
