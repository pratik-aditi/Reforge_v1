# Tasks: Schema Integration for Reforge Workflow

**Input**: Design documents from `/specs/003-schema-integration/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, quickstart.md ✅

**Tests**: Not requested for this documentation-only feature.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

This feature modifies only markdown files in the `.reforge/` directory (no source code):
- **Schemas**: `.reforge/schemas/*.md`
- **Commands**: `.reforge/commands/*.md`

---

## Phase 1: Setup (Verification)

**Purpose**: Verify current state matches research findings before making changes

- [x] T001 Verify audit-report.md does not have Contract Reference section in .reforge/schemas/audit-report.md
- [x] T002 [P] Verify correction-plan.md does not have Contract Reference section in .reforge/schemas/correction-plan.md
- [x] T003 [P] Verify cross-mappings.md does not have Schema Notes section in .reforge/schemas/cross-mappings.md
- [x] T004 [P] Verify features-requirements.md does not have Schema Notes section in .reforge/schemas/features-requirements.md
- [x] T005 [P] Verify fix.md does not have Output Schema References section in .reforge/commands/fix.md

**Checkpoint**: Current state verified - proceed to implementation ✅

---

## Phase 2: User Story 1 - Schema-Compliant Output Generation (Priority: P1) 🎯 MVP

**Goal**: Ensure schemas with XSD contracts have proper Contract Reference sections for traceability

**Independent Test**: Read `.reforge/schemas/audit-report.md` and `.reforge/schemas/correction-plan.md`; both should have "Contract Reference" section linking to correct XSD path

### Implementation for User Story 1

- [x] T006 [P] [US1] Add Contract Reference section to .reforge/schemas/audit-report.md pointing to specs/002-audit-fix-commands/contracts/audit-report.xsd
- [x] T007 [P] [US1] Add Contract Reference section to .reforge/schemas/correction-plan.md pointing to specs/002-audit-fix-commands/contracts/correction-plan.xsd

**Checkpoint**: User Story 1 complete - all schemas with XSD contracts now have Contract Reference sections ✅

---

## Phase 3: User Story 2 - Schema Documentation Discoverability (Priority: P2)

**Goal**: Ensure command templates reference their output schemas, enabling agents to find schema guidance

**Independent Test**: Read `.reforge/commands/fix.md`; should have "Output Schema References" section linking to correction-plan.md

### Implementation for User Story 2

- [x] T008 [US2] Add Output Schema References section to .reforge/commands/fix.md referencing .reforge/schemas/correction-plan.md

**Checkpoint**: User Story 2 complete - fix.md now references its output schema ✅

---

## Phase 4: User Story 3 - Schema Consistency Verification (Priority: P3)

**Goal**: Ensure derived schemas (no XSD) have clear documentation noting their authoritative status

**Independent Test**: Read `.reforge/schemas/cross-mappings.md` and `.reforge/schemas/features-requirements.md`; both should have "Schema Notes" section explaining they are derived schemas

### Implementation for User Story 3

- [x] T009 [P] [US3] Add Schema Notes section to .reforge/schemas/cross-mappings.md documenting derived schema status and related schemas
- [x] T010 [P] [US3] Add Schema Notes section to .reforge/schemas/features-requirements.md documenting derived schema status and related schemas

**Checkpoint**: User Story 3 complete - derived schemas have clear authoritative documentation ✅

---

## Phase 5: Polish & Verification

**Purpose**: Final validation and documentation

- [x] T011 Verify all 5 modified files have valid markdown syntax
- [x] T012 [P] Verify Contract Reference paths resolve to existing XSD files in specs/
- [x] T013 Run quickstart.md verification checklist in specs/003-schema-integration/quickstart.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - verification only
- **User Story 1 (Phase 2)**: No dependencies on other stories - can start immediately
- **User Story 2 (Phase 3)**: No dependencies on other stories - can start immediately
- **User Story 3 (Phase 4)**: No dependencies on other stories - can start immediately
- **Polish (Phase 5)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Independent - audit-report.md and correction-plan.md
- **User Story 2 (P2)**: Independent - fix.md only
- **User Story 3 (P3)**: Independent - cross-mappings.md and features-requirements.md

### Within Each User Story

- T006 and T007 can run in parallel (different files)
- T009 and T010 can run in parallel (different files)
- T008 is a single file change

### Parallel Opportunities

All user stories can be implemented in parallel since they modify different files:

| Story | Files Modified |
|-------|----------------|
| US1 | audit-report.md, correction-plan.md |
| US2 | fix.md |
| US3 | cross-mappings.md, features-requirements.md |

---

## Parallel Example: All User Stories

```bash
# All these tasks can run in parallel (different files):
Task: T006 [US1] "Add Contract Reference to audit-report.md"
Task: T007 [US1] "Add Contract Reference to correction-plan.md"
Task: T008 [US2] "Add Output Schema References to fix.md"
Task: T009 [US3] "Add Schema Notes to cross-mappings.md"
Task: T010 [US3] "Add Schema Notes to features-requirements.md"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Skip Phase 1 verification if confident in research findings
2. Complete Phase 2: User Story 1 (add Contract References)
3. **STOP and VALIDATE**: Verify XSD paths resolve correctly
4. Commit with message: "feat(schemas): add Contract Reference to audit-report and correction-plan"

### Full Implementation (Recommended)

1. Complete all User Stories in parallel (different files)
2. Complete Phase 5 verification
3. Commit all changes together: "feat(schemas): complete schema integration for FR-006 traceability"

### Incremental Delivery

Each user story can be committed separately:
1. US1: `feat(schemas): add Contract Reference sections for XSD traceability`
2. US2: `feat(commands): add schema reference to fix.md`
3. US3: `feat(schemas): document derived schema status for cross-mappings and features-requirements`

---

## Notes

- All tasks are markdown edits - no compiled code changes
- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- No tests requested - manual validation via quickstart.md checklist
- Total implementation: 5 file edits, ~20 lines added
