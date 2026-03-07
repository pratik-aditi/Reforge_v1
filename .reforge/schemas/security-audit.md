# Security Audit Schema

> Defines the structure for security vulnerability findings (`security-audit.xml`)

## Overview

The security audit schema captures vulnerabilities identified by `/reforge.security` through OWASP Top 10 scanning with CWE identifiers. It records injection patterns, authentication weaknesses, cryptographic issues, and sensitive data exposure found in source code analysis.

## Common Elements

This schema extends the [Common Extraction Schema](./common-schema.md), which defines shared structural elements used across all extraction types:

- **Root attributes**: `project-id`, `version`, `schema-version`, `generated`, `xmlns`
- **Metadata container**: `<metadata>` with `<total-count>`, `<confidence-distribution>`, `<extraction-timestamp>`
- **Source references**: Canonical `<source>` format with `file`, `line-start`, `line-end` attributes
- **Confidence vocabulary**: `high`, `medium`, `low` enumeration
- **ID patterns**: `VULN-{CATEGORY}-{SEQUENCE}`

See `common-schema.md` for complete definitions. Elements defined there MUST NOT be redefined in this schema.

## Root Element

```xml
<security-audit xmlns="http://reforge.dev/schema/extraction"
                project-id="my-app" version="1.0.0"
                schema-version="1.0.0"
                generated="2024-01-15T10:30:00Z"
                owasp-version="2021">
  <metadata>...</metadata>
  <summary>...</summary>
  <vulnerabilities>...</vulnerabilities>
</security-audit>
```

### Attributes

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `xmlns` | URI | Yes | Must be `http://reforge.dev/schema/extraction` |
| `project-id` | string | Yes | Reference to analysis project |
| `version` | string | Yes | Extraction version (semver) |
| `schema-version` | string | Yes | Common schema version (initial: `1.0.0`) |
| `generated` | dateTime | Yes | Extraction timestamp (ISO-8601) |
| `owasp-version` | string | Yes | OWASP Top 10 version used (`2021` or `2017`) |

> Root attributes and `<metadata>` are defined by the [Common Extraction Schema](./common-schema.md). The `<metadata>` element is required as the first child of the root element. The metadata `<total-count>` equals the count of all vulnerability items.

## Elements

### `<summary>`

Aggregate statistics for the security audit.

```xml
<summary>
  <by-severity>
    <critical count="2"/>
    <high count="5"/>
    <medium count="12"/>
    <low count="8"/>
  </by-severity>
  <by-owasp-category>
    <category id="A01" name="Broken Access Control" count="3"/>
    <category id="A03" name="Injection" count="4"/>
    <category id="A07" name="Identification and Authentication Failures" count="2"/>
  </by-owasp-category>
  <files-scanned>145</files-scanned>
  <files-with-findings>18</files-with-findings>
</summary>
```

### `<vulnerabilities>`

Container for vulnerability items.

```xml
<vulnerabilities count="27">
  <vulnerability>...</vulnerability>
</vulnerabilities>
```

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `count` | integer | Yes | Number of vulnerability items in this container |

### `<vulnerability>`

Individual security vulnerability with CWE mapping, OWASP category, and remediation guidance.

```xml
<vulnerability id="VULN-INJ-001" severity="critical" confidence="high">
  <cwe-id>CWE-89</cwe-id>
  <cwe-name>SQL Injection</cwe-name>
  <owasp-category>A03:2021-Injection</owasp-category>
  <title>SQL injection via unsanitized user input in search query</title>
  <description>User-supplied search term is concatenated directly into SQL query string without parameterization or escaping.</description>
  <impact>Attacker can read, modify, or delete arbitrary database records. Potential for full database compromise.</impact>
  <remediation>Replace string concatenation with parameterized queries or prepared statements.</remediation>
  <evidence>
    <pattern>String concatenation in SQL: "SELECT * FROM products WHERE name LIKE '%" + searchTerm + "%'"</pattern>
  </evidence>
  <source file="src/repository/ProductRepository.java" line-start="45" line-end="52">
    <snippet>String sql = "SELECT * FROM products WHERE name LIKE '%" + searchTerm + "%'";
Statement stmt = conn.createStatement();
ResultSet rs = stmt.executeQuery(sql);</snippet>
  </source>
</vulnerability>
```

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string | Yes | Unique vulnerability identifier (`VULN-{CATEGORY}-{SEQUENCE}`) |
| `severity` | string | Yes | Severity level (critical, high, medium, low) |
| `confidence` | ConfidenceType | Yes | Extraction confidence level |

### `<cwe-id>`

Common Weakness Enumeration identifier (e.g., `CWE-89`, `CWE-79`).

### `<cwe-name>`

Human-readable name for the CWE (e.g., "SQL Injection", "Cross-site Scripting").

### `<owasp-category>`

OWASP Top 10 category mapping (e.g., `A03:2021-Injection`).

### `<title>`

Short, descriptive title of the vulnerability.

### `<description>`

Full description of the vulnerability explaining the weakness and conditions for exploitation.

### `<impact>`

Description of the potential security impact if the vulnerability is exploited.

### `<remediation>`

Recommended approach to fix the vulnerability.

### `<evidence>`

Evidence supporting the vulnerability finding.

#### `<pattern>`

The specific code pattern or anti-pattern that triggered the finding.

### `<source>`

