# Feature Specification: Reforge Legacy Analyzer Framework

**Feature Branch**: `001-legacy-analyzer`
**Created**: 2025-01-13
**Status**: Draft
**Input**: User description: "Create an LLM-driven framework for legacy codebase inventory, analysis, documentation, and user story generation to enable application modernization"

## Clarifications

### Session 2025-01-13

- Q: How should checkpoint state persist between sessions for resumable analysis? → A: XML files in `.reforge/memory/` directory, following SpecKit pattern (`.reforge/` for framework, `reforge_output/` for outputs)
- Q: Should extractions include confidence indicators for LLM uncertainty? → A: Yes, include confidence level (high/medium/low) on each extraction to help users prioritize review
- Q: Should Reforge generate user stories for the modernization project? → A: Yes, add `/reforge.generate user-stories` to produce modernization backlog items from extracted metadata
- Q: Should the system maintain analysis logs for transparency? → A: Yes, log files processed, decisions made, and reasoning snippets to support validation and debugging
- Q: What format(s) should generated user stories be exported in? → A: Markdown + JSON/CSV - both human-readable and machine-parseable for tool integration

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Analyze Legacy Codebase (Priority: P1)

A modernization lead needs to understand a legacy application before planning its rewrite. They invoke the analysis command to scan the entire codebase, and the system inventories all files, identifies programming languages, detects frameworks, maps module boundaries, and produces a structured XML index of the codebase with file-by-file analysis including business logic, dependencies, and relationships.

**Why this priority**: Without a complete inventory and understanding of the existing codebase, no other extraction or documentation work can proceed. This is the foundation for all downstream activities.

**Independent Test**: Can be fully tested by pointing the analyzer at any legacy codebase and verifying that an XML inventory is produced with complete file coverage, language detection, and module mapping.

**Acceptance Scenarios**:

1. **Given** a legacy codebase with mixed languages (e.g., Java, JavaScript, SQL), **When** the user runs the analyze command, **Then** the system produces an XML file listing every source file with its language, purpose classification, and key components identified.
2. **Given** a large codebase with 1000+ files, **When** analysis is invoked, **Then** progress tracking shows completion percentage and the system can resume if interrupted.
3. **Given** incomplete analysis from a previous session, **When** the user invokes analyze again, **Then** the system resumes from the last checkpoint without re-analyzing completed files.

---

### User Story 2 - Extract Business Rules with Traceability (Priority: P1)

A business analyst needs to understand what business rules are embedded in the legacy code. They invoke extraction for business rules, and the system identifies conditional logic, validation rules, calculations, and business constraints. Each extracted rule includes exact source file paths and line numbers so the analyst can verify the extraction against the original code.

**Why this priority**: Business rules are the core intellectual property that must be preserved during modernization. Without accurate extraction and traceability, critical business logic could be lost or incorrectly reimplemented.

**Independent Test**: Can be fully tested by extracting rules from a file with known business logic and verifying each rule maps back to specific source code locations.

**Acceptance Scenarios**:

1. **Given** source code containing conditional business logic (e.g., "if order total > $500, apply 10% discount"), **When** extraction runs, **Then** the output XML contains a rule entry with the logic described, source file path, and line numbers.
2. **Given** validation rules scattered across multiple files, **When** extraction completes, **Then** related rules are grouped by domain/entity while preserving individual source references.
3. **Given** extracted business rules, **When** a user requests re-extraction of specific files, **Then** only those files are re-analyzed and the output is updated without affecting other extractions.

---

### User Story 3 - Extract Database Interactions and Data Model (Priority: P1)

A data architect needs to understand the data layer of the legacy application. They invoke extraction for database interactions, and the system captures all SQL statements, maps them to the code locations that execute them, and reverse-engineers the implied data model including tables, columns, relationships, and constraints.

**Why this priority**: The data model is fundamental infrastructure that must be understood before any modernization work. SQL statements need preservation for potential reuse or translation.

**Independent Test**: Can be fully tested by extracting database interactions from code with embedded SQL and verifying all statements are captured with their execution contexts.

**Acceptance Scenarios**:

1. **Given** code files containing embedded SQL (SELECT, INSERT, UPDATE, DELETE), **When** extraction runs, **Then** each SQL statement is captured with its triggering method, file path, and line numbers.
2. **Given** existing data model files (DDL, ORM configurations, entity definitions), **When** extraction runs, **Then** the system reads and incorporates these into the data model output.
3. **Given** SQL statements referencing tables and columns, **When** extraction completes, **Then** an inferred entity-relationship structure is produced showing tables, columns, and detected relationships.

