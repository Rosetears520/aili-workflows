# 测试文档：add-ship-release-blocker-audit

## 0. 文档元信息

- 来源：`openspec/changes/add-ship-release-blocker-audit/`
- 生成时间：2026-05-17
- 适用版本 / 分支：`define/context-saving-delegation-proposal`
- 测试负责人：ROSE / user confirmed 2026-05-17
- 状态：accepted for BUILD

## 1. 资料来源与证据

| 来源 | 已检查内容 | 观察到的事实 | 置信度 | 备注 |
|---|---|---|---|---|
| `proposal.md` | proposed scope | 本变更增强 `/ship` release-blocker audit，不新增 public top-level command | high | 本文档覆盖该 scope |
| `design.md` | design decisions | 默认 target 为 current change/final diff；baseline/full-codebase 需要显式输入或风险触发 | high | 用户已确认推荐默认答案 |
| `specs/aili-four-command-lifecycle/spec.md` | delta requirements | 新增 SHIP blocker audit、target selection、finding classification、internal-stage boundary | high | 可映射为验收用例 |
| `commands/ship.md` | current command | 已有 evidence freshness、review/repair、release-readiness hard stops | high | 需要验证文案增强后仍保留 hard stops |
| `skills/aili-delivery-flow/references/lifecycle.md` | SHIP lifecycle | 现有 SHIP hard stop 禁止 stale/missing evidence ready claim | high | 需要验证新增 audit 不削弱该 gate |
| `skills/aili-delivery-flow/references/review-repair-loop.md` | review/repair gates | SHIP 已 rerun stale/scope-affected lanes 并产生 closeout | high | 需要验证 blocker 分类加入此流程 |
| `docs/harness/command-lifecycle.md` | command set | 当前 docs 只允许四个 public command，review/repair 是 internal stages | high | 需要回归验证未新增命令 |

## 2. 被测对象与测试目标

- 被测对象：`/ship` command contract and AILI SHIP lifecycle docs/specs.
- 用户目标：在发版前明确检查 release-blocking bugs/risks，而不是只泛称 release-readiness。
- 业务目标：降低使用受影响、安全隐患、数据风险、流程破坏、证据过期时仍 claim ready 的概率。
- 技术目标：将 blocker audit 作为 SHIP 内部阶段，保持四命令 lifecycle 和 fresh evidence gate。
- 不测试内容：真实生产发版、真实 GitHub PR/release 创建、整库 bug 全证明、自动化安全扫描工具开发。

## 3. 测试范围

### In Scope

- `/ship` command wording includes release-blocker audit and supported target scopes.
- SHIP lifecycle references define audit freshness, blocking categories, and `Unverified` handling.
- Review/repair loop classifies findings and reruns stale/scope-affected lanes.
- Docs keep the four-command-only public surface.
- OpenSpec delta validates with strict mode.

### Out of Scope

- Adding a new public command.
- Adding a new skill unless later approved by a separate DEFINE/BUILD decision.
- Dependency, lockfile, memory schema, installer, or runtime automation changes.
- Exhaustive proof that the whole codebase has no bugs.

### Assumptions

- `openspec validate` is available in the current environment.
- Existing harness smoke checks remain the strongest local verification for command/lifecycle contract drift.

### Confirmed Decisions

- 2026-05-17: User confirmed the recommended defaults in `interview.md` and accepted this `test-plan.md` for `/build`.

## 4. 需求-测试追踪矩阵

| 需求 / 决策 / 风险 | 来源 | 测试点 | 测试类型 | 优先级 | 覆盖状态 |
|---|---|---|---|---|---|
| SHIP release-blocker audit | `specs/aili-four-command-lifecycle/spec.md` | `/ship` and lifecycle docs explicitly name blocker audit and blocker categories | Static doc/spec inspection | P0 | planned |
| Audit target selection | `design.md`, spec | Current diff/change default is documented; baseline/full-codebase are explicit/requested or risk-triggered | Static inspection + scenario review | P0 | planned |
| Finding classification | spec | Findings can be classified as `release-blocking`, `important`, `accepted risk`, `out-of-scope`, `Unverified` | Static inspection | P0 | planned |
| Fresh-evidence gate | current SHIP hard stops | Stale BUILD evidence cannot support ready claim | Static inspection + fixture smoke check | P0 | planned |
| No new public command | docs/harness contract | `commands/` remains only ideate/define/build/ship | File list / static inspection | P0 | planned |
| Harness docs consistency | README/docs | User-facing docs describe `/ship` consistently | Static inspection | P1 | planned |

