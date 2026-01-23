#!/usr/bin/env bash
# manage-checkpoint.sh - Checkpoint CRUD for analysis/extraction state
# Used by analyze.md and status.md for checkpoint management.
#
# Usage: manage-checkpoint.sh <read|create|delete> [--json] [--type analysis|extraction]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

# --- Argument Parsing ---

ACTION=""
JSON_OUTPUT=false
CHECKPOINT_TYPE="analysis"

while [[ $# -gt 0 ]]; do
  case "$1" in
    read|create|delete)
      ACTION="$1"
      shift
      ;;
    --json)
      JSON_OUTPUT=true
      shift
      ;;
    --type)
      CHECKPOINT_TYPE="$2"
      shift 2
      ;;
    *)
      shift
      ;;
  esac
done

if [ -z "$ACTION" ]; then
  echo "Error: Action required (read|create|delete)" >&2
  echo "Usage: manage-checkpoint.sh <read|create|delete> [--json] [--type analysis|extraction]" >&2
  exit 1
fi

# --- Resolve Paths ---

REPO_ROOT="$(get_repo_root)"
CHECKPOINT_DIR="$REPO_ROOT/.reforge/memory/checkpoints"
ensure_dir "$CHECKPOINT_DIR"

CHECKPOINT_FILE="$CHECKPOINT_DIR/${CHECKPOINT_TYPE}-checkpoint.xml"

# --- Actions ---

case "$ACTION" in
  read)
    if [ ! -f "$CHECKPOINT_FILE" ]; then
      if [ "$JSON_OUTPUT" = true ]; then
        printf '{"EXISTS":false,"TYPE":"%s","TOTAL_FILES":0,"PROCESSED_FILES":0,"CURRENT_FILE":"","STARTED_AT":"","ELAPSED_SECONDS":0,"PERCENTAGE":0}\n' \
          "$CHECKPOINT_TYPE"
      else
        echo "No checkpoint found for type: $CHECKPOINT_TYPE" >&2
      fi
      exit 0
    fi

    # Parse checkpoint XML using awk/grep
    TOTAL_FILES="$(grep -o '<total-files>[^<]*</total-files>' "$CHECKPOINT_FILE" 2>/dev/null | sed 's/<[^>]*>//g' || echo "0")"
    PROCESSED_FILES="$(grep -o '<processed-files>[^<]*</processed-files>' "$CHECKPOINT_FILE" 2>/dev/null | sed 's/<[^>]*>//g' || echo "0")"
    CURRENT_FILE="$(grep -o '<current-file>[^<]*</current-file>' "$CHECKPOINT_FILE" 2>/dev/null | sed 's/<[^>]*>//g' || echo "")"
    STARTED_AT="$(grep -o '<started-at>[^<]*</started-at>' "$CHECKPOINT_FILE" 2>/dev/null | sed 's/<[^>]*>//g' || echo "")"
    ELAPSED_SECONDS="$(grep -o '<elapsed-seconds>[^<]*</elapsed-seconds>' "$CHECKPOINT_FILE" 2>/dev/null | sed 's/<[^>]*>//g' || echo "0")"

    # Calculate percentage
    if [ "$TOTAL_FILES" -gt 0 ] 2>/dev/null; then
      PERCENTAGE=$(( (PROCESSED_FILES * 100) / TOTAL_FILES ))
    else
      PERCENTAGE=0
    fi

    if [ "$JSON_OUTPUT" = true ]; then
      printf '{"EXISTS":true,"TYPE":"%s","TOTAL_FILES":%s,"PROCESSED_FILES":%s,"CURRENT_FILE":"%s","STARTED_AT":"%s","ELAPSED_SECONDS":%s,"PERCENTAGE":%s}\n' \
        "$CHECKPOINT_TYPE" "$TOTAL_FILES" "$PROCESSED_FILES" "$CURRENT_FILE" "$STARTED_AT" "$ELAPSED_SECONDS" "$PERCENTAGE"
    else
      echo "Checkpoint: $CHECKPOINT_TYPE" >&2
      echo "  Total files: $TOTAL_FILES" >&2
      echo "  Processed: $PROCESSED_FILES ($PERCENTAGE%)" >&2
      echo "  Current: $CURRENT_FILE" >&2
      echo "  Started: $STARTED_AT" >&2
      echo "  Elapsed: ${ELAPSED_SECONDS}s" >&2
    fi
    ;;

  create)
    # Create is handled by the agent writing the checkpoint XML directly.
    # This action ensures the directory exists and returns the path.
    if [ "$JSON_OUTPUT" = true ]; then
      printf '{"CHECKPOINT_FILE":"%s","CHECKPOINT_DIR":"%s"}\n' \
        "$CHECKPOINT_FILE" "$CHECKPOINT_DIR"
    else
      echo "Checkpoint path: $CHECKPOINT_FILE" >&2
    fi
    ;;

  delete)
    if [ -f "$CHECKPOINT_FILE" ]; then
      rm -f "$CHECKPOINT_FILE"
      if [ "$JSON_OUTPUT" = true ]; then
        printf '{"DELETED":true,"FILE":"%s"}\n' "$CHECKPOINT_FILE"
      else
        echo "Deleted checkpoint: $CHECKPOINT_FILE" >&2
      fi
    else
      if [ "$JSON_OUTPUT" = true ]; then
        printf '{"DELETED":false,"FILE":"%s"}\n' "$CHECKPOINT_FILE"
      else
        echo "No checkpoint to delete: $CHECKPOINT_FILE" >&2
      fi
    fi
    ;;
esac
