---
name: repo-evidence-first
description: 在非平凡规划、编辑、审查或完成声明前，先用仓库证据锚点确认项目事实；无证据的项目判断必须标为 Hypothesis、Open Question、Unverified、委托调查或 blocked。
---

# Repo Evidence First

这个技能用于防止 ROSE 凭经验猜项目事实。凡是要声称“这个仓库通常怎样做”“某文件是权威”“某测试覆盖行为”“某任务已经完成”“某引用是 stale/current”等，都必须先拿到仓库证据。

## 什么时候使用

用于非平凡的：

- 规划、设计、任务拆分
- 编辑前的目标定位
- code review / test review / security review
- completion claim：complete、fixed、passing、verified、ready
- 需要判断 active/current/stale/archived/generated 的证据
- 需要项目约定、peer pattern、上下游、测试覆盖或验证路径

Direct allowlist 小改可以跳过完整 evidence pack，但必须说明为什么满足 direct 条件且 subagent 不会节省上下文。

## 工作流

1. 命名当前 contract：用户目标、scope、acceptance、stop conditions。
2. 查本地规则：`AGENTS.md`、`agents/rose.md`、active OpenSpec、skills、README/docs。
3. 建立 evidence pack，不要把 unsupported claim 写成 fact。
4. 遇到 broad/noisy search 时，派发最轻量 subagent。
5. 把冲突、stale、missing、generated、archived 证据显式标出。
6. 给出下一步：edit、delegate、ask_user、blocked、verify。

可选证据源：当非平凡代码任务需要文件/符号/调用方/被调用方/peer pattern/测试/影响面定位，且 CodeGraph 可用且有帮助时，ROSE 可把 CodeGraph 作为可选 locality provider 分配给合格 lane owner。CodeGraph 结果必须压缩成 evidence anchors；不可当作 proof；不可替代 edit/review/test/doc lane 的最终读文件、读 diff、读测试或读文档；不可用时回退到普通 search/read，只有 materially affects confidence 时标 `Unverified`。

🔴 CHECKPOINT: 在进入编辑、审查结论或 completion claim 前，必须能列出至少 1 个有效证据锚点，或把状态降级为 `PARTIAL` / `NOT_FOUND` / `CONFLICTING` / `BLOCKED`。没有 anchors，就不能说 “confirmed / verified / done / repository pattern”。

## Evidence pack 字段

```text
REPO EVIDENCE STATUS: GROUNDED | PARTIAL | NOT_FOUND | CONFLICTING | BLOCKED

Active contract:
- ...

Local rules inspected:
- path:line - rule

Project facts:
- path:line-or-symbol - fact - freshness - confidence

Existing patterns:
- path:line-or-symbol - pattern
- N/A if none found

Counter-evidence / stale evidence:
- path:line-or-symbol - stale/missing/archived/generated/conflicting signal
- N/A if none found

Verification path:
- command / inspection / test - why

Unknowns:
- Open Question / Unverified item

Next action:
- edit | delegate | ask_user | blocked | verify
```

## Claim classification

- `Grounded Fact`: supported by file paths with lines/symbols, command output summary, test result, spec/task/protocol section, explicit user instruction, or reconciled subagent evidence anchor.
- `Hypothesis`: plausible but not proven by current repo evidence.
- `Open Question`: needs user/product/architecture decision.
- `Unverified`: evidence may exist but was not inspected or command could not run.
- `Blocked`: evidence conflicts or scope/approval is missing.

Unsupported project facts must become `Hypothesis`, delegated evidence work, user questions, or blocked items.

## Routing

- Local code/config/tests/schemas/symbols/call chains: `code-scout`
- Local docs/workflow/OpenSpec/skills/rules: `doc-researcher`
- External official/current behavior: `web-researcher`
- Test coverage or verification strategy: `test-engineer`
- Secrets, auth, permissions, tool policy, install/hooks, trust model: `security-auditor`

Use the lightest specialist that can return compact anchors. Do not paste raw grep dumps or long logs into MainAgent context.

Runtime-valid delegation only:

| Need | If specialist is exposed and allowed | If not exposed/allowed |
|---|---|---|
| Broad local code evidence | Delegate to `code-scout` or equivalent read-only scout; optionally include CodeGraph locality evidence when available/useful | Search locally with available tools, or mark `Unverified` |
| Docs/OpenSpec/workflow evidence | Delegate to exposed docs scout | Read local docs yourself, or ask caller to dispatch |
| External/current behavior | Delegate/fetch only if web access is allowed | Mark external behavior `Unverified`; do not infer |
| Test/security review | Delegate only when caller/runtime permits | Provide escalation request; do not fabricate specialist verdict |

## 🛑 STOP / Blacklist

- Do not claim a repo fact without `path:line`, symbol, command output, explicit user instruction, or reconciled anchored subagent evidence.
- Do not name unavailable agents as if they ran; say “escalation needed” or `Unverified`.
- Do not convert stale docs, generated files, partial logs, or memory into current fact without freshness checks.
- Do not proceed from `CONFLICTING` evidence to edit/ship without resolving or reporting the conflict.

## 输出给用户

简短说明：

- 已确认的项目事实
- 证据锚点
- 冲突或 stale 证据
- 下一步动作
- 未验证项
