# Phase 1: Pattern Extraction

> Scan source files for acronyms and abbreviations using pattern matching, apply exclusion filtering, and produce an initial glossary draft at v1.0.0.

## Input

| Input | Source | Description |
|-------|--------|-------------|
| `analysis.xml` | `$ANALYSIS_DIR/analysis.xml` | File inventory from `/reforge.analyze` |
| Project context | `.reforge/memory/project-context.md` | Optional domain knowledge and tech stack guidance |
| Variables | Parent orchestrator | `$PROJECT_NAME`, `$REPO_ROOT`, `$PROJECT_OUTPUT_DIR`, `$GLOSSARY_XML`, `$TEAM_SIZE` |

## Output

| Output | Location | Description |
|--------|----------|-------------|
| Glossary XML | `$GLOSSARY_XML` (`$EXTRACTIONS_DIR/acronym-glossary.xml`) | Initial glossary draft at version `v1.0.0` |

---

## Workflow

### Step 1: Load File Inventory

Read `$ANALYSIS_DIR/analysis.xml` to obtain the complete list of source files.

For each `<file>` element, collect:
- `path` (relative file path from project root)
- `language` (detected programming language)
- `file-type` (source, config, template, data)
- `analysis-status` (skip files with status `skipped` or `error`)

**Include** files with `file-type` of: `source`, `config`, `template`.
**Exclude** files with `file-type` of: `binary`, `unknown`, or `analysis-status="skipped"`.

Record the total file count for progress reporting.

### Step 2: Partition Files into Processing Zones

Divide the file inventory into processing zones. Each zone is a batch of files that the agent processes sequentially.

**Partitioning strategy:**
1. Group files by top-level directory (e.g., `src/`, `lib/`, `config/`, `test/`)
2. If any group exceeds 50 files, subdivide by second-level directory
3. If fewer than 3 groups result, use a flat partition of approximately equal size

Record the zone assignments:
```
Zone 1: src/controllers/ (23 files)
Zone 2: src/services/ (18 files)
Zone 3: src/models/ (15 files)
Zone 4: config/ (8 files)
Zone 5: test/ (12 files)
```

Report:
> "Phase 1: Partitioned {total-files} files into {zone-count} zones."

### Step 3: Scan Each Zone for Acronym Patterns

Process each zone sequentially. For every file in the zone, read the file content using the Read tool and scan for the following pattern types.

**CRITICAL**: The agent MUST read each file using the Read tool before scanning it. Do NOT rely on analysis.xml metadata or memory from previous sessions. If a file is too large to read in one pass, read it in sections.

#### Pattern Type 1: Uppercase Identifiers (2+ characters)

Scan for standalone uppercase sequences of 2 or more letters that appear as identifiers:
- Variable names: `TMDS_CONFIG`, `SLA_THRESHOLD`
- Constant names: `MAX_RETRY_COUNT` where `MAX` is a candidate
- Class/type prefixes: `TMDSController`, `RUMOService`

Extract the uppercase portion as the candidate term. For compound identifiers like `TMDS_CONFIG`, extract `TMDS` as the candidate (the prefix before the first underscore, if it is all-uppercase and 2+ characters).

#### Pattern Type 2: PascalCase Prefixes

Scan for PascalCase identifiers where the leading segment is an all-uppercase acronym:
- `TMDSManager` yields candidate `TMDS`
- `OLAPQueryBuilder` yields candidate `OLAP`
- `SLAMonitor` yields candidate `SLA`

The candidate is the uppercase prefix before the first lowercase letter transition. Only extract prefixes of 2+ characters.

#### Pattern Type 3: Code Comments with Parenthetical Expansions

Scan for comments that define acronyms using parenthetical patterns:
- `// TMDS (Train Management Dispatch System)`
- `/* SLA - Service Level Agreement */`
- `# RUMO: Route Management Operations`

These provide both the term AND its expansion. Record both, and assign higher initial confidence (0.7) compared to patterns without expansions.

#### Pattern Type 4: Doc Comments

Scan for documentation comment blocks that define or reference acronyms:
- Javadoc: `/** @acronym TMDS Train Management Dispatch System */`
- JSDoc: `/** TMDS - Train Management Dispatch System */`
- XML doc: `/// <summary>TMDS = Train Management Dispatch System</summary>`
- Docstrings: `"""TMDS stands for Train Management Dispatch System"""`

These provide high-quality evidence. Record the term, expansion (if present), and assign confidence 0.7 when an expansion is found.

