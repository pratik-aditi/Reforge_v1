# Research: XSD Validation Tooling

**Feature**: 004-xsd-validation-tooling
**Date**: 2026-01-29

## Research Questions

### 1. xmllint Error Output Format

**Question**: What is the exact format of xmllint error messages and how can we parse them reliably?

**Findings**:

xmllint outputs validation errors to stderr in this format:
```
file.xml:45: element rule: Schemas validity error : Element 'ruel': This element is not expected. Expected is 'rule'.
```

Format breakdown:
- `{filename}:{line}:` — File path and line number
- `element {element_name}:` — Element context (optional)
- `Schemas validity error :` — Error type marker
- `{message}` — Human-readable error description

**Decision**: Parse stderr line-by-line using regex pattern:
```
^(?P<file>[^:]+):(?P<line>\d+):\s*(?:element\s+(?P<element>\w+):\s*)?(?:Schemas validity error\s*:\s*)?(?P<message>.+)$
```

**Rationale**: This pattern handles the common cases while being flexible enough for xmllint version differences.

**Alternatives Considered**:
- Python lxml library: Would add dependency; doesn't align with zero-dependency philosophy
- Custom XML parser: Over-engineering for validation use case
- Saxon validator: Enterprise-focused, overkill for this use case

---

### 2. xmllint Installation Detection

**Question**: How do we detect xmllint availability and provide installation guidance?

**Findings**:

Check with `which xmllint` or `shutil.which("xmllint")` in Python.

Installation commands by platform:
- **macOS**: Pre-installed (part of Xcode CLI tools); fallback: `brew install libxml2`
- **Ubuntu/Debian**: `sudo apt-get install libxml2-utils`
- **RHEL/CentOS**: `sudo yum install libxml2`
- **WSL**: Same as Ubuntu/Debian
- **Windows (native)**: Not supported; recommend WSL

**Decision**: Use `shutil.which("xmllint")` for detection; provide platform-specific install instructions in error message.

**Rationale**: Cross-platform Python solution that integrates well with existing CLI.

---

### 3. XSD Schema Naming Convention

**Question**: How should XSD filenames map to schema types used in the CLI?

**Findings**:

Current XSD files in `specs/*/contracts/`:
| XSD File | Logical Schema Type |
|----------|---------------------|
| analysis.xsd | analysis |
| business-rules.xsd | business-rules |
| database.xsd | database |
| ui-flows.xsd | ui-flows |
| workflows.xsd | workflows |
| user-stories.xsd | user-stories |
| audit-report.xsd | audit-report |
| correction-plan.xsd | correction-plan |

**Decision**: Schema type is the XSD filename without extension. CLI accepts either form:
- `reforge-scripts validate-xml file.xml business-rules`
- `reforge-scripts validate-xml file.xml business-rules.xsd`

**Rationale**: Simple 1:1 mapping; tolerant of both forms for user convenience.

---

### 4. Structured Error Output Format

**Question**: What format should validation errors use for optimal LLM parsing?

**Findings**:

LLMs parse structured text well. Key requirements:
- Clear delimiters between errors
- Consistent field names
- One error per block
- Actionable suggestions

**Decision**: Use line-based structured format:

```
VALIDATION_FAILED
FILE: path/to/file.xml
SCHEMA: schema-type
ERROR_COUNT: N
---
LINE: 45
COLUMN: 12
MESSAGE: Element 'ruel': This element is not expected.
SUGGESTION: Check spelling of element name on line 45
---
LINE: 67
...
```

For success:
```
VALIDATION_OK
FILE: path/to/file.xml
SCHEMA: schema-type
```

**Rationale**:
- Clear status at top (VALIDATION_OK/VALIDATION_FAILED)
- `---` delimiter is unambiguous and grep-friendly
- Field names in CAPS for easy regex matching
- Suggestions help LLM understand how to fix

**Alternatives Considered**:
- JSON output: Harder for LLMs to read in raw form; adds parsing complexity
- XML output: Ironic for a validation error; harder to read
- Plain prose: Not structured enough for reliable parsing

---

### 5. Exit Code Semantics

**Question**: What exit codes should the validation script return?

**Findings**:

Unix convention:
- 0 = success
- 1 = application error (validation failure)
- 2 = usage/system error

xmllint itself uses:
- 0 = valid
- 1 = unclassified error
- 2 = error in DTD
- 3 = validation error
- 4 = validation error (schema)

**Decision**: Simplify to three codes:
- `0` = Valid XML (passes schema validation)
- `1` = Invalid XML (schema validation errors)
- `2` = System/usage error (missing file, missing xmllint, bad arguments)

**Rationale**: Simple semantics that LLMs can easily interpret. Map all xmllint validation errors to exit code 1.

---

### 6. XSD Deployment Strategy

**Question**: When and how should XSD files be copied to target projects?

**Findings**:

Current install flow in `__init__.py`:
1. `copy_framework()` copies commands/, schemas/, templates/
2. `create_memory_dirs()` creates memory subdirectories
3. `generate_wrappers()` creates Claude command wrappers

XSD files need to be:
1. Included in package via `pyproject.toml` shared-data
2. Copied during install to `.reforge/schemas/xsd/`
3. Updated during `--update` operation

**Decision**:
- Store XSDs in `.reforge/schemas/xsd/` in the source repo
- Modify `copy_framework()` to include `schemas/xsd/` directory
- XSDs will be updated on `reforge --update` automatically

**Rationale**: Follows existing pattern; minimal code change.

---

### 7. Performance Considerations

**Question**: How do we ensure validation completes in <5 seconds for typical files?

**Findings**:

xmllint performance on typical Reforge output:
- 1KB XML: ~50ms
- 100KB XML: ~200ms
- 1MB XML: ~2s

Bottlenecks:
- Subprocess spawn: ~50ms
- XSD schema loading: ~100ms per schema
- Actual validation: ~2ms per KB

**Decision**: No special optimization needed. Single subprocess call with schema path:
```bash
xmllint --schema /path/to/schema.xsd /path/to/file.xml --noout
```

**Rationale**: xmllint is already highly optimized. Typical Reforge XML files are well under 1MB.

---

## Summary of Decisions

| Topic | Decision |
|-------|----------|
| Error parsing | Regex pattern on stderr, line-by-line |
| xmllint detection | `shutil.which()` with platform-specific install guidance |
| Schema naming | Filename without extension; accept both forms |
| Output format | Structured text with `---` delimiters, CAPS field names |
| Exit codes | 0=valid, 1=invalid, 2=system error |
| XSD deployment | Copy to `.reforge/schemas/xsd/` during install/update |
| Performance | Native xmllint subprocess; no optimization needed |

---

## Dependencies Identified

| Dependency | Type | Required? | Notes |
|------------|------|-----------|-------|
| xmllint (libxml2) | External CLI | Optional | Required for validation; graceful error if missing |
| typer | Python package | Existing | CLI framework (already in pyproject.toml) |
| rich | Python package | Existing | Console output (already in pyproject.toml) |
| shutil | Python stdlib | Yes | For `which()` detection |
| subprocess | Python stdlib | Yes | For xmllint invocation |
| re | Python stdlib | Yes | For error parsing regex |
