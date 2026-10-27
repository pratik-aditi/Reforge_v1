# Current Extraction Flow (Layer 1 Analysis)

> Scope: read-only analysis of how Reforge discovers and reads source today.
> No existing file was modified to produce this document.

## 1. Execution model

Reforge extraction is **a single agent in a single context**, executing the prompt
template `.reforge/commands/extract.md` (1,637 lines) top to bottom.

Verified by search: the strings `sub-agent`, `subagent`, `Task tool`, `spawn`,
`in parallel`, and `Agent tool` appear **nowhere** in `.reforge/commands/`.

This is the single most important finding of Layer 1, and it corrects the premise of
`reforge-update.txt`, which speaks of "the existing Sonnet extraction sub-agents" and
asks Agent 6 to "connect the new segments to" them. **There are no extraction
sub-agents today.** Layer 6 must *introduce* fan-out orchestration, not integrate
with it.

## 2. Step sequence (business-rules, the most developed type)

| Step | Line | What happens |
|------|------|--------------|
| 0 | 56 | `reforge-scripts check-prerequisites --json --require-analysis` → JSON with `PROJECT_NAME`, `REPO_ROOT`, `PROJECT_OUTPUT_DIR`, `CONFIG`, `ANALYSIS_STATUS`, `AVAILABLE_EXTRACTIONS`, `CHECKPOINT`, `CLARIFICATIONS_DIR` |
| 0.5 | 77 | Load `.reforge/memory/project-context.md` (optional) |
| 0.6 | 86 | Load `.reforge/memory/extraction-profile.md` (optional) |
| 0.7 | 100 | Read/update `.reforge/memory/project-plan.md` (optional) |
| 0.8 | 121 | Load `.reforge/memory/glossary.json` (optional) |
| 1 | 134 | Read `analysis/analysis.xml` → file list, languages, component locations |
| — | **140–146** | **The read mandate — see §3. This is the segmentation policy today.** |
| 2 | 149 | LLM scans for conditional / validation / calculation / constraint / enum patterns |
| 2.5 | 247 | Verbatim extraction rules (anti-hallucination mandate) |
| 3 | 268 | Extract rule details, confidence, category, source refs |
| 4 | 326 | Group related rules |
| 5 | 332 | Generate output XML |
| 5.5 | 394 | Post-extraction verification (re-read ≥20% of refs) |
| 5.6 | 432 | Schema compliance validation |
| 6 | 501 | Report results |

Shared trailing sections (apply to all types): `## Required Validation` (~1568),
`## Output Schema References` (~1620).

## 3. How source is read today

`extract.md:140-146`, verbatim:

```
**CRITICAL**: For every file you extract from, you MUST:
1. Read the file using the Read tool IN THIS SESSION before writing any extraction from it
2. Do NOT extract from memory of previous sessions or from analysis.xml metadata alone
3. If a file is too large to read in one pass, read it in sections and process each section
4. Track which files you have actually read -- only reference files read in this session
```

**Line 3 is the entire current segmentation policy**, and it delegates the boundary
decision to the LLM, at the exact moment the LLM's context is most saturated. This is
the root cause named in `reforge-update.txt`.

`.reforge/config.json` contains `analysis.chunkSize: 5000`, but it is referenced by no
command template — it is dead configuration.

## 4. Per-type divergence (affects insertion design)

Each extraction type restarts its own `Step 1`:

| Type | Line | Has a read mandate? |
|------|------|---------------------|
| business-rules | 134 | **Yes** (140–146) |
| database | 548 | No |
| ui | 791 | No |
| workflows | 953 | No |

Steps 0–0.8 sit textually under the `# Business Rules Extraction` heading (line 47)
yet are relied on by every type. The template has **no shared preamble section**.
Consequence: a segmentation step cannot be inserted in exactly one place without
either (a) editing four `Step 1` blocks, or (b) first promoting Steps 0–0.8 into a
shared section — which is a structural edit to a 1,637-line file.

## 5. Checkpoint / resume

`src/reforge_cli/scripts/manage_checkpoint.py` stores XML at
`.reforge/memory/checkpoints/<type>-checkpoint.xml` with fields:

```
total-files, processed-files, current-file, started-at, elapsed-seconds
```

Granularity is **whole files**. There is no segment, offset, or line-range concept.
Separately, `extract.md` never calls `checkpoint` — the `CHECKPOINT` field returned by
`check-prerequisites` is read but never acted on. Extraction today has **no working
resume at all**.

## 6. Helper-script infrastructure

- Package: `src/reforge_cli/` — `__init__.py` (Typer apps `app` and `scripts`) plus
  `scripts/{common,check_prerequisites,manage_checkpoint,init_project,migrate_output,update_agent_context,validation}.py`
- Prompts invoke helpers as `reforge-scripts <subcommand>` (entry point in `pyproject.toml`)
- Registered subcommands: `init-project`, `check-prerequisites`, `checkpoint`,
  `update-context`, `validate-xml`
- Dependencies: `typer`, `rich` only. Helpers are otherwise pure stdlib.
- Tests: `tests/test_scripts.py` using `pytest` + `typer.testing.CliRunner`;
  fixtures under `tests/fixtures/`

**Precedent established:** deterministic mechanics (path resolution, checkpointing,
XSD validation) already live in Python. The deterministic source layer is consistent
with that precedent, not a departure from it.

## 7. Blast radius — other commands that read source

`analyze.md`, `audit.md`, `dead-code.md`, `delta.md`, `metrics.md`, `profile.md`

All would benefit from the segment manifest later. **None are in scope now.**

## 8. Benchmark files

`Track.vb`, `Signal.vb`, `AdministrativeEvent.vb` are **not present in this
repository**. Layer 2 tests must therefore run against synthetic VB.NET fixtures
committed under `tests/fixtures/vbnet/`, with the real files used only in a separate,
manually-run benchmark against a legacy checkout.