#### Pattern Type 5: Enum Definitions

Scan for enum declarations where member names contain uppercase acronyms:
- `enum TMDSStatus { Active, Inactive }` yields candidate `TMDS`
- `enum SLALevel { Gold, Silver, Bronze }` yields candidate `SLA`
- Enum members that are all-uppercase: `PENDING_REVIEW`, `SLA_BREACH`

Record the enum name and file location as evidence with `evidence-type="enum-definition"`.

#### Pattern Type 6: Region Labels

Scan for region markers or section labels containing acronyms:
- `#region TMDS Configuration`
- `// --- RUMO Processing ---`
- `// ====== SLA Monitoring ======`

Record with `evidence-type="region-label"`.

#### Pattern Type 7: String Literals

Scan for string literals that contain or define acronyms:
- `"TMDS_SERVICE_NAME"`
- `"Error: SLA threshold exceeded"`
- `"RUMO route calculation failed"`

Record with `evidence-type="string-literal"`. Assign lower initial confidence (0.4) as string literals are less reliable indicators.

#### Pattern Type 8: Namespace Declarations

Scan for namespace or package declarations containing acronyms:
- `namespace TMDS.Core`
- `package com.company.tmds.dispatcher`
- `module RUMO::RouteEngine`

Record with `evidence-type="namespace"`. The namespace itself is strong evidence that the acronym is a real project term.

#### Evidence Recording

For each discovered candidate, record:
- **term**: The acronym exactly as found (preserving case)
- **expansion**: The full expansion if discovered in context (empty string if unknown)
- **confidence**: Initial confidence score (see Confidence Assignment below)
- **category**: Initial category guess (see Category Assignment below)
- **evidence**: Source reference with file, line-start, line-end, evidence-type, snippet, and `phase="1"`

#### Confidence Assignment (Initial)

| Condition | Confidence |
|-----------|------------|
| Expansion found in comment or doc comment | 0.7 |
| Term appears in namespace or package declaration | 0.6 |
| Term appears in enum definition | 0.5 |
| Term appears as uppercase identifier without expansion | 0.4 |
| Term appears only in string literals | 0.3 |

These are initial scores. Later phases will adjust confidence based on verification results.

#### Category Assignment (Initial)

Assign a preliminary category based on context clues:

| Context Signal | Category |
|----------------|----------|
| Appears in domain model, entity, or business logic files | `domain` |
| Appears in infrastructure, config, framework, or utility files | `technical` |
| Appears in org charts, team references, department codes | `organizational` |
| Appears in workflow, state machine, or process definitions | `process` |
| Appears in data model, schema, ETL, or reporting contexts | `data` |
| No clear signal | `domain` (default) |

### Step 4: Apply Exclusion List

After scanning all zones, filter the collected candidates against the exclusion list below. Remove any candidate whose term (case-insensitive) matches an entry in the exclusion list.

**Important**: The exclusion list is intentionally broad. It is better to exclude a borderline term and miss it than to pollute the glossary with common programming vocabulary. If a term is genuinely a project-specific acronym that happens to collide with a common term (e.g., a project named "API"), it will be absent from the glossary — this is acceptable.

#### Exclusion List

##### Programming Language Keywords and Types

| Term | Reason |
|------|--------|
| `IF` | Language keyword |
| `OR` | Language keyword |
| `AND` | Language keyword |
| `NOT` | Language keyword |
| `FOR` | Language keyword |
| `DO` | Language keyword |
| `INT` | Primitive type |
| `BOOL` | Primitive type |
| `CHAR` | Primitive type |
| `LONG` | Primitive type |
| `VOID` | Language keyword |
| `NULL` | Language keyword |
| `TRUE` | Language keyword |
| `FALSE` | Language keyword |
| `ENUM` | Language keyword |
| `CASE` | Language keyword |
| `ELSE` | Language keyword |
| `THEN` | Language keyword |
| `GOTO` | Language keyword |
| `THIS` | Language keyword |
| `SELF` | Language keyword |
| `BYTE` | Primitive type |
| `VAR` | Language keyword |
| `LET` | Language keyword |
| `SET` | Language keyword |
| `GET` | Language keyword |
| `NEW` | Language keyword |
| `TRY` | Language keyword |
| `END` | Language keyword |
| `DIM` | Language keyword (VB) |
| `SUB` | Language keyword (VB) |
| `REM` | Language keyword (VB) |

