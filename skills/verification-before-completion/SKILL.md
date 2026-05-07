---
name: verification-before-completion
description: Use before any agent claims a task is complete, fixed, passing, verified, ready, or accepted, especially after implementation, debugging, testing, review follow-up, configuration, or release work.
license: MIT
compatibility: opencode
metadata:
  source: adapted-from-superpowers
---

# Verification Before Completion

## Purpose

Do not claim success until fresh evidence supports the exact claim.

This skill adapts Superpowers-style "evidence before claims" discipline to this repository. It applies to ROSE and subagents whenever the final answer would say complete, fixed, passing, verified, ready, accepted, or equivalent.

## Gate

Before making a completion claim:

1. Identify the claim.
2. Identify what evidence would prove it.
3. Run, inspect, or collect fresh evidence.
4. Read the full output and exit code when a command is used.
5. Report success only if the evidence supports the claim.
6. Otherwise report the actual status and unverified risk.

## Evidence Sources

Prefer the narrowest relevant source that proves the claim:

- targeted test command for changed behavior
- build, typecheck, lint, or format command for project health claims
- diff inspection for documentation-only or metadata-only claims
- browser, API, or manual runbook evidence for runtime behavior
- subagent evidence only after ROSE reconciles it and checks for conflicts

Do not treat stale output, assumptions, or partial logs as proof.

## Completion Evidence Format

```text
- Claim:
- Evidence source:
- Command / inspection:
- Exit code / result:
- What is verified:
- What remains unverified:
```

## Failure Handling

If evidence does not support the claim:

- say what failed or could not be verified
- distinguish your change from pre-existing or unrelated failures
- do not weaken the claim into vague language like "should work"
- do not retry the same failing fix more than three times without escalating

## Trigger Validation

Realistic trigger prompts:

- "Before saying this is fixed, verify it."
- "Can you confirm the build passes after the change?"
- "Report completion with evidence."

Non-trigger prompt:

- "Brainstorm possible fixes for this bug." No completion claim is being made yet.
