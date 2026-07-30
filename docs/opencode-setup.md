# OpenCode Setup

This document is for an AI agent installing `Rosetears520/aili-workflows` into OpenCode.

[FRAME] Default scope installs reusable skills into `$HOME/.agents/skills` and runs the installer-owned OfficeCLI detect-or-install step at `$HOME/.agents/tools/officecli`. Pass `--skip-officecli` to skip that tool step. Add `--opencode` only when the user also wants OpenCode global rules, agents, commands, config integration, or OpenCode-only skills.

If OpenCode runs in WSL, clone and link inside WSL. If OpenCode runs in Windows native, clone and link inside Windows. Do not mix WSL and Windows paths by default. Do not clone into the user home root.

[FRAME] Default installation mode is selective shared-skill setup plus installer-managed OfficeCLI; OfficeCLI remains a non-routable tool rather than another Skill.

Do not replace `~/.config/opencode/agents`, `~/.config/opencode/commands`, or `$HOME/.agents/skills` by default. The installation scopes are:

- default: `$HOME/.agents/skills/<skill> -> <repo>/.agents/skills/<skill>`;
- default unless `--skip-officecli`: fixed OfficeCLI target `$HOME/.agents/tools/officecli`, with no Skill/MCP/PATH/shell integration;
- `--opencode`: `~/.config/opencode/AGENTS.md -> <repo>/templates/opencode-global-AGENTS.md`;
- `--opencode`: `~/.config/opencode/agents/<agent>.md -> <repo>/agents/<agent>.md`;
- `--opencode`: `~/.config/opencode/commands/<command>.md -> <repo>/commands/<command>.md`;
- `--opencode`, when manifest entries exist: `~/.config/opencode/skills/<skill> -> <repo>/.opencode/skills/<skill>`.

Managed directory symlink mode is only allowed when the user explicitly asks to let `aili-workflows` own the entire global `agents/` and `commands/` directories.

## Goal

Install reusable skills and the shared non-routable OfficeCLI tool by default, and opt into ROSE/OpenCode integration only when requested, while keeping:

- workflow source synced with this repository
- existing OpenCode global agents preserved and shared skills kept outside OpenCode home
- OpenCode global config lightweight
- reusable global AGENTS rules installed in OpenCode home
- DOCX, XLSX, and PPTX routing owned by their existing artifact Skills rather than OfficeCLI
- project memory local to each project
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
| WSL Ubuntu | `/home/<user>/code/ai/aili-workflows` | default: `/home/<user>/.agents/skills` and `/home/<user>/.agents/tools/officecli`; `--opencode`: also `/home/<user>/.config/opencode` | shared skill links plus OfficeCLI tool step by default; OpenCode entries only with `--opencode` |
| Linux/macOS | `$AILI_HOME` | default: `$HOME/.agents/skills` and `$HOME/.agents/tools/officecli`; `--opencode`: also `$HOME/.config/opencode` | shared skill links plus OfficeCLI tool step by default; OpenCode entries only with `--opencode` |
| Windows native | `%USERPROFILE%\code\ai\aili-workflows` | default: `%USERPROFILE%\.agents\skills` and managed OfficeCLI target; OpenCode integration is explicit | shared skill links plus OfficeCLI tool step by default; platform-specific entries remain opt-in |

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
- `.agents/skills/*/SKILL.md` - reusable shared skill sources installed by default.
- `.opencode/skills/*/SKILL.md` - reserved source location for manifest-declared OpenCode-only skills; these install only with `--opencode`.
- `commands/ideate.md`, `commands/define.md`, `commands/build.md`, and `commands/ship.md` - optional OpenCode delivery slash command entrypoints `/ideate`, `/define`, `/build`, and `/ship`.
- `commands/local-review.md` - optional OpenCode slash command entrypoint `/local-review` for report-first local review; it does not override OpenCode's `/review` or replace `/ship`.
- `.agents/skills/rose-memory/` - ROSE project-local SQLite memory skill and CLI.
- `.agents/skills/agents-md-initialization/` - project `AGENTS.md` initialization workflow.
- `templates/AGENTS.md` - single source template for project-local `AGENTS.md` files.
- `templates/opencode-global-AGENTS.md` - installer-owned source for reusable global OpenCode `AGENTS.md` rules.
- `scripts/agents_md.py` - `init`, `update`, and `check` tool for generated project `AGENTS.md` files.
- `scripts/install_opencode.sh` - safe WSL/Linux fallback installer: shared skills plus OfficeCLI by default, `--skip-officecli` to omit the tool, and OpenCode integration with `--opencode`.

