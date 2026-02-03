# Quickstart: Schema Integration Implementation

**Feature**: 003-schema-integration
**Date**: 2026-01-29

## Overview

This guide provides step-by-step instructions for implementing schema integration improvements across the Reforge framework.

## Prerequisites

- Access to the Reforge repository
- Understanding of markdown schema format (see `.reforge/schemas/analysis.md` as reference)

## Implementation Steps

### Step 1: Update audit-report.md with Contract Reference

**File**: `.reforge/schemas/audit-report.md`

**Action**: Add "Contract Reference" section at the end of the file.

**Content to add**:
```markdown
## Contract Reference

Based on: `specs/002-audit-fix-commands/contracts/audit-report.xsd`
```

### Step 2: Update correction-plan.md with Contract Reference

**File**: `.reforge/schemas/correction-plan.md`

**Action**: Add "Contract Reference" section at the end of the file.

**Content to add**:
```markdown
## Contract Reference

Based on: `specs/002-audit-fix-commands/contracts/correction-plan.xsd`
```

### Step 3: Update cross-mappings.md with Derived Schema Note

**File**: `.reforge/schemas/cross-mappings.md`

**Action**: Add "Schema Notes" section at the end of the file.

**Content to add**:
```markdown
## Schema Notes

This is a derived schema for traceability output. No formal XSD contract exists as cross-mappings are generated from other extraction artifacts. This markdown documentation serves as the authoritative schema definition.

## Related Schemas

- [analysis.md](./analysis.md) — Source file inventory
- [business-rules.md](./business-rules.md) — Referenced rules
- [workflows.md](./workflows.md) — Referenced workflows
- [ui-flows.md](./ui-flows.md) — Referenced UI components
- [features-requirements.md](./features-requirements.md) — Related derived schema
```

### Step 4: Update features-requirements.md with Derived Schema Note

**File**: `.reforge/schemas/features-requirements.md`

**Action**: Add "Schema Notes" section at the end of the file.

**Content to add**:
```markdown
## Schema Notes

This is a derived schema for features and requirements output. No formal XSD contract exists as features-requirements are generated from extraction analysis. This markdown documentation serves as the authoritative schema definition.

## Related Schemas

- [business-rules.md](./business-rules.md) — Source rules for requirements
- [workflows.md](./workflows.md) — Source workflows for features
- [cross-mappings.md](./cross-mappings.md) — Related derived schema
```

### Step 5: Update fix.md with Schema Reference

**File**: `.reforge/commands/fix.md`

**Action**: Add "Output Schema References" section before the Examples section (after Error Handling).

**Content to add**:
```markdown
---

## Output Schema References

- Correction Plan: `.reforge/schemas/correction-plan.md` — Structure for correction-plan.xml
```

## Verification Checklist

After implementation, verify:

- [ ] `audit-report.md` has Contract Reference pointing to correct XSD
- [ ] `correction-plan.md` has Contract Reference pointing to correct XSD
- [ ] `cross-mappings.md` has Schema Notes section explaining derived nature
- [ ] `features-requirements.md` has Schema Notes section explaining derived nature
- [ ] `fix.md` has Output Schema References section
- [ ] All modified files maintain valid markdown structure
- [ ] No duplicate sections introduced

## Testing

To validate the changes:

1. **Syntax Check**: Ensure all markdown files render correctly
2. **Link Validation**: Verify Contract Reference paths resolve to existing XSD files
3. **Consistency Check**: Compare similar sections across schema files for formatting consistency

## Rollback

If changes need to be reverted:

```bash
git checkout main -- .reforge/schemas/audit-report.md
git checkout main -- .reforge/schemas/correction-plan.md
git checkout main -- .reforge/schemas/cross-mappings.md
git checkout main -- .reforge/schemas/features-requirements.md
git checkout main -- .reforge/commands/fix.md
```
