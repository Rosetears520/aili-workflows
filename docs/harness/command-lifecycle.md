# Command Lifecycle

Exactly four top-level delivery shortcuts are provided by this harness. Equivalent natural-language IDEATE, DEFINE, BUILD, and SHIP intent uses the same classifier, gates, permissions, and evidence contract; a shortcut grants no extra authority. `/local-review` is additionally allowed as a standalone local audit command, not as a delivery lifecycle mode.

| Command | Mode | Contract |
|---|---|---|
| `/ideate` | IDEATE | Explore, compare, and surface uncertainty. Expose parallelism or no-parallel reasoning for multi-unit ideas and use research evidence when it can change the方案. No production edits. |
| `/define` | DEFINE | Produce aligned spec/questionnaire/test artifacts. For OpenSpec, route `interview.md` through `requirements-grilling` and `test-plan.md` through `test-document-generator`. Confirm evidence-backed方案 state before BUILD readiness. Stop before implementation. |
| `/build` | BUILD | Execute complete accepted Package 1–11 behavior through an explicit or synthesized dependency-ordered queue with lightweight savepoints, then run Package 12 as the single mandatory comprehensive quality gate. |
| `/ship` | SHIP | Reuse or refresh BUILD gates, run release-blocker audit for the selected change/final diff or explicitly requested baseline/repository scope, reconcile multi-lane review/repair with join evidence, then complete release-readiness review, repair, verification, archive/sync/closeout as approved. |
| `/local-review` | LOCAL_REVIEW | Run a report-first local audit over local changes, a base branch, a commit, a PR, or an OpenSpec change. It leaves OpenCode's `/review` untouched, reports skipped or `Unverified` lanes, and does not replace `/ship`. |

## Non-Commands

Research, questionnaire, test-plan, implementation, fix, debug, release-blocker audit, repair loop, and harness evolution are internal stages. They are not top-level commands unless a later approved change adds them. `/review` remains OpenCode-owned and is not an AILI trigger; AILI-owned standalone review uses `/local-review`.

AILI does not provide `/loop`, `/schedule`, `/goal`, `/proactive`, `/cycle`, `/watch`, `/objective`, a worktree-maintenance command, or a Graphify command. It adds no cron, scheduler, watcher, webhook, listener, daemon, persistent queue, hook, dependency, auto-retry, or other background runtime.

BUILD uses exactly six inner loops—question, delta, evidence/plan, neutral BUILD, review/repair, and convergence—and four outer profiles. `turn` and `objective` are executable; `interval` and `event` are design-owned protocol/runbook definitions for external/manual triggers only. AILI adds no seventh loop, scheduler, listener, daemon, persistent queue, hook, dependency, auto-retry, or background runtime.

Continuation resumes exactly one active authorized canonical envelope with current gates and remaining budgets. It preserves consumed counters and cannot reset/broaden authority, change phase/target, or refresh acceptance. Ordinary user/package/implementation goal wording and Goal-Driven Verification remain valid, but AILI does not own, imitate, bind, modify, or control native `/goal`; successful native behavior is Stage II / N/A.

`CONT-005` distinguishes three token states: no configured token budget is explicit `null` with no token enforcement; a requested token budget without reliable pre-start accounting stays non-null/unavailable and blocks; accounting lost midrun preserves non-null consumed/remaining counters with lost status. Do not silently convert requested or lost accounting to `null`.

Natural user identity input is NFC-normalized before stable LP identity resolution. Persisted or already-structured identity bytes must already be canonical raw-NFC compact-JSON UTF-8 bytes; escaped Unicode, decomposed NFC-equivalent bytes, controls, alternate field order, or JSON whitespace hard-block rather than being normalized in place. A different-identity allocation race permits one re-read and recomputed `max+1`; a second race or duplicate/malformed/conflicting persisted identity is corruption and hard-blocks with no write.

Pure or mixed requests to install, register, run, modify, update, reconfigure, enable, or reuse automation reject with zero mutation and zero LP. A later documentation-only restatement may create or reuse a design-owned external/manual interval/event protocol.

## Command Shape

Each public command remains a thin entrypoint but should name:

- mode purpose;
- required behavior;
- hard stops;
- output contract.
- any command-visible proactive planning, research-first, or packaging gate that would otherwise be hidden inside skill references.

Detailed lifecycle authority remains in `.agents/skills/aili-delivery-flow` source references in this repository; installed runtimes receive those skills under `$HOME/.agents/skills/aili-delivery-flow`.

The command prompts should stay thin: name the gates and expected evidence shape, but do not copy the full workflow from lifecycle skills or protocols.
