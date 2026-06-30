## Why

The current workflow harness is strong at lifecycle gating, but the IDEATE evidence found several gaps that now need a formal implementation contract:

- Skills should have a cross-tool shared substrate under `.agents/skills`, while OpenCode-native `.opencode`/global installation behavior remains intact.
- Testing and QA are currently concentrated in a broad `test-engineer` lane; ECC prior art shows useful specialized testing agents and skills for coverage review, PR test analysis, AI regression, silent failure detection, browser QA, and E2E artifact handling.
- Code-Spec-Plugin prior art shows that AILI should make requirement-to-task-to-file-to-verification traceability explicit instead of leaving it implicit in prose.
- Local evidence shows stale generated project facts in `AGENTS.md`, installer/source-of-truth logic spread across scripts, TypeScript, docs, manifests, and package metadata, and no local `.agents/` shared layer.
- CodeGraph is not initialized in this repository, so the change should define an explicit readiness/doctor/init boundary rather than silently assuming graph coverage.
- DeerFlow public skills provide useful clean-room patterns for skill trigger design, progressive disclosure, research synthesis, skill validation, and artifact/report discipline, but should not be copied verbatim without license/provenance handling.

## What Changes

- Migrate the repository-managed skills source into `.agents/skills` while preserving existing OpenCode-native installation surfaces and behavior through generated/copied/adapted OpenCode outputs.
- Strengthen the component manifest into the install/package source of truth for agents, skills, commands, shared skill targets, and future adapter outputs.
- Add the full requested QA/testing agent+skill expansion as in-scope: test coverage review, PR test analysis, AI regression scouting, silent failure hunting, browser QA, and E2E artifact handling.
- Absorb Code-Spec-Plugin patterns as AILI traceability contracts: requirement/decision/risk → task → file/artifact → verification command/evidence → spec coverage check.
- Fix stale project-local AGENTS facts through the generated-source path (`templates/AGENTS.md` and generation/check scripts), not by treating generated `AGENTS.md` as an independent source.
- Add doctor/readiness behavior for CodeGraph: detect uninitialized project indexes, report the current repository root, and offer/record an explicit project-local init path without running it implicitly during DEFINE.
- Absorb DeerFlow public skills through explicit provenance handling: derivative copying is allowed for selected skills when license/notice/provenance are recorded and DeerFlow-specific placeholders or runtime names receive the smallest necessary AILI/OpenCode adaptation.

## Capabilities

### New Capabilities

- `quality-assurance-lanes`: Specialized QA/testing agents and skills with routing, permission, evidence, artifact, and review-pipeline integration requirements.

### Modified Capabilities

- `aili-installer`: Shared `.agents/skills` target, manifest authority, package inclusion, doctor/readiness checks, and install source-of-truth behavior.
- `aili-four-command-lifecycle`: Traceability and spec coverage check across DEFINE/BUILD/SHIP artifacts.
- `agent-operating-discipline`: Generated AGENTS freshness and upstream pattern absorption policy.
- `codegraph-evidence-provider`: Project-local CodeGraph readiness and initialization reporting boundaries.

## Impact

- Likely BUILD implementation targets: `manifests/rose-aili.components.json`, `src/manifest.ts`, `src/installer.ts`, `src/doctor.ts`, `scripts/install_opencode.sh`, `package.json`, `.gitignore`, `docs/opencode-setup.md`, `README.md`, `templates/AGENTS.md`, generated `AGENTS.md`, `scripts/agents_md.py`, `agents/`, `.agents/skills/`, `.agents/skills/review-pipeline/SKILL.md`, `.agents/skills/test-document-generator/SKILL.md`, `.agents/skills/aili-delivery-flow/**`, and relevant tests/fixtures. Installed OpenCode runtime targets continue to use `skills/<name>` where explicitly described.
- Expected verification: OpenSpec strict validation, TypeScript build/typecheck/test, installer dry-run tests, package allowlist tests, AGENTS template check, harness fixture checks, shell syntax, Python compile/checks, npm pack dry-run if package metadata changes, and targeted review/test/security lanes.
- The change should leave `.playwright-mcp/` and other unrelated untracked state untouched.

## Non-goals

- Do not implement production changes during DEFINE.
- Do not standardize on `.agent/` singular.
- Do not remove OpenCode-native `.opencode` or global config installation behavior.
- Do not copy DeerFlow/ECC/Code-Spec-Plugin prompts, code, scripts, assets, or docs without license/provenance tracking, notices where required, and task-scoped AILI/OpenCode adaptation.
- Do not globally enable hooks, browser automation, E2E mutation, deploy, external provider uploads, or destructive test data behavior by default.
- Do not initialize CodeGraph automatically during DEFINE.
- Do not add new public lifecycle commands beyond `/ideate`, `/define`, `/build`, and `/ship`.

## Build Readiness

Status: `READY` after the user filled the generated `interview.md`, accepted the `test-plan.md` scope, and OpenSpec validation passed. Remaining implementation risks are tracked as BUILD-time verification items rather than DEFINE blockers.
