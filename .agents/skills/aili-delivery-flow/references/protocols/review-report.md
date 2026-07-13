# Review Report Protocol

Review, test, security, coverage, convergence, evaluator, and focused-recheck reports use the canonical shared finding/result envelope in `subagent-result.md`. Workers provide evidence and propose dispositions; ROSE reconciles and owns final disposition. Do not vote on lane results, average confidence, or treat a worker verdict as acceptance authority.

```text
CANONICAL RESULT:
result_id:
trace_id:
lane:
owner:
status:
confidence: HIGH | MED | LOW | VERY LOW | UNKNOWN
inspected_scope:
checks:
freshness:
skipped_checks:
blockers:
unverified:
convergence_links:
review_arbitration_ref: openspec/changes/<change-id>/review-arbitration.md | N/A

FINDINGS:
- finding_id:
  source:
  claim:
  severity:
  evidence_anchors:
  affected_requirement:
  proposed_disposition: fix | refute-with-counter-evidence | accept-named-risk | Unverified-block
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

`review_arbitration_ref` is non-`N/A` only for a disputed, blocking, cross-session, or materially inconsistent finding. The exact change-local path is `openspec/changes/<change-id>/review-arbitration.md`. That artifact preserves the stable finding ID, competing claims, evidence and counter-evidence, proposed dispositions, ROSE disposition and rationale, owner, status, required recheck, freshness, and residual `Unverified` items. Do not create it for routine agreement, and do not create an instance in advance of a real qualifying finding.
