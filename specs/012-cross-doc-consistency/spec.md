# Feature Specification: Cross-Document Consistency Checker

**Feature Branch**: `012-cross-doc-consistency`
**Created**: 2026-02-23
**Status**: Draft
**Input**: User description: "Metrics registry and consistency scanner to prevent contradictory statistics across generated Reforge documents."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Prevent Contradictory Statistics During Generation (Priority: P1)

A framework operator runs the document generation command for a legacy codebase project. Before any documents are created, the system automatically computes all aggregate statistics (file counts, rule counts, requirement counts, module counts, etc.) from the extraction data and stores them in a single authoritative registry. Every generated document then draws its numeric claims from this registry rather than computing them independently, ensuring all documents report identical values for the same metric.

**Why this priority**: This is the root-cause prevention mechanism. Without a shared metrics layer, every document independently derives statistics, leading to the contradictions observed in real projects (e.g., one document reporting 785 source files while another reports 864 for the same codebase). Prevention is more valuable than detection alone.

**Independent Test**: Can be fully tested by running a generation command against a project with known extraction data and verifying that every numeric claim in every output document matches the registry value.

**Acceptance Scenarios**:

1. **Given** extraction data exists with known element counts, **When** the operator runs the generation command, **Then** a metrics registry is created before any document and all generated documents reference registry values.
2. **Given** a metric has a breakdown (e.g., requirements split across categories), **When** the registry is populated, **Then** the sum of all breakdown components equals the stated total.
3. **Given** a document needs to display a statistic, **When** the document is generated, **Then** the value is read from the registry (not computed independently) and an annotation cites the metric identifier for traceability.

---

### User Story 2 - Detect Discrepancies Across Existing Documents (Priority: P1)

A framework operator has previously generated documents at different times. Some documents may contain stale or incorrect statistics because the underlying extraction data changed after they were generated. The operator runs a consistency audit that scans all generated documents, extracts every numeric claim, compares each against the authoritative registry, and produces a discrepancy report listing every mismatch with its exact location, severity, and recommended action.

**Why this priority**: Equally critical because existing projects already have generated documents with known contradictions. Detection is needed alongside prevention to address the backlog of inconsistencies and to catch any metrics that bypassed the registry.

**Independent Test**: Can be fully tested by placing documents with known incorrect values alongside a correct registry and verifying that the scan detects every mismatch and classifies severity correctly.

**Acceptance Scenarios**:

1. **Given** the registry says "864 source files" and a document says "785 source files", **When** the consistency audit runs, **Then** a critical-severity discrepancy is reported with the exact file and line number.
2. **Given** a document says "approximately 900 requirements" and the registry says 981, **When** tolerance rules are applied, **Then** the discrepancy is classified as warning (within 10% tolerance) rather than critical.
3. **Given** a document contains a numeric claim not tracked by any registry metric, **When** the scan encounters it, **Then** an informational discrepancy is reported as "unregistered metric."
4. **Given** multiple documents reference the same metric and one has the correct value while another does not, **When** the audit runs, **Then** only the incorrect document is flagged.

---

### User Story 3 - Scan Metrics in Diagrams and Graphics (Priority: P2)

A framework operator generates not just text reports but also diagrams (PlantUML, Mermaid) and vector graphics (SVG) that contain embedded statistics in titles, labels, and annotations. The consistency scanner detects and verifies metrics in these non-HTML formats using the same pattern-based extraction, ensuring diagram labels match the registry values.

**Why this priority**: Diagrams are a common source of hard-to-spot discrepancies (e.g., a state machine diagram title saying "48 states" when the actual count is 49). While less frequent than text document issues, diagram inconsistencies are particularly embarrassing in presentations and executive summaries.

**Independent Test**: Can be fully tested by creating diagram source files and SVG files with known incorrect metric values and verifying they are detected.

**Acceptance Scenarios**:

1. **Given** the registry says 49 states and a PlantUML diagram title says "48-State Machine", **When** the scan runs, **Then** a critical discrepancy is reported for the diagram file.
2. **Given** an SVG file contains a text element saying "16 modules" but the registry says 18, **When** the scan runs, **Then** the mismatch is detected in the SVG content.
3. **Given** an HTML report contains inline SVG with metric values, **When** the scan runs, **Then** the metric is detected once (not double-counted from both the HTML and SVG scan).

---

### User Story 4 - Bootstrap Registry for Existing Projects (Priority: P2)

A framework operator has a project with generated documents but no metrics registry (the project predates this feature). The operator runs the consistency audit, which automatically creates the registry from current extraction data, then scans existing documents against it. This produces a migration report showing all existing discrepancies and recommended corrections.

