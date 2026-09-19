# Portable task and result protocols

These files are the canonical semantic owner for the shared package envelope and the preserved `aili-agent-selection/v1` identity. They do not create a second lifecycle or result authority. Markdown packets, results, and selection references may render fields for a human or adapter but cannot redefine their authority.

- `package-envelope.schema.json` defines the ordinary/formal package task envelope: stable package identity, role, assignment, scope, forbidden scope, permission and acceptance boundaries, write scope, expected result/evidence, Worker result, verification evidence, and convergence linkage. A result keeps decision, authorization, execution, verification, and confidence separate; none grants a Worker final disposition authority.
- `aili-agent-selection.v1.schema.json` preserves the stable selection identity and uses the shared package base for specialist selection.

The former `aili-task-board/v1` schema is retired. Legacy `formal-task-board.md` files are unparsed human-readable historical notes, not a machine protocol. Ordinary and formal work must maintain `todo.md` current actions and concise free-form `progress.txt` history when triggered under `.agents/skills/aili-delivery-flow/references/formal-task-board.md`. This is main-model discipline with placement and read-only boundaries, not a schema or validation gate. Agent/job/turn/join/settlement state belongs to the runtime Journal.

Adapters may serialize the remaining schemas or map private runtime IDs, but runtime IDs cannot be sole completion evidence and adapter mappings cannot redefine the fields' authority. OpenCode dispatches each package through a fresh one-shot context. A persistent adapter may continue only when every base package field is unchanged; changed role, assignment, scope, forbidden scope, permission boundary, acceptance boundary, write scope, expected result, or expected evidence requires a new package. Empty, partial, failed, or blocked results never authorize automatic retry, nested dispatch, permission expansion, Worker integration, or a Worker final verdict.

## Bounded Worker report delivery

This is the single detailed contract for a designated report and compact receipt, not a new protocol, schema, public parameter, or lifecycle. Direct return is the default for short investigations and when no report is requested. Before dispatch, ROSE chooses report delivery for durable reference, multi-section evidence, or an explicit user request; there is no mandatory length threshold.

### Dispatch and permission intersection

Reuse the existing package fields:

- `assignment`, `expected_result`, and `expected_evidence` identify the questions, report content and evidence, whether a file is required, and the compact receipt.
- `scope` and `write_scope` identify one unique exact report file within the approved task root, and explicitly allow creation, update, or both. A directory, glob, or Worker-selected filename is not a report target. Update permission must bound the permitted changes to that file.
- `forbidden_scope` excludes product code, other reports, the main task's `todo.md` and `progress.txt`, legacy Boards, and acceptance state. Report delivery does not permit those edits or synthesis of other packages.
- `permission_boundary` requires explicit package authorization AND effective parent permissions, role/backend capabilities, and target-path permissions to permit the operation. `acceptance_boundary` reserves inspection, disposition, synthesis, continuity updates, and final acceptance to ROSE.

Only `code-scout` and `solution-architect` have this conditional exception to read-only research: the researched project remains read-only; only their own designated report may be written under the intersection above. Other roles gain no permission from this exception, and existing artifact-capable roles retain their existing boundaries. A packet cannot supply missing write tools or override a read-only parent or backend. Do not use Shell or another tool to bypass denial.

ROSE checks actual capability before dispatch. If bounded writing is unavailable and a file is optional, explicitly select direct return before dispatch; if the file is required, report delivery is blocked. Do not silently convert a failed report assignment into successful inline delivery. Parallel packages must use different exact report files; ROSE owns synthesis. Changing the target or write scope requires a new package under the existing identity rules, not an automatic retry.

### Worker delivery and failures

Keep the report tied to the current package and assignment, with conclusions, source/evidence anchors, actual checks, unverified items, and blockers. Before writing, check the target's current state. An existing target without authorized update is a conflict: stop and report it; do not overwrite, rename, choose another path, or expand the scope. Write only the authorized create/update content, then reread the report to confirm completeness and current-package content.

Return a compact receipt within the existing required result structure, not a bare path or a duplicate full report. Preserve status, evidence, blockers, confidence, and every other field required by the active result contract. Include a short conclusion, exact report path and useful section anchors, actual checks (including the reread), and remaining limitations. Serious findings must remain visible in the message, not only inside the file.

If writing is denied, fails, or leaves a partial file, stop and state the blocker and known partial state (or that it is unknown) in the receipt. A failed reread leaves completeness unverified. Do not claim complete delivery, bypass denial, or automatically retry. Inline evidence can assist ROSE but does not satisfy a required file deliverable.

### ROSE inspection and disposition

ROSE verifies the report's association with the current package and approved path, actually reads the portions relied upon for acceptance, and checks question coverage and material evidence. A path's existence, an empty file, a same-name old report, or Worker self-assessment is not completion evidence. Unreadable reports remain blocked; stale, incomplete, or unsupported content remains incomplete or `Unverified`. ROSE independently dispositions the evidence, requests a bounded revision only within an unchanged package and existing continuation rules, or returns the decision/blocker. Workers do not own final acceptance or continuity/lifecycle state.

### Compact example using existing fields

For an already approved root `tasks/parser-study/`, a report-capable backend, and a `code-scout` package `SCOUT-1`:

```text
assignment: Locate parser entry points and their focused tests; do not design or implement.
scope: Read src/parser/ and tests/parser/; report under tasks/parser-study/.
write_scope: Create only tasks/parser-study/scout-1.md; no update if it exists.
forbidden_scope: Product code, other reports, todo.md, progress.txt, legacy Boards, acceptance state.
permission_boundary: Report write only if parent, role/backend, and exact path permissions all allow it; no bypass.
acceptance_boundary: ROSE reads and dispositions evidence; Worker has no final acceptance authority.
expected_result: Required report plus compact receipt in the existing result structure.
expected_evidence: Current-package locality map, source anchors, actual checks, unverified items and blockers; receipt includes exact path and reread result.
```

For short discovery, use `write_scope: none` and request direct evidence instead. These contracts and their generated projections do not prove runtime exact-path enforcement or successful end-to-end report delivery in Pi or an external CLI; those behaviors remain `Unverified` until separately evidenced.
