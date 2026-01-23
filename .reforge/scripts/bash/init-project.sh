#!/usr/bin/env bash
# init-project.sh - Initialize project output structure
# Called by /reforge.analyze to set up directories and resolve paths.
#
# Usage: init-project.sh [--json] [--name <name>] [target-path]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

# --- Argument Parsing ---

JSON_OUTPUT=false
PROJECT_NAME_OVERRIDE=""
TARGET_PATH=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --json)
      JSON_OUTPUT=true
      shift
      ;;
    --name)
      PROJECT_NAME_OVERRIDE="$2"
      shift 2
      ;;
    *)
      TARGET_PATH="$1"
      shift
      ;;
  esac
done

# --- Resolve Paths ---

if [ -n "$TARGET_PATH" ]; then
  REPO_ROOT="$(get_repo_root "$TARGET_PATH")"
else
  REPO_ROOT="$(get_repo_root)"
fi

CONFIG="$REPO_ROOT/.reforge/config.json"

if [ ! -f "$CONFIG" ]; then
  echo "Error: config.json not found at $CONFIG" >&2
  exit 1
fi

# --- Resolve Project Name ---

if [ -n "$PROJECT_NAME_OVERRIDE" ]; then
  PROJECT_NAME="$PROJECT_NAME_OVERRIDE"
else
  PROJECT_NAME="$(get_project_name "$REPO_ROOT")"
fi

# Set project name in config.json if currently empty
CURRENT_NAME="$(get_config_value "project.name" "$CONFIG" 2>/dev/null || true)"
if [ -z "$CURRENT_NAME" ] && [ -n "$PROJECT_NAME" ]; then
  # Update config.json with derived project name (using sed, no jq)
  if [[ "$OSTYPE" == "darwin"* ]]; then
    sed -i '' "s/\"name\": \"\"/\"name\": \"$PROJECT_NAME\"/" "$CONFIG"
  else
    sed -i "s/\"name\": \"\"/\"name\": \"$PROJECT_NAME\"/" "$CONFIG"
  fi
fi

# --- Resolve Output Paths ---

OUTPUT_DIR="$(get_output_dir "$REPO_ROOT")"
PROJECT_OUTPUT_DIR="$REPO_ROOT/$OUTPUT_DIR/$PROJECT_NAME"

# --- Create Directory Structure ---

ensure_dir "$PROJECT_OUTPUT_DIR/analysis"
ensure_dir "$PROJECT_OUTPUT_DIR/extractions"
ensure_dir "$PROJECT_OUTPUT_DIR/derived/registries"
ensure_dir "$PROJECT_OUTPUT_DIR/generated"
ensure_dir "$PROJECT_OUTPUT_DIR/diagrams/sources"
ensure_dir "$PROJECT_OUTPUT_DIR/diagrams/rendered"

# --- Migrate Legacy Structure ---

# If analysis.xml exists at the old flat path, run migration
if [ -f "$PROJECT_OUTPUT_DIR/analysis.xml" ]; then
  bash "$SCRIPT_DIR/migrate-output.sh" --output-dir "$PROJECT_OUTPUT_DIR"
fi

ensure_dir "$REPO_ROOT/.reforge/memory/history"
ensure_dir "$REPO_ROOT/.reforge/memory/backups"
ensure_dir "$REPO_ROOT/.reforge/memory/checkpoints"
ensure_dir "$REPO_ROOT/.reforge/memory/clarifications"
ensure_dir "$REPO_ROOT/.reforge/memory/logs"

# --- Output ---

if [ "$JSON_OUTPUT" = true ]; then
  printf '{"PROJECT_NAME":"%s","OUTPUT_DIR":"%s","PROJECT_OUTPUT_DIR":"%s","CONFIG":"%s","REPO_ROOT":"%s"}\n' \
    "$PROJECT_NAME" "$OUTPUT_DIR" "$PROJECT_OUTPUT_DIR" "$CONFIG" "$REPO_ROOT"
else
  echo "Project initialized: $PROJECT_NAME" >&2
  echo "  Output directory: $PROJECT_OUTPUT_DIR" >&2
  echo "  Config: $CONFIG" >&2
fi