---

### User Story 4 - Extract UI Flows and Layouts (Priority: P2)

A UX designer needs to understand the existing user interfaces before redesigning them. They invoke extraction for UI components, and the system identifies screens, forms, navigation patterns, and user interaction flows. UI layouts are represented in a visual format (ASCII art or structured mockup notation) that conveys the spatial arrangement of elements.

**Why this priority**: UI understanding is essential for maintaining user familiarity during modernization and ensuring no critical functionality is lost. Visual representation helps non-technical stakeholders participate in review.

**Independent Test**: Can be fully tested by extracting UI definitions from a screen template and verifying the output includes a visual layout representation and interaction mappings.

**Acceptance Scenarios**:

1. **Given** UI template files (HTML, JSP, ASPX, etc.), **When** extraction runs, **Then** each screen is captured with component inventory (buttons, forms, inputs, labels) and source file references.
2. **Given** button click handlers in UI code, **When** extraction completes, **Then** each button is mapped to its action handler with the complete execution flow documented (which methods are called, what data is accessed).
3. **Given** extracted UI components, **When** the user requests layout visualization, **Then** an ASCII art or structured mockup representation is generated showing spatial arrangement of UI elements.

---

### User Story 5 - Extract Workflows and Process Flows (Priority: P2)

A process analyst needs to understand end-to-end business workflows. They invoke extraction for workflows, and the system traces execution paths from entry points through all called methods, capturing decision points, branches, loops, and state changes. The output shows the complete flow when "a user pushes this button."

**Why this priority**: Workflow understanding enables accurate recreation of business processes and helps identify optimization opportunities during modernization.

**Independent Test**: Can be fully tested by tracing a known workflow from UI trigger through data persistence and verifying all steps are captured in sequence.

**Acceptance Scenarios**:

1. **Given** a user action trigger (button click, form submit), **When** workflow extraction runs for that entry point, **Then** the output shows every method called in sequence, with parameters, return values, and data access operations.
2. **Given** conditional branching in a workflow, **When** extraction completes, **Then** all branches are documented with their trigger conditions and resulting paths.
3. **Given** workflow involving database operations, **When** extraction completes, **Then** the workflow diagram shows data read/write operations at each step with table references.

---

### User Story 6 - Generate Documentation from Extracted Metadata (Priority: P2)

A technical writer needs to produce documentation for stakeholders. After extraction is complete, they invoke the generate command specifying the desired output format (markdown, UML, SysML). The system produces documentation synthesized from the extracted XML metadata, with full source traceability.

**Why this priority**: Documentation enables stakeholder communication, knowledge transfer, and serves as the basis for creating user stories and modernization requirements.

**Independent Test**: Can be fully tested by generating a markdown document from existing XML extractions and verifying it accurately reflects the extracted content with source references.

**Acceptance Scenarios**:

1. **Given** completed XML extractions (business rules, database, UI, workflows), **When** the user runs generate with format "markdown", **Then** a comprehensive markdown document is produced covering all extracted elements.
2. **Given** extracted data model, **When** the user runs generate with format "UML", **Then** a UML class diagram notation is produced representing entities and relationships.
3. **Given** multiple extraction types, **When** the user requests specific documentation (e.g., only data dictionary), **Then** only the requested subset is generated.

---

### User Story 7 - Interactive Clarification for Ambiguities (Priority: P3)

During extraction, the system encounters code that is unclear or could be interpreted multiple ways. The clarify command allows the user to interactively resolve ambiguities, with the system presenting options and recording the user's decisions for consistent application across the codebase.

**Why this priority**: Ambiguity resolution ensures extraction accuracy and documents institutional knowledge that may not be explicit in code.

**Independent Test**: Can be fully tested by processing code with intentional ambiguity and verifying the system prompts for clarification and applies the decision consistently.

**Acceptance Scenarios**:

1. **Given** code with ambiguous business logic (e.g., undocumented magic numbers), **When** clarify is invoked, **Then** the system presents the ambiguous element with context and asks for user interpretation.
2. **Given** a clarification decision made for one instance, **When** similar patterns appear elsewhere in the codebase, **Then** the system applies the same interpretation consistently.
3. **Given** multiple pending clarifications, **When** the user requests clarification status, **Then** all unresolved items are listed with their context and impact.

---

### User Story 8 - Re-analyze and Regenerate Specific Files (Priority: P3)

