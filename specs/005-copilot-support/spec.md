# Feature Specification: GitHub Copilot Slash Command Support

**Feature Branch**: `005-copilot-support`
**Created**: 2026-02-09
**Status**: Draft
**Input**: User description: "Add support for GitHub Copilot to run slash commands. Use of copilot should be enabled with `reforge --copilot <path>`, similar to `reforge --claude <path>` and install into the .github and .vscode just as spec-kit does for copilot. This change should primarily involve a different folder structure for slash commands and agents. Use spec-kit as a model."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Install Reforge for Copilot (Priority: P1)

A developer wants to use Reforge with GitHub Copilot in VS Code. They run `reforge --copilot <path>` on a target project directory. The CLI installs the framework files into `.reforge/` (same as Claude), then generates Copilot-specific agent files in `.github/agents/` and prompt files in `.github/prompts/`, along with VS Code workspace settings in `.vscode/settings.json`. The developer can then invoke Reforge commands in Copilot Chat using `@reforge.analyze`, `@reforge.extract`, etc.

**Why this priority**: This is the core feature. Without the install pathway, nothing else works.

**Independent Test**: Run `reforge --copilot .` on a clean project directory and verify all expected files are created in the correct locations with correct content.

**Acceptance Scenarios**:

1. **Given** a project directory without Reforge installed, **When** the user runs `reforge --copilot .`, **Then** the CLI copies `.reforge/` framework files, creates `.github/agents/reforge.*.agent.md` files for each command, creates `.github/prompts/reforge.*.prompt.md` companion files, writes `.vscode/settings.json` with prompt file recommendations and terminal auto-approve settings, and displays a success message.
2. **Given** a project directory without Reforge installed, **When** the user runs `reforge --copilot --dry-run .`, **Then** the CLI lists all files that would be created without making any changes.
3. **Given** a project with Reforge already installed via `--copilot`, **When** the user runs `reforge --copilot .` again, **Then** the CLI reports an error directing the user to use `--update` or `--remove` first.

---

### User Story 2 - Update Copilot Installation (Priority: P2)

A developer has previously installed Reforge for Copilot and wants to update to the latest command templates after a framework upgrade. They run `reforge --copilot --update <path>`. The CLI refreshes framework files in `.reforge/`, regenerates Copilot agent and prompt files in `.github/` and `.vscode/`, and preserves user-configured project settings.

**Why this priority**: Updates are essential for ongoing use but require initial installation first.

**Independent Test**: Install via `--copilot`, modify config, run `--copilot --update`, verify framework files refreshed but user config preserved.

**Acceptance Scenarios**:

1. **Given** a project with Copilot installation, **When** the user runs `reforge --copilot --update .`, **Then** `.reforge/commands/`, `.reforge/schemas/`, `.reforge/templates/` are refreshed, `.github/agents/` and `.github/prompts/` are regenerated, `.vscode/settings.json` is updated, and `config.json` user fields are preserved.
2. **Given** a project without Copilot installation, **When** the user runs `reforge --copilot --update .`, **Then** the CLI reports an error indicating no existing installation.

---

### User Story 3 - Remove Copilot Installation (Priority: P2)

A developer wants to remove Reforge Copilot integration from their project. They run `reforge --remove .`. The CLI removes `.reforge/`, `.github/agents/reforge.*.agent.md`, `.github/prompts/reforge.*.prompt.md`, Copilot-specific entries from `.vscode/settings.json`, and Reforge entries from `.gitignore`.

**Why this priority**: Clean removal is important but only used occasionally.

**Independent Test**: Install via `--copilot`, then run `--remove`, verify all Reforge-related files are cleaned up without affecting non-Reforge files in `.github/` or `.vscode/`.

**Acceptance Scenarios**:

1. **Given** a Copilot-installed project, **When** the user runs `reforge --remove .`, **Then** `.reforge/` is removed, `reforge.*.agent.md` files are removed from `.github/agents/`, `reforge.*.prompt.md` files are removed from `.github/prompts/`, Reforge-added settings are removed from `.vscode/settings.json`, and Reforge entries are removed from `.gitignore`.
2. **Given** a project with both existing `.github/` content (workflows, CODEOWNERS) and Reforge agent files, **When** the user runs `reforge --remove .`, **Then** only Reforge-specific files are removed; other `.github/` content is untouched.

---

### User Story 4 - Invoke Reforge Commands in Copilot Chat (Priority: P1)

After installation, a developer opens the project in VS Code and uses Copilot Chat to invoke Reforge commands. They type `@reforge.analyze` in the Copilot Chat panel. Copilot discovers the agent file, loads the command template from `.reforge/commands/analyze.md`, and executes the analysis workflow.

**Why this priority**: This validates that the generated agent files actually work with Copilot.

**Independent Test**: After `reforge --copilot .`, open the project in VS Code, type `@reforge.analyze` in Copilot Chat, and verify the command is discovered and loads the correct template.

**Acceptance Scenarios**:

