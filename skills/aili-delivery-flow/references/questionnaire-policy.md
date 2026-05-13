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

DEFINE may draft questions and incorporate answers. BUILD must stop until blocking answers are confirmed or explicitly waived.
