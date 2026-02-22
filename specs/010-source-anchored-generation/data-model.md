# Data Model: Source-Anchored Generation

**Feature**: 010-source-anchored-generation
**Date**: 2026-02-20

## Overview

This feature introduces no new persistent data entities. All changes are to prompt template text that governs LLM behavior. The "data model" here is the catalog of new sections inserted into `generate.md` and their relationships.

## Section Catalog

### New Sections in generate.md

| Section | Type | Mandatory | References |
|---------|------|-----------|------------|
| Step 0.6: Source-Anchored Generation Constraints | Constraint definition | Yes | All subsequent sections |
| Canonical Metrics Computation | Operational procedure | Yes | Step 0.6 (Constraint 5) |
| Multi-File Extraction Discovery | Operational procedure | Yes | Canonical Metrics |
| Content Validation Checklist | Verification gate | Yes | Step 0.6 (all constraints) |
| Diagram Verification Protocol | Verification gate | Yes | Step 0.6 (Constraints 1, 4) |
| Cross-Extraction Consistency Check | Validation procedure | Yes | Canonical Metrics |
| Extraction Freshness & Gap Reporting | Validation procedure | Yes | Step 0.6 (Constraint 5) |
| Output Provenance Annotations | Output requirement | Yes | Step 0.6 (Constraint 1) |
| HTML Report Generation | Generation sub-command | Yes | Step 0.6 (all constraints) |
| Template Placeholder Specification | Reference table | Yes | Canonical Metrics |

### Dependency Graph

```
Step 0.6 (Constraints)
├── Canonical Metrics Computation
│   ├── Multi-File Extraction Discovery
│   ├── Cross-Extraction Consistency Check
│   └── Template Placeholder Specification
├── Content Validation Checklist
│   └── Selective Regeneration Update (rule 1)
├── Diagram Verification Protocol
├── Extraction Freshness & Gap Reporting
├── Output Provenance Annotations
├── HTML Report Generation
└── Template Annotations (5 files)
```

## Key Data Structures (In-Prompt)

### Canonical Metrics Table

A structured table computed by the agent at the start of each generation run. Not persisted as a separate file -- it exists in the agent's working context during the run.

```
Metric                    | Source                              | Value | Formula
--------------------------|-------------------------------------|-------|--------
total_files               | analysis.xml //file                 | [N]   | count(//file)
total_modules             | analysis.xml //module               | [N]   | count(//module)
total_business_rules      | business-rules/*.xml //rule         | [N]   | sum per file
total_functional_reqs     | functional-requirements/*.xml       | [N]   | sum per file
total_nfr                 | non-functional/*.xml                | [N]   | sum per file
total_ui_components       | ui/*.xml                            | [N]   | sum per file
```

**Lifecycle**: Created at generation start, referenced throughout, discarded at generation end. Recomputed for each new run.

### Content Validation Checklist

A 10-item boolean checklist completed by the agent before finalizing each generated document.

| Item | Validates |
|------|-----------|
| All numeric totals computed | FR-002, FR-003 |
| All identifiers verbatim | FR-004 |
| No unsourced claims | FR-001 |
| Diagrams verified | FR-009 |
| Consistent cross-references | FR-011 |
| Partial lists marked | FR-005 |
| No stale data | FR-012 |
| Provenance annotations present | FR-013 |
| No source code reads | FR-006 |
| Gap markers present | FR-007 |

### Diagram Verification Log

A structured comment block embedded in every generated diagram.

```
' === VERIFICATION LOG ===
' Source: [extraction-file.xml]
' Nodes: N verified against extraction
' Edges: M verified against extraction
' Omitted: K (with justification)
' Unresolved: 0
' === END VERIFICATION ===
```

### Provenance Annotation

HTML comments embedded in generated output sections.

```html
<!-- Source: extractions/business-rules/business-rules-authority.xml (42 rules) -->
```

### Gap Report (conditional)

A markdown file generated only when 3+ data gaps are encountered.

```
# Gap Report: [generation-run-date]

| # | Section | Gap Description | Recommended Command |
|---|---------|-----------------|---------------------|
| 1 | [section] | [what's missing] | /reforge.extract [type] |
```
