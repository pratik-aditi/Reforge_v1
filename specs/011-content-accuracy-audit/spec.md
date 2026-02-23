# Feature Specification: Content Accuracy Audit

**Feature Branch**: `011-content-accuracy-audit`
**Created**: 2026-02-22
**Status**: Draft
**Input**: Upstream SPEC-003 from TCOS-RUMO project: extend `/reforge.audit` with accuracy verification, consistency checking, and combined full-audit mode to detect fabricated content, arithmetic errors, broken cross-references, and stale generated output.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Accuracy Audit Detects Fabricated Content (Priority: P1)

As a modernization engineer reviewing extraction output, I want the audit command to verify that every extracted identifier actually exists in the source codebase so that fabricated content (hallucinated names, non-existent methods, invented enum values) is caught before it propagates to generated documentation.

**Why this priority**: Fabricated content is the most damaging audit failure. The TCOS-RUMO project shipped with 12 fabricated acronym entries, 2 fabricated enum member names, and 2 fabricated file/method references — none detectable by the existing coverage audit. Accuracy verification is the single highest-value addition to the audit command.

**Independent Test**: Run `/reforge.audit accuracy` against a known extraction corpus containing fabricated identifiers (restored pre-audit acronym glossary with 12 fabricated entries). Verify all 12 are flagged as fabricated with zero false negatives.

**Acceptance Scenarios**:

1. **Given** an extraction XML containing the identifier "IVSA" in an acronym glossary, **When** the agent runs `/reforge.audit accuracy` and searches the entire source codebase using word-boundary matching, **Then** the identifier is classified as `fabricated` because zero standalone occurrences exist.
2. **Given** an extraction XML containing the identifier "InactiveSelfTest" for a StateOfOnBoard enum member, **When** the agent runs the accuracy audit, **Then** the identifier is classified as `confirmed` because it exists as a standalone token in the source code.
3. **Given** an extraction item referencing source file `Locomotive.vb` at line 166, **When** the agent verifies the reference, **Then** the reference is classified as `passed` if the file exists and has content at that line, or `failed-missing`/`failed-line-mismatch` otherwise.
4. **Given** the accuracy audit completes with failures, **When** the results are written, **Then** a correction plan is generated with `type="fabricated"` entries recommending deletion of each fabricated item.

---

### User Story 2 - Consistency Audit Detects Contradictions and Staleness (Priority: P1)

As a modernization engineer reviewing generated documentation, I want the audit command to detect arithmetic errors, broken cross-references, duplicate IDs, and stale generated content so that I can trust the internal consistency of the extraction corpus and generated output.

**Why this priority**: The TCOS-RUMO project contained 4 arithmetic errors (e.g., "900 FR" vs. actual 981), 3 broken cross-references, and multiple stale file counts across generated documents. These consistency failures erode trust even when individual extractions are accurate. Consistency checking is a prerequisite for reliable documentation generation.

**Independent Test**: Run `/reforge.audit consistency` against a corpus containing known arithmetic mismatches, broken cross-references, and stale generated documents. Verify all known issues are detected.

**Acceptance Scenarios**:

1. **Given** an extraction XML file with a `total-items="120"` metadata attribute but only 115 actual child elements, **When** the agent runs `/reforge.audit consistency`, **Then** an arithmetic mismatch is reported with expected=120 and actual=115.
2. **Given** a generated document claiming "785 files" while `analysis.xml` records 864, **When** the consistency audit runs, **Then** a freshness/cross-document discrepancy is flagged with both values and their source locations.
3. **Given** an extraction file containing `<cross-ref target="business-rules-bulletins.xml">` where the actual file is named `bulletin-rules.xml`, **When** the consistency audit runs, **Then** a `broken-file` cross-reference finding is reported.
4. **Given** two different business-rules extraction files both containing an element with `id="BR-045"`, **When** the duplicate ID check runs, **Then** a critical-severity duplicate is reported with both file locations.

---

### User Story 3 - Full Audit Provides Unified Quality Assessment (Priority: P2)

As a modernization engineer preparing extraction output for downstream consumption, I want a single command that runs coverage, consistency, and accuracy audits in sequence and produces a unified quality score so that I have a comprehensive, single-number assessment of corpus quality.

**Why this priority**: Running three separate audit commands and manually correlating results is error-prone and time-consuming. A unified full-audit mode with a composite quality score (coverage 25%, consistency 35%, accuracy 40%) gives engineers a single actionable metric and a merged correction plan.

**Independent Test**: Run `/reforge.audit full` against the TCOS-RUMO corpus. Verify that four report files are generated, the composite quality score is arithmetically correct, and the correction plan merges items from all three audit types.

