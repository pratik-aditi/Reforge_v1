---
tags:
  - guides
  - planning
---

# Effort Estimation Guide

Conservative guidance for estimating the effort, duration, and complexity of a Reforge engagement. Based on empirical data from production engagements, with safety margins built in.

!!! warning "Estimates are directional, not commitments"
    Every legacy codebase is different. These estimates assume a practitioner with moderate Reforge experience. First-time users should add 30-50% to all estimates. Codebases with unusual characteristics (obfuscated code, generated code, deeply nested macros) may require significantly more effort.

---

## Project Size Categories

| Category | Lines of Code | Source Files | Modules | Typical Duration |
|----------|:------------:|:-----------:|:-------:|:----------------:|
| **Small** | < 50K | < 100 | < 5 | 2-5 days |
| **Medium** | 50K - 200K | 100 - 400 | 5 - 15 | 1-3 weeks |
| **Large** | 200K - 500K | 400 - 800 | 15 - 30 | 3-6 weeks |
| **Very Large** | 500K+ | 800+ | 30+ | 6-12 weeks |

!!! note "Duration = calendar days with a single practitioner"
    These durations assume one person running Reforge commands iteratively, not wall-clock time of autonomous agent execution. Actual agent execution time per command is typically minutes to hours depending on codebase size.

---

## Phase-by-Phase Effort Breakdown

### Phase 1: Setup (Plan, Init, Profile, Analyze)

| Project Size | Estimated Effort | Notes |
|:------------|:----------------:|-------|
| Small | 1-2 hours | Analysis completes in a single pass |
| Medium | 2-4 hours | May need exclusion patterns configured |
| Large | 4-8 hours | Expect checkpointing; tune `chunkSize` |
| Very Large | 1-2 days | Requires exclusion tuning, possible chunked analysis |

**Key risk**: Analysis on very large files (10K+ LOC single files) can strain agent context windows. Reduce `chunkSize` in `.reforge/config.json` if the agent stalls.

### Phase 2: Extraction

Extraction is the most variable phase. Effort depends on how many extraction types you run and the density of extractable content.

#### Per-Type Effort Estimates

| Extraction Type | Small | Medium | Large | Very Large |
|:---------------|:-----:|:------:|:-----:|:----------:|
| business-rules | 1-2h | 4-8h | 1-3d | 3-7d |
| database | 1-2h | 2-4h | 4-8h | 1-3d |
| ui-flows | 1-2h | 2-6h | 1-2d | 2-5d |
| workflows | 1-2h | 2-4h | 4-8h | 1-2d |
| functional-requirements | 1-2h | 4-8h | 1-2d | 2-5d |
| non-functional | 1h | 2-4h | 4-8h | 1-2d |
| architecture | 1-2h | 4-8h | 1-3d | 3-7d |
| issues | 1h | 2-4h | 4-8h | 1-2d |
| call-sites | 1h | 2-4h | 4-8h | 1-3d |
| dependencies | 1h | 2-4h | 4-8h | 1-2d |

!!! tip "You don't need all 10 types"
    Most engagements use 4-6 types. The **core four** (`business-rules`, `database`, `ui-flows`, `workflows`) cover the majority of modernization needs. Add `functional-requirements` and `architecture` for comprehensive documentation. Add `call-sites` and `dependencies` only for migration planning.

#### Expected Extraction Yields

Based on production data, expect the following extraction density per 1,000 lines of code:

| Extraction Type | Items per 1K LOC | Confidence |
|:---------------|:----------------:|:----------:|
| business-rules | 2-4 | Medium |
| database interactions | 1-2 | High |
| ui-flows | 0.3-0.6 | Medium |
| workflows | 0.3-0.5 | Medium |
| functional-requirements | 1-2 | Medium |
| call-sites | 8-12 | High |
| dependencies | 0.5-1.5 | High |
| architecture elements | 1-2 | Low |

These are conservative midpoints. Domain-heavy applications (financial, healthcare, logistics) tend toward the high end for business rules. CRUD-heavy applications tend toward the high end for database interactions.

### Phase 3: Validation (Audit/Fix)

The audit/fix cycle is iterative. Plan for **3-5 cycles** to reach acceptable coverage.

| Project Size | Cycles to 85%+ Coverage | Estimated Effort |
|:------------|:-----------------------:|:----------------:|
| Small | 1-2 | 2-4 hours |
| Medium | 2-3 | 1-2 days |
| Large | 3-5 | 3-7 days |
| Very Large | 4-6 | 1-3 weeks |

**Coverage progression pattern** (observed):

