# OpenCode Setup

This document is for an AI agent installing `Rosetears520/aili-workflows` into OpenCode.

[FRAME] The omitted profile is `default`: it installs 49 Core Skills into `$HOME/.agents/skills`. `pi` adds the generated Pi global `AGENTS.md` context and top-level prompts; `opencode` adds generated OpenCode global rules, agents, Commands, and optional config integration. Pass `--profile <default|pi|opencode>`; `--opencode` is the legacy alias for `--profile opencode`.

If OpenCode runs in WSL, clone and link inside WSL. If OpenCode runs in Windows native, clone and link inside Windows. Do not mix WSL and Windows paths by default. Do not clone into the user home root.

[FRAME] OfficeCLI and MemPalace are default-selected external operations, not Skills. Install/update reports each plan, but no external command runs until its separate exact approval is represented by `--enable-officecli` or `--enable-mempalace`. `--skip-officecli` and `--skip-mempalace` decline their respective operations.

Do not replace `~/.config/opencode/agents`, `~/.config/opencode/commands`, or `$HOME/.agents/skills` by default. The installation scopes are:

- every profile: `$HOME/.agents/skills/<selected-skill> -> <repo>/.agents/skills/<selected-skill>`;
- `pi`: `~/.pi/agent/AGENTS.md -> <repo>/generated/pi/AGENTS.md` and `~/.pi/agent/prompts/<command>.md -> <repo>/generated/pi/prompts/<command>.md`; prompt installation is non-recursive and excludes Pi system/runtime metadata;
- `opencode`: `~/.config/opencode/AGENTS.md -> <repo>/generated/opencode/AGENTS.md`;
- `opencode`: `~/.config/opencode/agents/<agent>.md -> <repo>/generated/opencode/agents/<agent>.md`;
- `opencode`: `~/.config/opencode/commands/<command>.md -> <repo>/generated/opencode/commands/<command>.md`;
- separately approval-gated OfficeCLI: fixed target `$HOME/.agents/tools/officecli`, with no Skill/MCP/PATH/shell integration.

Managed directory symlink mode is only allowed when the user explicitly asks to let `aili-workflows` own the entire global `agents/` and `commands/` directories.

## Goal

Install selected reusable Skills and opt into Pi/OpenCode integration only when requested, while keeping:

- workflow source synced with this repository
- existing OpenCode global agents preserved and shared skills kept outside OpenCode home
- OpenCode global config lightweight
- reusable global AGENTS rules installed in OpenCode home
- DOCX, XLSX, and PPTX routing owned by their existing artifact Skills rather than OfficeCLI
- one user-level MemPalace mapping with distinct project Wings when memory is separately available and approved
- project `AGENTS.md` self-contained and project-specific

Never store project memory inside the global OpenCode config directory.

## Runtime Detection Gate

Before installing, determine where OpenCode is actually running.

Use WSL install paths only when OpenCode is running inside WSL.

Use Windows install paths only when OpenCode is running natively from Windows PowerShell, CMD, or a Windows terminal process.

Do not mix WSL and Windows install roots.

Detection from WSL/Linux shell:

```bash
if [ -n "${WSL_DISTRO_NAME:-}" ] || grep -qi microsoft /proc/version 2>/dev/null; then
  echo "runtime=wsl"
else
  echo "runtime=linux"
fi
```

Detection from Windows PowerShell:

```powershell
if ($env:OS -eq "Windows_NT" -and -not $env:WSL_DISTRO_NAME) {
  "runtime=windows"
}
```

## Path Policy

Do not clone this repository into the current working directory by default.

Do not clone into the user home root:

- WSL/Linux forbidden by default: `~/aili-workflows`
- Windows forbidden by default: `%USERPROFILE%\aili-workflows`

Use a stable code directory instead.

WSL/Linux default:

```bash
$AILI_HOME
```

Example WSL/Linux expansion:

```bash
/home/<user>/code/ai/aili-workflows
```

Windows native default:

```powershell
$env:USERPROFILE\code\ai\aili-workflows
```

Alternative Windows native default if the user prefers tool-local storage:

```powershell
$env:LOCALAPPDATA\aili-workflows
```

The Windows Explorer path for a WSL install is only a viewing/editing convenience:

```text
\\wsl.localhost\Ubuntu\home\<user>\code\ai\aili-workflows
```

Do not treat this as the Windows native install path.

## Install Matrix

| OpenCode runtime | Repository clone path | OpenCode config path | Link style |
|---|---|---|---|
| WSL Ubuntu | `/home/<user>/code/ai/aili-workflows` | every profile: `/home/<user>/.agents/skills`; `pi`: also `/home/<user>/.pi/agent/AGENTS.md` and `/home/<user>/.pi/agent/prompts`; `opencode`: also `/home/<user>/.config/opencode` | selected shared-skill links; Pi/OpenCode entries only under their profile; OfficeCLI is separately approval-gated |
| Linux/macOS | `$AILI_HOME` | every profile: `$HOME/.agents/skills`; `pi`: also `$HOME/.pi/agent/AGENTS.md` and `$HOME/.pi/agent/prompts`; `opencode`: also `$HOME/.config/opencode` | selected shared-skill links; Pi/OpenCode entries only under their profile; OfficeCLI is separately approval-gated |
| Windows native | `%USERPROFILE%\code\ai\aili-workflows` | every profile: `%USERPROFILE%\.agents\skills`; Pi/OpenCode integration is explicit | selected shared-skill links; platform-specific entries remain opt-in |

Do not link Windows native OpenCode config to a WSL repository by default.

Do not link WSL OpenCode config to a Windows repository under `/mnt/c` by default.

## What This Repository Provides

