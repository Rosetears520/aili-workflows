# Portable task and result protocols

These files are the canonical semantic owner for the shared package envelope and the preserved `aili-agent-selection/v1` identity. They do not create a second lifecycle or result authority. Markdown packets, results, and selection references may render fields for a human or adapter but cannot redefine their authority.

- `package-envelope.schema.json` defines the ordinary/formal package task envelope: stable package identity, role, assignment, scope, forbidden scope, permission and acceptance boundaries, write scope, expected result/evidence, Worker result, verification evidence, and convergence linkage. A result keeps decision, authorization, execution, verification, and confidence separate; none grants a Worker final disposition authority.
- `aili-agent-selection.v1.schema.json` preserves the stable selection identity and uses the shared package base for specialist selection.

The former `aili-task-board/v1` schema is retired. `formal-task-board.md` is optional unparsed human-readable notes, not a machine protocol. `progress.txt` is concise free-form orchestrator continuity prose and has no schema or validation gate. Agent/job/turn/join/settlement state belongs to the runtime Journal.

Adapters may serialize the remaining schemas or map private runtime IDs, but runtime IDs cannot be sole completion evidence and adapter mappings cannot redefine the fields' authority. OpenCode dispatches each package through a fresh one-shot context. A persistent adapter may continue only when every base package field is unchanged; changed role, assignment, scope, forbidden scope, permission boundary, acceptance boundary, write scope, expected result, or expected evidence requires a new package. Empty, partial, failed, or blocked results never authorize automatic retry, nested dispatch, permission expansion, Worker integration, or a Worker final verdict.
