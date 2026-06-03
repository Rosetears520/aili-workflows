# Backend Routing

Backend adapters organize artifacts. They do not define permission to advance modes.

| Backend | Use when | Required handling |
|---|---|---|
| OpenSpec | A change directory, proposal, specs, design, or tasks exist | Run relevant `openspec` status/instructions/validation commands when available; create/update proposal, design, tasks, specs, `interview.md` through `change-interviewer`, `test-plan.md` through `test-document-generator`, and formal change context at `openspec/changes/<change-id>/context.md`; in BUILD, a single ready change with pending tasks is a ready target for autonomous package queue synthesis and progress ledger writes at `openspec/changes/<change-id>/progress.txt`; preserve lifecycle gates. |
| Superpowers-style plan | A plan/task list drives work | Map plan items to implementation packages; require user approval before BUILD. |
| Custom files | Repository docs, issues, or bespoke task packets define scope | Cite source files and convert work into artifact contracts before BUILD. |
| Auto detection | The user did not name a backend | Prefer existing explicit artifacts; ask when multiple plausible backends conflict. |

## Rules

- IDEATE may create recommendations for a backend but does not require one.
- IDEATE may capture backend-neutral candidate ideas in `ideas/workflow-inbox.md`; this does not create a formal change by default.
- DEFINE may create or update backend artifacts and must record open questions.
- OpenSpec DEFINE uses deterministic artifact placement under `openspec/changes/<change-id>/`, including `proposal.md`, `design.md`, `tasks.md`, `specs/**/spec.md`, `interview.md`, `test-plan.md`, and `context.md`.
- Non-OpenSpec DEFINE asks once where to place interview and test-plan artifacts, passes those locations to `change-interviewer` and `test-document-generator`, and records the decision in the active change context instead of asking repeatedly.
- Non-OpenSpec context/progress artifacts require a repository-local placement decision or backend adapter mapping before writing; do not default them to the repository root.
- BUILD requires approved backend scope plus either an explicit implementation package or enough ready artifact evidence to synthesize an implementation package queue.
- OpenSpec BUILD resolves and canonicalizes the target repository root from the change directory and OpenSpec context before running git safety checks. It reads `context.md` for drift checks and any existing `progress.txt` for resume/progress context. Do not treat the shell cwd as authoritative when the active change belongs to another repository. If the resolved root is outside the current workspace or allowed external directories, stop for explicit external-directory approval before editing or running write-capable commands.
- OpenSpec BUILD with exactly one ready change and pending tasks should synthesize packages from `tasks.md`, specs, design, and `test-plan.md`, then continue package-by-package until complete or blocked by a documented stop condition.
- Only ROSE writes progress ledger entries. Workers must return compact reports and evidence references instead of editing `progress.txt`.
- SHIP checks final evidence regardless of backend success state.
