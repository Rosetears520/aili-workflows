---
name: strategy-stress-test
description: Stress-tests a proposed strategy, interview packet, spec, plan, task breakdown, subagent reconciliation, review, or completion claim before acceptance; use after a first draft exists, before write-back, before implementation, during reconciliation, or before claiming complete/fixed/verified/ready.
license: MIT
compatibility: opencode
metadata:
  source: local-workflow-guardrail
---

# Strategy Stress Test

## Purpose

Use this skill to turn "are we confident enough?" into an engineering guardrail.

Do not pursue artificial 100% certainty. Target factually supportable high confidence.

If the user asks for 100% confidence, treat that as a request to stress-test harder, not as permission to manufacture certainty. Stop when the claim is supported, conditional, or explicitly marked with `Open Question` / `Unverified` items.

If confidence is not supportable, identify material loopholes, missing evidence, counterexamples, hidden assumptions, verification gaps, and repair options.

Anything still unresolved must be marked as `Open Question` or `Unverified`.

## When to Use

Use this skill after a first draft exists and before the draft is accepted, written back, implemented, dispatched, reviewed as final, or reported complete.

Common trigger points:

- after generating an interview packet
- between SPECIFY and PLAN
- before freezing an implementation plan or task breakdown
- after subagents return and before reconciliation is accepted
- before saying `complete`, `fixed`, `passing`, `verified`, `ready`, or `accepted`
- at the end of code-reviewer, security-auditor, or test-engineer reports

Do not use this skill for tiny obvious edits, pure brainstorming with no artifact, or cases where no concrete strategy, spec, plan, review, or claim exists yet.

## Loop Limit

Run up to 3 loops.

Stop earlier when:

- all material loopholes are resolved
- remaining issues are explicitly marked `Open Question` or `Unverified`
- additional loops would only produce wording tweaks or low-risk nitpicks

Never keep looping to manufacture certainty.

## Process

For each loop:

1. Restate the current strategy, spec, plan, review, interview packet, or completion claim in one short paragraph.
2. Ask whether it is factually supported enough to proceed.
3. If not, list only material loopholes that could change scope, design, task order, acceptance criteria, verification, security, privacy, reliability, rollout, or user decisions.
4. Classify each loophole as one of: Missing evidence, Hidden assumption, Counterexample, Edge case, Contradiction, Dependency/order problem, Security/privacy/reliability risk, Verification gap, or User decision required.
5. For each loophole, choose one repair action: edit the current artifact, inspect repository code/docs, fetch official or external docs, ask the user, defer as `Open Question`, or mark as `Unverified`.
6. Apply fixes only when they are within scope, allowed by the current mode, and supported by evidence.
7. Re-run the loop only if material loopholes remain.

## Evidence Rules

Use evidence before confidence.

Valid evidence can include:

- user-confirmed answers
- current spec, design, tasks, or acceptance docs
- repository source files, tests, schemas, configs, logs, or diffs
- official documentation or current web sources when external behavior matters
- fresh verification command output
- reconciled subagent evidence with anchors

Invalid evidence:

- intuition
- stale logs
- partial output not read fully
- unverified assumptions
- `should work` language
- subagent conclusions without evidence anchors

## Output Contract

Return this structure when reporting the stress-test result:

```text
Confidence: high | medium | low

Current artifact / claim:
- ...

Material loopholes found:
- [Category] Loophole:
  Evidence gap:
  Proposed fix:
  Status: fixed | ask_user | inspect_code | fetch_docs | open_question | unverified

Fixes applied:
- ...

Remaining open questions:
- Open Question: ...

Remaining unverified items:
- Unverified: ...

Evidence used:
- ...

Safe to proceed: yes | no | conditional
Reason:
- ...
```

## Integration Rules

When called by another skill or agent:

- Do not replace the caller skill.
- Do not write files unless the caller skill and current mode allow edits.
- Keep the output compact enough to paste into a final report or artifact appendix.
- Prefer editing the artifact to adding a long critique when the fix is obvious and allowed.
