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

- `code-reviewer`: correctness, maintainability, architecture, performance, and context adequacy
- `test-engineer`: coverage gaps, test quality, and verification story
- `security-auditor`: auth, permissions, secrets, command execution, network, dependency, deployment, schema, or data risk
- `code-scout`: context mining only when a reviewer reports missing repository context

Do not ask reviewers to edit files. Do not let reviewers spawn nested agents except where their own agent contract explicitly allows `code-scout`.

### Phase 3: Reconcile

Merge duplicate findings and classify each as:

- Critical: blocks acceptance or could cause data loss, security exposure, broken behavior, or irreversible workflow damage
- Important: should be fixed before acceptance unless user explicitly accepts the risk
- Suggestion: non-blocking improvement or follow-up

Name conflicts between reviewers and resolve them with evidence. If evidence is insufficient, mark the item `Unverified` instead of approving it.

### Phase 4: Fix Loop

If blocking issues exist:

1. Send a bounded work package to `implementer` or fix directly when the edit is small and safe.
2. Run the narrowest verification that proves the fix.
3. Re-run only the relevant reviewer pass.
4. Stop after three non-converging loops and report `BLOCKED_VERIFICATION` or `BLOCKED_REVIEW`.

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
