# INTERVIEW-PACKET-FORMAT.md

Use this reference when `requirements-grilling` drafts or appends an `interview.md` requirements grilling packet.

```markdown
# 需求拷问包：<change-name>

## 1. 资料来源与证据

| 来源 | 已检查内容 | 观察到的事实 | 置信度 | 备注 |
|---|---|---|---|---|
| `<path>` | 现有实现 / 文档 / 测试 | ... | high / medium / low | ... |

## 2. 当前理解

- 目标：
- 当前草稿表达的是：
- 现有代码 / 文档显示：
- 已确认约束：
- 暂定非目标：
- 仍不确定的地方：

## 3. 覆盖矩阵与状态

状态只能使用：`Confirmed by evidence`、`Not applicable`、`Needs question`、`Open Question`、`Unverified`。

| 维度 | 状态 | 证据 / 原因 | 关联问题 | 写回目标 |
|---|---|---|---|---|
| goal/success | ... | ... | Q? / N/A | `proposal.md` / `test-plan.md` |
| scope/non-goals | ... | ... | Q? / N/A | `proposal.md` |
| roles/permissions | ... | ... | Q? / N/A | `design.md` / specs |
| happy path | ... | ... | Q? / N/A | `design.md` / specs |
| failure path | ... | ... | Q? / N/A | `design.md` / `test-plan.md` |
| retries/rollback | ... | ... | Q? / N/A | `design.md` / `test-plan.md` |
| boundary conditions | ... | ... | Q? / N/A | specs / `test-plan.md` |
| data lifecycle | ... | ... | Q? / N/A | `design.md` / specs |
| state transitions | ... | ... | Q? / N/A | `design.md` / specs |
| API/CLI/UI contracts | ... | ... | Q? / N/A | specs / `tasks.md` |
| compatibility/migration | ... | ... | Q? / N/A | `design.md` / `tasks.md` |
| terminology/domain model | ... | ... | Q? / N/A | `context.md` / `adr.md` / `design.md` |
| security/privacy | ... | ... | Q? / N/A | `design.md` / `test-plan.md` |
| performance/reliability | ... | ... | Q? / N/A | `design.md` / `test-plan.md` |
| observability | ... | ... | Q? / N/A | `design.md` / `tasks.md` |
| acceptance/testability | ... | ... | Q? / N/A | specs / `test-plan.md` |
| rollout/rollback | ... | ... | Q? / N/A | `proposal.md` / `design.md` |
| explicit non-goals | ... | ... | Q? / N/A | `proposal.md` |

## 4. 需要你填写的问题

| ID | 问题 | 为什么要问 | 影响的 artifact / decision | 有证据支撑的推荐默认答案 | 后果 / 取舍 | 你的填写 | 写回位置 |
|---|---|---|---|---|---|---|---|
| Q1 | ... | ... | scope / design / tasks / acceptance / tests / risk / implementation safety | ...（证据：`<path>`） | 选 A 会...；选 B 会... |  | `proposal.md` |

## 5. 设计漏洞 / 证据缺口 / 反例

| ID | 类型 | 说明 | 建议处理方式 | 状态 |
|---|---|---|---|---|
| L1 | Missing evidence | ... | 查代码 / 查官方文档 / 问用户 / Open Question | open |

## 6. 术语 / 领域模型挑战

| ID | 术语或边界 | 冲突 / 模糊点 / 边界场景 | 证据 | 建议处理 | 写回位置 |
|---|---|---|---|---|---|
| D1 | ... | ... | `<path>` | 更新 `context.md` Language / 提出 ADR / 追问 | `context.md` |

## 7. 填写说明

- 可以直接在“你的填写”列里写答案。
- 不确定的地方写“不确定”即可。
- 接受推荐默认答案时，写“同意默认”。
- 不进入本次 scope 的内容，写“本次不做”。
- 未填写内容不会被写成事实，只会保留为 `Open Question`。
- 无证据支撑但暂时保留的内容会标为 `Unverified`。
- 如果填写内容仍有歧义、互相矛盾、不可测试、与证据冲突、术语冲突或超出 scope，会进入 Round 2+ 追问轮，不会直接写回为事实。

## 8. 后续写回映射

| 用户答案 | 将写回到 | 写回方式 | 写回前门禁 |
|---|---|---|---|
| Q1 | `proposal.md` | scope / non-goal | confirmed / waived / accepted `UNVERIFIED` |

## 9. 答案吸收记录

_用户填写后由模型补充。_

| 问题 | 用户答案 | 分类 | 形成的决策 | 已写回位置 | 剩余不确定 / 追问 |
|---|---|---|---|---|---|
```
