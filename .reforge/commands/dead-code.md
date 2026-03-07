# /reforge.dead-code

> Detect unreachable code via call-site and dependency graph analysis

## Command Syntax

```
/reforge.dead-code [--scope <module|project>] [--include-tests] [--format html|xml] [--json]
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `--scope` | No | Analysis scope: `module` (single directory) or `project` (entire codebase, default) |
| `--include-tests` | No | Include test files in dead code analysis (excluded by default) |
| `--format` | No | Output format: `html` or `xml` (default: `xml`) |
| `--json` | No | Output summary as JSON to stdout |

## Overview

This command identifies dead code by cross-referencing:
- **Call-site extraction**: Methods/functions with no callers
- **Dependency extraction**: Files/modules with no inbound dependencies
- **Analysis inventory**: Classes, methods, and variables in the codebase

Output is written to `derived/dead-code-report.xml` following the [Dead Code Report Schema](../schemas/dead-code-report.md).

## Prerequisites

- Analysis must be completed (`/reforge.analyze`)
- Call-sites extraction must exist (`/reforge.extract call-sites`)
- Dependencies extraction must exist (`/reforge.extract dependencies`)
- `$ANALYSIS_DIR/analysis.xml` must exist

---

## Workflow

### Step 0: Check Prerequisites

Run the prerequisites script to validate state and resolve paths:

```bash
reforge-scripts check-prerequisites --json --require-analysis
```

This returns JSON with resolved variables:
```json
{"PROJECT_NAME":"...","REPO_ROOT":"...","PROJECT_OUTPUT_DIR":"...","CONFIG":"...","ANALYSIS_STATUS":"completed","AVAILABLE_EXTRACTIONS":[...],"CHECKPOINT":null,"CLARIFICATIONS_DIR":"..."}
```

Use `$PROJECT_OUTPUT_DIR` for all output paths in subsequent steps.

Assign subdirectory variables:
```
$ANALYSIS_DIR = $PROJECT_OUTPUT_DIR/analysis
$EXTRACTIONS_DIR = $PROJECT_OUTPUT_DIR/extractions
$DERIVED_DIR = $PROJECT_OUTPUT_DIR/derived
```

Verify that `call-sites.xml` and `dependencies.xml` exist in `$EXTRACTIONS_DIR/`. If either is missing, report an error and suggest running the required extraction first.

### Step 0.5: Load Project Context

If `.reforge/memory/project-context.md` exists, read it now. Use its contents as
supplemental guidance throughout this command's execution:
- **Technology Stack**: Informs language/framework detection and pattern recognition
- **Domain Knowledge**: Provides business context for naming and categorization
- **Analysis Guidelines**: Directs focus and exclusions beyond config.json
- **Custom Rules**: Additional rules to follow alongside the constitution

### Step 0.7: Check/Update Project Plan

If `.reforge/memory/project-plan.md` exists, read it now.

**On command start:**
- Parse the plan file to count total items and completed items
- Display: "📋 Project Plan: X/Y items complete (Z%)"
- Derive the plan tag: `<!-- reforge:dead-code -->`
- Identify the item with that tag and display its status

**On command completion (success only):**
- Locate the plan item by searching for `<!-- reforge:dead-code -->`
- If found and unchecked (`- [ ]`): change to `- [x]` and append ` *(completed: YYYY-MM-DD)*`
- If found and already checked (`- [x]`): leave unchanged (idempotent)
- If tag not found: emit warning -- "No plan item found for dead-code. Run /reforge.plan to add it."
- If file write fails: emit warning -- "Could not update project plan." Continue without failing.
- Update the `**Last Updated**` metadata line to today's date

If `.reforge/memory/project-plan.md` does not exist, skip this step silently.
The project plan is optional -- its absence MUST NOT affect command behavior.

### Step 1: Load Analysis and Extractions

Read the following files:

1. **`$ANALYSIS_DIR/analysis.xml`** -- Get full inventory of classes, methods, functions, and files
2. **`$EXTRACTIONS_DIR/call-sites.xml`** -- Get all caller/callee relationships
3. **`$EXTRACTIONS_DIR/dependencies.xml`** -- Get all module dependency relationships

Build an in-memory index of:
- All declared methods/functions (from analysis)
- All declared classes (from analysis)
- All files (from analysis)
- All call relationships (from call-sites)
- All dependency relationships (from dependencies)

If `--include-tests` is NOT set, exclude files matching test patterns (`*Test.*`, `*Spec.*`, `test/**`, `tests/**`, `__tests__/**`, `*_test.*`).

### Step 2: Build Call Graph

From the call-sites extraction, build a call graph:

1. For each `<call-site>` entry, record the caller and callee
2. Build a set of all callees (methods/functions that are called by something)
3. Build a set of all callers (methods/functions that call something)

### Step 3: Identify Dead Methods

For each method/function in the analysis inventory:

1. Check if it appears as a callee in the call graph
2. Exclude entry points that are expected to have no callers:
   - `main()` methods
   - Framework lifecycle methods (e.g., `onCreate`, `componentDidMount`, `ngOnInit`)
   - Annotated endpoints (`@RequestMapping`, `@GetMapping`, `@Route`, etc.)
   - Event handlers and callbacks registered via configuration
   - Test methods (if `--include-tests`)
3. If a method has no callers and is not an entry point, flag as dead code with reason `no-callers`

Confidence levels:
- **high**: Method has no callers AND no dynamic invocation patterns in the codebase
- **medium**: Method has no callers but dynamic dispatch patterns exist (reflection, DI)
- **low**: Method may be called via framework convention or external system

### Step 4: Identify Dead Classes

For each class in the analysis inventory:

1. Check if any method in the class is called (from call graph)
2. Check if the class is referenced in dependency graph (imports, extends, implements)
3. Check if the class is instantiated anywhere
4. If none of the above, flag as dead code with reason `never-instantiated`

### Step 5: Identify Dead Files

For each file in the analysis inventory:

1. Check if any item from this file is referenced in the dependency graph
2. Check if any method in this file appears in the call graph
3. If no inbound references at all, flag as dead code with reason `no-callers`

### Step 6: Identify Dead Variables and Imports

For each file flagged in the analysis:

1. Read the file using the Read tool
2. Identify unused imports (imported but never referenced in file body)
3. Identify write-only variables (assigned but never read)
4. Flag with appropriate reason (`unused-import` or `no-readers`)

### Step 7: Generate Report

Write `$DERIVED_DIR/dead-code-report.xml` following the [Dead Code Report Schema](../schemas/dead-code-report.md):

- Assign IDs using the `DC-{CATEGORY}-{SEQUENCE}` pattern
- Include summary with breakdowns by type and reason
- Include evidence for each dead item referencing call-site and dependency data
- Include source references with file, line numbers, and optional snippets

If `--format html` is specified, also generate an HTML version following the HTML documentation standard.

### Step 8: Report Results

```
Dead Code Analysis Complete!

Output: $DERIVED_DIR/dead-code-report.xml

Summary:
  Dead methods:   15 (480 lines)
  Dead classes:    3 (320 lines)
  Dead files:      2 (400 lines)
  Dead variables:  8 (50 lines)
  Dead imports:   12

Total dead code: 1,250 lines across 18 files

Confidence levels:
  High:   20 (71%)
  Medium:  6 (21%)
  Low:     2 (7%)

Top candidates for removal:
  1. LegacyReportGenerator.java (50 lines, no references)
  2. PricingService.calculateLegacyDiscount (35 lines, no callers)
  3. OldImportBatch.java (400 lines, entire file unused)

Run /reforge.audit to validate findings.
```

---

## Error Handling

| Error | Response |
|-------|----------|
| `analysis.xml` not found | Report error, suggest `/reforge.analyze` |
| `call-sites.xml` not found | Report error: "Call-sites extraction required. Run `/reforge.extract call-sites` first." |
| `dependencies.xml` not found | Report error: "Dependencies extraction required. Run `/reforge.extract dependencies` first." |
| File read error during variable analysis | Log warning, skip file, continue with remaining files |
| Empty call graph | Warn: "Call graph is empty -- all methods will appear as dead. Verify call-sites extraction." |

---

## Examples

### Full project dead code analysis

```
/reforge.dead-code
```

### Module-scoped analysis including tests

```
/reforge.dead-code --scope module --include-tests
```

### HTML output

```
/reforge.dead-code --format html
```

### Sample output

```xml
<?xml version="1.0" encoding="UTF-8"?>
<dead-code-report xmlns="http://reforge.dev/schema/extraction"
                  project-id="ecommerce-legacy" version="1.0.0"
                  schema-version="1.0.0"
                  generated="2024-01-15T10:30:00Z">
  <metadata>
    <total-count>3</total-count>
    <confidence-distribution>
      <high>2</high>
      <medium>1</medium>
      <low>0</low>
    </confidence-distribution>
    <extraction-timestamp>2024-01-15T10:30:00Z</extraction-timestamp>
  </metadata>

  <summary total-lines="85" total-files-affected="2">
    <by-type>
      <type name="method" count="2" lines="55"/>
      <type name="import" count="1" lines="1"/>
    </by-type>
    <by-reason>
      <reason name="no-callers" count="2"/>
      <reason name="unused-import" count="1"/>
    </by-reason>
  </summary>

  <dead-items count="3">
    <dead-item id="DC-METH-001" item-type="method" reason="no-callers"
               confidence="high" severity="medium">
      <name>calculateLegacyDiscount</name>
      <description>Method has no callers in the call-site graph.</description>
      <containing-class>PricingService</containing-class>
      <lines-of-code>35</lines-of-code>
      <evidence>
        <call-site-ref>No CALL entries reference PricingService.calculateLegacyDiscount</call-site-ref>
        <dependency-ref>No DEP entries reference this symbol</dependency-ref>
      </evidence>
      <source file="src/service/PricingService.java" line-start="120" line-end="155"/>
    </dead-item>

    <dead-item id="DC-METH-002" item-type="method" reason="no-callers"
               confidence="high" severity="low">
      <name>formatLegacyDate</name>
      <description>Utility method with no callers.</description>
      <containing-class>DateUtils</containing-class>
      <lines-of-code>20</lines-of-code>
      <evidence>
        <call-site-ref>No CALL entries reference DateUtils.formatLegacyDate</call-site-ref>
      </evidence>
      <source file="src/util/DateUtils.java" line-start="80" line-end="100"/>
    </dead-item>

    <dead-item id="DC-IMP-001" item-type="import" reason="unused-import"
               confidence="high" severity="low">
      <name>java.util.LinkedList</name>
      <description>Import is present but LinkedList is never used in this file.</description>
      <lines-of-code>1</lines-of-code>
      <source file="src/service/OrderService.java" line-start="5" line-end="5"/>
    </dead-item>
  </dead-items>
</dead-code-report>
```
