# Research: Common Extraction Schema

**Feature**: 009-common-extraction-schema
**Date**: 2026-02-20

## Research Tasks

### R1: XSD Composition — `xs:import` vs `xs:include` for Common Types

**Decision**: Use `xs:import` with the unified namespace `http://reforge.dev/schema/extraction`.

**Rationale**: Since all extraction types are moving to a single shared namespace (`http://reforge.dev/schema/extraction` per clarification Q5), `xs:import` is the correct mechanism. Each type-specific XSD imports the common schema's types from the shared namespace. The alternative `xs:include` merges into the same namespace but doesn't provide the same level of type isolation — with `xs:import`, the common types are clearly owned by the common schema file.

**Alternatives considered**:
- `xs:include`: Simpler but requires same namespace. Would work with our single-namespace decision but provides less explicit separation between common and type-specific types.
- `xs:redefine`: Allows overriding imported types. Rejected — we want type-specific schemas to *extend* the common schema, not redefine its types.
- Chameleon includes (no targetNamespace on common): Anti-pattern, creates ambiguity.

**Implementation pattern**:
```xml
<!-- In common-schema.xsd -->
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema"
           xmlns:rf="http://reforge.dev/schema/extraction"
           targetNamespace="http://reforge.dev/schema/extraction"
           elementFormDefault="qualified">
  <!-- Shared types defined here -->
</xs:schema>

<!-- In business-rules.xsd -->
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema"
           xmlns:rf="http://reforge.dev/schema/extraction"
           targetNamespace="http://reforge.dev/schema/extraction"
           elementFormDefault="qualified">
  <xs:include schemaLocation="common-schema.xsd"/>
  <!-- Type-specific types reference rf:ConfidenceType, rf:SourceReferenceType, etc. -->
</xs:schema>
```

**Note**: Since both schemas share the same targetNamespace, `xs:include` (not `xs:import`) is technically the correct XSD mechanism. `xs:import` is for different namespaces. Updated decision: use `xs:include` since all schemas share `http://reforge.dev/schema/extraction`.

### R2: Current Redundancy Analysis — Shared Types Across XSDs

**Decision**: Extract `ConfidenceType`, `SourceReferenceType`, and root attribute definitions into `common-schema.xsd`. Add `MetadataType` as new shared type.

**Rationale**: Analysis of all 4 existing XSDs confirms identical duplication:

| Type | business-rules.xsd | database.xsd | ui-flows.xsd | workflows.xsd |
|------|-------------------|--------------|--------------|---------------|
| `ConfidenceType` | ✅ Identical | ✅ Identical | ✅ Identical | ✅ Identical |
| `SourceReferenceType` | ✅ Identical | ✅ Identical | ✅ Identical | ✅ Identical |
| Root `project-id` attr | ✅ Present | ✅ Present | ✅ Present | ✅ Present |
| Root `version` attr | ✅ Present | ✅ Present | ✅ Present | ✅ Present |
| Root `generated` attr | ✅ Present | ✅ Present | ✅ Present | ✅ Present |
| Root `count` attr | ✅ Present | ❌ Missing | ❌ Missing | ✅ Present |
| `MetadataType` | ❌ Missing | ❌ Missing | ❌ Missing | ❌ Missing |

**Findings**:
- `ConfidenceType` and `SourceReferenceType` are copy-pasted identically across all 4 XSDs — direct extraction candidates.
- Root attributes are consistent for `project-id`, `version`, `generated` but `count` is missing from database and ui-flows root elements.
- No existing XSD defines a `<metadata>` container — this is a new addition per FR-003.
- New common attributes per spec: `schema-version` (FR-009), `xmlns` set to unified namespace (FR-002).

**Alternatives considered**:
- Extract only `ConfidenceType`: Too conservative — `SourceReferenceType` is equally duplicated.
- Extract root element itself: Too aggressive — each type has a different root element name and structure.

### R3: Metadata Container Design

**Decision**: Define `<metadata>` as a required child element of each extraction root, containing `<total-count>`, `<confidence-distribution>`, and `<extraction-timestamp>`.

**Rationale**: FR-003 requires standardized metadata. Currently each type uses ad-hoc approaches:
- business-rules: `count` attribute on root (no distribution)
- database: `entity-count` on `<data-model>`, `count` on `<interactions>` (split across sub-elements)
- ui-flows: `count` on `<screens>` (no root-level aggregate)
- workflows: `count` attribute on root (no distribution)

A single `<metadata>` container provides consistent access for downstream commands (FR-012).

**Structure**:
```xml
<metadata>
  <total-count>25</total-count>
  <confidence-distribution>
    <high>15</high>
    <medium>8</medium>
    <low>2</low>
  </confidence-distribution>
  <extraction-timestamp>2024-01-15T10:30:00Z</extraction-timestamp>
</metadata>
```

**Alternatives considered**:
- Root attributes only (no child element): Doesn't accommodate confidence distribution cleanly.
- Inline distribution as attributes: `<metadata total="25" high="15" medium="8" low="2">` — less extensible, harder for agent to read.

### R4: Namespace Migration Strategy

**Decision**: Unified namespace `http://reforge.dev/schema/extraction` replaces all per-type namespaces.

**Rationale**: Per clarification Q5. Existing per-type namespaces (`http://reforge.dev/schema/business-rules`, etc.) are replaced. This simplifies downstream parsing — one namespace for all extraction XML.

**Migration impact**:
- All 4 XSD files change their `targetNamespace`
- All existing extraction output references old namespaces — covered by FR-014 (legacy file handling with warning)
- Extract command template XML examples must use new namespace
- No external consumers known — migration risk is low

### R5: Validation Gate Integration in Extract Command

**Decision**: Add a "Step 5.6: Schema Compliance Validation" section to `extract.md`, between Step 5.5 (Post-Extraction Verification) and Step 6 (Report Results).

**Rationale**: The extract command already has a Step 5.5 for content verification. The schema compliance gate (FR-008) is a structural check that runs after content verification but before the report. This positioning ensures output is both content-accurate and structurally conformant.

**Validation gate behavior**:
1. Agent reads `common-schema.md` to get the required structure
2. Agent checks extraction output for: required root attributes, `<metadata>` section, source reference format, `schema-version` attribute, namespace
3. Auto-corrects where possible (add missing elements, normalize source references)
4. Inserts `<!-- SCHEMA-WARNING: ... -->` for uncorrectable violations
5. Emits summary of validation results in Step 6 report

**Alternatives considered**:
- Separate validation command: Rejected — validation at write time (FR-008) prevents drift.
- Pre-generation validation: Rejected — can't validate structure before it's generated.

### R6: ID Pattern Convention Enforcement

**Decision**: Document ID patterns in common schema but do not enforce via XSD regex (agent validates during extraction).

**Rationale**: FR-006 requires standardized ID patterns (`BR-VAL-001`, `WF-AUTH-001`, etc.). XSD `xs:pattern` could enforce this, but:
- Pattern varies by type prefix (BR, DB, E, SCR, CMP, WF)
- Category segment is domain-specific and open-ended
- Agent-based validation is more flexible and provides better error messages

The common schema markdown documents the convention. The agent checks it during the validation gate.

**ID format**: `{TYPE-PREFIX}-{CATEGORY}-{SEQUENCE}`
- Type prefixes: `BR` (business-rules), `DB` (database interaction), `E` (entity), `SCR` (screen), `CMP` (component), `WF` (workflow)
- Category: Domain-specific short code (e.g., `VAL`, `AUTH`, `CALC`)
- Sequence: Zero-padded 3-digit number (001-999)
