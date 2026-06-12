# BUILD Goal Mode

BUILD goal mode makes `/build` an autonomous execution entrypoint for the current ready work item. It is modeled on long-running goal workflows: the command starts work, ROSE acts as BUILD Supervisor, dispatches dynamic worker increments, keeps driving packages until completion or a real stop condition, and the user receives the aggregate result instead of repeated package-approval prompts.

Goal mode does not bypass tool permissions, repository rules, high-risk gates, or verification requirements.

## Activation

Use BUILD goal mode when:

- the user invokes `/build` or asks to build an approved change;
- exactly one active ready target can be resolved from command arguments, OpenSpec/backend state, or current task context;
- implementation approval is present through the command invocation or explicit user wording;
- DEFINE readiness is `READY`, explicitly waived, or accepted as `UNVERIFIED` by the current active contract.

Ask before editing only when the target is missing or ambiguous, readiness/approval evidence is missing and not waived by the current active contract, a high-risk gate is reached, or the resolved repository root is outside the current workspace or allowed external directories.

`/build` is the only user-facing goal-style execution command. Do not add, require, or route users through `/goal` or another public lifecycle command for this behavior.

## Hydration Gate and Continuity

Before BUILD starts, resumes, continues after idle, or claims completion, hydrate from disk and memory instead of relying on raw chat history:

- active idea capsule or `ideas/workflow-inbox.md` entry when an IDEATE-stage idea is being promoted or referenced;
- backend-specific `context.md`, specs/design/tasks, `interview.md`, and `test-plan.md` when present;
- existing `progress.txt`, `implementation-notes.html`, closeout/review artifacts relevant to the current scope, and `rose-memory` checkpoints or handoff summaries when available.

Summarize the current goal, confirmed decisions, rejected options, open questions, `Unverified` items, drift notes, evidence anchors, and next action before deciding scope, readiness, continuation, or completion. If new user input changes requirements after DEFINE, route back to DEFINE artifacts before BUILD. If the user requests implementation changes after a BUILD pass, treat them as a revised BUILD loop for the changed scope; SHIP remains release-readiness review over completed BUILD evidence.

## Session Marker and Goal Contract

When `/build` uses scoped continuation, establish a BUILD goal contract before automatic continuation can occur. The accepted default is a combined marker strategy:

- a transcript-visible marker so the current session is self-describing;
- the same compact contract recorded in repository-local BUILD context/progress state for resume.

The marker/contract must include:

- `goal_id` or equivalent stable session marker;
- change id or backend target and resolved repository root;
- user-approved scope boundary, non-goals, and forbidden scope;
- evaluator criteria and required evidence sources;
- loop budget, including max continuations and unchanged-state threshold;
- stop conditions and permission policy summary.

Do not include secrets, credentials, raw logs, full transcripts, full file contents, or broad repository dumps in marker, context, progress, or evaluator input. ROSE owns the repository-local context/progress write; workers return compact evidence for reconciliation.

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

Preserve task dependencies. Prefer packages small enough to review and repair independently. Worker increments are dynamic: split by verifiable acceptance slice, clean ownership boundary, no parallel edit conflict, and clean handoff point rather than fixed file counts.

## Supervisor Harness

During BUILD, ROSE remains Supervisor and owns final status. Workers may implement, inspect, review, test, or audit only inside their task packet. Worker results are compact evidence for reconciliation; they never decide final PASS/FAIL/`Unverified` status for the package or change.

ROSE must maintain the active context and progress ledgers when the backend contract requires them:

- read backend-specific `context.md` before dispatching implementation and before claiming BUILD/SHIP readiness;
- for OpenSpec, use `openspec/changes/<change-id>/context.md` and `openspec/changes/<change-id>/progress.txt`;
- for non-OpenSpec, resolve repository-local context/progress placement through the backend adapter or ask once before writing;
- only ROSE writes/appends `progress.txt`; workers return reports and evidence references for ROSE to reconcile;
- ledger entries record objective, current progress, user feedback/corrections, checkpoint ledger, worker dispatches, evidence, changed/inspected files, verification/review/security status, blockers, ROSE decision, and next action;
- never put secrets, raw logs, full transcripts, full file contents, or long dumps in `context.md` or `progress.txt`.

Before long continuation, idle resume, or expected DCP compression, update `progress.txt` first so the current BUILD state can be recovered without raw chat history.

