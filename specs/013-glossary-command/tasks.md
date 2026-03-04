# Tasks: Glossary Command

**Input**: Design documents from `/specs/013-glossary-command/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, quickstart.md

**Tests**: Not requested — manual validation via sample legacy codebases per plan.md.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Prompt templates**: `.reforge/commands/`
- **Schema definitions**: `.reforge/schemas/`
- **Memory/state**: `.reforge/memory/`
- **Runtime output**: `reforge_output/<project-name>/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Verify existing directory structure and review command template patterns for consistency

- [x] T001 Verify `.reforge/commands/`, `.reforge/schemas/`, and `.reforge/memory/` directories exist; review existing command templates (extract.md, audit.md, generate.md, status.md) for structural patterns, Step 0.7 plan integration, and common-schema extension conventions

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Schema definition that all templates reference — MUST complete before any template writing

**CRITICAL**: No template work can begin until schema is complete

- [x] T002 Create glossary XML schema definition extending common-schema at `.reforge/schemas/glossary.md` — define `<acronym-glossary>` root element, `<entry>` structure (id, term, expansion, confidence, category, verification-status, version-added, version-modified, evidence chain), `<evidence>` structure (file, line-start, line-end, evidence-type, snippet, phase), audit finding structure, checkpoint JSON format, memory lookup JSON format, and version lifecycle (v1.0.0 through v1.3.0) per data-model.md

**Checkpoint**: Schema ready — template implementation can now begin

---

## Phase 3: User Story 1 — Run Full Glossary Extraction (Priority: P1) MVP

**Goal**: End-to-end 4-phase glossary pipeline that produces verified `acronym-glossary.xml`, `glossary-audit-report.xml`, and `.reforge/memory/glossary.json`

**Independent Test**: Run `/reforge.glossary` on an analyzed codebase (with `analysis.xml` present) and verify all 3 output files are produced with valid structure, entries contain required fields, and Phase 3/4 audit findings are documented

### Implementation for User Story 1

- [x] T003 [US1] Create parent orchestrator template at `.reforge/commands/glossary.md` — include command header and purpose, prerequisites check (analysis.xml must exist), basic flag documentation (--phase, --resume, --skip-external, --team-size), default full-pipeline dispatch loop (Phase 1 through 4 sequentially), checkpoint save after each phase to `.reforge/memory/checkpoints/glossary-checkpoint.json`, phase-level progress reporting per FR-025 (start/end with entry counts, elapsed time, verdict summary), memory persistence writing `.reforge/memory/glossary.json` after final phase, checkpoint file cleanup on successful completion, optional team orchestration section with sequential fallback per Constitution Principle V and R-001 (when `--team-size 1` is specified, skip team orchestration entirely and use sequential-only processing), and Step 0.7 project plan integration
- [x] T004 [P] [US1] Create Phase 1 (Pattern Extraction) template at `.reforge/commands/glossary-phase-1.md` — load analysis.xml for file inventory, partition source files into zones for processing, scan for uppercase identifiers (2+ chars), PascalCase prefixes, code comments with parenthetical expansions, doc comments, enum definitions, region labels, string literals, and namespace declarations per FR-004; embed static exclusion list of common programming terms (SQL, XML, JSON, HTTP, HTML, CSS, API, URL, etc.), framework terms, and generic abbreviations per R-007; create initial glossary entries with UNVERIFIED status and evidence chains; deduplicate entries by term keeping highest-confidence with merged evidence per FR-015; output `acronym-glossary.xml` at v1.0.0; include optional parallel zone processing section with sequential fallback
- [x] T005 [P] [US1] Create Phase 2 (External Verification) template at `.reforge/commands/glossary-phase-2.md` — load existing v1.0.0 glossary, iterate entries and use WebSearch tool to look up each acronym against Wikipedia, industry glossaries, and official documentation per FR-007 and R-002; assign verification status (CONFIRMED with confidence boost, CORRECTED with new expansion, UNVERIFIED if no source found, NOT_FOUND if not a recognized acronym); handle batch processing for efficiency; output updated glossary XML at v1.1.0; include graceful degradation instructions when WebSearch tool is unavailable
- [x] T006 [P] [US1] Create Phase 3 (Source Code Audit) template at `.reforge/commands/glossary-phase-3.md` — load current glossary version, for every entry run word-boundary grep (`\bTERM\b`) across all source files per FR-009; reject matches from LLM-authored files (CLAUDE.md, README.md, project-context.md, analysis.xml) per FR-011; mark entries with zero matches as FABRICATED and recommend deletion per FR-010; mark entries where term exists but no explicit expansion found as UNVERIFIED with confidence capped at 0.5 per FR-012; generate audit findings for each entry; write `glossary-audit-report.xml` to `reforge_output/<project>/audit/`; output updated glossary XML at v1.2.0
- [x] T007 [P] [US1] Create Phase 4 (Self-Audit) template at `.reforge/commands/glossary-phase-4.md` — load v1.2.0 glossary and audit report, independently re-verify all entries modified in Phase 3 and all entries with confidence below 1.0 per FR-013; independently re-run word-boundary grep to validate occurrence counts per FR-014; update audit findings with Phase 4 verdicts; apply final corrections (remove FABRICATED entries, update confidence scores); output final glossary XML at v1.3.0; update audit report with Phase 4 findings; signal orchestrator to persist memory and report final summary

