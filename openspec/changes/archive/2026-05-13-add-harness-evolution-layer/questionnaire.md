# 变更问卷：add-harness-evolution-layer / add-aili-delivery-harness umbrella

## 1. 资料来源与证据

| 来源 | 已检查内容 | 观察到的事实 | 置信度 | 备注 |
|---|---|---|---|---|
| `docs/research/agent-harness/command-lifecycle.md` | command lifecycle / define gates | 顶层命令应限定为 `/ideate`、`/define`、`/build`、`/ship`；OpenSpec 是 backend adapter；`/define` 首轮应同时产出 spec、questionnaire、test document | high | 支持四命令入口和 backend adapter 分层 |
| `docs/research/agent-harness/project-upgrade-inspirations.md` | harness 工程化方向 | 下一阶段目标是可观察、可评估、可回滚、可演化，而不是继续堆规则或扩写 prompt | high | 支持 harness contract、subagent evidence schema、fixtures、安全权限矩阵 |
| `docs/research/agent-harness/ahe-lite-transformation-plan.md` | AHE-lite 方案 | 推荐 `observe -> classify -> propose -> approve/review -> apply -> verify -> record verdict`，并要求 no naked harness edits | high | 首阶段不改 SQLite schema，不做自动 self-evolution |
| 用户填写内容 | Q1-Q8 / scope decision | 用户确认本次可做一次“大但受控”的架构落位，范围包含 `rose.md` 分割、commands、skills、docs/harness、protocols、fixtures、安装脚本接入 | high | 明确不做 SQLite schema、自动 benchmark、完整 self-evolution、批量重写所有 subagent、新依赖 |

## 2. 当前理解

- 目标：将本 change 从单一 `harness-evolution` 治理层扩展成 `add-aili-delivery-harness` umbrella 架构首版落位。
- 当前目录：仍为 `openspec/changes/add-harness-evolution-layer/`；目录重命名需要单独批准。
- 已确认范围：`rose.md` Runtime Charter 分割、四个 commands、`aili-delivery-flow`、`harness-evolution`、`docs/harness/**`、`protocols/**`、fixtures、零依赖 runner、install script/docs/README 接入、少量 shared guidance 更新。
- 已确认非目标：SQLite schema、自动 benchmark、完整 self-evolution、自动 commit/push、批量重写所有 subagent、新依赖、lockfile、生产部署行为。

## 3. 用户答案吸收

| ID | 用户答案摘要 | 形成的决策 | 写回位置 | 剩余不确定 |
|---|---|---|---|---|
| Q1 | 允许修改 `agents/rose.md`，但目标是分割/瘦身成 Runtime Charter，不是追加规则 | `rose.md` 只保留 runtime authority；流程细节下沉到 `aili-delivery-flow`、`harness-evolution`、`docs/harness/**`、`protocols/**` | `proposal.md`, `design.md`, `tasks.md`, `specs/aili-delivery-harness/spec.md` | 无；目录重命名另议 |
| Q2 | 命令做四个顶层入口 `/ideate`、`/define`、`/build`、`/ship`，内部阶段不暴露 | 新增 `commands/*.md`；commands 只触发 `aili-delivery-flow` 模式 | `proposal.md`, `design.md`, `tasks.md`, `specs/aili-delivery-harness/spec.md` | 无 |
| Q3 | 新增核心 skill `aili-delivery-flow`，复杂状态机放 references | 新增 skill 与 lifecycle/backend/artifact/questionnaire/test/implementation/review references | `proposal.md`, `design.md`, `tasks.md`, `specs/aili-delivery-harness/spec.md` | 无 |
| Q4 | `harness-evolution` 一起做，但定位为治理 skill；不做顶层 `/evolve` | 新增 report-first governance skill 和 references | `proposal.md`, `design.md`, `tasks.md`, `specs/harness-evolution/spec.md` | 无 |
| Q5 | 新增 `docs/harness/**`、`protocols/**`、`workflow.components.yaml` | docs/protocols 成为可观察架构面和唯一权威引用面 | `proposal.md`, `design.md`, `tasks.md`, specs | 无 |
| Q6 | 安装脚本一起改，支持 commands | 更新 `scripts/install_opencode.sh`、`docs/opencode-setup.md`、`README.md` | `proposal.md`, `design.md`, `tasks.md`, `specs/aili-delivery-harness/spec.md` | 无 |
| Q7 | 允许小幅更新现有 skill 触发描述；不批量重写 subagent | 只加短引用和触发关系，避免复制完整流程 | `tasks.md`, specs | 无 |
| Q8 | 验收标准改为 commands 可安装、`rose.md` 已瘦身、核心 skill 存在、fixtures 通过、OpenSpec validation 通过、无 SQLite schema/新依赖/自动提交 | 更新测试文档和任务验证标准 | `test-plan.md`, `tasks.md` | 无 |

## 4. 设计漏洞 / 证据缺口 / 反例

| ID | 类型 | 说明 | 处理方式 | 状态 |
|---|---|---|---|---|
| L1 | Scope risk | 本次改动面较大，容易多入口重复定义流程 | 指定唯一权威文件；`rose.md`/commands/README 只短引用 | mitigated |
| L2 | Blast radius | `rose.md` 分割可能遗漏安全、memory、git、verification 边界 | Runtime Charter 要求保留这些边界；后续用 review-pipeline/verification gate 检查 | mitigated |
| L3 | Verification gap | 新增 runner 可能滑向 benchmark/eval | runner 限定 Python 标准库静态必填字段/smoke validation | mitigated |
| L4 | Change-id drift | 用户建议新 umbrella 名称，但当前 OpenSpec 目录已存在 | 暂不移动目录；如需 rename，另取显式批准 | open_question |

## 5. 写回记录

- 已将 Q1-Q8 决策写入 `proposal.md`、`design.md`、`tasks.md`。
- 已新增 `specs/aili-delivery-harness/spec.md`，并扩展 `specs/harness-evolution/spec.md`。
- 已更新 `test-plan.md` 的 scope、trace matrix、commands、验收标准与执行记录位置。
