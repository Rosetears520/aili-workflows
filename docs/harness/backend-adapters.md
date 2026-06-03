# Backend Adapters

Backend adapters store and organize work; they do not weaken lifecycle gates.

| Adapter | Used for | Must preserve |
|---|---|---|
| OpenSpec | proposal, design, specs, tasks, `interview.md`, `test-plan.md`, validation | approved scope, tasks, strict validation, `change-interviewer` interview generation, `test-document-generator` test-plan generation |
| Superpowers-style plan | task lists and implementation sequencing | explicit package boundaries and verification |
| Custom files | repo-local plans, tickets, docs | source evidence and acceptance criteria |
| Auto detection | inferring available backend from repo | conservative fallback and clarification when ambiguous |

## Rules

- IDEATE stays non-implementation even if a backend has tasks.
- DEFINE stops before build until questions/test plan/scope are accepted, explicitly waived, or explicitly accepted as `UNVERIFIED`.
- OpenSpec DEFINE uses deterministic placement under `openspec/changes/<change-id>/`; non-OpenSpec DEFINE asks once where to place interview and test-plan artifacts and records that decision in the active change context.
- BUILD follows approved packages and forbidden scope.
- SHIP runs review/repair/final evidence regardless of backend.
