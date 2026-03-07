# Dead Code Report Schema

> Defines the structure for dead/unreachable code detection (`dead-code-report.xml`)

## Overview

The dead code report schema captures unreachable, unused, or orphaned code items identified by `/reforge.dead-code`. It cross-references call-site and dependency graph data to identify methods with no callers, classes never instantiated, files with no inbound dependencies, and unused variables/imports.

## Common Elements

This schema extends the [Common Extraction Schema](./common-schema.md), which defines shared structural elements used across all extraction types:

- **Root attributes**: `project-id`, `version`, `schema-version`, `generated`, `xmlns`
- **Metadata container**: `<metadata>` with `<total-count>`, `<confidence-distribution>`, `<extraction-timestamp>`
- **Source references**: Canonical `<source>` format with `file`, `line-start`, `line-end` attributes
- **Confidence vocabulary**: `high`, `medium`, `low` enumeration
- **ID patterns**: `DC-{CATEGORY}-{SEQUENCE}`

See `common-schema.md` for complete definitions. Elements defined there MUST NOT be redefined in this schema.

## Root Element

```xml
<dead-code-report xmlns="http://reforge.dev/schema/extraction"
                  project-id="my-app" version="1.0.0"
                  schema-version="1.0.0"
                  generated="2024-01-15T10:30:00Z">
  <metadata>...</metadata>
  <summary>...</summary>
  <dead-items>...</dead-items>
</dead-code-report>
```

### Attributes

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `xmlns` | URI | Yes | Must be `http://reforge.dev/schema/extraction` |
| `project-id` | string | Yes | Reference to analysis project |
| `version` | string | Yes | Extraction version (semver) |
| `schema-version` | string | Yes | Common schema version (initial: `1.0.0`) |
| `generated` | dateTime | Yes | Extraction timestamp (ISO-8601) |

> Root attributes and `<metadata>` are defined by the [Common Extraction Schema](./common-schema.md). The `<metadata>` element is required as the first child of the root element. The metadata `<total-count>` equals the count of all dead items.

## Elements

### `<summary>`

Aggregate statistics for the dead code report.

```xml
<summary total-lines="1250" total-files-affected="18">
  <by-type>
    <type name="method" count="15" lines="480"/>
    <type name="class" count="3" lines="320"/>
    <type name="file" count="2" lines="400"/>
    <type name="variable" count="8" lines="50"/>
  </by-type>
  <by-reason>
    <reason name="no-callers" count="12"/>
    <reason name="unreachable-branch" count="5"/>
    <reason name="unused-import" count="8"/>
    <reason name="never-instantiated" count="3"/>
  </by-reason>
</summary>
```

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `total-lines` | integer | Yes | Total lines of dead code identified |
| `total-files-affected` | integer | Yes | Number of files containing dead code |

### `<dead-items>`

Container for dead code items.

```xml
<dead-items count="28">
  <dead-item>...</dead-item>
</dead-items>
```

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `count` | integer | Yes | Number of dead code items in this container |

### `<dead-item>`

Individual dead code item with type, reason, and source traceability.

```xml
<dead-item id="DC-METH-001" item-type="method" reason="no-callers"
           confidence="high" severity="medium">
  <name>calculateLegacyDiscount</name>
  <description>Method has no callers in the call-site graph. Last modified 2019-03-15.</description>
  <containing-class>PricingService</containing-class>
  <lines-of-code>35</lines-of-code>
  <last-modified>2019-03-15</last-modified>
  <evidence>
    <call-site-ref>No CALL entries reference this method as callee</call-site-ref>
    <dependency-ref>No DEP entries reference this symbol</dependency-ref>
  </evidence>
  <source file="src/service/PricingService.java" line-start="120" line-end="155">
    <snippet>public BigDecimal calculateLegacyDiscount(Order order) {
    // Old discount logic replaced by NewPricingEngine
    ...</snippet>
  </source>
</dead-item>
```

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string | Yes | Unique dead code item identifier (`DC-{CATEGORY}-{SEQUENCE}`) |
| `item-type` | string | Yes | Type of dead code item |
| `reason` | string | Yes | Why the code is considered dead |
| `confidence` | ConfidenceType | Yes | Extraction confidence level |
| `severity` | string | Yes | Impact severity (critical, high, medium, low) |

### `<item-type>` Values

| Value | Description |
|-------|-------------|
| `method` | Method or function with no callers |
| `class` | Class never instantiated or referenced |
| `file` | File with no inbound dependencies |
| `variable` | Variable declared but never read |
| `import` | Import statement for unused symbol |
| `constant` | Constant defined but never referenced |
| `interface` | Interface with no implementations |

### `<reason>` Values

