# Data Model: Glossary Command

**Feature**: 013-glossary-command | **Date**: 2026-02-23

## Entities

### GlossaryEntry

The core entity — a single acronym/abbreviation with its verified expansion.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | yes | Unique ID, pattern: `GLOSS-{SEQUENCE}` (e.g., `GLOSS-001`) |
| `term` | string | yes | The acronym/abbreviation exactly as found in source (e.g., `TMDS`) |
| `expansion` | string | yes | Full expansion (e.g., `Train Management Dispatch System`) |
| `confidence` | float | yes | Confidence score 0.0-1.0 |
| `category` | enum | yes | One of: `domain`, `technical`, `organizational`, `process`, `data` |
| `verification-status` | enum | yes | One of: `CONFIRMED`, `CORRECTED`, `UNVERIFIED`, `FABRICATED`, `NOT_FOUND` |
| `version-added` | string | yes | Glossary version when entry was first added (e.g., `v1.0.0`) |
| `version-modified` | string | no | Glossary version when entry was last modified |
| `evidence` | Evidence[] | yes | One or more evidence records (min 1) |

**Identity/Uniqueness**: Entries are unique by `term` (case-sensitive). If multiple workers discover the same term, the lead agent deduplicates by keeping the highest-confidence entry and merging evidence arrays.

**State Transitions**:
```
Phase 1: → UNVERIFIED (initial draft, confidence based on extraction context)
Phase 2: → CONFIRMED (external source found)
        → CORRECTED (expansion corrected by external source)
        → UNVERIFIED (no external source found, confidence unchanged)
        → NOT_FOUND (not a recognized acronym per external sources)
Phase 3: → FABRICATED (zero word-boundary grep matches → marked for deletion)
        → UNVERIFIED (term found in code but no explicit expansion → confidence capped at 0.5)
        → CONFIRMED (term + expansion both verified in source)
        → CORRECTED (expansion updated based on source evidence)
Phase 4: → (re-verification of Phase 3 results; status may be upgraded or downgraded)
```

### Evidence

A source reference proving the existence or expansion of a term.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `file` | string | yes | Source file path relative to project root |
| `line-start` | integer | yes | Starting line number |
| `line-end` | integer | no | Ending line number (same as start if single line) |
| `evidence-type` | enum | yes | One of: `code-comment`, `doc-comment`, `enum-definition`, `namespace`, `string-literal`, `variable-name`, `region-label`, `external-source` |
| `snippet` | string | yes | Verbatim text snippet from source (max 200 chars) |
| `phase` | integer | yes | Phase in which this evidence was collected (1-4) |

**Validation**: `file` must NOT be an LLM-authored file (CLAUDE.md, README.md, project-context.md, analysis.xml).

### AuditFinding

A Phase 3/4 verification result for a single entry.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `entry-id` | string | yes | Reference to GlossaryEntry.id |
| `term` | string | yes | The acronym being audited |
| `phase` | integer | yes | Phase that produced this finding (3 or 4) |
| `verdict` | enum | yes | One of: `CONFIRMED`, `CORRECTED`, `FABRICATED`, `UNVERIFIABLE` (note: `UNVERIFIABLE` is distinct from GlossaryEntry's `UNVERIFIED` — `UNVERIFIABLE` means the audit could not reach a conclusion; `UNVERIFIED` means no external/source evidence was found for the expansion) |
| `grep-count` | integer | yes | Word-boundary grep match count across all source files |
| `evidence-files` | string[] | no | List of files where term was found |
| `original-expansion` | string | no | Previous expansion if corrected |
| `corrected-expansion` | string | no | New expansion if corrected |
| `action` | enum | yes | One of: `KEEP`, `UPDATE`, `DELETE`, `FLAG_FOR_REVIEW` |
| `rationale` | string | yes | Explanation of the verdict |

### Checkpoint

Phase-level save state for resume capability.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `feature` | string | yes | Always `glossary` |
| `last-completed-phase` | integer | yes | 0-4 (0 = no phases completed) |
| `current-version` | string | yes | Current glossary version (e.g., `v1.2.0`) |
| `entry-count` | integer | yes | Number of entries at checkpoint |
| `phases-skipped` | integer[] | no | Phase numbers that were skipped (e.g., `[2]` for air-gapped) |
| `timestamp` | string | yes | ISO-8601 timestamp |
| `team-size` | integer | yes | Team size used for this run |

### MemoryLookup

Persistent key-value store for cross-command consumption.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| (key) | string | yes | The acronym/term (e.g., `"TMDS"`) |
| `expansion` | string | yes | Full expansion |
| `confidence` | float | yes | Final confidence score |
| `category` | string | yes | Category from GlossaryEntry |

**Format**: JSON object keyed by term. Example:
```json
{
  "version": "v1.3.0",
  "generated": "2026-02-23T14:30:00Z",
  "entry-count": 42,
  "terms": {
    "TMDS": {
      "expansion": "Train Management Dispatch System",
      "confidence": 1.0,
      "category": "domain"
    }
  }
}
```

### GlossaryVersion

Semantic version tracking through phases.

| Version | Phase | Description |
|---------|-------|-------------|
| `v1.0.0` | Phase 1 | Initial draft from pattern extraction |
| `v1.1.0` | Phase 2 | After external verification (skipped if `--skip-external`) |
| `v1.2.0` | Phase 3 | After source code audit |
| `v1.3.0` | Phase 4 | Final version after self-audit |

**Note**: When `--skip-external` is used, v1.1.0 is skipped. The version progression becomes v1.0.0 → v1.2.0 → v1.3.0.

## Relationships

```
GlossaryEntry 1──* Evidence        (entry has one or more evidence records)
GlossaryEntry 1──* AuditFinding    (entry may have findings from Phase 3 and/or 4)
Checkpoint    *──1 GlossaryVersion (checkpoint tracks current version)
MemoryLookup  *──1 GlossaryEntry   (memory is a projection of surviving entries)
```

## File Locations

| Artifact | Path | Format |
|----------|------|--------|
| Glossary XML | `reforge_output/<project>/extractions/acronym-glossary.xml` | XML (extends common-schema) |
| Audit Report | `reforge_output/<project>/audit/glossary-audit-report.xml` | XML |
| Memory Lookup | `.reforge/memory/glossary.json` | JSON |
| Checkpoint | `.reforge/memory/checkpoints/glossary-checkpoint.json` | JSON |
| Phase Templates | `.reforge/commands/glossary.md`, `glossary-phase-{1-4}.md` | Markdown |
| Schema | `.reforge/schemas/glossary.md` | Markdown |
