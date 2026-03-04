# Typical Workflow

A step-by-step guide to analyzing a legacy codebase with Reforge, from installation through documentation generation.

## Workflow Phases

The Reforge workflow has five phases:

| Phase | Steps | Purpose |
|-------|-------|---------|
| **Planning** | Plan | Define the extraction roadmap |
| **Setup** | Install, Init, Profile | Prepare the framework and project context |
| **Extraction** | Analyze, Extract, Glossary, Clarify | Inventory the codebase and extract knowledge |
| **Generation** | Generate | Produce documentation and artifacts |
| **Maintenance** | Audit, Fix, Reanalyze | Validate coverage and fill gaps |

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

#### 11. Generate documentation

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

Produces documentation from the extracted XML. See [HTML Reports](html-reports.md) for the recommended HTML format.

#### 12. Audit coverage

=== "Claude Code"

    ```
    /reforge.audit
    ```

=== "GitHub Copilot"

    ```
    @reforge.audit
    ```

Compares the analysis inventory against extraction outputs to identify coverage gaps, stale references, and missing extractions.

#### 13. Fix gaps

=== "Claude Code"

    ```
    /reforge.fix
    ```

=== "GitHub Copilot"

    ```
    @reforge.fix
    ```

Processes corrections from the audit in dependency order: re-analyze stale files first, then re-extract, then regenerate affected outputs.

#### 14. Review results

All outputs are in `reforge_output/<project-name>/`. Open the generated HTML index page for a navigable overview.

## The Audit/Fix Cycle

The audit and fix commands form an iterative quality loop:

```
/reforge.audit  -->  review gaps  -->  /reforge.fix  -->  /reforge.audit  -->  ...
```

Repeat until the audit report shows acceptable coverage for your needs. Each cycle:

1. **Audit** identifies files with no extraction references, stale references to changed files, and per-type coverage statistics
2. **Fix** dispatches corrections to the appropriate commands (`reanalyze`, `extract`, `generate`) in dependency order
3. **Re-audit** validates the fixes took effect

!!! tip
    For targeted fixes, use `--type` and `--items` flags: `/reforge.fix --type business-rules --items BR-045,BR-046`

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
