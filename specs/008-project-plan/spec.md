# Feature Specification: Project Plan Command

**Feature Branch**: `008-project-plan`
**Created**: 2026-02-19
**Status**: Draft
**Input**: User description: "We need a command to plan how and what we will extract, audit, and generate for the project, this should create a markdown file with steps, list, checkboxes, that the following commands use to work through the process. The user should also be able to add to the plan by running the command again with some specifics."

## Context

Currently, users working through the Reforge workflow must decide ad-hoc what to extract, which audit types to run, and what documentation to generate. There is no central plan file that defines the project's extraction strategy upfront. This means:

- Users often discover they missed extraction types only after auditing
- There is no single place to track overall project progress across extractions, audits, and generation
- Re-running the workflow on the same project requires remembering what was already done
- New team members have no way to see what the project plan looks like or what remains

Real-world projects (e.g., TCOS-RUMO) end up with 46+ extraction files across 7 categories, 18+ generated documents, and 7 audit reports — all built iteratively without a declared upfront plan. A project plan command would let users declare intent before starting, track progress with checkboxes, and incrementally add new items as understanding deepens.

## Clarifications

### Session 2026-02-19

- Q: Which commands should read from and/or update the project plan? → A: All commands — every Reforge command checks for and updates the plan where relevant
- Q: Should the plan organize items as a flat list or as a workflow with sub-steps? → A: Workflow-oriented — grouped by extraction type, each with sub-steps (extract, audit, generate) plus a Setup section for init/analyze/profile
- Q: How should commands integrate with the plan — shared step pattern or centralized writes? → A: Standardized step in each command — add a "Step 0.7: Check/Update Project Plan" pattern to all command templates that reads on start and writes on completion

### Session 2026-02-20

- Q: Should each workflow group use the full 7-step pipeline or a simplified 3-step pipeline? → A: Full 7-step pipeline per group: extract → clarify → audit extractions → fix extractions → generate → audit generated → fix generated
- Q: How should commands identify their corresponding checkbox in the plan file? → A: HTML comment tag per item (e.g., `<!-- reforge:extract:business-rules -->`) — commands match by tag pattern, not display text
- Q: How should completed items be recorded in the plan file? → A: Inline timestamp after the tag: `- [x] Extract business rules <!-- reforge:extract:business-rules --> *(completed: 2026-02-20)*`
- Q: If Step 0.7 fails to update the plan, should the command fail or continue? → A: Warn and continue — command completes successfully, emits a warning that the plan was not updated

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Create Initial Project Plan (Priority: P1)

A user starting a new Reforge project wants to create a plan that defines what extractions, audits, and generated documents they intend to produce. The user runs `/reforge.plan` and interactively declares their intended extraction types, audit scope, and generation targets. The command creates a checklist-based markdown file at `.reforge/memory/project-plan.md` that subsequent commands can reference.

**Why this priority**: Without the plan file, none of the other stories function. This is the core creation capability.

**Independent Test**: Run `/reforge.plan` on a project with an analysis complete, verify that `.reforge/memory/project-plan.md` exists with extraction, audit, and generation sections containing checkboxes.

**Acceptance Scenarios**:

1. **Given** a project with `.reforge/memory/` directory present, **When** the user runs `/reforge.plan`, **Then** the command interactively gathers the user's intended extraction types, audit scope, and generation targets, and creates `.reforge/memory/project-plan.md` with checklist items for each
2. **Given** a project with a completed analysis (`analysis.xml` exists), **When** the user runs `/reforge.plan`, **Then** the command uses the analysis results to suggest relevant extraction types based on discovered languages, module structure, and file types (e.g., suggesting `database` extraction if `.sql` files or ORM patterns are found)
3. **Given** a project with a completed extraction profile (`.reforge/memory/extraction-profile.md` exists), **When** the user runs `/reforge.plan`, **Then** the command incorporates the declared languages and architecture patterns to suggest targeted extraction sub-tasks (e.g., "Extract WCF service contract rules" for a project declaring WCF)
4. **Given** the user declares they want business-rules extraction, **When** the plan is generated, **Then** the plan includes a checklist section for business-rules with the full 7-step pipeline: extract, clarify, audit extractions, fix extractions, generate documentation, audit generated output, and fix generated output
5. **Given** a project with no analysis and no profile, **When** the user runs `/reforge.plan`, **Then** the command still creates a plan using only what the user declares manually, noting that analysis-based suggestions will be available after running `/reforge.analyze`

---

### User Story 2 - Add Items to Existing Plan (Priority: P1)

A user who has been working through their project plan discovers additional extraction needs (e.g., they realize they need architecture extraction after reviewing business rules) and wants to add them to the existing plan without losing progress on already-completed items.

**Why this priority**: Equally critical to US1 — plans must be iteratively refinable since users discover new needs as they work through the codebase. Without this, the plan becomes stale immediately.

**Independent Test**: Create a plan with business-rules only, then run `/reforge.plan "add architecture extraction and security audit"` and verify the new items appear while existing checkboxes (including any already marked complete) are preserved.

**Acceptance Scenarios**:

