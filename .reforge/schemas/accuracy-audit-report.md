# Accuracy Audit Report Schema

> Defines the structure for the accuracy audit report (`accuracy-audit-report.xml`)

## Overview

The accuracy audit report schema captures the results of `/reforge.audit accuracy`. It records item-level verification results against the source codebase, accuracy scores by category and check type, and statistical sampling metadata when applicable.

## Root Element

```xml
<accuracy-audit-report project-id="my-app" version="1.0.0"
                       generated="2024-01-15T14:00:00Z"
                       methodology="sampling"
                       sample-rate="0.20"
                       total-items="4636" verified-items="928"
                       accuracy-score="97.6">
  <sampling-metadata>...</sampling-metadata>
  <accuracy-summary>...</accuracy-summary>
  <verification-results>...</verification-results>
  <recommendations>...</recommendations>
</accuracy-audit-report>
```

### Attributes

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

## Elements

### `<sampling-metadata>`

Conditional: present only when `methodology="sampling"`. Records the sampling parameters and per-stratum statistics.

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

#### `<sampling-metadata>` Child Elements

| Element | Type | Required | Description |
|---------|------|----------|-------------|
| `<sample-rate>` | decimal | Yes | Rate used for sampling (e.g., 0.20) |
| `<total-population>` | integer | Yes | Total items in the corpus |
| `<sample-size>` | integer | Yes | Items actually sampled |
| `<confidence-level>` | integer | Yes | Confidence level percentage (95) |
| `<confidence-interval>` | element | Yes | Lower and upper bounds of the interval |
| `<margin-of-error>` | decimal | Yes | Margin of error as percentage points |
| `<strata>` | element | Yes | Container for per-stratum breakdown |

#### `<stratum>` Attributes

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `category` | string | Yes | Extraction category (e.g., business-rules, database) |
| `population` | integer | Yes | Total items in this stratum |
| `sampled` | integer | Yes | Items sampled from this stratum |
| `accuracy` | decimal | Yes | Accuracy score for this stratum |

### `<accuracy-summary>`

Aggregated accuracy statistics by overall, category, and check type.

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

#### `<overall>` Attributes

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `accuracy` | decimal | Yes | Overall accuracy percentage |
| `confirmed` | integer | Yes | Items classified as confirmed |
| `plausible` | integer | Yes | Items classified as plausible |
| `incorrect` | integer | Yes | Items classified as incorrect |
| `fabricated` | integer | Yes | Items classified as fabricated |
| `skipped` | integer | Yes | Items classified as skipped |

#### `<category>` Attributes

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | string | Yes | Extraction category name |
| `accuracy` | decimal | Yes | Accuracy score for this category |
| `verified` | integer | Yes | Total items verified in this category |
| `confirmed` | integer | Yes | Items confirmed in this category |
| `fabricated` | integer | Yes | Items fabricated in this category |

#### `<check-type>` Attributes

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | string | Yes | Check type name (see Check Types below) |
| `total` | integer | Yes | Total checks of this type performed |
| `passed` | integer | Yes | Checks that passed |
| `failed` | integer | Yes | Checks that failed |

### `<verification-results>`

Individual item-level verification results.

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

#### `<item>` Attributes

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string | Yes | Extraction item ID (e.g., BR-001, ACR-015) |
| `extraction-type` | string | Yes | Category of extraction (business-rules, database, etc.) |
| `source-file` | string | No | Primary source file path for this item |
| `verdict` | VerdictType | Yes | Final verdict for this item |

#### `<check>` Attributes

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `type` | CheckType | Yes | Check type performed |
| `result` | enum | Yes | `pass`, `fail`, or `skip` |
| `detail` | string | No | Human-readable detail about the check result |

#### `<correction-hint>` Attributes

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `type` | CorrectionType | Yes | Suggested correction type (fabricated, inaccurate, etc.) |
| `action` | string | Yes | Suggested corrective action |

### `<recommendations>`

Actionable recommendations based on audit findings.

```xml
<recommendations>
  <recommendation severity="critical|high|medium|low" category="{text}">
    {recommendation text}
  </recommendation>
</recommendations>
```

#### `<recommendation>` Attributes

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `severity` | enum | Yes | `critical`, `high`, `medium`, or `low` |
| `category` | string | Yes | Category of the recommendation |

---

## Verdict Values (FR-022)

| Value | Meaning |
|-------|---------|
| `confirmed` | All applicable checks passed; item verified in source |
| `plausible` | Partial match (e.g., substring only); not conclusively confirmed |
| `incorrect` | Found in source but with wrong value or context |
| `fabricated` | No evidence of item in source codebase |
| `skipped` | Check not applicable or could not be performed |

## Check Types (FR-023)

