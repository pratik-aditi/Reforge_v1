# Research: 014 — Extraction Type Expansion

**Feature**: 014-extraction-type-expansion
**Created**: 2026-03-04

## Background

The TCOS-RUMO project produced 6 extraction categories beyond the 4 core types (business-rules, database, ui-flows, workflows) plus the glossary command. These additional types proved essential for comprehensive legacy codebase understanding but lacked formal schema support.

## Gap Analysis

### Current State (Pre-014)

| Type | Schema MD | XSD | Extract Section | Audit/Status/Generate |
|------|-----------|-----|-----------------|----------------------|
| business-rules | Yes | Yes | Yes | Yes |
| database | Yes | Yes | Yes | Yes |
| ui-flows | Yes | Yes | Yes | Yes |
| workflows | Yes | Yes | Yes | Yes |
| glossary | N/A (JSON) | N/A | Separate command | Partial |

### Missing Types (Identified from TCOS-RUMO)

| Type | Produced in TCOS-RUMO | Had Schema | Had XSD | Had Command Support |
|------|----------------------|------------|---------|-------------------|
| call-sites | Yes | No | No | No |
| dependencies | Yes | No | No | No |
| functional-requirements | Yes | No | No | No |
| non-functional | Yes | No | No | No |
| architecture | Yes | No | No | No |
| issues | Yes | No | No | No |

### Additional Fix: Glossary Prefix

The `GLOSS` prefix was not registered in `common-schema.md` Type Prefix Registry despite the glossary command (013) producing XML with `GLOSS-*` IDs.

## Design Alternatives Considered

### Alternative 1: Separate Commands Per Type

Each new type gets its own `/reforge.extract-<type>` command file.

**Rejected**: Would create 6 new command files with duplicated prerequisite/validation logic. The existing pattern consolidates all extraction types in a single `extract.md`.

### Alternative 2: Per-Module Output Files

Each extraction type produces per-module files (e.g., `call-sites/OrderController.xml`).

**Rejected**: TCOS-RUMO experience showed single consolidated files are easier to consume for downstream commands. Per-module splitting can be a future enhancement.

### Alternative 3: Separate Namespaces Per Type

Each new type gets its own XML namespace.

**Rejected**: Common schema (009) explicitly deprecates per-type namespaces in favor of the unified `http://reforge.dev/schema/extraction` namespace.

## Pattern References

- Schema pattern: `.reforge/schemas/business-rules.md`
- XSD pattern: `.reforge/schemas/xsd/business-rules.xsd`
- Extract section pattern: Business Rules section in `extract.md`
- Common schema extensibility guide: `common-schema.md` § Extensibility
