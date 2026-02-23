# Data Model: Content Accuracy Audit

**Feature**: 011-content-accuracy-audit
**Date**: 2026-02-22

## Overview

This feature introduces 3 new XML output schemas (accuracy audit report, consistency audit report, full audit report), extends the existing correction plan schema with new types/attributes, and adds verification-related data structures used by the agent during audit execution. All entities are XML documents written to the `$AUDIT_DIR` directory.

## Entity Catalog

### New XML Schemas

| Entity | File | Schema Definition |
|--------|------|-------------------|
| Accuracy Audit Report | `accuracy-audit-report.xml` | `.reforge/schemas/accuracy-audit-report.md` (NEW) |
| Consistency Audit Report | `consistency-audit-report.xml` | `.reforge/schemas/consistency-audit-report.md` (NEW) |
| Full Audit Report | `full-audit-report.xml` | `.reforge/schemas/full-audit-report.md` (NEW) |
| Accuracy Correction Plan | `accuracy-correction-plan.xml` | `.reforge/schemas/correction-plan.md` (UPDATED) |
| Consistency Correction Plan | `consistency-correction-plan.xml` | `.reforge/schemas/correction-plan.md` (UPDATED) |

### Updated Existing Schemas

| Entity | File | Change |
|--------|------|--------|
| Correction Plan | `correction-plan.xml` | Add 6 new CorrectionType values, 2 new CategoryType values, 3 new attributes |

## Accuracy Audit Report

Root element: `<accuracy-audit-report>`

### Root Attributes

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `project-id` | string | Yes | Reference to analyzed project |
| `version` | string | Yes | Schema version (1.0.0) |
| `generated` | dateTime | Yes | Audit execution timestamp |
| `methodology` | enum | Yes | `sampling` or `census` |
| `sample-rate` | decimal | No | Sample rate used (e.g., 0.20). Present when methodology=sampling |
| `total-items` | integer | Yes | Total extraction items in corpus |
| `verified-items` | integer | Yes | Items actually verified |
| `accuracy-score` | decimal | Yes | (confirmed / verified) * 100 |

### Child Elements

#### `<sampling-metadata>` (conditional: present when methodology=sampling)

```xml
<sampling-metadata>
  <sample-rate>0.20</sample-rate>
  <total-population>{integer}</total-population>
  <sample-size>{integer}</sample-size>
  <confidence-level>95</confidence-level>
  <confidence-interval lower="{decimal}" upper="{decimal}"/>
  <margin-of-error>{decimal}</margin-of-error>
  <strata>
    <stratum category="business-rules" population="{N}" sampled="{M}" accuracy="{decimal}"/>
    <stratum category="database" population="{N}" sampled="{M}" accuracy="{decimal}"/>
    <stratum category="ui-flows" population="{N}" sampled="{M}" accuracy="{decimal}"/>
    <stratum category="workflows" population="{N}" sampled="{M}" accuracy="{decimal}"/>
  </strata>
</sampling-metadata>
```

#### `<accuracy-summary>`

```xml
<accuracy-summary>
  <overall accuracy="{decimal}" confirmed="{N}" plausible="{N}" incorrect="{N}" fabricated="{N}" skipped="{N}"/>
  <by-category>
    <category name="business-rules" accuracy="{decimal}" verified="{N}" confirmed="{N}" fabricated="{N}"/>
    <!-- per extraction type -->
  </by-category>
  <by-check-type>
    <check-type name="identifier-exists" total="{N}" passed="{N}" failed="{N}"/>
    <check-type name="term-exists" total="{N}" passed="{N}" failed="{N}"/>
    <check-type name="line-reference" total="{N}" passed="{N}" failed="{N}"/>
    <check-type name="content-match" total="{N}" passed="{N}" failed="{N}"/>
    <check-type name="expansion-match" total="{N}" passed="{N}" failed="{N}"/>
    <check-type name="count-match" total="{N}" passed="{N}" failed="{N}"/>
    <check-type name="relationship-match" total="{N}" passed="{N}" failed="{N}"/>
  </by-check-type>
</accuracy-summary>
```

#### `<verification-results>`

```xml
<verification-results>
  <item id="{extraction-item-id}" extraction-type="{type}" source-file="{path}" verdict="{verdict}">
    <checks>
      <check type="identifier-exists" result="pass|fail|skip" detail="{text}"/>
      <check type="line-reference" result="pass|fail|skip" detail="{text}"/>
      <!-- applicable checks -->
    </checks>
    <correction-hint type="{correction-type}" action="{suggested-action}"/>
  </item>
  <!-- per verified item -->
</verification-results>
```

#### `<recommendations>`

```xml
<recommendations>
  <recommendation severity="critical|high|medium|low" category="{text}">
    {recommendation text}
  </recommendation>
</recommendations>
```

