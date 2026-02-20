# Tasks: Common Extraction Schema

**Input**: Design documents from `/specs/009-common-extraction-schema/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/

**Tests**: Not requested — no test tasks included.

**Organization**: Tasks grouped by user story. US2 is foundational (blocks all other stories). US1+US3 combined (both modify extract.md). US4 is independent (different files).

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- All schema files: `.reforge/schemas/` and `.reforge/schemas/xsd/`
- Command templates: `.reforge/commands/`
- No new directories needed

---

## Phase 1: Setup

**Purpose**: No project structure changes needed — all target directories already exist.

- [x] T001 Verify existing schema files are present and readable in `.reforge/schemas/` and `.reforge/schemas/xsd/` (business-rules.md, database.md, ui-flows.md, workflows.md + corresponding .xsd files)

---

## Phase 2: Foundational — Schema Definition (US2, P1)

**Purpose**: Create the common schema definition files. BLOCKS all subsequent phases.

**⚠️ CRITICAL**: No other story work can begin until both common schema files exist.

- [x] T002 [US2] Create common schema markdown definition in `.reforge/schemas/common-schema.md` — document all shared elements: root attributes (`project-id`, `version`, `schema-version`, `generated`, `xmlns`), `<metadata>` container with `<total-count>`, `<confidence-distribution>` (high/medium/low counts), `<extraction-timestamp>`, canonical `<source>` reference format (`file`, `line-start`, `line-end`, optional `<snippet>`), `ConfidenceType` enumeration (high/medium/low), ID pattern convention (`{PREFIX}-{CATEGORY}-{SEQUENCE}` with type prefix registry), namespace URI `http://reforge.dev/schema/extraction`, initial schema-version `1.0.0`, extensibility notes for type-specific additions, and validation rules from data-model.md. Structure per contract in `specs/009-common-extraction-schema/contracts/common-schema-contract.md`
- [x] T003 [US2] Create common schema XSD in `.reforge/schemas/xsd/common-schema.xsd` — define `ConfidenceType` (simpleType enumeration), `SourceReferenceType` (complexType with `file`, `line-start`, `line-end` attributes and optional `snippet` child), `MetadataType` (complexType with `total-count`, `confidence-distribution`, `extraction-timestamp` children), `ConfidenceDistributionType` (complexType with `high`, `medium`, `low` integer children). Use `targetNamespace="http://reforge.dev/schema/extraction"`. Ensure XSD parity with `common-schema.md` per FR-010

**Checkpoint**: Common schema definition complete — both markdown and XSD exist. Verify US2 acceptance: a contributor can determine all shared structural elements by reading `common-schema.md` alone.

---

## Phase 3: User Story 1 + User Story 3 — Consistent Output & Validation Gate (P1 + P2)

**Goal**: Update the extract command template so all extraction output conforms to the common schema, and add the validation gate that enforces conformance at write time.

**Independent Test (US1)**: Run `/reforge.extract business-rules` and `/reforge.extract database` on any codebase. Verify both output files use identical root attribute names, metadata structure, and source reference format. Validate against `common-schema.md`.

**Independent Test (US3)**: Temporarily remove `project-id` from an extraction template. Run `/reforge.extract` and verify the agent detects and corrects the missing attribute.

### Implementation

- [x] T004 [US1] Update business-rules XML example in `.reforge/commands/extract.md` (Step 5 section) — change `xmlns` from `http://reforge.dev/schema/business-rules` to `http://reforge.dev/schema/extraction`, add `schema-version="1.0.0"` attribute, add `<metadata>` as first child of root element with `<total-count>`, `<confidence-distribution>`, and `<extraction-timestamp>`, keep existing `<rule>` structure unchanged
- [x] T005 [US1] Update database XML example in `.reforge/commands/extract.md` (Step 6 section) — change `xmlns` to `http://reforge.dev/schema/extraction`, add `schema-version="1.0.0"`, add `<metadata>` as first child of `<database>` root (replacing the `entity-count` attribute pattern with metadata container), keep `<data-model>` and `<interactions>` structure unchanged
- [x] T006 [US1] Update ui-flows XML example in `.reforge/commands/extract.md` (Step 7 section) — change `xmlns` to `http://reforge.dev/schema/extraction`, add `schema-version="1.0.0"`, add `<metadata>` with aggregate counts from screens and components, keep `<screens>` and `<navigation>` structure unchanged
- [x] T007 [US1] Update workflows XML example in `.reforge/commands/extract.md` (Step 4 section under Workflow Extraction) — change `xmlns` to `http://reforge.dev/schema/extraction`, add `schema-version="1.0.0"`, add `<metadata>` as first child, keep `<workflow>` structure unchanged
- [x] T008 [US1] Update the "Common Elements" section near bottom of `.reforge/commands/extract.md` — add reference to `common-schema.md` for shared element definitions, update "Source References" subsection to explicitly state canonical format per common schema, update "Output Schema References" section to include `common-schema.md` as first entry
- [x] T009 [US3] Add "Step 5.6: Schema Compliance Validation" section to `.reforge/commands/extract.md` between existing Step 5.5 (Post-Extraction Verification) and Step 6 (Report Results) — instruct agent to read `.reforge/schemas/common-schema.md`, then check output for: (1) required root attributes present (`project-id`, `version`, `schema-version`, `generated`, `xmlns`), (2) namespace equals `http://reforge.dev/schema/extraction`, (3) `<metadata>` element present with all required children, (4) confidence distribution sums to total count, (5) all `<source>` elements use canonical `line-start`/`line-end` format, (6) `schema-version` is valid semver
- [x] T010 [US3] Add auto-correction rules to Step 5.6 in `.reforge/commands/extract.md` — document corrections: missing `schema-version` → add `schema-version="1.0.0"`, missing `xmlns` → add namespace URI, missing `<metadata>` → generate from item counts, legacy source ref format → normalize to `line-start`/`line-end`, missing `generated` → add current timestamp
- [x] T011 [US3] Add SCHEMA-WARNING behavior to Step 5.6 in `.reforge/commands/extract.md` — when auto-correction not possible, insert `<!-- SCHEMA-WARNING: [description] -->` XML comment at violation point, continue writing file (do not abort), include warning count and details in Step 6 report summary
- [x] T012 [US1] Update Step 6 (Report Results) in `.reforge/commands/extract.md` for each extraction type — add "Schema Compliance" section to report template showing: validation checks passed/failed, auto-corrections applied, SCHEMA-WARNING count, schema-version used
- [x] T013 [US1] Update the "Required Validation" section near bottom of `.reforge/commands/extract.md` — add schema compliance validation reference alongside existing structural (XSD) and content validation, note that schema compliance (Step 5.6) checks structural conformance to common schema while XSD validation checks formal type correctness