1. **Given** an existing project plan with some items already checked off, **When** the user runs `/reforge.plan "add database extraction"`, **Then** the new extraction items are appended to the appropriate sections while all existing items and their completion status are preserved
2. **Given** an existing project plan, **When** the user runs `/reforge.plan "add user-stories generation and cross-mappings"`, **Then** the generation section gains new checklist items for user-stories and cross-mappings
3. **Given** an existing project plan, **When** the user runs `/reforge.plan` with no arguments, **Then** the command displays the current plan status (completed/total per section) and asks whether to add new items or review the plan

---

### User Story 3 - All Commands Reference and Update the Plan (Priority: P2)

Every Reforge command checks for the project plan when it runs. Commands that produce outputs or complete workflow steps update the corresponding checkboxes upon successful completion. This covers all 10 commands: `init`, `analyze`, `profile`, `extract`, `clarify`, `generate`, `status`, `reanalyze`, `audit`, and `fix`.

**Why this priority**: This is the integration that makes the plan actionable rather than just a static document. Without it, users must manually track progress. The plan becomes the single source of truth for project progress across the entire Reforge workflow.

**Independent Test**: Create a plan with items spanning multiple command types, run those commands, verify all corresponding checkboxes are updated.

**Acceptance Scenarios**:

1. **Given** a project plan exists with an unchecked item for business-rules extraction, **When** the user successfully runs `/reforge.extract business-rules`, **Then** the corresponding checkbox in the plan is marked as complete with a completion timestamp
2. **Given** a project plan exists with an "Analyze codebase" item, **When** the user runs `/reforge.analyze`, **Then** the analysis checkbox is marked complete
3. **Given** a project plan exists with an "Initialize project context" item, **When** the user runs `/reforge.init`, **Then** the init checkbox is marked complete
4. **Given** a project plan exists with a "Generate extraction profile" item, **When** the user runs `/reforge.profile`, **Then** the profile checkbox is marked complete
5. **Given** a project plan exists with generation targets, **When** the user runs `/reforge.generate user-stories`, **Then** the corresponding generation checkbox is marked complete
6. **Given** a project plan exists, **When** the user runs `/reforge.audit`, **Then** the audit command reads the plan to understand which extraction types were planned and reports coverage against the plan, then marks the audit item complete
7. **Given** a project plan exists with correction items, **When** the user runs `/reforge.fix`, **Then** the fix checkbox is marked complete
8. **Given** a project plan exists, **When** the user runs `/reforge.status`, **Then** the status command includes plan progress alongside extraction coverage in its report
9. **Given** no project plan exists, **When** the user runs any command, **Then** the command proceeds normally without error — the plan is optional, not required

---

### User Story 4 - Plan Status Summary (Priority: P2)

A user wants a quick summary of their project plan progress showing what has been completed, what remains, and what percentage of the plan is done.

**Why this priority**: Provides visibility into overall project progress. Useful but not essential for the core plan creation and update flow.

**Independent Test**: Create a plan with multiple items, check off some, run `/reforge.plan --status` and verify it shows correct completion counts and percentages.

**Acceptance Scenarios**:

1. **Given** a project plan with 10 total items (6 checked, 4 unchecked), **When** the user runs `/reforge.plan --status`, **Then** the command displays a summary showing 60% complete with per-section breakdowns
2. **Given** a project plan where all items are complete, **When** the user runs `/reforge.plan --status`, **Then** the command congratulates the user and suggests next steps (e.g., final review, handoff)

---

### Edge Cases