##### Standard Data Formats and Protocols

| Term | Reason |
|------|--------|
| `SQL` | Standard query language |
| `XML` | Standard data format |
| `JSON` | Standard data format |
| `HTML` | Standard markup language |
| `CSS` | Standard style language |
| `HTTP` | Standard protocol |
| `HTTPS` | Standard protocol |
| `FTP` | Standard protocol |
| `SFTP` | Standard protocol |
| `SSH` | Standard protocol |
| `TCP` | Standard protocol |
| `UDP` | Standard protocol |
| `IP` | Standard protocol |
| `DNS` | Standard protocol |
| `SSL` | Standard protocol |
| `TLS` | Standard protocol |
| `SMTP` | Standard protocol |
| `IMAP` | Standard protocol |
| `POP` | Standard protocol |
| `LDAP` | Standard protocol |
| `SOAP` | Standard protocol |
| `REST` | Architectural style |
| `GRPC` | Standard protocol |
| `AMQP` | Standard protocol |
| `MQTT` | Standard protocol |
| `YAML` | Standard data format |
| `CSV` | Standard data format |
| `TSV` | Standard data format |
| `PDF` | Standard file format |
| `PNG` | Standard image format |
| `JPG` | Standard image format |
| `JPEG` | Standard image format |
| `GIF` | Standard image format |
| `SVG` | Standard image format |
| `MP3` | Standard audio format |
| `MP4` | Standard video format |
| `UTF` | Character encoding |
| `ASCII` | Character encoding |
| `URI` | Standard identifier |
| `URL` | Standard identifier |
| `URN` | Standard identifier |
| `UUID` | Standard identifier |
| `GUID` | Standard identifier |
| `RFC` | Standard specification |
| `ISO` | Standard specification |
| `IEEE` | Standards organization |
| `ANSI` | Standards organization |
| `MIME` | Standard type system |
| `BASE64` | Standard encoding |

##### Generic Programming and Software Terms

| Term | Reason |
|------|--------|
| `API` | Generic software term |
| `SDK` | Generic software term |
| `CLI` | Generic software term |
| `GUI` | Generic software term |
| `IDE` | Generic software term |
| `OOP` | Generic paradigm |
| `MVC` | Generic pattern |
| `MVVM` | Generic pattern |
| `MVP` | Generic pattern |
| `DDD` | Generic pattern |
| `TDD` | Generic practice |
| `BDD` | Generic practice |
| `CI` | Generic practice |
| `CD` | Generic practice |
| `CRUD` | Generic pattern |
| `FIFO` | Generic pattern |
| `LIFO` | Generic pattern |
| `ORM` | Generic pattern |
| `DAO` | Generic pattern |
| `DTO` | Generic pattern |
| `POJO` | Generic term (Java) |
| `POCO` | Generic term (.NET) |
| `ENUM` | Generic type |
| `REGEX` | Generic tool |
| `CRON` | Generic tool |
| `EOF` | Generic marker |
| `EOL` | Generic marker |
| `ACL` | Generic security term |
| `RBAC` | Generic security pattern |
| `JWT` | Generic security token |
| `OAuth` | Generic auth protocol |
| `SSO` | Generic auth pattern |
| `MFA` | Generic auth term |
| `CORS` | Generic web term |
| `XSS` | Generic security term |
| `CSRF` | Generic security term |
| `DOS` | Generic security term |
| `DDOS` | Generic security term |
| `AES` | Generic encryption |
| `RSA` | Generic encryption |
| `SHA` | Generic hash |
| `MD5` | Generic hash |
| `HMAC` | Generic hash |
| `PKI` | Generic security |
| `CA` | Generic security (certificate authority) |

##### Database and Data Terms

| Term | Reason |
|------|--------|
| `DDL` | Standard database term |
| `DML` | Standard database term |
| `DCL` | Standard database term |
| `ACID` | Standard database property |
| `BLOB` | Standard database type |
| `CLOB` | Standard database type |
| `OLAP` | Standard analytics term |
| `OLTP` | Standard database term |
| `ETL` | Standard data term |
| `ELT` | Standard data term |
| `CDC` | Standard data term |

##### Infrastructure and DevOps Terms

