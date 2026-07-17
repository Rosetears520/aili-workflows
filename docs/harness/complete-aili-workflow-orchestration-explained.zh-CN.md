# 完整 AILI 工作流编排：通俗说明

## 文档目的

[已知] 本文解释 OpenSpec 变更 `complete-aili-workflow-orchestration` 想解决什么、已经落地什么、还没有证明什么，以及用户现在应如何使用它。

[已知] 本文面向不熟悉 AILI、OpenSpec、OpenCode、子代理或工作树（worktree）的读者。技术名词会保留英文，并在第一次出现时解释。

[工具结果] 本文的状态截面日期是 2026-07-12。`progress.txt` 是执行状态账本，但其中也保留了没有重写的历史段；当前状态只能结合最后写入的 A30 条目、本次直接检查到的实现，以及与早期条目和正式 artifacts 的冲突来判断。提案、设计、任务、访谈和测试计划仍分别拥有正式合同内容；这些材料尚未完全对齐，因此不能声称整体合同已经一致。

[已知] 本文只解释 Stage I。它不宣布 `/ship` 就绪，不替代正式 OpenSpec 合同，也不授权真实外部目录、网络、发布、Graphify 执行或高风险操作。

## 2026-07-17 后续权威说明

[已知] 后续已接受变更 `simplify-aili-workflow-harness` 对重叠的通用编排/效率规则具有较新权威：ROSE 每次只选择一个 primary loop，最多增加一个有具体缺口的 auxiliary capability；自然语言与四个命令进入同一有界 loop；skill 不得自动调用另一个 process skill。本文下方的 Package 1–12、A30、六 loop、74 行审计等内容仅用于解释原伞形变更历史，不能再要求默认委派、全量 hydration、多轮 review、完整任务矩阵或全套测试。

[已知] 当前通用执行默认由 ROSE 直接完成。已授权范围内的安全本地读取、编辑、确定性诊断和 claim-matched 检查不做微审批；材料性决定和破坏性/外部/依赖/Schema/Auth/安全/Git/发布/A33 精确操作仍按原 gate 失败关闭。

[已知] 当前 hydration 按 mode、dependency 和 event 选择：每个写入文件在作为 durable evidence 前重读一次，后续只让相关事件使其 dependents 失效；阶段、时间、文件存在或“继续”不会触发全套 artifact 重读。

[已知] 当前 verification 只有一个 owner，由 ordinary/lifecycle owner 选择支持具体主张的最小新鲜检查。TDD、stress-test、review、安全、浏览器和 full suite 都不是 phase/package 自动步骤。[未验证] 这些精简规则的模型行为和成本效果等待真实应用反馈；静态文字本身不能证明效果。

[已知] `WT-001` 当前模式是 A33 shared-trust-domain；本文 A30/A31 runtime 结果和 A32/item-41 readiness 均为历史证据，不授予当前操作权限。A33 的 exact ADD/REMOVE、target-rule、identity、风险和新鲜审批语义未被后续简化变更改写。

## 状态与主张标签

| 标签 | 通俗含义 |
|---|---|
| `[已知]` | 有正式合同、明确决定或直接来源支持。 |
| `[工具结果]` | 本次文件检查、命令或当前实现直接显示的结果。 |
| `[推断]` | 从已知证据推出来，但不是来源逐字结论。 |
| `[框架内]` | 未来设计、提议或协议模型；逻辑可以完整，但还不是当前现实能力。 |
| `[未验证]` | 缺少新鲜运行证据，或现有证据不足。 |
| `[开放问题]` | 仍需用户、维护者或上游项目作决定。 |

[已知] 同一句中的多个相邻事实可以共用一个标签。没有标签的标题、表头、命令示例和纯提示语不表示状态主张。

## 执行摘要

[已知] 这项“伞形提案”曾把分散规则收拢为四路生命周期、一个 OpenSpec change 和最终测试计划接受门，并以 Package 1–12、A30 和完整收敛矩阵描述当时的实现历史。后续简化变更已经替换这些重叠的重型默认；DCP、伪 Goal Mode、CodeGraph 非证明性和 Graphify fail-closed 等不冲突边界继续保留。[未验证] 原 A30 provider-backed Task runtime 最后记录为退出 `3`，但它现在是历史证据，既不证明也不阻塞当前 A33 操作语义。

**一句话说明：** [推断] AILI 现在更像“同一位负责人根据当前意图选择一条有界路线，需要时只请一个专门帮手，并用最小证据验收”的工作流，而不是多套流程自动接力的系统。

## 以前出了什么问题

[已知] 旧需求散落在想法文件、旧草案、现有仓库合同和 Graphify 草案中。不同材料对审批、Goal、跨工作树、复审、连续性和自动化的说法不一致。

[已知] 旧方案曾混入多套没有被接受的机械装置，例如基线清单、摘要、回执、nonce、工作树维护平面和独立 worker。它们让“写了方案”看起来像“已经具备运行能力”。

[已知] 旧 BUILD 还曾模仿原生 `/goal`，引入 `goal_id` 和 Goal Mode 标记。这样会混淆 AILI 自己的工作流与 OpenCode 原生能力。

[推断] 可以把旧状态想成一间办公室里同时贴了几套流程图。每套图都有部分真相，但没有一张图能安全地告诉人“现在到底能做什么”。伞形提案的作用，就是分清合同、进度、证据和未来设计。

## 明确移除了什么

### AILI 自己拥有的 DCP 集成

[已知] AILI 自己的 DCP 安装、开关、类型、提示、检测、配置合并、状态、doctor、文档、模板、manifest、skill 和测试入口都被要求移除。

[已知] 旧参数 `--enable-dcp` 与 `--skip-dcp` 现在应按普通未知参数处理，而不是进入兼容模式或迁移流程。

[已知] 用户自己安装的第三方 DCP 插件，以及用户自己的 `dcp.json`、`dcp.jsonc`，不由 AILI 自动删除、迁移或改写。最多只能给出人工清理说明。

### 伪 BUILD Goal Mode

[已知] AILI 的伪 Goal Mode、`goal_id`、goal marker、goal contract、相关 fixture，以及对原生 goal 的绑定或模仿都被移除。

[已知] 普通中文“目标”、英文 `goal` 和 Goal-Driven Verification 仍可作为自然语言或验证方法使用。它们不再激活特殊执行模式。

[已知] OpenCode 原生 `/goal` 不归 AILI 所有，也没有被本变更修改。成功的 `/goal <objective>`、裸 `/goal` 和持久 goal 状态属于 Stage II / N/A。

### 被拒绝的重型机械

[已知] 当前 Stage I 不实现 `baseline-manifest.json`、通用 artifact digest、nonce、receipt、revision、内容绑定审批、工作树 registry、工作树 maintenance plane、P1–P4 权限层级或持久独立目标会话。

