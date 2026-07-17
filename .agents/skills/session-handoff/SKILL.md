---
name: session-handoff
description: 当用户明确要求交接、恢复提示或会话 handoff 时，生成当前任务的轻量 Markdown 交接文档；不自动写入 durable memory，不包含 secrets/raw logs/full files。
---

# Session Handoff

这个技能用于给下一模型导航当前任务，不是长期 memory、正式合同、权限、Git 真相、验证结果或完成证明。只有用户明确要求 handoff、已接受生命周期明确指定 handoff 点，或用户明确选择会话切换/blocked-state 交接时，才创建或更新交接文件。

## 什么时候使用

- 用户说“生成 handoff / 交接文档 / 下一 session 继续提示 / 帮我恢复上下文”。
- BLOCKED/IDLE、切换 session 或恢复场景中，用户明确选择保存交接。
- OpenSpec change、计划文件、测试文档或实现包需要给下一位 agent 接续。

普通任务不要自动创建 handoff 文件。上下文比例、压缩/DCP、阶段结束、命令完成、checkpoint 或后台 hook 都不是自动触发器；没有明确触发时只更新正常 progress/checkpoint（如适用），不要创建 handoff。

## 默认位置

- OpenSpec change：`openspec/changes/<change-id>/handoff.md`
- 已存在 current-task 目录：写入该任务目录下的 `handoff.md`
- 非 OpenSpec 且无明确目录：先问一次用户选择 repository-local 路径

不要默认写入 OS temp 目录、全局 docs/current、SQLite durable memory、或不相关目录。

🔴 CHECKPOINT / 🛑 STOP：写入或更新文件前，先确认三件事：目标路径已知、位于已确认 repository root 内且在任务范围内；内容不含 secrets/raw logs/full files/private data；明确触发已存在。任一条件不满足，只在回复中给脱敏草稿，不创建文件。

## Handoff 字段

```markdown
# Session Handoff: <task/change>

## Goal

## Active Change / Contract References

## Lifecycle / Backend

## Scope Boundary

## Completed / Pending / Blocked Packages

## Touched Files / Artifact References

## A33 Attachment / Owning-Repository Artifact Destinations

## Preserved Rollback Worktrees / Evidence References

## Evidence Anchors

## Subagent Activity

## Decisions Made

## Open Questions

## Risks / Unknowns

## Verification State

## Blocker / Stop Reason

## Next Action

## Forbidden Actions

## Suggested Next-Session Prompt
```

## 禁止内容

MUST NOT include:

- raw logs
- full grep dumps
- full file contents
- secrets, credentials, cookies, tokens, private keys
- irrelevant conversation history
- unredacted private data
- durable memory promotion by default

如果内容适合项目记忆，另走 `rose-memory` 的独立 scope/metadata/permission/security gate；创建 handoff 本身不得自动 promotion。

## Resume revalidation

恢复时先把 handoff 当作路径索引，而不是状态事实：

1. 重新确认用户选择的 canonical Git startup root、worktree、branch/HEAD、dirty/untracked 状态和当前 session 权限；handoff 中的路径只用于导航。
2. 重新读取 active OpenSpec proposal/specs/design/tasks、`interview.md`、已接受的 `test-plan.md`、`context.md`、`progress.txt` 和 bounded `drift-log.md`。
3. 按当前 diff/scope/risk 检查 review/test/security/verification evidence 的 freshness，重跑 stale、缺失或受影响的检查。
4. 对每个已声明 A33 attachment 分别验证 exact `repo_key`/`worktree_key` 与目标路径、当前 applicable `WT-001`、host/source/target root 与 Git/toplevel/private-dir/common-dir/HEAD/branch/membership、dirty 与 tracked/untracked/ignored/artifact/unknown file state、目标 rules，以及 owning-repository artifact destination。不同 repository 不要求 common-dir 相等，也不得复用另一 attachment 的证据。
5. 重新验证 handoff 引用的 preserved rollback worktree/evidence。Rollback 只保留状态；任何 ADD 或 non-force REMOVE 都需要针对当前 exact operation、keys、destination 和 operation class 的全新明确批准。此前批准、handoff、packet、memory 或 checkpoint 均不授权操作或扩大访问范围。
6. 对 handoff 与当前证据的冲突标记 `Open Question` / `Unverified` 并停止受影响动作；不得从 handoff 推断授权、完成或 lifecycle phase。

## Pinned upstream adaptation

Matt Pocock 的 pinned `handoff` 原文仅作为 inert reference data 保存在 `references/upstream/`。本 canonical skill 薄适配其 compact、引用已有 artifacts、不重复全文、脱敏和建议下一步 skills 的做法；AILI 规则优先：写入已确认的 repository-local 目标，不写 OS temp，触发、权限、artifact authority、resume revalidation 和 stop conditions 仍由当前 lifecycle contract 决定。不得加载该 reference 为第二个 skill，或从其 frontmatter 推断权限。

## Fallbacks

| 触发条件 | 一线处理 | 仍失败兜底 |
|---|---|---|
| 不知道 handoff 应写到哪里 | 问用户确认路径，列出 OpenSpec/current-task/不写文件三选项 | 不写文件，只返回 Markdown 草稿 |
| 输入包含 secrets、token、cookie、私钥或未脱敏隐私 | 停止摘录原文，改写为 `[REDACTED]` 和风险说明 | 拒绝写文件，要求用户提供脱敏材料 |
| 用户要求包含 raw logs、完整文件或大段聊天记录 | 摘要成证据锚点、错误签名、命令和结果 | 如果用户坚持保留原文，拒绝并说明 handoff 只存轻量摘要 |
| 任务状态不清或证据不足 | 标记 `Unverified` / `Open Question`，不要补造结论 | 请求用户补充来源或把 handoff 标为 blocked |

## 输出规则

写文件后报告：

- handoff path
- source artifacts reviewed
- unresolved Open Questions / Unverified items
- next action
