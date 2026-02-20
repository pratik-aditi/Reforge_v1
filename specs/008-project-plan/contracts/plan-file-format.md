# Contract: Project Plan File Format

**Feature**: 008-project-plan

## File Location

`.reforge/memory/project-plan.md`

## Format Specification

### Metadata Header

```markdown
# Project Plan

**Project**: <project-name>
**Created**: YYYY-MM-DD
**Last Updated**: YYYY-MM-DD
```

- `Project`: From config.json `project.name` or project-context.md
- `Created`: Date of initial plan creation
- `Last Updated`: Updated on every modification (add items, mark completions)

### Section: Setup (required)

```markdown
## Setup

- [ ] Initialize project context <!-- reforge:init -->
- [ ] Analyze codebase <!-- reforge:analyze -->
- [ ] Generate extraction profile <!-- reforge:profile -->
```

Always present. Items may be pre-checked if commands were already run.

### Section: Workflow Group (0..N)

```markdown
## <Extraction Type Display Name>

- [ ] Extract <type> <!-- reforge:extract:<slug> -->
- [ ] Clarify <type> extractions <!-- reforge:clarify:<slug> -->
- [ ] Audit <type> extractions <!-- reforge:audit:<slug> -->
- [ ] Fix <type> extraction issues <!-- reforge:fix:<slug> -->
- [ ] Generate <type> documentation <!-- reforge:generate:<slug> -->
- [ ] Audit <type> generated docs <!-- reforge:audit-generated:<slug> -->
- [ ] Fix <type> generated doc issues <!-- reforge:fix-generated:<slug> -->
```

One section per declared extraction type. Ordered as declared by user.

### Section: Custom Tasks (optional)

```markdown
## Custom Tasks

- [ ] <user-defined task description> <!-- reforge:custom:<slug> -->
```

Present only if user declares custom tasks.

## Plan Item Format

### Uncompleted

```
- [ ] <human-readable description> <!-- reforge:<command>[:<type>] -->
```

### Completed

```
- [x] <human-readable description> <!-- reforge:<command>[:<type>] --> *(completed: YYYY-MM-DD)*
```

## Tag Pattern

```
<!-- reforge:<command>[:<type>] -->
```

### Tag Components

| Component | Pattern | Examples |
|-----------|---------|---------|
| command | `[a-z][a-z-]*` | `init`, `extract`, `audit-generated`, `fix-generated`, `custom` |
| type | `[a-z][a-z-]*` | `business-rules`, `database`, `ui`, `workflows` |

### Tag Uniqueness

Each tag MUST appear at most once in the plan file. Duplicate tags are an error condition.

## Parsing Rules for Step 0.7

### Finding an item

1. Read the entire plan file as a string
2. Search for `<!-- reforge:<command_tag> -->` using string contains
3. If found: the line containing the tag is the target item

### Checking completion status

1. Inspect the target line
2. If it starts with `- [x]` (after optional whitespace): item is completed
3. If it starts with `- [ ]`: item is pending

### Marking complete

1. Replace `- [ ]` with `- [x]` on the target line
2. Append ` *(completed: YYYY-MM-DD)*` after the closing `-->` tag
3. Update the `**Last Updated**` metadata line to today's date
4. Write the modified content back to the file

### Progress counting

1. Count all lines matching pattern `^- \[([ x])\]`
2. Total items = count of all matches
3. Completed items = count of matches with `[x]`
4. Percentage = (completed / total) * 100, rounded to nearest integer
