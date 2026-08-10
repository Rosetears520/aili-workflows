# AILI Harness Contract

## Purpose

P0 architecture contract for the `add-aili-delivery-harness` umbrella. It defines where delivery flow, harness governance, evidence, and acceptance rules live without copying every rule into ROSE or command prompts.

## Roles

- **ROSE runtime charter**: final responsibility, instruction precedence, safety, git, memory, subagent, and completion-claim gates.
- **Commands**: four Delivery Commands (`/ideate`, `/define`, `/build`, `/ship`) and six Utility Commands (`/local-review`, `/handoff`, `/agents-md`, `/harness-audit`, `/retro`, `/security-review`). Utilities are explicit non-lifecycle operations and do not own acceptance or final verdicts.
- **Delivery flow skill**: one semantic router/control plane for first-class natural-language and shortcut lifecycle/ordinary loops, approvals, directed hydration, proactive delegation scans, and verification ownership.
- **Harness issue triage skill**: read-only localization for user-reported harness behavior problems.
- **Harness evolution skill**: report-first governance for approved harness changes.
- **Protocols**: versioned package, Agent-selection, and formal-Board schemas under `core/protocols/`; lifecycle, artifact, and human-readable subagent guidance under `.agents/skills/aili-delivery-flow/references/`, with practical selection guidance under `.agents/skills/parallel-subagent-dispatch/references/`.
- **Fixtures and runner**: static smoke coverage for routing and evidence claims.
- **Source classes**: canonical AILI source is distinct from generated/installed adapters, inert upstream references, and upstream runtime behavior.
- **Managed role inventory**: exactly primary ROSE plus 19 repository-managed subagents. All 19 managed profiles retain `external_directory: deny`; ROSE alone retains per-operation ask. `web-researcher` remains the web-only external-research role and gains no external local-directory, mutation, or delegation authority.

## Natural-Language and Delegation Routing

- Treat unambiguous natural-language IDEATE, DEFINE, BUILD, and SHIP requests as first-class entries to the same canonical loops. Never require slash syntax; ask one focused mode/target question only for genuine ambiguity.
- Run a proactive delegation scan at the start of each non-trivial intent and whenever changed evidence exposes a new work split. When an existing Task trigger is met, dispatch before duplicating that assignment directly unless overlap, dependency, permission, ownership, or negative-benefit evidence blocks delegation.
- Default concurrency is at most two but is not a hard cap. ROSE chooses any larger bounded fan-out from independent non-overlapping units, concrete benefit, suitable owners, and an explicit join plan; ready lanes launch together rather than being avoidably serialized.
- Ordinary work uses trigger/benefit routing after assignment-shape classification; formal ready Agent-owned packages use their exact `aili-agent-selection/v1` role unless a valid waiver was recorded before direct execution. The shared package contract supports one-shot and persistent adapters, while the current OpenCode Task adapter remains fresh, terminal, and non-resumable. Preserve no nested delegation, no automatic retry, no permission broadening, and no unconditional review/test/security swarm. ROSE remains the decision, integration, inspection, verification, disposition, and final-verdict owner.

## Lifecycle Gates

| Mode | Purpose | Stop rule |
|---|---|---|
| IDEATE | Run the delegation scan, then explore unclear ideas and options; work directly only when no Task trigger is met or delegation is concretely blocked | No production implementation. |
| DEFINE | Produce only dependency-ready spec/question/test artifacts; `requirements-grilling` and `test-document-generator` are bounded artifact adapters and do not auto-chain | Stop before BUILD until exact material/evidence blockers are resolved, required artifacts are coherent/valid, and the user accepts one final test plan. |
| BUILD | Derive the accepted queue from the active contract, execute each implementation package with progress-ledger savepoints, then run one minimal changed-scope completion check | No automatic package test/commit/approval; success records `IMPLEMENTED_TARGETED_VERIFIED` and stops before SHIP. This umbrella alone names Packages 1–11 plus Package 12. |
| SHIP | Reuse still-covering BUILD evidence, run the delegation scan, and refresh only evidence required by the affected closeout claim | Fresh explicit SHIP intent is required; direct inspection is the no-trigger/blocked fallback, no broad matrix/lane fanout exists without a concrete gap, and CI failure returns without automatic repair/Git action. |
| LOCAL_REVIEW | Resolve local changes, base branch, commit, PR, or OpenSpec change target and produce a categorized local review report before optional repair | Do not override OpenCode's `/review`, do not mutate remote state, do not repair before a categorized report and explicit approval, and do not claim release or archive readiness. |
| Utility Commands | Run the explicitly requested local-review, handoff, AGENTS, harness-audit, retrospective, or security-review operation | Do not create a lifecycle phase, grant acceptance/verification authority, or bypass the action-specific placement, external-operation, destructive-operation, or privacy gate. |

## Artifact Authority

