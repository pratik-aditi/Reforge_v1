"""Reforge CLI - LLM-driven legacy codebase analysis and documentation framework."""

import json
import shutil
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from .scripts import (
    check_prerequisites,
    create_checkpoint,
    delete_checkpoint,
    init_project,
    read_checkpoint,
    update_agent_context,
)
from .scripts.common import ReforgeError

__version__ = "1.0.0"

app = typer.Typer(help="Reforge - LLM-driven legacy codebase analysis and documentation framework")
console = Console()
console_err = Console(stderr=True)

# Create a subcommand group for helper scripts
scripts_app = typer.Typer(help="Helper scripts for Reforge commands")


def get_reforge_home() -> Path:
    import site
    
    for site_dir in site.getsitepackages():
        share_path = Path(site_dir).parent / "share" / "reforge-cli" / ".reforge"
        if share_path.exists():
            return share_path.parent
    
    package_dir = Path(__file__).parent.parent.parent
    if (package_dir / ".reforge").exists():
        return package_dir
    
    console_err.print("[red]Error: Framework files not found[/red]")
    raise typer.Exit(1)


def info(message: str):
    console.print(f"[blue][reforge][/blue] {message}")


def ok(message: str):
    console.print(f"[green][reforge][/green] {message}")


def warn(message: str):
    console.print(f"[yellow][reforge][/yellow] {message}")


def error(message: str):
    console_err.print(f"[red][reforge][/red] {message}")


def validate_source(reforge_home: Path):
    commands_dir = reforge_home / ".reforge" / "commands"
    config_file = reforge_home / ".reforge" / "config.json"
    
    if not commands_dir.exists():
        error(f"Framework source incomplete: {commands_dir} not found")
        raise typer.Exit(1)
    
    if not config_file.exists():
        error(f"Framework source incomplete: {config_file} not found")
        raise typer.Exit(1)


def validate_target(target: Path, reforge_home: Path):
    if not target.exists():
        error(f"Target directory does not exist: {target}")
        raise typer.Exit(1)
    
    if target.resolve() == reforge_home.resolve():
        error(f"Cannot install into the framework repository itself: {target}")
        raise typer.Exit(1)


def copy_framework(target: Path, reforge_home: Path, dry_run: bool):
    # Note: scripts/bash no longer copied - Python scripts are in the package
    dirs = ["commands", "schemas", "templates"]
    files = ["memory/constitution.md", "config.json", "README.md"]
    
    for dir_name in dirs:
        src = reforge_home / ".reforge" / dir_name
        dst = target / ".reforge" / dir_name
        if src.exists():
            if dry_run:
                info(f"Would copy: .reforge/{dir_name}/")
            else:
                dst.parent.mkdir(parents=True, exist_ok=True)
                if dst.exists():
                    shutil.rmtree(dst)
                shutil.copytree(src, dst)
    
    for file_name in files:
        src = reforge_home / ".reforge" / file_name
        dst = target / ".reforge" / file_name
        if src.exists():
            if dry_run:
                info(f"Would copy: .reforge/{file_name}")
            else:
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
    
    if dry_run:
        info("Would write: .reforge/.version")
    else:
        (target / ".reforge" / ".version").write_text(__version__)


def create_memory_dirs(target: Path, dry_run: bool):
    dirs = [".reforge/memory/history", ".reforge/memory/backups", ".reforge/memory/checkpoints",
            ".reforge/memory/clarifications", ".reforge/memory/logs", ".reforge/memory/analysis"]
    
    for dir_name in dirs:
        if dry_run:
            info(f"Would create: {dir_name}/")
        else:
            (target / dir_name).mkdir(parents=True, exist_ok=True)


