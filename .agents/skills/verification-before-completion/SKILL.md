---
name: verification-before-completion
description: Use after changed work or before an explicit fixed, passing, verified, ready, or complete claim. Run the smallest fresh check that proves the exact claim; do not create an automatic verifier lane, full-suite run, or review loop.
license: MIT
compatibility: opencode
---

# Verification Before Completion

## Goal

Match each success claim to fresh evidence without adding unnecessary process.

## Trigger

Use this skill when files or behavior changed, or when the answer would claim `fixed`, `passing`, `verified`, `ready`, or `complete`. It does not trigger for brainstorming, status-only answers, or unchanged copy.

## Method

1. State the exact claim.
2. Choose the smallest check that can prove it.
3. Run or inspect that check after the final edit.
4. Report what the evidence proves and what it does not.

Examples:

- documentation or metadata change: final diff and residual-reference inspection;
- focused logic change: targeted reproduction or test;
- type/build claim: the relevant typecheck or build command;
- broad readiness claim: only the gates explicitly required by the active contract.

Do not automatically dispatch a verifier, run a full suite, create a review swarm, or start a repair loop. Broaden verification only when the narrow check fails to cover the requested claim.

## Result

```text
CLAIM:
EVIDENCE:
RESULT: proved | failed | unverified
REMAINING RISK:
```

If evidence is missing, stale, partial, or failing, keep the claim `Unverified` or use narrower wording. Never convert absence of evidence into success.
