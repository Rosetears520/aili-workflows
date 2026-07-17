---
name: aili-delivery-flow
description: Run the AILI delivery lifecycle for /ideate, /define, /build, and /ship; use for idea shaping, spec/test definition, bounded BUILD package queues, review-repair closeout, or backend routing without exposing internal stage commands.
---

# AILI Delivery Flow

This skill is the workflow authority for the IDEATE, DEFINE, BUILD, and SHIP modes. Commands route here; they do not restate the lifecycle.

## References

- Lifecycle states and hard gates: `references/lifecycle.md`
- Backend adapters: `references/backend-routing.md`
- Artifact outputs: `references/artifact-contracts.md`
- Question handling: `references/questionnaire-policy.md`
- Test document rules: `references/test-document-policy.md`
- Direct versus delegated work: `references/direct-vs-delegated-work.md`
- Build package rules: `references/implementation-packages.md`
- Neutral BUILD execution and loop budgets: `references/build-execution-loop.md`
- Ship review and repair: `references/review-repair-loop.md`
- Protocol templates: `references/protocols/`

## Workflow

### Compact Mode Decision Table

| User intent | Mode | Required gate before continuing | Must not do |
|---|---|---|---|
| One bounded analysis/options outcome satisfying every ordinary condition | IDEATE | classification evidence; no hard trigger | create formal work or edit production code |
| Formal proposal/change/plan, implementation DEFINE, or any hard material trigger | DEFINE | one resolved OpenSpec change; coherent strict artifacts; final test-plan acceptance before BUILD | guess identity, ask per-artifact permission, or implement |
| Explicit implementation of the resolved accepted change | BUILD | current final test-plan acceptance plus target/package/permission/verification/budget gates | execute from acceptance or vague continuation alone |
| Explicit review/repair/closeout of implemented work | SHIP | new SHIP intent plus current implementation evidence; reuse or refresh only affected checks | infer preauthorization, require a broad matrix, or use DEFINE/direct-adapter output as proof |

### 🔴 Red Gates

Stop immediately and report the missing next action when:

- the requested mode is not one of IDEATE, DEFINE, BUILD, or SHIP;
- DEFINE has unresolved material decisions, incoherent/invalid artifacts, or no explicit acceptance of final `test-plan.md`;
- BUILD lacks explicit implementation intent, current final test-plan acceptance, package scope, resolvable ready-target evidence, permission, verification, or valid budget;
- an A33 attachment lacks the exact startup-root admission, identity/topology/rule, operation-class/risk, or fresh operation-approval gate;
- SHIP lacks fresh explicit intent, current implementation evidence, or evidence required by its exact affected claim;
- backend artifacts conflict with lifecycle state or make readiness ambiguous.

1. Apply one semantic classifier to command shortcuts and natural language. Record `ordinary` only when all ordinary conditions hold; record the hard trigger for `formal/material`. Explanation/comparison/translation/status lifecycle words are lexical near misses. A material clause wins conflicting ordinary-only wording, while an explicit no-write clause still controls persistence.
2. Ask exactly one focused question only when one answer changes classification, change identity, target, or authorization. Do not run a generic questionnaire for ordinary work.
3. On the first hard trigger, activate or reuse exactly one Stage-I OpenSpec change. Reuse same accepted scope; create a distinct change only after distinct scope is established; if two remain plausible or the answer is evasive, ask once and write nothing. Later material deltas update the same change.
4. Apply the mode gate before any work:
   - IDEATE explores options and uncertainty; do not edit production code.
   - DEFINE follows current OpenSpec instructions/status dependency order for proposal → specs/design → tasks, automatically writes and re-reads applicable `proposal.md`, specs, `design.md`, `tasks.md`, `interview.md`, `test-plan.md`, and `context.md`, then runs strict validation. `requirements-grilling` solely owns clarification and `interview.md`; `test-document-generator` owns test-plan generation. Final acceptance stays blocked while any unresolved research could change scope, architecture, dependency, public contract, permissions, acceptance, or verification strategy; waiver or accepted-`Unverified` wording cannot clear that material gap.
   - BUILD requires explicit implementation intent and current explicit acceptance of the final `test-plan.md`, plus a resolved ready target (or enough evidence to synthesize a package queue) and coherent validation/target/package/permission/verification/budget gates. BUILD may hydrate accepted evidence, confirm exact locality/contracts, and diagnose bounded failures; open-ended or mature-prior-art research blocks. A discovery changing scope, architecture, dependency, public contract, permissions, acceptance, or verification strategy emits `BUILD_MATERIAL_DISCOVERY`, stops before changed work, and returns to DEFINE writeback/revalidation/reacceptance. BUILD actions derive the queue from the active contract, complete every implementation package with progress-ledger savepoints, then ROSE directly inspects the changed-scope diff and affected task/contract links and runs the smallest sufficient completion check; at most two specialists are optional for a concrete capability gap. In this umbrella change only, Packages 1–11 are implementation history and Package 12 names that direct final inspection. Success records `IMPLEMENTED_TARGETED_VERIFIED` and stops BUILD without an automatic review swarm, test matrix, commit, push, PR, or SHIP transition. Acceptance alone executes nothing.
   - SHIP requires new explicit closeout intent and current implementation evidence. Reuse event-fresh BUILD evidence and select only stale, scope-affected, risk-triggered, integration, packaging, release, merge-result, or target-specific checks; do not rerun a full matrix because phase or time changed.
