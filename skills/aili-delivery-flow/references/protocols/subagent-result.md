# Subagent Result Protocol

Canonical path for this change: `skills/aili-delivery-flow/references/protocols/subagent-result.md`.

Subagent output is evidence for ROSE to reconcile, not authority. Separate facts from interpretation and recommendations.

```text
TRACE ID:
STATUS: PASS | NEEDS_REVISION | BLOCKED | PARTIAL | NOT_FOUND
CONFIDENCE: high | medium | low
SUMMARY:

INSPECTED SCOPE:
- path / command / source - what was inspected

COVERAGE COMPLETED:
- scope item - completed / skipped with reason

OBSERVED FACTS:
- path:line-or-symbol - fact - freshness(active/current/stale/archived/generated/unknown) - confidence

EVIDENCE ANCHORS:
- path:line / command / source - why it matters

INFERENCES:
- inference - evidence basis - risk/confidence
- N/A if none

RECOMMENDATIONS:
- proposed action - why - owner (ROSE/user/subagent type)
- N/A if none

UNKNOWNS / GAPS:
- unknown, conflict, or missing evidence

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
- Inferences must state the evidence basis and risk.
- Recommendations are proposals only; ROSE may accept, reject, or revise them after reading the target files and running verification.
- Unknowns remain `Unknown`, `Open Question`, or `Unverified`; do not convert them into facts.

## Compact scout variant

Small read-only scouts may return a shorter result, but they must still distinguish:

- facts with anchors
- recommendations or caller actions
- unknowns / not found items
- next reads

## Exclusions

Do not include secrets, credentials, cookies, tokens, raw logs, long grep dumps, full file contents, unrelated exploratory output, or implementation changes outside the packet.
