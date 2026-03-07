---
tags:
  - commands
---

# Commands

Reforge commands guide the AI agent through structured analysis workflows. Each command is a prompt template that the agent follows step-by-step using its native file tools.

## Command Syntax

Commands use a dot-prefixed notation that varies by AI agent:

=== "Claude Code"

    ```
    /reforge.<command> [arguments] [--flags]
    ```

=== "GitHub Copilot"

    ```
    @reforge.<command> [arguments] [--flags]
    ```

## Command Reference

Commands are organized by workflow phase. Run them in this order for a complete analysis.

### Planning

| Command | Description |
|---------|-------------|
| [`plan`](plan.md) | Create and manage a project plan for the extraction workflow |

### Setup

| Command | Description |
|---------|-------------|
| [`init`](init.md) | Initialize project context with domain knowledge |
| [`profile`](profile.md) | Generate language-specific and architecture-specific extraction profile |
| [`analyze`](analyze.md) | Scan and inventory a legacy codebase |

### Extraction

| Command | Description |
|---------|-------------|
| [`extract`](extract.md) | Extract business rules, database interactions, UI flows, workflows, and more |
| [`glossary`](glossary.md) | Extract, verify, and persist a glossary of acronyms and abbreviations |
| [`clarify`](clarify.md) | Interactively resolve ambiguities in extracted code elements |

### Generation

| Command | Description |
|---------|-------------|
| [`generate`](generate.md) | Generate documentation and artifacts from extracted metadata |
| [`status`](status.md) | Report analysis progress, coverage statistics, and pending items |

### Maintenance

| Command | Description |
|---------|-------------|
| [`audit`](audit.md) | Audit extraction coverage and identify gaps |
| [`fix`](fix.md) | Execute corrections from the audit correction plan |
| [`reanalyze`](reanalyze.md) | Re-process specific files without full re-analysis |

### Validation & Quality

| Command | Description |
|---------|-------------|
| [`validate`](validate.md) | Validate extraction XML for XSD conformance, ID uniqueness, and cross-reference integrity |
| [`metrics`](metrics.md) | Compute codebase metrics -- complexity, coupling, cohesion, and tech debt ratio |
| [`hotspot`](hotspot.md) | Identify high-risk modules with composite risk scoring |

### Analysis Depth

| Command | Description |
|---------|-------------|
| [`delta`](delta.md) | Git diff-based incremental extraction of changed files |
| [`dead-code`](dead-code.md) | Detect unreachable code via call-site and dependency analysis |
| [`security`](security.md) | OWASP Top 10 security scan with CWE identifiers |
| [`trace`](trace.md) | End-to-end traceability matrix across all extractions |
| [`compare`](compare.md) | Diff two extraction runs for regression detection |

### Modernization

| Command | Description |
|---------|-------------|
| [`estimate`](estimate.md) | Three-point effort estimation per module |
| [`migrate`](migrate.md) | Phased migration playbook with 5R strategy |
| [`recommend`](recommend.md) | Technology stack recommendations based on architecture analysis |

### Reporting & Integration

| Command | Description |
|---------|-------------|
| [`dashboard`](dashboard.md) | Interactive HTML dashboard of all extractions and metrics |
| [`export`](export.md) | Export to Jira CSV, Azure DevOps, Confluence, GitHub Issues |
| [`report`](report.md) | Generate milestone, status, or executive reports |

## Typical Workflow

```
 1. /reforge.plan              # Create a project plan
 2. /reforge.init              # Set project context
 3. /reforge.profile           # Generate extraction profile
 4. /reforge.analyze           # Inventory codebase
 5. /reforge.extract <type>    # Extract knowledge (repeat per type)
 6. /reforge.glossary          # Extract acronyms
 7. /reforge.clarify           # Resolve ambiguities
 8. /reforge.audit             # Check coverage
 9. /reforge.fix               # Fill gaps
10. /reforge.validate          # Validate XML structure
11. /reforge.generate <format> # Create documentation
12. /reforge.metrics           # Compute codebase metrics
13. /reforge.hotspot           # Identify risk hotspots
14. /reforge.security          # Run security scan
15. /reforge.dead-code         # Find dead code
16. /reforge.trace             # Build traceability matrix
17. /reforge.estimate          # Estimate modernization effort
18. /reforge.migrate           # Generate migration playbook
19. /reforge.recommend         # Get tech stack recommendations
20. /reforge.dashboard         # Generate interactive dashboard
21. /reforge.export <format>   # Export to project tools
22. /reforge.report            # Generate status reports
23. /reforge.status            # Review progress
```

The audit/fix/validate cycle (steps 8--10) can be repeated until comprehensive coverage is achieved. Steps 12--22 can be run in any order based on your modernization needs.
