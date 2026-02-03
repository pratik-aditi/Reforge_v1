# Research: Schema Integration Gap Analysis

**Feature**: 003-schema-integration
**Date**: 2026-01-29

## Summary

This research documents the current state of schema integration in the Reforge framework and identifies gaps that need to be addressed.

## Current State Analysis

### Markdown Schemas (`.reforge/schemas/`)

| Schema File | Has Example | Has Contract Reference | XSD Exists |
|-------------|-------------|------------------------|------------|
| analysis.md | ✅ Yes | ✅ Yes (`specs/001-legacy-analyzer/contracts/analysis.xsd`) | ✅ Yes |
| business-rules.md | ✅ Yes | ✅ Yes (`specs/001-legacy-analyzer/contracts/business-rules.xsd`) | ✅ Yes |
| database.md | ✅ Yes | ✅ Yes (`specs/001-legacy-analyzer/contracts/database.xsd`) | ✅ Yes |
| ui-flows.md | ✅ Yes | ✅ Yes (`specs/001-legacy-analyzer/contracts/ui-flows.xsd`) | ✅ Yes |
| workflows.md | ✅ Yes | ✅ Yes (`specs/001-legacy-analyzer/contracts/workflows.xsd`) | ✅ Yes |
| user-stories.md | ✅ Yes | ✅ Yes (`specs/001-legacy-analyzer/contracts/user-stories.xsd`) | ✅ Yes |
| cross-mappings.md | ✅ Yes | ❌ **MISSING** | ❌ No XSD |
| features-requirements.md | ✅ Yes | ❌ **MISSING** | ❌ No XSD |
| audit-report.md | ✅ Yes | ❌ **MISSING** | ✅ Yes (`specs/002-audit-fix-commands/contracts/audit-report.xsd`) |
| correction-plan.md | ✅ Yes | ❌ **MISSING** | ✅ Yes (`specs/002-audit-fix-commands/contracts/correction-plan.xsd`) |

### Command Templates (`.reforge/commands/`)

| Command | References Schema | Schema Path |
|---------|-------------------|-------------|
| analyze.md | ✅ Yes | `.reforge/schemas/analysis.md` |
| extract.md | ✅ Yes | All 4 extraction schemas referenced at end |
| generate.md | ✅ Yes | user-stories, cross-mappings, features-requirements |
| audit.md | ✅ Yes | audit-report.md, correction-plan.md |
| fix.md | ⚠️ **Needs verification** | Should reference correction-plan.md |
| clarify.md | N/A | No output schema (interactive) |
| init.md | N/A | No output schema (config only) |
| reanalyze.md | N/A | Uses analysis.md (same as analyze) |
| status.md | N/A | No output schema (report only) |

## Identified Gaps

### Gap 1: Missing Contract Reference Sections

**Affected schemas**: cross-mappings.md, features-requirements.md, audit-report.md, correction-plan.md

**Decision**: Add "Contract Reference" section to schemas that have corresponding XSD files.

**Rationale**: Per FR-006 in spec, markdown schemas MUST reference their corresponding XSD contract file for traceability.

**Action**:
- Add Contract Reference to `audit-report.md` pointing to `specs/002-audit-fix-commands/contracts/audit-report.xsd`
- Add Contract Reference to `correction-plan.md` pointing to `specs/002-audit-fix-commands/contracts/correction-plan.xsd`
- For `cross-mappings.md` and `features-requirements.md`, add a note that no XSD contract exists (these are derived artifacts)

### Gap 2: Derived Schemas Without XSD Contracts

**Affected schemas**: cross-mappings.md, features-requirements.md

**Decision**: These schemas do NOT need XSD contracts.

**Rationale**:
1. Cross-mappings and features-requirements are derived artifacts generated from other extractions
2. They were introduced in the specification phase but not formally contracted
3. Creating XSD contracts for them would add maintenance burden without significant value
4. The markdown schemas are sufficient for LLM guidance (Constitution Principle I)

**Action**: Add a note to these schemas: "Note: This is a derived schema with no formal XSD contract. The markdown documentation serves as the authoritative definition."

### Gap 3: fix.md Schema Reference Verification

**Decision**: Verify and add schema reference if missing.

**Rationale**: Commands that read/write XML files should reference the relevant schema for agent guidance.

**Action**: Review fix.md and ensure it references correction-plan.md schema.

## Alternatives Considered

### Alternative 1: Deploy XSD Files with Framework

**Rejected because**:
- Adds ~50% more tokens to schema files (XML syntax vs markdown tables)
- Requires external tooling for validation (violates Constitution Principle IV)
- LLMs parse markdown more naturally than XSD (Constitution Principle I)

### Alternative 2: Create XSD for All Schemas

**Rejected because**:
- cross-mappings and features-requirements are derived artifacts, not primary extractions
- Adds maintenance burden (two formats to keep in sync)
- No tooling currently uses XSD validation

### Alternative 3: Remove Contract Reference Sections Entirely

**Rejected because**:
- Loses traceability between deployed schemas and formal contracts
- Makes it harder for maintainers to find authoritative definitions
- Spec requirement FR-006 mandates traceability

## Implementation Summary

| Item | Action | Scope |
|------|--------|-------|
| audit-report.md | Add Contract Reference | 1 file |
| correction-plan.md | Add Contract Reference | 1 file |
| cross-mappings.md | Add "No XSD" note | 1 file |
| features-requirements.md | Add "No XSD" note | 1 file |
| fix.md | Verify schema reference | 1 file |

**Total files to modify**: 5 (all markdown, no runtime changes)
