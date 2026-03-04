# /reforge.glossary

> Extract, verify, and persist a glossary of acronyms and abbreviations from the analyzed codebase

## Command Syntax

```
/reforge.glossary [--phase <1|2|3|4|all>] [--resume] [--skip-external] [--team-size <n>]
```

### Arguments

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `--phase` | No | `all` | Run specific phase: `1` (extract), `2` (verify), `3` (audit), `4` (self-audit), or `all` |
| `--resume` | No | — | Resume from last checkpoint |
| `--skip-external` | No | — | Skip Phase 2 (external verification) for air-gapped environments |
| `--team-size` | No | `3` | Number of worker agents for parallel processing (range: 1-6) |

## Overview

This command executes a 4-phase acronym extraction and verification pipeline:

1. **Phase 1 — Pattern Extraction**: Scan source files for acronyms/abbreviations using pattern matching
2. **Phase 2 — External Verification**: Look up acronyms via WebSearch against authoritative sources
3. **Phase 3 — Source Code Audit**: Verify every entry using word-boundary grep against source files
4. **Phase 4 — Self-Audit**: Independent re-verification of modified and low-confidence entries

The final glossary persists to memory for consumption by all other Reforge commands.

## Prerequisites

- Analysis must be completed (`/reforge.analyze`)
- `$ANALYSIS_DIR/analysis.xml` must exist
- `.reforge/memory/` directory must be writable

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

Use `$PROJECT_OUTPUT_DIR`, `$PROJECT_NAME`, `$REPO_ROOT` throughout subsequent steps.

Assign subdirectory variables:
```
$ANALYSIS_DIR = $PROJECT_OUTPUT_DIR/analysis
$EXTRACTIONS_DIR = $PROJECT_OUTPUT_DIR/extractions
$AUDIT_DIR = $PROJECT_OUTPUT_DIR/audit
$GLOSSARY_XML = $EXTRACTIONS_DIR/acronym-glossary.xml
$GLOSSARY_AUDIT = $AUDIT_DIR/glossary-audit-report.xml
$GLOSSARY_MEMORY = .reforge/memory/glossary.json
$GLOSSARY_CHECKPOINT = .reforge/memory/checkpoints/glossary-checkpoint.json
```

Verify `$ANALYSIS_DIR/analysis.xml` exists. If not, report error:
> "Analysis not found. Run `/reforge.analyze` first."

Ensure `.reforge/memory/checkpoints/` directory exists. Create it if needed.

### Step 0.5: Load Project Context

If `.reforge/memory/project-context.md` exists, read it now for supplemental guidance (tech stack, domain knowledge, analysis rules). The project context is optional — its absence MUST NOT affect command behavior.

### Step 0.7: Check/Update Project Plan

If `.reforge/memory/project-plan.md` exists, read it now.

**On command start:**
- Parse the plan file to count total items and completed items
- Display: "Project Plan: X/Y items complete (Z%)"
- Derive the plan tag: `<!-- reforge:glossary -->`

**On command completion (success only):**
- Locate the plan item by searching for `<!-- reforge:glossary -->`
- If found and unchecked (`- [ ]`): change to `- [x]` and append ` *(completed: YYYY-MM-DD)*`
- If found and already checked (`- [x]`): leave unchanged (idempotent)
- If tag not found: emit warning — "No plan item found for glossary. Run /reforge.plan to add it."
- If file write fails: emit warning — "Could not update project plan." Continue without failing.
- Update the `**Last Updated**` metadata line to today's date

If `.reforge/memory/project-plan.md` does not exist, skip this step silently.
The project plan is optional — its absence MUST NOT affect command behavior.

### Step 1: Parse Flags and Determine Execution Mode

Parse the command arguments and determine the execution path:

**Flag Validation:**
- `--team-size` must be integer 1-6. Default: 3. If out of range, warn and clamp to nearest valid value.
- `--phase` must be one of: `1`, `2`, `3`, `4`, `all`. Default: `all`.
- `--resume` and `--phase` are mutually exclusive. If both specified, `--resume` takes precedence with a warning.
- `--skip-external` is compatible with all other flags.
- When `--team-size 1` is specified, skip all team orchestration and use sequential-only processing.

**Determine execution mode:**

1. **Resume mode** (`--resume` specified): Go to Step 2A.
2. **Single-phase mode** (`--phase N` where N is 1-4): Go to Step 2B.
3. **Full pipeline mode** (default or `--phase all`): Go to Step 2C.

