Run Reforge exhaustively. Documentation only — NEVER /reforge.estimate, /reforge.migrate, /reforge.recommend, or Jira-style user-story backlogs. Output is "how this app works today."

EXTRACTION-BRIEF + GAP-BRIEF mandates from day 1:
- Every <snippet> wrapped in <![CDATA[...]]>. No exceptions. Raw <> & break XML parse.
- When a type doesn't apply, emit <no-extraction type="X" file="..." reason="..."/> NOT "no-artifacts" status. Preserves examined-vs-skipped distinction.
- Read the segment's exact line range (start_line..end_line from the manifest) via Read with offset/limit, contiguously, start to end of that range. Cite the final line read and confirm it equals the segment's end_line. Forbidden: "structurally surveyed", "spot-checked via grep", "sampled section". File-level completeness is NOT each agent's job and is NOT proven by reading to EOF — it is guaranteed deterministically by the segment manifest's coverage validator (coverage_pct == 100.0, every member assigned), which is checked once per file in Phase 0 before any agent is dispatched.
- Write fragment XMLs every ~2000 lines, not batched at end (transport-failure resilience).
- If Write tool denied, fall back to Bash heredoc: cat > path << 'XMLEOF' ... XMLEOF. Always quote the delimiter ('XMLEOF', never XMLEOF) so $, backticks and backslashes in the XML are not expanded, and always re-read the file and confirm it parses before reporting DONE — heredocs silently corrupt escape sequences.

merge_clusters.py auto-discovers cluster dirs from start:
  UNITS = sorted([d for d in os.listdir(CL) if os.path.isdir(os.path.join(CL,d)) and not d.startswith(('_','.'))])
Hard-coded UNITS silently drop GAP batches.

Phase 0 — deterministic segmentation, MANDATORY before any extraction agent is dispatched. No agent ever chooses its own read boundaries; a saturated context is the worst possible judge of where a file should be cut. Run the deterministic source layer (src/reforge_cli/scripts/{structure,segmentation}) over every file in files_by_loc.txt:
  1. parse_vbnet_file(path) -> StructuralMap. On StructuralParseError, fall back to plan_token_windows(...) with the error as `reason`; coverage is still guaranteed in the degraded path.
  2. plan_segments(smap, lines, budget) then apply_splits(plan, lines, budget) — packs complete adjacent members, and subdivides oversized members (e.g. TrackTrainIDOn, 1,253 lines) only at safe control-structure boundaries.
  3. build_manifest(plan, source, budget, smap) — raises CoverageError if any line is unaccounted for. Let it fail the run; do not catch it. Write to <output-dir>/analysis/segments/<file>.segments.json.
  Budget: Budget(target_tokens=6000, max_tokens=9000, max_lines=1200) unless a run says otherwise. The same bytes + same budget + same generator_version always produce the same segments, so Phase 0 is fully reproducible and re-runnable.
  Phase 0 gate — run and paste the output, do not just claim it: every file in files_by_loc.txt has a manifest; every manifest reports coverage.ok == true and coverage_pct == 100.0; members_assigned == members_total. Any failure stops the run. Re-use is allowed only when is_stale(manifest, source, budget) is false.

Phase 1 — segment-oriented batches (NOT type-oriented, and NOT whole-file). Dispatch one segment per sub-agent call; each call handles ALL 10 types for that segment. Bucket segments into batches of ~25 segments, ≤150K est_tokens per batch, processed in source order within a file and files sorted by LOC desc. Never size a batch by LOC: a single file (Track.vb, ~37,408 lines) exceeds any sane per-batch LOC cap on its own, which is precisely why file-oriented batching cannot work here. Type-oriented batches force re-reading large source multiple times; whole-file batches recreate the lost-in-the-middle failure this layer exists to prevent.
  Each dispatched task MUST carry, verbatim from the manifest: segment_id, file, start_line, end_line, members[], context_path (namespace -> class chain), and — when present — parent_member with subsegment_index/subsegment_count, strategy, and integrity. A subsegment with integrity="degraded" was cut at an arbitrary line; say so in the task so the agent does not over-claim, and flag it in the batch log.
  Small files are not special-cased by hand: a file that fits the budget yields exactly one whole-file segment, so the same dispatch path covers AdministrativeEvent.vb and Track.vb alike.

