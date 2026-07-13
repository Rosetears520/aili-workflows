# Review and Repair Loop

Packages 1–11 implement complete accepted behavior and record lightweight savepoints without mandatory package-local quality closure. Package 12 runs the single comprehensive BUILD quality loop. SHIP uses that evidence plus broader release-readiness checks.

## Package 12 comprehensive BUILD gate

1. Require complete Package 1–11 implementations and lightweight savepoints; gather the final diff, P11 Partial traceability, optional feedback, and known findings. P11 traceability stays non-final. ROSE creates the separate final task-audit JSON only after command and review reconciliation; the final checker reads but never generates it.
2. Run the fresh full command matrix and independently dispatch diverse read-only canonical convergence, code, test/coverage, security, AI-regression, silent-failure, generated/docs/manifests, and other relevant lanes. Route prompt/agent/skill/model-tool/generated-output behavior to `ai-regression-scout`; route ordinary product test design/execution/coverage to `test-engineer`; dispatch both with distinct questions when both apply. Every final-review packet denies nested task dispatch; lanes return directly to ROSE using the shared finding/result envelope. This overlay is required policy, but declarative fields do not prove runtime enforcement; retain `UV-001` as `Unverified` until an executable permission probe proves the effective denial.
3. Join every expected lane at ROSE without majority voting, lane-count verdicts, averaged confidence, or worker final authority; missing evidence remains blocking or `Unverified`, and a credible material minority finding remains open until evidence-backed disposition. Final closure requires all 74 exact nine-field ROSE audit rows to be `Done` or resolved source-backed `N/A`, with final task-specific files/evidence, empty findings, resolved dispositions, and verified `UV-001` read-only edit and nested-task runtime enforcement.
4. Classify findings as must-fix, should-fix, accepted risk, out-of-scope, or unverified.
5. Apply all in-scope repairs for one holistic cycle, rerun affected lanes and the complete task matrix, and stop after at most three cycles.
6. For non-trivial closeout, inspect branch/status, classify dirty paths as task-scoped, unrelated/pre-existing, generated/ignored, scratch, or unknown, remove only safe task-owned non-user-visible scratch artifacts, and propose cleanup for residue.
7. Return BUILD evidence with passed, skipped, blocked, and `Unverified` lanes; map each changed file/artifact and verification result back to its source requirement, decision, or risk; cite compact evidence packs instead of raw dumps when evidence is noisy, and never treat CodeGraph evidence as completion proof by itself.

## SHIP Release-Readiness Gates

1. Gather BUILD evidence, final diff, task scope, artifacts, traceability matrix, requested release-blocker audit target, and closeout expectations; convert noisy prior evidence into compact evidence packs before reconciliation.
2. Resolve and report the audit target: current resolved change/final diff by default; named baseline or previous-release comparison only when a tag, commit, branch, or release reference is supplied; broader repository scan only when explicitly requested, risk-triggered, or the narrower target is insufficient.
3. Check whether BUILD review/test/security evidence is still fresh for the final diff and rerun stale or scope-affected lanes; optional graph-assisted residual scans may inform scope but do not replace lane evidence.
4. Run a spec coverage check for formal changes: compare accepted requirements/tasks/test-plan items against changed files/artifacts, verification evidence, review findings, and security evidence or skip reason; label uncovered items `Open Question` or `Unverified` before any readiness claim.
5. Audit release-blocker concerns: user-impacting regressions, security or permission exposure, unsafe/destructive workflow behavior, data-loss risk, documentation or artifact inconsistency, unresolved findings, rollback plan, commit/PR/release readiness, approval state, uncovered spec items, and unverified acceptance criteria.
6. Classify findings as `release-blocking`, `important`, `accepted risk`, `out-of-scope`, or `Unverified`. Resolve, disprove with fresh evidence, or obtain explicit risk acceptance from the user or current active contract owner for every `release-blocking` finding before a ready verdict.
7. Apply only approved in-scope repairs and rerun affected checks.
8. Inspect branch/status, classify dirty paths as task-scoped, unrelated/pre-existing, generated/ignored, scratch, or unknown, remove only safe task-owned non-user-visible scratch artifacts, and record cleanup approvals needed.
9. Produce a detailed repository-local Markdown closeout document with audited scope, spec coverage check result, compact fresh evidence, existing feature impact, branch/worktree hygiene status, remaining risks, `Open Question` / `Unverified` items, recommendation, and next steps. The CLI response may be concise, but it must include the document path and verdict summary.

## Hard Gates

- No Package 1–11 mandatory quality gate, package-quality repair budget, or closure claim from optional feedback.
- No BUILD pass claim before Package 12's complete task matrix, fresh command matrix, and joined diverse-lane evidence.
- No fourth holistic cycle, reduced matrix, dropped minority finding, nested final-review dispatch, vote-based verdict, or worker-owned final disposition.
- No SHIP ready claim without fresh release-readiness evidence.
- No SHIP ready claim for a formal change without a spec coverage check covering requirements/tasks/test-plan items against implementation, verification, review, and security evidence.
- No noisy evidence claim from summary alone; cite source, scope, result, and rerun/artifact access through a compact evidence pack.
- No BUILD/SHIP proof claim from CodeGraph or graph-like discovery output alone; final readiness still requires fresh review, test, static inspection, or accepted verification evidence.
- No SHIP ready claim with unresolved, unproven, or not explicitly user-or-active-contract-accepted `release-blocking` findings.
- No baseline comparison from an inferred previous release; ask for the baseline or mark that lane `Open Question` / `Unverified`.
- No exhaustive whole-codebase no-bugs claim; report scanned scope, skipped lanes, evidence limits, and residual `Open Question` / `Unverified` items.
- No silent scope expansion during repair.
- No chat-only SHIP closeout; every SHIP run must write or update the required repository-local Markdown closeout document, or explicitly block/mark `Unverified` if the document path or write is unavailable.
- No push, publish, OpenSpec archive, durable memory promotion, destructive clean/reset, branch deletion, worktree removal, stashing unrelated changes, or user-visible artifact deletion unless explicitly approved.

## Change Revision Decision

When review, test, or user feedback reveals a bug or adjustment after a lifecycle pass:

- If the issue has the same intent, overlapping scope, and the change is not archived, keep the current change and add repair tasks plus `test-plan.md` defect/fix/retest coverage.
- If the issue is in the same scope after SHIP but before archive, repair the current change and rerun affected review, test, and security lanes.
- If the source change is archived, merged, or released, open a new fix change and reference the source change instead of rewriting history.
- If the issue is about workflow, commands, skills, memory, subagents, installer, or tool policy, route through `harness-issue-triage` and then approved `harness-evolution`.
