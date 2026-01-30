# Data Model: XSD Validation Tooling

**Feature**: 004-xsd-validation-tooling
**Date**: 2026-01-29

## Overview

This document defines the data structures used by the XSD validation tooling feature.

---

## Core Entities

### ValidationResult

Represents the outcome of validating an XML file against an XSD schema.

```python
@dataclass
class ValidationResult:
    """Result of XML schema validation."""

    # Status
    valid: bool                    # True if XML passes validation
    exit_code: int                 # 0=valid, 1=invalid, 2=system error

    # Context
    xml_file: str                  # Path to validated XML file
    schema_type: str               # Schema type (e.g., "business-rules")
    schema_file: str               # Path to XSD file used

    # Errors (empty if valid)
    errors: list[ValidationError]  # List of validation errors
    error_count: int               # Total error count

    # Metadata
    elapsed_ms: int                # Validation duration in milliseconds
    xmllint_version: str | None    # Version of xmllint used
```

### ValidationError

Represents a single validation error with location and suggestion.

```python
@dataclass
class ValidationError:
    """Single validation error from xmllint."""

    line: int                      # Line number (1-indexed)
    column: int | None             # Column number (if available)
    element: str | None            # Element name (if parsed from error)
    message: str                   # Error message from xmllint
    suggestion: str | None         # AI-generated fix suggestion
    raw_output: str                # Original xmllint output line
```

---

## Output Formats

### Structured Text Format (Default)

Used for LLM consumption. Fields in CAPS, errors delimited by `---`.

**Success Output**:
```
VALIDATION_OK
FILE: reforge_output/myapp/extractions/business-rules.xml
SCHEMA: business-rules
ELAPSED_MS: 156
```

**Failure Output**:
```
VALIDATION_FAILED
FILE: reforge_output/myapp/extractions/business-rules.xml
SCHEMA: business-rules
ERROR_COUNT: 2
---
LINE: 45
COLUMN: 12
ELEMENT: ruel
MESSAGE: Element 'ruel': This element is not expected. Expected is 'rule'.
SUGGESTION: Check spelling of element name on line 45. Expected 'rule' not 'ruel'.
---
LINE: 67
COLUMN: 5
ELEMENT: rule
MESSAGE: Element 'rule': Missing required attribute 'id'.
SUGGESTION: Add id attribute to <rule> element on line 67.
```

### JSON Format (--json flag)

For programmatic consumption and testing.

```json
{
  "valid": false,
  "exit_code": 1,
  "xml_file": "reforge_output/myapp/extractions/business-rules.xml",
  "schema_type": "business-rules",
  "schema_file": ".reforge/schemas/xsd/business-rules.xsd",
  "error_count": 2,
  "elapsed_ms": 156,
  "xmllint_version": "20914",
  "errors": [
    {
      "line": 45,
      "column": 12,
      "element": "ruel",
      "message": "Element 'ruel': This element is not expected. Expected is 'rule'.",
      "suggestion": "Check spelling of element name on line 45. Expected 'rule' not 'ruel'."
    },
    {
      "line": 67,
      "column": 5,
      "element": "rule",
      "message": "Element 'rule': Missing required attribute 'id'.",
      "suggestion": "Add id attribute to <rule> element on line 67."
    }
  ]
}
```

---

## Schema Registry

Available schema types mapped to XSD files.

| Schema Type | XSD Filename | Source Spec |
|-------------|--------------|-------------|
| `analysis` | analysis.xsd | 001-legacy-analyzer |
| `business-rules` | business-rules.xsd | 001-legacy-analyzer |
| `database` | database.xsd | 001-legacy-analyzer |
| `ui-flows` | ui-flows.xsd | 001-legacy-analyzer |
| `workflows` | workflows.xsd | 001-legacy-analyzer |
| `user-stories` | user-stories.xsd | 001-legacy-analyzer |
| `audit-report` | audit-report.xsd | 002-audit-fix-commands |
| `correction-plan` | correction-plan.xsd | 002-audit-fix-commands |

---

## Exit Codes

| Code | Constant | Meaning |
|------|----------|---------|
| 0 | `EXIT_VALID` | XML passes schema validation |
| 1 | `EXIT_INVALID` | XML fails schema validation |
| 2 | `EXIT_ERROR` | System/usage error (missing file, no xmllint, bad args) |

---

## Error Categories

Validation errors are categorized for suggestion generation:

| Category | Pattern | Suggestion Template |
|----------|---------|---------------------|
| Unknown element | "This element is not expected" | "Check spelling of element name on line {line}" |
| Missing attribute | "Missing required attribute" | "Add {attr} attribute to <{element}> on line {line}" |
| Invalid attribute value | "not a valid value" | "Check value of {attr} attribute on line {line}" |
| Missing element | "Missing child element" | "Add required <{element}> child element on line {line}" |
| Wrong order | "expected before" | "Reorder elements on line {line}" |
| Extra content | "character content is not allowed" | "Remove text content from <{element}> on line {line}" |

---

## File Locations

### Source (Development)
```
specs/001-legacy-analyzer/contracts/*.xsd   # Original XSD files
specs/002-audit-fix-commands/contracts/*.xsd
```

### Deployed (Target Projects)
```
.reforge/schemas/xsd/*.xsd                  # Installed XSD files
```

### Package Distribution
```
share/reforge-cli/.reforge/schemas/xsd/*.xsd  # Wheel shared-data
```

---

## Validation Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    reforge-scripts validate-xml                  │
└─────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│ 1. Check xmllint availability                                    │
│    └─ If missing: Return EXIT_ERROR with install instructions   │
└─────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│ 2. Validate arguments                                            │
│    └─ xml_file exists? schema_type valid?                       │
│    └─ If not: Return EXIT_ERROR with usage message              │
└─────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│ 3. Resolve schema path                                           │
│    └─ .reforge/schemas/xsd/{schema_type}.xsd                    │
│    └─ If not found: Return EXIT_ERROR with missing schema msg   │
└─────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│ 4. Execute xmllint                                               │
│    └─ xmllint --schema {xsd} {xml} --noout 2>&1                 │
└─────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│ 5. Parse output                                                  │
│    └─ Extract line, column, element, message from stderr        │
│    └─ Generate suggestions based on error patterns              │
└─────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│ 6. Format and return result                                      │
│    └─ Structured text (default) or JSON (--json)                │
│    └─ Set exit code: 0 (valid) or 1 (invalid)                   │
└─────────────────────────────────────────────────────────────────┘
```
