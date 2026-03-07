---
tags:
  - guides
  - workflow
---

# Typical Workflow

A step-by-step guide to analyzing a legacy codebase with Reforge, from installation through documentation generation.

## Workflow Overview

```mermaid
graph TD
  subgraph Planning
    P["/reforge.plan"]
  end

  subgraph Setup
    I["/reforge.init"] --> PR["/reforge.profile"]
    PR --> A["/reforge.analyze"]
  end

  subgraph Extraction
    E["/reforge.extract"] --> G["/reforge.glossary"]
    G --> CL["/reforge.clarify"]
  end

  subgraph Validation
    AU["/reforge.audit"] --> FX["/reforge.fix"]
    FX --> RA["/reforge.reanalyze"]
    RA -.-> AU
  end

  subgraph Generation
    GEN["/reforge.generate"]
  end

  subgraph "Validation & Quality"
    VAL["/reforge.validate"] --> MET["/reforge.metrics"]
    MET --> HOT["/reforge.hotspot"]
  end

  subgraph "Deep Analysis"
    SEC["/reforge.security"]
    DC["/reforge.dead-code"]
    TR["/reforge.trace"]
  end

  subgraph Modernization
    EST["/reforge.estimate"] --> MIG["/reforge.migrate"]
    MIG --> REC["/reforge.recommend"]
  end

  subgraph Reporting
    DASH["/reforge.dashboard"]
    REP["/reforge.report"]
    EXP["/reforge.export"]
  end

  P --> I
  A --> E
  CL --> AU
  FX -.-> E
  AU --> GEN
  GEN --> VAL
  VAL -.-> SEC
  VAL -.-> DC
  VAL -.-> TR
  HOT --> EST
  MIG --> DASH
  MIG --> REP
  MIG --> EXP

  style Planning fill:#fff3d6,stroke:#FFA301,color:#00203A
  style Setup fill:#d6f0f7,stroke:#1FB3D9,color:#00203A
  style Extraction fill:#cce7f0,stroke:#1FB3D9,color:#00203A
  style Validation fill:#e8f4f8,stroke:#00203A,color:#00203A
  style Generation fill:#fff3d6,stroke:#FFA301,color:#00203A
  style "Validation & Quality" fill:#e8f4f8,stroke:#00203A,color:#00203A
  style "Deep Analysis" fill:#d6f0f7,stroke:#1FB3D9,color:#00203A
  style Modernization fill:#fff3d6,stroke:#FFA301,color:#00203A
  style Reporting fill:#cce7f0,stroke:#1FB3D9,color:#00203A
```

## Workflow Phases

The Reforge workflow has five phases:

| Phase | Steps | Purpose |
|-------|-------|---------|
| **Planning** | Plan | Define the extraction roadmap |
| **Setup** | Install, Init, Profile | Prepare the framework and project context |
| **Extraction** | Analyze, Extract, Glossary, Clarify | Inventory the codebase and extract knowledge |
| **Validation** | Audit, Fix, Reanalyze | Validate coverage and fill gaps iteratively |
| **Generation** | Generate | Produce documentation and artifacts from validated extractions |
| **Validation & Quality** | Validate, Metrics, Hotspot | Ensure extraction integrity and compute codebase metrics |
| **Deep Analysis** | Security, Dead-code, Trace, Delta | Build comprehensive codebase understanding |
| **Modernization** | Estimate, Migrate, Recommend | Plan the migration effort with data-driven estimates |
| **Reporting** | Dashboard, Report, Export, Compare | Generate reports and export to external tools |

## Step-by-Step Walkthrough

### Terminal Steps (1-2)

Steps 1 and 2 run in your **terminal** -- they are standard shell commands, not agent commands.

#### 1. Install the CLI tool

No cloning required -- install directly from GitHub:

```bash
uv tool install reforge-cli --from git+https://github.com/Aditi-Consulting/reforge.git
```

#### 2. Install into your target project

=== "Claude Code"

    ```bash
    reforge --claude /path/to/legacy-project
    ```

=== "GitHub Copilot"

    ```bash
    reforge --copilot /path/to/legacy-project
    ```

This copies the framework files (`.reforge/`) and registers the slash commands for your agent.

### Agent Steps (4+)

From this point on, all commands are **agent commands**. Run them inside your AI coding agent, not in a terminal.

#### 4. Create a project plan (optional)

=== "Claude Code"

    ```
    /reforge.plan
    ```

=== "GitHub Copilot"

    ```
    @reforge.plan
    ```

