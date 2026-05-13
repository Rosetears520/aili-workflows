## 1. Scope and Evidence Gates

- [x] 1.1 Confirm implementation approval for this change before editing any core harness files. User approved editing `agents/rose.md`, skills, and protocols during BUILD.
- [x] 1.2 Reconcile overlap with `openspec/changes/add-harness-evolution-layer/`, including whether its checked tasks correspond to files present in the current worktree; record the result as `current`, `stale`, `missing`, or `blocked` before BUILD edits begin. Result: stale/missing/conflicting; archived without syncing specs to `openspec/changes/archive/2026-05-13-add-harness-evolution-layer/`.
- [x] 1.3 Use `skills/aili-delivery-flow/references/protocols/` as the canonical authority path for subagent protocols; if top-level `protocols/**` exists, convert it to a pointer/index/migration note or block for separate approval instead of maintaining duplicate rules. Result: top-level `protocols/**` not present; no duplicate path created.
- [x] 1.4 Record direct implementation scope boundaries: no dependency changes, no lockfile changes, no SQLite schema changes, no command rename, no commit/push.

## 2. Direct vs Delegated Work Contract

- [x] 2.1 Add `skills/aili-delivery-flow/references/direct-vs-delegated-work.md` with direct allowlist, mandatory delegation triggers, context-saving rule, and high-risk gate boundaries.
- [x] 2.2 Define the exact criteria for direct work: exact target, low risk, surgical change, local verification, and no project-wide convention discovery.
- [x] 2.3 Define mandatory delegation triggers for broad search, 3+ relevant files, 2+ directories/subsystems, 2+ search passes, noisy logs, active/stale/generated judgment, reference scans, call-chain mapping, test mapping, and convention discovery.

## 3. Repo Evidence First Skill

- [x] 3.1 Add `skills/repo-evidence-first/SKILL.md` with Chinese body text and English skill name/path.
- [x] 3.2 Include project evidence pack fields: current contract, local rules, existing patterns, stale/generated/archived counter-evidence, verification path, unknowns, and next action.
- [x] 3.3 Include claim classification rules so unsupported project facts become `Hypothesis`, delegated work, user questions, or blocked items.
- [x] 3.4 Add routing guidance from repo evidence needs to `code-scout`, `doc-researcher`, `web-researcher`, `test-engineer`, and `security-auditor`.

## 4. Session Handoff Skill

- [x] 4.1 Add `skills/session-handoff/SKILL.md` for long sessions, compression, BLOCKED/IDLE states, and session transitions.
- [x] 4.2 Define handoff output fields: goal, contract, lifecycle mode, backend/source, scope, touched artifacts, evidence anchors, subagent activity, decisions, open questions, risks, verification state, blocked reason, next action, and continuation prompt.
- [x] 4.3 Define placement rules for OpenSpec changes, current task directories, and non-OpenSpec contexts.
- [x] 4.4 Define exclusions for raw logs, grep dumps, full file contents, secrets, irrelevant conversation, and default durable memory promotion.

## 5. Subagent Dispatch and Code Locality Mapping

- [x] 5.1 Update `skills/parallel-subagent-dispatch/SKILL.md` so context-saving delegation is mandatory when trigger conditions are met.
- [x] 5.2 Expand good single-subagent uses to include upstream callers, downstream consumers, peer/sibling implementations, test coverage mapping, convention discovery, and active-vs-stale classification.
- [x] 5.3 Update `agents/code-scout.md` or its shared result guidance so code-scout returns a code locality map with target, upstream, downstream, peer patterns, tests/verification, next reads, risk notes, and conclusion.
- [x] 5.4 Preserve read-only boundaries for code-scout: no edits, no raw grep dumps, no implementation decisions, and no nested agents. Security review found broad shell search allowances could bypass secret deny rules; user approved tightening `code-scout` bash permissions to `git status` / `git ls-files` only.

## 6. Subagent Protocols

- [x] 6.1 Add or update `skills/aili-delivery-flow/references/protocols/subagent-task-packet.md` with goal, context, allowed scope, forbidden scope, edit permission, evidence required, expected return format, stop conditions, placement rules, coverage expectations, and known exclusions.
- [x] 6.2 Add or update `skills/aili-delivery-flow/references/protocols/subagent-result.md` with status, inspected scope, observed facts, evidence anchors, freshness, confidence, inferences, recommendations, unknowns, and MainAgent next reads.
- [x] 6.3 Ensure result protocol explicitly states that subagent output is evidence for ROSE to reconcile, not authority.
- [x] 6.4 Ensure protocol examples avoid raw logs, long file excerpts, grep dumps, secrets, and unrelated exploratory output.

## 7. Minimal ROSE Runtime Router

- [x] 7.1 Add only short routing text to `agents/rose.md` for direct-vs-delegated work, repo-evidence-first, session-handoff, code locality mapping, and protocol paths.
- [x] 7.2 Ensure `agents/rose.md` does not duplicate full skill/reference/protocol content.
- [x] 7.3 Include a short rule that if ROSE skips delegation for a non-trivial task, it must state why the direct allowlist applies and why delegation would not add material evidence or context savings.

## 8. Verification and Closeout

- [x] 8.1 Run `openspec validate "strengthen-rose-delegation-protocols" --strict` after artifact creation and again after implementation. Result: PASS after implementation and again after review fixes.
- [x] 8.2 Run targeted structure checks confirming required files exist: `direct-vs-delegated-work.md`, `repo-evidence-first/SKILL.md`, `session-handoff/SKILL.md`, `parallel-subagent-dispatch/SKILL.md`, canonical `subagent-task-packet.md`, canonical `subagent-result.md`, and the minimal `agents/rose.md` router update. Result: `python scripts/delegation_protocols_check.py` PASS after implementation and after review fixes.
- [x] 8.3 Run targeted content checks confirming required sections/fields appear: direct allowlist, mandatory delegation triggers, repo evidence status/output, session handoff placement/exclusions, code locality map fields, task packet scope/permission/evidence/stop fields, result facts/inferences/recommendations/unknowns/next reads, and canonical protocol path statement. This BUILD adds `scripts/delegation_protocols_check.py` for PASS/FAIL structure/content checks; result: PASS after review-expanded field checks, top-level protocol check, and code-scout bash permission regression check.
- [x] 8.4 Run scoped diff/status review to confirm only approved files changed and no dependency, lockfile, SQLite schema, commit, push, or unrelated edits occurred. Result: `git diff --name-only` shows tracked modifications only in `agents/code-scout.md`, `agents/rose.md`, and `skills/parallel-subagent-dispatch/SKILL.md`; current untracked in-scope files are this OpenSpec change, archived old change, new skills/protocol refs, and `scripts/delegation_protocols_check.py`. Existing unrelated untracked `.opencode/**`, `docs/research/**`, and `openspec/config.yaml` remain excluded from this package.
- [x] 8.5 If implementation is completed later, run the appropriate review pipeline and mark any unrun checks as `Unverified`. Result: code-reviewer, test-engineer, and security-auditor ran; blocking findings were fixed and relevant re-reviews passed. Runtime behavior remains statically verified, not live-simulated.
