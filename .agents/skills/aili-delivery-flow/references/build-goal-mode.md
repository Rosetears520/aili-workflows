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
- existing `progress.txt`, `drift-log.md`, legacy `implementation-notes.html` as read-only migration evidence, closeout/review artifacts relevant to the current scope, and `rose-memory` checkpoints or handoff summaries when available.

Summarize the current goal, confirmed decisions, rejected options, open questions, `Unverified` items, traceability gaps, drift notes, evidence anchors, and next action before deciding scope, readiness, continuation, or completion. If new user input changes requirements after DEFINE, route back to DEFINE artifacts before BUILD. If the user requests implementation changes after a BUILD pass, treat them as a revised BUILD loop for the changed scope; SHIP remains release-readiness review over completed BUILD evidence.

## Session Marker and Goal Contract

When `/build` uses scoped continuation, establish a BUILD goal contract before automatic continuation can occur. The accepted default is a combined marker strategy:

- a transcript-visible marker so the current session is self-describing;
- the same compact contract recorded in repository-local BUILD context/progress state for resume.

The marker/contract must include:

- `goal_id` or equivalent stable session marker;
- change id or backend target and resolved repository root;
- user-approved scope boundary, non-goals, and forbidden scope;
- traceability sources for requirement/decision/risk coverage when the target is a formal change;
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

Before dispatching a queue with two or more independently actionable packages or lanes, add a concise parallelism analysis. Classify shared scaffold/source-of-truth work, safe parallel lanes, serial dependencies, concurrent read-only/research/review/test/search lanes, ownership boundaries, join points, expected evidence, blockers, and no-parallel reasons. Do not collapse existing package or lane boundaries without a dependency, ownership, verification, high-risk, missing-evidence, or current user-scope reason.

Each package must include:

- goal and acceptance criteria;
- likely allowed files or edit surface;
- forbidden scope and high-risk gates;
- evidence source;
- traceability mapping from source requirement/decision/risk to task/package, target files/artifacts, verification command or inspection, and expected evidence;
- parallelism role: shared scaffold/source-of-truth, safe parallel lane, serial dependency, research/review/test/search lane, blocked item, or no-parallel reason;
- owner/delegation plan;
- scoped subagent packet fields when delegated: allowed scope, forbidden scope, edit permission, high-risk stop gates, required evidence, and commit allowance;
- verification command or inspection path;
- code-review, test, and security lane trigger or skip condition;
- repair limit and rollback or pause condition;
- whether commits are allowed by the active contract;
- packaging target/platform and package/build command when packaging is requested.

Preserve task dependencies. Prefer packages small enough to review and repair independently. Worker increments are dynamic: split by verifiable acceptance slice, clean ownership boundary, no parallel edit conflict, and clean handoff point rather than fixed file counts.

## Supervisor Harness

During BUILD, ROSE remains Supervisor and owns final status. Workers may implement, inspect, review, test, or audit only inside their task packet. Worker results are compact evidence for reconciliation; they never decide final PASS/FAIL/`Unverified` status for the package or change.

ROSE must maintain the active context and progress ledgers when the backend contract requires them:

- read backend-specific `context.md` before dispatching implementation and before claiming BUILD/SHIP readiness;
- for OpenSpec, use `openspec/changes/<change-id>/context.md` and `openspec/changes/<change-id>/progress.txt`;
- for non-OpenSpec, resolve repository-local context/progress placement through the backend adapter or ask once before writing;
- only ROSE writes/appends `progress.txt`; workers return reports and evidence references for ROSE to reconcile;
- ledger entries record objective, worker dispatches, evidence references, traceability evidence, current progress, user feedback/corrections, checkpoint ledger, changed/inspected files, verification/review/security status, blockers, ROSE decision, and next action;
- never put secrets, raw logs, full transcripts, full file contents, or long dumps in `context.md` or `progress.txt`.

Before long continuation, idle resume, or expected DCP compression, update `progress.txt` first so the current BUILD state can be recovered without raw chat history.

For approved spec-backed implementation, ROSE maintains `drift-log.md` beside the active change artifacts as the compact model-readable drift log. Record only spec deviations, model drift/self-corrections, temporary decisions, trade-offs, open questions, unverified assumptions, and required DEFINE write-back; keep user feedback/corrections, ordinary progress ledger entries, review report status, raw transcripts, secrets, full logs, full file contents, and private data out of the file. Read legacy `implementation-notes.html` during hydration or convergence as migration evidence when present, but append new drift entries to it only when the active contract explicitly requires the legacy HTML format.

## Research-First Planning Gate

Before BUILD dispatch for unfamiliar stacks, official/API behavior, fast-changing or version-sensitive sources, packaging/distribution, platform/runtime behavior, security or permission surfaces, external integrations, UI/animation/product-form decisions, material model uncertainty, user-requested research/source verification, or industry/GitHub similar-project patterns, gather enough planning evidence to avoid guessing. Use the lightest appropriate route: source-driven official/API docs, mature-project/prior-art evidence, local repository evidence, or specialist research/search/security lanes.

