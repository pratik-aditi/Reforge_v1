# Glossary Schema

> Defines the structure for the acronym glossary extraction (`acronym-glossary.xml`), the glossary audit report (`glossary-audit-report.xml`), checkpoints, and memory lookup.

## Overview

The glossary schema captures acronyms and abbreviations extracted by `/reforge.glossary`. Each entry includes the term, its expansion, confidence score, evidence chain, category, and verification status. The glossary progresses through 4 phases with semantic versioning.

## Common Elements

This schema extends the [Common Extraction Schema](./common-schema.md), which defines shared structural elements used across all extraction types:

- **Root attributes**: `project-id`, `version`, `schema-version`, `generated`, `xmlns`
- **Metadata container**: `<metadata>` with `<total-count>`, `<confidence-distribution>`, `<extraction-timestamp>`
- **Source references**: Canonical `<source>` format with `file`, `line-start`, `line-end` attributes
- **Confidence vocabulary**: `high`, `medium`, `low` enumeration
- **ID patterns**: `GLOSS-{SEQUENCE}` format

See `common-schema.md` for complete definitions. Elements defined there MUST NOT be redefined in this schema.

## Root Element

```xml
<acronym-glossary xmlns="http://reforge.dev/schema/extraction"
                  project-id="my-app" version="v1.3.0"
                  schema-version="1.0.0"
                  generated="2026-02-23T14:30:00Z">
  <metadata>...</metadata>
  <entry>...</entry>
</acronym-glossary>
```

### Attributes

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `xmlns` | URI | Yes | Must be `http://reforge.dev/schema/extraction` |
| `project-id` | string | Yes | Reference to analysis project |
| `version` | string | Yes | Glossary version (see Version Lifecycle below) |
| `schema-version` | string | Yes | Common schema version (initial: `1.0.0`) |
| `generated` | dateTime | Yes | Extraction timestamp (ISO-8601) |

> Root attributes and `<metadata>` are defined by the [Common Extraction Schema](./common-schema.md). The `<metadata>` element is required as the first child of the root element.

### Confidence Mapping

The glossary uses numeric confidence scores (0.0-1.0) internally. For common-schema compatibility, these map to the standard vocabulary:

| Numeric Range | Common-Schema Value |
|---------------|-------------------|
| 0.8 - 1.0 | `high` |
| 0.5 - 0.79 | `medium` |
| 0.0 - 0.49 | `low` |

The `<confidence-distribution>` in `<metadata>` uses these mapped values.

## Elements

### `<entry>`

Individual glossary entry with full traceability.

```xml
<entry id="GLOSS-001" term="TMDS" confidence="0.95" category="domain"
       verification-status="CONFIRMED" version-added="v1.0.0" version-modified="v1.2.0">
  <expansion>Train Management Dispatch System</expansion>
  <evidence>
    <source file="src/tmds/core/Dispatcher.java" line-start="12" line-end="12"
            evidence-type="doc-comment" phase="1">
      <snippet>/** TMDS - Train Management Dispatch System */</snippet>
    </source>
    <source file="src/tmds/config/AppConfig.java" line-start="45" line-end="45"
            evidence-type="string-literal" phase="3">
      <snippet>"TMDS_SERVICE_NAME"</snippet>
    </source>
  </evidence>
</entry>
```

#### Entry Attributes

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string | Yes | Unique identifier, pattern: `GLOSS-{SEQUENCE}` (e.g., `GLOSS-001`) |
| `term` | string | Yes | The acronym/abbreviation exactly as found in source |
| `confidence` | float | Yes | Confidence score 0.0-1.0 |
| `category` | enum | Yes | One of: `domain`, `technical`, `organizational`, `process`, `data` |
| `verification-status` | enum | Yes | One of: `CONFIRMED`, `CORRECTED`, `UNVERIFIED`, `FABRICATED`, `NOT_FOUND` |
| `version-added` | string | Yes | Glossary version when entry was first added |
| `version-modified` | string | No | Glossary version when entry was last modified |

#### Entry Child Elements

| Element | Type | Required | Description |
|---------|------|----------|-------------|
| `<expansion>` | string | Yes | Full expansion of the acronym |
| `<evidence>` | container | Yes | One or more `<source>` elements (min 1) |

### `<source>` (within `<evidence>`)

