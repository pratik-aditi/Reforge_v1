# Data Model: Audit and Fix Commands

**Feature**: 002-audit-fix-commands
**Date**: 2026-01-23

## Entities

### Audit Report

The read-only diagnostic output of `/reforge.audit`. Stored as `audit-report.xml`.

| Field | Type | Description |
|-------|------|-------------|
| project-id | string | Reference to the analyzed project |
| version | string | Schema version |
| generated | dateTime | Audit execution timestamp |
| scope | string | "all" or specific type audited |
| total-files | integer | Total files in analysis.xml |
| covered-files | integer | Files with at least one extraction reference |
| uncovered-files | integer | Files with no extraction references |
| coverage-percentage | decimal | (covered / total) * 100 |
| stale-references | integer | Extraction references pointing to missing/changed files |

**Children**:
- `<coverage-by-type>` — Per extraction type breakdown
- `<uncovered-file-list>` — List of files with no coverage
- `<stale-reference-list>` — List of invalid source references
- `<summary>` — Human-readable summary text

### Coverage By Type

Breakdown of coverage per extraction type.

| Field | Type | Description |
|-------|------|-------------|
| type | string | Extraction type (business-rules, database, ui-flows, workflows) |
| files-referenced | integer | Number of unique files referenced by this type |
| total-items | integer | Total extraction items of this type |
| stale-items | integer | Items with invalid source references |

### Uncovered File Entry

A single file identified as having no extraction coverage.

| Field | Type | Description |
|-------|------|-------------|
| path | string | Relative file path |
| language | string | Detected language from analysis.xml |
| lines | integer | Line count from analysis.xml |
| components | string | Component types detected (class, function, etc.) |

### Stale Reference Entry

An extraction item whose source reference is no longer valid.

| Field | Type | Description |
|-------|------|-------------|
| extraction-type | string | Which extraction contains the stale reference |
| item-id | string | ID of the extraction item (e.g., BR-001) |
| referenced-file | string | File path that no longer exists or has changed |
| issue | string | "missing" (file deleted) or "modified" (hash changed) |

### Correction Plan

The actionable output consumed by `/reforge.fix`. Stored as `correction-plan.xml`. Mutable — the fix command updates item statuses.

| Field | Type | Description |
|-------|------|-------------|
| project-id | string | Reference to the analyzed project |
| version | string | Schema version |
| generated | dateTime | Plan creation timestamp |
| source-audit | string | Path to the audit report that generated this plan |
| total-items | integer | Total correction items |
| completed-items | integer | Items already fixed (updated by fix command) |

**Children**:
- `<correction>` — Individual correction items (ordered by priority)

### Correction Item

A single actionable correction within the plan.

| Field | Type | Description |
|-------|------|-------------|
| id | string | Unique correction identifier (COR-001, COR-002, ...) |
| priority | integer | Execution order (1 = highest priority) |
| type | enum | "gap" (missing coverage) or "stale" (invalid reference) |
| category | enum | "analysis", "extraction", or "generation" |
| extraction-type | string | Affected extraction type (if applicable) |
| status | enum | "pending", "in-progress", "completed", "failed", "skipped" |
| action | string | Recommended reforge command to execute |
| affected-files | list | File paths affected by this correction |
| description | string | Human-readable description of what needs fixing |
| completed-at | dateTime | Timestamp when correction was completed (null if pending) |

### Fix Checkpoint

Resume state for interrupted fix operations. Stored as `fix-checkpoint.xml`.

| Field | Type | Description |
|-------|------|-------------|
| plan-path | string | Path to the correction plan being executed |
| started-at | dateTime | Fix execution start time |
| last-completed-id | string | ID of the last successfully completed correction |
| total-items | integer | Total corrections in the plan |
| completed-count | integer | Number completed so far |
| failed-items | list | IDs of any failed corrections |

## Relationships

```
analysis.xml ─────────┐
                       ├──→ audit-report.xml ──→ correction-plan.xml ──→ fix-checkpoint.xml
extraction outputs ───┘
(business-rules.xml,
 database.xml,
 ui-flows.xml,
 workflows.xml)
```

- **Audit Report** references: analysis.xml (file inventory), all extraction XMLs (source references)
- **Correction Plan** references: audit-report.xml (source diagnostic), existing extraction schemas (for item IDs)
- **Fix Checkpoint** references: correction-plan.xml (tracks execution progress)

## State Transitions

### Correction Item Status

```
pending → in-progress → completed
                      → failed
pending → skipped (user chose to skip in interactive mode)
```

### Audit Lifecycle

```
1. /reforge.audit → produces audit-report.xml + correction-plan.xml
2. User reviews correction-plan.xml
3. /reforge.fix → reads plan, executes corrections, updates item statuses
4. /reforge.fix (spot-check) → verifies corrected items now have coverage
5. User may re-run /reforge.audit to get updated coverage percentage
```

## Storage Locations

| Artifact | Path |
|----------|------|
| Audit Report | `reforge_output/<project>/audit/audit-report.xml` |
| Correction Plan | `reforge_output/<project>/audit/correction-plan.xml` |
| Fix Checkpoint | `.reforge/memory/checkpoints/fix-checkpoint.xml` |
