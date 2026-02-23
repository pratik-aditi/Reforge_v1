# Metrics Registry Schema

> Defines the structure for the metrics registry (`metrics-registry.xml`)

## Overview

The metrics registry schema defines the authoritative store of all computed statistics for a project. One file per project, it serves as the single source of truth for every numeric claim that appears in generated documents. The `/reforge.audit consistency` command builds and recomputes this registry, and the post-generation scan populates the `<references>` section of each metric entry.

## Root Element

```xml
<metrics-registry project-id="my-app" version="1.0.0"
                  generated="2024-01-15T14:00:00Z"
                  total-metrics="25" source-extractions="4">
  <configuration>...</configuration>
  <metrics>...</metrics>
  <scan-patterns>...</scan-patterns>
</metrics-registry>
```

### Attributes

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `project-id` | string | Yes | Project identifier matching analysis.xml |
| `version` | string | Yes | Schema version (semver) |
| `generated` | dateTime | Yes | Registry creation/update timestamp |
| `total-metrics` | integer | Yes | Count of `<metric>` elements |
| `source-extractions` | integer | Yes | Count of extraction XML files read |

## Elements

### `<configuration>`

Tolerance defaults, scan file types, and exclusion list governing registry behaviour.

```xml
<configuration>
  <tolerance-defaults>
    <tolerance qualifier="approximately" percent="5" direction="gte"/>
    <tolerance qualifier="nearly" percent="3" direction="lte"/>
    <tolerance qualifier="over" percent="0" direction="gte"/>
    <tolerance qualifier="under" percent="0" direction="lte"/>
  </tolerance-defaults>
  <scan-file-types>
    <file-type extension=".md" parser="markdown"/>
    <file-type extension=".html" parser="html"/>
    <file-type extension=".puml" parser="plantuml"/>
    <file-type extension=".mmd" parser="mermaid"/>
    <file-type extension=".svg" parser="svg"/>
  </scan-file-types>
  <exclusion-list>
    <exclude pattern-text="version 1.0" added-by="operator" added-at="2024-01-15T14:00:00Z"/>
  </exclusion-list>
</configuration>
```

#### `<tolerance-defaults>`

Collection of `<tolerance>` rules that apply to all metrics unless overridden at the metric level.

#### `<tolerance>` Attributes (within `<tolerance-defaults>`)

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `qualifier` | string | Yes | Text qualifier triggering this tolerance (e.g., "approximately", "nearly", "over", "under") |
| `percent` | decimal | Yes | Non-negative tolerance percentage allowed |
| `direction` | enum | Yes | `gte` (document value may be greater-or-equal) or `lte` (document value may be less-or-equal) |

#### `<scan-file-types>`

Collection of `<file-type>` entries defining which generated document types the scanner reads.

#### `<file-type>` Attributes

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `extension` | string | Yes | File extension including leading dot (e.g., `.md`, `.html`, `.puml`, `.mmd`, `.svg`) |
| `parser` | string | Yes | Parser strategy to extract numeric claims: `markdown` (Markdown), `html` (HTML), `plantuml` (PlantUML title/note/comment text), `mermaid` (Mermaid node/label/comment text), `svg` (SVG `<text>` element content), `plaintext` (generic text) |

#### `<exclusion-list>`

Collection of `<exclude>` entries for intentionally ignored unregistered metric patterns.

#### `<exclude>` Attributes

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `pattern-text` | string | Yes | The numeric pattern text to suppress (e.g., "version 1.0") |
| `added-by` | string | Yes | Who added the exclusion (operator or audit run identifier) |
| `added-at` | dateTime | Yes | Timestamp when the exclusion was added |

### `<metrics>`

Collection of `<metric>` entries representing all computed statistics.

```xml
<metrics>
  <metric id="MET-FILE-TOTAL" category="codebase" name="Total Source Files"
          value="864" unit="files"
          computation="count(//file) in analysis.xml"
          source="reforge_output/TCOS-RUMO/analysis/analysis.xml"
          computed-at="2024-01-15T14:00:00Z">
    <references>
      <ref file="generated/documentation.md" line="12"/>
      <ref file="generated/user-stories.md" line="5"/>
    </references>
  </metric>
</metrics>
```

### `<metric>`

A single computed statistic within the registry.

