# Feature Specification: Extract Verification Gates

**Feature Branch**: `006-extract-verification-gates`
**Created**: 2026-02-19
**Status**: Draft
**Input**: User description: "Add verification gates to `/reforge.extract` to prevent LLM hallucination and fabrication during code extraction"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Verbatim Identifier Extraction (Priority: P1)

An AI agent running `/reforge.extract` on a legacy codebase must copy all identifiers (class names, method names, enum members, constant names, file names, variable names) character-for-character from the source code rather than generating plausible-sounding names from context or memory.

**Why this priority**: Fabricated identifiers are the single most common and impactful failure mode, responsible for 5 of 13 verified errors (C1, M1, M2, M4, M8). Downstream consumers who search for fabricated names in the codebase will find nothing, undermining trust in the entire extraction.

**Independent Test**: Run `/reforge.extract business-rules` on a codebase containing enums, then grep every extracted identifier against the source. Every identifier must return at least one match.

**Acceptance Scenarios**:

1. **Given** a VB.NET file with enum `StateOfOnBoard` containing members like `InactiveSelfTest`, `InactiveIniting`, **When** the agent extracts enum members, **Then** every member name in the extraction XML matches the source declaration character-for-character (no fabricated names like `InactiveLoggedOn`).
2. **Given** a codebase where class `Srm` lives in file `Srm.vb`, **When** the agent writes a source reference, **Then** the `file` attribute says `Srm.vb`, not a fabricated name like `SrmManager.vb`.
3. **Given** a method call `EnableJointControlTracks(False)` in source code, **When** the agent extracts the workflow step, **Then** the extraction records `EnableJointControlTracks(False)`, not a paraphrased `DisableJointControlTracks`.

---

### User Story 2 - Post-Extraction Source Verification (Priority: P1)

After writing extraction XML, the AI agent must re-read a sample of source files to verify that extracted content (identifiers, line numbers, snippets) actually exists at the stated locations. Verification failures must be corrected before finalizing output.

**Why this priority**: Post-extraction verification is the safety net that catches any fabrication that slips through the verbatim extraction rules. It addresses all 13 verified errors.

**Independent Test**: After extraction completes, re-read 20% of referenced source files and confirm every identifier and snippet matches. Any mismatch means the verification gate failed.

**Acceptance Scenarios**:

1. **Given** extraction output referencing 50 source files, **When** post-extraction verification runs, **Then** at least 10 files (20%) are re-read and verified, with a minimum of 5 items checked regardless of count.
2. **Given** an extraction containing enum members, **When** post-extraction verification runs, **Then** ALL enum and constant extractions are verified (not just the 20% sample).
3. **Given** a fabricated identifier that slipped through extraction, **When** post-extraction verification cannot find it via re-read or grep, **Then** the item is corrected or marked `confidence="low"` with a clarification note.

---

### User Story 3 - Type-Aware Enum Extraction (Priority: P2)

When extracting enumeration-like types, the AI agent must capture the declared type (string, integer, custom base class) from the source declaration and never assign values of a different type.

**Why this priority**: Type misrepresentation (H1: PTCStatus described as integer enum when it uses string values) causes incorrect downstream documentation and potential reimplementation errors.

**Independent Test**: Run extraction on a codebase with custom enum patterns (e.g., `Enumeration(Of String, T)`) and verify the extraction records string-typed values, not fabricated integer values.

**Acceptance Scenarios**:

1. **Given** a class `PTCStatus` inheriting from `Enumeration(Of String, PTCStatus)` with string values like `"NONE"`, `"IVOC-CREATE"`, **When** extraction runs, **Then** the extraction records the type as string and copies every value verbatim (no fabricated integer values 0, 1, 2...).
2. **Given** an enum with more than 20 members, **When** extraction runs, **Then** ALL members are extracted (no summarization) and the total count matches an explicit count of declarations in the source.

---

### User Story 4 - Protocol and Security Extraction Accuracy (Priority: P2)

When extracting protocol descriptions, authentication mechanisms, or security-related findings, the AI agent must describe the actual code behavior rather than inferring from general domain knowledge or textbook definitions.

**Why this priority**: Pattern assumption errors (H2, M8) caused HMAC to be described as challenge-response when the code shows client-side self-signing, and fabricated security findings that waste remediation effort.

**Independent Test**: Extract a security-related workflow, then compare the extraction description against the actual code flow. The description must match what the code does, not what the technology generally does.

**Acceptance Scenarios**:

