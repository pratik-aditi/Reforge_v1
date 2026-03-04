# Agent Setup

When you run `reforge --claude` or `reforge --copilot`, the CLI installs framework files into your target project. This page explains exactly what gets created for each agent.

## Shared Framework Files

Both `--claude` and `--copilot` install the core `.reforge/` directory:

```
.reforge/
├── commands/           # Prompt templates that define each /reforge.* command
├── schemas/            # XML output structure definitions
├── templates/          # Generation templates (UML, user stories, HTML, etc.)
├── scripts/            # Helper scripts called by the agent during execution
├── memory/
│   ├── constitution.md   # Framework governing principles
│   ├── project-context.md # Created by /reforge.init
│   ├── checkpoints/      # Resume state (gitignored)
│   ├── clarifications/   # Pending clarifications (gitignored)
│   └── logs/             # Operation logs (gitignored)
├── config.json         # Project configuration
└── .version            # Installed framework version
```

The `commands/` directory contains the prompt templates that drive every Reforge command. These are markdown files that instruct the AI agent on what to do, what to read, and how to structure output.

## Claude Code Files

The `--claude` flag adds thin wrapper files that register slash commands in Claude Code:

```
.claude/
├── commands/
│   ├── reforge.init.md
│   ├── reforge.profile.md
│   ├── reforge.analyze.md
│   ├── reforge.extract.md
│   ├── reforge.generate.md
│   ├── reforge.audit.md
│   ├── reforge.fix.md
│   ├── reforge.status.md
│   ├── reforge.clarify.md
│   ├── reforge.reanalyze.md
│   ├── reforge.glossary.md
│   └── reforge.plan.md
└── settings.local.json  # Permissions for reforge-scripts CLI
```

Each `.claude/commands/reforge.*.md` file is a short wrapper that loads the corresponding `.reforge/commands/` template. The `settings.local.json` file grants the agent permission to run `reforge-scripts` helper commands.

## GitHub Copilot Files

The `--copilot` flag creates agent and prompt files for VS Code Copilot Chat:

```
.github/
├── agents/
│   ├── reforge.init.agent.md
│   ├── reforge.profile.agent.md
│   ├── reforge.analyze.agent.md
│   ├── reforge.extract.agent.md
│   ├── reforge.generate.agent.md
│   ├── reforge.audit.agent.md
│   ├── reforge.fix.agent.md
│   ├── reforge.status.agent.md
│   ├── reforge.clarify.agent.md
│   ├── reforge.reanalyze.agent.md
│   ├── reforge.glossary.agent.md
│   └── reforge.plan.agent.md
└── prompts/
    └── reforge.*.prompt.md   # One prompt file per command

.vscode/
└── settings.json             # Copilot prompt recommendations, terminal auto-approve
```

In Copilot Chat, commands are invoked with `@` instead of `/` (e.g., `@reforge.analyze`).

## Output Directory

All analysis and extraction results are written to `reforge_output/<project-name>/`:

```
reforge_output/<project-name>/
├── analysis/           # Codebase inventory (analysis.xml)
├── extractions/        # Extracted knowledge (one XML file per type)
│   ├── business-rules.xml
│   ├── database.xml
│   ├── ui-flows.xml
│   ├── workflows.xml
│   ├── call-sites.xml
│   ├── dependencies.xml
│   ├── functional-requirements.xml
│   ├── non-functional-requirements.xml
│   ├── architecture.xml
│   └── issues.xml
├── derived/            # Cross-referenced artifacts
│   ├── cross-mappings/
│   ├── features-requirements/
│   └── registries/
├── generated/          # Documentation output (markdown, HTML, user stories)
├── audit/              # Audit reports and correction plans
└── diagrams/           # UML/SysML diagram sources and rendered output
```

!!! note "Git-ignored paths"
    The installer automatically adds these entries to your project's `.gitignore`:

    - `reforge_output/` -- analysis results (often large, regeneratable)
    - `.reforge/memory/checkpoints/` -- resume state
    - `.reforge/memory/clarifications/` -- pending clarification items
    - `.reforge/memory/logs/` -- operation logs

    The framework files (`.reforge/commands/`, `.reforge/schemas/`, etc.) are **not** gitignored -- commit them so your team shares the same analysis configuration.

!!! warning
    Running `reforge --remove` deletes the `.reforge/` directory and agent-specific files. The `reforge_output/` directory is preserved unless you explicitly confirm its removal during the uninstall process.
