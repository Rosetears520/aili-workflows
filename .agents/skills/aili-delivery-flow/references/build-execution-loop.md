# Neutral BUILD Execution Loop

This is the active authority for neutral BUILD package execution. It defines no pseudo execution mode, session identity, native command binding, or extra permission.

## Activation and readiness

`/build` or equivalent explicit natural-language implementation intent may start only when exactly one target, current final-test-plan acceptance, a dependency-ready package, verifiable exit criteria, required operation permission, and a valid canonical `CONT-005` envelope are established. Acceptance or vague continuation alone performs zero execution.

When no package is supplied, synthesize the queue from `tasks.md`, specs, design, `test-plan.md`, and repository evidence. Resolve and canonicalize the target repository root from backend/change context before Git safety checks; the shell cwd is not authority. External roots require exact current-session approval and the applicable fail-closed worktree protocol.

## Queue contract and lightweight savepoints

Packages preserve identity, dependency order, non-overlapping edit ownership, complete accepted behavior, forbidden scope, pre-action safety gates, traceability, and stop conditions. Before multiple work units, record shared source-of-truth work, safe parallel lanes, serial dependencies, ownership boundaries, join points, expected evidence, blockers, and the reason for serialization.

For each Package 1–11:

1. Hydrate the accepted contract, context, progress, bounded drift, and fresh repository evidence.
2. Implement its complete accepted behavior; scoped work is not a partial patch.
3. Run focused verification when useful; for packaging, run the most relevant focused tests/checks first.
4. Record a lightweight savepoint with scope, files changed, unresolved items, and next package.
5. Continue only when dependencies are ready and no material/safety/budget stop applies.

Optional feedback is not package closure, readiness, convergence, or a mandatory local code-review/test/security gate. Package 1–11 implementation-only objectives have no package-quality review-repair budget. Known quality findings remain inputs to Package 12.

Package 12 begins only after complete Package 1–11 implementations/savepoints. It owns the single mandatory comprehensive gate: canonical all-task matrix, fresh full command matrix, diverse read-only non-nesting review lanes joined by ROSE without voting, and at most three holistic repair/retest/re-review cycles.

## Loop taxonomy

Exactly six inner loops exist:

| Inner loop | Trigger | Terminal boundary |
|---|---|---|
| question | material ambiguity or explicit grilling | answered, waived, named `Unverified`, user stop |
| delta | correction or material feedback | covered, or DEFINE writeback/revalidation |
| evidence/plan | formal, unfamiliar, risky, or version-sensitive planning | sufficient stressed plan or blocked/`Unverified` |
| neutral BUILD | accepted plan plus runnable package | complete package/savepoint or material/safety/budget/cancel stop |
| review/repair | Package 12 findings | resolved within three holistic cycles or blocked/material delta |
| convergence | Package 12 after Package 1–11 | complete links or `/ship` blocked/`Unverified` |

Exactly four outer profiles select initiation and boundary:

- `turn`: executable one-cycle prompt flow; initialize iteration to one and never silently recurse or convert to objective.
- `objective`: executable bounded implementation/closeout flow with explicit intent, exit evidence, and valid budgets.
- `interval`: protocol-only design-owned external/manual timing runbook; no timing registration.
- `event`: protocol-only design-owned external/manual event runbook; no listener or queue.

Interval/event invoke one existing bounded inner flow when externally/manual triggered; they are not inner loops and do not create a seventh loop.

## Canonical `CONT-005` envelope and budgets

Every executable run and protocol definition references one envelope with `loop_kind`, `trigger`, `trigger_evidence`, `objective`, `accepted_contract`, `change_id`, `success_evidence`, nested `budgets`, `human_gate`, `operation_gate`, `allowed_actions`, `writeback_targets`, `stop_reason`, and `outcome`. Interval/event additionally reference the canonical `ROUTE-007` identity and may add only `external_trigger_source`, `event_classifier`, or `cancellation`.

The nested object contains exactly:

```yaml
budgets:
  iteration: { limit: <positive-integer>, consumed: <nonnegative-integer>, remaining: <nonnegative-integer> }
  time: null | { unit: ms, limit: <positive-integer>, consumed: <nonnegative-integer>, remaining: <nonnegative-integer> }
  tokens: null | { unit: tokens, accounting_status: active | unavailable | lost, limit: <positive-integer>, consumed: <nonnegative-integer>, remaining: <nonnegative-integer> }
  review_repair: null | { limit: <positive-integer>, consumed: <nonnegative-integer>, remaining: <nonnegative-integer> }
```

