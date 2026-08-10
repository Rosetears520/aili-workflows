#!/usr/bin/env bash
set -euo pipefail

MODE="selective"
PROFILE="default"
SELECTED_SKILLS=()
SELECTED_SKILL_GROUPS=()
REPO_URL="https://github.com/Rosetears520/aili-workflows.git"
AILI_HOME="${AILI_HOME:-$HOME/code/ai/aili-workflows}"
OPENCODE_HOME="${OPENCODE_HOME:-$HOME/.config/opencode}"
DRY_RUN="false"
NO_UPDATE="false"
INSTALL_OPENCODE="false"
SKIP_OFFICECLI="false"
ENABLE_OFFICECLI="false"
RECONCILE_RETIRED_SKILLS="false"
OFFICECLI_STATUS=""
OFFICECLI_PACKAGE_SPEC=""
OFFICECLI_VERSION=""
OFFICECLI_TARGET=""
OFFICECLI_SHIM=""
OFFICECLI_REASON=""
OFFICECLI_OBSERVED_VERSION=""
OFFICECLI_EXIT_CODE=""
RETIRED_SKILL_NAMES=()
RETIRED_RECONCILIATION_NAMES=()
RETIRED_RECONCILIATION_TARGETS=()
RETIRED_RECONCILIATION_ACTIONS=()
RETIRED_RECONCILIATION_REASONS=()

usage() {
  cat >&2 <<'EOF'
Usage: scripts/install_opencode.sh [--mode selective|symlink|copy|managed-directory|repair] [--profile default|pi|opencode] [--skill NAME] [--skill-group research|specialized-dev] [--aili-home PATH] [--opencode-home PATH] [--dry-run] [--no-update] [--enable-officecli|--skip-officecli] [--reconcile-retired-skills]

The default profile installs Core shared Skills. The pi profile adds generated Pi prompts. The opencode profile adds generated OpenCode integration files.

Modes:
  selective           Link shared skills; with --opencode, preserve OpenCode directories and link their managed entries.
  symlink             Alias for selective.
  copy                Copy entries instead of symlinking. Does not auto-sync later.
  managed-directory  Replace whole OpenCode agents/ and commands/ directories. Requires CONFIRM_MANAGED_DIRECTORY=yes.
  repair             Restore agents/, legacy skills/, and commands/ if they were replaced by directory-level symlinks.

Options:
  --profile NAME      Select default, pi, or opencode.
  --opencode          Legacy alias for --profile opencode.
  --skill NAME        Select one retained Skill; repeatable.
  --skill-group NAME  Select research or specialized-dev; repeatable.
  --dry-run           Print planned actions without writing OpenCode files or mutating directories.
  --no-update         Skip git pull when AILI_HOME is an existing git repository.
  --enable-officecli  Run the separately approved managed OfficeCLI operation.
  --skip-officecli    Do not plan or run OfficeCLI.
  --reconcile-retired-skills  Reconcile only proven installer-owned retired entries.
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
    --profile)
      PROFILE="${2:-}"
      shift 2
      ;;
    --skill)
      SELECTED_SKILLS+=("${2:-}")
      shift 2
      ;;
    --skill-group)
      SELECTED_SKILL_GROUPS+=("${2:-}")
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
    --opencode)
      if [ "$PROFILE" != "default" ] && [ "$PROFILE" != "opencode" ]; then
        log "--opencode cannot be combined with --profile $PROFILE"
        exit 2
      fi
      PROFILE="opencode"
      INSTALL_OPENCODE="true"
      shift
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
    --skip-officecli)
      SKIP_OFFICECLI="true"
      shift
      ;;
    --enable-officecli)
      ENABLE_OFFICECLI="true"
      shift
      ;;
    --reconcile-retired-skills)
      RECONCILE_RETIRED_SKILLS="true"
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

case "$PROFILE" in
  default|pi|opencode) ;;
  *)
    log "Unknown profile: $PROFILE"
    exit 2
    ;;
esac

if [ "$PROFILE" = "opencode" ]; then
  INSTALL_OPENCODE="true"
fi

if [ "$SKIP_OFFICECLI" = "true" ] && [ "$ENABLE_OFFICECLI" = "true" ]; then
  log "--enable-officecli cannot be combined with --skip-officecli"
  exit 2
