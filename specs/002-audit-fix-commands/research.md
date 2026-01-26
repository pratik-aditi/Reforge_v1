# Research: Audit and Fix Commands

**Feature**: 002-audit-fix-commands
**Date**: 2026-01-23

## Decision 1: Command Template Pattern

**Decision**: Follow the established command template pattern used by `/reforge.status` and `/reforge.reanalyze` — both the closest analogues to the new commands.

**Rationale**: The audit command shares structural similarity with `/reforge.status` (read-only reporting on output state) while the fix command shares patterns with `/reforge.reanalyze` (orchestrating changes to existing outputs with checkpoint support).

**Alternatives considered**:
- Single combined command (`/reforge.audit --fix`): Rejected because it conflates discovery and action, violating the principle that commands should have clear single responsibilities.
- Three commands (audit, plan, fix): Rejected because the correction plan is a natural output of audit — adding a separate plan command would add friction without value.

## Decision 2: Audit Output Storage Location

**Decision**: Store audit outputs in `reforge_output/<project>/audit/` subdirectory.

**Rationale**: Follows the existing pattern of categorized subdirectories (`analysis/`, `extractions/`, `generated/`). Keeps audit artifacts separate from extraction outputs to avoid confusion.

**Alternatives considered**:
- Store in `.reforge/memory/`: Rejected — memory is for framework state, not analysis outputs.
- Store alongside extractions in `extractions/`: Rejected — audit reports are meta-artifacts about extractions, not extractions themselves.
- Store in `derived/`: Considered viable but `derived/` is for cross-mappings between extraction types, not coverage reports.

## Decision 3: Correction Plan Execution Strategy

**Decision**: The fix command reads the correction plan and dispatches appropriate reforge commands in dependency order: analysis corrections first, then extraction corrections, then generation corrections.

**Rationale**: Downstream artifacts depend on upstream ones (generated docs depend on extractions which depend on analysis). Fixing in this order prevents cascading re-work.

**Alternatives considered**:
- Parallel execution: Rejected — dependency ordering prevents parallel execution of corrections across tiers.
- User-specified order: Rejected — the dependency order is deterministic and always correct; user override would risk inconsistency.

## Decision 4: Checkpoint Integration for Fix Command

**Decision**: Reuse the existing `.reforge/memory/checkpoints/` mechanism with a new checkpoint type `fix-checkpoint.xml`.

**Rationale**: The checkpoint infrastructure already exists for `/reforge.analyze`. The fix command has similar resumability needs (long-running, may be interrupted).

**Alternatives considered**:
- Inline status in correction-plan.xml (mark items as completed): Considered as complementary — the correction plan WILL track per-item status, AND a checkpoint provides resume state.
- No checkpoint (re-run from scratch): Rejected — re-executing already-completed corrections wastes time and may produce different results.

## Decision 5: Prerequisite Script Integration

**Decision**: Use existing `check-prerequisites.sh` with a new `--require-analysis` flag for audit (analysis must exist) and `--require-audit` flag for fix (correction plan must exist).

**Rationale**: Centralizes prerequisite checking in one script, consistent with how other commands validate state.

**Alternatives considered**:
- Inline prerequisite checks in command templates: Rejected — duplicates logic and is harder to maintain across commands.
- New script per command: Rejected — the existing script handles all prerequisite patterns.

## Decision 6: Coverage Calculation Method

**Decision**: Coverage percentage = (files with at least one extraction reference) / (total analyzed files - excluded files) * 100.

**Rationale**: Simple, deterministic, and aligned with the file-level granularity decision from clarification. A file is "covered" if any extraction type references it.

**Alternatives considered**:
- Weighted coverage (more extractions = better coverage): Rejected — overcomplicates the metric without clear value.
- Per-type coverage (separate percentage per extraction type): Will be reported as supplementary detail but the primary metric is aggregate coverage.

## Decision 7: Audit Report vs. Correction Plan Separation

**Decision**: The audit produces two separate XML files: `audit-report.xml` (read-only diagnostic) and `correction-plan.xml` (actionable, mutable by fix command).

**Rationale**: Separating the report from the plan allows the report to serve as historical record while the plan is consumed and modified by the fix command.

**Alternatives considered**:
- Single combined file: Rejected — the fix command needs to mutate status fields without corrupting the diagnostic report.
- Report only (plan derived at fix-time): Rejected — users need to review the plan before executing, which requires it to be persisted.
