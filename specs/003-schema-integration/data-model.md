# Data Model: Schema Integration

**Feature**: 003-schema-integration
**Date**: 2026-01-29

## Overview

This feature involves documentation/template files only. No runtime data entities are created or modified. The "data model" for this feature describes the relationship between files in the framework.

## Entity Relationships

```
┌─────────────────────────────────────────────────────────────────────┐
│                         DEVELOPMENT TIME                             │
│                                                                      │
│  specs/*/contracts/*.xsd ◄───── Authoritative Definition            │
│         │                                                            │
│         │ references                                                 │
│         ▼                                                            │
│  .reforge/schemas/*.md  ◄─────── LLM-Friendly Documentation         │
│         │                        (Contract Reference section)        │
│         │                                                            │
└─────────┼────────────────────────────────────────────────────────────┘
          │ deployed with framework
          ▼
┌─────────────────────────────────────────────────────────────────────┐
│                          RUNTIME (User Project)                      │
│                                                                      │
│  .reforge/commands/*.md ─────── References ─────► .reforge/schemas/  │
│         │                       (Output Schema References section)   │
│         │                                                            │
│         │ AI agent executes                                          │
│         ▼                                                            │
│  reforge_output/*.xml  ◄─────── Conforms to schemas                 │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

## File Entities

### XSD Contract (Development Only)

**Location**: `specs/*/contracts/*.xsd`
**Purpose**: Formal XML Schema Definition for validation and documentation
**Deployed**: No (remains in development specs)

| Attribute | Description |
|-----------|-------------|
| `targetNamespace` | XML namespace (e.g., `http://reforge.dev/schema/analysis`) |
| `elementFormDefault` | Schema form (always `qualified`) |
| Elements | Complex type definitions for all XML elements |
| Attributes | Attribute definitions with types and requirements |

**Existing Files**:
- `specs/001-legacy-analyzer/contracts/analysis.xsd`
- `specs/001-legacy-analyzer/contracts/business-rules.xsd`
- `specs/001-legacy-analyzer/contracts/database.xsd`
- `specs/001-legacy-analyzer/contracts/ui-flows.xsd`
- `specs/001-legacy-analyzer/contracts/workflows.xsd`
- `specs/001-legacy-analyzer/contracts/user-stories.xsd`
- `specs/002-audit-fix-commands/contracts/audit-report.xsd`
- `specs/002-audit-fix-commands/contracts/correction-plan.xsd`

### Markdown Schema (Deployed)

**Location**: `.reforge/schemas/*.md`
**Purpose**: LLM-readable schema documentation for output generation
**Deployed**: Yes (copied to user projects)

| Section | Required | Description |
|---------|----------|-------------|
| Overview | Yes | Schema purpose and context |
| Root Element | Yes | Root XML element with attributes |
| Elements | Yes | All child elements with types |
| Shared Types | No | Enum values, common types |
| Example Output | Yes | Complete XML example |
| Related Schemas | No | Cross-references to other schemas |
| Contract Reference | Conditional | Link to XSD if one exists |

**Files to Update**:
- `audit-report.md` - Add Contract Reference
- `correction-plan.md` - Add Contract Reference
- `cross-mappings.md` - Add note (no XSD exists)
- `features-requirements.md` - Add note (no XSD exists)

### Command Template (Deployed)

**Location**: `.reforge/commands/*.md`
**Purpose**: Prompt templates that guide AI agent through workflows
**Deployed**: Yes (copied to user projects)

| Section | Description |
|---------|-------------|
| Command Syntax | Usage pattern with arguments |
| Overview | Command purpose |
| Workflow | Step-by-step execution |
| Output Schema References | Links to `.reforge/schemas/` |

**Files to Update**:
- `fix.md` - Add schema reference to correction-plan.md

## Validation Rules

1. **Schema Completeness**: Every markdown schema MUST have:
   - Root Element section
   - Elements section with all attributes documented
   - At least one Example Output section

2. **Contract Traceability**: Markdown schemas MUST have Contract Reference section if:
   - A corresponding XSD file exists in `specs/*/contracts/`

3. **Command Reference**: Command templates that produce XML output MUST:
   - Reference the output schema in `.reforge/schemas/`
   - Place reference in "Output Schema References" or similar section

## State Transitions

N/A - This feature involves static documentation files with no runtime state.
