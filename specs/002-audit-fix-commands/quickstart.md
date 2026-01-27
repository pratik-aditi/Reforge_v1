# Quickstart: Audit and Fix Commands

## Prerequisites

1. `.reforge/` framework installed in your project
2. `/reforge.analyze` completed (analysis.xml exists)
3. At least one `/reforge.extract` type completed

## Basic Usage

### Step 1: Run an audit

```
/reforge.audit
```

This compares your analysis inventory against all extraction outputs and reports:
- Overall coverage percentage
- List of uncovered files (analyzed but no extractions reference them)
- Stale references (extractions pointing to files that no longer exist)

### Step 2: Review the correction plan

After the audit, review the generated correction plan:
- Path: `reforge_output/<project>/audit/correction-plan.xml`
- Each item has a priority, type (gap or stale), and recommended action

### Step 3: Execute corrections

```
/reforge.fix
```

This reads the correction plan and executes each correction in dependency order (analysis first, then extractions, then generation).

### Step 4: Verify

Run `/reforge.audit` again to confirm improved coverage.

## Targeted Audit

Audit a specific artifact type only:

```
/reforge.audit business-rules
/reforge.audit user-stories
/reforge.audit database
```

## Selective Fix

Fix only corrections of a specific type:

```
/reforge.fix --type business-rules
```

Fix specific items by ID:

```
/reforge.fix --items COR-001,COR-003
```

## Interactive Fix

Review each correction before execution:

```
/reforge.fix --interactive
```

## Resuming After Interruption

If the fix command is interrupted:

```
/reforge.fix --resume
```

## Output Locations

| Artifact | Location |
|----------|----------|
| Audit Report | `reforge_output/<project>/audit/audit-report.xml` |
| Correction Plan | `reforge_output/<project>/audit/correction-plan.xml` |
| Fix Checkpoint | `.reforge/memory/checkpoints/fix-checkpoint.xml` |

## JSON Output

For tooling integration:

```
/reforge.audit --json
```