| Value | Description |
|-------|-------------|
| `no-callers` | No call-site references this method/function |
| `unreachable-branch` | Code path that can never execute |
| `unused-import` | Import of symbol that is never used |
| `never-instantiated` | Class is never constructed or referenced |
| `no-readers` | Variable is written but never read |
| `no-implementations` | Interface has no implementing classes |
| `dead-parameter` | Function parameter that is never used |

### `<name>`

Qualified name of the dead code item (method name, class name, variable name, etc.).

### `<description>`

Explanation of why this item is considered dead code and any additional context.

### `<containing-class>`

Optional. The class or module containing the dead item, when applicable.

### `<lines-of-code>`

Number of lines of source code in the dead item.

### `<last-modified>`

Optional. Last modification date of the dead code, if determinable from git history. Format: `YYYY-MM-DD`.

### `<evidence>`

Evidence supporting the dead code determination.

#### `<call-site-ref>`

Explanation of call-site analysis result (e.g., no callers found).

#### `<dependency-ref>`

Explanation of dependency graph analysis result (e.g., no inbound references).

### `<source>`

Source code location where the dead item exists. Uses the canonical format defined in the [Common Extraction Schema](./common-schema.md#source-references). The optional `<snippet>` child element contains the relevant code.

## Common Categories

| Category | Description | Examples |
|----------|-------------|----------|
| `METH` | Dead methods/functions | No callers, unreachable |
| `CLS` | Dead classes | Never instantiated |
| `FILE` | Dead files | No inbound dependencies |
| `VAR` | Dead variables | Written but never read |
| `IMP` | Dead imports | Unused import statements |
| `CONST` | Dead constants | Defined but never referenced |
| `IFACE` | Dead interfaces | No implementations |

## Example Output

```xml
<?xml version="1.0" encoding="UTF-8"?>
<dead-code-report xmlns="http://reforge.dev/schema/extraction"
                  project-id="ecommerce-legacy" version="1.0.0"
                  schema-version="1.0.0"
                  generated="2024-01-15T10:30:00Z">

  <metadata>
    <total-count>2</total-count>
    <confidence-distribution>
      <high>1</high>
      <medium>1</medium>
      <low>0</low>
    </confidence-distribution>
    <extraction-timestamp>2024-01-15T10:30:00Z</extraction-timestamp>
  </metadata>

  <summary total-lines="85" total-files-affected="2">
    <by-type>
      <type name="method" count="1" lines="35"/>
      <type name="class" count="1" lines="50"/>
    </by-type>
    <by-reason>
      <reason name="no-callers" count="1"/>
      <reason name="never-instantiated" count="1"/>
    </by-reason>
  </summary>

  <dead-items count="2">
    <dead-item id="DC-METH-001" item-type="method" reason="no-callers"
               confidence="high" severity="medium">
      <name>calculateLegacyDiscount</name>
      <description>Method has no callers in the call-site graph. Superseded by NewPricingEngine.</description>
      <containing-class>PricingService</containing-class>
      <lines-of-code>35</lines-of-code>
      <last-modified>2019-03-15</last-modified>
      <evidence>
        <call-site-ref>No CALL entries reference PricingService.calculateLegacyDiscount as callee</call-site-ref>
        <dependency-ref>No DEP entries reference this symbol</dependency-ref>
      </evidence>
      <source file="src/service/PricingService.java" line-start="120" line-end="155">
        <snippet>public BigDecimal calculateLegacyDiscount(Order order) {
    // Old discount logic replaced by NewPricingEngine
    ...</snippet>
      </source>
    </dead-item>

    <dead-item id="DC-CLS-001" item-type="class" reason="never-instantiated"
               confidence="medium" severity="low">
      <name>LegacyReportGenerator</name>
      <description>Class is never instantiated or referenced anywhere in the codebase.</description>
      <lines-of-code>50</lines-of-code>
      <last-modified>2018-11-20</last-modified>
      <evidence>
        <call-site-ref>No CALL entries reference any methods in this class</call-site-ref>
        <dependency-ref>No DEP entries import or reference LegacyReportGenerator</dependency-ref>
      </evidence>
      <source file="src/reports/LegacyReportGenerator.java" line-start="1" line-end="50"/>
    </dead-item>
  </dead-items>

</dead-code-report>
```

## Related Schemas

- [Common Schema](./common-schema.md) — Shared elements (root attributes, metadata, source references, confidence)
- [call-sites.md](./call-sites.md) — Call-site data used to identify methods with no callers
- [dependencies.md](./dependencies.md) — Dependency graph used to identify orphaned files and classes
- [issues.md](./issues.md) — Issues schema which also tracks dead code as a category
