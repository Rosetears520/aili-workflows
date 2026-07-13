---
description: Execute accepted work as a neutral dependency-ordered package queue.
agent: rose
subtask: false
---

# /build

User input:
$ARGUMENTS

Invoke `aili-delivery-flow` in BUILD mode.

Purpose:
- Execute the complete accepted Package 1–11 queue with lightweight savepoints, then run Package 12 as the single mandatory comprehensive quality gate.

Required behavior:
- Treat `/build` and equivalent explicit natural-language implementation intent identically. Acceptance alone is zero execution.
- Resolve exactly one accepted target, infer its canonical target repository root from backend context, and require current final-test-plan acceptance, dependency readiness, operation permission, verifiable exit criteria, and a valid canonical `CONT-005` envelope.
- Use the supplied package or synthesize an ordered implementation package queue from tasks, specs, design, the accepted test plan, and repository evidence. Preserve package identity, dependencies, non-overlapping edit ownership, forbidden scope, and final traceability.
- Implement complete package behavior inside the accepted scope. `Surgical` or scoped means no unrelated work, not artificially tiny or partial patches.
- For each Package 1–11, finish accepted behavior and record a lightweight savepoint containing scope, files changed, unresolved items, and next package. Optional focused build, test, typecheck, harness, delegation, or diff feedback is not package closure and does not create a mandatory package-local quality gate or repair budget.
- After complete Package 1–11 implementations/savepoints, run Package 12's canonical task matrix, full command matrix, and diverse non-nesting review lanes. Package 12 alone may use up to three holistic review-repair-retest-re-review cycles.
- Use exactly six inner loops—question, delta, evidence/plan, neutral BUILD, review/repair, convergence—and four outer profiles: executable `turn` and `objective`, protocol-only `interval` and `event`. Do not create a seventh loop.
- Resume wording (`continue`, `继续`, `go ahead`, `继续做`) may resume exactly one active authorized envelope only when target, phase, authorization, current gates, and remaining budget are unambiguous. Preserve all consumed counters and stop state; never reset, broaden authorization, switch phase/target, refresh acceptance, or start from acceptance alone. Otherwise ask one focused target/authorization question and perform no loop, write, or mutation.
- Apply `CONT-005` as the only budget authority. Use one nested `budgets` object with iteration, time, tokens, and review_repair entries; Package 1–11 implementation-only objectives use `review_repair: null`, and Package 12 uses `review_repair.limit: 3`.
- Block pure or mixed requests to install, register, run, modify, update, reconfigure, enable, or reuse automation with zero mutation and zero LP. Only a later documentation-only request may define/reuse a design-owned external/manual interval/event LP.
- Before non-trivial closeout, inspect target repo branch/status, classify dirty paths as task-scoped, unrelated/pre-existing, generated/ignored, scratch, or unknown, and propose cleanup for residue; ask explicit approval before push, destructive clean/reset, branch deletion, worktree removal, OpenSpec archive, stashing unrelated changes, or deleting user-visible artifacts. Savepoint commits may be proactive only when current task/project rules explicitly allow task-scoped verified commits; otherwise ask once with the cleanup package.

Hard stops:
- Do not edit without exactly one accepted ready target, valid budgets, and required permissions. Do not use acceptance, vague continuation, task checkboxes, or optional package feedback as execution/completion authority.
- Do not own, bind, control, imitate, modify, or claim implementation of native `/goal`; successful native `/goal` behavior is Stage II / N/A. Do not add a public loop/profile alias.
- Do not add a scheduler, listener, daemon, persistent queue, hook, dependency, auto-retry, or other background runtime.
- Pause before destructive/high-risk operations, file deletion/move/rename, dependency or lockfile changes, schema/migration changes, auth/security weakening, external-root access, push/merge/history changes, archive, or secret handling without exact approval.
- Do not ask for manual package approval only because the user omitted a package.
- Stay inside the package; report scope expansion or missing verification instead of guessing.

Output contract:
- selected BUILD mode, backend, target, and active outer profile;
- package queue, lightweight savepoints, completed/blocked packages, and files changed;
- canonical budget state, stop reason/outcome, and optional feedback evidence;
- Package 12 gate evidence when reached, or why it has not started;
- residual risks, scope expansions, and `Unverified` items;
- whether the change is ready for `/ship`.
