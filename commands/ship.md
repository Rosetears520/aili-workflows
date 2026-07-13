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
- Treat `/ship` and equivalent natural-language review/repair/closeout intent identically, but require a new explicit SHIP intent plus current implementation evidence. DEFINE artifacts, acceptance, or an earlier “implement and then ship” request are insufficient.
- Resolve and report the release-blocker audit target: active change/proposal artifacts, current final diff, a named baseline or previous-release comparison, or a broader repository scan only when explicitly requested or risk-triggered.
- When SHIP decomposes review, repair, verification, security, packaging, or closeout work into multiple independently actionable lanes, report the parallelism analysis, lane boundaries, join point, and any serial/no-parallel reason before integration.
- Produce a detailed human-reviewable Markdown closeout document for every SHIP run. CLI output may be brief, but it must include the closeout document path, verdict, blocking/important/`Unverified` summary, and approved next action.
- For OpenSpec-backed changes, write the closeout document to `openspec/changes/<change-id>/ship-closeout.md`. For non-OpenSpec SHIP runs, ask for a repository-local closeout document path before the final verdict if no approved path exists.
- Re-check evidence freshness for final scope and rerun stale or scope-affected checks.
- Audit for release-blocking findings: user-impacting behavior regressions, security or permission exposure, unsafe/destructive workflow behavior, data-loss risk, artifact inconsistency, stale or missing evidence, unresolved review/test/security findings, and unverified acceptance criteria.
- Classify findings as `release-blocking`, `important`, `accepted risk`, `out-of-scope`, or `Unverified` before any readiness verdict.
- Reconcile code-review, test, and security findings; repair only approved in-scope issues.
- If packaging or release artifact generation is part of SHIP, require fresh relevant verification first and report package artifact evidence or blocker separately from review evidence.
- Verify release-readiness, artifact consistency, rollback/closeout expectations, and remaining risks.
- Before non-trivial SHIP closeout, inspect target repo branch/status, classify dirty paths as task-scoped, unrelated/pre-existing, generated/ignored, scratch, or unknown, remove only safe task-owned non-user-visible scratch artifacts, and propose cleanup for residue; ask explicit approval before push, destructive clean/reset, branch deletion, worktree removal, OpenSpec archive, stashing unrelated changes, or deleting user-visible artifacts. Savepoint commits may be proactive only when current task/project rules explicitly allow task-scoped verified commits; otherwise ask once with the cleanup package.
- For post-cycle bugs, decide whether to update the current change, create a new fix change, or route harness defects through triage and evolution.

Hard stops:
- Block natural-language SHIP when implementation evidence is missing; ask only for the unresolved target/evidence and run no review/repair/convergence mutation.
- Do not treat BUILD review/test/security evidence as fresh if scope changed or evidence is stale.
- Do not claim ready on stale or missing evidence.
- Do not claim ready when a `release-blocking` finding is unresolved, unproven, or not explicitly accepted as risk by the user or current active contract owner.
- Do not guess a previous-release baseline; ask for a tag/commit/branch/release reference or mark that comparison `Open Question` / `Unverified`.
- Do not claim exhaustive whole-codebase safety; report scanned scope, skipped lanes, and residual `Unverified` items.
- Do not infer SHIP preauthorization from BUILD intent or direct generated-adapter output; establish current AILI contract, implementation, and verification evidence independently.
- Mark residual risks and unverified items explicitly.
- Do not push, clean/reset destructively, delete branches, remove worktrees, archive OpenSpec changes, stash unrelated changes, or delete user-visible artifacts without explicit approval for that exact action.

Output contract:
- selected mode and backend;
- closeout document path and write/update status;
- release-blocker audit target, scope, finding classifications, and fresh evidence;
- final evidence and review/repair status;
- branch/worktree hygiene status and cleanup approvals needed;
- release-readiness or archive-readiness verdict;
- remaining risks and `Unverified` items;
- approved next steps only.