## 5. 测试策略

- 单元测试：N/A; this is Markdown/configured workflow contract.
- 集成测试：OpenSpec strict validation and harness fixture checks.
- E2E / 浏览器测试：N/A.
- API / 契约测试：OpenSpec delta requirements and command lifecycle contract inspection.
- 手工验收：Read `/ship` output contract and verify it can answer “what would block release?” for a selected target.
- 回归测试：Four-command-only command surface and no stale evidence ready claim.
- 非功能测试：Security/trust wording review for release-blocking categories.

## 6. 测试环境与测试数据

- 环境：local repository checkout under OpenCode on Linux/WSL.
- 依赖服务：none.
- 测试账号 / 权限：none.
- 测试数据：OpenSpec change artifacts and Markdown command/skill docs.
- 数据清理方式：N/A; no runtime data is created.

## 7. 功能测试用例

| ID | 场景 | 前置条件 | 步骤 | 预期结果 | 优先级 | 自动化建议 | 来源 |
|---|---|---|---|---|---|---|---|
| TC-FUNC-001 | `/ship` current change audit | Implementation updates are present | Inspect `commands/ship.md` | Command explicitly routes to SHIP and names release-blocker audit for selected/current scope | P0 | Static check | spec |
| TC-FUNC-002 | Baseline comparison missing baseline | User asks previous-release comparison without baseline | Inspect hard stop / target selection text | The flow asks for baseline or marks baseline audit `Open Question` / `Unverified` | P0 | Static check | spec |
| TC-FUNC-003 | Whole-codebase audit bounded | User requests whole-codebase audit | Inspect lifecycle/review docs | Output must include scanned scope, evidence, skipped lanes, residual `Unverified`; no exhaustive safety claim | P0 | Static check | spec |
| TC-FUNC-004 | Finding classification | Review/test/security findings exist | Inspect review-repair loop | Findings use required classifications before ready verdict | P0 | Static check | spec |
| TC-FUNC-005 | Internal stage boundary | User wants separate audit command | Inspect commands/docs | No new public command is introduced; `/ship` remains entrypoint | P0 | File list + static check | docs/spec |

## 8. 异常、边界与权限测试

| ID | 类型 | 场景 | 输入 / 操作 | 预期结果 | 风险 |
|---|---|---|---|---|---|
| TC-EDGE-001 | Stale evidence | BUILD evidence is stale after scope change | Inspect SHIP hard stops | Rerun affected lane or mark claim `Unverified` | False ready claim |
| TC-EDGE-002 | Security exposure | SHIP finds permission/security risk | Inspect blocker category text | Security exposure can be release-blocking | Security regression |
| TC-EDGE-003 | Unsafe workflow | Audit finds destructive/unsafe operation risk | Inspect blocker category text | Unsafe workflow behavior can block ready | Irreversible workflow damage |
| TC-EDGE-004 | Ambiguous target | Multiple plausible targets exist | Inspect target selection rule | Ask user or choose narrow default and mark broader scope not audited | Wrong scope reviewed |

## 9. 数据一致性 / 迁移 / 兼容性测试

- No database or data migration expected.
- Compatibility check: existing `/ideate`, `/define`, `/build`, `/ship` command names remain unchanged.
- Archive/sync check after implementation: OpenSpec main spec receives the new requirements only through approved archive/sync flow.

## 10. 性能、稳定性、安全、可观测性测试

- Performance: ensure default `/ship` audit does not imply whole-codebase scan unless requested or risk-triggered.
- Stability: ensure stale evidence cannot be reused silently after changed scope.
- Security: ensure security exposure, permissions, secrets/tool policy, and unsafe operations are listed as blocker categories when applicable.
- Observability: closeout should report target, evidence, blockers, skipped checks, and `Unverified` items.

## 11. 回归范围

- `commands/ship.md`
- `commands/{ideate,define,build}.md` for command-surface regression only if files are touched or command count changes.
- `skills/aili-delivery-flow/references/lifecycle.md`
- `skills/aili-delivery-flow/references/review-repair-loop.md`
- `skills/aili-delivery-flow/references/artifact-contracts.md` or closeout protocols if touched.
- `docs/harness/command-lifecycle.md`, `docs/harness/aili-harness-contract.md`, `README.md` if touched.

## 12. 自动化验证命令

