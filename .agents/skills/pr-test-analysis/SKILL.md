---
name: pr-test-analysis
description: PR test analysis routing. Use for pull request or diff test impact, changed-test review, CI failure interpretation, and focused test matrix recommendations; do not use for general code review or editing tests.
---

# PR Test Analysis

Use this skill to route PR or diff-level testing questions to `pr-test-analyzer`.

## Trigger

- User asks whether a PR/diff has enough tests.
- CI logs need triage against changed files.
- ROSE needs the smallest meaningful command matrix for a package or PR.

## Near Misses

- General code correctness review: `code-reviewer`.
- Coverage-only adequacy: `coverage-review`.
- Running E2E or collecting artifacts: `e2e-artifact-handling`.

## Required Routing

- Owner lane: `subagent:review`.
- Agent: `pr-test-analyzer`.
- Read-only: no PR comments, labels, pushes, merges, or test edits.