The planning evidence must separate official facts, local facts, prior-art patterns, assumptions, rejected options, risks, applicability, and `Unverified` gaps. Present an evidence-backed 方案 and pause before implementation until the 方案 is confirmed, explicitly waived, or explicitly accepted as `UNVERIFIED`. Existing current evidence may satisfy the gate when it directly answers the planning question and is cited.

## User-Requested Packaging Flow

When the user requests a packaged deliverable, treat packaging as an explicit delivery step in the BUILD loop:

1. confirm the package target and platform when missing;
2. run the most relevant focused tests/checks first;
3. repair in-scope failures before packaging;
4. run the package/build command as separate evidence;
5. classify package-time failures as package-specific, prior implementation defects, environment/tooling gaps, or blocked high-risk requirements;
6. repair in-scope issues, rerun affected tests, and retry packaging within the approved repair limit;
7. report the artifact path, skipped verification waiver, `UNVERIFIED` risk, or blocker.

Pause before signing, notarization, platform certificates, dependency or lockfile changes, external publishing, destructive cleanup, secret handling, or unsupported platform assumptions unless the current task explicitly approves the exact operation.

## Evaluator-Gated Continuation

Automatic BUILD continuation is optional and must be evaluator-gated. The evaluator returns one explicit state plus a reason:

- `done`: no automatic continuation; ROSE reports completion evidence or residual risks.
- `continue`: a bounded continuation prompt may be sent only when loop budget remains and no stop condition is active.
- `blocked`: no automatic continuation; ROSE reports the blocker and required user/action decision.
- `unverified`: no automatic continuation; ROSE reports the unverified claim, evidence gap, and next action.

The accepted default evaluator path is a structured/rule-based evaluator plus a ROSE-owned decision prompt. The evaluator may use session-visible messages, `context.md`, `progress.txt`, `drift-log.md`, task state, legacy `implementation-notes.html` as read-only migration evidence, and necessary readonly git/status/search/test summaries. It must not read secrets, full logs, raw transcripts, or broad repository contents, and it must not edit files, update backend task/progress state, or claim final PASS/SHIP readiness. Any hook/plugin is a scheduler only; ROSE remains BUILD Supervisor and final status owner.

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
2. Confirm scope boundaries from evidence and map requirement/decision/risk sources to task/package, file/artifact boundary, verification command or inspection, and expected evidence.
3. Apply the research-first planning gate when it is triggered; do not dispatch implementation until evidence-backed 方案 confirmation, waiver, or `UNVERIFIED` acceptance is recorded.
4. Delegate non-trivial implementation to `implementer` using dynamically sized worker increments, or edit directly only when direct-work rules apply.
5. Run focused verification.
6. If packaging is requested, follow the verification-first packaging flow before reporting a deliverable artifact.
7. Run independent local review lanes: code review and test verification for non-trivial BUILD work, plus security review when security-sensitive surfaces are present; record explicit skip reasons.
8. Apply bounded repairs and rerun affected checks.
9. Update `progress.txt` or backend task state only after ROSE reconciles evidence into the traceability mapping; unresolved links must be labeled `Open Question` or `Unverified`.

After the queue, run aggregate freshness checks for changed scope and report completed packages, blocked packages, verification, skipped lanes, residual risks, traceability gaps labeled `Open Question` or `Unverified`, and whether `/ship` is appropriate.

## Task-End Branch/Worktree Hygiene

Before non-trivial package or queue closeout, inspect `git status --short --branch` in the target repository and classify dirty paths as task-scoped, unrelated/pre-existing, generated/ignored, scratch, or unknown. Remove only safe task-owned, non-user-visible scratch artifacts created by the current task. Propose cleanup for remaining residue, and ask explicit approval before push, destructive clean/reset, branch deletion, worktree removal, OpenSpec archive, stashing unrelated changes, or deleting user-visible artifacts. Savepoint commits may be proactive only when current task/project rules explicitly allow task-scoped verified commits; otherwise ask once with the cleanup package.

## Stop Conditions

Stop automatic continuation, report, or ask before continuing when:

- no unique target can be resolved;
- approval/readiness evidence is missing and not waived by the current active contract;
- a continuation lacks the scoped BUILD goal marker or the evaluator returns `done`, `blocked`, or `unverified`;
- the target repository root is not canonicalized as the intended workspace/repository, or is outside the current workspace or allowed external directories without explicit approval;
- the package requires destructive commands, file deletes/moves/renames, dependency or lockfile changes, schema/migration changes, auth/permission/security weakening, pushes, merges, tags, history rewrites, branch deletion, worktree removal, OpenSpec archive, stashing unrelated changes, or deleting user-visible artifacts;
- packaging requires signing/notarization credentials, external publishing, secret handling, destructive cleanup, or unsupported platform assumptions without explicit approval;
- scope expands beyond approved artifacts;
- acceptance criteria cannot be verified;
- required independent review, test, or security lanes are unavailable;
- repair limits are exhausted;
- continuation reaches max continuations, unchanged-state threshold, permission wait, runtime error, or an unvalidated hook/plugin recursion path;
- the user interrupts or changes the goal.

Do not stop merely because a manual implementation package was not supplied.