**Checkpoint**: Extract command template now produces conformant output with validation gate. Verify: all 4 XML examples use `http://reforge.dev/schema/extraction` namespace, include `schema-version="1.0.0"`, contain `<metadata>` sections. Step 5.6 validation gate is documented.

---

## Phase 4: User Story 4 — Migrate Existing Schemas (P3)

**Goal**: Update all type-specific schema files to reference `common-schema.md`/`common-schema.xsd` instead of redefining shared elements.

**Independent Test**: Open each updated type-specific schema and verify shared elements (root attributes, metadata, source references, confidence) link to common schema — no redefinition.

### Markdown Schema Updates

- [x] T014 [P] [US4] Update `.reforge/schemas/business-rules.md` — add "Common Elements" section after Overview linking to `common-schema.md` for root attributes, metadata, source references, confidence vocabulary. Remove the inline "Shared Types" section (ConfidenceType table). Remove the `<source>` attribute table (now in common schema). Update root element example to include `schema-version` and `xmlns="http://reforge.dev/schema/extraction"`. Update the full example XML at bottom to include `<metadata>` and new namespace. Keep type-specific elements (`<rule>`, `<description>`, `<logic>`, `<entities>`, `<related-rules>`) unchanged.
- [x] T015 [P] [US4] Update `.reforge/schemas/database.md` — add "Common Elements" section linking to `common-schema.md`. Remove inline "Shared Types" (ConfidenceType, SourceReferenceType). Update root element to include `schema-version` and new namespace. Update example XML to include `<metadata>` container. Keep type-specific elements (`<data-model>`, `<entity>`, `<column>`, `<relationship>`, `<interactions>`, `<interaction>`) unchanged.
- [x] T016 [P] [US4] Update `.reforge/schemas/ui-flows.md` — add "Common Elements" section linking to `common-schema.md`. Remove inline "Shared Types". Update root element and example XML with `schema-version`, new namespace, and `<metadata>`. Keep type-specific elements (`<screens>`, `<screen>`, `<component>`, `<layout>`, `<navigation>`, `<flow>`) unchanged.
- [x] T017 [P] [US4] Update `.reforge/schemas/workflows.md` — add "Common Elements" section linking to `common-schema.md`. Remove inline "Shared Types". Update root element and example XML with `schema-version`, new namespace, and `<metadata>`. Keep type-specific elements (`<workflow>`, `<steps>`, `<step>`, `<branches>`, `<related>`) unchanged.

### XSD Updates

- [x] T018 [P] [US4] Update `.reforge/schemas/xsd/business-rules.xsd` — change `targetNamespace` to `http://reforge.dev/schema/extraction`, add `<xs:include schemaLocation="common-schema.xsd"/>`, remove local `ConfidenceType` simpleType definition, remove local `SourceReferenceType` complexType definition, update all type references to use the included common types, add `schema-version` attribute to root element definition, add `MetadataType` as required first child of root element
- [x] T019 [P] [US4] Update `.reforge/schemas/xsd/database.xsd` — change `targetNamespace` to `http://reforge.dev/schema/extraction`, add `<xs:include schemaLocation="common-schema.xsd"/>`, remove local `ConfidenceType` and `SourceReferenceType`, update type references, add `schema-version` attribute and `MetadataType` to root element
- [x] T020 [P] [US4] Update `.reforge/schemas/xsd/ui-flows.xsd` — change `targetNamespace` to `http://reforge.dev/schema/extraction`, add `<xs:include schemaLocation="common-schema.xsd"/>`, remove local `ConfidenceType` and `SourceReferenceType`, update type references, add `schema-version` attribute and `MetadataType` to root element
- [x] T021 [P] [US4] Update `.reforge/schemas/xsd/workflows.xsd` — change `targetNamespace` to `http://reforge.dev/schema/extraction`, add `<xs:include schemaLocation="common-schema.xsd"/>`, remove local `ConfidenceType` and `SourceReferenceType`, update type references, add `schema-version` attribute and `MetadataType` to root element

