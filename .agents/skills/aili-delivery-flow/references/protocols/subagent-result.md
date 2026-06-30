# Subagent Result Protocol

Repository source path: `.agents/skills/aili-delivery-flow/references/protocols/subagent-result.md`. Installed OpenCode runtime target: `skills/aili-delivery-flow/references/protocols/subagent-result.md`.

Subagent output is evidence for ROSE to reconcile, not authority. Separate facts from interpretation and recommendations.

Use internal English claim tags and canonical confidence labels in this protocol. Overall confidence must be `HIGH`, `MED`, `LOW`, `VERY LOW`, or `UNKNOWN`; `[GUESS]` and real-world `[FRAME]` claims cap confidence at `LOW`.

```text
TRACE ID:
STATUS: DONE | NEEDS_REVISION | BLOCKED | PARTIAL | NOT_FOUND
CONFIDENCE: HIGH | MED | LOW | VERY LOW | UNKNOWN
SUMMARY:

INSPECTED SCOPE:
- path / command / source - what was inspected

EVIDENCE PROVIDER NOTES:
- CodeGraph used/skipped/unavailable/stale/noisy/N/A - confidence impact and fallback used

COVERAGE COMPLETED:
- scope item - completed / skipped with reason

LANE / JOIN STATUS:
- lane id / owner / status (`completed`, `partial`, `blocked`, `skipped`, `unverified`) - expected evidence present/missing - blockers or N/A

OBSERVED FACTS:
- path:line-or-symbol - [claim tag] fact - freshness(active/current/stale/archived/generated/unknown) - confidence

EVIDENCE ANCHORS:
- path:line / command / source - why it matters

FALSIFICATION / NEGATIVE CHECKS:
- check attempted to disprove the finding, find counterexamples, or confirm absence - result
- N/A if none possible within scope, with reason

INFERENCES:
- [claim tag] inference - evidence basis - risk/confidence
- N/A if none

RECOMMENDATIONS:
- proposed action - why - owner (ROSE/user/subagent type)
- N/A if none

UNKNOWNS / GAPS:
- unknown, conflict, or missing evidence

RESIDUAL UNCERTAINTY:
- remaining uncertainty after checks - impact on ROSE/user decision

DECISION NEEDED FROM ROSE/USER:
- decision, approval, prioritization, or follow-up needed; N/A if no decision is needed

SKIPPED WORK:
- skipped item - reason - risk

HARNESS FAILURE SIGNALS:
- lifecycle/gate/protocol/memory/tool-policy failure signal, or N/A

MAINAGENT NEXT READS:
- path / command - why ROSE should inspect before acting

VERIFICATION EVIDENCE:
- command / inspection / test - result or not run with reason

STOP CONDITIONS HIT:
- scope expansion / missing permission / conflicting evidence / unsafe ambiguity / N/A
```

## Required separation

- Observed facts must include evidence anchors and freshness whenever relevant.
- Results must use internal English claim tags for factual, interpretive, verification, readiness, uncertainty, and recommendation claims unless the caller provides a stricter compatible format.
- Lane / join status must be present for parallel or multi-lane work. It must name the lane/work package id, owner, status, expected evidence presence, and blockers so ROSE can join without guessing.
- Falsification / negative checks should say what was tried to disprove the conclusion, find counterexamples, or confirm absence; if not possible, say why.
- Inferences must state the evidence basis and risk.
- Recommendations are proposals only; ROSE may accept, reject, or revise them after reading the target files and running verification.
- Unknowns remain `Unknown`, `Open Question`, or `Unverified`; do not convert them into facts.
- Missing, empty, status-less, or evidence-less lane output is not completion evidence. Do not infer completion from file state, adjacent lane success, or ROSE's later inspection; name the missing evidence and mark the lane `partial`, `blocked`, or `unverified` as applicable.
- `STATUS: DONE` means the worker completed its assigned packet and returned evidence. It is not a final PASS/FAIL/ready verdict for the package or change.
- Workers must not claim final PASS, final FAIL, final `Unverified`, approve, reject, ship, complete, accepted, or ready status for the package or change. ROSE/user owns final reconciliation, progress-ledger entries, and user-facing acceptance judgment.
- Results should make residual uncertainty and any decision needed from ROSE/user explicit instead of hiding them inside the recommendation.
- Results should preserve the assigned package/lane boundary. If the worker finds the boundary unsafe, dependent, overlapping, unverifiable, or out of scope, report that as a blocker or recommendation instead of silently merging, serializing, or taking over another lane.
- CodeGraph evidence is optional discovery evidence. It must be summarized as anchors, labeled when stale/noisy/no-result, and must not replace final file, diff, test, command, or document inspection by the responsible lane.

## Compact scout variant

Small read-only scouts may return a shorter result, but they must still distinguish:

- overall status and canonical confidence
- facts with anchors
- recommendations or caller actions
- unknowns / not found items
- next reads

## Compact evidence packs

For noisy logs, broad search output, long diffs, multi-source review evidence, or verbose test output, use or cite `.agents/skills/aili-delivery-flow/references/protocols/compact-evidence-pack.md` in repository source docs, or the installed runtime target `skills/aili-delivery-flow/references/protocols/compact-evidence-pack.md` when explicitly referring to an OpenCode home. The result must preserve source, scope, freshness, result, key observations, minimal failure excerpt when relevant, raw evidence access or rerun command, and remaining `Unverified` items.

## Exclusions

Do not include secrets, credentials, cookies, tokens, raw logs, long grep dumps, full file contents, unrelated exploratory output, or implementation changes outside the packet. Full logs may be shown only when the user explicitly requests them and the content has been checked as safe to show.