- Lifecycle: `.agents/skills/aili-delivery-flow/references/lifecycle.md`.
- Canonical Agent selection schema: `core/protocols/aili-agent-selection.v1.schema.json` (`aili-agent-selection/v1`); practical role matrix: `.agents/skills/parallel-subagent-dispatch/references/agent-selection-matrix.md`.
- Formal package/evidence Board schema: `core/protocols/aili-task-board.v1.schema.json` (`aili-task-board/v1`); human-readable Board guidance: `.agents/skills/aili-delivery-flow/references/formal-task-board.md`.
- Neutral BUILD execution, loop profiles, and canonical budgets: `.agents/skills/aili-delivery-flow/references/build-execution-loop.md`, `.agents/skills/aili-delivery-flow/references/implementation-packages.md`, and `.agents/skills/aili-delivery-flow/references/artifact-contracts.md`.
- Planning evidence shape: `.agents/skills/aili-delivery-flow/references/protocols/research-evidence-pack.md`, plus official-doc and prior-art skills where they are the lighter source.
- Backend adapters: `docs/harness/backend-adapters.md` and `.agents/skills/aili-delivery-flow/references/backend-routing.md`.
- DEFINE interview/test artifacts: `.agents/skills/requirements-grilling/SKILL.md`, `.agents/skills/test-document-generator/SKILL.md`, and `.agents/skills/aili-delivery-flow/references/artifact-contracts.md`.
- Harness issue localization: `.agents/skills/harness-issue-triage/SKILL.md` and `.agents/skills/harness-issue-triage/references/*`.
- Harness governance: `docs/harness/harness-change-report-template.md` and `.agents/skills/harness-evolution/references/*`.
- Subagent packet/result: `core/protocols/package-envelope.schema.json`, `.agents/skills/aili-delivery-flow/references/protocols/subagent-task-packet.md`, and `.agents/skills/aili-delivery-flow/references/protocols/subagent-result.md`.
- Verification closeout: `.agents/skills/aili-delivery-flow/references/protocols/closeout-report.md`, `docs/harness/fixtures/verification-claim-fixtures.yaml`.

## Source and Runtime Boundary

- Canonical AILI behavior lives in `core/commands/` for all ten Commands, `core/protocols/` for versioned shared schemas, top-level canonical skills, agents, templates/generators, manifests, TypeScript, and installer sources. Root `commands/` are generated compatibility projections, not independent semantic owners.
- Root `AGENTS.md`, `dist/`, installed OpenCode/shared-skill copies, and current generated `.opencode` OpenSpec direct adapters are downstream generated/installed surfaces. Current direct adapters stay unchanged and callable outside AILI guarantees; AILI does not route to, recommend, wrap, suppress, prevent, or control them, and their output is not AILI evidence.
- Pinned `references/upstream/` closures are licensed inert data. `SKILL.upstream.md` and non-executable upstream scripts never become component-manifest entries, public commands, runnable skills, hooks, or runtime authority.
- External OpenCode, OpenSpec, CodeGraph, and Graphify behavior is upstream runtime behavior. An AILI claim requires an AILI-owned route to apply and freshly record its own gates.

## FIX4/FIX5 Synchronization

- `CONT-005` is the only budget authority. No configured token budget is explicit `null`/no enforcement; requested tokens without reliable pre-start accounting stay non-null/unavailable and block; midrun loss preserves non-null counters and records lost accounting.
- Eligible raw natural-language identity input is NFC-normalized before stable LP resolution. Persisted/already-structured identities must already be raw-NFC compact-JSON UTF-8 canonical bytes. Persisted escape, decomposition, control, newline/NUL, field-order, or whitespace drift is corruption and is never normalized/repaired in place.
- One valid persisted identity key reuses. A different-identity candidate collision is a race and permits one re-read/recomputed `max+1`; a second race, duplicate key/ID, malformed identity, or conflicting body/key is corruption and hard-blocks without write.
- Hidden/unrequested AILI background lifecycle automation and mixed hidden-automation-plus-protocol requests block with zero mutation and zero LP, while explicit product/repository CI, cron, scheduler, webhook/listener, queue, daemon, hook, dependency, or auto-retry remains eligible through normal formal/high-risk gates; vocabulary-only comparison is ordinary. Documentation-only AILI interval/event definitions create no runtime or lifecycle permission.

## A33 Static Admission and Approval Gates

