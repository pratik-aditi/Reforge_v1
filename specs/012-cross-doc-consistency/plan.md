# Implementation Plan: Cross-Document Consistency Checker

**Branch**: `012-cross-doc-consistency` | **Date**: 2026-02-23 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/012-cross-doc-consistency/spec.md`

## Summary

Add a persistent metrics registry and pattern-based consistency scanner to prevent and detect contradictory statistics across generated Reforge documents. The existing ephemeral canonical metrics table in `generate.md` becomes a persistent `metrics-registry.xml` file. The existing consistency audit workflow in `audit.md` is extended with registry-based scanning, tolerance rules, exclusion lists, and confidence-scored discrepancy reporting.

## Technical Context

**Language/Version**: Markdown prompt templates (no compiled code per Constitution Principle I)
**Primary Dependencies**: None — LLM-native tools only (Read, Write, Glob, Grep)
**Storage**: XML files (`metrics-registry.xml`, `consistency-audit-report.xml`, `correction-plan.xml`); structured markdown for command and schema definitions
**Testing**: Manual validation via sample legacy codebases; LLM-executed acceptance scenarios from spec
**Target Platform**: Any AI coding assistant (Claude Code, GitHub Copilot, etc.)
**Project Type**: Prompt template framework (no compiled source code)
**Performance Goals**: Registry computation + consistency scan completes in under 5 minutes for typical project (<100 generated docs, <50 metrics)
**Constraints**: Zero runtime dependencies; all analysis by LLM agent; XML output per Constitution Principle III
**Scale/Scope**: Typical project: <100 generated documents, <50 registered metrics, <500 numeric claims to scan

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Evidence |
|-----------|--------|----------|
| I. LLM-First Architecture | PASS | All registry computation performed by LLM using Read, Glob, Grep. No external parsers, no compiled code. Pattern-based extraction uses LLM reading comprehension, not compiled regex. |
| II. Prompt Template Commands | PASS | Changes are modifications to existing command templates (`audit.md`, `generate.md`). No new standalone commands created — consistency scanning is integrated into the existing audit command. |
| III. Structured Output (XML/Markdown) | PASS | New output (`metrics-registry.xml`) follows XML with defined schema in `.reforge/schemas/`. Source references and traceability maintained via metric IDs. |
| IV. Installable via CLI Bootstrap | PASS | New schema files are markdown in `.reforge/schemas/`. No new runtime dependencies. Framework remains fully functional with only AI agent present. |
| V. Agent-Agnostic Design | PASS | All instructions use "the agent MUST" language. No agent-specific features referenced. Pattern descriptions are human-readable, not agent-specific tool calls. |
| VI. Extensibility via Tooling Layer | PASS | Core workflow functions without optional tooling. Scan patterns are extensible via registry configuration. |

**Gate result**: ALL PASS — no violations to track.

## Project Structure

### Documentation (this feature)

```text
specs/012-cross-doc-consistency/
├── plan.md              # This file
├── spec.md              # Feature specification
├── research.md          # Phase 0: Research decisions
├── data-model.md        # Phase 1: Entity and schema design
├── quickstart.md        # Phase 1: Implementation quickstart
├── checklists/
│   └── requirements.md  # Spec quality checklist
└── tasks.md             # Phase 2 output (/speckit.tasks command)
```

### Source Code (repository root)

```text
.reforge/
├── commands/
│   ├── audit.md              # MODIFY: Extend consistency workflow with registry-based scanning
│   └── generate.md           # MODIFY: Persist metrics table, add post-generation scan
├── schemas/
│   ├── metrics-registry.md           # NEW: Schema for metrics-registry.xml
│   ├── consistency-audit-report.md   # MODIFY: Add metrics-registry-checks section
│   └── correction-plan.md           # MODIFY: Add metric-mismatch, unregistered-metric types
└── config.json                       # NO CHANGE (registry path derived from existing output dir)
```

**Structure Decision**: This feature modifies existing prompt templates and schemas in `.reforge/`. No new directories are created. The metrics registry XML file is a runtime output stored alongside existing project outputs at `$PROJECT_OUTPUT_DIR/metrics-registry.xml`.

## Implementation Approach

### Phase A: Schema Definitions (Foundation)

Define the data structures before modifying command workflows.

**A1. Create metrics-registry.md schema**
- New file: `.reforge/schemas/metrics-registry.md`
- Define root element, metric entry, breakdown, references, configuration, scan patterns, tolerance rules, exclusion list, qualifier patterns
- Follow existing schema documentation conventions (see `audit-report.md`, `correction-plan.md`)
- Include complete examples with real TCOS-RUMO data

**A2. Extend correction-plan.md schema**
- Add `metric-mismatch` and `unregistered-metric` to CorrectionType values table
- Add `metrics-consistency` to CategoryType values table (priority: after `cross-document`, before `generation`)
- Add example XML showing metric-mismatch corrections
- Update priority assignment rules section

**A3. Extend consistency-audit-report.md schema**
- Add `<metrics-registry-checks>` section with: total-claims-scanned, total-discrepancies, critical/warning/info counts, files-scanned, registry-version
- Add `<discrepancy>` element with full attributes (metric-id, registry-value, document-value, file, line, context, confidence, action, pattern-id, qualifier, tolerance-percent)
- Add `<scan-summary>` with per-file and per-metric verification summaries
- Add `<exclusions-applied>` section documenting suppressed patterns
- Include complete example XML

### Phase B: Command Template Modifications (Workflows)

Modify existing command templates to integrate the metrics registry.

**B1. Modify generate.md — Persist metrics registry**

Changes to the "Canonical Metrics Computation" section (lines 1056-1079):
1. **Change rule 4**: Replace "The computed metrics table is ephemeral — it exists in the agent's working context during the run and is not persisted as a separate file" with instructions to write `$PROJECT_OUTPUT_DIR/metrics-registry.xml` following the metrics-registry schema
2. **Add metric ID generation**: Each computed metric gets a deterministic ID following the `MET-{CATEGORY}-{NAME}` pattern
3. **Add breakdown recording**: For aggregate metrics with per-file components, record the breakdown in the registry
4. **Add registry read-back rule**: After writing the registry, all subsequent generation steps MUST read metric values from the registry file, not recompute them

Changes to "Content Validation Checklist" (lines 1106-1124):
5. **Add item 11**: "Metric ID annotations are present for every numeric statistic as HTML comments (`<!-- metric: MET-XXX -->`) or diagram comments (`' metric: MET-XXX`)"