def generate_wrappers(target: Path, reforge_home: Path, dry_run: bool):
    cmd_dir = reforge_home / ".reforge" / "commands"
    
    if dry_run:
        info("Would create: .claude/commands/ wrappers")
    else:
        (target / ".claude" / "commands").mkdir(parents=True, exist_ok=True)
    
    for cmd_file in cmd_dir.glob("*.md"):
        name = cmd_file.stem
        description = f"Run reforge {name} command"
        
        try:
            content = cmd_file.read_text()
            for line in content.split('\n'):
                if line.startswith('>'):
                    description = line.lstrip('> ').strip()
                    break
        except Exception:
            pass
        
        if dry_run:
            info(f"  Would create: .claude/commands/reforge.{name}.md")
        else:
            wrapper_content = f"""---
description: {description}
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Execution

Load and execute the full command template at `.reforge/commands/{name}.md`.
Follow all steps defined in that file exactly as written, passing through any
arguments provided above.
"""
            (target / ".claude" / "commands" / f"reforge.{name}.md").write_text(wrapper_content)


def merge_settings(target: Path, dry_run: bool):
    settings_file = target / ".claude" / "settings.local.json"
    # Python scripts are invoked via `reforge` CLI, no bash permissions needed
    permissions = [
        'Bash(reforge init-project:*)',
        'Bash(reforge check-prerequisites:*)',
        'Bash(reforge checkpoint:*)',
        'Bash(reforge update-context:*)',
    ]

    if dry_run:
        info("Would update: .claude/settings.local.json with reforge permissions")
        return

    settings_file.parent.mkdir(parents=True, exist_ok=True)

    if settings_file.exists():
        try:
            settings = json.loads(settings_file.read_text())
        except json.JSONDecodeError:
            settings = {}

        if "permissions" not in settings:
            settings["permissions"] = {}
        if "allow" not in settings["permissions"]:
            settings["permissions"]["allow"] = []

        for perm in permissions:
            if perm not in settings["permissions"]["allow"]:
                settings["permissions"]["allow"].append(perm)
    else:
        settings = {"permissions": {"allow": permissions}}

    settings_file.write_text(json.dumps(settings, indent=2) + '\n')


def update_gitignore(target: Path, dry_run: bool):
    gitignore = target / ".gitignore"
    entries = ["reforge_output/", ".reforge/memory/checkpoints/",
               ".reforge/memory/clarifications/", ".reforge/memory/logs/"]
    header = "# Reforge Framework (runtime state)"
    
    if dry_run:
        info("Would update: .gitignore with reforge entries")
        return
    
    if gitignore.exists() and header in gitignore.read_text():
        return
    
    with gitignore.open('a') as f:
        f.write('\n' + header + '\n')
        for entry in entries:
            f.write(entry + '\n')


def merge_config(target: Path, reforge_home: Path, dry_run: bool):
    existing = target / ".reforge" / "config.json"
    new_config = reforge_home / ".reforge" / "config.json"
    
    if not existing.exists():
        if dry_run:
            info("Would copy: .reforge/config.json (fresh)")
        else:
            shutil.copy2(new_config, existing)
        return
    
    if dry_run:
        info("Would merge: .reforge/config.json (preserving user fields)")
        return
    
    shutil.copy2(existing, existing.parent / "config.json.bak")
    
    try:
        existing_data = json.loads(existing.read_text())
        new_data = json.loads(new_config.read_text())
        
        if "project" in existing_data:
            if "name" in existing_data["project"]:
                new_data["project"]["name"] = existing_data["project"]["name"]
            if "root" in existing_data["project"]:
                new_data["project"]["root"] = existing_data["project"]["root"]
            if "description" in existing_data["project"]:
                new_data["project"]["description"] = existing_data["project"]["description"]
        
        if "analysis" in existing_data and "exclusions" in existing_data["analysis"]:
            new_data["analysis"]["exclusions"] = existing_data["analysis"]["exclusions"]
        
        if "output" in existing_data and "directory" in existing_data["output"]:
            new_data["output"]["directory"] = existing_data["output"]["directory"]
        
        if "extraction" in existing_data:
            if "confidenceThreshold" in existing_data["extraction"]:
                new_data["extraction"]["confidenceThreshold"] = existing_data["extraction"]["confidenceThreshold"]
            if "includeSnippets" in existing_data["extraction"]:
                new_data["extraction"]["includeSnippets"] = existing_data["extraction"]["includeSnippets"]
            if "maxSnippetLines" in existing_data["extraction"]:
                new_data["extraction"]["maxSnippetLines"] = existing_data["extraction"]["maxSnippetLines"]
        
        existing.write_text(json.dumps(new_data, indent=2) + '\n')
        ok("Config merged (backup at config.json.bak)")
    except Exception as e:
        error(f"Failed to merge config: {e}")


