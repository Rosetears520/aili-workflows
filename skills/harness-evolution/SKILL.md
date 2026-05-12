---
name: harness-evolution
description: Produce or apply an approved report-first proposal for workflow, ROSE, skill, command, subagent, memory, install, or harness-doc changes; use after harness-issue-triage localizes a harness problem or when the user explicitly requests harness maintenance, and do not edit core harness files without explicit human approval.
---

# Harness Evolution

Use this skill when the harness itself may need to change. The default output is a structured report or proposal, not file edits.

If the user is only reporting that behavior is wrong and asking where the issue lives, use `harness-issue-triage` first.

## Triggers

- User asks to change workflow, ROSE, a skill, command, subagent, memory policy, install/setup path, or harness documentation.
- Repeated workflow failures or user corrections indicate process drift.
- Subagent dispatch/result boundaries fail.
- Verification claims lack fresh evidence or bypass required gates.
- Memory retrieval/writeback/provenance fails.
- Command lifecycle is bypassed or internal stages appear as top-level commands.
- Tool policy, middleware/hook, environment, or workflow-pattern defects appear.

## Workflow

1. Start from a `harness-issue-triage` report when available; otherwise classify the signal with `references/component-taxonomy.md`.
2. Decide required gates from `references/activation-matrix.md`.
3. Produce a report using `references/change-report-template.md`.
4. Ask for explicit approval before applying any core harness edit.
5. If approved, apply only the approved change and run the named verification trigger.
6. Record the verdict using `references/verdict-policy.md`.

## Boundaries

- Report/proposal artifacts are allowed by default.
- Core harness edits require explicit human approval in conversation, PR review, or approved OpenSpec record.
- Core harness includes ROSE/runtime rules, commands, skill routing, subagent contracts, memory policy, install scripts, OpenCode hooks, and harness docs.
- Do not write SQLite manually, change memory schema, add dependencies, commit, push, or silently edit protected harness files.
- Do not modify `agents/rose.md` during normal tasks. Agent prompt edits require an explicit harness maintenance task and human approval.

## Verification

- Every proposal names a verification trigger and rollback plan.
- Applied changes must record result, verdict, remaining risks, and evidence pointer.
- Missing approval returns a blocked report, not an edit.
