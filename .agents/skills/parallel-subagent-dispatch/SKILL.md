---
name: parallel-subagent-dispatch
description: Use when ROSE needs context-saving subagent dispatch: single read-only scouting for noisy repository evidence, or splitting two or more independent investigation, implementation, review, testing, documentation, or security work packages across subagents without shared mutable state, overlapping edits, or sequential dependencies.
license: MIT
compatibility: opencode
metadata:
  source: adapted-from-superpowers
---

# Parallel Subagent Dispatch

## Purpose

Use subagents when delegation preserves MainAgent context, when separate work packages can proceed independently and return evidence for ROSE to reconcile, or when a non-trivial repository task enters the subagent-first runtime path.

This skill adapts Superpowers-style parallel dispatch discipline to this repository's OpenCode model: ROSE remains the primary orchestrator, subagents receive precise task packets, and no persona delegates to another persona. A30 cross-root reads are supported only through ROSE Task dispatch in the same OpenCode instance; direct user `@` invocation is outside A30 guarantees.

For local review and review-pipeline fan-out, this skill also activates the orchestration boundaries recorded in `.agents/skills/local-review-gate/references/orchestration-adaptation.md`: borrow ECC/addyosmani fan-out/fan-in and main-agent-only-writer patterns, but reject public `multi-*` commands, router personas, nested persona calls, `.claude` paths, Claude-only tools, external workflow runtimes, `ccg-workflow`, Codex/Gemini runtime dependencies, and remote mutation defaults.

## When to Use

Use this skill for context-saving dispatch, parallel dispatch, and subagent-first routing of non-trivial repository work. Default toward delegation for non-trivial repository tasks; direct ROSE work needs the explicit direct allowlist or current-task opt-out from `.agents/skills/aili-delivery-flow/references/direct-vs-delegated-work.md` in repository source, or the installed runtime target under `$HOME/.agents/skills/aili-delivery-flow/`.

Pure conversation and explicit current-task subagent opt-out may stay direct. A clear target, exact path, short context, or DCP summary is not a direct-work reason by itself.

Use a single read-only subagent, especially `code-scout`, even when there is only one work package, if doing the work in MainAgent would pollute context with broad search, large grep output, repeated file reads, logs, or exploratory dead ends.

For ROSE runtime work, this is mandatory when the direct allowlist does not apply. ROSE remains Supervisor; workers return compact reports, recommendations, and evidence, not final PASS/FAIL/`Unverified` judgments.

Executable dispatch rules:

- When user asks for repository work and it is non-trivial, dispatch a scoped subagent unless the direct allowlist or explicit opt-out applies; if staying direct, say which one applies.
- After decomposing non-trivial work, actively look for independent lanes instead of only deciding whether ROSE should work directly or delegate.
- When decomposition yields two or more independently actionable work units, perform visible proactive parallelism analysis before dispatching or serializing: name shared scaffold/source-of-truth work, safe parallel lanes, serial dependencies, concurrent research/review/test/search lanes, ownership boundaries, join points, and blockers.
- When two or more independent evidence-returning slices can proceed without each other's outputs, do not share mutable edits/state, and can return structured evidence-only results, dispatch them in parallel; if they share mutable state or sequencing, split sequentially instead.
- Preserve already separated package or lane boundaries through packets, todos, and join reporting unless dependency, ownership overlap, verification coupling, safety risk, missing/failed evidence, or explicit current-task user direction requires merging, serializing, or reassignment; state the reason when boundaries change.
- When implementation is non-trivial, normally run separate review and test/verification evidence lanes afterward; add a security lane when the changed surface includes auth, permissions, secrets, shell/installers, dependencies, network, storage, or other security-sensitive behavior.
- For serial phase work, every phase packet declares a phase checkpoint: command, static check, artifact inspection, diff inspection, or skipped reason with risk; do not continue a dependent phase until ROSE reconciles that checkpoint or records user-accepted risk.
- For parallel phase work, every join contract declares merged-output verification; after all lanes return, ROSE reconciles statuses, evidence, conflicts, blockers, skipped checks, and missing evidence, then runs or requests verification over the merged output before continuing.
- When a subagent returns evidence, reconcile anchors before deciding; do not copy the recommendation as ROSE's final verdict.