| Term | Reason |
|------|--------|
| `AWS` | Cloud provider |
| `GCP` | Cloud provider |
| `VM` | Generic infrastructure |
| `CPU` | Generic hardware |
| `GPU` | Generic hardware |
| `RAM` | Generic hardware |
| `SSD` | Generic hardware |
| `HDD` | Generic hardware |
| `NAS` | Generic infrastructure |
| `SAN` | Generic infrastructure |
| `VPN` | Generic infrastructure |
| `CDN` | Generic infrastructure |
| `LB` | Generic infrastructure (load balancer) |
| `DNS` | Generic infrastructure |
| `CIDR` | Generic networking |
| `VLAN` | Generic networking |
| `NAT` | Generic networking |
| `DHCP` | Generic networking |

##### Framework and Library Terms

| Term | Reason |
|------|--------|
| `DOM` | Web standard |
| `JSX` | Framework syntax (React) |
| `TSX` | Framework syntax (React/TypeScript) |
| `NPM` | Package manager |
| `JVM` | Runtime platform |
| `CLR` | Runtime platform (.NET) |
| `GC` | Generic runtime term (garbage collection) |
| `JIT` | Generic runtime term |
| `AOT` | Generic runtime term |
| `DI` | Generic pattern (dependency injection) |
| `IOC` | Generic pattern (inversion of control) |
| `AOP` | Generic pattern (aspect-oriented programming) |
| `JPA` | Framework standard (Java) |
| `JDBC` | Framework standard (Java) |
| `JNDI` | Framework standard (Java) |
| `EJB` | Framework standard (Java) |
| `JSP` | Framework standard (Java) |
| `ASPX` | Framework standard (.NET) |
| `LINQ` | Framework feature (.NET) |
| `XAML` | Framework syntax (.NET) |
| `WPF` | Framework (.NET) |
| `WCF` | Framework (.NET) |

##### Generic Abbreviations

| Term | Reason |
|------|--------|
| `ID` | Generic abbreviation |
| `DB` | Generic abbreviation |
| `UI` | Generic abbreviation |
| `UX` | Generic abbreviation |
| `QA` | Generic abbreviation |
| `PM` | Generic abbreviation |
| `PR` | Generic abbreviation |
| `CR` | Generic abbreviation |
| `OK` | Generic abbreviation |
| `IO` | Generic abbreviation |
| `OS` | Generic abbreviation |
| `IT` | Generic abbreviation |
| `HR` | Generic abbreviation |
| `AM` | Generic abbreviation |
| `PM` | Generic abbreviation |
| `VS` | Generic abbreviation |
| `NA` | Generic abbreviation |
| `NO` | Generic abbreviation |
| `TO` | Generic abbreviation |
| `BY` | Generic abbreviation |
| `AS` | Generic abbreviation |
| `AT` | Generic abbreviation |
| `IN` | Generic abbreviation |
| `ON` | Generic abbreviation |
| `UP` | Generic abbreviation |
| `MAX` | Generic abbreviation |
| `MIN` | Generic abbreviation |
| `AVG` | Generic abbreviation |
| `SUM` | Generic abbreviation |
| `CNT` | Generic abbreviation |
| `IDX` | Generic abbreviation |
| `TMP` | Generic abbreviation |
| `SRC` | Generic abbreviation |
| `DST` | Generic abbreviation |
| `FMT` | Generic abbreviation |
| `MSG` | Generic abbreviation |
| `ERR` | Generic abbreviation |
| `LOG` | Generic abbreviation |
| `CFG` | Generic abbreviation |
| `STR` | Generic abbreviation |
| `NUM` | Generic abbreviation |
| `LEN` | Generic abbreviation |
| `POS` | Generic abbreviation |
| `REF` | Generic abbreviation |
| `PTR` | Generic abbreviation |
| `OBJ` | Generic abbreviation |
| `ARG` | Generic abbreviation |
| `VAL` | Generic abbreviation |
| `RET` | Generic abbreviation |
| `ACK` | Generic abbreviation |
| `NAK` | Generic abbreviation |
| `SYN` | Generic abbreviation |
| `FIN` | Generic abbreviation |
| `NUL` | Generic abbreviation |
| `SOH` | Generic control character |
| `STX` | Generic control character |
| `ETX` | Generic control character |
| `EOT` | Generic control character |
| `ENQ` | Generic control character |
| `BEL` | Generic control character |
| `DEL` | Generic abbreviation |
| `ESC` | Generic abbreviation |
| `TAB` | Generic abbreviation |
| `TODO` | Generic annotation |
| `FIXME` | Generic annotation |
| `HACK` | Generic annotation |
| `XXX` | Generic annotation |
| `NOTE` | Generic annotation |
| `TEMP` | Generic abbreviation |
| `IMPL` | Generic abbreviation |
| `INIT` | Generic abbreviation |
| `UTIL` | Generic abbreviation |
| `MISC` | Generic abbreviation |
| `INFO` | Generic abbreviation |
| `WARN` | Generic abbreviation |
| `DEBUG` | Generic abbreviation |
| `ERROR` | Generic abbreviation |
| `FATAL` | Generic abbreviation |
| `TRACE` | Generic abbreviation |

