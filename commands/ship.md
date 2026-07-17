---
description: Run release-blocker audit, review, repair, verification, and closeout through the AILI delivery flow.
agent: rose
subtask: false
---

# /ship

User input:
$ARGUMENTS

Invoke `aili-delivery-flow` in SHIP mode.

Required behavior:
- Reconcile final diff, release-blocker audit, review, repair, verification, and closeout before handoff, merge, release, or archive.

Hard stops:
- Do not review, repair, or claim readiness without fresh explicit SHIP intent, current implementation evidence, and fresh claim-relevant evidence; exact high-risk/Git/release operations retain separate approval.

Output contract:
- Mode/target, closeout path when applicable, verdict, blocking or `Unverified` evidence, approvals needed, and next action.
