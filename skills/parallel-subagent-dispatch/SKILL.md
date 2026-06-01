---
name: parallel-subagent-dispatch
description: Use when ROSE needs context-saving subagent dispatch: single read-only scouting for noisy repository evidence, or splitting two or more independent investigation, implementation, review, or testing work packages across subagents without shared mutable state, overlapping edits, or sequential dependencies.
license: MIT
compatibility: opencode
metadata:
  source: adapted-from-superpowers
---

# Parallel Subagent Dispatch

## Purpose

Use subagents when delegation preserves MainAgent context, when separate work packages can proceed independently and return evidence for ROSE to reconcile, or when a non-trivial repository task enters the subagent-first runtime path.

This skill adapts Superpowers-style parallel dispatch discipline to this repository's OpenCode model: ROSE remains the primary orchestrator, subagents receive precise task packets, and no persona delegates to another persona.

## When to Use

Use this skill for context-saving dispatch, parallel dispatch, and subagent-first routing of non-trivial repository work.

Pure conversation and explicit current-task subagent opt-out may stay direct. A clear target, exact path, short context, or DCP summary is not a direct-work reason by itself.

Use a single read-only subagent, especially `code-scout`, even when there is only one work package, if doing the work in MainAgent would pollute context with broad search, large grep output, repeated file reads, logs, or exploratory dead ends.

For ROSE runtime work, this is mandatory when the direct allowlist does not apply. ROSE remains Supervisor; workers return compact reports and evidence, not final PASS/FAIL/`Unverified` judgments.

Good single-subagent uses:
- residual marker scans across many files
- personal-name or local-path scans
- finding all references to a legacy API, config key, header, route, symbol, or marker
- mapping tests that cover a behavior
- mapping upstream callers or entrypoints
- mapping downstream consumers or output paths
- mapping sibling or peer implementations
- mapping convention examples before a non-trivial edit
- checking whether docs/specs/plans reference a path or symbol
- locating security/trust-model evidence
- finding active vs archived/generated references
- confirming whether migration leftovers remain

Use parallel subagents when there are two or more independent work packages, such as:

- code review and test analysis on the same completed diff; run the security lane independently when the changed surface includes auth, permissions, secrets, shell/installers, dependencies, network, storage, or other security-sensitive behavior
- separate root-cause investigations in unrelated subsystems
- independent documentation, test, and implementation checks that do not edit the same files
- research tasks where each subagent can inspect a distinct area and return evidence

Realistic trigger prompts:

- "Run reviewer, security, and test-engineer in parallel on this change."
- "Split these unrelated failures across investigators and merge the findings."
- "Have separate agents inspect frontend, backend, and CI without overlapping edits."

## When Not to Dispatch in Parallel

Do not dispatch in parallel when:

- tasks share mutable state or edit the same files
- one task depends on the result of another
- the work requires a single coherent design decision before implementation
- the task is an immediate tiny pure-conversation answer with no repository read, edit, or verification obligation
- the user asked for one specific persona or a sequential investigation

Non-trigger prompt:

- "Fix this failing test after you identify the root cause." Use `debugging-and-error-recovery` first, then a scoped implementation handoff if needed.

## Context-Saving Dispatch

Return only compact evidence anchors:
- file:line or symbol
- short classification
- active/current/stale/archived/generated status when relevant
- confidence
- recommended MainAgent next reads

Do not paste large file excerpts, full grep dumps, long logs, or exploratory dead ends back into MainAgent context.

Search evidence is a map. The editing, reviewing, testing, securing, or documenting agent must still read final target files before acting.

## Execution Ownership Gate

Assign every delegated todo and task packet one explicit owner: `ROSE`, `user`, `subagent:research`, `subagent:edit`, `subagent:review`, or `subagent:test`. Preserve owner prefixes when copying, splitting, reconciling, or reporting todos/task packets.

User-requested subagent ownership is binding for the current task. If the user asks a subagent to 修改, 补强, 完成, do, update, or implement, use `subagent:edit`; if the user asks a subagent to 复核, review, or audit, use `subagent:review`; if the user asks a subagent to 看一下, 调研, find evidence, or scout, use `subagent:research` only; if the user asks a subagent to test, verify, run tests, coverage, 测试, 验证, or 跑测试, use `subagent:test`.

