# Data Model: Extract Verification Gates

**Feature**: 006-extract-verification-gates
**Date**: 2026-02-19

## Overview

This feature modifies a single markdown prompt template (`.reforge/commands/extract.md`). There is no traditional data model with database entities or API schemas. The "data model" for this feature is the **section structure** of the modified extract.md file — the new sections being added and existing sections being modified.

## Section Map: New Sections Created

### 1. Enumeration and Constant Patterns (Step 2 addition)

**Location**: After line 151 (end of Constraint Patterns block), before Step 2.5
**Parent**: Step 2: Scan for Business Logic Patterns
**Purpose**: Add enum/constant detection patterns to the pattern recognition catalog
**Content type**: Code block examples + extraction protocol (7-point checklist)
**Requirements**: FR-003 (REQ-EXT-002)
**Relationships**: Referenced by Step 2.5 verbatim rules; feeds into Step 5.5 enum verification

### 2. Step 2.5: Verbatim Extraction Rules

**Location**: After Enumeration and Constant Patterns, before Step 3
**Parent**: Top-level workflow step (new)
**Purpose**: Anti-hallucination mandate for all identifier extraction
**Content type**: Directive text + identifier list + verification requirement + prohibited patterns list
**Requirements**: FR-001, FR-015 (REQ-EXT-001)
**Relationships**: Enforced by Step 5.5 post-verification; confidence levels reflect compliance

### 3. Step 3a: Technical Mechanism Accuracy

**Location**: After line 182 (Step 3 "Identify related entities"), before Step 4
**Parent**: Step 3: Extract Rule Details (sub-section)
**Purpose**: Prevent textbook-pattern substitution for protocols, security, and integrations
**Content type**: Directive text with domain-specific guidance (auth, protocols, external APIs) + self-check rule
**Requirements**: FR-010 (REQ-EXT-005)
**Relationships**: Feeds into Step 5.5 verification; referenced by security extraction findings

### 4. Step 5.5: Post-Extraction Verification

**Location**: Between Step 5 "Generate Output" (line 236) and Step 6 "Report Results" (line 238)
**Parent**: Top-level workflow step (new)
**Purpose**: Mandatory verification of extraction accuracy before finalizing output
**Content type**: Five sub-sections (A-E) with specific verification procedures
**Requirements**: FR-004, FR-005 (REQ-EXT-003)
**Sub-sections**:
  - A. Source File Existence — verify all `file` attributes
  - B. Identifier Sampling Verification — 20% sample, min 5 items
  - C. Line Number Accuracy — verify line ranges are valid
  - D. Enum/Constant Full Verification — 100% of enum extractions
  - E. Cross-Reference Consistency — verify rule-ref, sql-ref, workflow-ref IDs
**Relationships**: Depends on all prior extraction steps; feeds results into Step 6 reporting

### 5. Language-Specific Extraction Rules

**Location**: After line 812 (end of Common Elements), before Required Validation
**Parent**: Top-level section (new)
**Purpose**: Language quirk reference consulted during extraction
**Content type**: Per-language subsections (VB.NET: 6+ items, C#: 4+ items, General: 3+ items)
**Requirements**: FR-011 (REQ-EXT-009)
**Relationships**: Consulted during Step 2.5 verbatim extraction; referenced for boolean operator and array size accuracy

### 6. Required Validation (replaces Optional Validation)

**Location**: Lines 815-817 (replaces existing section header and intro)
**Parent**: Top-level section (replacement)
**Purpose**: Make validation mandatory; add content validation alongside structural XSD validation
**Content type**: Two subsections — Structural Validation (XSD, existing) + Content Validation (new) + XSD limitation documentation
**Requirements**: FR-013, FR-014 (REQ-EXT-003, REQ-EXT-012)
**Relationships**: References Step 5.5 for content verification procedures

## Section Map: Existing Sections Modified

### 1. Step 1: Load Analysis (line 84)

**Modification**: Append read-before-describe mandate
**Requirements**: FR-002 (REQ-EXT-010)
**Content added**: CRITICAL directive requiring file reads in current session

### 2. Step 3, sub-step 1: Capture the rule logic (line 160)

**Modification**: Insert type preservation text
**Requirements**: FR-003 (REQ-EXT-002 part 2)
**Content added**: Two bullet points on preserving data types and including type declarations in snippets

### 3. Step 5: Generate Output (line 195)

**Modification**: Insert aggregation accuracy requirements
**Requirements**: FR-012 (REQ-EXT-011)
**Content added**: Aggregation accuracy block with explicit counting mandate

### 4. Workflow Step 2: Follow method calls (line 683)

**Modification**: Insert method name accuracy text
**Requirements**: FR-007 (REQ-EXT-006)
**Content added**: Four bullet points on exact method names, actual parameters, Grep verification, call site recording

### 5. Confidence Levels table (lines 785-789)

**Modification**: Replace entire table with verification-based criteria
**Requirements**: FR-009 (REQ-EXT-008)
**Content replaced**: Three-row table + IMPORTANT note on verification vs. pattern clarity

### 6. Source References section (line 797)

**Modification**: Append file existence gate + snippet fidelity requirements
**Requirements**: FR-006, FR-008 (REQ-EXT-004, REQ-EXT-007)
**Content added**: File existence validation block + common fabrication patterns + snippet fidelity rules

## Traceability Matrix

| FR | REQ-EXT | Section Modified/Created | Operation |
|----|---------|--------------------------|-----------|
| FR-001 | REQ-EXT-001 | Step 2.5: Verbatim Extraction Rules | INSERT |
| FR-002 | REQ-EXT-010 | Step 1: Load Analysis | APPEND |
| FR-003 | REQ-EXT-002 | Enumeration and Constant Patterns + Step 3 type preservation | INSERT + INSERT |
| FR-004 | REQ-EXT-003 | Step 5.5: Post-Extraction Verification | INSERT |
| FR-005 | REQ-EXT-003 | Step 5.5 sub-section D | INSERT |
| FR-006 | REQ-EXT-004 | Source References | APPEND |
| FR-007 | REQ-EXT-006 | Workflow Step 2 | INSERT |
| FR-008 | REQ-EXT-007 | Source References | APPEND |
| FR-009 | REQ-EXT-008 | Confidence Levels table | REPLACE |
| FR-010 | REQ-EXT-005 | Step 3a: Technical Mechanism Accuracy | INSERT |
| FR-011 | REQ-EXT-009 | Language-Specific Extraction Rules | INSERT |
| FR-012 | REQ-EXT-011 | Step 5 aggregation accuracy | INSERT |
| FR-013 | REQ-EXT-003 | Required Validation (replaces Optional) | REPLACE |
| FR-014 | REQ-EXT-012 | Required Validation XSD limitation note | INSERT |
| FR-015 | REQ-EXT-001 | Step 2.5 Prohibited patterns list | INSERT |
