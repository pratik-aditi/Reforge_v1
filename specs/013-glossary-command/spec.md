# Feature Specification: Glossary Command — Multi-Phase Acronym Extraction and Verification

**Feature Branch**: `013-glossary-command`
**Created**: 2026-02-23
**Status**: Draft
**Input**: SPEC-005 reference spec for `/reforge.glossary` command — multi-phase acronym/terminology extraction with agent-team verification, memory persistence, and cross-command integration
**Depends On**: `/reforge.extract`, `/reforge.audit`, existing analysis pipeline

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Run Full Glossary Extraction (Priority: P1)

An AI agent operator runs `/reforge.glossary` against an analyzed legacy codebase to produce a complete, verified acronym/terminology glossary. The command executes 4 phases sequentially: pattern extraction from source files, external verification against authoritative sources, source code audit with word-boundary grep, and an independent self-audit. The final glossary is persisted to memory for use by all other Reforge commands.

**Why this priority**: This is the core value proposition. Without a working end-to-end glossary pipeline, no other story delivers value. The 4-phase approach is what prevents hallucinated entries from propagating into generated documentation.

**Independent Test**: Can be fully tested by running `/reforge.glossary` on any analyzed codebase and verifying the output glossary XML, audit report, and memory file are all produced with valid structure.

**Acceptance Scenarios**:

1. **Given** an analyzed codebase with `analysis.xml` present, **When** the operator runs `/reforge.glossary`, **Then** the system produces `acronym-glossary.xml` with entries containing term, expansion, confidence score, evidence, and category for each discovered acronym.
2. **Given** a completed Phase 1 draft with some fabricated entries (zero occurrences in source), **When** Phase 3 (source code audit) executes, **Then** all fabricated entries are identified via word-boundary grep returning 0 matches and marked for deletion.
3. **Given** all 4 phases complete, **When** the operator checks `.reforge/memory/glossary.json`, **Then** the memory file exists with a lookup table keyed by acronym, containing expansion, confidence, and category for every surviving entry.

---

### User Story 2 - Run Individual Phases Independently (Priority: P2)

An operator who has already completed some phases (or wants to re-run a specific phase) runs `/reforge.glossary --phase 3` to execute only the source code audit phase. This allows targeted re-verification without repeating earlier work.

**Why this priority**: Phase-by-phase execution enables iterative refinement and recovery from interruptions. It is the primary mechanism for re-running verification after corrections.

**Independent Test**: Can be tested by running Phase 1 first, then running Phase 3 alone and verifying it processes the existing glossary without re-extracting.

**Acceptance Scenarios**:

1. **Given** a completed Phase 1 glossary exists, **When** the operator runs `/reforge.glossary --phase 3`, **Then** the system loads the existing glossary and performs source code audit on all entries without re-running extraction.
2. **Given** no existing glossary, **When** the operator runs `/reforge.glossary --phase 3`, **Then** the system reports an error indicating Phase 1 must be completed first.

---

### User Story 3 - Resume After Interruption (Priority: P2)

An operator whose glossary extraction was interrupted mid-phase resumes from the last checkpoint using `/reforge.glossary --resume`. The system picks up from where it left off without re-processing completed phases.

**Why this priority**: Multi-phase extraction can be time-consuming. Without resume capability, any interruption forces a full restart, wasting time and cost.

**Independent Test**: Can be tested by running Phase 1, interrupting during Phase 2, then running with `--resume` and verifying Phase 1 results are preserved.

**Acceptance Scenarios**:

1. **Given** Phase 1 completed and Phase 2 in progress with a saved checkpoint, **When** the operator runs `/reforge.glossary --resume`, **Then** Phase 1 results are preserved and Phase 2 restarts from its beginning.
2. **Given** no checkpoint file exists, **When** the operator runs `/reforge.glossary --resume`, **Then** the system reports that no checkpoint was found and offers to start from Phase 1.

---

### User Story 4 - Cross-Command Glossary Consumption (Priority: P3)

After a glossary is persisted to memory, other Reforge commands automatically consume it. `/reforge.generate` expands acronyms on first occurrence in each section. `/reforge.extract` annotates extracted items with full terminology. `/reforge.audit` uses glossary terms as verification targets. `/reforge.status` reports glossary version and entry count.

**Why this priority**: Cross-command consumption is the multiplier effect that makes the glossary infrastructure rather than just documentation. However, it depends on the glossary existing first (Stories 1-3).

**Independent Test**: Can be tested by creating a glossary, then running `/reforge.generate` and verifying the output documents expand acronyms on first use and include a glossary appendix.

**Acceptance Scenarios**:

1. **Given** a glossary with "TMDS" = "Train Management Dispatch System" is in memory, **When** the operator runs `/reforge.generate`, **Then** the first occurrence of "TMDS" in each document section is expanded to "TMDS (Train Management Dispatch System)" and subsequent occurrences use "TMDS" only.
2. **Given** no glossary file exists in memory, **When** the operator runs `/reforge.generate`, **Then** the command completes normally without glossary features (graceful degradation).

