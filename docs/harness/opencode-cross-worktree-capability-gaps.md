# OpenCode v1.17.18 cross-worktree capability gaps

## Summary

- Trace ID: [KNOWN] `A30-OPENCODE-STATIC-CROSS-WORKTREE` with deferred `A27-OPENCODE-CROSS-WORKTREE-GAPS`.
- Date: [KNOWN] 2026-07-11.
- Reporter: [KNOWN] AILI DEFINE.
- Status: [KNOWN] A30 static fallback is implemented and its static validation passed; provider-backed runtime proof exits `3` as `Unverified` and remains disabled. No OpenCode fork is included in this report.
- Observed failure or rationale: [KNOWN] OpenCode v1.17.18 can create a target-root instance through `opencode run --dir`, but built-in Task cannot atomically select a different child root and apply an exact task permission overlay tied to an approved target identity.
- Primary affected component: [KNOWN] OpenCode Task/subagent session creation and permission composition.
- Secondary components: [KNOWN] instance context, external-directory checks, shell permission scanning/execution, CLI noninteractive approval, events/results, and cancellation.
- Root cause hypothesis: [INFERRED] target identity, child instance creation, permission composition, and task audit/process lifecycle are separate mechanisms without one native cross-worktree Task contract.
- Proposed change: [FRAME] **PROPOSAL:** add explicit Task target/context/permission/audit fields and native fail-closed composition semantics described below.
- Predicted fix: [INFERRED] a native atomic contract would remove AILI's need to create a separate temporary-config `opencode run --dir` worker for role-preserving target-root tasks.
- At-risk regression: [INFERRED] changing Task session creation or permission ordering could broaden existing subagents, break same-root Task behavior, or alter approval lifetime.
- Verification trigger: [FRAME] **PROPOSAL:** run the upstream acceptance suite in this report against an exact built OpenCode revision, then run AILI's future temporary-only C-OPENCODE-WORKER contract/runtime matrix before changing the fallback.
- Rollback plan: [FRAME] **PROPOSAL:** disable the new native target fields behind a capability/version gate, retain existing same-root Task behavior, and keep or restore AILI's separate-worker fallback; do not remove/prune external worktrees.
- Unknowns: [UNVERIFIED] upstream maintainers' preferred API shape, compatibility policy, Windows process-tree guarantees, and whether a stable plugin-independent task audit event schema is planned.
- Approval status: [KNOWN] A30 supersedes the unaccepted A27/A28/A29 implementation plan, and its static implementation has passed its gate rather than remaining pending acceptance. The future fork proposal remains unapproved and deferred.
- Application status: [KNOWN] A30 static role/config validation is applied; provider-backed runtime enablement and the future fork are not applied.
- Verification result: [KNOWN] A30 static validation passed; the runtime probe exits `3` because final child permission provenance and override-absence evidence are unavailable. No fork test was run.
- Final verdict: [KNOWN] A30 runtime use remains fail-closed and disabled; the future fork design remains `needs-review`.
- Memory/evidence pointer: [KNOWN] OpenSpec change `complete-aili-workflow-orchestration`, decision A27, OQ-005, and the URLs below.

## Evidence base and current v1.17.18 behavior

[KNOWN] Versioned source authority is tag `v1.17.18`: <https://github.com/anomalyco/opencode/tree/v1.17.18>. Official/source anchors used by the fallback contract are: run flags, stdin prompt handling, `--format json`, and session creation in <https://github.com/anomalyco/opencode/blob/v1.17.18/packages/opencode/src/cli/cmd/run.ts>; CLI reference <https://opencode.ai/docs/cli/#run-1>; config and `OPENCODE_CONFIG_CONTENT` loading <https://github.com/anomalyco/opencode/blob/v1.17.18/packages/opencode/src/config/config.ts> and <https://opencode.ai/docs/config/>; agent configuration <https://opencode.ai/docs/agents/>; session/event source <https://github.com/anomalyco/opencode/tree/v1.17.18/packages/opencode/src/session>; permissions <https://opencode.ai/docs/permissions/>; and provider/auth configuration <https://opencode.ai/docs/providers/>. [KNOWN] Version-specific claims remain anchored to tag source where current docs may move.

