# Contract: Common Extraction Schema

**Feature**: 009-common-extraction-schema
**Date**: 2026-02-20
**Version**: 1.0.0

## Overview

This contract defines the structural interface that all extraction output XML files MUST conform to. It specifies the common elements shared across business-rules, database, ui-flows, and workflows extraction types.

## Namespace

```
http://reforge.dev/schema/extraction
```

All extraction output files use this single shared namespace.

## Root Element Contract

Every extraction XML root element MUST include these attributes:

```xml
<{root-element}
    xmlns="http://reforge.dev/schema/extraction"
    project-id="{string}"
    version="{semver}"
    schema-version="1.0.0"
    generated="{ISO-8601-dateTime}">
  <metadata>...</metadata>
  <!-- type-specific content -->
</{root-element}>
```

### Root Attribute Specification

| Attribute | Type | Required | Validation |
|-----------|------|----------|------------|
| `xmlns` | URI | Yes | Must be `http://reforge.dev/schema/extraction` |
| `project-id` | string | Yes | Non-empty. References the analysis project name. |
| `version` | string | Yes | Semver pattern: `MAJOR.MINOR.PATCH` |
| `schema-version` | string | Yes | Common schema version. Initial: `1.0.0` |
| `generated` | dateTime | Yes | ISO-8601 format: `YYYY-MM-DDTHH:MM:SSZ` |

### Root Element Names (per type)

| Extraction Type | Root Element |
|----------------|-------------|
| business-rules | `<business-rules>` |
| database | `<database>` |
| ui-flows | `<ui-flows>` |
| workflows | `<workflows>` |

## Metadata Contract

Every extraction root MUST contain a `<metadata>` child element as its first child:

```xml
<metadata>
  <total-count>{integer}</total-count>
  <confidence-distribution>
    <high>{integer}</high>
    <medium>{integer}</medium>
    <low>{integer}</low>
  </confidence-distribution>
  <extraction-timestamp>{ISO-8601-dateTime}</extraction-timestamp>
</metadata>
```

### Metadata Validation Rules

| Rule | Description |
|------|-------------|
| SUM_CHECK | `high + medium + low` MUST equal `total-count` |
| NON_NEGATIVE | All count values MUST be ≥ 0 |
| TIMESTAMP_FORMAT | `extraction-timestamp` MUST be valid ISO-8601 |

## Source Reference Contract

All source code references MUST use this canonical format:

```xml
<source file="{relative-path}" line-start="{integer}" line-end="{integer}">
  <snippet>{optional-code-snippet}</snippet>
</source>
```

### Source Reference Validation Rules

| Rule | Description |
|------|-------------|
| RELATIVE_PATH | `file` MUST be relative (no leading `/`) |
| LINE_ORDER | `line-start` MUST be ≤ `line-end` |
| POSITIVE_LINES | Both line numbers MUST be > 0 |
| SNIPPET_OPTIONAL | `<snippet>` is optional; when present, must be verbatim source |

### Normalization Rules

Legacy source reference formats MUST be normalized to canonical format:

| Legacy Format | Canonical Format |
|--------------|-----------------|
| `line="145-160"` | `line-start="145" line-end="160"` |
| `lines="45,46,47"` | `line-start="45" line-end="47"` |
| `<LineNumber>45</LineNumber>` | `line-start="45" line-end="45"` |

## Confidence Vocabulary Contract

All `confidence` attributes MUST use one of these values:

| Value | Meaning |
|-------|---------|
| `high` | Item clearly identified with verified source references |
| `medium` | Item identified but may need verification |
| `low` | Possible item, requires human review |

No other values are permitted.

## ID Pattern Contract

Extraction item IDs MUST follow this convention:

```
{TYPE_PREFIX}-{CATEGORY}-{SEQUENCE}
```