Slash commands are optional entrypoints. This repository ships `/ideate`, `/define`, `/build`, and `/ship` as delivery commands mapped to `commands/{ideate,define,build,ship}.md` and backed by `.agents/skills/aili-delivery-flow`; it also ships `/local-review` as a standalone local audit command. Internal stages such as research, questionnaire, test-plan, implement, fix, debug, `/review`, and evolve are not shipped as AILI top-level commands; `/review` remains OpenCode-owned.

The canonical role inventory is primary ROSE plus 19 repository-managed subagents. ROSE runs a proactive Task-trigger scan at each non-trivial intent and changed-evidence work split; an eligible trigger dispatches promptly, while direct work is the no-trigger/blocked fallback. Default concurrency starts at two but is not a hard cap; larger model-selected fan-out requires independent non-overlapping units, concrete benefit, suitable owners, and an explicit join plan. Every concrete Task context is single-use: one bounded assignment, one terminal result or failure, and no old-`task_id` follow-up, repair, recheck, clarification, continuation, or automatic retry. A later same-type Task must start fresh and independently pass a fresh trigger-and-benefit decision. All 19 managed profiles remain non-delegating and retain `external_directory: deny`; only ROSE has per-operation external-directory ask and lifecycle/integration/final-verdict authority. `web-researcher` remains the web-only research role: its web capability does not grant external local-directory, mutation, or delegation access. Built-in `explore` and `general` are outside this managed inventory.

## Installation Decision Rule

[FRAME] Use `rose-aili install` for shared skills plus default OfficeCLI detect-or-install. Use `--skip-officecli` when the user explicitly declines that tool step. Use `rose-aili install --opencode` for repository-managed global AGENTS rules, agents, commands, OpenCode-only skills, and optional OpenCode JSON/JSONC config. A normal git clone uses selective symlinks; a packaged/non-git npm or npx source uses copied files so installed entries do not point at a transient package cache.

```bash
npx -y rose-aili install
npx -y rose-aili install --opencode
```

Before npm publishing, use the GitHub package-spec form from the repository URL:

```bash
npx -y --package github:<owner>/<repo> rose-aili install
```

Use these non-interactive flags for AI-agent or scripted setup:

```bash
npx -y rose-aili install --yes
npx -y rose-aili install --dry-run
npx -y rose-aili install --skip-officecli
npx -y rose-aili install --opencode --yes --model anthropic/claude-sonnet-4-5
npx -y rose-aili install --opencode --set-default-rose
npx -y rose-aili install --opencode --skip-opencode-config
npx -y rose-aili install --opencode --enable-playwright
npx -y rose-aili install --opencode --enable-codegraph
npx -y rose-aili install --opencode --enable-openspec --project-root <absolute-canonical-path>
npx -y rose-aili install --opencode --skip-openspec
npx -y rose-aili update --opencode --skip-openspec
npx -y rose-aili update --skip-officecli
npx -y rose-aili doctor
npx -y rose-aili update
```

[FRAME] OfficeCLI default-on/skip/dry-run behavior is independent of `--opencode`. OpenCode config sync remains disabled outside `--opencode` scope. Within `--opencode`, the existing preserve/conflict behavior remains, and Playwright, CodeGraph, Graphify, and OpenSpec retain their separate explicit flags. OpenCode-specific flags fail closed when `--opencode` is absent.

### Managed OfficeCLI Tool

[FRAME] `install` and `update` detect the fixed managed shim first. An exact current version is preserved without npm; a missing or drifted version uses the fixed local-prefix package contract from `manifests/officecli-tool.json`. The summary reports component installation and OfficeCLI separately; OfficeCLI failure returns nonzero without rolling back already-synced Skills.

[FRAME] `--skip-officecli` performs no OfficeCLI probe, target creation, or npm command. `--dry-run` reports the exact target, package, argv, and network/dependency effects without creating the target or running an executable. Neither flag installs an OfficeCLI Skill, MCP, public command, PATH entry, shell integration, or package full installer.

[UNVERIFIED] Fake/temp repository checks do not prove a real npm/native install, DOCX/XLSX/PPTX rendering, complex Word/workbook round-trip, or cross-viewer fidelity. Do not report those outcomes as verified after setup alone.

