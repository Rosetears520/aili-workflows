# Direct vs Delegated Work

Direct ROSE work is the default. Delegation is an optimization or capability boundary, not a mandatory ceremony.

## Use Task only when

At least one condition is true:

- the user explicitly requests a subagent;
- a specialist owns a capability ROSE cannot perform directly;
- broad search or noisy output would materially pollute the main context;
- at least two independent units can run concurrently with clear wall-clock or context benefit.

Otherwise ROSE reads, edits, and verifies directly. A non-trivial or multi-file task does not by itself require delegation.

## Dispatch shape

- Default concurrency is at most two.
- Parallel units must have independent inputs and non-overlapping writes.
- If units overlap or depend on one another, run them sequentially or keep the work direct.
- Do not automatically add review, test, security, coverage, or convergence lanes.
- Subagents never delegate and never own the final verdict.

Use the compact packet and result contracts in `protocols/subagent-task-packet.md` and `protocols/subagent-result.md`. A packet narrows scope but never expands effective permissions.

## Separate gates

Direct-first routing does not waive lifecycle, branch/status, secrets, high-risk, destructive, dependency, schema, public API, auth, external-operation, or verification gates.

## Completion

ROSE inspects the final changed files and runs the smallest check that proves the requested claim. Unsupported claims remain `Unverified`.
