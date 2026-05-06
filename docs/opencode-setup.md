# OpenCode Setup

This document is for an AI agent installing `Rosetears520/aili-workflows` into OpenCode.

The default installation model is symlink-based:

- clone this repository once into a stable local path;
- link OpenCode global `agents/` and `skills/` entries to the cloned repository;
- update by running `git pull` in the cloned repository;
- keep project state, memory databases, and project `AGENTS.md` files inside each target project.

Do not copy agents and skills by default. Copy only as a fallback when symlinks are unavailable or explicitly requested.

## Goal

Install ROSE agents and skills for OpenCode while keeping:

- workflow source synced with this repository;
- OpenCode global config lightweight;
- project memory local to each project;
- project `AGENTS.md` self-contained and project-specific.

Never store project memory inside the global OpenCode config directory.

## Default Paths

Recommended repository location:

```bash
~/code/ai/aili-workflows
```

OpenCode global config paths:

```bash
# Linux/macOS/WSL
~/.config/opencode/

# Windows native OpenCode
%USERPROFILE%\.config\opencode\
```

OpenCode uses plural config subdirectories such as:

```text
agents/
skills/
commands/
plugins/
```

## What This Repository Provides

- `agents/rose.md` - ROSE primary agent.
- `agents/implementer.md` - focused implementation subagent.
- `agents/code-reviewer.md` - code review subagent.
- `agents/security-auditor.md` - security review subagent.
- `agents/test-engineer.md` - testing subagent.
- `skills/*/SKILL.md` - OpenCode skills.
- `skills/rose-memory/` - ROSE project-local SQLite memory skill and CLI.
- `skills/agents-md-initialization/` - project `AGENTS.md` initialization workflow.
- `templates/AGENTS.md` - single source template for project-local `AGENTS.md` files.
- `scripts/agents_md.py` - `init`, `update`, and `check` tool for generated project `AGENTS.md` files.

There are no required slash commands or installer scripts. Natural language plus OpenCode's native skill discovery is the intended workflow.

## Installation Modes

Choose one mode based on the user's environment.

### Mode A: Managed Symlink Setup

Use this when the user wants the full ROSE workflow and does not need to preserve unrelated existing global OpenCode agents or skills.

This mode links the entire `agents/` and `skills/` directories.

```bash
AILI_HOME="${AILI_HOME:-$HOME/code/ai/aili-workflows}"
OPENCODE_HOME="${OPENCODE_HOME:-$HOME/.config/opencode}"

git clone https://github.com/Rosetears520/aili-workflows.git "$AILI_HOME" 2>/dev/null || git -C "$AILI_HOME" pull --ff-only

mkdir -p "$OPENCODE_HOME"

# Back up existing real directories before replacing them with symlinks.
if [ -e "$OPENCODE_HOME/agents" ] && [ ! -L "$OPENCODE_HOME/agents" ]; then
  mv "$OPENCODE_HOME/agents" "$OPENCODE_HOME/agents.backup.$(date +%Y%m%d%H%M%S)"
fi

if [ -e "$OPENCODE_HOME/skills" ] && [ ! -L "$OPENCODE_HOME/skills" ]; then
  mv "$OPENCODE_HOME/skills" "$OPENCODE_HOME/skills.backup.$(date +%Y%m%d%H%M%S)"
fi

ln -sfn "$AILI_HOME/agents" "$OPENCODE_HOME/agents"
ln -sfn "$AILI_HOME/skills" "$OPENCODE_HOME/skills"
```

Result:

```text
~/.config/opencode/agents -> ~/code/ai/aili-workflows/agents
~/.config/opencode/skills -> ~/code/ai/aili-workflows/skills
```

Update later:

```bash
git -C "$AILI_HOME" pull --ff-only
```

### Mode B: Non-Destructive Selective Symlink Setup

Use this when the user already has unrelated global OpenCode agents or skills and wants to add ROSE without replacing those directories.

