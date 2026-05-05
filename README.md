# aili-workflows

`aili-workflows` 是 [Rosetears](https://rosetears.cn/) 的个人 OpenCode 工作流仓库，用来沉淀常用的 agent、skill、执行规范和辅助脚本。

这个仓库不是上游项目的官方发布版，而是面向个人 OpenCode 使用习惯整理的工作流集合。仓库内包含原创编排内容，也包含来自开源项目的 agent/skill 内容。第三方内容的来源和许可在下方单独标明。

## 项目结构

```text
aili-workflows/
├── .gitignore
├── agents/
│   ├── rose.md                  # Rosetears 的 OpenCode primary agent
│   ├── implementer.md           # 单任务实现 subagent
│   ├── code-reviewer.md         # 代码审查 subagent
│   ├── security-auditor.md      # 安全审计 subagent
│   └── test-engineer.md         # 测试与覆盖率 subagent
├── scripts/
│   └── memory_cli.py            # 项目本地记忆状态管理脚本
├── skills/
│   ├── android-native-dev/
│   ├── api-and-interface-design/
│   ├── browser-testing-with-devtools/
│   ├── ci-cd-and-automation/
│   ├── code-review-and-quality/
│   ├── code-simplification/
│   ├── context-engineering/
│   ├── debugging-and-error-recovery/
│   ├── deprecation-and-migration/
│   ├── documentation-and-adrs/
│   ├── flutter-dev/
│   ├── frontend-dev/
│   ├── frontend-ui-engineering/
│   ├── fullstack-dev/
│   ├── git-workflow-and-versioning/
│   ├── idea-refine/
│   ├── incremental-implementation/
│   ├── ios-application-dev/
│   ├── minimax-docx/
│   ├── minimax-pdf/
│   ├── minimax-xlsx/
│   ├── performance-optimization/
│   ├── planning-and-task-breakdown/
│   ├── pptx-generator/
│   ├── react-native-dev/
│   ├── security-and-hardening/
│   ├── shader-dev/
│   ├── shipping-and-launch/
│   ├── source-driven-development/
│   ├── spec-driven-development/
│   ├── test-driven-development/
│   └── using-agent-skills/
├── tests/
└── README.md
```

## Agent 来源

| Agent | 用途 | 来源与说明 |
|---|---|---|
| `agents/rose.md` | OpenCode primary agent，负责个人主工作流、任务契约、记忆门禁、执行边界和子代理编排 | Rosetears 个人工作流内容 |
| `agents/implementer.md` | 执行一个明确边界的代码实现任务 | Rosetears 个人工作流内容 |
| `agents/code-reviewer.md` | 从 correctness、readability、architecture、security、performance 维度做代码审查 | 改编自 [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) 的 `agents/code-reviewer.md`，遵循 MIT License |
| `agents/security-auditor.md` | 做安全审计、威胁建模和漏洞检查 | 改编自 [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) 的 `agents/security-auditor.md`，遵循 MIT License |
| `agents/test-engineer.md` | 做测试策略、测试补充和覆盖率分析 | 改编自 [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) 的 `agents/test-engineer.md`，遵循 MIT License |

本仓库已移除这些 agent 文本中对 slash command 的直接引用，保留为 OpenCode 主代理自然语言触发和 MainAgent 编排使用。

## Skill 来源

### 来自 addyosmani/agent-skills

以下 skills 来自 [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills)，原项目许可为 MIT License，版权归 Addy Osmani 所有。本仓库用于个人 OpenCode 工作流整理，并保留来源说明。

| Skill | 说明 |
|---|---|
| `api-and-interface-design` | API、模块边界和接口设计 |
| `browser-testing-with-devtools` | 浏览器运行时验证和调试 |
| `ci-cd-and-automation` | CI/CD 与自动化质量门禁 |
| `code-review-and-quality` | 多维度代码审查流程 |
| `code-simplification` | 保持行为不变的代码简化 |
| `context-engineering` | agent 上下文组织和规则文件管理 |
| `debugging-and-error-recovery` | 根因调试和错误恢复 |
| `deprecation-and-migration` | 废弃、迁移和旧系统下线 |
| `documentation-and-adrs` | 文档和 ADR 记录 |
| `frontend-ui-engineering` | 生产级 UI 工程实践 |
| `git-workflow-and-versioning` | Git 工作流和版本管理 |
| `idea-refine` | 想法发散、收敛和澄清 |
| `incremental-implementation` | 小步增量实现 |
| `performance-optimization` | 性能测量和优化 |
| `planning-and-task-breakdown` | 任务拆解和执行计划 |
| `security-and-hardening` | 安全加固和 OWASP 基线 |
| `shipping-and-launch` | 发布前检查、监控和回滚 |
| `source-driven-development` | 基于官方文档的实现决策 |
| `spec-driven-development` | 规格先行开发 |
| `test-driven-development` | 测试驱动开发 |
| `using-agent-skills` | skill 选择和调用的元说明 |

### 来自 MiniMax-AI/skills

以下 skills 来自 [MiniMax-AI/skills](https://github.com/MiniMax-AI/skills)，原项目许可为 MIT License，版权归 MiniMax 所有。本仓库纳入的是适合个人 OpenCode 工作流的开发、文档、移动端、视觉和文件处理类 skills。

| Skill | 说明 |
|---|---|
| `android-native-dev` | Android Native、Kotlin、Compose 和 Material Design 3 |
| `flutter-dev` | Flutter、Riverpod/Bloc、GoRouter 和跨平台开发 |
| `frontend-dev` | 高级前端、视觉设计、动画和媒体增强页面 |
| `fullstack-dev` | 全栈后端架构、REST API、认证和前后端集成 |
| `ios-application-dev` | iOS、UIKit、SnapKit、SwiftUI 和 Apple HIG |
| `minimax-docx` | DOCX 创建、编辑、填充和模板格式化 |
| `minimax-pdf` | PDF 生成、表单填写和视觉重排 |
| `minimax-xlsx` | Excel、CSV、公式、财务表格和格式保真编辑 |
| `pptx-generator` | PowerPoint 生成、编辑和读取 |
| `react-native-dev` | React Native、Expo、导航、状态、测试和发布 |
| `shader-dev` | GLSL、ShaderToy、SDF、粒子和视觉特效 |

未纳入 `vision-analysis`、`gif-sticker-maker`、`minimax-multimodal-toolkit`、`minimax-music-gen`、`minimax-music-playlist`、`buddy-sings`，因为它们更偏 MiniMax API key 驱动的视觉、多模态或音乐娱乐工作流，不属于当前默认个人 OpenCode 工作流范围。

## 使用说明

这个仓库面向 OpenCode 使用，核心约定是通过自然语言任务触发 agent 和 skill，而不是依赖 slash command 文件。

典型使用方式：

```text
1. 将本仓库作为个人 OpenCode 工作流配置来源。
2. 让 OpenCode 发现 `agents/` 中的自定义 agent。
3. 让 OpenCode 发现 `skills/` 中的 SKILL.md 工作流。
4. 由 `rose.md` 作为 primary agent，按任务需要调用对应 skills 和 subagents。
```

`frontend-dev` 可用于纯前端设计、实现和动画工作；只有主动使用其中的媒体生成能力时才可能需要额外 MiniMax API key、CLI 或运行时依赖。使用前请阅读对应 skill 目录内的 `SKILL.md`、`README.md`、`scripts/` 或 `references/`。

## 许可与第三方声明

本仓库整体以 MIT License 发布，详见 [`LICENSE`](LICENSE)。其中 Rosetears 个人编排内容和第三方开源内容应分开理解，第三方内容保留原始版权声明。

第三方内容来源：

| 来源 | 仓库 | 许可 | 版权声明 |
|---|---|---|---|
| Addy Osmani | [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) | MIT License | Copyright (c) 2025 Addy Osmani |
| MiniMax | [MiniMax-AI/skills](https://github.com/MiniMax-AI/skills) | MIT License | Copyright (c) 2026 MiniMax |

根目录 [`LICENSE`](LICENSE) 已包含 Rosetears 原创内容和第三方 MIT 内容的版权声明。第三方 MIT License 许可文本如下，用于随本仓库中再分发的对应第三方内容一并保留：

```text
MIT License

Copyright (c) 2025 Addy Osmani
Copyright (c) 2026 MiniMax

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

如果继续从上游同步 agent 或 skill，请同步更新本 README 的来源表和许可说明。
