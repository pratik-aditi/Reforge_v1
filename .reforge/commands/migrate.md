# /reforge.migrate

> Generate a phased migration playbook with 5R strategy per module and risk register

## Command Syntax

```
/reforge.migrate [--strategy <5r|lift-shift|strangler>] [--phases <n>] [--format html|xml] [--json]
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `--strategy` | No | Migration strategy framework: `5r` (default), `lift-shift` (rehost-only), `strangler` (strangler-fig pattern) |
| `--phases` | No | Target number of migration phases (default: auto-determined from dependency graph) |
| `--format` | No | Output format: `xml` (default), `html` (standalone report) |
| `--json` | No | Output summary as JSON to stdout (for scripting) |

## Overview

This command generates a phased migration playbook that classifies each module by migration strategy, sequences modules into dependency-aware phases, and produces a risk register with mitigation plans.

**Strategy frameworks**:
- **5R**: Classify each module as Rehost, Replatform, Refactor, Rearchitect, or Retire based on complexity, coupling, and business value
- **Lift-shift**: All modules assigned `rehost` strategy (cloud migration with minimal changes)
- **Strangler**: Incremental replacement using strangler-fig pattern -- new modules replace legacy ones phase-by-phase

## Prerequisites

- Analysis must be completed (`/reforge.analyze`)
- Architecture extraction recommended (`/reforge.extract architecture`)
- Dependencies extraction required (`/reforge.extract dependencies`)
- Issues extraction recommended (`/reforge.extract issues`)
- Business rules extraction recommended (`/reforge.extract business-rules`)
- Non-functional extraction recommended (`/reforge.extract non-functional`)

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
$GENERATED_DIR = $PROJECT_OUTPUT_DIR/generated
```

### Step 0.5: Load Project Context

If `.reforge/memory/project-context.md` exists, read it now. Use its contents as
supplemental guidance throughout this command's execution:
- **Technology Stack**: Informs current/target stack assessment and strategy selection
- **Domain Knowledge**: Provides business context for module prioritization
- **Analysis Guidelines**: Directs focus and exclusions beyond config.json
- **Custom Rules**: Additional rules to follow alongside the constitution

### Step 0.7: Check/Update Project Plan

If `.reforge/memory/project-plan.md` exists, read it now.

**On command start:**
- Parse the plan file to count total items and completed items
- Display: "📋 Project Plan: X/Y items complete (Z%)"
- Search for `<!-- reforge:migrate -->` and display its status

**On command completion (success only):**
- Locate the plan item by searching for `<!-- reforge:migrate -->`
- If found and unchecked (`- [ ]`): change to `- [x]` and append ` *(completed: YYYY-MM-DD)*`
- If found and already checked (`- [x]`): leave unchanged (idempotent)
- If tag not found: emit warning -- "No plan item found for migrate. Run /reforge.plan to add it."
- If file write fails: emit warning -- "Could not update project plan." Continue without failing.
- Update the `**Last Updated**` metadata line to today's date

If `.reforge/memory/project-plan.md` does not exist, skip this step silently.
The project plan is optional -- its absence MUST NOT affect command behavior.

### Step 1: Load Input Data

Read available extraction files to build the migration context:

**Required:**
- `$ANALYSIS_DIR/analysis.xml` -- Module inventory and file list

**Strongly recommended:**
- `$EXTRACTIONS_DIR/dependencies.xml` -- Dependency graph for phase sequencing
- `$EXTRACTIONS_DIR/architecture.xml` -- Module boundaries, integration points

**Recommended (use if available):**
- `$EXTRACTIONS_DIR/issues.xml` -- Technical debt density, bug severity
- `$EXTRACTIONS_DIR/business-rules.xml` -- Business logic complexity per module
- `$EXTRACTIONS_DIR/non-functional.xml` -- SLA requirements, security constraints

If dependencies extraction is missing, warn prominently:

