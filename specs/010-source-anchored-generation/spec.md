# Feature Specification: Source-Anchored Generation

**Feature Branch**: `010-source-anchored-generation`
**Created**: 2026-02-20
**Status**: Draft
**Input**: SPEC-002 from TCOS-RUMO project: enforce extraction XML as the sole source of truth during the `/reforge.generate` phase, preventing fabrication, stale data, and identifier hallucination.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Faithful Document Generation (Priority: P1)

As a modernization engineer running `/reforge.generate`, I want the generation phase to reproduce facts exclusively from extraction XML files so that generated documents contain zero fabricated identifiers, zero incorrect statistics, and zero unsourced claims.

**Why this priority**: The generation phase introduced 7 of 13 verified errors in the TCOS-RUMO project. Every error shared the same root cause: the LLM treated extraction data as suggestive context rather than authoritative data. Preventing fabrication is the single highest-value fix.

**Independent Test**: Run `/reforge.generate markdown` against a known extraction dataset and verify every identifier and statistic in the output traces to an extraction XML element.

**Acceptance Scenarios**:

1. **Given** extraction XML contains enum members `NONE`, `IVOC-CREATE`, `ACTIVE` for PTCAuthorityStatus, **When** the agent generates a state machine document, **Then** the output contains only those exact member names (character-for-character) and no fabricated alternatives.
2. **Given** `analysis.xml` contains 864 `<file>` elements, **When** the agent generates an application overview, **Then** the output reports "864 source files" with the computation formula, not a stale or rounded number.
3. **Given** extraction XML describes "HMAC-SHA1 with hardcoded key", **When** the agent generates a security analysis, **Then** the output uses that exact description and does not substitute "challenge-response authentication".

---

### User Story 2 - Computed Statistics with Formula Transparency (Priority: P1)

As a modernization engineer reviewing generated documents, I want every numeric value to be computed by counting extraction XML elements at generation time, with the computation formula visible, so that I can verify accuracy without re-analyzing the source data.

**Why this priority**: 5 of the 13 verified errors were arithmetic/count errors (stale file counts, off-by-one state counts, wrong module counts). Computed totals with visible formulas eliminate this entire error class.

**Independent Test**: Generate a requirements registry from multiple extraction XML files and verify the total equals the sum of per-file element counts, with the formula stated inline.

**Acceptance Scenarios**:

1. **Given** 15 functional requirement extraction files totaling 938 `<requirement>` elements, **When** the agent generates a requirements registry, **Then** the output reports "938" with the formula "541 + 87 + 85 + 98 + 127 = 938".
2. **Given** `analysis.xml` contains 18 `<module>` elements, **When** the agent generates any document referencing module count, **Then** it reports "18 modules", not 16 or any other number.
3. **Given** a multi-document generation run, **When** multiple documents reference "total functional requirements", **Then** all documents show the identical value computed from the same canonical metrics table.

---

### User Story 3 - Graceful Gap Handling (Priority: P2)

As a modernization engineer, I want the generation phase to emit explicit `[DATA GAP]` markers when extraction data is insufficient, rather than fabricating content, so that I know exactly where extraction coverage needs improvement.

**Why this priority**: When the LLM fills gaps with plausible-sounding but incorrect content, the errors are hard to detect. Explicit gap markers make missing data visible and actionable.

**Independent Test**: Run `/reforge.generate` against extraction data that is deliberately incomplete for one section and verify the output contains `[DATA GAP]` markers instead of fabricated content.

**Acceptance Scenarios**:

1. **Given** extraction XML references `OnBoardState` enum but does not list member names, **When** the agent generates documentation for that enum, **Then** the output contains `[DATA GAP: OnBoardState enum member names not extracted]` and zero fabricated member names.
2. **Given** a generation run encounters 3 or more data gaps, **When** generation completes, **Then** a supplementary `gap-report.md` is produced listing all gaps with recommended `/reforge.extract` commands to fill them.
3. **Given** the generation agent needs information not present in any extraction XML, **When** it considers reading source code directly, **Then** it does NOT read source files and instead emits a `[DATA GAP]` marker.

---

### User Story 4 - Diagram Verification Protocol (Priority: P2)

As a modernization engineer, I want every generated diagram (PlantUML, Mermaid, ASCII) to pass a verification protocol that traces every node and edge to extraction XML, so that diagrams are trustworthy representations of the analyzed system.

**Why this priority**: Fabricated diagram elements (e.g., invented state names, synthesized method names) were among the most impactful errors because diagrams are often used as authoritative references in downstream modernization decisions.

**Independent Test**: Generate a PlantUML state machine diagram and verify the verification comment block reports the correct node/edge counts matching extraction data, with zero unresolved elements.

**Acceptance Scenarios**:

1. **Given** extraction XML contains 5 entity definitions with 3 relationships, **When** the agent generates a class diagram, **Then** the diagram contains exactly 5 classes and 3 relationships with a verification comment block reporting "5 nodes verified, 3 edges verified, 0 unresolved".
2. **Given** a diagram title states "49-State Machine", **When** the verification protocol runs, **Then** the diagram renders exactly 49 states matching the 49 `<member>` elements in extraction XML.
3. **Given** extraction data provides states but not transitions, **When** the agent generates a state diagram, **Then** states are rendered without transitions and a note reads "[Transitions not extracted -- see source code for state flow]".

