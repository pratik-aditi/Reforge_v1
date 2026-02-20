# Quickstart: Common Extraction Schema

**Feature**: 009-common-extraction-schema

## What This Feature Does

Introduces a common structural contract for all Reforge extraction output XML files. After implementation, every extraction type (business-rules, database, ui-flows, workflows) shares the same root attributes, metadata format, source references, and confidence vocabulary.

## Key Files

| File | Purpose |
|------|---------|
| `.reforge/schemas/common-schema.md` | Authoritative common schema definition (markdown) |
| `.reforge/schemas/xsd/common-schema.xsd` | Formal XSD with shared types |
| `.reforge/schemas/{type}.md` | Updated type-specific schemas (link to common) |
| `.reforge/schemas/xsd/{type}.xsd` | Updated XSDs (xs:include common) |
| `.reforge/commands/extract.md` | Updated with validation gate |

## How It Works

### For extraction consumers (audit, generate, status)

All extraction files now share these element paths:

```
Root attributes:  /{root}/@project-id, /@version, /@schema-version, /@generated
Metadata:         /{root}/metadata/total-count
Confidence dist:  /{root}/metadata/confidence-distribution/{high|medium|low}
Source refs:      //source/@file, //source/@line-start, //source/@line-end
```

No type-specific parsing needed for common fields.

### For the extract command

The extract command now includes a validation gate (Step 5.6) that:

1. Reads `common-schema.md` for required structure
2. Checks output for required root attributes, metadata, source format
3. Auto-corrects where possible (adds missing attributes, normalizes source refs)
4. Inserts `<!-- SCHEMA-WARNING: ... -->` for uncorrectable issues
5. Reports validation results in extraction summary

### For schema contributors

Type-specific schemas now reference `common-schema.md` instead of redefining shared elements:

```markdown
## Common Elements

> Inherited from [common-schema.md](./common-schema.md). See that file for:
> root attributes, metadata, source references, confidence vocabulary, ID patterns.

## Type-Specific Elements
<!-- Only type-specific content below -->
```

## Implementation Order

1. Create `common-schema.md` and `common-schema.xsd` (new files)
2. Update extract command template with validation gate
3. Update 4 type-specific markdown schemas (link to common)
4. Update 4 type-specific XSDs (xs:include common, remove duplicates)
5. Update extract command XML examples to use new namespace and metadata

## Namespace

All extraction types use the unified namespace:
```
http://reforge.dev/schema/extraction
```

This replaces the per-type namespaces (`http://reforge.dev/schema/business-rules`, etc.).
