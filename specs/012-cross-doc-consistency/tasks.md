# Tasks: Cross-Document Consistency Checker

**Input**: Design documents from `/specs/012-cross-doc-consistency/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, quickstart.md

**Tests**: No automated test tasks included. Testing is manual validation via sample legacy codebases and LLM-executed acceptance scenarios per quickstart.md.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

---

## Phase 1: Setup

**Purpose**: Understand existing file structures and conventions before making changes

- [x] T001 Review existing schema conventions in `.reforge/schemas/` and command structure in `.reforge/commands/generate.md` (Canonical Metrics Computation section, Content Validation Checklist) and `.reforge/commands/audit.md` (Consistency Audit Workflow section)

---

## Phase 2: Foundational — Schema Definitions

**Purpose**: Define all data structures before modifying command workflows. MUST be complete before any user story implementation.

- [x] T002 [P] Create metrics registry schema definition in `.reforge/schemas/metrics-registry.md` — define root element (`<metrics-registry>` with `project-id`, `version`, `generated`, `total-metrics`, `source-extractions` attributes), metric entry (`<metric>` with `id`, `category`, `name`, `value`, `unit`, `computation`, `source`, `computed-at` attributes), breakdown (`<breakdown>` with `<component>` children where sum of counts equals metric value), references (`<references>` with `<ref file="" line=""/>`), configuration (`<configuration>` with `<tolerance-defaults>`, `<scan-file-types>`, `<exclusion-list>`), scan patterns (`<scan-patterns>` with `<pattern>` entries having `id`, `description`, `metric-category`, `metric-hint`), and qualifier patterns. Follow existing schema conventions from `audit-report.md` and `correction-plan.md`. Include complete examples with sample data per data-model.md.
- [x] T003 [P] Extend correction plan schema with `metric-mismatch` and `unregistered-metric` CorrectionType values, add `metrics-consistency` CategoryType value (priority: after `cross-document`, before `generation`), add example XML showing metric-mismatch corrections, and update priority assignment rules section in `.reforge/schemas/correction-plan.md`
- [x] T004 [P] Extend consistency audit report schema with `<metrics-registry-checks>` section in `.reforge/schemas/consistency-audit-report.md` — add summary attributes (`total-claims-scanned`, `total-discrepancies`, `critical-count`, `warning-count`, `info-count`, `files-scanned`, `registry-version`), `<discrepancy>` element (with `id`, `severity`, `metric-id`, `registry-value`, `document-value`, `file`, `line`, `context`, `confidence`, `action`, `pattern-id`, `qualifier`, `tolerance-percent` attributes), `<scan-summary>` with per-file and per-metric verification summaries, `<exclusions-applied>` section documenting suppressed patterns, and complete example XML

**Checkpoint**: All schemas defined — user story implementation can begin

---

## Phase 3: User Story 1 — Prevent Contradictory Statistics During Generation (Priority: P1) 🎯 MVP

**Goal**: Ensure all generated documents draw numeric claims from a single authoritative metrics registry, preventing contradictions at the source.

**Independent Test**: Run the generation command against a project with known extraction data and verify: (1) `metrics-registry.xml` is created with correct values, (2) all generated documents contain metric ID annotations, (3) values in documents match registry entries.

### Implementation for User Story 1

- [x] T005 [US1] Modify Canonical Metrics Computation section in `.reforge/commands/generate.md` — change rule 4 from "ephemeral" to "persisted as `$PROJECT_OUTPUT_DIR/metrics-registry.xml` following the metrics-registry schema", add deterministic metric ID generation using `MET-{CATEGORY}-{NAME}` pattern, add breakdown recording for aggregate metrics with per-file components, add registry read-back rule requiring all subsequent generation steps to read metric values from the registry file rather than recomputing them. Handle missing or incomplete extraction data gracefully: report which metrics could not be computed, skip them in the registry, and continue with available data
- [x] T006 [US1] Add Content Validation Checklist item 11 in `.reforge/commands/generate.md` — "Metric ID annotations are present for every numeric statistic as HTML comments (`<!-- metric: MET-XXX -->`) or diagram comments (`' metric: MET-XXX`)"
- [x] T007 [US1] Add Post-Generation Consistency Scan section at end of `.reforge/commands/generate.md` — after all documents are generated, instruct agent to update `<references>` section of each metric in the registry with actual file and line locations, then run a quick scan comparing embedded values against registry values, emit WARNING with discrepancy count and path to consistency report if critical discrepancies found (FR-018: warn but do not block)

**Checkpoint**: User Story 1 complete — generation produces persistent registry and self-validates

---

## Phase 4: User Story 2 — Detect Discrepancies Across Existing Documents (Priority: P1)

**Goal**: Scan all generated documents against the authoritative registry, detect every numeric mismatch, classify severity, and produce actionable correction items.

**Independent Test**: Place documents with known incorrect values alongside a correct registry and verify the scan detects every mismatch, classifies severity correctly (critical for exact mismatches, warning for out-of-tolerance approximates, info for unregistered), applies tolerance for approximate values, and generates correction items.

