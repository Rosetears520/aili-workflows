#!/usr/bin/env bash
set -euo pipefail

MODE="selective"
REPO_URL="https://github.com/Rosetears520/aili-workflows.git"
AILI_HOME="${AILI_HOME:-$HOME/code/ai/aili-workflows}"
OPENCODE_HOME="${OPENCODE_HOME:-$HOME/.config/opencode}"
DRY_RUN="false"
NO_UPDATE="false"
RETIRED_SKILL_NAMES=("using-agent-skills" "repo-evidence-first" "verification-before-completion")
RETIRED_RECONCILIATION_NAMES=()
RETIRED_RECONCILIATION_TARGETS=()
RETIRED_RECONCILIATION_ACTIONS=()
RETIRED_RECONCILIATION_REASONS=()

usage() {
  cat >&2 <<'EOF'
Usage: scripts/install_opencode.sh [--mode selective|symlink|copy|managed-directory|repair] [--aili-home PATH] [--opencode-home PATH] [--dry-run] [--no-update]

Default mode is selective.

Modes:
  selective           Preserve OpenCode agents/ and commands/ directories; link skills into $HOME/.agents/skills.
  symlink             Alias for selective.
  copy                Copy entries instead of symlinking. Does not auto-sync later.
  managed-directory  Replace whole OpenCode agents/ and commands/ directories. Requires CONFIRM_MANAGED_DIRECTORY=yes.
  repair             Restore agents/, legacy skills/, and commands/ if they were replaced by directory-level symlinks.

Options:
  --dry-run           Print planned actions without writing OpenCode files or mutating directories.
  --no-update         Skip git pull when AILI_HOME is an existing git repository.
EOF
}

log() {
  printf '%s\n' "$*" >&2
}

json_escape() {
  printf '%s' "$1" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read()))'
}

canonicalize_path() {
  python3 -c 'import os,sys; print(os.path.realpath(os.path.abspath(sys.argv[1])))' "$1"
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --mode)
      MODE="${2:-}"
      shift 2
      ;;
    --aili-home)
      AILI_HOME="${2:-}"
      shift 2
      ;;
    --opencode-home)
      OPENCODE_HOME="${2:-}"
      shift 2
      ;;
    --dry-run)
      DRY_RUN="true"
      NO_UPDATE="true"
      shift
      ;;
    --no-update)
      NO_UPDATE="true"
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      log "Unknown argument: $1"
      usage
      exit 2
      ;;
  esac
done

case "$MODE" in
  selective|symlink|copy|managed-directory|repair) ;;
  *)
    log "Invalid mode: $MODE"
    usage
    exit 2
    ;;
esac

detect_runtime() {
  if [ -n "${WSL_DISTRO_NAME:-}" ] || grep -qi microsoft /proc/version 2>/dev/null; then
    printf 'wsl'
  elif [ "$(uname -s 2>/dev/null || true)" = "Darwin" ]; then
    printf 'macos'
  else
    printf 'linux'
  fi
}

RUNTIME="$(detect_runtime)"

