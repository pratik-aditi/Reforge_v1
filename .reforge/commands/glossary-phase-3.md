# Phase 3: Source Code Audit

> Verify every glossary entry against the actual source codebase using word-boundary grep, identify fabricated entries, and produce an audit report

## Overview

Phase 3 is the primary hallucination defense layer. It independently verifies each glossary entry by searching the source codebase for word-boundary matches of the term. Entries with zero source code presence are marked as FABRICATED and removed. Entries where the term exists but no explicit expansion is found are capped at low confidence.

**Model Tier Recommendation**: Fast/cheap — grep-based verification is mechanical.

## Input

- `$GLOSSARY_XML` — current glossary at v1.0.0 (if Phase 2 was skipped) or v1.1.0 (if Phase 2 ran)
- `$REPO_ROOT` — root directory of the source codebase
- `$GLOSSARY_AUDIT` — output path for the audit report
- `$TEAM_SIZE` — number of worker agents (used only in optional team orchestration)

## Output

- Updated `$GLOSSARY_XML` at **v1.2.0** — entries updated with Phase 3 verdicts, confidence adjustments, and new evidence
- `$GLOSSARY_AUDIT` — audit report documenting all Phase 3 findings

---

## LLM-Authored File Exclusion List

The following files MUST be excluded from all grep results and MUST NOT be accepted as evidence sources. These are LLM-generated files whose content cannot serve as independent verification:

- `CLAUDE.md`
- `README.md`
- `project-context.md`
- `analysis.xml`
- Any file under `.reforge/` (the entire `.reforge/` directory tree)

When filtering grep results, the agent MUST remove any match whose file path ends with one of the above filenames or whose file path contains `.reforge/` as a path segment.

---

## Workflow

### Step 1: Load Current Glossary

Read `$GLOSSARY_XML` and parse all `<entry>` elements. For each entry, extract:

- `id` (e.g., `GLOSS-001`)
- `term` (e.g., `TMDS`)
- `expansion` (e.g., `Train Management Dispatch System`)
- `confidence` (current score)
- `category`
- `verification-status` (current status)
- `evidence` (existing evidence chain)

Record `$ENTRY_COUNT` = total number of entries loaded.

If the glossary contains zero entries, report:
> "Phase 3: Glossary is empty (0 entries). Nothing to audit. Skipping to output."

Write an empty audit report and proceed to Step 9.

### Step 2: Build Audit Queue

Create an audit queue containing ALL entries from the glossary, regardless of their current verification status. Every entry must be independently verified against source code.

Initialize counters:
- `$CONFIRMED_COUNT` = 0
- `$CORRECTED_COUNT` = 0
- `$FABRICATED_COUNT` = 0
- `$UNVERIFIABLE_COUNT` = 0
- `$FINDINGS` = [] (empty list)

### Step 3: Audit Each Entry

For each entry in the audit queue, perform the following verification:

#### Step 3a: Run Word-Boundary Grep

Use the Grep tool to search for the term across all source files:

```
Pattern: \bTERM\b
Path: $REPO_ROOT
```

Replace `TERM` with the entry's `term` value. The `\b` anchors ensure only whole-word matches are counted, preventing false positives from substring matches (e.g., `\bAPI\b` will not match `CAPITAL`).

#### Step 3b: Filter Out LLM-Authored Files

From the grep results, remove ALL matches from excluded files:

- Any result where the file path ends with `CLAUDE.md`
- Any result where the file path ends with `README.md`
- Any result where the file path ends with `project-context.md`
- Any result where the file path ends with `analysis.xml`
- Any result where the file path contains `.reforge/` as a path segment

After filtering, record:
- `$GREP_COUNT` = number of remaining matches
- `$EVIDENCE_FILES` = list of unique file paths with matches (after exclusion)

#### Step 3c: Classify the Entry

Apply the following decision logic based on grep results:

**Case 1: Zero matches (`$GREP_COUNT` = 0)**
- **Verdict**: `FABRICATED`
- **Action**: `DELETE`
- **Rationale**: "Term '{term}' has zero word-boundary matches in the source codebase. Entry is fabricated and should be removed."
- Update entry: `verification-status` = `FABRICATED`
- Increment `$FABRICATED_COUNT`

**Case 2: Matches found AND explicit expansion found in source**