[已知] `artifact-integrity` 只保留为非约束性的未来名字。它现在没有 schema、manifest、配置、运行逻辑、审批语义或 gate。

[已知] A27/A28/A29 的独立 `opencode run --dir` worker、worker provenance manifest 和运行 driver 已被 A30 取代为当前非实现范围。它们只作为未来能力缺口资料保留。

## 没有被碰掉的用户能力

[已知] 用户自己管理的 DCP 文件和第三方插件保持用户所有。AILI 不自动清理它们。

[已知] OpenCode 原生 `/goal` 保持原样。AILI 的 `/build` 只做中性的 package 执行，不假装自己是 `/goal`。

[工具结果] 当前生成的 OpenSpec 直接适配器，例如 `.opencode/skills/openspec-*`，仍然存在；正式合同要求本变更不手改、不包裹或控制这些直接入口。 [未验证] 本次没有可引用的前后字节基线，因此不主张它们的内容在整个变更过程中保持不变。

[已知] 这些直接适配器不在 AILI 的四路生命周期保证内。AILI 不把它们的输出当成接受、就绪、验证、收敛或完成证据。

## 新增或改变了什么

### 普通、正式与实质性分类

[已知] 一个请求只有在以下条件全部成立时才是普通请求：目标单一且边界明确；不改变合同、公共接口、数据、安全、依赖、发布、范围、任务、验收、风险或已实现行为；大概率可在当前会话用聚焦验证完成；不需要多 package、跨会话或正式验收。

[已知] 文件少、文字短或预计耗时短，都不能单独证明请求普通。

[已知] 明确要求 proposal、spec、design、plan、正式 DEFINE，或触及公共 API、schema、迁移、权限、安全、依赖、lockfile、破坏性操作、发布、架构、跨 package 行为的请求，属于正式或实质性请求。

[已知] 自然语言与 slash command 使用同一个语义分类器。关键词只用于解释、比较、翻译或查询状态时，是近似命中（near miss），不会自动启动生命周期。

| 用户说法 | 分类结果 | 原因 |
|---|---|---|
| “解释一下 build 是什么。” | [已知] 普通。 | [已知] 只是解释词义。 |
| “比较 proposal 和 design。” | [已知] 普通。 | [已知] 只是比较现有材料。 |
| “把登录 API 改成新公开接口。” | [已知] 正式/实质性。 | [已知] 改变公共接口。 |
| “只分析，不要正式化，但修改验收条件。” | [已知] 实质性。 | [已知] 修改验收条件的条款优先；若同时明确“不要写文件”，则只给阻塞预览。 |

### 四个顶层路线

[已知] AILI 的顶层交付入口只有 `/ideate`、`/define`、`/build`、`/ship`。等价自然语言可以进入相同路线，但不会获得额外权限。

#### `/ideate`

[已知] 输入是尚不清晰的想法、约束或多个候选方向。输出是选项、取舍、假设、未知项和下一步建议。

[已知] `/ideate` 的硬停止是不能写生产实现，也不能因为出现 `build`、`ship` 等词就偷偷创建正式 OpenSpec 变更。

示例：

- [已知] “想几个减少测试时间的办法”进入 IDEATE `turn`，先产出方案，不写实现。
- [已知] “想几个办法，并决定跨 package 的正式架构”触发正式条件，转入 DEFINE。
- [已知] “解释 IDEATE 和 DEFINE 的区别”只是普通说明，不创建变更。

#### `/define`

[已知] 输入是可行但尚未达到实现条件的目标。输出是一个创建或复用的 OpenSpec 变更，以及 proposal、spec、design、tasks、interview、test-plan、context 等适用材料。

[已知] DEFINE 按依赖顺序只读取和写入当前所需材料；每个写入文件在使用前重读一次。真正不明确的 change identity 只问一次；在身份未解决前不写文件。

[已知] DEFINE 的硬停止是不能实现代码；存在未解决的实质性产品问题、合同不一致、严格验证失败或最终测试计划未明确接受时，不能进入 BUILD。

示例：

- [已知] “为缓存策略写正式提案、设计和测试计划”进入 DEFINE。
- [已知] “给现有同范围 change 补一条安全要求”复用该 change，并按 material delta 更新相关材料。
- [已知] “这个 design 是什么意思”是解释，不进入 DEFINE。

#### `/build`

[已知] 输入必须包括明确实现意图、唯一目标、当前有效的最终测试计划接受、可运行 package、可验证退出条件、适用权限和有效 `CONT-005` envelope。

[已知] 输出包括从当前 accepted contract 推导出的 package 队列、轻量 savepoint、阻塞项和预算状态；队列完成后由 ROSE 直接检查 changed scope，并选择支持完成主张的最小检查。Package 1–12 只保留为该伞形变更的历史命名。

[已知] BUILD 的硬停止包括目标不明确、接受过期、权限不足、预算耗尽、实质性 delta、禁改文件或高风险操作未获单独批准。

示例：

- [已知] “按已接受的测试计划实现 change X”可以选择 BUILD `objective`，但仍要先检查目标、权限和预算。
- [已知] “我接受测试计划”本身是零执行，不会启动 BUILD。
- [已知] “继续”在没有唯一活动 envelope 时不会启动 BUILD。

#### `/ship`

[已知] 输入必须是已经有当前实现证据的变更，加上新的、明确的 review/repair/closeout 意图。

[已知] 输出包括 release-blocker 审计范围、发现分类、新鲜验证、工作树卫生状态、closeout 文档和剩余风险。

[已知] DEFINE 材料、测试计划接受、生成适配器输出，或更早说过“实现后发布”，都不足以证明 SHIP 就绪。

[工具结果] 当前 umbrella change 的 Package 12 与运行证据仍有阻塞，因此本文不把它标记为 `/ship` 就绪。

### OpenSpec 的创建、复用、默认写回与增量行为

[已知] Stage I 的正式工作创建或复用一个 OpenSpec change。同范围继续使用同一个 change；明确不同范围才创建另一个 change。

[已知] 如果多个 change 都合理，系统只问一个聚焦的 identity 问题，并在答案明确前不写入。

[已知] 正式 DEFINE 默认自动写回，不反复问“要不要保存 proposal”“要不要保存 test plan”。写回后必须重新读取磁盘内容。

[已知] 默认只问一个会改变决定的问题；若多个已知独立 blocker 合并成一个有界 packet 能减少用户负担，才使用一次 packet。每个问题说明 decision/operation、target、why-now、risk/trade-off、options/recommendation 和 denial effect。

[已知] 每个纠正、新要求、发现或实现反馈都归入 `covered`、`material-question`、`material-delta`、`ordinary-steering` 或 `Unverified` 之一。

[已知] material delta 返回 DEFINE，更新并重新读取受影响材料，重跑状态和严格验证；如果验收内容或必需验证改变，旧测试计划接受会过期。

