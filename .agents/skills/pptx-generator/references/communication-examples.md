# Communication Examples

These original, fictional examples illustrate the decisions in [content-planning.md](content-planning.md), not project evidence, mandatory layouts, or rendered results. Keep the existing plan and build workflow; examples add no output fields.

## A Scoped Result, Not a Slogan

Source: “本次试点覆盖两个部门。平均处理时间从 10 分钟降至 8 分钟，其他部门尚未测试。”

Poor title: “全面赋能组织效能，实现革命性提升。” It replaces a limited observation with an unsupported organization-wide claim.

A source-bounded plan entry:

```markdown
## Slide 01: 两个试点部门的平均处理时间由 10 分钟降至 8 分钟
<!-- slide-id: pilot-processing-time -->

### 1. Layout
左右对照试点前后两个读数；紧邻读数注明试点范围与未测试范围，不画因果流程。

### 2. Content
试点前平均处理时间：10 分钟
试点后平均处理时间：8 分钟
范围：两个部门；其他部门尚未测试。
[Source: 用户提供的试点摘要]
```

The title states the observed result; the body provides readable evidence and scope rather than another slogan. No percentage, causal explanation, or action recommendation is needed.

## Same Mechanism, Different Reading Conditions

Source: “系统将最近一次查询结果保存在本地。网络不可用时，可以显示该结果，但它可能不是最新状态。”

For a live talk to non-technical managers, a compact body might be:

> 本地保存最近一次查询结果。断网时仍可显示，但可能不是最新状态。

For standalone reading, keep the referent explicit:

> 系统把最近一次查询结果保存在本地。网络不可用时，仍可以显示这份已保存的结果；它可能不是最新状态，不能直接当作当前信息。

Both preserve what is saved, where, when it can be shown, and the freshness limit. Moving “可能不是最新状态” to an undelivered speaker script would make either version misleading. The reading version need not be shorter or radically different.

## Explain Directly Before Using an Analogy

For the same mechanism, the direct wording above is sufficient for many non-experts. For engineers, “本地缓存最近一次查询结果，断网时可显示，但缓存可能非最新” retains the technical term without inventing a TTL or consistency guarantee.

If an analogy is specifically useful or requested:

> 像把最近查到的班车时刻表抄在随身本上：断网时还能查看，但班次调整后，本上的内容可能已经过时。

Mapping: the copied timetable represents the last query result; the notebook represents local storage; consulting it offline represents displaying the stored result. Limit: this comparison says nothing about how the system refreshes or detects stale data. It illustrates availability and staleness, not proof of the implementation. A fairy tale that promises “永远知道最新班次” loses the essential constraint.

## Three Items Do Not Necessarily Make a Process

| Source relationship | Suitable organization | Misleading alternative |
|---|---|---|
| 登录提示不清楚；检索缺少筛选入口；导出列名不一致 — independent issues | Three labeled rows or another parallel arrangement | Arrows implying that login causes search and export problems |
| 提交申请 → 审核申请 → 归档记录 — prescribed order | Ordered steps with arrows | A dated timeline when no dates or durations were supplied |
| A 离线可用但不能协作；B 可协作但依赖联网 | A/B table with shared rows for offline use and collaboration | Unmatched feature cards that hide the trade-off or imply a chosen winner |

Cards are not inherently wrong. Reusing a layout for genuinely parallel information can aid understanding; making all three relationships look identical erases meaning.

## Capacity Is a Constraint, Not a Font Trick

Suppose a fixed one-page template allows only six independent body records, in either one column of six or two columns of three. Eight records are mandatory; each record's object, deadline, and exclusion must remain. The font, slots, spacing, and one-record-per-line rule are fixed.

Removing empty transitions cannot turn eight independent records into six. Neither native layout adds capacity. A useful response is:

> 八条必需记录超过两种布局各六条的容量，仍差两条。压缩措辞不能减少独立记录数。需要确认是否允许增页或调整模板容量；当前约束下不能完成排入。

Shrinking the font, merging records, placing body text in the title, or hiding two exclusions is not a valid solution. This is logical capacity reasoning only, not a measurement of an actual rendered template.
