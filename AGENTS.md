<!-- AILI_AGENTS_TEMPLATE_VERSION: 2 -->
<!-- AILI_AGENTS_TEMPLATE_SOURCE: templates/AGENTS.md -->
<!-- AILI_AGENTS_TEMPLATE_MODE: generated-project-local-file -->

# AGENTS.md

This file is the project-level instruction contract for AI coding agents working in this repository.

It contains project facts, local commands, local artifact placement, and repository-specific exceptions. Reusable workflow and safety invariants are installed globally by `rose-aili` from `templates/opencode-global-AGENTS.md`.

Do not copy broad global operating rules into this file unless this project intentionally overrides or strengthens them.

## Project Overview

- Project purpose: Personal OpenCode workflow repository containing agents, skills, delivery commands, templates, docs, and helper scripts.
- Primary language/runtime: Markdown plus Python 3 and Bash helper scripts.
- Package manager: None for the tracked repository; `.opencode/package*.json` is ignored local OpenCode runtime state.
- Main application entry points: `commands/{ideate,define,build,ship}.md`, `agents/rose.md`, `skills/*/SKILL.md`, `scripts/install_opencode.sh`, and `scripts/agents_md.py`.
- Main test framework: Python stdlib smoke checks via `scripts/harness_fixture_check.py` and `scripts/agents_md.py check`.
- Important directories: `agents/`, `commands/`, `skills/`, `templates/`, `scripts/`, `docs/`, `tests/`, and `manifests/`.
- Generated/build output directories: none documented; `memory/`, `.opencode/`, `openspec/`, `__pycache__/`, and `*.py[cod]` are ignored local/runtime outputs.
- Deployment/runtime environment: OpenCode global config installed through `scripts/install_opencode.sh`; repository scripts run on Linux/macOS/WSL shells with Python 3.

## Setup Commands

- Install dependencies: no tracked dependency install documented.
- Start development server: not applicable; this is an OpenCode workflow/config repository.
- Build: no build command documented.
- Lint: `bash -n scripts/install_opencode.sh` for the installer shell syntax.
- Typecheck: `python -m py_compile scripts/harness_fixture_check.py scripts/agents_md.py`.
- Test all: `python scripts/harness_fixture_check.py` and `python scripts/agents_md.py check --project .`.
- Test focused: `python scripts/agents_md.py check --project .` for AGENTS template compliance.
- Format: no formatter command documented.
- Clean: no clean command documented.

## Architecture and Project Structure

- `src/`: no `src/` directory is present.
- `tests/`: present but no tracked tests were found during initialization.
- `docs/`: OpenCode setup and harness architecture/fixture documentation.
- `scripts/`: Python and Bash utilities for AGENTS generation/checking, harness fixture smoke checks, and OpenCode installation.
- Configuration files: `.gitignore`, `workflow.components.yaml`, `templates/AGENTS.md`, command prompts, agent prompts, and skill definitions.
- CI/CD files: no `.github/workflows/` or `Makefile` was found during initialization.
- Generated files: project-local `AGENTS.md` is generated from `templates/AGENTS.md`; runtime/local state is ignored in `memory/`, `.opencode/`, and `openspec/`.
- External integrations: OpenCode global config, GitHub repository URL in `scripts/install_opencode.sh`, and optional skills with third-party provenance listed in `README.md`.

## Project-Specific Rules

- Keep `/ideate`, `/define`, `/build`, and `/ship` as the only top-level delivery command entrypoints.
- Project `AGENTS.md` must remain generated from `templates/AGENTS.md`; validate template compliance with `scripts/agents_md.py`.

## Project-Specific Testing and Artifact Placement

- Unit tests: no convention documented.
- Integration tests: no convention documented.
- CLI tests: use repository scripts under `scripts/` and harness fixtures under `docs/harness/fixtures/`.
- API / contract tests: no API test convention documented.
- GUI / browser / Playwright tests: no browser test convention documented.
- Test fixtures: `docs/harness/fixtures/`.
- Snapshots / golden files: no convention documented.
- Test reports / traces / screenshots: no repository-local report path documented.
- Temporary test output: OS temp is allowed only for ephemeral scratch/cache data that users do not need to open, review, or reference.

Rules:

- Do not place new test files in the repository root unless this section explicitly allows it.
- Unless the user explicitly requests an external or temporary-only artifact, user-visible test files, test plans, reports, traces, screenshots, generated fixtures, golden files, and verification artifacts must be written inside the repository at a project-defined path or after a placement decision.
- Do not introduce `playwright.config.*`, `tests/e2e/`, `e2e/`, screenshots, traces, browser fixtures, or browser reports without first confirming the intended location.
- If a new test category is introduced, ask the user for its location once, then record the chosen convention here.
- OpenSpec test documents belong in `openspec/changes/<change-id>/test-plan.md`.
- Non-OpenSpec test documents require an explicit placement decision before writing.

## Local Overrides

- None documented.
