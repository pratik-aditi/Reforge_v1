---
hide:
  - navigation
---

# Reforge

[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![License: Apache 2.0](https://img.shields.io/badge/license-Apache%202.0-green.svg)](https://github.com/Aditi-Consulting/reforge/blob/main/LICENSE)
[![Tests](https://github.com/Aditi-Consulting/reforge/actions/workflows/test.yml/badge.svg)](https://github.com/Aditi-Consulting/reforge/actions/workflows/test.yml)
[![Docs](https://github.com/Aditi-Consulting/reforge/actions/workflows/docs.yml/badge.svg)](https://aditi-consulting.github.io/reforge/)

**LLM-driven legacy codebase analysis and documentation framework.**

Reforge enables AI coding agents to analyze legacy codebases and extract knowledge into structured formats -- without compiled code, external parsers, or runtime dependencies. Point your AI agent at a codebase, and Reforge's prompt templates guide it through systematic analysis, extraction, and documentation.

---

## Feature Highlights

<div class="grid cards" markdown>

-   **Zero Dependencies**

    No parsers, no AST tools, no language plugins. The AI reads source files directly using its native file tools.

-   **Agent-Agnostic**

    Works with Claude Code (`/reforge.*`) and GitHub Copilot (`@reforge.*`). Install both on the same project without conflict.

-   **10 Extraction Types**

    Business rules, database, UI flows, workflows, call-sites, dependencies, functional requirements, non-functional requirements, architecture, and issues.

-   **Structured XML Output**

    Every extraction produces schema-validated XML with confidence levels and source file traceability (file, line, snippet).

-   **Checkpoint & Resume**

    Interrupt long-running analyses and pick up where you left off. Works across sessions.

-   **Audit & Fix Cycle**

    Automated coverage auditing identifies gaps. The fix command fills them by dispatching to the appropriate extraction commands.

</div>

---

## Quick Links

- [**Getting Started**](getting-started/installation.md) -- Install Reforge and analyze your first codebase in 5 minutes
- [**Commands**](commands/index.md) -- Full reference for all `/reforge.*` commands
- [**Guides**](guides/workflow.md) -- Typical workflow, configuration, and extraction type details
