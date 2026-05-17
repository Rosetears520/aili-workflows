# 变更采访包：strengthen-rose-delegation-protocols

## 1. 资料来源与证据

| 来源 | 已检查内容 | 观察到的事实 | 置信度 | 备注 |
|---|---|---|---|---|
| `openspec/changes/strengthen-rose-delegation-protocols/proposal.md` | Why / What Changes / Capabilities / Impact | 变更目标是把 ROSE 直接执行边界、context-saving mandatory delegation、`repo-evidence-first`、`session-handoff`、code locality mapping、subagent task/result 协议固化成 OpenSpec 合约；用户已批准 BUILD 修改核心 harness 文件。 | high | BUILD 已执行，scope 仍限制为已批准文件，不包含依赖/lockfile/schema/install/commit/push。 |
| `openspec/changes/strengthen-rose-delegation-protocols/design.md` | Context / Goals / Decisions / Risks / Migration / Open Questions | 设计已选择 direct allowlist 四条件、mandatory delegation、`code-scout` locality map、中文 `repo-evidence-first`、`session-handoff` 非 memory、facts/inferences/recommendations 分离、`agents/rose.md` 短 router。 | high | 问卷答案已吸收；旧 `add-harness-evolution-layer` 已归档且未同步旧 delta specs。 |
| `openspec/changes/strengthen-rose-delegation-protocols/specs/delegation-protocols/spec.md` | ADDED Requirements / Scenarios | 规范已覆盖 direct allowlist、context-saving delegation、repo evidence first、code locality mapping、session handoff、task packet、canonical protocol authority、result evidence separation、minimal ROSE router。 | high | 规范是可测试方向，但部分“如何验证”仍需用户选择。 |
| `openspec/changes/strengthen-rose-delegation-protocols/tasks.md` | Implementation checklist | tasks 已拆成 scope/evidence、direct-vs-delegated、repo-evidence-first、session-handoff、subagent dispatch/code locality、protocols、ROSE router、verification。 | high | 任务项是草案；是否先处理 `add-harness-evolution-layer` overlap 仍待确认。 |
| `git status --short --branch --untracked-files=all` | 当前工作区状态 | 当前分支为 `define/context-saving-delegation-proposal`；除本 change 外，`.opencode/`、`docs/research/`、`openspec/changes/add-harness-evolution-layer/` 和 `openspec/config.yaml` 等也处于 untracked。 | high | 这些既有 untracked 项不是本问卷生成动作创建的，但会影响后续 scoped diff/commit 边界。 |

## 2. 当前理解

- 目标：把“ROSE 主 agent 只直接做小而确定的改动；复杂、证据分散、上下文污染或需要专业判断的任务必须进入 subagent/gate”落成可实施、可审查、可验证的 OpenSpec change。
- 当前草稿表达的是：新增/更新一组 harness 规则和技能，而不是直接实现业务功能。
- 现有文档显示：本 change 是 `add-harness-evolution-layer` 之后的 narrow follow-up；旧 change 已归档，不同步其旧 delta specs。
- 已确认约束：用户已批准修改 `agents/rose.md`、skills、subagent protocols；仍不新增依赖、不改 lockfile、不改 SQLite schema、不 commit/push、不修改未批准的 unrelated untracked 文件。
- 暂定非目标：不新增内部阶段顶层命令；不批量重写所有 subagent；不把 `session-handoff` 当长期 memory；不把顶层 `protocols/**` 作为第二套协议权威。
- 仍不确定的地方：运行时 ROSE/subagent 是否会完全遵循这些静态文档规则尚未 live-simulate；新 skills 的下游安装/发现流程未在本次验证中执行。

## 3. 需要你填写的问题