## Parallel Lane Discovery

After decomposing non-trivial work, ROSE should identify all safe independent lanes before dispatching. Look for:

- search or research lanes split by subsystem, hypothesis, evidence source, or direction to improve coverage
- implementation lanes with non-overlapping file ownership and clear verification/review boundaries
- documentation, test, review, and security lanes that can inspect the same completed diff or distinct artifacts without mutating shared state

Use fan-out/fan-in when lanes can start now, do not need each other's outputs, avoid shared mutable edits/state, and can return structured evidence-only results. Dispatch one subagent per lane in parallel, wait for all lanes, reconcile conflicts, missing evidence, and duplicated work, then decide the next action as ROSE or ask the user.

If no parallel lane is safe after two or more independently actionable units are identified, record the no-parallel reason visibly, such as `1 must complete before 2/3/4 can parallelize`, `1/2/3/4 must run strictly serially`, overlapping editable scope, shared mutable state, a missing scaffold, or a user-directed order. Keep any later fan-out candidates visible after the blocking scaffold or dependency join point.

Once ROSE has identified independent lanes, keep each lane's scope and owner visible even when execution becomes serial. Do not collapse separate packages, research directions, review/test/security lanes, or implementation slices into one opaque task unless new evidence shows the split is unsafe, dependent, unverifiable, or out of user scope.

Good single-subagent uses:
- residual marker scans across many files
- personal-name or local-path scans
- finding all references to a legacy API, config key, header, route, symbol, or marker
- mapping tests that cover a behavior
- mapping upstream callers or entrypoints
- mapping downstream consumers or output paths
- mapping sibling or peer implementations
- mapping convention examples before a non-trivial edit
- checking whether docs/specs/plans reference a path or symbol
- locating security/trust-model evidence
- finding active vs archived/generated references
- confirming whether migration leftovers remain

Use parallel subagents when there are two or more independent work packages, such as:

- code review and test analysis on the same completed diff; run the security lane independently when the changed surface includes auth, permissions, secrets, shell/installers, dependencies, network, storage, or other security-sensitive behavior
- separate root-cause investigations in unrelated subsystems
- independent documentation, test, and implementation checks that do not edit the same files
- research tasks where each subagent can inspect a distinct subsystem, hypothesis, source, or search direction and return evidence
- independent implementation packages with non-overlapping file ownership and clear verification/review boundaries

Realistic trigger prompts:

- "Run reviewer, security, and test-engineer in parallel on this change."
- "Split these unrelated failures across investigators and merge the findings."
- "Have separate agents inspect frontend, backend, and CI without overlapping edits."

## When Not to Dispatch in Parallel

Do not dispatch in parallel when:

- tasks share mutable state or edit the same files
- one task depends on the result of another
- the work requires a single coherent design decision before implementation
- the task is an immediate tiny pure-conversation answer with no repository read, edit, or verification obligation
- the user asked for one specific persona or a sequential investigation

Non-trigger prompt:

- "Fix this failing test after you identify the root cause." Use `debugging-and-error-recovery` first, then a scoped implementation handoff if needed.

## Context-Saving Dispatch

Return only compact evidence anchors:
- file:line or symbol
- short classification
- active/current/stale/archived/generated status when relevant
- confidence
- recommended MainAgent next reads

Do not paste large file excerpts, full grep dumps, long logs, or exploratory dead ends back into MainAgent context.

Search evidence is a map. The editing, reviewing, testing, securing, or documenting agent must still read final target files before acting.

Optional CodeGraph evidence may be requested in an eligible ROSE-directed lane only for the exact current repository root when it reduces missed-file or impact risk: broad scouting, implementation call-chain checks, review residual impact checks, test scope discovery, or doc/spec claims tied to code anchors. Confirm that root per operation. Initialization requires separate approval for exactly one root; refuse batch/multi-repository initialization even under broad approval. It is not mandatory, not proof, and has no lifecycle/completion authority. Require fallback to normal search/read when unavailable, stale, noisy, or no-result, require the acting lane to read final files, and mark material graph gaps as `Unverified`.

