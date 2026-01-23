# Feature Specification: Audit and Fix Commands

**Feature Branch**: `002-audit-fix-commands`
**Created**: 2026-01-23
**Status**: Draft
**Input**: User description: "We now need to add a new command to audit our results to make sure we are covering 100% of data out of the code base, the command should audit everything that has been created from the code or something specific like user stories. It should inform on what is incorrect and create a plan, we then need a command to execute the corrections. This should follow how our other reforge commands work"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Full Coverage Audit (Priority: P1)

As a user who has completed analysis and extractions, I want to audit all generated outputs against the original codebase to identify gaps in coverage so that I can be confident nothing was missed during the analysis and extraction phases.

**Why this priority**: The core value proposition is identifying coverage gaps. Without this, users cannot trust their extraction outputs are complete.

**Independent Test**: Can be tested by running the audit command after a completed analysis+extraction cycle and verifying it produces a coverage report with identified gaps.

**Acceptance Scenarios**:

1. **Given** a completed analysis and at least one extraction, **When** the user runs `/reforge.audit`, **Then** the system compares all analyzed files against extraction outputs and produces a coverage report showing files with no corresponding extractions.
2. **Given** a completed analysis with all extraction types, **When** the user runs `/reforge.audit`, **Then** the system reports overall coverage percentage and lists specific uncovered files with no extraction references.
3. **Given** no completed analysis exists, **When** the user runs `/reforge.audit`, **Then** the system reports an error with guidance to run `/reforge.analyze` first.

---

### User Story 2 - Targeted Artifact Audit (Priority: P2)

As a user who has generated specific artifacts (e.g., user stories, documentation), I want to audit a specific output type to verify its completeness and accuracy against the source extractions and codebase.

**Why this priority**: Users often work incrementally and need to validate specific outputs without re-auditing everything.

**Independent Test**: Can be tested by running the audit with a specific type argument and verifying it only validates that artifact type against its source data.

**Acceptance Scenarios**:

1. **Given** generated user stories exist, **When** the user runs `/reforge.audit user-stories`, **Then** the system validates each user story traces back to extraction items and identifies any extraction items not represented in user stories.
2. **Given** business rules have been extracted, **When** the user runs `/reforge.audit business-rules`, **Then** the system verifies each extracted rule has source references that still exist and identifies analyzed files with no business rule extractions referencing them.
3. **Given** a type argument for an artifact that doesn't exist, **When** the user runs `/reforge.audit diagrams`, **Then** the system reports that no diagrams have been generated and suggests the appropriate generate command.

---

### User Story 3 - Audit Report with Correction Plan (Priority: P2)

As a user who has run an audit and found gaps, I want the audit to produce a structured correction plan so that I know exactly what needs to be fixed and in what order.

**Why this priority**: Identifying gaps without actionable next steps leaves users without a clear path forward.

**Independent Test**: Can be tested by running an audit on a known-incomplete extraction and verifying the output includes a prioritized list of corrections with affected files and suggested actions.

**Acceptance Scenarios**:

1. **Given** an audit has identified coverage gaps, **When** the audit completes, **Then** it produces a correction plan file listing each gap with priority, affected files, and recommended action (re-extract, re-analyze, or generate).
2. **Given** an audit identifies accuracy issues (e.g., stale references), **When** the audit completes, **Then** the correction plan distinguishes between missing coverage and inaccurate/stale entries.
3. **Given** an audit finds no issues, **When** the audit completes, **Then** it reports 100% coverage with no correction plan needed.

---

### User Story 4 - Execute Corrections (Priority: P1)

As a user who has a correction plan from an audit, I want to execute the corrections automatically so that gaps and inaccuracies are resolved without manually running multiple commands.

**Why this priority**: This closes the feedback loop — without execution, the audit is informational only and requires significant manual effort to act on.

**Independent Test**: Can be tested by generating a correction plan and running the fix command, then verifying the specified corrections were applied and a re-audit shows improved coverage.

**Acceptance Scenarios**:

1. **Given** a correction plan exists from a previous audit, **When** the user runs `/reforge.fix`, **Then** the system executes each correction action (re-analyze, re-extract, regenerate) in dependency order.
2. **Given** a correction plan with multiple item types, **When** the user runs `/reforge.fix --type business-rules`, **Then** only corrections related to business rules are executed.
3. **Given** no correction plan exists, **When** the user runs `/reforge.fix`, **Then** the system reports that an audit must be run first and suggests `/reforge.audit`.
4. **Given** a correction plan is being executed, **When** the user interrupts or a correction fails, **Then** the system saves progress and supports `--resume` to continue from the last successful correction.

---

### User Story 5 - Selective Correction Execution (Priority: P3)

As a user reviewing a correction plan, I want to execute only specific corrections or approve corrections interactively so that I maintain control over what changes are made.

