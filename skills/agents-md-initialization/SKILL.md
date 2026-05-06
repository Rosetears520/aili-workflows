---
name: agents-md-initialization
description: Create, update, or validate a project-local AGENTS.md from the shared AILI template. Use when initializing project rules, running OpenCode /init-style setup, or checking AGENTS.md compliance.
---

# AGENTS.md Initialization

## Non-Negotiable Rule

Project `AGENTS.md` must be created from `templates/AGENTS.md`.

Do not write a project `AGENTS.md` from scratch.

Use the bundled script:

```bash
python ~/code/ai/aili-workflows/scripts/agents_md.py init --project .
```

If this repository is installed somewhere else, use that clone path instead of `~/code/ai/aili-workflows`.

## Commands

Initialize a project-local `AGENTS.md`:

```bash
python ~/code/ai/aili-workflows/scripts/agents_md.py init --project .
```

Update only AILI managed blocks:

```bash
python ~/code/ai/aili-workflows/scripts/agents_md.py update --project .
```

Check template compliance:

```bash
python ~/code/ai/aili-workflows/scripts/agents_md.py check --project .
```

## Workflow

1. Run `init` when the target project has no `AGENTS.md`.
2. If `AGENTS.md` already exists, do not overwrite it silently. Use `update` for managed blocks, or ask before using `init --strategy backup-overwrite`.
3. Inspect the repository and fill only project-specific sections:
   - `Project Overview`
   - `Setup Commands`
   - `Architecture and Project Structure`
   - `Project-Specific Rules`
4. Do not remove or weaken the `Agent Operating Discipline` managed block.
5. Run `check` before completion.

## CI / Pre-Commit Gate

Target projects should add a lightweight check when practical:

```bash
python ~/code/ai/aili-workflows/scripts/agents_md.py check --project .
```

For `Makefile` projects:

```makefile
check-agents:
	python ~/code/ai/aili-workflows/scripts/agents_md.py check --project .
```

For pre-commit hooks:

```bash
#!/usr/bin/env bash
python ~/code/ai/aili-workflows/scripts/agents_md.py check --project .
```

## Verification

Report:

- whether `init`, `update`, or `check` was used
- whether an existing `AGENTS.md` was backed up
- which project-specific sections were filled
- the final `check` result