- `agents/rose.md` - ROSE primary agent.
- `agents/implementer.md` - focused implementation subagent.
- `agents/code-scout.md` - local code discovery subagent.
- `agents/doc-researcher.md` - local documentation discovery subagent.
- `agents/web-researcher.md` - external research subagent.
- `agents/plan-auditor.md` - read-only plan audit subagent.
- `agents/code-reviewer.md` - code review subagent.
- `agents/convergence-reviewer.md` - read-only convergence subagent.
- `agents/security-auditor.md` - security review subagent.
- `agents/test-engineer.md` - testing subagent.
- `agents/test-coverage-reviewer.md`, `agents/pr-test-analyzer.md`, `agents/ai-regression-scout.md`, and `agents/silent-failure-reviewer.md` - relevant-triggered read-only QA review/scouting subagents.
- `agents/browser-qa-runner.md` and `agents/e2e-artifact-runner.md` - relevant-triggered browser/E2E test subagents that require repository-local placement before durable screenshots, traces, videos, reports, or bundles and avoid production data mutation.
- `agents/web-performance-auditor.md` - read-only Web performance audit subagent.
- `agents/spec-miner.md`, `agents/agent-evaluator.md`, and `agents/opensource-sanitizer.md` - relevant-triggered read-only spec-mining, agent-output evaluation, and OSS/public exposure review subagents.
- `.agents/skills/*/SKILL.md` - 58 reusable shared Skill sources; `default` installs the 49 Core Skills and explicit selectors add Optional Skills.
- `.opencode/skills/*/SKILL.md` - reserved source location for manifest-declared OpenCode-only skills; these install only with `--opencode`.
- `core/commands/*.md` - canonical Command bodies. `commands/*.md` are generated OpenCode compatibility projections.
- `commands/ideate.md`, `commands/define.md`, `commands/build.md`, and `commands/ship.md` - Delivery Commands `/ideate`, `/define`, `/build`, and `/ship`.
- `commands/local-review.md`, `commands/handoff.md`, `commands/agents-md.md`, `commands/harness-audit.md`, `commands/retro.md`, and `commands/security-review.md` - Utility Commands; they do not create lifecycle phases or independent acceptance/verdict authority.
- `core/governance/mempalace.md`, `manifests/mempalace-tool.json`, and `src/mempalace.ts` - the external MemPalace provider contract, capability planning, and fail-closed resolver.
- `templates/AGENTS.md` - single source template for project-local `AGENTS.md` files.
- `templates/opencode-global-AGENTS.md` - installer-owned source for reusable global OpenCode `AGENTS.md` rules.
- `scripts/agents_md.py` - `init`, `update`, and `check` tool for generated project `AGENTS.md` files.
- `scripts/install_opencode.sh` - safe WSL/Linux fallback installer with `--profile default|pi|opencode`, repeatable Skill selectors, generated adapter installation, and separately approval-gated OfficeCLI.

Slash commands are optional entrypoints. This repository ships four Delivery Commands—`/ideate`, `/define`, `/build`, and `/ship`—mapped to generated `commands/{ideate,define,build,ship}.md` and backed by `.agents/skills/aili-delivery-flow`. It also ships six Utility Commands: `/local-review`, `/handoff`, `/agents-md`, `/harness-audit`, `/retro`, and `/security-review`. Utilities retain their action-specific gates but are not lifecycle phases or independent acceptance/verdict owners. Internal stages such as research, questionnaire, test-plan, implement, fix, debug, `/review`, and evolve are not shipped as AILI top-level commands; `/review` remains OpenCode-owned. `/aili-doctor` and `/simplify` are not AILI commands.

The canonical role inventory is primary ROSE plus 19 repository-managed subagents. ROSE runs a proactive Task-trigger scan at each non-trivial intent and changed-evidence work split; an eligible trigger dispatches promptly, while direct work is the no-trigger/blocked fallback. Default concurrency starts at two but is not a hard cap; larger model-selected fan-out requires independent non-overlapping units, concrete benefit, suitable owners, and an explicit join plan. OpenCode dispatches every Task as a fresh terminal context with no old-`task_id` resumption. A persistent adapter may continue only unchanged same-package work; changed role, scope, permissions, acceptance, write scope, expected result, or evidence requires a new package. Empty, partial, failed, or blocked results never authorize automatic retry. All 19 managed profiles remain non-delegating and retain `external_directory: deny`; only ROSE has per-operation external-directory ask and lifecycle/integration/final-verdict authority. `web-researcher` remains the web-only research role: its web capability does not grant external local-directory, mutation, or delegation access. Built-in `explore` and `general` are outside this managed inventory.

## Profile and Skill Selection

`default`, `pi`, and `opencode` are additive over the same 49 Core Skills. The nine Optional Skills are `academic-paper-review`, `systematic-literature-review`, `newsletter-generation`, `consulting-analysis`, `android-native-dev`, `ios-application-dev`, `flutter-dev`, `react-native-dev`, and `shader-dev`. `research` and `specialized-dev` are convenience aliases for Optional Skill groups.

`--skill <name>` and `--skill-group <research|specialized-dev>` are repeatable. Repeated selectors compose and deduplicate; a single Skill never expands to its group. Unknown values fail closed before mutation. `doctor` accepts the same profile and selector flags and reports the matching installation requirements, generated drift, unavailable capabilities, and external-tool status without repairing anything.

```bash
npx -y rose-aili install --profile default
npx -y rose-aili install --profile pi
npx -y rose-aili install --profile opencode
npx -y rose-aili install --profile default --skill academic-paper-review --skill-group specialized-dev
npx -y rose-aili doctor --profile pi --skill systematic-literature-review
```

## Installation Decision Rule

[FRAME] Use `rose-aili install` for the default 49 Core Skills. Use `--profile pi` for the generated Pi global context and prompts or `--profile opencode` for repository-managed global AGENTS rules, agents, Commands, and optional OpenCode JSON/JSONC config. External OfficeCLI/MemPalace planning is reported separately; only a separately approved `--enable-officecli` or `--enable-mempalace` runs that external operation. A normal git clone uses selective symlinks; a packaged/non-git npm or npx source uses copied files so installed entries do not point at a transient package cache.

```bash
npx -y rose-aili install
npx -y rose-aili install --profile pi
npx -y rose-aili install --profile opencode
```

For `--profile pi`, a normal Git checkout installs managed links while a packaged npm/npx source installs copies so targets do not point into a transient cache. Before replacing a non-managed `~/.pi/agent/AGENTS.md` regular file, valid symlink, or broken symlink, install/update creates a timestamped recoverable backup; repeat runs are idempotent. `--dry-run` reports the planned backup/replacement without mutation. `rose-aili doctor --profile pi` reports missing or drifted generated context, installed context, prompts, and package-only runtime metadata without repairing them. After install or update, restart Pi or open a new Pi session so the global context and prompt inventory are reloaded.

Before npm publishing, use the GitHub package-spec form from the repository URL:

```bash
npx -y --package github:<owner>/<repo> rose-aili install
```

Use these non-interactive flags for AI-agent or scripted setup:

