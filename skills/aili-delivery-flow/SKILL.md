---
name: aili-delivery-flow
description: Run the AILI delivery lifecycle for /ideate, /define, /build, and /ship; use for idea shaping, spec/test definition, autonomous BUILD package queues, review-repair closeout, or backend routing without exposing internal stage commands.
---

# AILI Delivery Flow

This skill is the workflow authority for the IDEATE, DEFINE, BUILD, and SHIP modes. Commands route here; they do not restate the lifecycle.

## References

- Lifecycle states and hard gates: `references/lifecycle.md`
- Backend adapters: `references/backend-routing.md`
- Artifact outputs: `references/artifact-contracts.md`
- Question handling: `references/questionnaire-policy.md`
- Test document rules: `references/test-document-policy.md`
- Build package rules: `references/implementation-packages.md`
- Build goal mode: `references/build-goal-mode.md`
- Ship review and repair: `references/review-repair-loop.md`
- Protocol templates: `references/protocols/`

## Workflow

1. Select one mode from the user request or command: IDEATE, DEFINE, BUILD, or SHIP.
2. Select the backend adapter: OpenSpec, Superpowers-style plan, custom files, or conservative auto-detection.
3. Apply the mode gate before any work:
   - IDEATE explores options and uncertainty; do not edit production code.
   - DEFINE produces or updates spec, questionnaire/interview, and test document artifacts; for OpenSpec-backed changes it routes `interview.md` through `change-interviewer` and `test-plan.md` through `test-document-generator`; stop before implementation until the user confirms, explicitly waives, or explicitly accepts `Unverified` gates.
   - BUILD requires explicit approval plus either a scoped implementation package or a resolved ready target with enough evidence to synthesize a package queue, then runs automated local implementation quality gates.
   - SHIP requires full release-readiness review/repair, fresh verification evidence, and closeout before claiming ready.
4. Use the artifact contract for user-facing output and record unknowns instead of guessing.
5. Stop when a hard gate is missing, scope expands, backend evidence conflicts, or required verification cannot run.

## Boundaries

- Only four top-level commands are valid: `/ideate`, `/define`, `/build`, `/ship`.
- Research, questionnaire, test-plan, implementation, debugging, review, repair, and harness evolution are internal stages, not user command entrypoints.
- Backend-specific task systems store artifacts; they do not weaken lifecycle gates.
- Do not start BUILD from DEFINE output unless the user has confirmed the relevant spec/questionnaire/test document state, explicitly waived it, or explicitly accepted an `Unverified` gate.

## Verification

- Confirm the selected mode and backend in the response.
- Name the artifact(s) created or updated.
- For BUILD and SHIP, include fresh verification evidence or mark remaining items `Unverified`.
- For any blocked gate, return the missing approval, artifact, or evidence as the next action.
