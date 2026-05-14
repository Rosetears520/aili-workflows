# Command Lifecycle

Only four top-level delivery commands are planned for this harness.

| Command | Mode | Contract |
|---|---|---|
| `/ideate` | IDEATE | Explore, compare, and surface uncertainty. No production edits. |
| `/define` | DEFINE | Produce aligned spec/questionnaire/test artifacts. For OpenSpec, route `interview.md` through `change-interviewer` and `test-plan.md` through `test-document-generator`. Stop before implementation. |
| `/build` | BUILD | Execute approved implementation packages with local code-review, test, and security gates. |
| `/ship` | SHIP | Reuse or refresh BUILD gates, then complete release-readiness review, repair, verification, archive/sync/closeout as approved. |

## Non-Commands

Research, questionnaire, test-plan, implementation, fix, debug, review, repair loop, and harness evolution are internal stages. They are not top-level commands unless a later approved change adds them.

## Command Shape

Each public command remains a thin entrypoint but should name:

- mode purpose;
- required behavior;
- hard stops;
- output contract.

Detailed lifecycle authority remains in `skills/aili-delivery-flow` references.