def do_install(target: Path, reforge_home: Path, dry_run: bool):
    if (target / ".reforge").exists():
        error("Target already has .reforge/ directory. Use --update to refresh, or --remove first.")
        raise typer.Exit(1)
    
    info(f"Installing Reforge framework into: {target}")
    
    copy_framework(target, reforge_home, dry_run)
    create_memory_dirs(target, dry_run)
    generate_wrappers(target, reforge_home, dry_run)
    merge_settings(target, dry_run)
    update_gitignore(target, dry_run)
    
    if dry_run:
        console.print()
        info("Dry run complete. No changes made.")
    else:
        console.print()
        ok(f"Reforge v{__version__} installed successfully!")
        info("Run /reforge.analyze in Claude Code to begin codebase analysis.")


def do_update(target: Path, reforge_home: Path, dry_run: bool):
    if not (target / ".reforge").exists():
        error("No .reforge/ directory found. Run initial install first (without --update).")
        raise typer.Exit(1)
    
    info(f"Updating Reforge framework in: {target}")
    
    # Update framework files (scripts/bash no longer needed - Python scripts in package)
    dirs = ["commands", "schemas", "templates"]
    for dir_name in dirs:
        src = reforge_home / ".reforge" / dir_name
        dst = target / ".reforge" / dir_name
        
        if src.exists():
            if dry_run:
                info(f"Would refresh: .reforge/{dir_name}/")
            else:
                dst.parent.mkdir(parents=True, exist_ok=True)
                if dst.exists():
                    shutil.rmtree(dst)
                shutil.copytree(src, dst)
    
    # Update constitution and README
    for file_name in ["memory/constitution.md", "README.md"]:
        src = reforge_home / ".reforge" / file_name
        if src.exists():
            if dry_run:
                info(f"Would refresh: .reforge/{file_name}")
            else:
                dst = target / ".reforge" / file_name
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
    
    # Merge config
    merge_config(target, reforge_home, dry_run)
    
    # Update version stamp
    if dry_run:
        info("Would update: .reforge/.version")
    else:
        (target / ".reforge" / ".version").write_text(__version__)
    
    # Regenerate wrappers
    generate_wrappers(target, reforge_home, dry_run)
    
    # Ensure settings and gitignore are up to date
    merge_settings(target, dry_run)
    update_gitignore(target, dry_run)
    
    if dry_run:
        console.print()
        info("Dry run complete. No changes made.")
    else:
        console.print()
        ok(f"Reforge updated to v{__version__}!")