```xml
<metric id="MET-BR-COUNT" category="extraction" name="Business Rules Count"
        value="981" unit="rules"
        computation="count(//business-rule) in business-rules.xml"
        source="reforge_output/TCOS-RUMO/extractions/business-rules.xml"
        computed-at="2024-01-15T14:00:00Z">
  <breakdown>
    <component source="src/service/PaymentService.java" count="120"/>
    <component source="src/service/OrderService.java" count="95"/>
    <component source="src/rules/ValidationRules.java" count="766"/>
  </breakdown>
  <references>
    <ref file="generated/documentation.md" line="34"/>
    <ref file="generated/user-stories.md" line="18"/>
  </references>
  <tolerance qualifier="approximately" percent="5" direction="gte"/>
</metric>
```

#### Attributes

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string | Yes | Unique metric identifier. Pattern: `MET-{CATEGORY}-{NAME}` (e.g., `MET-FILE-TOTAL`, `MET-BR-COUNT`) |
| `category` | enum | Yes | `codebase` \| `extraction` \| `generation` \| `coverage` |
| `name` | string | Yes | Human-readable metric name |
| `value` | string | Yes | Canonical value (stored as string for numeric and percentage formats) |
| `unit` | string | Yes | Unit of measurement (files, rules, requirements, modules, states, percent, etc.) |
| `computation` | string | Yes | Formula or method used to derive the value |
| `source` | string | Yes | Path to the extraction/analysis file(s) used as input |
| `computed-at` | dateTime | Yes | Timestamp when the value was last computed |

#### CategoryType Values

| Value | Description |
|-------|-------------|
| `codebase` | Statistics derived from the analysis inventory (e.g., file counts, line counts) |
| `extraction` | Statistics derived from extraction XML files (e.g., business rule counts, workflow counts) |
| `generation` | Statistics about generated output (e.g., document counts, page counts) |
| `coverage` | Ratio metrics comparing extraction scope to codebase scope |

### `<breakdown>`

Optional decomposition of an aggregate metric into per-file or per-category components. Sum of all component counts MUST equal the parent metric `value`.

```xml
<breakdown>
  <component source="src/service/PaymentService.java" count="120"/>
  <component source="src/service/OrderService.java" count="95"/>
</breakdown>
```

#### `<component>` Attributes

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `source` | string | Yes | Source file or category contributing to the aggregate |
| `count` | integer | Yes | Count contributed by this source |

### `<references>`

Required list of every generated document location where the parent metric's value appears.

```xml
<references>
  <ref file="generated/documentation.md" line="12"/>
  <ref file="generated/user-stories.md" line="5"/>
</references>
```

#### `<ref>` Attributes

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `file` | string | Yes | Relative path to the generated document |
| `line` | string | Yes | Line number or section reference within the document |

### `<tolerance>` (metric-level override)

Optional per-metric tolerance override. When present, this overrides the matching qualifier in `<tolerance-defaults>`.

```xml
<tolerance qualifier="approximately" percent="10" direction="gte"/>
```

#### Attributes

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `qualifier` | string | Yes | Text qualifier this tolerance applies to |
| `percent` | decimal | Yes | Non-negative tolerance percentage allowed |
| `direction` | enum | Yes | `gte` (document value may be greater-or-equal) or `lte` (document value may be less-or-equal) |

### `<scan-patterns>`

Collection of `<pattern>` entries defining how the scanner recognizes metric categories in document text.

```xml
<scan-patterns>
  <pattern id="PAT-FILE-COUNT" description="Matches file count claims such as '864 source files' or '864 files analyzed'"
           metric-category="codebase" metric-hint="MET-FILE-TOTAL">
    <qualifier-patterns>
      <qualifier term="approximately" tolerance-percent="5"/>
      <qualifier term="nearly" tolerance-percent="3"/>
      <qualifier term="over" tolerance-percent="0"/>
    </qualifier-patterns>
  </pattern>
</scan-patterns>
```

### `<pattern>`

A named rule for recognizing a metric category in document text.

```xml
<pattern id="PAT-BR-COUNT" description="Matches business rule count claims such as '981 business rules' or '981 rules extracted'"
         metric-category="extraction" metric-hint="MET-BR-COUNT">
  <qualifier-patterns>
    <qualifier term="approximately" tolerance-percent="5"/>
  </qualifier-patterns>
</pattern>
```

