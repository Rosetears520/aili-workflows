# 测试文档：add-shared-agents-skills-qa-traceability

## 0. 文档元信息

- 来源：`/define` 用户输入、IDEATE 研究结果、本地 scout、DeerFlow public skills research、OpenSpec artifacts
- 生成时间：2026-06-29
- 适用版本 / 分支：`main`（用户已显式授权写 DEFINE artifacts on main）
- 测试负责人：ROSE / BUILD test lanes
- 状态：BUILD-final evidence reconciled; core automation/review gates passed, with residual CodeGraph/live-runtime/.playwright risks tracked below

## 1. 资料来源与证据

| 来源 | 已检查内容 | 观察到的事实 | 置信度 | 备注 |
|---|---|---|---|---|
| 用户输入 | DEFINE scope | `.agents/skills`、OpenCode 保留、QA agents+skills 全部加入、Code-Spec、本地 gap、DeerFlow public skills | high | 仍有策略问题需确认 |
| Local scout | installer / manifest / docs / tests / agents | 安装逻辑分散；AGENTS stale；无 `.agents`；QA agent 粒度不足 | high | CodeGraph unavailable |
| DeerFlow public skills research | `skills/public` taxonomy | 高适配 pattern 为 trigger/progressive disclosure/validation/research/report discipline | high | 不默认复制文本 |
| ECC research | QA/testing taxonomy | 可借鉴 coverage/PR test/E2E/browser/AI regression/silent failure lanes | high | 不默认批量 vendor |
| Code-Spec research | traceability workflow | 可借鉴 requirement → task → file → verification → coverage check | medium | 项目年轻，作为 pattern 而非成熟标准 |

## 2. 被测对象与测试目标

- 被测对象：AILI workflow harness install/package/docs/manifest/agents/skills/review pipeline/traceability/doctor behavior.
- 用户目标：跨工具共享 skills、保留 OpenCode 原生行为、补齐测试 agent+skill 分工、吸收 traceability 和 prior-art patterns、修复本地 stale/source-of-truth 问题。
- 技术目标：manifest-driven install source of truth；`.agents/skills` shared target；specialized QA lanes；traceability; CodeGraph readiness reporting.
- 不测试内容：真实第三方 provider/media generation、生产部署、外部 publishing、OpenCode core behavior changes、自动 CodeGraph init in DEFINE.

## 3. 测试范围

### In Scope

- Installer dry-run/real-plan behavior for `.agents/skills` and OpenCode-native targets.
- Manifest drift validation and package file inclusion.
- Doctor output for shared skills, native OpenCode targets, stale AGENTS facts, CodeGraph readiness.
- Added QA agents and skills: trigger boundaries, ownership, allowed tools, evidence output, routing.
- Review-pipeline integration for specialized QA lanes.
- Traceability requirements in DEFINE/BUILD/SHIP docs and test plans.
- Generated AGENTS freshness through template/check path.

### Out of Scope

- Actual external browser/E2E artifacts unless a repository-local path is approved.
- Unprovenanced copying of upstream DeerFlow/ECC/Code-Spec code/prompts.
- Automatic CodeGraph initialization.
- New public lifecycle commands.

### Assumptions

- User-confirmed strategy is full source migration: `.agents/skills` becomes canonical skill source, with OpenCode-native outputs preserved.
- User-confirmed strategy allows copying selected upstream content only with provenance/license handling and minimal AILI/OpenCode adaptation.

### Open Questions

- None blocking after filled `interview.md`; remaining items are BUILD-time verification risks.

## 4. 需求-测试追踪矩阵

