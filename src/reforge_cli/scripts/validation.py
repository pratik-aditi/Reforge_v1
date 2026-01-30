"""XSD validation tooling for Reforge XML output.

This module provides functions to validate XML files against XSD schemas
using xmllint, with structured output optimized for LLM consumption.
"""

import json
import platform
import re
import shutil
import subprocess
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional

from .common import get_repo_root, ReforgeError


# Exit codes per data-model.md
EXIT_VALID = 0
EXIT_INVALID = 1
EXIT_ERROR = 2

# Schema descriptions for --list-schemas
SCHEMA_DESCRIPTIONS = {
    "analysis": "Codebase inventory (analysis.xml)",
    "business-rules": "Extracted business rules",
    "database": "Database interactions",
    "ui-flows": "UI component flows",
    "workflows": "Business workflows",
    "user-stories": "Generated user stories",
    "audit-report": "Audit coverage report",
    "correction-plan": "Fix execution plan",
}


@dataclass
class ValidationError:
    """Single validation error from xmllint."""

    line: int
    column: Optional[int]
    element: Optional[str]
    message: str
    suggestion: Optional[str]
    raw_output: str


@dataclass
class ValidationResult:
    """Result of XML schema validation."""

    # Status
    valid: bool
    exit_code: int

    # Context
    xml_file: str
    schema_type: str
    schema_file: str

    # Errors (empty if valid)
    errors: list[ValidationError] = field(default_factory=list)
    error_count: int = 0

    # Metadata
    elapsed_ms: int = 0
    xmllint_version: Optional[str] = None

    def to_json(self) -> str:
        """Convert result to JSON string."""
        data = asdict(self)
        return json.dumps(data, indent=2)