```bash
AILI_HOME="${AILI_HOME:-$HOME/code/ai/aili-workflows}"
OPENCODE_HOME="${OPENCODE_HOME:-$HOME/.config/opencode}"

git clone https://github.com/Rosetears520/aili-workflows.git "$AILI_HOME" 2>/dev/null || git -C "$AILI_HOME" pull --ff-only

mkdir -p "$OPENCODE_HOME/agents" "$OPENCODE_HOME/skills"

# Link agent files.
for file in "$AILI_HOME"/agents/*.md; do
  name="$(basename "$file")"
  target="$OPENCODE_HOME/agents/$name"

  if [ -e "$target" ] && [ ! -L "$target" ]; then
    mv "$target" "$target.backup.$(date +%Y%m%d%H%M%S)"
  fi

  ln -sfn "$file" "$target"
done

# Link skill directories.
for dir in "$AILI_HOME"/skills/*; do
  [ -d "$dir" ] || continue
  name="$(basename "$dir")"
  target="$OPENCODE_HOME/skills/$name"

  if [ -e "$target" ] && [ ! -L "$target" ]; then
    mv "$target" "$target.backup.$(date +%Y%m%d%H%M%S)"
  fi

  ln -sfn "$dir" "$target"
done
```

Result examples:

```text
~/.config/opencode/agents/rose.md -> ~/code/ai/aili-workflows/agents/rose.md
~/.config/opencode/skills/rose-memory -> ~/code/ai/aili-workflows/skills/rose-memory
```

This mode preserves unrelated existing global agents and skills.

### Mode C: Copy Fallback

Use copy mode only when symlinks are unavailable, blocked by permissions, or explicitly requested.

Copy mode does not auto-sync with future repository updates.

```bash
AILI_HOME="${AILI_HOME:-$HOME/code/ai/aili-workflows}"
OPENCODE_HOME="${OPENCODE_HOME:-$HOME/.config/opencode}"

git clone https://github.com/Rosetears520/aili-workflows.git "$AILI_HOME" 2>/dev/null || git -C "$AILI_HOME" pull --ff-only

mkdir -p "$OPENCODE_HOME/agents" "$OPENCODE_HOME/skills"

cp -R "$AILI_HOME/agents/"*.md "$OPENCODE_HOME/agents/"
cp -R "$AILI_HOME/skills/"* "$OPENCODE_HOME/skills/"
```

## Windows Native Setup

Use this only when OpenCode is running natively in Windows.

PowerShell:

```powershell
$AiliHome = "$env:USERPROFILE\code\ai\aili-workflows"
$OpenCodeHome = "$env:USERPROFILE\.config\opencode"

if (!(Test-Path $AiliHome)) {
  git clone https://github.com/Rosetears520/aili-workflows.git $AiliHome
} else {
  git -C $AiliHome pull --ff-only
}

New-Item -ItemType Directory -Force -Path $OpenCodeHome | Out-Null

if ((Test-Path "$OpenCodeHome\agents") -and !((Get-Item "$OpenCodeHome\agents").LinkType)) {
  Rename-Item "$OpenCodeHome\agents" "agents.backup.$(Get-Date -Format yyyyMMddHHmmss)"
}

if ((Test-Path "$OpenCodeHome\skills") -and !((Get-Item "$OpenCodeHome\skills").LinkType)) {
  Rename-Item "$OpenCodeHome\skills" "skills.backup.$(Get-Date -Format yyyyMMddHHmmss)"
}

New-Item -ItemType SymbolicLink -Force -Path "$OpenCodeHome\agents" -Target "$AiliHome\agents"
New-Item -ItemType SymbolicLink -Force -Path "$OpenCodeHome\skills" -Target "$AiliHome\skills"
```

CMD alternative:

```cmd
mklink /D "%USERPROFILE%\.config\opencode\agents" "%USERPROFILE%\code\ai\aili-workflows\agents"
mklink /D "%USERPROFILE%\.config\opencode\skills" "%USERPROFILE%\code\ai\aili-workflows\skills"
```

If directory symbolic links are blocked by Windows permissions, use directory junctions as a fallback:

```cmd
mklink /J "%USERPROFILE%\.config\opencode\agents" "%USERPROFILE%\code\ai\aili-workflows\agents"
mklink /J "%USERPROFILE%\.config\opencode\skills" "%USERPROFILE%\code\ai\aili-workflows\skills"
```

