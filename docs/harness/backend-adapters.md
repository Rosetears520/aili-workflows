# Backend Adapters

Backend adapters store and organize work; they do not weaken lifecycle gates.
Shared Skill capability ownership, status, and missing-capability behavior live
in `manifests/skill-capabilities.json` and
`docs/harness/skill-capability-contract.md`. This document does not itself
grant a runtime capability or operation permission.

| Adapter | Used for | Must preserve |
|---|---|---|
| OpenSpec | proposal, design, specs, tasks, `interview.md`, `test-plan.md`, free-form `progress.txt`, optional `formal-task-board.md` notes | approved scope in `tasks.md`; `requirements-grilling` interview generation; `test-document-generator` test-plan generation; one targeted strict validation only when `proposal.md`, `design.md`, `tasks.md`, or `specs/**/spec.md` changed, or an explicit acceptance/archive gate requires it |
| Pi profile | generated global context and top-level prompts under `generated/pi/` | Core Skill selection, non-recursive prompt installation, and package-only Pi system/role/selection/protocol artifacts; it does not implement or prove Pi runtime/session behavior |
| Pi persistent Agent runtime | a self-contained canonical package handed to one official Pi Agent identity | the authority split, persistence/follow-up limits, effective capability intersection, bounded result object, and failure behavior in `docs/harness/aili-pi-runtime-handoff.md` |
| Custom files | repo-local plans, tickets, docs, and continuity text | source evidence and acceptance criteria; no required Markdown Board or progress grammar |
| Auto detection | inferring available backend from repo | conservative fallback and clarification when ambiguous |

## Rules

- IDEATE stays non-implementation even if a backend has tasks.
- Formal DEFINE stops before BUILD until applicable material questions are resolved, required artifacts are coherent/validated, and the final `test-plan.md` is explicitly accepted. `Unverified` does not substitute for a material decision.
- OpenSpec DEFINE uses deterministic placement under `openspec/changes/<change-id>/`; non-OpenSpec DEFINE asks once where to place interview and test-plan artifacts and records that decision in the active change context.
- For multi-step or formal work, ROSE creates `progress.txt` once when absent and appends concise free-form status, evidence, blockers, and next action. Workers do not write it. Its content is never parsed or format-validated.
- `formal-task-board.md` is optional arbitrary human-readable notes. Missing or arbitrary notes never block; no adapter parses or replays them as authority.
- Agent/job/turn/join/settlement state belongs to the runtime Journal. Code-only or sidecar-only work does not invoke OpenSpec validation.
- BUILD follows approved packages and forbidden scope.
- SHIP uses the same proactive trigger scan and affected-claim verification owner regardless of backend; an eligible review/repair gap dispatches promptly, and direct inspection is the no-trigger/blocked fallback.

## OpenSpec Direct-Adapter Boundary

AILI canonical command source is `core/commands/` for four Delivery Commands and six Utility Commands. Versioned package and Agent-selection schemas live in `core/protocols/`; lifecycle prose remains with `.agents/skills/aili-delivery-flow` and its references. Root `commands/` are downstream generated compatibility projections. Current generated `.opencode/commands/opsx-*` and `.opencode/skills/openspec-*` files are OpenSpec-owned direct adapters and remain unchanged.

Direct OpenSpec adapters may be callable outside AILI. AILI does not route to, recommend, wrap, suppress, prevent, or control those adapters, and direct output is not AILI acceptance, readiness, verification, completion, or Graphify-selection evidence. The four AILI routes must establish their own classifier, lifecycle gates, permissions, artifact freshness, and evidence even when OpenSpec is the selected storage backend.

Pinned files under canonical skill `references/upstream/` are upstream reference data, not backend adapters or runnable skills. External OpenSpec and OpenCode behavior remains upstream runtime behavior; generated adapter integration/control is outside this phase.

`--profile pi` installs only the generated global context and prompt projection at the supported global Pi paths. Git checkouts use managed links and packaged sources use copies. Install/update preserves a conflicting non-managed global-context regular file, valid symlink, or broken symlink in a timestamped backup before replacement; repeat runs are idempotent and dry-run is non-mutating. Pi-profile doctor reports generated and installed context, prompts, and package-only metadata without repair. Restart Pi or open a new session after install/update to reload context and prompts. `generated/pi/system.md`, role metadata, selection map, installation contract, and schemas are package artifacts for the separately owned Pi runtime; they are not installed or runtime-equivalence evidence. The normative handoff from an AILI package to the official Pi persistent Agent runtime is documented in `docs/harness/aili-pi-runtime-handoff.md`; runtime identity and persistence remain adapter-owned and never replace accepted contracts or repository evidence.
