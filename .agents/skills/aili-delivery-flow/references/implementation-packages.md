# Implementation Packages

An implementation package is the unit that BUILD may execute.

BUILD may receive a package explicitly from the user or synthesize an ordered package queue from approved ready artifacts. A `/build` invocation against a single ready target is enough approval to synthesize this queue; missing manual package text is not a stop condition.

## Required Fields

- goal and acceptance criteria;
- allowed files or scoped likely edit surface;
- forbidden scope;
- source artifacts and evidence;
- traceability mapping from source requirement, decision, or risk to task/package, target files or artifacts, verification command or inspection, and expected evidence or `Unverified` status;
- parallelism analysis: shared scaffold/source-of-truth work, safe parallel lanes, serial dependencies, concurrent research/review/test/search lanes, ownership boundaries, join points, expected evidence, blockers, or no-parallel reason;
- implementation owner or delegation plan;
- verification command(s);
- BUILD local review lanes: code review, test verification, and security review trigger or skip condition;
- repair or retry limit;
- rollback or pause condition;
- context/progress ledger placement when applicable;
- whether commits are allowed;
- task-end branch/worktree hygiene expectation for non-trivial closeout;
- packaging target/platform and package command when the user requested a packaged deliverable.

## Rules

- When no explicit package is supplied, synthesize packages from the highest-priority available artifacts: `tasks.md`, specs, design notes, `test-plan.md`, command arguments, and repository evidence.
- Each synthesized package must still name goal and acceptance criteria, likely edit surface, forbidden scope, evidence source, traceability mapping, owner or delegation plan, verification, review lanes, repair limit, rollback or pause condition, ledger handling, and commit allowance.
- For formal changes, every package must map each covered requirement, decision, or risk to the package task, file/artifact boundary, and verification/evidence target. If any link cannot be established, label it `Open Question` before dispatch when a decision is missing, or `Unverified` when evidence cannot yet prove coverage.
- Package implementation targets complete accepted behavior inside the package scope. `Surgical` or scoped means no unrelated changes, not artificially tiny or partial patches.
- Before dispatching two or more packages or work units, produce a visible parallelism analysis. Name any shared scaffold/source-of-truth package that must run first, safe parallel packages, serial dependencies, concurrent read-only/research/review/test/search lanes, ownership boundaries, join points, expected evidence, blockers, and the reason for any required serial execution.
- Preserve already separated package or lane boundaries unless dependency, ownership overlap, verification coupling, high-risk gating, failed/missing evidence, or explicit current user direction justifies merging or serializing them. Keep the boundary visible even when execution becomes serial.
- Delegated implementation packages must include a scoped subagent packet: allowed scope, forbidden scope, edit permission, high-risk stop gates, verification expectations, required evidence, and commit allowance.
- Preserve dependency order. Prefer dynamic increments that can be implemented completely, verified, reviewed, and repaired independently; use verifiability, reviewability, conflict-free ownership, and clean handoff as the sizing boundary rather than fixed file counts.
- Use subagents for broad evidence gathering, non-trivial implementation, noisy verification, and review lanes; ROSE remains responsible as Supervisor for integration, progress-ledger writes, and final judgment.
- Keep packages independently reviewable where practical.
- Do not combine unrelated feature, harness, install, and documentation work unless explicitly approved.
- BUILD is not complete after writing files; it must finish or explicitly block on independent local code-review and test gates, plus the security-review gate when a security-sensitive surface is present.
- Security review may be skipped only when no security-sensitive surface is present; record the skip reason.
- If an in-scope repair changes code or behavior, rerun the affected verification and review lane before returning BUILD evidence.
- If the user requested packaging, run the relevant tests/checks before packaging, repair in-scope failures first, run the package/build command as separate evidence, classify package-time failures, then repair/retest/repackage within the approved repair limit. Missing tests require an explicit waiver or `UNVERIFIED` risk before packaging proceeds.
- Workers return compact reports/evidence only. They do not write `progress.txt` and do not issue final PASS/FAIL/`Unverified` judgments. Their report must preserve the package traceability mapping by naming changed files/artifacts and verification evidence for each covered requirement, decision, or risk.
- For non-trivial package closeout, inspect branch/status, classify dirty paths as task-scoped, unrelated/pre-existing, generated/ignored, scratch, or unknown, remove only safe task-owned non-user-visible scratch artifacts, and ask explicit approval before push, destructive clean/reset, branch deletion, worktree removal, OpenSpec archive, stashing unrelated changes, or deleting user-visible artifacts.
- Pause if the package requires new dependencies, lockfile changes, schema changes, public API changes, forbidden files, broader scope than approved, signing/notarization credentials, external publishing, secret handling, destructive cleanup, or unsupported platform assumptions.

## Autonomous Queue Exit Criteria

Continue through the queue until one of these is true:

- all packages are implemented, verified, reviewed, and task state is updated with evidence;
- a stop condition requires explicit user approval;
- a package is blocked by missing target/readiness evidence, unavailable verification, or exhausted repair limits;
- the target repository root cannot be canonicalized inside the current workspace or allowed external directories;
- the user interrupts or narrows the goal.