```bash
npx -y rose-aili install --yes
npx -y rose-aili install --dry-run
npx -y rose-aili install --profile pi
npx -y rose-aili install --profile default --skill academic-paper-review --skill-group research
npx -y rose-aili install --enable-officecli
npx -y rose-aili install --enable-mempalace
npx -y rose-aili install --skip-officecli
npx -y rose-aili install --profile opencode --yes --model anthropic/claude-sonnet-4-5
npx -y rose-aili install --profile opencode --set-default-rose
npx -y rose-aili install --profile opencode --skip-opencode-config
npx -y rose-aili install --profile opencode --enable-playwright
npx -y rose-aili install --profile opencode --enable-codegraph
npx -y rose-aili install --profile opencode --enable-openspec --project-root <absolute-canonical-path>
npx -y rose-aili install --profile opencode --skip-openspec
npx -y rose-aili update --profile opencode --skip-openspec
npx -y rose-aili update --skip-officecli
npx -y rose-aili doctor
npx -y rose-aili update
```

[FRAME] OfficeCLI and MemPalace are default-selected plans, but their external execution is opt-in and separately approved. OpenCode config sync remains disabled outside the `opencode` profile. Within that profile, the existing preserve/conflict behavior remains, and Playwright, CodeGraph, Graphify, and OpenSpec retain their separate explicit flags. OpenCode-specific flags fail closed outside the `opencode` profile.

### Managed OfficeCLI Tool

[FRAME] OfficeCLI is an installer-managed, non-routable external tool, not a Skill, MCP, public command, PATH entry, or shell integration. An enabled OfficeCLI operation detects the fixed managed shim first. An exact current version is preserved without npm; a missing or drifted version uses the fixed local-prefix package contract from `manifests/officecli-tool.json`. Without `--enable-officecli`, the summary records the planned operation and no probe or install command runs. OfficeCLI failure returns nonzero without rolling back already-synced Skills.

[FRAME] `--skip-officecli` performs no OfficeCLI probe, target creation, or npm command. `--dry-run` reports the exact target, package, argv, and network/dependency effects without creating the target or running an executable. Neither flag installs an OfficeCLI Skill, MCP, public command, PATH entry, shell integration, or package full installer.

[UNVERIFIED] Fake/temp repository checks do not prove a real npm/native install, DOCX/XLSX/PPTX rendering, complex Word/workbook round-trip, or cross-viewer fidelity. Do not report those outcomes as verified after setup alone.

[KNOWN] Interactive `install` / `update` without `--opencode` performs no OpenCode prompts. Interactive `install --opencode` asks about the default agent, model, Playwright, CodeGraph, Graphify, and OpenSpec; `update --opencode` asks about CodeGraph and Graphify.

AILI has no active DCP integration. `install`, `update`, and `doctor` do not install, detect, configure, report, migrate, or remove a third-party DCP plugin and do not read or mutate user `dcp.json`/`dcp.jsonc`. Former DCP flags are ordinary unknown options. Historical DCP evidence may remain in archived ideas, accepted-change history, or negative fixtures, but it is not setup/runtime authority.

### Retired Skill Reconciliation

`local-review-gate`, `session-handoff`, `agents-md-initialization`, `harness-optimization-audit`, `evidence-scoped-retrospective`, and `rose-memory` are no longer runnable, catalogued, capability-assigned, or default-installed Skills. Fresh install and doctor requirements come from the current component manifest and omit them.

An explicit `install` or `update --reconcile-retired-skills`, including `--dry-run`, checks only those six exact destinations under `$HOME/.agents/skills`. The installer proves managed ownership only when the destination is a symlink whose resolved target exactly equals `<AILI_HOME>/.agents/skills/<retired-name>`. A proven link is reported and unlinked (or reported as a planned unlink in dry-run). A copied directory, ordinary file, unreadable/modified symlink, different target, or any other ambiguous entry is preserved and reported; the installer never removes a sibling, parent directory, backup, legacy memory data, or user file. The CLI exposes the per-name result under `componentInstall.retiredSkillReconciliation`. Doctor adds no stale-copy result field.

Do not manually delete an ambiguous retired-name entry. Review it separately and decide whether it is user content. Rolling back to a prior repository/package version may reinstall that version's managed catalog through the normal installer, but cannot reconstruct user-owned content from guesses.

CodeGraph opt-in is explicit: `rose-aili install --opencode --enable-codegraph` runs `npm install -g @colbymchenry/codegraph@latest`, then delegates `codegraph install --target=opencode --yes`.

Project-local CodeGraph initialization is separate from global install/update. An AI agent should confirm the current repository root before running `codegraph init -i` and `codegraph status` for that repository only. For an A33 host and its declared attachments, confirm root, readiness, and any init approval separately per target; one repository's CodeGraph result never covers another. It must not run `openspec init` as part of CodeGraph initialization, and it must not initialize multiple repositories without explicit approval for each exact target.

Project `AGENTS.md` initialization/update should also check CodeGraph readiness for the same repository. After generating or updating `AGENTS.md`, run or request `codegraph status`; if the repository is not initialized, ask whether to run `codegraph init -i`, then rerun `codegraph status` when approved. If CodeGraph is unavailable, skipped, or not approved, keep the `AGENTS.md` flow non-blocking but report that the project has no CodeGraph code-map coverage yet.

OpenSpec is explicit opt-in under OpenCode scope. `--opencode --enable-openspec --project-root <absolute-canonical-path>` retains the existing Node, detection, install, and project `init/update` gates.

User preferences belong in OpenCode runtime config, not in symlinked upstream agent Markdown:

```jsonc
{
  "default_agent": "rose",
  "agent": {
    "rose": {
      "model": "anthropic/claude-sonnet-4-5"
    }
  },
  "mcp": {
    "playwright": {
      "type": "local",
      "command": ["npx", "-y", "@playwright/mcp@0.0.75", "--caps=testing,storage"],
      "enabled": true
    }
  }
}
```

Use Selective Symlink Setup by default when falling back to the Bash script.

Choose Selective Symlink Setup when:

- `~/.config/opencode/agents` already exists
- the user has existing agents or skills
- the user says "soft link into opencode", "add this workflow", or "keep synced with repo"

Do not choose Managed Directory Symlink Setup unless the user explicitly says:

- replace the whole global agents directory
- let `aili-workflows` own the entire OpenCode agents/commands config

If unsure, use Selective Symlink Setup.

## Destructive-Config Guard

Do not delete, replace without backup, or convert these paths into directory symlinks unless explicitly approved by the user:

- `~/.config/opencode/agents`
- `~/.config/opencode/commands`
- `$HOME/.agents/skills`
- `~/.config/opencode/AGENTS.md`
- OpenCode runtime configuration files

Back up individual conflicting entries only.

Allowed by default:

- back up `~/.config/opencode/agents/rose.md` if it is a real file and conflicts with the new symlink
- back up `~/.config/opencode/commands/ideate.md` if it is a real file and conflicts with the new symlink
- back up `~/.config/opencode/AGENTS.md` if it is a real file and conflicts with the installer-owned global AGENTS file

Not allowed by default:

