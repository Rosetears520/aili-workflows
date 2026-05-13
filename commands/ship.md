---
description: Run full release-readiness review, repair, verification, and closeout through the AILI delivery flow.
agent: rose
subtask: false
---

# /ship

User input:
$ARGUMENTS

Route to `aili-delivery-flow` in SHIP mode.

Hard stops:
- Do not treat BUILD review/test/security evidence as fresh if scope changed or evidence is stale.
- Do not claim ready on stale or missing evidence.
- Mark residual risks and unverified items explicitly.