[KNOWN] Interactive `install` / `update` without `--opencode` performs no OpenCode prompts. Interactive `install --opencode` asks about the default agent, model, Playwright, CodeGraph, Graphify, and OpenSpec; `update --opencode` asks about CodeGraph and Graphify.

AILI has no active DCP integration. `install`, `update`, and `doctor` do not install, detect, configure, report, migrate, or remove a third-party DCP plugin and do not read or mutate user `dcp.json`/`dcp.jsonc`. Former DCP flags are ordinary unknown options. Historical DCP evidence may remain in archived ideas, accepted-change history, or negative fixtures, but it is not setup/runtime authority.

### Retired Skill Reconciliation

`using-agent-skills`, `repo-evidence-first`, and `verification-before-completion` are no longer runnable or default-installed skills. Fresh install and doctor requirements come from the current component manifest and omit them.

An explicit `install` or `update`, including `--dry-run`, checks only those three exact destinations under `$HOME/.agents/skills`. The installer proves managed ownership only when the destination is a symlink whose resolved target exactly equals `<AILI_HOME>/.agents/skills/<retired-name>`. A proven link is reported and unlinked (or reported as a planned unlink in dry-run). A copied directory, ordinary file, unreadable/modified symlink, different target, or any other ambiguous entry is preserved and reported; the installer never removes a sibling, parent directory, backup, or user file. The CLI exposes the per-name result under `componentInstall.retiredSkillReconciliation`. Doctor adds no stale-copy result field.

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
- back up `$HOME/.agents/skills/rose-memory` if it is a real directory and conflicts with the new symlink
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

Use this by default. Without `--opencode`, it links shared skills into `$HOME/.agents/skills`, runs the OfficeCLI tool step unless skipped, and leaves OpenCode home untouched. With `--opencode`, it also preserves OpenCode's existing global directories and links individual managed entries.

WSL/Linux recommended command:

```bash
scripts/install_opencode.sh --mode selective
scripts/install_opencode.sh --mode selective --skip-officecli
scripts/install_opencode.sh --mode selective --opencode
```

The full OpenCode entry-linking logic below corresponds only to the component portion of the `--opencode` scope. It does not implement OfficeCLI, exact retired-skill ownership reconciliation, or structured failure reporting; use the CLI or installer script rather than hand-rolling those steps.

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
  rose-memory -> $AILI_HOME/.agents/skills/rose-memory

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

Use the `agents-md-initialization` skill for this flow. The skill should call the script instead of writing `AGENTS.md` by hand:

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

- Canonical AILI source is this repository's four command files, shared `.agents/skills`, any explicitly manifest-declared `.opencode/skills`, agents, templates, manifests, TypeScript, and installer sources.
- Root `AGENTS.md`, `dist/`, installed OpenCode files, and installed shared skills are generated or installed downstream outputs. Change their canonical source/generator instead of hand-editing them.
- Current generated `.opencode/commands/opsx-*` and `.opencode/skills/openspec-*` direct adapters are OpenSpec-owned ignored outputs, not repository-managed OpenCode-only skills. They remain outside AILI guarantees and are not installed by `--opencode` unless a future accepted manifest change explicitly promotes a distinct canonical component.
- Pinned upstream files under canonical skill `references/upstream/` are inert licensed data, not another installed skill or runtime. They use `SKILL.upstream.md`; upstream scripts must remain non-executable data and must never become commands, hooks, or routing targets.
- `package.json#files` ships canonical agents, `.agents/`, commands, manifests, both AGENTS templates, required helpers/fixtures, README/setup docs, and built CLI. A future manifest-declared `.opencode/skills/<name>` component must add that exact canonical source to the package allowlist; the package must not broadly include ignored/generated `.opencode` state.

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

### Versioned Session Handoffs

The `session-handoff` skill supports explicit CREATE, LIST, and RESUME. OpenSpec changes use `openspec/changes/<change-id>/handoffs/`; ordinary tasks use one confirmed repository-local `<task-root>/handoffs/`. Legacy `<task-root>/handoff.md` remains an explicitly selected read-only input.

The skill-local `scripts/session_handoff.py` is a deterministic filesystem helper, not another workflow or public command. It enforces exclusive UTC snapshot names, containment and symlink rejection, validated draft/finalize transitions, SHA-256 checks, atomic regular-file `LATEST.md`, bounded-frontmatter LIST, exact-first RESOLVE, legacy preservation, and localized exact-path resume output. Finalized snapshots are not automatically edited, migrated, archived, or pruned; a correction creates a new `continues_from` snapshot.

