# OpenCode Setup

This document is for an AI agent installing `Rosetears520/aili-workflows` into OpenCode.

Default rule: install where OpenCode runs.

If OpenCode runs in WSL, clone and link inside WSL. If OpenCode runs in Windows native, clone and link inside Windows. Do not mix WSL and Windows paths by default. Do not clone into the user home root.

Default installation mode is selective symlink setup.

Do not replace `~/.config/opencode/agents`, `~/.config/opencode/commands`, or `$HOME/.agents/skills` by default. Preserve existing OpenCode agent/command directories and install skills into the shared skills directory:

- `~/.config/opencode/AGENTS.md -> <repo>/templates/opencode-global-AGENTS.md`
- `~/.config/opencode/agents/<agent>.md -> <repo>/agents/<agent>.md`
- `$HOME/.agents/skills/<skill> -> <repo>/.agents/skills/<skill>`
- `~/.config/opencode/commands/<command>.md -> <repo>/commands/<command>.md`

Managed directory symlink mode is only allowed when the user explicitly asks to let `aili-workflows` own the entire global `agents/` and `commands/` directories.

## Goal

Install ROSE agents and skills for OpenCode while keeping:

- workflow source synced with this repository
- existing OpenCode global agents preserved and shared skills kept outside OpenCode home
- OpenCode global config lightweight
- reusable global AGENTS rules installed in OpenCode home
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
| WSL Ubuntu | `/home/<user>/code/ai/aili-workflows` | `/home/<user>/.config/opencode` plus `/home/<user>/.agents/skills` | selective links: agents/commands inside OpenCode home; skills inside shared `.agents/skills` |
| Linux/macOS | `$AILI_HOME` | `$HOME/.config/opencode` plus `$HOME/.agents/skills` | selective links: agents/commands inside OpenCode home; skills inside shared `.agents/skills` |
| Windows native | `%USERPROFILE%\code\ai\aili-workflows` | `%USERPROFILE%\.config\opencode` plus `%USERPROFILE%\.agents\skills` | selective symlinks or junctions: agents/commands inside OpenCode home; skills inside shared `.agents\skills` |

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
- `agents/security-auditor.md` - security review subagent.
- `agents/test-engineer.md` - testing subagent.
- `agents/test-coverage-reviewer.md`, `agents/pr-test-analyzer.md`, `agents/ai-regression-scout.md`, and `agents/silent-failure-reviewer.md` - relevant-triggered read-only QA review/scouting subagents.
- `agents/browser-qa-runner.md` and `agents/e2e-artifact-runner.md` - relevant-triggered browser/E2E test subagents that require repository-local placement before durable screenshots, traces, videos, reports, or bundles and avoid production data mutation.
- `agents/spec-miner.md`, `agents/agent-evaluator.md`, and `agents/opensource-sanitizer.md` - relevant-triggered read-only spec-mining, agent-output evaluation, and OSS/public exposure review subagents.
- `.agents/skills/*/SKILL.md` - repository source for OpenCode skills.
- `commands/ideate.md`, `commands/define.md`, `commands/build.md`, and `commands/ship.md` - optional OpenCode delivery slash command entrypoints `/ideate`, `/define`, `/build`, and `/ship`.
- `commands/local-review.md` - optional OpenCode slash command entrypoint `/local-review` for report-first local review; it does not override OpenCode's `/review` or replace `/ship`.
- `.agents/skills/rose-memory/` - ROSE project-local SQLite memory skill and CLI.
- `.agents/skills/agents-md-initialization/` - project `AGENTS.md` initialization workflow.
- `templates/AGENTS.md` - single source template for project-local `AGENTS.md` files.
- `templates/opencode-global-AGENTS.md` - installer-owned source for reusable global OpenCode `AGENTS.md` rules.
- `scripts/agents_md.py` - `init`, `update`, and `check` tool for generated project `AGENTS.md` files.
- `scripts/install_opencode.sh` - safe WSL/Linux installer for OpenCode global AGENTS rules, agents, skills, and commands.

