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
- BUILD may start only when test expectations are accepted, explicitly waived, or explicitly accepted as `UNVERIFIED`.
- SHIP must use fresh evidence, compare the traceability matrix against implementation/review/security evidence, and identify any `Open Question` or `Unverified` items before readiness claims.

## Artifact Freshness Gate

Conversation context is stale by default; disk wins for user-editable test artifacts such as `test-plan.md`.

Before using, merging, validating, or overwriting a test document, ROSE must:

1. Inspect working-tree state for the change directory or artifact, such as `git status --short -- <change-dir>`.
2. Re-read the artifact from disk in the current turn.
3. Inspect `git diff -- <artifact>` when the file is tracked.
4. Treat on-disk content as the source of truth.
5. If user edits are detected, summarize them before merging or overwriting.
6. Never claim “no changes detected” unless the artifact was re-read in the current turn.