Generates a structured plan at `.reforge/memory/project-plan.md` that tracks progress across all subsequent steps. The plan is optional but recommended for large projects.

#### 5. Initialize project context

=== "Claude Code"

    ```
    /reforge.init
    ```

=== "GitHub Copilot"

    ```
    @reforge.init
    ```

An interactive step where you provide project metadata: name, description, tech stack, domain terminology, and analysis guidelines. This context improves extraction accuracy across all subsequent commands.

#### 6. Generate extraction profile

=== "Claude Code"

    ```
    /reforge.profile
    ```

=== "GitHub Copilot"

    ```
    @reforge.profile
    ```

Scans your project for languages and frameworks, then produces tailored extraction guidance at `.reforge/memory/extraction-profile.md`. The extract command loads this profile automatically.

#### 7. Analyze the codebase

=== "Claude Code"

    ```
    /reforge.analyze
    ```

=== "GitHub Copilot"

    ```
    @reforge.analyze
    ```

Inventories every source file -- detecting languages, frameworks, module boundaries, and file relationships. Produces `analysis.xml`, which all subsequent commands depend on.

!!! tip "Large codebases"
    Analysis supports checkpointing. If interrupted, resume with `/reforge.analyze --resume`.

#### 8. Extract knowledge

Run extractions for each type relevant to your project:

=== "Claude Code"

    ```
    /reforge.extract business-rules
    /reforge.extract database
    /reforge.extract ui
    /reforge.extract workflows
    /reforge.extract call-sites
    /reforge.extract dependencies
    /reforge.extract functional-requirements
    /reforge.extract non-functional
    /reforge.extract architecture
    /reforge.extract issues
    ```

=== "GitHub Copilot"

    ```
    @reforge.extract business-rules
    @reforge.extract database
    @reforge.extract ui
    @reforge.extract workflows
    @reforge.extract call-sites
    @reforge.extract dependencies
    @reforge.extract functional-requirements
    @reforge.extract non-functional
    @reforge.extract architecture
    @reforge.extract issues
    ```

Each extraction reads the source files identified during analysis and produces structured XML output. See [Extraction Types](extraction-types.md) for details on each type.

!!! note
    You do not need to run all 10 types. Choose the ones relevant to your modernization goals. The four core types (`business-rules`, `database`, `ui`, `workflows`) cover most use cases.

#### 9. Extract glossary (optional)

=== "Claude Code"

    ```
    /reforge.glossary
    ```

=== "GitHub Copilot"

    ```
    @reforge.glossary
    ```

Extracts acronyms and abbreviations from the codebase through a 4-phase pipeline (pattern extraction, external verification, source code audit, self-audit). The glossary is used by all other commands for acronym expansion.

#### 10. Resolve ambiguities

=== "Claude Code"

    ```
    /reforge.clarify
    ```

=== "GitHub Copilot"

    ```
    @reforge.clarify
    ```

Walks through items the agent flagged as unclear (magic numbers, ambiguous naming, undocumented logic) and applies your decisions consistently.

#### 11. Audit coverage

=== "Claude Code"

    ```
    /reforge.audit
    ```

=== "GitHub Copilot"

    ```
    @reforge.audit
    ```

Compares the analysis inventory against extraction outputs to identify coverage gaps, stale references, and missing extractions. Run this **before** generating documentation to ensure your extractions are complete.

#### 12. Fix gaps

=== "Claude Code"

    ```
    /reforge.fix
    ```

=== "GitHub Copilot"

    ```
    @reforge.fix
    ```

Processes corrections from the audit in dependency order: re-analyze stale files first, then re-extract affected types. Repeat the audit/fix cycle until coverage meets your threshold.

!!! tip
    For targeted fixes, use `--type` and `--items` flags: `/reforge.fix --type business-rules --items BR-045,BR-046`

#### 13. Generate documentation

=== "Claude Code"

    ```
    /reforge.generate html
    /reforge.generate user-stories
    /reforge.generate data-dictionary
    /reforge.generate cross-mappings
    ```

=== "GitHub Copilot"

    ```
    @reforge.generate html
    @reforge.generate user-stories
    @reforge.generate data-dictionary
    @reforge.generate cross-mappings
    ```

Produces documentation from the validated extraction XML. Generation runs **after** the audit/fix cycle so that all outputs reflect complete, verified extractions. See [HTML Reports](html-reports.md) for the recommended HTML format.

#### 14. Review results

All outputs are in `reforge_output/<project-name>/`. Open the generated HTML index page for a navigable overview.

## The Audit/Fix Cycle

The audit and fix commands form an iterative quality loop that runs **before** documentation generation:

