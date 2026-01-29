# /reforge.reanalyze

> Re-analyze specific files or directories without full re-processing

## Command Syntax

```
/reforge.reanalyze <path> [--type <extraction>] [--force]
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `path` | Yes | File or directory path to re-analyze |
| `--type` | No | Limit to extraction type: `analysis`, `business-rules`, `database`, `ui`, `workflows` |
| `--force` | No | Re-analyze even if file hash hasn't changed |

## Overview

This command enables incremental re-analysis:

1. Re-processes only specified files
2. Updates existing XML outputs without affecting other entries
3. Preserves cross-references and relationships
4. Maintains extraction history for comparison

## Prerequisites

- Initial analysis must be completed (`$ANALYSIS_DIR/analysis.xml` exists)
- Target files must be within the analyzed project root

---

## Workflow

### Step 0: Check Prerequisites

Run the prerequisites script to validate state and resolve paths:

```bash
reforge-scripts check-prerequisites --json --require-analysis
```

This returns JSON with resolved variables:
```json
{"PROJECT_NAME":"...","REPO_ROOT":"...","PROJECT_OUTPUT_DIR":"...","CONFIG":"...","ANALYSIS_STATUS":"completed","AVAILABLE_EXTRACTIONS":[...],"CHECKPOINT":null,"CLARIFICATIONS_DIR":"..."}
```

Use `$PROJECT_OUTPUT_DIR` for all output paths in subsequent steps.

Assign subdirectory variables:
```
$ANALYSIS_DIR = $PROJECT_OUTPUT_DIR/analysis
$EXTRACTIONS_DIR = $PROJECT_OUTPUT_DIR/extractions
```

### Step 0.5: Load Project Context

If `.reforge/memory/project-context.md` exists, read it now. Use its contents as
supplemental guidance throughout this command's execution:
- **Technology Stack**: Informs language/framework detection and pattern recognition
- **Domain Knowledge**: Provides business context for naming and categorization
- **Analysis Guidelines**: Directs focus and exclusions beyond config.json
- **Custom Rules**: Additional rules to follow alongside the constitution

### Step 1: Validate Targets

1. **Check path exists:**
   - If file: Validate file exists and is readable
   - If directory: Validate directory exists

2. **Check within project scope:**
   - Path must be within project root from `$ANALYSIS_DIR/analysis.xml`
   - Path must not match exclusion patterns

3. **Resolve file list:**
   - If file: Single file
   - If directory: All files within (respecting exclusions)

### Step 2: Check for Changes

For each target file:

1. **Read current file hash**
2. **Compare with stored hash** from `$ANALYSIS_DIR/analysis.xml`
3. **Determine action:**
   - Hash changed: Mark for re-analysis
   - Hash same + `--force`: Mark for re-analysis
   - Hash same (no force): Skip (already current)

Report:
```
Checking 15 files for changes...

Changed:
- src/service/OrderService.java (modified)
- src/model/Order.java (modified)

Unchanged (skipping):
- src/controller/OrderController.java
- src/repository/OrderRepository.java
...

Re-analyzing 2 files...
```

### Step 3: Backup Current State

Before modifying outputs:

1. **Create backup** of affected XML entries
2. **Store in** `.reforge/memory/backups/`
3. **Include timestamp** for rollback capability

```
Backing up current extractions...
- $ANALYSIS_DIR/analysis.xml entries: 2 files
- $EXTRACTIONS_DIR/business-rules.xml entries: 5 rules
- $EXTRACTIONS_DIR/database.xml entries: 3 interactions
```

### Step 4: Re-analyze Files

For each changed file:

#### Update Analysis Entry

1. **Re-read file content**
2. **Re-detect language and components**
3. **Update hash**
4. **Update timestamp**
5. **Replace entry in `$ANALYSIS_DIR/analysis.xml`**

#### Update Extractions

If `--type` is specified, only update that type.
Otherwise, update all extraction types:

**Business Rules:**
1. Find existing rules from this file
2. Remove old rules (keep IDs for reference tracking)
3. Re-extract rules from file
4. Add new rules with new IDs or updated existing IDs
5. Update `$EXTRACTIONS_DIR/business-rules.xml`

**Database:**
1. Find existing entities/interactions from this file
2. Re-extract with current content
3. Update `$EXTRACTIONS_DIR/database.xml`

**UI:**
1. Find existing screens/components from this file
2. Re-extract with current content
3. Update `$EXTRACTIONS_DIR/ui-flows.xml`

**Workflows:**
1. Find workflows that include this file in their path
2. Re-trace affected workflows
3. Update `$EXTRACTIONS_DIR/workflows.xml`

### Step 5: Update Cross-References

After re-analysis, verify cross-references:

1. **Rule references in workflows:**
   - Check if rule IDs still exist
   - Update or remove broken references

2. **Database references:**
   - Verify entity/interaction references
   - Update changed IDs

3. **UI references:**
   - Check component references in workflows
   - Update navigation flows if screens changed

Report broken references:
```
Cross-reference check:
- WF-001 references BR-045: ✓ Valid
- WF-003 references BR-089: ⚠ Rule removed
  → Updating workflow to remove reference
