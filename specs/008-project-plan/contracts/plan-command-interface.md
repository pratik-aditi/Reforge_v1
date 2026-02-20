# Contract: /reforge.plan Command Interface

**Feature**: 008-project-plan

## Command Syntax

```
/reforge.plan [arguments] [--status]
```

## Input Contract

| Input | Source | Required | Description |
|-------|--------|----------|-------------|
| `arguments` | User text | No | Natural language describing items to add (e.g., `"add database extraction and UML diagrams"`) |
| `--status` | Flag | No | Display progress summary without modifying the plan |
| `.reforge/config.json` | File | No | Project name for metadata |
| `.reforge/memory/project-context.md` | File | No | Project context for suggestions |
| `.reforge/memory/extraction-profile.md` | File | No | Extraction profile for targeted suggestions |
| `$PROJECT_OUTPUT_DIR/analysis/analysis.xml` | File | No | Analysis results for auto-suggestions |
| `.reforge/memory/project-plan.md` | File | No | Existing plan (for add/status modes) |

## Output Contract

| Output | Path | Format | When |
|--------|------|--------|------|
| Project plan | `.reforge/memory/project-plan.md` | Structured markdown | Create or Add mode |
| Status display | stdout | Formatted text | --status mode or Add mode (preamble) |

## Behavioral Modes

### Mode 1: Create (no existing plan, no `--status`)

1. Read available context (config, project-context, profile, analysis)
2. If arguments provided: parse intent, generate plan items directly
3. If no arguments: interactively gather extraction types, audit scope, generation targets
4. Suggest items based on analysis/profile data (if available)
5. Write `.reforge/memory/project-plan.md`

### Mode 2: Add (existing plan present, arguments provided)

1. Read existing plan, preserving all content and completion status
2. Parse arguments to determine new items
3. Check for duplicates via tag matching
4. Append new items to appropriate sections
5. Update `Last Updated` metadata
6. Write updated plan

### Mode 3: Interactive Review (existing plan present, no arguments, no `--status`)

1. Read existing plan
2. Display current status (completed/total per section)
3. Ask user: add new items or review the plan?
4. If adding: proceed as Mode 2 with interactive gathering
5. If reviewing: display detailed plan and suggest next steps

### Mode 4: Status (--status flag)

1. Read existing plan
2. Count completed/total per section
3. Display summary with percentages
4. If 100% complete: suggest final review and handoff
5. Do NOT modify the plan file

## Error Handling

| Condition | Behavior |
|-----------|----------|
| `.reforge/memory/` does not exist | Instruct user to run `/reforge.init` first |
| Plan file corrupted/invalid markdown | Attempt best-effort parsing; preserve what can be read; warn user |
| Duplicate item requested | Inform user, show existing item status, offer to skip |
| Unsupported extraction type | Accept as custom task — no validation against known types |
| No analysis/profile available | Proceed with manual-only input, note suggestion availability |
