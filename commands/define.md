---
description: Define an implementation-ready change contract with spec, interview, and test-plan artifacts.
agent: rose
subtask: false
---

# /define

User input:
$ARGUMENTS

Invoke `aili-delivery-flow` in DEFINE mode.

Purpose:
- Produce or align the complete implementation-readiness contract before BUILD.

Required behavior:
- Apply the same semantic ordinary/formal/material classifier used for natural language and commands, and record the decisive evidence. Formal Stage-I work uses OpenSpec; existing non-OpenSpec material is input evidence, not a competing formal authority.
- Treat `/define` and equivalent explicit natural-language definition/specification intent identically; the shortcut grants no extra persistence, permission, or readiness authority.
- Resolve one change by accepted scope: reuse the same-scope active change, create a distinct change only when distinct scope is established, or ask exactly one focused identity question and write nothing when multiple changes remain plausible or the answer is evasive.
- Before freezing a multi-unit plan, expose proactive parallelism analysis: shared scaffold/source-of-truth work, safe lanes, serial dependencies, ownership boundaries, join point, blockers, or a no-parallel reason.
- Gather applicable local-repository, official/current, and mature prior-art evidence before freezing the implementation方案, separate source classes and `Unverified` gaps, then stress-test the plan. This is mandatory evidence work, not a proposal approval/waiver gate.
- For OpenSpec-backed changes, create or update:
  - `openspec/changes/<change-id>/proposal.md`;
  - `openspec/changes/<change-id>/design.md`;
  - `openspec/changes/<change-id>/tasks.md`;
  - `openspec/changes/<change-id>/specs/**/spec.md`;
  - `openspec/changes/<change-id>/interview.md` through `requirements-grilling`;
  - `openspec/changes/<change-id>/test-plan.md` through `test-document-generator`.
  - `openspec/changes/<change-id>/context.md`.
- Follow current `openspec instructions proposal|specs|design|tasks --change <id> --json` dependencies/unlocks, run `openspec status --change <id> --json`, write/re-read every applicable artifact, and run `openspec validate <id> --strict`. File presence alone is not readiness.
- Write applicable artifacts automatically without “should I save this?” or per-artifact prompts. A current explicit no-write/chat-only instruction overrides persistence and returns only a `BLOCKED_FOR_CLARIFICATION`/`UNVERIFIED` preview until later explicit write permission.
- Route all requirement questions, including the phrase `change-interviewer`, solely to `requirements-grilling` and the one `interview.md` artifact.
- Before using or overwriting existing user-editable artifacts, apply the Artifact Freshness Gate: inspect working-tree state, re-read from disk, inspect diffs when available, and treat disk as source of truth.
- Report BUILD readiness as `READY`, `BLOCKED`, or `UNVERIFIED`. A named question may be recorded `WAIVED`, but that disposition is not BUILD readiness and cannot waive final test-plan acceptance. `READY` requires coherent strictly validated artifacts, no unresolved material product decision, and explicit acceptance of the final `test-plan.md`.

Hard stops:
- Do not implement.
- Stop until material decisions and coherence/validation are resolved and the final `test-plan.md` is explicitly accepted. No proposal, per-artifact, bundled-package, digest, receipt, or second lifecycle approval is allowed.

Output contract:
- selected mode and backend;
- artifacts created, updated, required, or blocked;
- unresolved questions, evidence-backed方案 status, and test-plan coverage summary;
- gate state and BUILD readiness: `READY` / `BLOCKED` / `UNVERIFIED`, with lifecycle acceptance separated from operation-specific permission/risk gates.
