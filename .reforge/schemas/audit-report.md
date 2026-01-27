# Audit Report Schema

> Defines the structure for the audit coverage report (`audit-report.xml`)

## Overview

The audit report schema captures the results of `/reforge.audit`. It records file-level coverage statistics, identifies uncovered files, and lists stale extraction references.

## Root Element

```xml
<audit-report project-id="my-app" version="1.0.0"
              generated="2024-01-15T14:00:00Z"
              scope="all"
              total-files="1247" covered-files="1100"
              uncovered-files-count="147"
              coverage-percentage="88.2"
              stale-references-count="5">
  <coverage-by-type>...</coverage-by-type>
  <uncovered-files>...</uncovered-files>
  <stale-references>...</stale-references>
  <summary>...</summary>
</audit-report>
```

### Attributes

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `project-id` | string | Yes | Reference to analyzed project |
| `version` | string | Yes | Schema version |
| `generated` | dateTime | Yes | Audit execution timestamp |
| `scope` | string | Yes | "all" or specific type audited (e.g., "business-rules") |
| `total-files` | integer | Yes | Total files in analysis inventory (after exclusions) |
| `covered-files` | integer | Yes | Files with at least one extraction reference |
| `uncovered-files-count` | integer | Yes | Files with no extraction references |
| `coverage-percentage` | decimal | Yes | (covered-files / total-files) * 100 |
| `stale-references-count` | integer | Yes | Extraction references pointing to missing/changed files |

## Elements

### `<coverage-by-type>`

Per extraction type breakdown of coverage.

```xml
<coverage-by-type>
  <type-coverage type="business-rules" files-referenced="450" total-items="156" stale-items="2"/>
  <type-coverage type="database" files-referenced="200" total-items="89" stale-items="0"/>
  <type-coverage type="ui-flows" files-referenced="150" total-items="45" stale-items="1"/>
  <type-coverage type="workflows" files-referenced="300" total-items="23" stale-items="2"/>
</coverage-by-type>
```

#### `<type-coverage>` Attributes

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `type` | string | Yes | Extraction type (business-rules, database, ui-flows, workflows) |
| `files-referenced` | integer | Yes | Number of unique files referenced by this extraction type |
| `total-items` | integer | Yes | Total extraction items of this type |
| `stale-items` | integer | Yes | Items with invalid source references |

### `<uncovered-files>`

List of analyzed files with no extraction coverage.

```xml
<uncovered-files>
  <file path="src/utils/StringHelper.java" language="java" lines="45" components="class,method"/>
  <file path="src/config/AppConfig.java" language="java" lines="120" components="class"/>
</uncovered-files>
```

#### `<file>` Attributes

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `path` | string | Yes | Relative file path from project root |
| `language` | string | Yes | Detected programming language |
| `lines` | integer | Yes | Total line count |
| `components` | string | No | Comma-separated component types (class, method, function, etc.) |

### `<stale-references>`

List of extraction items whose source references are no longer valid.

```xml
<stale-references>
  <stale-ref extraction-type="business-rules" item-id="BR-045"
             referenced-file="src/old/LegacyService.java" issue="missing"/>
  <stale-ref extraction-type="workflows" item-id="WF-012"
             referenced-file="src/service/OrderService.java" issue="modified"/>
</stale-references>
```

#### `<stale-ref>` Attributes

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `extraction-type` | string | Yes | Which extraction contains the stale reference |
| `item-id` | string | Yes | ID of the extraction item (e.g., BR-001, WF-012) |
| `referenced-file` | string | Yes | File path that is missing or has changed |
| `issue` | IssueType | Yes | Type of staleness issue |

#### IssueType Values

| Value | Description |
|-------|-------------|
| `missing` | Referenced file no longer exists on disk |
| `modified` | Referenced file exists but content hash has changed since extraction |

### `<summary>`

Human-readable summary text for display purposes.

```xml
<summary>
Coverage: 88.2% (1100 of 1247 files covered)
Uncovered: 147 files with no extraction references
Stale references: 5 items reference files that have changed or been removed
</summary>
```

---

## Scope Values

| Value | Description |
|-------|-------------|
| `all` | Full audit across all extraction types |
| `business-rules` | Audit only business rules extraction |
| `database` | Audit only database extraction |
| `ui-flows` | Audit only UI flows extraction |
| `workflows` | Audit only workflows extraction |
| `user-stories` | Audit generated user stories against extractions |
| `documentation` | Audit generated documentation against extractions |
| `diagrams` | Audit generated diagrams against extractions |
| `analysis` | Check analysis.xml for stale file entries |

---

## Storage Location

Output path: `reforge_output/<project-name>/audit/audit-report.xml`

---

## Examples

### Full Audit — Good Coverage

```xml
<audit-report project-id="legacy-ecommerce" version="1.0.0"
              generated="2024-01-15T14:00:00Z"
              scope="all"
              total-files="500" covered-files="485"
              uncovered-files-count="15"
              coverage-percentage="97.0"
              stale-references-count="0">
  <coverage-by-type>
    <type-coverage type="business-rules" files-referenced="300" total-items="120" stale-items="0"/>
    <type-coverage type="database" files-referenced="150" total-items="65" stale-items="0"/>
    <type-coverage type="ui-flows" files-referenced="100" total-items="40" stale-items="0"/>
    <type-coverage type="workflows" files-referenced="200" total-items="30" stale-items="0"/>
  </coverage-by-type>
  <uncovered-files>
    <file path="src/test/TestHelper.java" language="java" lines="30" components="class"/>
  </uncovered-files>
  <stale-references/>
  <summary>Coverage: 97.0% (485 of 500 files covered). 15 utility/config files have no extraction references.</summary>
</audit-report>
```

### Targeted Audit — Business Rules Only

```xml
<audit-report project-id="legacy-ecommerce" version="1.0.0"
              generated="2024-01-15T14:05:00Z"
              scope="business-rules"
              total-files="500" covered-files="300"
              uncovered-files-count="200"
              coverage-percentage="60.0"
              stale-references-count="2">
  <coverage-by-type>
    <type-coverage type="business-rules" files-referenced="300" total-items="120" stale-items="2"/>
  </coverage-by-type>
  <uncovered-files>
    <file path="src/service/PaymentService.java" language="java" lines="250" components="class,method"/>
  </uncovered-files>
  <stale-references>
    <stale-ref extraction-type="business-rules" item-id="BR-045"
               referenced-file="src/old/LegacyPricing.java" issue="missing"/>
    <stale-ref extraction-type="business-rules" item-id="BR-089"
               referenced-file="src/validate/OrderValidator.java" issue="modified"/>
  </stale-references>
  <summary>Business rules coverage: 60.0%. 2 stale references found.</summary>
</audit-report>
```
