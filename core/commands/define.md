# /define

User input:
`$ARGUMENTS`

Invoke `aili-delivery-flow` in DEFINE mode.

Required behavior:
- Produce or align the complete implementation-readiness contract before BUILD.

Hard stops:
- Do not implement; unresolved material decisions or decision-shaping research, invalid/incoherent artifacts, or missing explicit final `test-plan.md` acceptance block BUILD readiness.

Output contract:
- Mode and backend, artifact status, readiness exactly `READY | BLOCKED`, named `Unverified` residuals separately, and the next gate.