| 需求 / 决策 / 风险 | 来源 | 测试点 | 测试类型 | 优先级 | 覆盖状态 |
|---|---|---|---|---|---|
| `.agents/skills` shared target while preserving OpenCode native | user + installer spec | install dry-run shows both shared and native targets; existing OpenCode behavior preserved | CLI/unit/integration | P0 | covered by BUILD-final; live runtime E2E remains residual |
| manifest source of truth | proposal/design | manifest drift tests fail on missing/mismatched component | unit/CLI | P0 | covered by BUILD-final |
| package includes intended canonical `.agents/skills` source and OpenCode outputs only | installer spec | `npm pack --dry-run` includes intended files and excludes runtime indexes/secrets | package | P0 | covered by BUILD-final |
| QA agents+skills added | user + QA spec | files exist, descriptions precise, routing ownership correct | static/read | P0 | covered by BUILD-final + review |
| QA lanes do not over-trigger | QA spec | near-miss/static checks or review-pipeline rules prevent always-on fanout | static/unit | P1 | covered structurally; live runtime routing remains residual |
| browser/E2E artifacts require placement | QA spec | agent/skill wording and tests enforce repository-local placement decision | static/review | P0 | covered by static/review evidence; no live artifacts created |
| Code-Spec traceability | lifecycle spec | tasks/test-plan/progress guidance maps req→task→file→verification | static/harness | P0 | covered by BUILD-final |
| AGENTS stale facts fixed | local evidence | `scripts/agents_md.py check --project .` passes and generated facts match repo | CLI | P0 | covered by BUILD-final |
| CodeGraph readiness | codegraph spec | doctor reports uninitialized as optional and does not claim graph evidence | unit/CLI/manual | P1 | covered for readiness reporting; graph-backed evidence remains unverified |
| upstream provenance-controlled absorption/copying | proposal/spec | copied/adapted upstream content has source/license/notice/provenance; clean-room items are labeled as such | diff/security review | P0 | covered by BUILD-final + review |

## 5. 测试策略

- 单元测试：TypeScript manifest/installer/doctor tests and static validation helpers.
- 集成测试：installer dry-run in temp dirs; package allowlist checks; doctor output checks.
- E2E / 浏览器测试：only if browser QA skill/agent changes require behavior checks and artifact placement is approved.
- API / 契约测试：OpenSpec strict validation and manifest schema/allowlist validation.
- 手工验收：review generated docs/agents/skills for trigger clarity, ownership, provenance, and traceability.
- 回归测试：existing install/config/DCP/CodeGraph tests plus AGENTS/harness checks.
- 非功能测试：security/provenance review for upstream-inspired content and artifact placement.

## 6. 测试环境与测试数据

- 环境：Linux/WSL repository checkout.
- 依赖服务：Node/npm for TypeScript/package tests; Python 3 for scripts; OpenSpec CLI if available; CodeGraph optional.
- 测试账号 / 权限：none expected; no production browser data.
- 测试数据：temporary install homes and fixture directories.
- 数据清理方式：temp dirs only for ephemeral tests; user-visible artifacts repository-local only after placement decision.

## 7. 功能测试用例

| ID | 场景 | 前置条件 | 步骤 | 预期结果 | 优先级 | 自动化建议 | 来源 |
|---|---|---|---|---|---|---|---|
| FT-01 | Install plan includes shared skills | manifest includes shared target | run installer dry-run | reports `.agents/skills` plus OpenCode-native target | P0 | automated | installer spec |
| FT-02 | OpenCode native preserved | existing OpenCode skills/agents/commands present | run install/dry-run | parent dirs preserved; native paths unchanged except repository-managed entries | P0 | automated | installer spec |
| FT-03 | Manifest drift detected | temp manifest/disk mismatch | run validation/test | mismatch fails or reports `Unverified` | P0 | automated | manifest requirement |
| FT-04 | QA agents registered | new agents/skills exist | run manifest/package/static checks | all new QA lanes are listed and installable | P0 | automated | QA spec |
| FT-05 | Review pipeline routes QA lanes selectively | representative change categories | inspect/run route tests if available | only relevant lanes selected; join contract required for fanout | P1 | static/unit | QA spec |
| FT-06 | AGENTS facts updated | generated source changed | run `python scripts/agents_md.py check --project .` | passes and no stale no-src/no-tests/no-CI claims | P0 | automated | AGENTS requirement |
| FT-07 | Doctor reports CodeGraph readiness | repo without `.codegraph` | run doctor or unit test | reports optional not initialized and follow-up command | P1 | automated/manual | CodeGraph spec |
| FT-08 | Traceability present | formal change docs updated | inspect tasks/test-plan/lifecycle docs | req→task→file→verification mapping present | P0 | static/review | lifecycle spec |

## 8. 异常、边界与权限测试