For approved spec-backed implementation, ROSE also maintains `implementation-notes.html` beside the active change artifacts as a compact drift log. Record only spec deviations/interpretation, temporary decisions, trade-offs, open questions, unverified assumptions, and required DEFINE write-back; keep user feedback/corrections, progress ledger entries, raw transcripts, secrets, full logs, full file contents, and private data out of the file.

## Evaluator-Gated Continuation

Automatic BUILD continuation is optional and must be evaluator-gated. The evaluator returns one explicit state plus a reason:

- `done`: no automatic continuation; ROSE reports completion evidence or residual risks.
- `continue`: a bounded continuation prompt may be sent only when loop budget remains and no stop condition is active.
- `blocked`: no automatic continuation; ROSE reports the blocker and required user/action decision.
- `unverified`: no automatic continuation; ROSE reports the unverified claim, evidence gap, and next action.

The accepted default evaluator path is a structured/rule-based evaluator plus a ROSE-owned decision prompt. The evaluator may use session-visible messages, `context.md`, `progress.txt`, task state, `implementation-notes.html`, and necessary readonly git/status/search/test summaries. It must not read secrets, full logs, raw transcripts, or broad repository contents, and it must not edit files, update backend task/progress state, or claim final PASS/SHIP readiness. Any hook/plugin is a scheduler only; ROSE remains BUILD Supervisor and final status owner.

## Continuation Loop Budget and Runtime Fallback

Default loop budget starts small:

- max continuations: 3;
- unchanged-state threshold: 1;
- immediate stop on permission wait, failed required verification, user interruption, scope expansion, high-risk gate, runtime error, exhausted repair limit, exhausted loop budget, or evaluator `done`/`blocked`/`unverified`.

Before hardening or enabling a runtime hook/plugin, run the validation spike for the selected OpenCode path, especially marked `session.idle` or equivalent event followed by bounded same-session continuation. The spike must show marked-only continuation, ignored unmarked sessions, no duplicate prompts, usable lock/debounce behavior, max-loop stop, and safe stop on errors. If recursion is unreliable or remains `Unverified`, keep the plugin disabled or skipped by default and continue using prompt-only `/build` manual autonomous mode.

## Scoped Permission Policy

Scoped BUILD continuation does not weaken global tool safety. Do not use global `permission: "allow"`, do not rely on `--dangerously-skip-permissions`, and do not auto-approve ordinary chat, IDEATE, DEFINE, SHIP, or unmarked BUILD sessions.

The default allowlist for marked BUILD goal sessions is limited to readonly/status/search operations and verification commands explicitly approved by the current task contract. Edits, destructive shell actions, external-directory access, secret reads, dependency or lockfile changes, auth/security weakening, pushes, merges, tags, and history rewrites remain ask/deny unless the current task contract explicitly approves them.

## Execution Loop

For each package:

1. Hydrate relevant artifacts, memory/checkpoints, progress, drift notes, and repository state.
2. Confirm scope boundaries from evidence.
3. Delegate non-trivial implementation to `implementer` using dynamically sized worker increments, or edit directly only when direct-work rules apply.
4. Run focused verification.
5. Run independent local review lanes: code review and test verification for non-trivial BUILD work, plus security review when security-sensitive surfaces are present; record explicit skip reasons.
6. Apply bounded repairs and rerun affected checks.
7. Update `progress.txt` or backend task state only after ROSE reconciles evidence.

After the queue, run aggregate freshness checks for changed scope and report completed packages, blocked packages, verification, skipped lanes, residual risks, and whether `/ship` is appropriate.

## Stop Conditions

Stop automatic continuation, report, or ask before continuing when:

- no unique target can be resolved;
- approval/readiness evidence is missing and not waived by the current active contract;
- a continuation lacks the scoped BUILD goal marker or the evaluator returns `done`, `blocked`, or `unverified`;
- the target repository root is not canonicalized as the intended workspace/repository, or is outside the current workspace or allowed external directories without explicit approval;
- the package requires destructive commands, file deletes/moves/renames, dependency or lockfile changes, schema/migration changes, auth/permission/security weakening, pushes, merges, tags, or history rewrites;
- scope expands beyond approved artifacts;
- acceptance criteria cannot be verified;
- required independent review, test, or security lanes are unavailable;
- repair limits are exhausted;
- continuation reaches max continuations, unchanged-state threshold, permission wait, runtime error, or an unvalidated hook/plugin recursion path;
- the user interrupts or changes the goal.

Do not stop merely because a manual implementation package was not supplied.
