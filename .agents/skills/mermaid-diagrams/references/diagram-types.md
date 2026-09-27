# Choose by relationship

First state the question in ordinary language. Determine whether the source describes a branch, several paths meeting, a responsibility handoff, or an object's changing state. Then select the notation that makes that relationship explicit.

| Main question | Type | Preserve |
| --- | --- | --- |
| Which condition selects the next action? | Flowchart | Decision and branch results |
| Where do several routes meet? | Flowchart | Actual incoming edges and any evidenced waiting rule |
| Who sends what, in which order? | Sequence | Participants, message direction, conditions |
| Which states can this object enter? | State | States, triggering events, guards |
| How do records relate? | ER | Relationship meaning and supported cardinality |
| How do software types relate? | Class | Type identity and correct relationship kind |
| Which components communicate across which boundaries? | Architecture using flowchart | Responsibilities, boundaries, edge meaning |
| How are concepts grouped? | Mindmap | Parent-child hierarchy |
| What happened when? | Timeline | Sourced dates and event names |

A flowchart convergence alone does not assert that all inputs must finish. If synchronization matters, state the rule explicitly from evidence. A sequence arrow shows a message, not automatically a dependency or shared ownership. A state is a condition an object occupies; an action is work performed.

Choose the least elaborate view that answers the question. Do not route numerical comparisons or trends here solely because Mermaid can express some charts. Give that need to the quantitative visualization owner through the parent.

For complex material, use an overview for responsibilities and a detail view for a specific interaction or branch. Retain shared names and boundaries across views. Explain each example's type choice and indispensable labels; do not teach a shape without its meaning.
