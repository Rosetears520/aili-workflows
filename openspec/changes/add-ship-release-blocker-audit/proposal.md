## Why

`/ship` already owns release-readiness, but the current contract does not explicitly name the user-requested check for release-blocking bugs and risks across a selected proposal, final diff, baseline comparison, or broader codebase scan. Making this explicit will reduce stale-evidence ready claims and clarify that release-blocking user-impacting regressions, security exposure, unsafe workflow behavior, and unresolved verification gaps must be surfaced before handoff, merge, archive, or release.

## What Changes

- Add an explicit SHIP-mode **release-blocker audit** concept to the existing AILI delivery lifecycle.
- Define supported audit target scopes: active OpenSpec/change artifacts, current final diff, comparison against a named baseline or previous release, and broader repository scan only when explicitly requested or risk-triggered.
- Require `/ship` to classify findings that could block release-readiness, including user-impacting behavior regressions, security or permission exposure, unsafe/destructive workflow behavior, data-loss risk, artifact inconsistency, stale evidence, unresolved review/test/security findings, and unverified acceptance criteria.
- Keep review, repair, security, test, and blocker audit as internal SHIP stages rather than introducing a new public top-level command.
- Preserve the hard stop: no ready/ship/pass claim when release-blocking findings are unresolved, accepted-risk decisions are missing, or evidence is stale or absent.
- No **BREAKING** command rename or dependency change is intended.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `aili-four-command-lifecycle`: Clarify `/ship` release-readiness behavior by adding explicit release-blocker audit target selection, finding classification, fresh-evidence requirements, and no-new-top-level-command boundaries.

## Impact

- Affected command prompt: `commands/ship.md`.
- Affected lifecycle references: `skills/aili-delivery-flow/references/lifecycle.md`, `skills/aili-delivery-flow/references/review-repair-loop.md`, and possibly `skills/aili-delivery-flow/references/artifact-contracts.md` or protocol templates if the closeout report needs a blocker-audit field.
- Affected documentation/specs: `docs/harness/command-lifecycle.md`, `docs/harness/aili-harness-contract.md`, `README.md`, and `openspec/specs/aili-four-command-lifecycle/spec.md` after archive/sync.
- No production dependency, lockfile, database, memory schema, install script, or public command-set expansion is planned.
