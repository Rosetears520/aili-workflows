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

Use subagents when delegation preserves MainAgent context or when separate work packages can proceed independently and return evidence for ROSE to reconcile.

This skill adapts Superpowers-style parallel dispatch discipline to this repository's OpenCode model: ROSE remains the primary orchestrator, subagents receive precise task packets, and no persona delegates to another persona.

## When to Use

Use this skill for context-saving dispatch and parallel dispatch.

Use a single read-only subagent, especially `code-scout`, even when there is only one work package, if doing the work in MainAgent would pollute context with broad search, large grep output, repeated file reads, logs, or exploratory dead ends.

Good single-subagent uses:
- residual marker scans across many files
- personal-name or local-path scans
- finding all references to a legacy API, config key, header, route, symbol, or marker
- mapping tests that cover a behavior
- checking whether docs/specs/plans reference a path or symbol
- locating security/trust-model evidence
- finding active vs archived/generated references
- confirming whether migration leftovers remain

Use parallel subagents when there are two or more independent work packages, such as:

- code review, security audit, and test analysis on the same completed diff
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
- the task is small enough for one agent to handle directly
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

## Dispatch ROI Rule

Dispatch when expected MainAgent context cost is greater than subagent overhead.

Use subagent when likely required evidence includes:
- 3+ files
- 2+ directories/subsystems
- 2+ search passes
- broad grep/list output
- noisy logs/test output
- uncertain active vs stale references
- independent review or coverage assessment

Do not dispatch when:
- one exact file/symbol is already known
- the task can be completed by reading one short file section
- the result is purely conversational
- the user needs an immediate tiny answer
- the subagent would need to write overlapping files

Read-heavy delegation is preferred. Write-heavy parallel delegation requires explicit isolation through branch/worktree and non-overlapping file ownership.

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

For harness-sensitive work, use `skills/aili-delivery-flow/references/protocols/subagent-task-packet.md` and `skills/aili-delivery-flow/references/protocols/subagent-result.md` as the packet/result evidence contract instead of redefining fields here.

```text
Subagent task packet:
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
