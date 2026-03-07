---
tags:
  - commands
  - analysis
---

# /reforge.security

OWASP Top 10 security scan with CWE identifiers.

## Syntax

=== "Claude Code"

    ```
    /reforge.security [--owasp-version 2021|2017] [--severity critical|high|medium|low] [--format html|xml] [--json]
    ```

=== "GitHub Copilot"

    ```
    @reforge.security [--owasp-version 2021|2017] [--severity critical|high|medium|low] [--format html|xml] [--json]
    ```

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `--owasp-version` | No | OWASP Top 10 version to scan against (default: `2021`) |
| `--severity` | No | Minimum severity threshold to report (default: all) |
| `--format` | No | Output format: `html` or `xml` (default: `xml`) |
| `--json` | No | Output results as JSON for tooling integration |

## What It Does

Scans the analyzed codebase for common security vulnerabilities mapped to OWASP Top 10 categories and CWE identifiers. Detected vulnerability classes include:

- **Injection** -- SQL injection, XSS, command injection
- **Authentication weaknesses** -- hardcoded credentials, weak session handling
- **Cryptographic issues** -- weak algorithms, improper key management
- **Sensitive data exposure** -- unencrypted secrets, logging of PII
- **Access control** -- missing authorization checks, privilege escalation paths
- **Security misconfiguration** -- debug modes, default credentials, permissive CORS

Each finding includes the source file, line reference, OWASP category, CWE identifier, severity rating, and remediation guidance.

## Prerequisites

- Completed analysis (`/reforge.analyze`)
- Database and architecture extractions recommended for deeper coverage

## Output

Files are written to `reforge_output/<project>/extractions/`:

| File | Description |
|------|-------------|
| `security-audit.xml` | Security findings with OWASP/CWE mappings and remediation guidance |

## Example

=== "Claude Code"

    ```
    /reforge.security
    /reforge.security --severity critical
    /reforge.security --owasp-version 2017 --format html
    ```

=== "GitHub Copilot"

    ```
    @reforge.security
    @reforge.security --severity critical
    @reforge.security --owasp-version 2017 --format html
    ```

## Related Commands

- [`/reforge.extract`](extract.md) -- extract business rules and data flows that inform security analysis
- [`/reforge.validate`](validate.md) -- validate extraction integrity
- [`/reforge.audit`](audit.md) -- audit extraction coverage
