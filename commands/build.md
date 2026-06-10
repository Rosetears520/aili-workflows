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
- Treat `/build` as the user's only public goal-style execution entrypoint: execute the current ready work item in autonomous goal mode for BUILD, synthesize a scoped implementation package queue when needed, and prove the result with local quality gates.

Required behavior:
- Resolve the active target from user input, current OpenSpec/backend context, or a single ready work item; ask only when the target is missing or ambiguous.
- Hydrate current state before acting: re-read relevant DEFINE artifacts from disk plus active idea/context/progress/test/notes artifacts and memory/checkpoints when present, then summarize the current goal, decisions, open questions, `Unverified` items, drift notes, and next action.
- Infer the target repository root from the active backend/change context before running git safety commands; do not use the shell cwd as authority when it differs from the target repo.
- Establish a scoped BUILD goal marker/contract when continuation is needed, using a transcript-visible marker plus repository-local context/progress state; include `goal_id`, backend/change target, repository root, scope boundary, evaluator criteria, loop budget, stop conditions, and permission policy summary, without secrets, raw logs, full transcripts, or full file contents.
- Build an ordered implementation package queue from tasks, specs, design, test plans, and repository evidence when the user did not provide an explicit package.
- Confirm target files, forbidden scope, acceptance criteria, verification command, and review lanes for each synthesized or user-provided package before editing that package.
- Work package-by-package until all in-scope packages are complete, blocked by an allowed stop condition, or repair limits are reached; any automatic continuation must be gated by a structured evaluator state of `done`, `continue`, `blocked`, or `unverified` plus a ROSE-owned decision prompt.
- Implement only in-scope packages and update task state as work completes with evidence.
- Maintain `implementation-notes.html` during approved spec-backed implementation as the compact drift log for spec deviations, temporary decisions, unresolved assumptions, verification pointers, and required DEFINE write-back.
- Run local BUILD gates: code review, test verification, and security review when security surfaces are present.

Hard stops:
- Do not edit if `/build` cannot resolve exactly one approved or ready target, or if approval/readiness evidence is missing and not explicitly waived by the current active contract.
- Do not edit if the inferred target repository root is outside the current workspace or allowed external directories without explicit external-directory approval.
- Do not add or route users to `/goal`, `commands/goal.md`, or any new public delivery command; scoped goal execution is BUILD behavior only.
- Do not ask for manual package approval only because the user omitted a package; synthesize the package queue instead.
- Do not harden, enable by default, or depend on a scoped hook/plugin before the OpenCode validation spike proves marked-session recursion safe; fall back to prompt-only `/build` manual autonomous mode when runtime continuation remains `Unverified`.
- Do not weaken global permissions, use global `permission: "allow"`, or rely on `--dangerously-skip-permissions`; any scoped allowlist is limited to marked BUILD sessions, readonly/status/search operations, and current-task-approved verification commands.
- Pause before high-risk operations that require explicit approval: destructive commands, file deletes/moves/renames, dependency or lockfile changes, schema/migration changes, auth/permission/security weakening, pushes, merges, tags, or history rewrites.
- Do not stop after implementation without the local BUILD gates: code review, test verification, and security review when security surfaces are present.
- Stay inside the package; report scope expansion or missing verification instead of guessing.

Output contract:
- selected mode and backend;
- target, package queue summary, completed/blocked packages, and files changed;
- verification, review, and skipped-lane evidence;
- residual risks, scope expansions, and `Unverified` items;
- whether the change is ready for `/ship`.
