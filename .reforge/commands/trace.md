# /reforge.trace

> Build end-to-end traceability chains across all extractions

## Command Syntax

```
/reforge.trace [--from <id>] [--depth <n>] [--format html|xml] [--json]
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `--from` | No | Start tracing from a specific item ID (e.g., `FR-AUTH-001`). Without this, traces all items. |
| `--depth` | No | Maximum chain depth (default: 10). Limits how many links deep a trace can go. |
| `--format` | No | Output format: `html` or `xml` (default: `xml`) |
| `--json` | No | Output summary as JSON to stdout |

## Overview

This command builds cross-extraction traceability chains linking:

```
Functional Requirement -> Business Rule -> Source Code -> UI Flow -> User Story
```

It also identifies **orphaned items** -- extraction artifacts with no connections to other artifacts, indicating potential gaps in coverage or understanding.

Output is written to `derived/traceability-matrix.xml` following the [Traceability Matrix Schema](../schemas/traceability-matrix.md).

## Prerequisites

- Analysis must be completed (`/reforge.analyze`)
- At least two extraction types must exist for meaningful tracing
- `$ANALYSIS_DIR/analysis.xml` must exist

Recommended extractions for full traceability:
- `functional-requirements.xml`
- `business-rules.xml`
- `call-sites.xml`
- `ui-flows.xml`
- `workflows.xml`
- Generated user stories (if available)

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
$GENERATED_DIR = $PROJECT_OUTPUT_DIR/generated
```

### Step 0.5: Load Project Context

If `.reforge/memory/project-context.md` exists, read it now. Use its contents as
supplemental guidance throughout this command's execution:
- **Technology Stack**: Informs code-level tracing patterns
- **Domain Knowledge**: Provides context for linking business concepts across extractions
- **Analysis Guidelines**: Directs focus and exclusions beyond config.json
- **Custom Rules**: Additional rules to follow alongside the constitution

### Step 0.7: Check/Update Project Plan

If `.reforge/memory/project-plan.md` exists, read it now.

**On command start:**
- Parse the plan file to count total items and completed items
- Display: "📋 Project Plan: X/Y items complete (Z%)"
- Derive the plan tag: `<!-- reforge:trace -->`
- Identify the item with that tag and display its status

**On command completion (success only):**
- Locate the plan item by searching for `<!-- reforge:trace -->`
- If found and unchecked (`- [ ]`): change to `- [x]` and append ` *(completed: YYYY-MM-DD)*`
- If found and already checked (`- [x]`): leave unchanged (idempotent)
- If tag not found: emit warning -- "No plan item found for trace. Run /reforge.plan to add it."
- If file write fails: emit warning -- "Could not update project plan." Continue without failing.
- Update the `**Last Updated**` metadata line to today's date

If `.reforge/memory/project-plan.md` does not exist, skip this step silently.
The project plan is optional -- its absence MUST NOT affect command behavior.

### Step 1: Load All Extractions

Read all available extraction files from `$EXTRACTIONS_DIR/`:

| File | ID Prefixes | Item Types |
|------|-------------|------------|
| `functional-requirements.xml` | `FR-` | Functional requirements |
| `business-rules.xml` | `BR-` | Business rules |
| `call-sites.xml` | `CALL-` | Method/function calls |
| `dependencies.xml` | `DEP-` | Module dependencies |
| `ui-flows.xml` | `SCR-`, `CMP-` | Screens and components |
| `workflows.xml` | `WF-` | Process workflows |
| `database.xml` | `DB-`, `E-` | Database interactions and entities |
| `non-functional.xml` | `NFR-`, `SEC-` | Non-functional and security |
| `architecture.xml` | `ARCH-`, `INT-`, `DP-` | Architecture components |
| `issues.xml` | `BUG-`, `ISS-` | Bugs and issues |

Also check for generated user stories in `$GENERATED_DIR/user-stories/`.

Build a master index: `{item-id -> {type, label, source-file, source-lines}}`.

If `--from` is specified, verify the ID exists in the index. If not, report an error.

### Step 2: Build Cross-Reference Map

Create linkage rules based on shared source locations and semantic relationships:

#### Source-Based Linking
Items that reference the same source file and overlapping line ranges are linked:
- A business rule at `OrderService.java:45-60` links to a call-site at `OrderService.java:48`
- A UI component at `login.html:10-25` links to a workflow referencing `login.html`

#### Semantic Linking
Items connected through naming, references, or domain concepts:
- A functional requirement mentioning "authentication" links to business rules with `AUTH` category
- A workflow step referencing `OrderService.placeOrder()` links to call-sites for that method
- A database entity links to business rules that reference that entity's table name

#### ID-Based Linking
Items that explicitly reference other item IDs in their content or metadata.

### Step 3: Build Trace Chains

For each starting item (or the item specified by `--from`):

1. Start with the item as the first link in the chain
2. Follow cross-references to find connected items in other extraction types
3. Continue until:
   - No more connections are found
   - Maximum depth (`--depth`) is reached
   - A cycle is detected (same item appears twice in chain)
4. Record the complete chain as a trace

**Chain building priority order**:
```
functional-requirement -> business-rule -> code (call-site) -> ui-flow -> user-story
```

When multiple paths exist, create separate traces for each distinct path.

### Step 4: Identify Orphaned Items

After building all traces, identify items that appear in NO trace chain:

1. Collect all item IDs that appear in at least one trace
2. Compare against the master index
3. Items not in any trace are orphans
4. For each orphan, determine why it's disconnected:
   - "No functional requirement references this rule"
   - "No implementing code found for this requirement"
   - "No UI surface found for this workflow"

### Step 5: Compute Coverage Statistics

Calculate traceability coverage per extraction type:

```
For each extraction type:
  total = number of items in that extraction
  traced = number of items appearing in at least one trace
  percent = (traced / total) * 100
```

### Step 6: Generate Traceability Matrix

Write `$DERIVED_DIR/traceability-matrix.xml` following the [Traceability Matrix Schema](../schemas/traceability-matrix.md):

- Assign IDs using the `TRACE-{CATEGORY}-{SEQUENCE}` pattern
- Include summary with coverage statistics
- Include all trace chains with linked items
- Include orphaned items with reasons
- Set confidence based on link strength:
  - **high**: All links are source-based or ID-based
  - **medium**: Some links are semantic only
  - **low**: Most links are inferred or tenuous

If `--format html` is specified, also generate an HTML version following the HTML documentation standard.

### Step 7: Report Results

```
Traceability Analysis Complete!

Output: $DERIVED_DIR/traceability-matrix.xml

Summary:
  Trace chains:  45
  Total links:  182
  Orphaned items: 12

Coverage:
  Functional Requirements: 28/30 (93%)
  Business Rules:          72/85 (85%)
  UI Flows:               20/22 (91%)
  Workflows:              14/15 (93%)

Orphan Highlights:
  - BR-CALC-015: Legacy commission calculation (no requirement)
  - FR-RPT-003: Monthly compliance report (no implementing code)
  - SCR-ADMIN-005: Admin settings page (no workflow)

Confidence levels:
  High:   30 (67%)
  Medium: 12 (27%)
  Low:     3 (7%)

Run /reforge.generate to create traceability documentation.
```

---

## Error Handling

| Error | Response |
|-------|----------|
| `analysis.xml` not found | Report error, suggest `/reforge.analyze` |
| No extractions found | Report error: "At least two extraction types required for tracing. Run `/reforge.extract` first." |
| Only one extraction type | Warn: "Only one extraction type found. Traceability requires multiple types. Results will be limited." |
| `--from` ID not found | Report error: "Item ID not found in any extraction. Verify the ID and ensure the relevant extraction exists." |
| Cycle detected in chain | Terminate chain at cycle point, log: "Cycle detected at {item-id}, chain truncated." |
| Extraction file parse error | Warn and skip that extraction type, continue with remaining |

---

## Examples

### Full traceability matrix

```
/reforge.trace
```

### Trace from a specific requirement

```
/reforge.trace --from FR-AUTH-001
```

### Limited depth trace

```
/reforge.trace --depth 5
```

### HTML output

```
/reforge.trace --format html
```