---

### User Story 5 - Air-Gapped Environment Support (Priority: P3)

An operator working in an air-gapped (no internet) environment runs `/reforge.glossary --skip-external` to skip Phase 2 (external verification) while still completing all other phases.

**Why this priority**: Supports environments where internet access is restricted. Phase 2 is valuable but not essential — Phases 3 and 4 catch fabricated entries independently.

**Independent Test**: Can be tested by running with `--skip-external` and verifying Phases 1, 3, and 4 complete, with Phase 2 skipped and noted in the output.

**Acceptance Scenarios**:

1. **Given** an analyzed codebase with no internet access, **When** the operator runs `/reforge.glossary --skip-external`, **Then** Phases 1, 3, and 4 complete successfully and the glossary version increments through v1.0.0, v1.2.0, v1.3.0 (skipping v1.1.0).

---

### Edge Cases

- What happens when the source codebase has no acronyms? The system should produce an empty glossary with zero entries and a warning, not an error.
- What happens when two agents discover the same acronym with different expansions? The lead agent deduplicates by keeping the entry with highest confidence and merging evidence from both.
- What happens when Phase 3 marks ALL entries as fabricated? The system should produce an empty glossary and warn the operator that no verified acronyms were found.
- What happens when the glossary memory file is corrupted or malformed? Other commands that consume the glossary should gracefully skip glossary features and warn the operator.
- What happens when `--team-size 1` is specified? The system should fall back to single-agent mode (no team orchestration) for each phase.
- What happens when a term exists in source code but has no explicit expansion (e.g., "TCOS" appears in code but its meaning is never spelled out)? Phase 3 marks the expansion as "UNVERIFIED" and caps confidence at 0.5.

## Clarifications

### Session 2026-02-23

- Q: How should Phase 2 perform external verification given the LLM-native framework? → A: Phase 2 uses the agent's WebSearch tool to look up acronyms against public sources (Wikipedia, industry glossaries, official docs). Falls back gracefully when WebSearch is unavailable (air-gapped), which is the mechanism behind `--skip-external`.
- Q: What is the measurable performance target for SC-003? → A: Under 15 minutes per phase (60 min total budget) for a 500-file codebase at default team size.
- Q: What should be explicitly out of scope? → A: Non-English term extraction, manual curation UI, user-defined custom exclusion lists, and glossary version history/diffing are all out of scope.
- Q: Single monolithic template or separate per-phase templates? → A: Parent orchestrator (`glossary.md`) + per-phase templates (`glossary-phase-1.md` through `glossary-phase-4.md`).
- Q: How should progress be reported during execution? → A: Phase-level reporting — each phase reports start/end with entry counts, elapsed time, and phase verdict summary.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a `/reforge.glossary` command that executes a 4-phase acronym extraction and verification pipeline
- **FR-002**: System MUST support running individual phases via `--phase <1|2|3|4|all>` parameter, defaulting to all phases
- **FR-003**: System MUST support resuming from a checkpoint via `--resume` flag, preserving completed phase results
- **FR-004**: Phase 1 (Pattern Extraction) MUST scan source files for uppercase identifiers, PascalCase prefixes, code comments, doc comments, enum definitions, region labels, string literals, and namespace declarations
- **FR-005**: Phase 1 SHOULD partition source files into zones and assign each zone to a separate worker agent for parallel processing when the agent supports team orchestration; otherwise the agent MUST process zones sequentially
- **FR-006**: Phase 1 MUST exclude common programming terms (SQL, XML, JSON, HTTP, etc.), framework terms, and generic abbreviations from extraction
- **FR-007**: Phase 2 (External Verification) MUST use the agent's WebSearch tool to look up each acronym against public authoritative sources (Wikipedia, industry glossaries, official documentation) and report verification status (CONFIRMED, CORRECTED, UNVERIFIED, NOT_FOUND)
- **FR-008**: Phase 2 MUST be skippable via `--skip-external` flag for air-gapped environments
- **FR-009**: Phase 3 (Source Code Audit) MUST verify every glossary entry using word-boundary grep (`\bTERM\b`) against all source files
- **FR-010**: Phase 3 MUST mark entries with zero grep matches as FABRICATED and recommend deletion
- **FR-011**: Phase 3 MUST reject LLM-authored files (CLAUDE.md, README.md, project-context.md, analysis.xml) as valid evidence sources for expansions
- **FR-012**: Phase 3 MUST mark entries where the term exists in code but no explicit expansion is found as UNVERIFIED, capping confidence at 0.5
- **FR-013**: Phase 4 (Self-Audit) MUST independently re-verify all entries modified in Phase 3 and all entries with confidence below 1.0
- **FR-014**: Phase 4 MUST check for hallucinated occurrence counts by independently re-running word-boundary grep
- **FR-015**: The lead agent MUST deduplicate entries discovered by multiple worker agents, keeping the highest-confidence entry and merging evidence
- **FR-016**: System MUST persist the final glossary to memory as a lookup file consumed by all other Reforge commands
- **FR-017**: System MUST produce an audit report documenting all corrections, deletions, and verification findings from Phases 3-4
- **FR-018**: System MUST save checkpoints after each phase to enable resume capability
- **FR-019**: System MUST clean up checkpoint files and team resources upon successful completion
- **FR-020**: System MUST support configurable team size via `--team-size <n>` parameter (range: 1-6, default: 3)
- **FR-021**: Templates SHOULD recommend cost-appropriate model tiers (fast/cheap models for pattern matching phases, accurate models for verification phases) but MUST NOT depend on specific model selection, as model tier is controlled by the agent runtime
- **FR-022**: Other Reforge commands (`/reforge.extract`, `/reforge.generate`, `/reforge.audit`, `/reforge.status`) MUST consume the glossary from memory when available
- **FR-023**: Other Reforge commands MUST gracefully degrade when no glossary is available in memory
- **FR-024**: `/reforge.generate` MUST expand acronyms on first occurrence in each document section and include a glossary appendix
- **FR-025**: System MUST report phase-level progress to the operator: phase start/end, entry counts, elapsed time, and phase verdict summary (e.g., "Phase 3 complete: 42 entries audited, 3 FABRICATED, 2 CORRECTED, 37 CONFIRMED — 4m 12s")