### Implementation for User Story 2

- [x] T008 [US2] Add registry recomputation step to consistency audit workflow in `.reforge/commands/audit.md` — before any scanning, recompute metrics registry from current extraction data (FR-015) using the same computation approach as generate.md Canonical Metrics Computation but independently executable, write result to `$PROJECT_OUTPUT_DIR/metrics-registry.xml`, ensuring the audit always validates against freshest canonical values regardless of whether a registry file already exists. Handle missing or incomplete extraction data gracefully: report uncomputable metrics and skip them rather than failing the audit
- [x] T009 [US2] Add pattern-based document scanning step to consistency audit workflow in `.reforge/commands/audit.md` — for each file in `$PROJECT_OUTPUT_DIR/generated/` matching configured file types (HTML, Markdown), read contents, apply scan pattern descriptions from the registry to identify numeric claims, match each claim against registry metrics by pattern hint and value proximity, classify as consistent/approximate-match/mismatch/unregistered/ambiguous, for ambiguous matches report all candidate matches with confidence indicator (FR-020)
- [x] T010 [US2] Add tolerance application and exclusion list steps to consistency audit workflow in `.reforge/commands/audit.md` — tolerance: when qualifying language present (approximately, ~, about, roughly, nearly, over, fewer than) apply corresponding tolerance rule from registry configuration with default +/-10% (FR-012), per-metric tolerance overrides take precedence, values without qualifiers require exact match (FR-013); exclusion: before reporting unregistered metrics check exclusion list, skip suppressed patterns, report new unregistered metrics as info-severity (FR-019)
- [x] T011 [US2] Add discrepancy report and correction item generation steps to consistency audit workflow in `.reforge/commands/audit.md` — generate `<metrics-registry-checks>` section of consistency audit report per extended schema (T004) with all discrepancies, per-file scan summaries, per-metric verification summaries, and exclusion application log; generate correction items using `metric-mismatch` type for critical/warning discrepancies and `unregistered-metric` type for non-excluded unregistered metrics (FR-016), set category to `metrics-consistency`
- [x] T012 [US2] Update human-readable audit output display format in `.reforge/commands/audit.md` — add metrics consistency results section showing total claims scanned, discrepancy counts by severity, and summary table of critical mismatches with file, line, expected vs. actual values

**Checkpoint**: User Story 2 complete — audit detects all discrepancies and generates correction items

---

## Phase 5: User Story 3 — Scan Metrics in Diagrams and Graphics (Priority: P2)

**Goal**: Extend the consistency scanner to detect and verify metrics embedded in PlantUML, Mermaid, and SVG files alongside text documents.

**Independent Test**: Create diagram source files (PlantUML `.puml`, Mermaid `.mmd`) and SVG files with known incorrect metric values in titles, labels, and annotations, then verify the scanner detects discrepancies without double-counting metrics in inline SVG within HTML.

### Implementation for User Story 3

- [x] T013 [US3] Add diagram-specific scan pattern descriptions to metrics registry schema in `.reforge/schemas/metrics-registry.md` — add patterns for PlantUML title/note text, Mermaid node/label text, and SVG `<text>` element content; add `puml`, `mmd`, and `svg` entries to `<scan-file-types>` configuration examples with appropriate parser descriptions
- [x] T014 [US3] Add diagram file type scanning instructions to consistency audit workflow in `.reforge/commands/audit.md` — extend pattern-based scanning step (T009) to cover `.puml`, `.mmd`, and `.svg` files using the diagram-specific patterns, scan both `$PROJECT_OUTPUT_DIR/generated/` (recursively) and `$PROJECT_OUTPUT_DIR/diagrams/` (if present) to account for both possible diagram locations, add deduplication rule for inline SVG within HTML reports (detect metric once per location, not double-count from both HTML and embedded SVG scans)
- [x] T015 [P] [US3] Add diagram metric annotation conventions in `.reforge/commands/generate.md` — define PlantUML comment format (`' metric: MET-XXX`), Mermaid comment format (`%% metric: MET-XXX`), and SVG metadata convention for metric traceability in generated diagram files

**Checkpoint**: User Story 3 complete — diagrams and graphics are scanned alongside text documents

---

## Phase 6: User Story 4 — Bootstrap Registry for Existing Projects (Priority: P2)

**Goal**: Enable existing projects without a metrics registry to onboard by having the consistency audit automatically create the registry from extraction data and identify all current discrepancies.

**Independent Test**: Run the consistency audit on a project with generated documents but no `metrics-registry.xml` file and verify the registry is created from current extraction data and all existing document discrepancies are detected and reported as a bootstrap/migration scan.

### Implementation for User Story 4

- [x] T016 [US4] Add bootstrap scenario handling to consistency audit workflow in `.reforge/commands/audit.md` — ensure registry recomputation step (T008) handles absent registry gracefully (create fresh without error), add first-time bootstrap messaging indicating this is a migration scan when no prior registry existed, include guidance in audit output that existing discrepancies represent pre-registry state and can be resolved incrementally via the fix command

