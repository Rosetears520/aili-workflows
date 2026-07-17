# Harness Activation Matrix

| Task type | Required gates | Optional gates | Skipped by default | Approval-gated actions |
|---|---|---|---|---|
| Small local edit | Read target, targeted verify | TDD if behavior changes | OpenSpec, review-pipeline, memory writeback | None unless touching protected files |
| Unclear idea | IDEATE, parallelism/no-parallel analysis when decomposed, research-first evidence when方案 could change | mature prior-art or official-doc lanes | implementation | Any file edit |
| Spec or plan work | DEFINE, source evidence, questionnaire/test plan as needed, evidence-backed方案 state | plan audit, parallel read-only lanes | production code | Starting BUILD before approval |
| Bounded implementation | BUILD, package scope, parallelism analysis for multi-package work, targeted tests | code review for risk, official/prior-art research when triggered | broad repo rewrites | Scope expansion |
| User-requested packaging | target/platform confirmation, relevant tests/checks first, package evidence, repair/retest/repackage loop | release artifact smoke checks | packaging as a substitute for tests | signing, notarization, certificates, dependency/lockfile changes, external publishing |
| Ship/closeout | review/repair, fresh verification, closeout, join evidence for multi-lane work | memory receipt | new feature work | Archive/publish/push |
| Harness change | harness change report, component map, verification trigger | security/review audit | silent apply | ROSE/command/skill/subagent/memory/install edits |
| Security/trust boundary | security-hardening, threat/risk notes, targeted tests | independent security audit | unchecked completion claims | Weakening safety policy |
| Package 1–11 implementation | complete assigned package behavior, dependency/file ownership, lightweight savepoint with scope/files/unresolved/next | focused tests/checkers as implementation feedback | mandatory independent package-local quality gate | Scope expansion or high-risk/pre-action operation |
| Package 12 final inspection | direct final diff and applicable task-coverage inspection, smallest relevant fresh checks | at most two specialists for a concrete gap, one targeted repair/recheck | automatic review swarm, full command matrix by default | Graphify execution, publish/push/archive, destructive action |

## Gate Intent

- Prevent over-triggering for simple, local work.
- Prevent under-triggering for harness, memory, security, subagent, install, or completion-claim changes.
- Make proactive parallel planning, research-first planning evidence, and requested packaging sequencing visible without adding new public commands.
- Keep Package 1–11 verification lightweight and traceable; Package 12 is a direct final inspection, not an automatic comprehensive review swarm.
