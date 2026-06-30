[KNOWN] # Context: classify-ecc-agents-for-aili

[KNOWN] ## Source Signal

[KNOWN] The user asked: “新开个change，先列 ECC 全量 agents → 分类：直接吸收 / 合并进现有 agent / 不适合 / 需要改写 +强制 add ignored 的 OpenSpec 文件”.

[KNOWN] The user later invoked `/define` and selected a refined absorption set: add `spec-miner`, `comment-accuracy-review`, `agent-evaluator`, `opensource-sanitizer`, `oss-release-readiness`, and `build-failure-repair`; do not add dedicated per-language agents in this package.

[KNOWN] The user then explicitly removed `type-design-analyzer` from the selected additions because a specialized TypeScript/type-design review agent is not useful enough for their expected usage.

[KNOWN] The user later confirmed `harness-optimization-audit` should be included and all selected agents/skills should use the existing default-installed workflow component model.

[KNOWN] The immediate prior discussion established that OpenSpec artifacts had remained ignored by repository policy, and the user now explicitly requested force-adding ignored OpenSpec files for this new change.

[KNOWN] ## Confirmed Direction

[KNOWN] - OpenSpec backend.
[KNOWN] - New change id: `classify-ecc-agents-for-aili`.
[KNOWN] - Classify ECC full agents before implementing any new AILI agents or skills.
[KNOWN] - Force-add ignored OpenSpec artifacts after validation.
[KNOWN] - Update the implementation-readiness package plan around the user-selected additions.

[KNOWN] ## Evidence Anchors

[KNOWN] - ECC selected source: `https://github.com/affaan-m/ECC`.
[KNOWN] - ECC agents directory: `https://github.com/affaan-m/ECC/tree/main/agents`.
[KNOWN] - Local current agents and skills are declared in `manifests/rose-aili.components.json`.
[KNOWN] - Current git status before this change was `main...origin/main` with ignored OpenSpec directories.
[KNOWN] - Read-only subagent review found local gaps around reverse spec mining, type-invariant review, comment accuracy review, agent-output evaluation, and non-destructive open-source/release sanitization.

[KNOWN] ## Open Questions / Residual Risks

[KNOWN] - ECC source ambiguity remains if the user intended `sifxprime/kodelyth-ecc` or another fork instead of `affaan-m/ECC`.
[INFERRED] - The selected classification is a DEFINE-time recommendation and should be treated as editable before BUILD.
[INFERRED] - The selected additions are not missing a must-have core ECC testing lane; optional follow-ups include optional language reviewers, `type-design-analyzer`, and database change review if demand appears.

[KNOWN] ## Artifact Mapping

[KNOWN] - `proposal.md`: scope, non-goals, impact.
[KNOWN] - `design.md`: evidence, decisions, alternatives, risks.
[KNOWN] - `tasks.md`: artifact and gate checklist.
[KNOWN] - `test-plan.md`: validation and review plan.
[KNOWN] - `interview.md`: DEFINE clarification packet and readiness state for the selected package plan.
[KNOWN] - `ecc-agents-classification.md`: full 67-agent inventory and classification.
[KNOWN] - `specs/ecc-agent-assessment/spec.md`: classification-gate behavior.

[KNOWN] ## DEFINE Gate State

[KNOWN] - DEFINE artifacts are updated with the user-selected absorption set.
[KNOWN] - The interview/test-plan Q1 and Q2 decisions are confirmed: include `harness-optimization-audit`, and default-install the selected agents/skills.
[KNOWN] - BUILD implementation remains blocked until the user explicitly approves production file edits.