| Area | Current v1.17.18 evidence | Consequence |
|---|---|---|
| Task input | [KNOWN] `packages/opencode/src/tool/task.ts` defines `description`, `prompt`, `subagent_type`, optional `task_id`, optional `command`, and optional background state, with no directory/worktree, permission overlay, or approval-reference field: <https://github.com/anomalyco/opencode/blob/v1.17.18/packages/opencode/src/tool/task.ts> | [INFERRED] A Task packet cannot natively request an atomic target-root child context. |
| Child session permissions | [KNOWN] `deriveSubagentSessionPermission` derives child rules from parent/session and role state, while final session tools merge agent and session permissions: <https://github.com/anomalyco/opencode/blob/v1.17.18/packages/opencode/src/agent/subagent-permissions.ts> and <https://github.com/anomalyco/opencode/blob/v1.17.18/packages/opencode/src/session/tools.ts> | [INFERRED] Parent/session edit/bash/task `always` or allow state cannot be treated as fresh A30 evidence; A30 must inspect final child rules/provenance and block any override. |
| Tool permission merge | [KNOWN] session tools call `Permission.merge(input.agent.permission, input.session.permission)` before asking: <https://github.com/anomalyco/opencode/blob/v1.17.18/packages/opencode/src/session/tools.ts> | [INFERRED] effective behavior depends on ordered rules emitted by multiple sources. |
| Rule evaluator | [KNOWN] `evaluate` flattens rulesets and selects the last matching rule; `merge` concatenates: <https://github.com/anomalyco/opencode/blob/v1.17.18/packages/opencode/src/permission/index.ts> | [KNOWN] “deny wins” is not a general evaluator invariant; a later matching allow can win. |
| MCP visibility | [KNOWN] the tool registry filters MCP tools through `Permission.visibleTools` using the same merged ruleset: <https://github.com/anomalyco/opencode/blob/v1.17.18/packages/opencode/src/tool/registry.ts> | [INFERRED] runtime proof must inventory MCP visibility after the final merge rather than infer it from agent frontmatter. |
| Instance boundary | [KNOWN] instance context has `directory`, `worktree`, and project; containment accepts paths under directory or worktree: <https://github.com/anomalyco/opencode/blob/v1.17.18/packages/opencode/src/project/instance-context.ts> | [INFERRED] a native child target requires a new child instance/context, not packet metadata. |
| External directory | [KNOWN] outside-instance paths trigger `external_directory` permission and an always-pattern proposal: <https://github.com/anomalyco/opencode/blob/v1.17.18/packages/opencode/src/tool/external-directory.ts> | [KNOWN] this grants workspace crossing; it is not target identity, worktree approval, or containment. |
| Supported separate root | [KNOWN] `opencode run --dir` resolves/chdirs to the target and creates/uses an instance for that directory: <https://github.com/anomalyco/opencode/blob/v1.17.18/packages/opencode/src/cli/cmd/run.ts> | [INFERRED] a separate process is the supported AILI fallback for a native target-root instance. |
| Project-source suppression | [KNOWN] `OPENCODE_DISABLE_PROJECT_CONFIG=1` is parsed as truthy in core `flag.ts`; `config/config.ts` skips project `opencode.json[c]`, `config/paths.ts` omits project `.opencode` directories, and `session/instruction.ts` skips project `AGENTS.md`/`CLAUDE.md`/`CONTEXT.md` system discovery when true: <https://github.com/anomalyco/opencode/blob/v1.17.18/packages/core/src/flag/flag.ts>, <https://github.com/anomalyco/opencode/blob/v1.17.18/packages/opencode/src/config/config.ts>, <https://github.com/anomalyco/opencode/blob/v1.17.18/packages/opencode/src/config/paths.ts>, and <https://github.com/anomalyco/opencode/blob/v1.17.18/packages/opencode/src/session/instruction.ts> | [KNOWN] AILI can retain tracked target instructions/config while requiring runtime evidence that each detected source was suppressed; any unexpectedly loaded source blocks. |
| Noninteractive approval | [KNOWN] `run.ts` auto-rejects asked permissions by default and replies `once` when `--auto` is enabled: <https://github.com/anomalyco/opencode/blob/v1.17.18/packages/opencode/src/cli/cmd/run.ts> | [INFERRED] Auto can broaden external-read privacy. A30 isolated fixtures use no auto flag; observable override state blocks, while unavailable detection remains `Unverified` rather than claimed absent. |
| Always lifetime | [KNOWN] permission replies append always rules to instance permission state, while official docs describe always as lasting for the current OpenCode session: <https://github.com/anomalyco/opencode/blob/v1.17.18/packages/opencode/src/permission/index.ts> | [INFERRED] External-directory always can broaden reads and expose data. It is not mutation authority only when the final effective child profile still denies all mutation/delegation tools. |
| Shell behavior | [KNOWN] shell parses command text for permission patterns and selected path-bearing commands, then executes through a platform shell; timeout/abort kills the spawned handle with a force-kill delay: <https://github.com/anomalyco/opencode/blob/v1.17.18/packages/opencode/src/tool/shell.ts> | [INFERRED] pattern/path scanning is not a complete shell sandbox, and process-tree/effect containment requires dedicated tests. |
| Task cancellation/result | [KNOWN] Task cancellation calls child session cancellation and Task output is rendered as task text/metadata rather than a target-root audit/effect schema: <https://github.com/anomalyco/opencode/blob/v1.17.18/packages/opencode/src/tool/task.ts> | [INFERRED] target identity, changed paths, process cleanup, and neighboring-root effects are not native Task result fields. |

## Missing native Task fields

[KNOWN] v1.17.18 Task lacks these native fields:

1. [KNOWN] `directory` or `worktree` selecting and validating the child instance root.
2. [KNOWN] an atomic task permission overlay with explicit composition mode and a machine-readable effective-rule result.
3. [KNOWN] exact canonical target identity, repository/worktree identity, and an approval reference that can be revalidated before tools run.
4. [KNOWN] explicit no-nesting policy, network policy, output/time bounds, effect inventory, and structured postflight result fields.
5. [KNOWN] a native per-Task directory plus atomic permission/config overlay that cannot be broadened by ambient project/user/managed configuration.
6. [KNOWN] provider credential handles and enforceable per-Task egress policy instead of inheriting raw provider tokens/environment/network reachability.
7. [KNOWN] machine-readable configuration provenance and the compiled effective agent/tool/plugin/MCP/instruction profile.
8. [KNOWN] process isolation/lifecycle evidence covering process groups, survivors, late writes/events, and platform-specific termination guarantees.
9. [KNOWN] an edit transaction with bounded changed-path inventory, atomic commit/abort semantics, and rollback that does not rely on shell/Git cleanup.
10. [KNOWN] parent-verifiable audit receipts binding target, approval, effective config/permissions, provider/network policy, tool effects, edits, process outcome, and postflight without trusting prompt/model output.

## Desired permission composition semantics

[FRAME] **PROPOSAL:** Add a typed composition mode such as `permissionMode: "intersect"` with inputs `parent`, `role`, and `task`. For each permission/pattern/action, any deny from any layer should remain deny; allow should require every applicable layer to permit the action; absent/ambiguous rules should resolve deny for target-root tasks. The runtime should return the compiled effective rules and provenance for audit before the first tool call.

[KNOWN] This proposal cannot be emulated by merely concatenating v1.17.18 rules: the current evaluator uses the last matching rule. [INFERRED] Any compatibility implementation that compiles intersection into ordered rules must prove that no later wildcard/specific allow overrides a deny and must preserve existing non-target Task semantics.

## Child-session root, context, inheritance, and nesting

[FRAME] **PROPOSAL:** A Task request should optionally create a child `InstanceContext` from a canonical target rather than inheriting the parent's instance. Creation should bind the child session to canonical realpath, repository/worktree common-dir identity, HEAD/branch state, and an approval reference before prompt/tool resolution.

[FRAME] **PROPOSAL:** Parent model/provider selection and redacted task input may be inherited only when explicitly selected. Parent transcript, permission approvals, plugins, credentials, MCP servers, environment, and external-directory grants should not implicitly cross into a target-root child. `nestedDelegation: "deny"` should be enforceable at session creation and included in the audit result; any future narrow nesting mode should require a new child target/approval check rather than transitive inheritance.

## Path, symlink, TOCTOU, and shell limitations

[KNOWN] Lexical path containment and `external_directory` checks do not by themselves prove repository identity or protect against a symlink/realpath swap between approval and use. [KNOWN] Shell parsing cannot enumerate every effect of a general shell command, called executable, script, interpreter, subprocess, redirect, environment expansion, or same-user process.

[FRAME] **PROPOSAL:** Native target Tasks should canonicalize every target component, reject symlink ambiguity according to an explicit policy, bind repository/worktree identity, and expose a pre-tool revalidation hook using opened handles or platform-safe identity where practical. High-risk write/execute tools should compare current target identity immediately before effect and return a typed TOCTOU failure.

[FRAME] **PROPOSAL:** Shell support for target Tasks should prefer argv/cwd/env process APIs over shell strings, require literal allowlists for hard commands, expose child-process/network policy, and return complete process/effect metadata. [UNVERIFIED] Full same-user containment may still require OS sandboxing beyond OpenCode's permission evaluator.

## Audit, result, cancellation, and approval lifetime

[FRAME] **PROPOSAL:** Emit versioned events and a final result containing `task_id`, parent/child session IDs, canonical target identity, approval reference, requested/compiled permissions with provenance, role, argv/cwd/env policy, tool calls/denials, changed-path inventory, pre/post Git/root/dirty evidence, network/process effects, output truncation, timeout/cancel reason, process-tree termination, cleanup, and unresolved items.

[FRAME] **PROPOSAL:** Cancellation should terminate the complete process tree, wait for bounded cleanup, reject late events/results, and report surviving processes or cleanup failures as blocking. Timeout and parent-session cancellation should use the same idempotent state machine.

[KNOWN] `--auto` changes asks to one-time approval in noninteractive `run`; `always` creates approval state for later matching requests. [FRAME] **PROPOSAL:** Target Task approval references should be independent of `once`/`always`, scoped to exact canonical target plus operation set and task lifetime, and invalidated on root/HEAD/profile mismatch or task termination.

## Proposed upstream API/schema changes

> [FRAME] **PROPOSAL:** Everything in this section is a future upstream design, not current OpenCode behavior.

```ts
type TargetTask = {
  description: string
  prompt: RedactedPromptRef
  subagent_type: string
  target?: {
    directory: string
    repositoryIdentity: string
    worktreeIdentity?: string
    approvalRef: string
    expectedHead?: string
  }
  permission?: {
    mode: "intersect"
    taskRules: PermissionRule[]
    denyOnAsk: true
  }
  inheritance?: {
    transcript: "none" | "redacted-task-only"
    permissions: "intersect"
    approvals: "none"
    plugins: "none"
    environment: "sanitized"
  }
  nestedDelegation?: "deny"
  limits?: { timeoutMs: number; stdoutBytes: number; stderrBytes: number }
  resultSchemaVersion: string
}
```

