# Research: Extract Verification Gates

**Feature**: 006-extract-verification-gates
**Date**: 2026-02-19

## Research Task 1: Line Number Verification

**Decision**: SPEC-001's line number references are accurate with one minor exception.

**Findings**: Verified all 13 line number references from SPEC-001 against the current `.reforge/commands/extract.md`:

| SPEC-001 Reference | Expected Content | Actual | Status |
|---------------------|------------------|--------|--------|
| Line 84 | End of Step 1 "Load Analysis" | `- Component locations (classes, methods)` | MATCH |
| Line 151 | End of "Constraint Patterns" block | Closing ``` of code block | MATCH |
| Line 153 | Start of Step 3 | `### Step 3: Extract Rule Details` | MATCH |
| Line 160 | Within Step 3 sub-step 1 | `- Identify any else/default cases` | MATCH |
| Line 186 | "Identify related entities" | Blank line (actual content at line 182) | DRIFT -4 |
| Line 195 | Within Step 5 before XML example | `Write to $EXTRACTIONS_DIR/business-rules.xml:` | MATCH |
| Line 236 | End of Step 5 | Closing ``` of XML code block | MATCH |
| Line 238 | Start of Step 6 | `### Step 6: Report Results` | MATCH |
| Line 683 | "Note return values used" in Workflow Step 2 | `- Note return values used` | MATCH |
| Lines 785-789 | Confidence Levels table | Three-row table (high/medium/low) | MATCH |
| Line 797 | "snippet (optional)" in Source References | `- snippet (optional): Actual code snippet` | MATCH |
| Line 812 | End of Common Elements section | Blank line before `---` separator | MATCH |
| Lines 815-817 | "Optional Validation" header and intro | `## Optional Validation` + intro text | MATCH |

**Rationale**: 12 of 13 references are exact. The one drift (line 186 → 182) is a -4 line shift likely from content being shorter than SPEC-001 anticipated in the Step 3 sub-steps area. This is minor and easily handled by using semantic anchors (section/sub-step names) rather than absolute line numbers during implementation.

**Alternatives considered**: Could re-generate SPEC-001 with corrected line numbers, but unnecessary — the drift is small and the semantic context is unambiguous.

## Research Task 2: Insertion Strategy (Bottom-to-Top)

**Decision**: Apply modifications bottom-to-top to preserve line number accuracy.

**Rationale**: When inserting text into a file, all line numbers below the insertion point shift. By starting from the bottom of the file (line 815+) and working upward (to line 84), each operation's target line numbers remain valid because no prior operation has shifted them.

**Alternatives considered**:
- **Top-to-bottom with recalculation**: Would require recalculating line offsets after each insertion. Error-prone and harder to verify.
- **Semantic-only anchors (no line numbers)**: Possible but slower for the implementer. Used as fallback for the drifted line 186 case.

## Research Task 3: Agent-Agnostic Language Compliance

**Decision**: SPEC-001's insertion text is compliant with Constitution Principle V.

**Findings**: Scanned all markdown text blocks in SPEC-001 for agent-specific references:
- Uses "the LLM MUST", "you MUST" — no agent-specific names
- Tool references: "Read tool", "Glob", "Grep" — these are common tool patterns allowed by Principle V ("Commands MUST use only common tool patterns: file read, file write, glob, grep, directory listing")
- No MCP server references, no proprietary features

**Rationale**: No modifications needed to SPEC-001 text for agent-agnostic compliance.

## Research Task 4: Extraction Type Coverage

**Decision**: Verification gates apply across all 4 extraction types via shared sections.

**Findings**: SPEC-001's modifications target three location types:
1. **Common Elements section** (lines 781-812): Confidence levels, source references, file existence, snippet fidelity, language quirks — these apply to ALL extraction types (business-rules, database, ui, workflows)
2. **Business Rules workflow** (Steps 1-6): Read-before-describe, enum patterns, verbatim rules, type preservation, aggregation, post-extraction verification — apply to business-rules extraction specifically but establish patterns for all types
3. **Workflow extraction** (Step 2): Method name accuracy — applies to workflow extraction specifically

The Common Elements modifications (operations 1-5 in the plan) provide universal coverage. The type-specific modifications establish the pattern that other extraction types inherit by convention.

**Alternatives considered**: Could duplicate verification instructions in each extraction type's workflow. Rejected because it would increase maintenance burden and the Common Elements section already applies universally.

## Research Task 5: Boolean Operator Handling in Inserted Text

**Decision**: SPEC-001 correctly addresses VB.NET boolean operator capture.

**Findings**: The verbatim extraction rules (REQ-EXT-001) and language quirks (REQ-EXT-009) both address boolean operators:
- REQ-EXT-001 adds `OrElse`, `AndAlso`, `&&`, `||`, `Or`, `And` to the verbatim copy mandate
- REQ-EXT-009 adds VB.NET-specific explanation of `OrElse` vs `Or` and `AndAlso` vs `And`

Both are needed: REQ-EXT-001 establishes the rule, REQ-EXT-009 explains why it matters for VB.NET specifically.

**Rationale**: No changes needed. The dual coverage provides defense-in-depth.
