# Quickstart: Extract Verification Gates

**Feature**: 006-extract-verification-gates
**Date**: 2026-02-19

## What This Feature Does

Adds anti-hallucination verification gates to the `/reforge.extract` command template (`.reforge/commands/extract.md`). After implementation, the extract command will instruct AI agents to:

1. **Read before describing** — every source file must be read in the current session before extracting from it
2. **Copy identifiers verbatim** — never paraphrase, infer, or reconstruct names from memory
3. **Verify file existence** — confirm files exist via Glob before referencing them
4. **Extract enums type-aware** — capture actual declared types, copy all members
5. **Describe code behavior, not textbook patterns** — trace actual protocol/security implementations
6. **Verify after extraction** — re-read 20% of source files to spot-check accuracy
7. **Make validation mandatory** — both structural (XSD) and content verification required

## Prerequisites

- Branch `006-extract-verification-gates` checked out
- Access to SPEC-001 source document at `/Users/ryanhilliard/clients/wabtec/tcos/reforge_output/TCOS-RUMO/specs/SPEC-001-extract-verification-gates.md`
- Current `.reforge/commands/extract.md` at ~841 lines (verify line numbers match research.md)

## Implementation Steps

### Step 1: Verify Starting State

```bash
# Confirm target file exists and check line count
wc -l .reforge/commands/extract.md
# Expected: ~841 lines

# Verify key anchor points
grep -n "Optional Validation" .reforge/commands/extract.md
# Expected: line 815

grep -n "Step 3: Extract Rule Details" .reforge/commands/extract.md
# Expected: line 153
```

### Step 2: Apply Modifications (Bottom-to-Top)

Apply the 13 operations from the plan's Modification Sequence table, starting from the bottom of the file (line 815) and working upward (line 84). Each operation uses the exact markdown text from SPEC-001.

### Step 3: Verify Success Criteria

```bash
# SC-005: "verbatim" appears at least 3 times
grep -c "verbatim" .reforge/commands/extract.md
# Expected: >= 3

# SC-005: Prohibited patterns list exists
grep "Prohibited patterns" .reforge/commands/extract.md
# Expected: at least 1 match

# SC-007: "Optional Validation" replaced
grep "Optional Validation" .reforge/commands/extract.md
# Expected: 0 matches

grep "Required Validation" .reforge/commands/extract.md
# Expected: 1 match

# New sections exist
grep "Step 2.5" .reforge/commands/extract.md
grep "Step 5.5" .reforge/commands/extract.md
grep "Language-Specific Extraction Rules" .reforge/commands/extract.md
# Expected: all return matches

# Confidence table updated
grep "verified against source code" .reforge/commands/extract.md
# Expected: 1 match (in high confidence criteria)
```

### Step 4: Full Acceptance Verification

Run through all 12 acceptance criteria from SPEC-001 Section 5:
- AC-001 through AC-012 each have specific grep-verifiable checks
- See spec.md Success Criteria SC-001 through SC-008 for the full list

## Key Files

| File | Role |
|------|------|
| `.reforge/commands/extract.md` | Target file for all modifications |
| `SPEC-001-extract-verification-gates.md` | Source of exact markdown text to insert |
| `specs/006-extract-verification-gates/spec.md` | Feature specification |
| `specs/006-extract-verification-gates/plan.md` | Implementation plan with operation sequence |
| `specs/006-extract-verification-gates/data-model.md` | Section map and traceability matrix |

## Troubleshooting

**Line numbers don't match**: If extract.md has been modified since this plan was created, use semantic anchors (section headers like "### Step 3: Extract Rule Details") instead of line numbers to locate insertion points. See research.md for the one known drift (line 186 → 182).

**Agent-specific language found**: If inserted text references specific AI agents (Claude, Copilot), replace with "the agent" or "you" per Constitution Principle V.

**Markdown rendering issues**: After insertion, verify that code blocks (triple backtick) are properly opened and closed. Nested code blocks in SPEC-001 use indentation to avoid conflicts.
