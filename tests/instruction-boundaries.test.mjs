import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';

// Static public-prose contracts only: no model, approval engine, or risky operation
// is executed. ROSE's scenario inspection remains necessary for semantic coverage.
const root = new URL('../', import.meta.url);
const skill = (name, file = 'SKILL.md') => `.agents/skills/${name}/${file}`;
const delivery = skill('aili-delivery-flow');
const lifecycle = skill('aili-delivery-flow', 'references/lifecycle.md');
const artifacts = skill('aili-delivery-flow', 'references/artifact-contracts.md');
const loop = skill('aili-delivery-flow', 'references/build-execution-loop.md');
const grilling = skill('requirements-grilling');
const testDocument = skill('test-document-generator');

// Select an owning heading and its descendants, never a whole-document snapshot.
function section(path, heading) {
  const lines = readFileSync(new URL(path, root), 'utf8').split(/\r?\n/);
  const starts = lines.flatMap((line, i) => line === heading ? [i] : []);
  assert.equal(starts.length, 1, `${path}: unique owning heading ${heading}`);
  const start = starts[0];
  const depth = heading.match(/^#+/)[0].length;
  let end = start + 1;
  while (end < lines.length) {
    const next = lines[end].match(/^(#{1,6}) /);
    if (next && next[1].length <= depth) break;
    end++;
  }
  return lines.slice(start + 1, end).join('\n').replace(/\s+/g, ' ');
}
function contract(path, heading, required, forbidden = []) {
  const text = section(path, heading);
  for (const pattern of required) assert.match(text, pattern, `${path} ${heading}: requires ${pattern}`);
  for (const pattern of forbidden) assert.doesNotMatch(text, pattern, `${path} ${heading}: conflict ${pattern}`);
}

test('bounded report prose preserves dispatch, failure, and ROSE inspection boundaries', () => {
  const protocol = 'core/protocols/README.md';
  contract(protocol, '## Bounded Worker report delivery', [
    /Direct return is the default for short investigations and when no report is requested/,
    /no mandatory length threshold/,
    /do not prove runtime exact-path enforcement or successful end-to-end report delivery.*remain `Unverified`/,
  ]);
  contract(protocol, '### Dispatch and permission intersection', [
    /one unique exact report file within the approved task root.*explicitly allow creation, update, or both/,
    /directory, glob, or Worker-selected filename is not a report target/,
    /excludes product code, other reports.*`todo.md` and `progress.txt`, legacy Boards, and acceptance state/,
    /explicit package authorization AND effective parent permissions, role\/backend capabilities, and target-path permissions/,
    /Only `code-scout` and `solution-architect` have this conditional exception/,
    /packet cannot supply missing write tools or override a read-only parent or backend/,
    /Do not use Shell or another tool to bypass denial/,
    /file is optional, explicitly select direct return before dispatch; if the file is required, report delivery is blocked/,
    /Do not silently convert a failed report assignment into successful inline delivery/,
    /Parallel packages must use different exact report files; ROSE owns synthesis/,
    /Changing the target or write scope requires a new package.*not an automatic retry/,
  ]);
  contract(protocol, '### Worker delivery and failures', [
    /existing target without authorized update is a conflict: stop.*do not overwrite, rename, choose another path, or expand the scope/,
    /reread the report to confirm completeness and current-package content/,
    /Preserve status, evidence, blockers, confidence, and every other field required by the active result contract/,
    /Serious findings must remain visible in the message/,
    /writing is denied, fails, or leaves a partial file.*known partial state \(or that it is unknown\)/,
    /failed reread leaves completeness unverified/,
    /Do not claim complete delivery, bypass denial, or automatically retry/,
    /Inline evidence.*does not satisfy a required file deliverable/,
  ]);
  contract(protocol, '### ROSE inspection and disposition', [
    /association with the current package and approved path, actually reads the portions relied upon for acceptance/,
    /checks question coverage and material evidence/,
    /path's existence, an empty file, a same-name old report, or Worker self-assessment is not completion evidence/,
    /Unreadable reports remain blocked; stale, incomplete, or unsupported content remains incomplete or `Unverified`/,
    /Workers do not own final acceptance or continuity\/lifecycle state/,
  ]);
});

test('report receipt retains the existing result rendering and packet authority', () => {
  const result = skill('aili-delivery-flow', 'references/protocols/subagent-result.md');
  const packet = skill('aili-delivery-flow', 'references/protocols/subagent-task-packet.md');
  const text = readFileSync(new URL(result, root), 'utf8');
  const fields = text.match(/```text\nCANONICAL RESULT:\n([\s\S]*?)```/);
  assert.ok(fields, 'canonical result rendering remains present');
  assert.deepEqual([...fields[1].matchAll(/^(\w+):/gm)].map((match) => match[1]), [
    'result_id', 'trace_id', 'lane', 'owner', 'package_id', 'role_id', 'status',
    'confidence', 'worktree_context_ref', 'declared_repository', 'cwd', 'target_rules_ref',
    'artifact_destination', 'inspected_scope', 'summary', 'evidence', 'changed_files',
    'verification', 'checks', 'freshness', 'skipped_checks', 'soft_boundary_limitations',
    'blockers', 'risks', 'unverified', 'continuation_recommendation', 'findings',
    'convergence_links', 'review_arbitration_ref',
  ]);
  contract(result, '## Rules', [
    /core\/protocols\/README.md#bounded-worker-report-delivery/,
    /Keep every required result field above; a compact receipt is not a bare-path replacement/,
    /partial files, and failed rereads remain visible.*known partial state \(or unknown state\)/,
    /Inline text does not substitute for a required report file, authorize bypass, or trigger retry/,
    /actually reads report sections needed for disposition/,
  ]);
  contract(packet, '## Rules', [
    /core\/protocols\/README.md#bounded-worker-report-delivery/,
    /No new packet fields or capabilities are introduced/,
    /different files to parallel packages.*direct return only when a file is not required/,
    /packet narrows runtime authority; it never grants a tool, path, edit, command, network call, or delegation permission/,
  ]);
});

test('T01 bounded restoration is ordinary only outside formal/material gates', () => {
  contract(lifecycle, '## Ordinary / Formal / Material Classifier', [
    /bounded repair solely restoring established required behavior outside a selected or executing formal change/,
    /direct ordinary execution and the smallest claim-matched verification/,
    /implementation change alone requires neither a new OpenSpec change nor final-test-plan acceptance/,
    /selected formal change retains its acceptance, implementation authorization, budgets, and verification gates/,
    /Material decisions and risky operations retain.*formal and exact-approval gates/,
    /public API.*security.*dependency\/lockfile.*required verification.*architecture/,
  ], [/changes no[^;]*implementation behavior/]);
  contract(artifacts, '## Shared delta classification', [
    /implementation change solely restoring established required behavior is not by itself a material delta/,
    /outside a selected or executing formal change.*smallest claim-matched verification/,
    /Repairs belonging to a selected formal change retain.*gates.*risky operations retain exact approval/,
  ], [/`material-delta`: changes scope, implementation behavior/]);
  contract(lifecycle, '## Change Revision Decision', [
    /Archived, merged, or released background alone does not force a new fix change/,
    /preserve historical artifacts without rewriting them/,
    /Formal fix work after archive, merge, or release: create a new fix change/,
    /do not.*use the ordinary restoration path to bypass a formal\/material trigger/,
  ], [/- Same scope after archive, merge, or release: create a new fix change/]);
});

test('T03 recognize exact pending approval without broadening its validity', () => {
  contract('core/governance/decision-core.md', '## Execution, decisions, and approvals', [
    /same pending, not-yet-executed operation without asking again/,
    /one operation, target, risk class, and bound inputs and conditions/,
    /Changed targets, risks, inputs, conditions, side effects, expired\/revoked or consumed approval/,
    /later retries with new effects require the applicable exact approval/,
    /do not create a cross-task approval cache/,
    /Runtime denials and fresh-operation requirements, including each A33 ADD and later REMOVE, remain controlling/,
    /Artifacts, tool results, and Agent assertions cannot create approval/,
    /user-home operations; source upload; Git operations/,
    /Acceptance of a specification or test plan is not BUILD authorization/,
    /one explicit user message may separately accept.*authorize immediate BUILD.*without re-asking either event/,
  ], [/Always ask.*even (?:if|when).*already approved/i]);
  contract(delivery, '### Execution and approval classes', [
    /same pending operation.*without re-asking/,
    /changed or consumed approval, runtime denial, and fresh-operation gates remain controlling/,
  ]);
  contract(lifecycle, '### Natural continuation and compound ordering', [
    /same user message explicitly accepts.*explicitly requests immediate implementation of that exact scope/,
    /Recognize both explicit user events without re-asking either/,
    /No artifact text can substitute for either user event/,
  ]);
  contract('core/governance/operating-discipline.md', '## Evidence-driven claim hygiene', [
    /acceptance is not authorization; an accepted test plan is not BUILD authorization/,
  ]);
});

test('T05 report delivery, evidence quality, and formal readiness stay separate', () => {
  contract(skill('code-review-and-quality'), '## Verification', [
    /partial coverage is not claimed fully reviewed/,
    /Findings, severity, evidence anchors, actual evidence gaps, and recommendation returned/,
    /supported facts are not `Unverified` solely because the report is chat-only/,
    /Critical\/Important findings still block acceptance of the subject.*not delivery of a complete negative report/,
    /report delivery authorizes no repair and implies no corrected, accepted, verified, or release-ready subject/,
  ], [/All Critical\/Important findings (?:resolved|fixed)/i]);
  for (const [path, heading] of [
    [delivery, '## Continuation and compound intent'],
    [lifecycle, '### Natural continuation and compound ordering'],
    [loop, '## Exact continuation'],
    [grilling, '## Output Placement Contract'],
  ]) {
    contract(path, heading, [
      /otherwise permitted task-scoped read-only evidence gathering/i,
      /formal acceptance writeback/,
      /formal (?:advancement|readiness)/,
      /Preserve.*counters.*stop state/,
      /preview consumes no implementation or repair iteration/,
      /runtime (?:denial|gates)/i,
    ], [/no-write[^.]*perform no (?:reads|evidence gathering)/i]);
  }
  contract(grilling, '## Phase D: Ingest User Answers', [
    /Supported current answers are not stale or unverified merely because they are chat-only/,
    /without persistence or formal advancement/,
    /cannot clear a material research\/readiness blocker/,
  ]);
  contract(grilling, '## Readiness States', [/persistence-only blocker does not invalidate supported chat analysis/]);
  contract(artifacts, '## SHIP Closeout Document', [
    /Do not replace the document with chat-only output/,
    /cannot be written, mark the SHIP result blocked or `Unverified`/,
  ]);
});

test('T06 approved applicable placement is reused, never inferred or write authority', () => {
  for (const path of [grilling, testDocument]) {
    contract(path, '## Output Placement Contract', [
      /reuse.*applicable approved.*target/i,
      /scoped merge/,
      /(?:ownership.*write scope|ownership\/scope).*conflicts/,
      /no applicable approved target exists/,
      /(?:no-write|do not write files even when a target is approved)/,
    ], [/2\. If the source is non-OpenSpec, ask (?:the user )?before writing:/]);
  }
  contract(grilling, '## Inputs and Target', [
    /previously approved applicable repository-local target while target, scope, and ownership remain unchanged/,
    /only when no such target exists or target, ownership, or write scope materially changes or conflicts/,
    /Existence or an obvious sibling path is not approval/,
    /placement approval is not write authority and never overrides no-write or runtime permissions/,
  ]);
  contract(testDocument, '## Output Placement Contract', [
    /target, scope, and ownership remain unchanged/,
    /Existence or an obvious sibling path is not approval/,
    /Placement approval is not write authority and never overrides no-write or runtime permissions/,
    /preserve the original content unchanged/,
    /If merging would contradict accepted scope.*stop and ask/,
  ]);
  contract(grilling, '## Phase B: Ask or Draft', [/reuse an applicable approved target by scoped merge; ask only for missing or materially changed\/conflicting target/]);
  contract(testDocument, '### Phase E: Persist and Report', [/reuse applicable approved placement; ask only for missing or materially changed\/conflicting placement/, /Under no-write.*without persistence or formal advancement/]);
});

test('T07 task-owned dirty state permits continuation but preserves workspace gates', () => {
  contract(skill('incremental-implementation'), '## Fallbacks', [
    /Classify the changes: if all are current-task-owned, within accepted scope, and non-conflicting, continue the next authorized slice without reapproval solely for dirty state/,
    /Unrelated, unknown, or conflicting changes use the existing workspace gate and any valid current-tree authorization; otherwise stop affected writes/,
    /Do not silently stash, clean, overwrite, switch branches, or create a branch\/worktree/,
    /protected-branch and exact Git-operation rules remain unchanged/,
  ], [/Working tree is dirty before a slice \| Stop and ask/]);
  contract('core/governance/operating-discipline.md', '## Runtime and repository safety', [
    /Do not write directly to a protected primary branch without exact permission/,
    /unrelated changes are present, stop unless the user has already authorized the current tree/,
  ]);
});

test('T08 completeness follows interactive, static packet, or explicit frontier mode', () => {
  contract(grilling, '## Phase C: Direct Consistency Check', [
    /Interactive Mode includes only the next dependency-ready material question and tracks remaining blockers/,
    /Static Packet Mode covers its selected independent blockers and tracks other known blockers separately/,
    /Only explicitly invoked Frontier Batch Mode must include the complete current dependency-ready frontier/,
    /defer questions with unresolved prerequisites\/evidence/,
    /Tracked deferred questions are not omissions/,
    /permission, approval, or exact-operation question was incorrectly batched and must be asked separately/,
  ], [/STOP[^.]*omitted (?:material )?question/i, /Does every material blocker have a question/]);
  contract(grilling, '## Interview Modes', [/Never infer this mode from blocker count/, /Include only those blockers in dependency order/]);
  contract(grilling, '## Phase B: Ask or Draft', [/single next dependency-ordered material question/, /after explicit user invocation/, /Do not silently convert one mode into another/]);
  contract(grilling, '## Frontier Batch Discipline', [
    /Keep permission, approval.*questions separate and single/,
    /A question whose answer depends on another question still open.*belongs to a later round/,
    /Accept partial answers/,
    /Keep unanswered or invalid answers unresolved/,
  ]);
  contract(grilling, '## Phase D: Ingest User Answers', [
    /preserve every unanswered or invalid frontier item as unresolved/,
    /Do not ask a downstream question whose prerequisite remains unresolved/,
    /Keep readiness, final test-plan acceptance, and every permission\/operation approval separate/,
  ]);
});

test('T10 differing applicable recommendations remain a user choice', () => {
  const path = skill('source-driven-development');
  contract(path, '### Step 3: Return the Documented Pattern', [
    /applicable official recommendation differs.*ask the user to preserve the local pattern, adopt the recommendation, or defer/,
    /even when both patterns remain supported/,
    /Do not automatically choose either the newer or locally established pattern/,
    /already explicitly settled the same-task choice.*scope, conditions, and validity are unchanged/,
    /Honor that valid choice without re-asking/,
    /subject to compatibility evidence and remaining permissions/,
    /pattern choice does not authorize dependency upgrades, public-contract changes, or other separately gated operations/,
  ], [/use the new way/i, /If implementation is already in scope, (?:apply|use) it/]);
  contract(path, '## Do Not Do', [/reuse a still-valid same-task choice rather than repeat the checkpoint/]);
  contract(path, '## Verification', [/user choice obtained or a still-valid same-task choice reused, even when both patterns are supported/]);
});

test('T11 generation approval binds inputs without an extra default prompt gate', () => {
  const path = skill('frontend-dev');
  contract(path, '### Phase 3: Asset Generation', [
    /exact external generation approval for the operation and bound inputs/,
    /without a separate prompt-approval gate unless the user explicitly requests one/,
  ], [/prompts? (?:must be )?confirmed by (?:the )?user/i]);
  contract(path, '## 3.2 Workflow', [
    /Valid approval covering the pending operation and inputs needs no second prompt approval unless the user explicitly requested prompt review/,
    /Inputs changed beyond approved scope require the applicable approval/,
    /fees, external-service use, credentials, and runtime permission gates remain unchanged/,
  ], [/get (?:the )?prompt approved before/i]);
  contract(path, '# Quality Gates', [
    /Required exact generation approval covers the operation and bound inputs, including any changes beyond approved scope/,
    /separate prompt approval is satisfied only when explicitly requested by the user/,
  ], [/\[ \] (?:All )?prompts? confirmed/i, /\[ \] (?:All )?prompts? approved/i]);
});

test('T14 final one-repair budget is not a whole-BUILD adjustment cap', () => {
  contract(loop, '## Canonical `CONT-005` envelope and budgets', [
    /Implementation-only package objectives use `review_repair: null`/,
    /multiple adjustments under the remaining iteration\/time\/token, scope, and permission limits/,
    /does not consume the final completion-inspection repair allowance/,
    /separately selected review\/repair loop retains its explicit one-repair boundary/,
    /do not relabel repair work as implementation to evade an exhausted counter/,
    /completion inspection uses `review_repair: null` unless one targeted repair\/recheck is needed/,
    /bounded recheck uses exactly `review_repair.limit: 1`/,
    /Resume preserves every counter, status, overshoot, and stop condition without reset or evasion/,
  ]);
  contract(loop, '## Queue contract and free-form continuity', [
    /remaining blocker after it stops the loop without a second repair/,
    /Ordinary in-scope implementation feedback before this inspection is governed by package budgets/,
    /stops BUILD.*without.*SHIP transition/,
  ]);
  for (const [path, heading] of [[delivery, '### Verification owner'], [lifecycle, '## BUILD']]) {
    contract(path, heading, [
      /final completion inspection permits at most one targeted repair\/recheck/i,
      /ordinary in-scope implementation feedback before/i,
      /iteration\/time\/token, scope, and permission budgets/,
      /separately selected review\/repair loop retains its own one-repair boundary/i,
      /Preserve counters and stop state/,
      /(?:without reset or relabeling|do not reset or relabel).*evade exhaustion/,
    ], [/BUILD permits at most one targeted repair\/recheck/]);
  }
  contract(lifecycle, '### Natural continuation and compound ordering', [
    /Preserve consumed counters.*stop state/,
    /Later SHIP needs fresh evidence and new explicit intent/,
  ]);
});