- What happens when the user tries to add a duplicate item that already exists in the plan? The command should detect the duplicate and inform the user, offering to skip or replace it.
- What happens when the plan file is manually edited with invalid markdown? The command should be resilient to minor formatting differences and preserve any manual additions the user made.
- What happens when the user adds items for extraction types not supported by the extract command (e.g., "extract performance-metrics")? The command should accept any user-declared extraction type and create a full workflow group with the 7-step pipeline, same as standard types. The extract/audit/fix/generate commands will attempt to process them; if a command cannot handle a custom type, it skips the plan update for that item. Truly non-extraction tasks (e.g., "review architecture with stakeholders") go in the Custom Tasks section as single checklist items.
- What happens when the analysis changes after the plan was created (e.g., user runs `/reforge.reanalyze` adding new files)? The plan remains as-is; user can run `/reforge.plan` again to get updated suggestions for new items.
- What happens when Step 0.7 fails to update the plan (e.g., matching tag not found, file write error, malformed markdown)? The command emits a warning that the plan was not updated but completes successfully — the plan is a side-effect, not a gate.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST provide a `/reforge.plan` command defined as a markdown prompt template in `.reforge/commands/plan.md`
- **FR-002**: The command MUST create a checklist-based markdown plan file at `.reforge/memory/project-plan.md` containing a Setup section, workflow group sections for each extraction type (each following the full 7-step pipeline), and an optional Custom Tasks section
- **FR-003**: The command MUST accept optional text arguments to specify items to add (e.g., `/reforge.plan "add database extraction and UML diagrams"`)
- **FR-004**: The command MUST preserve existing plan content and completion status when adding new items
- **FR-005**: The command MUST use analysis results (when available) to suggest relevant extraction types, audit scopes, and generation targets based on discovered codebase characteristics
- **FR-006**: The command MUST use the extraction profile (when available) to suggest language-specific and architecture-specific extraction sub-tasks
- **FR-007**: Each plan item MUST be a markdown checkbox (`- [ ]` / `- [x]`) with a human-readable description followed by an inline HTML comment tag for machine matching (e.g., `- [ ] Extract business rules <!-- reforge:extract:business-rules -->`). Commands MUST match items by the tag pattern `<!-- reforge:<command>:<type> -->`, not by display text
- **FR-008**: The plan file MUST use a workflow-oriented structure: a Setup section (init, analyze, profile) followed by groups for each extraction type (e.g., "Business Rules", "Database", "UI"), where each group contains the full 7-step pipeline: extract → clarify → audit extractions → fix extractions → generate → audit generated → fix generated; an optional Custom Tasks section at the end for user-defined items
- **FR-009**: The command MUST support a `--status` flag that displays a progress summary without modifying the plan
- **FR-010**: All Reforge commands (`init`, `analyze`, `profile`, `extract`, `clarify`, `generate`, `status`, `reanalyze`, `audit`, `fix`) MUST check for the project plan during execution and mark corresponding items complete when they finish successfully
- **FR-011**: All Reforge commands MUST continue to function normally when no project plan exists — the plan is optional
- **FR-014**: Each command template MUST include a standardized "Step 0.7: Check/Update Project Plan" that reads the plan on start (to display current status context) and updates the corresponding checkbox on successful completion, following the same pattern as Step 0.5 (Load Project Context) and Step 0.6 (Load Extraction Profile). If the plan update fails (tag not found, write error, malformed file), the command MUST emit a warning but MUST NOT fail — the plan update is a non-blocking side-effect
- **FR-012**: The command MUST use agent-agnostic language per Constitution Principle V
- **FR-013**: The plan file MUST include metadata (creation date, last updated, project name) in the header

### Key Entities

- **Project Plan**: The markdown file (`.reforge/memory/project-plan.md`) containing all planned workflow tasks as checkboxes. Structure: metadata header, Setup section (init/analyze/profile checkboxes), then one section per extraction type (e.g., "Business Rules") each containing the full 7-step pipeline (extract → clarify → audit extractions → fix extractions → generate → audit generated → fix generated), and an optional Custom Tasks section at the end.
- **Plan Item**: A single checkbox entry representing one actionable task. Each item has a completion status, an inline HTML comment tag for machine matching, and an optional completion timestamp. Uncompleted format: `- [ ] <description> <!-- reforge:<command>:<type> -->`. Completed format: `- [x] <description> <!-- reforge:<command>:<type> --> *(completed: YYYY-MM-DD)*`. Commands identify their corresponding item by searching for the tag pattern `<!-- reforge:<command>:<type> -->` (e.g., `<!-- reforge:extract:business-rules -->`, `<!-- reforge:audit:business-rules -->`, `<!-- reforge:generate:business-rules -->`). Users may freely edit the display text without breaking command matching.
- **Workflow Group**: A named section in the plan representing one extraction area (e.g., "Business Rules", "Database", "UI"). Each group contains 7 ordered sub-steps that follow the full Reforge pipeline: extract → clarify → audit extractions → fix extractions → generate → audit generated → fix generated.

## Assumptions

- The `/reforge.plan` command follows the same interactive Q&A pattern as `/reforge.init` and `/reforge.profile` for gathering user input when run without arguments
- When run with text arguments (e.g., `/reforge.plan "add architecture extraction"`), the command operates in non-interactive mode, parsing the intent and adding items directly
- The plan file is a human-readable and human-editable markdown document — users may manually edit it, add custom items, or check off boxes directly
- Plan suggestions from analysis and profile data are recommendations, not requirements — the user confirms or modifies all suggestions
- All Reforge commands update the plan via markdown checkbox toggling (changing `- [ ]` to `- [x]`) and appending an inline completion timestamp (e.g., `*(completed: 2026-02-20)*`) — no complex state machine. Each command includes a standardized "Step 0.7" that reads the plan during initialization and updates the relevant checkbox upon successful completion, mirroring the Step 0.5/0.6 patterns already established across command templates.
- Running `/reforge.plan` before `/reforge.init` or `/reforge.analyze` is allowed but produces a plan based solely on user declarations with a note suggesting those commands for richer suggestions

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can create a complete project plan covering extraction, audit, and generation goals in under 5 minutes of interactive input
- **SC-002**: Users can add new items to an existing plan without losing any previously completed or unchecked items
- **SC-003**: The plan file accurately reflects project progress — completed commands result in checked items within the same session
- **SC-004**: All existing Reforge commands continue to function identically when no project plan exists
- **SC-005**: The plan status summary accurately reports completion counts and percentages matching the actual checkbox states in the file
- **SC-006**: 100% of plan file content uses agent-agnostic language
