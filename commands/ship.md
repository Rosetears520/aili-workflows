---
description: Run full release-readiness review, repair, verification, and closeout through the AILI delivery flow.
agent: rose
subtask: false
---

# /ship

User input:
$ARGUMENTS

Invoke `aili-delivery-flow` in SHIP mode.

Purpose:
- Reconcile final diff, review, repair, verification, and closeout before handoff, merge, release, or archive.

Required behavior:
- Re-check evidence freshness for final scope and rerun stale or scope-affected checks.
- Reconcile code-review, test, and security findings; repair only approved in-scope issues.
- Verify release-readiness, artifact consistency, rollback/closeout expectations, and remaining risks.
- For post-cycle bugs, decide whether to update the current change, create a new fix change, or route harness defects through triage and evolution.

Hard stops:
- Do not treat BUILD review/test/security evidence as fresh if scope changed or evidence is stale.
- Do not claim ready on stale or missing evidence.
- Mark residual risks and unverified items explicitly.

Output contract:
- selected mode and backend;
- final evidence and review/repair status;
- release-readiness or archive-readiness verdict;
- remaining risks and `Unverified` items;
- approved next steps only.