[已知] 当前回合若明确要求“只聊天”“不要写文件”，该要求优先。系统只能返回标为阻塞和未验证的预览，不能创建、复用或更新 change。

### 最终测试计划是唯一的生命周期级 BUILD 前审批

[已知] 用户明确接受最终 `test-plan.md`，是唯一必需的生命周期级 BUILD 前用户审批。

[已知] proposal、spec、design、interview、context 和 tasks 仍必须一致、严格有效，并且没有未解决的实质性产品问题。

[已知] 测试计划接受不等于内容摘要签名、package 回执、运行测试结果、BUILD 指令、外部目录许可、网络许可、破坏性操作批准或发布批准。

[已知] 如果 material delta 改变验收或必需验证，旧接受会变 stale，需要重新接受最终测试计划。普通编辑不增加逐 artifact 审批。

### Artifact 责任表

| Artifact | 负责什么 | 不负责什么 |
|---|---|---|
| `proposal.md` / `specs/**` | [已知] 产品范围、需求和正式能力合同。 | [已知] 不证明执行状态或完成。 |
| `design.md` | [已知] 架构决定、边界、协议体和取舍。 | [已知] 不授权运行高风险操作。 |
| `tasks.md` | [已知] 实现任务、依赖、所有权和验收映射。 | [已知] checkbox 不证明任务 Done。 |
| `interview.md` | [已知] 问题、用户回答、覆盖和未解决实质性。 | [已知] 不建立第二套需求权威。 |
| `test-plan.md` | [已知] 验收与可追踪验证合同，以及唯一生命周期级 BUILD 前接受门。 | [已知] 不证明测试已经运行，也不授予操作权限。 |
| `context.md` | [已知] 维护意图、决定、拒绝项、未知项和漂移检查锚点。 | [已知] 不拥有当前执行状态。 |
| `progress.txt` | [已知] 当前进度、反馈、dispatch、证据、阻塞、ROSE 决定和下一步。 | [已知] 不改写正式合同。 |
| `drift-log.md` | [已知] 规格偏差、自我纠正、临时决定、取舍、开放问题和待回写项。 | [已知] 不是聊天记录、进度账或最终 review。 |
| `review-arbitration.md` | [已知] 有争议、阻塞、跨会话或实质不一致 finding 的证据与处置。 | [已知] 不是投票表，也不是预先创建的例行报告。 |
| `rose-memory` | [已知] 项目本地、legacy/pre-runtime 的连续性事实或候选。 | [已知] 不是正式合同、原生全局状态或完成证据。 |
| `handoff.md` | [已知] 脱敏的导航、引用、阻塞和下一步。 | [已知] 不替代权限、Git 真相、合同或验证。 |

### 连续性、checkpoint 与恢复

[已知] 恢复工作只读取当前 mode/next dependency 所需证据：DEFINE 的 changed artifact 与直接 dependents；BUILD 的 accepted test-plan gate、current package/tasks、owning contract、target/rules 和 affected verification；SHIP 的 implemented tree、current BUILD evidence 与 affected closeout owners。`progress.txt`、`drift-log.md`、memory 或 review/test/security evidence 只在 resume reference、deviation、conflict 或 affected claim 需要时读取。

[已知] checkpoint 是“记下现在在哪里”，不是“自动获得继续施工的许可证”。Package 1–11 的 savepoint 只记录 package、范围、改动文件、未解决项和下一个 package。

[已知] `continue`、`继续`、`go ahead` 只能恢复一个唯一、仍获授权、阶段明确、接受仍有效且预算未耗尽的活动 envelope。已消耗预算不能重置。

[已知] 模糊 `continue` 不会选择 change、切换阶段、刷新接受、扩大权限或从“只接受测试计划”直接启动 BUILD。系统应只问一个目标或授权问题，并且不执行、不写入、不消耗预算。

### 两层循环

[已知] 外层 profile 决定工作如何被触发和限制；内层 loop 决定生命周期工作如何推进。它们共用一个 `CONT-005` envelope。

#### 四个外层 profile

| Profile | 当前形态 | 通俗解释 |
|---|---|---|
| `turn` | [已知] 可执行。 | [已知] 一次用户回合，只做一个有限循环，不偷偷递归。 |
| `objective` | [已知] 可执行且有预算。 | [已知] 有明确目标、退出证据和预算的 BUILD 或 closeout 工作。 |
| `interval` | [已知] 仅协议。 | [已知] 记录“每周由外部或人工触发一次要怎么做”，不注册定时器。 |
| `event` | [已知] 仅协议。 | [已知] 记录“CI 失败等外部事件发生后人工触发一次要怎么做”，不安装监听器。 |

#### 有界 loop 词汇（非自动流水线）

| Loop | 何时启动 | 何时停止 |
|---|---|---|
| question | [已知] 有实质性歧义或明确 grilling。 | [已知] 回答、放弃、命名为未验证或用户停止。 |
| delta | [已知] 有纠正、finding 或实现反馈。 | [已知] 确认为 covered，或返回 DEFINE。 |
| evidence/plan | [已知] 显式 planning/source intent，或一个材料性证据缺口。 | [已知] 有界证据足够，或阻塞/未验证。 |
| neutral BUILD | [已知] 测试计划已接受且 package 可运行。 | [已知] 完整实现并 savepoint，或遇到 delta、安全、预算、取消停止。 |
| review/repair | [已知] 显式 review/repair intent，或一个具体 blocking finding。 | [已知] 一次 targeted repair/recheck 后解决或阻塞。 |
| convergence | [已知] 具体 completion/SHIP 主张缺少一个 traceability link。 | [已知] 受影响链接齐全，或该主张阻塞/未验证。 |

[已知] 上表只是可选 primary loop 的词汇，不表示一次请求必须依次运行六个 loop。一个 skill 只能返回 unmet need 给 ROSE，不能自行进入下一 loop。

[已知] Stage I 没有 scheduler、listener、daemon、持久 queue、hook、无人值守后台循环，也没有公开 `/loop`、`/schedule`、`/objective` 或 `/proactive` 命令。

[已知] 要求安装、注册、运行、修改、更新、重新配置、启用或复用自动化的请求会失败关闭，并且不写 LP。只有后来重新表述为“仅记录外部/人工协议”的请求，才可在 `design.md` 中创建或复用 LP。

### Package 1–12 历史与当前 package 规则

[已知] Package 1 是共享 source inventory 和 scaffold。Package 2 负责 classifier、OpenSpec routing 和 grilling。Package 3 负责 continuity、memory 和 handoff。

[已知] Package 4 移除 AILI DCP。Package 5 移除伪 Goal Mode 并建立中性循环。Package 6 负责 A30 跨工作树只读权限与 packet。

[已知] Package 7 负责 review arbitration 与 convergence。Package 8 负责固定上游引用和薄适配。Package 9 负责 CodeGraph 与 Graphify 证据工作流。

