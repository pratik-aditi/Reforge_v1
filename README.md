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
- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) (or another AI coding agent that supports slash commands)

### Quick Start

Install Reforge CLI using `uv`:

```bash
uv tool install reforge-cli
```

Or install from git:

```bash
uv tool install git+https://github.com/your-org/reforge.git
```

Or using pip:

```bash
pip install reforge-cli
```

Then install into your target project:

```bash
reforge --claude /path/to/legacy-project
```

This copies the framework files, generates Claude Code slash command wrappers, configures permissions, and sets up `.gitignore` entries.

Open your project in Claude Code and run:

```
/reforge.analyze
```

### CLI Reference

```
Usage: reforge [OPTIONS] [TARGET_PATH]

Commands:
  --claude              Install/set up Reforge for Claude Code
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

| Example | What it does |
|---------|--------------|
| `reforge --claude .` | Install into current directory |
| `reforge --claude /opt/legacy-app` | Install into a specific project |
| `reforge --claude --update .` | Update framework files |
| `reforge --claude --dry-run .` | Preview what would be installed |
| `reforge --remove .` | Uninstall from current directory |

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

To update the Reforge CLI tool itself:

```bash
uv tool upgrade reforge-cli
```

To refresh framework files in an already-installed project:

```bash
reforge --claude --update /path/to/project
```

This refreshes commands, schemas, and templates while preserving your project-specific configuration (project name, custom exclusions, output directory).

### Uninstalling

Remove from a project:

```bash
reforge --remove /path/to/project
```

Removes all framework files and configuration. Your analysis output (`reforge_output/`) is preserved unless you explicitly confirm its removal.

Uninstall the CLI tool:

```bash
uv tool uninstall reforge-cli
```

## Commands

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
1. Install:     uv tool install reforge-cli
2. Setup:       reforge --claude /path/to/project
3. Configure:   Edit .reforge/config.json (project name, exclusions)
4. Analyze:     /reforge.analyze
5. Extract:     /reforge.extract business-rules
                /reforge.extract database
                /reforge.extract ui
                /reforge.extract workflows
6. Clarify:     /reforge.clarify (resolve ambiguities)
7. Generate:    /reforge.generate user-stories
                /reforge.generate data-dictionary
                /reforge.generate uml
8. Review:      Check reforge_output/ for results
```

## What Gets Installed

When you run `reforge --claude`, the following is added to your project:

```
.reforge/
├── commands/           # Prompt templates that define each command
├── schemas/            # XML output structure definitions
├── templates/          # Generation templates (UML, user stories, etc.)
├── memory/
│   ├── constitution.md # Framework principles
│   ├── analysis/       # Analysis state
│   ├── checkpoints/    # Resume capability (gitignored)
│   ├── clarifications/ # Pending clarifications (gitignored)
│   └── logs/           # Operation logs (gitignored)
├── config.json         # Project configuration
└── .version            # Installed framework version

.claude/
├── commands/
│   └── reforge.*.md    # Thin wrappers that register slash commands
└── settings.local.json # Permissions for reforge-scripts CLI
```

Runtime state directories (`checkpoints/`, `clarifications/`, `logs/`) and `reforge_output/` are added to `.gitignore` automatically.

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
