# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Reforge** is an LLM-driven application modernization framework. It enables AI agents (Claude Code, GitHub Copilot, etc.) to analyze legacy codebases and extract knowledge into structured formats — without any compiled code or external parsers.

The framework follows the [SpecKit](https://github.com/github/spec-kit) pattern: prompt templates guide the AI through structured workflows.

## Constitution

See `.reforge/memory/constitution.md` for governing principles. Key rules:

1. **LLM-First**: All analysis done by the AI agent using native tools (Read, Glob, Grep, Write)
2. **Prompt Templates**: Commands defined as markdown files in `.reforge/commands/`
3. **Structured Output**: Results stored as XML/markdown with source traceability
4. **Zero Dependencies**: Framework requires no runtime — just the AI agent
5. **Agent-Agnostic**: Works with any capable AI coding assistant

## Commands

Reforge commands follow the pattern `/reforge.<action>`:

- `/reforge.plan` — Create and manage a project plan for the extraction workflow
- `/reforge.init` — Initialize project context (name, tech stack, domain knowledge)
- `/reforge.analyze` — Scan and inventory a legacy codebase
- `/reforge.profile` — Generate language-specific and architecture-specific extraction profile
- `/reforge.extract [type]` — Extract business rules, database interactions, UI flows, workflows
- `/reforge.clarify` — Resolve ambiguities interactively
- `/reforge.generate [artifact]` — Generate documentation from extractions
- `/reforge.status` — Report analysis progress and coverage
- `/reforge.reanalyze [path]` — Re-process specific files without full re-analysis
- `/reforge.glossary` — Extract, verify, and persist a glossary of acronyms and abbreviations
- `/reforge.audit [type]` — Audit extraction coverage and identify gaps
- `/reforge.fix` — Execute corrections from the audit correction plan

## Directory Structure

```
.reforge/
├── commands/       # Slash command prompt templates
├── schemas/        # Output structure definitions
├── templates/      # Generation templates
├── scripts/        # Bash helper scripts
├── memory/         # Constitution and analysis state
└── config.json     # Configuration

reforge_output/<project-name>/
├── analysis/           # Codebase inventory (analysis.xml)
├── extractions/        # Extracted knowledge (business-rules, database, ui-flows, workflows)
├── derived/            # Derived artifacts (cross-mappings, features-requirements, registries/)
├── generated/          # Generated documentation (markdown, user-stories, data-dictionary)
├── audit/              # Audit outputs (audit-report.xml, correction-plan.xml)
└── diagrams/           # Diagram outputs (sources/, rendered/)
```

## Development

This project is built using the Specify workflow:
- `/speckit.specify` — Define feature specifications
- `/speckit.plan` — Create implementation plans
- `/speckit.tasks` — Generate task breakdowns
- `/speckit.implement` — Execute implementation

## Technical Stack

- **Language**: Markdown prompt templates (no compiled code)
- **Dependencies**: None - LLM-native tools only (Read, Write, Glob, Grep)
- **Storage**: XML files for extraction output, structured markdown for documentation
- **Testing**: Manual validation via sample legacy codebases

## Active Technologies
- Markdown prompt templates (no compiled code per Constitution Principle I) + None (LLM-native tools only: Read, Write, Glob, Grep) (002-audit-fix-commands)
- XML files for audit report and correction plan; structured markdown for command templates (002-audit-fix-commands)
- Python 3.11+ + Typer (CLI framework), Rich (console output) (005-copilot-support)
- Filesystem (markdown files, JSON config) (005-copilot-support)
- Markdown (prompt templates — no compiled code per Constitution Principle I) + None (LLM-native tools only: Read, Write, Glob, Grep) (006-extract-verification-gates)
- N/A (file-based markdown prompt template) (006-extract-verification-gates)
- Markdown prompt templates (no compiled code per Constitution Principle I) + None — LLM-native tools only (Read, Write, Glob, Grep) (008-project-plan)
- Filesystem — `.reforge/memory/project-plan.md` (structured markdown) (008-project-plan)
- Markdown prompt templates + XSD 1.0 (no compiled code per Constitution Principle I) + None — LLM-native tools only (Read, Write, Glob, Grep) (009-common-extraction-schema)
- XML files for extraction output; markdown for schema definitions; XSD for formal schema (009-common-extraction-schema)
- Markdown prompt templates (no compiled code per Constitution Principle I) + None -- LLM-native tools only (Read, Write, Glob, Grep) (010-source-anchored-generation)
- Filesystem -- markdown files in `.reforge/commands/` and `.reforge/templates/` (010-source-anchored-generation)
- XML files for audit reports and correction plans; structured markdown for command templates and schema definitions (011-content-accuracy-audit)
- XML files (`metrics-registry.xml`, `consistency-audit-report.xml`, `correction-plan.xml`); structured markdown for command and schema definitions (012-cross-doc-consistency)
- Markdown prompt templates (no compiled code per Constitution Principle I) + None — LLM-native tools only (Read, Write, Glob, Grep, WebSearch) (013-glossary-command)
- XML files for glossary output; JSON for memory lookup and checkpoints; markdown for templates (013-glossary-command)

## Recent Changes
- 002-audit-fix-commands: Added Markdown prompt templates (no compiled code per Constitution Principle I) + None (LLM-native tools only: Read, Write, Glob, Grep)
