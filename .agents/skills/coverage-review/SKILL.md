---
name: coverage-review
description: Coverage review and verification sufficiency routing. Use when test coverage, uncovered paths, coverage reports, or verification adequacy need a read-only QA review; do not use for writing tests or running browser/E2E artifacts.
---

# Coverage Review

Use this skill to route a completed change to `test-coverage-reviewer` when ROSE needs read-only coverage adequacy evidence.

## Trigger

- Coverage report or changed behavior needs independent interpretation.
- Review asks whether current tests prove the accepted scope.
- A package changes logic, error handling, integration seams, or user-visible behavior and verification may be thin.

## Near Misses

- Writing or modifying tests: use `test-engineer`.
- PR-wide test matrix or CI log analysis: use `pr-test-analysis`.
- Browser screenshots/traces: use `browser-qa` or `e2e-artifact-handling`.

## Required Routing

- Owner lane: `subagent:review`.
- Agent: `test-coverage-reviewer`.
- Default mode: read-only; findings recommend tests/commands but do not edit.
