# Full Audit Report Schema

> Defines the structure for the unified full audit report (`full-audit-report.xml`)

## Overview

The full audit report schema captures the results of `/reforge.audit full`. It aggregates scores from three audit dimensions (coverage, consistency, accuracy) into a composite quality score with a quality rating and action recommendation. Individual dimension reports are referenced by path.

## Root Element

```xml
<full-audit-report project-id="my-app" version="1.0.0"
                   generated="2024-01-15T14:00:00Z"
                   composite-score="96.2"
                   quality-rating="Good">
  <dimension-scores>...</dimension-scores>
  <quality-assessment>...</quality-assessment>
  <correction-summary>...</correction-summary>
</full-audit-report>
```

### Attributes

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `project-id` | string | Yes | Reference to analyzed project |
| `version` | string | Yes | Schema version (1.0.0) |
| `generated` | dateTime | Yes | Audit execution timestamp |
| `composite-score` | decimal | Yes | Weighted composite: coverage*0.25 + consistency*0.35 + accuracy*0.40 |
| `quality-rating` | enum | Yes | Excellent, Good, Acceptable, Poor, or Critical |

## Elements

### `<dimension-scores>`

Individual scores from each audit dimension with their weights and contributions.

```xml
<dimension-scores>
  <dimension name="coverage" score="{decimal}" weight="0.25"
             weighted-contribution="{decimal}" report="audit-report.xml"/>
  <dimension name="consistency" score="{decimal}" weight="0.35"
             weighted-contribution="{decimal}" report="consistency-audit-report.xml"/>
  <dimension name="accuracy" score="{decimal}" weight="0.40"
             weighted-contribution="{decimal}" report="accuracy-audit-report.xml"/>
</dimension-scores>
```

#### `<dimension>` Attributes

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | string | Yes | Dimension name: `coverage`, `consistency`, or `accuracy` |
| `score` | decimal | Yes | Score from the individual audit (0-100) |
| `weight` | decimal | Yes | Weight applied to this dimension |
| `weighted-contribution` | decimal | Yes | score * weight |
| `report` | string | Yes | Filename of the individual audit report |

### `<quality-assessment>`

Mapping of composite score to quality rating with action recommendation and highlights.

```xml
<quality-assessment>
  <rating>{Excellent|Good|Acceptable|Poor|Critical}</rating>
  <action-recommendation>{recommended action based on rating}</action-recommendation>
  <dimension-highlights>
    <highlight dimension="{name}" finding="{summary of key finding}"/>
  </dimension-highlights>
</quality-assessment>
```

#### `<highlight>` Attributes

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `dimension` | string | Yes | Dimension name this highlight is from |
| `finding` | string | Yes | Summary of the key finding |

### `<correction-summary>`

Summary of corrections from all audit types.

```xml
<correction-summary>
  <total-corrections>{N}</total-corrections>
  <by-source>
    <source audit-type="coverage" count="{N}"/>
    <source audit-type="consistency" count="{N}"/>
    <source audit-type="accuracy" count="{N}"/>
  </by-source>
  <merged-plan-path>{path to merged correction-plan.xml}</merged-plan-path>
</correction-summary>
```

#### `<source>` Attributes

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `audit-type` | string | Yes | Source audit: `coverage`, `consistency`, or `accuracy` |
| `count` | integer | Yes | Number of corrections from this audit type |

---

## Quality Rating Thresholds (FR-017)

| Rating | Score Range | Action Recommendation |
|--------|------------|----------------------|
| Excellent | >= 98% | Ready for downstream consumption |
| Good | 95 - 97.9% | Minor corrections recommended before use |
| Acceptable | 90 - 94.9% | Review corrections; address critical items before use |
| Poor | 80 - 89.9% | Significant corrections required; re-extract affected areas |
| Critical | < 80% | Major quality issues; consider full re-extraction |

---

## Storage Location

Output path: `reforge_output/<project-name>/audit/full-audit-report.xml`

---

## Examples

### Full Audit — Good Quality

```xml
<full-audit-report project-id="TCOS-RUMO" version="1.0.0"
                   generated="2024-01-15T14:00:00Z"
                   composite-score="96.2"
                   quality-rating="Good">
  <dimension-scores>
    <dimension name="coverage" score="97.0" weight="0.25"
               weighted-contribution="24.25" report="audit-report.xml"/>
    <dimension name="consistency" score="94.7" weight="0.35"
               weighted-contribution="33.15" report="consistency-audit-report.xml"/>
    <dimension name="accuracy" score="97.6" weight="0.40"
               weighted-contribution="39.04" report="accuracy-audit-report.xml"/>
  </dimension-scores>
  <quality-assessment>
    <rating>Good</rating>
    <action-recommendation>Minor corrections recommended before use</action-recommendation>
    <dimension-highlights>
      <highlight dimension="coverage" finding="97% file coverage; 15 utility files uncovered"/>
      <highlight dimension="consistency" finding="3 arithmetic mismatches in business-rules metadata"/>
      <highlight dimension="accuracy" finding="12 fabricated acronyms detected in glossary"/>
    </dimension-highlights>
  </quality-assessment>
  <correction-summary>
    <total-corrections>30</total-corrections>
    <by-source>
      <source audit-type="coverage" count="15"/>
      <source audit-type="consistency" count="3"/>
      <source audit-type="accuracy" count="12"/>
    </by-source>
    <merged-plan-path>reforge_output/TCOS-RUMO/audit/correction-plan.xml</merged-plan-path>
  </correction-summary>
</full-audit-report>
```
