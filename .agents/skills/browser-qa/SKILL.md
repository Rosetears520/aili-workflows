---
name: browser-qa
description: Browser QA routing. Use for local browser-rendered UI verification, DOM/accessibility/console/network checks, screenshots, and Playwright browser evidence; do not use for backend-only changes or production-mutating flows.
---

# Browser QA

Use this skill to route browser verification to `browser-qa-runner`.

## Trigger

- UI, browser rendering, accessibility tree, console, network, or screenshot verification is needed.
- A fix needs live browser evidence beyond static tests.

## Required Safety Gate

- Confirm target URL/environment before action.
- Avoid production mutation: no real purchases, messages, account changes, destructive forms, or production data writes without explicit safe-scenario approval.
- Before saving screenshots, traces, videos, reports, console logs, or network logs, obtain a repository-local artifact placement. If no placement exists, keep evidence inline/ephemeral and report no durable artifact.

## Near Misses

- Persistent E2E report/trace packaging: `e2e-artifact-handling`.
- Backend-only verification: use normal test/typecheck lanes.
- Creating Playwright config or test directories: requires explicit implementation scope and placement decision.

## Required Routing

- Owner lane: `subagent:test`.
- Agent: `browser-qa-runner`.
