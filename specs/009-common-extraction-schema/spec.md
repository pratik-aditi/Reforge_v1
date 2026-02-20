# Feature Specification: Common Extraction Schema

**Feature Branch**: `009-common-extraction-schema`
**Created**: 2026-02-20
**Status**: Draft
**Input**: User description: "Review our extracts XML, we really need a common format this will make it easier, we need to create a common schema that all can use and validate against when extracting"

## Clarifications

### Session 2026-02-20

- Q: How should type-specific schemas reference the common schema? → A: Reference-by-link with single source of truth — type-specific `.md` schemas link to `common-schema.md` for shared elements and only define type-specific additions. The agent reads both files during validation.
- Q: Should a `common-schema.xsd` be created alongside the markdown schema? → A: Yes — create `common-schema.xsd` in `.reforge/schemas/xsd/` and update type-specific XSDs to use `xs:import` to reference common types. Full XSD parity with the markdown layer.
- Q: What happens when validation finds a violation the agent cannot auto-correct? → A: Write the file with inline XML comment warnings at violation points (e.g., `<!-- SCHEMA-WARNING: missing confidence -->`) and emit a summary warning. Do not abort.
- Q: What should the initial common schema version be? → A: `1.0.0` — signals production readiness, follows semver.
- Q: How should XML namespaces be structured across extraction types? → A: Single shared namespace — all extraction types use `http://reforge.dev/schema/extraction`. Type-specific elements are distinguished by element names, not namespaces.

## Context

Reforge extraction commands (`/reforge.extract`) produce XML files for each extraction type (business-rules, database, ui-flows, workflows). Currently, each extraction type uses its own ad-hoc XML structure with significant inconsistencies:

- **3 different attribute names** for project identifier (`project`, `project-id`, `source-module`)
- **3 different version formats** (`2.0`, `1.0`, `1.0.0`)
- **4 different patterns** for source line references (`line="145-160"`, `line-start`/`line-end`, `lines="..."`, `<LineNumber>`)
- **2 of 8 files** declare XML namespaces (XSD requires all to)
- **No standardized metadata container** — each type invents its own
- Files within the same type (e.g., two business-rules files) use **incompatible element structures**
- Existing XSD schemas define structures that actual extraction output **does not conform to** (workflows at ~35% conformance)

This makes it difficult for downstream consumers (audit, generation, cross-mapping) to reliably parse extractions, and for the extract command to produce consistent output.

## User Scenarios & Testing

### User Story 1 — Consistent Extraction Output (Priority: P1)

When the agent runs `/reforge.extract [type]`, every extraction XML file produced conforms to a common structural contract — same root attributes, same metadata section, same source reference format — regardless of extraction type.

**Why this priority**: This is the core value proposition. Without consistent output, no downstream command can reliably consume extractions.

**Independent Test**: Run `/reforge.extract business-rules` and `/reforge.extract database` on any codebase. Open both output files and verify that root attributes, metadata sections, and source references follow the same structural pattern. Validate both files against the common schema definition.

**Acceptance Scenarios**:

1. **Given** a codebase with analysis complete, **When** the agent runs `/reforge.extract business-rules`, **Then** the output XML has the standardized root attributes (`project-id`, `version`, `generated`, `xmlns`), a `<metadata>` section with required fields, and all `<source>` elements use the canonical format
2. **Given** a codebase with analysis complete, **When** the agent runs `/reforge.extract database`, **Then** the output XML follows the exact same root attribute names, metadata structure, and source reference format as the business-rules output
3. **Given** extraction output from any type, **When** a downstream command reads the file, **Then** it can locate the project identifier, generation timestamp, item count, and confidence distribution using the same element paths regardless of extraction type
4. **Given** extraction output, **When** the file is validated against the common schema, **Then** it passes validation with zero structural errors

---

### User Story 2 — Schema Definition and Documentation (Priority: P1)

The framework provides a single common schema definition that documents the shared structural contract — root elements, metadata, source references, confidence levels, ID patterns — alongside type-specific extension points for each extraction type.

**Why this priority**: The schema definition is the authoritative reference that extraction commands validate against. Without it, consistency is aspirational rather than enforceable.

**Independent Test**: Read the schema definition file and verify it documents all common elements, attributes, and type-specific extensions. Verify that a sample extraction file can be validated against it.

**Acceptance Scenarios**:

