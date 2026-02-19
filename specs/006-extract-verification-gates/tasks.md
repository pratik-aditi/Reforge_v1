# Tasks: Extract Verification Gates

**Input**: Design documents from `/specs/006-extract-verification-gates/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, quickstart.md

**Tests**: No formal test tasks — verification is inline per user story via grep-based checks on `.reforge/commands/extract.md`.

**Organization**: Tasks are grouped by user story. All modifications target a single file (`.reforge/commands/extract.md`). See Dependencies section for the recommended bottom-to-top execution order that preserves line number accuracy across operations.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single file**: `.reforge/commands/extract.md` — all 13 modification operations target this file
- **Source text**: `/Users/ryanhilliard/clients/wabtec/tcos/reforge_output/TCOS-RUMO/specs/SPEC-001-extract-verification-gates.md` — provides exact markdown to insert

---

## Phase 1: Setup

**Purpose**: Verify the target file state matches expectations from research.md before any modifications begin.

- [x] T001 Verify `.reforge/commands/extract.md` exists and has ~841 lines via `wc -l`
- [x] T002 [P] Verify all 13 anchor points in `.reforge/commands/extract.md` per research.md line number table (grep for section headers at expected lines: "Step 3: Extract Rule Details" at 153, "Optional Validation" at 815, etc.)
- [x] T003 [P] Read SPEC-001 source document at `/Users/ryanhilliard/clients/wabtec/tcos/reforge_output/TCOS-RUMO/specs/SPEC-001-extract-verification-gates.md` to load exact markdown text for all 13 insertion operations

**Checkpoint**: Starting state verified — all anchor points confirmed, source text loaded. Modifications can begin.

---

## Phase 3: User Story 1 - Verbatim Identifier Extraction (Priority: P1) 🎯 MVP

**Goal**: Ensure all identifiers (class names, method names, enum members, file names, etc.) are copied character-for-character from source code, with prohibited fabrication patterns documented and file/snippet fidelity enforced.

**Independent Test**: Run `/reforge.extract business-rules` on a codebase with enums, then grep every extracted identifier against source. Every identifier must match.

### Implementation for User Story 1

- [x] T004 [US1] Append read-before-describe mandate (FR-002) to Step 1 "Load Analysis" after line 84 in `.reforge/commands/extract.md` — insert CRITICAL directive requiring file reads via Read tool in current session before extraction (Op 13, REQ-EXT-010)
- [x] T005 [US1/US3] Insert "Enumeration and Constant Patterns" section (FR-003) after line 151 (end of Constraint Patterns block) in `.reforge/commands/extract.md` — add enum/constant detection patterns with 7-point extraction protocol (Op 12, REQ-EXT-002). Note: serves both US1 (verbatim enum names) and US3 (type-aware enum extraction); placed in US1 phase for MVP delivery.
- [x] T006 [US1] Insert "Step 2.5: Verbatim Extraction Rules" section (FR-001, FR-015) after Enumeration Patterns, before Step 3 in `.reforge/commands/extract.md` — add verbatim copy mandate, identifier list, verification requirement, and prohibited patterns list with ≥5 entries (Op 11, REQ-EXT-001)
- [x] T007 [US1] Insert method name accuracy text (FR-007) in Workflow Step 2 after line 683 ("Note return values used") in `.reforge/commands/extract.md` — add 4 bullet points: exact method names, actual parameters, Grep verification, call site recording (Op 6, REQ-EXT-006)
- [x] T008 [US1] Append file existence gate (FR-006) to Source References section after line 797 in `.reforge/commands/extract.md` — add Glob/Read confirmation requirement before writing any `file` attribute, plus common fabrication patterns list (Op 4, REQ-EXT-004)
- [x] T009 [US1] Append snippet fidelity requirements (FR-008) to Source References section after line 797 in `.reforge/commands/extract.md` — mandate verbatim copies from Read tool output with no reformatting or simplification (Op 3, REQ-EXT-007)
- [x] T010 [US1] Verify US1 success criteria in `.reforge/commands/extract.md`: `grep -c "verbatim"` returns ≥3; `grep "Prohibited patterns"` returns match; `grep "Step 2.5"` returns match; file existence gate text present in Source References section

**Checkpoint**: US1 complete — verbatim extraction mandate, prohibited patterns, file existence gate, and snippet fidelity all in place.

---

## Phase 4: User Story 2 - Post-Extraction Source Verification (Priority: P1)

**Goal**: Add mandatory post-extraction verification step and make validation required (not optional), ensuring extracted content is verified against source before output is finalized.

**Independent Test**: After extraction, confirm Step 5.5 executes with ≥20% source file re-reads (min 5 items) and 100% enum verification. "Optional Validation" no longer exists.

### Implementation for User Story 2

- [x] T011 [US2] Insert "Step 5.5: Post-Extraction Verification" section (FR-004, FR-005) between Step 5 "Generate Output" (line 236) and Step 6 "Report Results" (line 238) in `.reforge/commands/extract.md` — add 5 sub-sections: A. Source File Existence, B. Identifier Sampling (20%, min 5), C. Line Number Accuracy, D. Enum/Constant Full Verification (100%), E. Cross-Reference Consistency (Op 7, REQ-EXT-003)
- [x] T012 [US2] Replace "Optional Validation" header and intro (lines 815-817) with "Required Validation" in `.reforge/commands/extract.md`, add content validation subsection alongside structural XSD validation, and append XSD limitation documentation noting XSD checks structure only (FR-013, FR-014) (Op 1, REQ-EXT-003/REQ-EXT-012)
- [x] T013 [US2] Verify US2 success criteria in `.reforge/commands/extract.md`: `grep "Step 5.5"` returns match; `grep "Required Validation"` returns match; `grep "Optional Validation"` returns 0 matches; XSD limitation text present

**Checkpoint**: US2 complete — post-extraction verification gate and mandatory validation in place. Both P1 stories done.

---

## Phase 5: User Story 3 - Type-Aware Enum Extraction (Priority: P2)

**Goal**: Ensure enum/constant extraction captures declared types accurately and aggregation counts are explicit, preventing type misrepresentation and arithmetic errors.

**Independent Test**: Extract from code with `Enumeration(Of String, T)` pattern and verify string-typed values recorded (not fabricated integers). Verify count attributes match explicit member counts.

### Implementation for User Story 3

- [x] T014 [US3] Insert type preservation text (FR-003 part 2) in Step 3 sub-step 1 after line 160 ("Identify any else/default cases") in `.reforge/commands/extract.md` — add 2 bullet points on preserving data types from declarations and including type declarations in snippets (Op 10, REQ-EXT-002)
- [x] T015 [US3] Insert aggregation accuracy requirements (FR-012) in Step 5 after line 195 ("Write to $EXTRACTIONS_DIR/business-rules.xml:") in `.reforge/commands/extract.md` — add explicit counting mandate with category sub-counts summing to totals (Op 8, REQ-EXT-011)
- [x] T016 [US3] Verify US3 success criteria in `.reforge/commands/extract.md`: type preservation bullets present after Step 3 sub-step 1; aggregation accuracy block present in Step 5

**Checkpoint**: US3 complete — type-aware extraction and aggregation accuracy in place.

---

## Phase 6: User Story 4 - Protocol and Security Extraction Accuracy (Priority: P2)

**Goal**: Prevent textbook-pattern substitution for protocols, authentication, and security descriptions by requiring actual code flow tracing.

**Independent Test**: Extract a security workflow and verify the description matches what the code does (e.g., "client-side HMAC-SHA1 signing"), not what the technology generally does (e.g., "challenge-response authentication").

### Implementation for User Story 4

- [x] T017 [US4] Insert "Step 3a: Technical Mechanism Accuracy" section (FR-010) after line 182 (adjusted from SPEC-001's line 186 per research findings) in `.reforge/commands/extract.md` — add directive text with domain-specific guidance for auth, protocols, and external APIs, plus self-check rule (Op 9, REQ-EXT-005)
- [x] T018 [US4] Verify US4 success criteria in `.reforge/commands/extract.md`: `grep "Step 3a"` returns match; `grep "Technical Mechanism"` returns match

**Checkpoint**: US4 complete — protocol accuracy gate in place. Both P2 stories done.

---

## Phase 7: User Story 5 - Language-Specific Extraction Accuracy (Priority: P3)

**Goal**: Add language quirk reference covering VB.NET and C# specific behaviors that cause subtle extraction errors.

**Independent Test**: Verify the new section exists with ≥6 VB.NET items (array bounds, OrElse/AndAlso, custom enum patterns, Option Strict, Nothing vs null, etc.) and ≥4 C# items.

### Implementation for User Story 5

- [x] T019 [US5] Insert "Language-Specific Extraction Rules" section (FR-011) after line 812 (end of Common Elements) in `.reforge/commands/extract.md` — add per-language subsections for VB.NET (≥6 items), C# (≥4 items), and General (≥3 items) covering array bounds, boolean operators, custom enum patterns, and other quirks (Op 2, REQ-EXT-009)
- [x] T020 [US5] Verify US5 success criteria in `.reforge/commands/extract.md`: `grep "Language-Specific Extraction Rules"` returns match; VB.NET subsection has ≥6 items; C# subsection has ≥4 items

**Checkpoint**: US5 complete — language quirk reference in place.

---

## Phase 8: User Story 6 - Confidence Level Reflects Verification (Priority: P3)

**Goal**: Redefine confidence levels so `high` requires source verification, `medium` indicates partial verification, and `low` indicates unverified/memory-based extraction.

**Independent Test**: Verify the confidence table includes "verified against source code" as a criterion for `high` confidence.

### Implementation for User Story 6

- [x] T021 [US6] Replace Confidence Levels table (lines 785-789) with verification-based criteria in `.reforge/commands/extract.md` — replace three-row table + add IMPORTANT note that confidence reflects verification status, not pattern clarity (FR-009) (Op 5, REQ-EXT-008)
- [x] T022 [US6] Verify US6 success criteria in `.reforge/commands/extract.md`: `grep "verified against source code"` returns match in confidence table

**Checkpoint**: US6 complete — verification-based confidence levels in place. All P3 stories done.

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Full acceptance verification across all user stories, structural integrity checks, and compliance validation.

- [x] T023 Run full acceptance criteria verification (AC-001 through AC-012 from SPEC-001 Section 5) on `.reforge/commands/extract.md`. For SC-004, trace each of the 8 extraction-phase errors (C1, H1, H2, M1, M2, M4, M5, M8) to the specific inserted gate that prevents it. Also verify that inserted Step 5.5 and Step 2.5 text addresses spec edge cases: large files, deleted files, 100+ member enums, grep-zero-results recovery, and >50% verification failure escalation.
- [x] T024 Run all quickstart.md validation steps on `.reforge/commands/extract.md`
- [x] T025 Verify agent-agnostic language compliance in `.reforge/commands/extract.md` — confirm no agent-specific names (Claude, Copilot, etc.), only "the agent", "you", or "the LLM" per Constitution Principle V
- [x] T026 Verify markdown structure integrity in `.reforge/commands/extract.md` — confirm all code blocks (triple backtick) properly opened/closed, no orphaned blocks, section heading hierarchy intact

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **User Stories (Phase 3-8)**: All depend on Setup (Phase 1) completion
  - US1 and US2 (P1) are highest priority — implement first
  - US3 and US4 (P2) follow P1 stories
  - US5 and US6 (P3) follow P2 stories
- **Polish (Phase 9)**: Depends on ALL user stories being complete

### ⚠️ CRITICAL: Bottom-to-Top Execution Order

All 13 operations modify the same file (`.reforge/commands/extract.md`). To preserve line number accuracy, operations **MUST** be applied bottom-to-top within the file. The recommended execution order across user stories is:

| Exec Order | Task | Operation | Story | Target Line | Description |
|------------|------|-----------|-------|-------------|-------------|
| 1 | T012 | Op 1 | US2 | 815-817 | Replace Optional→Required Validation |
| 2 | T019 | Op 2 | US5 | after 812 | Insert Language-Specific Rules |
| 3 | T009 | Op 3 | US1 | after 797 | Append snippet fidelity |
| 4 | T008 | Op 4 | US1 | after 797 | Append file existence gate |
| 5 | T021 | Op 5 | US6 | 785-789 | Replace Confidence table |
| 6 | T007 | Op 6 | US1 | after 683 | Insert method name accuracy |
| 7 | T011 | Op 7 | US2 | 236-238 | Insert Step 5.5 verification |
| 8 | T015 | Op 8 | US3 | after 195 | Insert aggregation accuracy |
| 9 | T017 | Op 9 | US4 | after 182 | Insert Step 3a technical accuracy |
| 10 | T014 | Op 10 | US3 | after 160 | Insert type preservation |
| 11 | T006 | Op 11 | US1 | after 151 | Insert Step 2.5 verbatim rules |
| 12 | T005 | Op 12 | US1/US3 | after 151 | Insert Enum patterns |
| 13 | T004 | Op 13 | US1 | after 84 | Append read-before-describe |

**Alternative**: If using semantic anchors (section headers) instead of line numbers to locate insertion points, operations can be applied in any order. The bottom-to-top order is required only when using absolute line number references.

### User Story Dependencies

- **US1 (P1)**: No dependencies on other stories — can start after Setup
- **US2 (P1)**: No dependencies on other stories — can start after Setup
- **US3 (P2)**: No dependencies on US1/US2 — can start after Setup (but recommended after P1)
- **US4 (P2)**: No dependencies on other stories — can start after Setup (but recommended after P1)
- **US5 (P3)**: No dependencies on other stories — can start after Setup (but recommended after P2)
- **US6 (P3)**: No dependencies on other stories — can start after Setup (but recommended after P2)

**Note**: While user stories are logically independent, the single-file constraint means the bottom-to-top execution order (above) interleaves tasks from different stories. Follow the execution order table for implementation; use the user story grouping for understanding and verification.

### Within Each User Story

- Implementation tasks before verification tasks
- Verification confirms the story's success criteria before proceeding
- All inserted text must come from SPEC-001 (no generated/paraphrased content)

### Parallel Opportunities

- T002 and T003 (Setup) can run in parallel
- Per-story verification tasks (T010, T013, T016, T018, T020, T022) are independent of each other
- Phase 9 polish tasks (T023-T026) can run in parallel after all stories complete

---

## Parallel Example: Setup Phase

```bash
# Launch verification and source loading in parallel:
Task: "Verify all 13 anchor points in .reforge/commands/extract.md"
Task: "Read SPEC-001 source document to load exact insertion text"
```

---

## Implementation Strategy

### MVP First (US1 + US2 Only)

1. Complete Phase 1: Setup — verify target file state
2. Complete Phase 3: US1 — verbatim extraction mandate, prohibited patterns, file/snippet fidelity
3. Complete Phase 4: US2 — post-extraction verification, mandatory validation
4. **STOP and VALIDATE**: Run T010 + T013 to confirm both P1 stories pass
5. These two stories address 10 of 13 verified errors from the failure taxonomy

### Incremental Delivery

1. Setup → Verify state
2. US1 + US2 (P1) → Verbatim extraction + Post-verification → Validates against 10/13 errors
3. US3 + US4 (P2) → Type-aware enums + Protocol accuracy → Validates remaining type/protocol errors
4. US5 + US6 (P3) → Language quirks + Confidence levels → Full coverage of all 13 errors
5. Polish → Full acceptance criteria verification

### Single-Implementer Strategy (Recommended)

Since all operations target one file, a single implementer should:

1. Complete Setup (T001-T003)
2. Follow the bottom-to-top execution order table (T012→T019→T009→...→T004)
3. Run per-story verifications after each story's tasks complete
4. Run full acceptance verification (Phase 9) at the end

---

## Notes

- All tasks target a single file: `.reforge/commands/extract.md`
- All inserted text MUST be copied from SPEC-001 — do not generate or paraphrase
- Use agent-agnostic language: "the agent MUST", "you MUST" — not "Claude", "Copilot"
- Line numbers are from research.md verification; one known drift: line 186→182 (Op 9)
- If line numbers don't match at implementation time, use semantic anchors (section headers)
- Commit after each completed user story phase
- Total: 26 tasks (3 setup + 17 implementation + 6 verification)
- Task count per story: US1=7, US2=3, US3=3, US4=2, US5=2, US6=2
