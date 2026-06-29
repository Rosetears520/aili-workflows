# AILI Harness Contract

## Purpose

P0 architecture contract for the `add-aili-delivery-harness` umbrella. It defines where delivery flow, harness governance, evidence, and acceptance rules live without copying every rule into ROSE or command prompts.

## Roles

- **ROSE runtime charter**: final responsibility, instruction precedence, safety, git, memory, subagent, and completion-claim gates.
- **Commands**: thin user entrypoints for `/ideate`, `/define`, `/build`, `/ship` only.
- **Delivery flow skill**: lifecycle state machine and backend adapter routing.
- **Harness issue triage skill**: read-only localization for user-reported harness behavior problems.
- **Harness evolution skill**: report-first governance for approved harness changes.
- **Protocols**: reusable artifact and subagent evidence contracts under `.agents/skills/aili-delivery-flow/references/protocols/` in this repository.
- **Fixtures and runner**: static smoke coverage for routing and evidence claims.

## Lifecycle Gates

| Mode | Purpose | Stop rule |
|---|---|---|
| IDEATE | Explore unclear ideas and options; surface parallelism/no-parallel reasoning and research-first evidence when they affect the方案 | No production implementation. |
| DEFINE | Produce/align spec, questions, tests, proactive parallelism analysis, and evidence-backed方案 state; OpenSpec interview/test artifacts route through `change-interviewer` and `test-document-generator` | Stop before build until blockers are answered, waived, or explicitly accepted as `Unverified`. |
| BUILD | Dispatch bounded implementation packages or synthesize a package queue from one resolved ready target, then run local quality gates and requested packaging gates | Stay inside approved scope and package boundaries; no BUILD pass without code-review/test evidence, security evidence or a skip reason, and package evidence or blocker when packaging was requested. |
| SHIP | Verify release-readiness, run release-blocker audit, reconcile review/repair/verification lanes, and close out | No ready/pass claim without fresh release-readiness evidence, resolved/disproven/user-or-active-contract-accepted release blockers, complete join evidence for multi-lane SHIP work, and explicit `Unverified` gaps. |

## Artifact Authority

- Lifecycle: `.agents/skills/aili-delivery-flow/references/lifecycle.md`.
- BUILD goal mode: `.agents/skills/aili-delivery-flow/references/build-goal-mode.md` and `.agents/skills/aili-delivery-flow/references/implementation-packages.md`.
- Planning evidence shape: `.agents/skills/aili-delivery-flow/references/protocols/research-evidence-pack.md`, plus official-doc and prior-art skills where they are the lighter source.
- Backend adapters: `docs/harness/backend-adapters.md` and `.agents/skills/aili-delivery-flow/references/backend-routing.md`.
- DEFINE interview/test artifacts: `.agents/skills/change-interviewer/SKILL.md`, `.agents/skills/test-document-generator/SKILL.md`, and `.agents/skills/aili-delivery-flow/references/artifact-contracts.md`.
- Harness issue localization: `.agents/skills/harness-issue-triage/SKILL.md` and `.agents/skills/harness-issue-triage/references/*`.
- Harness governance: `docs/harness/harness-change-report-template.md` and `.agents/skills/harness-evolution/references/*`.
- Subagent packet/result: `.agents/skills/aili-delivery-flow/references/protocols/subagent-task-packet.md`, `.agents/skills/aili-delivery-flow/references/protocols/subagent-result.md`.
- Verification closeout: `.agents/skills/aili-delivery-flow/references/protocols/closeout-report.md`, `docs/harness/fixtures/verification-claim-fixtures.yaml`.

## Stop Rules

- Do not rename the OpenSpec change directory without separate approval.
- Do not add internal top-level commands for research, questionnaire, test-plan, implement, fix, debug, review, release-blocker audit, or evolve.
- Do not hide cross-entrypoint proactive parallel planning, research-first planning evidence, or requested packaging gates solely inside long protocol text when a thin command/ROSE surface needs to expose the stop condition.
- Do not modify SQLite schema, lockfiles, dependency manifests, or memory DBs in this phase.
- Do not apply core harness edits without approved scope and verification trigger.

## Acceptance

- Required docs, protocols, fixtures, index, and static runner exist.
- `python scripts/harness_fixture_check.py` passes.
- Any completed OpenSpec task is backed by file evidence and verification evidence.
