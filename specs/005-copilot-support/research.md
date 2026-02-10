# Research: GitHub Copilot Slash Command Support

**Feature**: 005-copilot-support
**Date**: 2026-02-09

## R1: Copilot Agent File Convention

**Decision**: Use `.github/agents/reforge.<name>.agent.md` naming pattern with YAML frontmatter containing a `description` field.

**Rationale**: This matches FR-007's requirement for YAML frontmatter with description metadata. GitHub Copilot's agent discovery mechanism scans `.github/agents/` for `*.agent.md` files. The agent name is derived from the filename stem. The description field is extracted from the first `>` blockquote in the command template, providing context for agent discovery.

**Alternatives considered**:
- No YAML frontmatter: Rejected — FR-007 requires frontmatter for consistent metadata.
- Flat markdown without `.agent.md` extension: Rejected — Copilot requires the `.agent.md` extension for discovery.

## R2: Prompt File Convention

**Decision**: Use `.github/prompts/reforge.<name>.prompt.md` with minimal YAML frontmatter containing only `agent: reforge.<name>`.

**Rationale**: Spec-kit's `generate_copilot_prompts()` function creates these companion files with exactly this format. The `agent:` field links the prompt file to its corresponding agent file for Copilot Chat's discovery UI.

**Alternatives considered**:
- No prompt files (agents only): Rejected — spec-kit generates both, and prompt files are needed for Copilot Chat prompt recommendations in VS Code settings.
- Prompt files with full content: Rejected — spec-kit uses minimal metadata-only prompt files.

## R3: VS Code Settings Keys

**Decision**: Use `chat.promptFilesRecommendations` for agent discoverability and `chat.tools.terminal.autoApprove` for script auto-approval.

**Rationale**: These are the exact VS Code settings keys used by spec-kit's `vscode-settings.json` template. The `chat.promptFilesRecommendations` setting causes VS Code to recommend Reforge agents in Copilot Chat. The `chat.tools.terminal.autoApprove` setting auto-approves `reforge-scripts` CLI invocations.

**Alternatives considered**:
- Only `chat.promptFilesRecommendations` without auto-approve: Rejected — would cause excessive approval prompts during agent workflows.

## R4: Installation Detection Strategy

**Decision**: Detect existing Copilot installation by checking for `.github/agents/reforge.*.agent.md` files. Detect existing Claude installation by checking for `.claude/commands/reforge.*.md` files.

**Rationale**: Since `.reforge/` is shared between agent modes, it cannot be used as the sole installation marker. Checking for agent-specific generated files is the most reliable signal. This was decided during clarification.

**Alternatives considered**:
- Track mode in config.json: Rejected — adds state management complexity for minimal benefit.
- Marker files: Rejected — another file to manage; file presence detection is simpler.

## R5: Removal Scope

**Decision**: `--remove` always performs full uninstall regardless of installed agent modes.

**Rationale**: Decided during clarification. Simplifies the removal logic — one code path instead of conditional agent-aware removal. Users who want to switch agents can re-install the desired mode after removal.

**Alternatives considered**:
- Agent-aware `--remove --copilot`: Rejected by user — adds complexity for rare use case.

## R6: Code Reuse Strategy

**Decision**: Add new Copilot-specific generation functions alongside existing Claude functions rather than refactoring to a shared abstraction.

**Rationale**: The Claude `generate_wrappers()` and Copilot `generate_copilot_agents()` produce structurally different files (Claude uses YAML frontmatter + different body; Copilot uses YAML frontmatter with description only + agent.md extension + Load-and-Execute body). A shared abstraction would add indirection without simplifying much. The existing codebase has ~730 lines; adding ~120 lines for Copilot functions keeps it manageable.

**Alternatives considered**:
- Abstract `generate_agent_files(mode)` factory: Rejected — premature abstraction for 2 modes with different output formats.
- Separate module `copilot.py`: Rejected — all installation logic is currently in `__init__.py` and the functions are small enough to keep together.