### Key Entities

- **Glossary Entry**: An acronym/abbreviation with its expansion, confidence score (0.0-1.0), evidence chain (file, line, evidence type), category, and verification status
- **Glossary Version**: Semantic version tracking the glossary through each phase (v1.0.0 draft, v1.1.0 verified, v1.2.0 audited, v1.3.0 final)
- **Audit Finding**: A verification result for a single entry containing verdict (CONFIRMED, CORRECTED, FABRICATED, UNVERIFIABLE), grep count, evidence details, and recommended action
- **Checkpoint**: A phase-level save state containing completed phase number, entry count, team status, and timestamp
- **Memory Lookup**: A persistent key-value store mapping acronyms to their expansion, confidence, and category for cross-command consumption

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All fabricated entries (terms with zero word-boundary grep matches) are identified and removed by the end of Phase 3, achieving 100% detection rate for entries with no source code presence
- **SC-002**: The final glossary accuracy exceeds 95% (fewer than 5% of entries have incorrect expansions after all 4 phases)
- **SC-003**: Each glossary phase completes within 15 minutes (60 minutes total budget for all 4 phases) for codebases of up to 500 source files when using default team size
- **SC-004**: The glossary memory file is consumable by all other Reforge commands within 10 seconds of loading, with no manual configuration required
- **SC-005**: Resume from checkpoint preserves 100% of completed phase results with no re-processing of finished phases
- **SC-006**: Cross-command integration produces consistent terminology across all generated documents — every acronym is expanded on first occurrence in each section
- **SC-007**: The operator can complete a full glossary workflow (extract, verify, audit, persist) without manual intervention between phases when running `--phase all`
- **SC-008**: Air-gapped environments can produce a verified glossary (Phases 1, 3, 4) without any internet-dependent steps

## Assumptions

- The target codebase has already been analyzed via `/reforge.analyze` and `analysis.xml` is available
- The AI agent runtime supports spawning multiple sub-agents (team orchestration) for parallel phase execution
- Source code files contain enough context (comments, doc comments, namespace declarations) to identify at least some acronym expansions
- Common programming and framework terms are well-defined and can be excluded via a static exclusion list
- The memory file format (JSON lookup table) is sufficient for cross-command consumption without requiring a database
- Version numbering follows the pattern established in the TCOS-RUMO evidence (v1.0.0 through v1.3.0 for 4 phases)
- Implementation uses a parent orchestrator template (`glossary.md`) that dispatches to per-phase templates (`glossary-phase-1.md` through `glossary-phase-4.md`), enabling `--phase N` to invoke only the relevant template

## Out of Scope

- **Non-English term extraction**: Glossary extraction targets English-language acronyms and abbreviations only
- **Manual curation UI**: No interactive editing interface for glossary entries; corrections are made by re-running phases
- **User-defined custom exclusion lists**: The exclusion list (common programming/framework terms) is static and built into the template; user-configurable exclusions are deferred
- **Glossary version history/diffing**: No mechanism to compare glossary versions across runs or track entry-level change history

## Dependencies

- `/reforge.analyze` must have been run to produce `analysis.xml` (prerequisite for Phase 1 file partitioning)
- `/reforge.audit` command template (for audit report schema compatibility)
- `.reforge/memory/` directory must be writable for glossary persistence and checkpoint storage
- Agent team orchestration capabilities (TeamCreate, Task, SendMessage, TaskCreate, TaskUpdate, TeamDelete) — **optional**: enables parallel processing; sequential fallback when unavailable per Constitution Principle V
