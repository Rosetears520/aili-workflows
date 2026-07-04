# Direct vs Delegated Work

本文件定义 ROSE 何时可以直接回答，何时必须先派发 subagent 或进入 gate。它是 `agents/rose.md` 的短 router 背后的详细规则。

## Authority

- Repository source reference: `.agents/skills/aili-delivery-flow/references/direct-vs-delegated-work.md`
- Related source protocols: `.agents/skills/aili-delivery-flow/references/protocols/subagent-task-packet.md` and `.agents/skills/aili-delivery-flow/references/protocols/subagent-result.md`
- Installed runtime targets use the same suffix under `$HOME/.agents/skills/aili-delivery-flow/`.
- Search evidence is a map, not a replacement for reading final target files before editing, reviewing, testing, securing, or documenting.

## Subagent-first default

Non-trivial repository tasks default to subagent-first routing. ROSE stays in Supervisor/orchestrator mode, scopes the work, dispatches the appropriate subagent or worker for evidence, implementation, review, test, or security work, reconciles evidence, and owns the final user-facing judgment.

Read-only subagents are specifically for evidence gathering and context-saving investigation. They are not the only delegation path: non-trivial repository edits route to an appropriate implementation worker or other scoped worker rather than being performed directly by ROSE.

The following are not direct-work reasons by themselves:

- a clear target or exact path;
- short visible context;
- a DCP or handoff summary;
- confidence that the change is small after only reading the prompt;
- a single-file edit that changes runtime rules, skills, command routing, subagent contracts, memory policy, security, release, install, CI, schemas, dependencies, or data semantics.

## Direct allowlist

ROSE may work directly only when all criteria are true:

1. The task is either pure conversation with no repository edit/verification obligation, or the user gives an explicit current-task opt-out from subagents for repository-affecting work.
2. Low risk: no security, release, data semantics, dependency, schema, memory, install, CI, command routing, or permission blast radius.
3. Surgical change: small local edit with no adjacent cleanup, broad refactor, rename, or formatting sweep.
4. Locally verifiable: verification is obvious and local, such as diff inspection, a targeted static check, or a narrowly relevant command.
5. No convention discovery: the edit does not require learning project patterns, upstream/downstream behavior, peer examples, or active-vs-stale references.

Examples that can be direct without a subagent opt-out only when they are pure conversation with no repository-affecting edit or verification obligation:

- answering a question from already-provided context
- explaining a command, concept, or previously supplied snippet
- drafting wording in chat without writing it to the repository

Examples that still require an explicit current-task opt-out from subagents before direct repository work, even when the target is exact and the edit is tiny:

- typo, documentation wording, comment, or Markdown formatting in a file
- unimportant display text
- small README/example/test-instruction paragraph
- a single non-security, non-release, non-data-semantic parameter
- tiny local code fix with exact target and simple verification

Direct work is not allowed merely because a change touches one file or has an exact path. Single-file changes to ROSE/runtime rules, skills, commands, subagent contracts, memory policy, schema, CI, dependencies, security, release, install behavior, or data semantics must be delegated, evidence-gated, or approval-gated unless the current task explicitly opts out of subagents and the remaining gates still pass.

## Mandatory delegation triggers

ROSE MUST use a read-only subagent when evidence collection would materially pollute or consume MainAgent context, even if the final edit may be small.

Mandatory delegation triggers include:

- any non-trivial repository edit, review, test, security, or verification package without an explicit current-task subagent opt-out
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

1. the pure-conversation reason or explicit current-task subagent opt-out; and
2. the remaining safety, scope, and verification evidence basis.

## Gate mapping

- Local code evidence: read-only `code-scout`
- Local docs/workflow evidence: `doc-researcher`
- External official/current behavior: `web-researcher`
- Repository implementation: scoped implementation worker
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
