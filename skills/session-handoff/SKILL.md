---
name: session-handoff
description: 当用户明确要求交接、恢复提示或会话 handoff 时，生成当前任务的轻量 Markdown 交接文档；不自动写入 durable memory，不包含 secrets/raw logs/full files。
---

# Session Handoff

这个技能用于当前任务交接，不是长期 memory。只有用户明确要求 handoff，或后续已批准的命令合同明确要求写 handoff 时，才创建或更新交接文件。

## 什么时候使用

- 用户说“生成 handoff / 交接文档 / 下一 session 继续提示 / 帮我恢复上下文”。
- 长会话、压缩前、BLOCKED/IDLE、切换 session 时，且用户明确要求保存交接。
- OpenSpec change、计划文件、测试文档或实现包需要给下一位 agent 接续。

普通任务不要自动创建 handoff 文件。可以在最终回复里简短总结，但不要写文件，除非用户明确要求。

## 默认位置

- OpenSpec change：`openspec/changes/<change-id>/handoff.md`
- 已存在 current-task 目录：写入该任务目录下的 `handoff.md`
- 非 OpenSpec 且无明确目录：先问用户放哪里

不要默认写入 OS temp 目录、全局 docs/current、SQLite durable memory、或不相关目录。

🔴 CHECKPOINT / 🛑 STOP：写入或更新文件前，先确认三件事：目标路径已知且在任务范围内、内容不含 secrets/raw logs/full files、用户或上游合同明确允许写 handoff。任一条件不满足，只在回复中给草稿，不创建文件。

## Handoff 字段

```markdown
# Session Handoff: <task/change>

## Goal

## Active Contract

## Lifecycle / Backend

## Scope Boundary

## Touched Files / Artifacts

## Evidence Anchors

## Subagent Activity

## Decisions Made

## Open Questions

## Risks / Unknowns

## Verification State

## Blocker / Stop Reason

## Next Action

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

如果内容适合长期复用项目记忆，另走 `rose-memory`，并只写 evidence-backed durable finding 或 requirement memory。

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
