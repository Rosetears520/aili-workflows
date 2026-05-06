---
name: rose-memory
description: Use the ROSE project-local SQLite memory system through the bundled memory_cli.py. Use this for task checkpoints, requirement memory, durable findings, focused retrieval packs, and writeback receipts.
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
- recording user-stated requirements, preferences, decisions, corrections, or acceptance criteria
- recording durable project facts, findings, claims, or evidence
- retrieving focused project memory context after compaction or explicit resume
- recovering from interrupted work

## Rules

- Never edit `memory/memory.db` manually.
- Never create `memory.md`, JSON sidecars, or alternate memory state files.
- Never store project state under `~/.config/opencode/`.
- Always use the `rose-memory` shim when available, otherwise use the bundled `memory_cli.py` directly.
- Durable memory must have evidence or an explicit no-promotion receipt.
- Memory is additive context, not the active task contract. Current user instructions and current conversation override older memory.
- Record memory by default for non-trivial tasks, but classify it into task checkpoints, requirement memory, and durable project findings.
- Prefer writing user requirements and decisions over task transcript logs. Promote durable findings only when they are reusable and evidence-backed.
- DCP compression is normal context management. Use compressed summaries as the authoritative active-chat state; query memory only when the summary is insufficient, the active task is ambiguous, the user explicitly resumes prior work, or memory writeback is pending.
- If memory writeback fails, retry once when the fix is obvious. If it still fails, continue safe task progress, keep a pending TodoWrite item for memory writeback, retry before final handoff, and report any remaining failure.
- If the current directory is not inside a project, stop and report `SETUP_BLOCKED_NO_PROJECT_ROOT`.

## Memory Layers

Task checkpoint:
- Goal, scope, progress, files touched, and verification evidence.
- Write for every non-trivial task and meaningful phase transition.

Requirement memory:
- User-stated requirements, preferences, corrections, decisions, and acceptance criteria.
- Prioritize this layer because it reduces future drift.

Durable project finding:
- Reusable architecture facts, project constraints, and evidence-backed lessons learned.
- Do not promote ordinary task notes or raw DCP summaries into durable memory.

Conflict rule:
- Current user message wins over current chat history, DCP summaries, and memory.
- DCP compressed summary wins over stale memory for active-task state.
- If memory suggests a conflict that changes the next action, surface it before acting.

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

Record a structured task checkpoint:

```bash
rose-memory checkpoint \
  --db memory/memory.db \
  --goal "<goal>" \
  --scope "<scope>" \
  --progress "<progress>" \
  --file "<path>" \
  --evidence-ref "<file/command/result>"
```

Record requirement memory:

```bash
rose-memory remember-requirement \
  --db memory/memory.db \
  --text "<user requirement/preference/correction/decision>" \
  --source "conversation" \
  --task-key "<task>"
```

Retrieve memory context:

```bash
rose-memory pack --db memory/memory.db "<query>" --mode direct --budget 800
rose-memory search --db memory/memory.db "<query>" --limit 10
```

Retrieve the focused current-task pack:

```bash
rose-memory pack-current --db memory/memory.db --task-key "<task>" --budget 1200
```

After DCP compaction, prefer the compressed summary. Use `pack-current` or this focused fallback only when memory is actually needed:

```bash
rose-memory pack \
  --db memory/memory.db \
  "current active task requirements decisions evidence" \
  --mode direct \
  --budget 1200
```

Complete a task with no durable memory promoted:

```bash
rose-memory complete --db memory/memory.db --summary "<completion summary>" --no-durable-memory-promoted
```

Most completions should include `--no-durable-memory-promoted`. Use durable promotion only for stable user preferences, repeated corrections, architecture facts, reusable project findings, or evidence-backed decisions.

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
