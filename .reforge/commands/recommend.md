# /reforge.recommend

> Generate technology stack recommendations based on architecture analysis and requirements

## Command Syntax

```
/reforge.recommend [--focus <backend|frontend|data|infra>] [--constraints <text>] [--format html|xml] [--json]
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `--focus` | No | Limit recommendations to a specific domain: `backend`, `frontend`, `data`, `infra` |
| `--constraints` | No | Additional constraints to consider (e.g., "must support on-premises deployment") |
| `--format` | No | Output format: `html` (self-contained report) or `xml` (structured data, default) |
| `--json` | No | Output summary as JSON for tooling integration |

## Overview

This command analyzes the current architecture, non-functional requirements, and identified issues to generate technology stack recommendations for modernization. Each recommendation includes:

- Current technology assessment
- Proposed replacement with scored rationale
- Migration effort and risk assessment
- Alternative technologies considered
- Alignment with non-functional requirements

## Prerequisites

- Architecture extraction completed (`$EXTRACTIONS_DIR/architecture.xml`)
- Non-functional requirements extracted (`$EXTRACTIONS_DIR/non-functional.xml`) — recommended but not required
- Issues extraction completed (`$EXTRACTIONS_DIR/issues.xml`) — recommended but not required

---

## Workflow

### Step 0: Check Prerequisites

Run the prerequisites script to validate state and resolve paths:

```bash
reforge-scripts check-prerequisites --json --require-analysis --require-extraction architecture
```

This returns JSON with resolved variables:
```json
{"PROJECT_NAME":"...","REPO_ROOT":"...","PROJECT_OUTPUT_DIR":"...","CONFIG":"...","ANALYSIS_STATUS":"completed","AVAILABLE_EXTRACTIONS":[...],"CHECKPOINT":null,"CLARIFICATIONS_DIR":"..."}
```

Use `$PROJECT_OUTPUT_DIR` for all output paths in subsequent steps.

Assign subdirectory variables:
```
$EXTRACTIONS_DIR = $PROJECT_OUTPUT_DIR/extractions
$GENERATED_DIR = $PROJECT_OUTPUT_DIR/generated
```

Create the output directory if it does not exist:
```
mkdir -p $GENERATED_DIR
```

### Step 0.5: Load Project Context

If `.reforge/memory/project-context.md` exists, read it now. Use its contents as
supplemental guidance throughout this command's execution:
- **Technology Stack**: Informs current state assessment and upgrade paths
- **Domain Knowledge**: Provides business context for technology constraints
- **Analysis Guidelines**: Directs focus and exclusions beyond config.json
- **Custom Rules**: Additional rules to follow alongside the constitution

### Step 0.7: Check/Update Project Plan

If `.reforge/memory/project-plan.md` exists, read it now.

**On command start:**
- Parse the plan file to count total items and completed items
- Display: "📋 Project Plan: X/Y items complete (Z%)"
- Search for `<!-- reforge:recommend -->` tag and display its status

**On command completion (success only):**
- Locate the plan item by searching for `<!-- reforge:recommend -->`
- If found and unchecked (`- [ ]`): change to `- [x]` and append ` *(completed: YYYY-MM-DD)*`
- If found and already checked (`- [x]`): leave unchanged (idempotent)
- If tag not found: emit warning — "⚠️ No plan item found for recommend. Run /reforge.plan to add it."
- If file write fails: emit warning — "⚠️ Could not update project plan." Continue without failing.
- Update the `**Last Updated**` metadata line to today's date

If `.reforge/memory/project-plan.md` does not exist, skip this step silently.
The project plan is optional — its absence MUST NOT affect command behavior.

### Step 1: Load Architecture Data

Read `$EXTRACTIONS_DIR/architecture.xml` to identify:
- Current architectural components and their technologies
- Integration points and protocols
- Design patterns in use
- Technology stack elements (languages, frameworks, databases, middleware)

If `--focus` is specified, filter to components relevant to that domain:
- `backend`: Server-side components, APIs, services, middleware
- `frontend`: UI components, client frameworks, rendering engines
- `data`: Databases, caches, data pipelines, storage systems
- `infra`: Deployment, CI/CD, monitoring, cloud services

### Step 2: Load Non-Functional Requirements

If `$EXTRACTIONS_DIR/non-functional.xml` exists, read it to identify:
- Performance requirements (response time, throughput)
- Scalability requirements (load, concurrency)
- Security requirements (compliance, encryption)
- Maintainability requirements (code quality, documentation)
- Availability requirements (uptime, recovery)

These requirements drive technology evaluation criteria and scoring weights.

If not available, proceed with architecture data only and note the limitation in output.

### Step 3: Load Issues Data

If `$EXTRACTIONS_DIR/issues.xml` exists, read it to identify:
- Technical debt items that technology upgrades could resolve
- Deprecated API usage requiring migration
- Performance or security issues addressable through technology changes

If not available, proceed without issue context.

### Step 4: Define Evaluation Criteria

Based on project context and available data, define weighted evaluation criteria:

| Criterion | Default Weight | Description |
|-----------|---------------|-------------|
| `maturity` | 0.20 | Community adoption and ecosystem maturity |
| `migration-cost` | 0.25 | Effort and risk of migration from current stack |
| `performance` | 0.20 | Runtime performance characteristics |
| `team-skills` | 0.15 | Alignment with existing team expertise |
| `ecosystem` | 0.10 | Tooling, libraries, and community support |
| `long-term-viability` | 0.10 | Long-term maintenance and vendor stability |

Adjust weights based on non-functional requirements if available (e.g., increase `performance` weight if NFRs emphasize response time).

Apply `--constraints` if provided to further adjust criteria or eliminate candidates.

### Step 5: Evaluate and Score Technologies

For each identified technology area:

1. **Identify current technology** from architecture extraction data
2. **Determine candidate replacements** based on:
   - Modern equivalents in the same ecosystem
   - Technologies that address identified issues
   - Technologies that satisfy non-functional requirements
3. **Score each candidate** against evaluation criteria (0.0-1.0 scale)
4. **Select the highest-scoring candidate** as the primary recommendation
5. **Record runner-up candidates** as alternatives with rejection rationale

### Step 6: Generate Recommendations

For each technology area, produce a `<recommendation>` element containing:
- Current and proposed technology descriptions
- Rationale linking to specific evaluation criteria
- Migration effort assessment with estimated timeline
- Risk assessment with specific concerns and mitigations
- Alternative technologies considered
- Non-functional requirement alignment references

### Step 7: Write Output

Write the recommendations to `$GENERATED_DIR/tech-recommendation.xml` following the [tech-recommendation schema](../schemas/tech-recommendation.md).

If `--format html` is specified, also generate `$GENERATED_DIR/tech-recommendation.html` as a self-contained HTML report using the Stephen Few design system (see `.reforge/templates/html-report.md` for style patterns).

If `--json` is specified, output a JSON summary:
```json
{
  "total_recommendations": 5,
  "categories": {"language": 1, "framework": 1, "database": 1, "cloud": 1, "messaging": 1},
  "priority_distribution": {"critical": 0, "high": 2, "medium": 2, "low": 1},
  "avg_score": 0.78,
  "output_file": "generated/tech-recommendation.xml"
}
```

---

## Error Handling

| Condition | Action |
|-----------|--------|
| Architecture extraction missing | Error: "Architecture extraction required. Run `/reforge.extract architecture` first." |
| No technologies identified | Warning: "No technology patterns identified in architecture extraction. Verify extraction completeness." |
| Invalid `--focus` value | Error: "Invalid focus domain. Valid options: backend, frontend, data, infra" |
| Non-functional extraction missing | Warning: "Non-functional requirements not available. Recommendations will lack NFR alignment." Proceed. |
| Issues extraction missing | Continue without issue context. |

---

## Examples

### Basic Technology Recommendation

```
/reforge.recommend
```

Produces `generated/tech-recommendation.xml` covering all technology domains.

### Backend-Focused Recommendation

```
/reforge.recommend --focus backend --constraints "must support Kubernetes deployment"
```

Produces recommendations limited to backend technologies with Kubernetes compatibility as a constraint.

### HTML Report Output

```
/reforge.recommend --format html
```

Produces both `generated/tech-recommendation.xml` and `generated/tech-recommendation.html`.