**Why this priority**: Power users want fine-grained control, but this is not essential for the core audit-fix workflow.

**Independent Test**: Can be tested by running the fix command with `--interactive` and verifying it prompts for confirmation before each correction action.

**Acceptance Scenarios**:

1. **Given** a correction plan with 10 items, **When** the user runs `/reforge.fix --interactive`, **Then** the system presents each correction for approval before executing it.
2. **Given** a correction plan, **When** the user runs `/reforge.fix --items COR-001,COR-003`, **Then** only the specified corrections are executed.

---

### Edge Cases

- What happens when source files have been modified since the last analysis? The audit flags stale analysis entries and recommends re-analysis before corrections.
- How does the system handle circular dependencies in corrections? Executes in dependency order; if circular, reports and requires manual resolution.
- What happens when a correction action fails mid-execution? Saves checkpoint and allows `--resume`.
- What happens when the codebase contains files that are intentionally excluded from analysis? Respects exclusion patterns from config.json; excluded files do not count as coverage gaps.
- What if generated artifacts reference extraction items that no longer exist? Flags as accuracy issues in the audit with "stale reference" classification.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST cross-reference file paths in the analysis inventory against source references in all extraction outputs to calculate coverage percentage (metadata comparison, not source re-scan).
- **FR-002**: System MUST identify analyzed files that have no corresponding extraction entries referencing them.
- **FR-003**: System MUST validate that extraction source references (file paths and line numbers) still point to valid code.
- **FR-004**: System MUST support auditing all output types or a specific type (analysis, business-rules, database, ui-flows, workflows, user-stories, documentation, diagrams).
- **FR-005**: System MUST produce a structured correction plan (XML format) listing each identified gap or inaccuracy with priority, type, affected files, and recommended action.
- **FR-006**: System MUST execute corrections from the plan by invoking the appropriate reforge commands (reanalyze, extract, generate) in dependency order.
- **FR-007**: System MUST support resumable correction execution via checkpoints.
- **FR-008**: System MUST perform a targeted spot-check after each correction, verifying the specific files that were corrected now have extraction coverage. A full re-audit is not performed automatically.
- **FR-009**: System MUST respect project exclusion patterns and not flag excluded files as coverage gaps.
- **FR-010**: System MUST report audit results in both human-readable and JSON formats.
- **FR-011**: System MUST support interactive correction approval mode.
- **FR-012**: System MUST support selective correction by item ID or type filter.

### Key Entities

- **Audit Report**: The comprehensive coverage and accuracy assessment, containing file coverage percentages, gap listings, and accuracy checks per extraction type.
- **Correction Plan**: An ordered list of correction items, each with an ID, priority, type (gap vs. stale), affected files, recommended action, and execution status.
- **Correction Item**: A single actionable fix — describes what is missing or inaccurate, which files are affected, and what reforge command would resolve it.
- **Coverage Map**: A per-file breakdown showing which extraction types reference each file and which files have no extraction coverage.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can verify extraction coverage completeness in a single command execution, with results available within the same session.
- **SC-002**: Audit reports accurately identify at least 90% of actual coverage gaps when compared against manual review.
- **SC-003**: Correction plan execution resolves identified gaps, improving coverage percentage measurably between pre-fix and post-fix audit runs.
- **SC-004**: The audit-fix cycle (audit, review plan, execute fixes) can be completed without users needing to manually determine which reforge commands to run.
- **SC-005**: Interrupted correction executions can be resumed without re-processing already-completed corrections.
- **SC-006**: Audit results for a 1000+ file codebase complete without requiring multiple sessions or manual intervention.

## Clarifications

### Session 2026-01-23

- Q: What granularity should the audit use for coverage measurement? → A: File-level only (each analyzed file should have at least one extraction referencing it)
- Q: How should the audit detect coverage gaps? → A: Metadata comparison only (cross-reference file lists between analysis and extraction outputs)
- Q: How should the fix command verify corrections? → A: Targeted spot-check of only the items that were corrected (verify each file now has extraction coverage)

## Assumptions

- The audit command builds upon existing extraction schemas and output formats — no new output formats are introduced beyond the audit report and correction plan.
- Coverage is measured at the file level only: each analyzed file should have at least one extraction entry referencing it. Sub-file granularity (function/method level) is explicitly out of scope.
- The audit uses metadata comparison only (cross-referencing file paths between analysis.xml and extraction outputs). It does not re-read or re-scan source files to detect unextracted patterns — that is the responsibility of `/reforge.extract`.
- The fix command orchestrates existing reforge commands rather than implementing new extraction logic.
- Correction priorities follow the pattern: analysis gaps > extraction gaps > generation gaps (since downstream artifacts depend on upstream ones).
- The audit report and correction plan are stored in the existing output directory structure under a new `audit/` subdirectory.
