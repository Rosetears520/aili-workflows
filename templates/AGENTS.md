<!-- AILI_AGENTS_TEMPLATE_VERSION: 1 -->
<!-- AILI_AGENTS_TEMPLATE_SOURCE: templates/AGENTS.md -->
<!-- AILI_AGENTS_TEMPLATE_MODE: generated-project-local-file -->

# AGENTS.md

This file is the project-level instruction contract for AI coding agents working in this repository.

It is self-contained and project-local. Do not assume access to private global prompts, personal workflow repositories, external agent files, or out-of-band memory unless the user explicitly provides them in the current environment.

## Project Overview

<!-- Fill this section during initialization. Use facts from repository files only. Do not invent missing details. -->

- Project purpose: TODO
- Primary language/runtime: TODO
- Package manager: TODO
- Main application entry points: TODO
- Main test framework: TODO
- Important directories: TODO
- Generated/build output directories: TODO
- Deployment/runtime environment: TODO

## Setup Commands

<!-- Fill with verified commands from package manifests, README, docs, Makefile, CI, or equivalent project files. Use "unknown" only when the repository does not provide enough evidence. -->

- Install dependencies: TODO
- Start development server: TODO
- Build: TODO
- Lint: TODO
- Typecheck: TODO
- Test all: TODO
- Test focused: TODO
- Format: TODO
- Clean: TODO

## Architecture and Project Structure

<!-- Summarize only facts discovered from repository files. Do not invent architecture. -->

- `src/`: TODO
- `tests/`: TODO
- `docs/`: TODO
- `scripts/`: TODO
- Configuration files: TODO
- CI/CD files: TODO
- Generated files: TODO
- External integrations: TODO

<!-- AILI_MANAGED_BLOCK_BEGIN: agent-operating-discipline -->
## Agent Operating Discipline

These rules exist to reduce common LLM coding mistakes: wrong assumptions, hidden confusion, over-engineering, unrelated edits, and unverifiable completion.

If this repository installs AILI delivery commands, treat `/ideate`, `/define`, `/build`, and `/ship` as thin lifecycle entrypoints governed by `skills/aili-delivery-flow`; localize harness/process problems with `skills/harness-issue-triage`, then route approved harness changes through `skills/harness-evolution` rather than duplicating lifecycle rules here.

Tradeoff: these rules bias toward caution over speed. For trivial one-line tasks, use judgment and avoid ceremony. For non-trivial coding, debugging, refactoring, migration, review, documentation, or configuration work, follow them as hard execution rules.

### 1. Think Before Coding

Do not assume. Do not hide confusion. Surface tradeoffs before editing.

Before implementation:

- Inspect the relevant files before changing them.
- State assumptions that affect the implementation.
- If multiple interpretations exist, present them instead of choosing silently.
- If the user request conflicts with existing code, tests, docs, or project conventions, stop and name the conflict.
- If a simpler approach exists, say so and prefer it unless the user explicitly chooses the larger approach.
- If something is unclear enough that the wrong choice could cause broad rework, public API changes, schema changes, data loss, security risk, deployment risk, or destructive behavior, ask before editing.
- For low-risk ambiguity, state the assumption and proceed with the smallest reversible change.

Do not turn uncertainty into code. Clarify first, or state the assumption explicitly.

### 2. Simplicity First

Write the minimum code that solves the requested problem. Nothing speculative.

Do not add:

- features beyond what was requested
- abstractions for single-use code
- configuration options that were not requested
- new dependencies that are not required
- generalized frameworks for local problems
- broad error handling for impossible or out-of-scope scenarios
- future-proofing that is not needed for the current task

Prefer local, readable, boring solutions.

If the implementation becomes much larger than the problem, simplify before finalizing. A senior engineer should be able to look at the diff and say: this is the smallest reasonable change.

### No Evidence, No Edit

For non-trivial coding, debugging, refactoring, migration, documentation, configuration, test, security, or review work, do not act from memory or file names alone.

Before editing or approving a change, establish:

- exact files and symbols involved
- related tests or verification path
- existing pattern to follow
- types, schemas, config, docs, or specs that constrain the change
- known unknowns and assumptions

Use a read-only search agent when broad repository search would pollute the main context.

The search agent may locate evidence, but the editing, reviewing, testing, or security agent must still read the final target files before acting.

Before adding a local special-case, one-off branch, duplicated mapping, or hand-written generated output, inspect whether the behavior is controlled by an existing shared config, registry, manifest, template, schema, generator, or documented source of truth. If such a source exists, change that source and run the documented generation/check command; do not patch generated outputs or bypass the shared path unless the user explicitly approves the exception.

### 3. Surgical Changes

Touch only what the task requires. Clean up only your own mess.

When editing existing code:

