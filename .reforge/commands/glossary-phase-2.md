# Phase 2: External Verification

> Verify glossary entries against external authoritative sources using WebSearch, assigning verification status and adjusting confidence scores.

**Recommended Model Tier**: Standard (WebSearch requires judgment to evaluate source quality and relevance)

## Input / Output

| Item | Path | Version |
|------|------|---------|
| **Input** | `$GLOSSARY_XML` (`acronym-glossary.xml`) | v1.0.0 |
| **Output** | `$GLOSSARY_XML` (`acronym-glossary.xml`) | v1.1.0 |

**Variables provided by orchestrator**: `$PROJECT_NAME`, `$REPO_ROOT`, `$PROJECT_OUTPUT_DIR`, `$GLOSSARY_XML`, `$GLOSSARY_AUDIT`, `$TEAM_SIZE`

---

## Workflow

### Step 1: Load Existing Glossary

Read the glossary XML from `$GLOSSARY_XML`. Verify that:

- The file exists and is well-formed XML
- The `version` attribute is `v1.0.0` (Phase 1 output)

Parse all `<entry>` elements into a working list. Record the total entry count for progress reporting.

If `$GLOSSARY_XML` does not exist or the version is not `v1.0.0`:
> "Phase 2 requires a v1.0.0 glossary from Phase 1. Current state is invalid."

### Step 2: Check WebSearch Availability

Before beginning verification, confirm that the WebSearch tool is available to the agent.

**Test**: Attempt a simple WebSearch query (e.g., `"acronym glossary test"`).

- If WebSearch **succeeds**: Proceed to Step 3.
- If WebSearch **fails or is unavailable**: Go to the Graceful Degradation section below.

### Step 3: Build Verification Queue

Build a verification queue from all glossary entries. Prioritize entries for verification in this order:

1. Entries with `verification-status="UNVERIFIED"` (all Phase 1 entries start as UNVERIFIED)
2. Entries with lower confidence scores first (verify the least confident entries earliest)

Record the queue size for progress reporting.

### Step 4: Verify Entries via WebSearch

Process entries in batches of 5-10 for efficiency.

**For each entry in the verification queue:**

#### 4a: Search Strategy

Execute up to 3 WebSearch queries per entry, stopping early if a definitive result is found:

