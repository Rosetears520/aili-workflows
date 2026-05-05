# OpenCode Setup

This document is for an AI agent installing `Rosetears520/aili-workflows` into OpenCode.

The setup is intentionally document-driven. Do not assume a fixed installer command. Inspect the user's environment, choose the smallest useful install, and copy/configure only what the user needs.

## Goal

Install ROSE agents and skills for OpenCode while keeping project state local.

Default target paths:

- Linux/macOS global config: `~/.config/opencode/`
- Windows global config: `%USERPROFILE%\.config\opencode\`
- Project memory state: `<project>/memory/memory.db`

Never store project memory inside the global OpenCode config directory.

## What This Repository Provides

- `agents/rose.md` - ROSE primary agent.
- `agents/implementer.md` - focused implementation subagent.
- `agents/code-reviewer.md` - code review subagent.
- `agents/security-auditor.md` - security review subagent.
- `agents/test-engineer.md` - testing subagent.
- `skills/*/SKILL.md` - OpenCode skills.
- `skills/rose-memory/` - ROSE project-local SQLite memory skill and CLI.

There are no required slash commands or installer scripts. Natural language plus the `skill` tool is the intended workflow.

## Installation Modes

Choose one mode based on the user's request.

### Mode A: ROSE Full Setup

Use this when the user wants the full ROSE workflow.

Copy:

- `agents/*.md` to the global OpenCode `agents/` directory.
- `skills/*` to the global OpenCode `skills/` directory.

Do not overwrite unrelated existing agents or skills without checking the target file names first.

### Mode B: Skills Only

Use this when the user already has an agent and only wants reusable skills.

Copy:

- selected `skills/<name>/` directories, or
- all `skills/*` if the user asks for the complete skill collection.

### Mode C: ROSE Memory Only

Use this when the user only wants project-local memory continuity.

Copy:

- `skills/rose-memory/` to the global OpenCode `skills/` directory.

The CLI lives at:

`~/.config/opencode/skills/rose-memory/references/memory_cli.py`

Use a direct Python call:

```bash
python ~/.config/opencode/skills/rose-memory/references/memory_cli.py --help
```

## Optional Third-Party Setup

Only install third-party tools if the user asks for them or if they are clearly required by the task.

Available optional integrations:

- OpenCode DCP plugin: install globally from `@tarquinen/opencode-dcp@latest`.
- OpenCode shell strategy: clone `https://github.com/JRedeker/opencode-shell-strategy.git` into global OpenCode config and add its instruction file to `opencode.json` `instructions`.
- Playwright MCP: register `npx @playwright/mcp@latest`, disabled by default unless the user asks to enable it.
- Context7: run its OpenCode setup or register Context7 MCP, disabled by default unless the user asks to enable it.

Do not vendor third-party plugin source into this repository.

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

When a project needs ROSE memory, initialize it in that project only:

```bash
mkdir -p memory
python ~/.config/opencode/skills/rose-memory/references/memory_cli.py init --db memory/memory.db
python ~/.config/opencode/skills/rose-memory/references/memory_cli.py doctor --db memory/memory.db --record
```

Rules:

- Do not create `memory.md` or JSON sidecars.
- Do not edit `memory/memory.db` manually.
- Do not copy `memory/memory.db` into global config.
- If a `rose-memory` command already exists, it may replace the direct Python command.

## Verification

After copying files, verify only the pieces that were installed.

Required checks for ROSE Full Setup:

- Global `agents/rose.md` exists.
- Global `agents/implementer.md` exists.
- Global `skills/rose-memory/SKILL.md` exists.
- Global `skills/rose-memory/references/memory_cli.py` exists.
- The memory CLI prints help successfully.

Required checks for Skills Only:

- Each selected `skills/<name>/SKILL.md` exists in the global OpenCode skills directory.

Required checks for third-party setup:

- Existing `opencode.json` was backed up before edits.
- New config was merged, not overwritten.
- Playwright MCP and Context7 MCP are disabled by default unless the user asked otherwise.

## Report Back

After setup, report:

- which mode was chosen and why
- copied agents and skills
- any global config changes
- any backup files created
- verification results
- anything skipped because it was optional, unavailable, or not requested