- Do not improve adjacent code, comments, formatting, or names just because you noticed them.
- Do not refactor unrelated code.
- Do not rewrite working code into a preferred style.
- Do not delete pre-existing dead code unless explicitly asked.
- Match existing style, naming, structure, and patterns even if another style would be preferable.
- Keep the diff small and reviewable.

When your own change creates unused code:

- Remove imports, variables, functions, files, or comments made unused by your change.
- Do not remove unrelated pre-existing unused code.

The traceability test: every changed line must trace directly to the user request, the accepted task contract, the root-cause chain, or required verification. If a line cannot pass that test, remove it.

### 4. Goal-Driven Execution

Define success criteria. Loop until verified.

Before implementation, translate the task into verifiable goals.

Examples:

- "Add validation" means: define invalid inputs, test or verify those invalid inputs, then make validation pass.
- "Fix the bug" means: identify or reproduce the failure, fix the root cause, then verify the failure no longer occurs.
- "Refactor X" means: preserve behavior, verify before and after when practical, and keep the public contract stable unless explicitly changed.
- "Update docs" means: verify the documented command, path, API, or behavior matches the repository.

For multi-step tasks, use a brief plan with verification attached to each step:

```text
1. Inspect current behavior -> verify: relevant files/tests/docs identified.
2. Implement smallest change -> verify: diff only touches required scope.
3. Run focused check -> verify: targeted test/build/typecheck/manual evidence.
```

Do not claim completion without evidence.

Acceptable evidence includes:

- focused tests
- related test suite
- typecheck
- lint
- build
- reproduction logs
- manual verification with exact command/output
- static inspection when no executable check exists

If verification cannot be run, explain why and provide the strongest substitute evidence.

### 5. Stop Conditions

Stop and ask before proceeding when the task requires or appears to require:

- deleting, renaming, or moving files
- changing public APIs
- changing database schemas or migrations
- changing authentication, authorization, permissions, secrets, or security-sensitive behavior
- adding or removing production dependencies
- changing lockfiles without a dependency-related task
- running destructive commands
- rewriting Git history
- applying repo-wide formatting
- broad refactors across unrelated modules
- making product, architecture, or deployment decisions not specified by the user

When stopped, report:

- what is ambiguous or risky
- the concrete options
- the recommended option
- the tradeoff of each option

### 6. Completion Standard

A task is complete only when all are true:

- the implementation matches the user request
- the diff is surgical
- no speculative behavior was added
- every changed line passes the traceability test
- relevant verification was run or explicitly explained as unavailable
- remaining risks, skipped checks, and follow-up items are reported

These rules are working when diffs are smaller, clarifying questions happen before implementation, unnecessary rewrites decrease, and verification evidence replaces confidence.
<!-- AILI_MANAGED_BLOCK_END: agent-operating-discipline -->

## Project-Specific Rules

<!-- Add rules that are specific to this repository. Do not add personal preferences, temporary task notes, or generic advice. -->

- TODO

## Coding Conventions

Follow existing project conventions before introducing new ones.

- Match existing file organization, naming, formatting, imports, and error-handling style.
- Prefer existing utilities and patterns over new helpers.
- Do not introduce a new library when the existing stack already solves the problem.
- Do not change public behavior unless the task explicitly asks for it.
- Keep compatibility with the project's declared runtime, framework, and language version.

## Testing and Verification

Before the final response, run the smallest relevant verification available.

Preferred order:

1. Focused test for the changed behavior.
2. Related package/module test.
3. Typecheck when types may be affected.
4. Lint when style or static rules may be affected.
5. Build when integration, packaging, or runtime behavior may be affected.
6. Manual verification only when automated verification is unavailable.

When adding or fixing behavior:

- Prefer a failing test or clear reproduction before the fix when practical.
- Verify the fixed behavior after the change.
- Do not broaden tests just to increase coverage unless requested.
- Do not rewrite unrelated tests.

When verification cannot be run:

- state the exact reason
- state what was checked instead
- state the remaining risk

### Test Artifact Placement

Project-specific test locations:

- Unit tests: TODO
- Integration tests: TODO
- CLI tests: TODO
- API / contract tests: TODO
- GUI / browser / Playwright tests: TODO
- Test fixtures: TODO
- Snapshots / golden files: TODO
- Test reports / traces / screenshots: TODO (for example, `playwright-report/`, `test-results/`, or another project-defined path)
- Temporary test output: TODO (OS temp is allowed only for ephemeral scratch/cache data that users do not need to open, review, or reference)

Rules:

- Do not place new test files in the repository root unless this section explicitly allows it.
- Unless the user explicitly requests an external or temporary-only artifact, user-visible test files, test plans, reports, traces, screenshots, generated fixtures, golden files, and verification artifacts must be written inside the repository at a project-defined path or after a placement decision.
- Do not introduce `playwright.config.*`, `tests/e2e/`, `e2e/`, screenshots, traces, browser fixtures, or browser reports without first confirming the intended location.
- If a new test category is introduced, ask the user for its location once, then record the chosen convention here.
- OpenSpec test documents belong in `openspec/changes/<change-id>/test-plan.md`.
- Non-OpenSpec test documents require an explicit placement decision before writing.

