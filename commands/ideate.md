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
- When an idea decomposes into multiple independently actionable work units, surface a concise parallelism analysis or the reason the work must stay serial.
- When unfamiliar, fast-changing, platform/runtime, packaging, security, integration, UI/product-form, or user-requested research could change the方案, route to official-doc, local-repo, or mature prior-art evidence before recommending the方案.
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