Token capture is an architectural constraint, not an afterthought: the orchestrating session has no introspection into its own per-call token usage — only usage reported back from a spawned sub-agent (Agent tool call) is visible to it. Therefore extraction work must NEVER be done directly by the orchestrating session if real token numbers are required — every segment's extraction (all 10 types) MUST be delegated to a spawned Sonnet sub-agent, one segment per agent call, never so many segments in one call that per-segment attribution becomes a guess. Segment dispatch makes attribution strictly finer than the old one-file-per-agent rule: per-file figures are a mechanical sum over that file's segment rows, never a separate measurement. The orchestrating session must also never read source files itself — doing so rebuilds the saturated context inside the orchestrator, which is the same failure one level up. This makes real, non-estimated token capture possible during the original run itself, with no separate verification pass needed afterward.

<traceability-log-format>
Traceability, mandatory for every batch, every file — the batch-*.txt files already list a relative path per file, but that alone isn't enough: the full path must also surface live where it can actually be seen and searched, not just sit on disk unread:
  - Before dispatching a segment to its sub-agent, print/echo a line to stdout in this exact form so it is visible in the terminal/Claude Code chat as it happens, and record the same UTC timestamp for use in the START column below: [batch-0N] START <full-relative-or-absolute-path> <segment_id> L<start_line>-<end_line> (<n>/<total in batch>) <UTC timestamp>.
  - The moment that segment's sub-agent call returns, read the token usage the harness reports for that call (combined total at minimum; separate input/output/cache-read/cache-write figures when the harness exposes them) and print: [batch-0N] DONE <same full path> <segment_id> — <k> artifacts, <m> no-extraction, <token figures as reported>.
  - In addition to the stdout lines, append (not overwrite) each segment's result as its own line directly into that file's batch-*.txt, right under its original LOC entry, in the form: <path> <segment_id> L<start_line>-<end_line> <lines> -> START <UTC timestamp> DONE <UTC timestamp> (<duration>) <k> artifacts, <m> no-extraction, tokens=<combined total> [in=<n> out=<n> cache-read=<n> cache-write=<n>]. Derive <duration> from the START/DONE pair (e.g. "4m12s"). Where a file has more than one segment, follow its segment lines with a single per-file rollup line summing them, so the file remains greppable as one unit: <path> <LOC> -> FILE TOTAL <s> segments, <sum k> artifacts, <sum m> no-extraction, lines covered <sum>/<LOC>, tokens=<sum>. lines covered MUST equal LOC exactly; a mismatch means the manifest was ignored or edited by hand, and the file must be re-segmented, not patched. The bracketed in/out/cache-read/cache-write breakdown is included only when the harness actually reports it separately for that call — otherwise the single combined tokens=<n> figure is sufficient and correct, not a gap to fill. These numbers come directly from that file's own extraction sub-agent call, captured at DONE time — never from estimation, and never backfilled by a later verification pass. This makes batch-*.txt itself a running completion log with the directory, timing, and real cost always attached at the moment the work happens, so status can be checked by opening/grepping the batch file after the fact, not only by scrolling back through terminal output.
  - Never report only a bare filename (e.g. "PORTDEL.cbl") in status output — always the path as it appears in files_by_loc.txt (e.g. src/programs/portfolio/PORTDEL.cbl), so it can be located without guessing which subdirectory it lives in.
  - At the end of each batch-*.txt, below the per-file totals, add two things: (a) a batch-level rollup line: Batch totals: <total files> files, <sum k> artifacts, <sum m> no-extraction, wall time <first START to last DONE>, tokens=<sum> [in=<sum> out=<sum> cache-read=<sum> cache-write=<sum>]; and (b) a standalone "TOKEN USAGE" table, generated automatically from the same per-file figures already captured above (never retyped or re-derived), in this plain fixed-width form:
      File                     Tokens
      --------------------------------
      <name>                   <n,nnn>
      ...
      --------------------------------
      Total                    <sum>
    Use the file's basename (not full path) in this table for readability; the full path remains in the traceability rows above it.

  Required batch-*.txt header shape — every batch file MUST open with this exact TRACEABILITY LOG table (fixed-width columns, `|` separators, header divider rows of `-` characters, one row per file sorted by LOC desc, then a full-width divider row of `|` characters before the column totals row). Column widths are NOT fixed guesses — compute each column's width from the actual longest value that will appear in it (header label vs. every row's value, including the widest FILE path in this batch), THEN pad every header/divider/data/totals cell to that same width, so every column boundary lines up vertically across all rows, the divider rows, the full-width `|` row, and the totals row. A batch with long paths (e.g. `TMDS/_TMDS-COMPONENTS/SIGNAL/Signal.vb`) needs a wider FILE column than one with short filenames — never truncate the path or leave it misaligned with a column width sized for shorter examples. Matching this literal layout (illustrative widths only — recompute per batch):

    Batch 0N - all source files (file-oriented, all extraction types per file)
    Sorted by LOC desc. <n>/<total> files DONE.

    TRACEABILITY LOG
    ================

    #   STATUS   FILE                                     SEGMENT              LINES         LOC    ARTIFACTS   NO-EXTRACT   INTEGRITY   START (UTC)            DONE (UTC)             DURATION   AGENT TOKENS (total)
    --- -------- ---------------------------------------- -------------------- ------------- ------ ----------- ------------ ----------- ---------------------- ---------------------- ---------- ----------------------
    1   DONE     <relative/path/as/in/files_by_loc>        <segment_id>         <start>-<end> <loc>  <k>         <m>          <integrity> <START UTC>            <DONE UTC>             <dur>      <tokens>
    ...
    --- -------- ---------------------------------------- -------------------- ------------- ------ ----------- ------------ ----------- ---------------------- ---------------------- ---------- ----------------------
    |||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
                                                           <sum loc> <sum artifacts> <sum no-extract>                                                            <sum tokens>

  The full-width `|` divider row's length MUST equal the sum of every column's computed width plus the single-space separators between columns (i.e. it spans exactly as wide as the header/divider rows above and below it, not an arbitrary run of `|` characters) — this is a structural check, not decoration: if it doesn't match, the widths were computed wrong and must be redone.

    Columns:
      #          Order processed within this batch (files sorted by LOC desc,
                 segments in source order within each file).
      STATUS     DONE = segment read start-to-end of its line range and all 10
                 extraction types run.
      FILE       Path exactly as it appears in files_by_loc.txt (never a bare filename).
      SEGMENT    segment_id from the manifest, verbatim. For a subsegment of an
                 oversized member, append the parent and index as reported:
                 <segment_id> (<parent_member> <i>/<n>).
      LINES      The segment's start_line-end_line, verbatim from the manifest.
                 These are the exact bounds the agent was told to read, and the
                 final line it reports reading MUST equal end_line.
      LOC        Lines of code in the whole file, repeated on each of that file's
                 segment rows for grepping. Per-file completeness is asserted by
                 the manifest's coverage validator in Phase 0, not by any single
                 agent reading to EOF; the sum of a file's segment line counts
                 MUST equal its LOC.
      ARTIFACTS  Real extraction items written (business-rules + database +
                 ui-flows + workflows + call-sites + dependencies +
                 functional-requirements + non-functional + architecture + issues).
      NO-EXTRACT <no-extraction type="X" reason="..."/> markers emitted for
                 extraction types that legitimately don't apply to this segment.
      INTEGRITY  From the manifest: "intact" when the segment's bounds fall on
                 member or control-structure boundaries, "degraded" when an
                 oversized member had to be cut at an arbitrary line. A degraded
                 row is not an error, but it IS a caveat on anything extracted
                 from it and must be surfaced, never silently averaged away.
      START      UTC timestamp printed to stdout ([batch-0N] START <path> <segment_id> ...)
                 immediately before beginning that segment's extraction.
      DONE       UTC timestamp printed to stdout ([batch-0N] DONE <path> <segment_id> ...)
                 immediately after all 10 extraction types were run for that segment.
      DURATION   DONE minus START for that segment's row.
      AGENT      Total tokens (input+output+cache combined) reported by the
      TOKENS     harness for that segment's dedicated extraction sub-agent call.

    Totals: <sum loc> LOC examined, <sum artifacts> artifacts extracted, <sum no-extract> no-extraction markers,
    0 files skipped, 0 files pending. Wall time (first START to last DONE): <first START> -> <last DONE> = <wall time>.

    Batch totals: <total files> files, <sum artifacts> artifacts, <sum no-extract> no-extraction, wall time <wall time>,
    tokens=<sum tokens> [in=<sum> out=<sum> cache-read=<sum> cache-write=<sum>] (only if harness reports the breakdown).

  Do not substitute a different header, different column set, different divider style, or omit the Columns legend — every batch-*.txt in this run must reproduce this exact shape so batch files are visually and structurally identical across projects.