#### Attributes

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string | Yes | Pattern identifier (e.g., `PAT-FILE-COUNT`) |
| `description` | string | Yes | Human-readable description of what this pattern matches (used by the LLM agent) |
| `metric-category` | string | Yes | Which metric category this pattern typically maps to |
| `metric-hint` | string | No | Suggested metric ID for disambiguation |

#### `<qualifier-patterns>`

Collection of `<qualifier>` entries defining approximate value qualifiers for the parent pattern.

#### `<qualifier>` Attributes

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `term` | string | Yes | Qualifying word or phrase (e.g., "approximately", "nearly", "over") |
| `tolerance-percent` | decimal | Yes | Tolerance percentage when this qualifier is present |

---

## Validation Rules

1. **Breakdown integrity**: For every metric with `<breakdown>`, `sum(component/@count) == metric/@value`
2. **Metric ID uniqueness**: No duplicate `id` values within `<metrics>`
3. **Reference accuracy**: Every `<ref>` in a metric's `<references>` section must correspond to an actual occurrence in the cited file
4. **Tolerance bounds**: `percent` values must be non-negative decimals; `direction` must be `gte` or `lte`
5. **Pattern coverage**: Every metric category must have at least one corresponding scan pattern
6. **Exclusion integrity**: Excluded patterns must not match any registered metric ID

---

## Storage Location

Output path: `reforge_output/<project-name>/metrics-registry.xml`

---

## Examples

### Complete Metrics Registry

