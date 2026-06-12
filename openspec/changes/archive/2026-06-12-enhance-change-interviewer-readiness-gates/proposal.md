## Why

`change-interviewer` currently produces useful evidence-grounded interview packets, but the protocol can still allow shallow, one-round, or weakly actionable questions. The user reported that interview documents are too one-sided, ask too few or unimportant questions, and sometimes leave ambiguous filled answers that later force manual repair before implementation.

This is a harness/skill behavior defect: DEFINE should prevent unclear requirements from reaching BUILD, especially for skill/process changes where ambiguous scope can cause broad prompt drift.

## What Changes

- Upgrade `change-interviewer` from a single-pass packet generator into a comprehensive, multi-round change interview protocol.
- Require questions to be coverage-driven and decision-changing: each useful question must affect scope, design, tasks, acceptance criteria, tests, risk, or implementation safety.
- Require each interview question to include why it is asked, its impact, a recommended default answer, consequences/trade-offs, the answer slot, and write-back target.
- Add answer-quality ingestion rules: after the user fills an interview, ambiguous, contradictory, incomplete, untestable, or evidence-conflicting answers block write-back and BUILD until clarified, waived, or explicitly accepted as `UNVERIFIED`.
- Add an explicit multi-round loop: first-round comprehensive matrix, then follow-up rounds for remaining ambiguity and contradictions; user completion of a form alone is not enough to start BUILD.
- Strengthen evidence-first behavior: if code, docs, specs, configs, tests, or official docs can answer a point, the interviewer must gather evidence instead of asking the user.
- Make `strategy-stress-test` a mandatory quality gate for both generated interview packets and ingested answer sets.

## Capabilities

### New Capabilities

- `change-interviewer`: Multi-round comprehensive interview and answer-clarification gate.

### Modified Capabilities

- `aili-four-command-lifecycle`: DEFINE/BUILD readiness relies on confirmed questionnaire/interview state; ambiguous answer sets must remain blocking unless explicitly waived or accepted as `UNVERIFIED`.

### Constraints Referenced

- `skill-routing-boundaries`: Any implementation must avoid adding public lifecycle commands or splitting `change-interviewer` into new reference files without approval. This change does not currently propose a spec delta for that capability.

## Confirmed Decisions

- BUILD may add `skills/change-interviewer/references/*` files if that is the smallest clear way to keep the overhaul maintainable; any referenced file must exist and remain task-scoped.
- Add requirements-interview / write-back oriented grill triggers for `change-interviewer`; pure plan/design/spec/review/completion-claim stress-testing remains owned by `strategy-stress-test`.
- The current spec, interview, and test-plan gates are confirmed for BUILD readiness.

## Impact

- Likely affected files during BUILD: `skills/change-interviewer/SKILL.md`; possibly `skills/change-interviewer/references/*` if needed for maintainability, `skills/strategy-stress-test/SKILL.md`, `skills/aili-delivery-flow/references/questionnaire-policy.md`, README skill description, and targeted fixtures/docs if they assert interview behavior.
- No production app behavior, dependency, lockfile, OpenCode config, memory schema, installer behavior, or public top-level command changes are proposed.
- Verification should include OpenSpec strict validation, skill routing/fixture checks if touched, AGENTS/template checks only if those files are touched, and static inspection that no new skill-local references are added without approval.

## Non-Goals

- Do not create a separate public `/grill`, `/interview`, `/questionnaire`, or other top-level command.
- Do not copy upstream `grill-me` or `grill-with-docs` text; only adapt the general ideas of multi-round questioning, recommended answers, and evidence-before-asking.
- Do not implement the change during DEFINE.
- Do not weaken BUILD gates to proceed from vague or contradictory interview answers.