Evidence is sufficient may complete only a `subagent:research` task. It does not authorize ROSE to complete `subagent:edit`, `subagent:review`, `subagent:test`, or user-requested subagent completion work through ROSE's own edits, reviews, tests, or final integration. ROSE may change subagent-owned edit/review/test/completion work to `ROSE` only after explicit current-task user confirmation, not for efficiency, context, or faster integration reasons.

## Mandatory Dispatch Rule

Dispatch non-trivial repository work by default. Also dispatch when expected MainAgent context cost is greater than subagent overhead.

ROSE MUST use a read-only subagent when likely required evidence includes:
- 3+ relevant files
- 2+ directories/subsystems
- 2+ search passes
- broad grep/list output
- noisy logs/test output
- uncertain active vs stale references
- active/current/stale/archived/generated classification
- all-reference scans
- upstream/downstream/peer implementation mapping
- test coverage mapping
- convention discovery before non-trivial edits
- independent review or coverage assessment

ROSE may skip dispatch only when:
- the result is purely conversational
- the user gives an explicit current-task subagent opt-out
- the user needs an immediate tiny answer, meaning pure conversation only and no repository work
- parallel subagents would need to write overlapping files; avoid parallel dispatch and use sequential/scoped delegation, or stop if safe ownership cannot be established
- the work satisfies the direct allowlist in `skills/aili-delivery-flow/references/direct-vs-delegated-work.md`

If ROSE skips delegation for a non-trivial task, it must state the direct opt-out or pure-conversation reason and the remaining safety/evidence basis. Exact file knowledge, short context, or DCP summaries do not justify skipping dispatch.

Read-heavy delegation is preferred. Write-heavy parallel delegation requires explicit isolation through branch/worktree and non-overlapping file ownership.

Implementation worker increments are dynamic: size them by verifiability, reviewability, absence of parallel edit conflicts, and clean handoff boundaries rather than a fixed number of files.

## Independence Check

Before dispatching, ROSE must verify:

1. Each work package has a distinct goal.
2. Each package has distinct allowed files, systems, or evidence sources.
3. No package requires another package's output to start.
4. Any edit permissions are isolated and non-overlapping.
5. Each subagent can return enough evidence for ROSE to merge results.

If any item fails, run the work sequentially or narrow the task packets until independence is true.

## Subagent Task Packet Template

Send each subagent a complete packet. Do not rely on it inheriting the main conversation context.

For harness-sensitive work, use `skills/aili-delivery-flow/references/protocols/subagent-task-packet.md` as the canonical task packet protocol and `skills/aili-delivery-flow/references/protocols/subagent-result.md` as the canonical result protocol.

```text
Subagent task packet:
- Owner: ROSE | user | subagent:research | subagent:edit | subagent:review | subagent:test
- Goal:
- Context:
- Allowed scope:
- Forbidden scope:
- Edit permission:
- Evidence required:
- Expected return format:
- Stop conditions:
```

Guidelines:

- Include exact files, commands, diffs, symptoms, or acceptance criteria needed for the task.
- State whether the subagent may edit, may only inspect, or must ask before edits.
- Forbid nested agent calls unless the repository explicitly changes its orchestration rules.
- Require concrete evidence, not just conclusions.

## Reconciliation and Verification

After subagents return:

1. Compare conclusions against the evidence each subagent supplied.
2. Identify conflicts, duplicated work, missing evidence, and unresolved risks.
3. Decide whether follow-up work is sequential, parallel, or blocked.
4. Run or request fresh verification before claiming completion.
5. Summarize findings by work package and separate verified facts from recommendations.

### Reconciliation Stress Test

After reconciling subagent results, use `strategy-stress-test`.

Check whether:

- any subagent conclusion lacks evidence anchors
- two subagents conflict and the conflict is unresolved
- a high-risk claim depends on stale logs or unverified assumptions
- write-heavy parallel work has overlapping files, shared mutable state, or hidden sequence dependencies
- a missing specialist pass is required, such as security-auditor or test-engineer
- follow-up work must be sequential instead of parallel

Do not treat subagent output as truth. Treat it as evidence to reconcile.

Use `verification-before-completion` before reporting complete, fixed, passing, verified, or ready.