- moving the whole `agents/` directory
- moving the whole shared `$HOME/.agents/skills/` directory
- moving the whole `commands/` directory
- replacing the whole directory with a symlink

## Installation Modes

Choose one mode after the Runtime Detection Gate.

### Mode A: Selective Symlink Setup (Default)

Use this by default. The `default` profile links selected shared Skills into `$HOME/.agents/skills` and leaves OpenCode home untouched. `--profile pi` additionally installs the generated Pi global `AGENTS.md` context and top-level prompts; `--profile opencode` additionally preserves OpenCode's existing global directories and links individual managed entries. OfficeCLI runs only with its separately approved `--enable-officecli` flag.

WSL/Linux recommended command:

```bash
scripts/install_opencode.sh --mode selective
scripts/install_opencode.sh --mode selective --skip-officecli
scripts/install_opencode.sh --mode selective --opencode
```

The full OpenCode entry-linking logic below corresponds only to the component portion of the `opencode` profile. It does not implement OfficeCLI, MemPalace, exact retired-skill ownership reconciliation, or structured failure reporting; use the CLI or installer script rather than hand-rolling those steps.

```bash
: "${AILI_HOME:?Set AILI_HOME to the runtime-local aili-workflows clone}"
OPENCODE_HOME="${OPENCODE_HOME:-$HOME/.config/opencode}"

mkdir -p "$(dirname "$AILI_HOME")"
git clone https://github.com/Rosetears520/aili-workflows.git "$AILI_HOME" 2>/dev/null || git -C "$AILI_HOME" pull --ff-only

mkdir -p "$OPENCODE_HOME/agents" "$OPENCODE_HOME/commands" "$HOME/.agents/skills"

global_agents_target="$OPENCODE_HOME/AGENTS.md"
if [ -e "$global_agents_target" ] && [ ! -L "$global_agents_target" ]; then
  mv "$global_agents_target" "$global_agents_target.backup.$(date +%Y%m%d%H%M%S)"
fi
ln -sfn "$AILI_HOME/templates/opencode-global-AGENTS.md" "$global_agents_target"

for file in "$AILI_HOME"/agents/*.md; do
  name="$(basename "$file")"
  target="$OPENCODE_HOME/agents/$name"

  if [ -e "$target" ] && [ ! -L "$target" ]; then
    mv "$target" "$target.backup.$(date +%Y%m%d%H%M%S)"
  fi

  ln -sfn "$file" "$target"
done

for dir in "$AILI_HOME"/.agents/skills/*; do
  [ -d "$dir" ] || continue
  [ -f "$dir/SKILL.md" ] || continue
  name="$(basename "$dir")"
  target="$HOME/.agents/skills/$name"

  if [ -e "$target" ] && [ ! -L "$target" ]; then
    mv "$target" "$target.backup.$(date +%Y%m%d%H%M%S)"
  fi

  ln -sfn "$dir" "$target"
done

for file in "$AILI_HOME"/commands/*.md; do
  name="$(basename "$file")"
  target="$OPENCODE_HOME/commands/$name"

  if [ -e "$target" ] && [ ! -L "$target" ]; then
    mv "$target" "$target.backup.$(date +%Y%m%d%H%M%S)"
  fi

  ln -sfn "$file" "$target"
done
```

Result examples:

```text
~/.config/opencode/agents/
  rose_old.md
  rose.md -> $AILI_HOME/agents/rose.md
  implementer.md -> $AILI_HOME/agents/implementer.md

~/.config/opencode/AGENTS.md -> $AILI_HOME/templates/opencode-global-AGENTS.md

$HOME/.agents/skills/
  <selected shared Skills only>

~/.config/opencode/commands/
  ideate.md -> $AILI_HOME/commands/ideate.md
  define.md -> $AILI_HOME/commands/define.md
  build.md -> $AILI_HOME/commands/build.md
  ship.md -> $AILI_HOME/commands/ship.md
  local-review.md -> $AILI_HOME/commands/local-review.md
```

### Mode B: Managed Directory Symlink Setup (Exclusive / Advanced)

This is a dangerous exclusive mode. It replaces OpenCode's whole global `agents/` and `commands/` directories with directory-level symlinks. Skills still install as entries under `$HOME/.agents/skills`.

Do not use this mode unless the user explicitly says `aili-workflows` may replace the entire global `agents/` and `commands/` directories.

WSL/Linux command with explicit confirmation:

```bash
CONFIRM_MANAGED_DIRECTORY=yes scripts/install_opencode.sh --mode managed-directory --opencode
```

Manual logic, only after explicit approval:

```bash
: "${AILI_HOME:?Set AILI_HOME to the runtime-local aili-workflows clone}"
OPENCODE_HOME="${OPENCODE_HOME:-$HOME/.config/opencode}"

mkdir -p "$(dirname "$AILI_HOME")" "$OPENCODE_HOME" "$HOME/.agents/skills"
git clone https://github.com/Rosetears520/aili-workflows.git "$AILI_HOME" 2>/dev/null || git -C "$AILI_HOME" pull --ff-only

if [ -e "$OPENCODE_HOME/agents" ] && [ ! -L "$OPENCODE_HOME/agents" ]; then
  mv "$OPENCODE_HOME/agents" "$OPENCODE_HOME/agents.backup.$(date +%Y%m%d%H%M%S)"
fi

if [ -e "$OPENCODE_HOME/commands" ] && [ ! -L "$OPENCODE_HOME/commands" ]; then
  mv "$OPENCODE_HOME/commands" "$OPENCODE_HOME/commands.backup.$(date +%Y%m%d%H%M%S)"
fi

if [ -e "$OPENCODE_HOME/AGENTS.md" ] && [ ! -L "$OPENCODE_HOME/AGENTS.md" ]; then
  mv "$OPENCODE_HOME/AGENTS.md" "$OPENCODE_HOME/AGENTS.md.backup.$(date +%Y%m%d%H%M%S)"
fi

ln -sfn "$AILI_HOME/agents" "$OPENCODE_HOME/agents"
ln -sfn "$AILI_HOME/commands" "$OPENCODE_HOME/commands"
ln -sfn "$AILI_HOME/templates/opencode-global-AGENTS.md" "$OPENCODE_HOME/AGENTS.md"

for dir in "$AILI_HOME"/.agents/skills/*; do
  [ -d "$dir" ] || continue
  [ -f "$dir/SKILL.md" ] || continue
  name="$(basename "$dir")"
  ln -sfn "$dir" "$HOME/.agents/skills/$name"
done
```

### Mode C: Copy Fallback

Use copy mode only when symlinks are unavailable, blocked by permissions, or explicitly requested.

