# OpenCode Setup

This document is for an AI agent installing `Rosetears520/aili-workflows` into OpenCode.

Default rule: install where OpenCode runs.

If OpenCode runs in WSL, clone and link inside WSL. If OpenCode runs in Windows native, clone and link inside Windows. Do not mix WSL and Windows paths by default. Do not clone into the user home root.

Default installation mode is selective symlink setup.

Do not replace `~/.config/opencode/agents`, `~/.config/opencode/skills`, or `~/.config/opencode/commands` by default. Preserve existing OpenCode directories and create symlinks inside them:

- `~/.config/opencode/AGENTS.md -> <repo>/templates/opencode-global-AGENTS.md`
- `~/.config/opencode/agents/<agent>.md -> <repo>/agents/<agent>.md`
- `~/.config/opencode/skills/<skill> -> <repo>/skills/<skill>`
- `~/.config/opencode/commands/<command>.md -> <repo>/commands/<command>.md`

Managed directory symlink mode is only allowed when the user explicitly asks to let `aili-workflows` own the entire global `agents/`, `skills/`, and `commands/` directories.

## Goal

Install ROSE agents and skills for OpenCode while keeping:

- workflow source synced with this repository
- existing OpenCode global agents and skills preserved
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

For Rosetears' WSL Ubuntu environment this resolves to:

```bash
/home/rosetears/code/ai/aili-workflows
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
\\wsl.localhost\Ubuntu\home\rosetears\code\ai\aili-workflows
```

Do not treat this as the Windows native install path.

## Install Matrix

