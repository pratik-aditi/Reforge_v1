# Requirements Checklist: 014 — Extraction Type Expansion

## Schema Requirements

- [ ] `common-schema.md` updated with 7 new root elements
- [ ] `common-schema.md` updated with 11 new ID prefixes (including GLOSS)
- [ ] 6 schema markdown files created (call-sites, dependencies, functional-requirements, non-functional, architecture, issues)
- [ ] Each schema MD extends common-schema.md and documents all elements/attributes
- [ ] 6 XSD files created with `xs:include` of `common-schema.xsd`
- [ ] Each XSD uses `rf:CommonRootAttributes` on root element
- [ ] All use unified namespace `http://reforge.dev/schema/extraction`

## Command Requirements

- [ ] `extract.md` type argument includes all 6 new types
- [ ] `extract.md` has extraction workflow section for each new type
- [ ] `extract.md` `--subtype` argument documented for architecture type
- [ ] `extract.md` validation section includes new types
- [ ] `extract.md` schema references section includes new types
- [ ] `audit.md` valid types list includes all 6 new types
- [ ] `status.md` file checks include all 6 new extraction files
- [ ] `status.md` extraction status table includes all 6 new types
- [ ] `status.md` JSON output includes all 6 new types
- [ ] `status.md` reading statistics section covers all 6 new types
- [ ] `generate.md` `--scope` values include all 6 new types

## Documentation Requirements

- [ ] `CLAUDE.md` Active Technologies updated
- [ ] Spec documents complete (spec.md, plan.md, data-model.md, research.md, quickstart.md, tasks.md)
- [ ] Requirements checklist complete

## Verification

- [ ] All 6 new types appear in `extract.md` argument list
- [ ] No per-type namespaces — all use unified namespace
- [ ] ID prefix examples provided for all 11 new prefixes
- [ ] Call-sites schema uses dual source refs (caller-source + callee-source)
- [ ] Non-functional schema uses dual containers (requirements + findings)
- [ ] Architecture schema supports --subtype routing