fi

if [ "$INSTALL_OPENCODE" != "true" ] && { [ "$MODE" = "managed-directory" ] || [ "$MODE" = "repair" ]; }; then
  log "Mode $MODE requires --opencode because it mutates OpenCode-owned directories."
  exit 2
fi

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
  local source="$AILI_HOME/generated/opencode/AGENTS.md"
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

manifest_component_entries() {
  local component_kind="$1"
  python3 - "$AILI_HOME" "$component_kind" <<'PY'
import json
import pathlib
import sys

home = pathlib.Path(sys.argv[1])
kind = sys.argv[2]
manifest = json.loads((home / "manifests" / "rose-aili.components.json").read_text(encoding="utf-8"))
for entry in manifest.get("components", {}).get(kind, []):
    source = entry.get("sourcePath") or entry["path"]
    targets = entry.get("installTargets") or [{"kind": "opencode", "path": entry["path"]}]
    if len(targets) != 1 or targets[0].get("kind") != "opencode":
        raise SystemExit(f"Invalid manifest {kind} install target for {entry.get('name')}")
    print(f"{source}\t{targets[0]['path']}")
PY
}

validate_skill_selection() {
  manifest_skill_entries shared >/dev/null
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
  if [ "$INSTALL_OPENCODE" = "true" ]; then
    case "$root" in
      "$OPENCODE_HOME"|"$OPENCODE_HOME"/*)
        log "Refusing shared skill install root under OPENCODE_HOME: $root"
        exit 2
        ;;
    esac
  fi
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

    if [ "$RECONCILE_RETIRED_SKILLS" != "true" ]; then
      if [ -e "$target" ] || [ -L "$target" ]; then
        record_retired_skill_reconciliation "$name" "$target" "preserved" "Retired-entry reconciliation requires the explicit --reconcile-retired-skills operation."
      else
        record_retired_skill_reconciliation "$name" "$target" "absent" "Retired skill destination is absent."
      fi
      continue
    fi

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

load_retired_skill_names() {
  local names
  if ! names="$(python3 - "$AILI_HOME/manifests/rose-aili.components.json" <<'PY'
import json
import pathlib
import sys

manifest = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
for entry in sorted(manifest["retiredSkills"], key=lambda value: value["name"]):
    print(entry["name"])
PY
  )"; then
    log "Unable to load retired Skill inventory from the component manifest."
    exit 2
  fi
  mapfile -t RETIRED_SKILL_NAMES <<<"$names"
}

load_officecli_contract() {
  local manifest_path="$AILI_HOME/manifests/officecli-tool.json"
  local managed_target shim_path
  if ! IFS=$'\t' read -r OFFICECLI_PACKAGE_SPEC OFFICECLI_VERSION managed_target shim_path < <(python3 - "$manifest_path" <<'PY'
import json
import pathlib
import sys

path = pathlib.Path(sys.argv[1])
try:
    value = json.loads(path.read_text(encoding="utf-8"))
except (OSError, json.JSONDecodeError) as exc:
    print(f"Unable to load OfficeCLI tool manifest {path}: {exc}", file=sys.stderr)
    raise SystemExit(2)

expected_args = ["install", "--prefix", "{target}", "--no-save", "--no-package-lock", "@officecli/officecli@1.0.143"]
valid = (
    value.get("schemaVersion") == 1
    and value.get("name") == "officecli"
    and value.get("package") == "@officecli/officecli"
    and value.get("version") == "1.0.143"
    and value.get("packageSpec") == "@officecli/officecli@1.0.143"
    and value.get("registry") == "https://registry.npmjs.org"
    and value.get("license") == "Apache-2.0"
    and value.get("source") == "https://github.com/iOfficeAI/OfficeCLI/tree/v1.0.143"
    and value.get("managedTarget") == ".agents/tools/officecli"
    and value.get("shimPath") == "node_modules/.bin/officecli"
    and value.get("install", {}).get("command") == "npm"
    and value.get("install", {}).get("args") == expected_args
    and value.get("install", {}).get("effects") == ["network dependency resolution", "local-prefix package files under the managed target"]
    and value.get("environment", {}).get("OFFICECLI_SKIP_UPDATE") == "1"
    and value.get("upgradePolicy") == "exact-pin-only"
)
if not valid:
    print(f"OfficeCLI tool manifest differs from the fixed managed-install contract: {path}", file=sys.stderr)
    raise SystemExit(2)
print("\t".join([value["packageSpec"], value["version"], value["managedTarget"], value["shimPath"]]))
PY
  ); then
    return 1
  fi

  local home_root
  if [ -z "${HOME:-}" ]; then
    log "Refusing empty HOME for OfficeCLI managed target."
    return 1
  fi
  home_root="$(canonicalize_path "$HOME")"
  case "$home_root" in
    /|/tmp|/tmp/)
      log "Refusing unsafe HOME for OfficeCLI managed target: $home_root"
      return 1
      ;;
  esac
  OFFICECLI_TARGET="$home_root/$managed_target"
  OFFICECLI_SHIM="$OFFICECLI_TARGET/$shim_path"
}

probe_officecli() {
  local output code observed
  OFFICECLI_OBSERVED_VERSION=""
  if [ ! -e "$OFFICECLI_SHIM" ] && [ ! -L "$OFFICECLI_SHIM" ]; then
    OFFICECLI_STATUS="missing"
    OFFICECLI_REASON="Managed OfficeCLI shim is missing."
    return
  fi

  set +e
  output="$(OFFICECLI_SKIP_UPDATE=1 "$OFFICECLI_SHIM" --version 2>&1)"
  code=$?
  set -e
  if [ "$code" -ne 0 ]; then
    OFFICECLI_STATUS="invalid"
    OFFICECLI_REASON="${output:-managed OfficeCLI --version failed with exit code $code}"
    return
  fi
  observed="$(printf '%s' "$output" | python3 -c 'import re,sys; versions=sorted(set(re.findall(r"(?<![0-9])([0-9]+\.[0-9]+\.[0-9]+)(?![0-9])", sys.stdin.read()))); sys.stdout.write(versions[0]) if len(versions) == 1 else sys.exit(1)' 2>/dev/null || true)"
  if [ -z "$observed" ]; then
    OFFICECLI_STATUS="invalid"
    OFFICECLI_REASON="Managed OfficeCLI --version output did not contain exactly one semantic version."
    return
  fi
  OFFICECLI_OBSERVED_VERSION="$observed"
  if [ "$observed" != "$OFFICECLI_VERSION" ]; then
    OFFICECLI_STATUS="drift"
    OFFICECLI_REASON="Managed OfficeCLI version $observed differs from $OFFICECLI_VERSION."
    return
  fi
  OFFICECLI_STATUS="ready"
  OFFICECLI_REASON=""
}

officecli_protected_fingerprint() {
  python3 - "$HOME" "$OPENCODE_HOME" <<'PY'
import hashlib
import json
import os
import pathlib
import stat
import sys

home = pathlib.Path(sys.argv[1]).resolve()
opencode_homes = {home / ".config" / "opencode", pathlib.Path(sys.argv[2]).resolve()}
paths = [home / ".agents" / "skills" / name for name in ("officecli", "officecli-docx", "officecli-xlsx", "officecli-pptx")]
paths.extend(home / name for name in (".bashrc", ".bash_profile", ".profile", ".zshrc"))
for root in opencode_homes:
    paths.extend((root / "opencode.json", root / "opencode.jsonc"))
    paths.extend(root / "skills" / name for name in ("officecli", "officecli-docx", "officecli-xlsx", "officecli-pptx"))

def fingerprint(path):
    try:
        info = path.lstat()
    except FileNotFoundError:
        return "missing"
    if stat.S_ISLNK(info.st_mode):
        return "link:" + os.readlink(path)
    if stat.S_ISREG(info.st_mode):
        return f"file:{stat.S_IMODE(info.st_mode)}:" + hashlib.sha256(path.read_bytes()).hexdigest()
    if stat.S_ISDIR(info.st_mode):
        return f"directory:{stat.S_IMODE(info.st_mode)}:" + "|".join(f"{child.name}:{fingerprint(child)}" for child in sorted(path.iterdir(), key=lambda item: item.name))
    return f"other:{stat.S_IMODE(info.st_mode)}"

print(json.dumps({str(path): fingerprint(path) for path in sorted(set(paths), key=str)}, sort_keys=True, separators=(",", ":")))
PY
}

run_officecli_install() {
  local before after npm_output npm_code previous_status previous_reason
  if ! load_officecli_contract; then
    OFFICECLI_STATUS="failed"
    OFFICECLI_REASON="OfficeCLI managed-install contract could not be loaded."
    return 1
  fi
  if [ "$SKIP_OFFICECLI" = "true" ]; then
    OFFICECLI_STATUS="skipped"
    OFFICECLI_REASON="OfficeCLI explicitly skipped; no probe or install command ran."
    return 0
  fi
  if [ "$ENABLE_OFFICECLI" != "true" ]; then
    OFFICECLI_STATUS="planned"
    OFFICECLI_REASON="OfficeCLI is default-selected but requires a separate exact install approval; no probe or install command ran."
    return 0
  fi
  if [ "$DRY_RUN" = "true" ]; then
    OFFICECLI_STATUS="planned"
    OFFICECLI_REASON="Would detect the managed exact version and install only if missing or drifted; dry-run performed no probe, directory creation, or command execution."
    return 0
  fi

  before="$(officecli_protected_fingerprint)"
  probe_officecli
  after="$(officecli_protected_fingerprint)"
  if [ "$before" != "$after" ]; then
    OFFICECLI_STATUS="failed"
    OFFICECLI_REASON="OfficeCLI version probe changed a protected Skill, MCP, or shell integration path."
    return 1
  fi
  if [ "$OFFICECLI_STATUS" = "ready" ]; then
    OFFICECLI_STATUS="preserved"
    OFFICECLI_REASON="Existing exact managed OfficeCLI version preserved; npm did not run."
    return 0
  fi

  previous_status="$OFFICECLI_STATUS"
  previous_reason="$OFFICECLI_REASON"
  set +e
  npm_output="$(OFFICECLI_SKIP_UPDATE=1 npm install --prefix "$OFFICECLI_TARGET" --no-save --no-package-lock "$OFFICECLI_PACKAGE_SPEC" 2>&1)"
  npm_code=$?
  set -e
  OFFICECLI_EXIT_CODE="$npm_code"
  if [ -n "$npm_output" ]; then
    log "$npm_output"
  fi
  if [ "$npm_code" -ne 0 ]; then
    after="$(officecli_protected_fingerprint)"
    OFFICECLI_STATUS="failed"
    OFFICECLI_REASON="${npm_output:-npm local-prefix install exited with code $npm_code}; prior status was $previous_status: $previous_reason"
    if [ "$before" != "$after" ]; then
      OFFICECLI_REASON="$OFFICECLI_REASON; protected Skill, MCP, or shell integration path changed"
    fi
    return 1
  fi

  probe_officecli
  after="$(officecli_protected_fingerprint)"
  if [ "$before" != "$after" ]; then
    OFFICECLI_STATUS="failed"
    OFFICECLI_REASON="OfficeCLI local-prefix install changed a protected Skill, MCP, or shell integration path."
    return 1
  fi
  if [ "$OFFICECLI_STATUS" != "ready" ]; then
    previous_status="$OFFICECLI_STATUS"
    previous_reason="$OFFICECLI_REASON"
    OFFICECLI_STATUS="failed"
    OFFICECLI_REASON="npm exited successfully but managed postinstall verification was $previous_status: $previous_reason"
    return 1
  fi
  OFFICECLI_STATUS="installed"
  OFFICECLI_REASON="Fixed local-prefix install passed managed shim and exact-version verification."
  return 0
}

officecli_summary_json() {
  local observed_json="null" exit_code_json="null"
  if [ -n "$OFFICECLI_OBSERVED_VERSION" ]; then
    observed_json="$(json_escape "$OFFICECLI_OBSERVED_VERSION")"
  fi
  if [ -n "$OFFICECLI_EXIT_CODE" ]; then
    exit_code_json="$OFFICECLI_EXIT_CODE"
  fi
  printf '{"status":%s,"package":%s,"expectedVersion":%s,"observedVersion":%s,"target":%s,"shim":%s,"command":%s,"argv":[%s,%s,%s,%s,%s,%s,%s],"effects":[%s,%s],"reason":%s,"recovery":%s,"exitCode":%s}' \
    "$(json_escape "$OFFICECLI_STATUS")" \
    "$(json_escape "$OFFICECLI_PACKAGE_SPEC")" \
    "$(json_escape "$OFFICECLI_VERSION")" \
    "$observed_json" \
    "$(json_escape "$OFFICECLI_TARGET")" \
    "$(json_escape "$OFFICECLI_SHIM")" \
    "$(json_escape "npm install --prefix $OFFICECLI_TARGET --no-save --no-package-lock $OFFICECLI_PACKAGE_SPEC")" \
    "$(json_escape "npm")" \
    "$(json_escape "install")" \
    "$(json_escape "--prefix")" \
    "$(json_escape "$OFFICECLI_TARGET")" \
    "$(json_escape "--no-save")" \
    "$(json_escape "--no-package-lock")" \
    "$(json_escape "$OFFICECLI_PACKAGE_SPEC")" \
    "$(json_escape "network dependency resolution")" \
    "$(json_escape "local-prefix package files under the managed target")" \
    "$(json_escape "$OFFICECLI_REASON")" \
    "$(json_escape "Rerun rose-aili install, or run the fixed local-prefix command: npm install --prefix $OFFICECLI_TARGET --no-save --no-package-lock $OFFICECLI_PACKAGE_SPEC")" \
    "$exit_code_json"
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
retired_entries = manifest.get("retiredSkills", [])
expected_retired = {
    "agents-md-initialization",
    "evidence-scoped-retrospective",
    "harness-optimization-audit",
    "local-review-gate",
    "rose-memory",
    "session-handoff",
}
if not isinstance(retired_entries, list) or len(retired_entries) != len(expected_retired):
    fail("Invalid deferred retired Skill inventory")
retired_names = set()
for entry in retired_entries:
    if not isinstance(entry, dict):
        fail("Invalid deferred retired Skill inventory")
    name = entry.get("name")
    if name not in expected_retired or name in retired_names or entry.get("path") != f".agents/skills/{name}":
        fail("Invalid deferred retired Skill inventory")
    validate_relative(f"retired Skill for {name}", entry["path"])
    retired_names.add(name)
if retired_names != expected_retired:
    fail("Invalid deferred retired Skill inventory")

skills = components.get("skills", [])
optional = {
    "academic-paper-review",
    "systematic-literature-review",
    "newsletter-generation",
    "consulting-analysis",
    "android-native-dev",
    "ios-application-dev",
    "flutter-dev",
    "react-native-dev",
    "shader-dev",
}
if len(skills) != 58 or sum(bool(entry.get("defaultInstalled")) for entry in skills) != 49:
    fail("Component manifest must contain exactly 58 Skills with 49 default-installed Core Skills")
if {entry.get("name") for entry in skills if not entry.get("defaultInstalled")} != optional:
    fail("Component manifest Optional Skill inventory is invalid")
expected_groups = {
    "research": {"academic-paper-review", "systematic-literature-review", "newsletter-generation", "consulting-analysis"},
    "specialized-dev": {"android-native-dev", "ios-application-dev", "flutter-dev", "react-native-dev", "shader-dev"},
}
for group, names in expected_groups.items():
    if {entry.get("name") for entry in skills if group in (entry.get("groups") or [])} != names:
        fail(f"Component manifest Skill group is invalid: {group}")

expected_commands = {
    "ideate", "define", "build", "ship", "local-review", "handoff", "agents-md", "harness-audit", "retro", "security-review",
}
if {entry.get("name") for entry in components.get("commands", [])} != expected_commands or len(components.get("commands", [])) != len(expected_commands):
    fail("Component manifest command inventory is invalid")

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
            targets = entry.get("installTargets") or []
            if len(targets) != 1:
                fail(f"Invalid manifest skills installTargets for {name}: expected exactly one platform owner.")
            target_kind = targets[0].get("kind")
            if target_kind == "shared":
                expected_path = f".agents/skills/{name}"
                expected_targets = [("shared", expected_path)]
            elif target_kind == "opencode":
                expected_path = f".opencode/skills/{name}"
                expected_targets = [("opencode", f"skills/{name}")]
            else:
                fail(f"Invalid manifest skills install target kind for {name}: {target_kind}")

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

def disk_skills(manifest_skill_names):
    names = []
    shared_root = home / ".agents" / "skills"
    if shared_root.is_dir():
        names.extend(path.name for path in shared_root.iterdir() if path.is_dir() and (path / "SKILL.md").is_file() and path.name not in retired_names)
    opencode_root = home / ".opencode" / "skills"
    if opencode_root.is_dir():
        names.extend(path.name for path in opencode_root.iterdir() if path.name in manifest_skill_names and path.is_dir() and (path / "SKILL.md").is_file())
    if len(names) != len(set(names)):
        fail("Duplicate repository skill entry across .agents/skills and .opencode/skills.")
    return sorted(names)

expected_by_kind = {kind: manifest_names(kind) for kind in ("agents", "commands", "skills")}
disk_by_kind = {"agents": disk_agents(), "commands": disk_commands(), "skills": disk_skills(set(expected_by_kind["skills"]))}
errors = []
for kind in ("agents", "commands", "skills"):
    expected = expected_by_kind[kind]
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

manifest_skill_entries() {
  local target_kind="$1"
  local selector
  set --
  for selector in "${SELECTED_SKILLS[@]}"; do
    set -- "$@" --skill "$selector"
  done
  for selector in "${SELECTED_SKILL_GROUPS[@]}"; do
    set -- "$@" --skill-group "$selector"
  done
  python3 - "$AILI_HOME" "$target_kind" "$@" <<'PY'
import json
import pathlib
import sys

home = pathlib.Path(sys.argv[1])
target_kind = sys.argv[2]
manifest = json.loads((home / "manifests" / "rose-aili.components.json").read_text(encoding="utf-8"))
skills = manifest.get("components", {}).get("skills", [])
by_name = {entry["name"]: entry for entry in skills}
selected = {entry["name"] for entry in skills if entry.get("defaultInstalled")}
index = 3
while index < len(sys.argv):
    flag = sys.argv[index]
    if index + 1 >= len(sys.argv):
        raise SystemExit(f"Missing value for {flag}")
    value = sys.argv[index + 1]
    index += 2
    if flag == "--skill":
        if value not in by_name:
            raise SystemExit(f"Unknown skill: {value}")
        selected.add(value)
    elif flag == "--skill-group":
        if value not in {"research", "specialized-dev"}:
            raise SystemExit(f"Unknown skill group: {value}")
        selected.update(entry["name"] for entry in skills if value in entry.get("groups", []))
    else:
        raise SystemExit(f"Unknown selector: {flag}")

for entry in skills:
    if entry["name"] not in selected:
        continue
    targets = entry.get("installTargets") or []
    if len(targets) != 1 or targets[0].get("kind") != target_kind:
        continue
    print(f"{entry.get('sourcePath') or entry['path']}\t{targets[0]['path']}")
PY
}

install_entries() {
  local action="$1"
  local skills_target_root
  skills_target_root="$(shared_skill_install_root)"
  validate_manifest_allowlist
  load_retired_skill_names
  validate_skill_selection
  if [ "$DRY_RUN" = "true" ]; then
    log "DRY RUN: would ensure shared skills directory exists: $skills_target_root"
  else
    mkdir -p "$skills_target_root"
  fi

  reconcile_retired_skill_entries "$skills_target_root"

  local source_path target_path source target
  while IFS=$'\t' read -r source_path target_path; do
    [ -n "$source_path" ] || continue
    source="$AILI_HOME/$source_path"
    target="$HOME/$target_path"
    "$action" "$source" "$target"
  done < <(manifest_skill_entries shared)

  if [ "$PROFILE" = "pi" ]; then
    install_pi_prompts "$action"
    return
  fi

  if [ "$INSTALL_OPENCODE" != "true" ]; then
    return
  fi

  if [ -e "$OPENCODE_HOME" ] && { [ -L "$OPENCODE_HOME/agents" ] || [ -L "$OPENCODE_HOME/commands" ]; }; then
    log "Refusing selective/copy mode because agents or commands is a directory-level symlink. Run --mode repair --opencode first."
    exit 2
  fi

  if [ "$DRY_RUN" = "true" ]; then
    log "DRY RUN: would ensure OpenCode directory and subdirectories exist: $OPENCODE_HOME (agents, commands, skills)"
  else
    mkdir -p "$OPENCODE_HOME/agents" "$OPENCODE_HOME/commands" "$OPENCODE_HOME/skills"
  fi

  install_global_agents "$action"

  while IFS=$'\t' read -r source_path target_path; do
    [ -n "$source_path" ] || continue
    "$action" "$AILI_HOME/$source_path" "$OPENCODE_HOME/$target_path"
  done < <(manifest_component_entries agents)

  while IFS=$'\t' read -r source_path target_path; do
    [ -n "$source_path" ] || continue
    source="$AILI_HOME/$source_path"
    target="$OPENCODE_HOME/$target_path"
    "$action" "$source" "$target"
  done < <(manifest_skill_entries opencode)

  while IFS=$'\t' read -r source_path target_path; do
    [ -n "$source_path" ] || continue
    "$action" "$AILI_HOME/$source_path" "$OPENCODE_HOME/$target_path"
  done < <(manifest_component_entries commands)
}

install_pi_prompts() {
  local action="$1"
  local source_root="$AILI_HOME/generated/pi/prompts"
  local target_root="$HOME/.pi/agent/prompts"
  local source name
  if [ ! -d "$source_root" ]; then
    log "Missing generated Pi prompt source: $source_root"
    exit 2
  fi
  if [ "$DRY_RUN" = "true" ]; then
    log "DRY RUN: would ensure Pi prompt directory exists: $target_root"
  else
    mkdir -p "$target_root"
  fi
  for source in "$source_root"/*.md; do
    [ -f "$source" ] || continue
    name="$(basename "$source")"
    "$action" "$source" "$target_root/$name"
  done
}

managed_directory() {
  local skills_target_root
  skills_target_root="$(shared_skill_install_root)"
  validate_manifest_allowlist
  load_retired_skill_names
  validate_skill_selection

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
    local source_path target_path source target
    while IFS=$'\t' read -r source_path target_path; do
      [ -n "$source_path" ] || continue
      link_entry "$AILI_HOME/$source_path" "$HOME/$target_path"
    done < <(manifest_skill_entries shared)
    while IFS=$'\t' read -r source_path target_path; do
      [ -n "$source_path" ] || continue
      link_entry "$AILI_HOME/$source_path" "$OPENCODE_HOME/$target_path"
    done < <(manifest_skill_entries opencode)
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

  mkdir -p "$OPENCODE_HOME/skills"
  local source_path target_path
  while IFS=$'\t' read -r source_path target_path; do
    [ -n "$source_path" ] || continue
    link_entry "$AILI_HOME/$source_path" "$HOME/$target_path"
  done < <(manifest_skill_entries shared)
  while IFS=$'\t' read -r source_path target_path; do
    [ -n "$source_path" ] || continue
    link_entry "$AILI_HOME/$source_path" "$OPENCODE_HOME/$target_path"
  done < <(manifest_skill_entries opencode)
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

if [ "$INSTALL_OPENCODE" = "true" ]; then
  guard_opencode_home
fi

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

OFFICECLI_RESULT=0
run_officecli_install || OFFICECLI_RESULT=$?

printf '{"mode":%s,"profile":%s,"scope":%s,"runtime":%s,"aili_home":%s,"opencode_home":%s,"dry_run":%s,"no_update":%s,"retired_skill_reconciliation":' \
  "$(json_escape "$MODE")" \
  "$(json_escape "$PROFILE")" \
  "$(json_escape "$([ "$PROFILE" = "opencode" ] && printf opencode || { [ "$PROFILE" = "pi" ] && printf pi || printf skills; })")" \
  "$(json_escape "$RUNTIME")" \
  "$(json_escape "$AILI_HOME")" \
  "$(json_escape "$OPENCODE_HOME")" \
  "$(json_escape "$DRY_RUN")" \
  "$(json_escape "$NO_UPDATE")"
retired_skill_reconciliation_json
printf ',"officecli":'
officecli_summary_json
printf '}\n'
exit "$OFFICECLI_RESULT"
