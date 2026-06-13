# Subagent Task Packet Protocol

Canonical path for this change: `skills/aili-delivery-flow/references/protocols/subagent-task-packet.md`.

Use this packet for non-trivial, harness-sensitive, evidence-heavy, review, test, security, debugging, or implementation subagent work. Do not rely on a subagent inheriting the main conversation.

```text
Subagent task packet:
- Trace/work package id:
- Owner: ROSE | user | subagent:research | subagent:edit | subagent:review | subagent:test
- Work package type:
- Artifact target:
- Goal:
- Context / required context:
- Active contract / source artifacts:
- Allowed scope:
- Forbidden scope:
- Edit permission / allowed edits:
- Evidence required:
- Optional evidence provider request: CodeGraph if available/useful, or N/A
- Expected return format:
- Join contract for parallel lanes:
- Placement / artifact rules:
- Coverage expectations:
- Known exclusions:
- Verification or inspection commands, if any:
- Stop conditions:
```

## Field rules

- Owner: explicit execution owner. Preserve the owner prefix in todos and task packets; ROSE must not mark `subagent:*` todos complete based on ROSE's own edits, reviews, tests, or completion work.
- Goal: one bounded outcome.
- Context: only the facts needed to start; include current user decisions when relevant.
- Active contract / source artifacts: paths to specs, tasks, diffs, issues, or docs that define scope.
- Work package type: classify as implementation, scout, review, test, security, debug, or documentation so ROSE can reconcile lanes independently.
- Allowed scope: exact files, directories, systems, or evidence sources the subagent may inspect or edit.
- Forbidden scope: files, commands, subsystems, or decisions that are out of bounds.
- Edit permission: `read-only`, `may edit listed files`, or `ask before edits`.
- Evidence required: anchors, tests, compact evidence packs, command summaries, or inspected sections required for ROSE to reconcile; request minimal key failure excerpts instead of raw logs.
- Optional evidence provider request: CodeGraph may be requested only for eligible lane-local discovery; it must remain optional, compact, fallback-capable, and separate from final proof.
- Expected return format: normally the canonical `subagent-result.md` format, `compact-evidence-pack.md`, or a named compact variant.
- Join contract for parallel lanes: expected evidence for this lane, how ROSE will handle conflicts or missing evidence, ROSE/user final decision ownership, and stop conditions that block reconciliation.
- Placement / artifact rules: where generated artifacts go, or `no files`; raw evidence artifacts require an explicit repository-local placement and are not created by default.
- Coverage expectations: what must be checked before returning.
- Known exclusions: secrets, raw logs, long dumps, full file dumps, unrelated cleanup, nested agents, commits, pushes.
- Stop conditions: blockers, conflicting evidence, missing permissions, unsafe ambiguity, or scope expansion.

## Delegation safety pre-check

Before ROSE sends a packet, confirm:

1. ROSE can cheaply inspect the returned anchors, artifact, diff, or command summary.
2. Inspecting the returned result is cheaper than doing the work directly.
3. Likely errors are reversible, bounded, or caught by verification/review.
4. The subagent has enough context, allowed scope, forbidden scope, and stop conditions.
5. The output shape requires fixed evidence anchors, artifacts, commands, residual uncertainty, and any decision needed from ROSE/user.
6. ROSE/user remains the final decision owner.

If any check fails, narrow the scope, make the work read-only, dispatch sequentially, or ask the user before delegating.

## Hard rules

- Subagents do not spawn subagents unless a future approved contract explicitly changes orchestration rules.
- Execution Ownership Gate: valid owners are `ROSE`, `user`, `subagent:research`, `subagent:edit`, `subagent:review`, and `subagent:test`.
- User-requested subagent ownership: 修改/补强/完成/do/update/implement maps to `subagent:edit`; 复核/review/audit maps to `subagent:review`; 看一下/调研/find evidence/scout maps to `subagent:research` only; test/verify/run tests/coverage/测试/验证/跑测试 maps to `subagent:test`.
- Evidence is sufficient may complete only `subagent:research`; it must not let ROSE take over `subagent:edit`, `subagent:review`, `subagent:test`, or user-requested subagent completion work without explicit current-task user confirmation.
- After decomposing non-trivial work, ROSE actively looks for independent evidence/search directions, implementation packages, documentation checks, review, test, and security lanes before choosing dispatch shape.
- Split broad research/search by subsystem, hypothesis, evidence source, or direction when that increases coverage and lanes can return structured evidence-only results.
- Read-heavy delegation is preferred; write-heavy parallel work requires non-overlapping file ownership and clear verification/review boundaries.
- If independent implementation, research, review, test, documentation, or security lanes can proceed without each other's outputs and return evidence without overlapping edits or hidden dependencies, prefer parallel subagents.
- After non-trivial implementation, review, test/verification, and security lanes should normally be separate evidence lanes when relevant; they return recommendations and evidence only.
- Non-trivial repository work is subagent-first unless the current task explicitly opts out; clear paths, short context, and DCP summaries are not opt-outs.
- Worker increments are dynamically sized by verifiability, reviewability, lack of parallel conflicts, and clean handoff boundaries.
- Workers return compact reports and evidence only. They do not write `progress.txt` and do not issue final PASS/FAIL/`Unverified` judgments.
- CodeGraph, when requested or provided, is discovery evidence only; workers must fall back to normal search/read if it is unavailable, stale, noisy, or unhelpful, and acting edit/review/test/doc lanes must still inspect final targets before conclusions.
- A subagent packet is a scope boundary, not a license to broaden work.
- ROSE remains responsible for reconciliation, verification judgment, and final acceptance.