| ID | 问题 | 为什么要问 | 推荐默认答案 | 取舍影响 | 你的填写 | 写回位置 |
|---|---|---|---|---|---|---|
| Q1 | 这个 change 是否继续作为 `add-harness-evolution-layer` 的独立 follow-up，而不是合并/替换原 change？ | 影响后续 BUILD 顺序、scope 边界和是否要迁移既有 artifacts。 | 继续作为独立 follow-up；只在 BUILD 前做 overlap reconciliation。 | 独立 follow-up 更安全、可回滚；合并原 change 会扩大范围并可能需要处理大量 stale/untracked 文件。 | `add-harness-evolution-layer` 这个可以归档了 | `proposal.md`, `design.md`, `tasks.md` |
| Q2 | 后续是否允许进入 BUILD 修改核心 harness 文件，还是当前只停在 proposal/questionnaire？ | 影响是否可以编辑 `agents/rose.md`、skills、subagent prompt/protocols。 | 当前先停在 DEFINE；等你确认问卷答案后再决定 BUILD。 | 先停住能避免把未确认项写成事实；直接 BUILD 会更快但风险更高。 | 允许改核心 | `tasks.md` 1.1, final status |
| Q3 | 是否保留当前已写入的 canonical decision：subagent packet/result protocol 路径使用 `skills/aili-delivery-flow/references/protocols/`？ | 之前 broader change 提到过顶层 `protocols/**`，双权威会导致规则漂移。 | 保留当前 decision：使用 `skills/aili-delivery-flow/references/protocols/`；顶层 `protocols/**` 只做索引/兼容链接。 | skill-local path 更贴合当前 runtime charter；顶层 path 更像全局协议面，但会增加重复风险。 | 保留当前 decision：使用 `skills/aili-delivery-flow/references/protocols/`；顶层 `protocols/**` 只做索引/兼容链接。 | `design.md`, `specs/delegation-protocols/spec.md`, `tasks.md` 1.3/6.x |
| Q4 | `add-harness-evolution-layer` 中可能存在的 stale task/file-path evidence 是否必须先修复，才能实现本 change？ | 后续 implementation 可能读到已勾选但工作树不存在的文件，影响证据可靠性。 | 不阻塞本 proposal；BUILD 前必须执行 reconciliation，发现冲突则先处理或标记 blocked。 | 先修复最干净但会扩大 scope；BUILD 前 reconciliation 保持本 change 小而明确。 | 先修复 | `design.md` Open Questions, `tasks.md` 1.2 |
| Q5 | Direct allowlist 是否采用当前四条件：exact target、low risk、surgical、locally verifiable、no convention discovery？ | 这是 ROSE 能否直接做小改的核心边界。 | 同意当前四条件。 | 更宽会减少 subagent 调度但增加猜测风险；更窄会更安全但可能过度派发。 | 还有一个，如果开subagent可以节省上下文就开 | `specs/delegation-protocols/spec.md`, `direct-vs-delegated-work.md` |
| Q6 | Direct allowlist 是否包含“单个非安全、非发布、非数据语义参数”的小改？ | 参数改动有时看似小但可能改变行为语义。 | 保留，但必须同时满足 low-risk 和 local verification；涉及安全/发布/数据语义时排除。 | 保留能覆盖小配置微调；删除会让更多任务进入 gate。 | 保留 | `proposal.md`, `specs/delegation-protocols/spec.md` |
| Q7 | Mandatory delegation 的阈值是否确认使用 `3+ files`、`2+ directories/subsystems`、`2+ search passes`？ | 阈值决定 subagent 是否足够积极。 | 同意硬触发；只有未命中 mandatory triggers 且满足 direct allowlist 时才可跳过，并必须说明理由。 | 硬阈值可审查；想增加例外必须同步改 spec/design，否则会削弱 mandatory 语义。 | 同意 | `direct-vs-delegated-work.md`, `parallel-subagent-dispatch/SKILL.md` |
| Q8 | `code-scout` locality map 是否必须包含 upstream、downstream、peer patterns、tests/verification、freshness、next reads、risk notes、conclusion？ | 影响 code-scout 是“grep worker”还是“代码邻域定位 agent”。 | 必须包含；如果某项未找到，显式写 `N/A` 或 `unknown`。 | 完整 map 更可靠；格式更长但能减少 ROSE 主观猜测。 | 必须包含；如果某项未找到，显式写 `N/A` 或 `unknown`。 | `agents/code-scout.md`, `subagent-result.md` |
| Q9 | `repo-evidence-first` 的正文是否确认用中文，文件路径/skill name 保持英文？ | 用户已提出“最终文档中文”，但技能 metadata/路径通常英文。 | 正文中文；frontmatter name/path 英文；保留英文术语和 file paths。 | 中文便于你审查；英文 path 便于 agent routing。 | 正文中文；frontmatter name/path 英文；保留英文术语和 file paths。 | `skills/repo-evidence-first/SKILL.md` |
| Q9a | `repo-evidence-first` 和 `session-handoff` 是否确认直接落到仓库 `skills/`，而不是先放 OpenCode user config 后同步？ | `design.md` 仍把 repo-local vs user-config 作为 open question；tasks 当前默认写 repo-local `skills/`。 | 直接落到仓库 `skills/`，作为本 repo 的可审查、可版本化 runtime artifacts。 | repo-local 最利于 review/版本控制；user config 更快试验但不利于团队共享和 OpenSpec 验证。 | 直接落到仓库 `skills/`，作为本 repo 的可审查、可版本化 runtime artifacts。 | `design.md` Open Questions, `tasks.md` 3.x/4.x |
| Q10 | `repo-evidence-first` 是否应是每次非平凡规划/编辑/审查/完成声明前的 gate？ | 决定触发强度，避免 ROSE 再凭项目传统猜测。 | 是；但 direct allowlist 小改可跳过完整包，只需说明符合 direct 条件。 | 强触发更安全；弱触发更快但可能复发“凭经验猜”。 | 是 | `skills/repo-evidence-first/SKILL.md`, `agents/rose.md` router |
| Q11 | `session-handoff` 是否默认写到 `openspec/changes/<change-id>/handoff.md`，而不是 `docs/current/**`？ | OpenSpec source 有确定落点；非 OpenSpec 才需要询问/选择位置。 | OpenSpec change 默认写入 change directory；非 OpenSpec 需要确认落点。 | 默认写 change 目录便于恢复；全局 `docs/current` 更统一但可能污染仓库。 | OpenSpec change 默认写入 change directory；非 OpenSpec 需要确认落点。 | `skills/session-handoff/SKILL.md`, `specs/delegation-protocols/spec.md` |
| Q12 | `session-handoff` 是否允许自动创建文件，还是必须由用户显式要求？ | 影响压缩前/阻塞时是否自动保存当前任务状态。 | 仅在长会话、压缩前、BLOCKED/IDLE、切换 session 或用户明确要求时自动创建；普通任务不创建。 | 自动创建提高恢复能力；过度创建会产生文档噪声。 | 仅在用户明确要求时创建 | `skills/session-handoff/SKILL.md` |
| Q13 | subagent result protocol 中 facts/inferences/recommendations 是否必须强制分栏？ | 这是防止 ROSE 把子代理建议当事实的关键。 | 对 harness-sensitive、review/test/security/debug、evidence-heavy 任务强制；小型只读 scout 可用简化但仍要区分事实与建议。 | 强制分栏最清楚；全量强制可能让小 scout 输出过重。 | 按你的来 | `subagent-result.md`, `parallel-subagent-dispatch/SKILL.md` |
| Q14 | `agents/rose.md` 后续实现是“只加短 router”，还是也删除/瘦身现有旧的长段落？ | 影响 diff 大小和回归风险。 | 本 change 只加短 router/引用；旧段落瘦身另开 change 或在明确批准后做。 | 只加短 router 最安全；同时瘦身可减少重复但更难验证。 | 按你的来 | `agents/rose.md`, `tasks.md` 7.x |
| Q15 | 验证是否需要新增/更新 fixture runner，还是只做结构/内容检查 + OpenSpec validation？结构/内容检查允许人工 checklist，还是必须提供可运行脚本/命令和明确 PASS/FAIL 输出？ | 用户想让规则“可审查”，但是否要自动化 fixture 仍未定；manual checklist 与脚本化检查的成本/可靠性不同。 | 本 change 至少做 OpenSpec strict validation、文件存在检查、必填字段内容检查；若你要求可执行检查，则批准新增零依赖脚本或复用既有 runner，并定义 PASS/FAIL 输出。 | 人工 checklist 轻量但不可回归；脚本化检查更可靠但扩大实现范围。 | 全做 | `tasks.md` 8.2/8.3, optional test plan |
| Q16 | 后续实现时是否需要 review-pipeline/security-auditor/test-engineer 全量跑一遍？ | 这类变更改 agent workflow/harness 规则，错误会影响后续所有任务。 | BUILD 后至少运行 code-reviewer + test-engineer；security-auditor 仅在触及 secrets/tool permissions/memory/install/hook 时必跑。 | 全量 review 更安全；按触发条件跑更省成本。 | BUILD 后至少运行 code-reviewer + test-engineer；security-auditor 仅在触及 secrets/tool permissions/memory/install/hook 时必跑。 | `tasks.md` 8.5, closeout report |
| Q17 | 对现有 untracked `.opencode/`、`docs/research/`、`add-harness-evolution-layer/` 文件，后续是否允许本 change 引用/修改？ | 当前工作区已有大量 untracked 文件，可能污染 diff 边界。 | 本 change 不修改这些文件；只在 evidence/reconciliation 中引用。需要修改时另行批准。 | 保持隔离最安全；直接修改可顺手修复 overlap 但 scope 变大。 | 本 change 不修改这些文件；只在 evidence/reconciliation 中引用。需要修改时另行批准。 | `tasks.md` 1.2/8.4 |
| Q18 | 接受推荐默认答案时，我是否可以把“同意默认”的项直接写回 proposal/design/spec/tasks？ | 决定下一步是否继续问，还是可进入 write-back。 | 可以；未填写项继续保留为 `Open Question`，不写成事实。 | 这样能快速收敛；如果不允许，则必须逐项确认。 | 可以 | `interview.md`, later write-back log |