## Execution Ownership Gate

Assign every delegated todo and task packet one explicit owner: `ROSE`, `subagent:research`, `subagent:edit`, `subagent:review`, or `subagent:test`. Do not create `user:` todos; when user input, approval, or a decision is needed, ROSE owns the todo to ask the user and record the gate result. Preserve owner prefixes when copying, splitting, reconciling, or reporting todos/task packets.

User-requested subagent ownership is binding for the current task. If the user asks a subagent to 修改, 补强, 完成, do, update, or implement, use `subagent:edit`; if the user asks a subagent to 复核, review, or audit, use `subagent:review`; if the user asks a subagent to 看一下, 调研, find evidence, or scout, use `subagent:research` only; if the user asks a subagent to test, verify, run tests, coverage, 测试, 验证, or 跑测试, use `subagent:test`.

Evidence is sufficient may complete only a `subagent:research` task. It does not authorize ROSE to complete `subagent:edit`, `subagent:review`, `subagent:test`, or user-requested subagent completion work through ROSE's own edits, reviews, tests, or final integration. ROSE may change subagent-owned edit/review/test/completion work to `ROSE` only after explicit current-task user confirmation, not for efficiency, context, or faster integration reasons.

## Mandatory Dispatch Rule

Dispatch non-trivial repository work by default. Also dispatch when expected MainAgent context cost is greater than subagent overhead.

ROSE MUST use a read-only subagent when likely required evidence includes:
- 3+ relevant files
- 2+ directories/subsystems
- 2+ search passes
- broad grep/list output
- noisy logs/test output
- uncertain active vs stale references
- active/current/stale/archived/generated classification
- all-reference scans
- upstream/downstream/peer implementation mapping
- test coverage mapping
- convention discovery before non-trivial edits
- independent review or coverage assessment

ROSE may skip dispatch only when:
- the result is purely conversational
- the user gives an explicit current-task subagent opt-out
- the user needs an immediate tiny answer, meaning pure conversation only and no repository work
- parallel subagents would need to write overlapping files; avoid parallel dispatch and use sequential/scoped delegation, or stop if safe ownership cannot be established
- the work satisfies the direct allowlist in `.agents/skills/aili-delivery-flow/references/direct-vs-delegated-work.md` or its installed runtime target under `$HOME/.agents/skills/aili-delivery-flow/`

If ROSE skips delegation for a non-trivial task, it must state the direct opt-out or pure-conversation reason and the remaining safety/evidence basis. Exact file knowledge, short context, or DCP summaries do not justify skipping dispatch.

If independent implementation, research, review, test, documentation, or security lanes can return evidence without overlapping edits or hidden dependencies, prefer parallel subagents. Parallel outputs remain evidence for ROSE/user; they are not approve/reject/ship decisions.

Read-heavy delegation is preferred. Write-heavy parallel delegation requires non-overlapping file ownership and clear verification/review boundaries; if ownership overlaps, use sequential/scoped delegation or stop.

Implementation worker increments are dynamic: size them by verifiability, reviewability, absence of parallel edit conflicts, and clean handoff boundaries rather than a fixed number of files.

## Independence Check

Before dispatching, ROSE must verify:

1. Each work package has a distinct goal.
2. Each package has distinct allowed files, systems, or evidence sources.
3. No package requires another package's output to start.
4. Any edit permissions are isolated and non-overlapping.
5. Each subagent can return enough evidence for ROSE to merge results.
6. The join contract names expected evidence per lane, conflict/missing-evidence handling, final decision owner, and stop conditions.
7. Each serial phase packet declares a phase checkpoint: command, static check, artifact inspection, diff inspection, or skipped reason with risk.
8. Existing package/lane boundaries from the user, DEFINE artifacts, BUILD package queue, or prior ROSE plan are preserved, or every merge/serialization/reassignment has an explicit dependency, ownership, verification, safety, missing-evidence, failed-result, or user-scope reason.

If any item fails, run the work sequentially or narrow the task packets until independence is true.

## Join Contract Completeness

For parallel or multi-lane work, define the join contract before dispatch and reconcile it before integration or final reporting.

