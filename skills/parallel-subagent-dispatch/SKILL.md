---
name: parallel-subagent-dispatch
description: Use when ROSE needs to split two or more independent investigation, implementation, review, or testing work packages across subagents without shared mutable state, overlapping edits, or sequential dependencies.
license: MIT
compatibility: opencode
metadata:
  source: adapted-from-superpowers
---

# Parallel Subagent Dispatch

## Purpose

Use parallel subagents only when separate work packages can proceed independently and return evidence for ROSE to reconcile.

This skill adapts Superpowers-style parallel dispatch discipline to this repository's OpenCode model: ROSE remains the primary orchestrator, subagents receive precise task packets, and no persona delegates to another persona.

## When to Use

Use this skill when there are two or more independent work packages, such as:

- code review, security audit, and test analysis on the same completed diff
- separate root-cause investigations in unrelated subsystems
- independent documentation, test, and implementation checks that do not edit the same files
- research tasks where each subagent can inspect a distinct area and return evidence

Realistic trigger prompts:

- "Run reviewer, security, and test-engineer in parallel on this change."
- "Split these unrelated failures across investigators and merge the findings."
- "Have separate agents inspect frontend, backend, and CI without overlapping edits."

## When Not to Use

Do not dispatch in parallel when:

- tasks share mutable state or edit the same files
- one task depends on the result of another
- the work requires a single coherent design decision before implementation
- the task is small enough for one agent to handle directly
- the user asked for one specific persona or a sequential investigation

Non-trigger prompt:

- "Fix this failing test after you identify the root cause." Use `debugging-and-error-recovery` first, then a scoped implementation handoff if needed.

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

Use `verification-before-completion` before reporting complete, fixed, passing, verified, or ready.