def do_remove(target: Path, force: bool, dry_run: bool):
    if not (target / ".reforge").exists():
        error(f"No .reforge/ directory found in: {target}")
        raise typer.Exit(1)
    
    if dry_run:
        info("Would remove: .reforge/")
        info("Would remove: .claude/commands/reforge.*.md")
        info("Would remove reforge permissions from: .claude/settings.local.json")
        info("Would remove reforge entries from: .gitignore")
        console.print()
        info("Dry run complete. No changes made.")
        return
    
    # Confirmation
    if not force:
        console.print()
        warn("This will remove:")
        console.print("  - .reforge/ directory")
        console.print("  - .claude/commands/reforge.*.md wrappers")
        console.print("  - Reforge permissions from .claude/settings.local.json")
        console.print("  - Reforge entries from .gitignore")
        console.print()
        
        confirm = typer.confirm("Continue?", default=False)
        if not confirm:
            info("Aborted.")
            raise typer.Exit(0)
    
    # Remove .reforge directory
    shutil.rmtree(target / ".reforge")
    ok("Removed .reforge/")
    
    # Remove wrapper commands
    claude_commands = target / ".claude" / "commands"
    if claude_commands.exists():
        for wrapper in claude_commands.glob("reforge.*.md"):
            wrapper.unlink()
    ok("Removed .claude/commands/reforge.*.md")
    
    # Clean settings.local.json
    settings_file = target / ".claude" / "settings.local.json"
    if settings_file.exists():
        try:
            settings = json.loads(settings_file.read_text())
            
            if "permissions" in settings and "allow" in settings["permissions"]:
                # Remove reforge permissions (both old bash and new Python CLI)
                settings["permissions"]["allow"] = [
                    perm for perm in settings["permissions"]["allow"]
                    if ".reforge/scripts/bash/" not in perm
                    and not perm.startswith("Bash(reforge ")
                ]
            
            settings_file.write_text(json.dumps(settings, indent=2) + '\n')
            ok("Cleaned .claude/settings.local.json")
        except Exception as e:
            warn(f"Could not clean settings.local.json: {e}")
    
    # Clean gitignore
    gitignore = target / ".gitignore"
    if gitignore.exists():
        content = gitignore.read_text()
        # Remove reforge section
        lines = content.split('\n')
        new_lines = []
        skip = False
        
        for line in lines:
            if "# Reforge Framework (runtime state)" in line:
                skip = True
                continue
            if skip and line.strip() == "":
                skip = False
                continue
            if not skip:
                new_lines.append(line)
        
        gitignore.write_text('\n'.join(new_lines))
        ok("Cleaned .gitignore")
    
    console.print()
    ok(f"Reforge removed from: {target}")
    
    # Prompt about output directory
    output_dir = target / "reforge_output"
    if output_dir.exists():
        console.print()
        warn("Note: reforge_output/ still exists (your analysis data).")
        
        if not force:
            confirm_output = typer.confirm("Remove reforge_output/ as well?", default=False)
            if confirm_output:
                shutil.rmtree(output_dir)
                ok("Removed reforge_output/")
            else:
                info("Kept reforge_output/")
        else:
            info("Kept reforge_output/ (use rm -rf to remove manually)")


