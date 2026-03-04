# Common Extraction Schema

**Version**: 1.0.0
**Namespace**: `http://reforge.dev/schema/extraction`
**XSD**: [xsd/common-schema.xsd](./xsd/common-schema.xsd)

## Overview

This document defines the shared structural elements that ALL extraction output XML files MUST conform to. It is the authoritative reference for root attributes, metadata, source references, confidence vocabulary, and ID patterns used across business-rules, database, ui-flows, and workflows extraction types.

Type-specific schemas (e.g., `business-rules.md`, `database.md`) extend this common schema with domain-specific elements. They MUST NOT redefine any element specified here.

## Namespace

All extraction output files use a single shared namespace:

```
http://reforge.dev/schema/extraction
```

This namespace is used regardless of extraction type. Per-type namespaces (e.g., `http://reforge.dev/schema/business-rules`) are deprecated.

## Root Element Attributes

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

### Attribute Specification

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
| call-sites | `<call-sites>` |
| dependencies | `<dependencies>` |
| functional-requirements | `<functional-requirements>` |
| non-functional | `<non-functional-requirements>` |
| architecture | `<architecture>` |
| issues | `<issues>` |
| glossary | `<acronym-glossary>` |

## Metadata

Every extraction root MUST contain a `<metadata>` element as its **first child**:

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

### Metadata Elements

| Element | Type | Required | Description |
|---------|------|----------|-------------|
| `total-count` | integer | Yes | Total items extracted (must be ≥ 0) |
| `confidence-distribution` | container | Yes | Breakdown by confidence level |
| `confidence-distribution/high` | integer | Yes | Count of high-confidence items (≥ 0) |
| `confidence-distribution/medium` | integer | Yes | Count of medium-confidence items (≥ 0) |
| `confidence-distribution/low` | integer | Yes | Count of low-confidence items (≥ 0) |
| `extraction-timestamp` | dateTime | Yes | ISO-8601 format: `YYYY-MM-DDTHH:MM:SSZ` |

### Metadata Validation Rules

| Rule | Description |
|------|-------------|
| SUM_CHECK | `high + medium + low` MUST equal `total-count` |
| NON_NEGATIVE | All count values MUST be ≥ 0 |
| TIMESTAMP_FORMAT | `extraction-timestamp` MUST be valid ISO-8601 |

## Source References

All source code references MUST use this canonical format:

```xml
<source file="{relative-path}" line-start="{integer}" line-end="{integer}">
  <snippet>{optional-code-snippet}</snippet>
</source>
```

### Source Reference Attributes

| Attribute/Element | Type | Required | Description |
|-------------------|------|----------|-------------|
| `file` | string (attribute) | Yes | Relative file path (no leading `/`) |
| `line-start` | integer (attribute) | Yes | Starting line number (> 0) |
| `line-end` | integer (attribute) | Yes | Ending line number (> 0, ≥ `line-start`) |
| `snippet` | string (child element) | No | Verbatim source code excerpt |

### Source Reference Validation Rules

| Rule | Description |
|------|-------------|
| RELATIVE_PATH | `file` MUST be a relative path (no leading `/`) |
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

## Confidence Vocabulary

All `confidence` attributes MUST use one of these enumerated values:

| Value | Meaning |
|-------|---------|
| `high` | Item clearly identified with verified source references |
| `medium` | Item identified but may need verification |
| `low` | Possible item, requires human review |

No other values are permitted.

## ID Pattern Convention

Extraction item IDs MUST follow this convention:

```
{TYPE_PREFIX}-{CATEGORY}-{SEQUENCE}
```

| Component | Format | Description |
|-----------|--------|-------------|
| TYPE_PREFIX | 2-3 uppercase letters | Identifies extraction type and item kind |
| CATEGORY | uppercase short code | Domain-specific category (e.g., `VAL`, `AUTH`, `CALC`) |
| SEQUENCE | zero-padded 3 digits | Sequential number: `001`-`999` |

### Type Prefix Registry

| Prefix | Extraction Type | Item Type |
|--------|----------------|-----------|
| `BR` | business-rules | Business rule |
| `DB` | database | Database interaction |
| `E` | database | Data entity |
| `SCR` | ui-flows | Screen |
| `CMP` | ui-flows | UI component |
| `WF` | workflows | Workflow |
| `CALL` | call-sites | Method/function call relationship |
| `DEP` | dependencies | Module dependency reference |
| `FR` | functional-requirements | Functional requirement |
| `NFR` | non-functional | Non-functional requirement |
| `SEC` | non-functional | Security finding |
| `ARCH` | architecture | Architectural component |
| `INT` | architecture | Integration point |
| `DP` | architecture | Design pattern |
| `BUG` | issues | Bug or defect |
| `ISS` | issues | Technical debt / operational issue |
| `GLOSS` | glossary | Glossary entry |

### ID Examples

- `BR-VAL-001` — First business rule in the validation category
- `DB-SEL-003` — Third database interaction in the select category
- `E-CORE-001` — First core data entity
- `SCR-DASH-001` — First dashboard screen
- `WF-AUTH-002` — Second authentication workflow
- `CALL-SVC-001` — First service-layer call site
- `DEP-IMP-001` — First import dependency
- `FR-AUTH-001` — First authentication functional requirement
- `NFR-PERF-001` — First performance non-functional requirement
- `SEC-CWE-001` — First CWE security finding
- `ARCH-WEB-001` — First web-tier architectural component
- `INT-API-001` — First API integration point
- `DP-SING-001` — First singleton design pattern
- `BUG-NULL-001` — First null-reference bug
- `ISS-DEBT-001` — First technical debt issue
- `GLOSS-DOM-001` — First domain glossary entry

## Extensibility

Type-specific schemas extend this common schema by adding domain-specific child elements beneath the root. The common schema defines the structural envelope; type-specific schemas define the content within that envelope.

When adding new extraction types in the future:
1. Choose a root element name and register it in the Root Element Names table above
2. Register new type prefix(es) in the Type Prefix Registry
3. Create a type-specific schema that links to this common schema for shared elements
4. Create a corresponding XSD that uses `<xs:include schemaLocation="common-schema.xsd"/>`
5. All root attributes, metadata, source references, and confidence vocabulary are inherited — do not redefine

## Legacy File Handling

Files without a `schema-version` attribute are treated as pre-common-schema legacy files:

| Behavior | Description |
|----------|-------------|
| Detection | Absence of `schema-version` attribute on root element |
| Warning | Emit: "Legacy extraction file detected (no schema-version). Output may use inconsistent element names." |
| Parsing | Downstream commands attempt best-effort parsing with known legacy patterns |
| Failure mode | Never crash on legacy files — degrade gracefully with warnings |

## Validation Rules Summary

1. `confidence-distribution` counts MUST sum to `total-count`
2. `schema-version` MUST follow semver pattern (`MAJOR.MINOR.PATCH`)
3. `generated` MUST be valid ISO-8601 dateTime
4. `xmlns` MUST be `http://reforge.dev/schema/extraction`
5. `project-id` MUST be non-empty
6. `line-start` MUST be ≤ `line-end`
7. `file` attribute MUST be a relative path (no leading `/`)
8. Item IDs MUST follow `{PREFIX}-{CATEGORY}-{SEQUENCE}` convention
