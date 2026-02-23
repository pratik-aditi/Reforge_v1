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
  <metrics-registry-checks>...</metrics-registry-checks>
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

### `<metrics-registry-checks>`

Compares metric values in generated documents against the authoritative metrics registry.

```xml
<metrics-registry-checks total-claims-scanned="{N}" total-discrepancies="{N}"
                         critical-count="{N}" warning-count="{N}" info-count="{N}"
                         files-scanned="{N}" registry-version="{version}">
  <discrepancy id="DIS-001" severity="critical" metric-id="{metric-id}"
               registry-value="{value}" document-value="{value}"
               file="{path}" line="{N}" context="{text}"
               confidence="high" action="regenerate"
               pattern-id="{pattern}" qualifier="{qualifier}" tolerance-percent="{decimal}"/>
  <scan-summary>
    <file-summary file="{path}" claims-found="{N}" discrepancies="{N}" status="clean|has-issues"/>
    <metric-summary metric-id="{metric-id}" registry-value="{value}"
                    occurrences-found="{N}" consistent-count="{N}" discrepant-count="{N}"
                    status="verified|has-discrepancies|not-found"/>
  </scan-summary>
  <exclusions-applied>
    <exclusion pattern-text="{text}" matches-suppressed="{N}" files-affected="{N}"/>
  </exclusions-applied>
</metrics-registry-checks>
```

#### `<metrics-registry-checks>` Attributes

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `total-claims-scanned` | integer | Yes | Total numeric claims found across all scanned files |
| `total-discrepancies` | integer | Yes | Number of discrepancies detected |
| `critical-count` | integer | Yes | Exact value mismatches |
| `warning-count` | integer | Yes | Out-of-tolerance approximate mismatches |
| `info-count` | integer | Yes | Unregistered metrics |
| `files-scanned` | integer | Yes | Number of files scanned |
| `registry-version` | string | Yes | Version of the metrics registry used for comparison |

#### `<discrepancy>` Attributes (metrics-registry)

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string | Yes | Unique discrepancy ID (DIS-NNN) |
| `severity` | enum | Yes | `critical` \| `warning` \| `info` |
| `metric-id` | string | Yes | Registry metric ID, or `UNREGISTERED` |
| `registry-value` | string | Yes | Canonical value from registry (empty if unregistered) |
| `document-value` | string | Yes | Value extracted from the document |
| `file` | string | Yes | Relative path to the document file |
| `line` | integer | Yes | Line number in the document |
| `context` | string | Yes | Surrounding text snippet |
| `confidence` | enum | Yes | `high` \| `medium` \| `low` |
| `action` | enum | Yes | `regenerate` \| `review` \| `register-or-ignore` \| `investigate` |
| `pattern-id` | string | No | Which scan pattern matched |
| `qualifier` | string | No | Tolerance qualifier if approximate |
| `tolerance-percent` | decimal | No | Tolerance percentage applied |

**Confidence assignment criteria:**

- `high` = scan pattern matched AND metric unit/noun matched
- `medium` = scan pattern matched but unit/noun ambiguous or value requires normalization
- `low` = value-proximity match only with no supporting pattern or noun context

#### `<scan-summary>` Element

Contains per-file and per-metric summary rollups.

```xml
<scan-summary>
  <file-summary file="{path}" claims-found="{N}" discrepancies="{N}" status="clean|has-issues"/>
  <metric-summary metric-id="{metric-id}" registry-value="{value}"
                  occurrences-found="{N}" consistent-count="{N}" discrepant-count="{N}"
                  status="verified|has-discrepancies|not-found"/>
</scan-summary>
```

##### `<file-summary>` Attributes

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `file` | string | Yes | Relative path to the scanned file |
| `claims-found` | integer | Yes | Number of numeric claims found in the file |
| `discrepancies` | integer | Yes | Number of discrepancies in the file |
| `status` | enum | Yes | `clean` (no discrepancies) or `has-issues` |

