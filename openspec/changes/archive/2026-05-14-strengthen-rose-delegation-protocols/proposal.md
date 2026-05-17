## Why

ROSE 现在已有 subagent 路由、Context Evidence Gate 和 harness evolution 方向，但直接执行、强制派发、项目证据、session 交接、code-scout 定位语义和 subagent 结果协议仍分散在主 agent 与技能描述中，容易让 ROSE 在复杂任务里继续凭主观经验或把大量搜索证据塞进主上下文。

本变更把“主 agent 只直接做小而确定的改动；复杂、证据分散、上下文污染或需要专业判断的任务必须进入 subagent/gate”固化为可审查的 OpenSpec 合约。用户已在 BUILD 问卷中批准修改 `agents/rose.md`、skills 和 canonical protocol references；后续实现仍必须保持 scoped package、可验证、无依赖/lockfile/schema/commit/push 变更。

## What Changes

- 新增 Direct vs Delegated Work 合约，明确 ROSE 可直接处理的小改 allowlist，以及必须派发 subagent 或进入 gate 的条件。
- 强化 Context-Saving Mandatory Delegation：即使最终改动很小，只要证据收集会显著污染或消耗 MainAgent context，就必须派发只读 scout。
- 将 `code-scout` 从普通搜索 worker 明确升级为 code locality mapping：定位上游入口、下游消费者、同级/同层实现、测试覆盖、active/stale/generated/archived 引用与下一步阅读文件。
- 新增 `repo-evidence-first` 技能合约，正文使用中文，要求没有项目证据锚点就不能把判断写成项目事实。
- 新增 `session-handoff` 技能合约，用于长会话、压缩前、BLOCKED/IDLE 或切换 session 时输出轻量交接文档；它不同于长期 memory。
- 更新 subagent task/result 协议要求：任务包必须包含 goal、context、allowed/forbidden scope、edit permission、evidence required、expected return format、stop conditions；结果必须分离 observed facts、inferences、recommendations、unknowns 和 MainAgent next reads。协议权威路径以 `skills/aili-delivery-flow/references/protocols/` 为准；若存在或恢复顶层 `protocols/**`，只能作为兼容转接/索引，不再承载另一套冲突规则。
- 约束 `agents/rose.md` 只增加短 router/触发提示，详细规则进入 skills/references/protocols，避免继续膨胀主控 prompt。
- 保持与既有 `add-harness-evolution-layer` 的关系清晰：该 stale/conflicting change 已按用户批准归档到 `openspec/changes/archive/2026-05-13-add-harness-evolution-layer/`，未同步其 delta specs；本 change 继续作为当前 BUILD 权威。

## Capabilities

### New Capabilities

- `delegation-protocols`: 定义 ROSE 直接执行边界、context-saving 强制派发、repo evidence gate、code locality mapping、session handoff 和 subagent task/result 协议的可验证行为。

### Modified Capabilities

- None.

## Impact

- 预计新增或更新的 proposal scope 文件：`skills/aili-delivery-flow/references/direct-vs-delegated-work.md`、`skills/repo-evidence-first/SKILL.md`、`skills/session-handoff/SKILL.md`、`skills/parallel-subagent-dispatch/SKILL.md`、`skills/aili-delivery-flow/references/protocols/subagent-task-packet.md`、`skills/aili-delivery-flow/references/protocols/subagent-result.md`，以及 `agents/rose.md` 的最小 router 引用。顶层 `protocols/**` 不作为本 change 的规范权威；如后续发现它存在，必须链接到 canonical path 或另开 reconciliation 任务。
- 后续可选 scope：`skills/aili-delivery-flow/references/runtime-interfaces.md`、`session-event-log.md`、`hand-capabilities.md`。
- 不新增第三方依赖，不修改 lockfile，不修改 SQLite schema，不写入 secrets，不自动 commit/push/merge。
- 核心 harness 文件编辑已由用户在 BUILD 问卷中批准；任何超出本 change 的文件移动、依赖/lockfile/schema/install/permission/secret 相关变更仍需单独批准。
