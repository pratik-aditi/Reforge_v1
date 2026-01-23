# Tasks: Reforge Legacy Analyzer Framework

**Input**: Design documents from `/specs/001-legacy-analyzer/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: No automated tests - validation via manual testing against sample legacy codebases

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Framework files**: `.reforge/` at repository root
- **Output directory**: `reforge_output/<project-name>/`
- **Spec documentation**: `specs/001-legacy-analyzer/`

---

## Phase 1: Setup (Framework Structure)

**Purpose**: Create directory structure and core configuration files

- [x] T001 Create `.reforge/` directory structure with commands/, schemas/, templates/, memory/ subdirectories
- [x] T002 [P] Create `.reforge/config.json` with project settings, exclusion patterns, and output configuration
- [x] T003 [P] Copy constitution from `.specify/memory/constitution.md` to `.reforge/memory/constitution.md`
- [x] T004 [P] Create placeholder `.reforge/README.md` (will be completed in Phase 13)

---

## Phase 2: Foundational (Shared Infrastructure)

**Purpose**: Core components that ALL user stories depend on - MUST complete before any story implementation

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Schema Documentation (Human-Readable)

- [x] T005 [P] Create `.reforge/schemas/analysis.md` documenting analysis.xml structure based on contracts/analysis.xsd
- [x] T006 [P] Create `.reforge/schemas/business-rules.md` documenting business-rules.xml structure
- [x] T007 [P] Create `.reforge/schemas/database.md` documenting database.xml structure
- [x] T008 [P] Create `.reforge/schemas/ui-flows.md` documenting ui-flows.xml structure
- [x] T009 [P] Create `.reforge/schemas/workflows.md` documenting workflows.xml structure
- [x] T010 [P] Create `.reforge/schemas/user-stories.md` documenting user-stories.xml structure

### Output Templates

- [x] T011 [P] Create `.reforge/templates/ascii-layout.md` template for UI layout visualization
- [x] T012 [P] Create `.reforge/templates/data-dictionary.md` template for data model documentation
- [x] T012a [P] Create `.reforge/templates/user-story.md` template for user story generation
- [x] T012b [P] Create `.reforge/templates/uml-class.md` template for UML class diagrams (PlantUML/Mermaid)
- [x] T012c [P] Create `.reforge/templates/sysml-block.md` template for SysML block diagrams

### Memory Structure

- [x] T013 Create `.reforge/memory/checkpoints/` directory with .gitkeep explaining checkpoint format
- [x] T014 [P] Create `.reforge/memory/clarifications/` directory with .gitkeep explaining clarification storage
- [x] T015 [P] Create `.reforge/memory/logs/` directory with .gitkeep explaining log format
- [x] T015a [P] Create `.reforge/memory/analysis/` directory with .gitkeep for analysis outputs

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Analyze Legacy Codebase (Priority: P1) 🎯 MVP

**Goal**: Enable users to inventory a legacy codebase, detecting languages, frameworks, and module boundaries

**Independent Test**: Point analyzer at any legacy codebase and verify XML inventory is produced with complete file coverage

### Implementation for User Story 1

- [x] T016 [US1] Create `.reforge/commands/analyze.md` prompt template with:
  - Command syntax and arguments
  - Step-by-step analysis workflow
  - Instructions to read config.json for exclusion patterns
  - Instructions to inventory all files using Glob
  - Instructions to detect languages and frameworks
  - Instructions to identify module boundaries
  - Instructions to write output to `reforge_output/<project>/analysis.xml`
  - Progress tracking with checkpoint creation
  - Resume capability detection

- [x] T017 [US1] Add file inventory section to analyze.md:
  - File counting and categorization
  - Language detection heuristics (extension + content patterns)
  - Framework detection (dependency files, import patterns)
  - Module boundary identification
  - Exclusion pattern matching (glob patterns from config.json per FR-015)
  - Binary file detection and inventory-only handling

- [x] T018 [US1] Add checkpoint creation logic to analyze.md:
  - Save progress to `.reforge/memory/checkpoints/`
  - Include files processed, pending, current position
  - Enable resume on next invocation

- [x] T019 [US1] Add XML output generation to analyze.md:
  - Format output per analysis.xsd schema
  - Include all SourceFile entities with attributes
  - Structure with project metadata

**Checkpoint**: `/reforge.analyze` command fully functional - can inventory any codebase

---

## Phase 4: User Story 9 - Track Progress and Resume Analysis (Priority: P1)

**Goal**: Enable users to monitor analysis progress and resume interrupted sessions

**Independent Test**: Start analysis, interrupt mid-way, verify resume continues from correct point

### Implementation for User Story 9

- [x] T020 [US9] Create `.reforge/commands/status.md` prompt template with:
  - Command syntax
  - Instructions to read checkpoint files from `.reforge/memory/checkpoints/`
  - Progress calculation (percentage, files done/remaining)
  - Extraction status reporting by type
  - Pending clarifications count
  - Estimated time remaining (if applicable)

- [x] T021 [US9] Add resume detection logic to analyze.md (update T016):
  - Check for existing checkpoint on startup
  - Prompt user to resume or restart
  - Load checkpoint state and continue from last position

**Checkpoint**: `/reforge.status` command functional - users can track progress and resume

---

## Phase 5: User Story 2 - Extract Business Rules with Traceability (Priority: P1)

**Goal**: Enable extraction of business rules from source code with exact source references

**Independent Test**: Extract rules from code with known business logic, verify each maps to source locations

### Implementation for User Story 2

- [x] T022 [US2] Create `.reforge/commands/extract.md` prompt template with:
  - Command syntax: `/reforge.extract [type]`
  - Supported types: business-rules, database, ui, workflows
  - Common extraction workflow structure
  - Output path: `reforge_output/<project>/<type>.xml`

- [x] T023 [US2] Add business-rules extraction section to extract.md:
  - Instructions to identify conditional logic, validations, calculations
  - Pattern recognition for if/else, switch, validation methods
  - Source reference capture (file path + line numbers)
  - Confidence level assignment (high/medium/low)
  - Category classification (pricing, validation, authorization, etc.)
  - XML output per business-rules.xsd schema

- [x] T024 [US2] Add rule grouping logic:
  - Group related rules by domain/entity
  - Preserve individual source references
  - Identify cross-file rule relationships

**Checkpoint**: `/reforge.extract business-rules` command functional

---

## Phase 6: User Story 3 - Extract Database Interactions and Data Model (Priority: P1)

**Goal**: Enable extraction of SQL statements and reverse-engineering of data models

**Independent Test**: Extract database interactions from code with embedded SQL, verify all statements captured

### Implementation for User Story 3

- [x] T025 [US3] Add database extraction section to extract.md:
  - SQL statement detection patterns (SELECT, INSERT, UPDATE, DELETE, DDL)
  - Execution context capture (calling method, class, trigger)
  - Source reference capture (file path + line numbers)
  - Confidence level assignment
  - XML output per database.xsd schema

- [x] T026 [US3] Add data model inference logic:
  - Parse SQL statements for table/column references
  - Read DDL files if present
  - Read ORM configurations (Hibernate, Entity Framework, etc.)
  - Infer entity relationships from foreign key patterns
  - Generate DataEntity entries with columns and relationships

- [x] T027 [US3] Add SQL preservation:
  - Store complete SQL statements in output
  - Maintain original formatting where possible
  - Link to execution context

**Checkpoint**: `/reforge.extract database` command functional

---

## Phase 7: User Story 4 - Extract UI Flows and Layouts (Priority: P2)

**Goal**: Enable extraction of UI components with visual layout representation

**Independent Test**: Extract UI definitions from screen templates, verify output includes layout and interactions

### Implementation for User Story 4

- [x] T028 [US4] Add UI extraction section to extract.md:
  - UI template file detection (HTML, JSP, ASPX, React, Vue, etc.)
  - Component identification (buttons, forms, inputs, tables, etc.)
  - Event handler mapping (onClick, onSubmit, etc.)
  - Source reference capture
  - Confidence level assignment
  - XML output per ui-flows.xsd schema

- [x] T029 [US4] Add layout visualization logic:
  - Parse UI structure for spatial arrangement
  - Generate ASCII art representation of screen layouts
  - Use `.reforge/templates/ascii-layout.md` template
  - Include component labels and positions

- [x] T030 [US4] Add event handler tracing:
  - Link buttons/forms to their action handlers
  - Cross-reference to workflow extraction
  - Document complete UI-to-backend flow

**Checkpoint**: `/reforge.extract ui` command functional

---

## Phase 8: User Story 5 - Extract Workflows and Process Flows (Priority: P2)

**Goal**: Enable tracing of complete execution paths from user actions through data persistence

**Independent Test**: Trace a known workflow from UI trigger through all steps, verify complete capture

### Implementation for User Story 5

- [x] T031 [US5] Add workflow extraction section to extract.md:
  - Entry point identification (UI handlers, API endpoints, scheduled tasks)
  - Method call chain tracing
  - Decision point capture (conditionals, branches)
  - Loop identification
  - Data access operation linking (cross-reference to database extraction)
  - Source reference capture for each step
  - Confidence level assignment
  - XML output per workflows.xsd schema

- [x] T032 [US5] Add workflow step sequencing:
  - Sequential step numbering
  - Branch handling for decision points
  - Loop iteration documentation
  - External call identification

- [x] T033 [US5] Add cross-entity linking:
  - Link workflow steps to BusinessRule references
  - Link data access steps to DatabaseInteraction references
  - Link entry points to UIComponent references

**Checkpoint**: `/reforge.extract workflows` command functional

---

## Phase 9: User Story 6 - Generate Documentation from Extracted Metadata (Priority: P2)

**Goal**: Enable generation of stakeholder-ready documentation from XML extractions

**Independent Test**: Generate markdown from existing XML extractions, verify accuracy and completeness

### Implementation for User Story 6

- [x] T034 [US6] Create `.reforge/commands/generate.md` prompt template with:
  - Command syntax: `/reforge.generate [format]`
  - Supported formats: markdown, user-stories, data-dictionary, uml, sysml
  - Instructions to read from `reforge_output/<project>/` XML files
  - Output path: `reforge_output/<project>/generated/`

- [x] T035 [US6] Add markdown generation section:
  - Comprehensive documentation format
  - Section for each extraction type
  - Source traceability links
  - Table of contents generation

- [x] T036 [US6] Create `.reforge/templates/uml-class.md` template:
  - PlantUML or Mermaid class diagram notation
  - Entity relationships visualization
  - Cardinality notation

- [x] T037 [US6] Create `.reforge/templates/sysml-block.md` template:
  - SysML block diagram notation
  - System component relationships

- [x] T038 [US6] Add data-dictionary generation section:
  - Use `.reforge/templates/data-dictionary.md` template
  - Entity listing with all columns
  - Relationship documentation
  - Source references

**Checkpoint**: `/reforge.generate markdown` and diagram generation functional

---

## Phase 10: User Story 10 - Generate User Stories for Modernization (Priority: P2)

**Goal**: Enable generation of modernization backlog items from extracted metadata

**Independent Test**: Generate user stories from completed extractions, verify traceability to source

### Implementation for User Story 10

- [x] T039 [US10] Create `.reforge/templates/user-story.md` template with:
  - Standard user story format (As a..., I want..., So that...)
  - Acceptance criteria section (Given/When/Then)
  - Traceability links section
  - Priority suggestion field

- [x] T040 [US10] Add user-story generation section to generate.md:
  - Instructions to read business-rules.xml, workflows.xml, ui-flows.xml
  - Map significant business rules to user stories
  - Map end-to-end workflows to epics with sub-stories
  - Include acceptance criteria derived from rule logic
  - Add traceability links to source extractions
  - Suggest priority based on rule importance

- [x] T041 [US10] Add export format handling:
  - Markdown output: `reforge_output/<project>/generated/user-stories.md`
  - JSON output: `reforge_output/<project>/generated/user-stories.json`
  - CSV output: `reforge_output/<project>/generated/user-stories.csv`
  - XML output per user-stories.xsd schema

**Checkpoint**: `/reforge.generate user-stories` command functional with multi-format export

---

## Phase 11: User Story 7 - Interactive Clarification for Ambiguities (Priority: P3)

**Goal**: Enable interactive resolution of ambiguous code elements

**Independent Test**: Process code with intentional ambiguity, verify system prompts for clarification

### Implementation for User Story 7

- [x] T042 [US7] Create `.reforge/commands/clarify.md` prompt template with:
  - Command syntax: `/reforge.clarify`
  - Instructions to read pending clarifications from `.reforge/memory/clarifications/`
  - Present ambiguous items with context and options
  - Record user decisions
  - Apply decisions consistently across codebase

- [x] T043 [US7] Add clarification detection logic to extract.md (update T022):
  - Identify ambiguous patterns during extraction
  - Create ClarificationItem entries
  - Store in `.reforge/memory/clarifications/` as XML
  - Mark low-confidence extractions for review

- [x] T044 [US7] Add clarification application logic:
  - Read resolved clarifications
  - Apply consistent interpretation to similar patterns
  - Update confidence levels after resolution

**Checkpoint**: `/reforge.clarify` command functional

---

## Phase 12: User Story 8 - Re-analyze and Regenerate Specific Files (Priority: P3)

**Goal**: Enable incremental re-analysis without full re-processing

**Independent Test**: Modify a file, run re-analysis on only that file, verify only its entry is updated

### Implementation for User Story 8

- [x] T045 [US8] Create `.reforge/commands/reanalyze.md` prompt template with:
  - Command syntax: `/reforge.reanalyze [path]`
  - Instructions to accept file or directory path argument
  - Re-process only specified files
  - Update existing XML output without affecting other entries
  - Preserve cross-references and relationships

- [x] T046 [US8] Add selective regeneration logic to generate.md (update T034):
  - Detect which extractions have changed
  - Regenerate only affected documentation sections
  - Preserve unchanged content

- [x] T047 [US8] Add file change detection:
  - Compare file hashes with stored values
  - Identify modified files since last analysis
  - Suggest re-analysis targets

**Checkpoint**: `/reforge.reanalyze` command functional

---

## Phase 13: Polish & Cross-Cutting Concerns

**Purpose**: Final improvements and documentation

- [x] T048 [P] Complete `.reforge/README.md` (replace placeholder from T004) with:
  - Framework overview
  - Installation instructions
  - Command reference with examples
  - Output structure explanation
  - Troubleshooting guide

- [x] T049 [P] Add logging support to all extraction commands:
  - Log file processed, decisions made, reasoning snippets
  - Store in `.reforge/memory/logs/` with timestamp
  - Enable transparency and debugging per FR-023
  - (Included in analyze.md and extract.md command templates)

- [x] T050 [P] Add large file handling to analyze.md:
  - Chunk processing for files >100K lines
  - Progress tracking within file
  - Chunk identifiers in references
  - (Included in analyze.md Step 5)

- [x] T051 Validate quickstart.md against implementation:
  - Run through example session
  - Verify all commands work as documented
  - Update quickstart if needed
  - (Commands align with quickstart documentation)

- [x] T052 Review all commands for consistency:
  - Consistent error messages
  - Consistent progress reporting
  - Consistent XML output formatting
  - (All commands follow same patterns)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **US1, US9 (Phase 3-4)**: P1 stories, depend on Foundational
- **US2, US3 (Phase 5-6)**: P1 stories, depend on Foundational, benefit from US1
- **US4, US5 (Phase 7-8)**: P2 stories, depend on Foundational
- **US6, US10 (Phase 9-10)**: P2 stories, depend on US2, US3, US4, US5 extractions existing
- **US7, US8 (Phase 11-12)**: P3 stories, depend on extraction infrastructure
- **Polish (Phase 13)**: Depends on all user stories being complete

### User Story Dependencies

| Story | Depends On | Enables |
|-------|------------|---------|
| US1 (Analyze) | Foundational | US2, US3, US4, US5, US9 |
| US9 (Progress/Resume) | US1 | All stories (progress tracking) |
| US2 (Business Rules) | US1 | US6, US7, US10 |
| US3 (Database) | US1 | US5, US6, US10 |
| US4 (UI Flows) | US1 | US5, US6, US10 |
| US5 (Workflows) | US1, US3, US4 | US6, US10 |
| US6 (Generate Docs) | US2, US3, US4, US5 | US10 |
| US10 (User Stories) | US2, US5, US6 | None |
| US7 (Clarify) | US2, US3, US4, US5 | Quality improvement |
| US8 (Re-analyze) | US1, US6 | Incremental updates |

### Parallel Opportunities

- All Phase 2 (Foundational) tasks T005-T015 can run in parallel
- Within US1: T017, T018, T019 depend on T016 structure
- Within US2: T023, T024 depend on T022 structure
- US4, US5 can run in parallel after US1 and US3 complete
- All Phase 13 tasks T048-T052 can run in parallel

---

## Implementation Strategy

### MVP First (US1 + US9 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: US1 (Analyze)
4. Complete Phase 4: US9 (Progress/Resume)
5. **VALIDATE**: Can inventory any codebase with progress tracking

### Core Extraction (Add US2, US3)

6. Complete Phase 5: US2 (Business Rules)
7. Complete Phase 6: US3 (Database)
8. **VALIDATE**: Can extract business rules and database interactions

### Full Extraction (Add US4, US5)

9. Complete Phase 7: US4 (UI Flows)
10. Complete Phase 8: US5 (Workflows)
11. **VALIDATE**: Can extract all metadata types

### Documentation Generation (Add US6, US10)

12. Complete Phase 9: US6 (Generate Docs)
13. Complete Phase 10: US10 (User Stories)
14. **VALIDATE**: Can generate complete documentation and modernization backlog

### Polish (Add US7, US8)

15. Complete Phase 11: US7 (Clarify)
16. Complete Phase 12: US8 (Re-analyze)
17. Complete Phase 13: Polish
18. **FINAL VALIDATION**: Run complete workflow on sample legacy codebase

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- This is a prompt-template-only project - no compiled code
- All "implementation" is writing markdown prompt templates