##### `<metric-summary>` Attributes

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `metric-id` | string | Yes | Registry metric ID |
| `registry-value` | string | Yes | Canonical value from registry |
| `occurrences-found` | integer | Yes | Total occurrences of this metric found across files |
| `consistent-count` | integer | Yes | Occurrences matching the registry value |
| `discrepant-count` | integer | Yes | Occurrences not matching the registry value |
| `status` | enum | Yes | `verified` (all match) \| `has-discrepancies` \| `not-found` (no occurrences) |

#### `<exclusions-applied>` Element

Records patterns that were excluded from discrepancy reporting.

```xml
<exclusions-applied>
  <exclusion pattern-text="{text}" matches-suppressed="{N}" files-affected="{N}"/>
</exclusions-applied>
```

##### `<exclusion>` Attributes

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `pattern-text` | string | Yes | The exclusion pattern text |
| `matches-suppressed` | integer | Yes | Number of potential matches suppressed by this exclusion |
| `files-affected` | integer | Yes | Number of files where this exclusion applied |

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
  <metrics-registry-checks total-claims-scanned="142" total-discrepancies="3"
                           critical-count="1" warning-count="1" info-count="1"
                           files-scanned="6" registry-version="1.0.0">
    <discrepancy id="DIS-001" severity="critical" metric-id="MET-BR-TOTAL"
                 registry-value="981" document-value="785"
                 file="generated/documentation.md" line="12"
                 context="The system contains 785 business rules governing..."
                 confidence="high" action="regenerate"
                 pattern-id="PAT-COUNT-NOUN"/>
    <discrepancy id="DIS-002" severity="warning" metric-id="MET-DB-TABLE-COUNT"
                 registry-value="245" document-value="240"
                 file="generated/data-dictionary.md" line="38"
                 context="Approximately 240 database tables were identified..."
                 confidence="medium" action="review"
                 pattern-id="PAT-APPROX-COUNT" qualifier="approximately"
                 tolerance-percent="5.0"/>
    <discrepancy id="DIS-003" severity="info" metric-id="UNREGISTERED"
                 registry-value="" document-value="47"
                 file="generated/user-stories.md" line="94"
                 context="There are 47 integration points between subsystems..."
                 confidence="low" action="register-or-ignore"/>
    <scan-summary>
      <file-summary file="generated/documentation.md" claims-found="34" discrepancies="1" status="has-issues"/>
      <file-summary file="generated/data-dictionary.md" claims-found="52" discrepancies="1" status="has-issues"/>
      <file-summary file="generated/user-stories.md" claims-found="28" discrepancies="1" status="has-issues"/>
      <file-summary file="generated/api-reference.md" claims-found="15" discrepancies="0" status="clean"/>
      <file-summary file="generated/migration-guide.md" claims-found="8" discrepancies="0" status="clean"/>
      <file-summary file="generated/architecture-overview.md" claims-found="5" discrepancies="0" status="clean"/>
      <metric-summary metric-id="MET-BR-TOTAL" registry-value="981"
                      occurrences-found="4" consistent-count="3" discrepant-count="1"
                      status="has-discrepancies"/>
      <metric-summary metric-id="MET-DB-TABLE-COUNT" registry-value="245"
                      occurrences-found="3" consistent-count="2" discrepant-count="1"
                      status="has-discrepancies"/>
      <metric-summary metric-id="MET-WF-COUNT" registry-value="132"
                      occurrences-found="2" consistent-count="2" discrepant-count="0"
                      status="verified"/>
    </scan-summary>
    <exclusions-applied>
      <exclusion pattern-text="page numbers and section references" matches-suppressed="23" files-affected="4"/>
      <exclusion pattern-text="date and timestamp literals" matches-suppressed="18" files-affected="6"/>
    </exclusions-applied>
  </metrics-registry-checks>
</consistency-audit-report>
```