| ID | 类型 | 场景 | 输入 / 操作 | 预期结果 | 风险 |
|---|---|---|---|---|---|
| ET-01 | Conflict | user-owned `.agents/skills/<skill>` exists | install dry-run/install | preserve/backup/report; no parent dir replacement | data loss |
| ET-02 | Unsupported assumption | `.agent/` singular requested | docs/doctor/install behavior | recommends `.agents/skills`, marks `.agent` unsupported | wrong install target |
| ET-03 | Artifact placement | E2E/browser wants screenshot/trace | no approved path | ask/block; no OS-temp-only user artifact | lost artifacts |
| ET-04 | Upstream provenance | copied text accidentally appears | diff/review | block or add provenance only if approved | license/prompt conflict |
| ET-05 | CodeGraph absent | no `.codegraph` | doctor/planning | optional unavailable, no graph-backed claim | false evidence |

## 9. 数据一致性 / 迁移 / 兼容性测试

- Verify `.agents/skills` and OpenCode-native outputs do not diverge from manifest component definitions.
- Because source relocation is chosen, add migration checks for all old `skills/` references and package paths; any compatibility `skills/` output must be generated or non-authoritative.
- Verify `.gitignore` excludes `.codegraph/` and does not accidentally hide required shipped shared outputs unless intentionally generated.

## 10. 性能、稳定性、安全、可观测性测试

- Performance: install/package checks should not require expensive browser/E2E lanes by default.
- Stability: installer dry-runs should be idempotent.
- Security: no secrets, provider keys, third-party copied prompts/code, generated indexes, screenshots/traces, or production data are committed.
- Observability: doctor output separates core install, shared skill target, native OpenCode target, manifest drift, AGENTS freshness, CodeGraph readiness, and optional/skipped items.

## 11. 回归范围

- Existing install dry-run behavior.
- Existing DCP/OpenSpec optional config behavior.
- Existing CodeGraph install behavior tests.
- Existing manifest allowlist/package tests.
- Existing AGENTS template compliance.
- Existing four-command lifecycle and review-pipeline routing boundaries.

## 12. 自动化验证命令

| 层级 | 命令 | 目的 | 必须执行 | 备注 |
|---|---|---|---|---|
| OpenSpec | `openspec validate add-shared-agents-skills-qa-traceability --strict` | validate change artifacts | yes | after spec edits |
| Typecheck | `npm run typecheck` | TS type safety | yes if TS changes |  |
| Unit/CLI | `npm test` | installer/manifest/doctor tests | yes if source/tests change |  |
| Build | `npm run build` | package build | yes if TS/package changes |  |
| Shell | `bash -n scripts/install_opencode.sh` | Bash syntax | yes if Bash changes |  |
| Python | `python -m py_compile scripts/harness_fixture_check.py scripts/agents_md.py` | Python syntax | yes if scripts touched |  |
| Harness | `python scripts/harness_fixture_check.py` | harness fixture checks | yes if commands/skills refs touched |  |
| AGENTS | `python scripts/agents_md.py check --project .` | generated AGENTS compliance | yes if AGENTS/template touched |  |
| Delegation protocols | `python scripts/delegation_protocols_check.py` | subagent packet/result and delegation wording checks | yes if delegation protocols touched |  |
| Package | `npm pack --dry-run` | package file inclusion | yes if package/shared output changes | inspect output |
| Static review | final diff inspection | no upstream copied text/secrets/unrelated files | yes | include `.playwright-mcp/` untouched |

## 13. 手工验收清单

- [x] `.agents/skills` behavior is documented and tested without breaking OpenCode-native behavior. Residual: live OpenCode runtime session not exercised end-to-end.
- [x] Manifest is the clear component source of truth.
- [x] All requested QA agents and matching skills exist and have precise routing boundaries. Residual: live runtime routing not exercised end-to-end.
- [x] Code-Spec-style traceability appears in tasks/test-plan/progress/SHIP guidance.
- [x] `AGENTS.md` stale facts are fixed through generated-source path.
- [x] CodeGraph readiness is reported accurately and optional init remains explicit. Residual: CodeGraph index remains uninitialized.
- [x] DeerFlow/ECC/Code-Spec prior art is absorbed clean-room or copied/adapted only with provenance explicitly recorded.

## 14. Open Questions / Unverified

