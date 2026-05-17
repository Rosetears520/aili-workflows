# 变更采访包：add-ship-release-blocker-audit

## 1. 资料来源与证据

| 来源 | 已检查内容 | 观察到的事实 | 置信度 | 备注 |
|---|---|---|---|---|
| `commands/ship.md` | 当前 `/ship` 命令契约 | `/ship` 已要求 freshness、review/repair、release-readiness、artifact consistency、rollback/closeout、风险与 `Unverified` 输出 | high | 需要补充“release-blocker audit”命名和目标范围 |
| `skills/aili-delivery-flow/references/lifecycle.md` | SHIP 生命周期规则 | SHIP 输入包含 BUILD review/test/security evidence；输出 release-readiness 和 fresh evidence；禁止 stale/missing evidence ready claim | high | 适合作为核心改动点 |
| `skills/aili-delivery-flow/references/review-repair-loop.md` | review/repair gate | SHIP 已会刷新 stale 或 scope-affected lanes，并审计 release-readiness concerns | high | 需要补充 blocker 分类 |
| `docs/harness/command-lifecycle.md` | 命令生命周期 | 只规划 `/ideate`、`/define`、`/build`、`/ship` 四个顶层命令；review/repair 是内部阶段 | high | 支持不新增命令 |
| `docs/harness/aili-harness-contract.md` | harness 架构契约 | Commands 是四个薄入口；不得新增 internal top-level commands | high | 支持把能力放进 `/ship` |
| `README.md` | 使用说明 | `/ship` 是完整 release-readiness pipeline；仓库不提供内部阶段命令 | high | 需要同步用户可见描述 |
| `openspec/specs/aili-four-command-lifecycle/spec.md` | 现有 OpenSpec 能力 | 已有四命令生命周期、DEFINE gate、BUILD gate、post-cycle bugs 规则 | high | 本次应修改该能力而非新增 command capability |

## 2. 当前理解

- 目标：让 `/ship` 明确执行“release-blocker audit”，检查是否有会阻碍交付/合并/归档/发布的问题。
- 当前草稿表达的是：不要新增单独顶层命令；优先增强 `/ship` 和 `aili-delivery-flow` 的 SHIP 规则。
- 现有代码 / 文档显示：`/ship` 已承担 release-readiness，但没有明确列出用户提到的“本提案 / 本次变更 / 上次发版对比 / 整库扫描”的审计目标选择。
- 已确认约束：不能把 stale BUILD evidence 当 fresh；不能在缺失 fresh evidence 时 claim ready；必须显式报告 residual risks 和 `Unverified`。
- 暂定非目标：不新增 public top-level command；不新增依赖；不改 memory schema；不在 DEFINE 阶段实现。
- 仍不确定的地方：默认 audit target、baseline 如何定位、是否需要 closeout report 新字段、整库扫描触发条件。

## 3. 需要你填写的问题

| ID | 问题 | 为什么要问 | 推荐默认答案 | 取舍影响 | 你的填写 | 写回位置 |
|---|---|---|---|---|---|---|
| Q1 | `/ship` 没有明确目标时，默认审计哪个范围？ | 会影响默认行为和噪音大小 | 默认审计当前 resolved change / final diff；baseline 和 whole-codebase 仅在明确请求或风险触发时做 | 默认越窄越可验证；默认整库会更慢且容易产生不可验证 claim | 默认审计当前 resolved change / final diff；baseline 和 whole-codebase 仅在明确请求或风险触发时做 | `design.md`, `specs/aili-four-command-lifecycle/spec.md` |
| Q2 | 用户说“和上次发版对比”但没有 tag/commit/release 名称时，要不要停下来问？ | baseline 不明确会导致错误比较 | 停下来问 baseline；不能猜 | 更安全，但多一个交互；猜 baseline 会有误判风险 | 停下来问 baseline；不能猜 | `specs/aili-four-command-lifecycle/spec.md`, `tasks.md` |
| Q3 | “看整个代码库”是否作为 `/ship` 默认能力，还是只作为显式 broad scan？ | 影响 SHIP 的成本和完成声明边界 | 只在用户明确要求、风险触发、或 narrow target 不足时执行 bounded scan | 降低默认成本；但用户要整库时仍可支持 | 只在用户明确要求、风险触发、或 narrow target 不足时执行 bounded scan | `design.md`, `commands/ship.md` |
| Q4 | closeout report 是否要新增单独的 `release-blocker audit` 字段？ | 影响 artifact/protocol 改动范围 | 建议新增一个简短字段或小节：target、fresh evidence、blocking findings、Unverified | 更清晰；但会多改一个协议/文档点 | 建议新增一个简短字段或小节：target、fresh evidence、blocking findings、Unverified | `design.md`, `tasks.md` |
| Q5 | 是否需要单独 `release-blocker-audit` skill？ | 影响架构边界和 skill 数量 | 暂不新增；先由 `aili-delivery-flow` SHIP + `review-pipeline` 内部协作承载 | 保持简单；若后续重复逻辑过多再提新 skill | 暂不新增；先由 `aili-delivery-flow` SHIP + `review-pipeline` 内部协作承载 | `proposal.md`, `design.md` |
| Q6 | release-blocking finding 是否必须由用户明确接受风险后才能继续？ | 影响 ready verdict | 是；未修复、未证伪、未接受的 release-blocking finding 必须阻断 ready claim | 更符合安全交付；可能需要更多确认 | 是；未修复、未证伪、未接受的 release-blocking finding 必须阻断 ready claim | `specs/aili-four-command-lifecycle/spec.md` |