5. In DEFINE, close applicable local owner/architecture, official/current API/version, mature prior-art, dependency/security/platform, alternatives, and verification-strategy research before final acceptance. Separate source classes and named non-material runtime residuals, then stress-test the plan. Research and stress testing add no proposal approval, waiver, or bundled-artifact gate.
6. Use the artifact/delta contract, persist and re-read answers, and record unknowns instead of guessing.
7. Stop when a hard gate is missing, scope expands, backend evidence conflicts, or required verification cannot run.

## Continuation and compound intent

- `continue`, `继续`, `go ahead`, and `继续做` resume exactly one active authorized envelope with unambiguous target, phase, current gates, and remaining canonical budget. Preserve consumed counters, accounting state, overshoot, and stop state; never broaden authorization, change phase/target, refresh acceptance, or reset budget. Otherwise ask once and do no loop/write/mutation.
- A continuation carrying a material delta returns to DEFINE and never resumes execution. A no-write/chat-only clause overrides formal writeback, continue+delta, and acceptance+BUILD for that turn and yields only a blocked/`Unverified` preview with zero persistence/execution/mutation/acceptance/budget consumption.
- Same-turn acceptance+BUILD persists/classifies acceptance in `interview.md`, updates the final test-plan gate/checklist, re-reads both, then validates every BUILD gate before any execution. No execution-ledger row precedes actual BUILD start.
- Combined BUILD+SHIP intent authorizes only current-phase BUILD. Later SHIP requires fresh evidence and new explicit intent.
- Package savepoints contain `scope`, `files_changed`, `unresolved_items`, `evidence_state`, and `next_package`; they trigger no automatic test, commit, or package approval.
- Commit, push, merge, and release each require exact action-specific approval. CI failure reports the failed target/commit/tree/check and returns control to the user without automatic repair, commit, push, merge, or release.

## Generated OpenSpec adapter boundary

AILI guarantees only its four routes. Current generated `.opencode` `/opsx-*`, apply/continue/archive, and `openspec-*` adapters remain directly callable outside AILI. Do not route or recommend users to them, hand-edit/wrap/suppress/prevent them, alter their generator for control, or treat direct output as AILI evidence. Later AILI work must establish its own current contract, acceptance, and verification; integration/control is Phase II.

## Boundaries

- Only four top-level delivery commands are valid: `/ideate`, `/define`, `/build`, `/ship`.
- `/local-review` is a standalone non-delivery local audit command owned by `local-review-gate`; do not route it through this delivery lifecycle skill as a fifth lifecycle mode.
- Research, questionnaire, test-plan, implementation, debugging, review, repair, and harness evolution are internal stages, not user command entrypoints.
- Anti-entrypoint blacklist: do not expose or invent top-level `/research`, `/questionnaire`, `/test-plan`, `/implement`, `/debug`, `/review`, `/repair`, `/harness`, or backend-specific lifecycle commands.
- Do not register `/loop`, `/schedule`, `/goal`, `/proactive`, `/cycle`, `/watch`, `/objective`, or any other public lifecycle alias. Treat those words only as semantic classifier input. AILI does not own, imitate, bind, modify, or control native `/goal`; its successful behavior is Stage II / N/A. Automation scope blocks under the lifecycle reference.
- Backend-specific task systems store artifacts; they do not weaken lifecycle gates.
- Explicit acceptance of final `test-plan.md` is the sole mandatory lifecycle-level pre-BUILD user gate. Material-decision, coherence, strict-validation, permission, destructive/high-risk, external-operation, and named-risk gates remain separate and cannot be relabeled lifecycle acceptance.
- A33 routing starts only from the user-selected Git startup host. AILI does not rank, move, broadly scan for, or auto-select hosts; every lane targets one declared repository, target rules may only narrow, same-level conflicts block, and artifacts stay in the owning target. A30 external-read routing is historical only.
- A33 text here and in the references is admission/approval policy only. It creates no worktree operation authority: PREPARE has zero add/remove effect, and every real or `driver_fixture` ADD and later non-force REMOVE needs its own fresh exact key/class-bound approval and separate applicable risk gate.

## Verification

- Confirm the selected mode and backend in the response.
- Name the artifact(s) created or updated.
- For BUILD and SHIP, include traceability-backed fresh verification evidence or mark remaining items `Open Question` / `Unverified`.
- For any blocked gate, return the missing approval, artifact, or evidence as the next action.