@app.callback(invoke_without_command=True)
def cli(
    ctx: typer.Context,
    claude: bool = typer.Option(False, "--claude", help="Install/set up Reforge for Claude Code"),
    remove: bool = typer.Option(False, "--remove", help="Remove Reforge from target project"),
    version: bool = typer.Option(False, "--version", help="Show framework version"),
    update: bool = typer.Option(False, "--update", help="Refresh framework files (preserves config)"),
    force: bool = typer.Option(False, "--force", help="Skip confirmation prompts"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be done"),
    target_path: Optional[str] = typer.Argument(None, help="Target project directory (defaults to current directory)"),
):
    # If a subcommand is being invoked, skip the main callback logic
    if ctx.invoked_subcommand is not None:
        return

    if version:
        console.print(f"reforge v{__version__}")
        raise typer.Exit()

    if not claude and not remove:
        console.print(ctx.get_help())
        raise typer.Exit()

    target = Path(target_path) if target_path else Path.cwd()
    target = target.resolve()

    reforge_home = get_reforge_home()

    if claude:
        validate_source(reforge_home)
        validate_target(target, reforge_home)
        if update:
            do_update(target, reforge_home, dry_run)
        else:
            do_install(target, reforge_home, dry_run)
    elif remove:
        do_remove(target, force, dry_run)


# --- Script Subcommands ---


@app.command("init-project")
def cmd_init_project(
    target_path: Optional[str] = typer.Argument(None, help="Target directory"),
    name: Optional[str] = typer.Option(None, "--name", "-n", help="Override project name"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Initialize project output structure."""
    try:
        target = Path(target_path) if target_path else None
        result = init_project(target_path=target, project_name_override=name)

        if json_output:
            console.print(result.to_json())
        else:
            ok(f"Project initialized: {result.project_name}")
            info(f"  Output directory: {result.project_output_dir}")
            info(f"  Config: {result.config}")
    except ReforgeError as e:
        error(str(e))
        raise typer.Exit(1)


@app.command("check-prerequisites")
def cmd_check_prerequisites(
    require_analysis: bool = typer.Option(False, "--require-analysis", help="Require analysis.xml"),
    require_extraction: Optional[str] = typer.Option(None, "--require-extraction", help="Require specific extraction"),
    include_checkpoint: bool = typer.Option(False, "--include-checkpoint", help="Include checkpoint info"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Validate prerequisites for Reforge commands."""
    try:
        result = check_prerequisites(
            require_analysis=require_analysis,
            require_extraction=require_extraction,
            include_checkpoint=include_checkpoint,
        )

        if json_output:
            console.print(result.to_json())
        else:
            ok("Prerequisites check:")
            info(f"  Project: {result.project_name}")
            info(f"  Analysis: {result.analysis_status}")
            info(f"  Extractions: {', '.join(result.available_extractions) or 'none'}")
            if result.checkpoint:
                info(f"  Checkpoint: {result.checkpoint}")
    except ReforgeError as e:
        error(str(e))
        raise typer.Exit(1)


@app.command("checkpoint")
def cmd_checkpoint(
    action: str = typer.Argument(..., help="Action: read, create, or delete"),
    checkpoint_type: str = typer.Option("analysis", "--type", "-t", help="Checkpoint type"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Manage checkpoint state (read/create/delete)."""
    try:
        if action == "read":
            result = read_checkpoint(checkpoint_type=checkpoint_type)
            if json_output:
                console.print(result.to_json())
            else:
                if result.exists:
                    ok(f"Checkpoint: {checkpoint_type}")
                    info(f"  Total files: {result.total_files}")
                    info(f"  Processed: {result.processed_files} ({result.percentage}%)")
                    info(f"  Current: {result.current_file}")
                    info(f"  Started: {result.started_at}")
                    info(f"  Elapsed: {result.elapsed_seconds}s")
                else:
                    warn(f"No checkpoint found for type: {checkpoint_type}")

        elif action == "create":
            result = create_checkpoint(checkpoint_type=checkpoint_type)
            if json_output:
                console.print(result.to_json())
            else:
                ok(f"Checkpoint path: {result.checkpoint_file}")

        elif action == "delete":
            result = delete_checkpoint(checkpoint_type=checkpoint_type)
            if json_output:
                console.print(result.to_json())
            else:
                if result.deleted:
                    ok(f"Deleted checkpoint: {result.file}")
                else:
                    warn(f"No checkpoint to delete: {result.file}")

        else:
            error(f"Unknown action: {action}. Use read, create, or delete.")
            raise typer.Exit(1)

    except ReforgeError as e:
        error(str(e))
        raise typer.Exit(1)


@app.command("update-context")
def cmd_update_context(
    agent_type: str = typer.Argument("claude", help="Agent type: claude, gemini, copilot, cursor, windsurf"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Update agent context file with analysis results."""
    try:
        result = update_agent_context(agent_type=agent_type)

        if json_output:
            console.print(result.to_json())
        else:
            if result.updated:
                ok(f"Updated {result.context_file} with analysis results")
                info(f"  Languages: {result.languages}")
                info(f"  Frameworks: {result.frameworks or 'N/A'}")
            else:
                warn(f"Context file not found: {result.context_file} (skipped)")
    except ReforgeError as e:
        error(str(e))
        raise typer.Exit(1)


def main():
    app()


if __name__ == "__main__":
    main()
