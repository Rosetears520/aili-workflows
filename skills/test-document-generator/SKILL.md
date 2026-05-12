---
name: test-document-generator
description: Generate a repository-local, evidence-grounded Markdown test document from specs, proposals, plans, issues, or user descriptions; ask only for missing product decisions, map requirements to test cases, and persist the test plan before summarizing.
---

# Test Document Generator

## Purpose

Use this skill to generate a durable Markdown test document, test matrix, acceptance checklist, regression scope, or QA plan from existing product/change material.

This skill writes testing documentation. It does not replace `test-driven-development`, which writes or runs automated tests.

In the AILI lifecycle, `aili-delivery-flow` owns when DEFINE must produce or confirm a test document before BUILD. This skill owns only the test-document artifact generation rules.

## When to Use

Use this skill when the user asks for:

- test document
- test plan
- QA plan
- acceptance test matrix
- regression checklist
- test cases derived from a spec, plan, issue, PR, or feature description

## Inputs

Possible sources:

- `openspec/changes/<change-id>/`
- `proposal.md`, `design.md`, `tasks.md`, `acceptance.md`
- issue, ticket, or PR description
- user-pasted spec, solution, or feature description
- existing code, tests, docs, README, or CI commands when needed for evidence grounding

Do not ask questions that can be answered from repository code, docs, specs, tests, configs, or official sources.

## Output Placement Contract

When generating a test document, OpenSpec change output is the only deterministic no-question placement. For every non-OpenSpec source, including a single source document with an obvious sibling path, ask where to place the output before writing. Generate the draft, run the stress-test pass, repair the document, persist the final document, then summarize the path in chat.

Target path resolution:

1. If the source is an OpenSpec change directory, write `openspec/changes/<change-id>/test-plan.md` without asking.
2. If the source is non-OpenSpec, ask where to place the output before writing, even when the source is a single document:
   - A. create a sibling Markdown file beside the main source file;
   - B. create a sibling folder beside the source directory;
   - C. append a new section to the existing spec/design document;
   - D. print the result in chat only.
3. If the user pasted only free-form text and no source path exists, ask whether to:
   - A. create a new file in a user-specified location;
   - B. append to an existing spec/document;
   - C. print in chat only.
4. If the target already exists, update it by merging or appending a new revision section instead of blindly overwriting.
5. If the user explicitly says "print in chat", "do not create files", or "chat only", do not write files.

Use this concise placement question for non-OpenSpec sources:

```text
这个非 OpenSpec 输出需要先确认落点，你选一个：
A. 生成在源文件同级：<path>
B. 在源目录同级新建文件夹：<path>
C. 追加到现有 spec / design 文档末尾
D. 只打印在对话框，不写文件
```

Chat response after persistence should include only:

- generated file path
- source files reviewed
- coverage summary
- unresolved `Open Questions` / `Unverified` count
- suggested next action

## Workflow

### Phase A: Source Grounding

1. Read the user-provided spec, plan, proposal, issue, PR description, or pasted description.
2. If the source is an OpenSpec change, read `proposal.md`, `design.md`, `tasks.md`, and `specs/` when present.
3. When needed, inspect related code, existing tests, README, package scripts, CI docs, or API contracts to ground testability.
4. Build an evidence table that separates observed facts, inferences, assumptions, open questions, and unverified claims.
5. Do not ask the user for information that reliable source grounding can answer.

### Phase B: Clarification

Ask the user only when a missing decision materially affects the test document, such as:

- test scope or release boundary
- success criteria or acceptance threshold
- risk level and priority
- permission model or role matrix
- data lifecycle, retention, migration, or cleanup rules
- supported platforms, browsers, versions, or integrations

Small gaps can be recorded as `Open Question` without blocking document generation. For critical gaps, include a `需要你确认的问题` table in the document.

### Phase C: Generate Test Document