**Acceptance Scenarios**:

1. **Given** a complete extraction corpus, **When** the agent runs `/reforge.audit full`, **Then** three individual audit reports plus one unified report are produced, and one merged correction plan is generated.
2. **Given** the full audit completes with coverage=96.2%, consistency=94.7%, accuracy=97.6%, **When** the composite score is computed, **Then** it equals `96.2*0.25 + 94.7*0.35 + 97.6*0.40 = 96.2%` and the quality rating maps to the appropriate action recommendation.
3. **Given** the full audit produces corrections from all three audit types, **When** the merged correction plan is written, **Then** each correction includes a `source-audit-type` attribute indicating which audit produced it, and corrections are prioritized by category (analysis first, then extraction, then metadata, then cross-document, then generation).

---

### User Story 4 - Statistical Sampling for Large Corpora (Priority: P2)

As a modernization engineer working with large extraction corpora (thousands of items), I want the accuracy audit to use statistical sampling with configurable rates so that I can get a high-confidence accuracy assessment without verifying every single item.

**Why this priority**: Full verification of every extraction item is expensive for large corpora. Stratified random sampling at 20% provides a 95% confidence interval while reducing verification cost by 80%. Users who need full verification can opt in with a flag.

**Independent Test**: Run `/reforge.audit accuracy` on a corpus with 4,636+ items. Verify that at least 20% are sampled per extraction category, the sample is diverse across source files, and a confidence interval is reported.

**Acceptance Scenarios**:

1. **Given** a corpus with 4,636 total extraction items, **When** the agent runs `/reforge.audit accuracy` with default settings, **Then** at least 927 items (20%) are sampled with proportional representation across extraction categories.
2. **Given** the sampling completes, **When** the accuracy report is generated, **Then** it includes a confidence interval formatted as "95% CI: X% +/- Y%" with the margin of error below 3%.
3. **Given** the user specifies `--full-verify`, **When** the accuracy audit runs, **Then** every extraction item is verified (no sampling) and the report notes `methodology="census"`.
4. **Given** any stratum shows accuracy below 90% during sampling, **When** the audit evaluates results, **Then** it flags that stratum for full verification in its recommendations.

---

### User Story 5 - Backward Compatibility (Priority: P1)

As a user of the existing `/reforge.audit` command, I want the default behavior (no type argument) to remain unchanged so that existing workflows continue to work without modification.

**Why this priority**: Breaking backward compatibility would disrupt existing users. The new audit types are additive — they extend the command without altering existing behavior.

**Independent Test**: Run `/reforge.audit` with no type argument and compare output against a baseline run. Verify identical behavior.

**Acceptance Scenarios**:

1. **Given** a user runs `/reforge.audit` with no type argument, **When** the audit executes, **Then** only the existing coverage audit runs, producing only `audit-report.xml` and `correction-plan.xml` — no accuracy or consistency checks are performed and no new report files are generated.
2. **Given** a user runs `/reforge.audit business-rules`, **When** the audit executes, **Then** the existing extraction-type-scoped coverage audit runs unchanged.

---

### Edge Cases

- What happens when extraction XML uses non-standard element names for identifiers? The agent MUST adapt its counting and verification methodology to the actual element names present (consistent with Source-Anchored Generation Constraint 5 from feature 010).
- What happens when a source file referenced in extraction XML has been moved or renamed since extraction? The reference is classified as `failed-missing` with a suggestion to re-run `/reforge.extract`.
- What happens when an identifier exists only as a substring of another token (e.g., "PDFP" matching "PDFPage")? The word-boundary matching (`\b<identifier>\b`) correctly excludes substring matches; if no standalone match exists but the identifier appears as a substring, it is classified as `plausible` (per FR-022 canonical verdicts). If no match of any kind exists, it is classified as `fabricated`.
- What happens when extraction XML has no metadata attributes stating counts? The arithmetic check records `no-metadata` (no stated total to verify against) — not a failure.
- What happens when generated HTML documents cannot be parsed for numeric claims? The freshness check reports `skipped` for that document with a note explaining the parse failure.
- What happens when the source codebase is unavailable during an accuracy audit? The audit aborts with a clear error message stating that source code access is required for accuracy verification.

## Clarifications

### Session 2026-02-22

