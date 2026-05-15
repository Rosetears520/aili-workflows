# Implementation Packages

An implementation package is the unit that BUILD may execute.

BUILD may receive a package explicitly from the user or synthesize an ordered package queue from approved ready artifacts. A `/build` invocation against a single ready target is enough approval to synthesize this queue; missing manual package text is not a stop condition.

## Required Fields

- goal and acceptance criteria;
- allowed files or smallest likely edit surface;
- forbidden scope;
- source artifacts and evidence;
- implementation owner or delegation plan;
- verification command(s);
- BUILD local review lanes: code review, test verification, and security review trigger or skip condition;
- repair or retry limit;
- rollback or pause condition;
- whether commits are allowed.

## Rules

- When no explicit package is supplied, synthesize packages from the highest-priority available artifacts: `tasks.md`, specs, design notes, `test-plan.md`, command arguments, and repository evidence.
- Each synthesized package must still name goal and acceptance criteria, likely edit surface, forbidden scope, evidence source, owner or delegation plan, verification, review lanes, repair limit, rollback or pause condition, and commit allowance.
- Delegated implementation packages must include a scoped subagent packet: allowed scope, forbidden scope, edit permission, high-risk stop gates, verification expectations, required evidence, and commit allowance.
- Preserve dependency order. Prefer small packages that can be implemented, verified, reviewed, and repaired independently.
- Use subagents for broad evidence gathering, non-trivial implementation, noisy verification, and review lanes when delegation saves context or improves evidence; ROSE remains responsible for integration and final judgment.
- Keep packages independently reviewable where practical.
- Do not combine unrelated feature, harness, install, and documentation work unless explicitly approved.
- BUILD is not complete after writing files; it must finish or explicitly block on the local code-review, test, and security-review gates.
- Security review may be skipped only when no security-sensitive surface is present; record the skip reason.
- If an in-scope repair changes code or behavior, rerun the affected verification and review lane before returning BUILD evidence.
- Pause if the package requires new dependencies, schema changes, public API changes, forbidden files, or broader scope than approved.

## Autonomous Queue Exit Criteria

Continue through the queue until one of these is true:

- all packages are implemented, verified, reviewed, and task state is updated with evidence;
- a stop condition requires explicit user approval;
- a package is blocked by missing target/readiness evidence, unavailable verification, or exhausted repair limits;
- the target repository root cannot be canonicalized inside the current workspace or allowed external directories;
- the user interrupts or narrows the goal.
