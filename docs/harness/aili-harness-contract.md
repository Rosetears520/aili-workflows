# AILI Harness Contract

## Purpose

P0 architecture contract for the `add-aili-delivery-harness` umbrella. It defines where delivery flow, harness governance, evidence, and acceptance rules live without copying every rule into ROSE or command prompts.

## Roles

- **ROSE runtime charter**: final responsibility, instruction precedence, safety, git, memory, subagent, and completion-claim gates.
- **Commands**: thin user entrypoints for `/ideate`, `/define`, `/build`, `/ship` only.
- **Delivery flow skill**: lifecycle state machine and backend adapter routing.
- **Harness issue triage skill**: read-only localization for user-reported harness behavior problems.
- **Harness evolution skill**: report-first governance for approved harness changes.
- **Protocols**: reusable artifact and subagent evidence contracts under `skills/aili-delivery-flow/references/protocols/`.
- **Fixtures and runner**: static smoke coverage for routing and evidence claims.

## Lifecycle Gates

| Mode | Purpose | Stop rule |
|---|---|---|
| IDEATE | Explore unclear ideas and options | No production implementation. |
| DEFINE | Produce/align spec, questions, and tests | Stop before build until blockers are answered or waived. |
| BUILD | Dispatch bounded implementation packages and local quality gates | Stay inside approved scope and package boundaries; no BUILD pass without code-review/test evidence and security evidence or a skip reason. |
| SHIP | Verify release-readiness and close out | No ready/pass claim without fresh release-readiness evidence; mark residual gaps as `Unverified`. |

## Artifact Authority

- Lifecycle: `skills/aili-delivery-flow/references/lifecycle.md`.
- Backend adapters: `docs/harness/backend-adapters.md` and `skills/aili-delivery-flow/references/backend-routing.md`.
- Harness issue localization: `skills/harness-issue-triage/SKILL.md` and `skills/harness-issue-triage/references/*`.
- Harness governance: `docs/harness/harness-change-report-template.md` and `skills/harness-evolution/references/*`.
- Subagent packet/result: `skills/aili-delivery-flow/references/protocols/subagent-task-packet.md`, `skills/aili-delivery-flow/references/protocols/subagent-result.md`.
- Verification closeout: `skills/aili-delivery-flow/references/protocols/closeout-report.md`, `docs/harness/fixtures/verification-claim-fixtures.yaml`.

## Stop Rules

- Do not rename the OpenSpec change directory without separate approval.
- Do not add internal top-level commands for research, questionnaire, test-plan, implement, fix, debug, review, or evolve.
- Do not modify SQLite schema, lockfiles, dependency manifests, or memory DBs in this phase.
- Do not apply core harness edits without approved scope and verification trigger.

## Acceptance

- Required docs, protocols, fixtures, index, and static runner exist.
- `python scripts/harness_fixture_check.py` passes.
- Any completed OpenSpec task is backed by file evidence and verification evidence.
