# Delivery Lifecycle

AILI delivery has four public modes. The mode gate is mandatory even when a backend contains tasks that appear ready to execute.

## IDEATE

Use when the idea is unclear, broad, or competing options exist.

- Inputs: user goal, constraints, existing context.
- Actions: explore alternatives, identify assumptions, collect evidence needs. When repository/code evidence is needed and the relevant files are not already known, delegate broad search to `code-scout` first and base conclusions on returned evidence anchors rather than intuition.
- Outputs: idea brief, option list, open questions, recommended next mode.
- Hard stop: no production code or harness file edits.

## DEFINE

Use when the goal is plausible but not ready to implement.

- Inputs: idea brief, issue/spec notes, code/docs evidence.
- Actions: draft or update spec, questionnaire/interview, acceptance test document, and task/readiness artifacts. For OpenSpec-backed changes, use the OpenSpec backend for proposal/design/spec/tasks, route `interview.md` through `change-interviewer`, and route `test-plan.md` through `test-document-generator`.
- Outputs: confirmed scope, unresolved questions, test expectations, artifacts created/updated, and build-readiness status: `READY`, `BLOCKED`, `WAIVED`, or `UNVERIFIED`.
- Hard stop: do not implement until spec/questionnaire/test document gates are user-confirmed, explicitly waived, or explicitly accepted as `UNVERIFIED`.

## BUILD

Use when implementation is explicitly approved. A user `/build` invocation is approval to execute the resolved ready work item in autonomous goal mode unless the command text or project rules narrow that approval.

- Inputs: approved ready work item or explicit package, acceptance criteria, forbidden scope, BUILD review lanes, and any backend artifacts that define tasks or readiness. `UNVERIFIED` or waived readiness must be accepted by the current active contract, not inferred from stale conversation context.
- Actions: re-read relevant DEFINE artifacts from disk, infer the target repository root from the active backend/change context, synthesize an ordered implementation package queue when no explicit package is supplied, dispatch bounded implementation work package-by-package, repair bounded failures, then run local quality gates: code review, test verification, and security review when security surfaces are present.
- Outputs: target resolved, package queue summary, completed and blocked packages, changed files, verification evidence, review findings and resolutions, skipped-lane reasons, residual risks.
- Hard stop: pause on ambiguous or missing target, missing approval/readiness evidence that is not explicitly waived by the current active contract, target repository outside the current workspace or allowed external directories without explicit approval, scope expansion, forbidden file edits, high-risk operations requiring explicit approval, unverifiable acceptance criteria, unavailable required local review lanes, or exhausted repair limits. Do not pause solely because the user omitted a manual implementation package; synthesize the queue instead.

## SHIP

Use after BUILD is complete enough to evaluate for handoff, merge, release, or archive.

- Inputs: implementation result, BUILD review/test/security evidence, review targets, release-blocker audit target or target request, named baseline/previous-release reference when requested, verification commands, closeout expectations.
- Actions: resolve and report the release-blocker audit target, defaulting to the current resolved change or final diff when no broader target is requested; ask for a missing baseline rather than guessing; re-check evidence freshness; rerun stale or scope-affected checks; audit diff/scope/artifacts for user-impacting regressions, security or permission exposure, unsafe/destructive workflow behavior, data-loss risk, artifact inconsistency, stale or missing evidence, unresolved review/test/security findings, and unverified acceptance criteria; classify findings; verify release or handoff readiness; prepare closeout.
- Outputs: BUILD gate status, release-blocker audit target and finding classifications, release-readiness summary, final evidence, closeout report, archive/sync/memory/PR/release next steps when approved.
- Hard stop: do not claim ready without fresh evidence, resolved/disproven/explicitly user-or-active-contract-accepted `release-blocking` findings, a non-guessed baseline when baseline comparison is requested, and explicit `Unverified` items.

## Change Revision Decision

When bugs or adjustments appear after a lifecycle pass:

- Same intent, overlapping scope, and not archived: update the current change, add repair tasks, and update `test-plan.md` defect/fix coverage.
- Same scope after SHIP but before archive: repair the current change and rerun affected code-review, test, and security lanes.
- Archived, merged, or released: create a new fix change and reference the source change instead of rewriting history.
- Workflow, command, skill, memory, subagent, installer, or tool-policy defect: route through `harness-issue-triage` and then approved `harness-evolution`.
