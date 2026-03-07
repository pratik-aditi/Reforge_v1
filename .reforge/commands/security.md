# /reforge.security

> OWASP Top 10 security scan with CWE identifiers

## Command Syntax

```
/reforge.security [--owasp-version <2021|2017>] [--severity <critical|high|medium|low>] [--format html|xml] [--json]
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `--owasp-version` | No | OWASP Top 10 version to use: `2021` (default) or `2017` |
| `--severity` | No | Minimum severity threshold to report: `critical`, `high`, `medium`, `low` (default: all) |
| `--format` | No | Output format: `html` or `xml` (default: `xml`) |
| `--json` | No | Output summary as JSON to stdout |

## Overview

This command performs an LLM-driven security audit by scanning source code for vulnerability patterns mapped to the OWASP Top 10 and CWE identifiers. It examines:

- **Injection patterns**: SQL injection, XSS, command injection
- **Authentication weaknesses**: Hardcoded credentials, weak session management
- **Cryptographic issues**: Weak algorithms, improper key management
- **Data exposure**: Sensitive data in logs, unencrypted storage
- **Access control**: Missing authorization checks, IDOR vulnerabilities
- **Security misconfiguration**: Debug modes, default credentials, permissive CORS

Output is written to `extractions/security-audit.xml` following the [Security Audit Schema](../schemas/security-audit.md).

## Prerequisites

- Analysis must be completed (`/reforge.analyze`)
- `$ANALYSIS_DIR/analysis.xml` must exist

Optional but recommended:
- Database extraction (`/reforge.extract database`) -- for SQL injection analysis
- Architecture extraction (`/reforge.extract architecture`) -- for security boundary analysis

---

## Workflow

### Step 0: Check Prerequisites

Run the prerequisites script to validate state and resolve paths:

```bash
reforge-scripts check-prerequisites --json --require-analysis
```

This returns JSON with resolved variables:
```json
{"PROJECT_NAME":"...","REPO_ROOT":"...","PROJECT_OUTPUT_DIR":"...","CONFIG":"...","ANALYSIS_STATUS":"completed","AVAILABLE_EXTRACTIONS":[...],"CHECKPOINT":null,"CLARIFICATIONS_DIR":"..."}
```

Use `$PROJECT_OUTPUT_DIR` for all output paths in subsequent steps.

Assign subdirectory variables:
```
$ANALYSIS_DIR = $PROJECT_OUTPUT_DIR/analysis
$EXTRACTIONS_DIR = $PROJECT_OUTPUT_DIR/extractions
```

### Step 0.5: Load Project Context

If `.reforge/memory/project-context.md` exists, read it now. Use its contents as
supplemental guidance throughout this command's execution:
- **Technology Stack**: Informs framework-specific vulnerability patterns
- **Domain Knowledge**: Identifies sensitive data types and compliance requirements
- **Analysis Guidelines**: Directs focus and exclusions beyond config.json
- **Custom Rules**: Additional rules to follow alongside the constitution

### Step 0.7: Check/Update Project Plan

If `.reforge/memory/project-plan.md` exists, read it now.

**On command start:**
- Parse the plan file to count total items and completed items
- Display: "📋 Project Plan: X/Y items complete (Z%)"
- Derive the plan tag: `<!-- reforge:security -->`
- Identify the item with that tag and display its status

**On command completion (success only):**
- Locate the plan item by searching for `<!-- reforge:security -->`
- If found and unchecked (`- [ ]`): change to `- [x]` and append ` *(completed: YYYY-MM-DD)*`
- If found and already checked (`- [x]`): leave unchanged (idempotent)
- If tag not found: emit warning -- "No plan item found for security. Run /reforge.plan to add it."
- If file write fails: emit warning -- "Could not update project plan." Continue without failing.
- Update the `**Last Updated**` metadata line to today's date

If `.reforge/memory/project-plan.md` does not exist, skip this step silently.
The project plan is optional -- its absence MUST NOT affect command behavior.

### Step 1: Load Analysis and Available Extractions

Read `$ANALYSIS_DIR/analysis.xml` to get the file inventory and technology stack.

Optionally load:
- `$EXTRACTIONS_DIR/database.xml` -- to cross-reference SQL patterns
- `$EXTRACTIONS_DIR/architecture.xml` -- to understand security boundaries
- `$EXTRACTIONS_DIR/non-functional.xml` -- to check for existing security findings (SEC prefix)

### Step 2: Scan for Injection Vulnerabilities (A03)

For each source file, use Grep and Read to scan for:

#### SQL Injection (CWE-89)
```
Patterns:
  - String concatenation in SQL: "SELECT ... " + variable
  - String formatting in SQL: String.format("SELECT ... %s", ...)
  - Dynamic query construction without parameterization
  - Raw SQL execution with user input
```

#### Cross-Site Scripting (CWE-79)
```
Patterns:
  - Direct output of user input to HTML: response.write(userInput)
  - Template interpolation without escaping: ${userInput}
  - innerHTML assignment with user data
  - Disabled auto-escaping in templates
```

#### OS Command Injection (CWE-78)
```
Patterns:
  - Runtime.exec() with user input
  - ProcessBuilder with unsanitized arguments
  - System() calls with concatenated strings
  - Shell execution functions with user data