Extends the common-schema `<source>` format with glossary-specific attributes.

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `file` | string | Yes | Relative file path from project root |
| `line-start` | integer | Yes | Starting line number (> 0) |
| `line-end` | integer | No | Ending line number (>= line-start) |
| `evidence-type` | enum | Yes | One of: `code-comment`, `doc-comment`, `enum-definition`, `namespace`, `string-literal`, `variable-name`, `region-label`, `external-source` |
| `phase` | integer | Yes | Phase in which this evidence was collected (1-4) |

#### Evidence Validation Rules

| Rule | Description |
|------|-------------|
| MIN_EVIDENCE | Each entry MUST have at least one `<source>` element |
| NO_LLM_FILES | `file` MUST NOT be an LLM-authored file: `CLAUDE.md`, `README.md`, `project-context.md`, `analysis.xml` |
| PHASE_RANGE | `phase` MUST be 1, 2, 3, or 4 |
| VALID_TYPE | `evidence-type` MUST be one of the enumerated values |

### Verification Status Values

| Status | Meaning | Set By |
|--------|---------|--------|
| `CONFIRMED` | Term and expansion verified in source or external reference | Phase 2, 3, or 4 |
| `CORRECTED` | Expansion was updated based on better evidence | Phase 2, 3, or 4 |
| `UNVERIFIED` | Term exists but expansion not independently verified; confidence capped at 0.5 | Phase 1 (initial), Phase 3 |
| `FABRICATED` | Zero word-boundary grep matches; entry marked for deletion | Phase 3, 4 |
| `NOT_FOUND` | Not a recognized acronym per external sources | Phase 2 |

### Category Values

| Category | Description |
|----------|-------------|
| `domain` | Business domain-specific terms (e.g., TMDS, RUMO) |
| `technical` | Technical/infrastructure terms (e.g., ORM, MVC) |
| `organizational` | Organization-specific terms (e.g., department codes) |
| `process` | Business process terms (e.g., SLA, KPI) |
| `data` | Data-related terms (e.g., ETL, OLAP) |

---

## Glossary Audit Report

The glossary audit report documents all verification findings from Phases 3 and 4.

### Root Element

```xml
<glossary-audit-report project-id="my-app" version="1.0.0"
                       generated="2026-02-23T14:45:00Z"
                       glossary-version="v1.3.0"
                       total-findings="42"
                       confirmed-count="37" corrected-count="2"
                       fabricated-count="3" unverifiable-count="0">
  <findings>
    <finding>...</finding>
  </findings>
  <summary>...</summary>
</glossary-audit-report>
```

### Audit Report Attributes

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `project-id` | string | Yes | Reference to analysis project |
| `version` | string | Yes | Report schema version |
| `generated` | dateTime | Yes | Report generation timestamp (ISO-8601) |
| `glossary-version` | string | Yes | Glossary version at time of audit |
| `total-findings` | integer | Yes | Total audit findings |
| `confirmed-count` | integer | Yes | Entries confirmed by audit |
| `corrected-count` | integer | Yes | Entries corrected by audit |
| `fabricated-count` | integer | Yes | Entries identified as fabricated |
| `unverifiable-count` | integer | Yes | Entries that could not be verified |

### `<finding>`

```xml
<finding entry-id="GLOSS-005" term="TCOS" phase="3"
         verdict="CORRECTED" grep-count="14" action="UPDATE">
  <evidence-files>
    <file>src/tcos/MainController.java</file>
    <file>src/tcos/config/TcosConfig.java</file>
  </evidence-files>
  <original-expansion>Technical Control Operating System</original-expansion>
  <corrected-expansion>Train Control and Operating System</corrected-expansion>
  <rationale>Source code comments consistently use "Train Control and Operating System" across 14 files.</rationale>
</finding>
```

#### Finding Attributes

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `entry-id` | string | Yes | Reference to GlossaryEntry.id |
| `term` | string | Yes | The acronym being audited |
| `phase` | integer | Yes | Phase that produced this finding (3 or 4) |
| `verdict` | enum | Yes | One of: `CONFIRMED`, `CORRECTED`, `FABRICATED`, `UNVERIFIABLE` |
| `grep-count` | integer | Yes | Word-boundary grep match count across source files |
| `action` | enum | Yes | One of: `KEEP`, `UPDATE`, `DELETE`, `FLAG_FOR_REVIEW` |

> **Note**: `UNVERIFIABLE` in audit findings is distinct from `UNVERIFIED` in glossary entry status. `UNVERIFIABLE` means the audit could not reach a definitive conclusion; `UNVERIFIED` means no external/source evidence was found for the expansion.

#### Finding Child Elements

