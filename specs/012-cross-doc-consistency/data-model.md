# Data Model: Cross-Document Consistency Checker

**Branch**: `012-cross-doc-consistency` | **Date**: 2026-02-23

## Entities

### Metrics Registry (`metrics-registry.xml`)

The authoritative store of all computed statistics for a project. One file per project, stored at `$PROJECT_OUTPUT_DIR/metrics-registry.xml`.

**Root attributes**:
- `project-id` (string, required): Project identifier matching analysis.xml
- `version` (string, required): Schema version (semver)
- `generated` (dateTime, required): Registry creation/update timestamp
- `total-metrics` (integer, required): Count of `<metric>` elements
- `source-extractions` (integer, required): Count of extraction XML files read

**Child sections**:
- `<configuration>` — Tolerance defaults, scan file types, exclusion list
- `<metrics>` — Collection of metric entries
- `<scan-patterns>` — Pattern definitions and qualifier patterns

### Metric Entry (`<metric>`)

A single computed statistic within the registry.

**Attributes**:
- `id` (string, required): Unique metric identifier. Pattern: `MET-{CATEGORY}-{NAME}` (e.g., `MET-FILE-TOTAL`, `MET-BR-COUNT`)
- `category` (enum, required): `codebase` | `extraction` | `generation` | `coverage`
- `name` (string, required): Human-readable metric name
- `value` (string, required): Canonical value (stored as string for numeric and percentage formats)
- `unit` (string, required): Unit of measurement (files, rules, requirements, modules, states, percent, etc.)
- `computation` (string, required): Formula or method used to derive the value
- `source` (string, required): Path to the extraction/analysis file(s) used as input
- `computed-at` (dateTime, required): Timestamp when the value was last computed

**Child elements**:
- `<breakdown>` (optional): For aggregate metrics, per-file/per-category components. Each `<component>` has `source` and `count`. Sum of component counts MUST equal metric `value`.
- `<references>` (required): List of `<ref file="..." line="..."/>` entries documenting every generated document location where this metric appears.
- `<tolerance>` (optional): Per-metric tolerance override with `qualifier` and `percent` or `direction` attributes.

**Uniqueness**: `id` is unique within the registry.

**Lifecycle**: Created during generation (Step 0.7), recomputed on each audit run, updated during post-generation scan (references section).

### Configuration (`<configuration>`)

Tolerance defaults and scan settings within the registry.

**Child elements**:
- `<tolerance-defaults>`: Collection of `<tolerance>` rules with `qualifier`, `percent`, and `direction` attributes
- `<scan-file-types>`: Collection of `<file-type>` entries with `extension` and `parser` attributes
- `<exclusion-list>`: Collection of `<exclude>` entries for intentionally ignored unregistered metric patterns, each with `pattern-text`, `added-by`, and `added-at` attributes

### Scan Pattern (`<pattern>`)

A named rule for recognizing a metric category in document text.

**Attributes**:
- `id` (string, required): Pattern identifier (e.g., `PAT-FILE-COUNT`)
- `description` (string, required): Human-readable description of what this pattern matches (used by the LLM agent to recognize metrics)
- `metric-category` (string, required): Which metric category this pattern typically maps to
- `metric-hint` (string, optional): Suggested metric ID for disambiguation

**Child element**: `<qualifier-patterns>` defines approximate value qualifiers (approximate, nearly, over, under).

### Discrepancy

A detected mismatch between a document's numeric claim and the registry's canonical value. Appears in the consistency audit report.

**Attributes**:
- `id` (string, required): Unique discrepancy ID (DIS-NNN)
- `severity` (enum, required): `critical` | `warning` | `info`
- `metric-id` (string, required): Registry metric ID, or `UNREGISTERED`
- `registry-value` (string, required): Canonical value from registry (empty if unregistered)
- `document-value` (string, required): Value extracted from the document
- `file` (string, required): Relative path to the document file
- `line` (integer, required): Line number in the document
- `context` (string, required): Surrounding text snippet
- `confidence` (enum, required): `high` | `medium` | `low` — match confidence. Assignment criteria: `high` = scan pattern matched AND metric unit/noun matched (e.g., "864 source files" matches MET-FILE-TOTAL); `medium` = scan pattern matched but unit/noun ambiguous or value requires normalization; `low` = value-proximity match only with no supporting pattern or noun context (e.g., bare number "864" near no descriptive text)
- `action` (enum, required): `regenerate` | `review` | `register-or-ignore` | `investigate`
- `pattern-id` (string, optional): Which scan pattern matched
- `qualifier` (string, optional): Tolerance qualifier if approximate
- `tolerance-percent` (decimal, optional): Tolerance percentage applied

### Correction Item (extension to existing schema)

Two new CorrectionType values added to the existing correction-plan.md schema:

| New Type | Description | Typical Action |
|----------|-------------|----------------|
| `metric-mismatch` | Document value contradicts metrics registry | `/reforge.generate <doc-type> --refresh-metrics` |
| `unregistered-metric` | Document contains untracked numeric claim | Add metric to registry or add to exclusion list |

One new CategoryType value:

| New Category | Description | Priority Order |
|--------------|-------------|---------------|
| `metrics-consistency` | Issue detected by metrics registry scan | After `cross-document` (5th), before `generation` (6th) |

## Relationships

```
analysis.xml ──────────┐
                       │ (source data)
extraction/*.xml ──────┤
                       ▼
              metrics-registry.xml
                       │
          ┌────────────┼────────────┐
          │            │            │ (references by metric ID)
          ▼            ▼            ▼
    report-1.html  diagram.puml  report-2.md
          │            │            │
          └────────────┼────────────┘
                       │ (post-generation scan)
                       ▼
         consistency-audit-report.xml
                       │
                       ▼
            correction-plan.xml
                       │ (fix execution)
                       ▼
               /reforge.fix
```

## State Transitions

### Metric Entry Lifecycle

```
[computed] ──(generation run)──> [referenced] ──(audit recompute)──> [revalidated]
                                       │
                                       └──(stale extraction)──> [outdated] ──(recompute)──> [revalidated]
```

### Discrepancy Lifecycle

```
[detected] ──(severity classified)──> [reported] ──(correction generated)──> [actionable]
     │                                                                            │
     └──(excluded pattern)──> [suppressed]                    [completed] <──(fix run)──┘
```

## Validation Rules

1. **Breakdown integrity**: For every metric with `<breakdown>`, `sum(component/@count) == metric/@value`
2. **Metric ID uniqueness**: No duplicate `id` values within `<metrics>`
3. **Reference accuracy**: Every `<ref>` in a metric's `<references>` section must correspond to an actual occurrence in the cited file
4. **Tolerance bounds**: `percent` values must be non-negative decimals; `direction` must be `gte` or `lte`
5. **Pattern coverage**: Every metric category must have at least one corresponding scan pattern
6. **Exclusion integrity**: Excluded patterns must not match any registered metric ID
