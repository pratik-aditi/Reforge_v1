# Analysis Schema

> Defines the structure for codebase inventory output (`analysis.xml`)

## Overview

The analysis schema captures the results of the `/reforge.analyze` command, providing a complete inventory of the legacy codebase including file listings, detected languages, and component mappings.

## Root Element

```xml
<analysis version="1.0.0" generated="2024-01-15T10:30:00Z">
  <project>...</project>
  <files>...</files>
  <summary>...</summary>
</analysis>
```

### Attributes

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `version` | string | Yes | Schema version |
| `generated` | dateTime | Yes | Timestamp when analysis was generated |

## Elements

### `<project>`

Project identification and configuration.

```xml
<project id="my-legacy-app" name="My Legacy App" root-path="/src" status="completed">
  <configuration>
    <exclusion-pattern>**/node_modules/**</exclusion-pattern>
    <exclusion-pattern>**/vendor/**</exclusion-pattern>
    <language-hints>java</language-hints>
  </configuration>
</project>
```

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string | Yes | Unique project identifier |
| `name` | string | Yes | Human-readable project name |
| `root-path` | string | Yes | Root path of analyzed codebase |
| `status` | ProjectStatusType | Yes | Analysis status |

#### ProjectStatusType

| Value | Description |
|-------|-------------|
| `not-started` | Analysis not yet begun |
| `in-progress` | Analysis currently running |
| `completed` | Analysis finished successfully |
| `paused` | Analysis paused (can resume) |

### `<files>`

Collection of analyzed files.

```xml
<files count="150">
  <file path="src/Main.java" language="java" file-type="source"
        size-bytes="2048" line-count="85" hash="abc123"
        analysis-status="completed" analyzed-at="2024-01-15T10:30:00Z">
    <components>
      <component type="class" name="Main" line-start="10" line-end="85"/>
    </components>
    <imports>
      <import>java.util.List</import>
    </imports>
    <exports>
      <export>Main</export>
    </exports>
  </file>
</files>
```

#### File Attributes

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `path` | string | Yes | Relative file path |
| `language` | string | Yes | Detected programming language |
| `file-type` | FileTypeEnum | Yes | Classification of file |
| `size-bytes` | integer | Yes | File size in bytes |
| `line-count` | integer | No | Number of lines |
| `hash` | string | Yes | Content hash for change detection |
| `analysis-status` | AnalysisStatusType | Yes | File analysis status |
| `analyzed-at` | dateTime | No | When file was analyzed |

#### FileTypeEnum

| Value | Description |
|-------|-------------|
| `source` | Source code files |
| `config` | Configuration files |
| `template` | Template files (HTML, JSP, etc.) |
| `data` | Data files (JSON, XML, CSV) |
| `binary` | Binary files (images, compiled) |
| `unknown` | Unrecognized file type |

#### AnalysisStatusType

| Value | Description |
|-------|-------------|
| `pending` | Not yet analyzed |
| `in-progress` | Currently being analyzed |
| `completed` | Successfully analyzed |
| `skipped` | Excluded by configuration |
| `error` | Analysis failed |

### `<components>`

Code components within a file (classes, functions, etc.).

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `type` | string | Yes | Component type (class, function, interface) |
| `name` | string | Yes | Component identifier |
| `line-start` | integer | No | Starting line number |
| `line-end` | integer | No | Ending line number |

### `<summary>`

Aggregate statistics for the analysis.

```xml
<summary total-files="150" total-lines="12500" analyzed="145" skipped="5">
  <languages>
    <language name="java" count="100" lines="10000"/>
    <language name="xml" count="45" lines="2000"/>
  </languages>
  <file-types>
    <type name="source" count="100"/>
    <type name="config" count="45"/>
    <type name="binary" count="5"/>
  </file-types>
</summary>
```

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `total-files` | integer | Yes | Total files discovered |
| `total-lines` | integer | Yes | Total lines of code |
| `analyzed` | integer | Yes | Files successfully analyzed |
| `skipped` | integer | Yes | Files excluded from analysis |

## Example Output

```xml
<?xml version="1.0" encoding="UTF-8"?>
<analysis xmlns="http://reforge.dev/schema/analysis"
          version="1.0.0"
          generated="2024-01-15T10:30:00Z">
  <project id="ecommerce-legacy" name="E-Commerce Platform"
           root-path="/opt/app" status="completed">
    <configuration>
      <exclusion-pattern>**/node_modules/**</exclusion-pattern>
      <exclusion-pattern>**/test/**</exclusion-pattern>
    </configuration>
  </project>
  <files count="3">
    <file path="src/OrderService.java" language="java" file-type="source"
          size-bytes="4096" line-count="150" hash="a1b2c3"
          analysis-status="completed" analyzed-at="2024-01-15T10:30:00Z">
      <components>
        <component type="class" name="OrderService" line-start="15" line-end="150"/>
        <component type="method" name="createOrder" line-start="25" line-end="60"/>
      </components>
      <imports>
        <import>com.company.model.Order</import>
      </imports>
    </file>
  </files>
  <summary total-files="3" total-lines="450" analyzed="3" skipped="0">
    <languages>
      <language name="java" count="3" lines="450"/>
    </languages>
    <file-types>
      <type name="source" count="3"/>
    </file-types>
  </summary>
</analysis>
```

## Related Schemas

- [business-rules.md](./business-rules.md) — Extracted business logic
- [database.md](./database.md) — Database interactions
- [ui-flows.md](./ui-flows.md) — UI component flows
- [workflows.md](./workflows.md) — Process workflows

## Contract Reference

Based on: `specs/001-legacy-analyzer/contracts/analysis.xsd`
