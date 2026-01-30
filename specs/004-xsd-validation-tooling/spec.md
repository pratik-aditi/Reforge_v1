# Feature Specification: XSD Validation Tooling

**Feature Branch**: `004-xsd-validation-tooling`
**Created**: 2026-01-29
**Status**: Draft
**Input**: User description: "Deploy XSD schemas to .reforge folder and provide CLI validation script for LLM to validate XML output against schemas"

## Problem Statement

Currently, Reforge uses markdown schemas for LLM guidance but XSD contracts remain only in the development `specs/` folder. This means:
- AI agents cannot validate their XML output against formal schemas
- Validation errors are only caught when humans review output
- No automated feedback loop for the LLM to self-correct malformed XML

This feature adds **optional tooling** (per Constitution Principle VI) that:
1. Deploys XSD schemas alongside markdown schemas during install
2. Provides a CLI script the LLM can invoke to validate XML output
3. Returns structured error messages the LLM can parse and use to fix issues

## User Scenarios & Testing *(mandatory)*

### User Story 1 - XML Output Validation (Priority: P1)

As an AI agent executing Reforge extraction commands, I need to validate my XML output against the formal schema so I can detect and fix structural errors before completing the extraction.

**Why this priority**: This is the core value - enabling LLMs to self-validate and self-correct, improving output quality without human intervention.

**Independent Test**: Can be fully tested by running the validation script against a known-valid XML file (should pass) and a known-invalid XML file (should return parseable errors).

**Acceptance Scenarios**:

1. **Given** an AI agent has generated `business-rules.xml`, **When** it runs `reforge-scripts validate-xml business-rules.xml business-rules`, **Then** the script returns exit code 0 and message "Valid" if the XML conforms to the schema
2. **Given** an AI agent has generated malformed XML, **When** it runs the validation script, **Then** the script returns exit code 1 and a structured error message indicating the line number and nature of the error
3. **Given** the validation script reports an error, **When** the AI agent reads the error output, **Then** the error format is clear enough for the agent to identify and fix the specific issue

---

### User Story 2 - XSD Schema Deployment (Priority: P2)

As a user installing Reforge into a project, I need XSD schemas copied to `.reforge/schemas/xsd/` so the validation tooling has access to formal schema definitions.

**Why this priority**: Required infrastructure for P1 to work, but has no standalone value without the validation script.

**Independent Test**: Can be tested by running Reforge installation and verifying XSD files exist in `.reforge/schemas/xsd/`.

**Acceptance Scenarios**:

1. **Given** a user runs `reforge init` (or equivalent install command), **When** installation completes, **Then** all XSD files from `specs/*/contracts/` are copied to `.reforge/schemas/xsd/`
2. **Given** XSD files exist in `.reforge/schemas/xsd/`, **When** a user lists the directory, **Then** each XSD filename matches its corresponding markdown schema (e.g., `business-rules.xsd` for `business-rules.md`)
3. **Given** XSD schemas are deployed, **When** an update is run, **Then** XSD files are updated if source contracts have changed

---

### User Story 3 - Validation Integration in Commands (Priority: P3)

As an AI agent, I need extraction commands to include optional validation steps so I can automatically validate output as part of the extraction workflow.

**Why this priority**: Quality-of-life improvement that builds on P1+P2; the validation script can be used manually without command integration.

**Independent Test**: Can be tested by running `/reforge.extract business-rules` and observing the optional validation step in the workflow.

**Acceptance Scenarios**:

1. **Given** an extraction command template includes a validation step, **When** the AI agent executes the command, **Then** it can optionally run validation after generating output
2. **Given** validation fails during an extraction, **When** the AI agent receives the error, **Then** it can attempt to fix the XML and re-validate (up to 3 retry attempts)

---

### Edge Cases

- What happens if `xmllint` is not installed? The script MUST detect this and provide a clear error message with installation instructions.
- What happens if the XSD file for a schema type doesn't exist? The script MUST return a clear error indicating which schema is missing.
- What happens if the XML file path is invalid? The script MUST return exit code 2 with a "file not found" message.
- How does the system handle XML with encoding issues? The script MUST handle UTF-8 and common encodings, reporting encoding errors clearly.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The `reforge-scripts validate-xml` command MUST accept two arguments: `<xml-file-path>` and `<schema-type>`
- **FR-002**: The validation script MUST use `xmllint --schema` for XML validation against XSD
- **FR-003**: The validation script MUST return exit code 0 for valid XML, exit code 1 for invalid XML, and exit code 2 for usage/system errors
- **FR-004**: Error output MUST include: line number, column number (if available), and error description in a consistent parseable format
- **FR-005**: The Reforge install process MUST copy all XSD files from `specs/*/contracts/*.xsd` to `.reforge/schemas/xsd/`
- **FR-006**: XSD filenames in `.reforge/schemas/xsd/` MUST match their corresponding markdown schema names (e.g., `analysis.xsd`, `business-rules.xsd`)
- **FR-007**: The validation script MUST check for `xmllint` availability and provide installation guidance if missing
- **FR-008**: The validation script MUST support a `--help` flag that displays usage information
- **FR-009**: The validation script MUST support a `--list-schemas` flag that shows available schema types

### Non-Functional Requirements

- **NFR-001**: Validation of a typical extraction file (< 1MB) MUST complete in under 5 seconds
- **NFR-002**: The validation script MUST work on macOS, Linux, and WSL without modification
- **NFR-003**: The tooling MUST NOT be required for core Reforge functionality (optional enhancement per Constitution Principle VI)

### Key Entities

- **XSD Schema**: Formal XML Schema Definition file deployed to `.reforge/schemas/xsd/` for validation
- **Validation Script**: Python CLI command (`reforge-scripts validate-xml`) that invokes `xmllint` and formats output for LLM consumption
- **Validation Result**: Structured output containing status (valid/invalid), error details (if any), and suggested fixes

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of extraction schema types have corresponding XSD files deployed to `.reforge/schemas/xsd/`
- **SC-002**: Validation script correctly identifies valid XML (0% false negatives on conformant files)
- **SC-003**: Validation script correctly identifies invalid XML (0% false positives on malformed files)
- **SC-004**: AI agents can parse validation error output and successfully fix common XML issues (missing closing tags, invalid attributes, wrong element order)
- **SC-005**: Validation adds less than 5 seconds to extraction workflow for files under 1MB

## Assumptions

- `xmllint` (from libxml2) is available or easily installable on target systems
- AI agents can execute bash scripts via their tool capabilities
- Error messages from `xmllint` are consistent enough to parse reliably
- Users are willing to install `xmllint` if not present (optional tooling)

## Design Notes

### Error Output Format

The validation script should output errors in a format optimized for LLM parsing:

```
VALIDATION_FAILED
FILE: reforge_output/myapp/extractions/business-rules.xml
SCHEMA: business-rules
ERROR_COUNT: 2
---
LINE: 45
COLUMN: 12
MESSAGE: Element 'ruel': This element is not expected. Expected is 'rule'.
SUGGESTION: Check spelling of element name on line 45
---
LINE: 67
COLUMN: 5
MESSAGE: Element 'rule': Missing required attribute 'id'.
SUGGESTION: Add id attribute to <rule> element on line 67
```

### Constitution Compliance

This feature complies with Principle VI (Extensibility via Tooling Layer):
- Core workflow (markdown schemas + LLM generation) remains unchanged
- Validation is optional tooling that enhances quality
- No new dependencies for core functionality
- Script is clearly separated in `.reforge/scripts/`
