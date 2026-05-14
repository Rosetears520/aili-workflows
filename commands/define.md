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
- Select backend: OpenSpec, Superpowers-style plan, custom files, or conservative auto-detection.
- For OpenSpec-backed changes, create or update:
  - `openspec/changes/<change-id>/proposal.md`;
  - `openspec/changes/<change-id>/design.md`;
  - `openspec/changes/<change-id>/tasks.md`;
  - `openspec/changes/<change-id>/specs/**/spec.md`;
  - `openspec/changes/<change-id>/interview.md` through `change-interviewer`;
  - `openspec/changes/<change-id>/test-plan.md` through `test-document-generator`.
- For non-OpenSpec backends, ask once where to place interview and test-plan artifacts, then record that decision in the active change context.
- Before using or overwriting existing user-editable artifacts, apply the Artifact Freshness Gate: inspect working-tree state, re-read from disk, inspect diffs when available, and treat disk as source of truth.
- Report BUILD readiness as `READY`, `BLOCKED`, `WAIVED`, or `UNVERIFIED`.

Hard stops:
- Do not implement.
- Stop until spec, questionnaire/interview, and test document gates are confirmed, explicitly waived, or explicitly marked `UNVERIFIED` by the user.

Output contract:
- selected mode and backend;
- artifacts created, updated, required, or blocked;
- unresolved questions and test-plan coverage summary;
- gate state and BUILD readiness: `READY` / `BLOCKED` / `WAIVED` / `UNVERIFIED`.