1. **Given** HMAC code that shows client-side self-signing with a hardcoded key, **When** extraction runs, **Then** the extraction describes "client-side HMAC-SHA1 signing with hardcoded key", not "challenge-response authentication".
2. **Given** a security finding claim (e.g., function X used in file Y), **When** extraction runs, **Then** the extraction includes a verbatim code snippet from the stated file proving the claim.

---

### User Story 5 - Language-Specific Extraction Accuracy (Priority: P3)

The extract command must account for language-specific quirks that can cause subtle errors, such as VB.NET array bounds semantics and boolean operator differences.

**Why this priority**: Language quirks caused 2 errors (M4: OrElse vs OR, M5: VB.NET array size off-by-one). While lower frequency, these errors are particularly insidious because they appear correct to someone unfamiliar with the language.

**Independent Test**: Extract from VB.NET code containing `Dim arr(6) As Byte` and verify the extraction records 7 elements (not 6). Extract boolean logic with `OrElse` and verify the exact operator is preserved.

**Acceptance Scenarios**:

1. **Given** VB.NET code `Dim privateKey(6) As Byte`, **When** extraction runs, **Then** the extraction records 7 bytes (indices 0-6), not 6 bytes.
2. **Given** VB.NET code using `OrElse` for short-circuit OR, **When** extraction runs, **Then** the extraction preserves `OrElse` exactly, not paraphrasing to "OR" or "AND".

---

### User Story 6 - Confidence Level Reflects Verification (Priority: P3)

Confidence levels must reflect whether identifiers were verified against source code, not merely whether the pattern appears clear and well-named.

**Why this priority**: The current confidence system allows fabricated content to receive `confidence="high"` because the fabricated names sound descriptive. Redefining confidence to include verification status makes confidence meaningful for downstream consumers.

**Independent Test**: After extraction, check that any item with unverified identifiers is rated `medium` or `low`, even if the business logic appears clear.

**Acceptance Scenarios**:

1. **Given** an extraction item where all identifiers were verified via re-read against source, **When** confidence is assigned, **Then** it may be `high`.
2. **Given** an extraction item where identifiers were reconstructed from memory rather than copied from source, **When** confidence is assigned, **Then** it must be `low`, regardless of pattern clarity.

---

### Edge Cases

- What happens when a source file is too large to read in one pass? The agent must read it in sections and process each section, tracking which portions were read.
- How does the system handle files that exist in analysis.xml but have been deleted from disk since analysis? The agent must detect the missing file and exclude it from extraction output (or mark `confidence="low"`).
- What if an enum has more than 100 members? All members must still be extracted verbatim; summarization is never acceptable for identifiers.
- What happens when grep returns 0 results for an identifier that was just read from source? This indicates a possible Read tool error or path mismatch; the agent should re-read the specific file and retry before flagging as fabricated.
- What if post-extraction verification reveals errors in more than 50% of sampled items? The agent should flag the entire extraction type for potential re-extraction rather than proceeding with corrections alone.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The extract command MUST include a verbatim extraction mandate requiring all identifiers (class names, method names, enum members, constant names, property names, field names, variable names, file names, string literals) to be copied character-for-character from source code as read by the Read tool.
- **FR-002**: The extract command MUST include a "read-before-describe" mandate requiring every source file to be read via the Read tool in the current session before any extraction from it is written.
- **FR-003**: The extract command MUST include a type-aware extraction protocol for enumerations and constants that captures the declared type (string, integer, custom base class), copies every member name verbatim, and records the total member count by explicit counting.
- **FR-004**: The extract command MUST include a post-extraction verification step (Step 5.5) between output generation and result reporting, requiring re-read of at least 20% of referenced source files (minimum 5 items) to verify identifiers, line numbers, and snippets.
- **FR-005**: The extract command MUST require 100% verification for all enum and constant extractions (not just the 20% sample).
- **FR-006**: The extract command MUST include a file existence gate requiring Glob or Read confirmation before writing any `file` attribute value in extraction output.
- **FR-007**: The extract command MUST include method signature verification requiring Grep confirmation that method names exist in the codebase before including them in extraction output.
- **FR-008**: The extract command MUST include snippet fidelity requirements mandating that all code snippets are verbatim copies from Read tool output, with no reformatting, simplification, or language translation.
- **FR-009**: The extract command MUST redefine confidence levels so that `high` requires source verification, `medium` indicates partial verification, and `low` indicates unverified or memory-based extraction.
- **FR-010**: The extract command MUST include a protocol/sequence accuracy section requiring security and protocol descriptions to trace actual code flow rather than assuming textbook patterns.
- **FR-011**: The extract command MUST include a language-specific extraction rules section covering at minimum VB.NET (array bounds, boolean operators, custom enum patterns, Option Strict, Nothing vs null) and C# (trailing newline, nameof, null-conditional operators, pattern matching).
- **FR-012**: The extract command MUST include aggregation accuracy requirements mandating explicit counting for all `count` attributes, with category sub-counts summing exactly to totals.
- **FR-013**: The extract command MUST change the "Optional Validation" section to "Required Validation", making both structural (XSD) and content verification mandatory.
- **FR-014**: The extract command MUST include documentation of XSD validation limitations, clearly noting that XSD checks structure only and cannot verify content accuracy.
- **FR-015**: The extract command MUST include a prohibited patterns list with at least 5 entries documenting common fabrication patterns to avoid (generating enum names from context, creating inverse method names, appending suffixes to filenames, reconstructing string literals, paraphrasing boolean operators).

