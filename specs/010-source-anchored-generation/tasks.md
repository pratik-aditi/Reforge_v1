# Tasks: Source-Anchored Generation

**Input**: Design documents from `/specs/010-source-anchored-generation/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, quickstart.md

**Tests**: Not requested. Validation is manual via 8 test cases defined in spec.md against the TCOS-RUMO dataset.

**Organization**: Tasks are grouped by user story. All changes are prompt template edits (markdown files) -- no compiled code. Primary target file is `.reforge/commands/generate.md` (1009 lines); secondary targets are 5 template files in `.reforge/templates/`.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

## Path Conventions

All paths are relative to repository root. This is a prompt template project -- no `src/` or `tests/` directories.

---

## Phase 1: Setup

**Purpose**: Confirm file structure and insertion points before making changes

- [x] T001 Read `.reforge/commands/generate.md` and confirm all insertion points documented in `specs/010-source-anchored-generation/research.md`: Step 0.5 ends at ~line 75, Markdown Generation section at ~line 128, Selective Regeneration at ~line 975. Document any line number drift from prior feature branches.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Insert the core constraint definition and shared computation sections that ALL user stories depend on

**CRITICAL**: No user story work can begin until this phase is complete

- [x] T002 Insert Step 0.6 "Source-Anchored Generation Constraints" section into `.reforge/commands/generate.md` after the existing Step 0.5 section and before Step 0.7. Content: 7 mandatory constraints covering (1) extraction XML as sole source of truth, (2) no embellishment or paraphrasing beyond extraction data, (3) no LLM training-data contamination, (4) verbatim identifier copying character-for-character, (5) computed totals with derivation formulas, (6) source code boundary -- never read source files directly, (7) when-in-doubt-omit with `[DATA GAP]` markers. Constraints MUST address non-standard XML element names requiring adaptive XPath per spec edge case 1 (the agent adapts counting methodology but MUST still count -- never estimate). Implements FR-001, FR-004, FR-006, FR-007, FR-010. Use "the agent MUST" phrasing per Constitution Principle V. ~60 lines.
- [x] T003 Insert "Canonical Metrics Computation" section into `.reforge/commands/generate.md` before the existing Selective Regeneration section (~line 975). Content: procedure for computing a canonical metrics table at the start of each generation run by counting extraction XML elements. Table structure from `data-model.md`: Metric | Source | Value | Formula columns. Include metrics for total_files, total_modules, total_business_rules, total_functional_reqs, total_nfr, total_ui_components. Specify that the table is recomputed for every run (never reused). Implements FR-002, FR-003, FR-011, FR-012. ~35 lines.
- [x] T004 Insert "Multi-File Extraction Discovery" section into `.reforge/commands/generate.md` immediately after the Canonical Metrics Computation section. Content: mandatory procedure to glob all XML files in each extraction category subdirectory (`business-rules/*.xml`, `functional-requirements/*.xml`, etc.) rather than assuming a single file per type. Sum element counts across all discovered files for canonical metrics. Implements FR-016. ~20 lines.

**Checkpoint**: Foundation ready -- core constraints defined, canonical metrics and multi-file discovery procedures established. User story implementation can now begin.

---

## Phase 3: User Story 1 - Faithful Document Generation (Priority: P1)

**Goal**: Ensure every fact, name, count, and identifier in generated output traces to extraction XML with zero fabrication

**Independent Test**: Run `/reforge.generate markdown` against a known extraction dataset and verify every identifier and statistic in the output traces to an extraction XML element

### Implementation for User Story 1

- [x] T005 [US1] Insert "Content Validation Checklist" section into `.reforge/commands/generate.md` after the Multi-File Extraction Discovery section. Content: 10-item mandatory boolean checklist that the agent MUST complete before finalizing each generated document. Items from `data-model.md`: (1) all numeric totals computed from extraction XML, (2) all identifiers copied verbatim, (3) no unsourced claims, (4) all diagrams verified via Diagram Verification Protocol, (5) consistent cross-references using canonical metrics, (6) partial lists explicitly marked "Showing N of M", (7) no stale data from prior runs, (8) provenance annotations present on every major section, (9) no direct source code reads, (10) `[DATA GAP]` markers for insufficient data. Implements FR-015. ~30 lines.

**Checkpoint**: User Story 1 complete. The Content Validation Checklist is the primary enforcement mechanism for faithful generation. Combined with Step 0.6 constraints, this prevents fabricated identifiers, stale statistics, and unsourced claims.

---

## Phase 4: User Story 2 - Computed Statistics with Formula Transparency (Priority: P1)

**Goal**: Every numeric value is computed by counting extraction XML elements at generation time, with the computation formula visible

**Note**: Core computation infrastructure (Canonical Metrics T003, Multi-File Discovery T004) is delivered in the Foundational phase. This phase adds the template-level specification for formula transparency.

**Independent Test**: Generate a requirements registry from multiple extraction XML files and verify the total equals the sum of per-file element counts, with the formula stated inline

### Implementation for User Story 2

- [x] T006 [US2] Insert "Template Placeholder Specification" subsection into `.reforge/commands/generate.md` within the Markdown Generation section (after ~line 128). Content: typed placeholder reference table specifying how template variables map to extraction XML sources. Each placeholder includes: name, type (count/identifier/description), source XPath, derivation formula requirement. Example: `{{total_requirements}}` → count(`//requirement`) across all `functional-requirements/*.xml` → must show formula "541 + 87 + 85 + 98 + 127 = 938". Implements FR-002, FR-003. ~25 lines.

**Checkpoint**: User Story 2 complete. Canonical Metrics (from Foundational phase) + Template Placeholders ensure all statistics are computed with visible formulas.

---

## Phase 5: User Story 3 - Graceful Gap Handling (Priority: P2)

**Goal**: Emit explicit `[DATA GAP]` markers when extraction data is insufficient, rather than fabricating content

**Independent Test**: Run `/reforge.generate` against deliberately incomplete extraction data and verify `[DATA GAP]` markers appear instead of fabricated content

### Implementation for User Story 3

- [x] T007 [US3] Insert "Extraction Freshness & Gap Reporting" section into `.reforge/commands/generate.md` after the Content Validation Checklist section. Content: (a) mandatory pre-generation check that inspects extraction XML file timestamps -- if any extraction file is older than 7 days, the agent MUST emit a staleness warning at the top of generated output recommending `/reforge.extract` to refresh; (b) gap report trigger -- when 3+ `[DATA GAP]` markers are emitted in a single run, the agent MUST produce a supplementary `gap-report.md` at `reforge_output/<project>/generated/gap-report.md` listing all gaps with recommended extraction commands. Gap report structure from `data-model.md`: `# | Section | Gap Description | Recommended Command`. Implements FR-007, FR-008, FR-017. ~20 lines.

**Checkpoint**: User Story 3 complete. Gap handling and freshness validation ensure missing data is visible, not hidden behind fabrication.

---

## Phase 6: User Story 4 - Diagram Verification Protocol (Priority: P2)

**Goal**: Every generated diagram passes a verification protocol tracing all nodes and edges to extraction XML

**Independent Test**: Generate a PlantUML state machine diagram and verify the verification comment block reports correct node/edge counts with zero unresolved elements

### Implementation for User Story 4

- [x] T008 [US4] Insert "Diagram Verification Protocol" section into `.reforge/commands/generate.md` after the Extraction Freshness & Gap Reporting section. Content: mandatory 6-step protocol applied before generating any diagram (PlantUML, Mermaid, ASCII): (1) node audit -- verify every node/class/state exists in extraction XML, (2) edge audit -- verify every relationship/transition exists in extraction XML, (3) label audit -- verify all labels are verbatim from extraction XML, (4) count consistency -- verify stated count matches rendered element count, (5) completeness check -- if showing subset, explicitly state "Showing N of M items", (6) output verification comment block. Verification log format from `data-model.md`: `' === VERIFICATION LOG === / Source: [file] / Nodes: N verified / Edges: M verified / Omitted: K (justification) / Unresolved: 0 / === END VERIFICATION ===`. Implements FR-009. ~35 lines.

**Checkpoint**: User Story 4 complete. All generated diagrams now include a verification block proving traceability to extraction data.

---

## Phase 7: User Story 5 - Cross-Document Consistency via Canonical Metrics (Priority: P3)

**Goal**: Shared metrics are computed once and referenced consistently across all generated documents

**Independent Test**: Generate three documents in one run and verify all shared metrics are identical across documents

### Implementation for User Story 5

- [x] T009 [US5] Insert "Cross-Extraction Consistency Check" section into `.reforge/commands/generate.md` after the Diagram Verification Protocol section. Content: mandatory pre-generation validation that compares data across multiple extraction files for consistency. Checks: (1) module lists -- same modules referenced across extraction files, (2) file counts -- analysis.xml file count matches sum of module file counts, (3) entity references -- entity names spelled consistently across extractions, (4) identifier spelling -- flag any extraction files that spell the same identifier differently. When inconsistency detected, use the extraction with the most recent audit verification date as authoritative and flag the inconsistency in output. Implements FR-011, FR-018. ~25 lines.

**Checkpoint**: User Story 5 complete. Cross-extraction consistency plus canonical metrics (from Foundational) ensure no two documents disagree on the same fact.

---

## Phase 8: User Story 6 - Extraction Traceability and Provenance (Priority: P3)

**Goal**: Every major section includes provenance annotations citing specific extraction files and element counts

**Independent Test**: Generate a document and verify every major section contains an HTML comment citing its extraction source file(s) with element counts

### Implementation for User Story 6

- [x] T010 [US6] Insert "Output Provenance Annotations" section into `.reforge/commands/generate.md` after the Cross-Extraction Consistency Check section. Content: mandatory requirement that every major section of generated output includes a provenance annotation as an HTML comment citing the extraction file(s) used and element counts. Format: `<!-- Source: extractions/[category]/[filename].xml (N [elements]) -->`. When a section draws from multiple extraction files, list all files. Implements FR-013. ~15 lines.
- [x] T011 [US6] Insert "HTML Report Generation" section into `.reforge/commands/generate.md` after the Output Provenance Annotations section. Content: generation guidance for HTML report output format. Every generated HTML report MUST include a provenance footer listing all extraction source files used with element counts per file. Footer format: table with columns `Extraction File | Element Type | Count | Last Modified`. Include guidance for HTML-specific formatting of provenance annotations, gap markers, staleness warnings, and verification blocks. Implements FR-014. ~30 lines.

**Checkpoint**: User Story 6 complete. Every generated section now carries provenance annotations enabling downstream audit and verification.

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Finalize cross-cutting updates, annotate template files, and validate implementation

- [x] T012 Append 2 new rules to the existing Selective Regeneration section in `.reforge/commands/generate.md`: (1) when selectively regenerating a section, the agent MUST re-verify the regenerated content against the full Content Validation Checklist, (2) the canonical metrics table MUST be recomputed fresh before any selective regeneration (never reuse metrics from a prior run). Implements FR-012, FR-015. ~5 lines.
- [x] T013 [P] Add Source-Anchored Generation reference annotation block after the "Generation Guidelines" section in `.reforge/templates/sysml-block.md`. Content: ~10-line block titled "### Source-Anchored Generation (Mandatory)" referencing Step 0.6 constraints from `generate.md`. List 7 key obligations: extraction XML as sole source, verbatim identifiers, computed statistics with formulas, `[DATA GAP]` markers, provenance annotations, Content Validation Checklist completion, no source code reads. Implements FR-020.
- [x] T014 [P] Add Source-Anchored Generation reference annotation block after the "Generation Notes" section in `.reforge/templates/uml-class.md`. Content: identical ~10-line block as T013. Implements FR-020.
- [x] T015 [P] Add Source-Anchored Generation reference annotation block after the "Story Generation Rules" section in `.reforge/templates/user-story.md`. Content: identical ~10-line block as T013. Implements FR-020.
- [x] T016 [P] Add Source-Anchored Generation reference annotation block after the "Generation Guidelines" section in `.reforge/templates/ascii-layout.md`. Content: identical ~10-line block as T013. Implements FR-020.
- [x] T017 [P] Add Source-Anchored Generation reference annotation block after the "Notes for Agent" section in `.reforge/templates/data-dictionary.md`. Content: identical ~10-line block as T013. Implements FR-020.
- [x] T018 Validate implementation completeness: read `.reforge/commands/generate.md` and confirm all 10 new sections are present with correct section headers in the expected document order (Step 0.6 → Template Placeholders → Canonical Metrics → Multi-File Discovery → Content Validation → Freshness & Gap Reporting → Diagram Verification → Cross-Extraction Consistency → Provenance Annotations → HTML Report Generation → Selective Regeneration update). Confirm all 5 template files contain the annotation block.
- [x] T019 Run quickstart.md validation scenarios: confirm the implementation supports all 7 behaviors listed in `specs/010-source-anchored-generation/quickstart.md` (canonical metrics, verbatim identifiers, derivation formulas, diagram verification, content validation, gap markers, provenance annotations). Additionally, validate SC-008 by confirming the updated framework would prevent all 7 generation-phase errors from the TCOS-RUMO failure taxonomy. Document any discrepancies.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies -- start immediately
- **Foundational (Phase 2)**: Depends on Setup (T001) -- BLOCKS all user stories
- **User Stories (Phases 3-8)**: All depend on Foundational phase completion (T002, T003, T004)
  - US1 (Phase 3): Independent of other stories
  - US2 (Phase 4): Independent of other stories
  - US3 (Phase 5): Independent of other stories
  - US4 (Phase 6): Independent of other stories
  - US5 (Phase 7): Independent of other stories
  - US6 (Phase 8): Independent of other stories
- **Polish (Phase 9)**: T012 depends on T003 (Canonical Metrics) and T005 (Content Validation). T013-T017 depend only on T002 (Step 0.6). T018-T019 depend on all prior tasks.

### Document Ordering Constraint

All verification block sections are inserted into `.reforge/commands/generate.md` before the Selective Regeneration section. The document order MUST be maintained as:

1. Canonical Metrics Computation (T003)
2. Multi-File Extraction Discovery (T004)
3. Content Validation Checklist (T005)
4. Extraction Freshness & Gap Reporting (T007)
5. Diagram Verification Protocol (T008)
6. Cross-Extraction Consistency Check (T009)
7. Output Provenance Annotations (T010)
8. HTML Report Generation (T011)

**Implementation note**: When executing tasks, insert each section using the previous section's header as a text anchor. Execute T003-T004 first (Foundational), then story tasks in T-number order to maintain correct document positioning.

### User Story Dependencies

User stories share a single target file (`.reforge/commands/generate.md`), creating document-ordering dependencies. Each story's section uses the previous section as an insertion anchor. Execute in T-number order.

- **US1 (P1)**: Can start after Foundational (Phase 2). First story in verification block -- no story dependencies.
- **US2 (P1)**: Can start after Foundational (Phase 2). Inserts in Markdown Generation section -- independent of verification block order.
- **US3 (P2)**: Depends on US1 (T005 Content Validation Checklist must exist as insertion anchor).
- **US4 (P2)**: Depends on US3 (T007 Freshness & Gap Reporting section must exist as insertion anchor).
- **US5 (P3)**: Depends on US4 (T008 Diagram Verification Protocol must exist as insertion anchor).
- **US6 (P3)**: Depends on US5 (T009 Cross-Extraction Consistency Check must exist as insertion anchor).

### Within Each User Story

- Read the target file before editing
- Use text anchors (section headers) for insertion, not line numbers
- Verify insertion after each edit
- Follow FR requirements cited in the task description

### Parallel Opportunities

- T013, T014, T015, T016, T017 can ALL run in parallel (different template files)
- User stories are conceptually independent but share the same target file -- execute in T-number order for clean insertions
- T018 and T019 must run after all other tasks complete

---

## Parallel Example: Template Annotations

```bash
# Launch all 5 template annotations together (Phase 9):
Task: "Add Source-Anchored Generation annotation to .reforge/templates/sysml-block.md"
Task: "Add Source-Anchored Generation annotation to .reforge/templates/uml-class.md"
Task: "Add Source-Anchored Generation annotation to .reforge/templates/user-story.md"
Task: "Add Source-Anchored Generation annotation to .reforge/templates/ascii-layout.md"
Task: "Add Source-Anchored Generation annotation to .reforge/templates/data-dictionary.md"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001)
2. Complete Phase 2: Foundational (T002, T003, T004)
3. Complete Phase 3: User Story 1 (T005)
4. **STOP and VALIDATE**: Step 0.6 constraints + Content Validation Checklist are now active. Run `/reforge.generate` against test data to verify zero fabrication.

### Incremental Delivery

1. Setup + Foundational -> Core constraints and metrics in place
2. Add US1 -> Content Validation Checklist active (MVP!)
3. Add US2 -> Template Placeholders add formula transparency
4. Add US3 -> Gap handling and freshness validation active
5. Add US4 -> Diagram verification protocol active
6. Add US5 -> Cross-extraction consistency checks active
7. Add US6 -> Full provenance and traceability
8. Polish -> Template annotations, selective regeneration update, final validation
9. Each story adds a verification layer without breaking previous stories

### Requirement Traceability

| Requirement | Task(s) | User Story |
|-------------|---------|------------|
| FR-001 (sole source of truth) | T002 | Foundational |
| FR-002 (computed statistics) | T003, T006 | US2 |
| FR-003 (derivation formulas) | T003, T006 | US2 |
| FR-004 (verbatim identifiers) | T002 | Foundational |
| FR-005 (complete lists or "N of M") | T005 | US1 |
| FR-006 (no source code reads) | T002 | Foundational |
| FR-007 (gap markers) | T002, T007 | Foundational, US3 |
| FR-008 (gap report at 3+) | T007 | US3 |
| FR-009 (diagram verification) | T008 | US4 |
| FR-010 (no mechanism inference) | T002 | Foundational |
| FR-011 (canonical metrics) | T003, T009 | Foundational, US5 |
| FR-012 (recompute per run) | T003, T012 | Foundational, Polish |
| FR-013 (provenance annotations) | T010 | US6 |
| FR-014 (HTML provenance footer) | T011 | US6 |
| FR-015 (validation checklist) | T005, T012 | US1, Polish |
| FR-016 (multi-file discovery) | T004 | Foundational |
| FR-017 (freshness warning) | T007 | US3 |
| FR-018 (cross-extraction consistency) | T009 | US5 |
| FR-019 (Step 0.6 in generate.md) | T002 | Foundational |
| FR-020 (template annotations) | T013-T017 | Polish |

---

## Notes

- All changes are additive -- no existing content is removed or reordered
- Use "the agent MUST" phrasing throughout (Constitution Principle V)
- Total new content: ~295 lines in generate.md + ~50 lines across 5 templates
- The existing "Optional Validation" section (~line 986) is NOT removed but is superseded by the mandatory Content Validation Checklist
- Commit after each phase completion
- Stop at any checkpoint to validate independently