Source code location where the vulnerability was identified. Uses the canonical format defined in the [Common Extraction Schema](./common-schema.md#source-references). The optional `<snippet>` child element contains the relevant code.

## Common Categories

| Category | Description | CWE Examples |
|----------|-------------|--------------|
| `INJ` | Injection flaws | CWE-89 (SQL), CWE-78 (OS Command), CWE-77 (Command) |
| `XSS` | Cross-site scripting | CWE-79 (Reflected), CWE-80 (Basic) |
| `AUTH` | Authentication issues | CWE-287 (Improper Auth), CWE-798 (Hardcoded Creds) |
| `AUTHZ` | Authorization flaws | CWE-862 (Missing Auth), CWE-639 (IDOR) |
| `CRYPTO` | Cryptographic weaknesses | CWE-327 (Broken Crypto), CWE-328 (Weak Hash) |
| `EXPOSE` | Data exposure | CWE-200 (Info Exposure), CWE-532 (Log Insertion) |
| `CONFIG` | Security misconfig | CWE-16 (Configuration), CWE-614 (Missing Secure Flag) |
| `DESER` | Deserialization | CWE-502 (Unsafe Deserialization) |
| `COMP` | Vulnerable components | CWE-1104 (Unmaintained Components) |
| `LOG` | Logging/monitoring | CWE-778 (Insufficient Logging) |

## OWASP Top 10 (2021) Reference

| ID | Category |
|----|----------|
| A01 | Broken Access Control |
| A02 | Cryptographic Failures |
| A03 | Injection |
| A04 | Insecure Design |
| A05 | Security Misconfiguration |
| A06 | Vulnerable and Outdated Components |
| A07 | Identification and Authentication Failures |
| A08 | Software and Data Integrity Failures |
| A09 | Security Logging and Monitoring Failures |
| A10 | Server-Side Request Forgery |

## Example Output

```xml
<?xml version="1.0" encoding="UTF-8"?>
<security-audit xmlns="http://reforge.dev/schema/extraction"
                project-id="ecommerce-legacy" version="1.0.0"
                schema-version="1.0.0"
                generated="2024-01-15T10:30:00Z"
                owasp-version="2021">

  <metadata>
    <total-count>2</total-count>
    <confidence-distribution>
      <high>1</high>
      <medium>1</medium>
      <low>0</low>
    </confidence-distribution>
    <extraction-timestamp>2024-01-15T10:30:00Z</extraction-timestamp>
  </metadata>

  <summary>
    <by-severity>
      <critical count="1"/>
      <high count="0"/>
      <medium count="1"/>
      <low count="0"/>
    </by-severity>
    <by-owasp-category>
      <category id="A03" name="Injection" count="1"/>
      <category id="A07" name="Identification and Authentication Failures" count="1"/>
    </by-owasp-category>
    <files-scanned>85</files-scanned>
    <files-with-findings>2</files-with-findings>
  </summary>

  <vulnerabilities count="2">
    <vulnerability id="VULN-INJ-001" severity="critical" confidence="high">
      <cwe-id>CWE-89</cwe-id>
      <cwe-name>SQL Injection</cwe-name>
      <owasp-category>A03:2021-Injection</owasp-category>
      <title>SQL injection via unsanitized user input in search query</title>
      <description>User-supplied search term is concatenated directly into SQL query string without parameterization.</description>
      <impact>Full database compromise possible. Attacker can read, modify, or delete arbitrary records.</impact>
      <remediation>Replace string concatenation with parameterized queries or prepared statements.</remediation>
      <evidence>
        <pattern>String concatenation in SQL: "SELECT * FROM products WHERE name LIKE '%" + searchTerm + "%'"</pattern>
      </evidence>
      <source file="src/repository/ProductRepository.java" line-start="45" line-end="52">
        <snippet>String sql = "SELECT * FROM products WHERE name LIKE '%" + searchTerm + "%'";
Statement stmt = conn.createStatement();
ResultSet rs = stmt.executeQuery(sql);</snippet>
      </source>
    </vulnerability>

    <vulnerability id="VULN-AUTH-001" severity="medium" confidence="medium">
      <cwe-id>CWE-798</cwe-id>
      <cwe-name>Use of Hard-coded Credentials</cwe-name>
      <owasp-category>A07:2021-Identification and Authentication Failures</owasp-category>
      <title>Hardcoded database password in configuration class</title>
      <description>Database credentials are hardcoded as string constants rather than loaded from environment or secrets manager.</description>
      <impact>Credentials exposed in source control. Anyone with repository access can connect to the database.</impact>
      <remediation>Move credentials to environment variables or a secrets management service.</remediation>
      <evidence>
        <pattern>Hardcoded credential: private static final String DB_PASSWORD = "prod_secret_123"</pattern>
      </evidence>
      <source file="src/config/DatabaseConfig.java" line-start="12" line-end="15">
        <snippet>private static final String DB_PASSWORD = "prod_secret_123";
private static final String DB_USER = "admin";</snippet>
      </source>
    </vulnerability>
  </vulnerabilities>

</security-audit>
```

## Related Schemas

- [Common Schema](./common-schema.md) — Shared elements (root attributes, metadata, source references, confidence)
- [non-functional.md](./non-functional.md) — Non-functional requirements including security findings (SEC prefix)
- [architecture.md](./architecture.md) — Architectural components relevant to security boundaries
- [issues.md](./issues.md) — Code issues that may have security implications
