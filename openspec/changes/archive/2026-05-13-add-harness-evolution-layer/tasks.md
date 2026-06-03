## 1. Decision and Approval Gates

- [x] 1.1 Record user-provided Q1-Q8 answers and expand this change from `harness-evolution` only to an `add-aili-delivery-harness` umbrella scope.
- [x] 1.2 Write confirmed decisions back into `proposal.md`, `design.md`, `specs/aili-delivery-harness/spec.md`, `specs/harness-evolution/spec.md`, `questionnaire.md`, `tasks.md`, and `test-plan.md`.
- [ ] 1.3 Keep OpenSpec directory rename from `add-harness-evolution-layer` to `add-aili-delivery-harness` blocked unless the user separately approves file/folder move.

## 2. Harness Governance Documents and Protocols

- [x] 2.1 Create `docs/harness/aili-harness-contract.md` as the P0 architecture contract for roles, lifecycle, artifacts, stop rules, failure taxonomy, acceptance, and authority boundaries.
- [x] 2.2 Create `docs/harness/component-map.md` with system-rules, command, skill, subagent-config, memory, tool-policy, middleware/hooks, environment, workflow-pattern, docs/protocol, and install/setup categories.
- [x] 2.3 Create `docs/harness/activation-matrix.md` mapping task types to required, optional, skipped, and approval-gated harness gates.
- [x] 2.4 Create `docs/harness/backend-adapters.md`, `docs/harness/command-lifecycle.md`, `docs/harness/failure-taxonomy.md`, and `docs/harness/tool-policies.md` as short, pointer-rich authority docs.
- [x] 2.5 Create `docs/harness/harness-change-report-template.md` with observed failure/rationale, evidence, affected component, root cause, proposed change, predicted fix, at-risk regression, verification trigger, rollback plan, approval, application status, verdict, and memory/evidence pointer fields.
- [x] 2.6 Create protocol templates under `protocols/`: `idea-brief.md`, `research-evidence-pack.md`, `spec-draft.md`, `alignment-questionnaire.md`, `acceptance-test-plan.md`, `implementation-package.md`, `subagent-task-packet.md`, `subagent-result.md`, `review-report.md`, and `closeout-report.md`.
- [x] 2.7 Create `workflow.components.yaml` indexing authoritative lifecycle, backend, harness-change, protocol, verification, memory, command, and install components.

## 3. Delivery Flow and Harness Evolution Skills

- [x] 3.1 Create `skills/aili-delivery-flow/SKILL.md` with IDEATE, DEFINE, BUILD, and SHIP modes, trigger phrases, stop conditions, backend adapter handling, and concise user-facing output contracts.
- [x] 3.2 Create `skills/aili-delivery-flow/references/lifecycle.md`, `backend-routing.md`, `artifact-contracts.md`, `questionnaire-policy.md`, `test-document-policy.md`, `implementation-packages.md`, and `review-repair-loop.md`.
- [x] 3.3 Create `skills/harness-evolution/SKILL.md` that defaults to producing a report/proposal and does not modify files unless explicit human approval exists.
- [x] 3.4 Create `skills/harness-evolution/references/activation-matrix.md`, `component-taxonomy.md`, `change-report-template.md`, `approval-policy.md`, and `verdict-policy.md`.

## 4. Commands and OpenCode Installation

- [x] 4.1 Create `commands/ideate.md`, `commands/define.md`, `commands/build.md`, and `commands/ship.md` as thin command prompts that route to `aili-delivery-flow` modes.
- [x] 4.2 Confirm no top-level command files are created for `/research`, `/questionnaire`, `/test-plan`, `/implement`, `/fix`, `/debug`, `/review`, or `/evolve`.
- [x] 4.3 Update `scripts/install_opencode.sh` so managed OpenCode installation handles `commands/*.md` in addition to agents and skills.
- [x] 4.4 Update `docs/opencode-setup.md` and `README.md` to document command installation and lifecycle entrypoints without duplicating full flow details.

## 5. Runtime Charter and Shared Guidance Touchpoints

- [x] 5.1 Refactor `agents/rose.md` into Runtime Charter shape while preserving identity/final responsibility, instruction precedence, permission/safety/git boundaries, lifecycle binding, subagent orchestration boundary, memory boundary, verification gate, harness evolution gate, and minimal router.
- [x] 5.2 Update `skills/using-agent-skills/SKILL.md` with a short reference to `aili-delivery-flow` and `harness-evolution` trigger relationships.
- [x] 5.3 Update `skills/parallel-subagent-dispatch/SKILL.md` with a short reference to `protocols/subagent-task-packet.md` and `protocols/subagent-result.md`.
- [x] 5.4 Update `skills/review-pipeline/SKILL.md` and `skills/test-document-generator/SKILL.md` only as needed with short references; do not copy full lifecycle rules.
- [x] 5.5 Update `templates/AGENTS.md` only if a project-level lifecycle pointer is needed; keep it short and avoid duplicating Runtime Charter content.

## 6. Regression Fixtures and Static Runner

- [x] 6.1 Add `docs/harness/fixtures/command-routing-fixtures.yaml` covering `/ideate`, `/define`, `/build`, `/ship` and non-trigger internal stage examples.
- [x] 6.2 Add `docs/harness/fixtures/skill-routing-fixtures.yaml` for `aili-delivery-flow` and `harness-evolution` trigger/non-trigger cases.
- [x] 6.3 Add `docs/harness/fixtures/subagent-dispatch-fixtures.yaml` for packet/result evidence coverage examples.
- [x] 6.4 Add `docs/harness/fixtures/verification-claim-fixtures.yaml` for completion claims with sufficient evidence, insufficient evidence, and `Unverified` handling.
- [x] 6.5 Add `docs/harness/fixtures/agents-template-fixtures.yaml` for AGENTS/template smoke coverage.
- [x] 6.6 Add `scripts/harness_fixture_check.py` using only Python standard library to validate required fixture files/fields and fail on missing required coverage.

## 7. Verification and Closure

- [x] 7.1 Run `openspec status --change "add-harness-evolution-layer"` and `openspec validate "add-harness-evolution-layer" --strict` after OpenSpec artifact updates.
- [x] 7.2 Run `python scripts/harness_fixture_check.py` after fixtures/runner exist.
- [x] 7.3 Run targeted structure checks for commands, skills, protocols, docs, install script, and Runtime Charter references.
- [x] 7.4 Record execution results, skipped checks, unresolved items, and implementation evidence in `test-plan.md`.
- [x] 7.5 Run scoped status/diff review to verify no new dependencies, lockfile changes, SQLite schema changes, automatic commit/push behavior, or unrelated dirty-file edits were introduced.
- [x] 7.6 Record task completion through `rose-memory` with evidence pointers and `--no-durable-memory-promoted` unless the user explicitly approves durable promotion.