New section at end of generate.md:
6. **"Post-Generation Consistency Scan" section**: After all documents are generated, the agent updates the `<references>` section of each metric in the registry, then runs a quick scan comparing embedded values against registry values. If critical discrepancies found, emit a WARNING with count and path to consistency report.

**B2. Modify audit.md — Extend consistency audit workflow**

The existing consistency audit workflow already performs arithmetic checks, cross-reference checks, duplicate ID detection, freshness checks, and cross-document checks. The following additions extend the workflow:

1. **New Step: Registry Recomputation**: Before any scanning, recompute the metrics registry from current extraction data (FR-015). This reuses the same computation logic as generate.md Step 0.7 but is independently executable.

2. **New Step: Pattern-Based Document Scanning**: For each file in `$PROJECT_OUTPUT_DIR/generated/` matching configured file types:
   - Read file contents
   - Apply scan pattern descriptions from the registry to identify numeric claims
   - For each identified claim, match against registry metrics by pattern hint and value proximity
   - Classify: consistent, approximate-match (within tolerance), mismatch, unregistered, or ambiguous
   - For ambiguous matches, report all candidates with confidence indicator

3. **New Step: Tolerance Application**: When a numeric claim has qualifying language (approximately, ~, about, roughly, nearly, over, fewer than), apply the corresponding tolerance rule from the registry configuration. Per-metric tolerance overrides take precedence over defaults.

4. **New Step: Exclusion List Application**: Before reporting unregistered metrics, check the exclusion list. Suppressed patterns are skipped. New unregistered metrics are reported as info-severity.

5. **New Step: Discrepancy Report Generation**: Generate the `<metrics-registry-checks>` section of the consistency audit report with all discrepancies, per-file summaries, per-metric verification summaries, and exclusion application log.

6. **New Step: Correction Item Generation**: For critical and warning discrepancies, generate correction items using the new `metric-mismatch` type. For unregistered metrics (not excluded), generate items using the new `unregistered-metric` type. Category is `metrics-consistency`.

7. **Update display format**: Add metrics consistency results to the human-readable audit output.

### Phase C: Integration and Validation

**C1. Verify end-to-end workflow**
- Verify that generate.md → audit.md → fix.md pipeline works with the new registry
- Verify that the full audit workflow (coverage + consistency + accuracy) correctly includes metrics registry checks in its composite score
- Verify correction plan priority ordering places `metrics-consistency` items correctly

**C2. Update full audit workflow**
- Ensure the full audit's consistency dimension includes metrics registry checks
- Update composite score calculation if needed (metrics-consistency checks should contribute to the consistency dimension score)

## Key Design Decisions

1. **Evolve, don't replace**: The existing canonical metrics computation in generate.md is evolved (ephemeral → persistent) rather than replaced. Computation logic stays in generate.md; audit.md reuses the same approach.

2. **Extend, don't fork**: The consistency audit is extended with new steps rather than creating a separate audit type. This keeps the single `consistency` audit entry point.

3. **LLM-native patterns**: Scan patterns are described in human-readable language for the LLM agent to apply, not compiled regex. The agent reads documents and uses its language understanding to identify numeric claims matching pattern descriptions.

4. **Schema-first**: All new XML structures are defined in schema files before being referenced in command templates. This ensures consistency across generate.md and audit.md.

5. **Backward compatible**: All schema extensions add new elements/types without changing existing ones. Existing correction plans, audit reports, and generated documents remain valid.

## Complexity Tracking

> No constitution violations — table not needed.

## Post-Design Constitution Re-Check

| Principle | Status | Notes |
|-----------|--------|-------|
| I. LLM-First | PASS | No compiled code introduced. Pattern matching via LLM reading comprehension. |
| II. Prompt Templates | PASS | All changes are to existing `.md` command files and schema files. |
| III. Structured Output | PASS | New `metrics-registry.xml` has a full schema definition. |
| IV. CLI Bootstrap | PASS | New schema file auto-included in `.reforge/schemas/`. |
| V. Agent-Agnostic | PASS | Instructions use "the agent MUST" throughout. |
| VI. Extensibility | PASS | Scan patterns and tolerance rules are configurable in registry. |
