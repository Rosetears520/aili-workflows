#!/usr/bin/env bash
set -euo pipefail

MODE="selective"
REPO_URL="https://github.com/Rosetears520/aili-workflows.git"
AILI_HOME="${AILI_HOME:-$HOME/code/ai/aili-workflows}"
OPENCODE_HOME="${OPENCODE_HOME:-$HOME/.config/opencode}"

usage() {
  cat >&2 <<'EOF'
Usage: scripts/install_opencode.sh [--mode selective|copy|managed-directory|repair] [--aili-home PATH] [--opencode-home PATH]

Default mode is selective.

Modes:
  selective           Preserve agents/ and skills/ directories; link entries inside them.
  copy                Copy entries instead of symlinking. Does not auto-sync later.
  managed-directory  Replace whole agents/ and skills/ directories. Requires CONFIRM_MANAGED_DIRECTORY=yes.
  repair             Restore agents/ and skills/ if they were replaced by directory-level symlinks.
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
  selective|copy|managed-directory|repair) ;;
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

ensure_repo() {
  guard_paths
  mkdir -p "$(dirname "$AILI_HOME")"

  if [ -d "$AILI_HOME/.git" ]; then
    log "Updating repository: $AILI_HOME"
    git -C "$AILI_HOME" pull --ff-only >&2
  elif [ -e "$AILI_HOME" ]; then
    log "Refusing to use existing non-git path: $AILI_HOME"
    exit 2
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
    log "Backing up conflicting entry: $target -> $backup"
    mv "$target" "$backup"
  fi
}

link_entry() {
  local source="$1"
  local target="$2"
  backup_conflict "$target"
  if [ -L "$target" ]; then
    unlink "$target"
  fi
  ln -s "$source" "$target"
}

copy_entry() {
  local source="$1"
  local target="$2"
  backup_conflict "$target"
  rm -rf "$target"
  cp -R "$source" "$target"
}

install_entries() {
  local action="$1"
  mkdir -p "$OPENCODE_HOME"

  if [ -L "$OPENCODE_HOME/agents" ] || [ -L "$OPENCODE_HOME/skills" ]; then
    log "Refusing selective/copy mode because agents or skills is a directory-level symlink. Run --mode repair first."
    exit 2
  fi

  mkdir -p "$OPENCODE_HOME/agents" "$OPENCODE_HOME/skills"

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
}

managed_directory() {
  if [ "${CONFIRM_MANAGED_DIRECTORY:-}" != "yes" ]; then
    log "Refusing managed directory mode without explicit confirmation."
    log "Set CONFIRM_MANAGED_DIRECTORY=yes only after the user approves replacing whole agents/ and skills/ directories."
    exit 2
  fi

  mkdir -p "$OPENCODE_HOME"
  backup_conflict "$OPENCODE_HOME/agents"
  backup_conflict "$OPENCODE_HOME/skills"
  if [ -L "$OPENCODE_HOME/agents" ]; then
    unlink "$OPENCODE_HOME/agents"
  fi
  if [ -L "$OPENCODE_HOME/skills" ]; then
    unlink "$OPENCODE_HOME/skills"
  fi
  ln -s "$AILI_HOME/agents" "$OPENCODE_HOME/agents"
  ln -s "$AILI_HOME/skills" "$OPENCODE_HOME/skills"
}

repair_directory_symlinks() {
  local agents_backup skills_backup

  if [ -L "$OPENCODE_HOME/agents" ]; then
    log "Removing directory-level symlink: $OPENCODE_HOME/agents"
    unlink "$OPENCODE_HOME/agents"
  fi

  if [ -L "$OPENCODE_HOME/skills" ]; then
    log "Removing directory-level symlink: $OPENCODE_HOME/skills"
    unlink "$OPENCODE_HOME/skills"
  fi

  agents_backup="$(ls -dt "$OPENCODE_HOME"/agents.backup.* 2>/dev/null | head -n 1 || true)"
  skills_backup="$(ls -dt "$OPENCODE_HOME"/skills.backup.* 2>/dev/null | head -n 1 || true)"

  if [ -n "$agents_backup" ] && [ ! -e "$OPENCODE_HOME/agents" ]; then
    log "Restoring agents directory: $agents_backup -> $OPENCODE_HOME/agents"
    mv "$agents_backup" "$OPENCODE_HOME/agents"
  fi

  if [ -n "$skills_backup" ] && [ ! -e "$OPENCODE_HOME/skills" ]; then
    log "Restoring skills directory: $skills_backup -> $OPENCODE_HOME/skills"
    mv "$skills_backup" "$OPENCODE_HOME/skills"
  fi
}

case "$MODE" in
  repair)
    repair_directory_symlinks
    ;;
  selective)
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

printf '{"mode":%s,"runtime":%s,"aili_home":%s,"opencode_home":%s}\n' \
  "$(json_escape "$MODE")" \
  "$(json_escape "$RUNTIME")" \
  "$(json_escape "$AILI_HOME")" \
  "$(json_escape "$OPENCODE_HOME")"