| OpenCode runtime | Repository clone path | OpenCode config path | Link style |
|---|---|---|---|
| WSL Ubuntu | `/home/rosetears/code/ai/aili-workflows` | `/home/rosetears/.config/opencode` | selective symlinks inside `agents/`, `skills/`, and `commands/` |
| Linux/macOS | `$AILI_HOME` | `$HOME/.config/opencode` | selective symlinks inside `agents/`, `skills/`, and `commands/` |
| Windows native | `%USERPROFILE%\code\ai\aili-workflows` | `%USERPROFILE%\.config\opencode` | selective symlinks or junctions inside `agents\`, `skills\`, and `commands\` |

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
- `skills/*/SKILL.md` - OpenCode skills.
- `commands/ideate.md`, `commands/define.md`, `commands/build.md`, and `commands/ship.md` - optional OpenCode slash command entrypoints `/ideate`, `/define`, `/build`, and `/ship`.
- `skills/rose-memory/` - ROSE project-local SQLite memory skill and CLI.
- `skills/agents-md-initialization/` - project `AGENTS.md` initialization workflow.
- `templates/AGENTS.md` - single source template for project-local `AGENTS.md` files.
- `templates/opencode-global-AGENTS.md` - installer-owned source for reusable global OpenCode `AGENTS.md` rules.
- `scripts/agents_md.py` - `init`, `update`, and `check` tool for generated project `AGENTS.md` files.
- `scripts/install_opencode.sh` - safe WSL/Linux installer for OpenCode global AGENTS rules, agents, skills, and commands.

Slash commands are optional entrypoints. This repository ships only `/ideate`, `/define`, `/build`, and `/ship`, mapped to `commands/{ideate,define,build,ship}.md` and backed by `skills/aili-delivery-flow`; internal stages such as research, questionnaire, test-plan, implement, fix, debug, review, and evolve are not shipped as top-level commands.

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
npx -y rose-aili install --enable-playwright
npx -y rose-aili install --enable-dcp
npx -y rose-aili install --enable-codegraph
npx -y rose-aili install --enable-openspec
npx -y rose-aili doctor
npx -y rose-aili update
```

`--yes` sets `rose` as `default_agent` when no conflicting default exists. Existing non-rose `default_agent` and existing `agent.rose.model` values are preserved unless `--force-default-agent` or `--force-model` is passed. `--yes` does not silently install DCP/CodeGraph/OpenSpec and does not silently pin `agent.rose.model`; optional decisions are reported as skipped/pending with exact next-step commands. `--dry-run` reports planned component/config operations without mutating OpenCode files.

Interactive `rose-aili install` asks, in order: set default `rose`, optional `agent.rose.model`, Playwright MCP, DCP plugin, CodeGraph OpenCode integration, and OpenSpec install/configure. Interactive `rose-aili update` asks only the new CodeGraph integration question; OpenSpec remains install-time or explicit-flag-only so CodeGraph upgrade prompts do not trigger project OpenSpec initialization. The model prompt accepts a free-form `provider/model` value; pressing Enter with a blank value skips model writing. To make `rose` default while keeping OpenCode's default model behavior, run `rose-aili install --set-default-rose` without `--model`. Non-interactive setup can pass `--model <provider/model>` only when the user wants a fixed model override. Model preferences are always written to OpenCode JSON/JSONC under `agent.rose.model`, not to `agents/rose.md`.

DCP opt-in is explicit: `rose-aili install --enable-dcp` delegates `opencode plugin @tarquinen/opencode-dcp@latest --global` with argv execution. This uses a third-party `@latest` package, so treat it as user-accepted latest-version risk. If the plugin command is unavailable or fails, the core global `AGENTS.md`/agents/skills/commands install can still succeed and the summary reports DCP recovery instructions separately.

CodeGraph opt-in is explicit: `rose-aili install --enable-codegraph` runs `npm install -g @colbymchenry/codegraph@latest`, then delegates `codegraph install --target=opencode --yes`. Restart OpenCode after a configured CodeGraph install so OpenCode reloads the MCP integration. If either command is unavailable or fails, the core global `AGENTS.md`/agents/skills/commands install can still succeed and the summary reports CodeGraph recovery instructions separately.

Project-local CodeGraph initialization is separate from global install/update. An AI agent should confirm the current repository root before running `codegraph init -i` and `codegraph status` for that repository only. It must not run `openspec init` as part of CodeGraph initialization, and it must not initialize multiple repositories without explicit approval for that batch scope.

OpenSpec opt-in is explicit: `rose-aili install --enable-openspec` requires Node.js `20.19.0+`, runs `npm install -g @fission-ai/openspec@latest`, then runs `openspec update` inside projects with existing OpenSpec markers or `openspec init` for first-time setup. Expanded workflow selection with `openspec config profile` remains a manual follow-up.

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
- `~/.config/opencode/skills` already exists
- the user has existing agents or skills
- the user says "soft link into opencode", "add this workflow", or "keep synced with repo"

Do not choose Managed Directory Symlink Setup unless the user explicitly says:

- replace the whole global agents directory
- replace the whole global skills directory
- let `aili-workflows` own the entire OpenCode agents/skills config

If unsure, use Selective Symlink Setup.

## Destructive-Config Guard

Do not delete, replace without backup, or convert these paths into directory symlinks unless explicitly approved by the user:

- `~/.config/opencode/agents`
- `~/.config/opencode/skills`
- `~/.config/opencode/commands`
- `~/.config/opencode/AGENTS.md`
- OpenCode runtime configuration files

Back up individual conflicting entries only.

Allowed by default:

- back up `~/.config/opencode/agents/rose.md` if it is a real file and conflicts with the new symlink
- back up `~/.config/opencode/skills/rose-memory` if it is a real directory and conflicts with the new symlink
- back up `~/.config/opencode/commands/ideate.md` if it is a real file and conflicts with the new symlink
- back up `~/.config/opencode/AGENTS.md` if it is a real file and conflicts with the installer-owned global AGENTS file

Not allowed by default:

- moving the whole `agents/` directory
- moving the whole `skills/` directory
- moving the whole `commands/` directory
- replacing the whole directory with a symlink

## Installation Modes

Choose one mode after the Runtime Detection Gate.

### Mode A: Selective Symlink Setup (Default)

Use this by default. It preserves OpenCode's existing global `agents/`, `skills/`, and `commands/` directories, then links entries inside them.

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

mkdir -p "$OPENCODE_HOME/agents" "$OPENCODE_HOME/skills" "$OPENCODE_HOME/commands"

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

for dir in "$AILI_HOME"/skills/*; do
  [ -d "$dir" ] || continue
  [ -f "$dir/SKILL.md" ] || continue
  name="$(basename "$dir")"
  target="$OPENCODE_HOME/skills/$name"

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

~/.config/opencode/skills/
  caveman/
  caveman-commit/
  rose-memory -> $AILI_HOME/skills/rose-memory

~/.config/opencode/commands/
  ideate.md -> $AILI_HOME/commands/ideate.md
  define.md -> $AILI_HOME/commands/define.md
  build.md -> $AILI_HOME/commands/build.md
  ship.md -> $AILI_HOME/commands/ship.md
```

### Mode B: Managed Directory Symlink Setup (Exclusive / Advanced)

This is a dangerous exclusive mode. It replaces OpenCode's whole global `agents/`, `skills/`, and `commands/` directories with directory-level symlinks.

Do not use this mode unless the user explicitly says `aili-workflows` may replace the entire global `agents/`, `skills/`, and `commands/` directories.

WSL/Linux command with explicit confirmation:

```bash
CONFIRM_MANAGED_DIRECTORY=yes scripts/install_opencode.sh --mode managed-directory
```

Manual logic, only after explicit approval:

```bash
: "${AILI_HOME:?Set AILI_HOME to the runtime-local aili-workflows clone}"
OPENCODE_HOME="${OPENCODE_HOME:-$HOME/.config/opencode}"

mkdir -p "$(dirname "$AILI_HOME")" "$OPENCODE_HOME"
git clone https://github.com/Rosetears520/aili-workflows.git "$AILI_HOME" 2>/dev/null || git -C "$AILI_HOME" pull --ff-only

if [ -e "$OPENCODE_HOME/agents" ] && [ ! -L "$OPENCODE_HOME/agents" ]; then
  mv "$OPENCODE_HOME/agents" "$OPENCODE_HOME/agents.backup.$(date +%Y%m%d%H%M%S)"
fi

if [ -e "$OPENCODE_HOME/skills" ] && [ ! -L "$OPENCODE_HOME/skills" ]; then
  mv "$OPENCODE_HOME/skills" "$OPENCODE_HOME/skills.backup.$(date +%Y%m%d%H%M%S)"
fi

if [ -e "$OPENCODE_HOME/commands" ] && [ ! -L "$OPENCODE_HOME/commands" ]; then
  mv "$OPENCODE_HOME/commands" "$OPENCODE_HOME/commands.backup.$(date +%Y%m%d%H%M%S)"
fi

if [ -e "$OPENCODE_HOME/AGENTS.md" ] && [ ! -L "$OPENCODE_HOME/AGENTS.md" ]; then
  mv "$OPENCODE_HOME/AGENTS.md" "$OPENCODE_HOME/AGENTS.md.backup.$(date +%Y%m%d%H%M%S)"
fi

ln -sfn "$AILI_HOME/agents" "$OPENCODE_HOME/agents"
ln -sfn "$AILI_HOME/skills" "$OPENCODE_HOME/skills"
ln -sfn "$AILI_HOME/commands" "$OPENCODE_HOME/commands"
ln -sfn "$AILI_HOME/templates/opencode-global-AGENTS.md" "$OPENCODE_HOME/AGENTS.md"
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

mkdir -p "$OPENCODE_HOME/agents" "$OPENCODE_HOME/skills" "$OPENCODE_HOME/commands"

if [ -e "$OPENCODE_HOME/AGENTS.md" ] && [ ! -L "$OPENCODE_HOME/AGENTS.md" ]; then
  mv "$OPENCODE_HOME/AGENTS.md" "$OPENCODE_HOME/AGENTS.md.backup.$(date +%Y%m%d%H%M%S)"
fi

cp -R "$AILI_HOME/agents/"*.md "$OPENCODE_HOME/agents/"
cp -R "$AILI_HOME/skills/"* "$OPENCODE_HOME/skills/"
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
New-Item -ItemType Directory -Force -Path (Join-Path $OpenCodeHome "skills") | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $OpenCodeHome "commands") | Out-Null

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

Get-ChildItem "$AiliHome\skills" -Directory | ForEach-Object {
  $Target = Join-Path "$OpenCodeHome\skills" $_.Name

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

If Windows symbolic link permissions are blocked, use copy fallback for command files or junctions for skill directories, but keep the same rule: create entries inside `skills\` and `commands\`, do not replace the whole directory.

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

Use this only if `~/.config/opencode/agents` or `~/.config/opencode/skills` was accidentally replaced by a directory-level symlink.

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

Project `AGENTS.md` files must be generated from this repository's `templates/AGENTS.md`, then filled with project-specific commands, facts, and conventions, and committed to that project.

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

Recommended runtime add-ons are DCP plugin, Playwright MCP, OpenSpec, and Context7 integration. `rose-aili` can configure the pinned optional Playwright MCP entry and can delegate DCP/OpenSpec only after explicit opt-in flags or interactive confirmation. Fully restart OpenCode after installing plugins, MCP servers, Context7, or changing OpenCode runtime configuration.

### DCP Plugin

```bash
opencode plugin @tarquinen/opencode-dcp@latest --global
```

This is a trust-latest command for users who explicitly want DCP. `rose-aili install --enable-dcp` can run the same command; `rose-aili install`, `--yes`, and non-interactive runs without `--enable-dcp` do not silently install DCP plugins.

DCP reads configuration from `~/.config/opencode/dcp.jsonc` / `dcp.json`, `$OPENCODE_CONFIG_DIR/dcp.jsonc` / `dcp.json`, or project `.opencode/dcp.jsonc` / `dcp.json`. Project config overrides global config. Restart OpenCode after changing the file.

Recommended range thresholds for a 400k-token context window:

| DCP config key | Value | Intent |
|---|---:|---|
| `compress.minContextLimit` | `"35%"` | start range compression before noisy history dominates attention |
| `compress.maxContextLimit` | `"45%"` | upper automatic compression threshold for normal operation |

Do not add unsupported keys such as `warn`, `force_compress`, or `target_after_compress`; the DCP schema only accepts documented keys and warns on unknown properties.

Verify after restart by running `/dcp` in OpenCode and confirming the plugin reads `minContextLimit: "35%"` and `maxContextLimit: "45%"` from the active config.

### OpenSpec

OpenSpec is optional and explicit opt-in:

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
- Optional slash commands `/ideate`, `/define`, `/build`, and `/ship` provide thin entrypoints to `skills/aili-delivery-flow`; no internal stage commands are shipped.
- The user can work naturally: "implement this", "fix this bug", "review this", "plan this change".

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
python ~/.config/opencode/skills/rose-memory/references/memory_cli.py init --db memory/memory.db
python ~/.config/opencode/skills/rose-memory/references/memory_cli.py doctor --db memory/memory.db --record
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
test -d "$HOME/.config/opencode/skills"
test -d "$HOME/.config/opencode/commands"
test ! -L "$HOME/.config/opencode/agents"
test ! -L "$HOME/.config/opencode/skills"
test ! -L "$HOME/.config/opencode/commands"
test -L "$HOME/.config/opencode/AGENTS.md"
test -L "$HOME/.config/opencode/agents/rose.md"
test -L "$HOME/.config/opencode/agents/implementer.md"
test -L "$HOME/.config/opencode/skills/rose-memory"
test -L "$HOME/.config/opencode/commands/ideate.md"
test -L "$HOME/.config/opencode/commands/define.md"
test -L "$HOME/.config/opencode/commands/build.md"
test -L "$HOME/.config/opencode/commands/ship.md"
test -f "$HOME/.config/opencode/agents/rose.md"
test -f "$HOME/.config/opencode/skills/rose-memory/SKILL.md"
test -f "$HOME/.config/opencode/commands/ideate.md"
test -f "$HOME/.config/opencode/AGENTS.md"
readlink "$HOME/.config/opencode/AGENTS.md"
readlink "$HOME/.config/opencode/agents/rose.md"
readlink "$HOME/.config/opencode/skills/rose-memory"
readlink "$HOME/.config/opencode/commands/ideate.md"
python "$HOME/.config/opencode/skills/rose-memory/references/memory_cli.py" --help
```

Windows native selective symlink setup:

```powershell
Test-Path "$env:USERPROFILE\code\ai\aili-workflows"
Test-Path "$env:USERPROFILE\.config\opencode\agents"
Test-Path "$env:USERPROFILE\.config\opencode\skills"
Test-Path "$env:USERPROFILE\.config\opencode\commands"
Get-Item "$env:USERPROFILE\.config\opencode\AGENTS.md"
Get-Item "$env:USERPROFILE\.config\opencode\agents\rose.md"
Get-Item "$env:USERPROFILE\.config\opencode\skills\rose-memory"
Get-Item "$env:USERPROFILE\.config\opencode\commands\ideate.md"
```

Copy fallback:

```bash
test -f "$HOME/.config/opencode/agents/rose.md"
test -f "$HOME/.config/opencode/skills/rose-memory/SKILL.md"
test -f "$HOME/.config/opencode/commands/ideate.md"
test -f "$HOME/.config/opencode/AGENTS.md"
python "$HOME/.config/opencode/skills/rose-memory/references/memory_cli.py" --help
```

Required checks for runtime add-on setup:

- OpenCode was fully restarted after installation or runtime configuration changes.
- `/dcp` is available after installing the DCP plugin.
- DCP compression thresholds use documented keys only: `compress.minContextLimit=35%` and `compress.maxContextLimit=45%` when the installed plugin supports percentage values.
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