| Component | Format | Examples |
|-----------|--------|----------|
| TYPE_PREFIX | 2-3 uppercase letters | `BR`, `DB`, `E`, `SCR`, `CMP`, `WF` |
| CATEGORY | uppercase short code | `VAL`, `AUTH`, `CALC`, `SEL`, `INS` |
| SEQUENCE | zero-padded 3 digits | `001`, `002`, `099` |

### Type Prefix Registry

| Prefix | Extraction Type | Item Type |
|--------|----------------|-----------|
| `BR` | business-rules | Business rule |
| `DB` | database | Database interaction |
| `E` | database | Data entity |
| `SCR` | ui-flows | Screen |
| `CMP` | ui-flows | UI component |
| `WF` | workflows | Workflow |

## Validation Gate Contract

The `/reforge.extract` command MUST perform these checks before writing output:

### Required Checks

1. **Root attributes present**: `project-id`, `version`, `schema-version`, `generated`, `xmlns`
2. **Namespace correct**: `xmlns` equals `http://reforge.dev/schema/extraction`
3. **Metadata present**: `<metadata>` element exists with all required children
4. **Count consistency**: `confidence-distribution` sums to `total-count`
5. **Source format**: All `<source>` elements use canonical format (no legacy variants)
6. **Schema version**: `schema-version` attribute present and valid semver

### Auto-Correction Behavior

| Violation | Auto-Correction |
|-----------|----------------|
| Missing `schema-version` attribute | Add `schema-version="1.0.0"` |
| Missing `xmlns` | Add `xmlns="http://reforge.dev/schema/extraction"` |
| Missing `<metadata>` section | Generate from item counts |
| Legacy source reference format | Normalize to `line-start`/`line-end` |
| Missing `generated` timestamp | Add current timestamp |

### Warning Behavior

When auto-correction is not possible:
- Insert `<!-- SCHEMA-WARNING: [description] -->` at violation point
- Continue writing the file (do not abort)
- Include warning summary in extraction report

## Legacy File Handling Contract

Files without a `schema-version` attribute are treated as pre-common-schema legacy files:

| Behavior | Description |
|----------|-------------|
| Detection | Absence of `schema-version` attribute on root element |
| Warning | Emit: "⚠️ Legacy extraction file detected (no schema-version). Output may use inconsistent element names." |
| Parsing | Downstream commands attempt best-effort parsing with known legacy patterns |
| Failure mode | Never crash on legacy files — degrade gracefully with warnings |

## Example: Conformant Output

```xml
<?xml version="1.0" encoding="UTF-8"?>
<business-rules xmlns="http://reforge.dev/schema/extraction"
                project-id="ecommerce-legacy"
                version="1.0.0"
                schema-version="1.0.0"
                generated="2026-02-20T10:30:00Z">

  <metadata>
    <total-count>2</total-count>
    <confidence-distribution>
      <high>2</high>
      <medium>0</medium>
      <low>0</low>
    </confidence-distribution>
    <extraction-timestamp>2026-02-20T10:30:00Z</extraction-timestamp>
  </metadata>

  <rule id="BR-VAL-001" category="validation" confidence="high">
    <description>Order must have at least one line item</description>
    <logic>order.items.count MUST BE >= 1</logic>
    <source file="src/model/Order.java" line-start="78" line-end="82">
      <snippet>if (items == null || items.isEmpty()) {
    throw new ValidationException("Order must contain items");
}</snippet>
    </source>
    <entities>
      <entity>Order</entity>
    </entities>
  </rule>

  <rule id="BR-CALC-001" category="pricing" confidence="high">
    <description>Apply 10% discount for orders over $100</description>
    <logic>IF order.total > 100 THEN discount = order.total * 0.10</logic>
    <source file="src/service/PricingService.java" line-start="45" line-end="52">
      <snippet>if (order.getTotal().compareTo(DISCOUNT_THRESHOLD) > 0) {
    order.setDiscount(order.getTotal().multiply(DISCOUNT_RATE));
}</snippet>
    </source>
    <entities>
      <entity>Order</entity>
    </entities>
  </rule>

</business-rules>
```
