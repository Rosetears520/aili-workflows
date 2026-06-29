# Command Lifecycle

Only four top-level delivery commands are planned for this harness.

| Command | Mode | Contract |
|---|---|---|
| `/ideate` | IDEATE | Explore, compare, and surface uncertainty. Expose parallelism or no-parallel reasoning for multi-unit ideas and use research evidence when it can change the方案. No production edits. |
| `/define` | DEFINE | Produce aligned spec/questionnaire/test artifacts. For OpenSpec, route `interview.md` through `change-interviewer` and `test-plan.md` through `test-document-generator`. Confirm evidence-backed方案 state before BUILD readiness. Stop before implementation. |
| `/build` | BUILD | Execute approved ready work in goal mode: use an explicit package or synthesize a package queue from ready artifacts with parallelism analysis, then run local code-review, test, security, and requested packaging gates. |
| `/ship` | SHIP | Reuse or refresh BUILD gates, run release-blocker audit for the selected change/final diff or explicitly requested baseline/repository scope, reconcile multi-lane review/repair with join evidence, then complete release-readiness review, repair, verification, archive/sync/closeout as approved. |

## Non-Commands

Research, questionnaire, test-plan, implementation, fix, debug, review, release-blocker audit, repair loop, and harness evolution are internal stages. They are not top-level commands unless a later approved change adds them.

## Command Shape

Each public command remains a thin entrypoint but should name:

- mode purpose;
- required behavior;
- hard stops;
- output contract.
- any command-visible proactive planning, research-first, or packaging gate that would otherwise be hidden inside skill references.

Detailed lifecycle authority remains in `.agents/skills/aili-delivery-flow` source references in this repository; installed OpenCode homes receive those skills under `skills/aili-delivery-flow`.

The command prompts should stay thin: name the gates and expected evidence shape, but do not copy the full workflow from lifecycle skills or protocols.
