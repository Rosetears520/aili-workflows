# Subagent Task Packet Protocol

Canonical path for this change: `skills/aili-delivery-flow/references/protocols/subagent-task-packet.md`.

Use this packet for non-trivial, harness-sensitive, evidence-heavy, review, test, security, debugging, or implementation subagent work. Do not rely on a subagent inheriting the main conversation.

```text
Subagent task packet:
- Trace/work package id:
- Goal:
- Context:
- Active contract / source artifacts:
- Allowed scope:
- Forbidden scope:
- Edit permission:
- Evidence required:
- Expected return format:
- Placement / artifact rules:
- Coverage expectations:
- Known exclusions:
- Verification or inspection commands, if any:
- Stop conditions:
```

## Field rules

- Goal: one bounded outcome.
- Context: only the facts needed to start; include current user decisions when relevant.
- Active contract / source artifacts: paths to specs, tasks, diffs, issues, or docs that define scope.
- Allowed scope: exact files, directories, systems, or evidence sources the subagent may inspect or edit.
- Forbidden scope: files, commands, subsystems, or decisions that are out of bounds.
- Edit permission: `read-only`, `may edit listed files`, or `ask before edits`.
- Evidence required: anchors, tests, logs, screenshots, command summaries, or inspected sections required for ROSE to reconcile.
- Expected return format: normally the canonical `subagent-result.md` format or a named compact variant.
- Placement / artifact rules: where generated artifacts go, or `no files`.
- Coverage expectations: what must be checked before returning.
- Known exclusions: secrets, raw logs, full file dumps, unrelated cleanup, nested agents, commits, pushes.
- Stop conditions: blockers, conflicting evidence, missing permissions, unsafe ambiguity, or scope expansion.

## Hard rules

- Subagents do not spawn subagents unless a future approved contract explicitly changes orchestration rules.
- Read-heavy delegation is preferred; write-heavy parallel work requires isolated, non-overlapping file ownership.
- A subagent packet is a scope boundary, not a license to broaden work.
- ROSE remains responsible for reconciliation, verification judgment, and final acceptance.
