# Harness Activation Matrix

| Task type | Required gates | Optional gates | Skipped by default | Approval-gated actions |
|---|---|---|---|---|
| Small local edit | Read target, targeted verify | TDD if behavior changes | OpenSpec, review-pipeline, memory writeback | None unless touching protected files |
| Unclear idea | IDEATE | research evidence | implementation | Any file edit |
| Spec or plan work | DEFINE, source evidence, questionnaire/test plan as needed | plan audit | production code | Starting BUILD before approval |
| Bounded implementation | BUILD, package scope, targeted tests | code review for risk | broad repo rewrites | Scope expansion |
| Ship/closeout | review/repair, fresh verification, closeout | memory receipt | new feature work | Archive/publish/push |
| Harness change | harness change report, component map, verification trigger | security/review audit | silent apply | ROSE/command/skill/subagent/memory/install edits |
| Security/trust boundary | security-hardening, threat/risk notes, targeted tests | independent security audit | unchecked completion claims | Weakening safety policy |

## Gate Intent

- Prevent over-triggering for simple, local work.
- Prevent under-triggering for harness, memory, security, subagent, install, or completion-claim changes.
