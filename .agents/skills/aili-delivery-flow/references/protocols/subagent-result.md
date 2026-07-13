# Subagent Result Protocol

Repository source path: `.agents/skills/aili-delivery-flow/references/protocols/subagent-result.md`. Installed runtime target: `$HOME/.agents/skills/aili-delivery-flow/references/protocols/subagent-result.md`.

Subagent output is evidence for ROSE to reconcile, not authority. Separate facts from interpretation and recommendations.

Use internal English claim tags and canonical confidence labels in this protocol. Overall confidence must be `HIGH`, `MED`, `LOW`, `VERY LOW`, or `UNKNOWN`; `[GUESS]` and real-world `[FRAME]` claims cap confidence at `LOW`.

## Shared finding/result envelope

[KNOWN] Review, test, security, coverage, convergence, and focused-recheck results use one neutral envelope:

- `result_id`, `trace_id`, `lane`, `owner`, `status`, and `confidence`;
- `inspected_scope`, `checks`, `freshness`, `skipped_checks`, `blockers`, and `unverified`;
- `findings`, where every item has `finding_id`, `source`, `claim`, `severity`, `evidence_anchors`, `affected_requirement`, `proposed_disposition`, `required_action`, and `verification`;
- `convergence_links`, using the canonical link fields in `../artifact-contracts.md`;
- `review_arbitration_ref`, only when a finding is disputed, blocking, cross-session, or materially inconsistent; its exact OpenSpec path is `openspec/changes/<change-id>/review-arbitration.md`;
- `worktree_context_ref` and `role_overlay`, when cross-root, copied as references/status from the task packet rather than redefined or rebound root, Git, approval, path, dirty-state, command/cwd, containment, or permission facts. `role_overlay` is narrowing/evidence text, never authority or proof of effective permissions. Any duplicate or claimed effective rule derived only from the overlay is non-authoritative and blocks reconciliation against `worktree-context.md` (`WT-001`).

[KNOWN] Stable proposed dispositions are `fix`, `refute-with-counter-evidence`, `accept-named-risk`, and `Unverified-block`. A worker proposes a disposition; ROSE owns reconciliation and final status. A no-finding result still supplies inspected scope, checks, freshness, and skipped checks.

[KNOWN] Lane results are joined by evidence, never by majority vote or averaged confidence. A credible material minority finding remains open until ROSE records one evidence-backed outcome: fixed and freshly rechecked, refuted with preserved counter-evidence, accepted as a named risk by the authorized decision owner, or `Unverified-block`. Worker status is never final authority.

## Conditional review arbitration

Use `openspec/changes/<change-id>/review-arbitration.md` only when a finding is disputed, blocking, cross-session, or materially inconsistent. Preserve `finding_id`, competing claims, evidence anchors, counter-evidence, each proposed disposition, ROSE's final disposition and rationale, decision owner, status, required recheck, freshness, and residual `Unverified` items. Routine uncontested findings remain in the ordinary review report; do not pre-create an arbitration artifact.

## Canonical result text block

```text
CANONICAL RESULT:
result_id:
trace_id:
lane:
owner:
status:
confidence:
inspected_scope:
checks:
freshness:
skipped_checks:
blockers:
unverified:
findings: see FINDINGS or NO FINDINGS
convergence_links:
review_arbitration_ref:
worktree_context_ref:
role_overlay:
FINDINGS:
- finding_id:
  source:
  claim:
  severity:
  evidence_anchors:
  affected_requirement:
  proposed_disposition:
  required_action:
  verification:
NO FINDINGS:
findings: []
inspected_scope:
checks:
freshness:
skipped_checks:
blockers: []
unverified: []
```

[KNOWN] `source` identifies the command, file, runtime observation, or delegated evidence record from which the finding was derived. The no-findings form is valid only when its inspected scope, checks, freshness, skips, blockers, and `Unverified` items are explicit.

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

CONVERGENCE LINKS:
- requirement/decision/risk - task/package - file/artifact - fresh verification - disposition - freshness - status

REVIEW ARBITRATION REF:
- openspec/changes/<change-id>/review-arbitration.md | N/A

WORKTREE CONTEXT / ROLE OVERLAY:
- worktree_context_ref and role_overlay status | N/A

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
- A30 cross-root results must report parent/session root, parent and target HEAD/dirty snapshots, Git common-dir pre/post equivalence, probe exit/status/version, final merged child-rule provenance, override-evidence status, blocked and `Unverified` cases, and temporary cleanup. They must not claim safe/no-mutation/no-nesting when the probe is nonzero or final merged rules/provenance or override absence cannot be proven. No result authorizes automatic integration or cleanup of a source/target worktree.
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
