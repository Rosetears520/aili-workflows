# Backend Routing

Backend adapters organize artifacts. They do not define permission to advance modes.

| Backend | Use when | Required handling |
|---|---|---|
| OpenSpec | A change directory, proposal, specs, design, or tasks exist | Run relevant `openspec` status/instructions/validation commands when available; create/update proposal, design, tasks, specs, `interview.md` through `change-interviewer`, and `test-plan.md` through `test-document-generator`; preserve lifecycle gates. |
| Superpowers-style plan | A plan/task list drives work | Map plan items to implementation packages; require user approval before BUILD. |
| Custom files | Repository docs, issues, or bespoke task packets define scope | Cite source files and convert work into artifact contracts before BUILD. |
| Auto detection | The user did not name a backend | Prefer existing explicit artifacts; ask when multiple plausible backends conflict. |

## Rules

- IDEATE may create recommendations for a backend but does not require one.
- DEFINE may create or update backend artifacts and must record open questions.
- OpenSpec DEFINE uses deterministic artifact placement under `openspec/changes/<change-id>/`, including `proposal.md`, `design.md`, `tasks.md`, `specs/**/spec.md`, `interview.md`, and `test-plan.md`.
- Non-OpenSpec DEFINE asks once where to place interview and test-plan artifacts, passes those locations to `change-interviewer` and `test-document-generator`, and records the decision in the active change context instead of asking repeatedly.
- BUILD requires approved backend scope plus an implementation package.
- SHIP checks final evidence regardless of backend success state.
