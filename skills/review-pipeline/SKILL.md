---
name: review-pipeline
description: Orchestrates post-implementation review before final PASS. Use after non-trivial changes to fan out code-reviewer, test-engineer, security-auditor when relevant, reconcile findings, run a bounded fix loop, and gate completion without pushing or merging.
---

# Review Pipeline

## Purpose

Use this skill after non-trivial implementation and before ROSE claims `PASS`, `ready`, or equivalent acceptance.

It is an orchestration workflow, not a reviewer persona. ROSE owns dispatch, reconciliation, and final acceptance.

In the AILI lifecycle, this skill is normally entered from `aili-delivery-flow` SHIP mode; keep lifecycle gates there and keep this file focused on review orchestration.

## When to Use

Use after changes that are multi-file, behavior-changing, security-sensitive, permission-related, test-heavy, release-impacting, or hard to verify by a single narrow command.

Do not use for tiny documentation or one-line edits where diff inspection and a narrow check are sufficient.

## Workflow

### Phase 1: Identify Review Target

Collect:

- original user goal and accepted scope
- changed files and diff range
- acceptance criteria
- verification commands already run and results
- known skipped checks or `Unverified` items

### Phase 2: Fan Out Review

Dispatch only relevant read-only reviewers:

🔴 CHECKPOINT before dispatch: reviewers must be read-only, relevant to the changed surface, and given the same review target, accepted scope, diff/files, verification evidence, and stop conditions. Do not dispatch security or test lanes away when the changed surface makes them relevant.

- `code-reviewer`: correctness, maintainability, architecture, performance, and context adequacy
- `test-engineer`: coverage gaps, test quality, and verification story
- `security-auditor`: auth, permissions, secrets, command execution, network, dependency, deployment, schema, or data risk
- `code-scout`: context mining only when a reviewer reports missing repository context

When the changed surface is cross-file, high-risk, or likely to miss callers/consumers/tests, ROSE may request optional CodeGraph-assisted residual impact evidence from the relevant review/test lane or scout. Treat it as scope discovery only; reviewers and testers must still inspect the diff, critical files, tests, commands, or behavior before conclusions, and absence/staleness/noise only becomes `Unverified` when material to confidence.

Do not ask reviewers to edit files. Do not let reviewers spawn nested agents except where their own agent contract explicitly allows `code-scout`.

### Phase 3: Reconcile

Merge duplicate findings and classify each as:

- Critical: blocks acceptance or could cause data loss, security exposure, broken behavior, or irreversible workflow damage
- Important: should be fixed before acceptance unless user explicitly accepts the risk
- Suggestion: non-blocking improvement or follow-up

Name conflicts between reviewers and resolve them with evidence. If evidence is insufficient, mark the item `Unverified` instead of approving it.

🔴 CHECKPOINT before accepting reconciliation: each blocker must be fixed, disproven with cited evidence, or explicitly accepted by the user. ROSE remains responsible for the final gate; reviewers provide evidence and recommendations, not final PASS.

| Reconciliation failure | Required action | Do not do |
|---|---|---|
| Reviewers disagree on severity or correctness | Read cited evidence, classify by user scope and acceptance criteria, and request one focused follow-up only if needed | Average the opinions or choose the convenient result |
| A finding has no concrete evidence | Mark `Unverified` and ask for bounded evidence if it affects acceptance | Treat reviewer confidence as proof |
| A security/test lane reports missing context | Dispatch `code-scout` or a focused re-check for that context | Let ROSE invent context or waive the gate silently |
| Fix verification passes but reviewer concern remains plausible | Re-run only the relevant reviewer lane with the new diff and evidence | Claim PASS from the command result alone |
| Graph-assisted residual scan finds high-risk targets not inspected | Inspect or dispatch the responsible lane for those targets, or mark them `Unverified` | Treat graph output alone as proof of impact or safety |

### Phase 4: Fix Loop

If blocking issues exist:

1. Send a bounded work package to `implementer` or fix directly when the edit is small and safe.
2. Run the narrowest verification that proves the fix.
3. Re-run only the relevant reviewer pass.
4. 🛑 STOP after three non-converging loops on the same finding class; report `BLOCKED_VERIFICATION` or `BLOCKED_REVIEW` with the attempts, evidence, and remaining decision needed.

### Phase 5: Completion Gate

Return `PASS` only when blocking issues are resolved, disproven with evidence, or explicitly accepted by the user.

Never push, create PRs, merge, delete branches, or clean worktrees from this skill without explicit user approval.

## Output Contract

```text
REVIEW PIPELINE STATUS: PASS | NEEDS_FIXES | BLOCKED | SKIPPED

REVIEW TARGET:
- Diff/files:
- User goal:
- Verification already run:

FINDINGS:
- [Critical|Important|Suggestion] source - finding - evidence - required action

FIX LOOP:
- <fixes applied and verification, or N/A>

REMAINING UNVERIFIED:
- <item or N/A>

COMPLETION GATE:
- Safe to claim PASS: yes | no | conditional
- Reason:
```
