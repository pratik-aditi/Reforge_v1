---
tags:
  - getting-started
---

# Installation

## Platform Support

Reforge works on **macOS**, **Linux**, and **Windows**. Python, uv, and Claude Code all support all three platforms. The instructions below use forward slashes for paths -- Windows users can use either forward slashes or backslashes.

## Prerequisites

- **Python 3.11+** -- [Download](https://www.python.org/downloads/)
- **uv** -- [Install uv](https://docs.astral.sh/uv/getting-started/installation/) (recommended package manager)
- **An AI coding agent**:
    - [Claude Code](https://docs.anthropic.com/en/docs/claude-code) -- use `--claude`
    - [GitHub Copilot](https://github.com/features/copilot) in VS Code -- use `--copilot`

## Install the CLI

Install directly from GitHub -- no cloning required:

```bash
uv tool install reforge-cli --from git+https://github.com/Aditi-Consulting/reforge.git
```

Or if you've already cloned the repo:

```bash
uv tool install reforge-cli --from /path/to/reforge
```

!!! tip
    If `reforge` is not found after installation, ensure the `uv tool` bin directory is on your `PATH`. Run `uv tool dir --bin` to find it, then add it to your PATH:

    === "macOS / Linux"

        ```bash
        export PATH="$HOME/.local/bin:$PATH"
        ```

        Add this line to your `~/.zshrc` or `~/.bashrc` to make it permanent.

    === "Windows (PowerShell)"

        ```powershell
        $env:Path = "$env:USERPROFILE\.local\bin;$env:Path"
        ```

        To make it permanent, add the directory via **Settings > System > About > Advanced system settings > Environment Variables**, or run:

        ```powershell
        [Environment]::SetEnvironmentVariable("Path", "$env:USERPROFILE\.local\bin;$([Environment]::GetEnvironmentVariable('Path', 'User'))", "User")
        ```

## Install into Your Target Project

Navigate to (or specify the path of) the legacy project you want to analyze, then run the installer for your agent:

=== "Claude Code"

    ```bash
    reforge --claude /path/to/legacy-project
    ```

    This creates `.claude/commands/reforge.*.md` wrappers and registers slash commands.

=== "GitHub Copilot"

    ```bash
    reforge --copilot /path/to/legacy-project
    ```

    This creates `.github/agents/`, `.github/prompts/`, and `.vscode/settings.json` entries.

Both modes install the shared `.reforge/` framework directory. You can install both on the same project -- they coexist without conflict:

```bash
reforge --claude /path/to/project
reforge --copilot /path/to/project
```

## Managing Your Installation

### Update the CLI tool

Reinstall from GitHub to get the latest version:

```bash
uv tool install reforge-cli --from git+https://github.com/Aditi-Consulting/reforge.git --force
```

Or if updating from a local clone:

```bash
cd /path/to/reforge
git pull
uv tool install reforge-cli --from . --force
```

### Refresh framework files

Update the `.reforge/` directory in an already-installed project. Your `config.json` and analysis output are preserved.

=== "Claude Code"

    ```bash
    reforge --claude --update /path/to/project
    ```

=== "GitHub Copilot"

    ```bash
    reforge --copilot --update /path/to/project
    ```

### Remove from a project

Removes framework files and agent-specific integration files. Analysis output (`reforge_output/`) is preserved unless you explicitly confirm its removal.

```bash
reforge --remove /path/to/project
```

### Uninstall the CLI tool

```bash
uv tool uninstall reforge-cli
```

## CLI Reference

```
Usage: reforge [OPTIONS] [TARGET_PATH]
```

| Option | Description |
|--------|-------------|
| `--claude` | Install/set up Reforge for Claude Code |
| `--copilot` | Install/set up Reforge for GitHub Copilot |
| `--remove` | Remove Reforge from target project |
| `--update` | Refresh framework files (preserves config) |
| `--force` | Skip confirmation prompts |
| `--dry-run` | Show what would be done without making changes |
| `--version` | Show framework version |
| `--help` | Show help message |

`--claude` and `--copilot` are mutually exclusive per invocation.

| Example | What it does |
|---------|--------------|
| `reforge --claude .` | Install for Claude Code in current directory |
| `reforge --copilot .` | Install for GitHub Copilot in current directory |
| `reforge --claude /opt/legacy-app` | Install into a specific project (use `C:\projects\legacy-app` on Windows) |
| `reforge --claude --update .` | Update framework files for Claude Code |
| `reforge --copilot --dry-run .` | Preview what would be installed |
| `reforge --remove .` | Uninstall all Reforge artifacts |
