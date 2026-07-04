---
name: agents-md-initialization
description: Create, update, or validate a project-local AGENTS.md from the shared AILI template when initializing or checking repository agent rules.
metadata:
  tool: references/agents_md.py
  template: references/agents-template.md
---

# AGENTS.md Initialization

## Non-Negotiable Rule

Project `AGENTS.md` must be created from the bundled AILI AGENTS template.

Do not write a project `AGENTS.md` from scratch.

Use the bundled script:

```bash
python ~/.agents/skills/agents-md-initialization/references/agents_md.py init --project .
```

The script and template are distributed with this skill:

- `references/agents_md.py`
- `references/agents-template.md`

If this skill is being run from a repository checkout rather than an installed OpenCode skill, use the repository-local path:

```bash
python .agents/skills/agents-md-initialization/references/agents_md.py init --project .
```

## Commands

Initialize a project-local `AGENTS.md`:

```bash
python ~/.agents/skills/agents-md-initialization/references/agents_md.py init --project .
```

Update an existing generated project `AGENTS.md` against the current template-managed content:

```bash
python ~/.agents/skills/agents-md-initialization/references/agents_md.py update --project .
```

Check template compliance:

```bash
python ~/.agents/skills/agents-md-initialization/references/agents_md.py check --project .
```

If the global installed path is unavailable but the current repository contains this skill, replace the path prefix with `.agents/skills/agents-md-initialization/`.

## Workflow

1. Run `init` when the target project has no `AGENTS.md`.
2. If `AGENTS.md` already exists, do not overwrite it silently. Use `update` for template-managed compatibility updates, or ask before using `init --strategy backup-overwrite`.

   🛑 **STOP before overwrite or backup-overwrite:** show the existing path, state that project-local content may be replaced outside managed blocks, and wait for explicit human approval.

3. Inspect the repository and fill only project-specific sections:
   - `Project Overview`
   - `Setup Commands`
   - `Architecture and Project Structure`
   - `Project-Specific Rules`
   - `Project-Specific Testing and Artifact Placement`
   - `Local Overrides`
4. Do not copy broad global workflow/safety rules into the project file unless the project intentionally strengthens or specializes them.
5. Check CodeGraph readiness for the same target project after confirming the repository root:
   - run or request `codegraph status` for the target project
   - if CodeGraph is not initialized, ask whether to run `codegraph init -i` in that repository
   - if approved, run `codegraph init -i` and then `codegraph status`
   - if CodeGraph is unavailable, skipped, or not approved, report it as a non-blocking follow-up
   - do not initialize multiple repositories and do not run `openspec init` as part of this flow
6. Run `check` before completion.

## Fallbacks and Stop Conditions

| Trigger condition | First response | If still unresolved |
|---|---|---|
| `references/agents-template.md` is missing or unreadable | Stop and report the expected bundled template path; do not hand-write `AGENTS.md` | Ask the user to restore/reinstall the skill or provide an approved template source |
| `references/agents_md.py` is missing or not executable by Python | Stop and report the expected bundled script path and command attempted | Ask the user to restore/reinstall the skill; do not create a replacement script in the target project |
| Installed skill path is unavailable but a repository checkout is present | Use `.agents/skills/agents-md-initialization/references/agents_md.py` from the checkout | If neither installed nor repo-local bundled script exists, stop and ask for the AILI workflow checkout path |
| Existing `AGENTS.md` has unrecognized local content outside managed blocks | Prefer `update`; summarize preserved local sections before editing | Require explicit approval before any backup-overwrite strategy |
| CodeGraph is not installed, unavailable, or user declines initialization | Report CodeGraph as skipped/unavailable/not approved | Do not block `AGENTS.md` completion; do not claim code-map coverage |
| `check` fails after init/update | Report the failing output and inspect only the relevant sections | Do not claim completion until `check` passes or the failure is marked unresolved |

## CI / Pre-Commit Gate

Target projects should add a lightweight check when practical:

```bash
python ~/.agents/skills/agents-md-initialization/references/agents_md.py check --project .
```

For `Makefile` projects:

```makefile
check-agents:
	python "$${HOME}/.agents/skills/agents-md-initialization/references/agents_md.py" check --project .
```

For pre-commit hooks:

```bash
#!/usr/bin/env bash
python "$HOME/.agents/skills/agents-md-initialization/references/agents_md.py" check --project .
```

## Verification

Report:

- whether `init`, `update`, or `check` was used
- whether an existing `AGENTS.md` was backed up
- which project-specific sections were filled
- CodeGraph status: initialized / initialized this run / skipped / unavailable / not approved
- the final `check` result
