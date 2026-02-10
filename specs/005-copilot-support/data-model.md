# Data Model: GitHub Copilot Slash Command Support

**Feature**: 005-copilot-support
**Date**: 2026-02-09

## Entities

### Agent File

A generated markdown file that Copilot discovers as a chat participant.

| Attribute | Type | Description |
|-----------|------|-------------|
| filename | string | `reforge.<command>.agent.md` |
| location | path | `.github/agents/` |
| command_name | string | Stem of source template (e.g., `analyze`, `extract`) |
| description | string | Extracted from first `>` blockquote in source template |
| body | markdown | Load-and-Execute instruction referencing `.reforge/commands/<name>.md` |

**Source**: Generated from `.reforge/commands/*.md` templates.

### Prompt File

A minimal companion file for Copilot Chat discovery.

| Attribute | Type | Description |
|-----------|------|-------------|
| filename | string | `reforge.<command>.prompt.md` |
| location | path | `.github/prompts/` |
| agent_ref | string | `reforge.<command>` (links to corresponding agent file) |

**Relationship**: 1:1 with Agent File (same command name).

### VS Code Settings

JSON configuration merged into `.vscode/settings.json`.

| Key | Type | Description |
|-----|------|-------------|
| `chat.promptFilesRecommendations` | object | Map of `reforge.<command>: true` for each command |
| `chat.tools.terminal.autoApprove` | object | Map of `reforge-scripts : true` for auto-approving CLI calls |

**Merge behavior**: Deep-merge with existing settings. Reforge keys are added/updated without removing non-Reforge keys.

## Relationships

```text
.reforge/commands/<name>.md (source template)
    │
    ├── 1:1 ──► .github/agents/reforge.<name>.agent.md (generated)
    │
    ├── 1:1 ──► .github/prompts/reforge.<name>.prompt.md (generated)
    │
    └── 1:1 ──► .vscode/settings.json entry (merged)
```

## State Transitions

No runtime state. All entities are filesystem artifacts created during install and removed during uninstall.

| Operation | Effect on Agent Files | Effect on Prompt Files | Effect on VS Code Settings |
|-----------|----------------------|------------------------|---------------------------|
| `--copilot` (install) | Created | Created | Merged |
| `--copilot --update` | Regenerated | Regenerated | Re-merged |
| `--remove` | Deleted (reforge.* only) | Deleted (reforge.* only) | Reforge keys removed |
