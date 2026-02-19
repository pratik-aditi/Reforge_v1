# Tasks: Extraction Profiles Command

**Input**: Design documents from `/specs/007-extraction-profiles/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, quickstart.md

**Tests**: No formal test tasks — verification is inline per user story via grep-based checks on `.reforge/commands/profile.md` and `.reforge/commands/extract.md`.

**Organization**: Tasks are grouped by user story. Two files are affected: `.reforge/commands/profile.md` (new) and `.reforge/commands/extract.md` (modified). US1 and US2 target different files and can run in parallel. US3-US5 enhance profile.md and should run sequentially after US1.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **New file**: `.reforge/commands/profile.md` — the new `/reforge.profile` command template
- **Modified file**: `.reforge/commands/extract.md` — remove hardcoded language rules, add profile loading
- **Runtime output**: `.reforge/memory/extraction-profile.md` — generated when user runs the command
- **Reference files**: `.reforge/commands/init.md` (interactive pattern), `.reforge/commands/analyze.md` (file extension mapping at lines 323-359)

---

## Phase 1: Setup

**Purpose**: Verify the target file states and load reference patterns before any modifications begin.

- [x] T001 Verify `.reforge/commands/extract.md` exists at ~1048 lines, confirm "Language-Specific Extraction Rules" header at ~line 979, and confirm "Step 0.5: Load Project Context" at ~line 70
- [x] T002 [P] Read `.reforge/commands/init.md` to load the interactive command pattern (Steps 1-9), and read `.reforge/commands/analyze.md` lines 323-359 to load the file extension-to-language mapping for auto-discovery reference

**Checkpoint**: Starting state verified — reference patterns loaded. Implementation can begin.

---

## Phase 3: User Story 1 - Generate Extraction Profile from Tech Stack Declaration (Priority: P1) 🎯 MVP

**Goal**: Create the `/reforge.profile` command that lets users declare languages (or auto-discover them) and generates a tailored extraction profile stored in memory.

**Independent Test**: Run `/reforge.profile` with a tech stack declaration, then verify `.reforge/memory/extraction-profile.md` exists with language-specific sections.

### Implementation for User Story 1

- [x] T003 [US1] Create `.reforge/commands/profile.md` with command header (`# /reforge.profile`), command syntax section (`/reforge.profile [--update]`), arguments table, overview, Step 0 (check `.reforge/memory/` directory exists), and Step 0.5 (load project context — standard pattern from init.md)
- [x] T004 [US1] Write Step 1 (check existing profile — if `.reforge/memory/extraction-profile.md` exists and no `--update` flag, ask user whether to update or replace) and Step 2 (gather languages — interactive declaration with auto-discovery via Glob using the expanded file extension mapping from data-model.md covering modern, web/scripting, legacy/enterprise, systems, functional, and data languages; include catch-all instruction for the agent to identify any other source file extensions it recognizes; for ambiguous extensions like `.h` or `.m`, present disambiguation options to the user; users may also declare ANY language manually even if no files are found; present discovered languages with file counts for user confirmation) in `.reforge/commands/profile.md`
- [x] T005 [US1] Write Step 5 (generate profile — write structured markdown to `.reforge/memory/extraction-profile.md` with header metadata showing date/languages/architecture, `## Language-Specific Extraction Rules` with per-language subsections, and 5-category rule generation prompts that the LLM applies to ANY declared language from its training knowledge: type system quirks, operator differences, naming conventions, common pitfalls, framework patterns; no finite "supported languages" list — the LLM generates rules for COBOL, Fortran, Assembly, FoxPro, RPG, or any other language the same way it does for C# or Python) and Step 6 (display summary of generated profile, suggest running `/reforge.extract`) in `.reforge/commands/profile.md`
- [x] T006 [US1] Verify US1 success criteria in `.reforge/commands/profile.md`: file exists; `grep "reforge.profile"` returns match; `grep -i "auto-discover\|Glob"` returns match for auto-discovery; `grep "extraction-profile.md"` returns match for output path; `grep "Step 2"` returns match for language gathering

**Checkpoint**: US1 complete — profile command generates language-specific extraction profiles with auto-discovery.

---

## Phase 4: User Story 2 - Extract Command Loads and Applies Profile (Priority: P1)

**Goal**: Modify the extract command to load the extraction profile from memory and remove the hardcoded language-specific rules.

**Independent Test**: Verify extract.md no longer contains "Language-Specific Extraction Rules" and contains a directive to load the extraction profile.

### Implementation for User Story 2

- [x] T007 [US2] Remove the "Language-Specific Extraction Rules" section from `.reforge/commands/extract.md` — delete from `## Language-Specific Extraction Rules` (line ~979) through the trailing `---` separator (line ~1002), approximately 24 lines total
- [x] T008 [US2] Insert "Step 0.6: Load Extraction Profile" after the existing Step 0.5 block (~after line 77) in `.reforge/commands/extract.md` — add directive to load `.reforge/memory/extraction-profile.md` when present, with bullet points for Language Rules, Architecture Guidance, Framework Patterns, Custom Notes; include suggestion to run `/reforge.profile` when no profile exists
- [x] T009 [US2] Verify US2 success criteria in `.reforge/commands/extract.md`: `grep "Language-Specific Extraction Rules"` returns 0 matches; `grep "extraction-profile.md"` returns match; `grep "Load Extraction Profile"` returns match; `grep "reforge.profile"` returns match (in suggestion text)

**Checkpoint**: US2 complete — extract command loads profile from memory, hardcoded language rules removed. Both P1 stories done.

---

## Phase 5: User Story 3 - Declare Architecture Patterns for Extraction Guidance (Priority: P2)

**Goal**: Add architecture pattern gathering and architecture-specific extraction guidance generation to the profile command.

**Independent Test**: Run `/reforge.profile` declaring architecture patterns, verify the profile contains architecture-specific guidance sections.

### Implementation for User Story 3

- [x] T010 [US3] Write Step 3 (gather architecture patterns — ask user about architectural styles used in the codebase: layered/n-tier, microservices, event-driven, repository pattern, service bus, MVC, etc.; for each declared pattern, the agent generates guidance about where business rules, data access, workflows, and integration points typically reside) in `.reforge/commands/profile.md`
- [x] T011 [US3] Add `## Architecture-Specific Extraction Guidance` output section to the profile output template in Step 5 of `.reforge/commands/profile.md` — include per-pattern subsections with guidance on business rule locations, data access patterns, cross-layer call tracing, and workflow locations
- [x] T012 [US3] Verify US3 success criteria in `.reforge/commands/profile.md`: `grep "Step 3"` returns match for architecture gathering; `grep -i "architecture"` returns ≥3 matches; architecture output section present in Step 5 template

**Checkpoint**: US3 complete — architecture-specific extraction guidance in place.

---

## Phase 6: User Story 4 - Update Existing Profile (Priority: P2)

**Goal**: Add `--update` mode that preserves existing profile content while allowing additions and removals.

**Independent Test**: Verify profile.md documents --update flag handling with preservation logic.

### Implementation for User Story 4

- [x] T013 [US4] Enhance Steps 1 and 2 in `.reforge/commands/profile.md` with `--update` mode logic — Step 1: when `--update` flag is present, load existing profile and parse current languages/architecture/notes; Step 2: present current languages, allow user to add new ones or mark existing ones for removal; preserve all unchanged sections and custom notes when regenerating
- [x] T014 [US4] Verify US4 success criteria in `.reforge/commands/profile.md`: `grep "\-\-update"` returns ≥3 matches; `grep -i "preserve\|existing"` returns match confirming preservation logic documented

**Checkpoint**: US4 complete — update mode with content preservation in place. Both P2 stories done.

---

## Phase 7: User Story 5 - Add Custom Extraction Notes (Priority: P3)

**Goal**: Add custom extraction notes gathering and output to the profile command.

**Independent Test**: Verify profile.md contains Step 4 for custom notes and the profile output template includes a custom notes section.

### Implementation for User Story 5

- [x] T015 [US5] Write Step 4 (gather custom extraction notes — free-form user input for project-specific guidance: internal naming conventions, proprietary framework patterns, known code smells, directory organization hints, or any other extraction-relevant guidance the user wants to provide) in `.reforge/commands/profile.md`
- [x] T016 [US5] Add `## Custom Extraction Notes` output section to the profile output template in Step 5 of `.reforge/commands/profile.md` — user-provided notes rendered as bullet points in the generated profile
- [x] T017 [US5] Verify US5 success criteria in `.reforge/commands/profile.md`: `grep "Step 4"` returns match for custom notes gathering; `grep -i "custom.*notes\|custom.*extraction"` returns ≥2 matches; custom notes output section present in Step 5 template

**Checkpoint**: US5 complete — custom extraction notes in place. All stories done.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Full acceptance verification across all user stories, structural integrity checks, and compliance validation.

- [x] T018 [P] Verify agent-agnostic language compliance in `.reforge/commands/profile.md` — confirm no agent-specific names (Claude, Copilot, etc.), only "the agent", "you", or "the LLM" per Constitution Principle V
- [x] T019 [P] Verify markdown structure integrity in `.reforge/commands/profile.md` — confirm all code blocks (triple backtick) properly opened/closed, no orphaned blocks, section heading hierarchy intact (Steps 0-6 in order)
- [x] T020 Run all quickstart.md validation steps on `.reforge/commands/profile.md` and `.reforge/commands/extract.md` — verify all 8 success criteria checks pass

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **US1 (Phase 3)** and **US2 (Phase 4)**: Both depend on Setup only — can run **in parallel** (different files)
- **US3 (Phase 5)**: Depends on US1 (profile.md must exist before enhancing it)
- **US4 (Phase 6)**: Depends on US1 (modifies Steps 1-2 created by US1)
- **US5 (Phase 7)**: Depends on US1 (adds Step 4 to profile.md)
- **Polish (Phase 8)**: Depends on ALL user stories being complete

### User Story Dependencies

- **US1 (P1)**: No dependencies on other stories — can start after Setup
- **US2 (P1)**: No dependencies on other stories — can start after Setup; **parallel with US1** (different file)
- **US3 (P2)**: Depends on US1 (adds to profile.md created by US1)
- **US4 (P2)**: Depends on US1 (enhances Steps 1-2 in profile.md)
- **US5 (P3)**: Depends on US1 (adds Step 4 to profile.md)

### Within extract.md (US2)

Operations should be applied **bottom-to-top** to preserve line number accuracy:
1. First: Remove Language-Specific section (~line 979) — T007
2. Then: Insert Step 0.6 (~after line 77) — T008

### Parallel Opportunities

- T001 and T002 (Setup) can run in parallel
- US1 (T003-T006) and US2 (T007-T009) can run in parallel (different files)
- US3 (T010-T012), US4 (T013-T014), US5 (T015-T017) are sequential (same file) but independent of US2
- T018 and T019 (Polish) can run in parallel
- Per-story verification tasks (T006, T009, T012, T014, T017) are independent of each other

---

## Parallel Example: MVP Phase (US1 + US2)

```bash
# After Setup completes, launch US1 and US2 in parallel:
Task: "Create profile.md command template (US1: T003-T005)"
Task: "Modify extract.md — remove language rules and add profile loading (US2: T007-T008)"

# Then verify both stories:
Task: "Verify US1 success criteria (T006)"
Task: "Verify US2 success criteria (T009)"
```

---

## Implementation Strategy

### MVP First (US1 + US2 Only)

1. Complete Phase 1: Setup — verify file states, load reference patterns
2. Complete Phase 3: US1 — create profile.md with language gathering and auto-discovery
3. Complete Phase 4: US2 — modify extract.md to load profile and remove hardcoded rules
4. **STOP and VALIDATE**: Run T006 + T009 to confirm both P1 stories pass
5. The profile command is functional and the extract command loads profiles

### Incremental Delivery

1. Setup → Verify state
2. US1 + US2 (P1) → Profile generation + extract integration → MVP complete
3. US3 + US4 (P2) → Architecture patterns + update mode → Full profile management
4. US5 (P3) → Custom notes → Complete feature
5. Polish → Full acceptance verification

### Single-Implementer Strategy (Recommended)

Since profile.md is one new file and extract.md has only 2 small operations:

1. Complete Setup (T001-T002)
2. Create profile.md incrementally (T003-T005), then verify (T006)
3. Modify extract.md bottom-to-top (T007-T008), then verify (T009)
4. Enhance profile.md with architecture, update mode, custom notes (T010-T017)
5. Run polish verification (T018-T020)

---

## Notes

- Two files affected: `.reforge/commands/profile.md` (new, ~200-300 lines) and `.reforge/commands/extract.md` (2 operations: remove ~24 lines, insert ~12 lines)
- Profile.md follows the interactive Q&A pattern from init.md — use it as a structural reference
- Auto-discovery uses the file extension mapping from analyze.md lines 323-359 — reference it for consistency
- Use agent-agnostic language: "the agent MUST", "you MUST" — not "Claude", "Copilot"
- Bottom-to-top execution order for extract.md operations (remove at line 979 before inserting at line 77)
- If line numbers don't match at implementation time, use semantic anchors (section headers)
- Commit after each completed user story phase
- Total: 20 tasks (2 setup + 4 US1 + 3 US2 + 3 US3 + 2 US4 + 3 US5 + 3 polish)
- Task count per story: US1=4, US2=3, US3=3, US4=2, US5=3