**Why this priority**: Supports adoption for existing projects without requiring full regeneration upfront. The operator gets immediate visibility into inconsistencies and can address them incrementally.

**Independent Test**: Can be fully tested by running the audit on a project with no registry file and verifying the registry is created and existing document discrepancies are detected.

**Acceptance Scenarios**:

1. **Given** a project has generated documents (with or without an existing registry file), **When** the operator runs the consistency audit, **Then** the registry is always recomputed from current extraction data before the scan, ensuring validation uses the freshest canonical values.
2. **Given** the bootstrapped registry is created, **When** the scan completes, **Then** the discrepancy report shows all existing inconsistencies between documents and the freshly computed canonical values.

---

### Edge Cases

- What happens when a document contains the same metric multiple times on different lines? Each occurrence is independently verified and reported if mismatched.
- What happens when extraction data is missing or incomplete at registry population time? The system reports which metrics could not be computed and skips them.
- What happens when a numeric value in a document matches multiple registry metrics (e.g., "18" could be modules or a different count)? The scanner reports all candidate matches with a confidence indicator; the operator reviews ambiguous ones to determine the correct association.
- What happens when comma-separated numbers are used (e.g., "1,292")? The scanner normalizes number formatting before comparison.
- What happens when singular vs. plural forms differ (e.g., "1 module" vs "18 modules")? Patterns handle both forms.
- What happens when partial regeneration updates some documents but not others? The scan detects stale values in un-regenerated documents and flags them for update.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST compute all aggregate statistics from extraction data and store them in a single authoritative metrics registry before generating any document.
- **FR-002**: System MUST ensure every numeric statistic in a generated document originates from the metrics registry, not from independent computation.
- **FR-003**: Each registry entry MUST record its computation method, source data location, and timestamp, enabling upstream tracing of any value.
- **FR-004**: For aggregate metrics composed of multiple sub-counts, the registry MUST store the breakdown and verify that component values sum to the stated total.
- **FR-005**: Generated documents MUST include traceability annotations (comments or metadata) citing the metric identifier for each embedded statistic.
- **FR-006**: System MUST provide a post-generation consistency scan that extracts all numeric claims from generated documents and compares them against the registry.
- **FR-007**: The consistency scan MUST use configurable pattern-based extraction to recognize metrics in natural language context (e.g., "864 source files", "981 functional requirements").
- **FR-008**: The scan MUST support multiple document formats: HTML, Markdown, PlantUML source, Mermaid source, and SVG files.
- **FR-009**: The scan MUST produce a discrepancy report listing each mismatch with: metric identifier, expected value, actual value, file location, line number, severity, and recommended action.
- **FR-010**: Discrepancies MUST be classified by severity: critical (exact value mismatch), warning (approximate value outside tolerance), and informational (unregistered metric).
- **FR-011**: System MUST support configurable tolerance rules for approximate values, recognizing qualifying language ("approximately", "~", "about", "roughly", "nearly", "over", "fewer than") and applying appropriate tolerance bands.
- **FR-012**: Default tolerance for approximate qualifiers MUST be +/- 10%. Per-metric tolerance overrides MUST be supported.
- **FR-013**: Values with no qualifying language MUST require exact matches (zero tolerance).
- **FR-014**: The consistency audit MUST be runnable independently of generation, comparing existing documents against the current registry.
- **FR-015**: When the audit runs, the system MUST always recompute the metrics registry from current extraction data before scanning, regardless of whether a registry file already exists. This ensures the audit validates documents against the freshest canonical values, not a potentially stale registry.
- **FR-016**: The scan MUST generate correction items for each discrepancy, specifying the corrective action (regenerate document, register new metric, or investigate).
- **FR-017**: The pattern list MUST be extensible so that project-specific patterns can be added without modifying the framework.
- **FR-018**: The consistency scan MUST emit visible warnings for critical discrepancies but MUST NOT block or fail the generation workflow.
- **FR-019**: The system MUST support an exclusion list where operators can mark specific unregistered metric patterns as intentionally ignored. Excluded patterns MUST be skipped on subsequent scans. New (previously unseen) unregistered metrics MUST still be reported.
- **FR-020**: When a numeric claim matches multiple registry metrics ambiguously, the scan MUST report all candidate matches with a confidence indicator rather than silently picking one or skipping the match. The operator reviews ambiguous matches to determine the correct association.

### Non-Functional Requirements

