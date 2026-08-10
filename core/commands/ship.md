# /ship

User input:
`$ARGUMENTS`

Invoke `aili-delivery-flow` in SHIP mode.

Required behavior:
- Enter the same canonical SHIP loop as equivalent natural-language intent. Reconcile the implemented target directly and select only the evidence, review, repair, packaging, or release check required by the exact closeout claim.

Hard stops:
- Do not start a review swarm, broad matrix, or repair cycle merely because SHIP was requested. Fresh SHIP intent and current implementation evidence are required; exact high-risk/Git/release operations retain separate approval.

Output contract:
- Mode/target, closeout path when applicable, verdict, blocking or `Unverified` evidence, approvals needed, and next action.
