# Test Document Policy

The test document turns requirements into verification evidence before implementation starts.

## Required Content

- requirement or scenario identifier;
- traceability matrix for formal changes, mapping requirement, decision, or risk to task/package, file or artifact, verification command or inspection, evidence, and coverage status;
- test case or manual check;
- expected result;
- command or evidence source;
- status: planned, passed, failed, skipped, or unverified.

## Gate

- DEFINE should create or update the acceptance test document for non-trivial work. For OpenSpec-backed changes, DEFINE writes `openspec/changes/<change-id>/test-plan.md` through `test-document-generator`.
- Formal changes must include a requirements/decisions/risks traceability matrix. Missing task/package, file/artifact, verification, or evidence links must be labeled `Open Question` when they need a decision, or `Unverified` when they need later evidence.
- BUILD may start only after applicable decision-shaping research is closed, the artifacts and traceability are coherent/validated, and the user explicitly accepts the final test plan. A waiver or accepted-`Unverified` label cannot substitute for either material research closure or final test-plan acceptance.
- Named non-material runtime residuals such as UV-006/UV-007 may remain explicitly `Unverified` only when their runtime/operation paths fail closed; they continue to block any claim or operation that needs the missing evidence.
- BUILD readiness is only `READY` or `BLOCKED`; `WAIVED` and accepted-`UNVERIFIED` are not readiness alternatives. Package savepoints and package boundaries add no test-plan or package approval.
- BUILD ends after one minimal changed-scope completion check at `IMPLEMENTED_TARGETED_VERIFIED`. SHIP requires fresh explicit intent, reuses event-fresh BUILD evidence, and selects only stale/affected/risk/integration/packaging/release/merge-result/target checks. A full traceability matrix or review/test/security evidence lane is required only for a concrete gap or affected SHIP claim.
- Material DEFINE decisions, the one final test-plan acceptance, fresh SHIP intent, and exact commit/push/merge/release approvals remain distinct controls. CI failure returns to the user and never authorizes automatic repair, commit, push, merge, or release.

## Artifact Freshness Gate

Conversation context is stale by default; disk wins for user-editable test artifacts such as `test-plan.md`.

Before using, merging, validating, or overwriting a test document, ROSE must:

1. Inspect working-tree state for the change directory or artifact, such as `git status --short -- <change-dir>`.
2. Re-read the artifact from disk in the current turn.
3. Inspect `git diff -- <artifact>` when the file is tracked.
4. Treat on-disk content as the source of truth.
5. If user edits are detected, summarize them before merging or overwriting.
6. Never claim “no changes detected” unless the artifact was re-read in the current turn.
