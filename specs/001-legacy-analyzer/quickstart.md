# Quickstart: Reforge Legacy Analyzer Framework

**Branch**: `001-legacy-analyzer` | **Date**: 2025-01-13

## Overview

Reforge is an LLM-driven framework for analyzing legacy codebases. It helps modernization teams inventory, understand, and document existing applications—all without external dependencies or compiled code.

## Prerequisites

- An AI coding assistant with file read/write capabilities (Claude Code, GitHub Copilot, Cursor, etc.)
- Access to the legacy codebase via file system
- The Reforge framework installed in your project

## Installation

```bash
# Using Specify CLI (recommended)
specify init <project-path> --template reforge

# Or manually copy the .reforge directory
cp -r /path/to/reforge-template/.reforge <project-path>/
```

## Directory Structure After Installation

```
your-project/
├── .reforge/
│   ├── commands/        # Slash command templates
│   ├── schemas/         # XML schema documentation
│   ├── templates/       # Output templates
│   ├── memory/          # State and checkpoints
│   └── config.json      # Configuration
└── reforge_output/      # Generated outputs (created on first run)
```

## Quick Start Workflow

### Step 1: Configure Your Project

Edit `.reforge/config.json` to set your project name and exclusion patterns:

```json
{
  "project": {
    "name": "my-legacy-app",
    "root": "./src"
  },
  "exclusions": [
    "**/node_modules/**",
    "**/vendor/**",
    "**/generated/**",
    "**/*.min.js"
  ]
}
```

### Step 2: Analyze the Codebase

Run the analyze command to inventory all files:

```
/reforge.analyze
```

This produces `reforge_output/<project>/analysis.xml` with:
- Complete file inventory
- Language detection
- Component identification
- Module boundaries

### Step 3: Extract Knowledge

Extract specific types of information:

```
/reforge.extract business-rules
/reforge.extract database
/reforge.extract ui
/reforge.extract workflows
```

Each extraction creates an XML file with:
- Extracted elements with descriptions
- Source file and line number references
- Confidence levels (high/medium/low)
- Related entity mappings

### Step 4: Check Progress

Monitor analysis progress and coverage:

```
/reforge.status
```

Shows:
- Percentage complete
- Files analyzed vs. pending
- Extraction status by type
- Items needing clarification

### Step 5: Resolve Ambiguities

Handle unclear code elements interactively:

```
/reforge.clarify
```

The system presents ambiguous items and records your decisions for consistent application.

### Step 6: Generate Documentation

Create documentation from extracted metadata:

```
/reforge.generate markdown          # Comprehensive docs
/reforge.generate user-stories      # Modernization backlog
/reforge.generate data-dictionary   # Data model reference
/reforge.generate uml               # UML class diagrams
```

Outputs go to `reforge_output/<project>/generated/`.

## Command Reference

| Command | Purpose | Output |
|---------|---------|--------|
| `/reforge.analyze` | Inventory codebase | `analysis.xml` |
| `/reforge.extract [type]` | Extract specific elements | `<type>.xml` |
| `/reforge.generate [format]` | Generate documentation | `generated/<format>.*` |
| `/reforge.clarify` | Resolve ambiguities | Updates clarifications |
| `/reforge.status` | Show progress | Console output |
| `/reforge.reanalyze [path]` | Re-process specific files | Updates existing XML |

### Extraction Types

- `business-rules` - Conditional logic, validations, calculations
- `database` - SQL statements, data model, relationships
- `ui` - Screens, components, layouts, event handlers
- `workflows` - Execution paths, process flows

### Generation Formats

- `markdown` - Human-readable documentation
- `user-stories` - Modernization backlog (MD + JSON/CSV)
- `data-dictionary` - Entity and column reference
- `uml` - Class diagram notation
- `sysml` - System model notation

## Example Session

```
> /reforge.analyze
Analyzing codebase at ./src...
✓ Found 847 source files across 12 modules
✓ Languages: Java (523), JavaScript (189), SQL (98), JSP (37)
✓ Analysis saved to reforge_output/my-legacy-app/analysis.xml

> /reforge.extract business-rules
Extracting business rules...
✓ Found 156 business rules across 89 files
✓ Confidence: 78 high, 52 medium, 26 low
✓ Saved to reforge_output/my-legacy-app/business-rules.xml

> /reforge.extract database
Extracting database interactions...
✓ Found 234 SQL statements
✓ Inferred 45 entities with 312 columns
✓ Saved to reforge_output/my-legacy-app/database.xml

> /reforge.status
Project: my-legacy-app
Progress: 100% (847/847 files)
Extractions:
  ✓ analysis: complete
  ✓ business-rules: 156 items
  ✓ database: 234 interactions, 45 entities
  ○ ui: not started
  ○ workflows: not started
Clarifications: 12 pending

> /reforge.generate user-stories
Generating user stories from extracted metadata...
✓ Created 23 epics and 89 stories
✓ Saved to:
  - reforge_output/my-legacy-app/generated/user-stories.md
  - reforge_output/my-legacy-app/generated/user-stories.json
```

## Resuming Interrupted Analysis

If analysis is interrupted, simply run the command again:

```
> /reforge.analyze
Found checkpoint from 2025-01-13T10:30:00Z
Progress: 450/847 files (53%)
Resume from checkpoint? [Y/n]
```

The system automatically detects checkpoints and offers to resume.

## Best Practices

1. **Start with `/reforge.analyze`** - Always begin with a full inventory
2. **Extract incrementally** - Run extractions one type at a time
3. **Review low-confidence items** - Use `/reforge.clarify` regularly
4. **Re-analyze changed files** - Use `/reforge.reanalyze [path]` after updates
5. **Generate docs last** - Ensure extractions are complete before generating

## Troubleshooting

### "File too large to analyze"
Large files are processed in chunks. Check the analysis log in `.reforge/memory/logs/` for details.

### "Confidence levels seem low"
Low confidence often indicates:
- Obfuscated or minified code
- Unconventional coding patterns
- Missing context (run more extractions)

Use `/reforge.clarify` to manually verify and improve confidence.

### "Missing extractions in documentation"
Ensure all extraction types are complete before generating documentation. Run `/reforge.status` to check.

## Next Steps

After completing analysis and extraction:

1. Review generated user stories with stakeholders
2. Use data dictionary for modernization database design
3. Reference workflows when implementing new features
4. Trace business rules to ensure nothing is missed

## Support

- **Framework Issues**: Check `.reforge/memory/logs/` for error details
- **Documentation**: See `.reforge/schemas/` for XML structure reference
- **Constitution**: Review `.reforge/memory/constitution.md` for principles
