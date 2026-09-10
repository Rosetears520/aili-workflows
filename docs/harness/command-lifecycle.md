# Command Lifecycle

Exactly four Delivery Commands and six Utility Commands are provided by this harness. Equivalent natural-language IDEATE, DEFINE, BUILD, and SHIP intent uses the same classifier, gates, permissions, and evidence contract; a shortcut grants no extra authority. Utility Commands are explicit operations, not lifecycle modes or independent acceptance/verdict owners.

Treat natural language as a first-class lifecycle entry, not as a hint that the user must type a shortcut. When the requested outcome is unambiguous, enter the same canonical loop without asking the user to restate `/ideate`, `/define`, `/build`, or `/ship`. Classify “先帮我想几种方案，暂时不要实现” as IDEATE, “把这个需求定义成可实施方案和测试计划” as DEFINE, “按已经接受的方案开始实现” as BUILD, and “把已实现的改动收尾并准备交付” as SHIP. Explanation, comparison, translation, and status questions about those names remain ordinary near misses; genuine mode/target ambiguity asks one focused question.

| Command | Mode | Contract |
|---|---|---|
| `/ideate` | IDEATE | Run the delegation scan, then explore, compare, and surface uncertainty; work directly only when no Task trigger is met or delegation is concretely blocked. Add one evidence capability only for a concrete gap. No production edits. |
| `/define` | DEFINE | Produce only dependency-ready spec/questionnaire/test artifacts. For OpenSpec, `requirements-grilling` owns needed `interview.md` clarification and `test-document-generator` owns required `test-plan.md`; neither auto-chains. Stop before implementation. |
| `/build` | BUILD | Derive the accepted queue from the active contract, append concise free-form continuity to orchestrator-owned `progress.txt` with no Markdown parsing/replay gate or automatic tests/commits/approvals, run one minimal changed-scope completion check, record `IMPLEMENTED_TARGETED_VERIFIED`, and stop. This umbrella alone names Package 12 as that direct final inspection. |
| `/ship` | SHIP | After fresh explicit intent, reuse still-covering BUILD evidence, run the delegation scan, and refresh only checks required by the exact affected closeout claim. Direct inspection is the no-trigger/blocked fallback. |
| `/local-review` | LOCAL_REVIEW | Run a report-first local audit over local changes, a base branch, a commit, a PR, or an OpenSpec change. It leaves OpenCode's `/review` untouched, reports skipped or `Unverified` lanes, and does not replace `/ship`. |
| `/handoff` | Utility | Create, list, or resume an explicit redacted repository-local handoff. Resume revalidates current state; the snapshot is not lifecycle, acceptance, or verification authority. |
| `/agents-md` | Utility | Create, update, or validate a project-local `AGENTS.md` through the shared template/script flow without silently overwriting project facts or user content. |
| `/harness-audit` | Utility | Return a bounded report-first audit of a named harness concern and candidate follow-up; it does not edit harness controls or select a lifecycle state. |
| `/retro` | Utility | Analyze explicitly supplied or approved sanitized evidence and return a bounded retrospective; it does not claim global history or authorize changes. |
| `/security-review` | Utility | Preview a report-only independent security review with exact source-transmission/scan gates; it does not repair, accept risk, or claim completion. |

## Non-Commands

Research, questionnaire, test-plan, implementation, fix, debug, release-blocker audit, repair loop, and harness evolution are internal stages. They are not top-level commands unless a later approved change adds them. `/review` remains OpenCode-owned and is not an AILI trigger; AILI-owned standalone review uses `/local-review`. `/aili-doctor` and `/simplify` are not AILI commands.

AILI does not provide `/loop`, `/schedule`, `/goal`, `/proactive`, `/cycle`, `/watch`, `/objective`, a worktree-maintenance command, or a Graphify command. It adds no hidden/unrequested AILI cron, scheduler, watcher, webhook, listener, daemon, persistent queue, hook, dependency, auto-retry, or other background runtime. Explicit product/repository automation remains eligible only through normal formal/high-risk gates; vocabulary-only comparison remains ordinary.

