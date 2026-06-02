---
name: agents-md-initialization
description: Create, update, or validate a project-local AGENTS.md from the shared AILI template when initializing or checking repository agent rules.
---

# AGENTS.md Initialization

## Non-Negotiable Rule

Project `AGENTS.md` must be created from `templates/AGENTS.md`.

Do not write a project `AGENTS.md` from scratch.

Use the bundled script:

```bash
python "$AILI_HOME/scripts/agents_md.py" init --project .
```

Define `AILI_HOME` as the absolute path to the local `aili-workflows` clone. If `AILI_HOME` is unset, ask the user for the clone path or infer it safely from the current repository context; do not assume a fixed home-directory location.

## Commands

Initialize a project-local `AGENTS.md`:

```bash
python "$AILI_HOME/scripts/agents_md.py" init --project .
```

Update only AILI managed blocks:

```bash
python "$AILI_HOME/scripts/agents_md.py" update --project .
```

Check template compliance:

```bash
python "$AILI_HOME/scripts/agents_md.py" check --project .
```

## Workflow

1. Run `init` when the target project has no `AGENTS.md`.
2. If `AGENTS.md` already exists, do not overwrite it silently. Use `update` for managed blocks, or ask before using `init --strategy backup-overwrite`.

   🛑 **STOP before overwrite or backup-overwrite:** show the existing path, state that project-local content may be replaced outside managed blocks, and wait for explicit human approval.

3. Inspect the repository and fill only project-specific sections:
   - `Project Overview`
   - `Setup Commands`
   - `Architecture and Project Structure`
   - `Project-Specific Rules`
4. Do not remove or weaken the `Agent Operating Discipline` managed block.
5. Run `check` before completion.

## Fallbacks and Stop Conditions

| Trigger condition | First response | If still unresolved |
|---|---|---|
| `templates/AGENTS.md` is missing or unreadable | Stop and report the expected template path; do not hand-write `AGENTS.md` | Ask the user to restore the template or provide the correct `AILI_HOME` |
| `scripts/agents_md.py` is missing or not executable by Python | Stop and report the expected script path and command attempted | Ask for the correct clone path; do not create a replacement script |
| `AILI_HOME` is unset and cannot be inferred from the current repo | Ask the user for the absolute local `aili-workflows` clone path | Do not assume a home-directory path |
| Existing `AGENTS.md` has unrecognized local content outside managed blocks | Prefer `update`; summarize preserved local sections before editing | Require explicit approval before any backup-overwrite strategy |
| `check` fails after init/update | Report the failing output and inspect only the relevant sections | Do not claim completion until `check` passes or the failure is marked unresolved |

## CI / Pre-Commit Gate

Target projects should add a lightweight check when practical:

```bash
python "$AILI_HOME/scripts/agents_md.py" check --project .
```

For `Makefile` projects:

```makefile
check-agents:
	python "$(AILI_HOME)/scripts/agents_md.py" check --project .
```

For pre-commit hooks:

```bash
#!/usr/bin/env bash
python "$AILI_HOME/scripts/agents_md.py" check --project .
```

## Verification

Report:

- whether `init`, `update`, or `check` was used
- whether an existing `AGENTS.md` was backed up
- which project-specific sections were filled
- the final `check` result
