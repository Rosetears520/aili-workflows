# Backend Routing

Backend adapters organize artifacts. They do not define permission to advance modes.

| Backend | Use when | Required handling |
|---|---|---|
| OpenSpec | A change directory, proposal, specs, design, or tasks exist | Run relevant `openspec` status/instructions/validation commands when available; create/update proposal, design, tasks, specs, `interview.md` through `requirements-grilling`, `test-plan.md` through `test-document-generator`, and formal change context at `openspec/changes/<change-id>/context.md`; in BUILD, a single ready change with pending tasks is a ready target for autonomous package queue synthesis, scoped goal context/progress marker, progress/checkpoint ledger writes at `openspec/changes/<change-id>/progress.txt`, and spec drift notes at `openspec/changes/<change-id>/implementation-notes.html`; preserve lifecycle gates. |
| Superpowers-style plan | A plan/task list drives work | Map plan items to implementation packages; require user approval before BUILD. |
| Custom files | Repository docs, issues, or bespoke task packets define scope | Cite source files and convert work into artifact contracts before BUILD. |
| Auto detection | The user did not name a backend | Prefer existing explicit artifacts; ask when multiple plausible backends conflict. |

## Rules

- IDEATE may create recommendations for a backend but does not require one.
- IDEATE may capture backend-neutral candidate ideas in a lightweight idea capsule or `ideas/workflow-inbox.md`; this does not create a formal change by default.
- DEFINE may create or update backend artifacts and must record open questions; selected IDEATE ideas are promoted here rather than during pure IDEATE.
- OpenSpec DEFINE uses deterministic artifact placement under `openspec/changes/<change-id>/`, including `proposal.md`, `design.md`, `tasks.md`, `specs/**/spec.md`, `interview.md`, `test-plan.md`, and `context.md`.
- Non-OpenSpec DEFINE asks once where to place interview and test-plan artifacts, passes those locations to `requirements-grilling` and `test-document-generator`, and records the decision in the active change context instead of asking repeatedly.
- Non-OpenSpec context/progress/implementation-notes artifacts require a repository-local placement decision or backend adapter mapping before writing; do not default them to the repository root.
- BUILD requires approved backend scope plus either an explicit implementation package or enough ready artifact evidence to synthesize an implementation package queue.
- Before DEFINE/BUILD/SHIP or normal-chat continuation, hydrate from active idea/context/progress/test/notes artifacts plus memory/checkpoints and summarize current goal, decisions, open questions, `Unverified` items, traceability gaps, progress/checkpoint state, drift notes, and next action before acting.
- OpenSpec BUILD resolves and canonicalizes the target repository root from the change directory and OpenSpec context before running git safety checks. It reads `context.md` for drift checks, any existing `progress.txt` for resume/progress context, and `implementation-notes.html` for drift or required DEFINE write-back. Do not treat the shell cwd as authoritative when the active change belongs to another repository. If the resolved root is outside the current workspace or allowed external directories, stop for explicit external-directory approval before editing or running write-capable commands.
- OpenSpec BUILD with exactly one ready change and pending tasks should synthesize packages from `tasks.md`, specs, design, and `test-plan.md`, map requirement/decision/risk sources to package/file/artifact/verification evidence, then continue package-by-package until complete or blocked by a documented stop condition.
- OpenSpec scoped BUILD goal markers use a combined transcript-visible marker and repository-local context/progress state; required fields are `goal_id`, change id or backend target, repository root, scope boundary, evaluator criteria, loop budget, stop conditions, and permission policy summary.
- Approved spec-backed BUILD records current progress, user feedback/corrections, checkpoint ledger, traceability evidence, verification/review/security state, blockers, ROSE decisions, and next action in `progress.txt`.
- Approved spec-backed BUILD maintains `implementation-notes.html` only for spec deviations/interpretation, temporary decisions, trade-offs, open questions, unverified assumptions, and required DEFINE write-back.
- Keep sidecars such as `progress.txt`, `implementation-notes.html`, and scoped state markers as AILI-managed files for the MVP. Only create or fork a custom OpenSpec schema later if these sidecars need first-class OpenSpec generation or validation.
- Only ROSE writes progress ledger entries. Workers must return compact reports and evidence references instead of editing `progress.txt`.
- SHIP checks final evidence and formal-change spec coverage regardless of backend success state; uncovered items must be reported as `Open Question` or `Unverified` before readiness claims.
