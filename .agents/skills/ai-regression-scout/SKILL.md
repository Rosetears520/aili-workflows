---
name: ai-regression-scout
description: AI regression scouting routing. Use when agents, prompts, skills, model/tool routing, harness fixtures, or generated-output expectations change and need regression scenarios; do not use for ordinary product-code regressions.
---

# AI Regression Scout

Use this skill to route AI-workflow regression discovery to `ai-regression-scout`.

## Trigger

- Agent prompt, skill, routing rule, model/tool policy, fixture, or output contract changed.
- ROSE needs over-trigger, under-trigger, ownership, permission, or completion-claim regression scenarios.
- A formal harness change needs smoke cases before acceptance.

## Near Misses

- Product-code behavior regression: use `test-engineer` or `debug-investigator`.
- General prompt editing: use the assigned implementation lane.
- Review of false success gates: use `silent-failure-hunting`.

## Required Routing

- Owner lane: `subagent:test`.
- Agent: `ai-regression-scout`.
- Default mode: read-only; it recommends fixtures/checks but does not edit them.
