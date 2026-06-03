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

Default to 1 loop.

Run a second or third loop only when the previous loop found material loopholes that could change scope, design, acceptance, verification, security, rollout, or user decisions.

Hard limit: 3 loops.

Stop earlier when:

- all material loopholes are resolved
- remaining issues are explicitly marked `Open Question` or `Unverified`
- additional loops would only produce wording tweaks, low-risk nitpicks, or speculative concerns

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

## Adversarial Lenses

When the artifact is non-trivial, stress-test it through these lenses without turning the output into a long debate:

1. Pragmatist Skeptic
   - What can be deleted?
   - Is this over-engineered?
   - Is this abstraction premature?
2. Integration Validator
   - What adjacent module, state transition, failure path, or regression is missing?
   - What test proves this?
3. Evidence Researcher
   - Which claims are unsupported?
   - Which claims need repository evidence, official docs, or user confirmation?
4. Architect
   - Does this violate boundaries?
   - Does it introduce coupling or future maintenance debt?
5. Creative Challenger
   - Is there a simpler, more direct, or less invasive path?
   - Is there a better artifact shape?

Keep only material findings in the final stress-test result.

If the needed tool or skill is unavailable:

- perform the compact check inline when possible
- mark only the affected claim as `Unverified`
- mention tool unavailability only when it changes the result or blocks verification

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

## 🛑 Anti-Pattern Blacklist

Stop and repair the stress test if it does any of these:

- Manufactures certainty to satisfy a requested confidence level.
- Replaces missing evidence with confident tone, generic best practice, or “likely”.
- Treats a passing narrow check as proof of broad readiness.
- Hides unresolved user decisions inside assumptions.
- Ignores counter-evidence because it complicates the plan or final claim.
- Runs more loops only to polish wording instead of resolving material loopholes.
- Reports subagent conclusions without anchors or conflict reconciliation.

Fallback: downgrade confidence, mark the affected item `Open Question` or `Unverified`, and choose a concrete repair action from the process table.

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

## Example: Compact Embedded Use

Input artifact:

- Plan says: "Implement auth callback handling and update tests."

Stress-test result:

- Confidence: medium
- Material loophole: Verification gap - plan does not name the callback error cases or tests.
- Fix applied: add tasks for invalid state, expired code, provider error, and existing callback test file inspection.
- Remaining unverified: exact test command until package scripts are inspected.
- Safe to proceed: conditional.