1. **Given** a Copilot-installed project opened in VS Code, **When** the user types `@reforge.` in Copilot Chat, **Then** all Reforge commands appear as discoverable agents.
2. **Given** a Copilot-installed project, **When** the user invokes `@reforge.analyze`, **Then** the agent loads and follows the command template from `.reforge/commands/analyze.md`.

---

### Edge Cases

- What happens when `.github/agents/` already contains non-Reforge agent files? Only Reforge-prefixed files should be managed.
- What happens when `.vscode/settings.json` already exists with user settings? Reforge settings should be merged, not overwritten.
- What happens when the user runs `reforge --copilot` on a project that was previously set up with `reforge --claude`? Both should coexist (`.claude/` and `.github/agents/` side by side).
- What happens when `.github/prompts/` already contains other prompt files? Only Reforge-prefixed files should be managed.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST accept a `--copilot` CLI flag as an alternative to `--claude` for installation
- **FR-002**: System MUST generate Copilot agent files in `.github/agents/` with the naming pattern `reforge.<command>.agent.md` for each command in `.reforge/commands/`
- **FR-003**: System MUST generate companion prompt files in `.github/prompts/` with the naming pattern `reforge.<command>.prompt.md` for each command
- **FR-004**: System MUST create or merge `.vscode/settings.json` with `chat.promptFilesRecommendations` entries for each Reforge command and `chat.tools.terminal.autoApprove` entries for Reforge script paths
- **FR-005**: System MUST copy the same `.reforge/` framework files (commands, schemas, templates, config, constitution) regardless of whether `--claude` or `--copilot` is used
- **FR-006**: System MUST support `--update`, `--remove`, `--force`, and `--dry-run` flags with `--copilot`, mirroring the behavior of `--claude`. Installation presence for `--copilot --update` is detected by the existence of `.github/agents/reforge.*.agent.md` files (not by `.reforge/` alone, since that directory is shared across agent modes)
- **FR-007**: Each generated agent file MUST contain a YAML frontmatter `description` field extracted from the command template's first `>` blockquote line
- **FR-008**: Each generated agent file MUST reference the corresponding `.reforge/commands/<name>.md` template for execution
- **FR-009**: System MUST allow `--claude` and `--copilot` installations to coexist in the same project without conflict
- **FR-010**: The `--remove` operation MUST remove all Reforge artifacts across all agent modes: `.reforge/`, `.claude/commands/reforge.*.md`, `.github/agents/reforge.*.agent.md`, `.github/prompts/reforge.*.prompt.md`, and Reforge-specific entries from `.vscode/settings.json`. Non-Reforge content in `.github/`, `.vscode/`, and `.claude/` MUST be preserved
- **FR-011**: The `--remove` operation is always a full uninstall regardless of which agent modes (`--claude`, `--copilot`) were previously set up
- **FR-012**: System MUST update `.gitignore` with the same runtime-state exclusions regardless of installation mode

### Key Entities

- **Agent File**: A `.agent.md` file in `.github/agents/` that Copilot discovers as a chat participant. Contains YAML frontmatter with description and the command execution instructions.
- **Prompt File**: A `.prompt.md` file in `.github/prompts/` that acts as a companion to the agent file for Copilot Chat discovery.
- **VS Code Settings**: The `.vscode/settings.json` file containing Copilot-specific configuration for prompt recommendations and terminal script auto-approval.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Running `reforge --copilot .` on a clean project produces all expected files within a single CLI invocation
- **SC-002**: All 9 Reforge commands are discoverable as Copilot Chat agents after installation
- **SC-003**: Running `reforge --copilot --update .` preserves 100% of user-configured project settings while refreshing all framework files
- **SC-004**: Running `reforge --remove .` on a Copilot-installed project removes all and only Reforge-specific files, leaving other project files intact
- **SC-005**: A project with both `--claude` and `--copilot` installations functions correctly with both agents simultaneously

## Clarifications

### Session 2026-02-09

- Q: How should the system detect which agent mode was previously installed when `.reforge/` is shared? → A: Detect by presence of `.github/agents/reforge.*.agent.md` files (no tracking needed).
- Q: Should `--remove` be agent-aware when both Claude and Copilot are installed? → A: No. `--remove` always performs a full uninstall regardless of which agents were set up.

## Assumptions

- Copilot Chat agent discovery relies on `.github/agents/*.agent.md` file naming convention as used by spec-kit (this is GitHub's documented pattern).
- Copilot prompt file discovery uses `.github/prompts/*.prompt.md` as the companion file pattern.
- The `chat.promptFilesRecommendations` and `chat.tools.terminal.autoApprove` VS Code settings are the current mechanism for Copilot integration.
- The `reforge-scripts` Python CLI (used for helper operations like `init-project`, `check-prerequisites`) works identically regardless of which agent invokes it, so no agent-specific script changes are needed.
- Agent files will reference command templates via relative path (`.reforge/commands/<name>.md`) using the same Load-and-Execute pattern as Claude wrappers.
- The `--copilot` and `--claude` flags are mutually exclusive per invocation but both can be installed on the same project via separate invocations.