## 4. 设计漏洞 / 证据缺口 / 反例

| ID | 类型 | 说明 | 建议处理方式 | 状态 |
|---|---|---|---|---|
| L1 | Contradiction | `design.md` 已把 canonical protocol path 固定到 `skills/aili-delivery-flow/references/protocols/`，但既有 broader change 曾提到顶层 `protocols/**`。 | Q3 已确认 skill-local canonical；旧 change 已归档，顶层 path 只允许做索引/兼容链接。 | resolved |
| L2 | Missing evidence | `add-harness-evolution-layer` overlap/stale 状态目前只在本 change 中作为风险记录，没有完成 reconciliation。 | Q4 已确认先处理；BUILD 前已归档旧 change，未同步旧 delta specs。 | resolved |
| L3 | Verification gap | mandatory delegation、repo evidence、session handoff 和 code locality map 是行为规则，单靠 OpenSpec validation 不能证明 runtime 会遵守。 | Q15 已确认全做；已新增并运行 `scripts/delegation_protocols_check.py`，runtime behavior 仍标为 `Unverified`。 | resolved_with_unverified_runtime |
| L4 | Scope risk | 同时新增两个 skills、一个 reference doc、改 parallel dispatch、改 code-scout、改 subagent protocols、改 ROSE router，可能一次 BUILD 太大。 | 用户批准核心 edits；BUILD 后 code-review/test/security gate 已运行，scoped status/diff 已记录。 | resolved |
| L5 | Over-trigger risk | mandatory delegation 如果过硬，typo/小文档也可能被误派 subagent。 | Q5/Q7/Q10 已确认；direct allowlist + “跳过必须说明原因”写入 specs/reference/router。 | resolved |
| L6 | Memory boundary risk | `session-handoff` 容易被误当 durable memory 或把 raw logs 写入 memory。 | Q11/Q12 已确认；skill 明确仅用户要求时创建，且排除 raw logs/secrets/default durable memory promotion。 | resolved |
| L7 | Diff boundary risk | 当前工作区已有非本 change 的 untracked 文件，后续实现/提交容易混入。 | Q17 已确认；SHIP scoped status/diff 区分 in-scope files 与 unrelated `.opencode/**`、`docs/research/**`、`openspec/config.yaml`。 | resolved |

