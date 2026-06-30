## ADDED Requirements

### Requirement: Specialized QA/testing agents and skills

AILI SHALL provide specialized QA/testing agents and matching skill workflows for test coverage review, PR/change test analysis, AI regression scouting, silent failure detection, browser QA, and E2E artifact handling.

These lanes SHALL complement the existing broad `test-engineer` lane. They MUST have precise trigger boundaries, ownership labels, allowed tools, artifact placement rules, and evidence output contracts.

#### Scenario: Coverage review lane is triggered

- **WHEN** a change needs assessment of whether tests cover changed behavior, edge cases, error paths, and meaningful assertions
- **THEN** ROSE may route to `test-coverage-reviewer` or the matching skill
- **AND** the lane reports covered behavior, missing behavior, assertion quality, and recommended tests without claiming tests pass unless fresh commands prove it

#### Scenario: PR/change test analysis is triggered

- **WHEN** a change spans multiple files, packages, or externally visible behavior and the question is whether the test suite matches the diff
- **THEN** ROSE may route to `pr-test-analyzer`
- **AND** the lane maps changed files/behaviors to tests, risk areas, and regression gaps

#### Scenario: AI regression scout is triggered

- **WHEN** a change involves AI-generated code risk, mocks vs production paths, API/schema response shapes, optimistic updates, sandbox/runtime path differences, or error-state cleanup
- **THEN** ROSE may route to `ai-regression-scout`
- **AND** the lane reports AI-specific regression risks and focused verification suggestions

#### Scenario: Silent failure reviewer is triggered

- **WHEN** a change includes fallbacks, swallowed exceptions, async/background work, retries, logging, partial success, or error propagation
- **THEN** ROSE may route to `silent-failure-reviewer`
- **AND** the lane looks for hidden failures, misleading success states, and missing propagation or observability

#### Scenario: Browser QA is triggered

- **WHEN** a change affects UI/browser behavior and browser verification is relevant
- **THEN** ROSE may route to `browser-qa-runner` or the browser QA skill
- **AND** the lane checks DOM behavior, console/network signals, accessibility smoke, and visual/user-flow risks according to available tools
- **AND** it does not mutate production data or create user-visible browser artifacts outside an approved repository-local location

#### Scenario: E2E artifact lane is triggered

- **WHEN** a change requires E2E journeys, screenshots, traces, videos, flake triage, or CI artifact evidence
- **THEN** ROSE may route to `e2e-artifact-runner` or the matching skill
- **AND** the lane records artifact paths, flake status, skipped checks, and required cleanup

### Requirement: QA lanes integrate with review pipeline without over-triggering

The review pipeline SHALL select specialized QA/testing lanes based on task risk and changed behavior rather than always dispatching every lane.

#### Scenario: No specialized QA trigger matches

- **WHEN** a change has no browser/UI, E2E, AI-regression, silent-failure, or coverage-review trigger beyond ordinary focused verification
- **THEN** ROSE may use the broad `test-engineer` lane or direct focused verification only
- **AND** reports why specialized QA lanes were not needed

#### Scenario: Multiple specialized QA triggers match

- **WHEN** more than one specialized QA lane is relevant and their work is read-only or evidence-only
- **THEN** ROSE may fan out those lanes in parallel with a join contract
- **AND** reconciles conflicts, missing evidence, and `Unverified` items before any readiness claim

### Requirement: QA artifacts stay repository-local and scoped

QA/testing lanes SHALL follow project artifact placement rules for screenshots, traces, reports, fixtures, and generated test plans.

#### Scenario: Artifact location is missing

- **WHEN** a QA lane would create a user-visible report, trace, screenshot, fixture, or generated test artifact and no approved repository-local placement exists
- **THEN** ROSE or the lane MUST ask for placement or mark the artifact step blocked
- **AND** MUST NOT store user-visible artifacts only in OS temp paths
