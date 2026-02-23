# Consistency Audit Report Schema

> Defines the structure for the consistency audit report (`consistency-audit-report.xml`)

## Overview

The consistency audit report schema captures the results of `/reforge.audit consistency`. It records arithmetic checks, cross-reference validation, duplicate ID detection, freshness checks, and cross-document discrepancy detection within the extraction corpus and generated output.

## Root Element

```xml
<consistency-audit-report project-id="my-app" version="1.0.0"
                          generated="2024-01-15T14:00:00Z"
                          total-checks="85" passed-checks="80"
                          failed-checks="5"
                          consistency-score="94.1">
  <arithmetic-checks>...</arithmetic-checks>
  <cross-reference-checks>...</cross-reference-checks>
  <duplicate-id-checks>...</duplicate-id-checks>
  <freshness-checks>...</freshness-checks>
  <cross-document-checks>...</cross-document-checks>
</consistency-audit-report>
```

### Attributes

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `project-id` | string | Yes | Reference to analyzed project |
| `version` | string | Yes | Schema version (1.0.0) |
| `generated` | dateTime | Yes | Audit execution timestamp |
| `total-checks` | integer | Yes | Total consistency checks performed |
| `passed-checks` | integer | Yes | Checks that passed |
| `failed-checks` | integer | Yes | Checks that failed |
| `consistency-score` | decimal | Yes | (passed-checks / total-checks) * 100 |

## Elements

### `<arithmetic-checks>`

Compares stated metadata counts against actual element counts per extraction file. Zero tolerance for mismatches.

```xml
<arithmetic-checks total="{N}" passed="{N}" failed="{N}">
  <check file="{path}" element="{xpath}" stated="{N}" actual="{N}" result="pass|fail">
    <detail>{description of mismatch}</detail>
  </check>
</arithmetic-checks>
```

#### `<arithmetic-checks>` Attributes

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `total` | integer | Yes | Total arithmetic checks performed |
| `passed` | integer | Yes | Checks where stated count matches actual |
| `failed` | integer | Yes | Checks where stated count differs from actual |

#### `<check>` Attributes (arithmetic)

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `file` | string | Yes | Path to the extraction file checked |
| `element` | string | Yes | XPath or element description of the count attribute |
| `stated` | integer | Yes | Value stated in the metadata |
| `actual` | integer | Yes | Actual count of child elements |
| `result` | enum | Yes | `pass` or `fail` |

### `<cross-reference-checks>`

Validates that all cross-references (file references, ID references) resolve to existing targets.

```xml
<cross-reference-checks total="{N}" passed="{N}" failed="{N}">
  <check source-file="{path}" source-element="{id}" target="{ref}" target-type="file|id" result="pass|fail">
    <detail>{description}</detail>
  </check>
</cross-reference-checks>
```

#### `<cross-reference-checks>` Attributes

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `total` | integer | Yes | Total cross-reference checks performed |
| `passed` | integer | Yes | References that resolve correctly |
| `failed` | integer | Yes | References that do not resolve |

#### `<check>` Attributes (cross-reference)

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `source-file` | string | Yes | File containing the reference |
| `source-element` | string | Yes | Element ID or description containing the reference |
| `target` | string | Yes | The reference target (file path or ID) |
| `target-type` | enum | Yes | `file` (file path reference) or `id` (element ID reference) |
| `result` | enum | Yes | `pass` or `fail` |

### `<duplicate-id-checks>`

Detects duplicate element IDs across extraction files.

```xml
<duplicate-id-checks total-ids-scanned="{N}" duplicates-found="{N}">
  <duplicate id="{id}" severity="critical|info">
    <occurrence file="{path}" element="{xpath}"/>
    <occurrence file="{path}" element="{xpath}"/>
  </duplicate>
</duplicate-id-checks>
```

#### `<duplicate-id-checks>` Attributes

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `total-ids-scanned` | integer | Yes | Total unique IDs scanned across all files |
| `duplicates-found` | integer | Yes | Number of duplicate ID groups found |

#### `<duplicate>` Attributes

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string | Yes | The duplicated ID value |
| `severity` | enum | Yes | `critical` (within-file or within-category) or `info` (cross-category) |

#### `<occurrence>` Attributes

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `file` | string | Yes | File path containing this ID occurrence |
| `element` | string | Yes | XPath or element description of the occurrence |

### `<freshness-checks>`

Compares extraction timestamps against generated document timestamps and verifies numeric claims in generated documents match current extraction data.

```xml
<freshness-checks total="{N}" passed="{N}" failed="{N}" skipped="{N}">
  <check generated-file="{path}" extraction-file="{path}"
         generated-timestamp="{dateTime}" extraction-timestamp="{dateTime}"
         result="pass|fail|skipped">
    <discrepancy metric="{name}" generated-value="{value}" extraction-value="{value}"/>
  </check>
</freshness-checks>
```