## 5. 填写说明

- 可以直接在“你的填写”列里写答案。
- 不确定的地方写“不确定”即可。
- 接受推荐默认答案时，写“同意默认”。
- 不进入本次 scope 的内容，写“本次不做”。
- 未填写内容不会被写成事实，只会保留为 `Open Question`。
- 无证据支撑但暂时保留的内容会标为 `Unverified`。
- 如果你想快速推进，可以回复：“全部同意默认，除了 Qx=...”。

## 6. 后续写回映射

| 用户答案 | 将写回到 | 写回方式 |
|---|---|---|
| Q1 | `proposal.md`, `design.md` | 确认 change 与 `add-harness-evolution-layer` 的关系和 scope 边界。 |
| Q2 | `tasks.md` | 更新 implementation approval gate 和下一步状态。 |
| Q3 | `design.md`, `specs/delegation-protocols/spec.md`, `tasks.md` | 固化 canonical protocol authority path 或记录替代决策。 |
| Q4 | `design.md`, `tasks.md` | 决定 overlap reconciliation 是否阻塞 BUILD。 |
| Q5-Q7 | `specs/delegation-protocols/spec.md`, future `direct-vs-delegated-work.md` | 调整 direct allowlist 和 mandatory delegation 阈值。 |
| Q8 | `specs/delegation-protocols/spec.md`, future `agents/code-scout.md` | 调整 code locality map 必填字段。 |
| Q9-Q10 | future `skills/repo-evidence-first/SKILL.md`, `agents/rose.md` router | 确认中文正文、触发范围和路由边界。 |
| Q9a | `design.md`, `tasks.md`, future `skills/**` paths | 确认 `repo-evidence-first` 和 `session-handoff` 落到 repo-local `skills/` 还是 user config。 |
| Q11-Q12 | `specs/delegation-protocols/spec.md`, future `skills/session-handoff/SKILL.md` | 确认 handoff placement、触发条件和 memory 边界。 |
| Q13 | future `subagent-result.md`, `parallel-subagent-dispatch/SKILL.md` | 确认 facts/inferences/recommendations 分离强度。 |
| Q14 | `tasks.md`, future `agents/rose.md` diff | 决定仅短 router 还是顺带瘦身旧段落。 |
| Q15-Q16 | `tasks.md`, optional test plan/closeout | 调整验证命令、fixture/static checks、review pipeline 要求。 |
| Q17 | `tasks.md`, final closeout | 确认 scoped diff/commit 边界，避免混入其他 untracked 文件。 |
| Q18 | 后续 write-back log | 决定是否可批量吸收默认答案。 |