**Checkpoint**: At this point, `/reforge.glossary` with default flags should work end-to-end producing all output files

---

## Phase 4: User Story 2 — Run Individual Phases Independently (Priority: P2)

**Goal**: Operator can run a single phase via `--phase N` without re-running earlier phases

**Independent Test**: Run Phase 1 first, then run `/reforge.glossary --phase 3` alone and verify it processes existing glossary without re-extracting

### Implementation for User Story 2

- [x] T008 [US2] Add --phase N single-phase dispatch logic to orchestrator in `.reforge/commands/glossary.md` — when --phase is specified, validate that prerequisite phases have completed by checking glossary XML version (Phase 2 requires v1.0.0+, Phase 3 requires v1.0.0+ if Phase 2 was skipped or v1.1.0+ otherwise, Phase 4 requires v1.2.0+); report clear error with instruction to run missing prerequisite phase when validation fails per acceptance scenario 2; load existing glossary state before executing only the requested phase; save checkpoint and report progress for the single executed phase

**Checkpoint**: `/reforge.glossary --phase 3` correctly processes existing Phase 1 output without re-extraction

---

## Phase 5: User Story 3 — Resume After Interruption (Priority: P2)

**Goal**: Operator can resume from the last completed phase checkpoint without re-processing finished phases

**Independent Test**: Run Phase 1, simulate interruption during Phase 2, then run `/reforge.glossary --resume` and verify Phase 1 results are preserved and Phase 2 restarts

### Implementation for User Story 3

- [x] T009 [US3] Add --resume checkpoint loading and dispatch logic to orchestrator in `.reforge/commands/glossary.md` — when --resume is specified, load `.reforge/memory/checkpoints/glossary-checkpoint.json`, determine next incomplete phase from `last-completed-phase` field, skip all completed phases, resume from beginning of next phase (not mid-phase per R-006); report error with offer to start from Phase 1 when no checkpoint file exists per acceptance scenario 2; preserve all existing glossary data from completed phases

**Checkpoint**: `--resume` correctly picks up from last completed phase

---

## Phase 6: User Story 4 — Cross-Command Glossary Consumption (Priority: P3)

**Goal**: Other Reforge commands automatically consume glossary from memory when available and gracefully degrade when absent

**Independent Test**: Create a glossary, then run `/reforge.generate` and verify acronym expansion on first occurrence per section and glossary appendix

### Implementation for User Story 4

- [x] T010 [P] [US4] Add glossary consumption section to `.reforge/commands/generate.md` — load `.reforge/memory/glossary.json` if it exists, expand acronyms on first occurrence in each document section as "TERM (Full Expansion)" with subsequent occurrences using "TERM" only per FR-024, add glossary appendix to generated documentation, skip gracefully with no errors if glossary file is absent per FR-023
- [x] T011 [P] [US4] Add glossary annotation section to `.reforge/commands/extract.md` — load `.reforge/memory/glossary.json` if it exists, annotate extracted items with full terminology where acronyms match glossary entries per FR-022, skip gracefully if no glossary file per FR-023
- [x] T012 [P] [US4] Add glossary verification targets to `.reforge/commands/audit.md` — load `.reforge/memory/glossary.json` if it exists, use glossary terms as verification targets during audit per FR-022, skip gracefully if no glossary file per FR-023
- [x] T013 [P] [US4] Add glossary status reporting to `.reforge/commands/status.md` — load `.reforge/memory/glossary.json` if it exists, report glossary version and entry count in status output per FR-022, skip gracefully if no glossary file per FR-023

**Checkpoint**: All four existing commands integrate with glossary when available and produce no errors when absent

---

## Phase 7: User Story 5 — Air-Gapped Environment Support (Priority: P3)

**Goal**: `--skip-external` skips Phase 2 while completing all other phases with correct versioning

**Independent Test**: Run `/reforge.glossary --skip-external` and verify Phases 1, 3, 4 complete with versions v1.0.0, v1.2.0, v1.3.0 (skipping v1.1.0)

### Implementation for User Story 5

- [x] T014 [US5] Add --skip-external flag handling to orchestrator in `.reforge/commands/glossary.md` — when --skip-external is specified, skip Phase 2 dispatch entirely per FR-008, adjust version progression to v1.0.0 → v1.2.0 → v1.3.0 (skipping v1.1.0), record Phase 2 in `phases-skipped` array of checkpoint, update Phase 3 prerequisite validation to accept v1.0.0 when Phase 2 was skipped

