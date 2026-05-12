# Backend Adapters

Backend adapters store and organize work; they do not weaken lifecycle gates.

| Adapter | Used for | Must preserve |
|---|---|---|
| OpenSpec | proposal, design, specs, tasks, validation | approved scope, tasks, strict validation |
| Superpowers-style plan | task lists and implementation sequencing | explicit package boundaries and verification |
| Custom files | repo-local plans, tickets, docs | source evidence and acceptance criteria |
| Auto detection | inferring available backend from repo | conservative fallback and clarification when ambiguous |

## Rules

- IDEATE stays non-implementation even if a backend has tasks.
- DEFINE stops before build until questions/test plan/scope are accepted or explicitly waived.
- BUILD follows approved packages and forbidden scope.
- SHIP runs review/repair/final evidence regardless of backend.