Question, delta, evidence/plan, neutral BUILD, review/repair, and convergence are bounded loop vocabulary, not an automatic sequence. One current intent selects one primary loop and at most one concrete auxiliary capability. `turn` and `objective` are executable; `interval` and `event` are design-owned protocol/runbook definitions for external/manual triggers only. AILI adds no scheduler, listener, daemon, persistent queue, hook, dependency, auto-retry, or background runtime.

Continuation resumes exactly one active authorized canonical envelope with current gates and remaining budgets. It preserves consumed counters and cannot reset/broaden authority, change phase/target, or refresh acceptance. Ordinary user/package/implementation goal wording and Goal-Driven Verification remain valid, but AILI does not own, imitate, bind, modify, or control native `/goal`; successful native behavior is Stage II / N/A.

`CONT-005` distinguishes three token states: no configured token budget is explicit `null` with no token enforcement; a requested token budget without reliable pre-start accounting stays non-null/unavailable and blocks; accounting lost midrun preserves non-null consumed/remaining counters with lost status. Do not silently convert requested or lost accounting to `null`.

Natural user identity input is NFC-normalized before stable LP identity resolution. Persisted or already-structured identity bytes must already be canonical raw-NFC compact-JSON UTF-8 bytes; escaped Unicode, decomposed NFC-equivalent bytes, controls, alternate field order, or JSON whitespace hard-block rather than being normalized in place. A different-identity allocation race permits one re-read and recomputed `max+1`; a second race or duplicate/malformed/conflicting persisted identity is corruption and hard-blocks with no write.

Hidden/unrequested AILI automation, including a request mixed with AILI protocol documentation, blocks with zero mutation and zero LP. A later documentation-only restatement may create or reuse a design-owned external/manual interval/event protocol, which creates no runtime or lifecycle permission. Explicitly scoped product/repository CI, cron, scheduler, webhook/listener, queue, daemon, hook, dependency, or auto-retry routes through every applicable formal, permission, credential, persistent-service, dependency, destructive, and verification gate.

## A33 Admission Boundary

The user chooses the Git host by starting OpenCode there. `WT-001` mode `a33-attached-shared-trust-domain` is current; `a30-a31-external-read`, A30 runtime results, and A32/item-41 readiness evidence are historical/stale and non-gating. A33 requires exact `<session-root>/.worktrees/<repo_key>/<worktree_key>` placement; exact root `/.worktrees/` ignore with no re-inclusion/tracked destination; grammar-valid non-reserved collision-free keys; trusted unambiguous topology/path; distinct host/source/target evidence; narrow-only target rules; and explicit branch/base-ref, `existing|create` mode, and source reflog policy. No suffix, guess, force, `-B`, orphan, remote guess, or implicit ref is allowed.

One host may declare multiple attachments, but every lane references one separate current WT context and keeps exact keys, 17-field no-digest `A33Identity` pre/post evidence, operation approval, target rules, per-target CodeGraph evidence, and owning-repository artifact destination distinct. Rules are re-read at operation/dispatch, may only narrow, and same-level conflict blocks. Cross-attachment copying/rebinding and broad host scans are forbidden; user-visible artifacts stay in the owning target repository.

These are static gates, not operation authority. PREPARE has zero add/remove effect. Every real or fixture ADD and later non-force REMOVE needs a different fresh exact key/class-bound approval; ADD needs accepted trusted-code risk and REMOVE has a separate deletion-inventory/risk gate. Only the exact admin/membership and authorized ADD ref/reflog delta may change; unrelated/prunable state and remove-time branch ref/reflog remain. Rollback preserves worktrees/evidence. The host and attachments form a same-owner, same-sensitivity shared trust domain; path/cwd/permission controls are a soft coordination boundary, not hard isolation or a sandbox. Root `.worktrees/`, visible `worktrees/`, and historical `.tmp/worktrees/` remain package-excluded, and A33 adds no host-selector, attach, cleanup, registry, manifest, or maintenance command.

## Command Shape

Each public command remains a thin entrypoint but should name:

- mode purpose;
- required behavior;
- hard stops;
- output contract.
- only the exact material or risky-operation gate visible for the current intent.

Detailed lifecycle authority remains in `.agents/skills/aili-delivery-flow` source references in this repository; installed runtimes receive those skills under `$HOME/.agents/skills/aili-delivery-flow`.

The command prompts should stay thin: name the gates and expected evidence shape, but do not copy the full workflow from lifecycle skills or protocols.