### Step 2A: Resume from Checkpoint

Read `$GLOSSARY_CHECKPOINT`. If the file does not exist:
> "No checkpoint found at `.reforge/memory/checkpoints/glossary-checkpoint.json`. No prior run to resume."
> "Would you like to start from Phase 1? Run `/reforge.glossary` (without --resume) to begin a new extraction."

Stop execution — do not proceed to Step 3.

If the checkpoint file exists but cannot be parsed as valid JSON:
> "Checkpoint file is corrupt. Would you like to start from Phase 1? Run `/reforge.glossary` (without --resume) to begin fresh."

Stop execution — do not proceed to Step 3.

If the checkpoint exists and is valid, parse the JSON:
- Extract `last-completed-phase` to determine the next phase
- Extract `phases-skipped` to know which phases were skipped
- Extract `team-size` to preserve the original team configuration
- Load the existing `$GLOSSARY_XML` at `current-version` — this preserves all glossary data from completed phases

If `last-completed-phase` is 4, the pipeline already completed:
> "All phases already completed (v{current-version}). No further phases to run."

Stop execution.

Report:
> "Resuming glossary extraction. Last completed: Phase {N} ({current-version}). Continuing from Phase {N+1}."

Set `$START_PHASE = last-completed-phase + 1` and `$END_PHASE = 4`.
If `--skip-external` is specified, add Phase 2 to `phases-skipped` if not already present.
Skip any phases in `phases-skipped`.
Go to Step 3 with the determined phase range.

### Step 2B: Single-Phase Execution

Validate that prerequisite phases have completed by checking the glossary XML:

| Requested Phase | Prerequisite | Validation |
|-----------------|-------------|------------|
| Phase 1 | None | Can always run |
| Phase 2 | Phase 1 complete | `$GLOSSARY_XML` must exist with `version` >= `v1.0.0` |
| Phase 3 | Phase 1 complete (Phase 2 optional) | `$GLOSSARY_XML` must exist with `version` >= `v1.0.0` |
| Phase 4 | Phase 3 complete | `$GLOSSARY_XML` must exist with `version` >= `v1.2.0` |

If prerequisite not met, report error:
> "Phase {N} requires Phase {prerequisite} to be completed first. Run `/reforge.glossary --phase {prerequisite}` first."

**Load existing state**: Read `$GLOSSARY_XML` to load the current glossary entries. This is the state that the requested phase will operate on. If `$GLOSSARY_CHECKPOINT` exists, also read the checkpoint to inherit `phases-skipped` and `team-size` from the prior run.

Set `$START_PHASE = N` and `$END_PHASE = N`.
Go to Step 3 with the single phase.

### Step 2C: Full Pipeline Execution

Set `$START_PHASE = 1` and `$END_PHASE = 4`.

If `--skip-external` is specified:
- Add Phase 2 to the `$PHASES_SKIPPED` list
- The version progression becomes v1.0.0 → v1.2.0 → v1.3.0 (v1.1.0 is skipped)
- Phase 3 will accept v1.0.0 as its input version (instead of requiring v1.1.0)
- The `phases-skipped` array in each checkpoint will include `2`

Go to Step 3.

### Step 3: Execute Phase Loop

For each phase from `$START_PHASE` to `$END_PHASE`:

1. **Check skip list**: If this phase is in the skip list, report and continue:
   > "Skipping Phase {N} (--skip-external)."

2. **Report phase start**:
   > "Phase {N} starting: {phase-description}..."

   Record the start time.

3. **Dispatch to phase template**: Load and execute the corresponding phase template:
   - Phase 1: `.reforge/commands/glossary-phase-1.md`
   - Phase 2: `.reforge/commands/glossary-phase-2.md`
   - Phase 3: `.reforge/commands/glossary-phase-3.md`
   - Phase 4: `.reforge/commands/glossary-phase-4.md`

   Pass these variables to the phase template:
   - `$PROJECT_NAME`, `$REPO_ROOT`, `$PROJECT_OUTPUT_DIR`
   - `$GLOSSARY_XML`, `$GLOSSARY_AUDIT`
   - `$TEAM_SIZE` (from `--team-size`)
   - Current glossary state (if resuming or running later phases)

