# Artifact Contracts

Use the skill-internal `references/protocols/` templates as the first version of delivery artifacts.

| Mode | Primary artifacts | Minimum fields |
|---|---|---|
| IDEATE | `references/protocols/idea-brief.md`, optional research evidence pack | goal, options, assumptions, unknowns, next decision |
| DEFINE | spec draft, alignment questionnaire, acceptance test plan | scope, requirements, questions, test cases, approval state |
| BUILD | implementation package, subagent packet/result when delegated, local review report | target files, acceptance criteria, forbidden scope, verification command, review lanes |
| SHIP | review report, closeout report | BUILD gate status, review findings, repair result, fresh evidence, release-readiness risks, next steps |

## Output Contract

Every mode response should include:

- selected mode and backend;
- artifacts created, updated, or required;
- gates satisfied, waived, blocked, or unverified;
- next action.
