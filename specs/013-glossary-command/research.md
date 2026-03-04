# Research: Glossary Command

**Feature**: 013-glossary-command | **Date**: 2026-02-23

## R-001: Agent-Agnostic Team Orchestration

**Decision**: Team orchestration is an optional enhancement with mandatory sequential fallback.

**Rationale**: Constitution Principle V (Agent-Agnostic Design) states commands "MUST use only common tool patterns: file read, file write, glob, grep, directory listing" and "MUST NOT depend on agent-specific features." TeamCreate, Task, SendMessage are Claude Code-specific tools unavailable to Copilot, Cursor, or Gemini. Expressing team orchestration as optional preserves the core workflow for all agents while allowing Claude Code to accelerate via parallelism.

**Alternatives considered**:
- Hard dependency on team tools → Rejected: violates Principle V
- Remove parallelism entirely → Rejected: significant performance loss for capable agents
- Abstract team API in a script → Rejected: violates Principle I (no compiled code), Principle IV (no runtime dependencies)

**Implementation pattern**: "Conditional Capability with Optional Enhancement" — core template describes sequential zone-by-zone processing; a clearly marked optional section provides parallel instructions for agents with team orchestration support. Output is identical regardless of execution path.

## R-002: Phase 2 External Verification Mechanism

**Decision**: Phase 2 uses the agent's WebSearch tool to look up acronyms against public sources (Wikipedia, industry glossaries, official documentation).

**Rationale**: Reforge is LLM-native with zero dependencies. WebSearch is a common agent capability that provides real external evidence without requiring API keys or compiled code. The `--skip-external` flag skips Phase 2 entirely for air-gapped environments where WebSearch is unavailable.

**Alternatives considered**:
- LLM knowledge only → Rejected: no external evidence, defeats verification purpose
- Context7 MCP → Rejected: agent-specific, limited to library docs not domain terms
- Configurable fallback chain → Rejected: over-engineered; skip-external covers the gap

## R-003: Template Architecture (Parent + Per-Phase)

**Decision**: Parent orchestrator (`glossary.md`) dispatches to per-phase templates (`glossary-phase-1.md` through `glossary-phase-4.md`).

**Rationale**: Each phase has fundamentally different tool requirements (Phase 1: Read/Glob, Phase 2: WebSearch, Phase 3: Grep, Phase 4: Read/Grep). Separate templates keep each phase focused and self-contained per Principle II. The parent orchestrator handles `--phase`, `--resume`, `--skip-external` flag routing and checkpoint management. This also makes `--phase N` trivial — the orchestrator loads only the requested phase template.

**Alternatives considered**:
- Single monolithic template → Rejected: would exceed reasonable template length (~1000+ lines), harder to maintain
- Per-phase templates without orchestrator → Rejected: no coordination for checkpoints, resume, or full pipeline execution

## R-004: Glossary Schema Design

**Decision**: Extend Reforge common-schema pattern. Glossary XML uses `<acronym-glossary>` root with `<entry>` children containing term, expansion, confidence, evidence chain, category, and verification status.

**Rationale**: Aligns with existing extraction schemas (business-rules.md, database.md) that all extend common-schema.md. Maintains consistency in output format, confidence vocabulary (high/medium/low mapped to numeric 0.0-1.0), and source traceability (`<source file="" line-start="" line-end="">`).

**Alternatives considered**:
- JSON-only output → Rejected: inconsistent with all other Reforge extractions (XML)
- Custom schema not extending common → Rejected: breaks cross-extraction tooling patterns

## R-005: Memory Lookup Format

**Decision**: JSON file at `.reforge/memory/glossary.json` keyed by acronym, containing expansion, confidence, and category.

**Rationale**: JSON is the natural format for a lookup table consumed by other commands at runtime. Other memory files (project-context.md, project-plan.md) use markdown, but those are human-readable context — the glossary lookup is machine-readable data optimized for fast key-value access by the LLM.

**Alternatives considered**:
- Markdown glossary table → Rejected: harder to parse programmatically, slower lookup
- XML (same as extraction output) → Rejected: redundant with acronym-glossary.xml, heavier for quick lookups
- Embedded in project-context.md → Rejected: mixes concerns, bloats context file

## R-006: Checkpoint and Resume Strategy

**Decision**: JSON checkpoint file at `.reforge/memory/checkpoints/glossary-checkpoint.json` containing completed phase number, current glossary version, entry count, and timestamp. Resume restarts the next incomplete phase from scratch (not mid-phase).

**Rationale**: Phase-level granularity is sufficient because each phase reads the previous phase's output file. Mid-phase resume would require serializing LLM state, which violates Principle I (no runtime dependencies). The glossary XML serves as the inter-phase contract — each phase reads and writes the same file with version increments.

**Alternatives considered**:
- Mid-phase resume with partial results → Rejected: requires stateful runtime, violates Principle I
- No resume at all → Rejected: spec requirement FR-003, multi-phase pipeline can be time-consuming

## R-007: Exclusion List Strategy

**Decision**: Static exclusion list embedded in the Phase 1 template as a categorized reference table. Categories: programming keywords (SQL, XML, JSON, HTTP, HTML, CSS, etc.), framework terms (per detected stack), and generic abbreviations (ID, URL, API, etc.).

**Rationale**: Constitution Principle I requires no external files beyond prompt templates. Embedding the list in the template keeps it self-contained and version-controlled. The list is intentionally static per the spec's out-of-scope declaration (no user-configurable exclusions).

**Alternatives considered**:
- External exclusion file in `.reforge/config.json` → Rejected: out of scope per clarification
- Dynamic exclusion based on framework detection → Rejected: over-engineered for v1

## R-008: Progress Reporting Pattern

**Decision**: Phase-level structured console output. Each phase reports: start banner with phase name, entry counts at completion, elapsed time, and verdict summary (e.g., "Phase 3 complete: 42 entries audited, 3 FABRICATED, 2 CORRECTED, 37 CONFIRMED — 4m 12s").

**Rationale**: Aligns with existing Reforge command patterns (extract.md Step 6 summary, analyze.md final report). Provides sufficient operator visibility without verbose per-entry output. Matches FR-025 requirement.

**Alternatives considered**:
- Per-entry real-time output → Rejected: too verbose, overwhelms console
- No progress reporting → Rejected: spec requirement FR-025