## Security Rules

- Never print, commit, log, or expose secrets, tokens, private keys, cookies, credentials, or production environment values.
- Do not weaken authentication, authorization, validation, rate limiting, logging, auditing, encryption, sandboxing, or permission checks without explicit approval.
- Treat generated files, uploaded files, external data, and user-controlled input as untrusted.
- Prefer safe defaults and fail-closed behavior for security-sensitive code.
- Do not add network calls, telemetry, external services, or data collection unless explicitly requested.
- Do not modify production, deployment, or infrastructure behavior without explicit approval.

## Git Rules

Git is the safety net for AI-assisted changes.

### Branch Policy

- Read-only tasks do not require a branch.
- Any task that writes files must not work directly on `main`, `master`, or `trunk`.
- For small, local changes, create or use a task branch in the current working tree.
- For large, risky, experimental, multi-file, multi-session, or parallel-agent changes, use a task branch in a separate git worktree.
- If the current working tree has unrelated uncommitted changes, stop and ask the user how to proceed before writing files. Offer clear choices: continue in the current working tree and accept mixing risk, create/use a separate worktree, or wait for the user to commit/stash/clean the existing changes. Do not choose a separate worktree automatically unless the user already approved that workflow in the current task.
- If already on a non-main branch, confirm it belongs to the current task before editing. If it is unrelated, create a new task branch or worktree.

Suggested branch names:

- `feature/<short-slug>`
- `fix/<short-slug>`
- `refactor/<short-slug>`
- `docs/<short-slug>`
- `chore/<short-slug>`

### Savepoint Commit Policy

- On non-main task branches, create small verified savepoint commits.
- Commit after each logical increment that has been tested, built, typechecked, linted, or otherwise verified with the smallest relevant evidence.
- Each commit should do one logical thing.
- Do not accumulate large uncommitted changes.
- Prefer many small reversible commits over one giant commit.
- Use `wip:` commits only for private intermediate checkpoints that are not intended to merge as-is.

Before committing:

1. Run `git status --short --branch`.
2. Inspect `git diff` and/or `git diff --staged`.
3. Stage only explicit task-related paths.
4. Check for secrets, generated files, unrelated files, and accidental broad formatting.
5. Run the smallest relevant verification.
6. Commit with a message that explains the purpose.

### Worktree Policy

Ask before using branch + worktree when:

- the user asks not to pollute the current branch;
- the current working tree has unrelated uncommitted changes;

When unrelated uncommitted changes are present, ask the user to choose before writing files. Recommended options:

```text
A. Continue in the current working tree and accept mixing risk.
B. Create/use a separate worktree.
C. Pause while the existing changes are committed, stashed, or cleaned by the user.
```

Do not auto-select option B unless the user pre-approved isolated worktree handling for the current task.

Use branch + worktree without an extra dirty-workspace question when:

- the user explicitly chooses or requests an isolated worktree;
- multiple agents or implementation approaches will run in parallel;
- the task is broad, risky, experimental, or likely to span multiple sessions;
- the task touches many files or crosses multiple subsystems.

Prefer a sibling worktree directory:

```bash
git worktree add -b <branch-name> ../<repo>-<task-slug> <base-branch>
```

Use project-local `.worktrees/<task-slug>` only when `.worktrees/` is ignored. Do not add `.worktrees/` to this workflow repository just because a downstream project uses worktrees; add the ignore rule in the project where the worktree directory will exist.

### Never Without Explicit Approval

- push
- merge into main/default branch
- rebase shared history
- amend commits
- reset hard
- clean untracked files destructively
- delete branches or remove worktrees
- skip hooks
- commit secrets or environment files

## Documentation Rules

Update documentation when behavior, setup commands, public APIs, configuration, or user-facing workflows change.

Do not update documentation for unrelated cleanup.

Do not store temporary task state, personal memory, private notes, one-off decisions, or chat summaries in `AGENTS.md`.

## Dependency Rules

- Do not add dependencies unless the task requires them.
- Prefer standard library and existing project dependencies first.
- If a dependency is necessary, explain why the existing stack is insufficient.
- Do not change lockfiles unless dependency changes require it.
- Keep dependency changes isolated from unrelated code changes.

## Generated and Vendor Files

Do not edit generated or vendored files directly unless the project documentation explicitly requires it.

If generated output must change:

- modify the source file or generator input first
- run the documented generation command
- include generated output only when the project tracks it

## Final Response Requirements

In the final response for code-changing tasks, include:

- what changed
- files touched
- verification run
- skipped checks and why
- remaining risks or follow-up items

Do not overstate certainty. If something was not verified, say so.