1. **Primary query**: `"{TERM} acronym meaning"`
2. **Domain-specific query**: `"{TERM} {CATEGORY} abbreviation"` (using the entry's category — e.g., `"TMDS domain abbreviation"`)
3. **Targeted query**: `"{TERM} stands for"` OR `"what does {TERM} stand for"`

Evaluate results from authoritative sources in this priority order:
- Wikipedia
- Industry-specific glossaries and standards bodies
- Official project or product documentation
- Technical reference sites (e.g., IETF RFCs, W3C specs)

#### 4b: Assign Verification Status

Based on the search results, assign one of the following statuses:

**CONFIRMED** — External source confirms the term and its expansion matches:
- Set `verification-status="CONFIRMED"`
- Boost confidence by +0.2 (cap at 1.0): `new_confidence = min(confidence + 0.2, 1.0)`
- Add an `<source>` evidence element:
  ```xml
  <source file="external" line-start="0" line-end="0"
          evidence-type="external-source" phase="2">
    <snippet>{Source name}: {brief description of confirmation}</snippet>
  </source>
  ```
- Set `version-modified="v1.1.0"`

**CORRECTED** — External source identifies a different (more accurate) expansion:
- Set `verification-status="CORRECTED"`
- Update `<expansion>` to the corrected text
- Set confidence to 0.8: `new_confidence = 0.8`
- Add an `<source>` evidence element:
  ```xml
  <source file="external" line-start="0" line-end="0"
          evidence-type="external-source" phase="2">
    <snippet>{Source name}: corrected from "{old expansion}" to "{new expansion}"</snippet>
  </source>
  ```
- Set `version-modified="v1.1.0"`

**UNVERIFIED** — No external source found for this term (could be project-specific):
- Leave `verification-status="UNVERIFIED"`
- Leave confidence unchanged
- Do NOT add external evidence (there is none)
- Do NOT set `version-modified` (entry was not modified)

**NOT_FOUND** — External sources indicate this is not a recognized acronym:
- Set `verification-status="NOT_FOUND"`
- Reduce confidence by -0.2 (floor at 0.1): `new_confidence = max(confidence - 0.2, 0.1)`
- Add an `<source>` evidence element:
  ```xml
  <source file="external" line-start="0" line-end="0"
          evidence-type="external-source" phase="2">
    <snippet>No recognized acronym found in external sources</snippet>
  </source>
  ```
- Set `version-modified="v1.1.0"`

#### 4c: Batch Progress

After each batch of 5-10 entries, report progress:
> "Verified {completed}/{total} entries..."

### Step 5: Update Glossary XML

After all entries have been processed:

1. Update the root `<acronym-glossary>` element:
   - Set `version="v1.1.0"`
   - Update `generated` timestamp to the current ISO-8601 time

2. Recalculate `<metadata>`:
   - Update `<total-count>` (should be unchanged from v1.0.0)
   - Recalculate `<confidence-distribution>` based on updated confidence scores:
     - `high`: entries with confidence 0.8-1.0
     - `medium`: entries with confidence 0.5-0.79
     - `low`: entries with confidence 0.0-0.49

3. Write all updated entries back with their new statuses, confidence scores, and evidence.

### Step 6: Write Updated Glossary

Write the complete updated glossary XML to `$GLOSSARY_XML`, overwriting the v1.0.0 file.

Verify the written file:
- File exists at `$GLOSSARY_XML`
- Root element has `version="v1.1.0"`
- Entry count matches expected total

### Step 7: Report Summary

Report the Phase 2 summary to the orchestrator:

> "Phase 2 complete: {total} entries verified — {confirmed} CONFIRMED, {corrected} CORRECTED, {unverified} UNVERIFIED, {not_found} NOT_FOUND — {elapsed_time}"

Return the following counts for the orchestrator's checkpoint:
- Total entries processed
- Entries by verification status (CONFIRMED, CORRECTED, UNVERIFIED, NOT_FOUND)
- Elapsed time

---

## Graceful Degradation

If WebSearch is unavailable (tool not present, network error, or air-gapped environment):

1. **Warn the operator**:
   > "WebSearch tool is unavailable. Phase 2 (External Verification) cannot proceed without external search capability."

2. **Suggest alternatives**:
   > "Options:"
   > "  - Re-run with `--skip-external` to skip Phase 2 entirely"
   > "  - Ensure WebSearch tool access is configured and re-run Phase 2"

3. **Do NOT modify the glossary XML** — leave it at v1.0.0 unchanged.

4. **Signal failure to the orchestrator** so it can handle accordingly (the orchestrator will suggest `--skip-external` per the error handling table).

The agent MUST NOT attempt to verify entries using its own parametric knowledge as a substitute for WebSearch. External verification requires actual external sources. Falling back to LLM knowledge would undermine the verification purpose and risk reinforcing hallucinated expansions.

---

## Optional Enhancement: Team Orchestration

> **This section is OPTIONAL.** It applies only to agents that support team orchestration tools. Agents without these capabilities MUST use the sequential workflow described above. Output is identical regardless of execution path.

When `$TEAM_SIZE` is greater than 1 AND the agent supports team orchestration:

1. **Partition the verification queue** across `$TEAM_SIZE` worker agents, distributing entries evenly.
2. **Each worker agent** executes Steps 4a-4b independently for its assigned entries.
3. **The lead agent** collects results from all workers and merges them into the glossary.
4. **Conflict resolution**: If two workers produce different results for overlapping queries, the lead agent keeps the result from the most authoritative source.

When `$TEAM_SIZE` is 1: Skip all team orchestration. Process entries sequentially as described in Steps 3-4.
