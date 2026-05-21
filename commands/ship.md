---
description: Run release-blocker audit, review, repair, verification, and closeout through the AILI delivery flow.
agent: rose
subtask: false
---

# /ship

User input:
$ARGUMENTS

Invoke `aili-delivery-flow` in SHIP mode.

Purpose:
- Reconcile final diff, release-blocker audit, review, repair, verification, and closeout before handoff, merge, release, or archive.

Required behavior:
- Resolve and report the release-blocker audit target: active change/proposal artifacts, current final diff, a named baseline or previous-release comparison, or a broader repository scan only when explicitly requested or risk-triggered.
- Produce a detailed human-reviewable Markdown closeout document for every SHIP run. CLI output may be brief, but it must include the closeout document path, verdict, blocking/important/`Unverified` summary, and approved next action.
- For OpenSpec-backed changes, write the closeout document to `openspec/changes/<change-id>/ship-closeout.md`. For non-OpenSpec SHIP runs, ask for a repository-local closeout document path before the final verdict if no approved path exists.
- Re-check evidence freshness for final scope and rerun stale or scope-affected checks.
- Audit for release-blocking findings: user-impacting behavior regressions, security or permission exposure, unsafe/destructive workflow behavior, data-loss risk, artifact inconsistency, stale or missing evidence, unresolved review/test/security findings, and unverified acceptance criteria.
- Classify findings as `release-blocking`, `important`, `accepted risk`, `out-of-scope`, or `Unverified` before any readiness verdict.
- Reconcile code-review, test, and security findings; repair only approved in-scope issues.
- Verify release-readiness, artifact consistency, rollback/closeout expectations, and remaining risks.
- For post-cycle bugs, decide whether to update the current change, create a new fix change, or route harness defects through triage and evolution.

Hard stops:
- Do not treat BUILD review/test/security evidence as fresh if scope changed or evidence is stale.
- Do not claim ready on stale or missing evidence.
- Do not claim ready when a `release-blocking` finding is unresolved, unproven, or not explicitly accepted as risk by the user or current active contract owner.
- Do not guess a previous-release baseline; ask for a tag/commit/branch/release reference or mark that comparison `Open Question` / `Unverified`.
- Do not claim exhaustive whole-codebase safety; report scanned scope, skipped lanes, and residual `Unverified` items.
- Mark residual risks and unverified items explicitly.

Output contract:
- selected mode and backend;
- closeout document path and write/update status;
- release-blocker audit target, scope, finding classifications, and fresh evidence;
- final evidence and review/repair status;
- release-readiness or archive-readiness verdict;
- remaining risks and `Unverified` items;
- approved next steps only.
