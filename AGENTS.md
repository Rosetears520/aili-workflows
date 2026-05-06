# aili-workflow Agent Control Plane

This repository’s detailed primary-agent behavior lives in [`agents/rose.md`](agents/rose.md). Treat this file as the thin repo-level entry point, not as a full copy of any upstream `CLAUDE.md`.

## Operating Rules

- Use `agents/rose.md` as the canonical ROSE behavior contract for implementation discipline, memory boundaries, verification, and handoff.
- Use `skills/*/SKILL.md` as on-demand workflows. If a task matches a skill, load that skill and follow it.
- Keep changes small, surgical, goal-driven, and verified with concrete evidence.
- Do not create new skills, dependencies, commits, pushes, broad refactors, or repo-wide formatting unless the user explicitly asks.
