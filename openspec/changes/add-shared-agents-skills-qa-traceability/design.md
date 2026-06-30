## Overview

This change turns the IDEATE findings into an implementation-ready contract for a cross-tool shared skills layer, stronger installation source-of-truth behavior, specialized testing/QA lanes, traceability, local docs freshness, and CodeGraph readiness.

The design intentionally keeps AILI as an OpenCode workflow harness rather than a DeerFlow-style agent runtime. External projects are used as prior-art evidence, and selected skill content may be copied only under explicit provenance/license handling with minimal AILI/OpenCode adaptation.

## Current Evidence

- OpenCode and several other tools support `.agents/skills` or similar plural `.agents` skill paths; `.agent/` singular is not a broad standard.
- Local installer surfaces are split across Bash (`scripts/install_opencode.sh`), TypeScript (`src/installer.ts`, `src/manifest.ts`, `src/doctor.ts`), manifest (`manifests/rose-aili.components.json`), docs, package metadata, and tests.
- Local `AGENTS.md` is generated but stale: it claims no `src/`, no tracked tests, no CI, and no package manager while `src/`, `tests/`, `.github/workflows`, and `package.json` exist.
- Current QA lanes include a broad `test-engineer` plus review/security agents and testing skills; there are no dedicated agents for coverage review, PR test analysis, AI regression, silent failure hunting, browser QA, or E2E artifact handling.
- CodeGraph status for this repository reports not initialized.
- DeerFlow public skills show useful patterns: concrete trigger descriptions, progressive disclosure through references/scripts/templates/evals, skill validation loops, evidence-first research, synthesis over source listing, and explicit report/data authenticity discipline.
- Code-Spec-Plugin shows useful task traceability: requirement/spec → task → files → verification → coverage report.

## Proposed Design

### 1. Shared `.agents/skills` source with OpenCode preserved

AILI should migrate repository-managed skill source into `.agents/skills` while preserving OpenCode-native install behavior. The accepted implementation direction is:

- keep one repository-managed source of component metadata in the manifest;
- treat `.agents/skills` as the canonical skills source tree;
- install, generate, or copy adapted OpenCode-native skill outputs from that source where OpenCode expects them;
- continue installing OpenCode skills, agents, commands, and plugins into OpenCode-native locations exactly as before;
- make install/doctor report both native and shared target status;
- avoid symlink-only assumptions because Windows/WSL and tool-specific file watching can behave differently.

BUILD must update all references, package inclusion, checks, and docs so the source relocation does not leave stale `skills/` assumptions. If a compatibility mirror remains under `skills/`, it must be generated or clearly non-authoritative.

### 2. Manifest as stronger source of truth

The manifest should stop being only an allowlist. It should describe, at minimum:

- component id, kind, source path, default install state, required/optional status;
- supported harness targets such as OpenCode native, shared Agent Skills, Claude/Codex/Gemini/Goose/Cursor-compatible future adapters;
- generated output path(s), install mode, conflict behavior, dependencies, stability, and provenance;
- validation expectations for package allowlists and docs count consistency.

The Bash installer should not remain the only place that decides which directories are installed by globbing disk. BUILD should converge Bash, TypeScript, docs, package metadata, and tests on the manifest contract.

### 3. QA/testing agents + skills

Add all requested specialized testing agents and corresponding skills in one change scope:

- `test-coverage-reviewer`: maps changed behavior to tests and assertions; read-only review by default.
- `pr-test-analyzer`: PR/change-level test quality analysis; checks meaningful assertions, edge cases, and regression scope.
- `ai-regression-scout`: looks for AI-specific failure modes such as mock/prod drift, API shape mismatch, stale optimistic UI rollback, error-state leakage, and sandbox/real path divergence.
- `silent-failure-reviewer`: finds swallowed errors, unsafe fallbacks, missing propagation, async/background failures, and misleading success reports.
- `browser-qa-runner`: exercises browser/UI behavior with console/network/a11y/manual evidence; must respect project artifact placement and avoid production data mutation.
- `e2e-artifact-runner`: owns E2E journey execution and artifacts such as screenshots/traces/videos where a repository-local placement is approved.

Each agent should have a matching skill or compact skill workflow so ROSE can route either by subagent lane or by skill guidance. Review-pipeline integration should trigger only relevant lanes rather than always running every QA agent on every change.

