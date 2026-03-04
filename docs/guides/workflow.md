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

  P --> I
  A --> E
  CL --> AU
  FX -.-> E
  AU --> GEN

  style Planning fill:#fef3c7,stroke:#f59e0b,color:#1a1a2e
  style Setup fill:#e0e7ff,stroke:#6366f1,color:#1a1a2e
  style Extraction fill:#ede9fe,stroke:#8b5cf6,color:#1a1a2e
  style Validation fill:#fce7f3,stroke:#ec4899,color:#1a1a2e
  style Generation fill:#d1fae5,stroke:#10b981,color:#1a1a2e
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