For each non-null counter, `remaining = max(limit - consumed, 0)`. Zero, negative, fractional, nonnumeric, missing required values, wrong units, invalid statuses, or capability/null mismatches block rather than coerce.

- No configured token budget means explicit `tokens: null` and no token-enforcement claim.
- A requested token budget without reliable pre-start accounting remains non-null with `accounting_status: unavailable`, `consumed: 0`, and `remaining: limit`; execution blocks before the first action.
- Midrun accounting loss is valid only after active accounting. Preserve the non-null counter, last actual counters/overshoot, set `accounting_status: lost`, and block before another action.
- A turn uses iteration `{limit: 1, consumed: 0, remaining: 1}` and `review_repair: null`.
- Package 1–11 implementation-only objectives use `review_repair: null`.
- Package 12 holistic review/repair uses exactly `review_repair.limit: 3`.
- LP templates consume zero. Each external/manual run instantiates all four entries with concrete zeroed counters before execution.

Iteration and non-null review actions preflight one remaining unit, consume exactly one, and never exceed limit. For these discrete counters, `consumed > limit` is corrupted state: block before any action or repair, preserve the observed values for diagnosis, and do not classify the excess as an allowed overshoot. Time/token actions preflight current remaining and any reliable known bound. Only an indivisible observed time/token overshoot preserves actual consumed, sets remaining zero, records exact `overshoot`, stops, and permits no subsequent action. Resume preserves every counter, status, overshoot, and stop condition without reset or evasion.

Terminal outcomes are `complete`, `need-user`, `material-delta`, `blocked`, `Unverified`, `cancelled`, or `budget-exhausted`; terminal handling writes applicable formal/sidecar/progress evidence.

## Exact continuation

`continue`, `继续`, `go ahead`, or `继续做` resumes exactly one active authorized envelope only when target, lifecycle phase, accepted authorization, current acceptance/material gates, and remaining canonical budgets are unambiguous. Resume cannot create or broaden authority, select another target, change phase, refresh acceptance, reset counters, or clear a stop state. Otherwise ask exactly one focused target/authorization question and perform no loop, write, mutation, or budget consumption.

A material delta returns to DEFINE. A current no-write/chat-only clause overrides persistence and execution. Combined BUILD+SHIP intent authorizes current BUILD only; later SHIP needs fresh evidence and new intent.

## Protocol-only automation boundary

Formal documentation-only interval/event requests may define or reuse one `LP-INTERVAL-*` or `LP-EVENT-*` body only under the active change's `design.md` `## Loop Protocols`. If that documentation request lacks protocol scope or an external/manual trigger source, ask one focused documentation-protocol question without execution. An executable interval/event request blocks immediately with zero mutation and zero LP; do not mislabel it as documentation ambiguity. Tasks, tests, and context may reference a valid LP ID but not duplicate its body.

Any pure or mixed request to install, register, run, modify, update, reconfigure, enable, or reuse cron, a scheduler, watcher, webhook listener, queue, daemon, dependency, hook, or auto-retry runtime blocks wholly with zero mutation and zero LP. Only a later restated documentation-only external/manual protocol request may define or reuse an LP. No background primitive is provided.

## Native command non-ownership

Ordinary user, package, implementation, and Goal-Driven Verification wording remains valid and does not activate special execution semantics. Successful native `/goal <objective>`, bare `/goal`, and persistent native goal behavior are Stage II / N/A. AILI does not own, imitate, bind, modify, control, or claim those behaviors; `/build` remains neutral package execution.

## Safety and closeout

Pre-action gates remain mandatory for destructive/high-risk operations, external roots, dependencies/lockfiles, secrets, Graphify execution, and unsafe runtime behavior. Before non-trivial closeout, inspect `git status --short --branch` and classify dirty paths as task-scoped, unrelated/pre-existing, generated/ignored, scratch, or unknown. Propose cleanup for remaining residue; ask explicit approval before push, destructive clean/reset, branch deletion, worktree removal, OpenSpec archive, stashing unrelated changes, or deleting user-visible artifacts. Savepoint commits may be proactive only when current task/project rules explicitly allow task-scoped verified commits; otherwise ask once with the cleanup package.