### Verdict Values (FR-022)

| Value | Meaning |
|-------|---------|
| `confirmed` | All applicable checks passed; item verified in source |
| `plausible` | Partial match (e.g., substring only); not conclusively confirmed |
| `incorrect` | Found in source but with wrong value or context |
| `fabricated` | No evidence of item in source codebase |
| `skipped` | Check not applicable or could not be performed |

### Check Types (FR-023)

| Value | Description |
|-------|-------------|
| `identifier-exists` | Word-boundary search for identifier in source code |
| `term-exists` | Search for term in comments, strings, documentation |
| `line-reference` | Verify file exists and has content at stated line |
| `content-match` | Compare extracted code snippet against actual source |
| `expansion-match` | Verify acronym expansion matches source context |
| `count-match` | Recount elements and compare to stated count |
| `relationship-match` | Verify stated relationship (calls, inherits, etc.) exists |

## Consistency Audit Report

Root element: `<consistency-audit-report>`

### Root Attributes

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `project-id` | string | Yes | Reference to analyzed project |
| `version` | string | Yes | Schema version (1.0.0) |
| `generated` | dateTime | Yes | Audit execution timestamp |
| `total-checks` | integer | Yes | Total consistency checks performed |
| `passed-checks` | integer | Yes | Checks that passed |
| `failed-checks` | integer | Yes | Checks that failed |
| `consistency-score` | decimal | Yes | (passed / total) * 100 |

### Child Elements

#### `<arithmetic-checks>`

```xml
<arithmetic-checks total="{N}" passed="{N}" failed="{N}">
  <check file="{path}" element="{xpath}" stated="{N}" actual="{N}" result="pass|fail">
    <detail>{description of mismatch}</detail>
  </check>
</arithmetic-checks>
```

#### `<cross-reference-checks>`

```xml
<cross-reference-checks total="{N}" passed="{N}" failed="{N}">
  <check source-file="{path}" source-element="{id}" target="{ref}" target-type="file|id" result="pass|fail">
    <detail>{description}</detail>
  </check>
</cross-reference-checks>
```

#### `<duplicate-id-checks>`

```xml
<duplicate-id-checks total-ids-scanned="{N}" duplicates-found="{N}">
  <duplicate id="{id}" severity="critical|info">
    <occurrence file="{path}" element="{xpath}"/>
    <occurrence file="{path}" element="{xpath}"/>
  </duplicate>
</duplicate-id-checks>
```

#### `<freshness-checks>`

```xml
<freshness-checks total="{N}" passed="{N}" failed="{N}" skipped="{N}">
  <check generated-file="{path}" extraction-file="{path}"
         generated-timestamp="{dateTime}" extraction-timestamp="{dateTime}"
         result="pass|fail|skipped">
    <discrepancy metric="{name}" generated-value="{value}" extraction-value="{value}"/>
  </check>
</freshness-checks>
```

#### `<cross-document-checks>`

```xml
<cross-document-checks total="{N}" discrepancies="{N}">
  <discrepancy-cluster metric="{name}" occurrences="{N}">
    <occurrence file="{path}" location="{section/line}" value="{value}"/>
    <occurrence file="{path}" location="{section/line}" value="{value}"/>
    <recommendation>{resolution guidance}</recommendation>
  </discrepancy-cluster>
</cross-document-checks>
```

## Full Audit Report

Root element: `<full-audit-report>`

### Root Attributes

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `project-id` | string | Yes | Reference to analyzed project |
| `version` | string | Yes | Schema version (1.0.0) |
| `generated` | dateTime | Yes | Audit execution timestamp |
| `composite-score` | decimal | Yes | Weighted composite (coverage*0.25 + consistency*0.35 + accuracy*0.40) |
| `quality-rating` | enum | Yes | Excellent, Good, Acceptable, Poor, Critical |

### Child Elements

```xml
<full-audit-report project-id="{name}" version="1.0.0" generated="{timestamp}"
                   composite-score="{decimal}" quality-rating="{rating}">
  <dimension-scores>
    <dimension name="coverage" score="{decimal}" weight="0.25"
               weighted-contribution="{decimal}" report="audit-report.xml"/>
    <dimension name="consistency" score="{decimal}" weight="0.35"
               weighted-contribution="{decimal}" report="consistency-audit-report.xml"/>
    <dimension name="accuracy" score="{decimal}" weight="0.40"
               weighted-contribution="{decimal}" report="accuracy-audit-report.xml"/>
  </dimension-scores>
  <quality-assessment>
    <rating>{Excellent|Good|Acceptable|Poor|Critical}</rating>
    <action-recommendation>{recommended action based on rating}</action-recommendation>
    <dimension-highlights>
      <highlight dimension="{name}" finding="{summary of key finding}"/>
    </dimension-highlights>
  </quality-assessment>
  <correction-summary>
    <total-corrections>{N}</total-corrections>
    <by-source>
      <source audit-type="coverage" count="{N}"/>
      <source audit-type="consistency" count="{N}"/>
      <source audit-type="accuracy" count="{N}"/>
    </by-source>
    <merged-plan-path>{path to merged correction-plan.xml}</merged-plan-path>
  </correction-summary>
</full-audit-report>
```