1. **Given** the common schema definition exists, **When** a contributor reads it, **Then** they can determine the required root attributes, metadata structure, source reference format, and confidence vocabulary without examining individual extraction files
2. **Given** the schema definition, **When** it is compared to each type-specific schema, **Then** every type-specific schema imports or extends the common schema rather than redefining shared elements
3. **Given** the schema definition, **When** an extraction output file is produced, **Then** the extract command can reference the schema to verify structural compliance before writing the file

---

### User Story 3 — Extract Command Validation Gate (Priority: P2)

The `/reforge.extract` command validates its output against the common schema before writing the final file, catching structural inconsistencies at extraction time rather than at audit time.

**Why this priority**: Validation at write time prevents drift. Without it, schema conformance degrades over time as the agent makes ad-hoc decisions.

**Independent Test**: Modify an extraction template to produce a file missing a required attribute (e.g., remove `project-id`). Run `/reforge.extract` and verify the agent detects and corrects the missing attribute before writing the file.

**Acceptance Scenarios**:

1. **Given** the extract command produces output, **When** the output is missing a required common element (e.g., `<metadata>` section), **Then** the agent detects the omission and adds the missing element before writing
2. **Given** the extract command produces output, **When** a source reference uses a non-standard format (e.g., `line="145-160"` instead of `line-start`/`line-end`), **Then** the agent normalizes it to the canonical format
3. **Given** the extract command completes successfully, **When** the output file is examined, **Then** it contains a schema-version attribute indicating which common schema version it conforms to

---

### User Story 4 — Migration of Existing Schemas (Priority: P3)

The four existing type-specific schema definitions (business-rules, database, ui-flows, workflows) are updated to reference the common schema for shared elements, eliminating redundant definitions while preserving type-specific extensions.

**Why this priority**: Existing schemas must align with the new common schema to avoid having two competing sources of truth.

**Independent Test**: Open each updated type-specific schema and verify it references the common schema for shared elements (root attributes, metadata, source references) and only defines elements unique to that extraction type.

**Acceptance Scenarios**:

1. **Given** the updated business-rules schema, **When** compared to the common schema, **Then** shared elements (root attributes, metadata, source references, confidence) are inherited from the common schema, not redefined
2. **Given** all four updated type-specific schemas, **When** the set of common elements is extracted from each, **Then** they are identical across all four (zero divergence in shared element definitions)
3. **Given** the updated schemas, **When** an existing extraction output is compared to the new schema, **Then** a clear migration gap report identifies what attributes and elements need to change

---

### Edge Cases

- What happens when an extraction type has no items to extract? The output file should still contain valid root attributes and an empty metadata section with zero counts
- What happens when the agent produces an extraction file for a custom extraction type not covered by the four standard schemas? The common schema elements still apply; type-specific sections are unconstrained
- What happens when an existing extraction file from before this change is read by a command expecting the new format? Downstream commands should detect the schema version (or absence thereof) and handle legacy files gracefully with a warning
- What happens when the source file path contains special characters or very long paths? Source references should preserve the exact path without truncation or encoding changes
- What happens when validation detects a violation the agent cannot auto-correct (e.g., missing data for a required value)? The agent writes the file with inline `<!-- SCHEMA-WARNING: ... -->` comments at violation points and emits a summary warning; it does not abort the extraction

## Requirements

### Functional Requirements

