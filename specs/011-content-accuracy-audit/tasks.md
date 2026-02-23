# Tasks: Content Accuracy Audit

**Input**: Design documents from `/specs/011-content-accuracy-audit/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, quickstart.md

**Tests**: No automated test tasks — testing is manual validation via 8 success criteria run against the TCOS-RUMO dataset.

**Organization**: Tasks grouped by user story. US4 (Statistical Sampling) is embedded in US1 (Accuracy Audit) since sampling is part of the accuracy workflow. US5 (Backward Compatibility) is a verification task in the Polish phase.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

All paths are relative to repository root. This project modifies prompt template files under `.reforge/`.

---

## Phase 1: Setup

**Purpose**: No project initialization needed — this is a prompt template project with existing structure. Setup consists of confirming insertion points.

- [x] T001 Read existing `.reforge/commands/audit.md` to confirm insertion points documented in plan.md Change Map (Step 1.5 at ~line 123, after Step 7 at ~line 396)

---

## Phase 2: Foundational (Schemas + Routing)

**Purpose**: Create output schemas and extend the audit command's type routing. MUST complete before any user story workflow can be written.

**CRITICAL**: No user story work can begin until this phase is complete.

### Schema Definitions

- [x] T002 [P] Create accuracy audit report schema in `.reforge/schemas/accuracy-audit-report.md` based on data-model.md Accuracy Audit Report section (root element, attributes, sampling-metadata, accuracy-summary, verification-results, recommendations)
- [x] T003 [P] Create consistency audit report schema in `.reforge/schemas/consistency-audit-report.md` based on data-model.md Consistency Audit Report section (root element, attributes, arithmetic-checks, cross-reference-checks, duplicate-id-checks, freshness-checks, cross-document-checks)
- [x] T004 [P] Create full audit report schema in `.reforge/schemas/full-audit-report.md` based on data-model.md Full Audit Report section (root element, dimension-scores, quality-assessment, correction-summary, quality rating thresholds)
- [x] T005 Update correction plan schema in `.reforge/schemas/correction-plan.md` — add 6 new CorrectionType values (fabricated, inaccurate, inconsistent, broken-ref, arithmetic, duplicate-id), 2 new CategoryType values (cross-document, metadata), new attributes (source-audit-type, severity), new `<evidence>` child element, updated priority order, and fabricated correction example

### Command Routing

- [x] T006 Extend Step 1.5 type argument validation in `.reforge/commands/audit.md` to accept `accuracy`, `consistency`, and `full` as valid standalone audit modes (not combinable with existing scoping types)
- [x] T007 Insert audit mode routing section after Step 1.5 in `.reforge/commands/audit.md` — dispatch to accuracy workflow, consistency workflow, or full workflow based on type argument; existing types continue to the coverage workflow unchanged

**Checkpoint**: Schemas defined, routing in place. Audit command accepts new type values and routes to placeholder workflow sections.

---

## Phase 3: User Story 1 — Accuracy Audit Detects Fabricated Content (Priority: P1) + User Story 4 — Statistical Sampling (Priority: P2) MVP

**Goal**: The accuracy audit verifies extraction items against the source codebase, detecting fabricated identifiers, incorrect references, and hallucinated content. For large corpora, statistical sampling provides high-confidence assessment without full verification.

**Independent Test**: Run `/reforge.audit accuracy` against TCOS-RUMO pre-audit acronym glossary with 12 known fabricated entries. Verify all 12 flagged as fabricated with zero false negatives. For sampling: verify 20% sample with 95% CI on 4,636-item corpus.

### Implementation for User Story 1 + 4

- [x] T008 [US1] Insert accuracy audit prerequisites section in `.reforge/commands/audit.md` — source codebase availability check, abort with error if source unavailable, `$SOURCE_ROOT` variable resolution
- [x] T009 [US1] Insert extraction item enumeration workflow in accuracy audit section of `.reforge/commands/audit.md` — read all extraction files from `$EXTRACTIONS_DIR`, collect items with IDs, categorize by extraction type, count totals per category
- [x] T010 [US1] Insert statistical sampling logic in accuracy audit section of `.reforge/commands/audit.md` — stratified random sampling at 20% default, `--sample-rate`/`--sample-size`/`--full-verify` flag handling, minimum 5 items per stratum, systematic Nth-item selection, corpus <500 items defaults to full verification (FR-006, FR-007)
- [x] T011 [US1] Insert multi-check-type verification methodology in accuracy audit section of `.reforge/commands/audit.md` — 7 check types (identifier-exists, term-exists, line-reference, content-match, expansion-match, count-match, relationship-match) with agent instructions for each using Grep/Read tools, check type selection logic per item type (FR-023)
- [x] T012 [US1] Insert verdict classification rules in accuracy audit section of `.reforge/commands/audit.md` — 5 canonical verdicts (confirmed, plausible, incorrect, fabricated, skipped) with decision criteria for each, substring-only match → plausible (FR-022, FR-002)
- [x] T013 [US1] Insert accuracy score computation in accuracy audit section of `.reforge/commands/audit.md` — overall score formula (confirmed/verified*100), per-category breakdown, per-check-type breakdown, confidence interval calculation for sampling (95% CI formula), stratum <90% accuracy flagging (FR-004, FR-007, FR-008)
- [x] T014 [US1] Insert accuracy-audit-report.xml generation instructions in accuracy audit section of `.reforge/commands/audit.md` — XML structure per `.reforge/schemas/accuracy-audit-report.md`, write to `$AUDIT_DIR/accuracy-audit-report.xml` (FR-005)
- [x] T015 [US1] Insert accuracy-correction-plan.xml generation instructions in accuracy audit section of `.reforge/commands/audit.md` — correction entries for fabricated/incorrect items using extended schema, write to `$AUDIT_DIR/accuracy-correction-plan.xml`, deletion action format for fabricated items (FR-005, FR-018, FR-019)
- [x] T016 [US1] Insert accuracy audit display results section in `.reforge/commands/audit.md` — human-readable output showing accuracy score, per-category breakdown, sampling metadata (if applicable), verdict summary, top findings, next steps
- [x] T017 [P] [US1] Add deletion action dispatch for fabricated corrections in Step 3c of `.reforge/commands/fix.md` — new case for `type="fabricated"` that reads extraction XML, locates element by ID, removes it, updates `<metadata>/<total-count>` (FR-025)
- [x] T018 [P] [US1] Add deletion verification case in Step 4 of `.reforge/commands/fix.md` — confirm element no longer present after deletion, verify metadata count decremented (FR-025)

**Checkpoint**: Accuracy audit fully functional. Running `/reforge.audit accuracy` verifies extraction items against source, produces `accuracy-audit-report.xml` and `accuracy-correction-plan.xml`. Sampling works for large corpora. `/reforge.fix` can delete fabricated items.

---

## Phase 4: User Story 2 — Consistency Audit Detects Contradictions and Staleness (Priority: P1)

**Goal**: The consistency audit detects arithmetic errors, broken cross-references, duplicate IDs, stale generated documents, and cross-document discrepancies within the extraction corpus and generated output.

**Independent Test**: Run `/reforge.audit consistency` against corpus with known arithmetic mismatches (e.g., "900 FR" vs actual 981), 3 broken cross-references, and stale file counts. Verify all issues detected.

### Implementation for User Story 2

- [x] T019 [US2] Insert arithmetic checks section in consistency audit workflow of `.reforge/commands/audit.md` — compare `<metadata>/<total-count>` and `confidence-distribution` sums against actual child element counts per extraction file, zero tolerance, `no-metadata` handling for files without count attributes (FR-009)
- [x] T020 [US2] Insert cross-reference validation section in consistency audit workflow of `.reforge/commands/audit.md` — verify `<cross-ref target="...">` resolves to existing files, verify `<source file="...">` files exist on disk, verify ID references resolve within corpus (FR-010)
- [x] T021 [US2] Insert duplicate ID detection section in consistency audit workflow of `.reforge/commands/audit.md` — collect all `id` attributes across extraction files, detect within-file duplicates (critical), within-category duplicates (critical), cross-category duplicates (info) (FR-011)
- [x] T022 [US2] Insert freshness checks section in consistency audit workflow of `.reforge/commands/audit.md` — compare extraction `generated` timestamps against generated document timestamps, compare numeric claims in generated docs against current extraction XML counts, `skipped` for unparseable documents (FR-012)
- [x] T023 [US2] Insert cross-document discrepancy detection section in consistency audit workflow of `.reforge/commands/audit.md` — scan generated documents for numeric claims about same metric, cluster occurrences with different values, generate resolution recommendations (FR-013)
- [x] T024 [US2] Insert consistency score computation in consistency audit workflow of `.reforge/commands/audit.md` — (passed_checks / total_checks) * 100 with per-category breakdown
- [x] T025 [US2] Insert consistency-audit-report.xml generation instructions in consistency audit workflow of `.reforge/commands/audit.md` — XML structure per `.reforge/schemas/consistency-audit-report.md`, write to `$AUDIT_DIR/consistency-audit-report.xml` (FR-014)
- [x] T026 [US2] Insert consistency-correction-plan.xml generation instructions in consistency audit workflow of `.reforge/commands/audit.md` — correction entries for inconsistencies using extended schema, write to `$AUDIT_DIR/consistency-correction-plan.xml` (FR-014, FR-018, FR-019)
- [x] T027 [US2] Insert consistency audit display results section in `.reforge/commands/audit.md` — human-readable output showing consistency score, per-category breakdown (arithmetic, cross-reference, duplicate-id, freshness, cross-document), top findings, next steps

**Checkpoint**: Consistency audit fully functional. Running `/reforge.audit consistency` checks internal consistency, produces `consistency-audit-report.xml` and `consistency-correction-plan.xml`.

---

## Phase 5: User Story 3 — Full Audit Provides Unified Quality Assessment (Priority: P2)

**Goal**: A single `/reforge.audit full` command runs coverage, consistency, and accuracy audits in sequence, producing a unified quality score and merged correction plan.

**Independent Test**: Run `/reforge.audit full` against TCOS-RUMO corpus. Verify 4 report files generated, composite score arithmetically correct (coverage*0.25 + consistency*0.35 + accuracy*0.40), merged correction plan contains entries from all 3 audit types.

**Dependencies**: Requires Phase 3 (US1 accuracy workflow) and Phase 4 (US2 consistency workflow) complete.

### Implementation for User Story 3

- [x] T028 [US3] Insert full audit sequential execution orchestration in `.reforge/commands/audit.md` — run existing coverage audit (Steps 1-7), then consistency workflow, then accuracy workflow in sequence, collect scores from each (FR-015)
- [x] T029 [US3] Insert composite score computation and quality rating mapping in full audit section of `.reforge/commands/audit.md` — weighted formula (coverage*0.25 + consistency*0.35 + accuracy*0.40), rating thresholds (Excellent >=98%, Good 95-97.9%, Acceptable 90-94.9%, Poor 80-89.9%, Critical <80%), action recommendations per rating (FR-016, FR-017)
- [x] T030 [US3] Insert correction plan merging logic in full audit section of `.reforge/commands/audit.md` — read all 3 individual correction plans (IMPORTANT: read coverage's `correction-plan.xml` into memory before overwriting), merge into unified `$AUDIT_DIR/correction-plan.xml`, tag each entry with `source-audit-type`, prioritize by category order (analysis → extraction → metadata → cross-document → generation) (FR-015, FR-019)
- [x] T031 [US3] Insert full-audit-report.xml generation instructions in full audit section of `.reforge/commands/audit.md` — XML structure per `.reforge/schemas/full-audit-report.md`, write to `$AUDIT_DIR/full-audit-report.xml` (FR-015)
- [x] T032 [US3] Insert full audit display results section in `.reforge/commands/audit.md` — human-readable output showing all 3 dimension scores, composite score, quality rating, action recommendation, correction plan summary by source, next steps

**Checkpoint**: Full audit orchestration complete. Running `/reforge.audit full` produces individual reports + unified report + merged correction plan.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Backward compatibility verification (US5), language compliance, and final validation.

- [x] T033 [US5] Verify existing Steps 0-7 in `.reforge/commands/audit.md` are unmodified — diff the Steps 0 through Step 7 / Display Results sections against the pre-feature baseline to confirm no changes to default coverage audit behavior (FR-020)
- [x] T034 [US5] Verify that running `/reforge.audit` with no type argument routes exclusively to the existing coverage workflow and produces only `audit-report.xml` and `correction-plan.xml` — no accuracy/consistency reports generated (FR-020)
- [x] T035 Verify all new prompt text in `.reforge/commands/audit.md` and `.reforge/commands/fix.md` uses agent-agnostic language ("the agent MUST", not agent-specific names) per Constitution Principle V
- [x] T036 Verify cross-references between `.reforge/commands/audit.md` and all schema files in `.reforge/schemas/` — confirm report XML structures in command template match schema definitions exactly
- [x] T037 Run quickstart.md validation — confirm all command examples, output file names, and behavioral descriptions in `specs/011-content-accuracy-audit/quickstart.md` match the implemented command

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 — BLOCKS all user stories
- **US1+US4 (Phase 3)**: Depends on Phase 2 (schemas + routing)
- **US2 (Phase 4)**: Depends on Phase 2 (schemas + routing) — can proceed in parallel with Phase 3
- **US3 (Phase 5)**: Depends on Phase 3 AND Phase 4 (full audit orchestrates accuracy + consistency)
- **Polish (Phase 6)**: Depends on Phases 3, 4, 5

### User Story Dependencies

```
Phase 2 (Foundational)
├── Phase 3: US1+US4 Accuracy Audit ──┐
│                                     ├── Phase 5: US3 Full Audit ── Phase 6: Polish
├── Phase 4: US2 Consistency Audit ───┘
│
└── Phase 3 T017/T018 (fix.md) ── parallel with audit.md work
```

- **US1+US4 (P1)**: Can start after Foundational — no dependency on US2
- **US2 (P1)**: Can start after Foundational — no dependency on US1
- **US3 (P2)**: Depends on US1 AND US2 (orchestrates both)
- **US5 (P1)**: Verified in Polish phase after all modifications complete

### Within Each User Story

- Prerequisites/setup before verification logic
- Verification methodology before score computation
- Score computation before report generation
- Report generation before display results
- Core workflow before correction plan generation

### Parallel Opportunities

- T002, T003, T004: All schema files can be written in parallel (different files)
- T017, T018: Fix command tasks can run in parallel with audit.md tasks (different file)
- Phase 3 and Phase 4: Accuracy and consistency workflows can be drafted in parallel (different sections of audit.md, but same file — coordinate insertion points)

---

## Parallel Example: Foundational Phase

```
# Launch all schema definition tasks together (different files):
T002: Create accuracy-audit-report.md in .reforge/schemas/
T003: Create consistency-audit-report.md in .reforge/schemas/
T004: Create full-audit-report.md in .reforge/schemas/

