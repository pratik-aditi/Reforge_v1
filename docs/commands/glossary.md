---
tags:
  - commands
  - extraction
---

# /reforge.glossary

Extract, verify, and persist a glossary of acronyms and abbreviations found in the codebase.

## Syntax

```
/reforge.glossary [--phase <1|2|3|4|all>] [--resume] [--skip-external] [--team-size <n>]
```

## Arguments

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `--phase` | No | `all` | Run specific phase: `1` (extract), `2` (verify), `3` (audit), `4` (self-audit), or `all` |
| `--resume` | No | -- | Resume from last checkpoint |
| `--skip-external` | No | -- | Skip Phase 2 (external verification) for air-gapped environments |
| `--team-size` | No | `3` | Number of worker agents for parallel processing (range: 1--6) |

## What It Does

This command runs a 4-phase pipeline to build a verified glossary of acronyms and abbreviations:

1. **Phase 1 -- Pattern Extraction**: Scans source files for acronyms/abbreviations using pattern matching
2. **Phase 2 -- External Verification**: Looks up acronyms via web search against authoritative sources
3. **Phase 3 -- Source Code Audit**: Verifies every entry using word-boundary grep against source files
4. **Phase 4 -- Self-Audit**: Independent re-verification of modified and low-confidence entries

Each phase produces a versioned update to the glossary XML (v1.0.0 through v1.3.0). Entries are classified with verdicts such as CONFIRMED, CORRECTED, or FABRICATED (removed). The final glossary is persisted to `.reforge/memory/glossary.json` for consumption by all other Reforge commands.

The pipeline supports checkpointing -- you can interrupt and resume with `--resume`. Use `--skip-external` in air-gapped environments where web search is unavailable.

## Prerequisites

- Analysis must be completed (`/reforge.analyze`)

## Output

| File | Location |
|------|----------|
| Glossary XML | `reforge_output/<project>/extractions/acronym-glossary.xml` |
| Audit Report | `reforge_output/<project>/audit/glossary-audit-report.xml` |
| Memory Lookup | `.reforge/memory/glossary.json` |

## Example

=== "Claude Code"

    ```
    /reforge.glossary
    /reforge.glossary --phase 1
    /reforge.glossary --resume
    /reforge.glossary --skip-external --team-size 1
    ```

=== "GitHub Copilot"

    ```
    @reforge.glossary
    @reforge.glossary --phase 1
    @reforge.glossary --resume
    @reforge.glossary --skip-external --team-size 1
    ```

## Related Commands

- [`/reforge.analyze`](analyze.md) -- must be run before glossary extraction
- [`/reforge.extract`](extract.md) -- other extraction types that benefit from glossary context
- [`/reforge.status`](status.md) -- shows glossary availability and entry count
