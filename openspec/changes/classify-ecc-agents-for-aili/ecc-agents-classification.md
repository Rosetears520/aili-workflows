[KNOWN] # ECC Agents Classification

[KNOWN] Source selected for this inventory: `https://github.com/affaan-m/ECC`.
[KNOWN] Agents directory selected for this inventory: `https://github.com/affaan-m/ECC/tree/main/agents`.
[KNOWN] External research enumerated 67 Markdown agents from that source.
[KNOWN] Ambiguity: `https://github.com/sifxprime/kodelyth-ecc` appears to be a related candidate with a different agent count, but it is not the selected source for this artifact.

[KNOWN] ## Classification Summary

| Category | Count | Meaning |
|---|---:|---|
| [INFERRED] direct absorb | 2 | [INFERRED] Strong fit as a future AILI component with minimal adaptation |
| [INFERRED] merge into existing | 29 | [INFERRED] Useful behavior belongs in an existing AILI agent/skill |
| [INFERRED] needs rewrite | 24 | [INFERRED] Useful idea but needs OpenCode/AILI/domain/safety rewrite before use |
| [INFERRED] unsuitable | 12 | [INFERRED] Not aligned with this workflow repository or too domain-specific to carry |

[KNOWN] ## Full Inventory and Classification

| # | ECC agent | ECC purpose | Classification | AILI target / rationale |
|---:|---|---|---|---|
| 1 | [KNOWN] `a11y-architect` | [KNOWN] Accessibility/WCAG UI architecture | [INFERRED] merge into existing | [INFERRED] Merge into `frontend-ui-engineering`, `browser-qa`, and `test-coverage-reviewer` guidance |
| 2 | [KNOWN] `agent-evaluator` | [KNOWN] Evaluates agent output against quality rubric | [INFERRED] needs rewrite | [INFERRED] Could become a ROSE review/eval lane but needs AILI-specific rubric and no nested-agent assumptions |
| 3 | [KNOWN] `architect` | [KNOWN] System design and architecture decisions | [INFERRED] merge into existing | [INFERRED] Merge into `plan-auditor`, `api-and-interface-design`, and `planning-and-task-breakdown` |
| 4 | [KNOWN] `build-error-resolver` | [KNOWN] Build and TypeScript/type error fixes | [INFERRED] needs rewrite | [INFERRED] Useful as a debugging/build repair lane, but edit permissions and verification boundaries need AILI rewrite |
| 5 | [KNOWN] `chief-of-staff` | [KNOWN] Multi-channel communication triage/drafts | [INFERRED] unsuitable | [INFERRED] Not a coding workflow harness role |
| 6 | [KNOWN] `code-architect` | [KNOWN] Feature implementation architecture blueprints | [INFERRED] merge into existing | [INFERRED] Merge into `implementer`, `plan-auditor`, and `planning-and-task-breakdown` |
| 7 | [KNOWN] `code-explorer` | [KNOWN] Traces existing codebase behavior and dependencies | [INFERRED] merge into existing | [INFERRED] Covered by `code-scout` and CodeGraph evidence-provider guidance |
| 8 | [KNOWN] `code-reviewer` | [KNOWN] General quality/security/maintainability review | [INFERRED] merge into existing | [INFERRED] Covered by existing `code-reviewer`, `review-pipeline`, and `code-review-and-quality` |
| 9 | [KNOWN] `code-simplifier` | [KNOWN] Behavior-preserving simplification | [INFERRED] merge into existing | [INFERRED] Covered by `code-simplification` skill and review guidance |
| 10 | [KNOWN] `comment-analyzer` | [KNOWN] Comment accuracy and rot analysis | [INFERRED] direct absorb | [INFERRED] Strong candidate for a focused read-only review skill or subagent |
| 11 | [KNOWN] `conversation-analyzer` | [KNOWN] Transcript analysis for hook opportunities | [INFERRED] needs rewrite | [INFERRED] Could merge with `evidence-scoped-retrospective`, but raw transcript/privacy and hook policy need rewrite |
| 12 | [KNOWN] `cpp-build-resolver` | [KNOWN] C++/CMake/linker build fixes | [INFERRED] needs rewrite | [INFERRED] Keep as optional language-specific repair pattern only if repository demand appears |
| 13 | [KNOWN] `cpp-reviewer` | [KNOWN] C++ memory safety, idioms, concurrency, performance review | [INFERRED] needs rewrite | [INFERRED] Language-specific reviewer needs bounded trigger and safety evidence |
| 14 | [KNOWN] `csharp-reviewer` | [KNOWN] C#/.NET review | [INFERRED] needs rewrite | [INFERRED] Language-specific reviewer needs OpenCode/AILI adaptation |
| 15 | [KNOWN] `dart-build-resolver` | [KNOWN] Dart/Flutter build/analyzer/pub fixes | [INFERRED] merge into existing | [INFERRED] Merge build repair guidance into `flutter-dev` and `debugging-and-error-recovery` |
| 16 | [KNOWN] `database-reviewer` | [KNOWN] PostgreSQL/Supabase schema, SQL, migration review | [INFERRED] needs rewrite | [INFERRED] Security/schema migration gates make this useful but approval-sensitive |
| 17 | [KNOWN] `django-build-resolver` | [KNOWN] Django/Python setup, migration, dependency fixes | [INFERRED] needs rewrite | [INFERRED] Language/framework repair lane needs scoped trigger and dependency/migration gates |
| 18 | [KNOWN] `django-reviewer` | [KNOWN] Django/DRF/migration/security review | [INFERRED] needs rewrite | [INFERRED] Framework-specific reviewer can be folded into future backend skill if justified |
| 19 | [KNOWN] `doc-updater` | [KNOWN] Documentation and codemap updates | [INFERRED] merge into existing | [INFERRED] Covered by `documentation-and-adrs`, `doc-researcher`, and implementation closeout rules |
| 20 | [KNOWN] `docs-lookup` | [KNOWN] Current library/API documentation lookup | [INFERRED] merge into existing | [INFERRED] Covered by `source-driven-development`, Context7, and `web-researcher` |
| 21 | [KNOWN] `e2e-runner` | [KNOWN] End-to-end testing with browser/Playwright | [INFERRED] merge into existing | [INFERRED] Already covered by `e2e-artifact-runner`, `browser-qa-runner`, and matching skills |
| 22 | [KNOWN] `fastapi-reviewer` | [KNOWN] FastAPI review | [INFERRED] needs rewrite | [INFERRED] Framework-specific reviewer should be optional and evidence-gated |
| 23 | [KNOWN] `flutter-reviewer` | [KNOWN] Flutter/Dart review | [INFERRED] merge into existing | [INFERRED] Merge into `flutter-dev` review/testing guidance |
| 24 | [KNOWN] `fsharp-reviewer` | [KNOWN] F# functional code review | [INFERRED] unsuitable | [INFERRED] Too niche for this workflow repo without demonstrated demand |
| 25 | [KNOWN] `gan-evaluator` | [KNOWN] GAN harness evaluator using Playwright/rubric | [INFERRED] unsuitable | [INFERRED] GAN-specific harness does not match AILI workflow scope |
| 26 | [KNOWN] `gan-generator` | [KNOWN] GAN harness feature generator | [INFERRED] unsuitable | [INFERRED] GAN-specific generation is out of scope |
| 27 | [KNOWN] `gan-planner` | [KNOWN] GAN harness product/spec planner | [INFERRED] unsuitable | [INFERRED] GAN-specific planning is out of scope |
| 28 | [KNOWN] `go-build-resolver` | [KNOWN] Go build/vet/lint fixes | [INFERRED] needs rewrite | [INFERRED] Language-specific build repair needs trigger and verification design |
| 29 | [KNOWN] `go-reviewer` | [KNOWN] Go review | [INFERRED] needs rewrite | [INFERRED] Language-specific reviewer should not be imported without demand |
| 30 | [KNOWN] `harmonyos-app-resolver` | [KNOWN] HarmonyOS/ArkTS/ArkUI review | [INFERRED] unsuitable | [INFERRED] Too platform-specific for current AILI workflow scope |
| 31 | [KNOWN] `harness-optimizer` | [KNOWN] Local agent harness reliability/cost/throughput tuning | [INFERRED] merge into existing | [INFERRED] Merge into `harness-evolution`, `harness-issue-triage`, and `darwin-skill` style evaluation |
| 32 | [KNOWN] `healthcare-reviewer` | [KNOWN] Healthcare/PHI/clinical safety review | [INFERRED] unsuitable | [INFERRED] Domain compliance role is inappropriate for this generic workflow repo |
| 33 | [KNOWN] `homelab-architect` | [KNOWN] Home/small-lab network plans | [INFERRED] unsuitable | [INFERRED] Not aligned with repository purpose |
| 34 | [KNOWN] `java-build-resolver` | [KNOWN] Java/Maven/Gradle/Spring/Quarkus build fixes | [INFERRED] needs rewrite | [INFERRED] Language/framework repair lane needs opt-in and command evidence rules |
| 35 | [KNOWN] `java-reviewer` | [KNOWN] Java/Spring/Quarkus review | [INFERRED] needs rewrite | [INFERRED] Language-specific reviewer needs future demand signal |
| 36 | [KNOWN] `kotlin-build-resolver` | [KNOWN] Kotlin/Gradle build fixes | [INFERRED] merge into existing | [INFERRED] Merge into `android-native-dev` and debugging guidance |
| 37 | [KNOWN] `kotlin-reviewer` | [KNOWN] Kotlin/Android/KMP review | [INFERRED] merge into existing | [INFERRED] Merge into `android-native-dev` review guidance |
| 38 | [KNOWN] `loop-operator` | [KNOWN] Autonomous agent loop operation | [INFERRED] needs rewrite | [INFERRED] Autonomy loops are high-risk and must map to ROSE lifecycle gates |
| 39 | [KNOWN] `marketing-agent` | [KNOWN] Campaign, positioning, copy, launch marketing | [INFERRED] merge into existing | [INFERRED] Merge limited content workflow ideas into `newsletter-generation` or `shipping-and-launch` only if requested |
| 40 | [KNOWN] `mle-reviewer` | [KNOWN] Production ML/MLOps review | [INFERRED] needs rewrite | [INFERRED] Useful only as optional domain reviewer with data/model safety gates |
| 41 | [KNOWN] `network-architect` | [KNOWN] Enterprise/multi-site network architecture | [INFERRED] unsuitable | [INFERRED] Not aligned with this workflow repo |
| 42 | [KNOWN] `network-config-reviewer` | [KNOWN] Router/switch config review | [INFERRED] unsuitable | [INFERRED] Domain-specific and not part of AILI workflow scope |
| 43 | [KNOWN] `network-troubleshooter` | [KNOWN] Network diagnosis/root-cause analysis | [INFERRED] unsuitable | [INFERRED] Domain-specific operations role is out of scope |
| 44 | [KNOWN] `opensource-forker` | [KNOWN] Prepare sanitized open-source fork | [INFERRED] needs rewrite | [INFERRED] Useful release pattern but high-risk because it can delete/sanitize files and affect publication |
| 45 | [KNOWN] `opensource-packager` | [KNOWN] Generate OSS packaging/docs/templates | [INFERRED] needs rewrite | [INFERRED] Could merge into `shipping-and-launch`, but packaging/publication gates need rewrite |
| 46 | [KNOWN] `opensource-sanitizer` | [KNOWN] Scan sanitized repo before public release | [INFERRED] needs rewrite | [INFERRED] Useful security/release review lane but needs strict non-destructive evidence contract |
| 47 | [KNOWN] `performance-optimizer` | [KNOWN] Bottleneck/performance optimization | [INFERRED] merge into existing | [INFERRED] Covered by `performance-optimization` skill |
| 48 | [KNOWN] `php-reviewer` | [KNOWN] PHP/Laravel/Eloquent/security review | [INFERRED] needs rewrite | [INFERRED] Language/framework reviewer needs future demand signal |
| 49 | [KNOWN] `planner` | [KNOWN] Complex feature/refactor planning | [INFERRED] merge into existing | [INFERRED] Covered by `plan-auditor`, `planning-and-task-breakdown`, and lifecycle planning gates |
| 50 | [KNOWN] `pr-test-analyzer` | [KNOWN] PR test coverage quality review | [INFERRED] merge into existing | [INFERRED] Already absorbed as `pr-test-analyzer` |
| 51 | [KNOWN] `python-reviewer` | [KNOWN] Python review | [INFERRED] needs rewrite | [INFERRED] Could be useful but should be framework-agnostic and demand-gated |
| 52 | [KNOWN] `pytorch-build-resolver` | [KNOWN] PyTorch/CUDA/training runtime fixes | [INFERRED] unsuitable | [INFERRED] Too domain-specific for this workflow repo |
| 53 | [KNOWN] `react-build-resolver` | [KNOWN] React/Vite/Next/webpack build fixes | [INFERRED] merge into existing | [INFERRED] Merge into frontend build/debugging guidance rather than a separate always-installed agent |
| 54 | [KNOWN] `react-reviewer` | [KNOWN] React hooks/render/a11y/security review | [INFERRED] merge into existing | [INFERRED] Merge into `frontend-ui-engineering`, `frontend-dev`, and `code-reviewer` |
| 55 | [KNOWN] `refactor-cleaner` | [KNOWN] Dead code and duplicate cleanup | [INFERRED] merge into existing | [INFERRED] Covered by `code-simplification`, but cleanup must remain task-scoped |
| 56 | [KNOWN] `rust-build-resolver` | [KNOWN] Rust/Cargo/borrow-checker build fixes | [INFERRED] needs rewrite | [INFERRED] Language-specific repair lane needs future demand signal |
| 57 | [KNOWN] `rust-reviewer` | [KNOWN] Rust ownership/lifetime/unsafe review | [INFERRED] needs rewrite | [INFERRED] Language-specific reviewer needs future demand signal |
| 58 | [KNOWN] `security-reviewer` | [KNOWN] Vulnerability detection/remediation | [INFERRED] merge into existing | [INFERRED] Covered by `security-auditor` and `security-and-hardening` |
| 59 | [KNOWN] `seo-specialist` | [KNOWN] SEO audits, metadata, schema, Core Web Vitals | [INFERRED] merge into existing | [INFERRED] Merge into frontend/marketing only when web content tasks require it |
| 60 | [KNOWN] `silent-failure-hunter` | [KNOWN] Swallowed errors and bad fallbacks review | [INFERRED] merge into existing | [INFERRED] Already absorbed as `silent-failure-reviewer` and `silent-failure-hunting` |
| 61 | [KNOWN] `spec-miner` | [KNOWN] Extract OpenSpec-style behavioral specs from code | [INFERRED] direct absorb | [INFERRED] Strong fit for read-only spec recovery before DEFINE/BUILD |
| 62 | [KNOWN] `swift-build-resolver` | [KNOWN] Swift/Xcode/SPM build fixes | [INFERRED] merge into existing | [INFERRED] Merge into `ios-application-dev` debugging/build guidance |
| 63 | [KNOWN] `swift-reviewer` | [KNOWN] Swift/concurrency/ARC/protocol review | [INFERRED] merge into existing | [INFERRED] Merge into `ios-application-dev` review guidance |
| 64 | [KNOWN] `tdd-guide` | [KNOWN] TDD and coverage guidance | [INFERRED] merge into existing | [INFERRED] Covered by `test-driven-development`, `test-engineer`, and lifecycle verification gates |
| 65 | [KNOWN] `type-design-analyzer` | [KNOWN] Type design and invariant analysis | [INFERRED] merge into existing | [INFERRED] User removed this specialized code-review agent from the selected package; keep type/invariant checks inside existing `code-reviewer` and `api-and-interface-design` unless future demand appears |
| 66 | [KNOWN] `typescript-reviewer` | [KNOWN] TypeScript/JavaScript review | [INFERRED] merge into existing | [INFERRED] Merge into `code-reviewer`, `source-driven-development`, and TypeScript test gates |
| 67 | [KNOWN] `vue-reviewer` | [KNOWN] Vue/Nuxt/Pinia review | [INFERRED] needs rewrite | [INFERRED] Framework-specific reviewer should be optional and demand-gated |