```xml
<metrics-registry project-id="TCOS-RUMO" version="1.0.0"
                  generated="2024-01-15T14:00:00Z"
                  total-metrics="5" source-extractions="4">

  <configuration>
    <tolerance-defaults>
      <tolerance qualifier="approximately" percent="5" direction="gte"/>
      <tolerance qualifier="nearly" percent="3" direction="lte"/>
      <tolerance qualifier="over" percent="0" direction="gte"/>
      <tolerance qualifier="under" percent="0" direction="lte"/>
    </tolerance-defaults>
    <scan-file-types>
      <file-type extension=".md" parser="markdown"/>
      <file-type extension=".html" parser="html"/>
      <file-type extension=".puml" parser="plantuml"/>
      <file-type extension=".mmd" parser="mermaid"/>
      <file-type extension=".svg" parser="svg"/>
      <file-type extension=".txt" parser="plaintext"/>
    </scan-file-types>
    <exclusion-list>
      <exclude pattern-text="version 1.0" added-by="operator" added-at="2024-01-15T14:00:00Z"/>
      <exclude pattern-text="3 categories" added-by="audit-run-003" added-at="2024-01-16T09:30:00Z"/>
    </exclusion-list>
  </configuration>

  <metrics>
    <!-- Codebase metric: total source files -->
    <metric id="MET-FILE-TOTAL" category="codebase" name="Total Source Files"
            value="864" unit="files"
            computation="count(//file) in analysis.xml"
            source="reforge_output/TCOS-RUMO/analysis/analysis.xml"
            computed-at="2024-01-15T14:00:00Z">
      <references>
        <ref file="generated/documentation.md" line="12"/>
        <ref file="generated/user-stories.md" line="5"/>
        <ref file="generated/data-dictionary.md" line="8"/>
      </references>
    </metric>

    <!-- Extraction metric: business rules count with breakdown -->
    <metric id="MET-BR-COUNT" category="extraction" name="Business Rules Count"
            value="981" unit="rules"
            computation="count(//business-rule) in business-rules.xml"
            source="reforge_output/TCOS-RUMO/extractions/business-rules.xml"
            computed-at="2024-01-15T14:00:00Z">
      <breakdown>
        <component source="src/service/PaymentService.java" count="120"/>
        <component source="src/service/OrderService.java" count="95"/>
        <component source="src/rules/ValidationRules.java" count="412"/>
        <component source="src/rules/PricingEngine.java" count="354"/>
      </breakdown>
      <references>
        <ref file="generated/documentation.md" line="34"/>
        <ref file="generated/user-stories.md" line="18"/>
      </references>
      <tolerance qualifier="approximately" percent="3" direction="gte"/>
    </metric>

    <!-- Extraction metric: database table count -->
    <metric id="MET-DB-TABLES" category="extraction" name="Database Tables"
            value="245" unit="tables"
            computation="count(//table) in database.xml"
            source="reforge_output/TCOS-RUMO/extractions/database.xml"
            computed-at="2024-01-15T14:00:00Z">
      <references>
        <ref file="generated/data-dictionary.md" line="22"/>
        <ref file="generated/documentation.md" line="56"/>
      </references>
    </metric>

    <!-- Coverage metric: extraction coverage percentage -->
    <metric id="MET-COV-EXTRACT" category="coverage" name="Extraction Coverage"
            value="87.5" unit="percent"
            computation="(files-with-extractions / total-analysed-files) * 100"
            source="reforge_output/TCOS-RUMO/analysis/analysis.xml"
            computed-at="2024-01-15T14:00:00Z">
      <references>
        <ref file="generated/documentation.md" line="90"/>
      </references>
    </metric>

    <!-- Generation metric: generated document count -->
    <metric id="MET-GEN-DOCS" category="generation" name="Generated Documents"
            value="12" unit="documents"
            computation="count of files in generated/ directory"
            source="reforge_output/TCOS-RUMO/generated/"
            computed-at="2024-01-15T14:00:00Z">
      <breakdown>
        <component source="generated/markdown/" count="6"/>
        <component source="generated/user-stories/" count="4"/>
        <component source="generated/data-dictionary/" count="2"/>
      </breakdown>
      <references>
        <ref file="generated/documentation.md" line="3"/>
      </references>
    </metric>
  </metrics>

  <scan-patterns>
    <pattern id="PAT-FILE-COUNT" description="Matches file count claims such as '864 source files' or '864 files analyzed'"
             metric-category="codebase" metric-hint="MET-FILE-TOTAL">
      <qualifier-patterns>
        <qualifier term="approximately" tolerance-percent="5"/>
        <qualifier term="nearly" tolerance-percent="3"/>
        <qualifier term="over" tolerance-percent="0"/>
      </qualifier-patterns>
    </pattern>

    <pattern id="PAT-BR-COUNT" description="Matches business rule count claims such as '981 business rules' or '981 rules extracted'"
             metric-category="extraction" metric-hint="MET-BR-COUNT">
      <qualifier-patterns>
        <qualifier term="approximately" tolerance-percent="5"/>
        <qualifier term="nearly" tolerance-percent="3"/>
      </qualifier-patterns>
    </pattern>

    <pattern id="PAT-TABLE-COUNT" description="Matches database table count claims such as '245 tables' or '245 database tables'"
             metric-category="extraction" metric-hint="MET-DB-TABLES">
      <qualifier-patterns>
        <qualifier term="approximately" tolerance-percent="5"/>
        <qualifier term="over" tolerance-percent="0"/>
      </qualifier-patterns>
    </pattern>

    <pattern id="PAT-COVERAGE-PCT" description="Matches coverage percentage claims such as '87.5% coverage' or '87.5 percent extraction coverage'"
             metric-category="coverage" metric-hint="MET-COV-EXTRACT">
      <qualifier-patterns>
        <qualifier term="approximately" tolerance-percent="5"/>
        <qualifier term="nearly" tolerance-percent="3"/>
        <qualifier term="over" tolerance-percent="0"/>
        <qualifier term="under" tolerance-percent="0"/>
      </qualifier-patterns>
    </pattern>

    <pattern id="PAT-DOC-COUNT" description="Matches generated document count claims such as '12 documents generated' or '12 generated documents'"
             metric-category="generation" metric-hint="MET-GEN-DOCS">
      <qualifier-patterns>
        <qualifier term="approximately" tolerance-percent="5"/>
      </qualifier-patterns>
    </pattern>

    <!-- Diagram-specific patterns: match numeric claims in diagram titles, notes, labels -->
    <pattern id="PAT-PUML-TITLE" description="In PlantUML files (.puml): matches numeric claims in title directives (e.g., 'title 49 States') and note blocks (e.g., 'note: 981 business rules')"
             metric-category="extraction"/>
    <pattern id="PAT-MMD-LABEL" description="In Mermaid files (.mmd): matches numeric claims in node labels (e.g., 'A[981 Business Rules]') and annotation text"
             metric-category="extraction"/>
    <pattern id="PAT-SVG-TEXT" description="In SVG files (.svg): matches numeric claims within &lt;text&gt; element content (e.g., '&lt;text&gt;864 Source Files&lt;/text&gt;')"
             metric-category="codebase"/>
  </scan-patterns>

</metrics-registry>
```
