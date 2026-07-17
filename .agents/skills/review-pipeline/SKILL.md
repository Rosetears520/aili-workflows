---
name: review-pipeline
description: Optional focused post-implementation review routing. Use only when the user requests review or the changed surface has a clear specialist evidence need that direct diff inspection and the smallest relevant check cannot cover. Never creates an automatic review swarm.
---

# Review Pipeline

## Goal

Obtain the minimum additional review evidence needed for a specific risk.

## Trigger

Use only when:

- the user asks for review; or
- a specialist capability is required for a concrete unresolved risk.

Direct ROSE diff inspection and the smallest relevant check are the default. Multi-file work alone does not trigger this skill.

## Method

1. Name the unresolved review question.
2. Resolve one repository/cwd and applicable target rules. For A33, reference one current `WT-001` context, keep artifacts in the owning repository, disclose the shared-trust soft boundary, and do not scan the host broadly.
3. Choose at most two relevant specialists.
4. Send each the compact packet from `subagent-task-packet.md` and require the canonical result/finding envelope in `subagent-result.md`.
5. Inspect their evidence and resolve only the named question without voting.
6. If a blocking issue is fixed, run one targeted recheck. Stop after that and report any remaining blocker.

Do not automatically fan out code, test, security, coverage, AI, silent-failure, convergence, browser, or E2E lanes. Do not create a fixed multi-cycle repair loop.

## Result

Report the reviewed scope, evidence, blocking findings, skipped specialist checks, freshness, and remaining `Unverified` risks. ROSE owns the final judgment. A33 results reference rather than duplicate or rebind WT identity, keys, approvals, Git state, rules, or command/cwd.
