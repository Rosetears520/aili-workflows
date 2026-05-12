# Review and Repair Loop

BUILD runs the local implementation quality loop. SHIP runs the fuller release-readiness loop that includes BUILD evidence plus broader handoff, merge, release, archive, or rollback checks.

## BUILD Local Gates

1. Gather the implementation diff, package scope, and targeted verification evidence.
2. Run code review and test verification for the implemented package.
3. Run security review when the package touches auth, permissions, secrets, shell/installer behavior, dependencies, network, storage, or other security-sensitive surfaces.
4. Classify findings as must-fix, should-fix, accepted risk, out-of-scope, or unverified.
5. Apply only in-scope repairs and rerun affected verification/review lanes.
6. Return BUILD evidence with passed, skipped, blocked, and `Unverified` lanes.

## SHIP Release-Readiness Gates

1. Gather BUILD evidence, final diff, task scope, artifacts, and closeout expectations.
2. Check whether BUILD review/test/security evidence is still fresh for the final diff and rerun stale or scope-affected lanes.
3. Audit release-readiness concerns: documentation, artifact consistency, unresolved findings, rollback plan, commit/PR/release readiness, and approval state.
4. Apply only approved in-scope repairs and rerun affected checks.
5. Produce closeout with remaining risks and next steps.

## Hard Gates

- No BUILD pass claim without local code-review and test evidence, plus security evidence or a recorded non-security skip reason.
- No SHIP ready claim without fresh release-readiness evidence.
- No silent scope expansion during repair.
- No push, publish, archive, or durable memory promotion unless explicitly approved.