- Q: FR-002 lists 3 verdict values (`confirmed`, `fabricated`, `suspicious-substring`) while FR-022 lists 5 (`confirmed`, `plausible`, `incorrect`, `fabricated`, `skipped`) — which is canonical? → A: FR-022's 5 verdicts are canonical. `suspicious-substring` is folded into `plausible` as a subcase.
- Q: Can the new audit modes (`accuracy`, `consistency`, `full`) be scoped to a specific extraction type (e.g., `/reforge.audit accuracy business-rules`)? → A: No. New modes are standalone and always audit all extraction types. No combination with scoping arguments.
- Q: When running individual audit modes sequentially, does each overwrite `correction-plan.xml` or use separate files? → A: Separate files. Coverage uses `correction-plan.xml`, accuracy uses `accuracy-correction-plan.xml`, consistency uses `consistency-correction-plan.xml`. The `full` mode merges all into `correction-plan.xml`.
- Q: Should new XML schema definition files be created in `.reforge/schemas/` for the new report types? → A: Yes. Create `accuracy-audit-report.md`, `consistency-audit-report.md`, `full-audit-report.md`, and update `correction-plan.md` with the new types/attributes.
- Q: Does `/reforge.fix` need updating to handle new correction types from accuracy/consistency audits? → A: Minimal update. Add deletion action support for `fabricated` corrections (item removal from extraction XML). Other new types work via the existing `action` attribute mechanism.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The `/reforge.audit` command MUST accept three new type values: `accuracy`, `consistency`, and `full`. These are standalone audit modes that always operate across all extraction types — they cannot be combined with existing scoping arguments (e.g., `business-rules`).
- **FR-002**: The accuracy audit MUST verify each extracted identifier by searching the source codebase using word-boundary matching and classify results using the five canonical verdict values defined in FR-022 (`confirmed`, `plausible`, `incorrect`, `fabricated`, `skipped`). A substring-only match (e.g., identifier found only as part of a longer token) is classified as `plausible`.
- **FR-003**: The accuracy audit MUST verify source file references in extraction XML — confirming the file exists, line numbers are valid, and code snippets match the source (using the `content-match` check type defined in FR-023, which compares extracted text against actual source content with whitespace-insensitive matching).
- **FR-004**: The accuracy audit MUST compute an accuracy score as `(confirmed_items / total_verified_items) * 100` with per-category and per-check-type breakdowns.
- **FR-005**: The accuracy audit MUST generate an `accuracy-audit-report.xml` file with individual verification results, accuracy summary, and actionable recommendations. Its correction entries MUST be written to `accuracy-correction-plan.xml` (separate from the coverage audit's `correction-plan.xml`).
- **FR-006**: The accuracy audit MUST support statistical sampling with a default 20% sample rate, configurable via `--sample-rate`, `--sample-size` (absolute item count that overrides `--sample-rate` when specified), and `--full-verify` flags. Corpora with fewer than 500 items MUST default to full verification (no sampling).
- **FR-007**: When sampling, the accuracy audit MUST use stratified random sampling across extraction categories with proportional representation and report a 95% confidence interval.
- **FR-008**: If any stratum shows accuracy below 90% during sampling, the audit MUST recommend full verification of that stratum.
- **FR-009**: The consistency audit MUST verify arithmetic correctness by comparing stated metadata counts against actual element counts, with zero tolerance for mismatches.
- **FR-010**: The consistency audit MUST validate cross-references by verifying that all referenced files and IDs exist in the extraction corpus.
- **FR-011**: The consistency audit MUST detect duplicate element IDs — within the same file (critical severity), across files in the same category (critical severity), and across categories (info severity).
- **FR-012**: The consistency audit MUST detect stale generated documents by comparing timestamps and numeric claims against current extraction XML data.
- **FR-013**: The consistency audit MUST detect cross-document discrepancies where the same metric is cited with different values across documents.
- **FR-014**: The consistency audit MUST generate a `consistency-audit-report.xml` file with check results organized by category (arithmetic, cross-reference, duplicate-id, freshness, cross-document). Its correction entries MUST be written to `consistency-correction-plan.xml`.
- **FR-015**: The full audit MUST execute coverage, consistency, and accuracy audits in sequence, producing individual reports for each plus a unified `full-audit-report.xml`. The full audit MUST merge all correction entries into a single unified `correction-plan.xml` with each entry tagged by `source-audit-type`.
- **FR-016**: The full audit MUST compute a composite quality score using weights: coverage 25%, consistency 35%, accuracy 40%.
- **FR-017**: The full audit MUST map the composite score to a quality rating (Excellent >= 98%, Good 95-97.9%, Acceptable 90-94.9%, Poor 80-89.9%, Critical < 80%) with corresponding action recommendations.
- **FR-018**: All new audit types MUST generate correction plan entries using the existing `correction-plan.xml` schema, extended with new correction types (`fabricated`, `inaccurate`, `inconsistent`, `broken-ref`, `arithmetic`, `duplicate-id`) and category values (`cross-document`, `metadata`).
- **FR-019**: Each correction plan entry from the new audits MUST include a `source-audit-type` attribute indicating which audit produced it and a `severity` attribute.
- **FR-020**: The default `/reforge.audit` behavior (no type argument) MUST remain unchanged — running only the existing coverage audit.
- **FR-021**: The correction plan schema extensions MUST be additive and non-breaking — existing correction types and categories remain valid.
- **FR-022**: Accuracy audit results MUST use five verdict values: `confirmed`, `plausible`, `incorrect`, `fabricated`, and `skipped`.
- **FR-023**: The accuracy audit MUST support seven check types: `identifier-exists`, `term-exists`, `line-reference`, `content-match`, `expansion-match`, `count-match`, and `relationship-match`.
- **FR-024**: This feature MUST deliver new schema definition files in `.reforge/schemas/`: `accuracy-audit-report.md`, `consistency-audit-report.md`, `full-audit-report.md`. The existing `correction-plan.md` schema MUST be updated with the new correction types (`fabricated`, `inaccurate`, `inconsistent`, `broken-ref`, `arithmetic`, `duplicate-id`), category values (`cross-document`, `metadata`), attributes (`source-audit-type`, `severity`), and child element (`<evidence>`).
- **FR-025**: The `/reforge.fix` command MUST be minimally updated to support deletion actions for `fabricated` correction types (removing fabricated items from extraction XML). All other new correction types (`inaccurate`, `inconsistent`, `broken-ref`, `arithmetic`, `duplicate-id`) are handled by the existing `action` attribute mechanism without fix command changes.

### Key Entities

- **Accuracy Audit Report**: XML document recording individual verification results, sampling metadata, and accuracy scores per category and check type.
- **Consistency Audit Report**: XML document recording arithmetic checks, cross-reference validations, duplicate ID findings, freshness checks, and cross-document discrepancies.
- **Full Audit Report**: XML document aggregating scores from coverage, consistency, and accuracy dimensions into a composite quality score with rating and recommendations.
- **Extended Correction Plan**: Existing correction plan schema extended with new correction types (fabricated, inaccurate, inconsistent, broken-ref, arithmetic, duplicate-id), category values (cross-document, metadata), source-audit-type attribute, severity attribute, and evidence element.
- **Verification Result**: Individual item-level record with verdict, checks performed, confidence score, and optional correction hint.
- **Discrepancy Cluster**: Group of occurrences where the same metric is cited with different values across documents, with recommendation for resolution.

## Assumptions

- The source codebase is available on disk and accessible to the agent during accuracy audits. Accuracy audits cannot run without source code access.
- Extraction XML files follow the common extraction schema (feature 009) with recognizable element names and `id` attributes.
- The agent can use native tools (Read, Glob, Grep) to search the source codebase for identifier verification — no external parsers or compilers are required.
- Generated documents in `$PROJECT_OUTPUT_DIR/generated/` are HTML or markdown files that can be parsed for numeric claims using pattern matching.
- The existing `audit-report.xml` and `correction-plan.xml` schemas are defined in `.reforge/schemas/` and are stable.
- Word-boundary matching (`\b<identifier>\b`) is sufficient for identifier verification in most programming languages. Edge cases (dynamically generated identifiers, metaprogramming) are handled by the `plausible` verdict.
- The 20% default sampling rate provides sufficient statistical power for corpora of 500+ items. Smaller corpora default to full verification.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The accuracy audit detects 100% of fabricated identifiers in a test corpus — verified by running against the TCOS-RUMO pre-audit acronym glossary (12 known fabricated entries) with zero false negatives.
- **SC-002**: The consistency audit detects 100% of arithmetic mismatches where a stated metadata count disagrees with the actual element count — verified by running against known test cases (e.g., "900 FR" vs. actual 981).
- **SC-003**: The consistency audit detects 100% of broken cross-references where a referenced file or ID does not exist — verified against the 3 known broken cross-references in the TCOS-RUMO corpus.
- **SC-004**: The full audit produces a composite quality score that is arithmetically correct (coverage*0.25 + consistency*0.35 + accuracy*0.40) and maps to the correct quality rating.
- **SC-005**: The default `/reforge.audit` (no type argument) produces output identical to the current implementation — verified by diffing output against a baseline run.
- **SC-006**: Statistical sampling at 20% on a 4,636-item corpus produces a confidence interval with margin of error below 3%.
- **SC-007**: All correction plan entries from the new audits include `source-audit-type`, `severity`, and `evidence` attributes, and are compatible with the existing `/reforge.fix` command.
- **SC-008**: The combined audit system detects all 13 verified errors from the TCOS-RUMO failure taxonomy across the three audit dimensions (coverage, consistency, accuracy).