Search the evidence files for the expansion text. The agent should read the files where the term was found and look for:
- Comments or documentation that spell out what the acronym stands for (e.g., `// TMDS - Train Management Dispatch System`)
- Doc comments with the full expansion
- String literals containing the expansion
- Variable/class naming patterns that reveal the expansion

If the expansion found in source matches the current entry expansion:
- **Verdict**: `CONFIRMED`
- **Action**: `KEEP`
- **Rationale**: "Term '{term}' found in {grep-count} files. Expansion '{expansion}' confirmed by source evidence in {file}."
- Update entry: `verification-status` = `CONFIRMED`
- Boost confidence: set to `min(1.0, current_confidence + 0.2)` if not already 1.0
- Add new `<source>` evidence element with `phase="3"` and the relevant file/line
- Increment `$CONFIRMED_COUNT`

If the expansion found in source DIFFERS from the current entry expansion:
- **Verdict**: `CORRECTED`
- **Action**: `UPDATE`
- Record `$ORIGINAL_EXPANSION` = current expansion
- Record `$CORRECTED_EXPANSION` = expansion found in source
- **Rationale**: "Term '{term}' found in {grep-count} files. Source evidence indicates expansion is '{corrected-expansion}', not '{original-expansion}'."
- Update entry: `expansion` = corrected expansion, `verification-status` = `CORRECTED`
- Add new `<source>` evidence element with `phase="3"` and the relevant file/line
- Increment `$CORRECTED_COUNT`

**Case 3: Matches found BUT no explicit expansion found in source**
- **Verdict**: `UNVERIFIABLE`
- **Action**: `FLAG_FOR_REVIEW`
- **Rationale**: "Term '{term}' found in {grep-count} files but no explicit expansion found in source code. Confidence capped at 0.5."
- Update entry: `verification-status` = `UNVERIFIED`, `confidence` = `min(0.5, current_confidence)`
- Add new `<source>` evidence element with `phase="3"`, `evidence-type="variable-name"` or appropriate type, and the relevant file/line
- Increment `$UNVERIFIABLE_COUNT`

### Step 4: Generate Audit Findings

For each entry processed in Step 3, create a `<finding>` element:

```xml
<finding entry-id="GLOSS-001" term="TMDS" phase="3"
         verdict="CONFIRMED" grep-count="14" action="KEEP">
  <evidence-files>
    <file>src/tmds/core/Dispatcher.java</file>
    <file>src/tmds/config/TcosConfig.java</file>
  </evidence-files>
  <rationale>Term 'TMDS' found in 14 files. Expansion 'Train Management Dispatch System' confirmed by source evidence in src/tmds/core/Dispatcher.java.</rationale>
</finding>
```

For `CORRECTED` entries, also include:
```xml
<finding entry-id="GLOSS-005" term="TCOS" phase="3"
         verdict="CORRECTED" grep-count="14" action="UPDATE">
  <evidence-files>
    <file>src/tcos/MainController.java</file>
    <file>src/tcos/config/TcosConfig.java</file>
  </evidence-files>
  <original-expansion>Technical Control Operating System</original-expansion>
  <corrected-expansion>Train Control and Operating System</corrected-expansion>
  <rationale>Source code comments consistently use "Train Control and Operating System" across 14 files.</rationale>
</finding>
```

For `FABRICATED` entries, the `<evidence-files>` element is omitted (no files matched).

Append each finding to the `$FINDINGS` list.

### Step 5: Update Glossary Entries

Apply all Phase 3 changes to the in-memory glossary:

1. **For CONFIRMED entries**: Update `verification-status`, boost `confidence`, add Phase 3 `<source>` evidence, set `version-modified="v1.2.0"`
2. **For CORRECTED entries**: Update `expansion`, `verification-status`, add Phase 3 `<source>` evidence, set `version-modified="v1.2.0"`
3. **For UNVERIFIABLE entries**: Set `verification-status="UNVERIFIED"`, cap `confidence` at 0.5, add Phase 3 `<source>` evidence, set `version-modified="v1.2.0"`
4. **For FABRICATED entries**: Set `verification-status="FABRICATED"`, set `confidence` to 0.0, set `version-modified="v1.2.0"`

### Step 6: Remove FABRICATED Entries

Remove all entries with `verification-status="FABRICATED"` from the glossary. These entries have zero source code presence and are hallucinated.

Record the count of removed entries for the summary. Update `$ENTRY_COUNT` to reflect the surviving entry count.

