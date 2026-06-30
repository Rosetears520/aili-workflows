[KNOWN] ## Why

[KNOWN] The user asked to open a new OpenSpec change that lists the full ECC agent set, classifies each agent as `direct absorb`, `merge into existing`, `unsuitable`, or `needs rewrite`, and force-adds the ignored OpenSpec artifacts for this work.

[KNOWN] The previous `add-shared-agents-skills-qa-traceability` change absorbed ECC testing/QA taxonomy but did not vendor or fully port every ECC agent.

[INFERRED] A classification-first change reduces prompt bloat, role overlap, and unverified agent imports before any BUILD implementation.

[KNOWN] ## What Changes

[KNOWN] - Add an ECC agent inventory and classification artifact at `ecc-agents-classification.md`.
[KNOWN] - Add a requirement that ECC-style agent absorption must be classification-gated before BUILD.
[KNOWN] - Add a refined implementation-readiness package plan for the user-selected absorption set.
[KNOWN] - Track source ambiguity and evidence anchors for the ECC repository used as source of truth.
[KNOWN] - Keep implementation out of this DEFINE change unless the user later approves a BUILD package.

[KNOWN] ## Capabilities

[KNOWN] ### New Capabilities

[KNOWN] - `ecc-agent-assessment`: classification-gated upstream agent assessment before AILI/ROSE absorption.

[KNOWN] ### Modified Capabilities

[KNOWN] - None in this DEFINE package.

[KNOWN] ## Scope

[KNOWN] In scope:
[KNOWN] - Full ECC agent inventory from `affaan-m/ECC`.
[KNOWN] - Classification into direct absorb, merge into existing, unsuitable, and needs rewrite.
[KNOWN] - OpenSpec artifacts and validation.
[KNOWN] - Force-adding ignored OpenSpec artifacts that are task-scoped to this new change and the immediately preceding SHIP closeout change.
[KNOWN] - Selected future additions: `spec-miner`, `comment-accuracy-review`, `agent-evaluator`, `opensource-sanitizer`, `oss-release-readiness`, `build-failure-repair`, `code-review-quality-gates`, and `harness-optimization-audit`.
[KNOWN] - Review-quality prior-art sources for `code-review-quality-gates`: `sanyuan0704/sanyuan-skills` `code-review-expert`, `alirezarezvani/claude-skills` `code-reviewer`, and `laolaoshiren/claude-code-skills-zh` `zh-code-reviewer`.
[KNOWN] - All selected agents and skills will follow the existing default-installed workflow component model unless a later change introduces optional component packs.

[KNOWN] Out of scope:
[KNOWN] - Implementing new agents or skills.
[KNOWN] - Copying ECC prompt text into this repository.
[KNOWN] - Adding dedicated per-language agents in this package.
[KNOWN] - Adding `type-design-analyzer` in this package.
[KNOWN] - Pulling every ignored historical OpenSpec archive into git.
[KNOWN] - Changing runtime OpenCode configuration or installer behavior.

[KNOWN] ## Impact

[INFERRED] Likely BUILD follow-up files would be limited to selected `agents/*.md`, `.agents/skills/*`, `manifests/rose-aili.components.json`, README/setup docs, and targeted tests.

[INFERRED] The highest-risk category is `needs rewrite`, because those agents often encode tool/runtime/domain assumptions that need OpenCode/AILI adaptation before use.

[INFERRED] The selected additions cover the highest-value missing core lanes after removing specialized type-design review, and now include harness-level audit coverage.

[INFERRED] `code-review-quality-gates` should strengthen existing review/test behavior instead of creating another generic code-review agent.

[KNOWN] ## Non-Goals

[KNOWN] - Do not automatically absorb all ECC agents.
[KNOWN] - Do not introduce a language-agent swarm for TypeScript, Python, Go, Rust, Java, or framework-specific review in this package.
[KNOWN] - Do not add separate `code-review-expert`, upstream `code-reviewer`, or `zh-code-reviewer` agents.
[KNOWN] - Do not add new public lifecycle commands.
[KNOWN] - Do not weaken existing ROSE delegation, review, security, or verification gates.
[KNOWN] - Do not commit unrelated ignored OpenSpec history beyond the explicitly scoped artifacts.