| 类型 | 内容 | 影响 | 处理方式 |
|---|---|---|---|
| Closed by BUILD evidence | `.agents/skills` source relocation, manifest/package behavior, QA lane additions, traceability docs, AGENTS freshness, and provenance recording | final files/automation/review now covered by `progress.txt` evidence | keep final PASS evidence; rerun listed commands if artifacts change |
| Residual risk | ignored OpenSpec tracking policy unchanged | change artifacts remain local/ignored unless separately tracked | report caveat; do not change `.gitignore` for `openspec/` in this change |
| Unverified | CodeGraph graph evidence | no graph locality until init | fallback reads/search; optional init later |
| Unverified | live OpenCode runtime discovery/routing | structural install/package/manifest tests passed, but no real OpenCode session E2E was run | treat as residual runtime validation risk |
| Unverified | existing `.playwright-mcp/` contents | intentionally not inspected or deleted | leave untouched unless separately scoped |

## 15. 测试执行记录

| Run ID | 时间 | 执行者 | 测试层级 | 命令 / 工具 | 结果 | 关键证据 | 未验证项 |
|---|---|---|---|---|---|---|---|
| BUILD-final | 2026-06-29 | ROSE | OpenSpec / Typecheck / Build / Unit / Shell / Python / Harness / AGENTS / Delegation / Package | `openspec validate add-shared-agents-skills-qa-traceability --strict`; `npm run typecheck`; `npm run build`; `npm test`; `bash -n scripts/install_opencode.sh`; `python -m py_compile scripts/harness_fixture_check.py scripts/agents_md.py scripts/delegation_protocols_check.py`; `python scripts/harness_fixture_check.py`; `python scripts/agents_md.py check --project .`; `python scripts/delegation_protocols_check.py`; `npm pack --dry-run` | PASS | `progress.txt` BUILD-final evidence; `npm test` 66 passed / 1 skipped | CodeGraph graph evidence unavailable; live OpenCode runtime routing structurally tested, not end-to-end executed |
| BUILD-review | 2026-06-29 | ROSE + review lanes | Code review / test review / security review | Read-only review lanes after repair | PASS | Follow-up code/test/security review rechecks returned PASS | Existing `.playwright-mcp/` contents intentionally not inspected or deleted; CodeGraph not initialized |
| SHIP-final | 2026-06-29 | ROSE | OpenSpec / Typecheck / Build / Unit / Shell / Python / Harness / AGENTS / Delegation / Package / Audit / Diff | `openspec validate add-shared-agents-skills-qa-traceability --strict`; `npm run typecheck`; `npm run build`; `npm test`; `bash -n scripts/install_opencode.sh`; `python -m py_compile scripts/harness_fixture_check.py scripts/agents_md.py scripts/delegation_protocols_check.py`; `python scripts/harness_fixture_check.py`; `python scripts/agents_md.py check --project .`; `python scripts/delegation_protocols_check.py`; `npm pack --dry-run`; `npm audit --omit=dev`; `git diff --check` | PASS | `npm test` 70 passed / 1 skipped; `npm audit --omit=dev` found 0 vulnerabilities; `ship-closeout.md` records closeout | CodeGraph graph evidence unavailable; live OpenCode runtime routing not end-to-end exercised; previous-release baseline not provided |

## 16. 缺陷与修复闭环

| Bug ID | 来源测试 | 现象 | 根因 | 修复负责人 | 修复文件 | 复测命令 | 复测结果 | 状态 |
|---|---|---|---|---|---|---|---|---|
| REVIEW-01 | Code review | `templates/AGENTS.md` became repo-specific though `scripts/agents_md.py init` copies it to target projects | Package 3 initially treated the reusable template as this repo's generated source | ROSE / repair lane | `templates/AGENTS.md`, `AGENTS.md`, tests/docs | `python scripts/agents_md.py check --project .`; follow-up code review | PASS | closed |
| REVIEW-02 | Test/security review | Missing selective symlink, QA routing, CodeGraph initialized, package tar, and OpenCode home traversal coverage | New `.agents/skills` migration and installer safety behavior needed targeted regressions | ROSE / repair lane | `tests/rose-aili.test.mjs`, `src/installer.ts`, `scripts/install_opencode.sh`, `.gitignore`, README/docs | Full final verification and follow-up test/security review | PASS | closed |

## 17. 变更记录

- 2026-06-29: Initial DEFINE test plan generated through `test-document-generator` contract.
- 2026-06-29: BUILD execution and review/repair evidence recorded after final verification passed.
- 2026-06-29: SHIP release-blocking repairs and final post-repair verification recorded; closeout created.