[FRAME] **PROPOSAL:** Likely source surfaces include:

- [`packages/opencode/src/tool/task.ts`](https://github.com/anomalyco/opencode/blob/v1.17.18/packages/opencode/src/tool/task.ts): Task schema, child target/context creation, cancellation, structured result.
- [`packages/opencode/src/agent/subagent-permissions.ts`](https://github.com/anomalyco/opencode/blob/v1.17.18/packages/opencode/src/agent/subagent-permissions.ts): explicit composition API and provenance.
- [`packages/opencode/src/session/tools.ts`](https://github.com/anomalyco/opencode/blob/v1.17.18/packages/opencode/src/session/tools.ts): compiled effective rules and target-aware tool context.
- [`packages/opencode/src/permission/index.ts`](https://github.com/anomalyco/opencode/blob/v1.17.18/packages/opencode/src/permission/index.ts): evaluator ordering, atomic intersection mode, deny provenance, and approval scope/lifetime.
- [`packages/opencode/src/tool/registry.ts`](https://github.com/anomalyco/opencode/blob/v1.17.18/packages/opencode/src/tool/registry.ts): built-in/custom/plugin/MCP tool inventory and visibility filtering.
- [`packages/opencode/src/session/schema.ts`](https://github.com/anomalyco/opencode/blob/v1.17.18/packages/opencode/src/session/schema.ts): versioned diagnostic event/result schema.
- [`packages/opencode/src/project/instance-context.ts`](https://github.com/anomalyco/opencode/blob/v1.17.18/packages/opencode/src/project/instance-context.ts): child instance creation/binding and identity revalidation.
- [`packages/opencode/src/tool/external-directory.ts`](https://github.com/anomalyco/opencode/blob/v1.17.18/packages/opencode/src/tool/external-directory.ts): distinguish bound target root from an external-directory grant.
- [`packages/opencode/src/tool/shell.ts`](https://github.com/anomalyco/opencode/blob/v1.17.18/packages/opencode/src/tool/shell.ts): argv-capable restricted execution, effect/process-tree evidence, stronger target checks.
- [`packages/opencode/src/cli/cmd/run.ts`](https://github.com/anomalyco/opencode/blob/v1.17.18/packages/opencode/src/cli/cmd/run.ts): reusable noninteractive deny-on-ask semantics, output/result schema, cancellation wiring.

## Threat model

| Threat | Required control/test |
|---|---|
| Wrong parent, neighbor, nested repository, or worktree | [FRAME] **PROPOSAL:** canonical repository/worktree identity plus exact approval reference; reject alias/overlap. |
| Symlink or TOCTOU swap | [FRAME] **PROPOSAL:** pre-create and pre-effect identity checks; swap fixture must block before effect. |
| Permission broadening through rule order | [FRAME] **PROPOSAL:** native intersection compilation/provenance; adversarial wildcard/specific last-match tests. |
| Secret read or output leak | [FRAME] **PROPOSAL:** default deny, secret fixtures, bounded/redacted event and result output. |
| Shell/subprocess/outside-root mutation | [FRAME] **PROPOSAL:** literal argv/cwd policy, no-shell negative cases, process/effect inventory, parent/neighbor byte checks. |
| Network or credential inheritance | [FRAME] **PROPOSAL:** explicit network policy, sanitized environment, no implicit provider/plugin/MCP credential inheritance. |
| Nested delegation/escalation | [FRAME] **PROPOSAL:** session-level no-nesting enforcement and denied Task/worker-spawn tests. |
| `--auto`, ask, or always substitutes for exact approval | [FRAME] **PROPOSAL:** deny-on-ask target mode; approval-reference mismatch and lifetime tests. |
| Timeout/cancel leaves children running | [FRAME] **PROPOSAL:** process-tree fixture with grandchild, bounded termination, late-result rejection, cleanup evidence. |
| Worker claims success despite malformed/missing evidence | [FRAME] **PROPOSAL:** strict result schema and parent-derived changed-path/Git comparison; worker final authority forbidden. |

## Upstream acceptance tests

1. [FRAME] **PROPOSAL:** Same-root Task remains backward compatible when `target` is absent.
2. [FRAME] **PROPOSAL:** A target Task creates a child instance whose reported directory/worktree exactly matches the canonical approved target.
3. [FRAME] **PROPOSAL:** Parent allow + role/task deny and parent/role deny + task allow both remain denied under native intersection, independent of rule order.
4. [FRAME] **PROPOSAL:** Missing, stale, wrong-root, parent-root, neighbor-root, nested-repo, detached/HEAD-mismatch, dirty-policy, symlink, and swap approvals block before a tool effect.
5. [FRAME] **PROPOSAL:** Read-only, exact-edit, and literal-test roles succeed only on approved in-root operations.
6. [FRAME] **PROPOSAL:** Broad read/edit, shell form, substitutions, redirects, subprocess/outside-root writes, fake-secret reads, network-policy violations, and nested Task/worker attempts fail without forbidden mutation.
7. [FRAME] **PROPOSAL:** Noninteractive ask fails; `--auto` and always state cannot satisfy target approval or operation scope.
8. [FRAME] **PROPOSAL:** Parent transcript, approvals, external-directory grants, plugins, environment secrets, and MCP credentials do not implicitly enter the child.
9. [FRAME] **PROPOSAL:** Output limits, timeout, parent cancel, child crash, and malformed result each produce a typed terminal result; process grandchildren are terminated and cleanup is evidenced.
10. [FRAME] **PROPOSAL:** The final audit schema reconciles changed files and pre/post Git/root/dirty state and marks any unexplained neighbor/parent effect blocking.

## Future fork proof of effective Task child permissions

[KNOWN] In v1.17.18, permission rules are ordered and the last matching rule wins; a Task child receives a permission ruleset, final tools merge agent and session rules, and MCP visibility is filtered through the same rules. [KNOWN] The stock runtime does not expose enough final-merge provenance for this gate. [UNVERIFIED] The effective child profile and absence of auto/yolo/skip/global or stored-approval overrides therefore remain unproven. [KNOWN] Black-box observations that no mutation occurred do not prove that unexercised permissions were absent.

### Two-layer gate and isolated fixture

1. [FRAME] **PROPOSAL:** Layer 1 statically validate the installed, resolved agent definitions and reject every missing, reordered, unknown, `allow`, or `ask` rule outside the exact approved inventory. Static success is necessary but can never upgrade or substitute for Layer 2.
2. [FRAME] **PROPOSAL:** Layer 2 run provider-backed Task sessions against the fork and require both the post-merge diagnostic receipt and deterministic tool-call outcomes. The provider must force the complete ordered call matrix; model-selected or skipped calls are invalid evidence.
3. [FRAME] **PROPOSAL:** Each run must bind the exact OpenCode binary version, canonical path, and cryptographic hash; use fresh `HOME`, XDG roots, OpenCode database, and config; use a localhost-only mock provider and fake secret; create a temporary parent repository plus same-repository sibling worktree; and load no user state, plugins, MCP servers, or custom tools unless that source is the explicit case under test.

### Required post-merge diagnostic

[FRAME] **PROPOSAL:** Add a versioned machine-readable event, for example `task.permission_profile.finalized`, emitted synchronously after the final permission/tool merge and before the first tool call becomes dispatchable. The event must include parent and child session IDs, selected agent, ordered permission sources with source identity and rules, compiled/effective rules, visible tool inventory, override and approval mode/state, and every loaded config/plugin/MCP/instruction source with provenance and suppression status. The parent runner must reject a missing, duplicate, late, reordered, internally inconsistent, or unknown-schema event and must reconcile the inventory with built-in, custom, plugin, MCP, and browser tools. [FRAME] **PROPOSAL:** Instrument the tagged v1.17.18 source surfaces linked above: `task.ts`, `subagent-permissions.ts`, `session/tools.ts`, the permission evaluator, `tool/registry.ts`, and `session/schema.ts`; provenance collection must also cover config, plugin, MCP, and instruction loaders.

### Deterministic forced-call and effect matrix

[FRAME] **PROPOSAL:** The localhost provider must force exactly these cases in a declared order, and the runner must treat a missing, extra, or reordered case as exit `5`:

| Forced case | Required result |
|---|---|
| Exact external sentinel read | [FRAME] **PROPOSAL:** one exact scoped `external_directory` ask is parent-approved for the sentinel only, then the child read succeeds and returns the known non-secret bytes. |
| Parent-root and target-root writes | [FRAME] **PROPOSAL:** every write/edit/apply-patch route is denied or unavailable before effect. |
| Bash/shell/execute | [FRAME] **PROPOSAL:** denied or unavailable before process creation. |
| Task nesting or child-of-child creation | [FRAME] **PROPOSAL:** denied or unavailable; no descendant session/event may exist. |
| Unknown, MCP, browser, plugin, and custom tools | [FRAME] **PROPOSAL:** absent from the visible inventory or denied before execution; explicit under-test registrations must still resolve deny. |
| Git refs, hooks, config, and common-dir mutation | [FRAME] **PROPOSAL:** every direct or indirect write route is denied before effect, including `.git` indirection from the sibling worktree. |
| Fake-secret file/environment/config access | [FRAME] **PROPOSAL:** denied or unavailable, and the marker must not occur in provider requests, events, stdout, stderr, or results. |

[FRAME] **PROPOSAL:** The parent—not the child or model—must capture pre/post canonical path, byte/tree, Git HEAD/ref, worktree dirty state, hooks, config, common-dir, process, and session/event snapshots. Passing requires exact no-effects reconciliation outside the approved sentinel read, no child-of-child session, no surviving process or late event, mock-provider shutdown, database/config/HOME removal, sibling-worktree cleanup, and a complete cleanup receipt. Cleanup happens only after evidence capture; cleanup failure is non-pass and retained paths are reported.

### Exit contract and upstream acceptance checklist

- [FRAME] **PROPOSAL:** Exit `0` only when static validation, exact binary/provider identity, complete pre-tool provenance, every forced behavior, parent-owned no-effects snapshots, no-child-of-child evidence, and cleanup all pass.
- [FRAME] **PROPOSAL:** Exit `3` with status `Unverified` when final provenance, override/approval absence, exact binary identity, or provider-backed evidence is unavailable; no mutation observation may lower this to pass.
- [FRAME] **PROPOSAL:** Exit `5` on any rule/inventory/provenance mismatch, forbidden effect, secret disclosure, unsafe rule, missing/extra/reordered forced call, descendant session, survivor/late event, or cleanup failure.
- [FRAME] **PROPOSAL:** A static pass never upgrades an exit `3` or `5` runtime result.

[FRAME] **PROPOSAL:** Upstream acceptance requires: (1) the diagnostic is emitted exactly once after final merge and before tool dispatch; (2) ordered-source replay reproduces compiled/effective rules under last-match semantics; (3) visible built-in/custom/plugin/MCP/browser inventory matches the effective rules; (4) all forced matrix cases and adversarial late-allow/approval/override fixtures produce the specified result; (5) parent-owned snapshots prove no forbidden effect, descendant session, secret leak, survivor, or late event; (6) isolated-state and exact binary/provider receipts are complete; (7) exits are exactly `0`/`3`/`5` as defined above; and (8) same-root Task behavior without the diagnostic test mode remains backward compatible.

## Selected A30 static fallback

[KNOWN] A30 retains OpenCode v1.17.18 built-in Task subagents in the same OpenCode instance/root, supported only when ROSE dispatches Task. Direct user `@` invocation is outside A30 guarantees and must not be presented as safe. It uses static role frontmatter only and does not implement an independent `opencode run --dir` worker now.

[KNOWN] External access is limited to exactly these existing read-only roles: `agent-evaluator`, `ai-regression-scout`, `code-reviewer`, `code-scout`, `convergence-reviewer`, `doc-researcher`, `opensource-sanitizer`, `plan-auditor`, `pr-test-analyzer`, `security-auditor`, `silent-failure-reviewer`, `spec-miner`, `test-coverage-reviewer`, `web-performance-auditor`, and `web-researcher`.

[KNOWN] Every selected role has identical literal effective inventory: top-level/unknown/default `*`: deny; only `read`, `list`, `glob`, and `grep`: allow; only `external_directory`: ask; explicit `edit`, `bash`, `task`, `lsp`, `skill`, `webfetch`, `websearch`, and every enumerated plugin/MCP/custom/browser/other final merged tool: deny. Nested read-pattern denials may narrow reads. No other merged key may resolve allow/ask; Git-administrative read denial is optional defense-in-depth.

[KNOWN] `implementer`, ROSE, `browser-qa-runner`, `debug-investigator`, `e2e-artifact-runner`, `test-engineer`, and every other edit- or command-capable role retain `external_directory: deny`. A30 supplies no external edit, exact task-path edit, test/debug/browser/e2e, shell, or Git-command capability.

[KNOWN] A30 does not claim technical detection of auto/yolo/skip/global tool override or stored approval state when runtime does not expose it. Observable override state, `external_directory: allow`, or effective child edit/bash/task allow blocks; inability to prove absence leaves runtime `Unverified` and disabled. Isolated fixtures use no such flags. Auto/always may broaden external-read privacy and expose data.

[KNOWN] Deny-by-default effective child rules are primary prevention; ask behavior is not. Parent/session edit/bash/task `always` or allow state is not fresh A30 evidence. Runtime seeds each in isolation, inspects source-anchored derivation plus final merged child rules/provenance, and blocks any override. If effective rules cannot be exposed, runtime remains `Unverified`/disabled. External-directory always broadens reads only and is not mutation authority while all mutation/delegation tools remain effectively denied. Lexical Git rules and Git-administrative read denials are optional defense-in-depth; parent pre/postflight is evidence.

[KNOWN] Implementation ownership is the selected role frontmatters, worktree/task/result/dispatch protocols, `scripts/delegation_protocols_check.py`, `docs/harness/fixtures/cross-worktree-permission-fixtures.yaml`, `scripts/opencode_permission_probe.mjs`, and `tests/opencode-permission-probe.test.mjs`. The exact runtime command is `node scripts/opencode_permission_probe.mjs --project . --opencode-version 1.17.18 --fixture docs/harness/fixtures/cross-worktree-permission-fixtures.yaml --mode a30-same-instance-readonly --provider local-mock --json`. It creates only a temporary repository/sibling worktree and isolated OpenCode home, captures evidence before cleanup, uses no real user state or auto/yolo/skip flags, and covers final merged inventory, unexpected tool, direct invocation exclusion, isolated seeded edit/bash/task parent state, external-always read broadening, auto privacy caveat, mutation-capable effective-rule block, read positive, and unchanged parent/target/common-dir state.

## Deferred A27 independent-worker fallback and future fork

[KNOWN] The remainder of this section records the superseded A27/A28/A29 independent-worker plan as deferred future design only. It is not current implementation authority. Static A30 is weaker because it does not rebind the child instance root, provide atomic per-task permission intersection, prevent user-created always state, or create OS/process containment and native audit receipts. The upstream native Task fields, threat model, and acceptance tests above remain valid future fork requirements.

[KNOWN] A27 selects a separate bounded process; A28/A29 limit the current fallback claim to Linux/WSL read+edit on one pre-created explicitly approved task-owned disposable same-repository sibling worktree, using real OpenCode v1.17.18 with a deterministic parent-owned localhost mock provider and fake token. [KNOWN] Exact future Package-6 sources are launcher `scripts/opencode_worktree_worker.py`, narrow source-repository/harness-owned supply-chain manifest `manifests/opencode-worker-runtime.json`, and dedicated fixture driver `tests/test_opencode_worktree_worker.py`; the old permission probe is historical evidence only. [KNOWN] The worker manifest is not baseline-manifest, general lifecycle artifact-integrity, or digest/receipt approval machinery.

[KNOWN] The launcher will pass literal argv `opencode run --dir <target> --agent <unique-primary> --model <local-mock-provider/model> --format json`, stream one bounded UTF-8 prompt on stdin, use fresh HOME/XDG roots plus `OPENCODE_DB=:memory:` and deny-default `OPENCODE_CONFIG_CONTENT`, and parse only v1.17.18 `run.ts` emitted NDJSON record types `tool_use`, `step_start`, `step_finish`, `text`, `reasoning`, and `error`. Thinking remains disabled so reasoning is unexpected; error blocks success; no terminal done event is emitted or required. Typed approval remains parent-owned and separate from prompt/output.

[KNOWN] Ephemeral ROSE-owned approval has `execute_authorized` false by default/absence and true only for the exact current target/source/common-dir/HEAD/role/actions/paths/expiry/decision reference plus `runtime_record_id`, canonical source-manifest path/hash, current operation/host binding, exact canonical OpenCode path/hash and verified package record, and duplicate-free `trusted_helpers[]` exact name/path/hash/version/provenance-oracle records; it is the sole enable control and has no persisted/global counterpart. Execute resolves records only through the canonical approved-source-root manifest plus this descriptor, with no target/inherited-environment/prompt/model/candidate-metadata authority and no new CLI secret/path override. The launcher validates then closes the approval FD before starting OpenCode with `close_fds=True`; approval, sentinel, and unrelated descriptors must be invisible to the child.

[KNOWN] The child environment is built from an explicit minimal executable/runtime/locale/XDG/TMP/mock-provider/OpenCode-config allowlist, never copied then sanitized, and includes `OPENCODE_DISABLE_PROJECT_CONFIG=1`. Loaded-source evidence uses exactly `absent | detected-and-suppressed | unexpectedly-loaded`; unexpected load blocks. The positive runtime retains tracked target `AGENTS.md`, project `opencode.json`, and project `.opencode`, proves them detected-and-suppressed, then completes approved read/edit. Cloud/Git/npm/SSH/proxy/askpass/`NODE_OPTIONS`/`LD_*`/`PYTHON*`/runtime-hook/socket variables are rejected/omitted and tested with parent-observed canaries.

[KNOWN] PATH is not inherited. Linux/WSL candidates are exactly `/usr/bin` and `/bin`, canonicalized and deduplicated; WSL Windows interop/mounted paths, user/current directories, empty/relative entries, and every inherited entry are forbidden. Each admitted directory and complete symlink/component chain must be UID-0-owned, have no group/other write bit, and be non-writable by the non-root current user; launcher execution as UID 0 blocks, and links may resolve only within the admitted canonical set. Main OpenCode is invoked by the descriptor-bound absolute verified realpath. `git` and every fixture-proven required runtime helper are resolved only from the fixed path and must have exactly one approval record. Supported helper oracle classes are closed to native Linux/WSL `dpkg-root-db-v1` using root-owned/non-user-writable `/var/lib/dpkg` plus `/var/lib/dpkg/info` ownership/version/file-integrity evidence, and `rpm-root-db-v1` using root-owned/non-user-writable `/usr/lib/sysimage/rpm` or `/var/lib/rpm` ownership/version/digest/signature/file-verification evidence. Missing integrity metadata, ambiguity, failed verification, or absence of a trusted host oracle blocks; WSL Windows/user/target databases, PATH/version-only output, ad hoc allowlists, and runtime-observed candidate bytes cannot create trust. Fake Git, duplicate/unexpected helper, untrusted inherited PATH, symlink escape, writable component, unresolved/unapproved/no-oracle/changed helper, or fallback resolution blocks before spawn.

[KNOWN] `manifests/opencode-worker-runtime.json`, read only from its canonical approved source root, immutably owns package `opencode-ai`, version `1.17.18`, official npm dist integrity `sha512-gpCE5X3dwvYam2ba9r3mw+FTPBTDlmKkguiOoYF1nv9MVA3sDIXje3tPQ+EMNxYkWD43FN3+eVC1GW6tRO9Aiw==`, canonical tarball identity `https://registry.npmjs.org/opencode-ai/-/opencode-ai-1.17.18.tgz`, bin mapping `opencode` → `bin/opencode.exe`, and allowed helper oracle method identifiers. The fixture driver independently obtains/verifies official npm artifact evidence and validates the manifest; production execute refuses missing/mismatched/stale-hash manifest. Installed package/bin bytes are compared to the verified artifact and approval-bound exact path/hash/package record, every canonical realpath component is checked, and manifest/path/hash/package/helper comparisons rerun immediately before spawn to catch substitution. Alternate digest substitution, path/version-only trust, and candidate self-attestation are forbidden; unavailable provenance exits `3`, unsafe mismatch exits `5`.

[KNOWN] The dedicated stdlib driver creates a fully temporary repository plus sibling worktree, deterministic loopback mock provider, and typed approval pipe/FD; independently obtains/verifies official npm artifact evidence; validates the source manifest; invokes launcher/runtime directly; verifies detected-and-suppressed tracked project sources, the separate unexpectedly-loaded block, loaded-helper/oracle evidence, fake-Git/untrusted-PATH/helper-symlink/writable-component/unresolved-helper negatives, negative child-FD visibility, and environment canaries; and only after complete evidence capture cleans driver-owned fixture resources. Exact provenance cases are valid record, missing manifest, forged integrity, wrong operation/host/path, stale manifest hash, duplicate helper, unexpected helper, target-manifest shadow, candidate self-record, and substitution after preflight; every negative blocks before spawn. Cleanup failure is non-pass and retained artifacts are reported.

[KNOWN] The launcher MUST NOT automatically create/delete/reset/clean/prune/repair source or target worktrees, revert source, or integrate failed edits. Its exact result splits `source_cleanup:false`, `target_cleanup:false`, `private_runtime_cleanup`, `mock_server_cleanup`, and `fixture_cleanup`. Failed real-operation changes remain in the disposable target for inspection; only the runtime driver may remove its own temporary source/target/private fixtures after evidence capture. [KNOWN] It makes no OS-sandbox, general network-isolation, arbitrary-daemon, or race-free path claim; symlink/TOCTOU results are observed-path evidence and block when exact safety cannot be proven.

[KNOWN] This fallback proves only the selected read+edit/mock-provider mode. Test/Bash/debug execution, production provider/auth, provider credential handles, enforceable general egress policy, cross-platform support, native config provenance, process isolation, transactional edit/rollback, and native audit receipts remain future gaps.

[INFERRED] A plugin or hook is not selected now because it would add mutable runtime code inside the trust boundary, would not by itself supply atomic root/approval/permission semantics, and conflicts with the requirement to avoid plugin/global mutation when exact noninteractive behavior is uncertain. [INFERRED] The separate process is easier to bound, kill, clean, and audit using supported CLI behavior, while remaining fail-closed if temporary profile loading or permission answers cannot be proven.

## AILI verification trigger and rollback

- Verification status: [KNOWN] C-OPENCODE-A30-STATIC is implemented and passed. C-OPENCODE-A30-RUNTIME is implemented as a fail-closed probe and exits `3`/`Unverified` because stock v1.17.18 does not expose final child rule provenance or override absence; runtime rollout is disabled.
- Required evidence: [KNOWN] exact 15-role deny-by-default merged inventory; unexpected-tool denial; ROSE Task-only/direct-`@` exclusion; isolated seeded parent/session edit/bash/task states; external-always/auto privacy disclosure; mutation-capable effective-rule block; external read positive; unchanged snapshots; no real user state; exact JSON schema/exits/cleanup. Static evidence alone is insufficient.
- Stop condition: [KNOWN] any unexpected allow/ask, direct-invocation safety claim, observable override, mutation-capable child rule, unexposed effective rules/provenance or override absence, snapshot/schema/cleanup gap, or nonzero exit blocks rollout. Exit `3` is `Unverified`/disabled, not a no-mutation result.
- Rollback: [KNOWN] restore `external_directory: deny` on the selected roles. Do not mutate, remove, prune, clean, repair, reset, revert, or integrate a source/target worktree.
- Remaining risks: [UNVERIFIED] auto/always may broaden external-read privacy; override absence and effective child rules remain unobservable in stock v1.17.18. Until provider-backed proof passes, no runtime no-mutation claim is allowed. Cross-worktree edit/test, target-root rebinding, independent/native isolation, production provider/auth, and OS/process containment remain future scope.
- Next action: [FRAME] **PROPOSAL:** implement the post-merge diagnostic and provider-backed acceptance gate in the future OpenCode fork; keep A30 runtime disabled until that gate exits `0`. Independent/native edit/test still requires separate A27/fork scope and approval.