Slash commands are optional entrypoints. This repository ships `/ideate`, `/define`, `/build`, and `/ship` as delivery commands mapped to `commands/{ideate,define,build,ship}.md` and backed by `.agents/skills/aili-delivery-flow`; it also ships `/local-review` as a standalone local audit command. Internal stages such as research, questionnaire, test-plan, implement, fix, debug, `/review`, and evolve are not shipped as AILI top-level commands; `/review` remains OpenCode-owned.

## Installation Decision Rule

Use `rose-aili install` by default when Node/npm is available. It wraps the same entry-level setup for repository-managed global AGENTS rules, agents, skills, and commands, then safely merges optional OpenCode JSON/JSONC config. A normal git clone uses selective symlinks; a packaged/non-git npm or npx source uses copied files so OpenCode does not point at a transient package cache. The npm package bin target is `dist/cli.js`; builds enforce a Node shebang and executable file mode so npm/npx can execute it directly.

```bash
npx -y rose-aili install
```

Before npm publishing, use the GitHub package-spec form from the repository URL:

```bash
npx -y --package github:<owner>/<repo> rose-aili install
```

Use these non-interactive flags for AI-agent or scripted setup:

```bash
npx -y rose-aili install --yes --model anthropic/claude-sonnet-4-5
npx -y rose-aili install --set-default-rose
npx -y rose-aili install --skip-opencode-config
npx -y rose-aili install --enable-playwright
npx -y rose-aili install --enable-codegraph
npx -y rose-aili install --enable-openspec
npx -y rose-aili install --skip-openspec
npx -y rose-aili update --skip-openspec
npx -y rose-aili doctor
npx -y rose-aili update
```

OpenCode config sync is enabled by default for both `install` and `update`; use `--skip-opencode-config` to disable it. The default sync sets or keeps `default_agent: "rose"` when the value is absent or already `rose`, preserves a conflicting non-rose default unless `--force-default-agent` is passed, writes `agent.rose.model` only when `--model <provider/model>` is provided, and writes Playwright MCP only when `--enable-playwright` is provided. Existing `agent.rose.model` values are preserved unless `--force-model` is passed. Playwright, CodeGraph, and OpenSpec are explicit opt-ins; optional decisions are reported as skipped/pending with exact next-step commands. `--dry-run` reports planned component/config operations without mutating OpenCode files.

Interactive `rose-aili install` asks, in order, about the default agent, a missing model override, Playwright MCP, CodeGraph OpenCode integration, and OpenSpec. Interactive `rose-aili update` asks only the CodeGraph integration question. Non-interactive setup performs optional integration work only for explicit enable flags. Model preferences are always written to OpenCode JSON/JSONC under `agent.rose.model`, not to `agents/rose.md`.

AILI has no active DCP integration. `install`, `update`, and `doctor` do not install, detect, configure, report, migrate, or remove a third-party DCP plugin and do not read or mutate user `dcp.json`/`dcp.jsonc`. Former DCP flags are ordinary unknown options. Historical DCP evidence may remain in archived ideas, accepted-change history, or negative fixtures, but it is not setup/runtime authority.

CodeGraph opt-in is explicit: `rose-aili install --enable-codegraph` runs `npm install -g @colbymchenry/codegraph@latest`, then delegates `codegraph install --target=opencode --yes`. Restart OpenCode after a configured CodeGraph install so OpenCode reloads the MCP integration. If either command is unavailable or fails, the core global `AGENTS.md`/agents/skills/commands install can still succeed and the summary reports CodeGraph recovery instructions separately.

Project-local CodeGraph initialization is separate from global install/update. An AI agent should confirm the current repository root before running `codegraph init -i` and `codegraph status` for that repository only. It must not run `openspec init` as part of CodeGraph initialization, and it must not initialize multiple repositories without explicit approval for that batch scope.

Project `AGENTS.md` initialization/update should also check CodeGraph readiness for the same repository. After generating or updating `AGENTS.md`, run or request `codegraph status`; if the repository is not initialized, ask whether to run `codegraph init -i`, then rerun `codegraph status` when approved. If CodeGraph is unavailable, skipped, or not approved, keep the `AGENTS.md` flow non-blocking but report that the project has no CodeGraph code-map coverage yet.

