---
tags:
  - commands
  - modernization
---

# /reforge.migrate

Generate a phased migration playbook with per-module modernization strategies.

## Syntax

=== "Claude Code"

    ```
    /reforge.migrate [--strategy 5r|lift-shift|strangler] [--phases n] [--format html|xml] [--json]
    ```

=== "GitHub Copilot"

    ```
    @reforge.migrate [--strategy 5r|lift-shift|strangler] [--phases n] [--format html|xml] [--json]
    ```

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `--strategy` | No | Migration strategy: `5r` (default), `lift-shift`, or `strangler` |
| `--phases` | No | Number of migration phases to plan (default: auto-calculated) |
| `--format` | No | Output format: `xml` (default) or `html` for a styled playbook |
| `--json` | No | Output playbook as JSON for tooling integration |

## What It Does

This command produces a phased migration playbook that assigns each module a modernization strategy and organizes work into sequential phases.

The default **5R strategy** classifies each module as one of:

- **Rehost** -- move as-is with minimal changes
- **Replatform** -- adopt managed services without code changes
- **Refactor** -- restructure code for the target platform
- **Rearchitect** -- redesign to leverage cloud-native patterns
- **Retire** -- decommission modules no longer needed

The playbook includes:

- **Phase assignments** -- modules grouped into ordered phases based on dependencies and risk
- **Risk register** -- identified risks per phase with mitigation strategies
- **Dependency sequencing** -- ensures modules are migrated in the correct order

Alternative strategies (`lift-shift`, `strangler`) produce playbooks tailored to those approaches.

## Prerequisites

- Completed analysis (`/reforge.analyze`)
- Dependencies extraction required for dependency sequencing
- Architecture, issues, business-rules, and non-functional extractions recommended

## Output

Files are written to `reforge_output/<project>/generated/`:

| File | Description |
|------|-------------|
| `migration-playbook.xml` | Phased playbook with strategy assignments, risk register, and sequencing |

## Example

=== "Claude Code"

    ```
    /reforge.migrate
    /reforge.migrate --strategy strangler
    /reforge.migrate --phases 4
    /reforge.migrate --format html
    /reforge.migrate --json
    ```

=== "GitHub Copilot"

    ```
    @reforge.migrate
    @reforge.migrate --strategy strangler
    @reforge.migrate --phases 4
    @reforge.migrate --format html
    @reforge.migrate --json
    ```

## Related Commands

- [`/reforge.estimate`](estimate.md) -- effort estimates for each migration phase
- [`/reforge.recommend`](recommend.md) -- target technology recommendations
- [`/reforge.hotspot`](hotspot.md) -- risk scores informing phase prioritization
