# Data Model: Common Extraction Schema

**Feature**: 009-common-extraction-schema
**Date**: 2026-02-20

## Entities

### CommonSchema

The authoritative definition of shared structural elements across all extraction types.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| namespace | URI | Yes | `http://reforge.dev/schema/extraction` — single shared namespace |
| schema-version | semver string | Yes | Current version: `1.0.0` |
| root-attributes | RootAttributeSet | Yes | Standardized attributes for all extraction root elements |
| metadata | MetadataType | Yes | Standardized metadata container |
| source-reference | SourceReferenceType | Yes | Canonical source file reference format |
| confidence | ConfidenceType | Yes | Enumeration: high, medium, low |
| id-pattern | string (convention) | Yes | `{PREFIX}-{CATEGORY}-{SEQUENCE}` |

### RootAttributeSet

Attributes required on every extraction XML root element.

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `project-id` | string | Yes | Reference to analysis project |
| `version` | semver string | Yes | Extraction content version |
| `schema-version` | semver string | Yes | Common schema version (initially `1.0.0`) |
| `generated` | ISO-8601 dateTime | Yes | Extraction timestamp |
| `xmlns` | URI | Yes | `http://reforge.dev/schema/extraction` |

### MetadataType

Required child element of every extraction root.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `total-count` | integer | Yes | Total items extracted |
| `confidence-distribution` | ConfidenceDistribution | Yes | Breakdown by confidence level |
| `extraction-timestamp` | ISO-8601 dateTime | Yes | When extraction was performed |

### ConfidenceDistribution

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `high` | integer | Yes | Count of high-confidence items |
| `medium` | integer | Yes | Count of medium-confidence items |
| `low` | integer | Yes | Count of low-confidence items |

**Validation rule**: `high + medium + low` MUST equal `total-count` in parent MetadataType.

### SourceReferenceType

Canonical format for source code traceability.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `file` | string (attribute) | Yes | Relative file path |
| `line-start` | integer (attribute) | Yes | Starting line number |
| `line-end` | integer (attribute) | Yes | Ending line number |
| `snippet` | string (child element) | No | Actual code snippet |

### ConfidenceType

Enumeration for extraction confidence level.

| Value | Description |
|-------|-------------|
| `high` | Item clearly identified with verified source references |
| `medium` | Item identified but may need verification |
| `low` | Possible item, requires human review |

### SchemaWarning

Inline XML comment inserted when validation detects uncorrectable violations.

| Field | Type | Description |
|-------|------|-------------|
| format | XML comment | `<!-- SCHEMA-WARNING: [description] -->` |
| placement | inline | Inserted at the point of violation |

## Relationships

```
CommonSchema 1──────* TypeSpecificSchema    "is referenced by"
CommonSchema 1──────* ExtractionOutput      "validates"
TypeSpecificSchema 1──* ExtractionOutput    "defines structure for"

CommonSchema contains:
  ├── RootAttributeSet (1:1)
  ├── MetadataType (1:1)
  │   └── ConfidenceDistribution (1:1)
  ├── SourceReferenceType (1:1)
  └── ConfidenceType (1:1)
```

## Type-Specific Extensions

Each type-specific schema adds domain elements on top of the common schema:

| Type | Root Element | Type-Specific Elements |
|------|-------------|----------------------|
| business-rules | `<business-rules>` | `<rule>` with `<description>`, `<logic>`, `<entities>`, `<related-rules>` |
| database | `<database>` | `<data-model>` with `<entity>`, `<column>`, `<relationship>`; `<interactions>` with `<interaction>` |
| ui-flows | `<ui-flows>` | `<screens>` with `<screen>`, `<component>`, `<layout>`; `<navigation>` with `<flow>` |
| workflows | `<workflows>` | `<workflow>` with `<steps>`, `<step>`, `<branches>`, `<related>` |

## State Transitions

N/A — Schema definitions are static artifacts. No runtime state changes.

## Validation Rules

1. `confidence-distribution` counts MUST sum to `total-count`
2. `schema-version` MUST follow semver pattern (`MAJOR.MINOR.PATCH`)
3. `generated` MUST be valid ISO-8601 dateTime
4. `xmlns` MUST be `http://reforge.dev/schema/extraction`
5. `project-id` MUST be non-empty
6. `line-start` MUST be ≤ `line-end`
7. `file` attribute MUST be a relative path (no leading `/`)
8. Item IDs MUST follow `{PREFIX}-{CATEGORY}-{SEQUENCE}` convention
