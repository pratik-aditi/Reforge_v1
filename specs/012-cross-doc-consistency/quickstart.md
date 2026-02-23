# Quickstart: Cross-Document Consistency Checker

**Branch**: `012-cross-doc-consistency` | **Date**: 2026-02-23

## What This Feature Does

Adds a persistent metrics registry (`metrics-registry.xml`) and pattern-based consistency scanner to the Reforge framework. This prevents contradictory statistics across generated documents and detects discrepancies in existing documents.

## Files to Modify

| File | Action | What Changes |
|------|--------|-------------|
| `.reforge/schemas/metrics-registry.md` | CREATE | New schema defining metrics-registry.xml structure |
| `.reforge/schemas/correction-plan.md` | MODIFY | Add `metric-mismatch`, `unregistered-metric` types; add `metrics-consistency` category |
| `.reforge/schemas/consistency-audit-report.md` | MODIFY | Add `<metrics-registry-checks>` section with discrepancies, summaries, exclusions |
| `.reforge/commands/generate.md` | MODIFY | Persist metrics table to XML; add metric ID annotations; add post-generation scan |
| `.reforge/commands/audit.md` | MODIFY | Extend consistency workflow with registry recomputation, pattern scanning, tolerance, exclusion list |

## Implementation Order

1. **Schema first**: Create `metrics-registry.md`, then extend `correction-plan.md` and `consistency-audit-report.md`
2. **Generate second**: Modify `generate.md` to persist registry and add annotations
3. **Audit third**: Extend `audit.md` consistency workflow with scanning steps
4. **Verify last**: End-to-end walkthrough of generate → audit → fix pipeline

## Key Principle

This is a prompt-template-only framework. All changes are markdown files. The LLM agent performs all computation using Read, Glob, Grep, and Write tools. No compiled code. No external parsers.

## Testing Approach

Run the modified commands against a project with known extraction data (e.g., TCOS-RUMO) and verify:
1. `metrics-registry.xml` is created during generation with correct values
2. Generated documents contain metric ID annotations
3. `/reforge.audit consistency` detects deliberately introduced mismatches
4. Tolerance rules correctly classify approximate values
5. Correction plan contains `metric-mismatch` items for discrepancies
