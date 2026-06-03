# Failure Taxonomy

| Failure signal | Primary component candidates | Required response |
|---|---|---|
| User says workflow ran wrong | workflow-pattern, command, skill | classify, collect evidence, propose narrow fix |
| Command routes to wrong mode | command, skill | fixture or structure check |
| Skill over/under-triggers | skill, workflow-pattern | trigger wording review, routing fixture |
| Subagent lacks scope/evidence | subagent-config, docs/protocol | packet/result protocol update |
| Completion claim lacks proof | tool-policy, workflow-pattern | fresh verification or `Unverified` note |
| Memory provenance gap | memory, docs/protocol | CLI receipt/evidence pointer, no raw DB write |
| Install path drift | install/setup | setup/script review |
| Tool misuse or trust issue | tool-policy, system-rules | policy check; security escalation if needed |

## Report First

Use `harness-issue-triage` to localize unclear harness complaints first. Harness failures that affect core controls require a report with evidence, predicted fix, regression risk, verification trigger, rollback plan, and approval status before applying changes.
