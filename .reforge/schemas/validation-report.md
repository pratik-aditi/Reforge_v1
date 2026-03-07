# Validation Report Schema

> Defines the structure for unified validation results (`validation-report.xml`)

## Overview

The validation report schema captures results from `/reforge.validate` — XSD conformance checks, ID uniqueness verification, cross-reference integrity, and confidence sum validation. It uses the [Common Extraction Schema](./common-schema.md) for shared structural elements.

## Common Elements

This schema extends the [Common Extraction Schema](./common-schema.md), which defines shared structural elements used across all extraction types:

- **Root attributes**: `project-id`, `version`, `schema-version`, `generated`, `xmlns`
- **Metadata container**: `<metadata>` with `<total-count>`, `<confidence-distribution>`, `<extraction-timestamp>`
- **Source references**: Canonical `<source>` format with `file`, `line-start`, `line-end` attributes
- **Confidence vocabulary**: `high`, `medium`, `low` enumeration
- **ID patterns**: `VAL-{CATEGORY}-{SEQUENCE}` (validation findings)

See `common-schema.md` for complete definitions. Elements defined there MUST NOT be redefined in this schema.

## Root Element

```xml
<validation-report xmlns="http://reforge.dev/schema/extraction"
        project-id="my-app" version="1.0.0"
        schema-version="1.0.0"
        generated="2024-01-15T10:30:00Z">
  <metadata>...</metadata>
  <xsd-validation>...</xsd-validation>
  <id-uniqueness>...</id-uniqueness>
  <cross-references>...</cross-references>
  <confidence-checks>...</confidence-checks>
  <summary>...</summary>
</validation-report>
```

### Attributes

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `xmlns` | URI | Yes | Must be `http://reforge.dev/schema/extraction` |
| `project-id` | string | Yes | Reference to analysis project |
| `version` | string | Yes | Extraction version (semver) |
| `schema-version` | string | Yes | Common schema version (initial: `1.0.0`) |
| `generated` | dateTime | Yes | Validation timestamp (ISO-8601) |

> Root attributes and `<metadata>` are defined by the [Common Extraction Schema](./common-schema.md). The `<metadata>` element is required as the first child of the root element. The metadata `<total-count>` equals the total number of validation findings across all check categories.

## Elements

### `<xsd-validation>`

Container for per-file XSD conformance results.

```xml
<xsd-validation count="4" passed="3" failed="1">
  <file-result>...</file-result>
</xsd-validation>
```

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `count` | integer | Yes | Number of files validated |
| `passed` | integer | Yes | Number of files passing XSD validation |
| `failed` | integer | Yes | Number of files failing XSD validation |

### `<file-result>`

Individual file XSD validation result.

```xml
<file-result file="extractions/business-rules.xml" schema="xsd/business-rules.xsd" status="pass"/>
```

```xml
<file-result file="extractions/issues.xml" schema="xsd/issues.xsd" status="fail">
  <error id="VAL-XSD-001" line="45" confidence="high">
    <message>Element 'severity' has invalid value 'critical'. Expected: high, medium, low.</message>
  </error>
</file-result>
```

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `file` | string | Yes | Relative path to validated file |
| `schema` | string | Yes | Relative path to XSD used |
| `status` | string | Yes | `pass` or `fail` |

### `<error>` (xsd-validation)

Individual XSD validation error within a file result.

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string | Yes | Unique finding identifier (`VAL-XSD-{SEQUENCE}`) |
| `line` | integer | No | Line number of the error in the validated file |
| `confidence` | ConfidenceType | Yes | Confidence in the finding |

### `<message>`

Human-readable description of the validation error.

### `<id-uniqueness>`

Container for duplicate ID check results.

```xml
<id-uniqueness count="3" passed="2" failed="1">
  <scope-result>...</scope-result>
</id-uniqueness>
```

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `count` | integer | Yes | Number of scopes checked |
| `passed` | integer | Yes | Number of scopes with all unique IDs |
| `failed` | integer | Yes | Number of scopes with duplicate IDs |

### `<scope-result>`

ID uniqueness check for a single extraction file scope.

```xml
<scope-result file="extractions/business-rules.xml" status="pass" id-count="156"/>
```