OpenSpec is explicit opt-in for `rose-aili install` and `rose-aili update`. With `--enable-openspec`, it requires Node.js `20.19.0+`, detects an existing CLI with `openspec --version`, runs `npm install -g @fission-ai/openspec@latest` only when the CLI is missing, then runs `openspec update` inside projects with existing OpenSpec markers or `openspec init` for first-time setup. Expanded workflow selection with `openspec config profile` remains a manual follow-up.

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

Use this by default. It preserves OpenCode's existing global `agents/` and `commands/` directories, then links skills into `$HOME/.agents/skills`.

WSL/Linux recommended command:

```bash
scripts/install_opencode.sh --mode selective
```

Equivalent WSL/Linux logic:

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
CONFIRM_MANAGED_DIRECTORY=yes scripts/install_opencode.sh --mode managed-directory
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
```

Manual logic:

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

Use this only when OpenCode is running natively in Windows.

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

Recommended opt-in runtime add-ons are Playwright MCP, OpenSpec, CodeGraph, and Context7 integration. Fully restart OpenCode after installing plugins, MCP servers, Context7, or changing OpenCode runtime configuration.

### OpenSpec

OpenSpec is installed/configured only when explicitly enabled:

```bash
rose-aili install --enable-openspec
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

- Canonical AILI source is this repository's four command files, top-level canonical `SKILL.md` files and references, agents, templates, manifests, TypeScript, and installer sources.
- Root `AGENTS.md`, `dist/`, installed OpenCode files, and installed shared skills are generated or installed downstream outputs. Change their canonical source/generator instead of hand-editing them.
- Current generated `.opencode/commands/opsx-*` and `.opencode/skills/openspec-*` direct adapters are OpenSpec-owned outputs. They remain unchanged and directly callable outside AILI guarantees. AILI does not route to, recommend, wrap, suppress, prevent, control, or count their output as AILI acceptance/readiness/verification/completion evidence.
- Pinned upstream files under canonical skill `references/upstream/` are inert licensed data, not another installed skill or runtime. They use `SKILL.upstream.md`; upstream scripts must remain non-executable data and must never become commands, hooks, or routing targets.
- `package.json#files` ships canonical agents, `.agents/` (including protocols and inert references), commands, manifests, both AGENTS templates, `agents_md.py`, the Graphify guarded launcher and its contract fixture, the installer script, README/setup docs, and built CLI. Other repository-only checkers, tests, and harness fixtures are not installed runtime components; packaged helpers/data are not registered as commands or runnable skills.

The upstream distribution path is currently fail-closed. OpenCode `1.17.18` installed-catalog recursion remains `UV-005`, and filesystem mode evidence may not prove required upstream `0644` modes; until both are resolved, do not claim distribution/registration/enablement or release readiness. `npm pack --dry-run` is content evidence only and does not publish or resolve runtime catalog/mode behavior.

Cross-root delegation also fails closed against exact OpenCode `1.17.18` behavior. Root approval is not process containment: if ask/always/`--auto`, Task-root inheritance, symlink/TOCTOU, subprocess, bash-effect, secret, or neighboring-root behavior cannot be safely expressed and freshly proven, do not dispatch or mutate across roots; retain the runtime result as `Unverified`.

Graphify remains a separate operation. A real or synthetic process starts only after explicit approval for that exact operation and successful provenance, advisory, network-denial, isolated-environment, argv, output-root, and write-inventory controls. Missing control means blocked/`Unverified` before process start; Graphify is never installation, command routing, scheduled behavior, or completion evidence.

Typical intent mapping:

- Feature work: `spec-driven-development`, then `incremental-implementation` and `test-driven-development`.
- Planning: `planning-and-task-breakdown`.
- Bug or failure: `debugging-and-error-recovery`.
- Review: `code-review-and-quality`.
- UI work: `frontend-ui-engineering`.
- Memory continuity: `rose-memory`.

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

For symlink setup, update the cloned repository; the global `AGENTS.md` symlink will read the updated `templates/opencode-global-AGENTS.md` immediately after OpenCode restart:

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
- update command
- anything skipped because it was optional, unavailable, or not requested
