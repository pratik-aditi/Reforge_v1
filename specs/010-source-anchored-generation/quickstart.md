# Quickstart: Source-Anchored Generation

**Feature**: 010-source-anchored-generation
**Date**: 2026-02-20

## What Changed

The `/reforge.generate` command now enforces **Source-Anchored Generation** -- a set of mandatory constraints ensuring every fact in generated output traces to extraction XML data.

## For Users

No command syntax changes. Run `/reforge.generate` exactly as before. The agent now automatically:

1. **Computes a canonical metrics table** at the start of each generation run by counting extraction XML elements
2. **Copies identifiers verbatim** from extraction XML (no fabrication)
3. **States derivation formulas** for all computed statistics
4. **Runs the Diagram Verification Protocol** on every generated diagram
5. **Completes the Content Validation Checklist** before finalizing each document
6. **Emits `[DATA GAP]` markers** when extraction data is insufficient (instead of fabricating content)
7. **Adds provenance annotations** citing extraction sources and element counts

## New Behaviors to Expect

### Formula Transparency

Generated statistics now include their derivation:

```
Total functional requirements: 938 (541 base + 87 AUTH + 85 BUL + 98 TRN + 127 COMM)
```

### Provenance Annotations

Each major section includes a source citation:

```html
<!-- Source: extractions/business-rules/business-rules-authority.xml (42 rules) -->
```

### Diagram Verification Blocks

Every generated diagram includes a verification comment:

```
' === VERIFICATION LOG ===
' Source: extractions/architecture/strategy-patterns-deep.xml
' Nodes: 49 states from PTCStatus extraction, all verified
' Edges: 12 transitions from authority-lifecycle-workflow.xml
' Omitted: 0
' Unresolved: 0
' === END VERIFICATION ===
```

### Data Gap Markers

When extraction data is missing, you'll see explicit markers instead of fabricated content:

```
[DATA GAP: OnBoardState enum member names not extracted -- run /reforge.extract to fill]
```

If 3+ gaps occur, a supplementary `gap-report.md` is generated with recommended extraction commands.

### Staleness Warnings

If extraction timestamps are older than 7 days:

```
WARNING: Some extraction data may be outdated. Last extraction: [date].
Consider running /reforge.extract to refresh.
```

## Affected Files

| File | Change |
|------|--------|
| `.reforge/commands/generate.md` | New Step 0.6 + 8 verification sections + Selective Regeneration update |
| `.reforge/templates/sysml-block.md` | Source-Anchored Generation annotation |
| `.reforge/templates/uml-class.md` | Source-Anchored Generation annotation |
| `.reforge/templates/user-story.md` | Source-Anchored Generation annotation |
| `.reforge/templates/ascii-layout.md` | Source-Anchored Generation annotation |
| `.reforge/templates/data-dictionary.md` | Source-Anchored Generation annotation |

## Validation

After implementation, run the 8 test cases from the spec against the TCOS-RUMO dataset to confirm all 7 generation-phase errors are prevented.
