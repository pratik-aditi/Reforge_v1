#!/usr/bin/env bash
# migrate-output.sh - Migrate flat output structure to categorized subdirectories
# Called by init-project.sh when legacy flat structure is detected.
#
# Usage: migrate-output.sh [--json] [target-path]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

# --- Argument Parsing ---

JSON_OUTPUT=false
TARGET_PATH=""
OUTPUT_DIR_OVERRIDE=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --json)
      JSON_OUTPUT=true
      shift
      ;;
    --output-dir)
      OUTPUT_DIR_OVERRIDE="$2"
      shift 2
      ;;
    *)
      TARGET_PATH="$1"
      shift
      ;;
  esac
done

# --- Resolve Paths ---

if [ -n "$OUTPUT_DIR_OVERRIDE" ]; then
  PROJECT_OUTPUT_DIR="$OUTPUT_DIR_OVERRIDE"
elif [ -n "$TARGET_PATH" ]; then
  REPO_ROOT="$(get_repo_root "$TARGET_PATH")"
  PROJECT_OUTPUT_DIR="$(get_project_output_dir "$REPO_ROOT")"
else
  REPO_ROOT="$(get_repo_root)"
  PROJECT_OUTPUT_DIR="$(get_project_output_dir "$REPO_ROOT")"
fi

# --- Migration Logic ---

MOVED_FILES=0

move_if_exists() {
  local src="$1"
  local dest_dir="$2"
  if [ -f "$src" ]; then
    ensure_dir "$dest_dir"
    mv "$src" "$dest_dir/"
    MOVED_FILES=$((MOVED_FILES + 1))
    if [ "$JSON_OUTPUT" != true ]; then
      echo "  Moved: $(basename "$src") → ${dest_dir#"$PROJECT_OUTPUT_DIR"/}/" >&2
    fi
  fi
}

move_glob_if_exists() {
  local pattern="$1"
  local dest_dir="$2"
  local found=false
  for f in $pattern; do
    if [ -f "$f" ]; then
      ensure_dir "$dest_dir"
      mv "$f" "$dest_dir/"
      MOVED_FILES=$((MOVED_FILES + 1))
      found=true
      if [ "$JSON_OUTPUT" != true ]; then
        echo "  Moved: $(basename "$f") → ${dest_dir#"$PROJECT_OUTPUT_DIR"/}/" >&2
      fi
    fi
  done
}

if [ "$JSON_OUTPUT" != true ]; then
  echo "Migrating output structure..." >&2
fi

# Move analysis.xml → analysis/
move_if_exists "$PROJECT_OUTPUT_DIR/analysis.xml" "$PROJECT_OUTPUT_DIR/analysis"

# Move extraction XMLs → extractions/
move_if_exists "$PROJECT_OUTPUT_DIR/business-rules.xml" "$PROJECT_OUTPUT_DIR/extractions"
move_if_exists "$PROJECT_OUTPUT_DIR/database.xml" "$PROJECT_OUTPUT_DIR/extractions"
move_if_exists "$PROJECT_OUTPUT_DIR/ui-flows.xml" "$PROJECT_OUTPUT_DIR/extractions"
move_if_exists "$PROJECT_OUTPUT_DIR/workflows.xml" "$PROJECT_OUTPUT_DIR/extractions"

# Move derived artifacts → derived/
move_if_exists "$PROJECT_OUTPUT_DIR/cross-mappings.xml" "$PROJECT_OUTPUT_DIR/derived"
move_if_exists "$PROJECT_OUTPUT_DIR/features-requirements.xml" "$PROJECT_OUTPUT_DIR/derived"

# Move registry files → derived/registries/
move_glob_if_exists "$PROJECT_OUTPUT_DIR/*-registry.md" "$PROJECT_OUTPUT_DIR/derived/registries"

# Move user-stories.xml from root → generated/
move_if_exists "$PROJECT_OUTPUT_DIR/user-stories.xml" "$PROJECT_OUTPUT_DIR/generated"

# Move diagram sources from generated/diagrams/ → diagrams/sources/
if [ -d "$PROJECT_OUTPUT_DIR/generated/diagrams" ]; then
  move_glob_if_exists "$PROJECT_OUTPUT_DIR/generated/diagrams/*.puml" "$PROJECT_OUTPUT_DIR/diagrams/sources"
  move_glob_if_exists "$PROJECT_OUTPUT_DIR/generated/diagrams/*.mmd" "$PROJECT_OUTPUT_DIR/diagrams/sources"

  # Move rendered diagrams → diagrams/rendered/
  move_glob_if_exists "$PROJECT_OUTPUT_DIR/generated/diagrams/*.png" "$PROJECT_OUTPUT_DIR/diagrams/rendered"
  move_glob_if_exists "$PROJECT_OUTPUT_DIR/generated/diagrams/*.svg" "$PROJECT_OUTPUT_DIR/diagrams/rendered"

  # Remove empty generated/diagrams/ if now empty
  if [ -d "$PROJECT_OUTPUT_DIR/generated/diagrams" ]; then
    rmdir "$PROJECT_OUTPUT_DIR/generated/diagrams" 2>/dev/null || true
  fi
fi

# --- Output ---

if [ "$JSON_OUTPUT" = true ]; then
  printf '{"MIGRATED":true,"MOVED_FILES":%d,"PROJECT_OUTPUT_DIR":"%s"}\n' \
    "$MOVED_FILES" "$PROJECT_OUTPUT_DIR"
else
  if [ "$MOVED_FILES" -gt 0 ]; then
    echo "Migration complete: $MOVED_FILES files moved." >&2
  else
    echo "No files to migrate." >&2
  fi
fi
