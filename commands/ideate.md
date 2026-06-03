---
description: Explore an idea through the AILI delivery flow before defining or building.
agent: rose
subtask: false
---

# /ideate

User input:
$ARGUMENTS

Invoke `aili-delivery-flow` in IDEATE mode.

Purpose:
- Explore unclear ideas, compare options, and surface uncertainty before any change is defined or built.

Required behavior:
- Identify the likely backend only when useful: OpenSpec, Superpowers-style plan, custom files, or conservative auto-detection.
- Gather enough evidence to name options, assumptions, unknowns, and risks.
- When repository evidence is broad or noisy, use read-only scouting instead of guessing.
- Recommend the next decision: continue ideation, enter `/define`, or stop.

Hard stops:
- Do not write production implementation.
- Stop with options, assumptions, unknowns, and the next decision.

Output contract:
- selected mode and likely backend, if any;
- option list with trade-offs;
- assumptions and unknowns;
- recommended next action.
