# Review Orchestration Adaptation

## Provenance

| Field | Value |
|---|---|
| Upstream source | `https://github.com/affaan-m/ECC` |
| Upstream HEAD | `49128b5763b7ac0b50acef35ac0bcca08d1576af` |
| Source paths | `commands/orch-review.md`, `commands/multi-plan.md`, `commands/multi-execute.md`, `commands/multi-backend.md`, `commands/multi-frontend.md`, `commands/multi-workflow.md` |
| Source blobs | `5216c7df157a9099214c122bc096e9693730ac77`, `b50912b1f0900ed34935228d973dd92902b97342`, `167a9b559e54b2caa4ad0700635cf5c9b1a367d9`, `95cc95d831d65779d86203f446b043cbee0af66a`, `fc1c402d985f46baf31cacf465d1db2f6c0ce3da`, `5458945c22a20eaa43eb332f53db7a7da1d2a408` |
| License | MIT License, Copyright 2026 Affaan Mustafa |
| Copy/adapt scope | Adapted fan-out/fan-in, fail-closed review, dedupe, adversarial verification, and phased plan/execute/audit concepts; external runtime commands are rejected. |
| Rationale | ECC orchestration patterns strengthen AILI's existing ROSE-owned lane dispatch without broadening public command surface. |

## Secondary provenance

| Field | Value |
|---|---|
| Upstream source | `https://github.com/addyosmani/agent-skills` |
| Upstream HEAD | `8c6530305396f341b5da7201cf1f7e390fdb863f` |
| Source path | `references/orchestration-patterns.md` |
| Source blob | `09cddd31d52a95be1d9bca814547d184b9945e44` |
| License | MIT License, Copyright 2025 Addy Osmani |
| Copy/adapt scope | Adapted direct invocation, single-persona command, parallel fan-out with merge, user-driven pipelines, and research isolation; Claude-only runtime details are not active. |

## OpenCode / AILI adaptation boundaries

- Do not add public `multi-*` commands, ECC-named commands, or router personas.
- Do not activate external workflow runtimes, Agent Teams, Claude-specific team/tool assumptions, Codex/Gemini runtime dependencies, or `ccg-workflow`.
- ROSE/MainAgent is the only orchestrator and the only final decision owner.
- Personas do not invoke other personas; review lanes may recommend follow-up lanes only.
- Review, security, convergence, and test-analysis lanes are read-only unless their specific lane contract is a bounded test runner with no source edits.

## Activated AILI behavior

- Direct invocation remains preferred for one perspective on one artifact.
- Single-persona command behavior stays scoped to `/local-review`; it routes target resolution and report state, not a broad router command.
- Parallel fan-out is used only when lanes are independent, read-only, and return evidence that ROSE can merge.
- Each lane packet carries target identity, accepted scope, source artifacts, diff/files, verification evidence, skipped-lane constraints, artifact placement, forbidden remote mutation, expected status vocabulary, and missing-evidence handling.
- Fail closed when a required lane fails, returns empty/status-less output, lacks evidence anchors, or cannot inspect required context.
- Dedupe findings by affected file/artifact, failure mode, and required action; preserve the highest defensible severity.
- Split findings into blocking and advisory buckets: confirmed Critical/Important or unverifiable high-risk findings block; suggestions and refuted findings remain advisory.
- Use adversarial verification for Critical/Important findings: check whether context, tests, types, existing guards, or project rules disprove the finding before blocking.
- For phased BUILD work, run serial phase checkpoints and merged-output verification at parallel joins before later phases continue.

## Rejected upstream behavior

- A workflow tool owning approval or publish decisions.
- Raw PR argument shell use.
- Any GitHub comment, review, approve, merge, checkout, clone, push, or API mutation from review mode.
- Replacing `/ideate`, `/define`, `/build`, or `/ship` with ECC multi-agent commands.
