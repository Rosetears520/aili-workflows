---
description: Explore an idea through the AILI delivery flow before defining or building.
agent: rose
subtask: false
---

# /ideate

User input:
$ARGUMENTS

Invoke `aili-delivery-flow` in IDEATE mode.

Required behavior:
- Explore unclear ideas, compare options, and surface uncertainty before any change is defined or built.

Hard stops:
- Do not write production implementation; route any hard formal/material trigger through the canonical DEFINE gate.

Output contract:
- Mode, concise options/trade-offs, assumptions or `Unverified` items, and the recommended next action.