# Then sequentially (same file):
T005: Update correction-plan.md
T006: Extend Step 1.5 in audit.md
T007: Insert routing section in audit.md
```

## Parallel Example: US1 Accuracy Audit

```
# Main accuracy workflow (sequential within audit.md):
T008 → T009 → T010 → T011 → T012 → T013 → T014 → T015 → T016

# In parallel with the above (different file — fix.md):
T017: Add deletion action dispatch in fix.md
T018: Add deletion verification in fix.md
```

---

## Implementation Strategy

### MVP First (User Story 1 + User Story 4)

1. Complete Phase 1: Setup (confirm insertion points)
2. Complete Phase 2: Foundational (schemas + routing)
3. Complete Phase 3: US1+US4 (accuracy audit with sampling)
4. **STOP and VALIDATE**: Test accuracy audit against TCOS-RUMO dataset (SC-001, SC-006)
5. Deliver accuracy audit as standalone capability

### Incremental Delivery

1. Setup + Foundational → Schemas and routing ready
2. Add US1+US4 → Accuracy audit functional → Validate (MVP!)
3. Add US2 → Consistency audit functional → Validate (SC-002, SC-003)
4. Add US3 → Full audit orchestration → Validate (SC-004, SC-008)
5. Polish → Backward compatibility verified (SC-005), cross-cutting validation
6. Each phase adds value without breaking previous phases

### Parallel Team Strategy

With multiple contributors:

1. Complete Setup + Foundational together
2. Once Foundational is done:
   - Contributor A: US1+US4 (accuracy audit in audit.md + fix.md)
   - Contributor B: US2 (consistency audit in audit.md — different section)
3. After both complete: US3 (full audit orchestration)
4. Final pass: US5 verification + polish

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- All tasks in Phases 3-5 modify `.reforge/commands/audit.md` — coordinate insertion points to avoid conflicts
- Tasks T017-T018 modify `.reforge/commands/fix.md` and can run in parallel with audit.md tasks
- No test tasks generated — testing is manual validation per spec success criteria
- Commit after each phase completion for clean rollback points