### Step 5: Create Glossary Entries

For each surviving candidate (not excluded in Step 4), create a glossary entry:

1. **Assign sequential ID**: `GLOSS-001`, `GLOSS-002`, etc., ordered by first discovery.

2. **Set entry attributes**:
   - `id`: `GLOSS-{SEQ}` (zero-padded to 3 digits)
   - `term`: The acronym exactly as found (uppercase form)
   - `confidence`: Initial confidence from Step 3, capped at 0.5 for entries without an expansion (UNVERIFIED status requires confidence <= 0.5)
   - `category`: Initial category from Step 3
   - `verification-status`: `UNVERIFIED` (all Phase 1 entries start as UNVERIFIED)
   - `version-added`: `v1.0.0`

3. **Set expansion**:
   - If an expansion was found (Pattern Types 3 or 4), use it
   - If no expansion was found, set `<expansion>` to an empty string

4. **Attach evidence chain**:
   - Include all `<source>` elements collected for this term across all zones
   - Each `<source>` MUST have: `file`, `line-start`, `line-end`, `evidence-type`, `phase="1"`
   - Include `<snippet>` with the verbatim code at the evidence location

**Confidence cap rule**: If `verification-status` is `UNVERIFIED` and no expansion was found, confidence MUST NOT exceed 0.5. If the initial confidence from Step 3 exceeds 0.5 but no expansion exists, cap it at 0.5.

### Step 6: Deduplicate Entries

Multiple zones may discover the same acronym. Deduplicate by term (case-sensitive):

1. **Group** all entries by `term`
2. For each group with multiple entries:
   - **Keep** the entry with the highest `confidence` score
   - **Merge** all `<source>` evidence from duplicate entries into the surviving entry's `<evidence>` block
   - **Prefer** the expansion from the highest-confidence entry; if tied, prefer the entry whose expansion came from a doc-comment or code-comment over other evidence types
   - **Re-sequence** IDs after deduplication to maintain a contiguous `GLOSS-{SEQ}` series

3. After deduplication, verify:
   - Every `term` appears exactly once
   - Every entry has at least one `<source>` element
   - IDs are sequential with no gaps

### Step 7: Output Glossary XML

Write the deduplicated glossary to `$GLOSSARY_XML` at version `v1.0.0`.

Compute metadata tallies from the final entry list:
- `total-count`: Number of entries
- `confidence-distribution`: Count entries by mapped confidence level (high: 0.8-1.0, medium: 0.5-0.79, low: 0.0-0.49)
- `extraction-timestamp`: Current ISO-8601 timestamp

```xml
<?xml version="1.0" encoding="UTF-8"?>
<acronym-glossary xmlns="http://reforge.dev/schema/extraction"
                  project-id="{$PROJECT_NAME}" version="v1.0.0"
                  schema-version="1.0.0"
                  generated="{ISO-8601-timestamp}">

  <metadata>
    <total-count>{entry-count}</total-count>
    <confidence-distribution>
      <high>{high-count}</high>
      <medium>{medium-count}</medium>
      <low>{low-count}</low>
    </confidence-distribution>
    <extraction-timestamp>{ISO-8601-timestamp}</extraction-timestamp>
  </metadata>

  <entry id="GLOSS-001" term="TMDS" confidence="0.7" category="domain"
         verification-status="UNVERIFIED" version-added="v1.0.0">
    <expansion>Train Management Dispatch System</expansion>
    <evidence>
      <source file="src/tmds/core/Dispatcher.java" line-start="12" line-end="12"
              evidence-type="doc-comment" phase="1">
        <snippet>/** TMDS - Train Management Dispatch System */</snippet>
      </source>
      <source file="src/tmds/config/AppConfig.java" line-start="3" line-end="3"
              evidence-type="namespace" phase="1">
        <snippet>package com.company.tmds.config;</snippet>
      </source>
    </evidence>
  </entry>

  <entry id="GLOSS-002" term="RUMO" confidence="0.4" category="domain"
         verification-status="UNVERIFIED" version-added="v1.0.0">
    <expansion></expansion>
    <evidence>
      <source file="src/rumo/RouteEngine.java" line-start="1" line-end="1"
              evidence-type="namespace" phase="1">
        <snippet>package com.company.rumo;</snippet>
      </source>
    </evidence>
  </entry>

  <!-- More entries... -->

</acronym-glossary>
```