[已知] Package 10 同步文档、manifest 和生成适配器政策。Package 11 汇总 fixture、测试和 checker。原设计把 Package 12 作为完整质量/安全/收敛 gate；该重型默认已被后续简化变更取代。

[已知] Package 必须遵循依赖顺序和非重叠编辑所有权。当前默认直接/串行执行；只有实际存在两个独立单元且有明确收益时，ROSE 才选择一个 auxiliary capability，并在编辑路径冲突时保持串行。

[已知] 当前 package 边界本身不触发 test、review、commit 或 approval。savepoint 只记录 scope、files、unresolved、evidence state 和 next package，不能掩盖部分实现。

[已知] 当前 completion 默认由 ROSE 直接检查 changed scope 和 affected links；只有一个具体能力/证据缺口时，才选择最多一个 auxiliary capability。

[已知] 多数票和平均置信度被禁止。一个可信的重要少数 finding 必须被修复、被反证、被明确接受为风险，或以适当阻塞保留为 `Unverified`。

[已知] 当前 BUILD 最多允许一次 targeted repair/recheck；仍失败就报告 blocker，不会开始多轮 review-repair-retest-re-review 或重跑完整矩阵。

### 74 行任务审计（历史可选证据）与防止“假完成”

[已知] 原伞形变更有 74 个 task ID；只有具体 completion/SHIP 主张缺少 traceability 且 ROSE 选择该矩阵时，才使用这份历史审计形状。它不是所有 BUILD 的默认完成 gate。

[已知] 每行必须有九个字段：`task_id`、接受的 requirement/decision/risk、预期行为、实现文件/artifact、新鲜测试/检查/review 证据、status、findings、disposition、freshness。

| Status | 含义 | 是否可通过 |
|---|---|---|
| `Done` | [已知] 有任务特定实现和新鲜证据。 | [已知] 可以。 |
| `Partial` | [已知] 只完成了一部分或仍有 finding。 | [已知] 不可以。 |
| `Missing` | [已知] 预期实现或证据不存在。 | [已知] 不可以。 |
| `Blocked` | [已知] 被权限、环境、安全或其他 gate 阻塞。 | [已知] 不可以。 |
| `N/A` | [已知] 当前任务不适用。 | [已知] 只有引用明确接受来源、给出具体理由，并由 convergence reviewer/ROSE 确认解决时才可以。 |

[已知] checkbox 单独不能证明 `Done`。勾选但无证据是 `pseudo-complete`；实现了但未勾选是 `unchecked-task`；两者都必须被重新协调。

[已知] 缺行、重复行、未知行、无任务特定文件、旧证据、task/file 不匹配、task/test 不匹配和没有来源的 N/A 都会阻塞 `/ship`。

[工具结果] `task-audit.json` 中的 `Done=50, Partial=10, Blocked=14` 是 A30 之前的最终审计快照。它自己仍写着 OQ-005 待接受和 A30 未实现，因此在 A30 后已经过期，不能作为当前计数真相。

### A30：15 个同实例 Task 外部只读角色

[已知] A30 只支持 ROSE 在同一个 OpenCode instance/root 中通过内置 Task 分派。用户直接用 `@` 调用不在保证范围内。

[已知] 精确 15 个角色是：`agent-evaluator`、`ai-regression-scout`、`code-reviewer`、`code-scout`、`convergence-reviewer`、`doc-researcher`、`opensource-sanitizer`、`plan-auditor`、`pr-test-analyzer`、`security-auditor`、`silent-failure-reviewer`、`spec-miner`、`test-coverage-reviewer`、`web-performance-auditor`、`web-researcher`。

[已知] 合同要求这 15 个角色拥有相同的最终权限形状：默认 `* : deny`；只有 `read`、`list`、`glob`、`grep` 为 `allow`；只有 `external_directory` 为 `ask`；`edit`、`bash`、`task`、`lsp`、`skill`、`webfetch`、`websearch` 以及枚举出的 plugin、MCP、custom、browser 和其他工具全部为 `deny`。

[已知] 嵌套 read pattern 可以进一步禁止秘密文件、Git 管理目录或其他敏感路径。它不能增加能力。

[已知] A30 不提供外部编辑、shell、测试、debug、browser、E2E、Git 命令、精确 task-path 编辑或自动集成能力。

[工具结果] 当前 15 个选定角色的 frontmatter 已写入这种 deny-by-default 形状；`code-scout` 的当前 frontmatter 是直接检查到的代表样本，静态 checker 也枚举并检查全部 15 个角色。

[工具结果] `progress.txt` 与 capability-gap 文档记录局部静态 checker 退出 `0`，它确认了 15 个选定角色，但没有检查 ROSE 的互补 deny 合同。由于当前 `agents/rose.md` 为 `external_directory: ask`，这个结果是范围不完整的 false pass，不能称为 A30 整体静态 gate 通过。最后记录的 provider-backed runtime 结果是退出 `3`；[未验证] 没有 A30 后的新鲜 exit-0 证据，因此当前状态仍为 `Unverified`。

[未验证] 静态文件不能证明 Task 子会话在真实运行时的最终合并权限、规则来源、stored approval 或全局 override 缺失。

[已知] 如果运行时看到 `external_directory: allow`、有效 child `edit/bash/task: allow` 或其他意外 `allow/ask`，必须阻塞。如果不能看见最终 child 规则或不能证明 override 缺失，也必须退出 `3`。 [工具结果] 当前政策要求 ROSE 不得进行生产 A30 分派；[未验证] 仓库没有展示一个技术性 rollout kill switch，现有 frontmatter 仍可能触发 Task 和 `external_directory` ask，因此“禁用”目前依赖编排纪律，而不是 runtime 强制。

[已知] `auto`、`always`、yolo、skip-permission、全局工具 override 或存储的批准状态可能扩大外部读取范围。A30 不声称能在 stock runtime 中技术性检测所有这些状态。

[已知] 这里的隐私风险与写入风险不同。即使 edit/bash/task 最终仍被拒绝，`auto/always` 也可能让更多外部文件被读取并暴露给模型。

[工具结果] 当前实现与正式合同还有一个必须显式保留的冲突：合同多处写明 ROSE 应保持 `external_directory: deny`，但当前 `agents/rose.md` 写的是 `external_directory: ask`。当前静态 checker 明确把 ROSE 排除在“非选定角色必须 deny”的检查之外，因此“静态 gate 通过”不能消除这个合同冲突。

### CodeGraph 的角色

[已知] CodeGraph 是可选的、与当前 root 绑定的代码发现证据。它适合找文件、符号、调用关系和影响范围。

[已知] 初始化必须针对一个明确的当前 root。即使用户给了宽泛批准，也不能批量初始化多个仓库。

[已知] CodeGraph 过期、不可用或噪声太大时，应回退到直接搜索和读取。最终编辑与 verdict 仍需要新鲜文件和验证证据。