---

### User Story 5 - Cross-Document Consistency via Canonical Metrics (Priority: P3)

As a modernization engineer generating a full documentation suite, I want shared metrics (file counts, module counts, requirement totals) to be computed once and referenced consistently across all generated documents, so that no two documents disagree on the same fact.

**Why this priority**: Inconsistent counts across documents undermine trust in the entire documentation suite. A canonical metrics table computed once per generation run eliminates this class of error.

**Independent Test**: Generate three documents (overview, architecture, requirements registry) in one run and verify all shared metrics are identical across documents.

**Acceptance Scenarios**:

1. **Given** a multi-document generation run, **When** the canonical metrics table is computed at the start, **Then** all subsequent documents reference this table for aggregate statistics rather than computing independently.
2. **Given** a selective regeneration of one document, **When** regeneration begins, **Then** the canonical metrics table is recomputed fresh (not reused from a prior run).

---

### User Story 6 - Extraction Traceability and Provenance (Priority: P3)

As a modernization engineer auditing generated documents, I want every major section to include provenance annotations citing the specific extraction files and element counts used, so that I can trace any claim back to its source data.

**Why this priority**: Provenance annotations enable downstream verification and build trust. Without them, auditing generated content requires re-deriving every fact.

**Independent Test**: Generate a document and verify every major section contains an HTML comment citing its extraction source file(s) with element counts.

**Acceptance Scenarios**:

1. **Given** a generated section sourced from `business-rules-authority.xml` (42 rules), **When** the section is rendered, **Then** it contains a provenance annotation: `<!-- Source: extractions/business-rules/business-rules-authority.xml (42 rules) -->`.
2. **Given** a generated HTML report, **When** the report is complete, **Then** a provenance footer lists all extraction files used with element counts per file.

---

### Edge Cases

- What happens when extraction XML elements use non-standard tag names that don't match the expected counting methodology (e.g., `<item>` instead of `<rule>`)?
  - The agent MUST inspect the actual XML structure and adapt the counting XPath, but MUST still count elements -- never estimate.
- What happens when multiple extraction files reference the same entity with different spellings?
  - The agent uses the extraction with the most recent audit verification date as authoritative and flags the inconsistency in the output.
- What happens when extraction XML timestamps are older than 7 days?
  - The agent emits a staleness warning at the top of generated output recommending `/reforge.extract` to refresh.
- What happens when extraction data for a required section is entirely missing (no XML file exists)?
  - The agent emits a `[DATA GAP]` marker for the entire section and includes it in the gap report.
- What happens when a diagram would be too large to render all extraction elements?
  - The agent renders a subset and explicitly states: "Showing N of M items. See [extraction-file.xml] for complete list."

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The generation phase MUST treat extraction XML files as the sole source of truth. Every fact, name, count, identifier, state name, description, and relationship in generated output MUST trace to a specific extraction XML element.
- **FR-002**: All statistics MUST be computed by counting extraction XML elements at generation time. Round numbers, estimates, and carried-forward values from prior runs are prohibited.
- **FR-003**: After computing a total, the generated output MUST state the derivation formula (e.g., "541 + 87 + 85 + 98 + 127 = 938").
- **FR-004**: All code identifiers (class names, method names, enum values, file names, state names) MUST be copied character-for-character from extraction XML. No synthesis, suffix inference, abbreviation expansion, or logical-inverse creation.
- **FR-005**: When listing items from an extraction, the agent MUST reproduce the complete list or explicitly state "Showing N of M items" with a reference to the source file.
- **FR-006**: The generation phase MUST NOT read source code files directly. All information MUST flow through audited extraction XML.
- **FR-007**: When extraction data is insufficient, the agent MUST emit a `[DATA GAP]` marker and MUST NOT fabricate content or use LLM training data to fill gaps.
- **FR-008**: If 3 or more data gaps are encountered in a single generation run, a supplementary `gap-report.md` MUST be produced listing all gaps with recommended extraction commands.
- **FR-009**: Before generating any diagrams, the agent MUST run the Diagram Verification Protocol: node audit, edge audit, label audit, count consistency check, completeness check, and output a verification comment block.
- **FR-010**: Protocol and sequence descriptions MUST quote or directly paraphrase extraction XML descriptions without changing technical meaning. No mechanism inference, no boolean operator substitution, no behavioral assumptions.
- **FR-011**: Cross-document generation runs MUST compute a canonical metrics table once at the start and reference it for all shared statistics across documents.
- **FR-012**: The canonical metrics table MUST be recomputed for each new generation run (including selective regeneration). Stale metrics from prior runs are prohibited.
- **FR-013**: Every top-level section (H2 or equivalent) of generated output MUST include a provenance annotation citing the extraction file(s) used and element counts. Any section that draws from a distinct extraction source file also qualifies.
- **FR-014**: Every generated HTML report MUST include a provenance footer listing all extraction source files with element counts.
- **FR-015**: A mandatory Content Validation Checklist MUST be completed before declaring any generation step complete (covering computed totals, verbatim identifiers, unsourced claims, diagram verification, cross-reference consistency, partial list marking, stale data, provenance annotations, source code boundary, and gap markers).
- **FR-016**: Multi-file extraction discovery MUST glob all XML files in each extraction category subdirectory -- never assume a single file per extraction type.
- **FR-017**: If extraction XML timestamps are older than 7 days, the agent MUST emit a staleness warning at the top of generated output.
- **FR-018**: Before generating output from multiple extraction files, the agent MUST run a cross-extraction consistency check (module lists, file counts, entity references, identifier spelling).
- **FR-019**: Source-Anchored Generation constraints MUST be added to the `generate.md` command template as a mandatory step (Step 0.6).
- **FR-020**: All five generation template files MUST be annotated with a reference to the Source-Anchored Generation constraints.