Generate a complete Markdown draft using the template below or `references/test-document-template.md`. Every test point must map back to a requirement, risk, decision, or evidence source. Keep facts, inferences, assumptions, and unverified items separate.

The document is both a plan and the durable execution ledger. Include sections for automation commands, manual checks, run history, defect/fix/retest closure, and change history even when they start empty.

### Phase D: Stress-Test

Use `strategy-stress-test` to check whether the document misses failure paths, permission boundaries, data problems, regression scope, acceptance standards, or executable test cases.

Repair the document after stress-testing and before persistence.

### Phase E: Persist and Report

1. Resolve the target path using the Output Placement Contract.
2. Write or update the target Markdown file.
3. Inspect the written file and diff for accidental unrelated changes.
4. Return only the concise chat summary defined by the Output Placement Contract.

## Test Document Template

```markdown
# 测试文档：<feature/change-name>

## 0. 文档元信息
- 来源：
- 生成时间：
- 适用版本 / 分支：
- 测试负责人：
- 状态：draft / reviewed / accepted

## 1. 资料来源与证据
| 来源 | 已检查内容 | 观察到的事实 | 置信度 | 备注 |
|---|---|---|---|---|

## 2. 被测对象与测试目标
- 被测对象：
- 用户目标：
- 业务目标：
- 技术目标：
- 不测试内容：

## 3. 测试范围
### In Scope
### Out of Scope
### Assumptions
### Open Questions

## 4. 需求-测试追踪矩阵
| 需求 / 决策 / 风险 | 来源 | 测试点 | 测试类型 | 优先级 | 覆盖状态 |
|---|---|---|---|---|---|

## 5. 测试策略
- 单元测试：
- 集成测试：
- E2E / 浏览器测试：
- API / 契约测试：
- 手工验收：
- 回归测试：
- 非功能测试：

## 6. 测试环境与测试数据
- 环境：
- 依赖服务：
- 测试账号 / 权限：
- 测试数据：
- 数据清理方式：

## 7. 功能测试用例
| ID | 场景 | 前置条件 | 步骤 | 预期结果 | 优先级 | 自动化建议 | 来源 |
|---|---|---|---|---|---|---|---|

## 8. 异常、边界与权限测试
| ID | 类型 | 场景 | 输入 / 操作 | 预期结果 | 风险 |
|---|---|---|---|---|---|

## 9. 数据一致性 / 迁移 / 兼容性测试
## 10. 性能、稳定性、安全、可观测性测试
## 11. 回归范围

## 12. 自动化验证命令

| 层级 | 命令 | 目的 | 必须执行 | 备注 |
|---|---|---|---|---|
| Unit |  |  | yes/no |  |
| Integration |  |  | yes/no |  |
| CLI |  |  | yes/no |  |
| API / Contract |  |  | yes/no |  |
| GUI / Browser |  |  | yes/no |  |
| Regression |  |  | yes/no |  |

## 13. 手工验收清单

- [ ]

## 14. Open Questions / Unverified

| 类型 | 内容 | 影响 | 处理方式 |
|---|---|---|---|

## 15. 测试执行记录

| Run ID | 时间 | 执行者 | 测试层级 | 命令 / 工具 | 结果 | 关键证据 | 未验证项 |
|---|---|---|---|---|---|---|---|

## 16. 缺陷与修复闭环

| Bug ID | 来源测试 | 现象 | 根因 | 修复负责人 | 修复文件 | 复测命令 | 复测结果 | 状态 |
|---|---|---|---|---|---|---|---|---|

## 17. 变更记录
```

## Validation

Before finishing:

- Confirm `name` matches the skill directory name.
- Confirm the document is source-grounded and unresolved items are labeled `Open Question` or `Unverified`.
- Confirm the output location follows the placement contract.
- Confirm the automation-command, execution-record, and defect-closure sections exist.
- Confirm the chat response contains only the generated path, coverage summary, unresolved count, and next action.
