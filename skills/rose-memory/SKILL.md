---
name: rose-memory
description: Use the ROSE project-local SQLite memory system through the bundled memory_cli.py. Use this for task checkpoints, durable findings, state transitions, retrieval packs, and writeback receipts.
license: MIT
compatibility: opencode
metadata:
  tool: references/memory_cli.py
  state: project-local memory/memory.db
---

# ROSE Memory

## Purpose

This skill provides the ROSE memory protocol and the bundled SQLite CLI used by ROSE agents.

The CLI implementation is distributed with this skill:

`~/.config/opencode/skills/rose-memory/references/memory_cli.py`

The memory database is always project-local:

`memory/memory.db`

Never store project memory inside the global OpenCode config directory.

## When to Use

Use this skill when:

- starting or resuming a ROSE task
- checking current ROSE memory status
- recording task checkpoints or completion receipts
- recording durable project facts, findings, claims, or evidence
- retrieving project memory context after compaction or explicit resume
- recovering from interrupted work

## Rules

- Never edit `memory/memory.db` manually.
- Never create `memory.md`, JSON sidecars, or alternate memory state files.
- Never store project state under `~/.config/opencode/`.
- Always use the `rose-memory` shim when available, otherwise use the bundled `memory_cli.py` directly.
- Durable memory must have evidence or an explicit no-promotion receipt.
- If the current directory is not inside a project, stop and report `SETUP_BLOCKED_NO_PROJECT_ROOT`.

## Command

If a short shim exists, use it:

```bash
rose-memory --help
```

If the shim is unavailable, call the bundled tool directly:

```bash
python ~/.config/opencode/skills/rose-memory/references/memory_cli.py --help
```

Windows PowerShell fallback:

```powershell
python "$env:USERPROFILE\.config\opencode\skills\rose-memory\references\memory_cli.py" --help
```

For every example below, replace `rose-memory` with `python ~/.config/opencode/skills/rose-memory/references/memory_cli.py` when no shim exists.

## Standard Operations

Initialize project memory:

```bash
mkdir -p memory
rose-memory init --db memory/memory.db
```

Check health:

```bash
rose-memory doctor --db memory/memory.db --record
```

Start a session:

```bash
rose-memory session start --db memory/memory.db --session-key "<session-key>"
```

Start a task:

```bash
rose-memory task start --db memory/memory.db --session-key "<session-key>" --title "<task summary>"
```

Record an event checkpoint:

```bash
rose-memory event add --db memory/memory.db --event-type CHECKPOINT --state ACTIVE --summary "<summary>"
```

Retrieve memory context:

```bash
rose-memory pack --db memory/memory.db "<query>" --mode direct --budget 800
rose-memory search --db memory/memory.db "<query>" --limit 10
```

Complete a task with no durable memory promoted:

```bash
rose-memory complete --db memory/memory.db --summary "<completion summary>" --no-durable-memory-promoted
```

## Success Signal

A memory write succeeds only when the CLI returns JSON containing:

- `ok: true`
- `receipt_id`
- `result` with the operation-specific payload

If the receipt is missing, treat the operation as failed and do not claim writeback completion.

## References

- `references/memory_cli.py` - executable memory CLI
- `references/schema.sql` - current SQLite schema emitted by the CLI
- `references/README.md` - operator notes for global install and project-local state
