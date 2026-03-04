# Implementation Plan: 014 — Extraction Type Expansion

**Feature**: 014-extraction-type-expansion
**Created**: 2026-03-04

## Approach

Add 6 new extraction types to the Reforge framework with full schema standardization, XSD validation, and command integration.

## Phase Breakdown

### Phase 0: Spec Documents (T001–T006) — Parallel, No Dependencies

Create spec directory and all specification documents.

### Phase 1: Common Schema Update (T007) — BLOCKS All Below

Update `common-schema.md` to register:
- 7 new root elements (6 extraction types + glossary)
- 11 new ID prefixes (CALL, DEP, FR, NFR, SEC, ARCH, INT, DP, BUG, ISS, GLOSS)

### Phase 2: Schema Markdown Files (T008–T013) — Parallel After T007

Create 6 schema markdown files extending common-schema.md:
- call-sites.md, dependencies.md, functional-requirements.md
- non-functional.md, architecture.md, issues.md

### Phase 3: XSD Files (T014–T019) — Parallel After T007

Create 6 XSD files using `xs:include` of `common-schema.xsd`:
- call-sites.xsd, dependencies.xsd, functional-requirements.xsd
- non-functional.xsd, architecture.xsd, issues.xsd

### Phase 4: Command Updates (T020–T023) — Parallel After Phase 2+3

- T020: `extract.md` — 6 new type sections + argument list update
- T021: `audit.md` — Register 6 types in valid types list
- T022: `status.md` — Add file checks, table rows, JSON entries
- T023: `generate.md` — Add 6 `--scope` values

### Phase 5: Documentation (T024–T025) — After Phase 4

- T024: Update `CLAUDE.md` Active Technologies
- T025: Update constitution if needed

### Phase 6: Finalization (T026) — Last

- T026: Finalize tasks.md with completion status

## Key Patterns

- Schema template: `.reforge/schemas/business-rules.md`
- XSD template: `.reforge/schemas/xsd/business-rules.xsd`
- Extract section template: Business Rules section in `extract.md`
- All new types use unified namespace `http://reforge.dev/schema/extraction`

## Verification Checklist

- [ ] All 6 new types appear in `extract.md` argument list
- [ ] Each schema markdown extends common-schema.md
- [ ] Each XSD uses `xs:include` of `common-schema.xsd` and `rf:CommonRootAttributes`
- [ ] `common-schema.md` has all 11 new prefixes + 7 root elements
- [ ] `audit.md`, `status.md`, `generate.md` all reference the 6 new types
- [ ] No per-type namespaces — all use `http://reforge.dev/schema/extraction`
