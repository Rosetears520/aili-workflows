# BUILD Goal Mode

BUILD goal mode makes `/build` an autonomous execution entrypoint for the current ready work item. It is modeled on long-running goal workflows: the command starts work, ROSE keeps driving packages until completion or a real stop condition, and the user receives the aggregate result instead of repeated package-approval prompts.

Goal mode does not bypass tool permissions, repository rules, high-risk gates, or verification requirements.

## Activation

Use BUILD goal mode when:

- the user invokes `/build` or asks to build an approved change;
- exactly one active ready target can be resolved from command arguments, OpenSpec/backend state, or current task context;
- implementation approval is present through the command invocation or explicit user wording;
- DEFINE readiness is `READY`, explicitly waived, or accepted as `UNVERIFIED` by the current active contract.

Ask before editing only when the target is missing or ambiguous, readiness/approval evidence is missing and not waived by the current active contract, a high-risk gate is reached, or the resolved repository root is outside the current workspace or allowed external directories.

## Target and Repository Root Resolution

Before writing files or running git safety commands:

1. Resolve the active backend target from command arguments, OpenSpec change directory, task packet, or current context.
2. Infer and canonicalize the target repository root from the active change/backend context and repository markers.
3. Confirm the resolved root is the intended workspace/repository. If it is outside the current workspace or allowed external directories, stop for explicit external-directory approval before editing or running write-capable commands.
4. Run git status and branch checks in that target repository root.
5. If the shell cwd differs from the target repo, prefer the target repo and mention the inference in the BUILD evidence.

Do not fail solely because the harness/runtime cwd is not a git repository when the active target points to another repo.

## Package Queue Synthesis

When the user did not provide an explicit package, synthesize an ordered queue from the best available sources:

1. `tasks.md` or equivalent task list;
2. specs and acceptance criteria;
3. design notes and interface constraints;
4. `test-plan.md` or verification artifacts;
5. repository evidence and existing patterns.

Each package must include:

- goal and acceptance criteria;
- likely allowed files or edit surface;
- forbidden scope and high-risk gates;
- evidence source;
- owner/delegation plan;
- scoped subagent packet fields when delegated: allowed scope, forbidden scope, edit permission, high-risk stop gates, required evidence, and commit allowance;
- verification command or inspection path;
- code-review, test, and security lane trigger or skip condition;
- repair limit and rollback or pause condition;
- whether commits are allowed by the active contract.

Preserve task dependencies. Prefer packages small enough to review and repair independently.

## Execution Loop

For each package:

1. Refresh relevant artifacts and repository state.
2. Confirm scope boundaries from evidence.
3. Delegate broad/non-trivial implementation to `implementer` or edit directly only when direct-work rules apply.
4. Run focused verification.
5. Run local review lanes: code review, test verification, and security review when security surfaces are present.
6. Apply bounded repairs and rerun affected checks.
7. Update task state only after evidence supports completion.

After the queue, run aggregate freshness checks for changed scope and report completed packages, blocked packages, verification, skipped lanes, residual risks, and whether `/ship` is appropriate.

## Stop Conditions

Stop and ask when:

- no unique target can be resolved;
- approval/readiness evidence is missing and not waived by the current active contract;
- the target repository root is not canonicalized as the intended workspace/repository, or is outside the current workspace or allowed external directories without explicit approval;
- the package requires destructive commands, file deletes/moves/renames, dependency or lockfile changes, schema/migration changes, auth/permission/security weakening, pushes, merges, tags, or history rewrites;
- scope expands beyond approved artifacts;
- acceptance criteria cannot be verified;
- required review or verification lanes are unavailable;
- repair limits are exhausted;
- the user interrupts or changes the goal.

Do not stop merely because a manual implementation package was not supplied.