[KNOWN] ## Updated Absorption Recommendation

[KNOWN] The user selected a bounded package that adds `spec-miner`, `comment-accuracy-review`, `agent-evaluator`, `opensource-sanitizer`, `oss-release-readiness`, `build-failure-repair`, `code-review-quality-gates`, and `harness-optimization-audit`; dedicated per-language agents, `type-design-analyzer`, and duplicate general code-review agents are out of scope for this package.

[KNOWN] All selected agents and skills are intended to be default-installed workflow components.

| Priority | Add / update | Kind | Source ECC agent(s) | Recommendation |
|---|---|---|---|---|
| [INFERRED] P0 | `spec-miner` | agent | `spec-miner` | [INFERRED] Add as read-only reverse-spec-mining lane before DEFINE/BUILD when existing code/tests/docs need behavior extraction |
| [INFERRED] P0 | `comment-accuracy-review` | skill | `comment-analyzer` | [INFERRED] Add as focused skill rather than default agent to avoid over-triggering a narrow concern |
| [INFERRED] P1 | `agent-evaluator` | agent | `agent-evaluator` | [INFERRED] Add as read-only output-quality and evidence-quality evaluator for agent/subagent/harness work |
| [INFERRED] P1 | `opensource-sanitizer` | agent | `opensource-sanitizer` | [INFERRED] Add as read-only public-release/package exposure reviewer; prohibit destructive cleanup and secret disclosure |
| [INFERRED] P1 | `oss-release-readiness` | skill | `opensource-sanitizer`, `opensource-packager` | [INFERRED] Add non-destructive release/readiness checklist; exclude `opensource-forker` behavior |
| [INFERRED] P1 | `build-failure-repair` | skill | `build-error-resolver` | [INFERRED] Add root-cause-first minimal repair workflow; implementation still routes through approved edit lanes |
| [INFERRED] P1 | `code-review-quality-gates` | skill | `sanyuan code-review-expert`, `alirezarezvani code-reviewer`, `zh-code-reviewer` | [INFERRED] Add review rubric/output-contract/test-enhancement skill; strengthen existing `code-reviewer`, `review-pipeline`, `test-engineer`, and fixtures instead of adding duplicate reviewer agents |
| [INFERRED] P1 | `harness-optimization-audit` | skill | `harness-optimizer` | [INFERRED] Add report-first audit of routing, trigger noise, token/context cost, parallelism, review fan-out, false PASS risk, and evidence quality; approved edits still route through `harness-evolution` |

[KNOWN] ## Recommended BUILD Packages If Approved Later

[INFERRED] Package A: shared scaffold and source-of-truth updates for manifest, README/provenance, ROSE routing boundaries, fixture/test expectations, and OpenSpec progress tracking.
[INFERRED] Package B: read-only agent `spec-miner`.
[INFERRED] Package C: skill `comment-accuracy-review`.
[INFERRED] Package D: read-only agents `agent-evaluator` and `opensource-sanitizer`.
[INFERRED] Package E: skills `oss-release-readiness` and `build-failure-repair`.
[INFERRED] Package F: skill `code-review-quality-gates`, plus review/test fixture and golden-output expectations.
[INFERRED] Package G: skill `harness-optimization-audit`.
[INFERRED] Package H: integration, trigger validation, review-pipeline/lifecycle docs, manifest drift tests, and closeout evidence.

[INFERRED] Not missing for this package: no mandatory ECC testing lane remains excluded after adding `agent-evaluator`, `build-failure-repair`, and `code-review-quality-gates` as selected components.
[INFERRED] Deferred optional follow-ups: `type-design-analyzer`, language-specific reviewers, and `database-change-review` if future project demand appears.
