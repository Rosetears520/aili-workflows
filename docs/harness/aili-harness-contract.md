# AILI Harness Contract

## Purpose

P0 architecture contract for the `add-aili-delivery-harness` umbrella. It defines where delivery flow, harness governance, evidence, and acceptance rules live without copying every rule into ROSE or command prompts.

## Roles

- **ROSE runtime charter**: final responsibility, instruction precedence, safety, git, memory, subagent, and completion-claim gates.
- **Commands**: thin user entrypoints for `/ideate`, `/define`, `/build`, and `/ship` delivery modes, plus `/local-review` as a standalone local audit command that does not replace SHIP or OpenCode's `/review`.
- **Delivery flow skill**: lifecycle state machine and backend adapter routing.
- **Harness issue triage skill**: read-only localization for user-reported harness behavior problems.
- **Harness evolution skill**: report-first governance for approved harness changes.
- **Protocols**: reusable artifact and subagent evidence contracts under `.agents/skills/aili-delivery-flow/references/protocols/` in this repository.
- **Fixtures and runner**: static smoke coverage for routing and evidence claims.
- **Source classes**: canonical AILI source is distinct from generated/installed adapters, inert upstream references, and upstream runtime behavior.

## Lifecycle Gates

| Mode | Purpose | Stop rule |
|---|---|---|
| IDEATE | Explore unclear ideas and options; surface parallelism/no-parallel reasoning and research-first evidence when they affect the方案 | No production implementation. |
| DEFINE | Produce/align spec, questions, tests, proactive parallelism analysis, and evidence-backed方案 state; OpenSpec interview/test artifacts route through `requirements-grilling` and `test-document-generator` | Stop before build until blockers are answered, waived, or explicitly accepted as `Unverified`. |
| BUILD | Execute complete accepted Package 1–11 behavior with lightweight savepoints, then run Package 12 as the single comprehensive quality gate | Stay inside accepted scope and package boundaries; optional package feedback is not closure, no per-package quality gate is mandatory, and no BUILD pass exists before the Package 12 matrix and joined fresh evidence. |
| SHIP | Verify release-readiness, run release-blocker audit, reconcile review/repair/verification lanes, and close out | No ready/pass claim without fresh release-readiness evidence, resolved/disproven/user-or-active-contract-accepted release blockers, complete join evidence for multi-lane SHIP work, and explicit `Unverified` gaps. |
| LOCAL_REVIEW | Resolve local changes, base branch, commit, PR, or OpenSpec change target and produce a categorized local review report before optional repair | Do not override OpenCode's `/review`, do not mutate remote state, do not repair before a categorized report and explicit approval, and do not claim release or archive readiness. |

## Artifact Authority

- Lifecycle: `.agents/skills/aili-delivery-flow/references/lifecycle.md`.
- Neutral BUILD execution, loop profiles, and canonical budgets: `.agents/skills/aili-delivery-flow/references/build-execution-loop.md`, `.agents/skills/aili-delivery-flow/references/implementation-packages.md`, and `.agents/skills/aili-delivery-flow/references/artifact-contracts.md`.
- Planning evidence shape: `.agents/skills/aili-delivery-flow/references/protocols/research-evidence-pack.md`, plus official-doc and prior-art skills where they are the lighter source.
- Backend adapters: `docs/harness/backend-adapters.md` and `.agents/skills/aili-delivery-flow/references/backend-routing.md`.
- DEFINE interview/test artifacts: `.agents/skills/requirements-grilling/SKILL.md`, `.agents/skills/test-document-generator/SKILL.md`, and `.agents/skills/aili-delivery-flow/references/artifact-contracts.md`.
- Harness issue localization: `.agents/skills/harness-issue-triage/SKILL.md` and `.agents/skills/harness-issue-triage/references/*`.
- Harness governance: `docs/harness/harness-change-report-template.md` and `.agents/skills/harness-evolution/references/*`.
- Subagent packet/result: `.agents/skills/aili-delivery-flow/references/protocols/subagent-task-packet.md`, `.agents/skills/aili-delivery-flow/references/protocols/subagent-result.md`.
- Verification closeout: `.agents/skills/aili-delivery-flow/references/protocols/closeout-report.md`, `docs/harness/fixtures/verification-claim-fixtures.yaml`.

