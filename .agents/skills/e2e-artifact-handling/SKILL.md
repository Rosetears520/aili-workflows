---
name: e2e-artifact-handling
description: E2E artifact handling routing. Use when traces, videos, screenshots, reports, or failure bundles need controlled repository-local placement; do not use for simple unit tests or production-mutating E2E flows.
---

# E2E Artifact Handling

Use this skill to route E2E evidence collection or packaging to `e2e-artifact-runner`.

## Trigger

- E2E command needs trace/video/screenshot/report/failure-bundle evidence.
- A failing browser flow needs artifacts for ROSE review.
- User asks to preserve test artifacts from an E2E run.

## Required Safety Gate

- Use localhost, fixtures, or explicitly approved non-production/read-only targets.
- Require repository-local artifact placement before writing user-visible screenshots, traces, videos, reports, or bundles.
- Do not create new `tests/e2e/`, report, trace, screenshot, or golden directories without placement approval.
- Redact or avoid artifacts containing secrets, cookies, tokens, credentials, or private user data.

## Near Misses

- Browser manual QA without durable artifacts: `browser-qa`.
- Test design or unit/integration verification: `test-engineer`.
- Coverage sufficiency review: `coverage-review`.

## Required Routing

- Owner lane: `subagent:test`.
- Agent: `e2e-artifact-runner`.