### Quality Rating Thresholds (FR-017)

| Rating | Score Range | Action Recommendation |
|--------|------------|----------------------|
| Excellent | >= 98% | Ready for downstream consumption |
| Good | 95 - 97.9% | Minor corrections recommended before use |
| Acceptable | 90 - 94.9% | Review corrections; address critical items before use |
| Poor | 80 - 89.9% | Significant corrections required; re-extract affected areas |
| Critical | < 80% | Major quality issues; consider full re-extraction |

## Extended Correction Plan Schema

### New CorrectionType Values (FR-018)

| Value | Source Audit | Description |
|-------|-------------|-------------|
| `fabricated` | accuracy | Extraction item has no evidence in source codebase |
| `inaccurate` | accuracy | Extraction item exists but with incorrect value |
| `inconsistent` | consistency | Stated value disagrees with actual count or cross-reference |
| `broken-ref` | consistency | Cross-reference target does not exist |
| `arithmetic` | consistency | Metadata count disagrees with actual element count |
| `duplicate-id` | consistency | Same ID appears in multiple locations |

### New CategoryType Values (FR-018)

| Value | Description | Priority Order |
|-------|-------------|---------------|
| `cross-document` | Discrepancy across generated documents | Between extraction and generation |
| `metadata` | Metadata attribute errors in extraction XML | Between extraction and cross-document |

### Updated Priority Order

1. `analysis` (highest)
2. `extraction`
3. `metadata`
4. `cross-document`
5. `generation` (lowest)

### New Attributes on `<correction>` Element (FR-019)

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `source-audit-type` | enum | Yes (new audits) | `coverage`, `accuracy`, or `consistency` |
| `severity` | enum | Yes (new audits) | `critical`, `high`, `medium`, `low` |

### New Child Element: `<evidence>`

```xml
<correction id="COR-015" type="fabricated" category="extraction"
            extraction-type="business-rules" status="pending"
            source-audit-type="accuracy" severity="critical"
            action="delete business-rules.xml IVSA">
  <description>Acronym "IVSA" not found in source codebase. Classified as fabricated.</description>
  <evidence>
    <search-pattern>\bIVSA\b</search-pattern>
    <files-searched>{N}</files-searched>
    <matches-found>0</matches-found>
  </evidence>
  <affected-files>
    <file>reforge_output/{project}/extractions/business-rules.xml</file>
  </affected-files>
</correction>
```

## Dependency Graph

```
                    ┌─────────────────────┐
                    │  audit.md (command)  │
                    │   routing section    │
                    └──────────┬──────────┘
               ┌───────────────┼───────────────┐
               ▼               ▼               ▼
      ┌────────────┐  ┌────────────────┐  ┌────────────┐
      │  Accuracy   │  │  Consistency   │  │   Full     │
      │  Workflow   │  │  Workflow      │  │  Workflow   │
      └──────┬─────┘  └──────┬─────────┘  └──────┬─────┘
             ▼               ▼                    ▼
      ┌────────────┐  ┌────────────────┐  ┌────────────┐
      │ accuracy-  │  │ consistency-   │  │ full-audit │
      │ audit-     │  │ audit-         │  │ -report.xml│
      │ report.xml │  │ report.xml     │  └──────┬─────┘
      └──────┬─────┘  └──────┬─────────┘         │
             ▼               ▼                    ▼
      ┌────────────┐  ┌────────────────┐  ┌────────────┐
      │ accuracy-  │  │ consistency-   │  │ correction-│
      │ correction │  │ correction     │  │ plan.xml   │
      │ -plan.xml  │  │ -plan.xml      │  │ (merged)   │
      └────────────┘  └────────────────┘  └────────────┘
```

## File Output Map

All files written to `$PROJECT_OUTPUT_DIR/audit/`:

| Audit Mode | Report File | Correction Plan File |
|------------|-------------|---------------------|
| (no arg) / coverage | `audit-report.xml` | `correction-plan.xml` |
| `accuracy` | `accuracy-audit-report.xml` | `accuracy-correction-plan.xml` |
| `consistency` | `consistency-audit-report.xml` | `consistency-correction-plan.xml` |
| `full` | All 3 above + `full-audit-report.xml` | `correction-plan.xml` (merged from all 3) |
