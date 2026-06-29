---
name: silent-failure-hunting
description: Silent failure hunting routing. Use when a change might pass while skipping work, swallowing errors, losing evidence, weakening gates, or reporting false success; do not use for broad code review.
---

# Silent Failure Hunting

Use this skill to route false-success risk review to `silent-failure-reviewer`.

## Trigger

- Installer, packaging, verification, review, memory, artifact, CLI, or workflow gate changed.
- Logs/reports may hide skipped checks, stale evidence, partial writes, or ignored exit codes.
- Acceptance depends on distinguishing PASS, partial, skipped, blocked, and `Unverified`.

## Near Misses

- Security exploitability: `security-auditor`.
- Coverage adequacy: `coverage-review`.
- Running the failing command: `test-engineer` or a relevant runner.

## Required Routing

- Owner lane: `subagent:review`.
- Agent: `silent-failure-reviewer`.
- Read-only; recommendations may request fixes or negative tests.
