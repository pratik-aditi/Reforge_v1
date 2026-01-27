"""Update agent context file after analysis.

This module provides the same functionality as .reforge/scripts/bash/update-agent-context.sh
but implemented in pure Python for cross-platform compatibility.

Parses analysis.xml summary and updates CLAUDE.md (or equivalent) with discovered technologies.

Usage from CLI: reforge update-agent-context [agent-type] [--json]
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from .common import (
    ReforgeError,
    get_project_output_dir,
    get_repo_root,
    resolve_analysis_file,
)


# Agent type to context file mapping
AGENT_CONTEXT_FILES = {
    "claude": "CLAUDE.md",
    "gemini": "GEMINI.md",
    "copilot": ".github/copilot-instructions.md",
    "cursor": ".cursorrules",
    "windsurf": ".windsurfrules",
}


@dataclass
class AgentContextResult:
    """Result of updating agent context."""

    agent_type: str
    context_file: Path
    updated: bool
    languages: str
    frameworks: str
    total_files: str
    total_lines: str

    def to_json(self) -> str:
        """Convert to JSON string matching bash script output format."""
        return json.dumps(
            {
                "AGENT_TYPE": self.agent_type,
                "CONTEXT_FILE": str(self.context_file),
                "UPDATED": self.updated,
                "LANGUAGES": self.languages,
                "FRAMEWORKS": self.frameworks,
                "TOTAL_FILES": self.total_files,
                "TOTAL_LINES": self.total_lines,
            }
        )


def _extract_languages(content: str) -> str:
    """Extract languages from analysis.xml content.

    Args:
        content: XML content to parse.

    Returns:
        Comma-separated list of languages.
    """
    # Find all language name attributes
    pattern = r'<language [^>]*name="([^"]*)"'
    matches = re.findall(pattern, content)
    return ", ".join(matches) if matches else ""


def _extract_frameworks(content: str) -> str:
    """Extract frameworks/hints from analysis.xml content.

    Args:
        content: XML content to parse.

    Returns:
        Comma-separated list of frameworks.
    """
    # Find language-hints content
    pattern = r"<language-hints>([^<]*)</language-hints>"
    matches = re.findall(pattern, content)
    hints = [h.strip() for h in matches if h.strip()]
    return ", ".join(hints) if hints else ""


def _extract_attribute(content: str, attr: str) -> str:
    """Extract an attribute value from XML content.

    Args:
        content: XML content to parse.
        attr: Attribute name to find.

    Returns:
        Attribute value or "0" if not found.
    """
    pattern = rf'{attr}="([^"]*)"'
    match = re.search(pattern, content)
    return match.group(1) if match else "0"


def update_agent_context(agent_type: str = "claude") -> AgentContextResult:
    """Update agent context file with analysis results.

    Parses analysis.xml and updates the appropriate context file
    with discovered technologies.

    Args:
        agent_type: Type of agent ("claude", "gemini", "copilot", "cursor", "windsurf").

    Returns:
        AgentContextResult with update status.

    Raises:
        ReforgeError: If analysis.xml not found.
    """
    repo_root = get_repo_root()
    project_output_dir = get_project_output_dir(repo_root)
    analysis_file = resolve_analysis_file(project_output_dir)

    if not analysis_file.is_file():
        raise ReforgeError(f"analysis.xml not found at {analysis_file}")

    content = analysis_file.read_text()

    # Parse analysis summary
    languages = _extract_languages(content)
    frameworks = _extract_frameworks(content)
    total_files = _extract_attribute(content, "total-files")
    total_lines = _extract_attribute(content, "total-lines")

    # Determine context file
    if agent_type not in AGENT_CONTEXT_FILES:
        agent_type = "claude"  # Default fallback

    context_filename = AGENT_CONTEXT_FILES[agent_type]
    context_file = repo_root / context_filename

    # Update context file
    updated = False
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    if context_file.is_file():
        file_content = context_file.read_text()

        tech_block = f"""## Active Technologies

> Auto-updated by Reforge analysis on {timestamp}

- **Languages**: {languages}
- **Frameworks**: {frameworks or "N/A"}
- **Files analyzed**: {total_files}
- **Total lines**: {total_lines}"""

        if "## Active Technologies" in file_content:
            # Replace existing section
            pattern = r"## Active Technologies\n\n.*?(?=\n## |\Z)"
            new_content = re.sub(pattern, tech_block, file_content, flags=re.DOTALL)
            context_file.write_text(new_content)
            updated = True
        else:
            # Append section at end
            with context_file.open("a") as f:
                f.write("\n" + tech_block + "\n")
            updated = True

    return AgentContextResult(
        agent_type=agent_type,
        context_file=context_file,
        updated=updated,
        languages=languages,
        frameworks=frameworks,
        total_files=total_files,
        total_lines=total_lines,
    )
