# Research: Cross-Document Consistency Checker

**Branch**: `012-cross-doc-consistency` | **Date**: 2026-02-23

## R1: Relationship to Existing Canonical Metrics Computation

**Decision**: Evolve the existing ephemeral metrics table in `generate.md` (lines 1056-1079) into a persistent `metrics-registry.xml` file.

**Rationale**: `generate.md` already computes a canonical metrics table with per-file breakdowns and derivation formulas. However, rule 4 explicitly states: "The computed metrics table is ephemeral — it exists in the agent's working context during the run and is not persisted as a separate file." The new feature changes this single rule: the table is now written to `metrics-registry.xml` so that audits and subsequent generation runs can reference it. The computation logic, discovery procedure, and formula documentation remain identical.

**Alternatives considered**:
- Create a completely separate metrics computation in audit.md → Rejected because it duplicates the existing generate.md logic and risks drift between the two.
- Keep metrics ephemeral but add a separate cross-document comparison → Rejected because without a canonical file, audit scans have no authoritative reference to compare against.

## R2: Relationship to Existing Consistency Audit Workflow

**Decision**: Extend the existing consistency audit workflow in `audit.md` (Consistency Audit Workflow section) with new steps for registry-based scanning, rather than creating a new audit type.

**Rationale**: The existing consistency audit already has `<cross-document-checks>` and `<freshness-checks>` sections that partially address cross-document discrepancies. The new feature significantly deepens these sections with pattern-based extraction, tolerance rules, and a metrics registry reference. Extending the existing workflow avoids a proliferation of audit types and leverages the established audit pipeline (report generation, correction plan, fix execution).

**Alternatives considered**:
- New audit type: `/reforge.audit metrics` → Rejected because it fragments the consistency story. Cross-document metric consistency IS a subset of consistency auditing.
- Standalone command: `/reforge.metrics-check` → Rejected because it bypasses the existing audit infrastructure (correction plans, fix command integration).

## R3: Correction Plan Extension Strategy

**Decision**: Add two new CorrectionType values (`metric-mismatch`, `unregistered-metric`) and one new CategoryType value (`metrics-consistency`) to the existing correction-plan schema.

**Rationale**: The correction plan schema already supports 8 correction types and 5 categories. Adding new values is a backward-compatible extension. The existing `/reforge.fix` command processes corrections by category priority order, so adding a new category maintains the priority chain.

**Alternatives considered**:
- Reuse existing `inconsistent` type → Rejected because `inconsistent` is scoped to metadata count mismatches within a single file, not cross-document metric discrepancies.
- Separate correction file → Rejected because `/reforge.fix` reads a single correction plan file.

## R4: Schema for metrics-registry.xml

**Decision**: Create a new schema definition at `.reforge/schemas/metrics-registry.md` following the established schema documentation pattern used by other schemas (audit-report.md, correction-plan.md, etc.).

**Rationale**: Every XML output in Reforge has a corresponding schema definition in `.reforge/schemas/`. The metrics registry is a new XML artifact requiring its own schema. The schema documents root attributes, metric entries, scan patterns, tolerance configuration, and exclusion lists.

**Alternatives considered**:
- Embed registry schema in the audit.md command file → Rejected because schemas are a separate concern documented in their own files.
- Use JSON instead of XML → Rejected because all Reforge structured output uses XML per Constitution Principle III.

## R5: Pattern-Based Metric Extraction Approach

**Decision**: Define scan patterns as part of the metrics registry schema, with each pattern containing a human-readable description and a matching rule. The LLM agent uses these patterns as recognition guides when reading generated documents, not as compiled regex.

**Rationale**: Reforge is LLM-first (Constitution Principle I). The patterns describe what to look for in natural language terms that the agent can apply using its reading comprehension. The agent reads each generated document, identifies numeric claims matching the pattern descriptions, and compares them against registry values. No compiled regex engine is needed.

**Alternatives considered**:
- Compiled regex patterns → Rejected per Constitution Principle I (no compiled code, no external parsers).
- Fully freeform scanning with no pattern definitions → Rejected because patterns provide consistency and extensibility. Without defined patterns, the agent might inconsistently recognize metrics across runs.

## R6: Consistency Audit Report Schema Extension

**Decision**: Extend the existing `consistency-audit-report.md` schema with new sections for `<metrics-registry-checks>` covering registry-vs-document comparisons, tolerance results, and exclusion list application.

**Rationale**: The existing schema already has `<cross-document-checks>` and `<freshness-checks>` which partially overlap. The new sections provide the deeper detail needed for metrics registry validation (confidence indicators, tolerance application, exclusion list references). The existing sections remain valid for their original scope (internal corpus consistency).

**Alternatives considered**:
- Replace existing `<cross-document-checks>` → Rejected because the existing section serves a different purpose (detecting when the same metric appears with different values across documents without a registry reference).
- Separate report file → Rejected because the consistency audit produces a single report per run.

## R7: Generate.md Integration Points

**Decision**: Modify the "Canonical Metrics Computation" section in generate.md to persist the metrics table as `metrics-registry.xml`, and add a post-generation consistency scan step.

**Rationale**: The existing section already does 90% of the work (compute, discover files, count elements, document formulas). The only changes needed are: (1) write the result to an XML file instead of keeping it ephemeral, (2) add metric ID annotations to generated content, (3) add a final scan step. This is a minimal-diff modification to an established workflow.

**Changes required to generate.md**:
1. **Canonical Metrics Computation section**: Change rule 4 from "ephemeral" to "persisted as metrics-registry.xml". Add instructions to write the XML file following the metrics-registry schema.
2. **Content Validation Checklist**: Add item 11: "Metric ID annotations are present for every numeric statistic (HTML comments, diagram comments)."
3. **New final section**: "Post-Generation Consistency Scan" — after all documents are generated, run a quick scan comparing embedded values against the registry.
