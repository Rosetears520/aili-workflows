#!/usr/bin/env bash
set -euo pipefail

MODE="selective"
REPO_URL="https://github.com/Rosetears520/aili-workflows.git"
AILI_HOME="${AILI_HOME:-$HOME/code/ai/aili-workflows}"
OPENCODE_HOME="${OPENCODE_HOME:-$HOME/.config/opencode}"
DRY_RUN="false"
NO_UPDATE="false"

usage() {
  cat >&2 <<'EOF'
Usage: scripts/install_opencode.sh [--mode selective|symlink|copy|managed-directory|repair] [--aili-home PATH] [--opencode-home PATH] [--dry-run] [--no-update]

Default mode is selective.

Modes:
  selective           Preserve agents/, skills/, and commands/ directories; link entries inside them.
  symlink             Alias for selective.
  copy                Copy entries instead of symlinking. Does not auto-sync later.
  managed-directory  Replace whole agents/, skills/, and commands/ directories. Requires CONFIRM_MANAGED_DIRECTORY=yes.
  repair             Restore agents/, skills/, and commands/ if they were replaced by directory-level symlinks.

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
  local default_home="$HOME/.config/opencode"

  if [ -z "$OPENCODE_HOME" ]; then
    log "Refusing empty OPENCODE_HOME."
    exit 2
  fi

  case "$OPENCODE_HOME" in
    /|"$HOME"|"$HOME"/|/tmp|/tmp/)
      log "Refusing unsafe OPENCODE_HOME: $OPENCODE_HOME"
      exit 2
      ;;
  esac

  case "$OPENCODE_HOME" in
    /*) ;;
    *)
      log "Refusing relative OPENCODE_HOME: $OPENCODE_HOME"
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
  elif [ -e "$AILI_HOME" ] && [ "${AILI_ALLOW_PACKAGE_HOME:-}" = "yes" ] && [ -d "$AILI_HOME/agents" ] && [ -d "$AILI_HOME/skills" ] && [ -d "$AILI_HOME/commands" ]; then
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

install_entries() {
  local action="$1"
  if [ "$DRY_RUN" = "true" ]; then
    log "DRY RUN: would ensure OpenCode directory exists: $OPENCODE_HOME"
  else
    mkdir -p "$OPENCODE_HOME"
  fi

  if [ -e "$OPENCODE_HOME" ] && { [ -L "$OPENCODE_HOME/agents" ] || [ -L "$OPENCODE_HOME/skills" ] || [ -L "$OPENCODE_HOME/commands" ]; }; then
    log "Refusing selective/copy mode because agents, skills, or commands is a directory-level symlink. Run --mode repair first."
    exit 2
  fi

  if [ "$DRY_RUN" = "true" ]; then
    log "DRY RUN: would ensure OpenCode subdirectories exist: agents, skills, commands"
  else
    mkdir -p "$OPENCODE_HOME/agents" "$OPENCODE_HOME/skills" "$OPENCODE_HOME/commands"
  fi

  local file name target dir
  for file in "$AILI_HOME"/agents/*.md; do
    [ -f "$file" ] || continue
    name="$(basename "$file")"
    target="$OPENCODE_HOME/agents/$name"
    "$action" "$file" "$target"
  done

  for dir in "$AILI_HOME"/skills/*; do
    [ -d "$dir" ] || continue
    if [ ! -f "$dir/SKILL.md" ]; then
      log "Skipping non-skill directory without SKILL.md: $dir"
      continue
    fi
    name="$(basename "$dir")"
    target="$OPENCODE_HOME/skills/$name"
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
  if [ "${CONFIRM_MANAGED_DIRECTORY:-}" != "yes" ]; then
    log "Refusing managed directory mode without explicit confirmation."
    log "Set CONFIRM_MANAGED_DIRECTORY=yes only after the user approves replacing whole agents/, skills/, and commands/ directories."
    exit 2
  fi

  if [ "$DRY_RUN" = "true" ]; then
    log "DRY RUN: would ensure OpenCode directory exists: $OPENCODE_HOME"
    log "DRY RUN: would replace agents, skills, and commands with directory symlinks from $AILI_HOME"
    return
  fi

  mkdir -p "$OPENCODE_HOME"
  backup_conflict "$OPENCODE_HOME/agents"
  backup_conflict "$OPENCODE_HOME/skills"
  backup_conflict "$OPENCODE_HOME/commands"
  if [ -L "$OPENCODE_HOME/agents" ]; then
    unlink "$OPENCODE_HOME/agents"
  fi
  if [ -L "$OPENCODE_HOME/skills" ]; then
    unlink "$OPENCODE_HOME/skills"
  fi
  if [ -L "$OPENCODE_HOME/commands" ]; then
    unlink "$OPENCODE_HOME/commands"
  fi
  ln -s "$AILI_HOME/agents" "$OPENCODE_HOME/agents"
  ln -s "$AILI_HOME/skills" "$OPENCODE_HOME/skills"
  ln -s "$AILI_HOME/commands" "$OPENCODE_HOME/commands"
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

printf '{"mode":%s,"runtime":%s,"aili_home":%s,"opencode_home":%s,"dry_run":%s,"no_update":%s}\n' \
  "$(json_escape "$MODE")" \
  "$(json_escape "$RUNTIME")" \
  "$(json_escape "$AILI_HOME")" \
  "$(json_escape "$OPENCODE_HOME")" \
  "$(json_escape "$DRY_RUN")" \
  "$(json_escape "$NO_UPDATE")"
