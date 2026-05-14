# Artifact Contracts

Use the skill-internal `references/protocols/` templates as the first version of delivery artifacts.

| Mode | Primary artifacts | Minimum fields |
|---|---|---|
| IDEATE | `references/protocols/idea-brief.md`, optional research evidence pack | goal, options, assumptions, unknowns, next decision |
| DEFINE | spec draft, alignment questionnaire/interview, acceptance test plan | scope, requirements, questions, test cases, approval state, BUILD readiness |
| BUILD | implementation package, subagent packet/result when delegated, local review report | target files, acceptance criteria, forbidden scope, verification command, review lanes |
| SHIP | review report, closeout report | BUILD gate status, review findings, repair result, fresh evidence, release-readiness risks, next steps |

## Output Contract

Every mode response should include:

- selected mode and backend;
- artifacts created, updated, or required;
- gates satisfied, waived, blocked, or unverified;
- next action.

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