The join contract must list, per lane:

- lane id or work package id
- owner (`ROSE` or `subagent:*`)
- expected evidence and return format
- editable scope or read-only evidence source
- status vocabulary: `completed`, `partial`, `blocked`, `skipped`, or `unverified`
- blocker and stop conditions
- conflict handling and missing/empty-evidence handling
- final decision owner, normally ROSE, plus any required user approval/decision gate
- merged-output verification required at the join point before later phases continue

Missing, empty, or status-less lane output is not completion evidence. Do not infer a lane is complete from file state, adjacent successful lanes, or ROSE's own inspection. If required evidence is missing, request a bounded evidence-only follow-up, mark the lane `partial`/`blocked`/`unverified`, or reassign only with explicit current-task approval when ownership rules require it.

Join reports must name every lane and include its status, changed or inspected scope, verification result or skipped-verification reason, conflicts, remaining blockers, and any missing evidence before ROSE integrates results or claims completion. For parallel implementation or artifact lanes, the join report must also name the merged-output verification command, static check, artifact inspection, diff inspection, or skipped reason with risk.

## Delegation Safety Check

Before dispatching, ask:

1. Can ROSE cheaply inspect the returned anchors, artifact, diff, or command summary?
2. Is inspecting the returned result cheaper than doing the whole work inside ROSE?
3. Are likely errors reversible, bounded, or caught by verification/review?
4. Does the subagent packet contain enough context, scope, stop conditions, and forbidden scope?
5. Does the requested output require fixed evidence anchors, artifacts, commands, or residual uncertainty?
6. Is the final decision owner ROSE, not the subagent, with any required user approval/decision gate explicit?

If any answer is no, narrow the packet, make the lane read-only, run the work sequentially, or stop for clarification.

🔴 CHECKPOINT before dispatch: name each packet owner, allowed scope, evidence source, edit permission, expected evidence, conflict/missing-evidence handling, final decision owner, stop conditions, and reconciliation criterion. Do not dispatch until overlapping edits, hidden sequencing, and missing specialist lanes are resolved or explicitly blocked.

| If this is true | Do this first | If still unresolved |
|---|---|---|
| Two subagents would edit the same file or shared mutable state | Split into sequential packets or assign one editor and one read-only reviewer | Stop; report overlapping ownership instead of parallelizing |
| A packet needs another packet's result to start | Run the dependency first and dispatch only the independent remainder | Stop; mark parallel dispatch unsafe |
| Required evidence source is unclear | Narrow the packet to scouting only and require evidence anchors | Return `BLOCKED_CONTEXT_INSUFFICIENT` to ROSE |
| User requested a specific subagent owner | Preserve that owner in the packet | Ask the user before converting ownership to ROSE |

## Subagent Task Packet Template

Send each subagent a complete packet. Do not rely on it inheriting the main conversation context.

For harness-sensitive work, use `.agents/skills/aili-delivery-flow/references/protocols/subagent-task-packet.md` as the repository-source task packet protocol and `.agents/skills/aili-delivery-flow/references/protocols/subagent-result.md` as the repository-source result protocol; installed runtimes expose the same suffixes under `$HOME/.agents/skills/aili-delivery-flow/`.

```text
Subagent task packet:
- Owner: ROSE | subagent:research | subagent:edit | subagent:review | subagent:test
- Goal:
- Context:
- Allowed scope:
- Forbidden scope:
- Edit permission:
- Evidence required:
- Optional evidence provider request: CodeGraph if available/useful, or N/A
- Expected return format:
- Phase checkpoint: command | static check | artifact inspection | diff inspection | skipped reason with risk
- Join contract:
- Stop conditions:
```

Guidelines:

- Include exact files, commands, diffs, symptoms, or acceptance criteria needed for the task.
- State whether the subagent may edit, may only inspect, or must ask before edits.
- Forbid nested agent calls; every non-ROSE subagent has `task: deny`.
- Require concrete evidence, not just conclusions.
- For parallel lanes, include the join contract: expected evidence for that lane, conflict or missing-evidence handling, final decision owner, and stop conditions.
- For serial phase packets, include the phase checkpoint that proves the boundary before the next dependent phase starts.
- For multi-lane packets, preserve the lane/package id, owner, editable scope or read-only source, expected evidence, status vocabulary, blocker conditions, and missing/empty-evidence handling so ROSE can join without guessing.
- Ask for graph-assisted evidence only as compact locality anchors; forbid raw graph dumps and final proof claims based solely on graph output.

