# Delivery Lifecycle

AILI delivery has four public modes. The mode gate is mandatory even when a backend contains tasks that appear ready to execute.

## Lifecycle Hydration Gate

Before DEFINE, BUILD, SHIP, or normal-chat continuation acts on an active delivery thread, refresh current state from artifacts and memory instead of treating command invocations as isolated silos. Read the active idea capsule or `ideas/workflow-inbox.md` entry when relevant, backend-specific `context.md`, specs/design/tasks, `interview.md`, `test-plan.md`, `progress.txt`, `implementation-notes.html` when present, closeout/review artifacts relevant to the scope, and memory/checkpoints. Summarize the current goal, confirmed decisions, rejected options, open questions, `Unverified` items, progress/checkpoint state, drift notes, evidence anchors, and next action before changing scope, readiness, implementation, or release-readiness claims.

## IDEATE

Use when the idea is unclear, broad, or competing options exist.

- Inputs: user goal, constraints, existing context.
- Actions: explore alternatives, identify assumptions, collect evidence needs. When repository/code evidence is needed and the relevant files are not already known, delegate broad search to `code-scout` first and base conclusions on returned evidence anchors rather than intuition. When a candidate idea should be preserved without formalizing a change, write a lightweight idea capsule or update backend-neutral `ideas/workflow-inbox.md` if artifact placement is allowed.
- Outputs: idea brief, option list, open questions, recommended next mode, and optional idea capsule or `ideas/workflow-inbox.md` update.
- Hard stop: no production code or harness file edits.
- Do not create a formal OpenSpec proposal by default during pure IDEATE; DEFINE promotes only selected ideas into backend-specific change artifacts.

## DEFINE

Use when the goal is plausible but not ready to implement.

- Inputs: idea brief, preserved idea capsule or inbox entry when relevant, issue/spec notes, code/docs evidence, and hydrated prior context.
- Actions: draft or update spec, questionnaire/interview, acceptance test document, backend-specific `context.md`, and task/readiness artifacts. For OpenSpec-backed changes, use the OpenSpec backend for proposal/design/spec/tasks, route `interview.md` through `change-interviewer`, route `test-plan.md` through `test-document-generator`, and maintain `openspec/changes/<change-id>/context.md`.
- Outputs: confirmed scope, unresolved questions, confirmed decisions, rejected options, test expectations, artifacts created/updated, and build-readiness status: `READY`, `BLOCKED`, `WAIVED`, or `UNVERIFIED`.
- Hard stop: do not implement until spec/questionnaire/test document gates are user-confirmed, explicitly waived, or explicitly accepted as `UNVERIFIED`.

## BUILD

Use when implementation is explicitly approved. A user `/build` invocation is approval to execute the resolved ready work item in autonomous goal mode unless the command text or project rules narrow that approval.

- Inputs: approved ready work item or explicit package, acceptance criteria, forbidden scope, BUILD review lanes, backend-specific `context.md`, existing `progress.txt`, `implementation-notes.html` when present, and any backend artifacts that define tasks or readiness. `UNVERIFIED` or waived readiness must be accepted by the current active contract, not inferred from stale conversation context.
- Actions: apply the hydration gate; re-read relevant DEFINE artifacts from disk; check `context.md` and `implementation-notes.html` for drift; infer the target repository root from the active backend/change context; synthesize an ordered implementation package queue when no explicit package is supplied; establish a scoped BUILD goal marker/contract when continuation is needed; supervise dynamic worker increments package-by-package; reconcile compact worker reports/evidence; update `progress.txt` as ROSE-only ledger for current progress, user feedback/corrections, checkpoints, evidence, verification/review/security state, blockers, decisions, and next action; maintain `implementation-notes.html` only for spec deviations/interpretation, temporary decisions, trade-offs, open questions, unverified assumptions, and required DEFINE write-back; repair bounded failures; then run independent local quality gates: code review, test verification, and security review when security surfaces are present.
- Outputs: target resolved, package queue summary, scoped goal marker/contract summary when used, completed and blocked packages, changed files, progress-ledger entries or skip reason, drift-log entries or skip reason, verification evidence or compact evidence packs, review findings and resolutions, skipped-lane reasons, residual risks.
- Hard stop: pause on ambiguous or missing target, missing approval/readiness evidence that is not explicitly waived by the current active contract, target repository outside the current workspace or allowed external directories without explicit approval, scope expansion, forbidden file edits, high-risk operations requiring explicit approval, unverifiable acceptance criteria, unavailable required local review lanes, or exhausted repair limits. Do not pause solely because the user omitted a manual implementation package; synthesize the queue instead.

## SHIP

Use after BUILD is complete enough to evaluate for handoff, merge, release, or archive.

- Inputs: implementation result, BUILD review/test/security evidence, backend-specific `context.md`, `progress.txt` and `implementation-notes.html` when present, review targets, release-blocker audit target or target request, named baseline/previous-release reference when requested, verification commands, closeout expectations.
- Actions: apply the hydration gate; resolve and report the release-blocker audit target, defaulting to the current resolved change or final diff when no broader target is requested; ask for a missing baseline rather than guessing; re-check evidence freshness plus `context.md` and `implementation-notes.html` drift; reuse fresh BUILD evidence when it still covers the final diff and scoped risks; rerun only stale, scope-affected, risk-triggered, or release-readiness-specific lanes; audit diff/scope/artifacts for user-impacting regressions, security or permission exposure, unsafe/destructive workflow behavior, data-loss risk, artifact inconsistency, stale or missing evidence, unresolved review/test/security findings, and unverified acceptance criteria; classify findings; summarize noisy release-readiness evidence with compact evidence packs; verify release or handoff readiness; prepare closeout.
- Outputs: BUILD gate status, release-blocker audit target and finding classifications, release-readiness summary, final evidence or compact evidence packs, closeout report, archive/sync/memory/PR/release next steps when approved. Ambiguous "archive" or "归档" requests require target confirmation before compression or file writes.
- Hard stop: do not claim ready without fresh evidence, resolved/disproven/explicitly user-or-active-contract-accepted `release-blocking` findings, a non-guessed baseline when baseline comparison is requested, and explicit `Unverified` items.

## Change Revision Decision

When bugs or adjustments appear after a lifecycle pass:

- Same intent, overlapping scope, and not archived: update the current change, add repair tasks, and update `test-plan.md` defect/fix coverage.
- Additional implementation requested after BUILD: re-enter the BUILD-style test/repair/retest loop for the changed scope before completion.
- Same scope after SHIP but before archive: repair the current change and rerun affected code-review, test, and security lanes.
- Archived, merged, or released: create a new fix change and reference the source change instead of rewriting history.
- Workflow, command, skill, memory, subagent, installer, or tool-policy defect: route through `harness-issue-triage` and then approved `harness-evolution`.