**Checkpoint**: All type-specific schemas reference common schema. Verify: zero duplicate `ConfidenceType` or `SourceReferenceType` definitions across the 4 XSD files. All 4 markdown schemas link to `common-schema.md` for shared elements.

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Final consistency checks across all modified files.

- [x] T022 Cross-check namespace consistency — verify `http://reforge.dev/schema/extraction` appears in: `common-schema.md`, `common-schema.xsd`, all 4 type-specific markdown schemas, all 4 type-specific XSDs, and all 4 XML examples in `extract.md`. No old per-type namespaces should remain.
- [x] T023 Cross-check metadata structure consistency — verify the `<metadata>` container structure is identical in: `common-schema.md` definition, `common-schema.xsd` MetadataType, all 4 XML examples in `extract.md`, and all 4 type-specific schema example outputs
- [x] T024 Verify `common-schema.md` and `common-schema.xsd` parity — every element, attribute, and type defined in the markdown has a corresponding XSD definition, and vice versa
- [x] T025 Verify legacy handling — confirm `extract.md` does NOT reference any old namespace URIs (`http://reforge.dev/schema/business-rules`, etc.) in its XML examples or instructions, and that FR-014 legacy file guidance is present in the validation gate section

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — verification only
- **Foundational (Phase 2, US2)**: Depends on Phase 1 — BLOCKS all subsequent phases
- **US1+US3 (Phase 3)**: Depends on Phase 2 (common schema must exist before extract command can reference it)
- **US4 (Phase 4)**: Depends on Phase 2 (common schema must exist before type-specific schemas can link to it). Independent of Phase 3 — can run in parallel with US1+US3.
- **Polish (Phase 5)**: Depends on Phases 3 and 4 both complete

### User Story Dependencies

- **US2 (P1)**: Foundational — no story dependencies. Creates the common schema.
- **US1 (P1)**: Depends on US2 (schema must exist). Paired with US3 (same file).
- **US3 (P2)**: Depends on US2 (schema must exist). Paired with US1 (same file).
- **US4 (P3)**: Depends on US2 only. **Independent of US1/US3** — different files entirely.

### Within Phases

- Phase 2: T002 before T003 (markdown is authoritative source, XSD mirrors it)
- Phase 3: T004–T008 (US1 examples) before T009–T011 (US3 validation gate), then T012–T013 (reporting updates)
- Phase 4: All 8 tasks (T014–T021) are **fully parallel** — each touches a different file

### Parallel Opportunities

- **Phase 4 is highly parallel**: All 8 schema update tasks touch independent files
- T014, T015, T016, T017 (markdown schemas) — 4 parallel tasks
- T018, T019, T020, T021 (XSD schemas) — 4 parallel tasks
- Phase 3 and Phase 4 can execute in parallel (different files)
- Phase 5 verification tasks are parallel (different checks)

---

## Parallel Example: Phase 4 (US4)

```text
# All 8 tasks can launch in parallel — each modifies a different file:
T014: Update .reforge/schemas/business-rules.md
T015: Update .reforge/schemas/database.md
T016: Update .reforge/schemas/ui-flows.md
T017: Update .reforge/schemas/workflows.md
T018: Update .reforge/schemas/xsd/business-rules.xsd
T019: Update .reforge/schemas/xsd/database.xsd
T020: Update .reforge/schemas/xsd/ui-flows.xsd
T021: Update .reforge/schemas/xsd/workflows.xsd
```

---

## Implementation Strategy

### MVP First (US2 + US1 Only)

1. Complete Phase 1: Setup (verify files exist)
2. Complete Phase 2: Create `common-schema.md` and `common-schema.xsd` (US2)
3. Complete Phase 3: T004–T008 (US1 extract command examples only)
4. **STOP and VALIDATE**: Verify XML examples in extract.md use consistent namespace, schema-version, and metadata
5. The common schema exists and extraction output format is documented — MVP delivered

### Full Delivery

1. Setup → Foundational (US2) → US1+US3 (extract command) → US4 (schema migration) → Polish
2. Each phase adds value: schema → consistent output → enforcement → cleanup

### Parallel Team Strategy

With 2 contributors after Phase 2:
- Contributor A: Phase 3 (US1+US3 — extract command template)
- Contributor B: Phase 4 (US4 — type-specific schema updates, all 8 files parallel)
- Both converge for Phase 5 (verification)

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story
- US1 and US3 are combined in Phase 3 because both modify `.reforge/commands/extract.md`
- US4 tasks are all parallel because each touches a separate schema file
- No test tasks included (not requested in spec)
- Total: 25 tasks across 5 phases
