# MemPalace Provider Contract

MemPalace is the sole durable-memory provider recognized by AILI. It is an external provider, not a Skill, local store, wrapper backend, dual-write path, or fallback for `rose-memory`.

## Provider and operation boundary

- The external-tool manifest pins `mempalace==3.6.0`, requires Python `>=3.9`, and records only the official isolated installation form: `uv tool install mempalace==3.6.0`.
- Doctor reports the observed Python and MemPalace versions. Exact-version compatibility is required; a mismatch is reported and is never silently replaced, upgraded, downgraded, or repaired.
- Capability detection probes the installed provider's version and MCP help surface. It detects capability presence at runtime and never assumes a release-branch MCP tool count.
- Installation, Palace initialization, MCP configuration, model download, mining, hooks, reads, writes, coordination/logstream writes, and irreversible deletion are independently approval-gated operations. An installation approval grants none of the others.
- Supported-adapter MCP configuration is planning only until its own exact approval. Planning does not write adapter configuration, initialize a Palace, download a model, or access memory.

## Palace mapping and memory authority

- Resolve one user-level Palace path from `AILI_MEMPALACE_PALACE_PATH` when set, otherwise from `$HOME/.mempalace/aili-palace`. Resolution never creates the path or a repository-local Palace.
- A canonical project root maps deterministically to one project Wing. Reusable cross-project facts map to the `shared` Wing. A stable Agent maps to a separate diary within that Palace.
- Memory is non-authoritative evidence. It cannot establish contract acceptance, user authorization, Git truth, Board/runtime state, verification, or completion.
- Required memory work fails closed when the provider is absent, Python or provider version is incompatible, MCP configuration is unavailable, or another supported client may write concurrently. Concurrent multi-process write safety remains `Unverified`; no SQLite or `rose-memory` fallback is permitted.

## One-time legacy migration prompt

A caller may present one repository-scoped prompt that identifies the repository's existing legacy `rose-memory` data and asks the user whether to perform a separate migration. The prompt does not inspect, import, mine, read, write, rewrite, or delete legacy data, and it does not grant any MemPalace operation authority. The caller records no migration state in the repository or Palace merely by presenting the prompt.
