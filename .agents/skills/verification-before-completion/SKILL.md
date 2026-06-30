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

🔴 GATE: No completion wording until the claim is mapped to fresh evidence and the evidence actually proves that exact claim.

Apply the global Evidence-Driven Claim Hygiene rule to the completion report: tag every completion, verification, readiness, repo-state, and risk claim, or downgrade it to `I don't know.`, `Open Question`, `Unverified`, or `[GUESS]`.

Use the global language boundary: internal completion evidence uses English claim tags and `CONFIDENCE: HIGH | MED | LOW | VERY LOW | UNKNOWN`; user-facing completion/readiness/verification claims use the user's language and localized confidence/tags when available. Do not remove `Unverified` or localized uncertainty without new evidence.

Before making a completion claim:

1. Identify the claim.
2. Identify what evidence would prove it.
3. Run, inspect, or collect fresh evidence.
4. Read the full output and exit code when a command is used.
5. Report success only if the evidence supports the claim.
6. Otherwise report the actual status and unverified risk.

## Claim → Evidence Matrix

| Claim wording | Minimum acceptable evidence | Downgrade when missing |
|---|---|---|
| `implemented` | Diff inspection shows requested files/behavior changed | `changes drafted; implementation unverified` |
| `fixed` | Reproduction or targeted test now passes, or bug path manually verified | `fix attempted; not verified` |
| `tests passing` | Fresh command output with exit code/result read | `tests not run` or `tests failed` |
| `build/typecheck/lint passing` | Fresh relevant command output with exit code/result read | `check not run` or `check failed` |
| `ready` / `accepted` / `verified` | Required targeted evidence plus any requested broader gates; for formal changes, a spec coverage check mapping requirements/tasks/test-plan items to implementation, verification, review, and security evidence; stress-test if multi-source | `needs review`, `partially verified`, or `Unverified spec coverage` |
| `no new files/artifacts` | `git status`, `git ls-files --others`, or equivalent scoped inspection | `artifact state unverified` |

If evidence only proves a narrower claim, use the narrower wording.

## Completion Stress Test

Use `strategy-stress-test` before a completion claim when:

- the claim spans multiple files, modules, agents, or verification sources
- the verification evidence is partial, indirect, or mixed
- tests could not be run
- the work changed security, permissions, schema, migrations, release behavior, CI, or agent workflow rules
- subagent evidence is involved
- the final answer would say `ready`, `accepted`, `verified`, or equivalent beyond a narrow test result

The stress test must check:

- whether the evidence proves the exact claim
- whether unrun tests or uncovered boundaries remain
- whether formal-change requirements, tasks, and test-plan items have spec coverage evidence or are labeled `Open Question` / `Unverified`
- whether stale logs or assumptions are being used as proof
- whether final wording must be downgraded from `verified` to `implemented but unverified`

## Evidence Sources

Prefer the narrowest relevant source that proves the claim:

- targeted test command for changed behavior
- build, typecheck, lint, or format command for project health claims
- diff inspection for documentation-only or metadata-only claims
- browser, API, or manual runbook evidence for runtime behavior
- subagent evidence only after ROSE reconciles it and checks for conflicts
- spec coverage check for formal-change readiness claims, linking requirement/decision/risk to task/package, file/artifact, verification/review/security evidence, and uncovered `Open Question` / `Unverified` items

Do not treat stale output, assumptions, or partial logs as proof.

## Completion Evidence Format

```text
- Claim:
- Confidence: HIGH | MED | LOW | VERY LOW | UNKNOWN
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
