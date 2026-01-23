# Research: Reforge Legacy Analyzer Framework

**Branch**: `001-legacy-analyzer` | **Date**: 2025-01-13

## Overview

This document captures research findings and design decisions for the Reforge framework. All clarifications were resolved during the `/speckit.clarify` phase; this research focuses on best practices and implementation patterns.

---

## R1: XML Schema Design Patterns

**Context**: FR-007 requires structured XML files with defined schemas for all extractions.

**Decision**: Use self-describing XML with embedded source references and confidence indicators.

**Rationale**:
- XML is LLM-friendly for both reading and writing
- Self-describing format reduces need for separate schema validation tools
- Embedded source references (file:line) enable traceability without external linking
- Confidence levels as attributes allow filtering in downstream processing

**Alternatives Considered**:
- JSON: Rejected because XML handles nested hierarchies better and is more self-documenting
- YAML: Rejected because less precise for complex nested structures
- Custom format: Rejected to maintain compatibility with standard tooling

**Pattern**:
```xml
<extraction type="business-rule" confidence="high">
  <source file="src/Order.java" line-start="145" line-end="152"/>
  <description>Apply 10% discount when order total exceeds $500</description>
  <logic>if (orderTotal > 500) { discount = 0.10; }</logic>
  <entities>Order, Discount</entities>
</extraction>
```

---

## R2: Checkpoint and Resume Strategy

**Context**: FR-010/FR-019 require resumable sessions with checkpoint state in `.reforge/memory/`.

**Decision**: File-based checkpoints using XML with per-file analysis status.

**Rationale**:
- XML aligns with other extraction outputs (Principle III)
- Per-file granularity enables precise resume without re-analysis
- File-based storage requires no database (Principle I - LLM-first)
- Human-readable for debugging and manual intervention

**Alternatives Considered**:
- SQLite database: Rejected as external dependency
- JSON state file: Acceptable but XML preferred for consistency
- In-memory only: Rejected as not persistent across sessions

**Pattern**:
```xml
<checkpoint project="legacy-app" timestamp="2025-01-13T10:30:00Z">
  <progress total="1000" completed="450" pending="550"/>
  <files>
    <file path="src/Order.java" status="completed" hash="abc123"/>
    <file path="src/Customer.java" status="in-progress" position="line:200"/>
    <file path="src/Payment.java" status="pending"/>
  </files>
  <extractions completed="business-rules,database" pending="ui,workflows"/>
</checkpoint>
```

---

## R3: Confidence Level Assignment

**Context**: FR-021 requires confidence levels (high/medium/low) on each extraction.

**Decision**: Heuristic-based confidence assignment with explicit criteria.

**Rationale**:
- Enables users to prioritize review effort
- Integrates with clarification workflow (low confidence → clarification candidate)
- Transparent criteria help users understand and calibrate

**Criteria**:
| Level | Criteria |
|-------|----------|
| **High** | Clear patterns, explicit code comments, standard idioms, unambiguous logic |
| **Medium** | Recognizable patterns with some ambiguity, missing context, complex conditions |
| **Low** | Unclear intent, magic numbers, obfuscated code, multiple valid interpretations |

**Alternatives Considered**:
- Numeric scores (0-100): Rejected as false precision for LLM-based analysis
- Binary (certain/uncertain): Rejected as insufficient granularity
- No confidence: Rejected per clarification decision

---

## R4: UI Layout Visualization Format

**Context**: FR-005 requires visual UI layout representation (ASCII art or structured notation).

**Decision**: ASCII art with component annotations using box-drawing characters.

**Rationale**:
- Works in any text environment (terminal, markdown, chat)
- No external rendering dependencies (Principle I)
- Familiar to developers and non-technical stakeholders
- Supports component labeling and interaction mapping

**Alternatives Considered**:
- SVG generation: Rejected as requires rendering tools
- HTML mockups: Rejected as external dependency
- PlantUML: Acceptable for UML diagrams but ASCII preferred for quick layouts

**Pattern**:
```
┌─────────────────────────────────────────┐
│ Order Entry Screen                      │
├─────────────────────────────────────────┤
│ Customer: [________▼] (dropdown)        │
│ Product:  [__________] (text input)     │
│ Quantity: [___] (number)                │
│                                         │
│ ┌─────────┐ ┌─────────┐                │
│ │ Submit  │ │ Cancel  │                │
│ └─────────┘ └─────────┘                │
│  ^onClick:submitOrder()                 │
└─────────────────────────────────────────┘
Source: templates/order-entry.jsp:1-45
```

---

## R5: Workflow Tracing Strategy