**Checkpoint**: User Story 4 complete — existing projects can be onboarded without full regeneration

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: End-to-end validation and cross-cutting integration

- [x] T017 Update full audit workflow composite score to include metrics-consistency dimension in `.reforge/commands/audit.md` — ensure the full audit's consistency dimension incorporates metrics registry check results into the composite score calculation
- [x] T018 Verify end-to-end generate → audit → fix pipeline works with new registry — walk through complete workflow confirming metrics-registry.xml is produced during generation, consumed during audit, and correction plan priority ordering places `metrics-consistency` items correctly relative to other categories. Additionally verify selective regeneration (SC-008): regenerate a single document type while leaving others unchanged and confirm the regenerated document reads values from the existing registry, maintaining consistency with all other documents
- [x] T019 Run quickstart.md validation scenarios against implementation — execute all 5 validation scenarios from quickstart.md and verify expected outcomes match

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup (T001) — BLOCKS all user stories
- **US1 (Phase 3)**: Depends on Foundational — specifically T002 (metrics-registry schema)
- **US2 (Phase 4)**: Depends on Foundational — specifically T002, T003, T004 (all schemas)
- **US3 (Phase 5)**: Depends on US1 (Phase 3) AND US2 (Phase 4) — extends both generate.md and audit.md
- **US4 (Phase 6)**: Depends on US2 (Phase 4) — extends audit workflow
- **Polish (Phase 7)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Phase 2 — modifies only `.reforge/commands/generate.md`
- **User Story 2 (P1)**: Can start after Phase 2 — modifies only `.reforge/commands/audit.md`
- **US1 and US2 CAN proceed in parallel** (different command files: generate.md vs audit.md)
- **User Story 3 (P2)**: Depends on BOTH US1 and US2 — extends scanning in both commands plus schema
- **User Story 4 (P2)**: Depends on US2 only — extends audit workflow

### Within Each User Story

- Schema definitions referenced before command modifications
- Core logic before presentation/formatting
- Self-contained changes that preserve existing functionality

### Parallel Opportunities

- **Phase 2**: T002, T003, T004 can all run in parallel (three different schema files)
- **Phase 3 + Phase 4**: US1 and US2 can run in parallel after foundational phase (generate.md vs audit.md)
- **Phase 5**: T015 can run in parallel with T013/T014 (generate.md vs schema + audit.md)

---

## Parallel Example: Foundational Phase

```bash
# Launch all schema tasks together (different files):
Task: "Create metrics registry schema in .reforge/schemas/metrics-registry.md"     # T002
Task: "Extend correction plan schema in .reforge/schemas/correction-plan.md"        # T003
Task: "Extend audit report schema in .reforge/schemas/consistency-audit-report.md"  # T004
```

## Parallel Example: User Stories 1 & 2

```bash
# After foundational schemas are complete, launch both P1 stories in parallel:

# Developer A: User Story 1 (generate.md)
Task: "Modify Canonical Metrics Computation in .reforge/commands/generate.md"  # T005
Task: "Add Content Validation item 11 in .reforge/commands/generate.md"        # T006
Task: "Add Post-Generation Scan in .reforge/commands/generate.md"              # T007

# Developer B: User Story 2 (audit.md)
Task: "Add registry recomputation in .reforge/commands/audit.md"               # T008
Task: "Add pattern-based scanning in .reforge/commands/audit.md"               # T009
Task: "Add tolerance and exclusion in .reforge/commands/audit.md"              # T010
Task: "Add report and correction generation in .reforge/commands/audit.md"     # T011
Task: "Update display format in .reforge/commands/audit.md"                    # T012
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001)
2. Complete Phase 2: Foundational schemas (T002-T004)
3. Complete Phase 3: User Story 1 — generation produces persistent registry (T005-T007)
4. **STOP and VALIDATE**: Run generation against a test project and verify registry is created with correct values
5. This alone prevents future contradictions in newly generated documents

### Incremental Delivery

1. Setup + Foundational → Schema definitions ready
2. US1 (generate.md) → Registry prevention mechanism live → **MVP!**
3. US2 (audit.md) → Detection of existing discrepancies → Full P1 scope
4. US3 (diagrams) → Diagram scanning → Enhanced coverage
5. US4 (bootstrap) → Existing project onboarding → Complete feature
6. Polish → End-to-end validation → Production ready

### Parallel Team Strategy

1. Team completes Setup + Foundational together
2. Once schemas are defined:
   - Developer A: US1 (generate.md changes) — T005, T006, T007
   - Developer B: US2 (audit.md changes) — T008, T009, T010, T011, T012
3. After both P1 stories complete:
   - Developer A: US3 diagram scanning (generate.md + schema) — T013, T014, T015
   - Developer B: US4 bootstrap (audit.md) — T016
4. Polish phase together — T017, T018, T019

---

## Notes

- [P] tasks = different files, no dependencies on incomplete tasks
- [Story] label maps task to specific user story for traceability
- Each user story is independently completable and testable
- This is a prompt-template-only project — all tasks involve editing markdown files in `.reforge/`
- No compiled code, no external dependencies per Constitution Principle I
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