```xml
<scope-result file="extractions/workflows.xml" status="fail" id-count="23">
  <duplicate id="VAL-DUP-001" value="WF-AUTH-002" occurrences="2" confidence="high"/>
</scope-result>
```

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `file` | string | Yes | Relative path to checked file |
| `status` | string | Yes | `pass` or `fail` |
| `id-count` | integer | Yes | Total number of IDs checked in this scope |

### `<duplicate>`

Individual duplicate ID finding.

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string | Yes | Unique finding identifier (`VAL-DUP-{SEQUENCE}`) |
| `value` | string | Yes | The duplicated ID value |
| `occurrences` | integer | Yes | Number of times the ID appears |
| `confidence` | ConfidenceType | Yes | Confidence in the finding |

### `<cross-references>`

Container for broken cross-reference check results.

```xml
<cross-references count="45" passed="43" failed="2">
  <ref-result>...</ref-result>
</cross-references>
```

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `count` | integer | Yes | Total cross-references checked |
| `passed` | integer | Yes | Number of valid cross-references |
| `failed` | integer | Yes | Number of broken cross-references |

### `<ref-result>`

Individual cross-reference check result.

```xml
<ref-result id="VAL-REF-001" source-file="extractions/workflows.xml"
            source-id="WF-AUTH-002" target-file="extractions/business-rules.xml"
            target-id="BR-VAL-099" status="broken" confidence="high">
  <message>Referenced ID BR-VAL-099 not found in business-rules.xml</message>
</ref-result>
```

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string | Yes | Unique finding identifier (`VAL-REF-{SEQUENCE}`) |
| `source-file` | string | Yes | File containing the reference |
| `source-id` | string | Yes | ID of the item making the reference |
| `target-file` | string | Yes | File expected to contain the target |
| `target-id` | string | Yes | The referenced ID that was checked |
| `status` | string | Yes | `valid` or `broken` |
| `confidence` | ConfidenceType | Yes | Confidence in the finding |

### `<confidence-checks>`

Container for confidence sum validation results.

```xml
<confidence-checks count="4" passed="3" failed="1">
  <sum-result>...</sum-result>
</confidence-checks>
```

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `count` | integer | Yes | Number of files checked |
| `passed` | integer | Yes | Number of files with valid confidence sums |
| `failed` | integer | Yes | Number of files with invalid confidence sums |

### `<sum-result>`

Individual confidence sum validation for an extraction file.

```xml
<sum-result id="VAL-SUM-001" file="extractions/business-rules.xml" status="pass"
            total-count="156" high="100" medium="50" low="6" sum="156" confidence="high"/>
```

```xml
<sum-result id="VAL-SUM-002" file="extractions/database.xml" status="fail"
            total-count="89" high="50" medium="30" low="5" sum="85" confidence="high">
  <message>Confidence sum (85) does not equal total-count (89). Difference: 4.</message>
</sum-result>
```

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string | Yes | Unique finding identifier (`VAL-SUM-{SEQUENCE}`) |
| `file` | string | Yes | Relative path to checked file |
| `status` | string | Yes | `pass` or `fail` |
| `total-count` | integer | Yes | Stated total count from metadata |
| `high` | integer | Yes | High confidence count from metadata |
| `medium` | integer | Yes | Medium confidence count from metadata |
| `low` | integer | Yes | Low confidence count from metadata |
| `sum` | integer | Yes | Computed sum of high + medium + low |
| `confidence` | ConfidenceType | Yes | Confidence in the finding |

### `<summary>`

Aggregate validation summary.

```xml
<summary status="fail" total-checks="56" passed="52" failed="4">
  <by-category>
    <category name="xsd-validation" checks="4" passed="3" failed="1"/>
    <category name="id-uniqueness" checks="3" passed="2" failed="1"/>
    <category name="cross-references" checks="45" passed="43" failed="2"/>
    <category name="confidence-checks" checks="4" passed="4" failed="0"/>
  </by-category>
</summary>
```

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `status` | string | Yes | `pass` (all checks pass) or `fail` (any check fails) |
| `total-checks` | integer | Yes | Total number of individual checks performed |
| `passed` | integer | Yes | Total number of checks that passed |
| `failed` | integer | Yes | Total number of checks that failed |

### `<source>`

