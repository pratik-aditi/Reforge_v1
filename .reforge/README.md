# Reforge Framework

> **LLM-driven legacy codebase analysis and documentation**

Reforge enables AI agents (Claude Code, GitHub Copilot, etc.) to analyze legacy codebases and extract knowledge into structured formats — without any compiled code or external parsers.

## Overview

Reforge follows the **LLM-First Architecture** principle: all analysis is performed by the AI agent using its native capabilities (Read, Write, Glob, Grep). The framework consists entirely of:

- **Prompt template commands** (markdown files in `commands/`)
- **Output schemas** (documentation in `schemas/`)
- **Generation templates** (in `templates/`)
- **Configuration** (`config.json`)

## Quick Start

### 1. Analyze Your Codebase

```
/reforge.analyze
```

This scans all files, detects languages and frameworks, identifies module boundaries, and produces an XML inventory.

### 2. Extract Knowledge

```
/reforge.extract business-rules    # Extract business logic with traceability
/reforge.extract database          # Extract SQL and data model
/reforge.extract ui                # Extract UI components and layouts
/reforge.extract workflows         # Trace execution paths
```

### 3. Generate Documentation

```
/reforge.generate markdown         # Comprehensive documentation
/reforge.generate user-stories     # Modernization backlog items
/reforge.generate data-dictionary  # Database documentation
/reforge.generate uml              # Class diagrams (PlantUML/Mermaid)
```

### 4. Track Progress

```
/reforge.status                    # View analysis progress and coverage
/reforge.clarify                   # Resolve ambiguous extractions
/reforge.reanalyze src/file.java   # Incrementally re-analyze files
```

## Command Reference

| Command | Description |
|---------|-------------|
| `/reforge.analyze [path]` | Scan and inventory legacy codebase |
| `/reforge.extract <type>` | Extract specific elements (business-rules, database, ui, workflows) |
| `/reforge.generate <format>` | Generate documentation (markdown, user-stories, data-dictionary, uml, sysml) |
| `/reforge.status` | Show analysis progress and coverage statistics |
| `/reforge.clarify` | Interactively resolve ambiguous code patterns |
| `/reforge.reanalyze <path>` | Re-analyze specific files without full re-processing |

## Directory Structure

```
.reforge/
├── commands/           # Slash command prompt templates
│   ├── analyze.md      # /reforge.analyze
│   ├── extract.md      # /reforge.extract
│   ├── generate.md     # /reforge.generate
│   ├── status.md       # /reforge.status
│   ├── clarify.md      # /reforge.clarify
│   └── reanalyze.md    # /reforge.reanalyze
├── schemas/            # Output structure documentation
│   ├── analysis.md     # analysis.xml schema
│   ├── business-rules.md
│   ├── database.md
│   ├── ui-flows.md
│   ├── workflows.md
│   └── user-stories.md
├── templates/          # Generation templates
│   ├── user-story.md
│   ├── data-dictionary.md
│   ├── uml-class.md
│   ├── sysml-block.md
│   └── ascii-layout.md
├── memory/             # Runtime state
│   ├── constitution.md # Framework principles
│   ├── analysis/       # Analysis outputs
│   ├── checkpoints/    # Resume capability
│   ├── clarifications/ # Pending clarifications
│   └── logs/           # Operation logs
└── config.json         # Framework configuration

reforge_output/         # Generated analysis and documentation
└── <project-name>/
    ├── analysis.xml        # Codebase inventory
    ├── business-rules.xml  # Extracted business rules
    ├── database.xml        # Database interactions
    ├── ui-flows.xml        # UI components
    ├── workflows.xml       # Process flows
    ├── user-stories.xml    # Generated user stories
    └── generated/          # Documentation outputs
        ├── documentation.md
        ├── user-stories.md
        ├── user-stories.json
        ├── data-dictionary.md
        └── diagrams/
```

## Configuration

Edit `.reforge/config.json` to customize:

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
    "binaryExtensions": [".png", ".jpg", ".pdf"],
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

## Output Formats

### Analysis Output (analysis.xml)

Contains complete codebase inventory:
- File listings with language detection
- Component mappings (classes, methods, imports)
- Framework detection
- Summary statistics

### Extraction Outputs

| File | Contents |
|------|----------|
| `business-rules.xml` | Business logic with source traceability |
| `database.xml` | Data model and SQL interactions |
| `ui-flows.xml` | Screen definitions and navigation |
| `workflows.xml` | Execution paths and process flows |

### Generated Documentation

| Format | Description |
|--------|-------------|
| `markdown` | Comprehensive human-readable documentation |
| `user-stories` | Modernization backlog (MD/JSON/CSV) |
| `data-dictionary` | Database entity documentation |
| `uml` | PlantUML/Mermaid class diagrams |
| `sysml` | System architecture block diagrams |

## Confidence Levels

Extractions include confidence indicators:

| Level | Meaning | Action |
|-------|---------|--------|
| **High** | Clear pattern, strong evidence | Ready for use |
| **Medium** | Pattern identified, some ambiguity | Review recommended |
| **Low** | Unclear, may need clarification | Run `/reforge.clarify` |

## Resume Capability

Analysis can be interrupted and resumed:

1. Progress is saved to `.reforge/memory/checkpoints/`
2. Running `/reforge.analyze` detects existing checkpoint
3. Choose to resume or start fresh
4. `/reforge.status` shows current progress

## Troubleshooting

### Analysis taking too long?

- Check exclusion patterns to skip unnecessary files
- Large files are processed in chunks automatically
- Use `/reforge.status` to monitor progress

### Low confidence extractions?

- Run `/reforge.clarify` to resolve ambiguities
- Provide context for magic numbers and unclear patterns
- Decisions are applied consistently across codebase

### Need to update after code changes?

- Use `/reforge.reanalyze <path>` for specific files
- Only changed files are re-processed
- Cross-references are automatically updated

### Output too large?

- Outputs are structured with indices
- Use `--scope` flag to limit extraction types
- Generated documentation includes table of contents

## Principles

Reforge follows these core principles (see `memory/constitution.md`):

1. **LLM-First**: All analysis by AI agent native tools
2. **Prompt Templates**: Commands as markdown files
3. **Structured Output**: XML with defined schemas
4. **Zero Dependencies**: No runtime required
5. **Agent-Agnostic**: Works with any capable AI assistant
6. **Extensibility**: Optional tooling layer for enhancements

## Related Documentation

- [Constitution](memory/constitution.md) — Framework principles
- [Quickstart Guide](../specs/001-legacy-analyzer/quickstart.md) — Detailed usage guide
- Schema documentation in `schemas/` directory
- Templates in `templates/` directory

---

**Version**: 1.0.0 | **Framework**: Reforge | **Pattern**: SpecKit