**Context**: FR-006 requires tracing execution flows from user triggers through all called methods.

**Decision**: Static analysis via pattern matching, not runtime tracing.

**Rationale**:
- Aligns with LLM-first architecture (no code execution)
- Works across any language without language-specific tooling
- Safe for legacy code that may not run in current environment
- Pattern matching sufficient for most call graphs

**Approach**:
1. Identify entry points (UI handlers, API endpoints, scheduled jobs)
2. Follow method calls using grep/read patterns
3. Track data access operations (SQL, file I/O, API calls)
4. Build call tree with decision points
5. Assign confidence based on call chain clarity

**Limitations**:
- Dynamic dispatch may cause missed paths (document as medium/low confidence)
- Reflection-based calls not always traceable
- External library internals not traced

**Alternatives Considered**:
- Runtime profiling: Rejected as requires code execution
- AST parsing: Rejected as external dependency
- IDE integration: Rejected as agent-specific

---

## R6: User Story Generation Template

**Context**: FR-022 requires generating user stories from extracted metadata.

**Decision**: Template-based generation with traceability links and acceptance criteria derivation.

**Rationale**:
- Consistent format across all generated stories
- Traceability enables validation and impact analysis
- Acceptance criteria derived from source extraction ensures testability

**Template**:
```markdown
## US-{id}: {title}

**As a** {actor derived from UI flow or workflow}
**I want to** {action derived from business rule or workflow step}
**So that** {value derived from business context}

### Acceptance Criteria

- [ ] {criterion 1 derived from source rule logic}
- [ ] {criterion 2 derived from validation rules}
- [ ] {criterion 3 derived from edge cases}

### Source Traceability

- Business Rule: {rule-id} ({confidence})
- Workflow: {workflow-id}, Step {step-number}
- UI Component: {component-id}
- Database: {table operations}

### Priority Suggestion

{Priority based on rule complexity, workflow centrality, and usage patterns}
```

---

## R7: Multi-File XML Output Strategy

**Context**: Large codebases may generate XML outputs exceeding practical file sizes.

**Decision**: Category-based file splitting with cross-reference indices.

**Rationale**:
- Keeps individual files manageable for LLM context windows
- Category separation supports selective loading
- Index file enables navigation without loading all content

**Structure**:
```
reforge_output/<project>/
├── index.xml              # Master index with references to all files
├── analysis.xml           # Codebase inventory (may split by module)
├── business-rules.xml     # All business rules
├── business-rules-2.xml   # Overflow if needed
├── database.xml
├── ui-flows.xml
├── workflows.xml
└── generated/
```

**Index Pattern**:
```xml
<reforge-index project="legacy-app" generated="2025-01-13T12:00:00Z">
  <file type="analysis" path="analysis.xml" entries="1000"/>
  <file type="business-rules" path="business-rules.xml" entries="500"/>
  <file type="business-rules" path="business-rules-2.xml" entries="150"/>
  <!-- ... -->
</reforge-index>
```

---

## R8: Analysis Log Format

**Context**: FR-023 requires transparency logs for debugging and validation.

**Decision**: Append-only XML log with structured entries per file analyzed.

**Rationale**:
- Supports debugging without modifying extraction outputs
- Enables audit trail for compliance requirements
- Append-only prevents accidental data loss

**Pattern**:
```xml
<log-entry timestamp="2025-01-13T10:35:22Z" file="src/Order.java">
  <action>analyze</action>
  <decisions>
    <decision type="language" value="Java" confidence="high"/>
    <decision type="pattern" value="business-rule" count="5"/>
    <decision type="sql" value="found" count="3"/>
  </decisions>
  <reasoning>Identified Order class with discount calculation logic.
  Found embedded SQL in getOrderHistory method.</reasoning>
  <duration-ms>450</duration-ms>
</log-entry>
```

---

## Summary

| Research Item | Decision | Key Rationale |
|---------------|----------|---------------|
| R1: XML Schema | Self-describing with embedded references | LLM-friendly, traceable |
| R2: Checkpoints | Per-file XML state | Precise resume, no dependencies |
| R3: Confidence | High/Medium/Low heuristics | Prioritize review, integrate with clarify |
| R4: UI Layout | ASCII art with annotations | Universal compatibility |
| R5: Workflow Tracing | Static pattern matching | LLM-first, safe for legacy |
| R6: User Stories | Template with traceability | Consistent, testable |
| R7: Multi-File XML | Category split with index | Scalable, navigable |
| R8: Analysis Logs | Append-only XML | Audit trail, debugging |

**Status**: All research items resolved. Ready for Phase 1 design.
