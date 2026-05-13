## Why

`aili-workflow` 已经形成 ROSE 主控、skills、subagents、`rose-memory`、review/verification gates、OpenSpec 工作流等 agent harness 组件，但当前控制面仍偏集中：`agents/rose.md` 承担过多运行期职责，命令入口尚未显式化，交付流程、协议模板、harness 治理、fixtures 与安装路径之间缺少统一架构锚点。

用户已确认本次目标从单一 `harness-evolution` 治理层扩展为一次“大但受控”的架构落位：一次性搭起 runtime charter 分割、四个顶层命令、核心交付 flow skill、harness evolution skill、harness 文档、协议模板、fixtures、零依赖静态 runner 与 OpenCode 安装脚本接入；同时明确不做 SQLite schema、自动 benchmark、完整 self-evolution、批量重写所有 subagent 或新增第三方依赖。

## What Changes

- 将本变更定位为 `add-aili-delivery-harness` umbrella scope；当前目录仍使用既有 OpenSpec change id `add-harness-evolution-layer`，除非后续用户单独批准重命名 change 目录。
- 新增四个顶层命令入口：`/ideate`、`/define`、`/build`、`/ship`；不新增 `/research`、`/questionnaire`、`/test-plan`、`/review`、`/fix-loop`、`/evolve` 等内部阶段命令。
- 新增核心 skill `skills/aili-delivery-flow/SKILL.md`，并把 lifecycle、backend routing、artifact contracts、questionnaire/test document policy、implementation package、review-repair loop 等细节下沉到 references。
- 将 `agents/rose.md` 分割/瘦身为 Runtime Charter：只保留身份与最终责任、指令优先级、安全/权限边界、主流程绑定、subagent 编排边界、memory 边界、完成声明 gate、harness evolution gate 与最小 router。
- 新增治理 skill `skills/harness-evolution/SKILL.md`，用于 no-naked-harness-edits 的报告优先流程；默认只产出 report/proposal，未获显式人工批准不得 silent apply。
- 新增 `docs/harness/**` 作为可观察架构面，包括 harness contract、component map、activation matrix、backend adapters、command lifecycle、failure taxonomy、tool policies、harness change report template 和 fixtures。
- 新增 `protocols/**` 作为唯一协议模板面，包括 idea brief、research evidence pack、spec draft、alignment questionnaire、acceptance test plan、implementation package、subagent task packet/result、review report、closeout report。
- 新增 `workflow.components.yaml` 作为组件目录/权威来源索引，并新增 `scripts/harness_fixture_check.py` 做零依赖静态 fixture smoke validation。
- 更新 OpenCode 安装路径：`scripts/install_opencode.sh`、`docs/opencode-setup.md`、`README.md` 需包含 `commands/*.md` 的安装/说明，避免命令文件存在但不可用。
- 允许小幅更新现有 skill 触发描述和共享调度/测试/评审 guidance，只添加短引用和触发关系，禁止把完整流程复制进多个 skill 或批量重写所有 subagent。

## Capabilities

### New Capabilities

- `aili-delivery-harness`: 定义 ROSE runtime charter 分割、四个顶层命令、`aili-delivery-flow` 状态机、协议模板、安装接入、fixtures runner 与架构权威文件边界。
- `harness-evolution`: 定义 AHE-lite harness 演化治理层，包括触发条件、报告契约、组件归因、激活矩阵、审批/验证门禁、fixtures 与 memory/provenance 边界。

### Modified Capabilities

- None.

## Impact

- 预计新增：`commands/{ideate,define,build,ship}.md`、`skills/aili-delivery-flow/**`、`skills/harness-evolution/**`、`docs/harness/**`、`protocols/**`、`workflow.components.yaml`、`scripts/harness_fixture_check.py`。
- 预计修改：`agents/rose.md`、`skills/using-agent-skills/SKILL.md`、`skills/parallel-subagent-dispatch/SKILL.md`、`skills/review-pipeline/SKILL.md`、`skills/test-document-generator/SKILL.md`、`docs/opencode-setup.md`、`scripts/install_opencode.sh`、`README.md`，以及必要时的 `templates/AGENTS.md` 短引用。
- 不新增第三方依赖，不修改 lockfile，不改变生产部署行为或公共 API。
- 不修改 `rose-memory` SQLite schema，不绕过 `rose-memory` CLI 写 SQLite，不把 raw logs、完整对话或 secrets 写入 memory。
- 不自动 commit/push/merge harness 改动；核心 harness 改动必须有明确用户批准、验证证据与回滚说明。