def check_xmllint_available() -> tuple[bool, Optional[str], Optional[str]]:
    """Check if xmllint is available and return version info.

    Returns:
        Tuple of (is_available, version_string, install_instructions)
    """
    xmllint_path = shutil.which("xmllint")

    if xmllint_path is None:
        # Generate platform-specific install instructions
        system = platform.system().lower()

        if system == "darwin":
            instructions = (
                "xmllint is not installed. Install options:\n"
                "  - Xcode CLI tools: xcode-select --install\n"
                "  - Homebrew: brew install libxml2"
            )
        elif system == "linux":
            # Detect distro if possible
            instructions = (
                "xmllint is not installed. Install with:\n"
                "  - Ubuntu/Debian: sudo apt-get install libxml2-utils\n"
                "  - RHEL/CentOS: sudo yum install libxml2\n"
                "  - WSL: sudo apt-get install libxml2-utils"
            )
        else:
            instructions = (
                "xmllint is not available on this platform.\n"
                "Consider using WSL (Windows Subsystem for Linux) and installing libxml2-utils."
            )

        return False, None, instructions

    # Get version
    try:
        result = subprocess.run(
            ["xmllint", "--version"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        # xmllint outputs version to stderr
        version_output = result.stderr or result.stdout
        # Extract version number (e.g., "20914" from "xmllint: using libxml version 20914")
        match = re.search(r"version (\d+)", version_output)
        version = match.group(1) if match else "unknown"
        return True, version, None
    except (subprocess.TimeoutExpired, OSError):
        return True, "unknown", None


def get_available_schemas(repo_root: Optional[Path] = None) -> dict[str, Path]:
    """Get available XSD schemas from .reforge/schemas/xsd/.

    Args:
        repo_root: Repository root path. If None, auto-detected.

    Returns:
        Dict mapping schema type names to XSD file paths.
    """
    if repo_root is None:
        repo_root = get_repo_root()

    xsd_dir = repo_root / ".reforge" / "schemas" / "xsd"

    if not xsd_dir.exists():
        return {}

    schemas = {}
    for xsd_file in xsd_dir.glob("*.xsd"):
        schema_type = xsd_file.stem  # filename without .xsd
        schemas[schema_type] = xsd_file

    return schemas


def generate_suggestion(message: str, line: int, element: Optional[str]) -> Optional[str]:
    """Generate a fix suggestion based on error message patterns.

    Uses error categories from data-model.md:
    - unknown-element: "This element is not expected"
    - missing-attribute: "Missing required attribute"
    - invalid-value: "not a valid value"
    - missing-element: "Missing child element"
    - wrong-order: "expected before"
    - extra-content: "character content is not allowed"

    Args:
        message: The xmllint error message
        line: Line number of the error
        element: Element name if available

    Returns:
        Suggestion string or None if no pattern matched
    """
    msg_lower = message.lower()

    # Unknown element (misspelling)
    if "this element is not expected" in msg_lower or "is not expected" in msg_lower:
        # Try to extract expected element name
        expected_match = re.search(r"expected is ['\"]?(\w+)['\"]?", message, re.IGNORECASE)
        if expected_match:
            expected = expected_match.group(1)
            return f"Check spelling of element name on line {line}. Expected '{expected}'."
        return f"Check spelling of element name on line {line}."

    # Missing attribute
    if "missing required attribute" in msg_lower or "attribute .* is required" in msg_lower:
        attr_match = re.search(r"attribute ['\"]?(\w+)['\"]?", message, re.IGNORECASE)
        if attr_match and element:
            attr = attr_match.group(1)
            return f"Add '{attr}' attribute to <{element}> element on line {line}."
        elif element:
            return f"Add missing required attribute to <{element}> element on line {line}."
        return f"Add missing required attribute on line {line}."

    # Invalid attribute value
    if "not a valid value" in msg_lower or "is not valid" in msg_lower:
        if element:
            return f"Check attribute value on <{element}> element on line {line}."
        return f"Check attribute value on line {line}."

    # Missing element
    if "missing child element" in msg_lower or "expecting element" in msg_lower:
        if element:
            return f"Add required child element to <{element}> on line {line}."
        return f"Add missing required element on line {line}."

    # Wrong order
    if "expected before" in msg_lower:
        return f"Reorder elements on line {line} to match schema sequence."

    # Extra content
    if "character content is not allowed" in msg_lower:
        if element:
            return f"Remove text content from <{element}> element on line {line}."
        return f"Remove unexpected text content on line {line}."

    # Generic suggestion for unrecognized patterns
    return f"Review XML structure on line {line}."


def parse_xmllint_errors(stderr: str, xml_file: str) -> list[ValidationError]:
    r"""Parse xmllint stderr output into ValidationError objects.

    Uses regex pattern from research.md:
    ^(?P<file>[^:]+):(?P<line>\d+):\s*(?:element\s+(?P<element>\w+):\s*)?(?:Schemas validity error\s*:\s*)?(?P<message>.+)$

    Args:
        stderr: The stderr output from xmllint
        xml_file: Path to the XML file being validated

    Returns:
        List of ValidationError objects
    """
    errors = []

    # Pattern to match xmllint error lines
    # Format: file.xml:45: element rule: Schemas validity error : Element 'ruel': ...
    pattern = re.compile(
        r"^(?P<file>[^:]+):(?P<line>\d+):\s*"
        r"(?:element\s+(?P<element>[\w\-]+):\s*)?"
        r"(?:Schemas validity error\s*:\s*)?"
        r"(?P<message>.+)$",
        re.MULTILINE,
    )

    for match in pattern.finditer(stderr):
        line = int(match.group("line"))
        element = match.group("element")
        message = match.group("message").strip()
        raw_output = match.group(0)

        # Skip non-error lines (like "validates" success message)
        if "validates" in message.lower() and "error" not in message.lower():
            continue

        suggestion = generate_suggestion(message, line, element)

        errors.append(
            ValidationError(
                line=line,
                column=None,  # xmllint doesn't always provide column
                element=element,
                message=message,
                suggestion=suggestion,
                raw_output=raw_output,
            )
        )

    return errors


def validate_xml(
    xml_file: Path,
    schema_type: str,
    repo_root: Optional[Path] = None,
) -> ValidationResult:
    """Validate an XML file against an XSD schema using xmllint.

    Args:
        xml_file: Path to the XML file to validate
        schema_type: Schema type name (e.g., "business-rules")
        repo_root: Repository root path. If None, auto-detected.

    Returns:
        ValidationResult with status and any errors
    """
    start_time = time.time()

    if repo_root is None:
        repo_root = get_repo_root()

    # Normalize schema type (remove .xsd if present)
    schema_type = schema_type.removesuffix(".xsd")

    # Check xmllint availability
    xmllint_available, xmllint_version, install_instructions = check_xmllint_available()

    if not xmllint_available:
        elapsed_ms = int((time.time() - start_time) * 1000)
        return ValidationResult(
            valid=False,
            exit_code=EXIT_ERROR,
            xml_file=str(xml_file),
            schema_type=schema_type,
            schema_file="",
            errors=[
                ValidationError(
                    line=0,
                    column=None,
                    element=None,
                    message=install_instructions or "xmllint not found",
                    suggestion="Install xmllint to enable XML validation.",
                    raw_output="",
                )
            ],
            error_count=1,
            elapsed_ms=elapsed_ms,
            xmllint_version=None,
        )

    # Check XML file exists
    if not xml_file.exists():
        elapsed_ms = int((time.time() - start_time) * 1000)
        return ValidationResult(
            valid=False,
            exit_code=EXIT_ERROR,
            xml_file=str(xml_file),
            schema_type=schema_type,
            schema_file="",
            errors=[
                ValidationError(
                    line=0,
                    column=None,
                    element=None,
                    message=f"XML file not found: {xml_file}",
                    suggestion="Check the file path and ensure the file exists.",
                    raw_output="",
                )
            ],
            error_count=1,
            elapsed_ms=elapsed_ms,
            xmllint_version=xmllint_version,
        )

    # Resolve schema path
    schemas = get_available_schemas(repo_root)
    if schema_type not in schemas:
        available = ", ".join(sorted(schemas.keys())) if schemas else "none"
        elapsed_ms = int((time.time() - start_time) * 1000)
        return ValidationResult(
            valid=False,
            exit_code=EXIT_ERROR,
            xml_file=str(xml_file),
            schema_type=schema_type,
            schema_file="",
            errors=[
                ValidationError(
                    line=0,
                    column=None,
                    element=None,
                    message=f"Schema not found: {schema_type}. Available schemas: {available}",
                    suggestion=f"Use one of the available schema types: {available}",
                    raw_output="",
                )
            ],
            error_count=1,
            elapsed_ms=elapsed_ms,
            xmllint_version=xmllint_version,
        )

    schema_file = schemas[schema_type]

    # Run xmllint
    try:
        result = subprocess.run(
            ["xmllint", "--schema", str(schema_file), str(xml_file), "--noout"],
            capture_output=True,
            text=True,
            timeout=30,
        )
    except subprocess.TimeoutExpired:
        elapsed_ms = int((time.time() - start_time) * 1000)
        return ValidationResult(
            valid=False,
            exit_code=EXIT_ERROR,
            xml_file=str(xml_file),
            schema_type=schema_type,
            schema_file=str(schema_file),
            errors=[
                ValidationError(
                    line=0,
                    column=None,
                    element=None,
                    message="Validation timed out after 30 seconds",
                    suggestion="The XML file may be too large or contain circular references.",
                    raw_output="",
                )
            ],
            error_count=1,
            elapsed_ms=30000,
            xmllint_version=xmllint_version,
        )
    except OSError as e:
        elapsed_ms = int((time.time() - start_time) * 1000)
        return ValidationResult(
            valid=False,
            exit_code=EXIT_ERROR,
            xml_file=str(xml_file),
            schema_type=schema_type,
            schema_file=str(schema_file),
            errors=[
                ValidationError(
                    line=0,
                    column=None,
                    element=None,
                    message=f"Failed to run xmllint: {e}",
                    suggestion="Ensure xmllint is properly installed and accessible.",
                    raw_output="",
                )
            ],
            error_count=1,
            elapsed_ms=elapsed_ms,
            xmllint_version=xmllint_version,
        )

    elapsed_ms = int((time.time() - start_time) * 1000)

    # Parse results
    # xmllint returns 0 for valid, non-zero for errors
    # Success message goes to stderr: "file.xml validates"
    if result.returncode == 0:
        return ValidationResult(
            valid=True,
            exit_code=EXIT_VALID,
            xml_file=str(xml_file),
            schema_type=schema_type,
            schema_file=str(schema_file),
            errors=[],
            error_count=0,
            elapsed_ms=elapsed_ms,
            xmllint_version=xmllint_version,
        )

    # Parse errors from stderr
    errors = parse_xmllint_errors(result.stderr, str(xml_file))

    return ValidationResult(
        valid=False,
        exit_code=EXIT_INVALID,
        xml_file=str(xml_file),
        schema_type=schema_type,
        schema_file=str(schema_file),
        errors=errors,
        error_count=len(errors),
        elapsed_ms=elapsed_ms,
        xmllint_version=xmllint_version,
    )


def format_structured_output(result: ValidationResult) -> str:
    """Format validation result as structured text for LLM consumption.

    Uses format from data-model.md:
    - VALIDATION_OK/VALIDATION_FAILED header
    - FILE, SCHEMA, ELAPSED_MS fields
    - --- delimiter between errors
    - LINE, COLUMN, ELEMENT, MESSAGE, SUGGESTION for each error

    Args:
        result: The ValidationResult to format

    Returns:
        Structured text output
    """
    lines = []

    if result.valid:
        lines.append("VALIDATION_OK")
        lines.append(f"FILE: {result.xml_file}")
        lines.append(f"SCHEMA: {result.schema_type}")
        lines.append(f"ELAPSED_MS: {result.elapsed_ms}")
    else:
        lines.append("VALIDATION_FAILED")
        lines.append(f"FILE: {result.xml_file}")
        lines.append(f"SCHEMA: {result.schema_type}")
        lines.append(f"ERROR_COUNT: {result.error_count}")

        for error in result.errors:
            lines.append("---")
            lines.append(f"LINE: {error.line}")
            if error.column is not None:
                lines.append(f"COLUMN: {error.column}")
            if error.element:
                lines.append(f"ELEMENT: {error.element}")
            lines.append(f"MESSAGE: {error.message}")
            if error.suggestion:
                lines.append(f"SUGGESTION: {error.suggestion}")

    return "\n".join(lines)


def format_list_schemas(schemas: dict[str, Path]) -> str:
    """Format available schemas for display.

    Args:
        schemas: Dict mapping schema types to paths

    Returns:
        Formatted schema list
    """
    lines = ["Available schemas:"]
    for schema_type in sorted(schemas.keys()):
        description = SCHEMA_DESCRIPTIONS.get(schema_type, "")
        lines.append(f"  {schema_type:<18} - {description}")
    return "\n".join(lines)