### Key Entities

- **Verification Gate**: A checkpoint in the extraction workflow where accuracy is validated against source code before proceeding. Three types: pre-extraction (read-before-describe, file existence), during-extraction (verbatim copy, type-aware, method verification), and post-extraction (sampling verification, cross-reference check).
- **Extraction Item**: A single unit of extracted knowledge (business rule, database interaction, UI component, or workflow step) with source references, confidence level, and verification status.
- **Confidence Level**: A three-tier rating (high, medium, low) reflecting the verification status of an extraction item, not merely pattern clarity.
- **Source Reference**: A pointer to the original source code location (file path, line numbers, optional snippet) that must be validated for existence and accuracy.
- **Language Quirk**: A language-specific behavior that deviates from common assumptions and can cause extraction errors if not accounted for (e.g., VB.NET array bounds, OrElse vs Or).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: After implementation, running `/reforge.extract` on a codebase with enums produces extraction output where 100% of enum member names match source code when verified by grep.
- **SC-002**: After implementation, no extraction output references a file that does not exist in the project when verified by Glob.
- **SC-003**: After implementation, the post-extraction verification step runs on every extraction and checks at least 20% of source file references (minimum 5), reporting results in the extraction summary.
- **SC-004**: After implementation, all 8 original extraction-phase errors (C1, H1, H2, M1, M2, M4, M5, M8 from the failure taxonomy) would be prevented or detected by the new verification gates when the same source code is re-extracted.
- **SC-005**: After implementation, the word "verbatim" appears at least 3 times in extract.md and a "Prohibited patterns" list exists with at least 5 entries.
- **SC-006**: After implementation, confidence level `high` requires source verification, and items with unverified identifiers cannot receive `high` confidence.
- **SC-007**: After implementation, the "Optional Validation" section is replaced by "Required Validation" with both structural and content validation mandated.
- **SC-008**: After implementation, a "Language-Specific Extraction Rules" section exists covering VB.NET (at least 6 items) and C# (at least 4 items).

## Assumptions

- The target file for all modifications is `.reforge/commands/extract.md`, which is a markdown prompt template (not compiled code), consistent with the project's Constitution Principle I (LLM-First).
- The extract.md file structure (Steps 0-6, Common Elements, Validation sections) will remain stable enough that new sections can be inserted at the locations specified by the source spec.
- The Read, Glob, and Grep tools referenced in the verification gates are universally available to any AI agent executing the extract command.
- Line number references in the source spec (SPEC-001) pointing to specific locations in extract.md are approximately correct; exact insertion points may need minor adjustment during implementation.
- The XSD schemas will remain as structural-only validation; content-level validation will be handled by the new prompt-based verification gates described in this spec.
- The 20% sampling rate and minimum 5 items for post-extraction verification provide adequate coverage without making extraction prohibitively time-consuming for large codebases.

## Scope Boundaries

**In scope**:
- Modifications to `.reforge/commands/extract.md` only
- Adding new sections, replacing existing sections, and appending to existing sections per the insertion map in SPEC-001
- All 12 requirements (REQ-EXT-001 through REQ-EXT-012) from the source specification

**Out of scope**:
- Modifications to `generate.md`, `audit.md`, or `analyze.md` (these are separate future features per the failure taxonomy Priority 2-4)
- Changes to XSD schemas (structural validation is unchanged)
- Creation of new tooling or scripts (all verification is prompt-based, executed by the AI agent)
- Runtime enforcement mechanisms (gates are instructions, not automated checks)

## Dependencies

- **SPEC-001-extract-verification-gates.md**: The detailed source specification providing exact markdown text to insert at each location in extract.md.
- **failure-taxonomy.md**: Documents the 13 errors and 6 failure modes that these gates are designed to prevent.
- **extract-gap-analysis.md**: Identifies the 12 specific gaps in the current extract.md that enable failures.
- **Current extract.md**: The target file that will be modified. Implementation depends on its current structure remaining stable.