[已知] CodeGraph 输出不能单独证明实现正确、任务完成或 `/ship` 就绪。

### Graphify 的受控、人工角色

[已知] Graphify 基线被固定为 `Graphify-Labs/graphify` v0.9.12、commit `35665a76ba26da0e1bfcab074fede19c94fc5c89`、PyPI 包 `graphifyy`、可执行名 `graphify`、Python `>=3.10`、MIT。

[已知] `graphify install --platform opencode` 和 `graphify opencode install` 被排除，因为它们会修改 OpenCode/plugin 或可能修改 `AGENTS.md`。

[已知] Graphify 只能在用户明确请求并单独批准具体操作后，通过唯一受控 launcher 以 argv 数组和 `shell=False` 运行。输出应留在本地、未提交的新私有目录中，finding 只作建议。

[工具结果] 当前 `scripts/graphify_baseline_check.py` 已存在，并包含 contract、security evidence 和执行控制代码。

[工具结果] `progress.txt` 记录 Graphify contract mode 曾通过、security-evidence 曾退出 `3`，并且没有记录 Graphify execute mode 或真实 Graphify process 启动。 [未验证] 本次没有通过新鲜运行或独立进程证据证明 Graphify 从未启动。

[未验证] 网络静默、query/cache 副作用、依赖 advisory、当前安全支持、完整输出保证和真实执行安全仍未证明。因此 Graphify 真实执行操作保持阻塞，不能作为 lifecycle 或 completion authority。Graphify 未执行本身只阻塞这项可选操作；若要把 Graphify 缺陷列为 `/ship` blocker，必须另有尚未解决的 High/Important review finding，不能只以“没有运行 Graphify”为理由。

### 固定的 Matt Pocock / Addy Osmani 引用与薄适配

[已知] Matt Pocock 引用固定到 `mattpocock/skills@391a2701dd948f94f56a39f7533f8eea9a859c87`。Addy Osmani 引用固定到 `addyosmani/agent-skills@6bcfeb9dae52b11eaad23511acc165109746dbc3`。

[已知] 上游内容作为 inert data 放在现有 canonical skill 的 `references/upstream/...` 下。上游 `SKILL.md` 改名为 `SKILL.upstream.md`；Addy 脚本改名为 `idea-refine.upstream.sh` 并要求非可执行。

[已知] 引用带有根 MIT license、notice、源路径到本地路径映射和固定 blob/hash 信息。它们不注册为第二个可运行 skill。

[已知] 薄适配只把上游做法映射到 AILI 的 trigger、artifact、permission 和 stop condition，不复制一套新的生命周期权威。

[工具结果] 当前 `manifests/upstream-references.json` 已记录五组 canonical destination：`session-handoff`、`skill-authoring-and-validation`、`requirements-grilling`、`idea-refine`、`spec-driven-development`。

[未验证] 当前安装 catalog 的递归发现与 DrvFS 打包 mode 问题仍阻塞分发/启用证明。

### 生成的 OpenSpec 适配器

[工具结果] 当前生成或安装的 OpenSpec adapter 仍存在；[已知] 它们不属于 AILI-owned source，正式合同要求本变更不修改或控制它们。 [未验证] 没有可信的前后字节基线，因此本文不声称其内容实际未变。

[已知] AILI 不手改、不包裹、不屏蔽、不阻止，也不推荐用户通过这些直接 adapter 进入 AILI 生命周期。

[已知] 直接调用的行为是当前 OpenSpec 行为。它不在 AILI readiness、verification 或 completion 保证内。

[未验证] 这些 adapter 的直接运行输出没有被 AILI 做完整 runtime 验证，也不能拿来证明 AILI gate 已满足。

### Memory、handoff、安全与高风险边界

[已知] `rose-memory` 在 Stage I 是项目本地的 legacy/pre-runtime 连续性工具。范围清晰且安全时，可记录用户明确给出的要求、偏好、纠正和决定。

[已知] 模型推导的事实只能作为有证据的候选或 `Unverified` 项，不能升级成正式合同。

[已知] handoff 只有在用户明确要求时生成。它必须脱敏、以引用为主，不包含 secret、raw log、完整 transcript 或整份文件。

[已知] handoff 不授权恢复操作。恢复时仍要重新验证 root、Git、合同、权限和验证新鲜度。

[已知] 破坏性操作、外部 root、依赖/lockfile、secret、Graphify 执行、网络、发布、push、merge、archive、工作树删除或历史改写，都需要各自的当前明确批准。测试计划接受不代替这些批准。

## 实际实现状态

### 已实际实现

| 领域 | 当前证据 | 边界 |
|---|---|---|
| 四路命令与自然语言合同 | [工具结果] `commands/{ideate,define,build,ship}.md` 和 lifecycle reference 已包含统一分类、输入、输出和停止条件。 | [已知] 这是 AILI 路由合同，不控制直接 OpenSpec adapter。 |
| DCP 移除 | [工具结果] 当前 CLI、installer、docs、manifest 和测试表面包含 DCP 移除后的实现；历史 progress 也记录 Package 4 已实施。 | [未验证] A30 后没有重新做一次完整独立审计，旧日志不能证明当前版本通过。 |
| 中性 BUILD 与循环 | [工具结果] 当前 `build-execution-loop.md` 保留外层 profile、bounded loop 词汇、`CONT-005` budget 和 no-background 边界，并明确一次只选一个 primary loop。 | [已知] 不拥有原生 `/goal`，也不把 loop 词汇变成自动链。 |
| 连续性、memory、handoff | [工具结果] 当前 artifact contract、memory skill 和 handoff skill 已包含相应职责边界；历史 progress 记录 Package 3 已实施。 | [未验证] A30 后未重跑完整验证；这些 artifacts 本身也不是完成或权限证据。 |
| 完成检查合同 | [工具结果] 当前 lifecycle、artifact contract 和 build reference 要求 ROSE 直接检查 affected scope，并只在具体缺口时选择一个 auxiliary capability和一次 targeted recheck。 | [未验证] 模型层面的触发质量等待真实应用反馈。 |
| A30 静态角色配置 | [工具结果] 15 个角色清单、frontmatter、checker、fixture、probe 和 tests 已存在；局部 checker 返回 `0`。 | [未验证] checker 漏掉 ROSE 的 `external_directory` 合同冲突，因此整体静态 gate 是 false pass；最后记录的 runtime 结果为退出 `3`，当前仍无新鲜 exit-0 证据。 |
| CodeGraph policy | [工具结果] 当前合同已写入 exact-root、可选证据、fallback 和 no-proof 边界。 | [已知] 不证明正确或完成。 |
| Graphify fail-closed launcher | [工具结果] launcher 与 fixture 已存在；历史 progress 记录 contract mode 曾通过。 | [未验证] 该旧记录不是当前通过证明；最后记录的 security result 未通过，本次未取得真实执行证据。 |
| 固定上游引用 | [工具结果] provenance manifest、引用路径和 thin adapter 文件已存在。 | [未验证] 当前 catalog 与文件 mode 的分发安全仍未证明。 |