```
Warning: dependencies.xml not found.
  Phase sequencing will be based on directory structure only.
  Migration order may not reflect actual dependency relationships.

  Strongly recommended: Run /reforge.extract dependencies first.

Proceeding with limited dependency information...
```

If other recommended extractions are missing, warn and proceed:

```
Warning: Missing recommended extractions for migration planning:
  - architecture.xml (not found) -- module boundaries inferred from analysis
  - issues.xml (not found) -- risk assessment will use conservative defaults
  - business-rules.xml (not found) -- business logic complexity unknown

Consider running: /reforge.extract architecture issues business-rules
Proceeding with available data...
```

### Step 2: Classify Modules by 5R Strategy

For each module identified in Step 1, assess and assign a migration strategy:

**Assessment factors**:

1. **Complexity**: Lines of code, cyclomatic complexity indicators, issue density
2. **Coupling**: Dependency count (internal and external), integration points
3. **Business value**: Business rule density, usage frequency indicators
4. **Technical debt**: Bug count, deprecated API usage, anti-pattern indicators
5. **Platform compatibility**: Current stack vs. target stack compatibility

**Strategy assignment rules** (for `--strategy 5r`):

| Strategy | Criteria |
|----------|----------|
| `rehost` | Low complexity, no code changes needed, compatible runtime |
| `replatform` | Low-moderate complexity, minor platform adjustments (e.g., database driver swap) |
| `refactor` | Moderate complexity, business logic restructuring needed, maintainable interfaces |
| `rearchitect` | High complexity, fundamental design changes required (e.g., monolith decomposition) |
| `retire` | No active usage, superseded by other modules, or identified as dead code |

**For `--strategy lift-shift`**: Assign `rehost` to all modules.

**For `--strategy strangler`**: Assign `rearchitect` to modules with highest coupling, `refactor` to moderate, `replatform` to low-coupling modules. Sequence phases so new implementations shadow legacy modules incrementally.

### Step 3: Sequence Into Phases

Organize modules into migration phases based on dependency order:

1. **Build dependency graph**: From dependencies.xml or inferred from analysis
2. **Topological sort**: Identify modules with no upstream dependencies (Phase 1 candidates)
3. **Group by dependency tier**: Modules that depend only on Phase N modules go into Phase N+1
4. **Respect `--phases` target**: If specified, merge or split tiers to match target phase count
5. **Minimize cross-phase dependencies**: Optimize grouping to reduce inter-phase coupling

**Phase construction**:
- Each phase gets a descriptive name (e.g., "Foundation", "Core Services", "Integration Layer")
- Define prerequisites: what must be complete before the phase starts
- Define success criteria: measurable conditions that define phase completion
- Estimate duration based on included module effort estimates

### Step 4: Build Risk Register

Identify migration risks by analyzing:

1. **Data migration risks**: Schema incompatibilities, data volume, transformation complexity
2. **Performance risks**: SLA requirements from non-functional extraction, latency-sensitive paths
3. **Compatibility risks**: API breaking changes, protocol differences, library version conflicts
4. **Team/skill risks**: Unfamiliar target technologies, knowledge concentration in specific modules
5. **Vendor risks**: License changes, deprecation timelines, vendor lock-in indicators
6. **Scope risks**: Hidden complexity, undocumented dependencies, missing test coverage

**For each risk**:
- Assign severity (critical, high, medium, low) and probability (high, medium, low)
- Link to affected modules
- Define mitigation strategy
- Define contingency plan (fallback if mitigation fails)

### Step 5: Generate Migration Playbook

Write the playbook to `$GENERATED_DIR/migration-playbook.xml` following the
[migration-playbook schema](../schemas/migration-playbook.md).

**Schema compliance**:
- Root element: `<migration-playbook>` with common root attributes
- Include `<metadata>` as first child with total migration item count and confidence distribution
- Phases ordered by `order` attribute (1-based)
- Each `<module>` has `id`, `name`, `strategy`, and `confidence` attributes
- Module `id` follows `MIG-{CATEGORY}-{SEQUENCE}` pattern
- Risk `id` follows `RISK-{CATEGORY}-{SEQUENCE}` pattern
- `<strategy-summary>` totals computed by counting elements at generation time
- All `<dependency ref="...">` attributes must reference valid module IDs within the playbook