> **Note**: FABRICATED entries remain documented in the audit report (Step 9) even though they are removed from the glossary. The audit report is the permanent record of what was found and removed.

### Step 7: Update Glossary Version

Set the glossary root element `version` attribute to `v1.2.0`.

Update `<metadata>`:
- Recalculate `<total-count>` to reflect surviving entries
- Recalculate `<confidence-distribution>` based on updated confidence scores:
  - `high`: entries with confidence 0.8 - 1.0
  - `medium`: entries with confidence 0.5 - 0.79
  - `low`: entries with confidence 0.0 - 0.49
- Update `<extraction-timestamp>` to current ISO-8601 timestamp

### Step 8: Write Updated Glossary

Write the updated glossary XML to `$GLOSSARY_XML`, overwriting the previous version.

The output MUST conform to the schema defined in `.reforge/schemas/glossary.md`:
- Root element `<acronym-glossary>` with `version="v1.2.0"`
- All surviving entries with updated attributes and evidence chains
- Valid `<metadata>` with accurate counts

### Step 9: Write Audit Report

Write the audit report to `$GLOSSARY_AUDIT`:

```xml
<glossary-audit-report project-id="$PROJECT_NAME" version="1.0.0"
                       generated="{ISO-8601-timestamp}"
                       glossary-version="v1.2.0"
                       total-findings="{$CONFIRMED_COUNT + $CORRECTED_COUNT + $FABRICATED_COUNT + $UNVERIFIABLE_COUNT}"
                       confirmed-count="{$CONFIRMED_COUNT}"
                       corrected-count="{$CORRECTED_COUNT}"
                       fabricated-count="{$FABRICATED_COUNT}"
                       unverifiable-count="{$UNVERIFIABLE_COUNT}">
  <findings>
    <!-- One <finding> per audited entry, from Step 4 -->
    <finding entry-id="..." term="..." phase="3"
             verdict="..." grep-count="..." action="...">
      <evidence-files>
        <file>...</file>
      </evidence-files>
      <original-expansion>...</original-expansion>    <!-- only for CORRECTED -->
      <corrected-expansion>...</corrected-expansion>  <!-- only for CORRECTED -->
      <rationale>...</rationale>
    </finding>
  </findings>
  <summary>
    <phase-3-summary entries-audited="{total entries processed}"
                     confirmed="{$CONFIRMED_COUNT}"
                     corrected="{$CORRECTED_COUNT}"
                     fabricated="{$FABRICATED_COUNT}"
                     unverifiable="{$UNVERIFIABLE_COUNT}"
                     elapsed-time="{elapsed}"/>
  </summary>
</glossary-audit-report>
```

If a `$GLOSSARY_AUDIT` file already exists (from a previous run), overwrite it. Phase 4 will append its own findings to this report.

### Step 10: Report Summary

Report phase completion to the operator:

> "Phase 3 complete: {entries-audited} entries audited, {$FABRICATED_COUNT} FABRICATED, {$CORRECTED_COUNT} CORRECTED, {$CONFIRMED_COUNT} CONFIRMED, {$UNVERIFIABLE_COUNT} UNVERIFIABLE — {elapsed-time}"

Example:
> "Phase 3 complete: 42 entries audited, 3 FABRICATED, 2 CORRECTED, 35 CONFIRMED, 2 UNVERIFIABLE — 4m 12s"

---

## Optional Enhancement: Team Orchestration

> **This section is OPTIONAL.** It applies only to agents that support team orchestration tools. Agents without these capabilities MUST use the sequential workflow described above. Output is identical regardless of execution path.

When `$TEAM_SIZE` is greater than 1 AND the agent supports team orchestration:

1. **Partition entries**: Divide the audit queue into `$TEAM_SIZE` batches of approximately equal size.
2. **Assign to workers**: Each worker agent receives a batch of entries and independently executes Steps 3a-3c (grep, filter, classify) for its assigned entries.
3. **Collect results**: The lead agent collects all findings from worker agents and merges them into the single `$FINDINGS` list.
4. **Continue sequentially**: Steps 4-10 are executed by the lead agent using the merged findings.

The parallel grep approach can significantly reduce elapsed time for large glossaries, as word-boundary grep operations are independent across entries.

When `$TEAM_SIZE` is 1: Skip team orchestration entirely. Use the sequential workflow above.
