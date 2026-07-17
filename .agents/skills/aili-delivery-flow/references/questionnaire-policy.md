# Questionnaire Policy

`requirements-grilling` is the sole requirements-refinement authority. `interview.md` is its one OpenSpec artifact. The phrase `change-interviewer` is compatibility routing only and owns no skill, prompt, artifact, state, manifest entry, or readiness authority.

## When Required

- Requirements can be implemented in incompatible ways.
- Product, safety, data, or UX decisions are missing.
- Scope boundaries or forbidden files are unclear.
- Acceptance criteria cannot be verified from existing artifacts.

## When Not Required

- The task is a small local edit with clear acceptance criteria.
- A current spec already answers the blocking questions.
- Current evidence fully resolves every material dimension.

## Gate

DEFINE writes `openspec/changes/<change-id>/interview.md` through `requirements-grilling`. Ask one decision-changing question at a time, or use a dependency-ordered packet for non-trivial DEFINE. Every question states why it matters, affected decision/artifact/test/risk, evidence-backed recommendation or explicit uncertainty, tradeoffs, short options plus custom input, and writeback target. Do not ask for facts current code/spec/test/config/official evidence already establishes.

Write accepted chat/UI/custom answers to `interview.md`, then re-read disk before classification or readiness. Ambiguous, contradictory, incomplete, untestable, out-of-scope, or evidence-conflicting answers remain `Open Question`/`Unverified` and trigger a focused follow-up rather than guessed writeback. A custom answer is evaluated against the same evidence and materiality rules as a listed option; it is never forced into the nearest option.

Classify every confirmed correction, new requirement, artifact/design/task/test change, accepted finding, or implementation feedback into exactly one exhaustive class: `covered`, `material-question`, `material-delta`, `ordinary-steering`, or `Unverified`. A `material-delta` automatically writes/re-reads affected OpenSpec artifacts, reruns status/strict validation, and stales prior final-test-plan acceptance only when acceptance or required verification changes. Never ask whether to save the delta, guess identity, expand permission, bypass high-risk approval, or start BUILD.

BUILD readiness requires complete dimension coverage, coherent strict proposal/spec/design/interview/context/tasks, no unresolved material product decision, closure of every decision-shaping local owner/architecture, official/current API/version, mature prior-art, dependency/security/platform, alternatives, and verification-strategy question, and explicit acceptance of final `test-plan.md`. Any unresolved research capable of changing scope, architecture, dependency, public contract, permissions, acceptance, or verification strategy blocks final acceptance and BUILD; waiver or accepted-`Unverified` wording cannot substitute. Named non-material runtime residuals may remain `Unverified` only under their separate fail-closed runtime/operation gates. Test-plan acceptance is the sole mandatory lifecycle user gate; material/coherence/validation/permission/destructive/high-risk gates remain separate.

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

## Complete coverage

Cover and link to writeback/test evidence: goal/success; scope/non-goals; roles/permissions; happy/failure paths; retry/rollback; boundaries; data/artifact lifecycle; state transitions; API/CLI/UI; compatibility/migration; security/privacy/secrets; reliability; observability/audit; acceptance/testability; rollout/rollback; explicit non-goals. Give each exactly one state: confirmed by evidence/user, not applicable with reason, needs question, open question, or `Unverified`.

Run `strategy-stress-test` after generating/materially revising the packet and after answer writeback. Repair missed questions, evidence-answerable questions, unsupported recommendations, contradictions, missing failure/counterexamples, untestable acceptance, required-field gaps, over-design, and unlabeled uncertainty. Stress testing is not proposal approval or a second lifecycle gate.
