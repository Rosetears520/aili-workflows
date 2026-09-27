# Flowchart

Use for actions, branches, and paths meeting. Keep actions and decisions distinct, and label each decision exit. A meeting of arrows alone does not imply synchronization.

Fictional example: an application proceeds to review only when its required fields are present. A flowchart fits because the main question is which action follows the check. “完整” and “缺失” are indispensable branch results; removing them would hide the rule.

```mermaid
flowchart TD
    receive["接收申请"] --> check{"必填内容完整？"}
    check -->|完整| review["审核申请"]
    check -->|缺失| request["请求补充"]
    request --> receive
```

Summary: complete applications enter review; incomplete ones return for more information.

For a more complex fictional process, split by question:

**Overview — which stage follows review?**

```mermaid
flowchart TD
    receive["接收申请"] --> review["审核申请"]
    review --> notify["通知申请人"]
```

**Detail — what are the review outcomes?**

```mermaid
flowchart TD
    review["审核申请"] --> eligible{"满足条件？"}
    eligible -->|满足| approve["记录批准结果"]
    eligible -->|不满足| reject["记录拒绝原因"]
    approve --> notify["通知申请人"]
    reject --> notify
```

The overview intentionally abstracts the internal review decision; the detail retains both real outcomes and the same stage names. “满足” and “不满足” explain the branching rule, and the shared notification action explains convergence. No invented routing node is needed.

Use quoted labels and uncomplicated identifiers. Choose direction for the reading context; verify subgraph direction behavior when external links are present.

Official syntax: https://mermaid.js.org/syntax/flowchart.html