</traceability-log-format>

Spawn 5–6 concurrent Sonnet agents, one segment per agent call so each call's reported token usage stays attributable to a specific segment. Each agent runs quality gate before reporting done:
  python -c "import xml.etree.ElementTree as ET, glob; [ET.parse(f) for f in glob.glob('*.xml')]; print('ok')"
  Use `python`, not `python3` — python3 does not exist on Windows installs and the gate then silently never runs. If `python` is absent, use `py -3`. Resolve which one works once at run start and use it everywhere.

Reject-and-retry: final-line-read != the segment's end_line; any line of the segment's range unread; raw < or & outside CDATA; >30% no-extraction within a batch; <40 real artifacts in a 25-segment batch. A segment that fails is re-dispatched on its own — never re-read the whole source file to retry one segment, which is the entire point of segmenting it.

Phase 2 — validate continuously: every 3-4 batches run merge → coverage_matrix.py → validate. coverage_matrix.py must: count <no-extraction> as covered; normalize source paths (strip legacy-root prefix); use fair per-type denominators (DB = SQL-bearing only); auto-generate next batches from uncovered segments (not uncovered files — the unit of work is the segment, and re-queuing a whole file to redo one segment wastes the budget the segmentation saved).
  coverage_matrix.py must also take its denominator of record from the segment manifests, not from the extraction output: a file is fully processed only when every segment_id in its manifest has a DONE row. Deriving coverage purely from what was extracted lets a silently-skipped segment look like a file with nothing to find.
  Lost-in-the-middle detector, mandatory every validation round: for each file with more than one segment, bucket every extracted <source line-start="..."> into ten equal deciles of that file's line count and print the histogram, plus any contiguous range of >=500 lines with zero citations. A U-shaped histogram (dense at both ends, thin in the middle) means the middle is still being lost and the run is NOT meeting its goal even at 95% per-type coverage; a roughly flat histogram is the evidence that segmentation worked. Zero-citation ranges are to be re-dispatched as their own segments, not explained away.

