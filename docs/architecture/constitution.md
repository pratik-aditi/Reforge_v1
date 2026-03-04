---
tags:
  - architecture
---

# Constitution

The Reforge Constitution defines the governing principles that all framework components must follow. It establishes non-negotiable architectural rules and guides how the framework evolves.

## Core Principles

### I. LLM-First Architecture

Reforge is an LLM-driven framework. The AI agent performs **all** analysis, extraction, and generation using its native capabilities. There is no compiled code, no runtime dependencies, and no external parsers.

**Key rules:**

- All analysis is performed by the LLM using file tools (Read, Glob, Grep, Write)
- No AST parsers, Tree-sitter grammars, or language-specific tooling in the framework
- The framework consists entirely of prompt templates, schemas, and configuration files

**Rationale:** LLMs understand code semantically across any language without custom parsers. This eliminates dependency complexity and makes the framework instantly usable in any AI-assisted environment.

### II. Prompt Template Commands

Every Reforge capability is exposed as a slash command backed by a markdown prompt template.

**Key rules:**

- Commands are defined as markdown files in `.reforge/commands/`
- Command names follow the pattern `/reforge.<action>`
- Each command is self-contained with clear inputs, steps, and outputs
- Commands do not require external tool execution beyond LLM-native tools

**Rationale:** Prompt templates are portable across AI agents, version-controllable, and require no installation beyond copying files.

### III. Structured Output (XML/Markdown)

All extraction and analysis results are stored in structured, human-readable formats that LLMs can parse and generate.

**Key rules:**

- Extracted knowledge is stored as XML with defined schemas or structured markdown
- Schemas are documented in `.reforge/schemas/`
- Output includes source references (file path, line numbers) for traceability
- Output is deterministic given the same input and prompts

**Rationale:** Structured output enables downstream processing, validation, and transformation while remaining LLM-friendly.

### IV. Installable via CLI Bootstrap

Reforge is installable via a simple CLI command that copies framework files into a target project.

**Key rules:**

- Installation is achieved via `reforge --claude <path>` or `reforge --copilot <path>`
- Installation does not require Node.js, Python, or other runtime dependencies for the framework itself
- The installed framework is fully functional with only the AI agent present
- All framework files live under the `.reforge/` directory

**Rationale:** Zero-dependency installation ensures immediate usability and eliminates environment setup friction.

### V. Agent-Agnostic Design

Reforge works with any capable AI coding assistant without agent-specific code.

**Key rules:**

- Prompt templates do not reference specific agent names (use "the agent" rather than naming a product)
- Commands use only common tool patterns: file read, file write, glob, grep, directory listing
- The framework does not depend on agent-specific features (MCP servers, custom tools)
- Documentation may include agent-specific tips in clearly marked optional sections

**Rationale:** Agent-agnostic design future-proofs the framework and maximizes adoption across different AI tools.

### VI. Extensibility via Tooling Layer

Additional tooling (validators, transformers, visualizers) may be added as an optional layer that enhances but never replaces the core LLM workflow.

**Key rules:**

- The core workflow functions without any optional tooling
- Optional tools are separated in `.reforge/tools/` or external packages
- Tools are not required for any slash command to complete
- Tools provide value-add capabilities: validation, visualization, export

**Rationale:** Keeping tooling optional maintains the zero-dependency core while allowing power users to enhance their workflow.

## Project-Specific Context

The file `.reforge/memory/project-context.md` (created via `/reforge.init`) contains project-specific guidance. When present, its contents serve as supplemental rules alongside the constitution. On conflicts, the constitution takes precedence.

## Governance

### Amendment Process

Changes to the constitution follow a formal process:

1. Proposed changes must be documented with rationale
2. Changes affecting core principles (I--VI) require explicit justification
3. All amendments update the version number per semantic versioning:
    - **MAJOR** -- Principle removal or incompatible redefinition
    - **MINOR** -- New principle, section, or material expansion
    - **PATCH** -- Clarifications, typo fixes, non-semantic changes

### Compliance

- All slash commands are validated against the constitution before merge
- The Constitution Check section in plan templates verifies principles I--VI
- Violations are documented with explicit justification

### Guidance Files

- `CLAUDE.md` (or equivalent agent configuration) references the constitution
- Runtime guidance must not contradict constitutional principles

The constitution is maintained at `.reforge/memory/constitution.md` and is versioned independently from the framework release cycle.
