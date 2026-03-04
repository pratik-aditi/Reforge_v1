# Quickstart: 014 — Extraction Type Expansion

**Feature**: 014-extraction-type-expansion
**Created**: 2026-03-04

## Quick Reference

After this feature is implemented, the following new extraction commands are available:

```bash
# Extract method/function call relationships
/reforge.extract call-sites

# Extract module dependency graphs
/reforge.extract dependencies

# Extract functional requirements with acceptance criteria
/reforge.extract functional-requirements

# Extract non-functional requirements and security findings
/reforge.extract non-functional

# Extract architectural components, integrations, and design patterns
/reforge.extract architecture
/reforge.extract architecture --subtype design-patterns
/reforge.extract architecture --subtype integrations
/reforge.extract architecture --subtype infrastructure

# Extract bugs, defects, technical debt, and operational issues
/reforge.extract issues
```

## Output Files

| Command | Output File |
|---------|------------|
| `/reforge.extract call-sites` | `$EXTRACTIONS_DIR/call-sites.xml` |
| `/reforge.extract dependencies` | `$EXTRACTIONS_DIR/dependencies.xml` |
| `/reforge.extract functional-requirements` | `$EXTRACTIONS_DIR/functional-requirements.xml` |
| `/reforge.extract non-functional` | `$EXTRACTIONS_DIR/non-functional-requirements.xml` |
| `/reforge.extract architecture` | `$EXTRACTIONS_DIR/architecture.xml` |
| `/reforge.extract issues` | `$EXTRACTIONS_DIR/issues.xml` |

## Schema Files

Each type has a schema markdown and XSD in `.reforge/schemas/`:

| Type | Schema | XSD |
|------|--------|-----|
| call-sites | `call-sites.md` | `xsd/call-sites.xsd` |
| dependencies | `dependencies.md` | `xsd/dependencies.xsd` |
| functional-requirements | `functional-requirements.md` | `xsd/functional-requirements.xsd` |
| non-functional | `non-functional.md` | `xsd/non-functional.xsd` |
| architecture | `architecture.md` | `xsd/architecture.xsd` |
| issues | `issues.md` | `xsd/issues.xsd` |

## Validation

```bash
reforge-scripts validate-xml $EXTRACTIONS_DIR/call-sites.xml call-sites
reforge-scripts validate-xml $EXTRACTIONS_DIR/dependencies.xml dependencies
reforge-scripts validate-xml $EXTRACTIONS_DIR/functional-requirements.xml functional-requirements
reforge-scripts validate-xml $EXTRACTIONS_DIR/non-functional-requirements.xml non-functional
reforge-scripts validate-xml $EXTRACTIONS_DIR/architecture.xml architecture
reforge-scripts validate-xml $EXTRACTIONS_DIR/issues.xml issues
```

## Prerequisites

All new extraction types require a completed analysis (`/reforge.analyze`). Some types benefit from prior extractions:

- `functional-requirements`: Best results with existing `business-rules` and `workflows` extractions
- `architecture`: Benefits from `dependencies` and `call-sites` extractions
- `issues`: Can cross-reference `non-functional` findings