```

### Step 6: Update Clarifications

Check if re-analysis affects pending clarifications:

1. **Resolved clarifications:**
   - If underlying code changed, may need re-clarification
   - Flag for review if patterns differ significantly

2. **Pending clarifications:**
   - If code addressed, mark as potentially resolved
   - Update context if code changed but issue remains

### Step 7: Update Generated Outputs

If any generated documentation exists, mark as stale:

```
Generated outputs may be stale:
- $GENERATED_DIR/documentation.md (affected by BR-045, BR-089)
- $GENERATED_DIR/user-stories.md (affected by WF-001)

Run /reforge.generate <format> to regenerate.
```

### Step 8: Report Results

```
=== Re-analysis Complete ===

Files processed: 2
- src/service/OrderService.java
- src/model/Order.java

Updates:
- $ANALYSIS_DIR/analysis.xml: 2 file entries updated
- $EXTRACTIONS_DIR/business-rules.xml:
  - Removed: 1 (obsolete rule)
  - Updated: 3 (logic changes)
  - Added: 1 (new rule detected)
- $EXTRACTIONS_DIR/database.xml:
  - Updated: 2 interactions
- $EXTRACTIONS_DIR/workflows.xml:
  - Updated: 1 workflow (WF-001)

Cross-references:
- 1 broken reference fixed

Clarifications:
- 1 resolved clarification may need review

Time: 00:00:45

Next steps:
- Run /reforge.status to see updated statistics
- Run /reforge.clarify to review affected clarifications
- Run /reforge.generate markdown to update documentation
```

---

## Change Detection

### File Hash Calculation

Hash is calculated from file content:
- Algorithm: SHA-256 (or MD5 for speed)
- Excludes: Whitespace-only changes (configurable)
- Stored in: `$ANALYSIS_DIR/analysis.xml` file entry `hash` attribute

### Change Types

| Change Type | Detection | Action |
|-------------|-----------|--------|
| Content modified | Hash differs | Full re-extraction |
| File renamed | Path differs, hash matches | Update path only |
| File deleted | Path missing | Mark entries as orphaned |
| File added | Path new | Add to analysis |

---

## Preserving History

### Extraction History

Store previous versions for comparison:

```
.reforge/memory/history/
├── analysis/
│   ├── 2024-01-15T10-30-00.xml
│   └── 2024-01-15T14-00-00.xml
├── business-rules/
│   ├── BR-045-v1.xml
│   └── BR-045-v2.xml
└── ...
```

### Diff Reporting

Show what changed:

```
Changes in BR-045:
- Description: "Discount logic" → "Volume discount: 10% over $100"
- Logic: Updated threshold from 50 to 100
- Confidence: low → high (after clarification)
- Lines: 45-50 → 48-55 (code moved)
```

---

## Selective Re-analysis

### By Extraction Type

```
/reforge.reanalyze src/service/ --type business-rules
```

Only re-extracts business rules from files in the directory.

### By File Pattern

```
/reforge.reanalyze "src/**/*Service.java"
```

Re-analyzes all service files matching the pattern.

### Force Re-analysis

```
/reforge.reanalyze src/service/OrderService.java --force
```

Re-analyzes even if file hasn't changed (useful after clarifications).

---

## Error Handling

### File Access Errors

```
Error: Cannot read src/service/DeletedService.java
Action: Marking file as removed in analysis.xml
        Orphaning related extractions (BR-120, DB-045)
```

### Circular Reference Detection

If re-analysis creates circular references:
- Log warning
- Preserve both references
- Flag for manual review

### Extraction Conflicts

If re-extraction produces conflicting IDs:
- Generate new IDs for new items
- Preserve old IDs for updated items
- Log ID mapping for traceability

---

## Examples

### Re-analyze Single File

```
User: /reforge.reanalyze src/service/OrderService.java

Agent: Checking src/service/OrderService.java...
File hash changed (last analyzed: 2024-01-15T10:30:00Z)

Re-analyzing...
- Updated analysis entry
- Found 2 modified business rules
- Found 1 new business rule
- Updated 3 database interactions

Complete! Updates saved.
```

### Re-analyze Directory

```
User: /reforge.reanalyze src/service/

Agent: Scanning src/service/...
Found 12 files.

Checking for changes...
- 3 files modified
- 9 files unchanged

Re-analyzing modified files...
[1/3] OrderService.java - 5 extractions updated
[2/3] CustomerService.java - 2 extractions updated
[3/3] ProductService.java - 3 extractions updated

Complete! 10 extractions updated across 3 files.
```

### Re-analyze After Code Changes

```
User: /reforge.reanalyze src/model/Order.java --type database

Agent: Re-analyzing database extractions from src/model/Order.java...

Changes detected in entity definition:
- Entity E-001 (orders):
  - Added column: discount_code (varchar)
  - Modified column: total (decimal(10,2) → decimal(12,2))

Updated $EXTRACTIONS_DIR/database.xml with new schema.

Note: Related SQL interactions may need review.
Run /reforge.extract database --files "src/**/*Repository.java"
to update interaction mappings.
```