## 7. 答案吸收记录

| 问题 | 用户答案 | 形成的决策 | 已写回位置 | 剩余不确定 |
|---|---|---|---|---|
| Q1 | `add-harness-evolution-layer` 可以归档 | 旧 change 按用户批准归档；本 change 作为当前 BUILD 权威 | `proposal.md`, `design.md`, `tasks.md` | 无 |
| Q2 | 允许改核心 | BUILD 可修改 `agents/rose.md`、skills、protocol refs | `proposal.md`, `design.md`, `tasks.md` | 无 |
| Q3 | 保留 canonical path | `skills/aili-delivery-flow/references/protocols/` 是本 change 唯一协议权威 | `proposal.md`, `design.md`, `spec.md`, `tasks.md` | 无 |
| Q4 | 先修复 | BUILD 前归档 stale/conflicting old change，未同步旧 delta specs | `design.md`, `tasks.md` | 无 |
| Q5 | 如果开 subagent 可以节省上下文就开 | direct allowlist 不能覆盖 context-saving mandatory delegation | `spec.md`, `direct-vs-delegated-work.md` | 无 |
| Q6 | 保留 | 单个非安全/非发布/非数据语义参数仍可 direct，但必须 low-risk 且 local verification | `spec.md`, `direct-vs-delegated-work.md` | 无 |
| Q7 | 同意 | 使用硬触发阈值；跳过需说明 direct allowlist 与无 material context savings | `direct-vs-delegated-work.md`, `parallel-subagent-dispatch/SKILL.md` | 无 |
| Q8 | 必须包含；未找到写 `N/A`/`unknown` | `code-scout` 输出 locality map 必填字段 | `agents/code-scout.md`, `subagent-result.md` | 无 |
| Q9 | 中文正文，英文 name/path | `repo-evidence-first` 正文中文、frontmatter/path 英文 | `skills/repo-evidence-first/SKILL.md` | 无 |
| Q9a | 直接落到仓库 `skills/` | 两个新 skills repo-local、可版本化 | `design.md`, `tasks.md` | 无 |
| Q10 | 是 | 非平凡规划/编辑/审查/完成声明前使用 repo evidence gate；direct 小改可简化说明 | `repo-evidence-first/SKILL.md`, `agents/rose.md` | 无 |
| Q11 | OpenSpec change 默认写入 change directory | handoff path follows artifact source | `spec.md`, `session-handoff/SKILL.md` | 无 |
| Q12 | 仅用户明确要求时创建 | 不自动创建 handoff 文件，除非用户明确要求或后续已批准命令合同要求 | `spec.md`, `session-handoff/SKILL.md` | 无 |
| Q13 | 按模型推荐 | harness-sensitive/review/test/security/debug/evidence-heavy 强制分栏，小型 scout 可简化但仍区分事实与建议 | `subagent-result.md`, `parallel-subagent-dispatch/SKILL.md` | 无 |
| Q14 | 按模型推荐 | `agents/rose.md` 只加短 router，不做旧段落瘦身 | `agents/rose.md`, `tasks.md` | 无 |
| Q15 | 全做 | 添加零依赖 PASS/FAIL 结构/内容检查脚本，并运行 OpenSpec validation | `tasks.md`, `scripts/delegation_protocols_check.py` | 无 |
| Q16 | code-reviewer + test-engineer；security 条件触发 | BUILD 后运行 review/test gate；security-auditor 仅在触及 secrets/tool permissions/memory/install/hook 时必跑 | `tasks.md`, closeout | 无 |
| Q17 | 不修改其他 untracked；需要另批 | 除已单独批准归档 old change 外，不修改 `.opencode/`、`docs/research/` 等 unrelated untracked | `tasks.md`, closeout | 无 |
| Q18 | 可以 | 默认答案和明确答案可写回；未填写项不写成事实 | 本表 | 无 |
