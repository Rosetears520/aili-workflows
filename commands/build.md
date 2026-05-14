---
description: Build an approved scoped package through automated implementation and local quality gates.
agent: rose
subtask: false
---

# /build

User input:
$ARGUMENTS

Invoke `aili-delivery-flow` in BUILD mode.

Purpose:
- Execute an approved, scoped implementation package and prove it with local quality gates.

Required behavior:
- Confirm explicit user approval and the scoped implementation package before editing.
- Confirm target files, forbidden scope, acceptance criteria, verification command, and review lanes.
- Re-read relevant DEFINE artifacts from disk before trusting their state.
- Implement only the approved package and update task state as work completes.
- Run local BUILD gates: code review, test verification, and security review when security surfaces are present.

Hard stops:
- Do not edit without explicit approval and a scoped implementation package.
- Do not stop after implementation without the local BUILD gates: code review, test verification, and security review when security surfaces are present.
- Stay inside the package; report scope expansion or missing verification instead of guessing.

Output contract:
- selected mode and backend;
- implementation package and files changed;
- verification, review, and skipped-lane evidence;
- residual risks, scope expansions, and `Unverified` items;
- whether the change is ready for `/ship`.
