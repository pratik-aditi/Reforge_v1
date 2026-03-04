# Data Model: 014 — Extraction Type Expansion

**Feature**: 014-extraction-type-expansion
**Created**: 2026-03-04

## New Extraction Types

### Call Sites (`call-sites.xml`)

| Element | Parent | Attributes | Description |
|---------|--------|------------|-------------|
| `<call-sites>` | root | CommonRootAttributes | Root element |
| `<call>` | call-sites | id, confidence | Single call relationship |
| `<caller>` | call | method, class, module | Calling side |
| `<caller-source>` | caller | file, line-start, line-end | SourceReferenceType |
| `<callee>` | call | method, class, module | Called side |
| `<callee-source>` | callee | file, line-start, line-end | SourceReferenceType |
| `<call-type>` | call | — | direct, virtual, interface, event, callback, reflection |
| `<parameters>` | call | — | Optional parameter list |
| `<return-type>` | call | — | Optional return type |

### Dependencies (`dependencies.xml`)

| Element | Parent | Attributes | Description |
|---------|--------|------------|-------------|
| `<dependencies>` | root | CommonRootAttributes | Root element |
| `<dep-ref>` | dependencies | id, dependency-type, confidence | Single dependency |
| `<from-module>` | dep-ref | — | Source module |
| `<to-module>` | dep-ref | — | Target module |
| `<coupling>` | dep-ref | — | tight, loose, runtime |
| `<direction>` | dep-ref | — | unidirectional, bidirectional, circular |
| `<source>` | dep-ref | file, line-start, line-end | SourceReferenceType |

### Functional Requirements (`functional-requirements.xml`)

| Element | Parent | Attributes | Description |
|---------|--------|------------|-------------|
| `<functional-requirements>` | root | CommonRootAttributes | Root element |
| `<requirement>` | functional-requirements | id, category, priority, confidence | Single requirement |
| `<title>` | requirement | — | Short title |
| `<description>` | requirement | — | Full description |
| `<acceptance-criteria>` | requirement | — | Container for criteria |
| `<criterion>` | acceptance-criteria | — | Single acceptance criterion |
| `<source>` | requirement | file, line-start, line-end | SourceReferenceType |
| `<related-rules>` | requirement | — | Cross-refs to business rules |
| `<related-workflows>` | requirement | — | Cross-refs to workflows |

### Non-Functional Requirements (`non-functional-requirements.xml`)

| Element | Parent | Attributes | Description |
|---------|--------|------------|-------------|
| `<non-functional-requirements>` | root | CommonRootAttributes | Root element |
| `<requirements>` | root | count | NFR container |
| `<requirement>` | requirements | id, category, confidence | Single NFR |
| `<metric>` | requirement | name, threshold, unit | Measurable metric |
| `<findings>` | root | count | Security findings container |
| `<finding>` | findings | id, category, severity, confidence | Single finding |
| `<cwe-id>` | finding | — | CWE identifier |
| `<affected-component>` | finding | — | Component affected |
| `<remediation>` | finding | — | Fix recommendation |

### Architecture (`architecture.xml`)

| Element | Parent | Attributes | Description |
|---------|--------|------------|-------------|
| `<architecture>` | root | CommonRootAttributes | Root element |
| `<components>` | root | count | Component container |
| `<component>` | components | id, name, layer, confidence | Architectural component |
| `<technology>` | component | — | Technology used |
| `<responsibilities>` | component | — | Responsibility list |
| `<integrations>` | root | count | Integration container |
| `<integration>` | integrations | id, name, protocol, confidence | Integration point |
| `<endpoint>` | integration | — | Connection endpoint |
| `<direction>` | integration | — | inbound, outbound, bidirectional |
| `<patterns>` | root | count | Pattern container |
| `<pattern>` | patterns | id, name, pattern-type, confidence | Design pattern |
| `<implementation-notes>` | pattern | — | How it's implemented |
| `<affected-components>` | pattern | — | Components using pattern |

### Issues (`issues.xml`)

| Element | Parent | Attributes | Description |
|---------|--------|------------|-------------|
| `<issues>` | root | CommonRootAttributes | Root element |
| `<bugs>` | root | count | Bug container |
| `<bug>` | bugs | id, category, severity, confidence | Code defect |
| `<detection-method>` | bug | — | How it was found |
| `<impact>` | bug | — | Runtime impact |
| `<issues-list>` | root | count | Tech debt container |
| `<issue>` | issues-list | id, category, severity, confidence | Tech debt item |
| `<issue-type>` | issue | — | Classification |
| `<effort-estimate>` | issue | — | low, medium, high |
| `<recommendation>` | issue | — | Fix recommendation |

## ID Prefix Registry Additions

| Prefix | Type | Item |
|--------|------|------|
| CALL | call-sites | Call relationship |
| DEP | dependencies | Dependency reference |
| FR | functional-requirements | Functional requirement |
| NFR | non-functional | Non-functional requirement |
| SEC | non-functional | Security finding |
| ARCH | architecture | Architectural component |
| INT | architecture | Integration point |
| DP | architecture | Design pattern |
| BUG | issues | Bug/defect |
| ISS | issues | Tech debt/operational issue |
| GLOSS | glossary | Glossary entry |