Copy mode does not auto-sync with future repository updates.

WSL/Linux command:

```bash
scripts/install_opencode.sh --mode copy
scripts/install_opencode.sh --mode copy --opencode
```

The manual logic below represents the full `--opencode` copy scope:

```bash
: "${AILI_HOME:?Set AILI_HOME to the runtime-local aili-workflows clone}"
OPENCODE_HOME="${OPENCODE_HOME:-$HOME/.config/opencode}"

mkdir -p "$(dirname "$AILI_HOME")"
git clone https://github.com/Rosetears520/aili-workflows.git "$AILI_HOME" 2>/dev/null || git -C "$AILI_HOME" pull --ff-only

mkdir -p "$OPENCODE_HOME/agents" "$OPENCODE_HOME/commands" "$HOME/.agents/skills"

if [ -e "$OPENCODE_HOME/AGENTS.md" ] && [ ! -L "$OPENCODE_HOME/AGENTS.md" ]; then
  mv "$OPENCODE_HOME/AGENTS.md" "$OPENCODE_HOME/AGENTS.md.backup.$(date +%Y%m%d%H%M%S)"
fi

cp -R "$AILI_HOME/agents/"*.md "$OPENCODE_HOME/agents/"
cp -R "$AILI_HOME/.agents/skills/"* "$HOME/.agents/skills/"
cp -R "$AILI_HOME/commands/"*.md "$OPENCODE_HOME/commands/"
cp -R "$AILI_HOME/templates/opencode-global-AGENTS.md" "$OPENCODE_HOME/AGENTS.md"
```

## Windows Native Selective Symlink Setup

Use this only when OpenCode is running natively in Windows and the user requested the equivalent of `--opencode`. A skills-only Windows install writes only `%USERPROFILE%\.agents\skills`.

Do not reuse WSL paths from Windows native OpenCode.

PowerShell:

```powershell
$AiliHome = Join-Path $env:USERPROFILE "code\ai\aili-workflows"
$OpenCodeHome = Join-Path $env:USERPROFILE ".config\opencode"

New-Item -ItemType Directory -Force -Path (Split-Path $AiliHome) | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $OpenCodeHome "agents") | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $OpenCodeHome "commands") | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $env:USERPROFILE ".agents\skills") | Out-Null

if (!(Test-Path $AiliHome)) {
  git clone https://github.com/Rosetears520/aili-workflows.git $AiliHome
} else {
  git -C $AiliHome pull --ff-only
}

$GlobalAgentsTarget = Join-Path $OpenCodeHome "AGENTS.md"
if ((Test-Path $GlobalAgentsTarget) -and -not ((Get-Item $GlobalAgentsTarget).Attributes -band [IO.FileAttributes]::ReparsePoint)) {
  Rename-Item $GlobalAgentsTarget "$($GlobalAgentsTarget).backup.$(Get-Date -Format yyyyMMddHHmmss)"
}
if (Test-Path $GlobalAgentsTarget) {
  Remove-Item $GlobalAgentsTarget -Force
}
New-Item -ItemType SymbolicLink -Path $GlobalAgentsTarget -Target (Join-Path $AiliHome "templates\opencode-global-AGENTS.md") | Out-Null

Get-ChildItem "$AiliHome\agents" -Filter "*.md" | ForEach-Object {
  $Target = Join-Path "$OpenCodeHome\agents" $_.Name

  if ((Test-Path $Target) -and -not ((Get-Item $Target).Attributes -band [IO.FileAttributes]::ReparsePoint)) {
    Rename-Item $Target "$($Target).backup.$(Get-Date -Format yyyyMMddHHmmss)"
  }

  if (Test-Path $Target) {
    Remove-Item $Target -Force
  }

  New-Item -ItemType SymbolicLink -Path $Target -Target $_.FullName | Out-Null
}

Get-ChildItem "$AiliHome\.agents\skills" -Directory | ForEach-Object {
  $Target = Join-Path (Join-Path $env:USERPROFILE ".agents\skills") $_.Name

  if ((Test-Path $Target) -and -not ((Get-Item $Target).Attributes -band [IO.FileAttributes]::ReparsePoint)) {
    Rename-Item $Target "$($Target).backup.$(Get-Date -Format yyyyMMddHHmmss)"
  }

  if (Test-Path $Target) {
    Remove-Item $Target -Force
  }

  New-Item -ItemType SymbolicLink -Path $Target -Target $_.FullName | Out-Null
}

Get-ChildItem "$AiliHome\commands" -Filter "*.md" | ForEach-Object {
  $Target = Join-Path "$OpenCodeHome\commands" $_.Name

  if ((Test-Path $Target) -and -not ((Get-Item $Target).Attributes -band [IO.FileAttributes]::ReparsePoint)) {
    Rename-Item $Target "$($Target).backup.$(Get-Date -Format yyyyMMddHHmmss)"
  }

  if (Test-Path $Target) {
    Remove-Item $Target -Force
  }

  New-Item -ItemType SymbolicLink -Path $Target -Target $_.FullName | Out-Null
}
```

If Windows symbolic link permissions are blocked, use copy fallback for command files or junctions for skill directories, but keep the same rule: create skills under `%USERPROFILE%\.agents\skills` and commands under OpenCode `commands\`, do not replace whole directories.

## Cross-Environment Guard

Do not install WSL OpenCode into Windows paths.

Forbidden from WSL unless explicitly requested:

```bash
/mnt/c/Users/<user>/aili-workflows
/mnt/c/Users/<user>/.config/opencode
```

Do not install Windows native OpenCode into WSL paths.

Forbidden from Windows native unless explicitly requested:

```text
\\wsl.localhost\Ubuntu\home\<user>\code\ai\aili-workflows
\\wsl.localhost\Ubuntu\home\<user>\.config\opencode
```

If both WSL OpenCode and Windows native OpenCode are used, install twice:

- one WSL clone under `/home/<user>/code/ai/aili-workflows`
- one Windows clone under `%USERPROFILE%\code\ai\aili-workflows`

Each runtime owns its own `~/.config/opencode`.

## A33 Attached Repository Boundary

Cross-repository AILI work starts only from the user-selected Git repository where OpenCode was started. The current `WT-001` mode is `a33-attached-shared-trust-domain`; historical `a30-a31-external-read`, A30 runtime results, and A32/item-41 readiness evidence are non-gating history. AILI supplies no host selector, attachment command, cleanup manager, registry, or additional manifest.

Each declared attachment is admitted only at exact `<session-root>/.worktrees/<repo_key>/<worktree_key>`. Both keys must match `^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$`, be non-reserved and collision-free, and the prospective target must pass exact root `/.worktrees/` ignore with no re-inclusion, no tracked destination, and trusted non-submodule/path topology. Visible `worktrees/` and historical `.tmp/worktrees/` are not aliases. The npm `package.json#files` allowlist excludes all three worktree roots.