## Source and Runtime Boundary

- Canonical AILI behavior lives in the four delivery commands, top-level canonical skills and protocols, agents, templates/generators, manifests, TypeScript, and installer sources.
- Root `AGENTS.md`, `dist/`, installed OpenCode/shared-skill copies, and current generated `.opencode` OpenSpec direct adapters are downstream generated/installed surfaces. Current direct adapters stay unchanged and callable outside AILI guarantees; AILI does not route to, recommend, wrap, suppress, prevent, or control them, and their output is not AILI evidence.
- Pinned `references/upstream/` closures are licensed inert data. `SKILL.upstream.md` and non-executable upstream scripts never become component-manifest entries, public commands, runnable skills, hooks, or runtime authority.
- External OpenCode, OpenSpec, CodeGraph, and Graphify behavior is upstream runtime behavior. An AILI claim requires an AILI-owned route to apply and freshly record its own gates.

## FIX4/FIX5 Synchronization

- `CONT-005` is the only budget authority. No configured token budget is explicit `null`/no enforcement; requested tokens without reliable pre-start accounting stay non-null/unavailable and block; midrun loss preserves non-null counters and records lost accounting.
- Eligible raw natural-language identity input is NFC-normalized before stable LP resolution. Persisted/already-structured identities must already be raw-NFC compact-JSON UTF-8 canonical bytes. Persisted escape, decomposition, control, newline/NUL, field-order, or whitespace drift is corruption and is never normalized/repaired in place.
- One valid persisted identity key reuses. A different-identity candidate collision is a race and permits one re-read/recomputed `max+1`; a second race, duplicate key/ID, malformed identity, or conflicting body/key is corruption and hard-blocks without write.
- Pure automation modification and mixed modification-plus-documentation requests reject with zero mutation and zero LP. Only a later documentation-only request may define/reuse an external/manual interval/event protocol.

## Package Gate Matrix

| Packages | Required behavior | Quality meaning |
|---|---|---|
| 1–11 | Implement complete assigned behavior in dependency order; preserve exact file ownership and a lightweight savepoint with scope, changed files, unresolved items, and next package | Focused tests/checkers are optional implementation feedback, not package closure or release readiness |
| 12 | Audit all 74 task rows exactly once, run the fresh mandatory command matrix, join diverse non-nesting review lanes without voting, and perform at most three holistic repair/retest/re-review cycles | The single mandatory comprehensive quality/convergence gate; unresolved gaps block SHIP |

Cross-root execution is fail-closed against exact OpenCode `1.17.18` behavior. Current ask/always/`--auto`, Task-root, role-overlay, symlink/TOCTOU, subprocess/bash, secret, and neighboring-root runtime evidence remains `Unverified`; root approval is not hard containment. Graphify is a separate explicitly approved operation, and missing controls mean no process start. The OpenCode `1.17.18` recursive installed-catalog result for inert upstream reference data remains `UV-005`; distribution/registration/enablement and release readiness must not be claimed while catalog or required `0644` mode evidence is unresolved.

## Stop Rules

- Do not rename the OpenSpec change directory without separate approval.
- Do not add internal top-level commands for research, questionnaire, test-plan, implement, fix, debug, `/review`, release-blocker audit, or evolve; `/local-review` is the only AILI-owned public review command allowed by the local review gate contract.
- Do not hide cross-entrypoint proactive parallel planning, research-first planning evidence, or requested packaging gates solely inside long protocol text when a thin command/ROSE surface needs to expose the stop condition.
- Do not modify SQLite schema, lockfiles, dependency manifests, or memory DBs in this phase.
- Do not apply core harness edits without approved scope and verification trigger.
- Do not add `/loop`, `/schedule`, `/goal`, `/proactive`, `/cycle`, `/watch`, `/objective`, worktree-maintenance, or Graphify commands, or cron/scheduler/watcher/webhook/listener/daemon/queue/dependency/hook/auto-retry runtime.

## Acceptance

- Required docs, protocols, fixtures, index, and static runner exist.
- `python scripts/harness_fixture_check.py` passes.
- Any completed OpenSpec task is backed by file evidence and verification evidence.