#### `<freshness-checks>` Attributes

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `total` | integer | Yes | Total freshness checks performed |
| `passed` | integer | Yes | Checks that passed (timestamps current, values match) |
| `failed` | integer | Yes | Checks that found stale or mismatched data |
| `skipped` | integer | Yes | Checks skipped (unparseable documents) |

#### `<check>` Attributes (freshness)

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `generated-file` | string | Yes | Path to the generated document |
| `extraction-file` | string | Yes | Path to the source extraction file |
| `generated-timestamp` | dateTime | No | Timestamp of the generated document |
| `extraction-timestamp` | dateTime | No | Timestamp of the extraction |
| `result` | enum | Yes | `pass`, `fail`, or `skipped` |

#### `<discrepancy>` Attributes

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `metric` | string | Yes | Name of the metric that differs |
| `generated-value` | string | Yes | Value found in the generated document |
| `extraction-value` | string | Yes | Current value from extraction XML |

### `<cross-document-checks>`

Detects discrepancies where the same metric is cited with different values across documents.

```xml
<cross-document-checks total="{N}" discrepancies="{N}">
  <discrepancy-cluster metric="{name}" occurrences="{N}">
    <occurrence file="{path}" location="{section/line}" value="{value}"/>
    <occurrence file="{path}" location="{section/line}" value="{value}"/>
    <recommendation>{resolution guidance}</recommendation>
  </discrepancy-cluster>
</cross-document-checks>
```

#### `<cross-document-checks>` Attributes

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `total` | integer | Yes | Total cross-document metrics checked |
| `discrepancies` | integer | Yes | Number of metrics with conflicting values |

#### `<discrepancy-cluster>` Attributes

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `metric` | string | Yes | Name of the metric with conflicting values |
| `occurrences` | integer | Yes | Number of documents citing this metric |

#### `<occurrence>` Attributes (cross-document)

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `file` | string | Yes | Document file path |
| `location` | string | Yes | Section or line reference within the document |
| `value` | string | Yes | Value cited for this metric |

---

## Storage Location

Output path: `reforge_output/<project-name>/audit/consistency-audit-report.xml`

---

## Examples

### Consistency Audit with Mixed Results

```xml
<consistency-audit-report project-id="TCOS-RUMO" version="1.0.0"
                          generated="2024-01-15T14:00:00Z"
                          total-checks="85" passed-checks="78"
                          failed-checks="7"
                          consistency-score="91.8">
  <arithmetic-checks total="12" passed="9" failed="3">
    <check file="extractions/business-rules.xml" element="metadata/total-count"
           stated="900" actual="981" result="fail">
      <detail>Metadata states 900 business rules but actual element count is 981</detail>
    </check>
    <check file="extractions/database.xml" element="metadata/total-count"
           stated="245" actual="245" result="pass"/>
    <check file="extractions/business-rules.xml" element="confidence-distribution/@sum"
           stated="900" actual="981" result="fail">
      <detail>Confidence distribution sums to 900 but 981 elements exist</detail>
    </check>
  </arithmetic-checks>
  <cross-reference-checks total="45" passed="42" failed="3">
    <check source-file="extractions/business-rules.xml" source-element="BR-120"
           target="business-rules-bulletins.xml" target-type="file" result="fail">
      <detail>Referenced file does not exist. Actual file is bulletin-rules.xml</detail>
    </check>
  </cross-reference-checks>
  <duplicate-id-checks total-ids-scanned="4636" duplicates-found="0"/>
  <freshness-checks total="18" passed="16" failed="1" skipped="1">
    <check generated-file="generated/documentation.md" extraction-file="extractions/business-rules.xml"
           generated-timestamp="2024-01-10T10:00:00Z" extraction-timestamp="2024-01-14T16:00:00Z"
           result="fail">
      <discrepancy metric="business-rule-count" generated-value="785" extraction-value="981"/>
    </check>
    <check generated-file="generated/data-dictionary.html" extraction-file="extractions/database.xml"
           result="skipped">
      <detail>HTML document could not be parsed for numeric claims</detail>
    </check>
  </freshness-checks>
  <cross-document-checks total="10" discrepancies="1">
    <discrepancy-cluster metric="total-files-analyzed" occurrences="3">
      <occurrence file="generated/documentation.md" location="Overview section" value="785"/>
      <occurrence file="generated/user-stories.md" location="Introduction" value="864"/>
      <occurrence file="extractions/business-rules.xml" location="metadata" value="864"/>
      <recommendation>Update documentation.md to use current value of 864 from analysis.xml</recommendation>
    </discrepancy-cluster>
  </cross-document-checks>
</consistency-audit-report>
```
