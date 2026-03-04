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

## Typical Workflow

```
 1. /reforge.plan              # Create a project plan
 2. /reforge.init              # Set project context
 3. /reforge.profile           # Generate extraction profile
 4. /reforge.analyze           # Inventory codebase
 5. /reforge.extract <type>    # Extract knowledge (repeat per type)
 6. /reforge.glossary          # Extract acronyms
 7. /reforge.clarify           # Resolve ambiguities
 8. /reforge.generate <format> # Create documentation
 9. /reforge.audit             # Check coverage
10. /reforge.fix               # Fill gaps
11. /reforge.status            # Review progress
```

The audit/fix cycle (steps 9--10) can be repeated until comprehensive coverage is achieved.