**Checkpoint**: Air-gapped workflow produces valid glossary without Phase 2

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Framework integration, documentation updates, and final validation

- [x] T015 [P] Update constitution directory listing in `.reforge/memory/constitution.md` to add glossary.md under commands/ and glossary.md under schemas/ in Framework Architecture section
- [x] T016 [P] Update CLAUDE.md commands list to include `/reforge.glossary` with description, and update Active Technologies section with glossary-specific technologies (013-glossary-command)
- [x] T017 Validate implementation against all quickstart.md usage scenarios in `specs/013-glossary-command/quickstart.md` — verify full pipeline, --skip-external, --phase N, --resume, and --team-size flag behaviors are correctly documented in templates

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup — BLOCKS all template writing
- **US1 (Phase 3)**: Depends on Foundational (schema must exist before templates reference it)
- **US2 (Phase 4)**: Depends on US1 T003 (modifies orchestrator created in T003)
- **US3 (Phase 5)**: Depends on US1 T003 (modifies orchestrator created in T003)
- **US4 (Phase 6)**: Depends on Foundational only (modifies existing command files, needs schema for glossary.json format) — CAN run in parallel with US1
- **US5 (Phase 7)**: Depends on US1 T003 (modifies orchestrator created in T003)
- **Polish (Phase 8)**: Depends on all user stories being complete

### User Story Dependencies

- **US1 (P1)**: Can start after Foundational (Phase 2) — No dependencies on other stories
- **US2 (P2)**: Depends on US1 T003 (orchestrator must exist) — Modifies `.reforge/commands/glossary.md`
- **US3 (P2)**: Depends on US1 T003 (orchestrator must exist) — Modifies `.reforge/commands/glossary.md`
- **US4 (P3)**: Can start after Foundational (Phase 2) — Independent of US1 (modifies different files)
- **US5 (P3)**: Depends on US1 T003 (orchestrator must exist) — Modifies `.reforge/commands/glossary.md`

### Within User Story 1

- T003 (orchestrator) FIRST — creates the dispatch structure phase templates reference
- T004, T005, T006, T007 can run in parallel after T003 (different files, no dependencies)

### Parallel Opportunities

- T004, T005, T006, T007 — all phase templates can be written in parallel (different files)
- T010, T011, T012, T013 — all cross-command modifications can be done in parallel (different files)
- T015, T016 — documentation updates can run in parallel
- US4 (Phase 6) can run in parallel with US1 (Phase 3) since they modify different files

---

## Parallel Example: User Story 1

```bash
# After T003 (orchestrator) completes, launch all phase templates in parallel:
Task: "Create Phase 1 template in .reforge/commands/glossary-phase-1.md"
Task: "Create Phase 2 template in .reforge/commands/glossary-phase-2.md"
Task: "Create Phase 3 template in .reforge/commands/glossary-phase-3.md"
Task: "Create Phase 4 template in .reforge/commands/glossary-phase-4.md"
```

## Parallel Example: User Story 4

```bash
# After schema (T002) completes, all cross-command modifications in parallel:
Task: "Add glossary consumption to .reforge/commands/generate.md"
Task: "Add glossary annotation to .reforge/commands/extract.md"
Task: "Add glossary verification to .reforge/commands/audit.md"
Task: "Add glossary status to .reforge/commands/status.md"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001)
2. Complete Phase 2: Foundational schema (T002)
3. Complete Phase 3: US1 — orchestrator + 4 phase templates (T003-T007)
4. **STOP and VALIDATE**: Test full pipeline on a sample codebase
5. The glossary command is fully functional at this point

### Incremental Delivery

1. Complete Setup + Foundational → Schema ready
2. Add US1 → Full pipeline works → **MVP!**
3. Add US2 → Per-phase execution works
4. Add US3 → Resume from checkpoint works
5. Add US4 → Other commands consume glossary
6. Add US5 → Air-gapped environments supported
7. Polish → Framework fully integrated

### Parallel Team Strategy

With multiple developers:

1. All complete Setup + Foundational together
2. Once Foundational is done:
   - Developer A: US1 (orchestrator + phase templates)
   - Developer B: US4 (cross-command consumption — independent of orchestrator)
3. After US1 orchestrator (T003) is done:
   - Developer A: US2 + US3 + US5 (all modify orchestrator)
   - Developer B: continues US4 if not finished
4. Polish phase after all stories complete

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- This is a prompt template project — all "implementation" is writing markdown files
- No automated tests — validation is manual per plan.md
- The orchestrator file (`.reforge/commands/glossary.md`) is modified by US1, US2, US3, and US5 — these MUST be sequential
- US4 modifies existing command files and CAN run in parallel with US1
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