Do not create a handoff because of context pressure, compression, phase completion, a timer, or a hook. Do not promote it into memory. On RESUME, revalidate the current root, worktree, branch/HEAD, dirty state, permissions, contracts, attachments, and affected evidence before continuing.

Typical intent mapping selects one primary loop rather than a default skill chain:

- Explicit specification or a named material contract gap: `spec-driven-development`.
- Explicit task/package planning: `planning-and-task-breakdown`.
- Accepted implementation that benefits from coherent slices: `incremental-implementation`; ROSE separately selects `test-driven-development` only for explicit TDD, accepted reproduction-first proof, or a named high-risk red/green need.
- One concrete build, typecheck, lint, test, packaging, or CI failure: `build-failure-repair`.
- Explicit bounded review: `code-review-and-quality`.
- App UI as the primary deliverable: `frontend-ui-engineering`.
- Explicit project-local memory continuity: `rose-memory`.

## Memory Setup

Project memory is always project-local.

Do not symlink `memory/memory.db` into global OpenCode config.

When a project needs ROSE memory:

```bash
mkdir -p memory
python ~/.agents/skills/rose-memory/references/memory_cli.py init --db memory/memory.db
python ~/.agents/skills/rose-memory/references/memory_cli.py doctor --db memory/memory.db --record
```

Rules:

- Do not create `memory.md` or JSON sidecars.
- Do not edit `memory/memory.db` manually.
- Do not copy or symlink `memory/memory.db` into global config.
- If the `rose-memory` skill is symlinked, the CLI updates automatically when this repository updates.

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
test -L "$HOME/.agents/skills/rose-memory"
test -L "$HOME/.config/opencode/commands/ideate.md"
test -L "$HOME/.config/opencode/commands/define.md"
test -L "$HOME/.config/opencode/commands/build.md"
test -L "$HOME/.config/opencode/commands/ship.md"
test -L "$HOME/.config/opencode/commands/local-review.md"
test -f "$HOME/.config/opencode/agents/rose.md"
test -f "$HOME/.agents/skills/rose-memory/SKILL.md"
test -f "$HOME/.config/opencode/commands/ideate.md"
test -f "$HOME/.config/opencode/commands/local-review.md"
test -f "$HOME/.config/opencode/AGENTS.md"
readlink "$HOME/.config/opencode/AGENTS.md"
readlink "$HOME/.config/opencode/agents/rose.md"
readlink "$HOME/.agents/skills/rose-memory"
readlink "$HOME/.config/opencode/commands/ideate.md"
readlink "$HOME/.config/opencode/commands/local-review.md"
python "$HOME/.agents/skills/rose-memory/references/memory_cli.py" --help
```

Windows native selective symlink setup:

```powershell
Test-Path "$env:USERPROFILE\code\ai\aili-workflows"
Test-Path "$env:USERPROFILE\.config\opencode\agents"
Test-Path "$env:USERPROFILE\.config\opencode\commands"
Test-Path "$env:USERPROFILE\.agents\skills"
Get-Item "$env:USERPROFILE\.config\opencode\AGENTS.md"
Get-Item "$env:USERPROFILE\.config\opencode\agents\rose.md"
Get-Item "$env:USERPROFILE\.agents\skills\rose-memory"
Get-Item "$env:USERPROFILE\.config\opencode\commands\ideate.md"
Get-Item "$env:USERPROFILE\.config\opencode\commands\local-review.md"
```

Copy fallback:

```bash
test -f "$HOME/.config/opencode/agents/rose.md"
test -f "$HOME/.agents/skills/rose-memory/SKILL.md"
test -f "$HOME/.config/opencode/commands/ideate.md"
test -f "$HOME/.config/opencode/commands/local-review.md"
test -f "$HOME/.config/opencode/AGENTS.md"
python "$HOME/.agents/skills/rose-memory/references/memory_cli.py" --help
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

For symlink setup, `rose-aili update` refreshes components and performs OfficeCLI detect-or-install unless `--skip-officecli` is passed. Updating only the cloned repository makes symlinked content current but does not run the OfficeCLI tool step; the global `AGENTS.md` symlink will read the updated template after OpenCode restart:

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
