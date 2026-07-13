# Backend Routing

Backend adapters organize artifacts. They do not define permission to advance modes.

| Backend | Use when | Required handling |
|---|---|---|
| OpenSpec | Any Stage-I formal/material work, or an existing change directory/proposal/spec/design/tasks | Resolve one change by accepted scope; run/read current `openspec instructions proposal\|specs\|design\|tasks --change <id> --json`, honor dependencies/unlocks, write/re-read applicable native artifacts in dependency order plus `interview.md` through `requirements-grilling`, `test-plan.md` through `test-document-generator`, and `context.md`; run `openspec status --change <id> --json` and strict validation; preserve lifecycle and separate operation gates. |
| Superpowers-style plan | A plan/task list drives work | Map plan items to implementation packages; require user approval before BUILD. |
| Custom files | Repository docs, issues, or bespoke task packets define scope | Cite source files and convert work into artifact contracts before BUILD. |
| Auto detection | The user did not name a backend | Prefer existing explicit artifacts; ask when multiple plausible backends conflict. |

## Rules

- IDEATE may create recommendations for a backend but does not require one.
- IDEATE may capture backend-neutral candidate ideas in a lightweight idea capsule or `ideas/workflow-inbox.md`; this does not create a formal change by default.
- DEFINE may create or update backend artifacts and must record open questions; selected IDEATE ideas are promoted here rather than during pure IDEATE.
- OpenSpec DEFINE uses deterministic artifact placement under `openspec/changes/<change-id>/`, including `proposal.md`, `design.md`, `tasks.md`, `specs/**/spec.md`, `interview.md`, `test-plan.md`, and `context.md`.
- Formal Stage-I activation creates or reuses one OpenSpec change exactly once. Same accepted scope reuses; distinct established scope may create; multiple plausible changes or evasive identity answers trigger one focused question and zero writes. Never guess identity or ask whether to write each artifact.
- File presence is not readiness. Re-read written artifacts, rerun status/instructions when dependencies change, and require strict validation plus coherent material decisions and explicit final test-plan acceptance before BUILD.
- Non-OpenSpec DEFINE asks once where to place interview and test-plan artifacts, passes those locations to `requirements-grilling` and `test-document-generator`, and records the decision in the active change context instead of asking repeatedly.
- Non-OpenSpec context/progress/drift-log artifacts require a repository-local placement decision or backend adapter mapping before writing; do not default them to the repository root.
- BUILD requires approved backend scope plus either an explicit implementation package or enough ready artifact evidence to synthesize an implementation package queue.
- Before DEFINE/BUILD/SHIP or normal-chat continuation, resolve one active change; hydrate from its OpenSpec contract, accepted test plan, context, progress, bounded drift, scoped legacy/pre-runtime memory, and fresh scope-relevant review/verification evidence; then revalidate canonical root/worktree/Git identity and permissions. Idea/inbox, handoff, memory, old logs, stale chat, task checkboxes, and DCP/compression state are not authority.
- OpenSpec BUILD resolves and canonicalizes the target repository root from the change directory and OpenSpec context before running git safety checks. It reads `context.md` for drift checks, any existing `progress.txt` for resume/progress context, `drift-log.md` for drift or required DEFINE write-back, and legacy `implementation-notes.html` as read-only migration evidence when present. Do not treat the shell cwd as authoritative when the active change belongs to another repository. If the resolved root is outside the current workspace or allowed external directories, stop for explicit external-directory approval before editing or running write-capable commands.
- Cross-root backend resolution must create/reference one `WT-001` context at `protocols/worktree-context.md`. Backend artifacts carry only its reference and cannot duplicate/rebind root, Git, approval, dirty-state, path, command/cwd, or containment facts. A30 is ROSE Task-dispatched read-only access for the exact selected roles; direct `@`, edits, commands, tests, debug, browser/E2E work, and nesting are excluded. The current-version probe must exit `0` with final merged child-rule provenance and proven override absence; otherwise remain `Unverified` and fail closed.
- OpenSpec BUILD with exactly one ready change and pending tasks synthesizes a neutral package queue from `tasks.md`, specs, design, and `test-plan.md`, maps requirement/decision/risk sources to package/file/artifact/verification evidence, completes Package 1–11 with lightweight savepoints, then enters Package 12's single mandatory comprehensive gate.
- Continuation references exactly one active canonical `CONT-005` envelope through current context/progress state. It preserves target, phase, accepted authorization, current gates, consumed budgets, accounting/overshoot state, and stop reason; it creates no second session identity or marker contract.
- Approved spec-backed BUILD records current progress, user feedback/corrections, checkpoint ledger, traceability evidence, verification/review/security state, blockers, ROSE decisions, and next action in `progress.txt`.
- Approved spec-backed BUILD maintains `drift-log.md` only for spec deviations, model drift/self-corrections, temporary decisions, trade-offs, open questions, unverified assumptions, and required DEFINE write-back; append to legacy `implementation-notes.html` only when the active contract explicitly requires legacy HTML.
- Keep sidecars such as `progress.txt`, `drift-log.md`, legacy `implementation-notes.html`, and scoped state markers as AILI-managed files for the MVP. Only create or fork a custom OpenSpec schema later if these sidecars need first-class OpenSpec generation or validation.
- Only ROSE writes progress ledger entries. Workers must return compact reports and evidence references instead of editing `progress.txt`.
- SHIP checks final evidence and formal-change spec coverage regardless of backend success state; uncovered items must be reported as `Open Question` or `Unverified` before readiness claims.

## Generated/direct OpenSpec surfaces

Classify OpenSpec-facing surfaces before edits as canonical AILI source, generated/installed adapter, or upstream runtime/tool. Current `.opencode/commands/opsx-*` and `.opencode/skills/openspec-*` are unchanged direct routes outside AILI guarantees. Do not route or recommend users to them, hand-edit/wrap/suppress/prevent them, alter a generator to control them, or treat their output as AILI evidence. AILI-owned generated output changes only through an explicitly in-scope canonical source/generator. Upstream runtime changes are out of scope.
