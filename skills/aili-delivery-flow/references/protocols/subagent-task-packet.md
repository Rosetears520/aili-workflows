# Subagent Task Packet Protocol

Canonical path for this change: `skills/aili-delivery-flow/references/protocols/subagent-task-packet.md`.

Use this packet for non-trivial, harness-sensitive, evidence-heavy, review, test, security, debugging, or implementation subagent work. Do not rely on a subagent inheriting the main conversation.

```text
Subagent task packet:
- Trace/work package id:
- Owner: ROSE | subagent:research | subagent:edit | subagent:review | subagent:test
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
- Trace/work package id: stable lane/package id used in dispatch, todos, and join reporting. Preserve existing ids from user packets, DEFINE artifacts, BUILD package queues, or prior ROSE plans unless a boundary change is explicitly justified.
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
- Join contract for parallel lanes: expected evidence for this lane, lane owner, editable scope or read-only source, status vocabulary, blocker conditions, how ROSE will handle conflicts or missing/empty evidence, ROSE final decision ownership, any required user approval/decision gate, and stop conditions that block reconciliation.
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
5. The output shape requires fixed evidence anchors, artifacts, commands, residual uncertainty, and any decision or approval gate ROSE must resolve with the user.
6. ROSE remains the final decision owner and records any required user decision/approval before acting.
7. Existing package/lane boundaries are preserved or every merge, serialization, scope reassignment, or owner change has an explicit dependency, ownership-overlap, verification, safety, missing-evidence, failed-result, or current-user reason.

If any check fails, narrow the scope, make the work read-only, dispatch sequentially, or ask the user before delegating.

## Proactive parallelism and boundary rules

- Before dispatching or presenting work with two or more independently actionable units, ROSE must perform visible proactive parallelism analysis: shared scaffold/source-of-truth work, safe parallel lanes, serial dependencies, concurrent research/review/test/search lanes, ownership boundaries, join points, and blockers.
- If no parallelism is safe, the packet or plan must name the no-parallel reason, such as `1 must complete before 2/3/4 can parallelize`, `1/2/3/4 must run strictly serially`, overlapping editable scope, shared mutable state, missing scaffold, or user-directed ordering.
- Preserve existing package/lane boundaries in packet ids, owners, scopes, todos, and expected return formats. Do not collapse or serialize separated lanes without a stated dependency, ownership conflict, verification coupling, safety gate, failed/missing evidence, or explicit current-task user direction.

## Join completeness rules

- Multi-lane or parallel packet sets must define the join contract before dispatch: lane id, owner, expected evidence, editable scope or read-only evidence source, status vocabulary (`completed`, `partial`, `blocked`, `skipped`, `unverified`), blocker conditions, conflict handling, missing/empty-evidence handling, ROSE final decision owner, and any required user approval/decision gate.
- A missing, empty, status-less, or evidence-less lane result is not complete. ROSE must not infer completion from file state, adjacent lane success, or ROSE's own inspection.
- If required lane evidence is missing, ROSE requests a bounded evidence-only follow-up, marks the lane `partial`/`blocked`/`unverified`, or reassigns only with explicit current-task approval when ownership rules require it.
- Join reporting must list every expected lane with status, changed or inspected scope, verification result or skipped-verification reason, remaining blockers, and missing evidence before integration or completion claims.

## Hard rules

- Subagents do not spawn subagents unless a future approved contract explicitly changes orchestration rules.
- Execution Ownership Gate: valid owners are `ROSE`, `subagent:research`, `subagent:edit`, `subagent:review`, and `subagent:test`. Do not create `user:` todos; ROSE owns asking the user and recording any needed approval or decision gate.
- User-requested subagent ownership: 修改/补强/完成/do/update/implement maps to `subagent:edit`; 复核/review/audit maps to `subagent:review`; 看一下/调研/find evidence/scout maps to `subagent:research` only; test/verify/run tests/coverage/测试/验证/跑测试 maps to `subagent:test`.
- Evidence is sufficient may complete only `subagent:research`; it must not let ROSE take over `subagent:edit`, `subagent:review`, `subagent:test`, or user-requested subagent completion work without explicit current-task user confirmation.
- After decomposing non-trivial work, ROSE actively looks for independent evidence/search directions, implementation packages, documentation checks, review, test, and security lanes before choosing dispatch shape.
- Two or more independently actionable work units require proactive parallelism analysis before dispatch or serialization.
- Split broad research/search by subsystem, hypothesis, evidence source, or direction when that increases coverage and lanes can return structured evidence-only results.
- Read-heavy delegation is preferred; write-heavy parallel work requires non-overlapping file ownership and clear verification/review boundaries.
- If independent implementation, research, review, test, documentation, or security lanes can proceed without each other's outputs and return evidence without overlapping edits or hidden dependencies, prefer parallel subagents.
- After non-trivial implementation, review, test/verification, and security lanes should normally be separate evidence lanes when relevant; they return recommendations and evidence only.
- Non-trivial repository work is subagent-first unless the current task explicitly opts out; clear paths, short context, and DCP summaries are not opt-outs.
- Worker increments are dynamically sized by verifiability, reviewability, lack of parallel conflicts, and clean handoff boundaries.
- Workers return compact reports and evidence only. They do not write `progress.txt` and do not issue final PASS/FAIL/`Unverified` judgments.
- CodeGraph, when requested or provided, is discovery evidence only; workers must fall back to normal search/read if it is unavailable, stale, noisy, or unhelpful, and acting edit/review/test/doc lanes must still inspect final targets before conclusions.
- A subagent packet is a scope boundary, not a license to broaden work.
- Package/lane ids, owners, allowed scopes, and expected evidence are boundary markers and must survive dispatch and reconciliation unless ROSE records an approved boundary-change reason.
- ROSE remains responsible for reconciliation, verification judgment, and final acceptance.
