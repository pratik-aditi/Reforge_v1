# Tasks: XSD Validation Tooling

**Input**: Design documents from `/specs/004-xsd-validation-tooling/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, quickstart.md ✅

**Tests**: Tests ARE requested — existing pytest infrastructure in `tests/test_scripts.py`.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

This feature extends the existing reforge-cli package:
- **Scripts**: `src/reforge_cli/scripts/`
- **CLI**: `src/reforge_cli/__init__.py`
- **Tests**: `tests/`
- **XSD Schemas**: `.reforge/schemas/xsd/`

---

## Phase 1: Setup (Verification)

**Purpose**: Verify current state and XSD files are in place

- [x] T001 Verify XSD files exist in .reforge/schemas/xsd/ (8 files: analysis, business-rules, database, ui-flows, workflows, user-stories, audit-report, correction-plan)
- [x] T002 Create test fixtures directory at tests/fixtures/validation/

**Checkpoint**: XSD schemas in place, test fixtures directory ready ✅

---

## Phase 2: User Story 1 - XML Output Validation (Priority: P1) 🎯 MVP

**Goal**: Provide `reforge-scripts validate-xml` command that invokes xmllint and returns structured, LLM-parseable output

**Independent Test**: Run `reforge-scripts validate-xml tests/fixtures/validation/valid-analysis.xml analysis` → exit code 0, "VALIDATION_OK"; run with invalid file → exit code 1, structured errors

### Tests for User Story 1

- [x] T003 [P] [US1] Create valid XML test fixture at tests/fixtures/validation/valid-analysis.xml (minimal valid analysis.xml)
- [x] T004 [P] [US1] Create invalid XML test fixture at tests/fixtures/validation/invalid-analysis.xml (missing required attribute)
- [x] T005 [US1] Add validation tests to tests/test_scripts.py (test_validate_xml_valid, test_validate_xml_invalid, test_validate_xml_missing_file, test_validate_xml_missing_xmllint)

### Implementation for User Story 1

- [x] T006 [US1] Create ValidationError dataclass in src/reforge_cli/scripts/validation.py per data-model.md
- [x] T007 [US1] Create ValidationResult dataclass in src/reforge_cli/scripts/validation.py per data-model.md
- [x] T008 [US1] Implement check_xmllint_available() function in src/reforge_cli/scripts/validation.py (uses shutil.which, returns install instructions if missing)
- [x] T009 [US1] Implement get_available_schemas() function in src/reforge_cli/scripts/validation.py (reads .reforge/schemas/xsd/ directory)
- [x] T010 [US1] Implement parse_xmllint_errors() function in src/reforge_cli/scripts/validation.py (regex parsing per research.md)
- [x] T011 [US1] Implement generate_suggestion() function in src/reforge_cli/scripts/validation.py using error categories from data-model.md: unknown-element, missing-attribute, invalid-value, missing-element, wrong-order, extra-content
- [x] T012 [US1] Implement validate_xml() main function in src/reforge_cli/scripts/validation.py (subprocess call to xmllint, parse output, return ValidationResult)
- [x] T013 [US1] Implement format_structured_output() function in src/reforge_cli/scripts/validation.py (VALIDATION_OK/FAILED format per spec)
- [x] T014 [US1] Export validation functions from src/reforge_cli/scripts/__init__.py
- [x] T015 [US1] Add validate-xml command to scripts CLI in src/reforge_cli/__init__.py (typer command with --json, --list-schemas, --help flags)
- [x] T016 [US1] Add Bash permission for validate-xml in src/reforge_cli/__init__.py merge_settings() function

**Checkpoint**: User Story 1 complete — validate-xml command works with valid/invalid XML files ✅

---

## Phase 3: User Story 2 - XSD Schema Deployment (Priority: P2)

**Goal**: XSD schemas copied to `.reforge/schemas/xsd/` during install and update operations

**Independent Test**: Run `reforge --claude . --update` on a test project → verify `.reforge/schemas/xsd/` contains 8 XSD files

### Tests for User Story 2

- [x] T017 [US2] Add XSD deployment test to tests/test_scripts.py (test_install_copies_xsd_schemas, test_update_refreshes_xsd_schemas)

### Implementation for User Story 2

- [x] T018 [US2] Modify copy_framework() in src/reforge_cli/__init__.py to include schemas/xsd/ directory (already included - copies entire schemas/ directory)
- [x] T019 [US2] Modify do_update() in src/reforge_cli/__init__.py to refresh schemas/xsd/ on update (already included - refreshes entire schemas/ directory)
- [x] T020 [US2] Verify pyproject.toml shared-data includes .reforge/schemas/xsd/ (confirmed - .reforge in shared-data includes all subdirectories)

**Checkpoint**: User Story 2 complete — XSD files deployed on install/update ✅

---

## Phase 4: User Story 3 - Validation Integration in Commands (Priority: P3)

**Goal**: Extraction command templates include optional validation step guidance

**Independent Test**: Read `.reforge/commands/extract.md` → contains validation step reference; agent can follow guidance to validate output

### Implementation for User Story 3

- [x] T021 [US3] Add "Optional Validation" section to .reforge/commands/extract.md with reforge-scripts validate-xml usage
- [x] T022 [P] [US3] Add "Optional Validation" section to .reforge/commands/generate.md with validation guidance
- [x] T023 [US3] Update .reforge/README.md to document validate-xml command availability

**Checkpoint**: User Story 3 complete — command templates reference validation tooling ✅

---

## Phase 5: Polish & Verification

**Purpose**: Final validation and cross-cutting concerns

- [x] T024 Run all pytest tests to verify no regressions (141 tests passed; cross-platform compatibility per NFR-002 verified by CI or manual testing on macOS/Linux/WSL)
- [x] T025 [P] Run quickstart.md verification checklist in specs/004-xsd-validation-tooling/quickstart.md
- [x] T026 [P] Verify validate-xml --help shows correct usage
- [x] T027 [P] Verify validate-xml --list-schemas shows all 8 schemas
- [x] T028 Test xmllint-not-found error message includes platform-specific install instructions

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — verification only
- **User Story 1 (Phase 2)**: Depends on Setup — XSD files must be in place
- **User Story 2 (Phase 3)**: No dependencies on US1 — can run in parallel
- **User Story 3 (Phase 4)**: No dependencies on US1/US2 — documentation only
- **Polish (Phase 5)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Core functionality — validation script
- **User Story 2 (P2)**: Infrastructure — XSD deployment (independent of US1)
- **User Story 3 (P3)**: Documentation — command template updates (independent)

### Within User Story 1

- T003, T004 can run in parallel (different test fixture files)
- T005 depends on T003, T004 (needs fixtures)
- T006, T007 can run in parallel (different dataclasses, same file but independent sections)
- T008-T013 should be sequential (each builds on previous)
- T014 depends on T006-T013 (exports functions)
- T015 depends on T014 (uses exported functions)
- T016 depends on T015 (adds permission for new command)

### Parallel Opportunities

- US1, US2, US3 can all proceed in parallel after Setup (different files)
- Within US1: T003, T004 in parallel (test fixtures)
- Within US1: T006, T007 in parallel (dataclasses)
- Polish tasks T025, T026, T027 can run in parallel

---

## Parallel Example: User Story 1 Test Fixtures

```bash
# Launch test fixture creation in parallel:
Task: T003 "Create valid-analysis.xml fixture in tests/fixtures/validation/"
Task: T004 "Create invalid-analysis.xml fixture in tests/fixtures/validation/"
```

## Parallel Example: All User Stories

```bash
# After Setup, all stories can proceed in parallel:
Story US1: T003-T016 (validation script implementation)
Story US2: T017-T020 (XSD deployment in install/update)
Story US3: T021-T023 (command template documentation)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (verify XSD files)
2. Complete Phase 2: User Story 1 (validate-xml command)
3. **STOP and VALIDATE**: Run `reforge-scripts validate-xml` manually
4. If working, can deploy/use immediately

### Full Implementation (Recommended)

1. Complete Setup
2. Implement US1, US2, US3 in parallel (independent files)
3. Complete Phase 5 verification
4. Commit all changes together: `feat(validation): add XSD validation tooling per spec 004`

### Incremental Delivery

Each user story can be committed separately:
1. US1: `feat(validation): add reforge-scripts validate-xml command`
2. US2: `feat(install): deploy XSD schemas to .reforge/schemas/xsd/`
3. US3: `docs(commands): add validation guidance to extract/generate templates`

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Total tasks: 28 (1 already complete: T001)
- US1: 14 tasks (core validation functionality)
- US2: 4 tasks (install/update integration)
- US3: 3 tasks (documentation updates)
- Polish: 5 tasks (verification)
- XSD files already copied to `.reforge/schemas/xsd/` during planning phase
- Existing test infrastructure at `tests/test_scripts.py` will be extended