After initial analysis, the codebase is updated or the user wants to refine analysis of specific files. They invoke re-analysis targeting specific files or directories, and only those items are re-processed while preserving existing analysis for unchanged files.

**Why this priority**: Incremental re-analysis supports iterative refinement and ongoing codebase changes without requiring full re-analysis.

**Independent Test**: Can be fully tested by modifying a single file, running re-analysis on only that file, and verifying only its XML entry is updated.

**Acceptance Scenarios**:

1. **Given** a previously analyzed file that has been modified, **When** the user runs reanalyze targeting that file, **Then** only that file's extraction is updated in the XML output.
2. **Given** completed documentation, **When** the user regenerates documentation after re-analysis, **Then** only affected sections are updated while preserving the rest.
3. **Given** a list of files to re-analyze, **When** the batch reanalyze command runs, **Then** all specified files are processed and their extractions updated.

---

### User Story 9 - Track Progress and Resume Analysis (Priority: P1)

During analysis of a large codebase, the user needs visibility into progress and the ability to pause and resume. The status command shows analysis progress, coverage statistics, and any pending items. If the session is interrupted, the next invocation automatically resumes from the last checkpoint.

**Why this priority**: Large codebases may require hours or days of analysis. Progress tracking and resume capability are essential for practical use.

**Independent Test**: Can be fully tested by starting analysis, interrupting it mid-way, and verifying resume continues from the correct point with accurate progress reporting.

**Acceptance Scenarios**:

1. **Given** analysis in progress on a large codebase, **When** the user runs status, **Then** the system shows percentage complete, files processed, files remaining, and estimated time.
2. **Given** an interrupted analysis session, **When** the user starts a new session and runs analyze, **Then** the system detects the checkpoint and offers to resume.
3. **Given** completed analysis, **When** the user runs status, **Then** coverage statistics show what percentage of the codebase has been fully analyzed vs. partially analyzed.

---

### User Story 10 - Generate User Stories for Modernization (Priority: P2)

A product owner needs to create a backlog for the modernization project. They invoke the generate command with "user-stories" format, and the system produces structured user stories derived from the extracted business rules, workflows, and UI flows. Each generated story includes acceptance criteria and traces back to the source extractions.

**Why this priority**: User story generation directly enables the modernization goal and transforms analysis output into actionable development work items.

**Independent Test**: Can be fully tested by generating user stories from completed extractions and verifying each story maps to specific extracted elements with acceptance criteria.

**Acceptance Scenarios**:

1. **Given** completed business rule extractions, **When** the user runs generate with format "user-stories", **Then** each significant business rule produces a corresponding user story with acceptance criteria derived from the rule logic.
2. **Given** extracted workflows, **When** user story generation runs, **Then** end-to-end user journeys are captured as epic-level stories with sub-stories for individual steps.
3. **Given** generated user stories, **When** the user views a story, **Then** it includes traceability links to the source extractions (business rules, UI components, workflows) that informed it.
4. **Given** generated user stories, **When** the user requests export, **Then** stories are available in both markdown (human-readable) and JSON/CSV (machine-parseable) formats for tool integration.

---

### Edge Cases

- What happens when the codebase contains generated code that should be excluded from analysis?
  - The configuration allows specifying exclusion patterns (e.g., `**/generated/**`, `**/node_modules/**`)
- How does the system handle binary files or non-text assets?
  - Binary files are inventoried (name, size, type) but not analyzed for content; they are marked as "non-analyzable"
- What happens when source files are encrypted or obfuscated?
  - The system reports these files as "analysis-limited" with a note explaining the limitation
- How are very large individual files (100K+ lines) handled?
  - Files are processed in chunks with progress tracking; extraction references include chunk identifiers for traceability
