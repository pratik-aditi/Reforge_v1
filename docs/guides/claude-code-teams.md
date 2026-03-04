# Using Claude Code Teams

Reforge commands can run with Claude Code's [agent teams](https://code.claude.com/docs/en/agent-teams) feature, spawning multiple teammates to work in parallel. This dramatically speeds up extraction and analysis of large codebases.

## What Are Claude Code Teams?

Agent teams let you coordinate multiple Claude Code instances working together. One session acts as the **team lead**, coordinating work, assigning tasks, and synthesizing results. **Teammates** work independently, each in its own context window, and communicate directly with each other.

Unlike [sub-agents](https://code.claude.com/docs/en/sub-agents) (which run within a single session and only report back), teammates are full Claude Code sessions that can read files, write files, run commands, and message each other.

For Reforge, this means you can:

- Extract multiple types simultaneously (business-rules, database, workflows in parallel)
- Split large file sets across agents for faster analysis
- Run audit and fix cycles concurrently across extraction types

## Enabling Agent Teams

!!! warning "Experimental Feature"
    Agent teams are experimental and disabled by default. See the [official documentation](https://code.claude.com/docs/en/agent-teams) for the latest status and known limitations.

### Step 1: Enable the feature flag

Add the following to your Claude Code `settings.json`:

```json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  }
}
```

You can edit this file at `~/.claude/settings.json` (global) or `.claude/settings.json` (project-level).

Alternatively, set it as an environment variable before launching Claude Code:

```bash
export CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1
claude
```

### Step 2: Choose a display mode (optional)

Agent teams support two display modes:

| Mode | Description | Requirement |
|------|-------------|-------------|
| **In-process** (default) | All teammates run inside your main terminal. Use `Shift+Down` to cycle through them. | Any terminal |
| **Split panes** | Each teammate gets its own pane. See everyone's output at once. | tmux or iTerm2 |

To set split-pane mode, add to your `settings.json`:

```json
{
  "teammateMode": "tmux"
}
```

Or pass it as a flag:

```bash
claude --teammate-mode tmux
```

### Step 3: Verify it works

Start Claude Code and ask it to create a simple team:

```
Create an agent team with 2 teammates to explore this project.
One should look at the directory structure, the other at the tech stack.
```

If teammates spawn successfully, you're ready to use teams with Reforge.

## Using Teams with Reforge

### Parallel extractions

The most common use case is running multiple extraction types at the same time. Instead of extracting sequentially:

```
/reforge.extract business-rules
/reforge.extract database
/reforge.extract workflows
/reforge.extract ui
```

Ask Claude Code to run them in parallel:

```
Create a team to extract all four core types in parallel:
business-rules, database, workflows, and ui
```

Claude Code spawns a team with one teammate per extraction type, each running independently against the analyzed codebase.

### Full extraction campaign

```
Create a team to run all 10 extraction types in parallel against my analyzed codebase.
Run business-rules, database, ui, workflows, call-sites, dependencies,
functional-requirements, non-functional, architecture, and issues.
Batch them into groups of 2-3 per teammate.
```

### Parallel audit and fix

```
Run /reforge.audit for each extraction type in parallel, then consolidate
the results and run /reforge.fix for any types that need corrections.
```

### Scoped generation

```
Generate html documentation for business-rules, database, and workflows
in parallel using separate teammates.
```

## The `--team-size` Flag

Some Reforge commands have built-in team support via the `--team-size` flag. The glossary command is the primary example:

```
/reforge.glossary --team-size 4
```

This spawns 4 worker agents that partition the source files into zones and process them in parallel. The lead agent collects and deduplicates results.

| Value | Behavior |
|-------|----------|
| `--team-size 1` | Sequential processing (no team orchestration) |
| `--team-size 3` | Default -- 3 worker agents |
| `--team-size 6` | Maximum -- 6 worker agents |

!!! tip
    Start with the default (`3`) and increase only if you have a very large codebase. More agents means more concurrent file reads, which can hit context limits faster.

## How It Works

When Claude Code creates a team for Reforge work:

1. **Lead agent** reads the project context (`.reforge/config.json`, analysis inventory)
2. **Teammates** are spawned with specific assignments (extraction type, file set, or audit scope)
3. Each teammate runs its assigned `/reforge.*` command independently
4. Teammates write output to the standard `reforge_output/` directory
5. **Lead agent** collects results, checks for conflicts, and reports status

```
Lead Agent
├── Teammate 1: /reforge.extract business-rules
├── Teammate 2: /reforge.extract database
├── Teammate 3: /reforge.extract workflows
└── Teammate 4: /reforge.extract ui
```

Teams and tasks are stored locally:

- **Team config**: `~/.claude/teams/{team-name}/config.json`
- **Task list**: `~/.claude/tasks/{team-name}/`

!!! warning "File conflicts"
    Each extraction type writes to its own XML file, so parallel extractions don't conflict. However, avoid running the same extraction type in multiple agents simultaneously -- they would overwrite each other's output.

## Recommended Team Patterns

| Task | Team Size | Strategy |
|------|-----------|----------|
| Full extraction (all 10 types) | 4-5 teammates | Batch types into groups of 2-3 per teammate |
| Glossary extraction | 3 teammates | Use `--team-size 3` (built-in) |
| Audit all types | 3-4 teammates | One teammate per 2-3 extraction types |
| Generate all formats | 2-3 teammates | Group by output format |
| Large codebase analysis | 2-3 teammates | Split by directory/module |

!!! tip "Sizing guidance"
    Start with 3-5 teammates for most workflows. Having 5-6 tasks per teammate keeps everyone productive. Three focused teammates often outperform five scattered ones.

!!! note
    Team orchestration is a Claude Code feature. GitHub Copilot does not currently support multi-agent teams. For Copilot, run commands sequentially.

## Configuration Tips

### CLAUDE.md integration

Teammates read your project's `CLAUDE.md` automatically. Add team guidance to help Claude Code make better orchestration decisions:

```markdown
## Reforge Team Configuration

- Default team size for extractions: 4 teammates
- Always run /reforge.init and /reforge.analyze before spawning extraction teams
- Preferred extraction batching:
  - Teammate 1: business-rules, functional-requirements
  - Teammate 2: database, dependencies
  - Teammate 3: ui, workflows, call-sites
  - Teammate 4: non-functional, architecture, issues
```

### Require plan approval

For complex or risky extraction work, you can require teammates to plan before executing:

```
Spawn teammates to extract all types in parallel.
Require plan approval before they make any changes.
```

The lead reviews each teammate's plan and approves or rejects it with feedback before they proceed.

### Permissions

The `settings.local.json` installed by `reforge --claude` grants permissions for `reforge-scripts` commands. Teammates inherit the lead's permission settings. To reduce permission prompts during team runs, pre-approve common operations in your [permission settings](https://code.claude.com/docs/en/permissions).

## Interacting with Teammates

You can message any teammate directly without going through the lead:

- **In-process mode**: `Shift+Down` to cycle through teammates, type to send a message
- **Split-pane mode**: Click into a teammate's pane to interact directly

Press `Ctrl+T` to toggle the shared task list view.

## Troubleshooting

**Agents can't find analysis inventory**
Run `/reforge.analyze` before spawning a team. All teammates need `reforge_output/<project>/analysis/analysis.xml` to exist.

**Extraction output is incomplete**
Check that each teammate was assigned a different extraction type. Two teammates running the same type will overwrite each other.

**Context limits reached**
Reduce team size or batch fewer extraction types per teammate. Each teammate loads the analysis inventory into its context.

**Team not spawning**
Verify the feature flag is set: check `~/.claude/settings.json` for `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS: "1"`. Ensure you're running in Claude Code (not Copilot).

**Teammates not visible**
In in-process mode, press `Shift+Down` to cycle through active teammates. They may be running but not displayed.

**Permission prompts interrupting work**
Pre-approve `reforge-scripts` and common file operations in your permission settings before spawning the team.

## Further Reading

- [Agent Teams documentation](https://code.claude.com/docs/en/agent-teams) -- Official Claude Code reference
- [Sub-agents documentation](https://code.claude.com/docs/en/sub-agents) -- Lighter-weight alternative for focused tasks
- [Permissions](https://code.claude.com/docs/en/permissions) -- Configure permissions for team workflows
- [Settings reference](https://code.claude.com/docs/en/settings) -- All Claude Code configuration options