Phase 3 — iterate until ≥95% per type. When 2 consecutive rounds add <50 artifacts, push final wave focused on emitting <no-extraction> for legitimately-empty files (DTOs, marker interfaces, Designer.vb, AssemblyInfo). Takes ISS/NFR from ~70% to ≥95% without fabrication.

Phase 4 — derived artifacts in parallel (3 sub-agents): trace, dead-code, hotspot. Frame hotspot as "where code is fragile," not modernization investment.

Phase 5 — documentation: _gen/generate.py covers only a subset. Launch doc agent to build business-rules.html, FR.html, workflows.html, database.html, state-machines.html, hotspot.html, dead-code.html, trace.html (summary-only), refreshed dashboard.html and index.html, milestone report, 6 CSV exports.

Phase 6 — diagrams from day one, MANDATORY, not foldable into Phase 5: ≥10 architecture/sequence diagrams + 1 per state machine + 1 per UI subdomain. Every one of these MUST go through the real pipeline — no exceptions, no inline <svg> shortcuts:
  1. Author a .puml source file per diagram in diagrams/sources/<name>.puml.
  2. Render it with the PlantUML CLI: java -jar <path-to>/plantuml.jar -tsvg -o <abs-path-to>/diagrams/rendered diagrams/sources/<name>.puml. Locate the jar/Java on this machine first (do not assume /opt/homebrew/bin/plantuml exists — that path is macOS-specific and will not exist on Windows; search the project's reforge-files/tools/ or ask where plantuml.jar and java live).
  3. Embed the rendered SVG in the relevant HTML page via <img src="../diagrams/rendered/<name>.svg">. Never paste raw <svg> markup inline into HTML — if you catch yourself writing an inline <svg> block, stop and go back to step 1.
  Quality gate before Phase 6 can be marked done — run and paste the output, do not just claim completion:
    a. Count .puml files in diagrams/sources/ and .svg files in diagrams/rendered/ — they must be equal, and both must be >= the number of state machines + UI subdomains + 10.
    b. Every rendered SVG's filename must appear as an <img src> in at least one generated HTML page (grep generated/html/*.html for each name).
    c. Zero raw <svg> tags may exist inside generated/html/*.html — grep for "<svg" in generated HTML and confirm 0 matches (only <img> references to diagrams/rendered/*.svg are allowed).
  If any of a/b/c fails, Phase 6 is NOT done — fix the missing sources/renders/embeds and re-run the gate. Do not proceed to Phase 7 until all three checks pass on a live re-run.

Phase 7 — user-stories.xml (50-80 stories, ~10 epics) cross-linked to real BR/FR/WF IDs. Render user-stories.html with embedded diagrams.

Phase 8 — generated/reports/documentation-audit.html rating every HTML page, enumerating diagram coverage, naming gaps honestly.

Phase 9 — universal-batch.txt: write a single project-root-level summary file, <output-dir>/universal-batch.txt, that is the canonical end-of-run report handed back to whoever asked for the run. Plain text, not markdown — no `**bold**`, no `#` headers; use plain dashes only for the closing findings list, never for the phase summary (that part is tabular, see below). Regenerate it (overwrite, don't append) any time Phase 1-8 output changes. It MUST follow this exact shape, scaled to what the run actually produced (no invented counts, no copy-pasted numbers from a different run):

  1. Opening line: "All phases from goal.md complete[, scaled per the approved plan]." — include the bracketed clause only if scale deviations actually occurred (see Phase 8).
  2. "Summary of what was produced in <reforge_output-relative-path, including the parent project dir (e.g. reforge-game/reforge_output/<project>/)>:" followed by a plain-text ASCII table, one row per phase actually executed, rendered with fixed-width columns and `+---+` / `|` border characters (monospace-safe, no markdown table syntax) so it lines up when the file is opened in a plain text viewer. Columns, in order: Phase | What it covers | Key artifacts / files | Counts | Time taken | Tokens. Populate every column from real, current data — the Counts/artifacts columns from on-disk files, and Time taken / Tokens from the START/DONE timestamps and per-agent-call usage captured live during that phase's own execution (Phase 1-2's row rolls up the batch-level rollup lines and TOKEN USAGE tables already written into each batch-*.txt during extraction itself; every other phase that dispatches sub-agents must likewise capture and log each call's usage as it returns, then roll that up here). Never invented, never estimated, and never sourced from a separate post-hoc verification pass — if a phase's agents were run in a way that made token capture genuinely impossible, say "n/a" and note why, rather than inventing a number or running an after-the-fact pass to backfill one. At minimum include rows for:
     - Phase 0: files segmented, total segments, whole-file vs member-pack vs block-split vs block-split-deep vs fallback-window counts, oversized members subdivided, degraded-integrity segments, and the coverage assertion result (must be 100.0% on every file).
     - Phase 1-2: files examined, segments dispatched, extraction types run, per-type counts, XML files passing the well-formedness gate, the decile-histogram verdict (flat vs U-shaped) with any remaining zero-citation ranges named, plus that phase's total wall time and total tokens rolled up across all batch-*.txt files.
     - Phase 4: derived artifact files and their counts (trace chains, dead-code findings, hotspots).
     - Phase 5: HTML doc count, cross-navigation status.
     - Phase 6: .puml/.svg counts, pipeline used (real PlantUML CLI, not inline <svg>), and whether the gate needed a fix-and-recheck pass.
     - Phase 7: user-story count and epic count, cross-linked to real BR/FR/WF IDs.
     - Phase 8: audit report filename and what it covers, plus a one-line rollup of any Phase 8 scale deviations.
     Wrap long cell text onto continuation lines within the same bordered row rather than widening the table past ~100 columns. After the table, add a run-level rollup line: "Run totals: wall time <sum>, tokens=<sum> [in=<sum> out=<sum> cache-read=<sum> cache-write=<sum>]." summed across every phase row above, and beneath it reproduce the full per-file TOKEN USAGE table (file basename + tokens, all files across all batches, plus grand total) so the run-level token breakdown is visible without opening every individual batch-*.txt.
  3. A closing paragraph titled by content (not literally "correctness catch" every time, but always naming the real category) that surfaces anything found during the run worth flagging on its own — a self-corrected mistake made during extraction, a genuine bug (BUG-*) discovered in the target codebase, or an unenforced assumption (ISSUE-*) the code silently depends on. Name the concrete ID(s) (e.g. BUG-001, ISSUE-004) and state the mechanism in one or two sentences each, as plain-dash bullets under the paragraph. If a run genuinely finds nothing worth flagging here, say so explicitly rather than omitting the section or inventing a finding.

  universal-batch.txt is meant to read standalone — someone opening only this file (not the chat transcript) should get the same picture as the final chat summary. Keep it terse: prefer the bullet/paragraph shape above over prose padding, and never let it drift out of sync with what's actually on disk in reforge_output/ — regenerate it from the real files, don't hand-carry stale numbers forward from an earlier draft.

Operating rules:
- Sonnet for batches; Opus only for orchestration/synthesis
- Pre-create cluster dirs (mkdir -p) before sub-agent launch
- Track with TaskCreate/TaskUpdate; filesystem state (ls _clusters/) beats agent notifications across session restarts
- Max 5-6 concurrent agents; more = transport failures
- Never claim 95% without running coverage_matrix.py against merged XML — audit headers can lie about denominators
- Never do a segment's extraction directly in the orchestrating session when a real token count is required — dispatch it to a sub-agent, per the Phase 1 token-capture rule, so the number is real from the start. The orchestrator never reads source files at all.
- The deterministic layer decides WHERE the code is, where a member begins and ends, what belongs together, how large a task may be, and what exact source an agent receives. The LLM decides only what that bounded source MEANS. Never let an agent choose or widen its own segment boundaries; if a segment looks wrong, fix the budget and re-run Phase 0, which is reproducible, rather than patching boundaries by hand.
- Segmentation is deterministic and cached: same bytes + same budget + same generator_version yields identical segments. Re-run Phase 0 freely; skip files where is_stale() is false. Never hand-edit a manifest — regenerate it.
- On a large legacy codebase spanning many batches and dozens/hundreds of sub-agent calls, don't hold every per-segment token figure in working memory to total at the end — write each segment's tokens into its batch-*.txt (and that batch's running TOKEN USAGE table) the moment its agent call returns, so a crash or session restart never loses already-captured numbers; per-file figures are a sum over segment rows, and Phase 9's run-level total is then just a mechanical sum over what's already on disk in every batch-*.txt, not a re-derivation.

Done means: every file segmented with a manifest reporting coverage_pct == 100.0 and members_assigned == members_total, every segment_id in every manifest carrying a DONE row, a flat (not U-shaped) decile-citation histogram on every multi-segment file with no zero-citation range >=500 lines left unexplained, ≥95% per-type coverage, 0 validation errors/duplicate IDs/unresolved refs, 50+ HTML pages with diagrams, 50+ rendered SVGs on disk in diagrams/rendered/ with matching .puml sources in diagrams/sources/ (every state machine + UI subdomain — no inline <svg> substitutes, per Phase 6's quality gate), every batch-*.txt file annotated in place with a DONE line + timestamp + real per-file token figures + artifact counts per source file (captured live during extraction, not backfilled), a TOKEN USAGE table in every batch-*.txt and a run-level rollup of the same in universal-batch.txt, user-stories.html, milestone + audit reports, 6 stakeholder CSVs, honest "what we didn't do" callouts, and a current universal-batch.txt (Phase 9) that matches what's actually on disk.

Start by reading existing reforge_output state and any existing analysis/segments/*.segments.json, then run Phase 0, then proceed.