| Cycle | Typical Coverage | What Happens |
|:-----:|:----------------:|:-------------|
| 1 | 50-60% | Baseline audit exposes major gaps |
| 2 | 70-80% | First correction plan fills structural gaps |
| 3 | 85-90% | Targeted fixes for remaining modules |
| 4 | 90-95% | Deep accuracy audit, line-number verification |
| 5 | 95%+ | Edge cases only (auto-generated files, stubs) |

!!! info "Diminishing returns above 90%"
    Pushing from 90% to 95%+ coverage takes disproportionate effort. The final 5% often consists of auto-generated files, designer files, or configuration stubs that contain no extractable business logic. Set your coverage target based on project goals, not perfection.

### Phase 4: Generation

Generation is the fastest phase — it operates on already-validated extraction XML.

| Project Size | Estimated Effort | Output Volume |
|:------------|:----------------:|:-------------:|
| Small | 1-2 hours | 20-50 files |
| Medium | 2-4 hours | 50-150 files |
| Large | 4-8 hours | 150-350 files |
| Very Large | 1-2 days | 350-500+ files |

---

## Complexity Multipliers

Not all codebases are equal. Apply these multipliers to the base estimates above:

| Factor | Multiplier | When to Apply |
|:-------|:---------:|:--------------|
| **Mixed languages** (2+) | 1.3x | Multiple primary languages (e.g., VB.NET + C#, Java + Kotlin) |
| **Legacy frameworks** | 1.2x | Pre-2010 frameworks, custom ORMs, proprietary libraries |
| **Minimal documentation** | 1.2x | No README, no comments, no architecture docs |
| **Deep inheritance** | 1.3x | 4+ levels of class inheritance, heavy polymorphism |
| **Large single files** | 1.4x | Files exceeding 5K LOC (agent context pressure) |
| **Generated code mixed in** | 1.2x | Designer files, ORM-generated code not separated |
| **Safety-critical domain** | 1.3x | Requires higher extraction confidence thresholds |
| **Obfuscated/minified code** | 1.5x-2.0x | Variable names stripped, control flow obscured |
| **First Reforge engagement** | 1.3-1.5x | Learning curve for the practitioner |
| **Monorepo with multiple apps** | 1.5x | Must analyze each app boundary separately |

**Example**: A 300K LOC codebase (Large) with mixed languages (1.3x) and large single files (1.4x) would have an effective complexity of Large x 1.82, pushing it toward the Very Large effort range.

---

## Assumptions

These estimates assume:

1. **Single practitioner** running Reforge commands through one AI agent session at a time
2. **Unobstructed access** to the full source tree (no restricted files, no binary-only modules)
3. **Readable source code** in a language the AI agent handles well (mainstream languages: Java, C#, Python, JavaScript/TypeScript, VB.NET, Go, Ruby, PHP, C/C++)
4. **Agent context window** of 100K+ tokens (Claude Code or GitHub Copilot with a capable model)
5. **Stable codebase** — no active development changing files mid-extraction
6. **Default Reforge configuration** — no custom schemas or template modifications
7. **Core extraction types** (4-6 types); using all 10 types adds 40-60% to extraction effort
8. **Coverage target** of 85-90%; targeting 95%+ adds 30-50% to validation effort

---

## Risks

| Risk | Likelihood | Impact | Mitigation |
|:-----|:---------:|:------:|:-----------|
| Agent stalls on very large files | High for files >10K LOC | Delays analysis phase | Reduce `chunkSize`, use `--files` scoping |
| Low extraction confidence in unfamiliar domain | Medium | Requires more clarification cycles | Run `/reforge.init` thoroughly with domain experts |
| Audit/fix cycle doesn't converge | Low | Extended validation phase | Set a coverage floor, accept diminishing returns |
| Generated code inflates file counts | Medium | False coverage gaps in audit | Add generated file patterns to exclusions |
| Context window exhaustion on large modules | Medium for 500K+ LOC | Incomplete extraction per pass | Scope extractions to specific directories with `--files` |
| Schema changes between Reforge versions | Low | Re-extraction needed | Pin Reforge version for the duration of the engagement |
| Checkpoint corruption on interrupted analysis | Low | Must restart analysis phase | Use `--resume` flag; keep `.reforge/memory/checkpoints/` intact |

---

## Reference Data Point

The following anonymized engagement provides a concrete reference:

| Dimension | Value |
|:----------|:------|
| **Codebase size** | ~600K LOC |
| **Source files** | ~1,000 |
| **Languages** | 2 primary (VB.NET, C#) + markup (XAML) |
| **Modules** | 29 (19 application + 10 library) |
| **Domain** | Industrial operations management (safety-critical) |
| **Framework** | .NET Framework 4.8, WinForms + WPF |
| **Extraction types used** | 8 of 10 |
| **Total items extracted** | ~11,400 structured items |
| **Extraction files produced** | 133 XML files (~7.6 MB) |
| **Audit cycles** | 5 rounds, 29 total corrections |
| **Coverage achieved** | 89-96% (100% excluding auto-generated files) |
| **Generated output** | ~490 files (~30 MB): 166 HTML, 62 PlantUML, 47 SVG, 25 markdown |
| **Active extraction + audit** | ~16 working days |
| **Total project duration** | ~29 calendar days |
| **Generation phase** | ~3 days (after extractions validated) |

### Phase timeline for the reference engagement

```
Week 1:  Analysis → Initial extractions (4 core types + architecture)
         First audit cycle (baseline: ~55% coverage)
         Correction plans v1-v2 (20 corrections)

Week 2:  Deep extractions (remaining modules)
         Audit cycles v3-v5 (88% → 96% coverage)
         9 additional corrections
         Glossary extraction

Week 3:  (Gap — team availability)

Week 4:  Documentation generation (HTML, user stories, cross-mappings)
         Additional extraction types (call-sites, dependencies)
         Final status reporting
```

### Key observations from this engagement

- **Business rules** were the highest-effort extraction type — 26 files, ~1,870 items, required the most audit corrections
- **Call-sites** produced the highest volume (6,267 items) but required the least human oversight
- **Audit coverage jumped dramatically** after the first correction plan (+34 percentage points in one cycle)
- **The final 10% of coverage** (90% → 100%) was mostly auto-generated `.Designer` files with no business logic
- **Generation was fast** relative to extraction — ~3 days for ~490 output files once extractions were validated
- **Large single files** (10K-22K LOC) required scoped extraction passes and were the primary source of audit corrections

---

## Guidance for Scoping an Engagement

### Step 1: Characterize the codebase

Before committing to an estimate, run a quick characterization:

=== "macOS / Linux"

    ```bash
    # Count source files
    find /path/to/project -name "*.java" -o -name "*.cs" -o -name "*.py" | wc -l

    # Count lines of code (install cloc first: brew install cloc / apt install cloc)
    cloc /path/to/project --quiet
    ```

=== "Windows (PowerShell)"

    ```powershell
    # Count source files
    (Get-ChildItem C:\path\to\project -Recurse -Include *.java,*.cs,*.py).Count

    # Count lines of code (install cloc first: winget install AlDanial.Cloc)
    cloc C:\path\to\project --quiet
    ```

Determine:

- Total LOC and file count → **size category**
- Number of languages → **complexity multiplier**
- Largest single file → **context pressure risk**
- Domain (financial, healthcare, industrial, etc.) → **extraction density**

### Step 2: Choose extraction types

| Goal | Recommended Types | Typical Count |
|:-----|:-----------------|:-------------:|
| **Quick assessment** | business-rules, database | 2 |
| **Modernization planning** | business-rules, database, ui-flows, workflows | 4 |
| **Full documentation** | All core + functional-requirements, architecture | 6 |
| **Migration readiness** | All 10 types | 10 |

### Step 3: Calculate effort estimate

```
Base effort (from Phase tables above)
  × Complexity multipliers (from Multipliers table)
  × Number of extraction types / 4 (normalized to core four)
  + Validation effort (from Audit/Fix table)
  + Generation effort (from Generation table)
  = Total estimated effort
```

### Step 4: Build in contingency

| Confidence Level | Contingency |
|:----------------|:-----------:|
| High (similar to past engagement) | +20% |
| Medium (new domain or language) | +40% |
| Low (unusual codebase characteristics) | +60-100% |

---

## Scaling with Parallel Agents

For very large codebases, Reforge supports scoping extractions to specific directories. This enables parallel execution with multiple agent sessions:

| Approach | Speedup | Coordination Overhead |
|:---------|:-------:|:---------------------:|
| Single agent, sequential | 1x (baseline) | None |
| 2 agents, split by module groups | 1.5-1.7x | Low — merge extraction outputs |
| 3-4 agents, split by extraction type | 2-3x | Medium — coordinate audit/fix |
| Team orchestration (Claude Code Teams) | 2-4x | Higher — requires team lead coordination |

See [Claude Code Teams](claude-code-teams.md) for details on parallel agent orchestration.

!!! warning "Parallel agents do not reduce audit/fix effort"
    The audit/fix cycle must operate on the complete set of extractions. Parallelism helps with the extraction phase but the validation phase remains sequential.