**Validation rules**:
- Every module appears in exactly one phase
- Phase `order` values are sequential starting from 1
- Module dependencies reference only modules in the same or earlier phases
- Strategy summary counts match actual module strategy assignments
- Risk `affected-modules` references are valid module IDs

### Step 6: Report Results

```
Migration Playbook Complete!

Output: $GENERATED_DIR/migration-playbook.xml

Strategy Summary:
- Total modules: 12
- Strategy framework: 5R

By Strategy:
  - Rehost:       2 modules (17%)
  - Replatform:   3 modules (25%)
  - Refactor:     4 modules (33%)
  - Rearchitect:  1 module  (8%)
  - Retire:       2 modules (17%)

Phases: 3
  Phase 1 (Foundation):      4 modules, ~3 weeks
  Phase 2 (Core Services):   5 modules, ~5 weeks
  Phase 3 (Integration):     3 modules, ~4 weeks

Total Estimated Effort: 12 person-weeks

Risk Register: 5 risks identified
  - Critical: 0
  - High:     2
  - Medium:   2
  - Low:      1

Run /reforge.estimate for detailed per-module effort estimates.
Run /reforge.generate html --scope migration-playbook for a formatted report.
```

---

## Error Handling

### Missing Analysis

If analysis.xml does not exist (caught by prerequisites script):

```
Error: Analysis not found. Run /reforge.analyze first.
  Expected: $ANALYSIS_DIR/analysis.xml

The migrate command requires a completed analysis to inventory modules.
Run /reforge.analyze to inventory your codebase first.
```

### Missing Dependencies Extraction

If dependencies.xml is not found:

```
Warning: Dependencies extraction not found.
  Expected: $EXTRACTIONS_DIR/dependencies.xml

  Phase sequencing will use directory structure as a proxy for dependencies.
  This may produce suboptimal migration ordering.

  Recommended: Run /reforge.extract dependencies first.

Proceeding with inferred dependencies...
```

### Empty Analysis

If analysis.xml exists but contains no file entries:

```
Warning: Analysis contains no file entries.
  No modules to plan migration for.

  This may indicate:
  - All files matched exclusion patterns
  - Analysis was interrupted before processing files

  Run /reforge.analyze to re-inventory the codebase.
```

### Circular Dependencies

If the dependency graph contains cycles:

```
Warning: Circular dependency detected:
  ModuleA -> ModuleB -> ModuleC -> ModuleA

  Circular modules will be grouped into the same phase.
  Consider running /reforge.extract dependencies for detailed cycle analysis.
```

### Invalid Phase Count

If `--phases` value is less than the minimum required by dependency constraints:

```
Warning: Requested 2 phases but dependency graph requires minimum 4.
  Using 4 phases to respect dependency ordering.
```

---

## Examples

### Basic Usage

```
/reforge.migrate
```

Generates a 5R migration playbook with auto-determined phases.

### Lift-and-Shift Migration

```
/reforge.migrate --strategy lift-shift
```

All modules assigned `rehost` strategy for cloud migration with minimal changes.

### Fixed Phase Count

```
/reforge.migrate --phases 3
```

Organizes migration into exactly 3 phases (merging dependency tiers as needed).

### JSON Output for Scripting

```
/reforge.migrate --json
```

Outputs summary as JSON to stdout in addition to the XML file:

```json
{
  "total_modules": 12,
  "strategy": "5r",
  "phases": 3,
  "by_strategy": {
    "rehost": 2,
    "replatform": 3,
    "refactor": 4,
    "rearchitect": 1,
    "retire": 2
  },
  "total_effort": "12 person-weeks",
  "total_risks": 5
}
```

### Strangler-Fig Migration

```
/reforge.migrate --strategy strangler --phases 5
```

Generates a 5-phase incremental replacement plan using the strangler-fig pattern.
