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

### Compact Mode Decision Table

| User intent | Mode | Required gate before continuing | Must not do |
|---|---|---|---|
| Explore/refine an idea | IDEATE | none beyond evidence discipline | edit production code or create BUILD packages |
| Define requirements, specs, tests, or interviews | DEFINE | stop before implementation unless the user confirms, waives, or accepts `Unverified` gates | implement, review-repair, or claim BUILD readiness |
| Implement approved work | BUILD | explicit approval plus scoped package queue or ready target evidence | weaken DEFINE artifacts or skip local quality gates |
| Review/repair/close out implemented work | SHIP | implementation evidence plus review/repair readiness and spec coverage check for formal changes | claim ready without fresh verification, coverage check, and closeout |

### 🔴 Red Gates

Stop immediately and report the missing next action when:

- the requested mode is not one of IDEATE, DEFINE, BUILD, or SHIP;
- DEFINE output lacks required spec/interview/test-document confirmation for BUILD;
- BUILD lacks explicit approval, package scope, or resolvable ready-target evidence;
- SHIP lacks fresh implementation, review, repair, verification evidence, or formal-change spec coverage evidence;
- backend artifacts conflict with lifecycle state or make readiness ambiguous.

1. Select one mode from the user request or command: IDEATE, DEFINE, BUILD, or SHIP.
2. Select the backend adapter: OpenSpec, Superpowers-style plan, custom files, or conservative auto-detection.
3. Apply the mode gate before any work:
   - IDEATE explores options and uncertainty; do not edit production code.
   - DEFINE produces or updates spec, questionnaire/interview, and test document artifacts; for OpenSpec-backed changes it routes `interview.md` through `requirements-grilling` and `test-plan.md` through `test-document-generator`; stop before implementation until the user confirms, explicitly waives, or explicitly accepts `Unverified` gates.
   - BUILD requires explicit approval plus either a scoped implementation package or a resolved ready target with enough evidence to synthesize a package queue, then runs automated local implementation quality gates.
   - SHIP requires full release-readiness review/repair, fresh verification evidence, a spec coverage check for formal changes, and closeout before claiming ready.
4. Use the artifact contract for user-facing output and record unknowns instead of guessing.
5. Stop when a hard gate is missing, scope expands, backend evidence conflicts, or required verification cannot run.

## Boundaries

- Only four top-level delivery commands are valid: `/ideate`, `/define`, `/build`, `/ship`.
- `/local-review` is a standalone non-delivery local audit command owned by `local-review-gate`; do not route it through this delivery lifecycle skill as a fifth lifecycle mode.
- Research, questionnaire, test-plan, implementation, debugging, review, repair, and harness evolution are internal stages, not user command entrypoints.
- Anti-entrypoint blacklist: do not expose or invent top-level `/research`, `/questionnaire`, `/test-plan`, `/implement`, `/debug`, `/review`, `/repair`, `/harness`, or backend-specific lifecycle commands.
- Backend-specific task systems store artifacts; they do not weaken lifecycle gates.
- Do not start BUILD from DEFINE output unless the user has confirmed the relevant spec/questionnaire/test document state, explicitly waived it, or explicitly accepted an `Unverified` gate.

## Verification

- Confirm the selected mode and backend in the response.
- Name the artifact(s) created or updated.
- For BUILD and SHIP, include traceability-backed fresh verification evidence or mark remaining items `Open Question` / `Unverified`.
- For any blocked gate, return the missing approval, artifact, or evidence as the next action.