### 已规定但尚未证明或启用

| 领域 | 已规定的目标 | 当前状态 |
|---|---|---|
| A30 provider-backed runtime | [已知] 真实 Task 子会话应暴露最终合并权限与 provenance，并完成 forced negative/positive matrix。 | [工具结果] 最后记录结果为退出 `3`；[未验证] 没有 A30 后的新鲜 exit-0 证据，政策要求不进行生产分派，但缺少技术性 rollout 开关。 |
| A30 no-mutation runtime claim | [已知] 只有最终 child mutation/delegation tools 都被证明 deny 时才能成立。 | [未验证] stock runtime 不暴露足够 provenance，不能作该主张。 |
| A30 外部只读正例 | [已知] 应通过 ROSE Task 对批准路径完成一次只读访问。 | [未验证] 当前没有 rollout-eligible provider-backed exit `0`。 |
| Graphify 真实运行 | [已知] 需要单独操作许可、可信 executable、当前 security evidence、network deny、隔离环境和写入清单。 | [未验证] 最后记录的 security-evidence 结果为退出 `3`；当前没有可验证的真实运行证据。 |
| 上游引用分发安全 | [已知] 安装 catalog 必须证明引用不会成为 runnable skill，archive mode 必须正确。 | [未验证] catalog 输出与 DrvFS mode 仍阻塞。 |
| A30 后完整 Package 12 | [已知] 这是原伞形变更的历史要求，已被后续 direct-first、claim-matched 最小检查规则取代。 | [未验证] 历史矩阵未重跑不构成当前通用 completion gate。 |
| `/ship` readiness | [已知] 需要所有阻塞 gate 和重要 finding 解决，并有新鲜证据。 | [未验证] 当前明确不满足。 |

### 明确没有实现或已推迟

| 项目 | 处置 |
|---|---|
| 原生 `/goal` 行为 | [已知] Stage II / N/A；AILI 不实现。 |
| AILI-owned DCP | [已知] 已移除，不恢复。 |
| scheduler/listener/daemon/queue/hook/background loop | [已知] 明确不实现。 |
| 基线 manifest、通用 digest/receipt/nonce/revision gate | [已知] 明确拒绝；只保留未来名字。 |
| 工作树 registry/maintenance/自动 create-delete-reset-clean-prune-repair | [已知] 明确不实现。 |
| A27/A28/A29 独立 `opencode run --dir` worker | [已知] 被 A30 取代，作为未来能力缺口历史保留。 |
| 跨工作树 edit/test/debug/browser/E2E | [已知] 当前不实现。 |
| OS/filesystem/process hard sandbox | [已知] 当前不作保证。 |
| 自动 Git commit/merge/apply/integration | [已知] 明确不实现。 |
| 生成 OpenSpec adapter 的包裹、屏蔽或控制 | [已知] 推迟到 Phase II。 |
| Graphify 安装、注册、hook、定时或自动执行 | [已知] 明确不实现。 |

## 当前已知失败与阻塞

| 项目 | 新鲜度 | 当前含义 |
|---|---|---|
| A30 runtime 没有 exit-0 证据 | [工具结果] 最后记录的结果是退出 `3`。 | [未验证] A30 后没有新鲜重跑或 exit-0 证据；最终 child 权限/provenance 和 override 缺失无法证明，政策要求停止生产分派，但技术性禁用未被证明。 |
| A30 后完整独立 review 未重跑 | [工具结果] `progress.txt` 的下一步仍要求重跑静态/runtime gate 和独立 code/security/AI review。 | [未验证] 不能用旧 Package 12 join 宣布 A30 完成。 |
| ROSE `external_directory` 合同冲突 | [工具结果] 正式 A30 文本要求 ROSE deny；当前 `agents/rose.md` 为 ask；静态 checker 排除 ROSE。 | [开放问题] 需要在后续获批修复中统一合同、实现和 checker。 |
| Graphify security | [工具结果] `progress.txt` 记录 security-evidence 曾退出 `3`，且没有记录真实 execute。 | [未验证] 本次未独立证明从未启动；Graphify 可选真实执行仍无通过证据，该事实本身不自动等于 `/ship` blocker。 |
| 上游 packaging/catalog | [工具结果] 最新进度记录 C-UPSTREAM 退出 `5`，包括 DrvFS 的 0755/0644 mode 与 catalog 不完整问题。 | [未验证] 分发、注册和启用保持阻塞。 |
| residual / Node / npm | [工具结果] 历史最终矩阵记录 C-RESIDUAL=`5`、C-NODE=`1`、C-NPM=`1`，原因指向一个 stale exact occurrence。 | [未验证] A30 后没有新鲜重跑结果；这些是“仍需重跑确认”的历史失败，不应冒充当前已复现失败。 |
| release workflow gate | [工具结果] `progress.txt` 记录 `.github/workflows/release.yml` 不在当时接受的编辑范围内，自动发布 gate 未获批准修改。 | [未验证] 它对最终 `/ship` 的准确影响仍需结合接受范围和发布要求重新裁定；不能在本文中自动升级为已证实 blocker。 |
| 旧 74 行 audit 计数 | [工具结果] 旧快照是 50 Done、10 Partial、14 Blocked，但内容早于 A30 接受与实现。 | [已知] 数字已 stale；只能说明旧审计当时没有收敛。 |

## 未来 OpenCode fork 工作

[框架内] 未来 fork 应在最终权限合并后、第一次 tool call 可分派前，发出机器可读的 child permission/provenance diagnostic。它应列出 parent/child session、agent、按顺序的权限来源、compiled/effective rules、可见工具、override/approval 状态，以及 config/plugin/MCP/instruction 来源。

[框架内] 未来 runtime matrix 应由本地 mock provider 强制按固定顺序调用完整案例。模型跳过、添加或重排案例都不能算有效证据。

[框架内] 强制矩阵应覆盖外部 sentinel read、parent/target write、bash、嵌套 Task、未知/MCP/browser/plugin/custom 工具、Git refs/hooks/config/common-dir 写入和 fake secret 泄露。

[框架内] future target-root Task 应把 canonical target、repository/worktree identity、approval reference 和权限交集作为原生字段。权限语义应接近 parent ∩ role ∩ task，并让任一层 deny 保持 deny。

[框架内] 这些设计不能靠当前 packet 文本模拟，也不能靠“这次没观察到写入”证明权限不存在。

[已知] 完整技术设计、威胁模型、上游源文件候选、forced-call matrix 和退出码 `0/3/5` 合同见 [`opencode-cross-worktree-capability-gaps.md`](./opencode-cross-worktree-capability-gaps.md)。本文不重复整份 fork 设计。