- **FR-001**: The framework MUST define a common extraction schema that specifies the shared structural contract for all extraction output files
- **FR-002**: The common schema MUST define standardized root attributes: `project-id` (string), `version` (semver pattern), `generated` (ISO-8601 timestamp), `schema-version` (semver), and `xmlns` set to `http://reforge.dev/schema/extraction` — a single shared namespace used by all extraction types
- **FR-003**: The common schema MUST define a standardized `<metadata>` container with required child elements: `<total-count>`, `<confidence-distribution>` (with `<high>`, `<medium>`, `<low>` counts), and `<extraction-timestamp>`
- **FR-004**: The common schema MUST define a standardized source reference format: `<source file="..." line-start="..." line-end="...">` with an optional `<snippet>` child element
- **FR-005**: The common schema MUST define the confidence vocabulary as an enumeration: `high`, `medium`, `low`
- **FR-006**: The common schema MUST define a standardized ID pattern convention for extraction items (prefix-category-sequence, e.g., `BR-VAL-001`, `WF-AUTH-001`)
- **FR-007**: Each type-specific schema (business-rules, database, ui-flows, workflows) MUST link to `common-schema.md` for shared elements (root attributes, metadata, source references, confidence vocabulary) and only define type-specific additions — no redefinition of common elements
- **FR-008**: The `/reforge.extract` command MUST validate its output against the common schema before writing the file, checking for required root attributes, metadata section, and source reference format. When auto-correction is not possible, the agent MUST still write the file but insert `<!-- SCHEMA-WARNING: [description] -->` XML comments at each violation point and emit a summary warning to the user
- **FR-009**: Extraction output files MUST include a `schema-version` attribute on the root element indicating which version of the common schema they conform to. The initial version is `1.0.0`, following semver conventions
- **FR-010**: The common schema MUST be delivered as both `common-schema.md` in `.reforge/schemas/` and `common-schema.xsd` in `.reforge/schemas/xsd/`, maintaining full parity between markdown and XSD representations
- **FR-011**: The common schema MUST support extensibility — type-specific schemas can add elements and attributes beyond the common set without violating the common schema
- **FR-012**: Downstream commands (audit, generate, status) MUST be able to extract project identifier, generation timestamp, item count, and confidence distribution using the same element paths regardless of extraction type
- **FR-013**: The extract command MUST normalize source references to the canonical format (converting `line="X-Y"` variants to `line-start`/`line-end`) during output generation
- **FR-014**: The framework MUST handle legacy extraction files (pre-common-schema) gracefully — downstream commands should detect missing schema-version and emit a warning rather than failing

### Key Entities

- **Common Schema**: The shared structural definition that all extraction types inherit — defines root attributes, metadata, source references, confidence vocabulary, and ID conventions
- **Type-Specific Schema**: Extension schema for each extraction type (business-rules, database, ui-flows, workflows) that adds domain-specific elements on top of the common schema
- **Extraction Output**: An XML file produced by `/reforge.extract` that conforms to both the common schema and its type-specific schema
- **Source Reference**: A standardized element that traces an extracted item back to its origin in the analyzed codebase (file path, line range, optional code snippet)
- **Schema Version**: A version identifier on each extraction output indicating which common schema version the file conforms to

## Success Criteria

### Measurable Outcomes

- **SC-001**: 100% of extraction output files produced by `/reforge.extract` pass validation against the common schema (zero structural errors on required elements)
- **SC-002**: All four extraction types use identical attribute names for project identifier, version, and generation timestamp (zero naming divergence)
- **SC-003**: Downstream commands can parse any extraction file's metadata (project ID, item count, confidence distribution) using a single set of element paths — no type-specific parsing logic for common fields
- **SC-004**: The common schema definition fits within a single document that a contributor can read and understand in under 10 minutes
- **SC-005**: Type-specific schemas reference the common schema for shared elements, with zero redundant element definitions across the four type-specific schemas

## Assumptions

- The four standard extraction types (business-rules, database, ui-flows, workflows) are sufficient for the common schema scope. Additional extraction types (functional-requirements, non-functional, issues) may be added later but are out of scope for this feature
- A new `common-schema.xsd` will be created in `.reforge/schemas/xsd/`, and existing type-specific XSDs will be updated to use `xs:import` to reference common types. The markdown in `.reforge/schemas/` remains the authoritative source; XSDs maintain parity
- Backward compatibility with existing extraction files is a soft requirement — a migration guide or tooling is not in scope, but downstream commands should not crash on legacy files
- The common schema covers structural consistency only — it does not prescribe extraction completeness, coverage quality, or content accuracy (those remain the domain of `/reforge.audit`)

## Dependencies

- **Constitution Principle I**: The common schema must be enforceable by the LLM agent using native tools (Read, Write, Glob, Grep) — no external XML validators or parsers
- **Constitution Principle III**: Structured output with defined schemas — this feature directly strengthens that principle
- **Existing schemas**: `.reforge/schemas/business-rules.md`, `database.md`, `ui-flows.md`, `workflows.md` and their XSD counterparts must be updated to reference the common schema
- **Extract command**: `.reforge/commands/extract.md` must be updated to include a validation gate referencing the common schema

## Out of Scope

- Migrating or converting existing extraction output files to the new format
- Schema definitions for non-standard extraction types (functional-requirements, non-functional, issues-and-bugs, architecture)
- Runtime XML validation tooling (e.g., XSD validators) — validation is performed by the LLM agent reading the schema definition
- Changes to the audit, generate, or status command templates (those will naturally benefit from consistent extraction output but are not modified in this feature)
