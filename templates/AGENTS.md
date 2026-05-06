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

## Security Rules

- Never print, commit, log, or expose secrets, tokens, private keys, cookies, credentials, or production environment values.
- Do not weaken authentication, authorization, validation, rate limiting, logging, auditing, encryption, sandboxing, or permission checks without explicit approval.
- Treat generated files, uploaded files, external data, and user-controlled input as untrusted.
- Prefer safe defaults and fail-closed behavior for security-sensitive code.
- Do not add network calls, telemetry, external services, or data collection unless explicitly requested.
- Do not modify production, deployment, or infrastructure behavior without explicit approval.

## Git Rules

- Do not create commits, branches, tags, or pull requests unless explicitly requested.
- Do not rewrite Git history unless explicitly requested.
- Do not stage unrelated files.
- Do not include generated files in commits unless the project normally tracks them or the user requests it.
- Before summarizing changes, inspect the diff when possible.

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
