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
- Package 12 review-lane relevance or Package 1–11 deferral note;
- objective iteration budget and, only for Package 12, the holistic review-repair limit;
- rollback or pause condition;
- context/progress ledger placement when applicable;
- whether commits are allowed;
- task-end branch/worktree hygiene expectation for non-trivial closeout;
- packaging target/platform and package command when the user requested a packaged deliverable.

## Rules

- When no explicit package is supplied, synthesize packages from the highest-priority available artifacts: `tasks.md`, specs, design notes, `test-plan.md`, command arguments, and repository evidence.
- Each synthesized package must still name goal and acceptance criteria, likely edit surface, forbidden scope, evidence source, traceability mapping, owner or delegation plan, optional feedback command, Package 12 review relevance or Package 1–11 deferral, canonical objective budget, rollback or pause condition, ledger handling, and commit allowance.
- For formal changes, every package must map each covered requirement, decision, or risk to the package task, file/artifact boundary, and verification/evidence target. If any link cannot be established, label it `Open Question` before dispatch when a decision is missing, or `Unverified` when evidence cannot yet prove coverage.
- Package implementation targets complete accepted behavior inside the package scope. `Surgical` or scoped means no unrelated changes, not artificially tiny or partial patches.
- Before dispatching two or more packages or work units, produce a visible parallelism analysis. Name any shared scaffold/source-of-truth package that must run first, safe parallel packages, serial dependencies, concurrent read-only/research/review/test/search lanes, ownership boundaries, join points, expected evidence, blockers, and the reason for any required serial execution.
- Preserve already separated package or lane boundaries unless dependency, ownership overlap, verification coupling, high-risk gating, failed/missing evidence, or explicit current user direction justifies merging or serializing them. Keep the boundary visible even when execution becomes serial.
- Delegated implementation packages must include a scoped subagent packet: allowed scope, forbidden scope, edit permission, high-risk stop gates, verification expectations, required evidence, and commit allowance.
- A cross-root package references exactly one canonical `WT-001` context from `protocols/worktree-context.md`; it never duplicates or rebinds identity/approval/path evidence. Its `role_overlay` is evidence/narrowing text only, never authority or proof of final effective rules. Probe exit other than `0`, missing merged-rule provenance, missing override-absence evidence, or `Unverified` status blocks cross-root use.
- A30 permits only ROSE Task-dispatched external reads by the exact selected read-only roles. It grants no cross-root implementer, test, debug, browser, E2E, shell, artifact-write, or nested-delegation capability. Direct user `@` invocation is outside A30 guarantees.
- Preserve dependency order. Prefer dynamic increments that can be implemented completely and remain independently traceable/reviewable; use verifiability, conflict-free ownership, and clean handoff as sizing boundaries rather than fixed file counts.
- Use subagents for broad evidence gathering and non-trivial implementation when routing permits; Package 12 owns mandatory independent review lanes. ROSE remains responsible for integration, progress-ledger writes, and final judgment.
- Keep packages independently reviewable where practical.
- Do not combine unrelated feature, harness, install, and documentation work unless explicitly approved.
- Package 1–11 are not closed by optional package-local code-review, test, security, convergence, or repair-budget evidence. They finish complete accepted behavior and a lightweight savepoint; preserve known quality findings for Package 12.
- Package 12 is the single mandatory comprehensive quality gate and uses exactly three holistic review-repair cycles at most, rerunning affected checks and the complete task matrix.
- If the user requested packaging, run the relevant tests/checks before packaging, repair in-scope failures first, run the package/build command as separate evidence, classify package-time failures, then repair/retest/repackage within the approved repair limit. Missing tests require an explicit waiver or `UNVERIFIED` risk before packaging proceeds.
- Workers return compact reports/evidence only. They do not write `progress.txt` and do not issue final PASS/FAIL/`Unverified` judgments. Their report must preserve the package traceability mapping by naming changed files/artifacts and verification evidence for each covered requirement, decision, or risk.
- For non-trivial package closeout, inspect branch/status, classify dirty paths as task-scoped, unrelated/pre-existing, generated/ignored, scratch, or unknown, remove only safe task-owned non-user-visible scratch artifacts, and ask explicit approval before push, destructive clean/reset, branch deletion, worktree removal, OpenSpec archive, stashing unrelated changes, or deleting user-visible artifacts.
- Pause if the package requires new dependencies, lockfile changes, schema changes, public API changes, forbidden files, broader scope than approved, signing/notarization credentials, external publishing, secret handling, destructive cleanup, or unsupported platform assumptions.

## Autonomous Queue Exit Criteria

Continue through the queue until one of these is true:

- Packages 1–11 are completely implemented/savepointed and Package 12 has completed its mandatory comprehensive gate;
- a stop condition requires explicit user approval;
- a package is blocked by missing target/readiness evidence, unverifiable accepted behavior, or exhausted canonical objective budgets;
- the target repository root cannot be canonicalized inside the current workspace or allowed external directories;
- the user interrupts or narrows the goal.