```
/reforge.extract  -->  /reforge.audit  -->  /reforge.fix  -->  /reforge.audit  -->  ...  -->  /reforge.generate
```

Repeat until the audit report shows acceptable coverage for your needs. Each cycle:

1. **Audit** identifies files with no extraction references, stale references to changed files, and per-type coverage statistics
2. **Fix** dispatches corrections to the appropriate commands (`reanalyze`, `extract`) in dependency order
3. **Re-audit** validates the fixes took effect

Once coverage is satisfactory, proceed to `/reforge.generate` to produce documentation from the validated extractions.

## Validation & Quality

After the audit/fix cycle, validate your extraction files and compute codebase metrics:

=== "Claude Code"

    ```
    /reforge.validate
    /reforge.metrics
    /reforge.hotspot
    ```

=== "GitHub Copilot"

    ```
    @reforge.validate
    @reforge.metrics
    @reforge.hotspot
    ```

- **Validate** checks all extraction XML for structural integrity (XSD conformance, ID uniqueness, cross-references)
- **Metrics** computes complexity, coupling, cohesion, and tech debt ratio per module
- **Hotspot** produces a risk heatmap ranking modules by composite risk score

## Deep Analysis

Run additional analysis commands to build a comprehensive understanding of the codebase:

=== "Claude Code"

    ```
    /reforge.security
    /reforge.dead-code
    /reforge.trace
    /reforge.delta --since <commit>
    ```

=== "GitHub Copilot"

    ```
    @reforge.security
    @reforge.dead-code
    @reforge.trace
    @reforge.delta --since <commit>
    ```

- **Security** scans for OWASP Top 10 vulnerabilities with CWE identifiers
- **Dead-code** identifies unreachable methods, classes, and files via call-site analysis
- **Trace** builds end-to-end traceability chains (requirement → rule → code → UI → story)
- **Delta** incrementally re-extracts only files changed since a given commit or date

## Modernization Planning

Use extraction data to plan the modernization effort:

=== "Claude Code"

    ```
    /reforge.estimate
    /reforge.migrate
    /reforge.recommend
    ```

=== "GitHub Copilot"

    ```
    @reforge.estimate
    @reforge.migrate
    @reforge.recommend
    ```

- **Estimate** generates three-point (PERT) effort estimates per module with complexity multipliers
- **Migrate** creates a phased migration playbook using 5R strategy (Rehost, Replatform, Refactor, Rearchitect, Retire)
- **Recommend** provides scored technology stack recommendations based on architecture and requirements

## Reporting & Integration

Generate reports and export to external tools:

=== "Claude Code"

    ```
    /reforge.dashboard
    /reforge.report --type executive
    /reforge.export jira-csv
    /reforge.compare baseline.xml current.xml
    ```

=== "GitHub Copilot"

    ```
    @reforge.dashboard
    @reforge.report --type executive
    @reforge.export jira-csv
    @reforge.compare baseline.xml current.xml
    ```

- **Dashboard** generates an interactive HTML dashboard summarizing all extractions
- **Report** produces milestone, status, or executive reports
- **Export** transforms artifacts into Jira CSV, Azure DevOps, Confluence, or GitHub Issues format
- **Compare** diffs two extraction runs to detect regressions

## Tips for Large Codebases

### Use exclusion patterns

Edit `.reforge/config.json` to skip directories that add noise without value:

```json
{
  "analysis": {
    "exclusions": [
      "**/node_modules/**",
      "**/vendor/**",
      "**/dist/**",
      "**/build/**",
      "**/*.min.js",
      "**/__pycache__/**",
      "**/test-fixtures/**"
    ]
  }
}
```

### Reduce chunk size for very large files

If analysis hangs on large files, reduce the chunk size:

```json
{
  "analysis": {
    "chunkSize": 2000
  }
}
```

### Use incremental reanalysis

After code changes, update specific files without re-running the full analysis:

=== "Claude Code"

    ```
    /reforge.reanalyze src/services/
    ```

=== "GitHub Copilot"

    ```
    @reforge.reanalyze src/services/
    ```

### Scope extractions to specific files

Focus extraction on a subset of the codebase:

=== "Claude Code"

    ```
    /reforge.extract business-rules --files "src/domain/**"
    ```

=== "GitHub Copilot"

    ```
    @reforge.extract business-rules --files "src/domain/**"
    ```

### Run init and profile first

Providing project context (`/reforge.init`) and generating an extraction profile (`/reforge.profile`) significantly improves extraction accuracy, especially for large codebases with domain-specific terminology.
