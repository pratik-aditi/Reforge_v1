# Using Claude Code Teams

Reforge commands can run with Claude Code's agent teams feature, spawning multiple sub-agents to work in parallel. This dramatically speeds up extraction and analysis of large codebases.

## What Are Claude Code Teams?

Claude Code can create teams of sub-agents that work concurrently on different parts of a task. A lead agent coordinates the work, assigns tasks, and collects results. Each sub-agent gets its own context and tools.

For Reforge, this means you can:

- Extract multiple types simultaneously (business-rules, database, workflows in parallel)
- Split large file sets across agents for faster analysis
- Run audit and fix cycles concurrently across extraction types

## Setup

No special configuration is required. Claude Code's team features (TeamCreate, Task, SendMessage) are available by default. Reforge commands detect team capabilities automatically.

## Parallel Extractions

The most common use case is running multiple extraction types at the same time. Instead of extracting sequentially:

```
/reforge.extract business-rules
/reforge.extract database
/reforge.extract workflows
/reforge.extract ui
```

Ask Claude Code to run them in parallel:

```
Extract all four core types in parallel: business-rules, database, workflows, and ui
```

Claude Code will spawn a team with one agent per extraction type, each running independently against the analyzed codebase.

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

## Manual Team Orchestration

You can ask Claude Code to orchestrate any Reforge workflow as a team. Here are practical examples:

### Parallel extraction campaign

```
Create a team to run all 10 extraction types in parallel against my analyzed codebase.
Run business-rules, database, ui, workflows, call-sites, dependencies,
functional-requirements, non-functional, architecture, and issues simultaneously.
```

### Parallel audit and fix

```
Run /reforge.audit for each extraction type in parallel, then consolidate
the results and run /reforge.fix for any types that need corrections.
```

### Scoped generation

```
Generate html documentation for business-rules, database, and workflows
in parallel using separate agents.
```

## How It Works Under the Hood

When Claude Code creates a team for Reforge work:

1. **Lead agent** reads the project context (`.reforge/config.json`, analysis inventory)
2. **Worker agents** are spawned with specific assignments (extraction type, file set, or audit scope)
3. Each worker runs its assigned `/reforge.*` command independently
4. Workers write output to the standard `reforge_output/` directory
5. **Lead agent** collects results, checks for conflicts, and reports status

```
Lead Agent
├── Worker 1: /reforge.extract business-rules
├── Worker 2: /reforge.extract database
├── Worker 3: /reforge.extract workflows
└── Worker 4: /reforge.extract ui
```

!!! warning "File conflicts"
    Each extraction type writes to its own XML file, so parallel extractions don't conflict. However, avoid running the same extraction type in multiple agents simultaneously -- they would overwrite each other's output.

## Recommended Team Patterns

| Task | Team Size | Strategy |
|------|-----------|----------|
| Full extraction (all 10 types) | 4-5 agents | Batch types into groups of 2-3 per agent |
| Glossary extraction | 3 agents | Use `--team-size 3` (built-in) |
| Audit all types | 3-4 agents | One agent per 2-3 extraction types |
| Generate all formats | 2-3 agents | Group by output format |
| Large codebase analysis | 2-3 agents | Split by directory/module |

!!! note
    Team orchestration is a Claude Code feature. GitHub Copilot does not currently support multi-agent teams. For Copilot, run commands sequentially.

## Configuration Tips

### CLAUDE.md integration

Add team guidance to your project's `CLAUDE.md` to help Claude Code make better orchestration decisions:

```markdown
## Reforge Team Configuration

- Default team size for extractions: 4 agents
- Always run /reforge.init and /reforge.analyze before spawning extraction teams
- Preferred extraction batching:
  - Agent 1: business-rules, functional-requirements
  - Agent 2: database, dependencies
  - Agent 3: ui, workflows, call-sites
  - Agent 4: non-functional, architecture, issues
```

### Settings permissions

The `settings.local.json` installed by `reforge --claude` already grants the necessary permissions for `reforge-scripts` commands. Sub-agents inherit these permissions from the project configuration.

## Troubleshooting

**Agents can't find analysis inventory**
Run `/reforge.analyze` before spawning a team. All agents need `reforge_output/<project>/analysis/analysis.xml` to exist.

**Extraction output is incomplete**
Check that each agent was assigned a different extraction type. Two agents running the same type will overwrite each other.

**Context limits reached**
Reduce `--team-size` or batch fewer extraction types per agent. Each agent loads the analysis inventory into its context.

**Team not spawning**
Ensure you're running in Claude Code (not Copilot). Team orchestration requires Claude Code's TeamCreate and Task tools.
