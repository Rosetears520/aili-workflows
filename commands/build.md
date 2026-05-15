---
description: Build approved ready work autonomously through implementation and local quality gates.
agent: rose
subtask: false
---

# /build

User input:
$ARGUMENTS

Invoke `aili-delivery-flow` in BUILD mode.

Purpose:
- Treat `/build` as the user's approval to execute the current ready work item in autonomous goal mode, synthesize a scoped implementation package queue when needed, and prove the result with local quality gates.

Required behavior:
- Resolve the active target from user input, current OpenSpec/backend context, or a single ready work item; ask only when the target is missing or ambiguous.
- Re-read relevant DEFINE artifacts from disk before trusting their state.
- Infer the target repository root from the active backend/change context before running git safety commands; do not use the shell cwd as authority when it differs from the target repo.
- Build an ordered implementation package queue from tasks, specs, design, test plans, and repository evidence when the user did not provide an explicit package.
- Confirm target files, forbidden scope, acceptance criteria, verification command, and review lanes for each synthesized or user-provided package before editing that package.
- Work package-by-package until all in-scope packages are complete, blocked by an allowed stop condition, or repair limits are reached.
- Implement only in-scope packages and update task state as work completes with evidence.
- Run local BUILD gates: code review, test verification, and security review when security surfaces are present.

Hard stops:
- Do not edit if `/build` cannot resolve exactly one approved or ready target, or if approval/readiness evidence is missing and not explicitly waived by the current active contract.
- Do not edit if the inferred target repository root is outside the current workspace or allowed external directories without explicit external-directory approval.
- Do not ask for manual package approval only because the user omitted a package; synthesize the package queue instead.
- Pause before high-risk operations that require explicit approval: destructive commands, file deletes/moves/renames, dependency or lockfile changes, schema/migration changes, auth/permission/security weakening, pushes, merges, tags, or history rewrites.
- Do not stop after implementation without the local BUILD gates: code review, test verification, and security review when security surfaces are present.
- Stay inside the package; report scope expansion or missing verification instead of guessing.

Output contract:
- selected mode and backend;
- target, package queue summary, completed/blocked packages, and files changed;
- verification, review, and skipped-lane evidence;
- residual risks, scope expansions, and `Unverified` items;
- whether the change is ready for `/ship`.
