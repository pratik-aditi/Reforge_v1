# Reforge

LLM-driven legacy codebase analysis and documentation framework.

Reforge enables AI coding agents (Claude Code, GitHub Copilot, etc.) to analyze legacy codebases and extract knowledge into structured formats — without compiled code, external parsers, or runtime dependencies.

## How It Works

Reforge is a set of prompt templates that guide an AI agent through structured analysis workflows. The agent uses its native file tools (Read, Glob, Grep, Write) to scan code, identify patterns, and produce documented outputs. No AST parsers, no language-specific tooling — just the AI reading and reasoning about your code.

The framework installs into your target project as a set of slash commands. When you run `/reforge.analyze` in Claude Code, the agent follows the command template to systematically inventory your codebase, extract business rules, map database interactions, and generate modernization documentation.

## Installation

### Prerequisites

- Python 3.11 or higher
- [uv](https://docs.astral.sh/uv/) (recommended) or pip
- An AI coding agent:
  - [Claude Code](https://docs.anthropic.com/en/docs/claude-code) — use `--claude`
  - [GitHub Copilot](https://github.com/features/copilot) in VS Code — use `--copilot`

### Quick Start

1. **Clone the repository**:

```bash
git clone https://github.com/Aditi-Consulting/reforge.git
cd reforge
```

2. **Install the CLI tool**:

```bash
uv tool install reforge-cli --from .
```

Or from a path outside the repo:

```bash
uv tool install reforge-cli --from /path/to/reforge
```

3. **Install into your target project**:

For **Claude Code**:

```bash
reforge --claude /path/to/legacy-project
```

For **GitHub Copilot** (VS Code):

```bash
reforge --copilot /path/to/legacy-project
```

You can install both on the same project — they coexist without conflict:

```bash
reforge --claude /path/to/legacy-project
reforge --copilot /path/to/legacy-project
```

4. **Start analyzing**:

In **Claude Code**, run:

```
/reforge.init      # Set up project context (recommended)
/reforge.profile   # Generate extraction profile (recommended)
/reforge.analyze   # Begin codebase analysis
```

In **GitHub Copilot Chat** (VS Code), type:

```
@reforge.init      # Set up project context (recommended)
@reforge.profile   # Generate extraction profile (recommended)
@reforge.analyze   # Begin codebase analysis
```

### CLI Reference

```
Usage: reforge [OPTIONS] [TARGET_PATH]

Commands:
  --claude              Install/set up Reforge for Claude Code
  --copilot             Install/set up Reforge for GitHub Copilot
  --remove              Remove Reforge from target project

Options:
  --update              Refresh framework files (preserves config)
  --force               Skip confirmation prompts
  --dry-run             Show what would be done
  --version             Show framework version
  --help                Show this message and exit

Arguments:
  TARGET_PATH           Target project directory (defaults to current directory)
```

`--claude` and `--copilot` are mutually exclusive per invocation but can be run separately on the same project.

| Example | What it does |
|---------|--------------|
| `reforge --claude .` | Install for Claude Code |
| `reforge --copilot .` | Install for GitHub Copilot |
| `reforge --claude /opt/legacy-app` | Install into a specific project |
| `reforge --claude --update .` | Update Claude Code framework files |
| `reforge --copilot --update .` | Update Copilot agent files |
| `reforge --copilot --dry-run .` | Preview what would be installed |
| `reforge --remove .` | Uninstall all Reforge artifacts |

### Helper Scripts CLI

The `reforge-scripts` command provides internal utilities used by prompt templates during analysis:

```
Usage: reforge-scripts [OPTIONS] COMMAND [ARGS]...

Commands:
  init-project          Initialize project output structure
  check-prerequisites   Validate prerequisites for Reforge commands
  checkpoint            Manage checkpoint state (read/create/delete)
  update-context        Update agent context file with analysis results
```

These are called automatically by the AI agent during `/reforge.*` command execution. You typically don't need to run them directly.

### Updating

To update the Reforge CLI tool itself, pull the latest and reinstall:

```bash
cd /path/to/reforge
git pull
uv tool install reforge-cli --from . --force
```

To refresh framework files in an already-installed project:

```bash
reforge --claude --update /path/to/project   # Claude Code
reforge --copilot --update /path/to/project  # GitHub Copilot
```

This refreshes commands, schemas, templates, and agent files while preserving your project-specific configuration (project name, custom exclusions, output directory).

### Uninstalling

Remove from a project:

```bash
reforge --remove /path/to/project
```

Removes all Reforge artifacts — framework files, Claude wrappers, Copilot agents/prompts, and VS Code settings entries. Your analysis output (`reforge_output/`) is preserved unless you explicitly confirm its removal.

Uninstall the CLI tool:

```bash
uv tool uninstall reforge-cli
```

## Commands

### `/reforge.init`

Initialize project context with domain knowledge. This interactive command collects information about your project that guides all subsequent analysis.

```
/reforge.init [--update]
```

Creates `.reforge/memory/project-context.md` containing:
- Project identity (name, description, root path)
- Technology stack (languages, frameworks, databases)
- Domain knowledge (business concepts, terminology)
- Analysis guidelines (focus areas, known patterns)

Run this before `/reforge.analyze` for best results.

### `/reforge.profile`

Generate a language-specific and architecture-specific extraction profile. Gathers your project's tech stack (languages, frameworks, architectural patterns) and produces tailored extraction guidance at `.reforge/memory/extraction-profile.md`.

```
/reforge.profile [--update]
```

- **Auto-discovers** languages by scanning file extensions when you don't declare them
- **Universal language support** — the LLM generates extraction rules for any language from its training knowledge (no restrictions)
- **Architecture guidance** — declare patterns (layered, microservices, event-driven, etc.) for targeted extraction
- **Custom notes** — add project-specific extraction guidance
- **Update mode** — add or remove languages without losing existing profile content

The extract command loads this profile automatically. Run before `/reforge.extract` for language-aware extraction.

### `/reforge.analyze`

Scan and inventory a legacy codebase. Detects languages, frameworks, module boundaries, and file relationships. Produces an XML inventory used by subsequent commands.

```
/reforge.analyze [path] [--resume] [--force]
```

- Supports checkpointing — interrupt and resume large analyses
- Respects exclusion patterns from `config.json`
- Skips binary files automatically

### `/reforge.extract`

Extract specific knowledge elements from the analyzed codebase.

```
/reforge.extract <type> [--files <pattern>] [--confidence <level>]
```

| Type | What it extracts |
|------|-----------------|
| `business-rules` | Business logic, validation rules, calculations with source file traceability |
| `database` | SQL queries, data models, ORM mappings, schema definitions |
| `ui` | Screen layouts, components, navigation flows, form structures |
| `workflows` | Execution paths, state machines, event handlers, process flows |

Each extraction includes confidence levels (high/medium/low) and source location references.

### `/reforge.generate`

Generate documentation and artifacts from extracted metadata.

```
/reforge.generate <format> [--output <path>] [--scope <type>]
```

| Format | Output |
|--------|--------|
| `markdown` | Comprehensive human-readable documentation |
| `user-stories` | Modernization backlog items (MD, JSON, CSV) |
| `data-dictionary` | Database entity documentation |
| `uml` | Class diagrams (PlantUML/Mermaid) |
| `sysml` | System architecture block diagrams |
| `cross-mappings` | Relationships between extraction types |
| `features` | Features and requirements derived from extractions |
| `registries` | Consolidated registries (API endpoints, events, etc.) |

### `/reforge.audit`

Audit extraction coverage and identify gaps against the analyzed codebase.

```
/reforge.audit [type] [--json]
```

Compares your analysis inventory against extraction outputs to identify:
- **Coverage gaps** — analyzed files with no extraction references
- **Stale references** — extractions pointing to changed or missing files
- **Per-type breakdown** — coverage statistics for each extraction type

Produces two outputs in `reforge_output/<project>/audit/`:
- `audit-report.xml` — Read-only diagnostic with coverage statistics
- `correction-plan.xml` — Actionable plan consumed by `/reforge.fix`

### `/reforge.fix`

Execute corrections from the audit correction plan.

```
/reforge.fix [--type <type>] [--items <ids>] [--interactive] [--resume]
```

Processes corrections in dependency order:
1. **Analysis corrections** — Re-analyze stale files first
2. **Extraction corrections** — Re-extract or fill gaps
3. **Generation corrections** — Regenerate affected outputs

Each correction dispatches to the appropriate command (`/reforge.reanalyze`, `/reforge.extract`, `/reforge.generate`). Supports checkpointing for interruption/resume.

### `/reforge.status`

Show analysis progress, coverage statistics, and pending items.

```
/reforge.status [--detailed] [--json]
```

Reports which files have been analyzed, extraction coverage, and any items needing clarification.

### `/reforge.clarify`

Interactively resolve ambiguities in extracted code elements.

```
/reforge.clarify [--id <item-id>] [--all] [--category <type>]
```

When the AI encounters unclear patterns (magic numbers, ambiguous naming, undocumented logic), it flags them for clarification. This command walks through pending items and applies your decisions consistently across the codebase.

### `/reforge.reanalyze`

Re-analyze specific files or directories without full re-processing.

```
/reforge.reanalyze <path> [--type <extraction>] [--force]
```

Use after code changes to incrementally update analysis results. Cross-references are automatically updated.

## Configuration

After installation, edit `.reforge/config.json` in your target project:

```json
{
  "project": {
    "name": "my-legacy-app",
    "root": "./",
    "description": "Legacy e-commerce platform"
  },
  "analysis": {
    "exclusions": [
      "**/node_modules/**",
      "**/vendor/**",
      "**/.git/**"
    ],
    "maxFileSize": 1048576,
    "chunkSize": 5000
  },
  "output": {
    "directory": "reforge_output"
  },
  "extraction": {
    "confidenceThreshold": "medium",
    "includeSnippets": true,
    "maxSnippetLines": 10
  }
}
```

| Field | Purpose |
|-------|---------|
| `project.name` | Identifier used in output filenames |
| `analysis.exclusions` | Glob patterns for files/directories to skip |
| `analysis.maxFileSize` | Skip files larger than this (bytes) |
| `analysis.chunkSize` | Lines per processing chunk for large files |
| `output.directory` | Where generated output goes |
| `extraction.confidenceThreshold` | Minimum confidence to include (`low`, `medium`, `high`) |
| `extraction.includeSnippets` | Include source code snippets in extractions |

## Typical Workflow

```
 1. Clone:       git clone https://github.com/Aditi-Consulting/reforge.git
 2. Install:     uv tool install reforge-cli --from /path/to/reforge
 3. Setup:       reforge --claude /path/to/project   # or --copilot
 4. Initialize:  /reforge.init                       # Set project context
 5. Profile:     /reforge.profile                    # Generate extraction profile
 6. Analyze:     /reforge.analyze                    # Inventory codebase
 7. Extract:     /reforge.extract business-rules     # Extract knowledge
                 /reforge.extract database
                 /reforge.extract ui
                 /reforge.extract workflows
 8. Clarify:     /reforge.clarify                    # Resolve ambiguities
 9. Generate:    /reforge.generate user-stories      # Create documentation
                 /reforge.generate data-dictionary
                 /reforge.generate cross-mappings
10. Audit:       /reforge.audit                      # Check coverage
11. Fix:         /reforge.fix                        # Fill gaps
12. Review:      Check reforge_output/ for results
```

The audit/fix cycle (steps 9-10) can be repeated as needed to achieve comprehensive coverage.

## What Gets Installed

Both `--claude` and `--copilot` install the shared framework files. Each mode adds its own agent integration on top.

### Shared framework (always installed)

```
.reforge/
├── commands/           # Prompt templates that define each command
├── schemas/            # XML output structure definitions
├── templates/          # Generation templates (UML, user stories, etc.)
├── memory/
│   ├── constitution.md   # Framework principles
│   ├── project-context.md # Project-specific context (from /reforge.init)
│   ├── checkpoints/      # Resume capability (gitignored)
│   ├── clarifications/   # Pending clarifications (gitignored)
│   └── logs/             # Operation logs (gitignored)
├── config.json         # Project configuration
└── .version            # Installed framework version
```

### Claude Code (`--claude`)

```
.claude/
├── commands/
│   └── reforge.*.md    # Thin wrappers that register slash commands
└── settings.local.json # Permissions for reforge-scripts CLI
```

### GitHub Copilot (`--copilot`)

```
.github/
├── agents/
│   └── reforge.*.agent.md   # Copilot Chat agent files (one per command)
└── prompts/
    └── reforge.*.prompt.md  # Copilot Chat prompt files (one per command)

.vscode/
└── settings.json            # Copilot settings (prompt recommendations, terminal auto-approve)
```

Analysis outputs go to `reforge_output/<project-name>/`:

```
reforge_output/<project-name>/
├── analysis/           # Codebase inventory (analysis.xml)
├── extractions/        # Extracted knowledge
│   ├── business-rules/
│   ├── database/
│   ├── ui-flows/
│   └── workflows/
├── derived/            # Cross-referenced artifacts
│   ├── cross-mappings/
│   ├── features-requirements/
│   └── registries/
├── generated/          # Documentation output
│   ├── markdown/
│   ├── user-stories/
│   └── data-dictionary/
├── audit/              # Audit reports and correction plans
└── diagrams/           # UML/SysML diagram sources and renders
```

Runtime state directories and `reforge_output/` are added to `.gitignore` automatically.

## Architecture

Reforge follows a zero-dependency, prompt-template architecture:

- **No parsers**: The AI agent reads source files directly — no AST, no Tree-sitter, no language plugins
- **No runtime**: Framework is pure markdown templates + configuration
- **Structured output**: Results stored as XML with defined schemas for consistency and machine-readability
- **Source traceability**: Every extracted element links back to file, line number, and code snippet
- **Checkpoint/resume**: Long analyses can be interrupted and continued
- **Agent-agnostic**: Works with any AI coding assistant that supports file operations and slash commands

## Contributing

This project uses the [SpecKit](https://github.com/github/spec-kit) workflow for development:

```
/speckit.specify    # Define feature specifications
/speckit.plan       # Create implementation plans
/speckit.tasks      # Generate task breakdowns
/speckit.implement  # Execute implementation
```

## License

See [LICENSE](LICENSE) for details.