## 4. 设计漏洞 / 证据缺口 / 反例

| ID | 类型 | 说明 | 建议处理方式 | 状态 |
|---|---|---|---|---|
| L1 | Missing evidence | 仓库当前没有明确“previous release”基线命名规则 | 要求用户提供 tag/commit/branch/release 名称；否则标 `Open Question` / `Unverified` | open |
| L2 | Verification gap | “整库没有 bug”无法被穷尽证明 | 输出 scanned scope、fresh evidence、skipped lanes、residual `Unverified`，避免绝对化 ready claim | open |
| L3 | Architecture risk | 新增单独命令会违反当前四命令生命周期约束 | 保持 `/ship` 入口；不新增 public top-level command | mitigated |
| L4 | Scope risk | release-blocker audit 可能和 BUILD code-review/test/security 重复 | SHIP 只判断 freshness 并 rerun stale/scope-affected lanes | mitigated |

## 5. 填写说明

- 可以直接在“你的填写”列里写答案。
- 不确定的地方写“不确定”即可。
- 接受推荐默认答案时，写“同意默认”。
- 不进入本次 scope 的内容，写“本次不做”。
- 未填写内容不会被写成事实，只会保留为 `Open Question`。
- 无证据支撑但暂时保留的内容会标为 `Unverified`。

## 6. 后续写回映射

| 用户答案 | 将写回到 | 写回方式 |
|---|---|---|
| Q1 | `design.md`, `specs/aili-four-command-lifecycle/spec.md` | 默认目标和 broaden 条件 |
| Q2 | `specs/aili-four-command-lifecycle/spec.md`, `commands/ship.md` | baseline 缺失时的 hard stop / question |
| Q3 | `design.md`, `commands/ship.md` | whole-codebase scan 触发条件和输出边界 |
| Q4 | `tasks.md`, possible closeout/artifact protocol | 是否新增输出字段 |
| Q5 | `proposal.md`, `design.md` | 保持 no-new-skill 或另立 skill 的决策 |
| Q6 | `specs/aili-four-command-lifecycle/spec.md` | release-blocking finding 的 acceptance gate |

## 7. 答案吸收记录

用户于 2026-05-17 确认：同意本采访包的推荐默认答案，并确认 `test-plan.md`，可以进入 `/build`。

| 问题 | 用户答案 | 形成的决策 | 已写回位置 | 剩余不确定 |
|---|---|---|---|---|
| Q1 | 同意推荐默认答案 | `/ship` 默认审计当前 resolved change / final diff；baseline 和 whole-codebase 仅在明确请求或风险触发时做 | `design.md`, `specs/aili-four-command-lifecycle/spec.md`, `commands/ship.md` | 无 |
| Q2 | 同意推荐默认答案 | 用户要求 previous-release comparison 但未提供 tag/commit/branch/release 时，停下来问或标 `Open Question` / `Unverified`；不能猜 | `specs/aili-four-command-lifecycle/spec.md`, `commands/ship.md`, `review-repair-loop.md` | 仓库仍无 canonical previous-release 命名规则 |
| Q3 | 同意推荐默认答案 | 整库扫描只在用户明确要求、风险触发、或 narrow target 不足时执行 bounded scan | `design.md`, `commands/ship.md`, `lifecycle.md` | 整库审计仍不能穷尽证明无 bug |
| Q4 | 同意推荐默认答案 | closeout 增加简短 `Release-blocker audit` 字段/小节，包含 target、fresh evidence、blocking findings、`Unverified` | `artifact-contracts.md`, `closeout-report.md` | 无 |
| Q5 | 同意推荐默认答案 | 本次不新增 `release-blocker-audit` skill；先由 `aili-delivery-flow` SHIP + `review-pipeline` 内部协作承载 | `proposal.md`, `design.md`, docs | 若后续重复逻辑过多，可另起提案 |
| Q6 | 同意推荐默认答案 | 未修复、未证伪、未接受的 `release-blocking` finding 必须阻断 ready claim | `specs/aili-four-command-lifecycle/spec.md`, `commands/ship.md`, `review-repair-loop.md` | 无 |
