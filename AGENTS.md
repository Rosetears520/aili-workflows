<!-- AILI_AGENTS_TEMPLATE_VERSION: 2 -->
<!-- AILI_AGENTS_TEMPLATE_SOURCE: templates/AGENTS.md -->
<!-- AILI_AGENTS_TEMPLATE_MODE: generated-project-local-file -->

# AGENTS.md

This file is the project-level instruction contract for AI coding agents working in this repository.

It contains project facts, local commands, local artifact placement, and repository-specific exceptions. Reusable workflow and safety invariants are installed globally by `rose-aili` from `templates/opencode-global-AGENTS.md`.

Do not copy broad global operating rules into this file unless this project intentionally overrides or strengthens them.

## Project Overview

- Project purpose: Personal OpenCode workflow repository containing the `rose-aili` TypeScript/Node CLI, agents, skills, delivery commands, templates, docs, and helper scripts.
- Primary language/runtime: TypeScript on Node.js 20.19+, Markdown, Python 3, and Bash helper scripts.
- Package manager: npm with tracked `package.json` and `package-lock.json`; install dependencies with `npm ci`.
- Main application entry points: `src/cli.ts`, `src/installer.ts`, `src/doctor.ts`, `commands/{ideate,define,build,ship}.md`, `agents/rose.md`, `.agents/skills/*/SKILL.md`, `scripts/install_opencode.sh`, and `scripts/agents_md.py`.
- Main test framework: Node's built-in test runner via `tests/rose-aili.test.mjs`, plus Python stdlib smoke checks via `scripts/harness_fixture_check.py` and `scripts/agents_md.py check`.
- Important directories: `src/`, `agents/`, `.agents/skills/`, `commands/`, `templates/`, `scripts/`, `docs/`, `tests/`, and `manifests/`.
- Generated/build output directories: `dist/`, `node_modules/`, `memory/`, `.opencode/`, `.codegraph/`, `.playwright-mcp/`, `openspec/`, `__pycache__/`, and `*.py[cod]` are ignored local/runtime outputs.
- Deployment/runtime environment: `rose-aili` runs through npm/npx or a local Node build; OpenCode global config is installed through the CLI or `scripts/install_opencode.sh`; repository scripts run on Linux/macOS/WSL shells with Node.js 20.19+, npm, Python 3, and Bash.

## Setup Commands

- Install dependencies: `npm ci`.
- Start development server: not applicable; this is an OpenCode workflow/config repository.
- Build: `npm run build`.
- Lint: `bash -n scripts/install_opencode.sh` for the installer shell syntax.
- Typecheck: `npm run typecheck` and `python -m py_compile scripts/harness_fixture_check.py scripts/agents_md.py`.
- Test all: `npm test`, `python scripts/harness_fixture_check.py`, and `python scripts/agents_md.py check --project .`.
- Test focused: `python scripts/agents_md.py check --project .` for AGENTS template compliance; `npm run build && node --test tests/*.test.mjs` for Node CLI behavior.
- Format: no formatter command documented.
- Clean: no clean command documented.

## Architecture and Project Structure

- `src/`: TypeScript source for the `rose-aili` CLI, installer/update/doctor flows, manifest handling, and OpenCode config merge helpers.
- `tests/`: tracked Node test suite covering CLI/install/config/manifest behavior.
- `docs/`: OpenCode setup and harness architecture/fixture documentation.
- `scripts/`: Python, Bash, and Node utilities for AGENTS generation/checking, harness fixture smoke checks, OpenCode installation, and CLI executable packaging.
- Configuration files: `package.json`, `package-lock.json`, `tsconfig.json`, `.gitignore`, `workflow.components.yaml`, `manifests/rose-aili.components.json`, `templates/AGENTS.md`, command prompts, agent prompts, and skill definitions.
- CI/CD files: `.github/workflows/ci.yml` and `.github/workflows/release.yml`; no `Makefile` is present.
- Generated files: project-local `AGENTS.md` is generated from `templates/AGENTS.md`; runtime/local state is ignored in `memory/`, `.opencode/`, and `openspec/`.
- External integrations: OpenCode global config, npm package execution/publishing, GitHub repository URL in `scripts/install_opencode.sh`, optional OpenSpec/CodeGraph setup, and optional skills with third-party provenance listed in `README.md`.

## Project-Specific Rules

- Keep `/ideate`, `/define`, `/build`, and `/ship` as the only top-level delivery command entrypoints.
- Root `AGENTS.md` is repo-specific and must keep the v2 template markers/section schema without copying global rules; validate compliance with `scripts/agents_md.py`.

## Project-Specific Testing and Artifact Placement

- Unit tests: Node test files under `tests/` using `node --test` after `npm run build`.
- Integration tests: CLI/install behavior is covered by `tests/rose-aili.test.mjs` with temporary OpenCode homes.
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