| Element | Type | Required | Description |
|---------|------|----------|-------------|
| `<evidence-files>` | container | No | List of `<file>` elements where term was found |
| `<original-expansion>` | string | No | Previous expansion (when verdict is `CORRECTED`) |
| `<corrected-expansion>` | string | No | New expansion (when verdict is `CORRECTED`) |
| `<rationale>` | string | Yes | Explanation of the verdict |

### `<summary>`

```xml
<summary>
  <phase-3-summary entries-audited="42" confirmed="35" corrected="2"
                   fabricated="3" unverifiable="2" elapsed-time="4m 12s"/>
  <phase-4-summary entries-re-verified="7" confirmed="5" corrected="0"
                   fabricated="0" unverifiable="2" elapsed-time="2m 05s"/>
</summary>
```

---

## Checkpoint Format (JSON)

Saved to `.reforge/memory/checkpoints/glossary-checkpoint.json` after each phase.

```json
{
  "feature": "glossary",
  "last-completed-phase": 2,
  "current-version": "v1.1.0",
  "entry-count": 45,
  "phases-skipped": [],
  "timestamp": "2026-02-23T14:20:00Z",
  "team-size": 3
}
```

### Checkpoint Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `feature` | string | Yes | Always `"glossary"` |
| `last-completed-phase` | integer | Yes | 0-4 (0 = no phases completed) |
| `current-version` | string | Yes | Current glossary version |
| `entry-count` | integer | Yes | Number of entries at checkpoint |
| `phases-skipped` | integer[] | No | Phase numbers skipped (e.g., `[2]` for `--skip-external`) |
| `timestamp` | string | Yes | ISO-8601 timestamp |
| `team-size` | integer | Yes | Team size used for this run |

---

## Memory Lookup Format (JSON)

Saved to `.reforge/memory/glossary.json` after final phase. Consumed by all other Reforge commands.

```json
{
  "version": "v1.3.0",
  "generated": "2026-02-23T14:30:00Z",
  "entry-count": 42,
  "terms": {
    "TMDS": {
      "expansion": "Train Management Dispatch System",
      "confidence": 1.0,
      "category": "domain"
    },
    "RUMO": {
      "expansion": "Route Management Operations",
      "confidence": 0.85,
      "category": "domain"
    }
  }
}
```

### Memory Lookup Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `version` | string | Yes | Glossary version that produced this lookup |
| `generated` | string | Yes | ISO-8601 timestamp |
| `entry-count` | integer | Yes | Total entries in lookup |
| `terms` | object | Yes | Key-value map of acronyms to their data |
| `terms[key].expansion` | string | Yes | Full expansion |
| `terms[key].confidence` | float | Yes | Final confidence score (0.0-1.0) |
| `terms[key].category` | string | Yes | Category from GlossaryEntry |

---

## Version Lifecycle

| Version | Phase | Description |
|---------|-------|-------------|
| `v1.0.0` | Phase 1 | Initial draft from pattern extraction |
| `v1.1.0` | Phase 2 | After external verification (skipped if `--skip-external`) |
| `v1.2.0` | Phase 3 | After source code audit |
| `v1.3.0` | Phase 4 | Final version after self-audit |

**Note**: When `--skip-external` is used, v1.1.0 is skipped. The version progression becomes v1.0.0 → v1.2.0 → v1.3.0.

---

## Type Registration

Per common-schema extensibility guidelines:

| Registration | Value |
|-------------|-------|
| Root Element Name | `<acronym-glossary>` |
| Type Prefix | `GLOSS` |
| ID Pattern | `GLOSS-{SEQUENCE}` (e.g., `GLOSS-001`) |

---

## Validation Rules

| Rule | Description |
|------|-------------|
| UNIQUE_TERM | Entries MUST be unique by `term` (case-sensitive) |
| MIN_EVIDENCE | Each entry MUST have at least one evidence `<source>` |
| NO_LLM_FILES | Evidence `file` MUST NOT reference LLM-authored files |
| CONFIDENCE_RANGE | `confidence` MUST be between 0.0 and 1.0 |
| FABRICATED_CAP | `FABRICATED` entries MUST have `grep-count` = 0 |
| UNVERIFIED_CAP | `UNVERIFIED` entries MUST have `confidence` ≤ 0.5 |
| VERSION_SEQUENCE | Glossary `version` MUST follow the version lifecycle progression |
| SUM_CHECK | Metadata `confidence-distribution` counts MUST sum to `total-count` |