## 实用用户旅程

### 旅程 1：普通问题

用户：`解释一下为什么测试计划是唯一审批。`

[已知] 这是普通解释。系统回答概念，不创建 OpenSpec change，不写 artifact，也不启动 BUILD。

### 旅程 2：正式功能

用户：`为新的缓存策略写正式方案，并准备实现。`

[已知] 这触发 DEFINE。系统创建或复用一个 change，写 proposal/spec/design/tasks/interview/test-plan/context，解决实质性问题并严格验证。

[已知] 用户明确接受最终 test plan 后，状态只变为可供未来明确 BUILD。系统仍需等“开始实现”以及操作权限检查。

### 旅程 3：BUILD 中纠正需求

用户：`继续，但把验收条件改成离线也必须通过。`

[已知] 这不是普通 continue，而是 material delta。系统返回 DEFINE，更新并重新读取受影响材料，旧 test-plan acceptance 变 stale，不恢复 BUILD。

### 旅程 4：模糊 continue

用户：`继续。`

[已知] 若只有一个活动 envelope，目标、阶段、授权、接受和预算都明确，系统可以恢复并保留已消耗预算。

[已知] 若存在多个 change、接受过期、预算耗尽或没有活动 envelope，系统只问一个聚焦问题，不执行、不写入、不消耗预算。

### 旅程 5：“实现然后 ship”

用户：`实现这个 change，然后 ship。`

[已知] 当前只授权 BUILD 意图。系统可以记录用户希望后续 SHIP，但不能预授权 SHIP，也不能自动跨阶段。

[已知] BUILD 后仍需要新鲜实现/review/verification 证据，以及新的明确 SHIP 意图。

### 旅程 6：审查外部 worktree

用户：`让 code-reviewer 只读审查已声明 attachment。`

[已知] 当前路线先独立通过 A33 attachment admission 与 exact operation/risk gate，再由 ROSE 判断是否存在 concrete review capability gap。默认直接工作；若确需 Task，只创建一次 fresh bounded context，target rules 只可收窄，artifact 留在 owning repository。

[已知] A30 provider-backed runtime 结果仅是历史证据，不能授权或阻塞 A33。系统也不能把静态 frontmatter 当成真实隔离/no-mutation 证明。

## 常见问题

### 接受 test plan 后，为什么还不能立即执行？

[已知] 因为接受 test plan 只确认“如何验收”。BUILD 还需要明确实现意图、唯一目标、当前权限、可运行 package、有效预算和安全 gate。

### tasks.md 都打勾了，是否表示完成？

[已知] 不是。checkbox 只是一条状态提示。当前完成主张需要 affected task/requirement 与实现的链接，以及 canonical owner 选择的最小新鲜证据；只有具体缺口才增加 review 或完整矩阵。

### 为什么不让 reviewer 投票？

[已知] 因为安全或正确性 finding 的价值取决于证据，不取决于人数。一个有证据的重要少数意见不能被多个空泛 PASS 覆盖。

### `continue` 为什么这么严格？

[推断] 因为“继续”像“接着开车”，但没有说明是哪辆车、哪条路、油量是否够、驾照是否仍有效。严格恢复规则避免把模糊语言变成新授权。

### A30 为什么只能读？

[已知] stock OpenCode v1.17.18 的内置 Task 不能原子地绑定另一个 target root 和精确 per-task permission overlay。只读范围更容易失败关闭，但仍需要 runtime provenance 才能启用。

### `external_directory: ask` 是否保证安全？

[已知] 不是。ask 只控制跨 workspace 请求。它不是 target identity、工作树批准、写入隔离或 OS sandbox。真正的 A30 防写依赖最终 child profile 中所有 mutation/delegation tools 仍为 deny。

### CodeGraph 和 Graphify 谁是权威？

[已知] 都不是完成权威。CodeGraph 帮助发现代码；Graphify 提供建议性图分析。最终结论仍依赖当前文件、测试、review 和安全证据。

### 用户能直接运行 `/opsx-*` 吗？

[已知] 当前可以，但那是直接 OpenSpec 行为，位于 AILI 四路保证之外。它的输出不能自动证明 AILI gate 已通过。

### 当前能 `/ship` 吗？

[工具结果] 不能据现有证据宣布 ready。A30 静态合同冲突、A30 runtime、完整复审、上游 packaging/catalog、历史 residual/Node/npm 重跑和 release gate 仍有阻塞或未验证项。 [未验证] Graphify 可选执行仍被禁用，但只有独立的未解决 High/Important finding 才能让其成为 `/ship` blocker。

## 术语表

| 术语 | 通俗解释 |
|---|---|
| AILI | [已知] 本仓库定义的交付工作流与 harness。 |
| ROSE | [已知] 负责分类、编排、证据汇总和最终用户报告的主代理。 |
| OpenSpec | [已知] 正式变更的 proposal/spec/design/tasks 后端。 |
| Stage I | [已知] 不修改 OpenCode 原生 runtime 的当前工作流层。 |
| Ordinary | [已知] 单一、有边界、当前会话可完成且不触及实质合同的请求。 |
| Formal/material | [已知] 需要正式变更或会改变合同、风险、架构、权限、验收等的请求。 |
| Envelope | [已知] 记录触发、目标、合同、预算、gate、允许动作、停止原因和结果的统一容器。 |
| Savepoint | [已知] Package 1–11 的轻量进度点，不是完成证明。 |
| Convergence | [已知] 把 requirement、task、实现、验证、review 和 disposition 连成完整证据链。 |
| Pseudo-complete | [已知] 看似完成，例如 checkbox 已勾，但缺少任务特定新鲜证据。 |
| A30 | [已知] 同实例内置 Task 的 15 角色外部只读静态方案。 |
| Provider-backed | [已知] 使用真实模型/provider 调度路径，而不只是解析静态文件。 |
| Fail-closed | [已知] 证据不足或控制不可见时停止并禁用，而不是猜测安全。 |
| Worktree | [已知] 同一 Git 仓库的另一个工作目录。 |
| CodeGraph | [已知] 可选的代码索引与发现工具。 |
| Graphify | [已知] 可选的本地代码图分析工具；当前真实运行受阻。 |
| Generated adapter | [已知] 由外部工具生成或安装的 OpenSpec 直接入口，不由 AILI 生命周期保证。 |

## 证据与来源地图

[已知] `progress.txt` 是执行状态账本，但其历史段不会自动重写。当前状态应优先采用最后写入的 A30 条目，并同时列出它与早期 progress 段及正式 artifacts 的冲突。proposal、spec、design、tasks、interview 和 test-plan 分别拥有正式合同、决定、任务和验收内容；正式材料未统一前，不得声称合同整体一致或严格验证完成。

