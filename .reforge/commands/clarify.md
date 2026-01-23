# /reforge.clarify

> Interactively resolve ambiguities in extracted code elements

## Command Syntax

```
/reforge.clarify [--id <item-id>] [--all] [--category <type>]
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `--id` | No | Resolve specific clarification item |
| `--all` | No | Process all pending clarifications sequentially |
| `--category` | No | Filter by category: `business-rules`, `database`, `ui`, `workflows` |

## Overview

This command allows interactive resolution of ambiguous code patterns identified during extraction. Each clarification:

1. Presents the ambiguous code with context
2. Offers interpretation options
3. Records the user's decision
4. Applies the decision consistently across the codebase

## Prerequisites

- At least one extraction must be completed
- Pending clarifications exist in `$CLARIFICATIONS_DIR/`

---

## Workflow

### Step 0: Check Prerequisites

Run the prerequisites script to validate state and resolve paths:

```bash
bash .reforge/scripts/bash/check-prerequisites.sh --json --require-analysis
```

This returns JSON with resolved variables:
```json
{"PROJECT_NAME":"...","REPO_ROOT":"...","PROJECT_OUTPUT_DIR":"...","CONFIG":"...","ANALYSIS_STATUS":"completed","AVAILABLE_EXTRACTIONS":[...],"CHECKPOINT":null,"CLARIFICATIONS_DIR":"..."}
```

Use `$CLARIFICATIONS_DIR` for clarification file paths.

Assign subdirectory variables:
```
$EXTRACTIONS_DIR = $PROJECT_OUTPUT_DIR/extractions
```

### Step 0.5: Load Project Context

If `.reforge/memory/project-context.md` exists, read it now. Use its contents as
supplemental guidance throughout this command's execution:
- **Technology Stack**: Informs language/framework detection and pattern recognition
- **Domain Knowledge**: Provides business context for naming and categorization
- **Analysis Guidelines**: Directs focus and exclusions beyond config.json
- **Custom Rules**: Additional rules to follow alongside the constitution

### Step 1: Load Pending Clarifications

Read all `.xml` files from `$CLARIFICATIONS_DIR/`:

```
$CLARIFICATIONS_DIR/
├── CL-001-business-rule.xml
├── CL-002-database.xml
├── CL-003-ui-component.xml
└── ...
```

### Step 2: Filter and Prioritize

Apply filters if specified:
- `--id`: Select specific item only
- `--category`: Filter by extraction type
- Default: Sort by impact (high to low)

**Impact scoring:**
- Referenced by multiple workflows: +3
- Affects business rule: +2
- Affects data model: +2
- Low confidence extraction: +1

### Step 3: Present Clarification

For each pending item, display:

```
=== Clarification Required ===

ID: CL-001
Category: Business Rule
Related Extraction: BR-045
Confidence: Low
Impact: High (affects 3 workflows)

--- Context ---

File: src/service/PricingService.java
Lines: 78-85

Code:
```java
if (order.getTotal().compareTo(MAGIC_THRESHOLD) > 0) {
    order.setDiscount(order.getTotal().multiply(MAGIC_RATE));
}
```

--- Ambiguity ---

Magic numbers detected: MAGIC_THRESHOLD and MAGIC_RATE are not defined
in visible scope. Unable to determine exact discount logic.

--- Options ---

1. [Specify values] Enter the threshold and rate values
2. [Business rule] This implements a volume discount rule
3. [Legacy code] This is dead/obsolete code
4. [External config] Values come from external configuration
5. [Skip] Mark for later review
6. [Custom] Provide custom interpretation

Your choice (1-6):
```

### Step 4: Record Decision

Based on user choice:

#### Option 1: Specify Values

```
Enter threshold value (e.g., 100, 500): 100
Enter rate value (e.g., 0.10, 0.15): 0.10

Recording: Discount of 10% applies when order exceeds $100
```

#### Option 2: Business Rule

```
Describe the business rule:
> Volume discount - orders over threshold receive percentage discount

Recording as business rule with user-provided description
```

#### Option 3: Legacy Code

```
Marking as legacy/obsolete code.
This extraction will be flagged as "deprecated" in output.
```

#### Option 4: External Config

```
Where is this configured?
> application.properties

Recording: Values loaded from external configuration (application.properties)
```

#### Option 5: Skip

```
Skipping CL-001. Item remains pending.
```

#### Option 6: Custom

```
Enter your interpretation:
> This is a promotional discount that varies by season

Recording custom interpretation.
```

### Step 5: Update Clarification File

Save decision to clarification file:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<clarification id="CL-001" status="resolved">
  <context>
    <file>src/service/PricingService.java</file>
    <lines>78-85</lines>
    <extraction-type>business-rule</extraction-type>
    <extraction-ref>BR-045</extraction-ref>
  </context>
  <ambiguity>
    <type>magic-number</type>
    <description>Undefined constants MAGIC_THRESHOLD and MAGIC_RATE</description>
  </ambiguity>
  <resolution>
    <type>specify-values</type>
    <timestamp>2024-01-15T14:30:00Z</timestamp>
    <values>
      <value name="MAGIC_THRESHOLD">100</value>
      <value name="MAGIC_RATE">0.10</value>
    </values>
    <interpretation>Discount of 10% applies when order exceeds $100</interpretation>
  </resolution>
</clarification>
```

