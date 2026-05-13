# Backend Routing

Backend adapters organize artifacts. They do not define permission to advance modes.

| Backend | Use when | Required handling |
|---|---|---|
| OpenSpec | A change directory, proposal, specs, design, or tasks exist | Run relevant `openspec` status/instructions/validation commands when available; preserve lifecycle gates. |
| Superpowers-style plan | A plan/task list drives work | Map plan items to implementation packages; require user approval before BUILD. |
| Custom files | Repository docs, issues, or bespoke task packets define scope | Cite source files and convert work into artifact contracts before BUILD. |
| Auto detection | The user did not name a backend | Prefer existing explicit artifacts; ask when multiple plausible backends conflict. |

## Rules

- IDEATE may create recommendations for a backend but does not require one.
- DEFINE may create or update backend artifacts and must record open questions.
- BUILD requires approved backend scope plus an implementation package.
- SHIP checks final evidence regardless of backend success state.
