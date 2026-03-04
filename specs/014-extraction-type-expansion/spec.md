# Feature Specification: Extraction Type Expansion

**Feature Branch**: `014-extraction-type-expansion`
**Created**: 2026-03-04
**Status**: Draft
**Input**: TCOS-RUMO project experience producing 6 extraction categories beyond the 4 core types
**Depends On**: Common extraction schema (009), extract command, audit/status/generate commands

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Extract Call Sites (Priority: P1)

An AI agent operator runs `/reforge.extract call-sites` against an analyzed legacy codebase to produce a complete map of method/function call relationships with caller and callee source references.

**Why this priority**: Call site mapping is foundational for understanding code dependencies and enabling downstream workflow and architecture analysis.

**Acceptance Scenarios**:

1. **Given** an analyzed codebase, **When** the operator runs `/reforge.extract call-sites`, **Then** the system produces `call-sites.xml` with `<call>` elements containing caller/callee information, dual source references, call type classification, and confidence scores.
2. **Given** a completed call-sites extraction, **When** `/reforge.audit` is run, **Then** call-sites coverage is included in the audit report.

---

### User Story 2 - Extract Dependencies (Priority: P1)

An operator runs `/reforge.extract dependencies` to produce a module dependency graph capturing imports, event subscriptions, interface implementations, and other coupling mechanisms.

**Acceptance Scenarios**:

1. **Given** an analyzed codebase, **When** the operator runs `/reforge.extract dependencies`, **Then** the system produces `dependencies.xml` with `<dep-ref>` elements documenting module-to-module relationships with coupling and direction metadata.

---

### User Story 3 - Extract Functional Requirements (Priority: P1)

An operator runs `/reforge.extract functional-requirements` to derive functional requirements with acceptance criteria from the codebase's behavior.

**Acceptance Scenarios**:

1. **Given** an analyzed codebase with completed business-rules and workflows extractions, **When** the operator runs `/reforge.extract functional-requirements`, **Then** the system produces `functional-requirements.xml` with `<requirement>` elements containing title, description, acceptance criteria, and cross-references.

---

### User Story 4 - Extract Non-Functional Requirements (Priority: P2)

An operator runs `/reforge.extract non-functional` to extract NFRs/SLAs and security findings (CWE-mapped) from the codebase.

**Acceptance Scenarios**:

1. **Given** an analyzed codebase, **When** the operator runs `/reforge.extract non-functional`, **Then** the system produces `non-functional-requirements.xml` with dual containers: `<requirements>` for NFRs and `<findings>` for security issues with CWE IDs.

---

### User Story 5 - Extract Architecture (Priority: P2)

An operator runs `/reforge.extract architecture` to document architectural components, integration points, and design patterns. Optional `--subtype` flag allows focused extraction.

**Acceptance Scenarios**:

1. **Given** an analyzed codebase, **When** the operator runs `/reforge.extract architecture`, **Then** the system produces `architecture.xml` with `<components>`, `<integrations>`, and `<patterns>` containers.
2. **Given** `--subtype design-patterns` is specified, **When** the extraction runs, **Then** only the `<patterns>` container is populated.

---

### User Story 6 - Extract Issues (Priority: P2)

An operator runs `/reforge.extract issues` to catalog bugs, defects, TODOs, technical debt, and operational issues found in the codebase.

**Acceptance Scenarios**:

1. **Given** an analyzed codebase, **When** the operator runs `/reforge.extract issues`, **Then** the system produces `issues.xml` with `<bugs>` and `<issues-list>` containers.

---

### User Story 7 - All New Types Integrated with Existing Commands (Priority: P1)

All 6 new extraction types are recognized by `/reforge.audit`, `/reforge.status`, and `/reforge.generate`.

**Acceptance Scenarios**:

1. **Given** completed extractions of any new type, **When** `/reforge.status` is run, **Then** the new types appear in the Extraction Status table.
2. **Given** completed extractions, **When** `/reforge.audit` is run with a new type argument, **Then** coverage is reported for that type.
3. **Given** completed extractions, **When** `/reforge.generate markdown --scope call-sites` is run, **Then** documentation is generated scoped to call-sites data.

---

## Design Decisions

1. **One combined spec** — All 6 types in a single feature to avoid 6x boilerplate.
2. **All types in extract.md** — Each type is a section in the existing extract command, not a standalone command.
3. **Architecture sub-type routing** — Optional `--subtype design-patterns|integrations|infrastructure` for focused extraction.
4. **Non-functional dual containers** — `<requirements>` + `<findings>` under one root element.
5. **Single file per type** — Consolidated output per extraction type.
6. **Call-sites dual source refs** — `<caller-source>` + `<callee-source>` both use `SourceReferenceType`.
7. **Glossary prefix registration** — `GLOSS` prefix added to common-schema.md Type Prefix Registry.

## Schema Changes

- `common-schema.md`: 7 new root elements + 11 new ID prefixes (+ GLOSS fix)
- 6 new schema markdown files in `.reforge/schemas/`
- 6 new XSD files in `.reforge/schemas/xsd/`

## Command Changes

- `extract.md`: 6 new extraction type sections + updated argument list
- `audit.md`: 6 new types in valid types list
- `status.md`: 6 new file checks, table rows, JSON entries
- `generate.md`: 6 new `--scope` values
