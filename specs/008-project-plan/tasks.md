# Tasks: Project Plan Command

**Input**: Design documents from `/specs/008-project-plan/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story. US1 and US2 are combined into a single phase since they are both P1 and implemented in the same file (`.reforge/commands/plan.md`).

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Project type**: Prompt template framework (no compiled source directories)
- All command templates: `.reforge/commands/<name>.md`
- Framework state: `.reforge/memory/`
- Agent context: `CLAUDE.md` at repository root

---

## Phase 1: Setup

**Purpose**: Orientation — review existing command template patterns to ensure consistency

- [x] T001 Review existing command template patterns in `.reforge/commands/` — examine Step 0/0.5/0.6 structure, interactive Q&A patterns (init.md, profile.md), argument parsing conventions (extract.md, audit.md), and plan file format contract in `specs/008-project-plan/contracts/plan-file-format.md`

---

## Phase 2: US1+US2 — Core Plan Command (Priority: P1) 🎯 MVP

**Goal**: Create the `/reforge.plan` command template that can create a new project plan (US1) and add items to an existing plan (US2). This is the MVP — a working plan file that users can create and iterate on.

**Independent Test**: Run `/reforge.plan` on a project with analysis complete, verify `.reforge/memory/project-plan.md` exists with Setup section and workflow groups containing 7-step pipeline checkboxes with HTML comment tags. Then run `/reforge.plan "add database extraction"` and verify new items appear while existing items are preserved.

### Implementation for US1+US2

- [x] T002 [US1] Create plan.md command header — syntax (`/reforge.plan [arguments] [--status]`), arguments table, and overview section in `.reforge/commands/plan.md`
- [x] T003 [US1] Create plan.md Step 0 (Check Prerequisites — verify `.reforge/memory/` exists) and Step 0.5 (Load Project Context — read project-context.md for suggestions) in `.reforge/commands/plan.md`
- [x] T004 [US1] Create plan.md Step 1 — Check Existing Plan: detect whether plan exists, determine behavioral mode (create/add/review), handle `--status` flag routing in `.reforge/commands/plan.md`
- [x] T005 [US1] Create plan.md Create Mode — interactive gathering workflow: ask user for intended extraction types, audit scope, generation targets, custom tasks following same Q&A pattern as init.md and profile.md in `.reforge/commands/plan.md`
- [x] T006 [US1] Create plan.md analysis-based suggestion logic: read `$PROJECT_OUTPUT_DIR/analysis/analysis.xml` to suggest extraction types based on discovered languages, file extensions, and module structure (e.g., suggest `database` if `.sql` files or ORM patterns found) in `.reforge/commands/plan.md`
- [x] T007 [US1] Create plan.md profile-based suggestion logic: read `.reforge/memory/extraction-profile.md` to suggest language-specific and architecture-specific extraction sub-tasks (e.g., "Extract WCF service contract rules" for WCF projects) in `.reforge/commands/plan.md`
- [x] T008 [US1] Create plan.md plan file generation step: write `.reforge/memory/project-plan.md` with metadata header (project name, created date, last updated), Setup section (init/analyze/profile items with tags), workflow group sections (7-step pipeline per extraction type with `<!-- reforge:<command>:<type> -->` tags), and optional Custom Tasks section per contract in `specs/008-project-plan/contracts/plan-file-format.md` in `.reforge/commands/plan.md`
- [x] T009 [US2] Create plan.md Add Mode — argument parsing, duplicate detection via `<!-- reforge:<command>:<type> -->` tag matching, section-appropriate insertion of new workflow groups preserving all existing content and completion status, Last Updated metadata update in `.reforge/commands/plan.md`
- [x] T010 [US2] Create plan.md Interactive Review Mode — display per-section completion counts (completed/total), prompt user to add new items or review the plan, and handle edge cases (duplicate items, custom extraction types, invalid markdown resilience) in `.reforge/commands/plan.md`

**Checkpoint**: At this point, `/reforge.plan` can create and iteratively update a project plan. The plan file contains properly tagged checkboxes. This is the MVP — test by running `/reforge.plan` to create, then `/reforge.plan "add ..."` to extend.

---

## Phase 3: US3 — All Commands Reference and Update the Plan (Priority: P2)

**Goal**: Add Step 0.7 (Check/Update Project Plan) to all 10 existing Reforge command templates so they auto-read the plan on start and auto-mark their corresponding checkbox on successful completion.

**Independent Test**: Create a plan with items spanning multiple command types (init, analyze, extract business-rules), run those commands, verify all corresponding checkboxes are toggled to `[x]` with completion timestamps. Then delete the plan file and verify all commands still work normally.

### Implementation for US3

- [x] T011 [P] [US3] Add Step 0.7 to `.reforge/commands/init.md` — insert completion-only update as final step after writing project-context.md, tag: `<!-- reforge:init -->`, no read-on-start display (init is typically the first command)
- [x] T012 [P] [US3] Add Step 0.7 to `.reforge/commands/analyze.md` — insert after Step 0.5 (Load Project Context), tag: `<!-- reforge:analyze -->`, standard two-phase pattern (read on start, write on completion)
- [x] T013 [P] [US3] Add Step 0.7 to `.reforge/commands/profile.md` — insert after Step 0.5 (Load Project Context), tag: `<!-- reforge:profile -->`, standard two-phase pattern
- [x] T014 [P] [US3] Add Step 0.7 to `.reforge/commands/extract.md` — insert after Step 0.6 (Load Extraction Profile), tag: `<!-- reforge:extract:<type> -->` derived from command type argument, standard two-phase pattern
- [x] T015 [P] [US3] Add Step 0.7 to `.reforge/commands/clarify.md` — insert after Step 0.5, tag: `<!-- reforge:clarify:<type> -->` from `--category` argument; if no category specified, skip plan update (clarify may partially cover multiple types)
- [x] T016 [P] [US3] Add Step 0.7 to `.reforge/commands/generate.md` — insert after Step 0.5, tag: `<!-- reforge:generate:<type> -->` from `--scope` argument; without scope, mark generate items for all types with available extractions (multi-type marking)
- [x] T017 [P] [US3] Add Step 0.7 to `.reforge/commands/status.md` — insert after Step 0.5, READ-ONLY variant: display plan progress (X/Y items, Z%), per-section breakdown, suggested next steps; do NOT mark any item complete; if no plan exists, suggest running `/reforge.plan`
- [x] T018 [P] [US3] Add Step 0.7 to `.reforge/commands/reanalyze.md` — insert after Step 0.5, tag: `<!-- reforge:analyze -->` (same artifact as analyze), standard two-phase pattern
- [x] T019 [P] [US3] Add Step 0.7 to `.reforge/commands/audit.md` — insert after Step 0.5; determine audit target context (extractions vs generated output) from what was audited; use tag `<!-- reforge:audit:<type> -->` for extraction audits, `<!-- reforge:audit-generated:<type> -->` for generated output audits; without type arg, mark matching tags for all audited types (multi-type, multi-context marking)
- [x] T020 [P] [US3] Add Step 0.7 to `.reforge/commands/fix.md` — insert after Step 0.5; determine fix target context (extractions vs generated output) from what was fixed; use tag `<!-- reforge:fix:<type> -->` for extraction fixes, `<!-- reforge:fix-generated:<type> -->` for generated output fixes; without type arg, mark matching tags for all fixed types (multi-type, multi-context marking)

**Checkpoint**: At this point, all commands auto-read and auto-update the project plan. Test by creating a plan, running several commands, and verifying checkboxes are toggled. Verify all commands still work when no plan file exists.

---

## Phase 4: US4 — Plan Status Summary (Priority: P2)

**Goal**: Add `--status` flag support that displays a progress summary without modifying the plan file.

**Independent Test**: Create a plan with multiple items, manually check some off, run `/reforge.plan --status` and verify it shows correct per-section completion counts, percentages, and 100%-complete messaging.

### Implementation for US4

- [x] T021 [US4] Add `--status` flag handling (Mode 4) to `.reforge/commands/plan.md` — count completed/total per section, display per-section breakdown with percentages, show overall progress, congratulate and suggest next steps when 100% complete, do NOT modify the plan file

**Checkpoint**: `/reforge.plan --status` provides accurate progress visibility. All four user stories are now functional.

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Framework documentation updates and compliance validation

- [x] T022 [P] Update `.reforge/memory/constitution.md` — add `plan.md`, `init.md`, `profile.md`, `audit.md`, and `fix.md` to commands directory listing in Framework Architecture (correcting pre-existing omissions alongside the new command); rewrite Command Workflow section to reflect the full pipeline: Planning Phase (`/reforge.plan`) → Setup Phase (init, analyze, profile) → Extraction Phase per type (extract, clarify, audit, fix) → Generation Phase per type (generate, audit generated, fix generated) → Cross-Cutting Commands (status, reanalyze); add workflow rule "Planning is optional"; bump version 1.3.0 → 1.4.0 with sync impact report comment
- [x] T023 [P] Update `CLAUDE.md` — add `/reforge.plan` to Commands section with description, ensure command listing order reflects workflow (plan before analyze)
- [x] T024 Audit all new and modified files for agent-agnostic language compliance (Constitution Principle V) — scan `.reforge/commands/plan.md` and all Step 0.7 additions for agent-specific references (replace "Claude" with "The agent", etc.)
- [x] T025 Validate plan file format contract — verify the plan.md template generates output matching `specs/008-project-plan/contracts/plan-file-format.md` spec: correct tag patterns, metadata header format, section ordering, 7-step pipeline per workflow group

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — orientation only, no file changes
- **US1+US2 (Phase 2)**: Depends on Setup (understanding existing patterns)
- **US3 (Phase 3)**: Can start after US1+US2 checkpoint (plan.md must exist to reference its tag convention)
- **US4 (Phase 4)**: Can start after US1+US2 checkpoint (adds to plan.md)
- **Polish (Phase 5)**: Depends on all user stories being complete

### User Story Dependencies

- **US1+US2 (P1)**: Can start after Setup — No dependencies on other stories. Creates `.reforge/commands/plan.md`
- **US3 (P2)**: Depends on US1+US2 completion — needs plan.md tag convention finalized. Modifies 10 separate command templates (all parallelizable)
- **US4 (P2)**: Depends on US1+US2 completion — adds --status mode to plan.md. Can run in parallel with US3 (different sections of plan.md vs different files)
- **Polish**: Depends on US3 + US4 completion — constitution and CLAUDE.md should reflect final state

### Within Each User Story

- US1+US2: Sequential within plan.md (T002→T003→T004→T005→T006→T007→T008→T009→T010)
- US3: All 10 tasks (T011-T020) are fully parallelizable — each modifies a different file
- US4: Single task (T021)

### Parallel Opportunities

- **Phase 3 (US3)**: All 10 Step 0.7 integrations can run in parallel — each modifies a different command template file
- **Phase 4 (US4)**: Can run in parallel with Phase 3 (different sections of plan.md vs different command files)
- **Phase 5**: T022 and T023 can run in parallel (different files: constitution.md vs CLAUDE.md)

---

## Parallel Example: US3 (Step 0.7 Integration)

```bash
# All 10 Step 0.7 integrations can launch simultaneously:
Task: "Add Step 0.7 to .reforge/commands/init.md"
Task: "Add Step 0.7 to .reforge/commands/analyze.md"
Task: "Add Step 0.7 to .reforge/commands/profile.md"
Task: "Add Step 0.7 to .reforge/commands/extract.md"
Task: "Add Step 0.7 to .reforge/commands/clarify.md"
Task: "Add Step 0.7 to .reforge/commands/generate.md"
Task: "Add Step 0.7 to .reforge/commands/status.md"
Task: "Add Step 0.7 to .reforge/commands/reanalyze.md"
Task: "Add Step 0.7 to .reforge/commands/audit.md"
Task: "Add Step 0.7 to .reforge/commands/fix.md"
```

---

## Implementation Strategy

### MVP First (US1+US2 Only)

1. Complete Phase 1: Setup (orientation)
2. Complete Phase 2: US1+US2 (create `.reforge/commands/plan.md`)
3. **STOP and VALIDATE**: Test by running `/reforge.plan` to create a plan, then `/reforge.plan "add ..."` to extend it
4. The plan file is usable at this point — commands just don't auto-update it yet

### Incremental Delivery

1. US1+US2 → Test plan creation and add mode → Plan file works (MVP!)
2. US3 → Test Step 0.7 integration → Commands auto-update plan checkboxes
3. US4 → Test --status flag → Progress visibility
4. Polish → Constitution and CLAUDE.md updated → Feature complete
5. Each phase adds value without breaking previous functionality

### Parallel Team Strategy

With multiple agents:

1. Complete Setup + US1+US2 together (sequential — same file)
2. Once US1+US2 complete:
   - Agent A: US3 tasks T011-T015 (init, analyze, profile, extract, clarify)
   - Agent B: US3 tasks T016-T020 (generate, status, reanalyze, audit, fix)
   - Agent C: US4 task T021 (--status mode)
3. All complete → Polish phase

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- This is a prompt-template-only project — no compiled code, no tests, no runtime
- All "implementation" is writing/editing markdown files
- The plan.md command template is the largest single artifact (~200-300 lines)
- Each Step 0.7 addition is ~20-30 lines of markdown per command template
- Agent-agnostic language is critical — never say "Claude MUST", always "The agent MUST"
