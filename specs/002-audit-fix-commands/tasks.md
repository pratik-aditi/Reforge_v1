# Tasks: Audit and Fix Commands

**Input**: Design documents from `/specs/002-audit-fix-commands/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- All framework files live under `.reforge/`
- Command templates: `.reforge/commands/<name>.md`
- Schema docs: `.reforge/schemas/<name>.md`
- Scripts: `.reforge/scripts/bash/<name>.sh`
- Runtime output: `reforge_output/<project>/audit/`

---

## Phase 1: Setup

**Purpose**: Verify existing structure and prepare supporting infrastructure

- [x] T001 Verify `.reforge/commands/` and `.reforge/schemas/` directories exist and contain existing command/schema files
- [x] T002 Update `.reforge/scripts/bash/check-prerequisites.sh` to support `--require-audit` flag that verifies `correction-plan.xml` exists in the project audit directory

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Create XML schema documentation that both command templates will reference

**CRITICAL**: Command templates reference these schemas — they must be complete first

- [x] T003 [P] Create audit report schema documentation in `.reforge/schemas/audit-report.md` defining the XML structure for `audit-report.xml` (root element, coverage-by-type, uncovered-files, stale-references per data-model.md and contracts/audit-report.xsd)
- [x] T004 [P] Create correction plan schema documentation in `.reforge/schemas/correction-plan.md` defining the XML structure for `correction-plan.xml` (root element, correction items with id/priority/type/category/status/action/affected-files per data-model.md and contracts/correction-plan.xsd)

**Checkpoint**: Schema documentation ready — command templates can now reference defined output structures

---

## Phase 3: User Story 1 + User Story 3 - Full Coverage Audit with Correction Plan (Priority: P1+P2) MVP

**Goal**: Users can run `/reforge.audit` to get a coverage report and actionable correction plan

**Independent Test**: Run the audit command after a completed analysis+extraction cycle; verify it produces audit-report.xml with coverage percentage and correction-plan.xml with prioritized items

### Implementation for User Story 1 + 3

- [x] T005 [US1] Create `.reforge/commands/audit.md` with command header: syntax block (`/reforge.audit [type] [--json]`), arguments table, overview section, and prerequisites section (requires completed analysis)
- [x] T006 [US1] Add Step 0 to `.reforge/commands/audit.md`: Initialize project using `check-prerequisites.sh --json --require-analysis`, resolve `$PROJECT_OUTPUT_DIR`, `$ANALYSIS_DIR`, `$EXTRACTIONS_DIR`, create `$AUDIT_DIR = $PROJECT_OUTPUT_DIR/audit`
- [x] T007 [US1] Add Step 0.5 to `.reforge/commands/audit.md`: Load project context from `.reforge/memory/project-context.md` if exists
- [x] T008 [US1] Add Step 1 to `.reforge/commands/audit.md`: Read analysis inventory — read `$ANALYSIS_DIR/analysis.xml`, extract all file paths from `<file>` elements, then read exclusion patterns from `$CONFIG` (config.json `analysis.exclusions` array) and remove matching files from the audit scope; build the final analyzed file list used for coverage calculation
- [x] T009 [US1] Add Step 2 to `.reforge/commands/audit.md`: Read extraction references — for each extraction file (business-rules.xml, database.xml, ui-flows.xml, workflows.xml) in `$EXTRACTIONS_DIR`, extract all `<source file="...">` attributes to build the set of files referenced by extractions
- [x] T010 [US1] Add Step 3 to `.reforge/commands/audit.md`: Calculate coverage — compute set difference (analyzed files minus referenced files) to identify uncovered files, calculate coverage percentage using formula from research.md Decision 6
- [x] T011 [US1] Add Step 4 to `.reforge/commands/audit.md`: Check stale references — for each extraction source reference, verify the referenced file still exists in analysis.xml and on disk (check file path validity), classify issues as "missing" or "modified"
- [x] T012 [US3] Add Step 5 to `.reforge/commands/audit.md`: Generate correction plan — for each uncovered file create a "gap" correction item, for each stale reference create a "stale" correction item, assign priorities (analysis > extraction > generation), assign recommended actions (`/reforge.reanalyze` for stale, `/reforge.extract` for gaps), write `correction-plan.xml` to `$AUDIT_DIR`
- [x] T013 [US1] Add Step 6 to `.reforge/commands/audit.md`: Generate audit report — assemble `audit-report.xml` with all coverage statistics, per-type breakdown, uncovered file list, and stale reference list per schema; write to `$AUDIT_DIR`
- [x] T014 [US1] Add Step 7 to `.reforge/commands/audit.md`: Display results — standard human-readable output format showing coverage percentage, uncovered file count, stale reference count, and correction plan summary (following status.md report pattern)
- [x] T015 [US1] Add JSON output section to `.reforge/commands/audit.md`: When `--json` flag provided, output structured JSON with all audit statistics (following status.md JSON output pattern)
- [x] T016 [US3] Add correction plan display section to `.reforge/commands/audit.md`: After audit report, display correction plan summary with item count by priority and category, and next-steps guidance (`Run /reforge.fix to execute corrections`)
- [x] T017 [US1] Add error handling section to `.reforge/commands/audit.md`: Handle missing analysis (suggest `/reforge.analyze`), missing extractions (warn partial audit), file access errors, and empty analysis scenarios
- [x] T018 [US1] Add examples section to `.reforge/commands/audit.md`: Include examples for full audit with coverage gaps found, full audit with 100% coverage, and audit with stale references

**Checkpoint**: `/reforge.audit` command is fully functional — produces coverage report and correction plan

---

## Phase 4: User Story 4 - Execute Corrections (Priority: P1)

**Goal**: Users can run `/reforge.fix` to automatically execute corrections from the plan

**Independent Test**: Generate a correction plan via audit, run the fix command, verify corrections executed in dependency order and spot-check confirms improved coverage

### Implementation for User Story 4

- [x] T019 [US4] Create `.reforge/commands/fix.md` with command header: syntax block (`/reforge.fix [--type <type>] [--items <ids>] [--interactive] [--resume] [--json]`), arguments table, overview section, and prerequisites section (requires correction plan)
- [x] T020 [US4] Add Step 0 to `.reforge/commands/fix.md`: Initialize project using `check-prerequisites.sh --json --require-audit`, resolve `$AUDIT_DIR`, read `correction-plan.xml`, validate plan exists and has pending items
- [x] T021 [US4] Add Step 0.5 to `.reforge/commands/fix.md`: Load project context from `.reforge/memory/project-context.md` if exists
- [x] T022 [US4] Add Step 1 to `.reforge/commands/fix.md`: Check for resume state — if `--resume` flag, read `.reforge/memory/checkpoints/fix-checkpoint.xml`, identify last completed correction ID, filter plan to remaining items only
- [x] T023 [US4] Add Step 2 to `.reforge/commands/fix.md`: Sort corrections by dependency order — group by category (analysis first, then extraction, then generation), within each category sort by priority number
- [x] T024 [US4] Add Step 3 to `.reforge/commands/fix.md`: Execute corrections loop — for each pending correction item: update status to "in-progress" in plan, execute the recommended action (dispatch to appropriate reforge command: `/reforge.reanalyze` for stale files, `/reforge.extract` for coverage gaps, `/reforge.generate` for generation gaps), save checkpoint after each successful correction
- [x] T025 [US4] Add Step 4 to `.reforge/commands/fix.md`: Spot-check verification — after each correction completes, re-check the specific affected files to verify they now have extraction coverage (re-read extraction XMLs for those file paths), update correction status to "completed" or "failed"
- [x] T026 [US4] Add Step 5 to `.reforge/commands/fix.md`: Update plan and checkpoint — write updated statuses back to `correction-plan.xml`, update `completed-items` count, write checkpoint to `.reforge/memory/checkpoints/fix-checkpoint.xml`
- [x] T027 [US4] Add Step 6 to `.reforge/commands/fix.md`: Report results — display summary of corrections executed, successes, failures, and remaining items; suggest `/reforge.audit` for full re-verification
- [x] T028 [US4] Add error handling section to `.reforge/commands/fix.md`: Handle missing plan (suggest `/reforge.audit`), correction execution failures (save progress, continue or stop), and checkpoint corruption
- [x] T029 [US4] Add examples section to `.reforge/commands/fix.md`: Include examples for full fix execution, resumed fix, and fix with failures
- [x] T029b [US4] Add JSON output section to `.reforge/commands/fix.md`: When `--json` flag provided, output structured JSON summary after execution with fields: total_corrections, completed, failed, skipped, remaining, and per-item status array (following audit.md JSON output pattern)

**Checkpoint**: `/reforge.fix` command is fully functional — executes corrections in order with checkpoint support

---

## Phase 5: User Story 2 - Targeted Artifact Audit (Priority: P2)

**Goal**: Users can run `/reforge.audit <type>` to audit a specific extraction or generation type

**Independent Test**: Run `/reforge.audit business-rules` and verify it only checks business-rules.xml coverage and stale references, not other types

### Implementation for User Story 2

- [x] T030 [US2] Extend Step 1 in `.reforge/commands/audit.md`: Add type-specific file selection logic — when `[type]` argument provided, only read the specified extraction file instead of all extraction files; support types: analysis (check for stale file entries within analysis.xml), business-rules, database, ui-flows, workflows, user-stories, documentation, diagrams
- [x] T031 [US2] Extend Step 2 in `.reforge/commands/audit.md`: Add type-specific reference collection — when targeting generated artifacts (user-stories, documentation, diagrams), validate those artifacts exist in `$PROJECT_OUTPUT_DIR/generated/` and trace their references back to extraction items
- [x] T032 [US2] Extend Step 4 in `.reforge/commands/audit.md`: Add type-specific stale reference checking — only check references for the specified type, report per-type statistics
- [x] T033 [US2] Extend report output in `.reforge/commands/audit.md`: When type specified, adjust report to show type-specific coverage (e.g., "business-rules coverage: 85%") and scope correction plan to that type only
- [x] T034 [US2] Add type validation in `.reforge/commands/audit.md`: When type argument provided but artifact doesn't exist, report error with suggestion to run the appropriate command (e.g., "No user-stories found. Run /reforge.generate user-stories first.")
- [x] T035 [US2] Add targeted audit examples to `.reforge/commands/audit.md`: Examples for `/reforge.audit business-rules`, `/reforge.audit user-stories`, and invalid type argument

**Checkpoint**: `/reforge.audit <type>` works for targeted auditing of specific artifact types

---

## Phase 6: User Story 5 - Selective Correction Execution (Priority: P3)

**Goal**: Users can execute specific corrections or approve interactively

**Independent Test**: Run `/reforge.fix --interactive` and verify it prompts before each correction; run `/reforge.fix --items COR-001` and verify only that item is executed

### Implementation for User Story 5

- [x] T036 [US5] Extend Step 2 in `.reforge/commands/fix.md`: Add `--type` filter logic — when provided, filter correction plan to only items matching the specified extraction type before execution
- [x] T037 [US5] Extend Step 2 in `.reforge/commands/fix.md`: Add `--items` filter logic — when provided (comma-separated IDs), filter correction plan to only the specified item IDs
- [x] T038 [US5] Extend Step 3 in `.reforge/commands/fix.md`: Add `--interactive` mode — before executing each correction, display the correction details (ID, description, affected files, action) and ask user for confirmation (proceed/skip/abort); mark skipped items with "skipped" status
- [x] T039 [US5] Add selective execution examples to `.reforge/commands/fix.md`: Examples for `--interactive`, `--type business-rules`, `--items COR-001,COR-003`, and combined flags

**Checkpoint**: All fix modes (full, typed, selective, interactive) are functional

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Integration updates and documentation alignment

- [x] T040 [P] Update CLAUDE.md commands section to include `/reforge.audit` and `/reforge.fix` with brief descriptions
- [x] T041 [P] Update `.reforge/commands/status.md` next-steps recommendations to include audit/fix suggestions when extractions are complete
- [x] T042 [P] Update `.reforge/memory/constitution.md` Framework Architecture directory listing to include `audit.md` and `fix.md` commands, `audit-report.md` and `correction-plan.md` schemas
- [x] T043 [P] Update `.reforge/memory/constitution.md` Output Directory listing to include `audit/` subdirectory with `audit-report.xml` and `correction-plan.xml`
- [x] T044 [P] Update `.reforge/memory/constitution.md` Command Workflow section to add Verification Phase with audit and fix commands
- [x] T045 Run quickstart.md validation: verify all command examples in `specs/002-audit-fix-commands/quickstart.md` are consistent with implemented command syntax

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion — BLOCKS all user stories
- **US1+US3 (Phase 3)**: Depends on Foundational (schemas must exist for command to reference)
- **US4 (Phase 4)**: Depends on Phase 3 (fix command references audit output format)
- **US2 (Phase 5)**: Depends on Phase 3 (extends audit.md which must exist)
- **US5 (Phase 6)**: Depends on Phase 4 (extends fix.md which must exist)
- **Polish (Phase 7)**: Depends on Phases 3-6 completion

### User Story Dependencies

- **US1+US3 (Full Audit + Plan)**: Can start after Foundational — no dependencies on other stories
- **US4 (Execute Fix)**: Can start after US1+US3 — reads correction plan format
- **US2 (Targeted Audit)**: Can start after US1+US3 — extends existing audit.md
- **US5 (Selective Fix)**: Can start after US4 — extends existing fix.md

### Within Each User Story

- Schema documentation before command templates
- Command structure (header/syntax) before workflow steps
- Core workflow steps before error handling
- Error handling before examples

### Parallel Opportunities

- T003 and T004 (schemas) can run in parallel
- T040-T044 (polish updates) can all run in parallel
- US2 (Phase 5) and US4 (Phase 4) can run in parallel after Phase 3 completes
- Within Phase 3: T005-T007 (command setup) are sequential, but once structure exists, steps can be written sequentially as they build on each other

---

## Parallel Example: Phase 2 (Foundational)

```bash
# Launch both schema tasks together:
Task: "Create audit report schema documentation in .reforge/schemas/audit-report.md"
Task: "Create correction plan schema documentation in .reforge/schemas/correction-plan.md"
```

## Parallel Example: Phase 7 (Polish)

```bash
# Launch all integration updates together:
Task: "Update CLAUDE.md commands section"
Task: "Update .reforge/commands/status.md next-steps"
Task: "Update .reforge/memory/constitution.md Framework Architecture"
Task: "Update .reforge/memory/constitution.md Output Directory"
Task: "Update .reforge/memory/constitution.md Command Workflow"
```

---

## Implementation Strategy

### MVP First (User Stories 1+3+4)

1. Complete Phase 1: Setup (verify structure, update prerequisites)
2. Complete Phase 2: Foundational (schemas)
3. Complete Phase 3: US1+US3 (audit command with correction plan)
4. **STOP and VALIDATE**: Run `/reforge.audit` against a test codebase
5. Complete Phase 4: US4 (fix command)
6. **STOP and VALIDATE**: Run `/reforge.fix` and verify corrections applied

### Incremental Delivery

1. Setup + Foundational → Infrastructure ready
2. Add US1+US3 (audit) → Test full audit → Usable for coverage reporting
3. Add US4 (fix) → Test full fix → Complete audit-fix cycle (MVP!)
4. Add US2 (targeted audit) → Test type-specific auditing
5. Add US5 (selective fix) → Test interactive/selective modes
6. Polish → All integration points updated

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- US1 and US3 are combined because the audit command naturally produces both the report and the plan in a single execution
- US4 and US5 are separated because basic fix (US4) is P1 priority while selective modes (US5) are P3
- Each task in Phase 3-4 adds a specific section to the command template file — they are sequential within those phases because each step builds on the previous
- The "implementation" is markdown prompt templates, not compiled code — tasks describe writing structured markdown content