- What happens when the XML output becomes very large?
  - Outputs are structured with indices and can be split into multiple files by category while maintaining cross-references

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST scan and inventory all source files in a target codebase, identifying language, file type, and basic structure
- **FR-002**: System MUST extract business rules from source code with exact source file paths and line number references
- **FR-003**: System MUST capture all SQL statements and database interactions with their execution context and calling code locations
- **FR-004**: System MUST reverse-engineer data models from code, ORM files, or DDL when present
- **FR-005**: System MUST extract UI component definitions and represent layouts in a visual format (ASCII art or structured notation)
- **FR-006**: System MUST trace complete execution flows from user action triggers through all called methods
- **FR-007**: System MUST store all extraction results in structured XML files with defined schemas
- **FR-008**: System MUST support generating markdown documentation from XML metadata
- **FR-009**: System MUST support generating UML/SysML diagrams from extracted data models and workflows (output as PlantUML or Mermaid notation for portability)
- **FR-010**: System MUST track analysis progress and support resumable sessions for large codebases
- **FR-011**: System MUST allow re-analysis of specific files or directories without full re-processing
- **FR-012**: System MUST allow regeneration of specific documentation artifacts without full regeneration
- **FR-013**: System MUST provide interactive clarification workflow for ambiguous code elements
- **FR-014**: System MUST preserve all extracted SQL statements for later reuse in modernization
- **FR-015**: System MUST support exclusion patterns for files/directories that should not be analyzed
- **FR-016**: System MUST operate entirely through AI agent native tools (Read, Write, Glob, Grep) with no external parsers or compiled code
- **FR-017**: System MUST be implemented as slash command prompt templates following the SpecKit pattern
- **FR-018**: System MUST include a constitution document defining framework principles and governance
- **FR-019**: System MUST store checkpoint and session state as XML in `.reforge/memory/` directory
- **FR-020**: System MUST store analysis outputs in `reforge_output/<project-name>/` directory, following the SpecKit pattern
- **FR-021**: System MUST assign a confidence level (high/medium/low) to each extracted item to indicate LLM certainty and prioritize human review
- **FR-022**: System MUST support generating user stories for modernization from extracted metadata, with acceptance criteria and source traceability
- **FR-023**: System MUST maintain analysis logs recording files processed, extraction decisions, and reasoning snippets for transparency and debugging
- **FR-024**: System MUST support exporting generated user stories in both markdown (human-readable) and structured formats (JSON/CSV) for tool integration

### Key Entities

- **AnalysisProject**: Represents a target codebase under analysis; contains configuration, progress state, and output references
- **SourceFile**: Individual source file with language, path, analysis status, and extracted content references
- **BusinessRule**: Extracted business logic with description, source references (file + line numbers), category, related entities, and confidence level (high/medium/low)
- **DatabaseInteraction**: Captured SQL statement with operation type, tables involved, calling code location, execution context, and confidence level
- **DataEntity**: Inferred or extracted data model element (table/entity) with columns, relationships, source references, and confidence level
- **UIComponent**: Extracted UI element with type, properties, layout position, associated event handlers, and confidence level
- **Workflow**: Traced execution path with steps, decision points, data access operations, source references, and confidence level
- **GeneratedUserStory**: Modernization backlog item with title, description, acceptance criteria, priority suggestion, and traceability links to source extractions
- **ClarificationItem**: Ambiguous code element pending user interpretation with context, options, and resolution status
- **AnalysisCheckpoint**: Progress state enabling resume capability with files processed, pending, and extraction status
- **AnalysisLog**: Transparency record with timestamp, file analyzed, extraction decisions made, reasoning snippets, and confidence assessments

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can inventory a 1000-file legacy codebase in under 2 hours with 100% file coverage (measured on standard development machine with AI agent having sufficient context window; excludes network latency for remote codebases)
- **SC-002**: 95% of business rules extracted include accurate source file and line number references that point to the actual code
- **SC-003**: All SQL statements in analyzed files are captured with their execution context within a single analysis pass
- **SC-004**: Generated documentation accurately reflects extracted metadata with zero content drift from source XML
- **SC-005**: Users can resume interrupted analysis within 30 seconds of session start with correct progress state
- **SC-006**: Re-analysis of individual files completes in under 1 minute per file without affecting other extracted content
- **SC-007**: Users report 80% or higher satisfaction with UI layout visualizations matching their mental model of the screens (measured via post-extraction survey asking "Does this ASCII layout accurately represent the screen?" with 5-point scale; 4+ = satisfied)
- **SC-008**: Complete workflow traces show all method calls from trigger to data persistence without missing steps
- **SC-009**: Framework operates without any external dependencies - only AI agent native capabilities required
- **SC-010**: Users can produce stakeholder-ready documentation within 15 minutes of completed extraction

## Assumptions

- The target codebase is accessible via file system (not remote repositories requiring authentication)
- Source files are in text format and not encrypted or binary (binary files are inventoried but not analyzed)
- The AI agent has sufficient context window to analyze individual files (very large files may require chunking)
- Users have basic familiarity with command-line/chat interface for invoking slash commands
- The framework will be used with AI coding assistants that support file read/write operations
- Common programming languages and frameworks will be recognizable without specialized parsers due to LLM training data
- XML is an appropriate intermediate format for structured data exchange between analysis and generation phases
- Users accept that LLM-based analysis may require clarification for ambiguous or unusual code patterns
