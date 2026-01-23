# /reforge.status

> Show analysis progress, coverage statistics, and pending items

## Command Syntax

```
/reforge.status [--detailed] [--json]
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `--detailed` | No | Show file-level progress details |
| `--json` | No | Output status as JSON for tooling integration |

## Overview

This command provides visibility into the analysis state, showing:

1. Analysis progress (if in progress)
2. Extraction completion status by type
3. Pending clarifications count
4. Coverage statistics
5. Resume capability status

---

## Workflow

### Step 1: Check Analysis State

Look for analysis outputs and checkpoints:

1. **Check for active checkpoint:**
   - Path: `.reforge/memory/checkpoints/analysis-checkpoint.xml`
   - If exists: Analysis is in progress or interrupted

2. **Check for completed analysis:**
   - Path: `reforge_output/<project-name>/analysis.xml`
   - If exists: Analysis has completed at least once

3. **Check for extraction outputs:**
   - `reforge_output/<project-name>/business-rules.xml`
   - `reforge_output/<project-name>/database.xml`
   - `reforge_output/<project-name>/ui-flows.xml`
   - `reforge_output/<project-name>/workflows.xml`

4. **Check for pending clarifications:**
   - Path: `.reforge/memory/clarifications/*.xml`
   - Count pending items

### Step 2: Gather Statistics

**If analysis checkpoint exists (in-progress):**

Read checkpoint and calculate:
- Total files discovered
- Files processed
- Files remaining
- Current file being processed
- Elapsed time
- Estimated time remaining (based on average processing speed)

**If analysis.xml exists (completed):**

Read summary section and extract:
- Total files analyzed
- Languages breakdown
- File types breakdown
- Last analysis timestamp

**For each extraction type:**

If output file exists, count:
- Total items extracted
- High confidence items
- Medium confidence items
- Low confidence items (may need clarification)

### Step 3: Generate Report

#### Standard Output

```
=== Reforge Analysis Status ===
Project: [project-name]
Root: [root-path]

--- Analysis Phase ---
Status: [Not Started | In Progress | Completed]
[If in progress:]
  Progress: [X]% ([Y] of [Z] files)
  Current: [current-file-path]
  Elapsed: [HH:MM:SS]
  Estimated remaining: [HH:MM:SS]
[If completed:]
  Completed: [timestamp]
  Total files: [count]
  Coverage: [X]%

--- Extraction Status ---
| Type           | Status      | Items | Confidence         |
|----------------|-------------|-------|-------------------|
| Business Rules | [status]    | [N]   | H:[x] M:[y] L:[z] |
| Database       | [status]    | [N]   | H:[x] M:[y] L:[z] |
| UI Flows       | [status]    | [N]   | H:[x] M:[y] L:[z] |
| Workflows      | [status]    | [N]   | H:[x] M:[y] L:[z] |

--- Clarifications ---
Pending: [count] items
[If any pending:]
  Run /reforge.clarify to resolve ambiguities

--- Generated Outputs ---
| Artifact         | Status      | Last Generated |
|------------------|-------------|----------------|
| Markdown docs    | [status]    | [timestamp]    |
| User stories     | [status]    | [timestamp]    |
| Data dictionary  | [status]    | [timestamp]    |
| UML diagrams     | [status]    | [timestamp]    |

--- Next Steps ---
[Contextual recommendations based on current state]
```

#### Detailed Output (--detailed)

Add file-level information:

```
--- File Analysis Details ---
Completed files:
  src/main/java/com/app/Service.java [completed]
  src/main/java/com/app/Controller.java [completed]
  ...

Pending files:
  src/main/java/com/app/Repository.java [pending]
  src/main/java/com/app/Model.java [pending]
  ...

Skipped files:
  node_modules/... [excluded by pattern]
  build/... [excluded by pattern]
  ...

Files with errors:
  src/legacy/BrokenFile.java [encoding-error]
  ...
```

#### JSON Output (--json)

```json
{
  "project": {
    "name": "[project-name]",
    "root": "[root-path]"
  },
  "analysis": {
    "status": "completed|in-progress|not-started",
    "progress": {
      "total": 1000,
      "processed": 1000,
      "skipped": 50,
      "errors": 2,
      "percentage": 100
    },
    "timing": {
      "started": "2024-01-15T10:00:00Z",
      "completed": "2024-01-15T11:30:00Z",
      "duration_seconds": 5400
    },
    "languages": {
      "java": { "files": 500, "lines": 50000 },
      "javascript": { "files": 300, "lines": 25000 }
    }
  },
  "extractions": {
    "business-rules": {
      "status": "completed",
      "count": 150,
      "confidence": { "high": 100, "medium": 40, "low": 10 }
    },
    "database": {
      "status": "not-started",
      "count": 0
    },
    "ui-flows": {
      "status": "not-started",
      "count": 0
    },
    "workflows": {
      "status": "not-started",
      "count": 0
    }
  },
  "clarifications": {
    "pending": 5,
    "resolved": 10
  },
  "generated": {
    "markdown": {
      "status": "not-generated"
    },
    "user-stories": {
      "status": "not-generated"
    }
  }
}
```

### Step 4: Provide Recommendations

Based on current state, suggest next steps:

**If analysis not started:**
```
Next steps:
→ Run /reforge.analyze to start codebase inventory
```

**If analysis in progress:**
```
Next steps:
→ Wait for analysis to complete, or
→ Run /reforge.analyze --resume to continue if interrupted
```

**If analysis completed, no extractions:**
```
Next steps:
→ Run /reforge.extract business-rules to extract business logic
→ Run /reforge.extract database to extract data model
→ Run /reforge.extract ui to extract UI components
→ Run /reforge.extract workflows to trace execution paths
```

**If extractions completed, clarifications pending:**
```
Next steps:
→ Run /reforge.clarify to resolve [N] pending ambiguities
→ This will improve confidence levels across extractions
```

**If extractions completed, no clarifications:**
```
Next steps:
→ Run /reforge.generate markdown to create documentation
→ Run /reforge.generate user-stories to create modernization backlog
→ Run /reforge.generate uml to create diagrams
```

**If all complete:**
```
Analysis complete! All extractions and documentation generated.

Available commands:
→ /reforge.reanalyze [path] - Re-analyze specific files
→ /reforge.generate [format] - Regenerate documentation
→ /reforge.clarify - Review and update clarifications
```

---

## Status Values

### Analysis Status

| Status | Meaning |
|--------|---------|
| `not-started` | No analysis has been run |
| `in-progress` | Analysis checkpoint exists, can be resumed |
| `completed` | analysis.xml exists with completed status |
| `partial` | Analysis completed but some files had errors |

### Extraction Status

| Status | Meaning |
|--------|---------|
| `not-started` | Extraction output file does not exist |
| `completed` | Output file exists with items |
| `partial` | Output exists but analysis has been updated since |

### Generation Status

| Status | Meaning |
|--------|---------|
| `not-generated` | Output does not exist |
| `generated` | Output exists |
| `stale` | Output exists but extractions have been updated since |

---

## Reading Progress from Checkpoint

Checkpoint path: `.reforge/memory/checkpoints/analysis-checkpoint.xml`

Extract:
- `<progress><total-files>` → Total count
- `<progress><processed-files>` → Completed count
- `<progress><current-file>` → Currently processing
- `<timing><started-at>` → Start timestamp
- `<timing><elapsed-seconds>` → Time elapsed

Calculate:
- Percentage: `(processed / total) * 100`
- Average time per file: `elapsed / processed`
- Estimated remaining: `(total - processed) * average`

---

## Reading Statistics from Analysis Output

Analysis path: `reforge_output/<project-name>/analysis.xml`

Extract from `<summary>`:
- `total-files` attribute
- `total-lines` attribute
- `analyzed` attribute
- `skipped` attribute
- `<languages>/<language>` for each language
- `<file-types>/<type>` for each type

---

## Reading Extraction Statistics

For each extraction file, if it exists:

**business-rules.xml:**
- Count `<rule>` elements
- Group by `@confidence` attribute

**database.xml:**
- Count `<entity>` and `<interaction>` elements
- Group by `@confidence` attribute

**ui-flows.xml:**
- Count `<screen>` and `<component>` elements
- Group by `@confidence` attribute

**workflows.xml:**
- Count `<workflow>` elements
- Group by `@confidence` attribute

---

## Examples

### Status After Fresh Analysis

```
User: /reforge.status

Agent:
=== Reforge Analysis Status ===
Project: legacy-ecommerce
Root: /opt/codebase

--- Analysis Phase ---
Status: Completed
Completed: 2024-01-15T11:30:00Z
Total files: 1,247
Coverage: 100%

--- Extraction Status ---
| Type           | Status       | Items | Confidence         |
|----------------|--------------|-------|-------------------|
| Business Rules | Not Started  | -     | -                 |
| Database       | Not Started  | -     | -                 |
| UI Flows       | Not Started  | -     | -                 |
| Workflows      | Not Started  | -     | -                 |

--- Clarifications ---
Pending: 0 items

--- Generated Outputs ---
| Artifact         | Status         | Last Generated |
|------------------|----------------|----------------|
| Markdown docs    | Not Generated  | -              |
| User stories     | Not Generated  | -              |
| Data dictionary  | Not Generated  | -              |
| UML diagrams     | Not Generated  | -              |

--- Next Steps ---
→ Run /reforge.extract business-rules to extract business logic
→ Run /reforge.extract database to extract data model
→ Run /reforge.extract ui to extract UI components
→ Run /reforge.extract workflows to trace execution paths
```

### Status During Analysis

```
User: /reforge.status

Agent:
=== Reforge Analysis Status ===
Project: legacy-ecommerce
Root: /opt/codebase

--- Analysis Phase ---
Status: In Progress
Progress: 45% (562 of 1,247 files)
Current: src/main/java/com/app/OrderService.java
Elapsed: 00:32:15
Estimated remaining: 00:39:28

--- Next Steps ---
→ Wait for analysis to complete, or
→ Run /reforge.analyze --resume to continue if interrupted
```

### Status After Full Extraction

```
User: /reforge.status --detailed

Agent:
=== Reforge Analysis Status ===
Project: legacy-ecommerce
Root: /opt/codebase

--- Analysis Phase ---
Status: Completed
Completed: 2024-01-15T11:30:00Z
Total files: 1,247
Coverage: 100%

--- Extraction Status ---
| Type           | Status    | Items | Confidence         |
|----------------|-----------|-------|-------------------|
| Business Rules | Completed | 156   | H:98 M:45 L:13    |
| Database       | Completed | 89    | H:72 M:15 L:2     |
| UI Flows       | Completed | 45    | H:38 M:5 L:2      |
| Workflows      | Completed | 23    | H:18 M:4 L:1      |

--- Clarifications ---
Pending: 13 items
  Run /reforge.clarify to resolve ambiguities

--- File Analysis Details ---
Languages:
  Java: 650 files (52%)
  JavaScript: 312 files (25%)
  SQL: 125 files (10%)
  HTML: 89 files (7%)
  Other: 71 files (6%)

Low confidence items requiring review:
  - BR-045: Unclear discount calculation (src/pricing/Discount.java:78)
  - BR-089: Magic number in validation (src/validate/OrderValidator.java:156)
  - UI-012: Ambiguous button handler (webapp/orders/list.jsp:45)
  ...

--- Next Steps ---
→ Run /reforge.clarify to resolve 13 pending ambiguities
→ This will improve confidence levels across extractions
```
