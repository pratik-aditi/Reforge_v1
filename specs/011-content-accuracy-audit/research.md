# Research: Content Accuracy Audit

**Feature**: 011-content-accuracy-audit
**Date**: 2026-02-22
**Status**: Complete

## Research Summary

No technology unknowns or NEEDS CLARIFICATION items exist. This feature modifies markdown prompt templates and schema definition files only (no compiled code). Research focused on: (1) structuring the audit.md command extension, (2) defining the accuracy verification methodology, (3) designing the consistency check categories, (4) planning the fix command update, and (5) determining the statistical sampling approach.

## R1: Audit Command Extension Strategy

**Decision**: Extend the existing `.reforge/commands/audit.md` by adding new workflow sections for accuracy, consistency, and full audit modes. The type argument validation (Step 1.5) is extended to recognize the three new values. Each new mode gets its own self-contained workflow section inserted after the existing Step 7.

**Rationale**: The existing audit command is 697 lines with a well-defined step structure (Step 0 through Step 7). Adding new audit modes as new step groups (e.g., "Accuracy Audit Workflow", "Consistency Audit Workflow", "Full Audit Workflow") after the existing display results step preserves backward compatibility -- the existing steps 1-7 remain untouched and continue to handle the coverage audit. A routing section at the top (after Step 1.5) dispatches to the correct workflow based on the type argument.

**Alternatives considered**:
- Separate command files per audit type (`audit-accuracy.md`, `audit-consistency.md`): Rejected -- would fragment the audit command and require users to learn multiple commands. The spec explicitly calls for a single `/reforge.audit` command with type argument.
- Insert new audit logic inline within existing steps: Rejected -- would entangle coverage audit with new audit types, risking backward compatibility violations (FR-020).

## R2: Accuracy Verification Methodology

**Decision**: The accuracy audit uses a multi-check-type approach with 7 check types (FR-023). For each extraction item, the agent selects applicable check types based on the item's content:
- **identifier-exists**: Grep the source codebase for `\b<identifier>\b` using word-boundary matching
- **term-exists**: Grep for the term as a natural-language occurrence (comments, strings, docs)
- **line-reference**: Read the referenced file and verify content exists at the stated line
- **content-match**: Compare extracted code snippets against actual source content
- **expansion-match**: For acronyms, verify the expansion matches what's found near the acronym in source
- **count-match**: For stated counts, recount the actual elements
- **relationship-match**: For stated relationships (e.g., "X calls Y"), verify the relationship exists in source

**Rationale**: Different extraction item types require different verification approaches. A business rule identifier needs `identifier-exists`, an acronym entry needs `identifier-exists` + `expansion-match`, a source reference needs `line-reference` + `content-match`. The 5-verdict classification (FR-022) maps naturally: `confirmed` (all checks pass), `plausible` (partial match, e.g., substring), `incorrect` (found but wrong value), `fabricated` (no evidence in source), `skipped` (check not applicable or could not be performed).

**Alternatives considered**:
- Single check type (identifier search only): Rejected -- insufficient for source references, acronym expansions, and relationship claims.
- Compiled regex engine: Rejected -- Constitution Principle I prohibits compiled code. The agent's native Grep tool supports regex.

## R3: Consistency Check Category Design

**Decision**: Five consistency check categories (FR-014), executed in this order:
1. **arithmetic**: Compare `<metadata>/<total-count>` (and `confidence-distribution` sums) against actual child element counts per extraction file
2. **cross-reference**: Verify `<cross-ref target="...">` and `<source file="...">` references resolve to existing files/IDs
3. **duplicate-id**: Collect all `id` attributes across extraction files; detect duplicates within-file (critical), within-category (critical), cross-category (info)
4. **freshness**: Compare extraction `generated` timestamps against generated document timestamps; compare numeric claims in generated docs against current extraction data
5. **cross-document**: Scan all generated documents for numeric claims about the same metric; flag where values disagree

**Rationale**: Ordering follows dependency: arithmetic validates individual files first, cross-reference validates inter-file links, duplicate-id validates global uniqueness, freshness compares extractions to generated output, and cross-document validates generated output consistency. This progression from local to global catches cascading inconsistencies at their source.

**Alternatives considered**:
- Run all checks in parallel: Rejected -- freshness checks need accurate extraction metadata (validated by arithmetic checks first). Sequential ordering catches errors closer to their root cause.
- Include a "schema validation" category: Rejected -- schema validation is a prerequisite concern (common-schema.md), not a consistency concern.

## R4: Fix Command Deletion Action

**Decision**: Add a new action pattern to fix.md for `type="fabricated"` corrections. The action field uses the format `action="/reforge.fix-item delete <extraction-file> <item-id>"` which instructs the agent to:
1. Read the extraction XML file
2. Locate the element with the specified ID
3. Remove the element
4. Update the `<metadata>/<total-count>` to reflect the removal
5. Write the updated file

**Rationale**: Fabricated items should be deleted, not re-extracted. The existing fix command dispatches actions like `/reforge.reanalyze` and `/reforge.extract` -- these create or update content. Deletion is a fundamentally different operation that needs explicit prompt guidance for the agent. Using an inline action pattern (rather than a new command) keeps the change minimal per the clarification decision.

**Alternatives considered**:
- Create a new `/reforge.delete-item` command: Rejected -- over-engineering for a single action type. A dispatch case within the existing fix workflow is simpler.
- Rely on the agent to figure out deletion: Rejected -- explicit instructions prevent ambiguity about whether to delete, archive, or comment out the fabricated item.

## R5: Statistical Sampling Implementation

**Decision**: The agent implements stratified random sampling procedurally within the prompt template instructions:
1. Count total items per extraction category (stratum)
2. Compute sample size per stratum: `max(5, ceil(stratum_count * sample_rate))`
3. Select items from each stratum using a deterministic spread: every Nth item (systematic sampling) starting from a random offset
4. After verification, compute confidence interval: `accuracy ± 1.96 * sqrt(accuracy * (1-accuracy) / n)`
5. If any stratum accuracy < 90%, recommend full verification of that stratum

**Rationale**: Systematic sampling (every Nth item) is implementable by the agent using simple counting without random number generation. The minimum of 5 per stratum ensures even small categories get meaningful representation. The confidence interval formula is the standard Wald interval for proportions, appropriate for sample sizes ≥ 30.

**Alternatives considered**:
- True random sampling: Rejected -- agents don't have reliable random number generators. Systematic sampling with the Nth-item approach achieves similar statistical properties.
- Cluster sampling (by file): Rejected -- items from the same file may share common patterns, reducing sample diversity.

## R6: Agent-Agnostic Language Verification

**Decision**: All new prompt text uses "the agent MUST" phrasing consistently, following the pattern established in feature 010.

**Rationale**: Constitution Principle V requires agent-agnostic design. Verified no agent-specific references needed.

**Alternatives considered**: None -- Constitution requirement is non-negotiable.
