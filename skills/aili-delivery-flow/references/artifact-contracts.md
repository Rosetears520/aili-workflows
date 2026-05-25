# Artifact Contracts

Use the skill-internal `references/protocols/` templates as the first version of delivery artifacts.

| Mode | Primary artifacts | Minimum fields |
|---|---|---|
| IDEATE | `references/protocols/idea-brief.md`, optional research evidence pack | goal, options, assumptions, unknowns, next decision |
| DEFINE | spec draft, alignment questionnaire/interview, acceptance test plan | scope, requirements, questions, test cases, approval state, BUILD readiness |
| BUILD | implementation package, subagent packet/result when delegated, compact evidence pack when evidence is noisy, local review report | target files, acceptance criteria, forbidden scope, verification command, review lanes, skipped checks, `Unverified` items |
| SHIP | review report, compact evidence pack when evidence is noisy, required repository-local Markdown closeout report | closeout document path, BUILD gate status, release-blocker audit target/status, review findings, finding classifications, repair result, fresh evidence, existing feature impact, release-readiness risks, `Unverified` items, next steps |

## Output Contract

Every mode response should include:

- selected mode and backend;
- artifacts created, updated, or required;
- gates satisfied, waived, blocked, or unverified;
- next action.

## SHIP Closeout Document

Every SHIP run must create or update a detailed, human-reviewable Markdown closeout document. The CLI response may stay concise, but it must include the document path, write/update status, verdict, blocking/important/`Unverified` summary, and approved next action.

- OpenSpec-backed SHIP writes `openspec/changes/<change-id>/ship-closeout.md`.
- Non-OpenSpec SHIP must ask for a repository-local closeout document path before the final verdict if no approved path exists.
- The document content should be written in Chinese unless the active contract explicitly requests another language.
- Do not replace the document with chat-only output; if the document cannot be written, mark the SHIP result blocked or `Unverified` and explain why.

## DEFINE Artifact Fan-Out

For OpenSpec-backed changes, DEFINE should create or update the complete change contract under `openspec/changes/<change-id>/`:

```text
proposal.md
design.md
tasks.md
specs/**/spec.md
interview.md
test-plan.md
```

- `proposal.md`, `design.md`, `tasks.md`, and `specs/**/spec.md` follow the OpenSpec backend.
- `interview.md` is generated or updated through `change-interviewer`.
- `test-plan.md` is generated or updated through `test-document-generator`.
- Non-OpenSpec artifacts require one placement decision before writing, then the selected locations become part of the active change context.

## BUILD Readiness

DEFINE output must report one of:

- `READY`: spec/questionnaire/test document gates are confirmed and implementation scope is clear.
- `BLOCKED`: a required artifact, answer, approval, or evidence item is missing.
- `WAIVED`: the user explicitly waived a gate and accepted the risk.
- `UNVERIFIED`: the gate state is known to be unverified and the user explicitly accepts proceeding with that label.
