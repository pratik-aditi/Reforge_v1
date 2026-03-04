# Schemas

Reforge uses a schema system to define the structure of all XML output files. Schemas ensure consistency across extractions and enable validation of generated output.

## What Schemas Define

Each schema specifies:

- The **root element** name and required attributes
- **Metadata** structure (counts, confidence distribution, timestamps)
- **Domain-specific elements** for the extraction type
- **Source reference** format for traceability back to code
- **ID conventions** for unique element identification
- **Validation rules** that output must satisfy

Schemas are documented as markdown files in `.reforge/schemas/` and formalized as XSD files in `.reforge/schemas/xsd/`.

## Common Schema

The common schema (`common-schema.md`) defines shared elements that all extraction types inherit. Type-specific schemas extend it -- they must not redefine any common element.

### Root Element Attributes

Every extraction XML file includes these attributes on the root element:

| Attribute | Description |
|-----------|-------------|
| `xmlns` | Namespace URI: `http://reforge.dev/schema/extraction` |
| `project-id` | Project identifier from configuration |
| `version` | Extraction version (semver) |
| `schema-version` | Common schema version (currently `1.0.0`) |
| `generated` | ISO-8601 timestamp of generation |

### Metadata Block

Every extraction file starts with a `<metadata>` element containing:

- `total-count` -- number of items extracted
- `confidence-distribution` -- breakdown into high, medium, and low counts
- `extraction-timestamp` -- when the extraction was performed

The sum of confidence counts must equal `total-count`.

### Source References

All source code references use a canonical format:

```xml
<source file="src/auth/login.py" line-start="45" line-end="52">
  <snippet>def validate_token(token): ...</snippet>
</source>
```

- `file` -- relative path from project root (no leading `/`)
- `line-start` and `line-end` -- line range (both required, both positive integers)
- `snippet` -- optional verbatim code excerpt

### Confidence Levels

All `confidence` attributes use one of three values:

| Value | Meaning |
|-------|---------|
| `high` | Clearly identified with verified source references |
| `medium` | Identified but may need verification |
| `low` | Possible item, requires human review |

### ID Conventions

Item IDs follow the pattern `{PREFIX}-{CATEGORY}-{SEQUENCE}`:

- **PREFIX** -- 2-3 uppercase letters identifying the extraction type (e.g., `BR` for business rules, `DB` for database)
- **CATEGORY** -- short uppercase code for the domain category (e.g., `VAL`, `AUTH`)
- **SEQUENCE** -- zero-padded 3-digit number (`001`--`999`)

## Available Schemas

### Core Extraction Types

| Schema | Root Element | Description |
|--------|-------------|-------------|
| `analysis.md` | `<analysis>` | Codebase inventory -- files, modules, languages, frameworks |
| `business-rules.md` | `<business-rules>` | Business logic, validation rules, calculations |
| `database.md` | `<database>` | SQL queries, data models, ORM mappings, entities |
| `ui-flows.md` | `<ui-flows>` | Screens, components, navigation flows, forms |
| `workflows.md` | `<workflows>` | Execution paths, state machines, event handlers |

### Extended Extraction Types

| Schema | Root Element | Description |
|--------|-------------|-------------|
| `call-sites.md` | `<call-sites>` | Method/function call relationships with caller-callee traceability |
| `dependencies.md` | `<dependencies>` | Module dependency graphs -- imports, events, interfaces, inheritance |
| `functional-requirements.md` | `<functional-requirements>` | Functional requirements with acceptance criteria derived from code |
| `non-functional.md` | `<non-functional-requirements>` | Non-functional requirements (SLAs, performance) and security findings (CWE) |
| `architecture.md` | `<architecture>` | Architectural components, integration points, design patterns |
| `issues.md` | `<issues>` | Bugs, defects, TODOs, technical debt, operational issues |

### Derived and Generated Types

| Schema | Root Element | Description |
|--------|-------------|-------------|
| `cross-mappings.md` | `<cross-mappings>` | Relationships between extraction types |
| `features-requirements.md` | `<features-requirements>` | Features and requirements derived from extractions |
| `user-stories.md` | `<user-stories>` | Modernization backlog items |
| `glossary.md` | `<acronym-glossary>` | Acronyms and abbreviations with definitions |

### Audit Types

| Schema | Root Element | Description |
|--------|-------------|-------------|
| `audit-report.md` | `<audit-report>` | Coverage gaps and stale references |
| `full-audit-report.md` | `<full-audit-report>` | Comprehensive audit across all types |
| `accuracy-audit-report.md` | `<accuracy-audit-report>` | Content accuracy validation |
| `consistency-audit-report.md` | `<consistency-audit-report>` | Cross-document consistency checks |
| `correction-plan.md` | `<correction-plan>` | Actionable corrections from audit findings |
| `metrics-registry.md` | `<metrics-registry>` | Cross-document metrics for consistency scanning |

## How Schemas Relate to Extraction Types

Each `/reforge.extract <type>` command produces an XML file that conforms to the corresponding schema:

```
/reforge.extract business-rules  -->  business-rules.xml  -->  business-rules.md schema
/reforge.extract database        -->  database.xml        -->  database.md schema
/reforge.extract architecture    -->  architecture.xml    -->  architecture.md schema
```

The extraction command reads the schema to understand what elements to produce, what attributes are required, and how to format source references. The audit command (`/reforge.audit`) validates extraction output against these schemas.

## XSD Validation

Formal XML Schema Definition (XSD) files are available in `.reforge/schemas/xsd/` for machine-validation of extraction output:

| XSD File | Validates |
|----------|-----------|
| `common-schema.xsd` | Shared types included by all other XSDs |
| `analysis.xsd` | Analysis inventory files |
| `business-rules.xsd` | Business rules extractions |
| `database.xsd` | Database extractions |
| `ui-flows.xsd` | UI flow extractions |
| `workflows.xsd` | Workflow extractions |
| `call-sites.xsd` | Call site extractions |
| `dependencies.xsd` | Dependency extractions |
| `functional-requirements.xsd` | Functional requirement extractions |
| `non-functional.xsd` | Non-functional requirement extractions |
| `architecture.xsd` | Architecture extractions |
| `issues.xsd` | Issue extractions |
| `audit-report.xsd` | Audit report files |
| `correction-plan.xsd` | Correction plan files |
| `user-stories.xsd` | User story generation output |

Type-specific XSDs include the common schema via `<xs:include schemaLocation="common-schema.xsd"/>`, inheriting all shared type definitions.

## Adding New Extraction Types

To add a new extraction type:

1. Choose a root element name and register it in the common schema
2. Register new type prefix(es) in the ID prefix registry
3. Create a type-specific schema markdown file in `.reforge/schemas/`
4. Create a corresponding XSD in `.reforge/schemas/xsd/` that includes `common-schema.xsd`
5. All root attributes, metadata, source references, and confidence vocabulary are inherited automatically
