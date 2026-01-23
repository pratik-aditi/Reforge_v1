# /reforge.init

> Initialize project context for Reforge analysis

## Command Syntax

```
/reforge.init [--update]
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `--update` | No | Update existing project context (re-run questions) |

## Overview

This command collects project-specific information to guide all subsequent
Reforge analysis. It creates `.reforge/memory/project-context.md` which is
read by all commands as supplemental context alongside the constitution.

## Workflow

### Step 1: Check Existing Context

Read `.reforge/memory/project-context.md` if it exists. If present and
`--update` was not specified, ask the user if they want to update it or
keep the existing context.

### Step 2: Gather Project Identity

Ask the user:
1. What is the project name?
2. What does this project do? (1-2 sentence description)
3. What is the root path to analyze? (e.g., `./`, `./src`, `./legacy`)

### Step 3: Gather Technology Stack

Ask the user:
1. What programming languages are used? (and versions if known)
2. What frameworks are used? (and versions if known)
3. What build system is used?
4. What database(s) are used?
5. Any other notable technologies? (messaging, caching, APIs, etc.)

### Step 4: Gather Domain Knowledge

Ask the user:
"Describe the business domain this application serves. Include key
business concepts and terminology that will help with analysis.
(Press enter twice to finish)"

### Step 5: Gather Analysis Guidelines

Ask the user:
"Are there any specific analysis guidelines? For example:
- Directories or packages to focus on or ignore
- Known patterns in the codebase
- Areas of particular interest or concern
(Press enter twice to finish)"

### Step 6: Gather Custom Rules

Ask the user:
"Any additional rules the AI should follow when analyzing this codebase?
For example:
- Architectural patterns (where business logic lives, data access patterns)
- Naming conventions
- Known technical debt or areas to flag
(Press enter twice to finish)"

### Step 7: Write Project Context

Write all gathered information to `.reforge/memory/project-context.md`
using the following format:

```markdown
# Project Context

## Project Identity
- **Name**: <project name>
- **Description**: <what this project does>
- **Root Path**: <path to analyze>

## Technology Stack
- **Languages**: <languages and versions>
- **Frameworks**: <frameworks and versions>
- **Build System**: <build system>
- **Database**: <database(s)>
- **Other**: <other technologies>

## Domain Knowledge
<business domain context>

## Analysis Guidelines
<project-specific analysis guidance>

## Custom Rules
<additional rules for the AI>
```

### Step 8: Update Configuration

Update `.reforge/config.json`:
- Set `project.name` to the provided name
- Set `project.description` to the provided description
- Set `project.root` to the provided root path

### Step 9: Confirm

Display a summary of what was saved and remind the user that they can
run `/reforge.analyze` next to begin codebase analysis.
