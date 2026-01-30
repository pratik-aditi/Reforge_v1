# Quickstart: XSD Validation Tooling

**Feature**: 004-xsd-validation-tooling
**Date**: 2026-01-29

## Overview

This guide explains how to use the XSD validation tooling to validate Reforge XML output against formal schemas.

---

## Prerequisites

### xmllint Installation

The validation script requires `xmllint` from libxml2. Check if installed:

```bash
xmllint --version
```

**Installation by platform**:

| Platform | Command |
|----------|---------|
| macOS | Pre-installed with Xcode CLI tools |
| macOS (Homebrew) | `brew install libxml2` |
| Ubuntu/Debian | `sudo apt-get install libxml2-utils` |
| RHEL/CentOS | `sudo yum install libxml2` |
| WSL | `sudo apt-get install libxml2-utils` |

---

## Basic Usage

### Validate an XML File

```bash
reforge-scripts validate-xml <xml-file> <schema-type>
```

**Example**:
```bash
reforge-scripts validate-xml reforge_output/myapp/extractions/business-rules.xml business-rules
```

### Available Schema Types

```bash
reforge-scripts validate-xml --list-schemas
```

Output:
```
Available schemas:
  analysis         - Codebase inventory (analysis.xml)
  business-rules   - Extracted business rules
  database         - Database interactions
  ui-flows         - UI component flows
  workflows        - Business workflows
  user-stories     - Generated user stories
  audit-report     - Audit coverage report
  correction-plan  - Fix execution plan
```

---

## Understanding Output

### Successful Validation

```
VALIDATION_OK
FILE: reforge_output/myapp/extractions/business-rules.xml
SCHEMA: business-rules
ELAPSED_MS: 156
```

Exit code: `0`

### Failed Validation

```
VALIDATION_FAILED
FILE: reforge_output/myapp/extractions/business-rules.xml
SCHEMA: business-rules
ERROR_COUNT: 2
---
LINE: 45
COLUMN: 12
ELEMENT: ruel
MESSAGE: Element 'ruel': This element is not expected. Expected is 'rule'.
SUGGESTION: Check spelling of element name on line 45. Expected 'rule' not 'ruel'.
---
LINE: 67
COLUMN: 5
ELEMENT: rule
MESSAGE: Element 'rule': Missing required attribute 'id'.
SUGGESTION: Add id attribute to <rule> element on line 67.
```

Exit code: `1`

---

## Command Reference

### validate-xml

```
reforge-scripts validate-xml [OPTIONS] <xml-file> <schema-type>

Arguments:
  xml-file      Path to XML file to validate
  schema-type   Schema type (e.g., business-rules, analysis)

Options:
  --json        Output in JSON format
  --help        Show help message

Special Options:
  --list-schemas    Show available schema types
  --help            Show usage information
```

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Valid — XML passes schema validation |
| 1 | Invalid — XML fails schema validation |
| 2 | Error — System/usage error |

---

## Integration Examples

### LLM Workflow Integration

After generating XML output, validate before considering the task complete:

```bash
# Generate business rules extraction
# ... LLM generates business-rules.xml ...

# Validate output
reforge-scripts validate-xml reforge_output/myapp/extractions/business-rules.xml business-rules

# If exit code is 1, read errors and fix
```

### Scripted Validation

```bash
#!/bin/bash
XML_FILE="$1"
SCHEMA="$2"

if reforge-scripts validate-xml "$XML_FILE" "$SCHEMA"; then
    echo "✅ Validation passed"
else
    echo "❌ Validation failed — see errors above"
    exit 1
fi
```

### JSON Output for Parsing

```bash
reforge-scripts validate-xml file.xml schema --json | jq '.errors[0].line'
```

---

## Verification Checklist

Use this checklist to verify the feature is working correctly:

### Installation Verification

- [ ] XSD files exist in `.reforge/schemas/xsd/`
- [ ] `reforge-scripts validate-xml --help` shows usage
- [ ] `reforge-scripts validate-xml --list-schemas` shows 8 schemas

### Validation Verification

- [ ] Valid XML file returns exit code 0 and "VALIDATION_OK"
- [ ] Invalid XML file returns exit code 1 and structured errors
- [ ] Missing XML file returns exit code 2 with clear error
- [ ] Missing schema type returns exit code 2 with clear error
- [ ] Missing xmllint returns exit code 2 with install instructions

### Output Format Verification

- [ ] Default output uses structured text format
- [ ] `--json` flag produces valid JSON
- [ ] Errors include LINE, MESSAGE, and SUGGESTION fields
- [ ] Suggestions are actionable and specific

---

## Troubleshooting

### "xmllint not found"

Install xmllint using the commands above for your platform.

### "Schema not found: xyz"

The schema type must match one of the available schemas. Use `--list-schemas` to see valid options.

### "File not found"

Ensure the XML file path is correct and the file exists.

### Encoding Errors

If you see encoding-related errors, ensure your XML file:
1. Has a proper XML declaration: `<?xml version="1.0" encoding="UTF-8"?>`
2. Is actually saved in UTF-8 encoding
3. Contains no invalid byte sequences
