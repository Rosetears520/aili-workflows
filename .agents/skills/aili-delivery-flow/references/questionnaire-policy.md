# Questionnaire Policy

Questionnaires prevent ambiguous work from entering BUILD.

## When Required

- Requirements can be implemented in incompatible ways.
- Product, safety, data, or UX decisions are missing.
- Scope boundaries or forbidden files are unclear.
- Acceptance criteria cannot be verified from existing artifacts.

## When Optional

- The task is a small local edit with clear acceptance criteria.
- A current spec already answers the blocking questions.
- The user explicitly waives the questionnaire gate and accepts the risk.

## Gate

DEFINE may draft questions and incorporate answers. For OpenSpec-backed changes, DEFINE writes the initial `openspec/changes/<change-id>/interview.md` packet through `requirements-grilling`, then uses chat as the default surface for unresolved blocking questions. ROSE writes accepted answers, accepted defaults, explicit waivers, or accepted `UNVERIFIED` states back into `interview.md`; direct user edits to the file remain a fallback, not the default interaction model. BUILD must stop until blocking answers are confirmed, explicitly waived, or explicitly accepted as `UNVERIFIED`.

## Default Interaction

- Initial packet generation is durable-file-first: create or update `interview.md` so later sessions and review lanes have a persistent record.
- Follow-up unresolved readiness questions are chat-first by default: ask concise blocking questions in chat, not by requiring the user to manually fill `interview.md`.
- Chat answers are not readiness evidence until ROSE writes them back into `interview.md` or the agreed questionnaire artifact.
- Direct file editing is supported when the user chooses it; after any direct edit, disk content wins after re-read and reconciliation.
- Before answer classification, readiness, BUILD gating, or local review evidence use, ROSE must re-read the artifact from disk after any AI write-back or user edit.

## Artifact Freshness Gate

Conversation context is stale by default; disk wins for user-editable questionnaire artifacts such as `interview.md`.

Before using, merging, validating, or overwriting a questionnaire artifact, ROSE must:

1. Inspect working-tree state for the change directory or artifact, such as `git status --short -- <change-dir>`.
2. Re-read the artifact from disk in the current turn.
3. Inspect `git diff -- <artifact>` when the file is tracked.
4. Treat on-disk content as the source of truth.
5. If user edits are detected, summarize them before merging or overwriting.
6. Never claim “no changes detected” unless the artifact was re-read in the current turn.