Multiple attachments are allowed only as separate repository lanes. Each lane keeps its own current WT reference, exact keys, target rules, owning-repository artifact paths, operation approval, and no-digest `A33Identity` pre/post evidence with all and only these fields: `identity_state`, `declared_root`, `path_state`, `canonical_root`, `git_toplevel`, `git_private_dir`, `git_common_dir`, `git_head`, `git_branch`, `detached_head`, `worktree_membership`, `dirty_state`, `tracked_files`, `untracked_files`, `ignored_files`, `artifact_files`, and `unknown_files`. No attachment may reuse or rebind another attachment's identity, rules, approval, Git state, CodeGraph evidence, or artifact destination.

PREPARE is descriptor-only. Every real or driver-fixture ADD requires a fresh exact key/class-bound approval and accepted trusted-code risk; every later non-force REMOVE requires a different fresh exact approval after complete deletion inventory and its own risk gate. REMOVE preserves branch ref/reflog, and rollback preserves worktrees and evidence. Add/remove approval grants no test, debug, verification, integration, cleanup, commit, push, merge, release, or other-operation authority.

The host and all attachments must be an explicitly trusted same-owner, same-sensitivity, mutually readable/writable trust domain. OpenCode path/cwd/permission rules are a soft coordination boundary, not hard isolation or an OS sandbox. Target `AGENTS.md` and applicable rules are re-read per operation/dispatch, may only narrow authority, and block on same-level conflict. User-visible artifacts stay in the owning target repository.

## Repair: Restore Directory-Level Symlink Mistake

Use this only if `~/.config/opencode/agents`, legacy `~/.config/opencode/skills`, or `~/.config/opencode/commands` was accidentally replaced by a directory-level symlink.

```bash
OPENCODE_HOME="${OPENCODE_HOME:-$HOME/.config/opencode}"

if [ -L "$OPENCODE_HOME/agents" ]; then
  unlink "$OPENCODE_HOME/agents"
fi

if [ -L "$OPENCODE_HOME/skills" ]; then
  unlink "$OPENCODE_HOME/skills"
fi

latest_agents_backup="$(ls -dt "$OPENCODE_HOME"/agents.backup.* 2>/dev/null | head -n 1)"
latest_skills_backup="$(ls -dt "$OPENCODE_HOME"/skills.backup.* 2>/dev/null | head -n 1)"

if [ -n "$latest_agents_backup" ] && [ ! -e "$OPENCODE_HOME/agents" ]; then
  mv "$latest_agents_backup" "$OPENCODE_HOME/agents"
fi

if [ -n "$latest_skills_backup" ] && [ ! -e "$OPENCODE_HOME/skills" ]; then
  mv "$latest_skills_backup" "$OPENCODE_HOME/skills"
fi
```

Then rerun Mode A selective setup.

## Project AGENTS.md Rule

`~/.config/opencode/AGENTS.md` is the global reusable rule file installed from `templates/opencode-global-AGENTS.md`.

Do not symlink this repository's `AGENTS.md` into each target project's root by default.

Project `AGENTS.md` files must be generated from this repository's slim `templates/AGENTS.md`, then filled with project-specific commands, facts, artifact locations, and local exceptions, and committed to that project.

The project template is intentionally small. Reusable safety, git, verification, dependency, documentation, and workflow discipline belongs in the global `AGENTS.md` installed from `templates/opencode-global-AGENTS.md`.

Use symlinks for reusable global ROSE agents and skills. Use project-local generated files for project-specific instructions.

Use the `/agents-md` Utility Command for this flow. It should call the script instead of writing `AGENTS.md` by hand:

```bash
AILI_HOME="/absolute/path/to/aili-workflows"

python "$AILI_HOME/scripts/agents_md.py" init --project .
python "$AILI_HOME/scripts/agents_md.py" check --project .
```

Set `AILI_HOME` to the clone that matches the runtime where OpenCode is running; do not default to a fixed home-directory path.

If a target project already has `AGENTS.md`, do not overwrite it silently. Use managed-block update or explicitly back up before overwrite:

```bash
python "$AILI_HOME/scripts/agents_md.py" update --project .
python "$AILI_HOME/scripts/agents_md.py" init --project . --strategy backup-overwrite
```

Recommended target-project CI/pre-commit gate:

```bash
python "$AILI_HOME/scripts/agents_md.py" check --project .
```

## Recommended OpenCode Runtime Add-ons

Recommended opt-in runtime add-ons are Playwright MCP, OpenSpec, CodeGraph, the official global Graphify skill, and Context7 integration. Fully restart OpenCode after installing plugins, MCP servers, Context7, or changing OpenCode runtime configuration.

### OpenSpec

OpenSpec is installed/configured only when explicitly enabled:

```bash
rose-aili install --opencode --enable-openspec --project-root <absolute-canonical-path>
```

The delegated command path is:

```bash
npm install -g @fission-ai/openspec@latest
openspec init    # first-time project setup
openspec update  # existing OpenSpec project refresh
```

Requires Node.js `20.19.0+`. `rose-aili` detects existing OpenSpec project markers and chooses `openspec update`; otherwise it chooses `openspec init` in the current project directory. Optional expanded workflow selection remains manual:

```bash
openspec config profile
openspec update
```

### Playwright MCP

Start interactive setup:

```bash
opencode mcp add
```

Use these answers/details:

- name: `playwright`
- type: `local`
- command: `npx -y @playwright/mcp@0.0.75 --caps=testing,storage`
- default caps: `testing,storage`

Optional profiles:

- trace/debug: `npx -y @playwright/mcp@0.0.75 --caps=devtools`
- full automation only when explicitly needed: `npx -y @playwright/mcp@0.0.75 --caps=network,storage,testing,vision,pdf,devtools`

Verify after restart with `opencode mcp list`, then ask `test-engineer` or `browser-testing-with-devtools` to use Playwright for a simple local page check.

### Context7 Integration

```bash
npx ctx7 setup --opencode
```

Choose CLI mode or MCP mode based on the environment. Do not vendor a Context7 skill; official setup installs or configures an external capability used by `source-driven-development`. The recommended default is the installed Context7 CLI unless a project explicitly needs MCP tools.

Verify after restart by asking ROSE or `source-driven-development` to use Context7 for a library documentation lookup.

### Optional Add-ons

