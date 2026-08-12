# aili-pi runtime implementation handoff

## Status and immutable upstream input

This document is the implementation contract for a separate change in `aili-pi`. It does not prove that `aili-pi`, Pi, MCP, or MemPalace has changed.

Consume the released workflow bundle only after all immutable release fields are verified:

- package: `rose-aili@0.4.7` (target; not yet released while this document is authored);
- Git tag: `v0.4.7` (pending release);
- release commit: **Unverified until the tag exists**;
- npm `gitHead`: **Unverified until publication**.

Before downstream implementation, resolve the tag commit and run:

```bash
npm view rose-aili@0.4.7 version gitHead dist.tarball --json
```

The tag commit, npm `gitHead`, and downloaded package must agree. Do not substitute the current working tree, an archived chat, an unpinned branch, or an earlier package version.

## Current evidence boundary

The workflow repository currently defines the Pi projection in `adapters/pi/adapter.json`, generates it through `scripts/generate-runtime-projections.mjs`, and installs the public context/prompt subset through the `pi` profile. The accepted workflow bundle contains:

- `generated/pi/AGENTS.md` — installed global Pi context;
- `generated/pi/prompts/*.md` — installed non-recursive top-level prompts;
- `generated/pi/system.md` — package-only system projection;
- `generated/pi/role-metadata.json` — package-only canonical role metadata;
- `generated/pi/selection-map.json` — package-only selector mapping;
- `generated/pi/protocols/*.json` — package-only package, selection, and Board schemas;
- `generated/pi/installation-contract.json` and `generated/pi/provenance.json` — package-only installation/provenance evidence.

`aili-pi` consumes the package-only runtime bundle; it must not maintain a competing copy of workflow semantics or reinstall/own `~/.pi/agent/AGENTS.md`. The DEFINE evidence used public `aili-pi` main commit `18242f7b2b26a18bd3a0c0ae2e83df8294b9d529` as its static baseline, especially its persistent-Agent runtime, Matrix extension, and Zentui thinking/tool rendering. Treat that commit as a historical navigation anchor, not the implementation target: before editing, resolve the current intended downstream commit and re-inspect exact files, APIs, dependencies, tests, and runtime behavior. Any difference that changes the accepted architecture or verification strategy returns to the downstream definition/approval owner rather than being guessed through.

## Required implementation packages

### 1. Pin and load the generated bundle

- Pin exactly `rose-aili@0.4.7` plus its verified tag commit/npm `gitHead`.
- Load system, roles, selector map, protocols, prompts, installation contract, and provenance from the package.
- Validate required schema/provenance versions and fail closed on missing, stale, incompatible, or mixed-version artifacts.
- Keep runtime-private Agent/job/session IDs adapter-owned; they never replace canonical package identity, the formal Board, accepted task IDs, repository evidence, approvals, or ROSE disposition.

Acceptance:

- one immutable workflow bundle supplies all workflow semantics;
- no copied selector/role/protocol table becomes a second authority;
- incompatible or incomplete bundles produce an explicit non-success result.

### 2. Integrate maintained generic MCP transport

Use a maintained MCP adapter rather than implementing the protocol. Before selecting or coding against it, freshly verify its current version, license, supported Pi/runtime version, `configPath` API, configuration schema, lifecycle, error propagation, and permission behavior.

Shared MCP configuration belongs under:

```text
$XDG_CONFIG_HOME/opencode/
# default: ~/.config/opencode/
```

Use a separate shared file, recommended as `mcp.json`, only if the verified adapter supports that filename and schema. Do not create a second MCP configuration under `~/.pi/agent/`, and do not rewrite user-owned `opencode.json` or `opencode.jsonc` merely to configure Pi.

Every MCP tool call remains subject to the effective intersection of parent grant, canonical role ceiling, runtime/provider capability, repository policy, and package restrictions. Missing capabilities must be visible and fail closed; MCP transport does not broaden permission or authorize credentials/network access.

Acceptance:

- Parent and Worker sessions receive the same generic MCP transport under their effective permissions;
- adapter failures and unavailable tools remain explicit blockers/unavailable results;
- secrets, full prompts, raw environment variables, and unbounded tool output are not surfaced.

### 3. Connect MemPalace only through MCP

MemPalace is the only durable-memory provider. Connect it through the generic MCP transport; do not add an AILI-owned memory database, schema, SQLite fallback, automatic transcript mining, or direct provider-specific runtime path.

Pi `AgentSession` and conversation history remain hot runtime context, not durable semantic memory, acceptance evidence, or correctness evidence. If MemPalace or compatible MCP configuration is unavailable, memory-dependent behavior must fail closed or report unavailable while ordinary task/session execution may continue without claiming durable memory.

Acceptance:

- Parent and Worker memory access uses the same generic MCP boundary;
- provider absence never silently falls back or reports memory continuity;
- no transcript is mined or persisted without the provider's separately authorized operation.

