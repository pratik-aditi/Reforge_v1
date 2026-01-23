#!/usr/bin/env bash
# common.sh - Shared library for Reforge scripts
# Sourced by all other scripts. Provides path resolution and validation helpers.

set -e

# --- Path Resolution ---

get_repo_root() {
  local dir="${1:-$(pwd)}"
  while [ "$dir" != "/" ]; do
    if [ -d "$dir/.reforge" ]; then
      echo "$dir"
      return 0
    fi
    if [ -d "$dir/.git" ]; then
      echo "$dir"
      return 0
    fi
    dir="$(dirname "$dir")"
  done
  echo "Error: Could not find repository root (.reforge/ or .git/ marker)" >&2
  return 1
}

get_config_value() {
  local key_path="$1"
  local config_file="$2"

  if [ ! -f "$config_file" ]; then
    echo ""
    return 1
  fi

  # Parse JSON string values using awk (no jq dependency)
  # Supports dotted key paths like "project.name" or "output.directory"
  local IFS='.'
  read -ra keys <<< "$key_path"

  if [ ${#keys[@]} -eq 1 ]; then
    local target_key="${keys[0]}"
    awk -v key="$target_key" '
      $0 ~ "\"" key "\"[ \t]*:" {
        # Extract value after the colon
        sub(/.*"'"$target_key"'"[ \t]*:[ \t]*/, "")
        # Remove trailing comma and whitespace
        sub(/,[ \t]*$/, "")
        # Remove surrounding quotes if present
        if (match($0, /^"(.*)"$/, m)) {
          print m[1]
        } else {
          # Trim whitespace for non-string values
          gsub(/^[ \t]+|[ \t]+$/, "")
          print
        }
        exit
      }
    ' "$config_file"
  elif [ ${#keys[@]} -eq 2 ]; then
    local parent="${keys[0]}"
    local child="${keys[1]}"
    awk '
      BEGIN { in_parent=0; depth=0 }
      /"'"$parent"'"[ \t]*:/ && /\{/ {
        in_parent=1
        depth=1
        next
      }
      /"'"$parent"'"[ \t]*:/ && !/\{/ {
        in_parent=1
        depth=0
        next
      }
      in_parent && /\{/ { depth++ }
      in_parent && /\}/ {
        depth--
        if (depth <= 0) { in_parent=0; next }
      }
      in_parent && /"'"$child"'"[ \t]*:/ {
        sub(/.*"'"$child"'"[ \t]*:[ \t]*/, "")
        sub(/,[ \t]*$/, "")
        if (match($0, /^"(.*)"$/, m)) {
          print m[1]
        } else {
          gsub(/^[ \t]+|[ \t]+$/, "")
          print
        }
        exit
      }
    ' "$config_file"
  else
    echo ""
    return 1
  fi
}

get_project_name() {
  local repo_root="$1"
  local config_file="$repo_root/.reforge/config.json"
  local name=""

  if [ -f "$config_file" ]; then
    name="$(get_config_value "project.name" "$config_file" 2>/dev/null || true)"
  fi

  if [ -z "$name" ]; then
    name="$(basename "$repo_root")"
  fi

  echo "$name"
}

get_output_dir() {
  local repo_root="$1"
  local config_file="$repo_root/.reforge/config.json"
  local dir=""

  if [ -f "$config_file" ]; then
    dir="$(get_config_value "output.directory" "$config_file" 2>/dev/null || true)"
  fi

  if [ -z "$dir" ]; then
    dir="reforge_output"
  fi

  echo "$dir"
}

get_project_output_dir() {
  local repo_root="$1"
  local output_dir
  local project_name

  output_dir="$(get_output_dir "$repo_root")"
  project_name="$(get_project_name "$repo_root")"

  echo "$repo_root/$output_dir/$project_name"
}

# --- Validation Helpers ---

check_file() {
  local file_path="$1"
  local label="${2:-$file_path}"

  if [ -f "$file_path" ]; then
    echo "  [OK] $label" >&2
    return 0
  else
    echo "  [MISSING] $label" >&2
    return 1
  fi
}

check_dir() {
  local dir_path="$1"
  local label="${2:-$dir_path}"

  if [ -d "$dir_path" ]; then
    echo "  [OK] $label" >&2
    return 0
  else
    echo "  [MISSING] $label" >&2
    return 1
  fi
}

ensure_dir() {
  local dir_path="$1"
  mkdir -p "$dir_path"
}