### 4. Code-Spec-style traceability

AILI artifacts should make traceability explicit:

```text
requirement / decision / risk
→ task / package
→ file or artifact touched
→ verification command or inspection
→ evidence / unverified item
```

DEFINE should include this mapping in specs/tasks/test-plan. BUILD should preserve it in `progress.txt` and worker packets. SHIP should run a spec coverage check before readiness claims.

### 5. Generated AGENTS freshness

Because project `AGENTS.md` is generated, BUILD should update the source template/check path rather than hand-editing only the generated file. The check should catch stale claims about `src/`, tracked tests, CI, package manager, package scripts, and generated/runtime outputs.

### 6. CodeGraph readiness boundary

CodeGraph should remain optional. Doctor and setup guidance should report when the current repository is not initialized and offer the safe command path only after root confirmation:

```text
codegraph init -i
codegraph status
```

DEFINE/BUILD/SHIP must not claim graph-backed evidence when the index is missing. Missing CodeGraph is a blocker only when the task requires graph confidence and fallback evidence is insufficient.

### 7. DeerFlow public skill absorption

Absorb selected DeerFlow public skills and patterns with provenance discipline. The confirmed in-scope set is:

- workflow/meta/research/report/data-authenticity patterns from `skill-creator`, `deep-research`, `github-deep-research`, `code-documentation`, `consulting-analysis`, `data-analysis`, and `chart-visualization`;
- `academic-paper-review`;
- `systematic-literature-review`;
- `newsletter-generation`;
- `frontend-design` anti-generic UI rules only, excluding DeerFlow branding requirements;
- `web-design-guidelines` UI audit ideas.

The absorption rules are:

- concise trigger descriptions with positive and near-miss examples;
- progressive disclosure: compact `SKILL.md`, details in `references/`, executable helpers in `scripts/`, templates/evals where useful;
- skill validation loop: realistic prompts, baseline comparison, trigger tests, and iteration;
- research synthesis discipline: source quality, dates, confidence, disagreements, gaps, and no fabricated data;
- report-first and data authenticity discipline for consulting/research/data/chart workflows.

When content is copied or closely paraphrased, BUILD must preserve license/notice/provenance and adapt only the DeerFlow-specific placeholders, tool names, paths, or branding required for AILI/OpenCode fit. Do not adopt DeerFlow runtime assumptions such as `/mnt/user-data`, `present_files`, provider-specific media tools, or DeerFlow branding.

## Alternatives Considered

- Use `.agent/` singular as the universal home: rejected because evidence does not support it as a broad standard.
- Keep `skills/` as canonical source and generate `.agents/skills`: rejected by user; accepted direction is a full source migration to `.agents/skills` with OpenCode-native output preserved.
- Import ECC/DeerFlow prompts wholesale without provenance: rejected. User approved copying only with provenance and minimal AILI/OpenCode adaptation.
- Keep one generic `test-engineer`: rejected because the user explicitly asked for all testing agents+skills and prior art supports finer QA lanes.
- Initialize CodeGraph during DEFINE: rejected because DEFINE is not implementation/setup execution and CodeGraph init is a project-local command with its own confirmation boundary.

## Risks and Mitigations

- Risk: agent proliferation causes over-triggering. Mitigation: precise descriptions, should-trigger/should-not-trigger evals, and review-pipeline relevance gates.
- Risk: `.agents/skills` and OpenCode native skills drift. Mitigation: manifest source of truth plus generated/copy verification.
- Risk: upstream prompt copying creates license/provenance issues. Mitigation: clean-room pattern extraction by default and explicit derivative policy if copying is requested.
- Risk: browser/E2E agents create user-visible artifacts in unapproved locations. Mitigation: require repository-local placement decisions and artifact contract checks.
- Risk: stale AGENTS facts continue to mislead agents. Mitigation: generated-source update plus checks.
- Risk: CodeGraph readiness is overclaimed. Mitigation: doctor status and explicit `Unverified` labels when graph evidence is absent.

## Rollback Plan

Revert manifest/install target additions, remove newly added QA agents/skills, revert traceability wording, and restore prior installer/package/test behavior. Because `.agents/skills` should be generated or manifest-controlled, rollback should remove generated shared outputs without affecting OpenCode-native installations.