- `WT-001` has historical non-gating mode `a30-a31-external-read` and current mode `a33-attached-shared-trust-domain`. A30 runtime results and A32/item-41 readiness evidence are stale/historical and cannot prove current A33 readiness.
- The user-selected startup root must be Git. Destination is exactly `<session-root>/.worktrees/<repo_key>/<worktree_key>` and the exact prospective destination must be ignored through root `/.worktrees/` with no re-inclusion or tracked destination.
- Keys use `^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$`; reserved/path/control/newline/NUL values and collisions block with no suffix, guess, force, `-B`, orphan, remote guess, or implicit ref. Source/path/submodule topology must be trusted and unambiguous.
- One host may declare multiple attachments, but every repository lane separately references one current WT context and keeps exact keys, host/source/target identity, target rules, operation approval, CodeGraph evidence, and owning-repository artifact destination distinct. Cross-attachment copy/rebind and broad host scans block.
- `A33Identity` is no-digest and has all and only: `identity_state`, `declared_root`, `path_state`, `canonical_root`, `git_toplevel`, `git_private_dir`, `git_common_dir`, `git_head`, `git_branch`, `detached_head`, `worktree_membership`, `dirty_state`, `tracked_files`, `untracked_files`, `ignored_files`, `artifact_files`, `unknown_files`. Host/source are populated; ADD target is absent→populated and REMOVE target is populated→absent.
- Host/source/target identity evidence remains distinct; target rules are re-read at every operation/dispatch boundary, narrow only, and same-level conflict blocks. Branch, base ref, `existing|create` mode, and source `enabled|disabled` reflog policy are explicit. User-visible artifacts stay in the owning target repository.
- PREPARE performs no add/remove. Every real or `driver_fixture` ADD and later non-force REMOVE has a separate fresh exact key/class-bound approval. ADD needs accepted trusted-code risk; observed REMOVE uses `trusted_code_risk:not_applicable` only under its separate complete deletion-inventory/risk gate.
- Only the declared admin entry/membership and branch-mode/reflog-policy-authorized ADD ref transaction may change. REMOVE retains branch ref/reflog; common-dir path identity and unrelated/prunable state remain unchanged. Rollback preserves worktrees/evidence. These text/fixture gates grant no operation authority.
- The host and attachments are an explicitly trusted same-owner, same-sensitivity, mutually readable/writable trust domain. OpenCode path/cwd/permission rules are a soft coordination boundary, not hard isolation, sandboxing, DLP, network isolation, or arbitrary-process containment.
- Root `.worktrees/`, visible `worktrees/`, and historical `.tmp/worktrees/` remain outside the npm package allowlist. A33 adds no helper registry/manifest, public attach/cleanup command, host selector, or maintenance plane.

## Package Gate Matrix

| Packages | Required behavior | Quality meaning |
|---|---|---|
| Active-contract implementation packages | Implement complete assigned behavior in dependency order; preserve exact file ownership and a progress-ledger savepoint with `scope`, `files_changed`, `unresolved_items`, `evidence_state`, and `next_package` | Tests/checkers are risk/need-triggered feedback, not automatic savepoint work, package approval, closure, or release readiness |
| Active-contract completion package | ROSE directly inspects changed-scope diff and affected requirement/task links, runs the smallest sufficient check, optionally uses one auxiliary capability for a concrete gap, and permits one targeted repair/recheck | Record `IMPLEMENTED_TARGETED_VERIFIED` or a blocker and stop BUILD; Package 12 is this umbrella's historical name only |

Cross-root execution is fail-closed against exact OpenCode `1.17.18` behavior. Current ask/always/`--auto`, Task-root, role-overlay, symlink/TOCTOU, subprocess/bash, secret, and neighboring-root runtime evidence remains `Unverified`; root approval is not hard containment. Graphify is a separate explicitly approved operation, and missing controls mean no process start. The OpenCode `1.17.18` recursive installed-catalog result for inert upstream reference data remains `UV-005`; distribution/registration/enablement and release readiness must not be claimed while catalog or required `0644` mode evidence is unresolved.

## Stop Rules

- Do not rename the OpenSpec change directory without separate approval.
- Do not add internal top-level commands for research, questionnaire, test-plan, implement, fix, debug, `/review`, release-blocker audit, or evolve; `/local-review` is the only AILI-owned public review command. Do not add `/aili-doctor` or `/simplify`.
- Do not add proactive parallelism/research/review ceremony to thin command surfaces; expose only the current material decision or exact risky-operation stop condition.
- Do not modify SQLite schema, lockfiles, dependency manifests, or memory DBs in this phase.
- Do not apply core harness edits without approved scope and verification trigger.
- Do not add `/loop`, `/schedule`, `/goal`, `/proactive`, `/cycle`, `/watch`, `/objective`, worktree-maintenance, or Graphify commands, or hidden/unrequested AILI cron/scheduler/watcher/webhook/listener/daemon/queue/dependency/hook/auto-retry runtime. This does not blanket-reject explicitly scoped product/repository automation that passes its formal/high-risk gates.

## Acceptance

- Required current owners and artifacts are structurally coherent.
- The active change selects its accepted smallest static/runtime checks; this architecture document imposes no fixture suite or full matrix.
- Any completion claim is backed by affected-file links and fresh claim-matched evidence; model behavior remains `Unverified` when only static evidence exists.