### Step 6: Apply to Extraction

Update the related extraction with resolved information:

1. **Update confidence level**: Low → High (if fully resolved)
2. **Update description**: Include clarified interpretation
3. **Add resolution note**: Reference clarification ID

```xml
<rule id="BR-045" category="pricing" confidence="high">
  <description>Volume discount: 10% off orders over $100</description>
  <logic>IF order.total > 100 THEN order.discount = order.total * 0.10</logic>
  <source file="src/service/PricingService.java" line-start="78" line-end="85"/>
  <clarification-ref>CL-001</clarification-ref>
</rule>
```

### Step 7: Apply Consistently

Find similar patterns in codebase:

```
Searching for similar patterns...

Found 3 similar usages:
1. src/service/DiscountService.java:45 - Same constants
2. src/batch/ReportGenerator.java:120 - Similar pattern
3. src/test/PricingTest.java:55 - Test case

Apply same interpretation to all? (Y/n):
```

If yes, update all related extractions with consistent interpretation.

### Step 8: Report Progress

```
=== Clarification Complete ===

Resolved: CL-001
Category: Business Rule
Interpretation: Volume discount of 10% for orders over $100

Applied to:
- BR-045 (confidence: low → high)
- 3 similar patterns updated

Remaining clarifications: 12
- Business Rules: 5
- Database: 3
- UI Components: 2
- Workflows: 2

Run /reforge.clarify --all to continue, or
Run /reforge.status to see overall progress.
```

---

## Clarification Types

### Magic Numbers

Undefined or unclear numeric constants.

**Detection**: Numbers without clear context or definition
**Resolution**: Specify value and meaning

### Ambiguous Logic

Code where intent is unclear.

**Detection**: Complex conditionals, unclear variable names
**Resolution**: Describe business intent

### Missing Context

Code referencing external resources.

**Detection**: External file reads, configuration lookups
**Resolution**: Identify source of values

### Dead Code

Potentially unused or obsolete code.

**Detection**: Unreachable code, deprecated patterns
**Resolution**: Confirm status (active/deprecated)

### Dynamic SQL

SQL built from variables at runtime.

**Detection**: String concatenation in SQL
**Resolution**: Describe expected query patterns

### Event Handlers

UI events with unclear triggers.

**Detection**: Generic handler names
**Resolution**: Describe user action and expected behavior

---

## Clarification File Format

Path: `$CLARIFICATIONS_DIR/<id>.xml`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<clarification id="CL-XXX" status="pending|resolved|skipped">
  <context>
    <file>[relative-path]</file>
    <lines>[start]-[end]</lines>
    <extraction-type>[business-rule|database|ui|workflow]</extraction-type>
    <extraction-ref>[extraction-id]</extraction-ref>
    <snippet>[code-snippet]</snippet>
  </context>

  <ambiguity>
    <type>[magic-number|ambiguous-logic|missing-context|dead-code|dynamic-sql|event-handler]</type>
    <description>[what is unclear]</description>
    <impact>[high|medium|low]</impact>
  </ambiguity>

  <options>
    <option id="1">[interpretation option]</option>
    <option id="2">[interpretation option]</option>
  </options>

  <!-- Only present if resolved -->
  <resolution>
    <type>[option-type]</type>
    <timestamp>[ISO-8601]</timestamp>
    <interpretation>[user interpretation]</interpretation>
    <values>
      <value name="[name]">[value]</value>
    </values>
    <similar-patterns-applied>[count]</similar-patterns-applied>
  </resolution>
</clarification>
```

---

## Creating Clarifications During Extraction

When extraction encounters ambiguity:

1. **Detect ambiguity type**
2. **Create clarification file** in `$CLARIFICATIONS_DIR/`
3. **Set confidence to "low"** in extraction output
4. **Continue processing** other files
5. **Report pending clarifications** at end of extraction

---

## Examples

### Interactive Session

```
User: /reforge.clarify

Agent: Found 15 pending clarifications.
Processing in order of impact...

=== Clarification Required [1/15] ===

ID: CL-003
Category: Business Rule
Impact: High

File: src/service/OrderValidator.java
Lines: 45-52

Code:
```java
if (order.getItems().size() < MIN_ITEMS) {
    throw new ValidationException("ERR_001");
}
```

Ambiguity: MIN_ITEMS constant not defined; error code ERR_001 meaning unknown

Options:
1. [Specify] MIN_ITEMS = 1, ERR_001 = "Order must have items"
2. [Business rule] Minimum order size requirement
3. [Skip] Review later

Your choice: 1

Enter MIN_ITEMS value: 1
Enter ERR_001 message: Order must contain at least one item

Resolved! Confidence updated: low → high
Applied to 2 similar patterns.

=== Clarification Required [2/15] ===
...
```

### Batch Processing

```
User: /reforge.clarify --all --category business-rules

Agent: Processing 8 business rule clarifications...

[1/8] CL-001: Magic numbers in discount logic
      → Resolved: 10% discount over $100

[2/8] CL-005: Unclear validation rule
      → Resolved: Age verification for restricted products

[3/8] CL-007: Ambiguous calculation
      → Skipped: Needs domain expert input

...

Batch complete!
- Resolved: 6
- Skipped: 2

Updated extractions:
- BR-045: low → high
- BR-089: low → high
- BR-102: low → medium
...
```
