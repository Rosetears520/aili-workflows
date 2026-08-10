# Backend Adapters

Backend adapters store and organize work; they do not weaken lifecycle gates.
Shared Skill capability ownership, status, and missing-capability behavior live
in `manifests/skill-capabilities.json` and
`docs/harness/skill-capability-contract.md`. This document does not itself
grant a runtime capability or operation permission.

| Adapter | Used for | Must preserve |
|---|---|---|
| OpenSpec | proposal, design, specs, tasks, `interview.md`, `test-plan.md`, change-local `formal-task-board.md`, validation | approved scope in `tasks.md`, one `aili-task-board/v1` current-state projection across formal phases, strict validation, `requirements-grilling` interview generation, `test-document-generator` test-plan generation |
| Pi profile | generated top-level prompts under `generated/pi/prompts/` | Core Skill selection, non-recursive prompt installation, and package-only Pi system/role/selection/protocol artifacts; it does not implement or prove Pi runtime/session behavior |
| Custom files | repo-local plans, tickets, docs, adapter-mapped formal Board | source evidence, acceptance criteria, and one repository-local Board path when formal packages exist |
| Auto detection | inferring available backend from repo | conservative fallback and clarification when ambiguous |

## Rules

- IDEATE stays non-implementation even if a backend has tasks.
- Formal DEFINE stops before BUILD until applicable material questions are resolved, required artifacts are coherent/validated, and the final `test-plan.md` is explicitly accepted. `Unverified` does not substitute for a material decision.
- OpenSpec DEFINE uses deterministic placement under `openspec/changes/<change-id>/`; non-OpenSpec DEFINE asks once where to place interview and test-plan artifacts and records that decision in the active change context.
- After stable formal identity and package decomposition, OpenSpec persists one Board at `openspec/changes/<change-id>/formal-task-board.md`. A non-OpenSpec adapter uses an existing repository-local Board mapping or one explicit repository-local placement decision. Runtime-private selector/session mappings remain adapter-owned and cannot be the Board's only completion evidence.
- BUILD follows approved packages and forbidden scope.
- SHIP uses the same proactive trigger scan and affected-claim verification owner regardless of backend; an eligible review/repair gap dispatches promptly, and direct inspection is the no-trigger/blocked fallback.

## OpenSpec Direct-Adapter Boundary

AILI canonical command source is `core/commands/` for four Delivery Commands and six Utility Commands. Versioned package/selection/Board schemas live in `core/protocols/`; lifecycle prose remains with `.agents/skills/aili-delivery-flow` and its references. Root `commands/` are downstream generated compatibility projections. Current generated `.opencode/commands/opsx-*` and `.opencode/skills/openspec-*` files are OpenSpec-owned direct adapters and remain unchanged.

Direct OpenSpec adapters may be callable outside AILI. AILI does not route to, recommend, wrap, suppress, prevent, or control those adapters, and direct output is not AILI acceptance, readiness, verification, completion, or Graphify-selection evidence. The four AILI routes must establish their own classifier, lifecycle gates, permissions, artifact freshness, and evidence even when OpenSpec is the selected storage backend.

Pinned files under canonical skill `references/upstream/` are upstream reference data, not backend adapters or runnable skills. External OpenSpec and OpenCode behavior remains upstream runtime behavior; generated adapter integration/control is outside this phase.

`--profile pi` installs only the generated prompt projection at the supported global Pi prompt path. `generated/pi/system.md`, role metadata, selection map, and schemas are package artifacts for the separately owned Pi runtime; they are not installed or runtime-equivalence evidence.
