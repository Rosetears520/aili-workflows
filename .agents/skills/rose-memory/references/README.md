# ROSE Memory References

This directory is distributed as part of the global `rose-memory` OpenCode skill.

Files:

- `memory_cli.py` - the only supported interface for schema creation, migrations, reads, writes, receipts, checkpoints, requirement memory, evidence, findings, and retrieval packs.
- `schema.sql` - the current SQLite schema emitted by `memory_cli.py` for review and auditing.

State boundary:

- Global skill directory: tool and protocol only.
- Project directory: `memory/memory.db` state only.

Do not store `memory.db` in this directory. Do not edit SQLite rows manually.

Memory policy:

- Record task-relevant memory by default for non-trivial tasks.
- Use checkpoints for current goal, scope, progress, touched files, and verification evidence.
- Use requirement memory for user-stated requirements, preferences, decisions, corrections, and acceptance criteria.
- Use durable findings only for reusable, evidence-backed project knowledge.
- Current conversation and DCP compressed summaries override stale memory for active-task state.
- Memory writeback failure should be retried once, tracked, retried before handoff, and reported if still failing; it should not block otherwise safe task progress.

If a `rose-memory` command is available:

```bash
rose-memory doctor --db memory/memory.db --record
```

Direct fallback:

```bash
python ~/.config/opencode/skills/rose-memory/references/memory_cli.py doctor --db memory/memory.db --record
```

Focused current-task pack:

```bash
rose-memory pack-current --db memory/memory.db --budget 1200
```