guard_paths() {
  case "$AILI_HOME" in
    "$HOME/aili-workflows"|"$HOME"/aili-workflows/)
      log "Refusing to clone into the user home root: $AILI_HOME"
      exit 2
      ;;
  esac

  if [ "$RUNTIME" = "wsl" ]; then
    case "$AILI_HOME" in
      /mnt/c/*|/mnt/d/*|/mnt/*)
        log "Refusing WSL install into a mounted Windows path by default: $AILI_HOME"
        log "Set AILI_ALLOW_CROSS_ENV=yes only if the user explicitly requested this mixed setup."
        [ "${AILI_ALLOW_CROSS_ENV:-}" = "yes" ] || exit 2
        ;;
    esac
  fi
}

guard_opencode_home() {
  local default_home

  if [ -z "$OPENCODE_HOME" ]; then
    log "Refusing empty OPENCODE_HOME."
    exit 2
  fi

  case "$OPENCODE_HOME" in
    /*) ;;
    *)
      log "Refusing relative OPENCODE_HOME: $OPENCODE_HOME"
      exit 2
      ;;
  esac

  OPENCODE_HOME="$(canonicalize_path "$OPENCODE_HOME")"
  default_home="$(canonicalize_path "$HOME/.config/opencode")"

  case "$OPENCODE_HOME" in
    /|"$HOME"|"$HOME"/|/tmp|/tmp/)
      log "Refusing unsafe OPENCODE_HOME: $OPENCODE_HOME"
      exit 2
      ;;
  esac

  case "$OPENCODE_HOME" in
    "$default_home"|"$default_home"/)
      return
      ;;
  esac

  if [ "${OPENCODE_ALLOW_CUSTOM_HOME:-}" != "yes" ]; then
    log "Refusing custom OPENCODE_HOME without OPENCODE_ALLOW_CUSTOM_HOME=yes: $OPENCODE_HOME"
    exit 2
  fi
}

ensure_repo() {
  guard_paths
  if [ "$DRY_RUN" = "true" ]; then
    log "DRY RUN: would ensure parent directory exists: $(dirname "$AILI_HOME")"
  else
    mkdir -p "$(dirname "$AILI_HOME")"
  fi

  if [ -d "$AILI_HOME/.git" ]; then
    if [ "$NO_UPDATE" = "true" ]; then
      log "Skipping repository update: $AILI_HOME"
    else
      log "Updating repository: $AILI_HOME"
      git -C "$AILI_HOME" pull --ff-only >&2
    fi
  elif [ -e "$AILI_HOME" ] && [ "${AILI_ALLOW_PACKAGE_HOME:-}" = "yes" ] && [ -d "$AILI_HOME/agents" ] && { [ -d "$AILI_HOME/.agents/skills" ] || [ -d "$AILI_HOME/skills" ]; } && [ -d "$AILI_HOME/commands" ]; then
    log "Using existing packaged AILI_HOME without git update: $AILI_HOME"
  elif [ -e "$AILI_HOME" ]; then
    log "Refusing to use existing non-git path: $AILI_HOME"
    exit 2
  elif [ "$DRY_RUN" = "true" ]; then
    log "DRY RUN: would clone repository: $REPO_URL -> $AILI_HOME"
  else
    log "Cloning repository: $AILI_HOME"
    git clone "$REPO_URL" "$AILI_HOME" >&2
  fi
}

timestamp() {
  date +%Y%m%d%H%M%S
}

backup_conflict() {
  local target="$1"
  if [ -e "$target" ] && [ ! -L "$target" ]; then
    local backup="$target.backup.$(timestamp)"
    if [ "$DRY_RUN" = "true" ]; then
      log "DRY RUN: would back up conflicting entry: $target -> $backup"
      return
    fi
    log "Backing up conflicting entry: $target -> $backup"
    mv "$target" "$backup"
  fi
}

link_entry() {
  local source="$1"
  local target="$2"
  backup_conflict "$target"
  if [ "$DRY_RUN" = "true" ]; then
    log "DRY RUN: would link entry: $target -> $source"
    return
  fi
  if [ -L "$target" ]; then
    unlink "$target"
  fi
  ln -s "$source" "$target"
}

copy_entry() {
  local source="$1"
  local target="$2"
  backup_conflict "$target"
  if [ "$DRY_RUN" = "true" ]; then
    log "DRY RUN: would copy entry: $source -> $target"
    return
  fi
  rm -rf "$target"
  cp -R "$source" "$target"
}

install_global_agents() {
  local action="$1"
  local source="$AILI_HOME/templates/opencode-global-AGENTS.md"
  local target="$OPENCODE_HOME/AGENTS.md"

  if [ ! -f "$source" ]; then
    if [ "$DRY_RUN" = "true" ]; then
      log "DRY RUN: would install global AGENTS from expected source: $source -> $target"
      return
    fi
    log "Missing global AGENTS source: $source"
    exit 2
  fi

  "$action" "$source" "$target"
}

skill_source_root() {
  if [ ! -d "$AILI_HOME/.agents/skills" ]; then
    log "Missing canonical skills source: $AILI_HOME/.agents/skills"
    exit 2
  fi
  printf '%s\n' "$AILI_HOME/.agents/skills"
}

shared_skill_install_root() {
  local home_root root
  if [ -z "${HOME:-}" ]; then
    log "Refusing empty HOME for shared skill install root."
    exit 2
  fi
  home_root="$(canonicalize_path "$HOME")"
  case "$home_root" in
    /|/tmp|/tmp/)
      log "Refusing unsafe HOME for shared skill install root: $home_root"
      exit 2
      ;;
  esac
  root="$(canonicalize_path "$HOME/.agents/skills")"
  case "$root" in
    /|/tmp|/tmp/)
      log "Refusing unsafe shared skill install root: $root"
      exit 2
      ;;
  esac
  case "$root" in
    "$OPENCODE_HOME"|"$OPENCODE_HOME"/*)
      log "Refusing shared skill install root under OPENCODE_HOME: $root"
      exit 2
      ;;
  esac
  printf '%s\n' "$root"
}

record_retired_skill_reconciliation() {
  local name="$1"
  local target="$2"
  local action="$3"
  local reason="$4"
  local index="${#RETIRED_RECONCILIATION_NAMES[@]}"
  RETIRED_RECONCILIATION_NAMES[$index]="$name"
  RETIRED_RECONCILIATION_TARGETS[$index]="$target"
  RETIRED_RECONCILIATION_ACTIONS[$index]="$action"
  RETIRED_RECONCILIATION_REASONS[$index]="$reason"
}

reconcile_retired_skill_entries() {
  local skills_target_root="$1"
  local name target expected_source raw_target candidate resolved_target reason

  for name in "${RETIRED_SKILL_NAMES[@]}"; do
    target="$skills_target_root/$name"
    expected_source="$(canonicalize_path "$AILI_HOME/.agents/skills/$name")"

    if [ -L "$target" ]; then
      if ! raw_target="$(readlink "$target")"; then
        reason="symlink target could not be read; ownership is ambiguous"
        log "Preserving ambiguous retired skill entry: $target ($reason)"
        record_retired_skill_reconciliation "$name" "$target" "preserved" "$reason"
        continue
      fi
      case "$raw_target" in
        /*) candidate="$raw_target" ;;
        *) candidate="$(dirname "$target")/$raw_target" ;;
      esac
      resolved_target="$(canonicalize_path "$candidate")"
      if [ "$resolved_target" = "$expected_source" ]; then
        reason="exact symlink target matches the canonical retired skill source"
        if [ "$DRY_RUN" = "true" ]; then
          log "DRY RUN: would unlink proven installer-managed retired skill: $target -> $raw_target"
          record_retired_skill_reconciliation "$name" "$target" "planned-unlink" "$reason"
        else
          log "Unlinking proven installer-managed retired skill: $target -> $raw_target"
          unlink "$target"
          record_retired_skill_reconciliation "$name" "$target" "unlinked" "$reason"
        fi
      else
        reason="symlink target differs from the canonical retired skill source; ownership is ambiguous"
        log "Preserving ambiguous retired skill entry: $target -> $raw_target"
        record_retired_skill_reconciliation "$name" "$target" "preserved" "$reason"
      fi
    elif [ -e "$target" ]; then
      reason="entry is not a symlink to the canonical retired skill source; copied, modified, or user-owned content is preserved"
      log "Preserving ambiguous retired skill entry: $target ($reason)"
      record_retired_skill_reconciliation "$name" "$target" "preserved" "$reason"
    else
      reason="retired skill destination is absent"
      log "Retired skill entry absent; no action: $target"
      record_retired_skill_reconciliation "$name" "$target" "absent" "$reason"
    fi
  done
}

retired_skill_reconciliation_json() {
  local index separator=""
  printf '['
  for index in "${!RETIRED_RECONCILIATION_NAMES[@]}"; do
    printf '%s{"name":%s,"target":%s,"action":%s,"reason":%s}' \
      "$separator" \
      "$(json_escape "${RETIRED_RECONCILIATION_NAMES[$index]}")" \
      "$(json_escape "${RETIRED_RECONCILIATION_TARGETS[$index]}")" \
      "$(json_escape "${RETIRED_RECONCILIATION_ACTIONS[$index]}")" \
      "$(json_escape "${RETIRED_RECONCILIATION_REASONS[$index]}")"
    separator=','
  done
  printf ']'
}

validate_manifest_allowlist() {
  python3 - "$AILI_HOME" <<'PY'
import json
import os
import pathlib
import sys

home = pathlib.Path(sys.argv[1])
manifest_path = home / "manifests" / "rose-aili.components.json"

def fail(message):
    print(message, file=sys.stderr)
    raise SystemExit(2)

def validate_relative(label, value):
    if not value or pathlib.PurePosixPath(value).is_absolute() or ".." in pathlib.PurePosixPath(value).parts:
        fail(f"Invalid manifest {label} path: {value}")

try:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
except FileNotFoundError:
    fail(f"Missing component manifest: {manifest_path}")
except json.JSONDecodeError as exc:
    fail(f"Invalid component manifest JSON: {manifest_path}: {exc}")

if manifest.get("name") != "rose-aili" or manifest.get("schemaVersion") != 1:
    fail(f"Unsupported component manifest: {manifest_path}")

components = manifest.get("components", {})

def validate_install_targets(kind, name, targets, expected_targets):
    if len(targets) != len(expected_targets):
        fail(f"Invalid manifest {kind} installTargets for {name}: expected {len(expected_targets)}, got {len(targets)}")
    actual = {(target.get("kind"), target.get("path")) for target in targets}
    for target in targets:
        validate_relative(f"install target for {name}", target.get("path"))
        if target.get("kind") not in {"shared", "opencode"}:
            fail(f"Invalid install target kind for {name}: {target.get('kind')}")
    for expected in expected_targets:
        if (expected[0], expected[1]) not in actual:
            fail(f"Invalid manifest {kind} installTargets for {name}: missing {expected[0]}:{expected[1]}")

def manifest_names(kind):
    names = []
    for entry in components.get(kind, []):
        name = entry.get("name")
        if not name:
            fail(f"Invalid manifest {kind} entry without name.")
        if kind == "agents":
            expected_path = f"agents/{name}.md"
            expected_targets = [("opencode", expected_path)]
        elif kind == "commands":
            expected_path = f"commands/{name}.md"
            expected_targets = [("opencode", expected_path)]
        else:
            expected_path = f".agents/skills/{name}"
            expected_targets = [("shared", expected_path)]

        path_value = entry.get("path")
        validate_relative(f"{kind} for {name}", path_value)
        if path_value != expected_path:
            fail(f"Invalid manifest {kind} path for {name}: expected {expected_path}, got {path_value}")
        source_paths = [entry.get("sourcePath"), *(entry.get("sourceFallbackPaths") or []), path_value]
        for source_path in dict.fromkeys(value for value in source_paths if value):
            validate_relative(f"{kind} source for {name}", source_path)
        if kind == "skills":
            source_path = entry.get("sourcePath")
            if source_path and source_path != expected_path:
                fail(f"Invalid manifest {kind} sourcePath for {name}: expected {expected_path}, got {source_path}")
        validate_install_targets(kind, name, entry.get("installTargets") or [{"kind": "opencode", "path": path_value}], expected_targets)
        names.append(name)
    if len(set(names)) != len(names):
        fail(f"Duplicate manifest {kind} entry.")
    return sorted(names)

def disk_agents():
    root = home / "agents"
    return sorted(path.stem for path in root.glob("*.md") if path.is_file()) if root.is_dir() else []

def disk_commands():
    root = home / "commands"
    return sorted(path.stem for path in root.glob("*.md") if path.is_file()) if root.is_dir() else []

def disk_skills():
    root = home / ".agents" / "skills"
    if not root.is_dir():
        return []
    return sorted(path.name for path in root.iterdir() if path.is_dir() and (path / "SKILL.md").is_file())

disk_by_kind = {"agents": disk_agents(), "commands": disk_commands(), "skills": disk_skills()}
errors = []
for kind in ("agents", "commands", "skills"):
    expected = manifest_names(kind)
    actual = disk_by_kind[kind]
    extras = [name for name in actual if name not in expected]
    missing = [name for name in expected if name not in actual]
    if extras:
        errors.append(f"Unmanifested {kind} component(s): {', '.join(extras)}")
    if missing:
        errors.append(f"Manifest {kind} component(s) missing from AILI_HOME: {', '.join(missing)}")

if errors:
    for error in errors:
        print(error, file=sys.stderr)
    raise SystemExit(2)
PY
}

install_entries() {
  local action="$1"
  local skills_source
  skills_source="$(skill_source_root)"
  local skills_target_root
  skills_target_root="$(shared_skill_install_root)"
  validate_manifest_allowlist
  if [ "$DRY_RUN" = "true" ]; then
    log "DRY RUN: would ensure OpenCode directory exists: $OPENCODE_HOME"
    log "DRY RUN: would ensure shared skills directory exists: $skills_target_root"
  else
    mkdir -p "$OPENCODE_HOME"
    mkdir -p "$skills_target_root"
  fi

  if [ -e "$OPENCODE_HOME" ] && { [ -L "$OPENCODE_HOME/agents" ] || [ -L "$OPENCODE_HOME/commands" ]; }; then
    log "Refusing selective/copy mode because agents or commands is a directory-level symlink. Run --mode repair first."
    exit 2
  fi

  if [ "$DRY_RUN" = "true" ]; then
    log "DRY RUN: would ensure OpenCode subdirectories exist: agents, commands"
  else
    mkdir -p "$OPENCODE_HOME/agents" "$OPENCODE_HOME/commands"
  fi

  reconcile_retired_skill_entries "$skills_target_root"

  install_global_agents "$action"

  local file name target dir
  for file in "$AILI_HOME"/agents/*.md; do
    [ -f "$file" ] || continue
    name="$(basename "$file")"
    target="$OPENCODE_HOME/agents/$name"
    "$action" "$file" "$target"
  done

  for dir in "$skills_source"/*; do
    [ -d "$dir" ] || continue
    if [ ! -f "$dir/SKILL.md" ]; then
      log "Skipping non-skill directory without SKILL.md: $dir"
      continue
    fi
    name="$(basename "$dir")"
    target="$skills_target_root/$name"
    "$action" "$dir" "$target"
  done

  for file in "$AILI_HOME"/commands/*.md; do
    [ -f "$file" ] || continue
    name="$(basename "$file")"
    target="$OPENCODE_HOME/commands/$name"
    "$action" "$file" "$target"
  done
}

managed_directory() {
  local skills_source
  skills_source="$(skill_source_root)"
  local skills_target_root
  skills_target_root="$(shared_skill_install_root)"
  validate_manifest_allowlist

  if [ "${CONFIRM_MANAGED_DIRECTORY:-}" != "yes" ]; then
    log "Refusing managed directory mode without explicit confirmation."
    log "Set CONFIRM_MANAGED_DIRECTORY=yes only after the user approves replacing whole agents/ and commands/ directories."
    exit 2
  fi

  reconcile_retired_skill_entries "$skills_target_root"

  if [ "$DRY_RUN" = "true" ]; then
    log "DRY RUN: would ensure OpenCode directory exists: $OPENCODE_HOME"
    log "DRY RUN: would replace agents and commands with directory symlinks from $AILI_HOME"
    log "DRY RUN: would install shared skill entries into: $skills_target_root"
    install_global_agents link_entry
    local dir name target
    for dir in "$skills_source"/*; do
      [ -d "$dir" ] || continue
      [ -f "$dir/SKILL.md" ] || continue
      name="$(basename "$dir")"
      target="$skills_target_root/$name"
      link_entry "$dir" "$target"
    done
    return
  fi

  mkdir -p "$OPENCODE_HOME"
  mkdir -p "$skills_target_root"
  install_global_agents link_entry
  backup_conflict "$OPENCODE_HOME/agents"
  backup_conflict "$OPENCODE_HOME/commands"
  if [ -L "$OPENCODE_HOME/agents" ]; then
    unlink "$OPENCODE_HOME/agents"
  fi
  if [ -L "$OPENCODE_HOME/commands" ]; then
    unlink "$OPENCODE_HOME/commands"
  fi
  ln -s "$AILI_HOME/agents" "$OPENCODE_HOME/agents"
  ln -s "$AILI_HOME/commands" "$OPENCODE_HOME/commands"

  local dir name target
  for dir in "$skills_source"/*; do
    [ -d "$dir" ] || continue
    if [ ! -f "$dir/SKILL.md" ]; then
      log "Skipping non-skill directory without SKILL.md: $dir"
      continue
    fi
    name="$(basename "$dir")"
    target="$skills_target_root/$name"
    link_entry "$dir" "$target"
  done
}

repair_directory_symlinks() {
  local agents_backup skills_backup commands_backup

  if [ -L "$OPENCODE_HOME/agents" ]; then
    if [ "$DRY_RUN" = "true" ]; then
      log "DRY RUN: would remove directory-level symlink: $OPENCODE_HOME/agents"
    else
      log "Removing directory-level symlink: $OPENCODE_HOME/agents"
      unlink "$OPENCODE_HOME/agents"
    fi
  fi

  if [ -L "$OPENCODE_HOME/skills" ]; then
    if [ "$DRY_RUN" = "true" ]; then
      log "DRY RUN: would remove directory-level symlink: $OPENCODE_HOME/skills"
    else
      log "Removing directory-level symlink: $OPENCODE_HOME/skills"
      unlink "$OPENCODE_HOME/skills"
    fi
  fi

  if [ -L "$OPENCODE_HOME/commands" ]; then
    if [ "$DRY_RUN" = "true" ]; then
      log "DRY RUN: would remove directory-level symlink: $OPENCODE_HOME/commands"
    else
      log "Removing directory-level symlink: $OPENCODE_HOME/commands"
      unlink "$OPENCODE_HOME/commands"
    fi
  fi

  agents_backup="$(ls -dt "$OPENCODE_HOME"/agents.backup.* 2>/dev/null | head -n 1 || true)"
  skills_backup="$(ls -dt "$OPENCODE_HOME"/skills.backup.* 2>/dev/null | head -n 1 || true)"
  commands_backup="$(ls -dt "$OPENCODE_HOME"/commands.backup.* 2>/dev/null | head -n 1 || true)"

  if [ -n "$agents_backup" ] && [ ! -e "$OPENCODE_HOME/agents" ]; then
    if [ "$DRY_RUN" = "true" ]; then
      log "DRY RUN: would restore agents directory: $agents_backup -> $OPENCODE_HOME/agents"
    else
      log "Restoring agents directory: $agents_backup -> $OPENCODE_HOME/agents"
      mv "$agents_backup" "$OPENCODE_HOME/agents"
    fi
  fi

  if [ -n "$skills_backup" ] && [ ! -e "$OPENCODE_HOME/skills" ]; then
    if [ "$DRY_RUN" = "true" ]; then
      log "DRY RUN: would restore skills directory: $skills_backup -> $OPENCODE_HOME/skills"
    else
      log "Restoring skills directory: $skills_backup -> $OPENCODE_HOME/skills"
      mv "$skills_backup" "$OPENCODE_HOME/skills"
    fi
  fi

  if [ -n "$commands_backup" ] && [ ! -e "$OPENCODE_HOME/commands" ]; then
    if [ "$DRY_RUN" = "true" ]; then
      log "DRY RUN: would restore commands directory: $commands_backup -> $OPENCODE_HOME/commands"
    else
      log "Restoring commands directory: $commands_backup -> $OPENCODE_HOME/commands"
      mv "$commands_backup" "$OPENCODE_HOME/commands"
    fi
  fi
}

guard_opencode_home

case "$MODE" in
  repair)
    repair_directory_symlinks
    ;;
  selective|symlink)
    ensure_repo
    install_entries link_entry
    ;;
  copy)
    ensure_repo
    install_entries copy_entry
    ;;
  managed-directory)
    ensure_repo
    managed_directory
    ;;
esac

printf '{"mode":%s,"runtime":%s,"aili_home":%s,"opencode_home":%s,"dry_run":%s,"no_update":%s,"retired_skill_reconciliation":' \
  "$(json_escape "$MODE")" \
  "$(json_escape "$RUNTIME")" \
  "$(json_escape "$AILI_HOME")" \
  "$(json_escape "$OPENCODE_HOME")" \
  "$(json_escape "$DRY_RUN")" \
  "$(json_escape "$NO_UPDATE")"
retired_skill_reconciliation_json
printf '}\n'
