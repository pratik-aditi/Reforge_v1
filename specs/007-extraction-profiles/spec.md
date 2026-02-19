# Feature Specification: Extraction Profiles Command

**Feature Branch**: `007-extraction-profiles`
**Created**: 2026-02-19
**Status**: Draft
**Input**: User description: "Create a new command that allows users to define languages and architecture, generating language-specific extraction instruction profiles stored in memory for the extract command to use"

## Context

The `/reforge.extract` command currently contains hardcoded language-specific extraction rules (VB.NET, C#, General) embedded directly in the command template. This approach has limitations:

- Adding support for new languages requires modifying the core extract command
- Every project loads all language rules, even for languages it doesn't use
- Users cannot customize or extend language-specific guidance for their codebase
- Architecture-specific extraction patterns (layered, microservices, event-driven) are not addressed at all

This feature introduces a `/reforge.profile` command that lets users declare their project's technology stack and generates a tailored extraction profile. The command can also auto-discover languages by scanning the codebase for file extensions when the user doesn't specify them. The extract command then loads this profile from memory, and the hardcoded language-specific content is removed from extract.md entirely.

## Clarifications

### Session 2026-02-19

- Q: When no extraction profile exists, should the extract command still have language-specific rules available? → A: Remove language-specific rules from extract.md entirely (Option B). The profile command should also auto-discover languages from the codebase when the user doesn't specify them.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Generate Extraction Profile from Tech Stack Declaration (Priority: P1)

A user starting a new Reforge project wants to declare the programming languages and frameworks in their legacy codebase so that subsequent extractions are tailored to those technologies.

The user runs `/reforge.profile` and declares their tech stack (e.g., "VB.NET 4.8, C#, SQL Server, WCF services"). The command generates a profile file at `.reforge/memory/extraction-profile.md` containing language-specific extraction rules, common pitfalls, type system quirks, and framework-specific patterns relevant to the declared technologies.

**Why this priority**: Without the profile file, extraction has no language-specific guidance. This is the minimum viable feature — generating the profile that other stories depend on.

**Independent Test**: Run `/reforge.profile` with a tech stack declaration, then verify that `.reforge/memory/extraction-profile.md` exists and contains language-specific sections for each declared technology.

**Acceptance Scenarios**:

1. **Given** a project with no existing extraction profile, **When** the user runs `/reforge.profile` and declares "VB.NET, C#, SQL Server", **Then** the command creates `.reforge/memory/extraction-profile.md` with dedicated sections for VB.NET extraction rules, C# extraction rules, and SQL Server extraction patterns
2. **Given** a project with an existing `project-context.md` containing technology stack info, **When** the user runs `/reforge.profile`, **Then** the command pre-populates language suggestions from the existing project context and asks the user to confirm or modify
3. **Given** the user declares any established programming language (e.g., VB.NET), **When** the profile is generated, **Then** the language section contains at least 5 language-specific extraction rules generated from the LLM's training knowledge covering known pitfalls (type system quirks, operator differences, naming conventions, common pitfalls, framework patterns)
4. **Given** the user declares any established programming language (e.g., COBOL, Fortran, Assembly, FoxPro, RPG, Ada), **When** the profile is generated, **Then** the LLM generates extraction rules from its training knowledge using the same 5-category structure (type system quirks, operator differences, naming conventions, common pitfalls, framework patterns) — no language is treated as "unknown" unless it is a truly proprietary or internal DSL, in which case the command prompts the user for extraction-relevant details
5. **Given** the user runs `/reforge.profile` without specifying any languages, **When** the codebase contains `.vb`, `.cs`, and `.sql` files, **Then** the command auto-discovers these languages, presents them to the user for confirmation, and generates profile sections for VB.NET, C#, and SQL

---

### User Story 2 - Extract Command Loads and Applies Profile (Priority: P1)

A user who has created an extraction profile wants the extract command to automatically use the profile's language-specific guidance during extraction, without requiring any additional flags or configuration.

**Why this priority**: The profile is only useful if the extract command actually reads it. This story completes the integration loop and is equally critical to US1 — together they form the MVP.

**Independent Test**: Generate a profile via US1, then run `/reforge.extract business-rules`. Verify that the extract command references the extraction profile and applies language-specific rules from the profile during extraction.

**Acceptance Scenarios**:

1. **Given** a project with `.reforge/memory/extraction-profile.md` present, **When** the user runs `/reforge.extract`, **Then** the extract command loads the profile during its initialization step and applies language-specific rules during extraction
2. **Given** a project with no extraction profile, **When** the user runs `/reforge.extract`, **Then** the extract command proceeds normally without error using general extraction guidance only (no language-specific rules apply), and suggests running `/reforge.profile` for better results
3. **Given** a profile that includes VB.NET rules about array upper bounds, **When** the extract command encounters a VB.NET array declaration, **Then** the extraction output reflects the profile's guidance (e.g., correctly noting array size vs. upper bound)

---

### User Story 3 - Declare Architecture Patterns for Extraction Guidance (Priority: P2)

A user wants to declare architectural patterns in their codebase (e.g., layered architecture, repository pattern, service bus) so that the extraction profile includes architecture-specific guidance about where business rules, data access, and workflows typically reside.

**Why this priority**: Architecture guidance improves extraction quality by directing the agent to look in the right places, but extraction works without it. Language-specific rules (US1) have higher impact on extraction accuracy.

**Independent Test**: Run `/reforge.profile` declaring both languages and architecture patterns, then verify the profile contains architecture-specific extraction guidance sections.

**Acceptance Scenarios**:

1. **Given** the user runs `/reforge.profile` and declares "layered architecture with repository pattern", **When** the profile is generated, **Then** it includes guidance about where business rules are expected (service layer), where data access patterns reside (repository classes), and how to trace cross-layer calls
2. **Given** the user declares "microservices with message bus", **When** the profile is generated, **Then** it includes guidance about inter-service communication patterns, message contracts, and distributed workflow extraction

---

### User Story 4 - Update Existing Profile (Priority: P2)

A user who previously created an extraction profile discovers new technologies in the codebase during analysis and wants to add them to the existing profile without losing their current configuration.

**Why this priority**: Important for iterative workflows where the user learns more about the codebase over time, but the initial profile generation (US1) covers the primary need.

**Independent Test**: Create a profile with VB.NET only, then run `/reforge.profile --update` adding C# and verify both languages appear in the updated profile.

**Acceptance Scenarios**:

1. **Given** a project with an existing extraction profile containing VB.NET rules, **When** the user runs `/reforge.profile --update` and adds C#, **Then** the updated profile contains both VB.NET and C# sections, with the original VB.NET rules preserved
2. **Given** a project with an existing extraction profile, **When** the user runs `/reforge.profile --update` and removes a language, **Then** that language's section is removed from the profile while other sections remain intact
3. **Given** a project with an existing extraction profile, **When** the user runs `/reforge.profile` without `--update`, **Then** the command asks whether to update or replace the existing profile

---

### User Story 5 - Add Custom Extraction Notes (Priority: P3)

A user wants to add project-specific extraction notes beyond what the built-in language rules provide — for example, documenting internal conventions, proprietary frameworks, or known code patterns that affect extraction accuracy.

**Why this priority**: Custom notes are a nice-to-have that improves extraction for complex projects, but the built-in language rules cover the common cases.

**Independent Test**: Run `/reforge.profile`, add custom extraction notes, then verify the notes appear in the profile and are loaded by the extract command.

**Acceptance Scenarios**:

1. **Given** the user runs `/reforge.profile` and provides custom extraction notes like "All business rules are in classes ending with 'Manager'", **When** the profile is generated, **Then** the custom notes appear in a dedicated section and are available to the extract command
2. **Given** a profile with custom notes, **When** the user runs `/reforge.profile --update`, **Then** existing custom notes are preserved and the user can add additional notes

---

### Edge Cases

- What happens when the user declares contradictory technologies (e.g., both "VB.NET 3.5" and "VB.NET 4.8")? The profile should use the most recent version's rules and note the version range.
- What happens when the extraction profile is corrupted or has invalid markdown structure? The extract command should log a warning and continue without profile guidance rather than failing.
- What happens when the user runs `/reforge.profile` before `/reforge.init`? The command should work independently (profile only needs `.reforge/memory/` directory to exist), but suggest running `/reforge.init` first for better results since project context informs profile generation.
- What happens when the profile references languages not present in any analyzed files? The extract command should still load the profile — the rules simply won't apply if those languages aren't encountered.
- What happens when the user provides no languages at all? The command should auto-discover languages by scanning the codebase for file extensions (e.g., `.vb` → VB.NET, `.cs` → C#, `.py` → Python), present the findings for user confirmation, and generate profile sections for confirmed languages. If auto-discovery also finds nothing, generate a minimal profile with only General extraction rules and architecture guidance (if provided).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST provide a `/reforge.profile` command defined as a markdown prompt template in `.reforge/commands/profile.md`
- **FR-002**: The command MUST accept user declarations of programming languages (with optional version information) used in the target codebase
- **FR-003**: The command MUST accept user declarations of architectural patterns used in the target codebase
- **FR-004**: The command MUST generate an extraction profile file at `.reforge/memory/extraction-profile.md` containing language-specific extraction rules for each declared technology
- **FR-005**: The generated profile MUST include at least 5 extraction rules per language for any language the LLM has training knowledge of (covering type system quirks, operator differences, naming conventions, common pitfalls, and framework-specific patterns) — this includes virtually all established programming languages (COBOL, Fortran, Assembly, FoxPro, RPG, Ada, etc.), not just a predefined list
- **FR-006**: The extract command (`extract.md`) MUST load `.reforge/memory/extraction-profile.md` during initialization when the file is present
- **FR-007**: The extract command MUST continue to function normally when no extraction profile exists
- **FR-008**: The command MUST support an `--update` flag to modify an existing profile without replacing it
- **FR-009**: The command MUST pre-populate language suggestions from `.reforge/memory/project-context.md` when that file exists
- **FR-010**: The generated profile MUST use agent-agnostic language (per Constitution Principle V)
- **FR-011**: The command MUST accept user-provided custom extraction notes and include them in the profile
- **FR-012**: The generated profile MUST include architecture-specific extraction guidance when architectural patterns are declared
- **FR-013**: The extract command's hardcoded "Language-Specific Extraction Rules" section MUST be removed entirely from `extract.md` and replaced with a directive to load the extraction profile from memory; when no profile exists, the extract command operates without language-specific rules and suggests running `/reforge.profile`
- **FR-014**: The command MUST auto-discover programming languages in the target codebase by scanning file extensions (using Glob) when the user does not declare languages explicitly, presenting discovered languages for user confirmation before generating profile sections

### Key Entities

- **Extraction Profile**: The generated file (`.reforge/memory/extraction-profile.md`) containing all language-specific, architecture-specific, and custom extraction guidance. Sections include: language rules, architecture patterns, framework guidance, and custom notes.
- **Language Rule Set**: A collection of extraction rules for a specific programming language, including type system quirks, operator behavior, naming conventions, common pitfalls, and anti-hallucination traps.
- **Architecture Pattern**: Extraction guidance tied to a specific architectural style, describing where business rules, data access, workflows, and integration points typically reside.

## Assumptions

- The `/reforge.profile` command follows the same interactive question-and-answer pattern as `/reforge.init` for gathering user input
- The LLM generates extraction rules for ANY declared programming language from its training knowledge. The 5-category rule structure (type system quirks, operator differences, naming conventions, common pitfalls, framework patterns) applies universally. There is no finite "supported languages" list — LLMs have training knowledge of virtually all established programming languages including legacy and enterprise languages (COBOL, Fortran, Assembly, FoxPro, RPG, MUMPS, Ada, ABAP, Delphi, etc.). Only truly proprietary or internal DSLs require user-provided custom notes as the primary source of rules.
- The extraction profile is a markdown file (not XML) since it contains instructional text for the AI agent, not structured extraction output
- Running `/reforge.profile` does not require a prior `/reforge.analyze` — users may know their tech stack before analysis
- The profile supplements (does not replace) the project context from `/reforge.init` — both files serve different purposes

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can generate a complete extraction profile for a 3-language codebase in under 5 minutes of interactive input
- **SC-002**: The generated profile contains at least 5 specific extraction rules per declared language (for any language the LLM has training knowledge of, which includes virtually all established programming languages)
- **SC-003**: The extract command loads the profile without user intervention — no additional flags or configuration required after profile creation
- **SC-004**: The extract command continues to function without error when no profile exists, operating with general extraction guidance only and prompting the user to run `/reforge.profile` for language-specific coverage
- **SC-005**: Users can update an existing profile to add or remove languages without losing previously configured content
- **SC-006**: 100% of generated profile content uses agent-agnostic language (no references to specific AI agent names)
- **SC-007**: The profile command works independently of `/reforge.init` — users can create a profile even without prior project context initialization