| Value | Description |
|-------|-------------|
| `identifier-exists` | Word-boundary search for identifier in source code |
| `term-exists` | Search for term in comments, strings, documentation |
| `line-reference` | Verify file exists and has content at stated line |
| `content-match` | Compare extracted code snippet against actual source |
| `expansion-match` | Verify acronym expansion matches source context |
| `count-match` | Recount elements and compare to stated count |
| `relationship-match` | Verify stated relationship (calls, inherits, etc.) exists |

---

## Storage Location

Output path: `reforge_output/<project-name>/audit/accuracy-audit-report.xml`

---

## Examples

### Accuracy Audit with Sampling

```xml
<accuracy-audit-report project-id="TCOS-RUMO" version="1.0.0"
                       generated="2024-01-15T14:00:00Z"
                       methodology="sampling"
                       sample-rate="0.20"
                       total-items="4636" verified-items="928"
                       accuracy-score="97.6">
  <sampling-metadata>
    <sample-rate>0.20</sample-rate>
    <total-population>4636</total-population>
    <sample-size>928</sample-size>
    <confidence-level>95</confidence-level>
    <confidence-interval lower="96.4" upper="98.8"/>
    <margin-of-error>1.2</margin-of-error>
    <strata>
      <stratum category="business-rules" population="981" sampled="197" accuracy="98.0"/>
      <stratum category="database" population="1200" sampled="240" accuracy="99.2"/>
      <stratum category="ui-flows" population="855" sampled="171" accuracy="95.3"/>
      <stratum category="workflows" population="1600" sampled="320" accuracy="97.8"/>
    </strata>
  </sampling-metadata>
  <accuracy-summary>
    <overall accuracy="97.6" confirmed="906" plausible="5" incorrect="3" fabricated="12" skipped="2"/>
    <by-category>
      <category name="business-rules" accuracy="98.0" verified="197" confirmed="193" fabricated="3"/>
      <category name="database" accuracy="99.2" verified="240" confirmed="238" fabricated="0"/>
      <category name="ui-flows" accuracy="95.3" verified="171" confirmed="163" fabricated="5"/>
      <category name="workflows" accuracy="97.8" verified="320" confirmed="312" fabricated="4"/>
    </by-category>
    <by-check-type>
      <check-type name="identifier-exists" total="928" passed="910" failed="18"/>
      <check-type name="term-exists" total="200" passed="195" failed="5"/>
      <check-type name="line-reference" total="350" passed="345" failed="5"/>
      <check-type name="content-match" total="150" passed="148" failed="2"/>
      <check-type name="expansion-match" total="120" passed="115" failed="5"/>
      <check-type name="count-match" total="80" passed="78" failed="2"/>
      <check-type name="relationship-match" total="60" passed="58" failed="2"/>
    </by-check-type>
  </accuracy-summary>
  <verification-results>
    <item id="ACR-015" extraction-type="business-rules" source-file="extractions/business-rules.xml" verdict="fabricated">
      <checks>
        <check type="identifier-exists" result="fail" detail="No word-boundary match for 'IVSA' in source codebase (0 matches across 864 files)"/>
        <check type="expansion-match" result="fail" detail="Expansion 'Inactive Vehicle Self-Assessment' not found near any occurrence"/>
      </checks>
      <correction-hint type="fabricated" action="delete business-rules.xml IVSA"/>
    </item>
    <item id="BR-042" extraction-type="business-rules" source-file="src/Locomotive.vb" verdict="confirmed">
      <checks>
        <check type="identifier-exists" result="pass" detail="Found 3 word-boundary matches in source"/>
        <check type="line-reference" result="pass" detail="File exists with content at stated line 166"/>
      </checks>
    </item>
  </verification-results>
  <recommendations>
    <recommendation severity="critical" category="fabricated-content">
      12 items classified as fabricated. Run /reforge.fix to delete fabricated items from extraction XML.
    </recommendation>
    <recommendation severity="medium" category="low-accuracy-stratum">
      Stratum 'ui-flows' has accuracy 95.3% (below 98% threshold). Consider full verification with --full-verify.
    </recommendation>
  </recommendations>
</accuracy-audit-report>
```

### Full Verification (Census)

```xml
<accuracy-audit-report project-id="small-app" version="1.0.0"
                       generated="2024-01-15T14:00:00Z"
                       methodology="census"
                       total-items="120" verified-items="120"
                       accuracy-score="100.0">
  <accuracy-summary>
    <overall accuracy="100.0" confirmed="118" plausible="2" incorrect="0" fabricated="0" skipped="0"/>
    <by-category>
      <category name="business-rules" accuracy="100.0" verified="60" confirmed="59" fabricated="0"/>
      <category name="database" accuracy="100.0" verified="60" confirmed="59" fabricated="0"/>
    </by-category>
    <by-check-type>
      <check-type name="identifier-exists" total="120" passed="120" failed="0"/>
    </by-check-type>
  </accuracy-summary>
  <verification-results>
    <!-- all 120 items listed -->
  </verification-results>
  <recommendations/>
</accuracy-audit-report>
```
