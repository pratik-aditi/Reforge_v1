# User Story Template

> Template for generating individual user stories from extracted artifacts

## Template Variables

| Variable | Source | Description |
|----------|--------|-------------|
| `{{story.id}}` | Generated | Unique story identifier (US-XXX) |
| `{{story.title}}` | Derived | Descriptive title from workflow/rule |
| `{{story.priority}}` | Derived | critical/high/medium/low |
| `{{story.epic_ref}}` | Derived | Parent epic ID |
| `{{story.points}}` | Estimated | Story point estimate |
| `{{story.as_a}}` | Extracted | User role from UI/workflow |
| `{{story.i_want}}` | Extracted | Action from workflow/rule |
| `{{story.so_that}}` | Extracted | Business value |
| `{{story.criteria}}` | Generated | Array of acceptance criteria |
| `{{story.traceability}}` | Linked | Source artifact references |
| `{{story.notes}}` | Generated | Modernization notes |

## Markdown Output Template

```markdown
## {{story.id}}: {{story.title}}

**Priority:** {{story.priority}} | **Points:** {{story.points}} | **Epic:** {{story.epic_ref}}

### User Story

**As a** {{story.as_a}},
**I want** {{story.i_want}},
**So that** {{story.so_that}}.

### Acceptance Criteria

{{#each story.criteria}}
- [ ] **{{this.id}}**: Given {{this.given}}, when {{this.when}}, then {{this.then}}.
{{/each}}

### Traceability

| Type | ID | Confidence |
|------|-----|------------|
{{#each story.traceability}}
| {{this.type}} | {{this.id}} | {{this.confidence}} |
{{/each}}

{{#if story.notes}}
### Notes

{{story.notes}}
{{/if}}

---
```

## JSON Output Template

```json
{
  "id": "{{story.id}}",
  "title": "{{story.title}}",
  "priority": "{{story.priority}}",
  "epic_ref": "{{story.epic_ref}}",
  "story_points": {{story.points}},
  "as_a": "{{story.as_a}}",
  "i_want": "{{story.i_want}}",
  "so_that": "{{story.so_that}}",
  "acceptance_criteria": [
    {{#each story.criteria}}
    {
      "id": "{{this.id}}",
      "given": "{{this.given}}",
      "when": "{{this.when}}",
      "then": "{{this.then}}",
      "source_ref": "{{this.source_ref}}"
    }{{#unless @last}},{{/unless}}
    {{/each}}
  ],
  "traceability": {
    "business_rules": [{{#each story.traceability.rules}}"{{this}}"{{#unless @last}},{{/unless}}{{/each}}],
    "workflows": [{{#each story.traceability.workflows}}"{{this}}"{{#unless @last}},{{/unless}}{{/each}}],
    "ui_components": [{{#each story.traceability.ui}}"{{this}}"{{#unless @last}},{{/unless}}{{/each}}],
    "database_ops": [{{#each story.traceability.db}}"{{this}}"{{#unless @last}},{{/unless}}{{/each}}]
  },
  "notes": "{{story.notes}}"
}
```

## CSV Output Template

```csv
ID,Title,Priority,Epic,Points,As A,I Want,So That,Criteria Count,Rules,Workflows,Notes
{{story.id}},"{{story.title}}",{{story.priority}},{{story.epic_ref}},{{story.points}},"{{story.as_a}}","{{story.i_want}}","{{story.so_that}}",{{story.criteria.length}},"{{story.traceability.rules|join:';'}}","{{story.traceability.workflows|join:';'}}","{{story.notes}}"
```

## Story Generation Rules

### Source-Anchored Generation (Mandatory)

All generated user stories MUST comply with the Source-Anchored Generation constraints
defined in Step 0.6 of `.reforge/commands/generate.md`. Key obligations:

1. Extraction XML is the sole source of truth for all story content
2. All identifiers (rule IDs, workflow IDs, component IDs) MUST be copied verbatim from extraction XML
3. All statistics (story counts, criteria counts) MUST be computed with visible derivation formulas
4. `[DATA GAP]` markers MUST replace any content not supported by extraction data
5. Provenance annotations MUST cite extraction source files and element counts
6. The Content Validation Checklist MUST be completed before finalizing any story output
7. The agent MUST NOT read source code files directly — all source context comes from extraction XML

### Priority Derivation

| Source Signal | Priority |
|---------------|----------|
| Business rule with `critical` flag | critical |
| Workflow with `startup` trigger | high |
| UI screen marked as primary | high |
| Standard business rule | medium |
| Secondary UI component | low |

### Story Point Estimation

| Complexity Indicators | Points |
|----------------------|--------|
| Single rule, no branches | 1-2 |
| Rule with conditions + workflow | 3-5 |
| Multiple workflows + UI + database | 5-8 |
| Complex branching + external calls | 8-13 |

### As-A Role Derivation

1. Check UI component for user role indicators
2. Check workflow trigger type
3. Default to "User" if unclear

### I-Want Action Derivation

1. Primary: Workflow name/entry point
2. Secondary: Business rule description
3. Tertiary: UI component action

### So-That Value Derivation

1. Business rule `so-that` or outcome
2. Workflow end state/notification
3. Generic business value statement

## Acceptance Criteria Generation

For each linked business rule, generate a criterion:

```
Given: Rule preconditions or entity state
When: Rule trigger or action
Then: Rule outcome or assertion
```

Example mapping:

```
Business Rule: "Discount applies when order total exceeds $100"
→ Given: I have a cart totaling over $100
→ When: I submit my order
→ Then: a 10% discount is applied to the total
```

## Example Generated Story

### Input Artifacts

- Business Rule BR-001: "Order discount for totals over $100"
- Workflow WF-001: "Order Submission" triggered by UI action
- UI Component CMP-011: "Submit Order" button

### Generated Output

```markdown
## US-001: Submit Order with Discount

**Priority:** high | **Points:** 5 | **Epic:** EPIC-001

### User Story

**As a** Customer,
**I want** to submit my order and receive applicable discounts,
**So that** I can complete my purchase with the best price.

### Acceptance Criteria

- [ ] **AC-001**: Given I have items totaling over $100, when I submit the order, then a 10% discount is applied.
- [ ] **AC-002**: Given I have an empty cart, when I try to submit, then I see an error message.

### Traceability

| Type | ID | Confidence |
|------|-----|------------|
| Business Rule | BR-001 | high |
| Business Rule | BR-002 | high |
| Workflow | WF-001 | high |
| UI Component | CMP-011 | high |

---
```