**Validation checks before writing:**
1. `total-count` equals the actual number of `<entry>` elements
2. `high + medium + low` in `<confidence-distribution>` equals `total-count`
3. Every `<entry>` has a unique `id` and unique `term`
4. Every `<entry>` has at least one `<source>` element in `<evidence>`
5. All `<source>` elements have `phase="1"`
6. No entry has `verification-status` other than `UNVERIFIED`
7. No entry with empty `<expansion>` has `confidence` > 0.5

### Step 8: Report Summary

Report Phase 1 results to the operator:

```
Phase 1: Pattern Extraction Complete

Output: {$GLOSSARY_XML}

Summary:
- Total entries: {count}
- With expansion: {count-with-expansion}
- Without expansion: {count-without-expansion}
- By category:
  - Domain: {n}
  - Technical: {n}
  - Organizational: {n}
  - Process: {n}
  - Data: {n}
- Confidence levels:
  - High (0.8-1.0): {n}
  - Medium (0.5-0.79): {n}
  - Low (0.0-0.49): {n}
- Zones processed: {zone-count}
- Files scanned: {file-count}
- Candidates before exclusion: {pre-exclusion-count}
- Candidates after exclusion: {post-exclusion-count}
- Duplicates merged: {duplicate-count}
- Elapsed time: {elapsed}
```

Return the entry count and version (`v1.0.0`) to the parent orchestrator for checkpoint recording.

---

## Optional Enhancement: Parallel Zone Processing

> **This section is OPTIONAL.** It applies only to agents that support team orchestration tools. Agents without these capabilities MUST use the sequential zone-by-zone workflow described above. Output is identical regardless of execution path.

When `$TEAM_SIZE` is greater than 1 AND the agent supports team orchestration:

1. **Distribute zones** across worker agents. Each worker receives:
   - Its assigned zone (list of file paths)
   - The exclusion list reference (embedded in this template)
   - Instructions to produce a partial entry list

2. **Each worker** executes Steps 3-4 for its assigned zone and returns:
   - A list of candidate entries with evidence chains
   - The count of files scanned and candidates found

3. **The lead agent** collects all partial results and:
   - Executes Step 5 (create entries) across all collected candidates
   - Executes Step 6 (deduplicate) across the merged set
   - Continues with Steps 7-8 as normal

When `$TEAM_SIZE` is 1: Skip all team orchestration. Process all zones sequentially as described in the main workflow.

---

## Reference: Evidence Types

| Evidence Type | Description | Typical Confidence |
|---------------|-------------|-------------------|
| `code-comment` | Inline comment (`//`, `/* */`, `#`) containing the term with parenthetical expansion | 0.7 |
| `doc-comment` | Documentation comment (Javadoc, JSDoc, XML doc, docstring) defining the term | 0.7 |
| `enum-definition` | Enum type or member name containing the term | 0.5 |
| `namespace` | Package, namespace, or module declaration containing the term | 0.6 |
| `string-literal` | String constant or literal containing the term | 0.3-0.4 |
| `variable-name` | Variable, constant, or field name containing the term as a prefix | 0.4 |
| `region-label` | Region marker or section label containing the term | 0.4 |

---

## Reference: Schema Compliance

Phase 1 output MUST conform to the [glossary schema](../schemas/glossary.md) and the [common extraction schema](../schemas/common-schema.md):

- Root element: `<acronym-glossary>`
- Namespace: `http://reforge.dev/schema/extraction`
- Required root attributes: `xmlns`, `project-id`, `version`, `schema-version`, `generated`
- Required `<metadata>` as first child with `<total-count>`, `<confidence-distribution>`, `<extraction-timestamp>`
- Entry ID pattern: `GLOSS-{SEQUENCE}` (e.g., `GLOSS-001`)
- All entries: `verification-status="UNVERIFIED"`, `version-added="v1.0.0"`
- Evidence: minimum one `<source>` per entry, all with `phase="1"`
- Confidence: 0.0-1.0 numeric; entries without expansion capped at 0.5
