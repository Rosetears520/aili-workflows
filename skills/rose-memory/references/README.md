# ROSE Memory References

This directory is distributed as part of the global `rose-memory` OpenCode skill.

Files:

- `memory_cli.py` - the only supported interface for schema creation, migrations, reads, writes, receipts, evidence, findings, and retrieval packs.
- `schema.sql` - the current SQLite schema emitted by `memory_cli.py` for review and auditing.

State boundary:

- Global skill directory: tool and protocol only.
- Project directory: `memory/memory.db` state only.

Do not store `memory.db` in this directory. Do not edit SQLite rows manually.

If a `rose-memory` command is available:

```bash
rose-memory doctor --db memory/memory.db --record
```

Direct fallback:

```bash
python ~/.config/opencode/skills/rose-memory/references/memory_cli.py doctor --db memory/memory.db --record
```
