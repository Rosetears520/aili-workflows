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

Use when implementation is explicitly approved.

- Inputs: approved scope, implementation package, acceptance criteria, forbidden scope, BUILD review lanes.
- Actions: re-read relevant DEFINE artifacts from disk, dispatch bounded implementation work, then run local quality gates: code review, test verification, and security review when security surfaces are present.
- Outputs: changed files, verification evidence, review findings and resolutions, skipped-lane reasons, residual risks.
- Hard stop: pause on scope expansion, missing approval, missing package, forbidden file edits, unverifiable acceptance criteria, or unavailable required local review lanes.

## SHIP

Use after BUILD is complete enough to evaluate for handoff, merge, release, or archive.

- Inputs: implementation result, BUILD review/test/security evidence, review targets, verification commands, closeout expectations.
- Actions: re-check evidence freshness, rerun stale or scope-affected checks, audit diff/scope/artifacts, verify release or handoff readiness, prepare closeout.
- Outputs: BUILD gate status, release-readiness summary, final evidence, closeout report, archive/sync/memory/PR/release next steps when approved.
- Hard stop: do not claim ready without fresh evidence, resolved or accepted blocking findings, and explicit `Unverified` items.

## Change Revision Decision

When bugs or adjustments appear after a lifecycle pass:

- Same intent, overlapping scope, and not archived: update the current change, add repair tasks, and update `test-plan.md` defect/fix coverage.
- Same scope after SHIP but before archive: repair the current change and rerun affected code-review, test, and security lanes.
- Archived, merged, or released: create a new fix change and reference the source change instead of rewriting history.
- Workflow, command, skill, memory, subagent, installer, or tool-policy defect: route through `harness-issue-triage` and then approved `harness-evolution`.
