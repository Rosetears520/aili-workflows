---
name: harness-issue-triage
description: Diagnose user-reported AILI/ROSE harness or workflow behavior problems without editing files; use when the user says a command, skill trigger, subagent packet, memory flow, installer, docs, or agent prompt behavior is wrong and wants to know where the issue lives and how to fix it. Do not use for normal product-code bugs; hand off approved harness modifications to harness-evolution.
---

# Harness Issue Triage

Use this skill to localize harness problems before proposing or applying harness changes.

The default output is a diagnosis and recommended fix path, not file edits.

## When to Use

- User says the workflow, ROSE behavior, slash command, skill routing, subagent packet/result, memory writeback, installer, OpenCode setup, or harness documentation is wrong.
- User asks “这个问题出在哪里”, “哪里不合适”, “为什么 agent 不按流程走”, or “应该改哪个文件”.
- Reviewing whether a proposed harness change targets the right component.

Do not use this for ordinary application bugs or product-code implementation issues.

## Workflow

1. Restate the observed behavior and expected behavior in one sentence.
2. Locate the likely component using `references/component-diagnosis.md`.
3. Collect only the smallest needed evidence anchors.
4. Classify the issue as command, skill, protocol, docs, installer, memory, subagent packet/result, tool policy, environment, or agent/system prompt.
5. Explain the narrowest fix and why broader prompt changes are or are not needed.
6. If a core harness edit is needed, stop with a triage report and ask for approval or hand off to `harness-evolution`.

## Boundaries

- Read-only by default: do not edit, stage, commit, push, or rewrite harness files.
- Do not modify `agents/rose.md` during normal tasks.
- Agent prompt changes require an explicit harness maintenance task and user approval.
- Read `docs/harness/**` only for harness issues, harness maintenance, or review of a harness change.
- In downstream/global installs, do not assume `docs/harness/**` exists. Use this skill’s packaged `references/` first.

## Output

Use `references/triage-report-template.md`.

Minimum fields:

- observed behavior;
- expected behavior;
- primary component;
- evidence anchors;
- recommended fix;
- approval needed: yes/no;
- next skill or action.

## Handoff

- If the user only asked “where is the problem”, stop after the triage report.
- If the user approves a harness change, use `harness-evolution` for the report-first change workflow.
- If the issue is not harness-related, route to the normal debugging, planning, review, or implementation skill.

## Symlink Runtime Note

Selective OpenCode install links `skills/*` into the global skills directory. This makes this skill and its `references/` available at runtime.

Source-repo docs such as `docs/harness/**` are maintenance documentation, not guaranteed runtime context in downstream projects. Keep any always-needed triage rules inside this skill’s `references/`.
