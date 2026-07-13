# ROSE Memory References

This directory is distributed with the `rose-memory` skill. The CLI is a legacy/pre-runtime compatibility tool; all state remains project-local and has no native/global or formal lifecycle authority.

Files:

- `memory_cli.py` - the only supported interface for schema creation, migrations, reads, writes, receipts, checkpoints, requirement memory, evidence, findings, and retrieval packs.
- `schema.sql` - the current SQLite schema emitted by `memory_cli.py` for review and auditing.

State boundary:

- Global skill directory: tool and protocol only.
- Project directory: `memory/memory.db` state only.

Do not store `memory.db` in this directory. Do not edit SQLite rows manually.

Memory policy:

- Default-write only explicit user-stated requirements, preferences, decisions, corrections, and acceptance criteria when identity, project/change/session scope, source metadata, timestamp, permission, and content safety are clear.
- Block or keep the item in the active change artifact when scope, metadata, identity, or permission is ambiguous; never persist secrets or private data.
- Use checkpoints as bounded continuity input. Formal `progress.txt`, OpenSpec artifacts, fresh Git/filesystem state, and fresh verification retain their own authority.
- Keep model-derived facts as evidence-backed candidates or change-local `Unverified` items. Do not invent storage operations when the current CLI cannot represent the required lifecycle.
- DCP, compression thresholds, stale chat summaries, task checkboxes, and old logs have no active-task authority.
- Do not import, migrate, dual-read, dual-write, or bridge this database to native/global or reserved `.aili` state.
- Memory writeback failure should be retried once, tracked, retried before handoff, and reported if still failing; it should not block otherwise safe task progress.

If a `rose-memory` command is available:

```bash
rose-memory doctor --db memory/memory.db --record
```

Direct fallback:

```bash
python ~/.agents/skills/rose-memory/references/memory_cli.py doctor --db memory/memory.db --record
```

Focused current-task pack:

```bash
rose-memory pack-current --db memory/memory.db --budget 1200
```
