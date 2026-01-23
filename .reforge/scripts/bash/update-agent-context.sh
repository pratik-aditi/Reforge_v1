#!/usr/bin/env bash
# update-agent-context.sh - Update agent context file after analysis
# Called by /reforge.analyze after analysis completes.
# Parses analysis.xml summary and updates CLAUDE.md (or equivalent) with discovered technologies.
#
# Usage: update-agent-context.sh [agent-type] [--json]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

# --- Argument Parsing ---

AGENT_TYPE="claude"
JSON_OUTPUT=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --json)
      JSON_OUTPUT=true
      shift
      ;;
    claude|gemini|copilot|cursor|windsurf)
      AGENT_TYPE="$1"
      shift
      ;;
    *)
      shift
      ;;
  esac
done

# --- Resolve Paths ---

REPO_ROOT="$(get_repo_root)"
PROJECT_OUTPUT_DIR="$(get_project_output_dir "$REPO_ROOT")"
ANALYSIS_FILE="$PROJECT_OUTPUT_DIR/analysis.xml"

if [ ! -f "$ANALYSIS_FILE" ]; then
  echo "Error: analysis.xml not found at $ANALYSIS_FILE" >&2
  exit 1
fi

# --- Parse Analysis Summary ---

# Extract languages from analysis.xml
LANGUAGES=""
while IFS= read -r line; do
  name="$(echo "$line" | grep -o 'name="[^"]*"' | head -1 | sed 's/name="//;s/"//')"
  if [ -n "$name" ]; then
    if [ -n "$LANGUAGES" ]; then
      LANGUAGES="$LANGUAGES, $name"
    else
      LANGUAGES="$name"
    fi
  fi
done < <(grep '<language ' "$ANALYSIS_FILE" 2>/dev/null || true)

# Extract frameworks (from configuration/language-hints or detected patterns)
FRAMEWORKS=""
while IFS= read -r line; do
  hint="$(echo "$line" | sed 's/<[^>]*>//g' | sed 's/^[[:space:]]*//' | sed 's/[[:space:]]*$//')"
  if [ -n "$hint" ]; then
    if [ -n "$FRAMEWORKS" ]; then
      FRAMEWORKS="$FRAMEWORKS, $hint"
    else
      FRAMEWORKS="$hint"
    fi
  fi
done < <(grep '<language-hints>' "$ANALYSIS_FILE" 2>/dev/null || true)

# Extract file count
TOTAL_FILES="$(grep -o 'total-files="[^"]*"' "$ANALYSIS_FILE" 2>/dev/null | head -1 | sed 's/total-files="//;s/"//' || echo "0")"
TOTAL_LINES="$(grep -o 'total-lines="[^"]*"' "$ANALYSIS_FILE" 2>/dev/null | head -1 | sed 's/total-lines="//;s/"//' || echo "0")"

# --- Determine Context File ---

case "$AGENT_TYPE" in
  claude)
    CONTEXT_FILE="$REPO_ROOT/CLAUDE.md"
    ;;
  gemini)
    CONTEXT_FILE="$REPO_ROOT/GEMINI.md"
    ;;
  copilot)
    CONTEXT_FILE="$REPO_ROOT/.github/copilot-instructions.md"
    ;;
  cursor)
    CONTEXT_FILE="$REPO_ROOT/.cursorrules"
    ;;
  windsurf)
    CONTEXT_FILE="$REPO_ROOT/.windsurfrules"
    ;;
esac

# --- Update Context File ---

UPDATED=false
TIMESTAMP="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

if [ -f "$CONTEXT_FILE" ]; then
  # Check if Active Technologies section exists
  if grep -q "## Active Technologies" "$CONTEXT_FILE" 2>/dev/null; then
    # Replace existing section (between ## Active Technologies and next ##)
    TECH_BLOCK="## Active Technologies\n\n> Auto-updated by Reforge analysis on $TIMESTAMP\n\n- **Languages**: $LANGUAGES\n- **Frameworks**: ${FRAMEWORKS:-N/A}\n- **Files analyzed**: $TOTAL_FILES\n- **Total lines**: $TOTAL_LINES"

    if [[ "$OSTYPE" == "darwin"* ]]; then
      sed -i '' '/^## Active Technologies$/,/^## /{/^## Active Technologies$/!{/^## /!d;}}' "$CONTEXT_FILE"
      sed -i '' "s|^## Active Technologies$|$(echo -e "$TECH_BLOCK")|" "$CONTEXT_FILE"
    else
      sed -i '/^## Active Technologies$/,/^## /{/^## Active Technologies$/!{/^## /!d;}}' "$CONTEXT_FILE"
      sed -i "s|^## Active Technologies$|$(echo -e "$TECH_BLOCK")|" "$CONTEXT_FILE"
    fi
    UPDATED=true
  else
    # Append section at end
    {
      echo ""
      echo "## Active Technologies"
      echo ""
      echo "> Auto-updated by Reforge analysis on $TIMESTAMP"
      echo ""
      echo "- **Languages**: $LANGUAGES"
      echo "- **Frameworks**: ${FRAMEWORKS:-N/A}"
      echo "- **Files analyzed**: $TOTAL_FILES"
      echo "- **Total lines**: $TOTAL_LINES"
    } >> "$CONTEXT_FILE"
    UPDATED=true
  fi
fi

# --- Output ---

if [ "$JSON_OUTPUT" = true ]; then
  printf '{"AGENT_TYPE":"%s","CONTEXT_FILE":"%s","UPDATED":%s,"LANGUAGES":"%s","FRAMEWORKS":"%s","TOTAL_FILES":"%s","TOTAL_LINES":"%s"}\n' \
    "$AGENT_TYPE" "$CONTEXT_FILE" "$UPDATED" "$LANGUAGES" "${FRAMEWORKS:-}" "$TOTAL_FILES" "$TOTAL_LINES"
else
  if [ "$UPDATED" = true ]; then
    echo "Updated $CONTEXT_FILE with analysis results" >&2
    echo "  Languages: $LANGUAGES" >&2
    echo "  Frameworks: ${FRAMEWORKS:-N/A}" >&2
  else
    echo "Context file not found: $CONTEXT_FILE (skipped)" >&2
  fi
fi
