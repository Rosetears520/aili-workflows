---
name: build-failure-repair
description: Repair build, typecheck, lint, or test failures with a root-cause-first minimal workflow; route read-only investigation before approved implementation, do not change dependencies or lockfiles without approval, and never bypass or skip failing gates to claim success.
---

# Build Failure Repair

Use this skill when an executable quality gate fails and the task is to get the gate passing without expanding scope.

## Trigger

- Build, typecheck, lint, unit test, integration test, fixture smoke, packaging, or CI command fails.
- A package is blocked on a reproducible failure and needs root-cause analysis followed by the smallest safe repair.
- Verification output suggests missing files, stale generated output, type errors, broken tests, changed fixtures, or environment-sensitive failures.

## Near Misses

- Runtime bug with no failing gate yet: use `debugging-and-error-recovery` to create or identify a repro first.
- Broad test strategy, coverage adequacy, or PR test matrix: use `pr-test-analysis` or `coverage-review`.
- Dependency upgrades, lockfile regeneration, toolchain migration, or CI redesign: stop for explicit approval before repair.
- Product behavior changes discovered during repair: return to the owner for scope clarification.

## Required Routing

- First lane: `debug-investigator` for read-only root-cause evidence when ROSE is orchestrating.
- Repair lane: `implementer` only after the likely root cause, exact files, allowed scope, and verification command are known or approved.
- Default repair style: minimal, task-scoped, reversible, and backed by a failing loop that becomes passing.

## Repair Workflow

1. Capture the exact command, exit status, failing output, environment clues, and recent changed files.
2. Reproduce the failure with the narrowest deterministic command available.
3. Localize the failure boundary: source, test, fixture, generated artifact, config, dependency/tooling, or environment.
4. State the top root-cause hypothesis and the proof expected after repair.
5. Apply the smallest code/test/config change inside the approved scope.
6. Re-run the failing command, then broaden only to adjacent gates needed to prove no regression.

## Boundaries

- Do not skip tests, loosen assertions, suppress type errors, ignore exit codes, lower quality gates, or mark failures as passing.
- Do not change dependencies, package managers, lockfiles, engine versions, generated-source policy, CI config, or public APIs without explicit approval.
- Do not hide unrelated failures; report them as pre-existing or out of scope with command evidence.
- Stop after three non-converging repair attempts and return `BLOCKED_VERIFICATION` with the evidence table.

## Verification

- Required evidence: original failing command, repair diff summary, rerun result, and any remaining skipped or unrelated failures.
- Passing means the exact failing gate passes without bypasses and the output supports the claimed scope.
- If the failure cannot be reproduced or the environment/tool is unavailable, report the closest probe and mark the repair readiness `Unverified` or blocked.
