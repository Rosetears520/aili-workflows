# Review and Repair Loop

BUILD runs the local implementation quality loop. SHIP runs the fuller release-readiness loop that includes BUILD evidence plus broader handoff, merge, release, archive, or rollback checks.

## BUILD Local Gates

1. Gather the implementation diff, package scope, targeted verification evidence, and optional graph-assisted impact evidence when useful; summarize noisy or long evidence with `protocols/compact-evidence-pack.md`.
2. Run code review and test verification for the implemented package.
3. Run security review when the package touches auth, permissions, secrets, shell/installer behavior, dependencies, network, storage, or other security-sensitive surfaces.
4. Classify findings as must-fix, should-fix, accepted risk, out-of-scope, or unverified.
5. Apply only in-scope repairs and rerun affected verification/review lanes.
6. Return BUILD evidence with passed, skipped, blocked, and `Unverified` lanes; cite compact evidence packs instead of raw dumps when evidence is noisy, and never treat CodeGraph evidence as completion proof by itself.

## SHIP Release-Readiness Gates

1. Gather BUILD evidence, final diff, task scope, artifacts, requested release-blocker audit target, and closeout expectations; convert noisy prior evidence into compact evidence packs before reconciliation.
2. Resolve and report the audit target: current resolved change/final diff by default; named baseline or previous-release comparison only when a tag, commit, branch, or release reference is supplied; broader repository scan only when explicitly requested, risk-triggered, or the narrower target is insufficient.
3. Check whether BUILD review/test/security evidence is still fresh for the final diff and rerun stale or scope-affected lanes; optional graph-assisted residual scans may inform scope but do not replace lane evidence.
4. Audit release-blocker concerns: user-impacting regressions, security or permission exposure, unsafe/destructive workflow behavior, data-loss risk, documentation or artifact inconsistency, unresolved findings, rollback plan, commit/PR/release readiness, approval state, and unverified acceptance criteria.
5. Classify findings as `release-blocking`, `important`, `accepted risk`, `out-of-scope`, or `Unverified`. Resolve, disprove with fresh evidence, or obtain explicit risk acceptance from the user or current active contract owner for every `release-blocking` finding before a ready verdict.
6. Apply only approved in-scope repairs and rerun affected checks.
7. Produce a detailed repository-local Markdown closeout document with audited scope, compact fresh evidence, existing feature impact, remaining risks, `Unverified` items, recommendation, and next steps. The CLI response may be concise, but it must include the document path and verdict summary.

## Hard Gates

- No BUILD pass claim without local code-review and test evidence, plus security evidence or a recorded non-security skip reason.
- No SHIP ready claim without fresh release-readiness evidence.
- No noisy evidence claim from summary alone; cite source, scope, result, and rerun/artifact access through a compact evidence pack.
- No BUILD/SHIP proof claim from CodeGraph or graph-like discovery output alone; final readiness still requires fresh review, test, static inspection, or accepted verification evidence.
- No SHIP ready claim with unresolved, unproven, or not explicitly user-or-active-contract-accepted `release-blocking` findings.
- No baseline comparison from an inferred previous release; ask for the baseline or mark that lane `Open Question` / `Unverified`.
- No exhaustive whole-codebase no-bugs claim; report scanned scope, skipped lanes, evidence limits, and residual `Unverified` items.
- No silent scope expansion during repair.
- No chat-only SHIP closeout; every SHIP run must write or update the required repository-local Markdown closeout document, or explicitly block/mark `Unverified` if the document path or write is unavailable.
- No push, publish, archive, or durable memory promotion unless explicitly approved.

## Change Revision Decision

When review, test, or user feedback reveals a bug or adjustment after a lifecycle pass:

- If the issue has the same intent, overlapping scope, and the change is not archived, keep the current change and add repair tasks plus `test-plan.md` defect/fix/retest coverage.
- If the issue is in the same scope after SHIP but before archive, repair the current change and rerun affected review, test, and security lanes.
- If the source change is archived, merged, or released, open a new fix change and reference the source change instead of rewriting history.
- If the issue is about workflow, commands, skills, memory, subagents, installer, or tool policy, route through `harness-issue-triage` and then approved `harness-evolution`.