| 层级 | 命令 | 目的 | 必须执行 | 备注 |
|---|---|---|---|---|
| Contract | `openspec validate "add-ship-release-blocker-audit" --strict` | Validate OpenSpec delta | yes | Run after DEFINE and after implementation |
| CLI smoke | `python scripts/harness_fixture_check.py` | Check harness fixture expectations | yes | Run after implementation |
| Template check | `python scripts/agents_md.py check --project .` | Check AGENTS template compliance | no | Only required if AGENTS/template rules are touched |
| Diff hygiene | `git diff --check` | Detect whitespace and patch hygiene issues | yes | Run after implementation |
| Scope review | `git diff --name-only` | Confirm files are in approved scope | yes | Include ignored OpenSpec note if needed |

## 13. 手工验收清单

- [ ] `/ship` answers which target was audited.
- [ ] `/ship` can report release-blocking user-impacting bugs and security risks.
- [ ] `/ship` does not claim ready when evidence is stale or missing.
- [ ] `/ship` marks baseline/full-codebase gaps as `Open Question` or `Unverified` when needed.
- [ ] No new public top-level command is introduced.
- [ ] Residual risks and skipped checks are explicit in closeout.

## 14. Open Questions / Unverified

| 类型 | 内容 | 影响 | 处理方式 |
|---|---|---|---|
| Confirmed decision | Default audit target is current resolved change / final diff; broader scans need explicit request or risk trigger | Sets command/lifecycle wording | Reflected in implementation docs |
| Confirmed decision | Missing previous-release baseline must be requested or marked `Open Question` / `Unverified`; do not guess | Blocks ambiguous baseline comparison | Reflected in implementation docs |
| Confirmed decision | Closeout gets a concise release-blocker audit field | Adds protocol/artifact-contract wording | Reflected in implementation docs |
| Unverified | Whole-codebase scans cannot prove absence of all bugs | Prevents absolute safety claims | Report scope and residual `Unverified` |

## 15. 测试执行记录

| Run ID | 时间 | 执行者 | 测试层级 | 命令 / 工具 | 结果 | 关键证据 | 未验证项 |
|---|---|---|---|---|---|---|---|
| RUN-2026-05-17-01 | 2026-05-17 | ROSE | Contract | `openspec validate "add-ship-release-blocker-audit" --strict` | pass | OpenSpec change is valid after implementation | None |
| RUN-2026-05-17-02 | 2026-05-17 | ROSE | CLI smoke | `python scripts/harness_fixture_check.py` | pass | `harness fixture check: PASS (5 fixture files + command contracts)` | None |
| RUN-2026-05-17-03 | 2026-05-17 | ROSE | Python syntax | `python -m py_compile scripts/harness_fixture_check.py` | pass | no compiler output | None |
| RUN-2026-05-17-04 | 2026-05-17 | ROSE | Diff hygiene | `git diff --check` | pass | no whitespace/hygiene output | None |
| RUN-2026-05-17-05 | 2026-05-17 | review-pipeline lanes | Code review / test / security | `code-reviewer`, `test-engineer`, `security-auditor` | pass after fix loop | code-reviewer and test-engineer reruns PASS; security-auditor PASS | Runtime OpenCode execution and exhaustive whole-codebase no-bug proof not performed |
| RUN-2026-05-17-06 | 2026-05-17 | ROSE | Template check | `python scripts/agents_md.py check --project .` | skipped | `AGENTS.md` and `templates/AGENTS.md` were not touched | Template compliance not re-run |

## 16. 缺陷与修复闭环

| Bug ID | 来源测试 | 现象 | 根因 | 修复负责人 | 修复文件 | 复测命令 | 复测结果 | 状态 |
|---|---|---|---|---|---|---|---|---|
| QA-2026-05-17-01 | code-reviewer | Risk acceptance wording did not consistently require explicit user/current-contract owner acceptance | SHIP docs used generic “accepted as risk” wording | ROSE | `commands/ship.md`, `lifecycle.md`, `review-repair-loop.md`, `docs/harness/aili-harness-contract.md` | code-reviewer rerun + harness/OpenSpec checks | pass | closed |
| QA-2026-05-17-02 | code-reviewer / test-engineer / security-auditor | `release-blocking-unresolved` fixture existed but was not semantically validated | Smoke checker only checked generic markers | ROSE | `scripts/harness_fixture_check.py`, `docs/harness/fixtures/verification-claim-fixtures.yaml`, `docs/harness/fixtures/command-routing-fixtures.yaml` | test-engineer rerun + `python scripts/harness_fixture_check.py` | pass | closed |

## 17. 变更记录

- 2026-05-17: Initial draft generated during DEFINE.
- 2026-05-17: User confirmed recommended interview defaults and accepted test plan for BUILD.
- 2026-05-17: BUILD verification records and review/fix closure added after implementation.
