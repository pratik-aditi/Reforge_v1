# Quickstart: Content Accuracy Audit

**Feature**: 011-content-accuracy-audit
**Date**: 2026-02-22

## What Changed

The `/reforge.audit` command now supports three new audit modes beyond the existing coverage audit:

- **`/reforge.audit accuracy`** — Verifies extraction items against the source codebase, detecting fabricated identifiers, incorrect references, and hallucinated content
- **`/reforge.audit consistency`** — Detects arithmetic errors, broken cross-references, duplicate IDs, stale generated documents, and cross-document discrepancies
- **`/reforge.audit full`** — Runs all three audits (coverage + consistency + accuracy) and produces a unified quality score

## For Users

### New Commands

```bash
# Run accuracy audit (verifies extractions against source code)
/reforge.audit accuracy

# Run accuracy audit with full verification (no sampling)
/reforge.audit accuracy --full-verify

# Run accuracy audit with custom sample rate
/reforge.audit accuracy --sample-rate 0.50

# Run consistency audit (checks internal consistency)
/reforge.audit consistency

# Run full audit (coverage + consistency + accuracy)
/reforge.audit full

# Existing command unchanged
/reforge.audit                    # Coverage audit only (backward compatible)
/reforge.audit business-rules     # Scoped coverage audit (backward compatible)
```

### Important Notes

- New audit modes (`accuracy`, `consistency`, `full`) **cannot** be combined with existing scoping arguments (e.g., `business-rules`)
- Each audit mode writes its own report and correction plan file (no overwriting between modes)
- The `full` mode merges all correction plans into a single `correction-plan.xml`
- The existing `/reforge.audit` behavior with no arguments remains unchanged

## New Output Files

| Audit Mode | Report | Correction Plan |
|------------|--------|-----------------|
| `accuracy` | `accuracy-audit-report.xml` | `accuracy-correction-plan.xml` |
| `consistency` | `consistency-audit-report.xml` | `consistency-correction-plan.xml` |
| `full` | `full-audit-report.xml` (+ individual reports) | `correction-plan.xml` (merged) |

All files written to `$PROJECT_OUTPUT_DIR/audit/`.

## New Behaviors to Expect

### Accuracy Verdicts

Each verified extraction item receives one of five verdicts:
- **confirmed** — Item verified in source codebase
- **plausible** — Partial match (e.g., substring only)
- **incorrect** — Found in source but with wrong value
- **fabricated** — No evidence in source codebase
- **skipped** — Could not be verified

### Statistical Sampling

For corpora with 500+ items, the accuracy audit samples 20% by default using stratified sampling across extraction categories. The report includes a 95% confidence interval. Use `--full-verify` for complete verification.

### Composite Quality Score

The full audit computes a weighted quality score:
```
composite = coverage * 0.25 + consistency * 0.35 + accuracy * 0.40
```

Mapped to ratings: Excellent (>=98%), Good (95-97.9%), Acceptable (90-94.9%), Poor (80-89.9%), Critical (<80%).

### Correction Plan Extensions

New correction types: `fabricated`, `inaccurate`, `inconsistent`, `broken-ref`, `arithmetic`, `duplicate-id`. Each entry includes `source-audit-type` and `severity` attributes for traceability.

### Fix Command Update

`/reforge.fix` now supports deletion actions for `fabricated` correction entries — removing fabricated items from extraction XML files.

## Affected Files

| File | Change |
|------|--------|
| `.reforge/commands/audit.md` | Add routing, accuracy workflow, consistency workflow, full audit workflow |
| `.reforge/commands/fix.md` | Add deletion action dispatch for fabricated corrections |
| `.reforge/schemas/accuracy-audit-report.md` | NEW — Accuracy audit report schema |
| `.reforge/schemas/consistency-audit-report.md` | NEW — Consistency audit report schema |
| `.reforge/schemas/full-audit-report.md` | NEW — Full audit report schema |
| `.reforge/schemas/correction-plan.md` | UPDATE — Add new types, categories, attributes |

## Validation

After implementation, run the 8 success criteria from the spec:
1. Accuracy audit against TCOS-RUMO pre-audit acronym glossary (12 fabricated entries)
2. Consistency audit against known arithmetic mismatches and broken cross-references
3. Full audit composite score arithmetic verification
4. Backward compatibility diff against baseline `/reforge.audit` output
5. Statistical sampling confidence interval verification on 4,636-item corpus