```

### Step 3: Scan for Authentication/Authorization Issues (A01, A07)

#### Broken Access Control (CWE-862, CWE-639)
```
Patterns:
  - Missing authorization checks on endpoints
  - Direct object references without ownership validation
  - Privilege escalation via role manipulation
  - Missing CSRF tokens on state-changing operations
```

#### Authentication Failures (CWE-287, CWE-798)
```
Patterns:
  - Hardcoded passwords/API keys/tokens
  - Weak password validation (no complexity requirements)
  - Missing rate limiting on login endpoints
  - Session tokens in URLs
  - Credentials in source code or config files
```

### Step 4: Scan for Cryptographic Issues (A02)

```
Patterns:
  - Weak hash algorithms: MD5, SHA1 for passwords
  - Hardcoded encryption keys
  - ECB mode usage
  - Missing TLS/SSL enforcement
  - Custom cryptography implementations
  - Predictable random number generators (java.util.Random, Math.random)
```

CWE mappings: CWE-327 (Broken Crypto), CWE-328 (Weak Hash), CWE-330 (Insufficient Randomness)

### Step 5: Scan for Data Exposure (A01, A04)

```
Patterns:
  - Sensitive data in log statements (passwords, tokens, SSN, credit cards)
  - PII in error messages returned to users
  - Unencrypted sensitive data storage
  - Sensitive data in URL query parameters
  - Missing secure/httpOnly flags on cookies
  - Verbose error messages exposing stack traces
```

CWE mappings: CWE-200 (Info Exposure), CWE-532 (Log Insertion), CWE-614 (Missing Secure Flag)

### Step 6: Scan for Security Misconfiguration (A05)

```
Patterns:
  - Debug mode enabled in production config
  - Default credentials in configuration
  - Permissive CORS policies (Access-Control-Allow-Origin: *)
  - Disabled security headers
  - Verbose error pages enabled
  - Unnecessary services/features enabled
```

### Step 7: Scan for Additional OWASP Categories

#### Insecure Deserialization (A08, CWE-502)
```
  - ObjectInputStream.readObject() with untrusted data
  - JSON/XML deserialization without type validation
  - Pickle.loads() with user input (Python)
```

#### Vulnerable Components (A06, CWE-1104)
```
  - Outdated framework versions in build files
  - Known vulnerable library versions
  - Unmaintained dependencies
```

#### Logging Failures (A09, CWE-778)
```
  - Missing audit logging for security events
  - No logging on authentication failures
  - Missing tamper detection for logs
```

### Step 8: Map Findings to OWASP/CWE

For each identified vulnerability:

1. Assign CWE identifier based on the weakness type
2. Map to OWASP Top 10 category (2021 or 2017 based on `--owasp-version`)
3. Assign severity: `critical`, `high`, `medium`, or `low`
4. Assign confidence: `high`, `medium`, or `low`
5. Generate remediation guidance

Severity guidelines:
| Severity | Criteria |
|----------|----------|
| `critical` | Directly exploitable, high impact (RCE, full DB access, auth bypass) |
| `high` | Exploitable with moderate effort, significant impact |
| `medium` | Requires specific conditions, moderate impact |
| `low` | Informational or requires significant effort to exploit |

If `--severity` is specified, filter out findings below the threshold.

### Step 9: Generate Security Audit

Write `$EXTRACTIONS_DIR/security-audit.xml` following the [Security Audit Schema](../schemas/security-audit.md):

- Assign IDs using the `VULN-{CATEGORY}-{SEQUENCE}` pattern
- Include summary with severity and OWASP category breakdowns
- Include evidence with the specific code pattern that triggered each finding
- Include source references with file, line numbers, and code snippets
- Include remediation guidance for each finding

If `--format html` is specified, also generate an HTML version following the HTML documentation standard.

### Step 10: Report Results

```
Security Audit Complete!

Output: $EXTRACTIONS_DIR/security-audit.xml
OWASP Version: 2021

Findings by Severity:
  Critical:  2
  High:      5
  Medium:   12
  Low:       8
  Total:    27

Top OWASP Categories:
  A03 Injection:           4 findings
  A01 Broken Access Ctrl:  3 findings
  A07 Auth Failures:       2 findings

Critical Findings:
  1. VULN-INJ-001: SQL injection in ProductRepository.java:45
  2. VULN-INJ-002: Command injection in FileProcessor.java:112

Confidence levels:
  High:   18 (67%)
  Medium:  7 (26%)
  Low:     2 (7%)

Run /reforge.generate to create security documentation.
```

---

## Error Handling

| Error | Response |
|-------|----------|
| `analysis.xml` not found | Report error, suggest `/reforge.analyze` |
| File read error during scanning | Log warning, skip file, continue with remaining files |
| Unknown OWASP version | Report error: "Unsupported OWASP version. Use `2021` or `2017`." |
| No vulnerabilities found | Report: "No security vulnerabilities detected. Consider manual review for logic-level vulnerabilities." |
| Database extraction missing | Warn: "Database extraction not found. SQL injection analysis may be incomplete." Continue. |

---

## Examples

### Full security audit

```
/reforge.security
```

### Critical and high findings only

```
/reforge.security --severity high
```

### Using OWASP 2017 classification

```
/reforge.security --owasp-version 2017
```

### HTML report

```
/reforge.security --format html
```
