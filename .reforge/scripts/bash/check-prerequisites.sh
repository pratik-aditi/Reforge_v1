#!/usr/bin/env bash
# check-prerequisites.sh - Validate prerequisites for Reforge commands
# Called by /reforge.extract, /reforge.generate, /reforge.clarify, /reforge.status, /reforge.reanalyze.
#
# Usage: check-prerequisites.sh [--json] [--require-analysis] [--require-extraction <type>] [--require-audit] [--include-checkpoint]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

# --- Argument Parsing ---

JSON_OUTPUT=false
REQUIRE_ANALYSIS=false
REQUIRE_EXTRACTION=""
REQUIRE_AUDIT=false
INCLUDE_CHECKPOINT=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --json)
      JSON_OUTPUT=true
      shift
      ;;
    --require-analysis)
      REQUIRE_ANALYSIS=true
      shift
      ;;
    --require-extraction)
      REQUIRE_EXTRACTION="$2"
      shift 2
      ;;
    --require-audit)
      REQUIRE_AUDIT=true
      shift
      ;;
    --include-checkpoint)
      INCLUDE_CHECKPOINT=true
      shift
      ;;
    *)
      shift
      ;;
  esac
done

# --- Resolve Paths ---

REPO_ROOT="$(get_repo_root)"
CONFIG="$REPO_ROOT/.reforge/config.json"

if [ ! -f "$CONFIG" ]; then
  echo "Error: config.json not found at $CONFIG" >&2
  exit 1
fi

PROJECT_NAME="$(get_project_name "$REPO_ROOT")"
PROJECT_OUTPUT_DIR="$(get_project_output_dir "$REPO_ROOT")"
CLARIFICATIONS_DIR="$REPO_ROOT/.reforge/memory/clarifications"

# --- Check Analysis Status ---

ANALYSIS_STATUS="not-found"
ANALYSIS_FILE="$(resolve_analysis_file "$PROJECT_OUTPUT_DIR")"

if [ -f "$ANALYSIS_FILE" ]; then
  ANALYSIS_STATUS="completed"
fi

if [ "$REQUIRE_ANALYSIS" = true ] && [ "$ANALYSIS_STATUS" = "not-found" ]; then
  echo "Error: Analysis not found. Run /reforge.analyze first." >&2
  echo "  Expected: $ANALYSIS_FILE" >&2
  exit 1
fi

# --- Check Extraction ---

if [ -n "$REQUIRE_EXTRACTION" ]; then
  EXTRACTION_FILE="$(resolve_extraction_file "$PROJECT_OUTPUT_DIR" "$REQUIRE_EXTRACTION")"
  if [ ! -f "$EXTRACTION_FILE" ]; then
    echo "Error: Extraction '$REQUIRE_EXTRACTION' not found. Run /reforge.extract $REQUIRE_EXTRACTION first." >&2
    echo "  Expected: $EXTRACTION_FILE" >&2
    exit 1
  fi
fi

# --- Check Audit (Correction Plan) ---

if [ "$REQUIRE_AUDIT" = true ]; then
  AUDIT_DIR="$PROJECT_OUTPUT_DIR/audit"
  CORRECTION_PLAN="$AUDIT_DIR/correction-plan.xml"
  if [ ! -f "$CORRECTION_PLAN" ]; then
    echo "Error: Correction plan not found. Run /reforge.audit first." >&2
    echo "  Expected: $CORRECTION_PLAN" >&2
    exit 1
  fi
fi

# --- List Available Extractions ---

AVAILABLE_EXTRACTIONS=()
for ext_type in business-rules database ui-flows workflows; do
  local_ext_file="$(resolve_extraction_file "$PROJECT_OUTPUT_DIR" "$ext_type")"
  if [ -f "$local_ext_file" ]; then
    AVAILABLE_EXTRACTIONS+=("$ext_type")
  fi
done

# --- Checkpoint State ---

CHECKPOINT_PATH=""
if [ "$INCLUDE_CHECKPOINT" = true ]; then
  CHECKPOINT_FILE="$REPO_ROOT/.reforge/memory/checkpoints/analysis-checkpoint.xml"
  if [ -f "$CHECKPOINT_FILE" ]; then
    CHECKPOINT_PATH="$CHECKPOINT_FILE"
  fi
fi

# --- Output ---

if [ "$JSON_OUTPUT" = true ]; then
  # Build available extractions JSON array
  EXTRACTIONS_JSON="["
  first=true
  for ext in "${AVAILABLE_EXTRACTIONS[@]}"; do
    if [ "$first" = true ]; then
      first=false
    else
      EXTRACTIONS_JSON+=","
    fi
    EXTRACTIONS_JSON+="\"$ext\""
  done
  EXTRACTIONS_JSON+="]"

  # Checkpoint value
  if [ -n "$CHECKPOINT_PATH" ]; then
    CHECKPOINT_JSON="\"$CHECKPOINT_PATH\""
  else
    CHECKPOINT_JSON="null"
  fi

  printf '{"PROJECT_NAME":"%s","REPO_ROOT":"%s","PROJECT_OUTPUT_DIR":"%s","CONFIG":"%s","ANALYSIS_STATUS":"%s","AVAILABLE_EXTRACTIONS":%s,"CHECKPOINT":%s,"CLARIFICATIONS_DIR":"%s"}\n' \
    "$PROJECT_NAME" "$REPO_ROOT" "$PROJECT_OUTPUT_DIR" "$CONFIG" "$ANALYSIS_STATUS" "$EXTRACTIONS_JSON" "$CHECKPOINT_JSON" "$CLARIFICATIONS_DIR"
else
  echo "Prerequisites check:" >&2
  echo "  Project: $PROJECT_NAME" >&2
  echo "  Analysis: $ANALYSIS_STATUS" >&2
  echo "  Extractions: ${AVAILABLE_EXTRACTIONS[*]:-none}" >&2
  if [ -n "$CHECKPOINT_PATH" ]; then
    echo "  Checkpoint: $CHECKPOINT_PATH" >&2
  fi
fi
