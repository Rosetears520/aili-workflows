---
description: Build an approved scoped package through automated implementation and local quality gates.
agent: rose
subtask: false
---

# /build

User input:
$ARGUMENTS

Route to `aili-delivery-flow` in BUILD mode.

Hard stops:
- Do not edit without explicit approval and a scoped implementation package.
- Do not stop after implementation without the local BUILD gates: code review, test verification, and security review when security surfaces are present.
- Stay inside the package; report scope expansion or missing verification instead of guessing.
