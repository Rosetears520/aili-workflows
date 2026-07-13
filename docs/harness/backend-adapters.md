# Backend Adapters

Backend adapters store and organize work; they do not weaken lifecycle gates.

| Adapter | Used for | Must preserve |
|---|---|---|
| OpenSpec | proposal, design, specs, tasks, `interview.md`, `test-plan.md`, validation | approved scope, tasks, strict validation, `requirements-grilling` interview generation, `test-document-generator` test-plan generation |
| Superpowers-style plan | task lists and implementation sequencing | explicit package boundaries and verification |
| Custom files | repo-local plans, tickets, docs | source evidence and acceptance criteria |
| Auto detection | inferring available backend from repo | conservative fallback and clarification when ambiguous |

## Rules

- IDEATE stays non-implementation even if a backend has tasks.
- DEFINE stops before build until questions/test plan/scope are accepted, explicitly waived, or explicitly accepted as `UNVERIFIED`.
- OpenSpec DEFINE uses deterministic placement under `openspec/changes/<change-id>/`; non-OpenSpec DEFINE asks once where to place interview and test-plan artifacts and records that decision in the active change context.
- BUILD follows approved packages and forbidden scope.
- SHIP runs review/repair/final evidence regardless of backend.

## OpenSpec Direct-Adapter Boundary

AILI canonical source is the four delivery command documents plus `.agents/skills/aili-delivery-flow` and its referenced protocols. Installed copies are downstream adapters. Current generated `.opencode/commands/opsx-*` and `.opencode/skills/openspec-*` files are OpenSpec-owned direct adapters and remain unchanged.

Direct OpenSpec adapters may be callable outside AILI. AILI does not route to, recommend, wrap, suppress, prevent, or control those adapters, and direct output is not AILI acceptance, readiness, verification, completion, or Graphify-selection evidence. The four AILI routes must establish their own classifier, lifecycle gates, permissions, artifact freshness, and evidence even when OpenSpec is the selected storage backend.

Pinned files under canonical skill `references/upstream/` are upstream reference data, not backend adapters or runnable skills. External OpenSpec and OpenCode behavior remains upstream runtime behavior; generated adapter integration/control is outside this phase.
