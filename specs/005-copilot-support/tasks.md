# Tasks: GitHub Copilot Slash Command Support

**Input**: Design documents from `/specs/005-copilot-support/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md

**Tests**: Tests are included — the existing test suite (`tests/test_scripts.py`) has comprehensive patterns for installation/removal testing that should be extended.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup

**Purpose**: Verify baseline and understand existing patterns

- [x] T001 Run existing test suite to confirm baseline passes: `pytest tests/test_scripts.py`
- [x] T002 Read existing `generate_wrappers()` function in `src/reforge_cli/__init__.py` to understand the Claude wrapper pattern that Copilot generation will mirror

---

## Phase 2: Foundational (Core Generation Functions)

**Purpose**: Implement the three new generation functions that all user stories depend on

**CRITICAL**: No user story work can begin until these functions exist

- [x] T003 [P] Implement `generate_copilot_agents()` function in `src/reforge_cli/__init__.py` — iterates `.reforge/commands/*.md`, extracts description from first `>` blockquote, generates `.github/agents/reforge.<name>.agent.md` files with YAML frontmatter containing `description` field and Load-and-Execute body (per research.md R1 and FR-007). Support `dry_run` parameter. Mirror pattern of `generate_wrappers()`
- [x] T004 [P] Implement `generate_copilot_prompts()` function in `src/reforge_cli/__init__.py` — iterates generated agent files in `.github/agents/`, creates `.github/prompts/reforge.<name>.prompt.md` with minimal YAML frontmatter `agent: reforge.<name>` (per research.md R2). Support `dry_run` parameter
- [x] T005 [P] Implement `merge_vscode_settings()` function in `src/reforge_cli/__init__.py` — creates or deep-merges `.vscode/settings.json` with `chat.promptFilesRecommendations` entries for each command and `chat.tools.terminal.autoApprove` for `reforge-scripts` (per research.md R3). Support `dry_run` parameter. Preserve existing non-Reforge settings. Mirror pattern of `merge_settings()`
- [x] T006 Add `--copilot` CLI flag to the `cli()` callback in `src/reforge_cli/__init__.py` — add `copilot: bool = typer.Option(False, "--copilot", ...)`. Update the dispatch logic so `--copilot` triggers the same validation + install/update flow as `--claude` but calls Copilot generation functions instead of Claude wrapper functions. Ensure `--claude` and `--copilot` are mutually exclusive per invocation

**Checkpoint**: Core generation functions exist and CLI accepts `--copilot` flag

---

## Phase 3: User Story 1 - Install Reforge for Copilot (Priority: P1) MVP

**Goal**: `reforge --copilot .` installs framework files + Copilot agents + prompts + VS Code settings

**Independent Test**: Run `reforge --copilot .` on a clean temp directory and verify all expected files are created

### Tests for User Story 1

- [x] T007 [P] [US1] Add `test_generate_copilot_agents_creates_agent_files` test in `tests/test_scripts.py` — verify `.github/agents/reforge.*.agent.md` files created for each command template, with correct body content (Load-and-Execute instruction), YAML frontmatter with `description` field, and description extracted from blockquote
- [x] T008 [P] [US1] Add `test_generate_copilot_agents_dry_run` test in `tests/test_scripts.py` — verify no files created when `dry_run=True`
- [x] T009 [P] [US1] Add `test_generate_copilot_prompts_creates_prompt_files` test in `tests/test_scripts.py` — verify `.github/prompts/reforge.*.prompt.md` files created with correct `agent: reforge.<name>` YAML frontmatter
- [x] T010 [P] [US1] Add `test_merge_vscode_settings_creates_new_file` test in `tests/test_scripts.py` — verify `.vscode/settings.json` created with `chat.promptFilesRecommendations` and `chat.tools.terminal.autoApprove` entries
- [x] T011 [P] [US1] Add `test_merge_vscode_settings_merges_existing` test in `tests/test_scripts.py` — verify existing `.vscode/settings.json` user settings are preserved while Reforge entries are added
- [x] T012 [P] [US1] Add `test_copilot_install_dry_run` CLI test in `tests/test_scripts.py` — verify `reforge --copilot --dry-run .` lists expected files without creating them (use CliRunner)
- [x] T013 [P] [US1] Add `test_copilot_install_fails_if_already_installed` CLI test in `tests/test_scripts.py` — verify error when `.reforge/` already exists

### Implementation for User Story 1

- [x] T014 [US1] Implement `do_install()` Copilot path in `src/reforge_cli/__init__.py` — when `--copilot` is used: call `copy_framework()`, `create_memory_dirs()`, `generate_copilot_agents()`, `generate_copilot_prompts()`, `merge_vscode_settings()`, `update_gitignore()`. Display success message with Copilot-specific instructions (e.g., "Run @reforge.analyze in Copilot Chat")
- [x] T015 [US1] Add `test_do_copilot_install_full_flow` integration test in `tests/test_scripts.py` — verify end-to-end: `.reforge/` copied, `.github/agents/` populated, `.github/prompts/` populated, `.vscode/settings.json` created, `.gitignore` updated
- [x] T016 [US1] Verify all 9 commands produce correct agent files — run `reforge --copilot` against `mock_reforge_home` fixture and check each of the 9 `.agent.md` files exists with expected naming

**Checkpoint**: `reforge --copilot .` works end-to-end. MVP complete.

---

## Phase 4: User Story 2 - Update Copilot Installation (Priority: P2)

**Goal**: `reforge --copilot --update .` refreshes framework and Copilot files while preserving user config

**Independent Test**: Install via `--copilot`, modify config, run `--copilot --update`, verify refresh + preservation

### Tests for User Story 2

- [x] T017 [P] [US2] Add `test_copilot_update_refreshes_agents` test in `tests/test_scripts.py` — verify `.github/agents/` files are regenerated on update
- [x] T018 [P] [US2] Add `test_copilot_update_requires_existing` test in `tests/test_scripts.py` — verify error when no `.github/agents/reforge.*.agent.md` files exist (installation detection per clarification)
- [x] T019 [P] [US2] Add `test_copilot_update_preserves_config` test in `tests/test_scripts.py` — verify `config.json` user fields preserved after update

### Implementation for User Story 2

- [x] T020 [US2] Implement `do_update()` Copilot path in `src/reforge_cli/__init__.py` — detect existing Copilot installation by checking for `.github/agents/reforge.*.agent.md` files. Refresh `.reforge/` framework dirs, regenerate agents + prompts, re-merge VS Code settings, merge config preserving user fields. Display update success message
- [x] T021 [US2] Add `test_copilot_update_cli` integration test in `tests/test_scripts.py` — verify `reforge --copilot --update .` via CliRunner

**Checkpoint**: Update workflow works. Users can upgrade Copilot installations.

---

## Phase 5: User Story 3 - Remove Copilot Installation (Priority: P2)

**Goal**: `reforge --remove .` fully uninstalls all Reforge artifacts including Copilot files

**Independent Test**: Install via `--copilot`, run `--remove`, verify cleanup

### Tests for User Story 3

- [x] T022 [P] [US3] Add `test_remove_cleans_copilot_agents` test in `tests/test_scripts.py` — verify `.github/agents/reforge.*.agent.md` files removed, non-Reforge agent files preserved
- [x] T023 [P] [US3] Add `test_remove_cleans_copilot_prompts` test in `tests/test_scripts.py` — verify `.github/prompts/reforge.*.prompt.md` files removed, non-Reforge prompt files preserved
- [x] T024 [P] [US3] Add `test_remove_cleans_vscode_settings` test in `tests/test_scripts.py` — verify Reforge entries removed from `.vscode/settings.json`, other settings preserved

### Implementation for User Story 3

- [x] T025 [US3] Extend `do_remove()` in `src/reforge_cli/__init__.py` — add cleanup of `.github/agents/reforge.*.agent.md`, `.github/prompts/reforge.*.prompt.md`, and Reforge-specific keys from `.vscode/settings.json`. Only remove Reforge-prefixed files (preserve non-Reforge content). Update the confirmation message to list Copilot artifacts
- [x] T026 [US3] Add `test_remove_full_uninstall_copilot` integration test in `tests/test_scripts.py` — install via `--copilot`, run `--remove`, verify all Reforge artifacts gone

**Checkpoint**: Full uninstall works. Reforge can be cleanly removed from any project.

---

## Phase 6: User Story 4 - Coexistence & Copilot Chat Discovery (Priority: P1)

**Goal**: Claude and Copilot installations coexist; Copilot Chat discovers all 9 agents

**Independent Test**: Install both `--claude` and `--copilot`, verify both sets of files exist and don't conflict

### Tests for User Story 4

- [x] T027 [P] [US4] Add `test_claude_and_copilot_coexist` test in `tests/test_scripts.py` — install `--claude` then `--copilot`, verify `.claude/commands/reforge.*.md` AND `.github/agents/reforge.*.agent.md` both present
- [x] T028 [P] [US4] Add `test_copilot_and_claude_coexist_reverse_order` test in `tests/test_scripts.py` — install `--copilot` then `--claude`, verify same coexistence
- [x] T029 [P] [US4] Add `test_remove_cleans_both_agents` test in `tests/test_scripts.py` — install both modes, run `--remove`, verify all Claude and Copilot artifacts removed

### Implementation for User Story 4

- [x] T030 [US4] Verify agent file content references correct template paths — inspect generated `.agent.md` content to ensure `.reforge/commands/<name>.md` paths resolve correctly for Copilot Chat
- [x] T031 [US4] Add `test_claude_copilot_mutual_exclusion` CLI test in `tests/test_scripts.py` — verify `reforge --claude --copilot .` produces error (mutually exclusive per invocation)

**Checkpoint**: Both agents coexist correctly. Copilot Chat can discover and invoke all commands.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Edge cases, documentation, and cleanup

- [x] T032 [P] Add `test_merge_vscode_settings_handles_malformed_json` test in `tests/test_scripts.py` — verify graceful handling of corrupt `.vscode/settings.json`
- [x] T033 [P] Add `test_copilot_agents_preserve_non_reforge_files` test in `tests/test_scripts.py` — create non-Reforge `.agent.md` file in `.github/agents/`, run install, verify it's untouched
- [x] T034 Update help text and examples in CLI (`EXAMPLES` constant and option help strings) in `src/reforge_cli/__init__.py` to include `--copilot` usage
- [x] T035 Run full test suite to verify no regressions: `pytest tests/test_scripts.py -v`
- [x] T036 Run quickstart.md validation — manually execute the quickstart steps against a temp directory

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 completion — BLOCKS all user stories
- **US1 Install (Phase 3)**: Depends on Phase 2 — MVP target
- **US2 Update (Phase 4)**: Depends on Phase 2 — can run parallel with US1
- **US3 Remove (Phase 5)**: Depends on Phase 2 — can run parallel with US1/US2
- **US4 Coexistence (Phase 6)**: Depends on US1 completion (needs working install)
- **Polish (Phase 7)**: Depends on all user stories complete

### User Story Dependencies

- **US1 (Install)**: Can start after Phase 2. No dependencies on other stories
- **US2 (Update)**: Can start after Phase 2. Independent from US1 (but shares generation functions)
- **US3 (Remove)**: Can start after Phase 2. Independent from US1/US2
- **US4 (Coexistence)**: Depends on US1 (needs working `--copilot` install to test alongside `--claude`)

### Within Each User Story

- Tests first (written to fail)
- Core implementation
- Integration test
- Checkpoint verification

### Parallel Opportunities

- T003, T004, T005 can all run in parallel (independent functions in same file, different code sections)
- All test tasks marked [P] within a phase can run in parallel
- US1, US2, US3 can theoretically run in parallel after Phase 2 (different functions)

---

## Parallel Example: Phase 2 (Foundational)

```text
# Launch all three generation functions in parallel:
Task: "Implement generate_copilot_agents() in src/reforge_cli/__init__.py"
Task: "Implement generate_copilot_prompts() in src/reforge_cli/__init__.py"
Task: "Implement merge_vscode_settings() in src/reforge_cli/__init__.py"
```

## Parallel Example: User Story 1 Tests

```text
# Launch all US1 tests in parallel:
Task: "test_generate_copilot_agents_creates_agent_files in tests/test_scripts.py"
Task: "test_generate_copilot_agents_dry_run in tests/test_scripts.py"
Task: "test_generate_copilot_prompts_creates_prompt_files in tests/test_scripts.py"
Task: "test_merge_vscode_settings_creates_new_file in tests/test_scripts.py"
Task: "test_merge_vscode_settings_merges_existing in tests/test_scripts.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T002)
2. Complete Phase 2: Foundational (T003-T006)
3. Complete Phase 3: User Story 1 (T007-T016)
4. **STOP and VALIDATE**: Run `reforge --copilot .` on a temp directory
5. Verify all 9 agent files + 9 prompt files + settings.json created correctly

### Incremental Delivery

1. Setup + Foundational → Core functions ready
2. Add US1 (Install) → MVP: `reforge --copilot .` works
3. Add US2 (Update) → `reforge --copilot --update .` works
4. Add US3 (Remove) → `reforge --remove .` cleans Copilot artifacts
5. Add US4 (Coexistence) → Claude + Copilot side by side
6. Polish → Edge cases, docs, final validation

---

## Notes

- [P] tasks = different files or different code sections, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story is independently completable and testable
- Tests are written first (TDD pattern matches existing test suite)
- Commit after each phase completion
- Stop at any checkpoint to validate story independently
