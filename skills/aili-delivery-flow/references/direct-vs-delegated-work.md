# Direct vs Delegated Work

本文件定义 ROSE 何时可以直接编辑，何时必须先派发 subagent 或进入 gate。它是 `agents/rose.md` 的短 router 背后的详细规则。

## Authority

- Canonical reference: `skills/aili-delivery-flow/references/direct-vs-delegated-work.md`
- Related protocols: `skills/aili-delivery-flow/references/protocols/subagent-task-packet.md` and `skills/aili-delivery-flow/references/protocols/subagent-result.md`
- Search evidence is a map, not a replacement for reading final target files before editing, reviewing, testing, securing, or documenting.

## Direct allowlist

ROSE may work directly only when all criteria are true:

1. Exact target: exact file, symbol, line, or clearly bounded artifact is known.
2. Low risk: no security, release, data semantics, dependency, schema, memory, install, CI, command routing, or permission blast radius.
3. Surgical change: small local edit with no adjacent cleanup, broad refactor, rename, or formatting sweep.
4. Locally verifiable: verification is obvious and local, such as diff inspection, a targeted static check, or a narrowly relevant command.
5. No convention discovery: the edit does not require learning project patterns, upstream/downstream behavior, peer examples, or active-vs-stale references.

Examples that can be direct when all criteria above hold:

- typo, documentation wording, comment, Markdown formatting
- unimportant display text
- small README/example/test-instruction paragraph
- a single non-security, non-release, non-data-semantic parameter
- tiny local code fix with exact target and simple verification

Direct work is not allowed merely because a change touches one file. Single-file changes to ROSE/runtime rules, skills, commands, subagent contracts, memory policy, schema, CI, dependencies, security, release, install behavior, or data semantics must be delegated, evidence-gated, or approval-gated.

## Mandatory delegation triggers

ROSE MUST use a read-only subagent when evidence collection would materially pollute or consume MainAgent context, even if the final edit may be small.

Mandatory delegation triggers include:

- broad grep/list/search output
- 3+ relevant files
- 2+ directories/subsystems
- 2+ search passes
- noisy logs, tests, or CI output
- active/current/stale/archived/generated reference judgment
- all-reference scans
- upstream/downstream/peer implementation mapping
- test coverage mapping
- convention discovery before non-trivial edits
- residual marker, migration completeness, or stale artifact scans

If ROSE skips delegation for a non-trivial task, it must state both:

1. why the direct allowlist applies; and
2. why subagent dispatch would not add material evidence or context savings.

## Gate mapping

- Local code evidence: `code-scout`
- Local docs/workflow evidence: `doc-researcher`
- External official/current behavior: `web-researcher`
- Verification coverage or test strategy: `test-engineer`
- Security, secrets, permissions, auth, trust model, install/hooks: `security-auditor`
- Ambiguous plan/spec/task package: `plan-auditor`

Use the lightest specialist that can return compact evidence anchors.

## High-risk boundaries

Require explicit approval before dependencies, lockfiles, schema/migrations, public API/auth/permission behavior, install scripts, hooks, destructive commands, file deletes/moves/renames, pushes, merges, tags, broad formatting, or core harness authority rewrites outside the approved package.

## Completion evidence

Before claiming complete, report:

- files changed
- evidence source and command/result
- which direct/delegated gates were used
- unverified or deferred items