[已知] `openspec/` 在本仓库中属于忽略的运行/本地输出范围。Git status 或普通 diff 看不到这些文件时，不能声称它们未改变；必须直接读取。

| 来源 | 本文使用位置 | 主要作用 |
|---|---|---|
| `openspec/changes/complete-aili-workflow-orchestration/proposal.md` | “以前出了什么问题”“明确移除了什么”“没有被碰掉的用户能力” | [已知] 本地忽略文件；拥有总范围、breaking removal、A30 与非目标，不可作为发布包中的可点击链接。 |
| `openspec/changes/complete-aili-workflow-orchestration/design.md` | “新增或改变了什么”“两层循环”“A30”“Graphify” | [已知] 本地忽略文件；拥有分类、artifact、review、loop、权限和工具设计。 |
| `openspec/changes/complete-aili-workflow-orchestration/tasks.md` | “Package 1–12”“74 行审计” | [已知] 本地忽略文件；拥有 package 依赖、所有权和 74 个 task。 |
| `openspec/changes/complete-aili-workflow-orchestration/context.md` | “实际实现状态”“明确没有实现” | [已知] 本地忽略文件；维护合同摘要、接受限制和术语边界。 |
| `openspec/changes/complete-aili-workflow-orchestration/test-plan.md` | “测试计划审批”“A30 runtime”“失败与阻塞” | [已知] 本地忽略文件；拥有命令、退出码、覆盖矩阵和验收语义。 |
| `openspec/changes/complete-aili-workflow-orchestration/progress.txt` | “实际实现状态”“当前失败与阻塞” | [已知] 本地忽略文件；是包含历史段的执行状态账本，最后 A30 条目优先但必须与冲突一起解释。 |
| `openspec/changes/complete-aili-workflow-orchestration/drift-log.md` | “为什么有伞形提案”“Package 12”“A30” | [已知] 本地忽略文件；记录 review 策略、任务审计和 A30 架构变化。 |
| `openspec/changes/complete-aili-workflow-orchestration/task-audit.json` | “74 行审计”“旧计数 stale” | [工具结果] 本地忽略的 A30 前 74 行快照；不能当当前计数。 |
| `openspec/changes/complete-aili-workflow-orchestration/interview.md` | “用户决定”“OQ-005”“A30” | [已知] 本地忽略文件；记录 A1–A30 决定与 OQ-005 接受。 |
| [`opencode-cross-worktree-capability-gaps.md`](./opencode-cross-worktree-capability-gaps.md) | “A30”“未来 OpenCode fork 工作” | [已知] v1.17.18 能力缺口、静态/runtime 区分和未来 fork 设计。 |
| [`lifecycle.md`](../../.agents/skills/aili-delivery-flow/references/lifecycle.md) | “四路路线”“continuation”“SHIP” | [工具结果] 当前安装源中的生命周期行为。 |
| [`build-execution-loop.md`](../../.agents/skills/aili-delivery-flow/references/build-execution-loop.md) | “两层循环”“budgets”“Package” | [工具结果] 当前中性 BUILD 权威。 |
| [`artifact-contracts.md`](../../.agents/skills/aili-delivery-flow/references/artifact-contracts.md) | “Artifact 责任表”“savepoint”“task audit” | [工具结果] 当前 artifact 和 convergence contract。 |
| [`delegation_protocols_check.py`](../../scripts/delegation_protocols_check.py) | “A30 静态配置”“合同冲突” | [工具结果] 15 角色检查、工具清单与 ROSE 例外。 |
| [`opencode_permission_probe.mjs`](../../scripts/opencode_permission_probe.mjs) | “A30 runtime” | [工具结果] 当前 fail-closed provider-backed probe，默认无法取得最终 child provenance。 |
| [`agents/rose.md`](../../agents/rose.md) 与 [`agents/code-scout.md`](../../agents/code-scout.md) | “A30 静态配置”“ROSE 冲突” | [工具结果] 当前主代理与代表性只读角色 frontmatter。 |
| [`graphify_baseline_check.py`](../../scripts/graphify_baseline_check.py) | “Graphify 的受控角色” | [工具结果] 当前 guarded launcher 实现。 |
| [`upstream-references.json`](../../manifests/upstream-references.json) | “固定上游引用” | [工具结果] 固定 commit、路径、hash、license、mode 和 catalog exclusion 数据。 |

### 已显式保留的冲突

[工具结果] `test-plan.md` 顶部和 `design.md` 的旧 gate 段仍写着 OQ-005 待接受、BUILD 被阻塞；较新的 `interview.md` OQ-005 Resolution 与最新 `progress.txt` 写明 A30 已接受且实现 savepoint 完成。本文采用后者作为当前执行状态，并把前者标记为 stale formal-state text。

[工具结果] `tasks.md` 的 6.1–6.5、12.2、12.3、12.5、12.7 等 A30 行仍未勾选；最新 `progress.txt` 记录 A30 静态实现已经完成。checkbox 不能覆盖更新的实现证据，也不能单独证明 Done。

[工具结果] `task-audit.json` 仍写着 A30 item 40/OQ-005 待接受、frontmatter/checker/runtime 未实现；这与最新进度和当前文件冲突。因此旧 audit 只能作为 A30 前历史快照。

[工具结果] 正式 A30 合同要求 ROSE 与 command-capable roles 保持外部目录 deny；当前 `agents/rose.md` 为 ask，且 checker 对 ROSE 例外处理。本文不把这个矛盾平滑成“已满足”。

## 最朴素的结论

[已知] 当前价值很明确：AILI 的四路入口、正式/普通分类、OpenSpec 默认写回、单一测试计划接受门、连续性边界、中性 BUILD、两层循环、Package 12 收敛、DCP/伪 Goal 移除、CodeGraph/Graphify 边界和 A30 只读意图，都已经被组织成一套比旧草案更清楚、更失败关闭的合同。

[工具结果] 当前仓库也已经有大量对应实现，包括四个命令、lifecycle/build/artifact references、A30 的 15 个角色 frontmatter、静态 checker、runtime probe、Graphify launcher 和上游 provenance manifest。

[未验证] 但“写好了静态规则”不等于“真实 Task runtime 已安全工作”。15 角色局部 checker 的 exit `0` 因漏检 ROSE 冲突而构成 false pass；最后记录的 A30 provider-backed gate 结果是退出 `3`，且没有 A30 后的新鲜 exit-0 证据。当前禁用主要依赖编排政策而非技术开关，A30 后完整独立复审未重跑，上游分发仍阻塞，旧 residual/Node/npm 失败也尚未得到新鲜复核。Graphify 可选执行仍缺少通过证据，但不能仅凭未执行就把它列为 `/ship` blocker。

[推断] 因此当前正确结论是：这套工作流已经提供有用的结构和大量静态实现，但跨工作树 runtime、完整收敛和发布准备尚未就绪；不得据此宣称 `/ship` ready。