## WSL Rule

If OpenCode runs inside WSL, install and link inside WSL:

```text
~/code/ai/aili-workflows
~/.config/opencode/
```

Do not link WSL OpenCode config to `%USERPROFILE%\.config\opencode\` unless the user explicitly wants a mixed Windows/WSL setup.

## Project AGENTS.md Rule

Do not symlink this repository's `AGENTS.md` into each target project's root by default.

Project `AGENTS.md` files must be generated from this repository's `templates/AGENTS.md`, then filled with project-specific commands and conventions, and committed to that project.

Use symlinks for reusable global ROSE agents and skills. Use project-local generated files for project-specific instructions.

Use the `agents-md-initialization` skill for this flow. The skill should call the script instead of writing `AGENTS.md` by hand:

```bash
AILI_HOME="${AILI_HOME:-$HOME/code/ai/aili-workflows}"

python "$AILI_HOME/scripts/agents_md.py" init --project .
python "$AILI_HOME/scripts/agents_md.py" check --project .
```

If a target project already has `AGENTS.md`, do not overwrite it silently. Use managed-block update or explicitly back up before overwrite:

```bash
python "$AILI_HOME/scripts/agents_md.py" update --project .
python "$AILI_HOME/scripts/agents_md.py" init --project . --strategy backup-overwrite
```

Recommended target-project CI/pre-commit gate:

```bash
python ~/code/ai/aili-workflows/scripts/agents_md.py check --project .
```

## Optional Third-Party Setup

Only install third-party tools if the user asks for them or if they are clearly required by the task.

Available optional integrations:

- OpenCode DCP plugin: install globally from `@tarquinen/opencode-dcp@latest`.
- OpenCode shell strategy: clone `https://github.com/JRedeker/opencode-shell-strategy.git` into a stable local path and reference it from OpenCode config.
- Playwright MCP: register `npx @playwright/mcp@latest`, disabled by default unless the user asks to enable it.
- Context7: run its OpenCode setup or register Context7 MCP, disabled by default unless the user asks to enable it.

Do not vendor third-party plugin source into this repository unless the user explicitly decides to vendor it.

## OpenCode Behavior

This repository follows an agent-driven model similar to `addyosmani/agent-skills`:

- Skills are selected automatically by intent.
- `AGENTS.md` or the active primary agent should require skill usage when a skill applies.
- Slash commands are not required.
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

For managed symlink setup:

```bash
test -L ~/.config/opencode/agents
test -L ~/.config/opencode/skills
test -f ~/.config/opencode/agents/rose.md
test -f ~/.config/opencode/skills/rose-memory/SKILL.md
python ~/.config/opencode/skills/rose-memory/references/memory_cli.py --help
```

For selective symlink setup:

```bash
test -L ~/.config/opencode/agents/rose.md
test -L ~/.config/opencode/skills/rose-memory
test -f ~/.config/opencode/agents/rose.md
test -f ~/.config/opencode/skills/rose-memory/SKILL.md
python ~/.config/opencode/skills/rose-memory/references/memory_cli.py --help
```

For copy fallback:

```bash
test -f ~/.config/opencode/agents/rose.md
test -f ~/.config/opencode/skills/rose-memory/SKILL.md
python ~/.config/opencode/skills/rose-memory/references/memory_cli.py --help
```

Required checks for third-party setup:

- Existing `opencode.json` was backed up before edits.
- New config was merged, not overwritten.
- Playwright MCP and Context7 MCP are disabled by default unless the user asked otherwise.

## Update

For symlink setup, update the cloned repository:

```bash
git -C ~/code/ai/aili-workflows pull --ff-only
```

No reinstall is needed unless new optional third-party integrations were added or the user wants to change installation mode.

For copy fallback, update requires copying files again.

## Report Back

After setup, report:

- which mode was chosen and why
- repository clone path
- linked or copied agents and skills
- backup files created
- global config changes
- verification results
- update command
- anything skipped because it was optional, unavailable, or not requested