4. **Report phase completion**:
   > "Phase {N} complete: {entry-count} entries, {verdict-summary} — {elapsed-time}"

   Example: "Phase 3 complete: 42 entries audited, 3 FABRICATED, 2 CORRECTED, 37 CONFIRMED — 4m 12s"

5. **Save checkpoint** to `$GLOSSARY_CHECKPOINT`:
   ```json
   {
     "feature": "glossary",
     "last-completed-phase": N,
     "current-version": "{version}",
     "entry-count": {count},
     "phases-skipped": [...],
     "timestamp": "{ISO-8601}",
     "team-size": {team-size}
   }
   ```

6. **Continue** to next phase.

### Step 4: Persist Memory and Finalize

After all phases complete successfully:

1. **Generate memory lookup file** at `$GLOSSARY_MEMORY`:

   Read the final `$GLOSSARY_XML` and create a JSON lookup keyed by term. Include only entries that are NOT `FABRICATED`:

   ```json
   {
     "version": "{final-version}",
     "generated": "{ISO-8601}",
     "entry-count": {surviving-count},
     "terms": {
       "TERM": {
         "expansion": "Full Expansion",
         "confidence": 0.95,
         "category": "domain"
       }
     }
   }
   ```

2. **Clean up checkpoint file**: Delete `$GLOSSARY_CHECKPOINT` (successful completion means no resume needed).

3. **Report final summary**:
   > "Glossary extraction complete."
   > "- Version: {version}"
   > "- Total entries: {count}"
   > "- Confirmed: {n}, Corrected: {n}, Unverified: {n}"
   > "- Fabricated (removed): {n}"
   > "- Memory persisted to: .reforge/memory/glossary.json"
   > "- Audit report: {$GLOSSARY_AUDIT}"

4. **Update project plan** (Step 0.7 completion hook).

---

## Model Tier Recommendations

Templates SHOULD recommend cost-appropriate model tiers for each phase, but the agent runtime controls actual model selection:

| Phase | Recommended Tier | Rationale |
|-------|-----------------|-----------|
| Phase 1 (Pattern Extraction) | Fast/cheap | Pattern matching is mechanical |
| Phase 2 (External Verification) | Standard | WebSearch requires judgment |
| Phase 3 (Source Code Audit) | Fast/cheap | Grep-based verification is mechanical |
| Phase 4 (Self-Audit) | Accurate | Independent re-verification requires careful analysis |

---

## Optional Enhancement: Team Orchestration

> **This section is OPTIONAL.** It applies only to agents that support team orchestration tools (e.g., Claude Code with TeamCreate, Task, SendMessage). Agents without these capabilities MUST use the sequential workflow described in each phase template. Output is identical regardless of execution path.

When `--team-size` is greater than 1 AND the agent supports team orchestration:

1. **Before Phase 1**: Create a team with `--team-size` worker agents.
2. **Phase 1**: Partition source files into zones and assign each zone to a worker agent for parallel extraction. The lead agent collects and deduplicates results.
3. **Phases 2-4**: Partition entries across worker agents for parallel processing. The lead agent collects and merges results.
4. **After final phase**: Shut down the team and clean up resources.

When `--team-size 1` is specified: Skip all team orchestration. Use sequential-only processing for all phases.

The sequential workflow described in each phase template is the canonical implementation. Team orchestration is an acceleration layer that produces identical output.

---

## Error Handling

| Error | Response |
|-------|----------|
| `analysis.xml` not found | Report error, suggest `/reforge.analyze` |
| Phase prerequisite not met | Report error with specific phase to run first |
| Checkpoint file corrupt | Warn and offer to restart from Phase 1 |
| WebSearch unavailable (Phase 2) | Suggest `--skip-external` flag |
| Zero entries after Phase 1 | Produce empty glossary with warning, continue pipeline |
| All entries FABRICATED after Phase 3 | Produce empty glossary with warning, continue to Phase 4 |
| Write failure | Report error with path, suggest checking permissions |

## Output Files

| File | Location | Description |
|------|----------|-------------|
| Glossary XML | `$EXTRACTIONS_DIR/acronym-glossary.xml` | Full glossary with entries, evidence, metadata |
| Audit Report | `$AUDIT_DIR/glossary-audit-report.xml` | Phase 3-4 verification findings |
| Memory Lookup | `.reforge/memory/glossary.json` | Persistent lookup for cross-command consumption |
| Checkpoint | `.reforge/memory/checkpoints/glossary-checkpoint.json` | Resume state (cleaned up on success) |
