---
name: parallel-subagent-dispatch
description: Use when the user explicitly requests subagents, a specialist capability is required, repository exploration would materially pollute context, or at least two independent work units have a clear wall-clock or context benefit. Direct ROSE work is the default.
license: MIT
compatibility: opencode
---

# Parallel Subagent Dispatch

## Goal

Work directly by default. When delegation has a concrete benefit, use the smallest fresh, single-use Task shape without turning ordinary work into orchestration overhead.

## Trigger

Use Task only when at least one condition is true:

- the user explicitly asks for a subagent;
- a required capability belongs to a specialist;
- broad search or noisy output would materially pollute ROSE context;
- at least two independent units can run concurrently with clear benefit.

Otherwise work directly. Do not delegate a single straightforward task merely because a subagent exists.

Every actual Task invocation must pass this benefit decision independently. A prior failure, partial result, empty result, or desire to continue is not by itself a reason to dispatch another Task.

## Parallelism

- Default to at most two concurrent subagents.
- Parallel units must not edit the same files or depend on each other's output.
- If work overlaps or has a dependency, run it sequentially or keep it direct.
- Do not automatically add review, test, security, or coverage agents after implementation.

## Single-use sessions

- Each Task context receives one bounded assignment and ends permanently with one terminal result or failure.
- Never resume an old `task_id` for follow-up, clarification, continuation, repair, recheck, or additional work.
- Do not automatically retry in a fresh session after a failed, empty, blocked, or partial result; ROSE handles the bounded gap directly or reports the blocker.
- The same `subagent_type` may be selected later only in a fresh Task invocation with no prior `task_id`, after a new direct-first benefit decision for an independently justified assignment or changed evidence.
- Subagents never nest or delegate. ROSE retains lifecycle, approval, integration, reconciliation, and final-verdict ownership.

## Compact packet

Send only:

```text
Goal:
Scope:
Allowed actions:
Expected result:
Stop when:
```

A packet narrows scope; it never expands effective permissions. Every subagent remains non-delegating.

For A33, a packet/result carries one compact `WT-001` reference for one declared repository/cwd. It never duplicates or rebinds root, key, identity, Git, approval, operation, risk, delta, rule, command/cwd, or containment authority. Target rules are re-read at dispatch, can only narrow, and same-level conflicts block. Artifacts stay with the owning target repository.

## Compact result

Require only:

```text
STATUS: completed | partial | blocked | unverified
EVIDENCE: compact anchors, artifacts, or command result
BLOCKERS: none or exact missing input/permission
```

ROSE checks the returned evidence, resolves conflicts, and owns the lifecycle, integration, and final decision. Missing or empty evidence is not completion and does not authorize resume or an automatic fresh-session retry.

## Stop

Do not dispatch when permission, scope, ownership, or independence is unclear. Ask the user only when the missing answer changes the task or authorization.