### Non-Functional Requirements

- **NFR-001**: N/A -- this feature modifies prompt templates only (no runtime code). Prompt size growth (~295 lines added to generate.md's existing ~1009 lines) is within acceptable limits for LLM context windows. No performance, latency, or scalability constraints apply.

### Key Entities

- **Extraction XML**: Audited XML files produced by `/reforge.extract` containing business rules, requirements, architecture data, UI definitions, and other extracted knowledge. Serves as the sole source of truth for generation.
- **Canonical Metrics Table**: A temporary table computed at the start of each generation run containing aggregate statistics (file counts, module counts, requirement totals, etc.) derived from extraction XML. Valid only for the current run.
- **Content Validation Checklist**: A mandatory 10-item verification checklist applied to every generated document before it is finalized.
- **Diagram Verification Protocol**: A 6-step verification process applied to every generated diagram (PlantUML, Mermaid, ASCII) ensuring all nodes, edges, and labels trace to extraction XML.
- **Gap Report**: A supplementary markdown file listing data gaps encountered during generation, produced when 3+ gaps occur, with recommended extraction commands to fill them.
- **Provenance Annotation**: An HTML comment or inline reference citing the specific extraction file(s) and element counts used to generate a section.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Zero fabricated identifiers in generated output -- every code identifier (class, method, enum value, file name, state name) exists verbatim in extraction XML when verified by post-generation audit.
- **SC-002**: Zero arithmetic errors -- every numeric statistic in generated output matches the element count derived from extraction XML, with the computation formula stated.
- **SC-003**: Zero unsourced claims -- every factual statement in generated output traces to a specific extraction XML element, verified by provenance annotations.
- **SC-004**: 100% of generated diagrams pass the Diagram Verification Protocol with zero unresolved nodes or edges.
- **SC-005**: Cross-document consistency -- all shared metrics (file counts, module counts, requirement totals) are identical across all documents in a multi-document generation run.
- **SC-006**: When extraction data is insufficient, the agent produces `[DATA GAP]` markers 100% of the time instead of fabricating content.
- **SC-007**: The Content Validation Checklist is completed for every generated document, with all items passing before the document is finalized.
- **SC-008**: Regression test -- when applied to the TCOS-RUMO project dataset, the updated framework prevents all 7 generation-phase errors identified in the failure taxonomy.

## Assumptions

- Extraction XML files have been audited for accuracy before the generation phase runs.
- The extraction XML schema uses recognizable element names (e.g., `<rule>`, `<requirement>`, `<module>`, `<file>`, `<state>`, `<member>`) that can be counted. When the schema differs, the agent adapts the XPath but still counts elements.
- The `analysis.xml` file represents the current project structure and has been updated by a recent `/reforge.analyze` run.
- Template files in `.reforge/templates/` are editable and can receive additional annotation sections.
- The `generate.md` command file supports adding new mandatory steps (like Step 0.6) without breaking existing step numbering.

## Dependencies

- **SPEC-002 (TCOS-RUMO)**: This feature implements the requirements defined in the TCOS-RUMO Source-Anchored Generation spec.
- **Existing extraction pipeline**: The `/reforge.extract` command must produce well-formed XML with countable elements.
- **Existing `generate.md` command template**: Changes are additive (new sections inserted) -- no existing behavior is removed.
- **Failure taxonomy**: The 13 verified errors and 14 gap analysis items from the TCOS-RUMO project serve as the validation baseline.

## Scope

### In Scope

- Modifications to `.reforge/commands/generate.md` (adding Step 0.6, canonical metrics, validation checklist, diagram verification, provenance annotations, cross-extraction consistency, freshness validation, HTML report generation, template placeholder specification, selective regeneration updates)
- Annotations added to 5 template files in `.reforge/templates/`
- Validation through 8 defined test cases

### Out of Scope

- Changes to the extraction phase (`/reforge.extract`)
- Changes to the analysis phase (`/reforge.analyze`)
- Changes to the audit phase (`/reforge.audit`)
- Automated tooling or scripts to enforce constraints at runtime (constraints are enforced by the LLM agent following the prompt template)
- Schema changes to extraction XML output formats
