# Quickstart: Glossary Command

**Feature**: 013-glossary-command | **Date**: 2026-02-23

## Prerequisites

1. Reforge framework initialized in project (`.reforge/` directory exists)
2. Codebase analyzed via `/reforge.analyze` (`analysis.xml` present in output directory)
3. AI agent with Read, Write, Glob, Grep capabilities (WebSearch optional for Phase 2)

## Basic Usage

### Full Pipeline (All 4 Phases)
```
/reforge.glossary
```
Runs Phases 1-4 sequentially: Pattern Extraction → External Verification → Source Code Audit → Self-Audit. Produces `acronym-glossary.xml`, `glossary-audit-report.xml`, and `.reforge/memory/glossary.json`.

### Skip External Verification (Air-Gapped)
```
/reforge.glossary --skip-external
```
Runs Phases 1, 3, 4 only. Glossary versions: v1.0.0 → v1.2.0 → v1.3.0 (skipping v1.1.0).

### Run a Specific Phase
```
/reforge.glossary --phase 3
```
Runs only Phase 3 (Source Code Audit). Requires that earlier phases have already completed.

### Resume After Interruption
```
/reforge.glossary --resume
```
Picks up from the last completed phase checkpoint.

### Custom Team Size
```
/reforge.glossary --team-size 5
```
Uses 5 worker agents for parallel processing (range: 1-6, default: 3). Use `--team-size 1` for single-agent mode.

## Output Files

| File | Location | Purpose |
|------|----------|---------|
| Glossary XML | `reforge_output/<project>/extractions/acronym-glossary.xml` | Full glossary with all entries, evidence, and metadata |
| Audit Report | `reforge_output/<project>/audit/glossary-audit-report.xml` | Phase 3-4 verification findings |
| Memory Lookup | `.reforge/memory/glossary.json` | Persistent lookup for cross-command consumption |
| Checkpoint | `.reforge/memory/checkpoints/glossary-checkpoint.json` | Resume state (cleaned up on success) |

## What Happens After

Once the glossary is persisted to memory:
- `/reforge.generate` expands acronyms on first occurrence per section and appends a glossary appendix
- `/reforge.extract` annotates extracted items with full terminology
- `/reforge.audit` uses glossary terms as verification targets
- `/reforge.status` reports glossary version and entry count

If no glossary exists, all commands gracefully degrade (no errors, no glossary features).

## Implementation Files

| File | Purpose |
|------|---------|
| `.reforge/commands/glossary.md` | Parent orchestrator template (flag routing, checkpoints, phase dispatch) |
| `.reforge/commands/glossary-phase-1.md` | Phase 1: Pattern Extraction |
| `.reforge/commands/glossary-phase-2.md` | Phase 2: External Verification (WebSearch) |
| `.reforge/commands/glossary-phase-3.md` | Phase 3: Source Code Audit (word-boundary grep) |
| `.reforge/commands/glossary-phase-4.md` | Phase 4: Self-Audit |
| `.reforge/schemas/glossary.md` | Glossary XML schema definition |

## Contracts

N/A — This feature consists entirely of markdown prompt templates and XML/JSON schema definitions. There are no REST APIs, GraphQL endpoints, or programmatic interfaces. The "contract" between phases is the glossary XML file: each phase reads and writes the same `acronym-glossary.xml` with version increments.