### Cross-root permission overlay

- Reference one canonical `WT-001` context from `.agents/skills/aili-delivery-flow/references/protocols/worktree-context.md`; never duplicate or rebind its identity, approval, Git, path, dirty-state, command/cwd, soft-boundary, or containment facts.
- Treat `role_overlay` as evidence/narrowing text only, never permission authority. Final effective permissions must come from final runtime-merged child rules and provenance; missing rules, provenance, or override-absence evidence returns `Unverified` and keeps rollout disabled.
- Delegation is non-transitive. Every non-ROSE subagent has `task: deny`; only ROSE uses its unchanged Task allowlist.
- The exact 15 A30 roles may ask for external reads with only `read`, `list`, `glob`, and `grep`; all mutation, shell, delegation, LSP, skill, web, plugin, MCP, custom, and browser tools remain denied. All nonselected roles retain `external_directory: deny`.
- Disclose that external-directory ask/always/auto may broaden private-data reads. No-mutation/no-nesting depends on final effective tool denies, not ask behavior.
- Parent pre/postflight must capture exact session root, parent/target HEAD and dirty state, and Git common-dir and require equality. Do not auto-integrate, commit, merge, rebase, reset, clean, repair, prune, remove, or roll back worktrees.

## Reconciliation and Verification

After subagents return:

1. Compare conclusions against the evidence each subagent supplied.
2. Identify conflicts, duplicated work, missing evidence, and unresolved risks.
3. List every expected lane with status (`completed`, `partial`, `blocked`, `skipped`, or `unverified`) and do not treat missing or empty evidence as completion.
4. Reconcile conflicts and skipped checkpoint risks before integration.
5. Run or request fresh merged-output verification before claiming completion or starting later dependent phases.
6. Decide whether follow-up work is sequential, parallel, or blocked.
7. Summarize findings by work package and separate verified facts from recommendations.

🔴 CHECKPOINT before reconciliation: every accepted conclusion must have evidence anchors and an owner. ROSE owns evidence reconciliation, routing, and final acceptance gates, but must not fabricate, redo, or silently replace subagent-owned edit/review/test work; if ownership must change, get explicit user approval first.

| Reconciliation failure | ROSE action | Stop condition |
|---|---|---|
| Subagents conflict on a fact or recommendation | Read the cited evidence and request one focused follow-up if needed | If evidence remains split, mark `Unverified`; do not claim PASS |
| A result lacks file/line, command, log, or source evidence | Ask for a bounded evidence-only follow-up or exclude the claim | If the claim is required for acceptance, block completion |
| An expected lane returns empty output, no status, or no usable evidence | Keep the lane named in the join report and request focused evidence, mark `partial`/`blocked`/`unverified`, or reassign only with explicit current-task approval | Do not infer completion from file state or adjacent lanes |
| A required reviewer/test/security lane was missed | Dispatch the missing lane before final acceptance | If dispatch is unavailable, report `NEEDS_REVIEW` |
| Parallel edit work produced overlap or ordering ambiguity | Stop new edits; reconcile ownership and verify the combined diff sequentially | If ownership cannot be made safe, block and ask the user |

### Reconciliation Stress Test

After reconciling subagent results, use `strategy-stress-test`.

Check whether:

- any subagent conclusion lacks evidence anchors
- two subagents conflict and the conflict is unresolved
- a high-risk claim depends on stale logs or unverified assumptions
- write-heavy parallel work has overlapping files, shared mutable state, or hidden sequence dependencies
- a missing specialist pass is required, such as security-auditor or test-engineer
- follow-up work must be sequential instead of parallel

Do not treat subagent output as truth. Treat it as evidence to reconcile.

Use `verification-before-completion` before reporting complete, fixed, passing, verified, or ready.
