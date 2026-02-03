# Feature Specification: Schema Integration for Reforge Workflow

**Feature Branch**: `003-schema-integration`
**Created**: 2026-01-29
**Status**: Draft
**Input**: User description: "We created xml schemas for our work, but I don't see them part of the reforge workflow. We need to make sure we're following these schemas when creating content for consistency. The specs folder has the XSD schemas but they are not deployed as part of the workflow - is this to reduce tokens?"

## Problem Statement

Reforge has two types of schema definitions:
1. **XSD schemas** in `specs/*/contracts/` - Formal XML Schema Definition files (machine-validatable)
2. **Markdown schemas** in `.reforge/schemas/` - Human-readable documentation deployed with the framework

Currently, the markdown schemas are deployed to users while XSD schemas remain in the development specs folder. This raises consistency concerns:
- Commands reference markdown schemas for output format guidance
- XSD schemas may drift from markdown documentation
- No runtime validation against formal schemas
- Unclear whether the AI agent should/can use XSD schemas for validation

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Schema-Compliant Output Generation (Priority: P1)

As an AI agent executing Reforge commands, I need clear schema guidance so that all generated XML output is consistent and valid.

**Why this priority**: This is the core value proposition - ensuring all extraction commands produce consistent, well-structured XML output that matches documented schemas.

**Independent Test**: Can be fully tested by running `/reforge.extract business-rules` on a sample codebase and validating the output XML structure matches the documented schema.

**Acceptance Scenarios**:

1. **Given** an AI agent runs `/reforge.extract business-rules`, **When** the extraction completes, **Then** the generated `business-rules.xml` MUST conform to the schema structure documented in `.reforge/schemas/business-rules.md`
2. **Given** schema documentation exists for an extraction type, **When** the AI agent reads the schema file, **Then** all required elements, attributes, and their data types MUST be clearly specified
3. **Given** an extraction command is executed, **When** the output file is generated, **Then** the root element MUST include the correct namespace declaration as specified in the schema

---

### User Story 2 - Schema Documentation Discoverability (Priority: P2)

As an AI agent, I need to easily locate and load the correct schema for each extraction type so I can generate compliant output without guesswork.

**Why this priority**: Enables the agent to self-serve schema information, reducing errors and clarification needs.

**Independent Test**: Can be tested by verifying that each command's documentation explicitly references the correct schema file and that schema files contain all information needed for output generation.

**Acceptance Scenarios**:

1. **Given** an AI agent reads an extraction command template, **When** it processes the command, **Then** the command MUST reference the corresponding schema file in `.reforge/schemas/`
2. **Given** a schema file exists in `.reforge/schemas/`, **When** the AI agent reads it, **Then** it MUST contain: root element structure, all required attributes, all child elements with types, and at least one complete example

---

### User Story 3 - Schema Consistency Verification (Priority: P3)

As a framework maintainer, I need a way to verify that markdown schemas stay synchronized with XSD contracts so documentation doesn't drift from formal definitions.

**Why this priority**: Maintains long-term quality but is not blocking for immediate usage.

**Independent Test**: Can be tested by comparing the structure defined in an XSD file with its corresponding markdown schema documentation.

**Acceptance Scenarios**:

1. **Given** an XSD schema exists in `specs/*/contracts/`, **When** comparing it to the corresponding markdown schema in `.reforge/schemas/`, **Then** all elements and attributes MUST match between the two formats
2. **Given** a markdown schema file exists, **When** it references a formal XSD contract, **Then** the reference MUST include the relative path to the XSD file for traceability

---

### Edge Cases

- What happens when a schema is updated but the command template is not? The command template MUST reference schema version numbers.
- How does the system handle schema elements marked as optional? Optional elements MUST be clearly indicated with "minOccurs" equivalent documentation.
- What if the AI agent generates XML with an element not in the schema? The schema documentation MUST list all valid elements; unlisted elements indicate a schema gap to be addressed.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Each extraction command template in `.reforge/commands/` MUST explicitly reference its output schema file in `.reforge/schemas/`
- **FR-002**: Each markdown schema file MUST document: root element with namespace, all required attributes, all child elements with data types, and enumerated values where applicable
- **FR-003**: Each markdown schema file MUST include at least one complete XML example that demonstrates proper structure
- **FR-004**: Schema documentation MUST indicate which elements/attributes are required vs optional
- **FR-005**: Schema documentation MUST specify data types for all attributes (string, integer, dateTime, enum values)
- **FR-006**: Markdown schemas MUST reference their corresponding XSD contract file (if one exists) for traceability
- **FR-007**: Command templates MUST include output validation guidance that references the schema for post-generation self-check

### Design Decision: Markdown-Only Deployment

The framework deploys **markdown schemas only** (not XSD files) for the following reasons:

1. **Token Efficiency**: XSD files are verbose XML syntax; markdown provides the same structural information in ~50% fewer tokens
2. **LLM Readability**: AI agents parse markdown more naturally than XSD syntax
3. **Constitution Compliance**: Principle I (LLM-First Architecture) emphasizes LLM-native formats over machine-specific formats
4. **Zero Dependencies**: XSD validation would require external tooling, violating Principle IV

XSD contracts remain in `specs/*/contracts/` as the authoritative source during development, with markdown schemas as the deployed LLM-friendly representation.

### Key Entities

- **Markdown Schema**: Human-readable schema documentation file (`.reforge/schemas/*.md`) that guides AI output generation
- **XSD Contract**: Formal XML Schema Definition file (`specs/*/contracts/*.xsd`) that serves as the authoritative structural definition during development
- **Command Template**: Prompt template (`.reforge/commands/*.md`) that references schemas and guides extraction workflow

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of extraction commands reference their corresponding schema file in command documentation
- **SC-002**: 100% of markdown schema files include a complete XML example section
- **SC-003**: AI agents can generate schema-compliant XML output by reading only the markdown schema (no XSD access needed)
- **SC-004**: Schema documentation is sufficient for an agent to self-validate output structure without external tools
- **SC-005**: All markdown schemas include a "Contract Reference" section linking to the corresponding XSD file (where applicable)

## Assumptions

- AI agents can understand and follow markdown-formatted schema documentation
- XML namespaces can be correctly applied by AI agents based on documented examples
- The token cost savings of markdown over XSD (~50%) justifies maintaining two formats
- Schema versioning follows semantic versioning and is tracked in the schema files themselves
