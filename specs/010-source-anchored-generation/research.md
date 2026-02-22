# Research: Source-Anchored Generation

**Feature**: 010-source-anchored-generation
**Date**: 2026-02-20
**Status**: Complete

## Research Summary

No technology unknowns or NEEDS CLARIFICATION items exist. This feature modifies markdown prompt templates only. Research focused on confirming insertion points in existing files and validating the approach against the Constitution.

## R1: Insertion Point Analysis for generate.md

**Decision**: Insert Step 0.6 between existing Step 0.5 (line 67-75) and Step 0.7 (line 76).

**Rationale**: Step 0.5 loads project context. Step 0.6 establishes the constraints that govern all subsequent generation steps. Step 0.7 checks the project plan. This ordering ensures constraints are loaded before any generation work begins.

**Alternatives considered**:
- Insert as Step 0.4 (before project context load): Rejected -- constraints reference project context paths that Step 0.5 resolves.
- Insert as Step 1 (after all setup): Rejected -- constraints are a pre-condition for generation, not a generation step.

## R2: Bulk Section Insertion Location

**Decision**: Insert 7 verification/validation sections as a block before the Selective Regeneration section (line 975), creating a "Generation Quality Assurance" region.

**Rationale**: The Selective Regeneration section is the last operational section before "Optional Validation" and "Output Schema Reference". Placing verification sections before it ensures they apply to both full and selective generation runs. The existing "Optional Validation" section (line 986) will be superseded by the mandatory Content Validation Checklist -- this is intentional (the new checklist is mandatory, not optional).

**Alternatives considered**:
- Insert after each generation type (markdown, user-stories, etc.): Rejected -- duplicates content 8+ times. A single authoritative section that all generation types reference is cleaner.
- Insert at the very end: Rejected -- would be after "Output Schema Reference" which serves as an appendix.

## R3: Template Annotation Strategy

**Decision**: Add an identical 10-line annotation block to each of the 5 template files, referencing Step 0.6 by name.

**Rationale**: A reference block (rather than duplicating all constraints) keeps templates concise and ensures a single source of truth for the constraint definitions. If constraints change, only generate.md needs updating.

**Alternatives considered**:
- Duplicate full constraints in each template: Rejected -- maintenance burden and drift risk.
- Add constraints only to generate.md with no template changes: Rejected -- SPEC-002 explicitly requires template annotations (Section 4.6).

## R4: Agent-Agnostic Language Verification

**Decision**: All new text uses "the agent MUST" phrasing consistently.

**Rationale**: Constitution Principle V requires agent-agnostic design. The upstream SPEC-002 occasionally uses "the LLM" -- these will be normalized to "the agent" during implementation.

**Alternatives considered**: None -- Constitution requirement is non-negotiable.

## R5: Existing "Optional Validation" Section

**Decision**: The existing "Optional Validation" section (line 986) will NOT be removed but will be superseded by the new mandatory Content Validation Checklist.

**Rationale**: Removing existing content risks breaking backward compatibility for projects that reference it. The new mandatory checklist is more comprehensive. The "Optional Validation" section becomes a lighter-weight alternative that projects may use for quick checks.

**Alternatives considered**:
- Remove "Optional Validation" entirely: Rejected -- may break existing project workflows.
- Merge into new checklist: Rejected -- the new checklist has a different structure and is mandatory vs optional.