Install these only if the user asks or the project clearly needs them: notifier/notificator, vibeguard, Sentry MCP, Grep by Vercel/`gh_grep`, `opencode-worktree`, and `opencode-pty`/shell-strategy.

Not recommended as default add-ons: GitHub MCP, Filesystem MCP, Puppeteer/Chrome DevTools MCP, Memory MCP/Supermemory, and Sequential Thinking MCP.

## OpenCode Behavior

This repository follows an agent-driven model similar to `addyosmani/agent-skills`:

- Skills are selected automatically by intent.
- `AGENTS.md` or the active primary agent should require skill usage when a skill applies.
- Exactly four optional delivery shortcuts—`/ideate`, `/define`, `/build`, and `/ship`—provide thin entrypoints to `.agents/skills/aili-delivery-flow`; equivalent natural-language intent uses the same classifier, gates, and evidence rules. `/local-review` is a standalone report-first local audit entrypoint, not a delivery mode. No loop/schedule/goal/proactive/cycle/watch/objective/worktree-maintenance/Graphify shortcut and no internal-stage AILI `/review` command is shipped.
- The user can work naturally: "implement this", "fix this bug", "review this", "plan this change".

AILI provides no cron, scheduler, watcher, webhook, listener, daemon, persistent queue, hook, dependency, or auto-retry runtime for the four outer profiles. `turn` and `objective` are bounded executable profiles inside the existing lifecycle; `interval` and `event` are protocol/runbook descriptions for external/manual triggering only.

## Source, Adapter, and Distribution Boundaries

- Canonical AILI source is `core/commands/` for four Delivery and six Utility Commands, `core/protocols/` for versioned shared schemas, shared `.agents/skills`, canonical governance/roles, adapters, manifests, TypeScript, and installer sources. Root `agents/`, `commands/`, and `templates/opencode-global-AGENTS.md` are generated compatibility projections, not independent semantic owners.
- Root `AGENTS.md`, `dist/`, `generated/`, installed Pi/OpenCode files, and installed shared Skills are generated or installed downstream outputs. Change their canonical source/generator instead of hand-editing them.
- Current generated `.opencode/commands/opsx-*` and `.opencode/skills/openspec-*` direct adapters are OpenSpec-owned ignored outputs, not repository-managed OpenCode-only skills. They remain outside AILI guarantees and are not installed by `--opencode` unless a future accepted manifest change explicitly promotes a distinct canonical component.
- Pinned upstream files under canonical skill `references/upstream/` are inert licensed data, not another installed skill or runtime. They use `SKILL.upstream.md`; upstream scripts must remain non-executable data and must never become commands, hooks, or routing targets.
- `package.json#files` ships built CLI, `core/`, `adapters/`, `generated/`, compatibility projections, `.agents/`, manifests, both AGENTS templates, required helpers/fixtures, and README/setup docs. A future manifest-declared `.opencode/skills/<name>` component must add that exact canonical source to the package allowlist; the package must not broadly include ignored/generated `.opencode` state.

The upstream distribution path is currently fail-closed. OpenCode `1.17.18` installed-catalog recursion remains `UV-005`, and filesystem mode evidence may not prove required upstream `0644` modes; until both are resolved, do not claim distribution/registration/enablement or release readiness. `npm pack --dry-run` is content evidence only and does not publish or resolve runtime catalog/mode behavior.

Cross-root delegation also fails closed against exact OpenCode `1.17.18` behavior. Root approval is not process containment: if ask/always/`--auto`, Task-root inheritance, symlink/TOCTOU, subprocess, bash-effect, secret, or neighboring-root behavior cannot be safely expressed and freshly proven, do not dispatch or mutate across roots; retain the runtime result as `Unverified`.

Graphify CLI installation, global agents-skill registration, and every project-level Graphify operation remain separate. Each real operation requires its own fresh exact approval; installer or lifecycle acceptance never authorizes a later stage. Graphify output is optional architecture-navigation evidence, never contract, current-code, completion, or release authority.

### Official Graphify CLI and Global Skill

Use only the official two-stage flow. `uv` must already exist; AILI does not bootstrap uv, Python, a system package manager, pip/pipx, or a source build.

```bash
rose-aili install --opencode --enable-graphify
# delegated official command: uv tool install graphifyy

# Run later in a different invocation after a different exact approval:
rose-aili install --opencode --register-graphify-skill
# delegated official command: graphify install --platform agents
```

`--enable-graphify` and `--register-graphify-skill` are mutually exclusive. `--skip-graphify` explicitly declines both, and `--yes`, CodeGraph consent, lifecycle acceptance, or first-stage approval does not imply either Graphify stage. Use `--dry-run` with one stage flag to inspect the exact command, effects, refusal result, candidate global-skill targets, and current-project `.opencode` target without running uv or Graphify. A real stage first performs read-only `uv --version`, uv tool-directory/list, `graphify --version`, and global-skill inventory checks; an unavailable prerequisite or ownership conflict blocks without fallback.

The registration target is the upstream-owned `$HOME/.agents/skills/graphify/`. Verification checks regular `SKILL.md` and `.graphify_version`, packaged references when the upstream command reports them, exactly one OpenCode catalog route, and an unchanged current-project `.opencode` tree. It does not install a project `.opencode` plugin/config, invoke `/graphify`, or build/update/query a repository graph. `rose-aili doctor` reports `graphifyCli` and `graphifyGlobalSkill` separately with observed upstream version/path state.

Use an already installed official Graphify skill only for one scoped architecture-orientation result when a usable upstream graph exists. Use CodeGraph or current files for exact symbols, source, call paths, tests, and current impact. Treat upgrade, reinstall, unregistration, removal, and every project graph operation as new exact operations.

### Repository-Local Handoffs

The `/handoff` Utility Command supports explicit CREATE, LIST, and RESUME. OpenSpec changes use `openspec/changes/<change-id>/handoffs/`; ordinary tasks use one confirmed repository-local `<task-root>/handoffs/`. Legacy `<task-root>/handoff.md` remains an explicitly selected read-only input.

The Utility Command preserves a redacted, immutable, reference-first snapshot rather than creating a new workflow. Finalized snapshots are not automatically edited, migrated, archived, or pruned; a correction creates a new `continues_from` snapshot.

Do not create a handoff because of context pressure, compression, phase completion, a timer, or a hook. Do not promote it into memory. On RESUME, revalidate the current root, worktree, branch/HEAD, dirty state, permissions, contracts, attachments, and affected evidence before continuing.

Typical intent mapping selects one primary loop rather than a default skill chain:

- Explicit specification or a named material contract gap: `spec-driven-development`.
- Explicit task/package planning: `planning-and-task-breakdown`.
- Accepted implementation that benefits from coherent slices: `incremental-implementation`; ROSE separately selects `test-driven-development` only for explicit TDD, accepted reproduction-first proof, or a named high-risk red/green need.
- One concrete build, typecheck, lint, test, packaging, or CI failure: `build-failure-repair`.
- Explicit bounded review: `code-review-and-quality`.
- App UI as the primary deliverable: `frontend-ui-engineering`.
- Durable-memory request: MemPalace provider planning; no local memory Skill is routed.

## MemPalace Planning

MemPalace is an external provider, not a project-local SQLite store or installed Skill. `rose-aili install` reports the exact default-selected install plan `uv tool install mempalace==3.6.0`; installation, MCP configuration, initialization, model download, mining, hooks, reads, writes, coordination/logstream writes, and deletion require independent exact approvals.

The canonical Palace path resolves to `$AILI_MEMPALACE_PALACE_PATH` when set, otherwise `$HOME/.mempalace/aili-palace`. Resolution and planning do not create either path or a repository-local Palace. Project Wings, the `shared` Wing, and stable-Agent diaries are deterministic mappings inside that one Palace.

Required memory work fails closed if MemPalace is absent, Python or exact provider version is incompatible, supported MCP configuration is absent, or another supported client may write concurrently. Concurrent-write safety remains `Unverified`; there is no SQLite or `rose-memory` fallback. Legacy user data remains untouched. A one-time repository-scoped migration prompt may be presented, but no data is read, migrated, rewritten, or deleted automatically.

## Security Review Planning

`/security-review` is a report-only Utility Command, not a scan authorization or code-repair route. It resolves whole-repository, path, diff/ref/commit, or default working-tree input into scan units and presents each unit's target, coverage, backend, output location, and source-transmission boundary before any scan. Default working-tree planning keeps staged/unstaged tracked changes in one `--working-tree` unit and each explicitly inventoried untracked path in a separate `--path` unit. Refused, failed, uncovered, or unsupported units remain incomplete.

The standalone adapter is pinned to `@openai/codex-security@0.1.8`. Its injected-runner preflight and dry-run planning do not read, infer, copy, or persist credentials. If the exact CLI is unavailable, package acquisition needs a separate dependency/network/cache-write approval; each actual source-transmission scan unit needs its own approval. Findings never authorize edits, accepted risk, or a final verdict.

Any potentially source-bearing scan manifest, findings, coverage, report, or artifact must use a caller-declared private location outside both the scanned repository and its enclosing Git worktree. By default AILI retains references rather than copying source-bearing output into the repository. The provider's exact transmitted source scope, endpoints, retention, encryption, telemetry, proxy behavior, backend untracked-file inclusion, and private-output filesystem/symlink privacy remain `Unverified`.

## Verification

After symlinking or copying files, verify only the pieces that were installed.

WSL/Linux selective symlink setup:

```bash
: "${AILI_HOME:?Set AILI_HOME to the runtime-local aili-workflows clone}"

test -d "$AILI_HOME"
test -d "$HOME/.config/opencode/agents"
test -d "$HOME/.config/opencode/commands"
test -d "$HOME/.agents/skills"
test ! -L "$HOME/.config/opencode/agents"
test ! -L "$HOME/.config/opencode/commands"
test -L "$HOME/.config/opencode/AGENTS.md"
test -L "$HOME/.config/opencode/agents/rose.md"
test -L "$HOME/.config/opencode/agents/implementer.md"
test -L "$HOME/.config/opencode/commands/ideate.md"
test -L "$HOME/.config/opencode/commands/define.md"
test -L "$HOME/.config/opencode/commands/build.md"
test -L "$HOME/.config/opencode/commands/ship.md"
test -L "$HOME/.config/opencode/commands/local-review.md"
test -f "$HOME/.config/opencode/agents/rose.md"
test -f "$HOME/.config/opencode/commands/ideate.md"
test -f "$HOME/.config/opencode/commands/local-review.md"
test -f "$HOME/.config/opencode/AGENTS.md"
readlink "$HOME/.config/opencode/AGENTS.md"
readlink "$HOME/.config/opencode/agents/rose.md"
readlink "$HOME/.config/opencode/commands/ideate.md"
readlink "$HOME/.config/opencode/commands/local-review.md"
```

Windows native selective symlink setup:

```powershell
Test-Path "$env:USERPROFILE\code\ai\aili-workflows"
Test-Path "$env:USERPROFILE\.config\opencode\agents"
Test-Path "$env:USERPROFILE\.config\opencode\commands"
Test-Path "$env:USERPROFILE\.agents\skills"
Get-Item "$env:USERPROFILE\.config\opencode\AGENTS.md"
Get-Item "$env:USERPROFILE\.config\opencode\agents\rose.md"
Get-Item "$env:USERPROFILE\.config\opencode\commands\ideate.md"
Get-Item "$env:USERPROFILE\.config\opencode\commands\local-review.md"
```

Copy fallback:

```bash
test -f "$HOME/.config/opencode/agents/rose.md"
test -f "$HOME/.config/opencode/commands/ideate.md"
test -f "$HOME/.config/opencode/commands/local-review.md"
test -f "$HOME/.config/opencode/AGENTS.md"
```

Required checks for selected runtime add-on setup:

- OpenCode was fully restarted after installation or runtime configuration changes.
- `opencode mcp list` shows the expected Playwright MCP entry.
- Context7 can answer a library documentation lookup through the installed CLI or MCP capability.

## Update

Preferred CLI update/check:

```bash
npx -y rose-aili update
npx -y rose-aili doctor
```

For symlink setup, `rose-aili update` refreshes the selected profile's components and reports external-tool plans. It runs OfficeCLI only when separately approved with `--enable-officecli`. Updating only the cloned repository makes symlinked content current but does not run any external tool; the global `AGENTS.md` symlink will read the updated template after OpenCode restart:

```bash
: "${AILI_HOME:?Set AILI_HOME to the runtime-local aili-workflows clone}"

git -C "$AILI_HOME" pull --ff-only
```

No reinstall is needed unless new optional third-party integrations were added or the user wants to change installation mode.

For copy fallback, update requires copying files again, including `templates/opencode-global-AGENTS.md` to `AGENTS.md`.

## Report Back

After setup, report:

- runtime detected and why
- which mode was chosen and why
- repository clone path
- linked or copied agents and skills
- backup files created
- global config changes
- verification results
- OfficeCLI status (`preserved`, `installed`, `skipped`, or `failed`) and any recovery command, without claiming real render/viewer fidelity
- update command
- anything skipped because it was optional, unavailable, or not requested
