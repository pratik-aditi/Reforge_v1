# Quick Start

A 5-minute walkthrough from installation to your first generated documentation.

!!! note
    Steps 1-2 run in your **terminal**. Steps 3-7 are **agent commands** -- run them inside Claude Code or Copilot Chat, not in the terminal.

## 1. Install Reforge into your project

=== "Claude Code"

    ```bash
    reforge --claude /path/to/legacy-project
    ```

=== "GitHub Copilot"

    ```bash
    reforge --copilot /path/to/legacy-project
    ```

## 2. Open the project in your agent

=== "Claude Code"

    ```bash
    cd /path/to/legacy-project
    claude
    ```

=== "GitHub Copilot"

    Open the project folder in VS Code and launch Copilot Chat.

## 3. Initialize project context

=== "Claude Code"

    ```
    /reforge.init
    ```

=== "GitHub Copilot"

    ```
    @reforge.init
    ```

The agent asks about your project name, tech stack, and domain concepts. This context improves all subsequent analysis.

## 4. Generate an extraction profile

=== "Claude Code"

    ```
    /reforge.profile
    ```

=== "GitHub Copilot"

    ```
    @reforge.profile
    ```

Auto-discovers languages in your project and produces tailored extraction rules at `.reforge/memory/extraction-profile.md`.

## 5. Analyze the codebase

=== "Claude Code"

    ```
    /reforge.analyze
    ```

=== "GitHub Copilot"

    ```
    @reforge.analyze
    ```

The agent scans your codebase, inventories files, detects frameworks, and maps module boundaries. Results are saved to `reforge_output/<project>/analysis/analysis.xml`.

!!! tip
    Large codebases support checkpoint/resume. If the analysis is interrupted, re-run the same command with `--resume` to continue where it left off.

## 6. Extract business rules

=== "Claude Code"

    ```
    /reforge.extract business-rules
    ```

=== "GitHub Copilot"

    ```
    @reforge.extract business-rules
    ```

The agent reads through analyzed files, identifies business logic, validation rules, and calculations, then writes structured XML to `reforge_output/<project>/extractions/business-rules.xml`. Each extraction includes confidence levels and source file references.

## 7. Generate HTML documentation

=== "Claude Code"

    ```
    /reforge.generate html
    ```

=== "GitHub Copilot"

    ```
    @reforge.generate html
    ```

Produces self-contained HTML reports from your extractions with inline diagrams and cross-document navigation.

## 8. Review the output

Check the `reforge_output/` directory in your project:

```
reforge_output/<project-name>/
├── analysis/           # Codebase inventory
├── extractions/        # Extracted knowledge (XML)
└── generated/          # Documentation output
```

## Next Steps

- Run additional extraction types: `database`, `ui`, `workflows`, `call-sites`, `dependencies`, `functional-requirements`, `non-functional`, `architecture`, `issues`
- Run `/reforge.audit` to check coverage and `/reforge.fix` to fill gaps
- See the [Commands](../commands/index.md) reference for the full list of options
- Read the [Typical Workflow](../guides/workflow.md) guide for the complete end-to-end process