### 4. Make task execution visibly attributable

Replace generic active task presentation with bounded task-specific rendering that shows:

- canonical Agent selector and human role title;
- redacted, length-limited assignment summary;
- sync/async mode and current status;
- allocated Agent/job identity once available;
- terminal state and `agent://` / `history://` references.

Keep `hub` as the detailed inspection/control surface. Do not display full prompts, credentials, secrets, raw arguments, or unbounded output. Rendering is presentation only and cannot become completion or acceptance evidence.

Acceptance:

- while a task runs, users can identify the selected Agent and bounded assignment;
- terminal presentation links to detailed output/history;
- task failure, malformed result, cancellation, and blocked state remain distinguishable.

### 5. Restore Pi-native working/thinking UI

Remove the complete custom Matrix active-working surface: the upper shimmer/status row and all four waterfall rows. Stop hiding or replacing Pi's native working indicator. Remove any custom in-progress thinking animation that replaces native Pi presentation.

Static styling of completed reasoning may remain only if it does not patch, hide, or replace Pi's active animation.

Acceptance:

- while Parent or Worker reasoning/tool execution is active, Pi's native working/thinking animation is the only active animation;
- no upper shimmer/status or waterfall animation renders;
- completed output remains readable without altering native in-progress behavior.

### 6. Add downstream doctor and diagnostics

Add non-repairing diagnostics for:

- exact pinned workflow package/tag/npm provenance;
- bundle presence, schema compatibility, and provenance consistency;
- selected MCP adapter/version and supported configuration path/schema;
- shared configuration location and parse status without exposing secrets;
- MemPalace availability through generic MCP;
- task-rendering integration and native-UI override state.

Doctor must report missing, incompatible, drifted, or unavailable states as non-pass without silently installing, migrating, rewriting, or repairing them.

## Migration

If an older Pi-only MCP file exists, migration is preview-first and non-destructive:

1. report exact source and proposed shared destination;
2. inventory both files without printing credentials;
3. explain merge/conflict and backup behavior;
4. obtain the required operation approvals;
5. preserve conflicting source and destination content;
6. never silently move credentials or overwrite `opencode.json`/`opencode.jsonc`.

Legacy memory/session data is not automatically interpreted as MemPalace semantic memory. Do not delete, rewrite, import, or mine it without a separately accepted migration contract and exact operation approval.

## Verification matrix

Run against the pinned `aili-pi` baseline and record exact commands/files:

1. **Bundle tests:** correct package loads; missing/mixed/stale schema or provenance fails closed.
2. **MCP configuration tests:** XDG/default path resolution, supported `configPath`, valid/invalid schema, absent adapter, provider failure, and redacted diagnostics.
3. **Migration tests:** no-source, source-only, destination-only, identical, conflicting, credential-bearing, dry-run, backup, and denial cases.
4. **MemPalace tests:** available/unavailable provider, Parent/Worker parity, no fallback database, and no false durable-memory claim.
5. **Task presentation tests:** selector/title/summary/mode/status/identity/references, length limits, redaction, malformed result, cancellation, and async terminal state.
6. **Native UI tests:** Parent reasoning, Worker reasoning, and tool execution show only Pi-native active animation; no shimmer/status/waterfall rows remain.
7. **Doctor tests:** package provenance, bundle drift, MCP config/adapter, MemPalace availability, rendering integration, and no-repair behavior.
8. **Integration test:** one bounded sync task and one bounded async task traverse selection, execution, hub inspection, result validation, and terminal presentation without treating presentation/session metadata as formal evidence.

Static repository tests do not prove live provider behavior, credential safety, Pi UI fidelity, park/revive persistence, hard isolation, or memory continuity. Preserve those claims as **Unverified** until observed in the exact target runtime.

## Release gates for aili-pi

Before release:

- all version-sensitive MCP and Pi APIs have fresh official/source evidence;
- the exact workflow bundle is immutable and provenance-checked;
- migration remains preview-first and non-destructive;
- focused and aggregate downstream checks pass;
- package contents and user-facing migration/reload notes are inspected;
- commit, push, tag, publish, and release each receive their own exact approval;
- CI and published package metadata are inspected before success is claimed.

CI failure stops the release and reports the exact target commit/tag/job. Do not auto-repair, retag, republish, or fall back to a local manual publish.

## Forbidden scope

- Do not edit or release `aili-workflow` from the downstream change.
- Do not replace Pi's system prompt, native TUI, session storage, settings, or package manager beyond the accepted integration points.
- Do not install MCP packages, configure servers, move credentials, initialize/write MemPalace, or mutate user-home data without the applicable exact approvals.
- Do not create competing workflow semantics, a memory database/fallback, hidden background work, scheduler, daemon, watcher, or automatic retry.
- Do not claim OpenCode equivalence, hard isolation, durable memory, UI correctness, or released provenance without fresh target evidence.