Source code location where a finding was identified. Uses the canonical format defined in the [Common Extraction Schema](./common-schema.md#source-references). The optional `<snippet>` child element contains the relevant code.

## Example Output

```xml
<?xml version="1.0" encoding="UTF-8"?>
<validation-report xmlns="http://reforge.dev/schema/extraction"
        project-id="ecommerce-legacy" version="1.0.0"
        schema-version="1.0.0"
        generated="2024-01-15T10:30:00Z">

  <metadata>
    <total-count>4</total-count>
    <confidence-distribution>
      <high>4</high>
      <medium>0</medium>
      <low>0</low>
    </confidence-distribution>
    <extraction-timestamp>2024-01-15T10:30:00Z</extraction-timestamp>
  </metadata>

  <xsd-validation count="4" passed="3" failed="1">
    <file-result file="extractions/business-rules.xml" schema="xsd/business-rules.xsd" status="pass"/>
    <file-result file="extractions/database.xml" schema="xsd/database.xsd" status="pass"/>
    <file-result file="extractions/workflows.xml" schema="xsd/workflows.xsd" status="pass"/>
    <file-result file="extractions/issues.xml" schema="xsd/issues.xsd" status="fail">
      <error id="VAL-XSD-001" line="45" confidence="high">
        <message>Element 'severity' has invalid value 'critical'. Expected: high, medium, low.</message>
      </error>
    </file-result>
  </xsd-validation>

  <id-uniqueness count="4" passed="3" failed="1">
    <scope-result file="extractions/business-rules.xml" status="pass" id-count="156"/>
    <scope-result file="extractions/database.xml" status="pass" id-count="89"/>
    <scope-result file="extractions/workflows.xml" status="fail" id-count="23">
      <duplicate id="VAL-DUP-001" value="WF-AUTH-002" occurrences="2" confidence="high"/>
    </scope-result>
    <scope-result file="extractions/issues.xml" status="pass" id-count="13"/>
  </id-uniqueness>

  <cross-references count="45" passed="43" failed="2">
    <ref-result id="VAL-REF-001" source-file="extractions/workflows.xml"
                source-id="WF-AUTH-002" target-file="extractions/business-rules.xml"
                target-id="BR-VAL-099" status="broken" confidence="high">
      <message>Referenced ID BR-VAL-099 not found in business-rules.xml</message>
    </ref-result>
    <ref-result id="VAL-REF-002" source-file="extractions/call-sites.xml"
                source-id="CALL-SVC-015" target-file="extractions/architecture.xml"
                target-id="ARCH-WEB-050" status="broken" confidence="high">
      <message>Referenced ID ARCH-WEB-050 not found in architecture.xml</message>
    </ref-result>
  </cross-references>

  <confidence-checks count="4" passed="3" failed="1">
    <sum-result id="VAL-SUM-001" file="extractions/business-rules.xml" status="pass"
                total-count="156" high="100" medium="50" low="6" sum="156" confidence="high"/>
    <sum-result id="VAL-SUM-002" file="extractions/database.xml" status="fail"
                total-count="89" high="50" medium="30" low="5" sum="85" confidence="high">
      <message>Confidence sum (85) does not equal total-count (89). Difference: 4.</message>
    </sum-result>
    <sum-result id="VAL-SUM-003" file="extractions/workflows.xml" status="pass"
                total-count="23" high="15" medium="6" low="2" sum="23" confidence="high"/>
    <sum-result id="VAL-SUM-004" file="extractions/issues.xml" status="pass"
                total-count="13" high="10" medium="2" low="1" sum="13" confidence="high"/>
  </confidence-checks>

  <summary status="fail" total-checks="57" passed="53" failed="4">
    <by-category>
      <category name="xsd-validation" checks="4" passed="3" failed="1"/>
      <category name="id-uniqueness" checks="4" passed="3" failed="1"/>
      <category name="cross-references" checks="45" passed="43" failed="2"/>
      <category name="confidence-checks" checks="4" passed="4" failed="0"/>
    </by-category>
  </summary>

</validation-report>
```

## Related Schemas

- [Common Schema](./common-schema.md) — Shared elements (root attributes, metadata, source references, confidence)
- [issues.md](./issues.md) — Issues extraction validated by this report
- [business-rules.md](./business-rules.md) — Business rules extraction validated by this report