- **NFR-001**: Registry computation plus full consistency scan MUST complete in under 5 minutes for a typical project (fewer than 100 generated documents, fewer than 50 registered metrics, fewer than 500 numeric claims).
- **NFR-002**: All schema extensions MUST be backward compatible — existing correction plans, audit reports, and generated documents MUST remain valid without modification.

### Key Entities

- **Metrics Registry**: The authoritative store of all computed statistics for a project. Contains metric entries, tolerance configuration, scan patterns, and an exclusion list for intentionally ignored unregistered patterns. One per project.
- **Metric Entry**: A single computed statistic with its identifier, canonical value, computation method, source reference, timestamp, optional breakdown, and list of document locations where it appears.
- **Scan Pattern**: A named rule for recognizing a metric category in document text, with associated metric hints for disambiguation.
- **Tolerance Rule**: Configuration defining how approximate values are matched against canonical values, with qualifier recognition and percentage bands.
- **Discrepancy**: A detected mismatch between a document's numeric claim and the registry's canonical value, with severity classification, confidence indicator, and corrective action.
- **Consistency Report**: The output of a scan, containing all discrepancies, per-file scan summaries, per-metric verification summaries, and a human-readable overview.
- **Correction Item**: An actionable entry generated from a discrepancy, specifying what needs to change and how.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: After a full generation run, zero critical discrepancies exist across all generated documents (all documents agree on every metric).
- **SC-002**: The consistency scan detects 100% of deliberately introduced value mismatches in test scenarios (no false negatives for exact-match metrics).
- **SC-003**: Every aggregate statistic appearing in any generated document can be traced back to a single registry entry with documented computation method and source data.
- **SC-004**: The scan correctly applies tolerance rules, classifying approximate values as warnings rather than critical errors when qualifying language is present and the value falls within the configured tolerance band.
- **SC-005**: Diagram and graphic files (PlantUML, Mermaid, SVG) are scanned with the same detection accuracy as text documents.
- **SC-006**: Existing projects without a registry can be onboarded through an automated bootstrap process that creates the registry and identifies all current discrepancies in under 5 minutes for a typical project.
- **SC-007**: The discrepancy report provides sufficient detail (file, line, expected vs. actual, severity, action) for an operator to resolve each issue without additional investigation.
- **SC-008**: Selective regeneration of a single document uses registry values, maintaining consistency with all other documents that reference the same metrics.

## Clarifications

### Session 2026-02-23

- Q: Should the consistency audit always recompute the registry from extraction data, or trust an existing registry? → A: Always recompute from extraction data before scanning, regardless of whether a registry already exists.
- Q: How should repeated unregistered metric reports be handled across audit runs? → A: Allow an exclusion list where operators mark specific unregistered patterns as intentionally ignored; new unregistered metrics still get flagged.
- Q: How should the scanner handle ambiguous matches where a numeric claim could match multiple registry metrics? → A: Report all candidate matches with a confidence indicator; operator reviews ambiguous ones.

## Assumptions

- The extraction data (XML files) is the ultimate source of truth for all computed statistics. The registry derives values from extraction data, not from generated documents.
- A "typical project" for performance expectations contains fewer than 100 generated documents and fewer than 50 registered metrics.
- Document formats are limited to HTML, Markdown, PlantUML, Mermaid, and SVG. Other formats (e.g., PDF, DOCX) are out of scope.
- The pattern-based extraction approach (matching "NNN noun" patterns in text) provides sufficient coverage for recognizing metrics in natural language. Highly unusual phrasings may not be detected and can be addressed by adding custom patterns.
- Tolerance rules apply only when qualifying language is explicitly present in the document text. A bare number without qualifiers always requires an exact match.
- The registry is project-scoped (one per project). Cross-project metric consistency is out of scope.
- The registry uses a single canonical value per metric (no versioning of historical values).

## Scope Boundaries

### In Scope

- Metrics registry creation and population from extraction data
- Pattern-based metric extraction from HTML, Markdown, PlantUML, Mermaid, and SVG files
- Configurable tolerance rules with qualifier recognition
- Discrepancy reporting with severity classification
- Correction item generation for identified mismatches
- Integration with the existing generation and audit commands
- Bootstrap workflow for existing projects without a registry

### Out of Scope

- Cross-project metric consistency
- Historical metric versioning (tracking values over time)
- Automated regeneration triggered by discrepancies (requires operator approval)
- PDF or DOCX document scanning
- Real-time monitoring of metric drift (batch scan only)

## Dependencies

- Depends on the existing extraction data format and analysis output
- Depends on the existing generation command workflow (for integration of the registry population step)
- Depends on the existing audit command framework (for adding the consistency audit type)
- Depends on the existing correction plan format (for adding new correction types)
