#!/usr/bin/env python3
"""Zero-dependency structure/content check for delegation protocol harness files."""

from __future__ import annotations

import argparse
import copy
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import sys
import tempfile
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "agents/rose.md",
    "agents/implementer.md",
    "agents/code-scout.md",
    ".agents/skills/parallel-subagent-dispatch/SKILL.md",
    ".agents/skills/verification-before-completion/SKILL.md",
    ".agents/skills/review-pipeline/SKILL.md",
    ".agents/skills/repo-evidence-first/SKILL.md",
    ".agents/skills/session-handoff/SKILL.md",
    ".agents/skills/aili-delivery-flow/references/direct-vs-delegated-work.md",
    ".agents/skills/aili-delivery-flow/references/artifact-contracts.md",
    ".agents/skills/aili-delivery-flow/references/build-execution-loop.md",
    ".agents/skills/aili-delivery-flow/references/test-document-policy.md",
    ".agents/skills/aili-delivery-flow/references/protocols/subagent-task-packet.md",
    ".agents/skills/aili-delivery-flow/references/protocols/subagent-result.md",
    ".agents/skills/aili-delivery-flow/references/protocols/compact-evidence-pack.md",
    ".agents/skills/mature-project-pattern-research/SKILL.md",
    ".agents/skills/mature-project-pattern-research/references/research-rubric.md",
    ".agents/skills/aili-delivery-flow/references/protocols/worktree-context.md",
    ".agents/skills/aili-delivery-flow/references/protocols/implementation-package.md",
    "scripts/opencode_permission_probe.mjs",
    "docs/harness/fixtures/cross-worktree-permission-fixtures.yaml",
    "tests/opencode-permission-probe.test.mjs",
]

P6_AGENT_FILES = [
    "agents/rose.md",
    "agents/agent-evaluator.md",
    "agents/ai-regression-scout.md",
    "agents/browser-qa-runner.md",
    "agents/code-reviewer.md",
    "agents/code-scout.md",
    "agents/convergence-reviewer.md",
    "agents/doc-researcher.md",
    "agents/e2e-artifact-runner.md",
    "agents/implementer.md",
    "agents/opensource-sanitizer.md",
    "agents/plan-auditor.md",
    "agents/pr-test-analyzer.md",
    "agents/security-auditor.md",
    "agents/silent-failure-reviewer.md",
    "agents/spec-miner.md",
    "agents/test-coverage-reviewer.md",
    "agents/test-engineer.md",
    "agents/web-performance-auditor.md",
    "agents/web-researcher.md",
]

ROSE_TASK_RULES = [
    ("*", "deny"), ("code-scout", "allow"), ("convergence-reviewer", "allow"),
    ("doc-researcher", "allow"), ("web-researcher", "allow"), ("plan-auditor", "allow"),
    ("implementer", "allow"), ("code-reviewer", "allow"),
    ("test-coverage-reviewer", "allow"), ("pr-test-analyzer", "allow"),
    ("ai-regression-scout", "allow"), ("silent-failure-reviewer", "allow"),
    ("browser-qa-runner", "allow"), ("e2e-artifact-runner", "allow"), ("spec-miner", "allow"),
    ("agent-evaluator", "allow"), ("opensource-sanitizer", "allow"), ("test-engineer", "allow"),
    ("security-auditor", "allow"), ("explore", "allow"), ("general", "ask"),
]

CONTENT_CHECKS = {
    "agents/rose.md": ["# ROSE", "Prefer direct work", "Default concurrency is at most two", "smallest claim-matched check", "aili-delivery-flow"],
    "agents/implementer.md": ["## Role", "## Goal", "Implement one complete, scoped code-change assignment", "## Success criteria", "## Stop"],
    "agents/code-scout.md": ["## Role", "compact locality map", "Do not plan, review, edit, or implement", "## Output"],
    ".agents/skills/parallel-subagent-dispatch/SKILL.md": ["Direct ROSE work is the default", "Default to at most two concurrent subagents", "## Compact packet", "Goal:", "STATUS:"],
    ".agents/skills/verification-before-completion/SKILL.md": ["smallest fresh check", "Do not automatically dispatch a verifier", "Unverified"],
    ".agents/skills/aili-delivery-flow/references/direct-vs-delegated-work.md": ["Direct ROSE work is the default", "Default concurrency is at most two", "Do not automatically add review"],
    ".agents/skills/aili-delivery-flow/references/protocols/subagent-task-packet.md": ["Goal:", "Scope:", "Allowed actions:", "Expected result:", "Stop when:"],
    ".agents/skills/aili-delivery-flow/references/protocols/subagent-result.md": ["STATUS: completed | partial | blocked | unverified", "EVIDENCE:", "BLOCKERS:"],
    ".agents/skills/review-pipeline/SKILL.md": ["Never creates an automatic review swarm", "at most two relevant specialists", "one targeted recheck"],
    ".agents/skills/aili-delivery-flow/references/artifact-contracts.md": ["evidence_state", "one minimal direct changed-scope", "IMPLEMENTED_TARGETED_VERIFIED", "neither a waiver nor accepted-`Unverified` wording is a BUILD-readiness alternative"],
    ".agents/skills/aili-delivery-flow/references/build-execution-loop.md": ["active accepted contract", "A33 admission and operation gates", "Hidden or unrequested AILI self-automation", "explicitly scoped product/repository CI", "IMPLEMENTED_TARGETED_VERIFIED"],
    ".agents/skills/aili-delivery-flow/references/test-document-policy.md": ["BUILD readiness is only `READY` or `BLOCKED`", "fresh explicit intent", "exact commit/push/merge/release approvals"],
}

FORBIDDEN_CODE_SCOUT_BASH = [
    '"git grep*": allow',
    '"rg*": allow',
    '"grep*": allow',
    '"find*": allow',
    '"ls*": allow',
]

CANONICAL_PROTOCOL_PATH = ".agents/skills/aili-delivery-flow/references/protocols/"
A33_SCHEMA = "aili.a33-worktree-evidence.v1"
A33_FIXTURE_SCHEMA = "aili.cross-worktree-permission-fixtures.v3"
A33_CASE_FIELDS = ["id", "subset", "status", "exit_code", "operation_id", "approval_ref", "host_identity", "source_identity", "target_identity", "expected_delta", "observed_delta", "evidence_refs", "unverified", "cleanup_state"]
A33_RUNTIME_CASE_FIELDS = ["id", "subset", "status", "exit_code", "run_id", *A33_CASE_FIELDS[4:]]
A33_IDENTITY_FIELDS = ["identity_state", "declared_root", "path_state", "canonical_root", "git_toplevel", "git_private_dir", "git_common_dir", "git_head", "git_branch", "detached_head", "worktree_membership", "dirty_state", "tracked_files", "untracked_files", "ignored_files", "artifact_files", "unknown_files"]
A33_DELTA_FIELDS = ["target_path", "worktree_membership", "common_dir_identity", "common_dir_admin_entry", "branch_ref", "branch_reflog", "unrelated_common_dir_entries", "unrelated_refs", "config", "hooks", "unrelated_worktree_records", "unrelated_prunable_entries", "other_files"]
A33_INTERNAL_EVIDENCE_VERSION = "aili.a33-runtime-evidence.internal.v1"
A33_OPERATION_FIELDS = ["operation_id", "kind", "operation_class", "source", "destination", "repo_key", "worktree_key", "branch", "base_ref", "branch_mode", "reflog_policy"]
A33_APPROVAL_FIELDS = ["approval_id", "run_id", "operation_id", "kind", "operation_class", "source", "destination", "repo_key", "worktree_key", "branch", "base_ref", "branch_mode", "reflog_policy", "expiry", "decision_ref", "trusted_code_risk", "status"]
A33_OPERATION_RESULT_FIELDS = ["schema_version", "command", "status", "exit_code", "run_id", "operation", "approval", "effect_started", "expected_delta", "observed_delta", "evidence_refs", "unverified"]
A33_SCENARIO_FIELDS = ["id", "family", "expected_outcome", "prerequisites", "operation_kind", "attachment_selector", "approval_variant", "expected_transition", "required_evidence_types", "cleanup_expectation"]
A33_EVIDENCE_FIELDS = ["schema_version", "evidence_id", "scenario_id", "family", "source", "operation_id", "operation_kind", "attachment_selector", "approval_variant", "status", "exit_code", "effect_started", "before_state", "after_state", "expected_delta", "observed_delta", "evidence_types", "evidence_refs", "contradiction", "semantic_observation", "semantic_rejection", "operation_bindings", "attempt", "cleanup_state"]
A33_RAW_INVENTORY_FIELDS = ["schema_version", "target_present", "status_porcelain_v2", "worktree_porcelain", "tracked_files", "artifact_files", "unknown_files", "visible_files", "allowlisted_ephemeral_artifacts", "expected_source", "observed_source", "expected_path", "observed_path", "expected_membership", "observed_membership"]
A33_MARKER_FIELDS = ["schema_version", "run_root", "run_id", "cleanup_nonce"]
A33_SNAPSHOT_PRECONDITION_FIELDS = ["destination_present", "registered"]
A33_OPERATION_SNAPSHOT_FIELDS = ["schema_version", "run_id", *A33_OPERATION_FIELDS, "preconditions"]
A33_APPROVAL_BINDING_FIELDS = ["run_id", "operation_id", "kind", "operation_class", "source", "destination", "repo_key", "worktree_key", "branch", "base_ref", "branch_mode", "reflog_policy"]
A33_APPROVAL_TAXONOMY = ["schema_omission", "missing", "declined", "unavailable", "stale_snapshot_mismatch", "stale_unverified", "expired", "reused", "wrong_operation", "wrong_source", "wrong_destination", "wrong_branch", "wrong_base_ref", "repo_key_mismatch", "worktree_key_mismatch", "real_for_fixture", "operation_class_mismatch", "mismatched", "add_risk_declined", "add_risk_unavailable", "remove_risk_invalid", "valid"]


def _a33_scenario(id_: str, family: str, outcome: str, prerequisites: str, kind: str | None,
                  selector: str, variant: str, transition: str, evidence: str, cleanup: str) -> dict[str, Any]:
    return {"id": id_, "family": family, "expected_outcome": outcome,
            "prerequisites": prerequisites.split() if prerequisites else [], "operation_kind": kind,
            "attachment_selector": selector, "approval_variant": variant,
            "expected_transition": transition, "required_evidence_types": evidence.split(),
            "cleanup_expectation": cleanup}


_S = _a33_scenario
A33_RUNTIME_SCENARIO_REGISTRY = [
    _S("a33-host-git-positive", "host-ignore-nested-prepare", "pass", "prepare", None, "host", "none", "unchanged", "host-identity git-toplevel", "retain"),
    _S("a33-ignore-positive", "host-ignore-nested-prepare", "pass", "prepare", None, "host-destination", "none", "unchanged", "check-ignore-nonmatching ignore-provenance", "retain"),
    _S("a33-multiple-attachments", "host-ignore-nested-prepare", "pass", "prepare", None, "all-attachments", "none", "unchanged", "attachment-descriptors distinct-destinations", "retain"),
    _S("a33-runtime-prepare-no-worktree-effect", "host-ignore-nested-prepare", "pass", "prepare", None, "all-attachments", "none", "unchanged", "worktree-list-before worktree-list-after zero-worktree-effects", "retain"),
    _S("a33-runtime-effective-profile-observed", "effective-profile-install", "pass", "isolated-current-platform-profile", None, "isolated-opencode", "none", "unchanged", "effective-merged-permissions permission-provenance", "retain"),
    _S("a33-runtime-install-observed", "effective-profile-install", "pass", "isolated-current-platform-install", None, "isolated-opencode", "none", "unchanged", "canonical-agent-files installed-whole-file-equality", "retain"),
    _S("a33-runtime-nested-repository-observed", "host-ignore-nested-prepare", "pass", "valid-adds", "add", "all-attachments", "valid", "absent-to-populated", "nested-destinations worktree-membership", "retain"),
    _S("a33-runtime-approval-positive", "valid-add", "pass", "fresh-add-approval", "add", "existing", "valid", "absent-to-populated", "approval-binding approval-unexpired approval-unique", "registered"),
    _S("a33-runtime-each-attachment-add-separate-approval", "valid-add", "pass", "valid-adds", "add", "all-attachments", "valid-distinct", "absent-to-populated", "all-add-approvals approval-unique approval-binding", "registered"),
    _S("a33-runtime-each-attachment-remove-separate-approval", "valid-remove", "pass", "valid-removes", "remove", "all-attachments", "valid-distinct", "populated-to-absent", "all-remove-approvals approval-unique approval-binding", "removed"),
    _S("a33-runtime-add-approval-wrong-zero-effect", "approval-key-class-risk-negative", "blocked", "prepare", "add", "existing", "wrong-operation-id", "unchanged", "approval-classification no-effect unchanged-state", "not_registered"),
    _S("a33-runtime-add-approval-reused-zero-effect", "approval-key-class-risk-negative", "blocked", "used-add-approval", "add", "existing", "reused", "unchanged", "approval-classification approval-reuse no-effect unchanged-state", "not_registered"),
    _S("a33-runtime-remove-approval-wrong-zero-effect", "approval-key-class-risk-negative", "blocked", "registered-target", "remove", "existing", "wrong-operation", "unchanged", "approval-classification no-effect unchanged-state", "registered"),
    _S("a33-runtime-remove-approval-reused-zero-effect", "approval-key-class-risk-negative", "blocked", "registered-target used-remove-approval", "remove", "existing", "reused", "unchanged", "approval-classification approval-reuse no-effect unchanged-state", "registered"),
    _S("a33-runtime-fixture-add-real-approval-zero-effect", "approval-key-class-risk-negative", "blocked", "prepare", "add", "existing", "real-for-fixture", "unchanged", "approval-classification no-effect unchanged-state", "not_registered"),
    _S("a33-runtime-fixture-remove-real-approval-zero-effect", "approval-key-class-risk-negative", "blocked", "registered-target", "remove", "existing", "real-for-fixture", "unchanged", "approval-classification no-effect unchanged-state", "registered"),
    _S("a33-runtime-operation-class-mismatch-zero-effect", "approval-key-class-risk-negative", "blocked", "prepare", "add", "existing", "operation-class-mismatch", "unchanged", "approval-classification no-effect unchanged-state", "not_registered"),
    _S("a33-runtime-approval-missing-zero-effect", "approval-key-class-risk-negative", "blocked", "prepare", "add", "existing", "missing", "unchanged", "approval-classification no-effect unchanged-state", "not_registered"),
    _S("a33-runtime-missing-approval-null-fields", "approval-key-class-risk-negative", "blocked", "prepare", "add", "existing", "missing", "unchanged", "missing-approval-null-fields no-effect unchanged-state", "not_registered"),
    _S("a33-runtime-approval-stale-zero-effect", "approval-key-class-risk-negative", "blocked", "approval-snapshot", "add", "existing", "stale-snapshot-mismatch", "unchanged", "approval-classification snapshot-mismatch no-effect unchanged-state", "not_registered"),
    _S("a33-runtime-approval-mismatched-zero-effect", "approval-key-class-risk-negative", "blocked", "prepare", "add", "existing", "mismatched", "unchanged", "approval-classification no-effect unchanged-state", "not_registered"),
    _S("a33-runtime-approval-expired-zero-effect", "approval-key-class-risk-negative", "blocked", "prepare", "add", "existing", "expired", "unchanged", "approval-classification no-effect unchanged-state", "not_registered"),
    _S("a33-runtime-approval-wrong-source-zero-effect", "approval-key-class-risk-negative", "blocked", "prepare", "add", "existing", "wrong-source", "unchanged", "approval-classification no-effect unchanged-state", "not_registered"),
    _S("a33-runtime-approval-wrong-destination-zero-effect", "approval-key-class-risk-negative", "blocked", "prepare", "add", "existing", "wrong-destination", "unchanged", "approval-classification no-effect unchanged-state", "not_registered"),
    _S("a33-runtime-approval-wrong-branch-zero-effect", "approval-key-class-risk-negative", "blocked", "prepare", "add", "existing", "wrong-branch", "unchanged", "approval-classification no-effect unchanged-state", "not_registered"),
    _S("a33-runtime-approval-wrong-ref-zero-effect", "approval-key-class-risk-negative", "blocked", "prepare", "add", "existing", "wrong-base-ref", "unchanged", "approval-classification no-effect unchanged-state", "not_registered"),
    _S("a33-runtime-add-approval-reused-real-remove-zero-effect", "approval-key-class-risk-negative", "blocked", "used-add-approval registered-target", "remove", "existing", "reused-add-for-remove", "unchanged", "approval-classification approval-reuse no-effect unchanged-state", "registered"),
    _S("a33-runtime-approval-other-operation-zero-effect", "approval-key-class-risk-negative", "blocked", "prepare", "add", "existing", "wrong-operation-kind", "unchanged", "approval-classification no-effect unchanged-state", "not_registered"),
    _S("a33-runtime-approval-declined-unavailable", "approval-key-class-risk-negative", "blocked", "prepare", "add", "existing", "declined-or-unavailable", "unchanged", "approval-classification no-effect unchanged-state", "not_registered"),
    _S("a33-runtime-add-trusted-code-risk-accepted", "valid-add", "pass", "fresh-add-approval", "add", "all-attachments", "add-risk-accepted", "absent-to-populated", "trusted-code-risk approval-binding worktree-effect", "registered"),
    _S("a33-runtime-add-trusted-code-risk-declined-zero-effect", "approval-key-class-risk-negative", "blocked", "prepare", "add", "existing", "add-risk-declined", "unchanged", "approval-classification trusted-code-risk no-effect unchanged-state", "not_registered"),
    _S("a33-runtime-add-trusted-code-risk-unavailable-zero-effect", "approval-key-class-risk-negative", "blocked", "prepare", "add", "existing", "add-risk-unavailable", "unchanged", "approval-classification trusted-code-risk no-effect unchanged-state", "not_registered"),
    _S("a33-runtime-remove-trusted-code-risk-not-applicable", "valid-remove", "pass", "fresh-remove-approval clean-inventory", "remove", "all-attachments", "remove-risk-not-applicable", "populated-to-absent", "trusted-code-risk approval-binding worktree-effect", "removed"),
    _S("a33-pre-add-target-absent", "valid-add", "pass", "fresh-add-approval", "add", "all-attachments", "valid", "absent-to-populated", "target-before-identity identity-schema", "registered"),
    _S("a33-add-delta-exact", "valid-add", "pass", "valid-adds", "add", "all-attachments", "valid", "absent-to-populated", "expected-delta observed-delta exact-delta", "registered"),
    _S("a33-add-common-dir-exact-allowed-delta", "valid-add", "pass", "valid-adds", "add", "all-attachments", "valid", "absent-to-populated", "common-dir-admin-entry branch-ref branch-reflog exact-delta", "registered"),
    _S("a33-add-common-dir-identity-preserved", "valid-add", "pass", "valid-adds", "add", "all-attachments", "valid", "absent-to-populated", "common-dir-identity exact-delta", "registered"),
    _S("a33-add-existing-branch-no-ref-reflog-creation", "valid-add", "pass", "valid-add-existing", "add", "existing", "valid", "absent-to-populated", "branch-ref branch-reflog exact-delta", "registered"),
    _S("a33-add-new-branch-reflog-enabled-created", "valid-add", "pass", "valid-add-create-enabled", "add", "create-enabled", "valid", "absent-to-populated", "branch-ref branch-reflog exact-delta", "registered"),
    _S("a33-add-new-branch-reflog-disabled-absent", "valid-add", "pass", "valid-add-create-disabled", "add", "create-disabled", "valid", "absent-to-populated", "branch-ref branch-reflog exact-delta", "registered"),
    _S("a33-unrelated-common-dir-preserved", "valid-add", "pass", "valid-adds valid-removes", None, "all-attachments", "valid", "declared-only", "unrelated-common-dir unrelated-refs unrelated-worktrees exact-delta", "removed"),
    _S("a33-add-unrelated-preserved", "valid-add", "pass", "valid-adds", "add", "all-attachments", "valid", "absent-to-populated", "unrelated-common-dir unrelated-refs unrelated-worktrees exact-delta", "registered"),
    _S("a33-pre-remove-target-populated", "valid-remove", "pass", "clean-inventory", "remove", "all-attachments", "valid", "populated-to-absent", "target-before-identity identity-schema", "removed"),
    _S("a33-remove-delta-exact", "valid-remove", "pass", "valid-removes", "remove", "all-attachments", "valid", "populated-to-absent", "expected-delta observed-delta exact-delta", "removed"),
    _S("a33-remove-common-dir-exact-allowed-delta", "valid-remove", "pass", "valid-removes", "remove", "all-attachments", "valid", "populated-to-absent", "common-dir-admin-entry branch-ref branch-reflog exact-delta", "removed"),
    _S("a33-remove-common-dir-identity-preserved", "valid-remove", "pass", "valid-removes", "remove", "all-attachments", "valid", "populated-to-absent", "common-dir-identity exact-delta", "removed"),
    _S("a33-remove-dirty-block", "typed-removal-inventory", "blocked", "registered-target", "remove", "existing", "tracked-modified-or-deleted", "unchanged", "typed-inventory tracked-state no-effect unchanged-state", "registered"),
    _S("a33-remove-unknown-block", "typed-removal-inventory", "blocked", "registered-target", "remove", "existing", "unknown", "unchanged", "typed-inventory unknown-state no-effect unchanged-state", "registered"),
    _S("a33-remove-user-visible-block", "typed-removal-inventory", "blocked", "registered-target", "remove", "existing", "user-visible", "unchanged", "typed-inventory user-visible-state no-effect unchanged-state", "registered"),
    _S("a33-remove-ignored-block", "typed-removal-inventory", "blocked", "registered-target", "remove", "existing", "ignored", "unchanged", "typed-inventory ignored-state no-effect unchanged-state", "registered"),
    _S("a33-remove-untracked-block", "typed-removal-inventory", "blocked", "registered-target", "remove", "existing", "untracked", "unchanged", "typed-inventory untracked-state no-effect unchanged-state", "registered"),
    _S("a33-remove-artifact-block", "typed-removal-inventory", "blocked", "registered-target", "remove", "existing", "artifact", "unchanged", "typed-inventory artifact-state no-effect unchanged-state", "registered"),
    _S("a33-remove-locked-block", "typed-removal-inventory", "blocked", "registered-target", "remove", "existing", "locked", "unchanged", "typed-inventory locked-state no-effect unchanged-state", "registered"),
    _S("a33-remove-wrong-source-block", "typed-removal-inventory", "blocked", "registered-target", "remove", "existing", "wrong-source", "unchanged", "typed-inventory source-binding no-effect unchanged-state", "registered"),
    _S("a33-remove-wrong-path-block", "typed-removal-inventory", "blocked", "registered-target", "remove", "existing", "wrong-path-or-membership", "unchanged", "typed-inventory path-binding membership-binding no-effect unchanged-state", "registered"),
    _S("a33-remove-missing-target-block", "typed-removal-inventory", "blocked", "prepare", "remove", "existing", "missing", "unchanged", "typed-inventory missing-state no-effect unchanged-state", "not_registered"),
    _S("a33-runtime-cleanup-after-approved-removes", "cleanup-global-consumption", "pass", "valid-removes", None, "all-attachments", "all-removed", "removed", "registered-attachments approved-removes cleanup-eligibility", "eligible_for_global_join"),
    _S("a33-runtime-cleanup-retain-registered", "cleanup-global-consumption", "pass", "blocked-remove", None, "run-root", "retained", "unchanged", "registered-attachments retained-root cleanup-ineligible", "retain"),
    _S("a33-residual-nongoal-exit0", "cleanup-global-consumption", "pass", "all-runtime-cases", None, "global", "named-residuals", "unchanged", "residual-nongoals cleanup-eligibility", "eligible_for_global_join"),
    _S("a33-material-missing-exit3", "deliberate-violation", "unverified", "missing-mandatory-positive", None, "global", "missing-positive", "unchanged", "missing-evidence-classification", "retain"),
    _S("a33-contract-violation-exit5", "deliberate-violation", "fail", "contradictory-evidence", None, "global", "contract-violation", "contradictory", "violation-classification", "retain"),
    _S("a33-common-dir-identity-change-block", "deliberate-violation", "fail", "mutated-add-or-remove", None, "all-attachments", "common-dir-identity-change", "wrong-delta", "common-dir-identity violation-classification", "retain"),
    _S("a33-add-common-dir-unrelated-mutation-block", "deliberate-violation", "fail", "mutated-add", "add", "all-attachments", "unrelated-mutation", "wrong-delta", "unrelated-common-dir violation-classification", "retain"),
    _S("a33-remove-common-dir-unrelated-mutation-block", "deliberate-violation", "fail", "mutated-remove", "remove", "all-attachments", "unrelated-mutation", "wrong-delta", "unrelated-common-dir violation-classification", "retain"),
    _S("a33-add-new-branch-reflog-enabled-missing-block", "deliberate-violation", "fail", "mutated-add-create-enabled", "add", "create-enabled", "missing-reflog", "wrong-delta", "branch-ref branch-reflog violation-classification", "retain"),
    _S("a33-add-new-branch-reflog-disabled-unexpected-block", "deliberate-violation", "fail", "mutated-add-create-disabled", "add", "create-disabled", "unexpected-reflog", "wrong-delta", "branch-ref branch-reflog violation-classification", "retain"),
    _S("a33-remove-branch-deletion-block", "deliberate-violation", "fail", "mutated-remove", "remove", "all-attachments", "branch-deletion", "wrong-delta", "branch-ref violation-classification", "retain"),
    _S("a33-remove-branch-reflog-mutation-block", "deliberate-violation", "fail", "mutated-remove", "remove", "all-attachments", "reflog-mutation", "wrong-delta", "branch-reflog violation-classification", "retain"),
    _S("a33-runtime-key-mismatch-zero-effect", "approval-key-class-risk-negative", "blocked", "prepare registered-target", None, "repo-and-worktree-keys-add-and-remove", "repo-or-worktree-key-mismatch", "unchanged", "approval-classification key-parameter-matrix no-effect unchanged-state", "retain"),
    _S("a33-runtime-identity-transition-schema", "cleanup-global-consumption", "pass", "valid-adds valid-removes", None, "all-attachments", "valid", "absent-populated-absent", "host-identity source-identity target-before-identity target-after-identity identity-schema", "removed"),
]
del _S


def frontmatter(text: str) -> str:
    parts = text.split("---", 2)
    return parts[1] if len(parts) == 3 else ""


def permission_block(fm: str, key: str) -> str:
    marker = f"\n  {key}:"
    start = fm.find(marker)
    if start == -1:
        return ""
    remainder = fm[start + len(marker):]
    next_key = remainder.find("\n  ")
    return remainder if next_key == -1 else remainder[:next_key]


def permission_entries(fm: str) -> list[tuple[str, str]]:
    lines = fm.splitlines()
    try:
        start = lines.index("permission:") + 1
    except ValueError:
        return []
    entries: list[tuple[str, str]] = []
    for line in lines[start:]:
        if line and not line.startswith(" "):
            break
        if not line.startswith("  ") or line.startswith("    "):
            continue
        key, separator, value = line.strip().partition(":")
        if not separator:
            continue
        entries.append((key.strip('"\''), value.strip()))
    return entries


def nested_permission_rules(fm: str, key: str) -> list[tuple[str, str]]:
    rules: list[tuple[str, str]] = []
    lines = fm.splitlines()
    marker = f"  {key}:"
    try:
        start = lines.index(marker) + 1
    except ValueError:
        return rules
    for line in lines[start:]:
        if line.startswith("  ") and not line.startswith("    "):
            break
        stripped = line.strip()
        if not stripped or ":" not in stripped:
            continue
        name, value = stripped.rsplit(":", 1)
        rules.append((name.strip().strip('"\''), value.strip()))
    return rules


def p6_permission_failures() -> list[str]:
    failures: list[str] = []
    current = {path.relative_to(ROOT).as_posix() for path in (ROOT / "agents").glob("*.md")}
    expected = set(P6_AGENT_FILES)
    if len(P6_AGENT_FILES) != 20 or len(expected) != 20:
        failures.append("LEAN AGENT INVENTORY: expected exactly 20 unique Agent files")
    if current != expected:
        failures.append(f"LEAN AGENT INVENTORY MISMATCH: missing={sorted(expected-current)!r} extra={sorted(current-expected)!r}")

    headings = ["## Role", "## Goal", "## Success criteria", "## Constraints", "## Tools", "## Output", "## Stop"]
    for relative_path in P6_AGENT_FILES:
        path = ROOT / relative_path
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        fm = frontmatter(text)
        values = dict(permission_entries(fm))
        for heading in headings:
            if heading not in text:
                failures.append(f"LEAN AGENT STRUCTURE: {relative_path} :: {heading}")
        if relative_path == "agents/rose.md":
            if values.get("external_directory") != "ask":
                failures.append("LEAN AGENT ROSE EXTERNAL: expected ask for separately approved operations")
            if nested_permission_rules(fm, "task") != ROSE_TASK_RULES:
                failures.append("LEAN AGENT ROSE TASK ALLOWLIST CHANGED")
            continue
        if values.get("external_directory") != "deny":
            failures.append(f"LEAN AGENT MANAGED EXTERNAL: {relative_path}")
        if values.get("task") != "deny":
            failures.append(f"LEAN AGENT NON-DELEGATING: {relative_path}")
        read_rules = dict(nested_permission_rules(fm, "read"))
        if values.get("read") != "deny" and (read_rules.get(".git/**") != "deny" or read_rules.get("**/.git/**") != "deny"):
            failures.append(f"LEAN AGENT GIT READ: {relative_path}")
        edit_rules = dict(nested_permission_rules(fm, "edit"))
        if values.get("edit") != "deny" and (edit_rules.get(".git/**") != "deny" or edit_rules.get("**/.git/**") != "deny"):
            failures.append(f"LEAN AGENT GIT EDIT: {relative_path}")

    web = ROOT / "agents/web-researcher.md"
    if web.is_file():
        values = dict(permission_entries(frontmatter(web.read_text(encoding="utf-8"))))
        expected_web = {
            "*": "deny", "read": "deny", "list": "deny", "glob": "deny", "grep": "deny",
            "external_directory": "deny", "edit": "deny", "bash": "deny", "task": "deny",
            "lsp": "deny", "skill": "deny", "webfetch": "ask", "websearch": "ask",
            "apply_patch": "deny", "doom_loop": "deny",
        }
        if values != expected_web:
            failures.append(f"LEAN WEB-ONLY PROFILE: {values!r}")
    if (ROOT / "agents/debug-investigator.md").exists():
        failures.append("REMOVED AGENT STILL PRESENT: agents/debug-investigator.md")
    if (ROOT / ".agents/skills/debugging-and-error-recovery").exists():
        failures.append("REMOVED SKILL STILL PRESENT: debugging-and-error-recovery")
    return failures


def exact_keys(value: Any, fields: list[str]) -> bool:
    return isinstance(value, dict) and list(value) == fields


def load_a33_fixture(project: Path, fixture_arg: str) -> tuple[Path, dict[str, Any]]:
    candidate = Path(fixture_arg)
    candidate = (candidate if candidate.is_absolute() else project / candidate).resolve(strict=True)
    expected = (project / "docs/harness/fixtures/cross-worktree-permission-fixtures.yaml").resolve(strict=True)
    if candidate != expected or project not in candidate.parents:
        raise ValueError("fixture path must be the canonical project-local A33 fixture")
    fixture = json.loads(candidate.read_text(encoding="utf-8"))
    if fixture.get("schema") != A33_FIXTURE_SCHEMA or not isinstance(fixture.get("a33"), dict):
        raise ValueError("A33 fixture schema mismatch")
    config = fixture["a33"]
    exact_arrays = {
        "identity_fields": A33_IDENTITY_FIELDS, "delta_fields": A33_DELTA_FIELDS,
        "runtime_case_fields": A33_RUNTIME_CASE_FIELDS, "joined_case_fields": A33_CASE_FIELDS,
    }
    if any(config.get(name) != expected_fields for name, expected_fields in exact_arrays.items()):
        raise ValueError("A33 fixture field schema mismatch")
    static_ids = config.get("static_mandatory_case_ids", [])
    runtime_ids = config.get("runtime_mandatory_case_ids", [])
    if len(static_ids + runtime_ids) != len(set(static_ids + runtime_ids)):
        raise ValueError("A33 fixture case subsets overlap or duplicate")
    return candidate, config


def valid_case(row: Any, subset: str) -> bool:
    if not exact_keys(row, A33_CASE_FIELDS) or subset not in {"static", "runtime"} or row["subset"] != subset:
        return False
    if not isinstance(row["id"], str) or not row["id"] or row["status"] not in {"pass", "blocked", "Unverified", "fail"} or row["exit_code"] not in {0, 3, 5}:
        return False
    if any(row[name] is not None and (not isinstance(row[name], str) or not row[name]) for name in ("operation_id", "approval_ref")):
        return False
    if not isinstance(row["evidence_refs"], list) or not row["evidence_refs"] or not all(isinstance(item, str) and item for item in row["evidence_refs"]):
        return False
    if not isinstance(row["unverified"], list) or not all(isinstance(item, str) for item in row["unverified"]):
        return False
    if row["cleanup_state"] not in {None, "not_registered", "registered", "removed", "retained", "eligible_for_global_join", "blocked"}:
        return False
    if subset == "static":
        return all(row[name] is None for name in A33_CASE_FIELDS[4:11]) and row["cleanup_state"] is None
    if row["operation_id"] is None:
        return row["approval_ref"] is None and all(row[name] is None for name in ("host_identity", "source_identity", "target_identity", "expected_delta", "observed_delta"))
    if not all(valid_identity(row[name]) for name in ("host_identity", "source_identity", "target_identity")):
        return False
    if not valid_delta(row["expected_delta"]) or not valid_delta(row["observed_delta"]) or row["cleanup_state"] is None:
        return False
    return True


def valid_identity(identity: Any) -> bool:
    if not exact_keys(identity, A33_IDENTITY_FIELDS) or not isinstance(identity["declared_root"], str) or not identity["declared_root"].startswith("/"):
        return False
    if identity["identity_state"] == "absent":
        if identity["path_state"] != "absent" or identity["worktree_membership"] != "absent":
            return False
        allowed = {"identity_state", "declared_root", "path_state", "worktree_membership"}
        return all(identity[name] is None for name in A33_IDENTITY_FIELDS if name not in allowed)
    if identity["identity_state"] != "populated" or identity["path_state"] != "present" or identity["worktree_membership"] not in {"main", "linked"}:
        return False
    if any(not isinstance(identity[name], str) or not identity[name] for name in ("canonical_root", "git_toplevel", "git_private_dir", "git_common_dir", "git_head")):
        return False
    if not isinstance(identity["detached_head"], bool) or (identity["detached_head"] and identity["git_branch"] is not None) or (not identity["detached_head"] and (not isinstance(identity["git_branch"], str) or not identity["git_branch"])):
        return False
    dirty = identity["dirty_state"]
    if not exact_keys(dirty, ["tracked_modified", "tracked_deleted", "untracked_count", "ignored_count"]):
        return False
    if not isinstance(dirty["tracked_modified"], bool) or not isinstance(dirty["tracked_deleted"], bool) or any(not isinstance(dirty[name], int) or isinstance(dirty[name], bool) or dirty[name] < 0 for name in ("untracked_count", "ignored_count")):
        return False
    for name in ("tracked_files", "untracked_files", "ignored_files", "artifact_files", "unknown_files"):
        values = identity[name]
        if not isinstance(values, list) or values != sorted(set(values)) or any(not isinstance(value, str) or not value or value.startswith("/") or ".." in value.split("/") for value in values):
            return False
    return True


def valid_delta(delta: Any) -> bool:
    if not exact_keys(delta, A33_DELTA_FIELDS):
        return False
    for name in A33_DELTA_FIELDS:
        if not exact_keys(delta[name], ["before", "after", "change"]):
            return False
        before, after, change = delta[name]["before"], delta[name]["after"], delta[name]["change"]
        before_absent = before is None or before == "absent"
        if change == "created" and (not before_absent or after is None or after == "absent"):
            return False
        if change == "deleted" and (before_absent or (after is not None and after != "absent")):
            return False
        if change == "unchanged" and before != after:
            return False
        if change not in {"created", "deleted", "unchanged"}:
            return False
    return True


def validate_a33_scenario_registry(expected_ids: list[str], registry: Any = None) -> int:
    candidate = A33_RUNTIME_SCENARIO_REGISTRY if registry is None else registry
    if not isinstance(candidate, list) or candidate != A33_RUNTIME_SCENARIO_REGISTRY:
        return 5
    if len(candidate) != 70 or expected_ids != [row["id"] for row in candidate]:
        return 5
    if len(set(expected_ids)) != 70:
        return 5
    families = {"effective-profile-install", "host-ignore-nested-prepare", "approval-key-class-risk-negative", "valid-add", "typed-removal-inventory", "valid-remove", "deliberate-violation", "cleanup-global-consumption"}
    selectors = {"host", "host-destination", "all-attachments", "isolated-opencode", "existing", "create-enabled", "create-disabled", "repo-and-worktree-keys-add-and-remove", "run-root", "global"}
    signatures: set[str] = set()
    for row in candidate:
        if not exact_keys(row, A33_SCENARIO_FIELDS) or row["family"] not in families or row["expected_outcome"] not in {"pass", "blocked", "unverified", "fail"}:
            return 5
        if row["operation_kind"] not in {None, "add", "remove"} or row["attachment_selector"] not in selectors:
            return 5
        if not all(isinstance(value, str) and value for value in row["prerequisites"] + row["required_evidence_types"]):
            return 5
        if not row["required_evidence_types"] or len(row["required_evidence_types"]) != len(set(row["required_evidence_types"])):
            return 5
        signature = json.dumps([row[name] for name in A33_SCENARIO_FIELDS[1:]], sort_keys=True)
        if signature in signatures:
            return 5
        signatures.add(signature)
    return 0


def _inside(candidate: Path, parent: Path) -> bool:
    try:
        candidate.relative_to(parent)
        return candidate != parent
    except ValueError:
        return False


def _valid_key(value: Any) -> bool:
    return isinstance(value, str) and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}", value) is not None and value not in {".", "..", ".git", ".worktrees", "worktrees"}


def _operation_selector(operation: dict[str, Any]) -> str:
    if operation.get("branch_mode") == "existing":
        return "existing"
    return "create-enabled" if operation.get("reflog_policy") == "enabled" else "create-disabled"


def validate_a33_operation(operation: Any, state: dict[str, Any]) -> bool:
    if not exact_keys(operation, A33_OPERATION_FIELDS) or operation["kind"] not in {"add", "remove"} or operation["operation_class"] != "driver_fixture":
        return False
    if not _valid_key(operation["repo_key"]) or not _valid_key(operation["worktree_key"]):
        return False
    if operation["branch_mode"] not in {"existing", "create"} or operation["reflog_policy"] not in {"enabled", "disabled"}:
        return False
    strings = ["operation_id", "source", "destination", "branch", "base_ref"]
    if any(not isinstance(operation[name], str) or not operation[name] for name in strings):
        return False
    expected_destination = Path(state["host"]) / ".worktrees" / operation["repo_key"] / operation["worktree_key"]
    return Path(operation["destination"]) == expected_destination and _inside(Path(operation["source"]), Path(state["run_root"]))


def a33_approval_binding(value: dict[str, Any]) -> dict[str, Any]:
    return {name: value.get(name) for name in A33_APPROVAL_BINDING_FIELDS}


def build_a33_operation_snapshot(state: dict[str, Any], operation: dict[str, Any], registered: list[str] | None = None, destination_present: bool | None = None) -> dict[str, Any]:
    active = state.get("registered", []) if registered is None else registered
    return {
        "schema_version": A33_INTERNAL_EVIDENCE_VERSION, "run_id": state.get("run_id"), **operation,
        "preconditions": {"destination_present": Path(operation["destination"]).exists() if destination_present is None else destination_present, "registered": operation["destination"] in active},
    }


def valid_a33_operation_snapshot(snapshot: Any, state: dict[str, Any], operation: dict[str, Any]) -> bool:
    return exact_keys(snapshot, A33_OPERATION_SNAPSHOT_FIELDS) and snapshot["schema_version"] == A33_INTERNAL_EVIDENCE_VERSION \
        and snapshot["run_id"] == state.get("run_id") and all(snapshot[name] == operation[name] for name in A33_OPERATION_FIELDS) \
        and exact_keys(snapshot["preconditions"], A33_SNAPSHOT_PRECONDITION_FIELDS) \
        and all(isinstance(value, bool) for value in snapshot["preconditions"].values())


def valid_a33_approval_snapshot(record: Any, approval: dict[str, Any], state: dict[str, Any], operation: dict[str, Any]) -> bool:
    return exact_keys(record, ["approval_binding", "operation_snapshot"]) \
        and exact_keys(record["approval_binding"], A33_APPROVAL_BINDING_FIELDS) \
        and record["approval_binding"] == a33_approval_binding(approval) \
        and valid_a33_operation_snapshot(record["operation_snapshot"], state, operation)


def exact_consumed_add_for_remove(approval: dict[str, Any], consumed: Any, state: dict[str, Any], operation: dict[str, Any]) -> bool:
    if operation["kind"] != "remove" or not exact_keys(consumed, ["approval", "snapshot"]) \
            or not exact_keys(consumed["approval"], A33_APPROVAL_FIELDS) or consumed["approval"] != approval \
            or approval["kind"] != "add" or approval["status"] != "valid" or approval["run_id"] != state.get("run_id"):
        return False
    prior = next((candidate for candidate in state.get("operations", []) if candidate.get("operation_id") == approval["operation_id"] and candidate.get("kind") == "add"), None)
    shared = ["operation_class", "source", "destination", "repo_key", "worktree_key", "branch", "base_ref", "branch_mode", "reflog_policy"]
    return prior is not None and valid_a33_operation_snapshot(consumed["snapshot"], state, prior) \
        and all(approval[name] == prior[name] == operation[name] for name in shared)


def parse_managed_frontmatter(text: str) -> dict[str, Any]:
    lines = text.replace("\r\n", "\n").split("\n")
    if not lines or lines[0] != "---":
        raise ValueError("managed frontmatter malformed")
    try:
        end = lines.index("---", 1)
        permission_line = lines.index("permission:", 1, end)
    except ValueError as exc:
        raise ValueError("managed frontmatter malformed") from exc
    modes = [line[5:].strip() for line in lines[1:end] if line.startswith("mode:")]
    if len(modes) != 1 or modes[0] not in {"primary", "subagent"}:
        raise ValueError("managed frontmatter malformed")
    pattern = re.compile(r'^\s*(?:"((?:\\.|[^"])*)"|\'([^\']*)\'|([^:]+)):\s*(.*)$')
    stack: list[tuple[int, list[str]]] = [(-1, ["permission"])]
    permissions: list[dict[str, str]] = []
    for line in lines[permission_line + 1:end]:
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip(" "))
        if indent == 0:
            break
        if indent % 2 or "\t" in line:
            raise ValueError("managed permission malformed")
        match = pattern.fullmatch(line)
        if match is None:
            raise ValueError("managed permission malformed")
        key = json.loads(f'"{match.group(1)}"') if match.group(1) is not None else match.group(2) if match.group(2) is not None else match.group(3).strip()
        while len(stack) > 1 and stack[-1][0] >= indent:
            stack.pop()
        path = [*stack[-1][1], key]
        raw = match.group(4).strip()
        if not raw:
            stack.append((indent, path))
        else:
            value = json.loads(raw) if raw.startswith('"') else raw[1:-1] if raw.startswith("'") and raw.endswith("'") else raw
            if value not in {"allow", "ask", "deny"}:
                raise ValueError("managed permission malformed")
            permissions.append({"path": ".".join(path), "value": value})
    if not permissions or len({entry["path"] for entry in permissions}) != len(permissions):
        raise ValueError("managed permission malformed")
    return {"mode": modes[0], "permissions": permissions}


def managed_agent_sources(project: Path) -> tuple[Path, list[dict[str, Any]]]:
    manifest_path = project / "manifests" / "rose-aili.components.json"
    if manifest_path.resolve(strict=True) != manifest_path or manifest_path.is_symlink() or not manifest_path.is_file():
        raise ValueError("managed manifest path mismatch")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    entries = manifest.get("components", {}).get("agents") if isinstance(manifest, dict) else None
    fields = ["name", "path", "required", "defaultInstalled", "repositoryManaged"]
    if not isinstance(manifest, dict) or manifest.get("name") != "rose-aili" or manifest.get("schemaVersion") != 1 or not isinstance(entries, list) or len(entries) != 20:
        raise ValueError("managed manifest malformed")
    by_path: dict[str, dict[str, Any]] = {}
    for entry in entries:
        if not exact_keys(entry, fields) or not isinstance(entry["name"], str) or entry["path"] != f'agents/{entry["name"]}.md' \
                or entry["required"] is not True or entry["defaultInstalled"] is not True or entry["repositoryManaged"] is not True or entry["path"] in by_path:
            raise ValueError("managed manifest malformed")
        by_path[entry["path"]] = entry
    if set(by_path) != set(P6_AGENT_FILES) or len(by_path) != len(P6_AGENT_FILES):
        raise ValueError("managed manifest inventory mismatch")
    agents: list[dict[str, Any]] = []
    for relative in P6_AGENT_FILES:
        entry = by_path[relative]
        canonical_path = project / entry["path"]
        if canonical_path.resolve(strict=True) != canonical_path or canonical_path.is_symlink() or not canonical_path.is_file():
            raise ValueError("managed canonical path mismatch")
        content = canonical_path.read_bytes()
        agents.append({"name": entry["name"], "canonical_path": str(canonical_path), "bytes": content, "parsed": parse_managed_frontmatter(content.decode("utf-8"))})
    return manifest_path, agents


def exact_installer_summary(summary: Any, project: Path, opencode_home: Path) -> bool:
    return exact_keys(summary, ["mode", "runtime", "aili_home", "opencode_home", "dry_run", "no_update"]) \
        and summary["mode"] == "copy" and summary["runtime"] in {"linux", "macos", "wsl"} \
        and summary["aili_home"] == str(project) and summary["opencode_home"] == str(opencode_home) \
        and summary["dry_run"] == "false" and summary["no_update"] == "true"


def canonical_copy_installer(project: Path) -> Path | None:
    script = project / "scripts" / "install_opencode.sh"
    try:
        text = script.read_text(encoding="utf-8")
        mode = script.stat().st_mode
    except OSError:
        return None
    markers = ["--no-update)", 'NO_UPDATE="true"', '[ "$NO_UPDATE" = "true" ]', "Skipping repository update:", "copy)\n    ensure_repo\n    install_entries copy_entry"]
    if not Path("/bin/bash").is_file() or script.is_symlink() or script.resolve(strict=True) != script or not script.is_file() or not mode & 0o111:
        return None
    if any(marker not in text for marker in markers) or re.search(r"codegraph|openspec|npx\s|npm\s+install", text, re.IGNORECASE):
        return None
    return script


def observe_managed_profile(state: dict[str, Any], summary: Any) -> dict[str, Any]:
    project, run_root = Path(state["project"]), Path(state["run_root"])
    opencode_home = run_root / "opencode-home"
    manifest_path, canonical = managed_agent_sources(project)
    if opencode_home.resolve(strict=True) != opencode_home or opencode_home.is_symlink() or not opencode_home.is_dir() or not _inside(opencode_home, run_root):
        raise ValueError("managed install path mismatch")
    agents_root = opencode_home / "agents"
    if agents_root.resolve(strict=True) != agents_root or agents_root.is_symlink() or not agents_root.is_dir():
        raise ValueError("managed install path mismatch")
    disk = list(agents_root.iterdir())
    if any(not entry.name.endswith(".md") or entry.is_symlink() or not entry.is_file() for entry in disk):
        raise ValueError("managed install inventory mismatch")
    disk_names = [entry.stem for entry in disk]
    expected_names = [source["name"] for source in canonical]
    if set(disk_names) != set(expected_names) or len(disk_names) != len(expected_names):
        raise ValueError("managed install inventory mismatch")
    installed_names = list(expected_names)
    agents: list[dict[str, Any]] = []
    for source in canonical:
        installed_path = agents_root / f'{source["name"]}.md'
        if installed_path.is_symlink() or installed_path.resolve(strict=True) != installed_path or not installed_path.is_file() or not _inside(installed_path, opencode_home):
            raise ValueError("managed install path mismatch")
        installed_bytes = installed_path.read_bytes()
        if installed_bytes != source["bytes"]:
            raise ValueError("managed install byte mismatch")
        parsed = parse_managed_frontmatter(installed_bytes.decode("utf-8"))
        if parsed != source["parsed"]:
            raise ValueError("managed permission mismatch")
        permissions = {entry["path"]: entry["value"] for entry in parsed["permissions"]}
        if source["name"] == "rose":
            if parsed["mode"] != "primary":
                raise ValueError("managed ROSE distinction malformed")
        elif parsed["mode"] != "subagent" or permissions.get("permission.external_directory") != "deny" or permissions.get("permission.task") != "deny":
            raise ValueError("managed permission broadened")
        installed_text = str(installed_path)
        agents.append({
            "name": source["name"], "canonical_path": source["canonical_path"], "installed_path": installed_text,
            "install_mode": "copy", "exact_byte_equality": True, "mode": parsed["mode"], "permissions": parsed["permissions"],
            "unexpected_allow_ask": [],
            "provenance": [f'canonical:{source["canonical_path"]}', f"installed:{installed_text}", *[f'permission:{entry["path"]}={entry["value"]}' for entry in parsed["permissions"]]],
        })
    config_root = run_root / "home" / ".config"
    config_entries = sorted(str(path.relative_to(config_root)).replace("\\", "/") for path in config_root.rglob("*")) if config_root.exists() else []
    if config_entries or any((opencode_home / name).exists() or (opencode_home / name).is_symlink() for name in ["opencode.json", "opencode.jsonc"]) \
            or sorted(path.name for path in opencode_home.iterdir()) != ["AGENTS.md", "agents", "commands"]:
        raise ValueError("managed override layer unexpected")
    if not exact_installer_summary(summary, project, opencode_home):
        raise ValueError("managed installer summary malformed")
    return {
        "schema_version": A33_INTERNAL_EVIDENCE_VERSION, "command": state["managed_install_attempt"]["command"],
        "installer_summary": summary, "manifest_path": str(manifest_path), "manifest_regular_nonsymlink": True,
        "environment_controls": {"OPENCODE_ALLOW_CUSTOM_HOME": "yes", "AILI_ALLOW_CROSS_ENV": "yes"},
        "environment_provenance": {"HOME": str(run_root / "home"), "XDG_CONFIG_HOME": str(run_root / "home" / ".config"), "XDG_DATA_HOME": str(run_root / "home" / ".local" / "share"), "XDG_CACHE_HOME": str(run_root / "home" / ".cache"), "TMPDIR": str(run_root / "tmp")},
        "manifest_agent_paths": [entry["path"] for entry in json.loads(manifest_path.read_text(encoding="utf-8"))["components"]["agents"]],
        "canonical_agent_paths": list(P6_AGENT_FILES), "aili_home": str(project), "opencode_home": str(opencode_home),
        "canonical_agent_names": expected_names, "installed_agent_names": installed_names, "agents": agents,
        "no_additional_override_layer": True, "isolated_config_entries": config_entries,
        "managed_subagents_restricted": len([agent for agent in agents if agent["name"] != "rose"]) == 19,
        "rose_distinction": next(agent for agent in agents if agent["name"] == "rose"), "builtins_inferred": False, "uv006_resolved": False,
    }


def validate_managed_collectors(state: dict[str, Any]) -> int:
    ids = ["a33-runtime-effective-profile-observed", "a33-runtime-install-observed"]
    records = [record for record in state.get("collector_records", []) if isinstance(record, dict) and record.get("scenario_id") in set(ids)]
    if [record.get("scenario_id") for record in records] != ids:
        return 5
    project, run_root = Path(state.get("project", "")), Path(state.get("run_root", ""))
    script, opencode_home = project / "scripts" / "install_opencode.sh", run_root / "opencode-home"
    command = ["/bin/bash", str(script), "--mode", "copy", "--aili-home", str(project), "--opencode-home", str(opencode_home), "--no-update"]
    attempt = state.get("managed_install_attempt")
    controls = {"OPENCODE_ALLOW_CUSTOM_HOME": "yes", "AILI_ALLOW_CROSS_ENV": "yes"}
    provenance = {"HOME": str(run_root / "home"), "XDG_CONFIG_HOME": str(run_root / "home" / ".config"), "XDG_DATA_HOME": str(run_root / "home" / ".local" / "share"), "XDG_CACHE_HOME": str(run_root / "home" / ".cache"), "TMPDIR": str(run_root / "tmp")}
    if not exact_keys(attempt, ["command", "script", "opencode_home", "environment_controls", "environment_provenance", "status", "exit_code"]) or attempt["command"] != command \
            or attempt["script"] != str(script) or attempt["opencode_home"] != str(opencode_home) \
            or attempt["environment_controls"] != controls or attempt["environment_provenance"] != provenance:
        return 5
    if state.get("git_environment", {}).get("OPENCODE_ALLOW_CUSTOM_HOME") != "yes" or state.get("git_environment", {}).get("AILI_ALLOW_CROSS_ENV") != "yes":
        return 5
    if any(not _inside(Path(value), run_root) for value in [*provenance.values(), str(opencode_home)]):
        return 5
    created = [str(opencode_home), str(run_root / "home" / ".agents" / "skills")]
    created = [path for path in created if Path(path).exists() or Path(path).is_symlink()]
    if state.get("collector_install_paths") != created:
        return 5
    try:
        managed_agent_sources(project)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError):
        return 5
    script_available = canonical_copy_installer(project) == script
    if not script_available or not opencode_home.exists():
        return 3 if attempt["status"] == "unavailable" and all(record["status"] == "Unverified" and record["exit_code"] == 3 and record.get("before_state") == attempt for record in records) else 5
    if attempt["status"] == "unavailable":
        if not all(record["status"] == "Unverified" and record["exit_code"] == 3 and record.get("before_state") == attempt for record in records):
            return 5
        synthetic_summary = {"mode": "copy", "runtime": "linux", "aili_home": str(project), "opencode_home": str(opencode_home), "dry_run": "false", "no_update": "true"}
        try:
            observe_managed_profile(state, synthetic_summary)
        except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError):
            return 5
        return 3
    if attempt["status"] != "completed" or attempt["exit_code"] != 0:
        return 5
    pass_records = all(record["status"] == "pass" and record["exit_code"] == 0 and isinstance(record.get("before_state"), dict) for record in records)
    if not pass_records:
        return 5
    summary = records[0]["before_state"].get("installer_summary")
    try:
        observation = observe_managed_profile(state, summary)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError):
        return 5
    return 0 if all(record["before_state"] == observation for record in records) else 5


def classify_a33_approval(approval: Any, state: dict[str, Any], operation: dict[str, Any], used: set[str], registered: list[str] | None = None, destination_present: bool | None = None) -> tuple[str, str | None]:
    if not exact_keys(approval, A33_APPROVAL_FIELDS):
        return "schema_omission", None
    exact = ["operation_id", "kind", "operation_class", "source", "destination", "repo_key", "worktree_key", "branch", "base_ref", "branch_mode", "reflog_policy"]
    if approval["status"] == "missing":
        valid = approval["run_id"] == state["run_id"] and all(approval[name] == operation[name] for name in exact) and all(approval[name] is None for name in ["approval_id", "expiry", "decision_ref", "trusted_code_risk"])
        return ("missing" if valid else "schema_omission"), None
    consumed = state.get("consumed_approvals", {}).get(approval.get("approval_id")) if isinstance(state.get("consumed_approvals"), dict) else None
    if approval.get("approval_id") in used:
        if not exact_keys(consumed, ["approval", "snapshot"]) or consumed["approval"] != approval:
            return "schema_omission", None
        if exact_consumed_add_for_remove(approval, consumed, state, operation):
            return "reused", "reused-add-for-remove"
    if approval["operation_id"] != operation["operation_id"]:
        return "wrong_operation", "wrong-operation-id"
    if approval["kind"] != operation["kind"] or approval["run_id"] != state["run_id"]:
        return "wrong_operation", "wrong-operation-kind"
    for field, category in [("source", "wrong_source"), ("destination", "wrong_destination")]:
        if approval[field] != operation[field]:
            return category, None
    if approval["branch"] != operation["branch"] or approval["branch_mode"] != operation["branch_mode"]:
        return "wrong_branch", None
    if approval["base_ref"] != operation["base_ref"] or approval["reflog_policy"] != operation["reflog_policy"]:
        return "wrong_base_ref", None
    if not _valid_key(approval["repo_key"]) or approval["repo_key"] != operation["repo_key"]:
        return "repo_key_mismatch", None
    if not _valid_key(approval["worktree_key"]) or approval["worktree_key"] != operation["worktree_key"] or Path(state["host"], ".worktrees", approval["repo_key"], approval["worktree_key"]) != Path(approval["destination"]):
        return "worktree_key_mismatch", None
    if operation["operation_class"] == "driver_fixture" and approval["operation_class"] == "real":
        return "real_for_fixture", None
    if approval["operation_class"] != operation["operation_class"]:
        return "operation_class_mismatch", None
    if approval["status"] in {"declined", "unavailable"}:
        return approval["status"], None
    if approval["status"] == "stale":
        snapshot = state.get("approval_snapshots", {}).get(approval.get("approval_id")) if isinstance(state.get("approval_snapshots"), dict) else None
        if not valid_a33_approval_snapshot(snapshot, approval, state, operation):
            return "schema_omission", None
        current = build_a33_operation_snapshot(state, operation, registered, destination_present)
        return ("stale_snapshot_mismatch" if snapshot["operation_snapshot"] != current else "stale_unverified"), None
    if approval["status"] == "expired":
        return "expired", None
    if not isinstance(approval["expiry"], str) or re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z", approval["expiry"]) is None:
        return "expired", None
    try:
        expiry = datetime.fromisoformat(approval["expiry"].replace("Z", "+00:00")).astimezone(timezone.utc)
    except ValueError:
        return "expired", None
    if expiry <= datetime.now(timezone.utc):
        return "expired", None
    if approval["approval_id"] in used:
        return "reused", None
    if approval["status"] == "mismatched":
        return "mismatched", None
    if approval["status"] != "valid" or not isinstance(approval["approval_id"], str) or not approval["approval_id"] or not isinstance(approval["decision_ref"], str) or not approval["decision_ref"]:
        return "schema_omission", None
    if operation["kind"] == "add" and approval["trusted_code_risk"] != "accepted":
        return ("add_risk_declined" if approval["trusted_code_risk"] == "declined" else "add_risk_unavailable"), None
    if operation["kind"] == "remove" and approval["trusted_code_risk"] != "not_applicable":
        return "remove_risk_invalid", None
    return "valid", None


def parse_a33_porcelain_v2(records: Any) -> dict[str, list[str]] | None:
    if not isinstance(records, list) or any(not isinstance(record, str) for record in records):
        return None
    values = {"tracked_modified": [], "tracked_deleted": [], "untracked": [], "ignored": []}
    index = 0
    while index < len(records):
        record = records[index]
        if record.startswith("? "):
            values["untracked"].append(record[2:])
        elif record.startswith("! "):
            values["ignored"].append(record[2:])
        elif record.startswith(("1 ", "2 ", "u ")):
            fields = record.split(" ")
            xy = fields[1] if len(fields) > 1 else ""
            path_index = 8 if record.startswith("1 ") else 9 if record.startswith("2 ") else 10
            path = " ".join(fields[path_index:])
            if not path:
                return None
            values["tracked_deleted" if "D" in xy else "tracked_modified"].append(path)
            if record.startswith("2 "):
                index += 1
                if index >= len(records) or not isinstance(records[index], str):
                    return None
        else:
            return None
        index += 1
    for name in values:
        values[name] = sorted(set(values[name]))
    return values


def parse_a33_worktree_porcelain(records: Any) -> list[dict[str, Any]] | None:
    if not isinstance(records, list) or any(not isinstance(record, str) for record in records):
        return None
    parsed: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    for field in records:
        if field.startswith("worktree "):
            path = field[9:]
            if not path:
                return None
            current = {"path": path, "locked": False, "prunable": False, "fields": []}
            parsed.append(current)
        else:
            if current is None:
                return None
            current["fields"].append(field)
            if field == "locked" or field.startswith("locked "):
                current["locked"] = True
            if field == "prunable" or field.startswith("prunable "):
                current["prunable"] = True
    return parsed


def _relative_string_list(value: Any) -> bool:
    return isinstance(value, list) and value == sorted(set(value)) and all(isinstance(item, str) and item and not item.startswith("/") and ".." not in item.split("/") for item in value)


def derive_a33_removal_inventory(raw: Any, attempt: dict[str, Any], operation: dict[str, Any]) -> dict[str, Any] | None:
    if not exact_keys(raw, A33_RAW_INVENTORY_FIELDS) or raw["schema_version"] != A33_INTERNAL_EVIDENCE_VERSION or not isinstance(raw["target_present"], bool):
        return None
    if any(not _relative_string_list(raw[name]) for name in ["tracked_files", "artifact_files", "unknown_files", "visible_files", "allowlisted_ephemeral_artifacts"]):
        return None
    status = parse_a33_porcelain_v2(raw["status_porcelain_v2"])
    worktrees = parse_a33_worktree_porcelain(raw["worktree_porcelain"])
    if status is None or worktrees is None:
        return None
    target = attempt.get("target_before")
    source = attempt.get("source_identity")
    if not valid_identity(target) or not valid_identity(source):
        return None
    expected_strings = [raw["expected_source"], raw["expected_path"], raw["observed_path"], raw["expected_membership"], raw["observed_membership"]]
    if any(not isinstance(value, str) or not value for value in expected_strings) or raw["observed_source"] is not None and (not isinstance(raw["observed_source"], str) or not raw["observed_source"]):
        return None
    if raw["expected_source"] != source["git_common_dir"] or raw["expected_path"] != operation["destination"] or raw["observed_path"] != target["declared_root"] or raw["expected_membership"] != "linked" or raw["observed_membership"] != target["worktree_membership"] or raw["observed_source"] != target["git_common_dir"]:
        return None
    if raw["target_present"] != (target["identity_state"] == "populated"):
        return None
    target_worktrees = [record for record in worktrees if Path(record["path"]) == Path(operation["destination"])]
    if len(target_worktrees) != (1 if raw["target_present"] else 0):
        return None
    if not raw["target_present"]:
        if any(raw[name] for name in ["status_porcelain_v2", "tracked_files", "artifact_files", "unknown_files", "visible_files", "allowlisted_ephemeral_artifacts"]):
            return None
        return {"clean": False, "classes": ["missing"], "primary_class": "missing", "evidence_by_class": {}, "contradiction": False}
    if raw["tracked_files"] != target["tracked_files"] or status["untracked"] != target["untracked_files"] or status["ignored"] != target["ignored_files"] or raw["artifact_files"] != target["artifact_files"] or raw["unknown_files"] != target["unknown_files"]:
        return None
    if bool(status["tracked_modified"]) != target["dirty_state"]["tracked_modified"] or bool(status["tracked_deleted"]) != target["dirty_state"]["tracked_deleted"]:
        return None
    typed = [raw["tracked_files"], status["untracked"], status["ignored"], raw["artifact_files"], raw["unknown_files"]]
    assigned: set[str] = set()
    contradiction = False
    for paths in typed:
        for path in paths:
            if path in assigned:
                contradiction = True
            assigned.add(path)
    allowlisted = set(raw["allowlisted_ephemeral_artifacts"])
    user_visible = sorted(path for path in raw["visible_files"] if path not in assigned and path not in allowlisted)
    classes: list[str] = []
    if status["tracked_modified"]:
        classes.append("tracked_modified")
    if status["tracked_deleted"]:
        classes.append("tracked_deleted")
    evidence = {"untracked": status["untracked"], "ignored": status["ignored"], "artifact": raw["artifact_files"], "unknown": raw["unknown_files"]}
    for name in ["untracked", "ignored", "artifact", "unknown"]:
        if evidence[name]:
            classes.append(name)
    if target_worktrees[0]["locked"]:
        classes.append("locked")
    if raw["observed_source"] != raw["expected_source"]:
        classes.append("wrong_source")
    if raw["observed_path"] != raw["expected_path"]:
        classes.append("wrong_path")
    if raw["observed_membership"] != raw["expected_membership"]:
        classes.append("wrong_membership")
    evidence["user_visible"] = user_visible
    if user_visible:
        classes.append("user_visible")
    return {"clean": not classes and not contradiction, "classes": classes, "primary_class": classes[0] if classes else "clean", "evidence_by_class": evidence, "contradiction": contradiction}


def validate_a33_removal_inventory(inventory: Any, attempt: dict[str, Any], operation: dict[str, Any]) -> bool:
    derived = derive_a33_removal_inventory(attempt.get("raw_inventory_observation"), attempt, operation)
    return derived is not None and exact_keys(inventory, ["clean", "classes", "primary_class", "evidence_by_class", "contradiction"]) and inventory == derived


def _unchanged_evidence(record: dict[str, Any]) -> bool:
    if record.get("before_state") is not None or record.get("after_state") is not None:
        return record.get("before_state") == record.get("after_state")
    return valid_delta(record.get("expected_delta")) and record["expected_delta"] == record.get("observed_delta") and all(record["observed_delta"][name]["change"] == "unchanged" for name in A33_DELTA_FIELDS)


def derive_a33_delta(before: Any, after: Any) -> dict[str, Any] | None:
    if not exact_keys(before, A33_DELTA_FIELDS) or not exact_keys(after, A33_DELTA_FIELDS):
        return None
    derived: dict[str, Any] = {}
    for name in A33_DELTA_FIELDS:
        left, right = before[name], after[name]
        if name in {"branch_ref", "branch_reflog"}:
            if not exact_keys(left, ["path", "value"]) or not exact_keys(right, ["path", "value"]):
                return None
            left, right = left["value"], right["value"]
        if left == right:
            change = "unchanged"
        elif right is None or right == "absent":
            change = "deleted"
        elif left is None or left == "absent":
            change = "created"
        else:
            return None
        derived[name] = {"before": left, "after": right, "change": change}
    return derived if valid_delta(derived) else None


def _validate_raw_admin_snapshot(snapshot: Any, identity: dict[str, Any], source: dict[str, Any], operation: dict[str, Any]) -> bool:
    if not exact_keys(snapshot, A33_DELTA_FIELDS):
        return False
    common = source["git_common_dir"]
    if snapshot["target_path"] != identity["path_state"] or snapshot["worktree_membership"] != identity["worktree_membership"] or snapshot["common_dir_identity"] != common:
        return False
    branch_ref = snapshot["branch_ref"]
    branch_reflog = snapshot["branch_reflog"]
    if not exact_keys(branch_ref, ["path", "value"]) or not exact_keys(branch_reflog, ["path", "value"]):
        return False
    if not isinstance(branch_ref["path"], str) or not isinstance(branch_reflog["path"], str):
        return False
    if Path(branch_ref["path"]) != Path(common, "refs", "heads", operation["branch"]) or Path(branch_reflog["path"]) != Path(common, "logs", "refs", "heads", operation["branch"]):
        return False
    admin = snapshot["common_dir_admin_entry"]
    if admin is not None:
        if not exact_keys(admin, ["path", "entries"]) or not isinstance(admin["path"], str) or not isinstance(admin["entries"], list):
            return False
        expected_name = Path(identity["git_private_dir"]).name if identity["identity_state"] == "populated" else Path(operation["destination"]).name
        if Path(admin["path"]) != Path(common, "worktrees", expected_name):
            return False
    list_fields = ["unrelated_common_dir_entries", "unrelated_refs", "hooks", "unrelated_worktree_records", "unrelated_prunable_entries"]
    if any(not isinstance(snapshot[name], list) for name in list_fields) or not isinstance(snapshot["config"], str):
        return False
    if snapshot["unrelated_prunable_entries"] != snapshot["unrelated_worktree_records"]:
        return False
    return snapshot["other_files"] is None


def _validate_operation_delta(operation: dict[str, Any], attempt: dict[str, Any]) -> bool:
    result = attempt["result"]
    raw_before, raw_after = attempt.get("raw_admin_before"), attempt.get("raw_admin_after")
    if not _validate_raw_admin_snapshot(raw_before, attempt["target_before"], attempt["source_identity"], operation) or not _validate_raw_admin_snapshot(raw_after, attempt["target_after"], attempt["source_identity"], operation):
        return False
    derived = derive_a33_delta(raw_before, raw_after)
    if derived is None or result["command"] != f"runtime-{operation['kind']}" or result["expected_delta"] != derived or result["observed_delta"] != derived:
        return False
    if attempt["host_identity"]["identity_state"] != "populated" or attempt["source_identity"]["identity_state"] != "populated":
        return False
    delta = result["observed_delta"]
    ref_before, ref_after = raw_before["branch_ref"]["value"], raw_after["branch_ref"]["value"]
    reflog_before, reflog_after = raw_before["branch_reflog"]["value"], raw_after["branch_reflog"]["value"]
    if operation["kind"] == "add":
        if result["effect_started"] is not True:
            return False
        if attempt["target_before"]["identity_state"] != "absent" or attempt["target_after"]["identity_state"] != "populated":
            return False
        if attempt["target_after"]["worktree_membership"] != "linked" or attempt["target_after"]["git_common_dir"] != attempt["source_identity"]["git_common_dir"]:
            return False
        expected_changes = {"target_path": "created", "worktree_membership": "created", "common_dir_admin_entry": "created"}
        if operation["branch_mode"] == "create":
            if ref_before is not None or ref_after is None:
                return False
            expected_changes["branch_ref"] = "created"
            if operation["reflog_policy"] == "enabled":
                if reflog_before is not None or reflog_after is None:
                    return False
                expected_changes["branch_reflog"] = "created"
            elif reflog_before is not None or reflog_after is not None:
                return False
        elif ref_before != ref_after or reflog_before != reflog_after:
            return False
    else:
        if result["effect_started"] is not True:
            return False
        if attempt["target_before"]["identity_state"] != "populated" or attempt["target_after"]["identity_state"] != "absent":
            return False
        if attempt["target_before"]["worktree_membership"] != "linked" or attempt["target_before"]["git_common_dir"] != attempt["source_identity"]["git_common_dir"]:
            return False
        if ref_before != ref_after or reflog_before != reflog_after:
            return False
        expected_changes = {"target_path": "deleted", "worktree_membership": "deleted", "common_dir_admin_entry": "deleted"}
    if operation["kind"] == "add" and (raw_before["common_dir_admin_entry"] is not None or raw_after["common_dir_admin_entry"] is None):
        return False
    if operation["kind"] == "remove" and (raw_before["common_dir_admin_entry"] is None or raw_after["common_dir_admin_entry"] is not None):
        return False
    for name in A33_DELTA_FIELDS:
        if delta[name]["change"] != expected_changes.get(name, "unchanged"):
            return False
    return delta["common_dir_identity"]["change"] == "unchanged"


def _expected_operation_coverage(metadata: dict[str, Any], operations: list[dict[str, Any]]) -> list[tuple[str, str, str]]:
    if metadata["id"] == "a33-runtime-approval-declined-unavailable":
        selected = [operation for operation in operations if operation["kind"] == "add" and _operation_selector(operation) == "existing"] * 2
    elif metadata["id"] == "a33-runtime-key-mismatch-zero-effect":
        selected = [operation for operation in operations if _operation_selector(operation) == "existing" for _ in range(2)]
    elif metadata["operation_kind"] is not None:
        selected = [operation for operation in operations if operation["kind"] == metadata["operation_kind"]]
    elif metadata["id"] in {"a33-unrelated-common-dir-preserved", "a33-runtime-identity-transition-schema", "a33-common-dir-identity-change-block"}:
        selected = list(operations)
    else:
        return []
    if metadata["attachment_selector"] != "all-attachments" and metadata["id"] not in {"a33-runtime-approval-declined-unavailable", "a33-runtime-key-mismatch-zero-effect"}:
        selected = [operation for operation in selected if _operation_selector(operation) == metadata["attachment_selector"]]
    return sorted([(operation["operation_id"], operation["kind"], _operation_selector(operation)) for operation in selected])


def validate_a33_evidence_bindings(metadata: dict[str, Any], record: Any, operations: list[dict[str, Any]], attempts: list[dict[str, Any]]) -> int:
    bindings = record.get("operation_bindings") if isinstance(record, dict) else None
    if not isinstance(bindings, list) or len({binding.get("attempt_id") for binding in bindings if isinstance(binding, dict)}) != len(bindings):
        return 5
    attempt_index: dict[str, list[dict[str, Any]]] = {}
    for attempt in attempts:
        attempt_index.setdefault(attempt.get("evidence_id"), []).append(attempt)
    actual = []
    for binding in bindings:
        if not exact_keys(binding, ["attempt_id", "operation_id", "operation_kind", "attachment_selector"]):
            return 5
        candidates = attempt_index.get(binding["attempt_id"], [])
        if len(candidates) != 1:
            return 5
        attempt = candidates[0]
        if (attempt.get("operation_id"), attempt.get("operation_kind"), attempt.get("attachment_selector")) != (binding["operation_id"], binding["operation_kind"], binding["attachment_selector"]):
            return 5
        if not any(operation["operation_id"] == binding["operation_id"] and operation["kind"] == binding["operation_kind"] and _operation_selector(operation) == binding["attachment_selector"] for operation in operations):
            return 5
        actual.append((binding["operation_id"], binding["operation_kind"], binding["attachment_selector"]))
    if record.get("operation_id") is not None and (len(bindings) != 1 or bindings[0]["operation_id"] != record["operation_id"]):
        return 5
    return 0 if sorted(actual) == _expected_operation_coverage(metadata, operations) else 5


def validate_a33_semantic_mutation(observation: Any) -> int:
    if not exact_keys(observation, ["kind", "expected", "observed"]):
        return 5
    kind, expected, observed = observation["kind"], observation["expected"], observation["observed"]
    if kind in {"delta", "ref", "reflog"}:
        if not valid_delta(expected) or not valid_delta(observed):
            return 5
        return 5 if expected != observed else 3
    if kind in {"delta-set", "ref-set", "reflog-set"}:
        valid = isinstance(expected, list) and isinstance(observed, list) and len(expected) == len(observed) > 0 and all(valid_delta(value) for value in expected + observed)
        if not valid:
            return 5
        return 5 if all(left != right for left, right in zip(expected, observed, strict=True)) else 3
    if kind == "identity":
        if not valid_identity(expected) or not valid_identity(observed):
            return 5
        return 5 if expected != observed else 3
    if kind in {"cleanup", "effect", "inventory"}:
        return 5 if expected != observed else 3
    return 3


def load_a33_runtime_state(runtime_path: Path, runtime: dict[str, Any], project: Path,
                           fixture_path: Path) -> tuple[dict[str, Any] | None, list[str]]:
    errors: list[str] = []
    run_root = runtime_path.parent.resolve()
    temp_root = Path(tempfile.gettempdir()).resolve()
    if run_root.parent != temp_root or re.fullmatch(r"aili-a33-runtime-[A-Za-z0-9]{6}", run_root.name) is None or run_root == project or _inside(run_root, project):
        errors.append("runtime result is not inside the external driver-owned temporary root")
    marker = run_root / ".aili-a33-driver-owned"
    state_path = run_root / "state.json"
    if marker.is_symlink() or state_path.is_symlink():
        return None, errors + ["driver-owned marker or state path is a symlink"]
    try:
        state = json.loads(state_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None, errors + ["missing or malformed sibling state.json"]
    if not isinstance(state, dict):
        return None, errors + ["runtime state must be an object"]
    expected_state_fields = ["schema_version", "run_id", "run_root", "project", "fixture", "fixture_sha256", "cleanup_nonce", "host", "operations", "attempts", "attempt_sequence", "used_approvals", "approval_snapshots", "consumed_approvals", "registered", "worktree_effects", "internal_evidence_version", "collector_records", "managed_install_attempt", "collector_install_paths", "git_environment", "current_operation_snapshots", "join_evidence_records", "join_case_bindings"]
    if list(state) != expected_state_fields:
        errors.append("runtime state field schema mismatch")
    run_id = runtime.get("run_id")
    if not isinstance(run_id, str) or not run_id or state.get("run_id") != run_id or run_root.name != run_id or state.get("run_root") != str(run_root):
        errors.append("runtime run/root identity mismatch")
    try:
        marker_value = json.loads(marker.read_text(encoding="utf-8"))
        expected_marker = {"schema_version": A33_INTERNAL_EVIDENCE_VERSION, "run_root": str(run_root), "run_id": run_id, "cleanup_nonce": state.get("cleanup_nonce")}
        if not exact_keys(marker_value, A33_MARKER_FIELDS) or marker_value != expected_marker:
            errors.append("driver-owned marker identity mismatch")
    except (OSError, json.JSONDecodeError):
        errors.append("driver-owned marker missing")
    fixture_text = fixture_path.read_bytes()
    if state.get("schema_version") != A33_SCHEMA or state.get("internal_evidence_version") != A33_INTERNAL_EVIDENCE_VERSION:
        errors.append("runtime internal evidence version mismatch")
    if not isinstance(state.get("cleanup_nonce"), str) or re.fullmatch(r"[0-9a-f]{64}", state["cleanup_nonce"]) is None:
        errors.append("runtime cleanup nonce malformed")
    if state.get("project") != str(project) or state.get("fixture") != str(fixture_path) or state.get("fixture_sha256") != hashlib.sha256(fixture_text).hexdigest():
        errors.append("runtime project/fixture identity mismatch")
    if runtime.get("ephemeral_result") != str(runtime_path):
        errors.append("runtime result path identity mismatch")
    host = run_root / "host"
    if state.get("host") != str(host):
        errors.append("runtime host identity mismatch")
    expected_env = {
        "HOME": str(run_root / "home"), "XDG_CONFIG_HOME": str(run_root / "home" / ".config"),
        "XDG_DATA_HOME": str(run_root / "home" / ".local" / "share"), "XDG_CACHE_HOME": str(run_root / "home" / ".cache"),
        "TMPDIR": str(run_root / "tmp"), "PATH": "/usr/bin:/bin", "LANG": "C.UTF-8", "LC_ALL": "C.UTF-8",
        "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_SYSTEM": "/dev/null", "GIT_CONFIG_GLOBAL": "/dev/null",
        "GIT_CONFIG_COUNT": "1", "GIT_CONFIG_KEY_0": "core.hooksPath", "GIT_CONFIG_VALUE_0": str(run_root / "empty-hooks"),
        "GIT_AUTHOR_NAME": "A33 Probe", "GIT_AUTHOR_EMAIL": "probe@example.invalid",
        "GIT_COMMITTER_NAME": "A33 Probe", "GIT_COMMITTER_EMAIL": "probe@example.invalid",
        "OPENCODE_ALLOW_CUSTOM_HOME": "yes", "AILI_ALLOW_CROSS_ENV": "yes",
    }
    if state.get("git_environment") != expected_env:
        errors.append("isolated Git environment mismatch")
    for name in ["HOME", "XDG_CONFIG_HOME", "XDG_DATA_HOME", "XDG_CACHE_HOME", "TMPDIR", "GIT_CONFIG_VALUE_0"]:
        candidate = Path(expected_env[name])
        if not _inside(candidate, run_root) or not candidate.is_dir():
            errors.append(f"isolated Git environment path invalid: {name}")
    hooks = Path(expected_env["GIT_CONFIG_VALUE_0"])
    try:
        if any(hooks.iterdir()):
            errors.append("isolated hooks directory is not empty")
    except OSError:
        errors.append("isolated hooks directory unavailable")
    try:
        root_stat = run_root.lstat()
        if stat.S_ISLNK(root_stat.st_mode) or root_stat.st_uid != os.getuid() or stat.S_IMODE(root_stat.st_mode) & 0o077:
            errors.append("runtime root ownership or mode is unsafe")
    except OSError:
        errors.append("runtime root metadata unavailable")
    cleanup_security_exit, _, cleanup_security_errors = capture_a33_cleanup_security(state, run_root)
    if cleanup_security_exit != 0:
        errors.extend(cleanup_security_errors)
    return state, errors


def _valid_operation_result(result: Any, state: dict[str, Any]) -> bool:
    return exact_keys(result, A33_OPERATION_RESULT_FIELDS) and result["schema_version"] == A33_SCHEMA \
        and result["command"] in {"runtime-add", "runtime-remove"} and result["status"] in {"pass", "blocked", "Unverified", "fail"} \
        and result["exit_code"] in {0, 3, 5} and validate_a33_operation(result["operation"], state) \
        and exact_keys(result["approval"], A33_APPROVAL_FIELDS) and isinstance(result["effect_started"], bool) \
        and (result["expected_delta"] is None or valid_delta(result["expected_delta"])) \
        and (result["observed_delta"] is None or valid_delta(result["observed_delta"])) \
        and isinstance(result["evidence_refs"], list) and bool(result["evidence_refs"]) \
        and all(isinstance(value, str) and value for value in result["evidence_refs"]) and isinstance(result["unverified"], list)


def replay_a33_attempt_sequence(attempts: Any, operations: Any) -> tuple[int, list[str], dict[str, int]]:
    if not isinstance(attempts, list) or not isinstance(operations, list):
        return 5, [], {"adds": 0, "removes": 0}
    operation_index = {operation.get("operation_id"): operation for operation in operations if isinstance(operation, dict)}
    registered: list[str] = []
    successful: set[str] = set()
    effects = {"adds": 0, "removes": 0}
    for attempt in attempts:
        if not isinstance(attempt, dict) or not isinstance(attempt.get("result"), dict):
            return 5, registered, effects
        result = attempt["result"]
        if result.get("status") != "pass" or result.get("exit_code") != 0:
            continue
        operation = operation_index.get(attempt.get("operation_id"))
        if operation is None or operation["operation_id"] in successful or operation.get("destination") != result.get("operation", {}).get("destination"):
            return 5, registered, effects
        destination = operation["destination"]
        if operation["kind"] == "add":
            if destination in registered:
                return 5, registered, effects
            registered.append(destination)
            effects["adds"] += 1
        elif operation["kind"] == "remove":
            matching_add = next((candidate for candidate in operations if candidate.get("kind") == "add" and candidate.get("destination") == destination), None)
            if matching_add is None or matching_add.get("operation_id") not in successful or destination not in registered:
                return 5, registered, effects
            registered.remove(destination)
            effects["removes"] += 1
        else:
            return 5, registered, effects
        successful.add(operation["operation_id"])
    return 0, registered, effects


def _validate_attempts(state: dict[str, Any]) -> tuple[int, dict[str, dict[str, Any]]]:
    operations = state.get("operations")
    attempts = state.get("attempts")
    if not isinstance(operations, list) or not isinstance(attempts, list) or len(operations) != 6:
        return 5, {}
    operation_index: dict[str, dict[str, Any]] = {}
    for operation in operations:
        if not validate_a33_operation(operation, state) or operation["operation_id"] in operation_index:
            return 5, {}
        operation_index[operation["operation_id"]] = operation
    attempt_index: dict[str, dict[str, Any]] = {}
    used: set[str] = set()
    successful_approvals: list[str] = []
    expected_consumed: dict[str, dict[str, Any]] = {}
    latest_snapshots: dict[str, dict[str, Any]] = {}
    required = {"evidence_id", "sequence", "category", "reason", "scenario_ids", "operation_kind", "operation_id", "attachment_selector", "approval_variant", "result", "host_identity", "source_identity", "target_before", "target_after", "raw_admin_before", "raw_admin_after", "raw_inventory_observation", "evidence_records"}
    if state.get("attempt_sequence") != [attempt.get("evidence_id") for attempt in attempts if isinstance(attempt, dict)]:
        return 5, {}
    replay_registered: list[str] = []
    successful_operation_ids: set[str] = set()
    for index, attempt in enumerate(attempts, 1):
        if not isinstance(attempt, dict) or (set(attempt) != required and set(attempt) != required | {"inventory"}):
            return 5, {}
        evidence_id = attempt["evidence_id"]
        if evidence_id != f"attempt:{index}" or attempt["sequence"] != index or evidence_id in attempt_index:
            return 5, {}
        if not isinstance(attempt["category"], str) or not attempt["category"] or not isinstance(attempt["reason"], str) or not attempt["reason"]:
            return 5, {}
        result = attempt["result"]
        if not _valid_operation_result(result, state):
            return 5, {}
        operation = operation_index.get(attempt["operation_id"])
        if operation is None or result["operation"] != operation or attempt["operation_kind"] != operation["kind"] or attempt["attachment_selector"] != _operation_selector(operation):
            return 5, {}
        if any(not valid_identity(attempt[name]) for name in ["host_identity", "source_identity", "target_before", "target_after"]):
            return 5, {}
        if attempt["host_identity"]["declared_root"] != state["host"] or attempt["source_identity"]["declared_root"] != operation["source"] or attempt["target_before"]["declared_root"] != operation["destination"] or attempt["target_after"]["declared_root"] != operation["destination"]:
            return 5, {}
        operation_snapshot = build_a33_operation_snapshot(
            state, operation, replay_registered, attempt["target_before"]["identity_state"] == "populated"
        )
        latest_snapshots[operation["operation_id"]] = operation_snapshot
        category, variant = classify_a33_approval(
            result["approval"], state, operation, used, replay_registered,
            attempt["target_before"]["identity_state"] == "populated",
        )
        if category not in A33_APPROVAL_TAXONOMY:
            return 5, {}
        expected_category = attempt["category"]
        if expected_category.startswith("inventory_") or expected_category in {"valid", "git_add_failed", "git_remove_failed", "destination_collision"}:
            if category != "valid":
                return 5, {}
        elif category != expected_category or (variant is not None and attempt["approval_variant"] not in {category, variant}):
            return 5, {}
        if result["status"] == "pass" and result["exit_code"] == 0:
            approval_id = result["approval"]["approval_id"]
            if approval_id in used or category != "valid" or not _validate_operation_delta(operation, attempt):
                return 5, {}
            if operation["operation_id"] in successful_operation_ids:
                return 5, {}
            if operation["kind"] == "add":
                if operation["destination"] in replay_registered:
                    return 5, {}
                replay_registered.append(operation["destination"])
            else:
                matching_add = next((candidate for candidate in operations if candidate["kind"] == "add" and candidate["destination"] == operation["destination"]), None)
                if matching_add is None or matching_add["operation_id"] not in successful_operation_ids or operation["destination"] not in replay_registered:
                    return 5, {}
                replay_registered.remove(operation["destination"])
            successful_operation_ids.add(operation["operation_id"])
            used.add(approval_id)
            successful_approvals.append(approval_id)
            expected_consumed[approval_id] = {"approval": result["approval"], "snapshot": operation_snapshot}
        elif result["status"] == "blocked":
            if result["exit_code"] != 3 or result["effect_started"] is not False or not _unchanged_evidence(result) or attempt["target_before"] != attempt["target_after"]:
                return 5, {}
            raw_before, raw_after = attempt["raw_admin_before"], attempt["raw_admin_after"]
            derived = derive_a33_delta(raw_before, raw_after)
            if not _validate_raw_admin_snapshot(raw_before, attempt["target_before"], attempt["source_identity"], operation) or not _validate_raw_admin_snapshot(raw_after, attempt["target_after"], attempt["source_identity"], operation) or derived is None or result["expected_delta"] != derived or result["observed_delta"] != derived or any(derived[name]["change"] != "unchanged" for name in A33_DELTA_FIELDS):
                return 5, {}
        elif result["exit_code"] != 5:
            return 5, {}
        if operation["kind"] == "remove":
            derived_inventory = derive_a33_removal_inventory(attempt.get("raw_inventory_observation"), attempt, operation)
            if derived_inventory is None:
                return 5, {}
        elif attempt.get("raw_inventory_observation") is not None:
            return 5, {}
        if "inventory" in attempt and not validate_a33_removal_inventory(attempt["inventory"], attempt, operation):
            return 5, {}
        if not isinstance(attempt["scenario_ids"], list) or not isinstance(attempt["evidence_records"], list) or attempt["scenario_ids"] != [record.get("scenario_id") for record in attempt["evidence_records"] if isinstance(record, dict)]:
            return 5, {}
        if any(record.get("source") != "operation" or record.get("evidence_id") != f"{evidence_id}:{record.get('scenario_id')}" for record in attempt["evidence_records"] if isinstance(record, dict)):
            return 5, {}
        attempt_index[evidence_id] = attempt
    if state.get("used_approvals") != successful_approvals or len(successful_approvals) != len(set(successful_approvals)):
        return 5, {}
    if state.get("consumed_approvals") != expected_consumed or state.get("current_operation_snapshots") != latest_snapshots:
        return 5, {}
    approval_snapshots = state.get("approval_snapshots")
    if not isinstance(approval_snapshots, dict):
        return 5, {}
    for approval_id, record in approval_snapshots.items():
        if not isinstance(approval_id, str) or not approval_id or not exact_keys(record, ["approval_binding", "operation_snapshot"]):
            return 5, {}
        operation = operation_index.get(record["approval_binding"].get("operation_id") if isinstance(record.get("approval_binding"), dict) else None)
        synthetic_values = {**record.get("approval_binding", {}), "approval_id": approval_id, "expiry": None, "decision_ref": None, "trusted_code_risk": None, "status": "stale"}
        synthetic = {name: synthetic_values.get(name) for name in A33_APPROVAL_FIELDS}
        if operation is None or not exact_keys(synthetic, A33_APPROVAL_FIELDS) or not valid_a33_approval_snapshot(record, synthetic, state, operation):
            return 5, {}
    for approval_id, consumed in expected_consumed.items():
        if approval_snapshots.get(approval_id) != {"approval_binding": a33_approval_binding(consumed["approval"]), "operation_snapshot": consumed["snapshot"]}:
            return 5, {}
    successful_operations = [attempt["operation_id"] for attempt in attempts if attempt["result"]["status"] == "pass" and attempt["result"]["exit_code"] == 0]
    if len(successful_operations) != len(set(successful_operations)):
        return 5, {}
    if not exact_keys(state.get("worktree_effects"), ["adds", "removes"]):
        return 5, {}
    observed_effects = {kind: sum(1 for attempt in attempts if attempt["result"]["status"] == "pass" and attempt["operation_kind"] == kind) for kind in ["add", "remove"]}
    if state["worktree_effects"] != {"adds": observed_effects["add"], "removes": observed_effects["remove"]}:
        return 5, {}
    if state.get("registered") != replay_registered:
        return 5, {}
    replay_exit, replay_final, replay_effects = replay_a33_attempt_sequence(attempts, operations)
    if replay_exit == 5 or replay_final != state["registered"] or replay_effects != state["worktree_effects"]:
        return 5, {}
    return 0, attempt_index


def _valid_evidence_record(record: Any, metadata: dict[str, Any]) -> bool:
    return exact_keys(record, A33_EVIDENCE_FIELDS) and record["schema_version"] == A33_INTERNAL_EVIDENCE_VERSION \
        and record["scenario_id"] == metadata["id"] and record["family"] == metadata["family"] \
        and record["operation_kind"] == metadata["operation_kind"] and record["attachment_selector"] == metadata["attachment_selector"] \
        and record["approval_variant"] == metadata["approval_variant"] and record["evidence_types"] == metadata["required_evidence_types"] \
        and record["source"] in {"collector", "operation"} and isinstance(record["evidence_id"], str) and bool(record["evidence_id"]) \
        and record["status"] in {"pass", "blocked", "Unverified", "fail"} and record["exit_code"] in {0, 3, 5} \
        and (record["effect_started"] is None or isinstance(record["effect_started"], bool)) and isinstance(record["evidence_refs"], list) and bool(record["evidence_refs"]) \
        and all(isinstance(value, str) and value for value in record["evidence_refs"]) and isinstance(record["contradiction"], bool) \
        and record["attempt"] is None and (record["expected_delta"] is None or valid_delta(record["expected_delta"])) \
        and (record["observed_delta"] is None or valid_delta(record["observed_delta"]))


def _evaluate_evidence(metadata: dict[str, Any], record: dict[str, Any], operations: list[dict[str, Any]], attempts: list[dict[str, Any]]) -> tuple[str, int, str | None]:
    if not _valid_evidence_record(record, metadata) or record["contradiction"] is True or validate_a33_evidence_bindings(metadata, record, operations, attempts) == 5:
        return "fail", 5, "wrong-bound or contradictory evidence"
    attempt_index = {attempt["evidence_id"]: attempt for attempt in attempts}
    bound_attempts = [attempt_index[binding["attempt_id"]] for binding in record["operation_bindings"]]
    if metadata["family"] in {"valid-add", "valid-remove"} or metadata["id"] in {"a33-runtime-nested-repository-observed", "a33-unrelated-common-dir-preserved", "a33-runtime-identity-transition-schema"}:
        if any(attempt["category"] != "valid" or attempt["result"]["status"] != "pass" or attempt["result"]["exit_code"] != 0 for attempt in bound_attempts):
            return "fail", 5, "positive operation binding is not a successful valid attempt"
    if metadata["family"] == "approval-key-class-risk-negative":
        expected_categories = {
            "wrong-operation-id": {"wrong_operation"}, "wrong-operation": {"wrong_operation"},
            "wrong-operation-kind": {"wrong_operation"}, "reused": {"reused"}, "reused-add-for-remove": {"reused"},
            "real-for-fixture": {"real_for_fixture"}, "operation-class-mismatch": {"operation_class_mismatch"},
            "missing": {"missing"}, "stale-snapshot-mismatch": {"stale_snapshot_mismatch"}, "mismatched": {"mismatched"},
            "expired": {"expired"}, "wrong-source": {"wrong_source"}, "wrong-destination": {"wrong_destination"},
            "wrong-branch": {"wrong_branch"}, "wrong-base-ref": {"wrong_base_ref"},
            "declined-or-unavailable": {"declined", "unavailable"}, "add-risk-declined": {"add_risk_declined"},
            "add-risk-unavailable": {"add_risk_unavailable"}, "repo-or-worktree-key-mismatch": {"repo_key_mismatch", "worktree_key_mismatch"},
        }.get(metadata["approval_variant"])
        if expected_categories is not None:
            observed_categories = {attempt["category"] for attempt in bound_attempts}
            if observed_categories != expected_categories:
                return "fail", 5, "approval taxonomy/category binding mismatch"
        if metadata["id"] == "a33-runtime-key-mismatch-zero-effect":
            expected_cells = sorted([("add", "repo_key_mismatch"), ("add", "worktree_key_mismatch"), ("remove", "repo_key_mismatch"), ("remove", "worktree_key_mismatch")])
            observed_cells = sorted((attempt["operation_kind"], attempt["category"]) for attempt in bound_attempts)
            if observed_cells != expected_cells or len({attempt["evidence_id"] for attempt in bound_attempts}) != 4:
                return "fail", 5, "exact key mismatch matrix coverage mismatch"
    if metadata["family"] == "typed-removal-inventory":
        expected_inventory = {
            "tracked-modified-or-deleted": {"inventory_tracked_modified", "inventory_tracked_deleted"},
            "unknown": {"inventory_unknown"}, "user-visible": {"inventory_user_visible"},
            "ignored": {"inventory_ignored"}, "untracked": {"inventory_untracked"},
            "artifact": {"inventory_artifact"}, "locked": {"inventory_locked"},
            "wrong-source": {"inventory_wrong_source"}, "wrong-path-or-membership": {"inventory_wrong_path", "inventory_wrong_membership"},
            "missing": {"inventory_missing"},
        }[metadata["approval_variant"]]
        if len(bound_attempts) != 1 or bound_attempts[0]["category"] not in expected_inventory:
            return "fail", 5, "typed removal inventory category mismatch"
    observation = record["semantic_observation"]
    if observation is not None:
        rejection = validate_a33_semantic_mutation(observation)
        return ("pass", 0, None) if metadata["expected_outcome"] == "fail" and rejection == 5 else ("fail", 5, "semantic mutation was not independently rejected")
    if metadata["expected_outcome"] == "blocked":
        passed = record["status"] == "blocked" and record["exit_code"] == 3 and record["effect_started"] is False and _unchanged_evidence(record)
        return ("pass", 0, None) if passed else ("fail", 5, "negative outcome/effect/unchanged-state mismatch")
    if metadata["expected_outcome"] == "pass":
        if record["status"] == "Unverified" and record["exit_code"] == 3 and record["source"] == "collector" and any(value.startswith("missing-collector:") for value in record["evidence_refs"]):
            return "Unverified", 3, "mandatory positive evidence unavailable"
        if record["status"] != "pass" or record["exit_code"] != 0:
            return "fail", 5, "positive evidence contradiction"
        if record["expected_delta"] is not None and record["expected_delta"] != record["observed_delta"]:
            return "fail", 5, "positive expected/observed delta mismatch"
        return "pass", 0, None
    if metadata["expected_outcome"] == "unverified":
        return ("pass", 0, None) if record["status"] == "Unverified" and record["exit_code"] == 3 else ("fail", 5, "partitioned Unverified outcome mismatch")
    return "fail", 5, "semantic rejection evidence missing"


def validate_a33_runtime_semantics(state: dict[str, Any], runtime: dict[str, Any], config: dict[str, Any], *, run_oracles: bool = True) -> tuple[int, list[dict[str, Any]], list[str]]:
    errors: list[str] = []
    if validate_a33_scenario_registry(config["runtime_mandatory_case_ids"]) == 5:
        return 5, [], ["Python A33 scenario registry mismatch"]
    expected_operations = []
    for index, attachment in enumerate(config["attachments"], 1):
        common = {
            "operation_class": "driver_fixture", "source": str(Path(state["run_root"]) / f"source-{index}"),
            "destination": str(Path(state["host"]) / ".worktrees" / attachment["repo_key"] / attachment["worktree_key"]),
            **attachment,
        }
        expected_operations.extend([
            {"operation_id": f"add-{index}", "kind": "add", **common},
            {"operation_id": f"remove-{index}", "kind": "remove", **common},
        ])
    if state.get("operations") != expected_operations:
        return 5, [], ["runtime operation registry does not match exact fixture attachments"]
    if not isinstance(state.get("current_operation_snapshots"), dict) or set(state["current_operation_snapshots"]) != {operation["operation_id"] for operation in expected_operations}:
        return 5, [], ["current operation snapshot registry mismatch"]
    if not isinstance(state.get("registered"), list) or len(state["registered"]) != len(set(state["registered"])) or any(path not in {operation["destination"] for operation in expected_operations} for path in state["registered"]):
        return 5, [], ["registered destination inventory mismatch"]
    attempt_exit, attempt_index = _validate_attempts(state)
    if attempt_exit == 5:
        return 5, [], ["runtime operation/attempt evidence invalid"]
    operations, attempts = state["operations"], state["attempts"]
    key_cells = sorted((attempt["operation_kind"], attempt["category"]) for attempt in attempts if attempt["category"] in {"repo_key_mismatch", "worktree_key_mismatch"})
    expected_key_cells = sorted([("add", "repo_key_mismatch"), ("add", "worktree_key_mismatch"), ("remove", "repo_key_mismatch"), ("remove", "worktree_key_mismatch")])
    if key_cells != expected_key_cells:
        return 5, [], ["exact four-cell key mismatch matrix missing, duplicated, or swapped"]
    collectors = state.get("collector_records")
    joined = state.get("join_evidence_records")
    bindings = state.get("join_case_bindings")
    if not isinstance(collectors, list) or not isinstance(joined, list) or not isinstance(bindings, list):
        return 5, [], ["runtime collector/join evidence arrays missing"]
    required_collectors = config["runtime_mandatory_case_ids"][:6]
    if [record.get("scenario_id") for record in collectors if isinstance(record, dict)] != required_collectors:
        return 5, [], ["mandatory prepare/profile/install collector inventory mismatch"]
    attempt_records = [record for attempt in attempts for record in attempt["evidence_records"]]
    records = collectors + attempt_records + joined
    if any(record.get("source") != "collector" for record in collectors + joined if isinstance(record, dict)):
        return 5, [], ["collector/join evidence source mismatch"]
    evidence_ids = [record.get("evidence_id") for record in records if isinstance(record, dict)]
    if len(evidence_ids) != len(records) or len(evidence_ids) != len(set(evidence_ids)):
        return 5, [], ["duplicate or malformed evidence id"]
    metadata_index = {row["id"]: row for row in A33_RUNTIME_SCENARIO_REGISTRY}
    for record in records:
        metadata = metadata_index.get(record.get("scenario_id")) if isinstance(record, dict) else None
        if metadata is None or not _valid_evidence_record(record, metadata):
            return 5, [], ["collector/join evidence metadata mismatch"]
    managed_collector_exit = validate_managed_collectors(state)
    if managed_collector_exit == 5:
        return 5, [], ["managed effective-profile/install collector mismatch"]
    if len(bindings) != 70 or [row.get("scenario_id") for row in bindings if isinstance(row, dict)] != config["runtime_mandatory_case_ids"]:
        return 5, [], ["join case binding order/set mismatch"]
    recomputed: list[dict[str, Any]] = []
    any_missing = managed_collector_exit == 3
    for metadata, producer_binding, public_row in zip(A33_RUNTIME_SCENARIO_REGISTRY, bindings, runtime.get("cases", []), strict=False):
        candidates = [record for record in records if record["scenario_id"] == metadata["id"]]
        if len(candidates) > 1:
            status, exit_code, reason, record = "fail", 5, "duplicate or ambiguous compatible evidence", None
        elif not candidates:
            status, exit_code, reason, record = "Unverified", 3, "mandatory compatible evidence unavailable", None
            any_missing = True
        else:
            record = candidates[0]
            status, exit_code, reason = _evaluate_evidence(metadata, record, operations, attempts)
            any_missing = any_missing or status == "Unverified"
        if not exact_keys(producer_binding, ["scenario_id", "evidence_id", "status", "exit_code", "reason"]) or producer_binding["evidence_id"] != (record["evidence_id"] if record else None) or producer_binding["status"] != status or producer_binding["exit_code"] != exit_code or producer_binding["reason"] != reason:
            status, exit_code, reason = "fail", 5, "producer join binding contradicts independent classification"
        attempt = None
        if record is not None and record["operation_id"] is not None:
            bound = record["operation_bindings"]
            attempt = attempt_index.get(bound[0]["attempt_id"]) if len(bound) == 1 else None
            if attempt is None:
                status, exit_code, reason = "fail", 5, "singular public row attempt binding unavailable"
        expected_row = {
            "id": metadata["id"], "subset": "runtime", "status": status, "exit_code": exit_code, "run_id": state["run_id"],
            "operation_id": attempt["operation_id"] if attempt else None,
            "approval_ref": attempt["result"]["approval"]["approval_id"] if attempt else None,
            "host_identity": attempt["host_identity"] if attempt else None,
            "source_identity": attempt["source_identity"] if attempt else None,
            "target_identity": (attempt["target_before"] if attempt and "target-before-identity" in metadata["required_evidence_types"] else attempt["target_after"] if attempt else None),
            "expected_delta": attempt["result"]["expected_delta"] if attempt else None,
            "observed_delta": attempt["result"]["observed_delta"] if attempt else None,
            "evidence_refs": ([record["evidence_id"], *record["evidence_refs"]] if record else [f"missing-compatible-evidence:{metadata['id']}"]),
            "unverified": (["mandatory runtime evidence unavailable"] if status in {"Unverified", "blocked"} else []),
            "cleanup_state": record["cleanup_state"] if record else None,
        }
        if public_row != expected_row:
            status, exit_code, reason = "fail", 5, "public runtime row contradicts independently recomputed evidence"
            expected_row["status"], expected_row["exit_code"] = status, exit_code
        recomputed.append({"id": metadata["id"], "status": status, "exit_code": exit_code, "reason": reason, "row": expected_row})
    if len(recomputed) != 70 or any(row["exit_code"] == 5 for row in recomputed):
        return 5, recomputed, errors
    successful = [attempt for attempt in attempts if attempt["result"]["status"] == "pass" and attempt["result"]["exit_code"] == 0]
    successful_ids = [attempt["operation_id"] for attempt in successful]
    all_operations_once = sorted(successful_ids) == sorted(operation["operation_id"] for operation in operations)
    eligible = all_operations_once and state.get("registered") == [] and state.get("worktree_effects") == {"adds": 3, "removes": 3}
    expected_cleanup = {"eligible": eligible, "attempted": False, "status": "eligible_for_global_join" if eligible else "retained_registered" if state.get("registered") else "blocked", "retained_paths": [state["run_root"]], "errors": []}
    if runtime.get("cleanup") != expected_cleanup or runtime.get("operations") != [attempt["result"] for attempt in attempts]:
        return 5, recomputed, ["runtime operations or cleanup contradict recorded state"]
    semantic_exit = 3 if any_missing or not eligible else 0
    if runtime.get("exit_code") != semantic_exit or runtime.get("status") != ("pass" if semantic_exit == 0 else "Unverified"):
        return 5, recomputed, ["producer runtime result contradicts independent semantic exit"]
    if run_oracles and validate_a33_internal_mutation_oracles(state, runtime, config) == 5:
        return 5, recomputed, ["internal semantic mutation oracle failed"]
    return semantic_exit, recomputed, errors


def validate_a33_internal_mutation_oracles(state: dict[str, Any], runtime: dict[str, Any], config: dict[str, Any]) -> int:
    if validate_a33_scenario_registry(config["runtime_mandatory_case_ids"][1:]) != 5:
        return 5
    records = state["collector_records"]
    swapped = copy.deepcopy(state)
    swapped["collector_records"][0]["scenario_id"], swapped["collector_records"][1]["scenario_id"] = swapped["collector_records"][1]["scenario_id"], swapped["collector_records"][0]["scenario_id"]
    if validate_a33_runtime_semantics(swapped, runtime, config, run_oracles=False)[0] != 5:
        return 5
    removed = copy.deepcopy(state)
    removed["collector_records"].pop(0)
    if validate_a33_runtime_semantics(removed, runtime, config, run_oracles=False)[0] != 5:
        return 5
    family = copy.deepcopy(state)
    family["collector_records"][0]["family"] = "effective-profile-install"
    if validate_a33_runtime_semantics(family, runtime, config, run_oracles=False)[0] != 5:
        return 5
    selector = copy.deepcopy(state)
    selector["collector_records"][0]["attachment_selector"] = "global"
    if validate_a33_runtime_semantics(selector, runtime, config, run_oracles=False)[0] != 5:
        return 5
    operation = copy.deepcopy(state)
    operation["operations"].append(copy.deepcopy(operation["operations"][0]))
    if validate_a33_runtime_semantics(operation, runtime, config, run_oracles=False)[0] != 5:
        return 5
    if state["attempts"]:
        duplicate_attempt = copy.deepcopy(state)
        duplicate_attempt["attempts"].append(copy.deepcopy(duplicate_attempt["attempts"][-1]))
        if validate_a33_runtime_semantics(duplicate_attempt, runtime, config, run_oracles=False)[0] != 5:
            return 5
        sequence = copy.deepcopy(state)
        sequence["attempt_sequence"] = list(reversed(sequence["attempt_sequence"]))
        if validate_a33_runtime_semantics(sequence, runtime, config, run_oracles=False)[0] != 5:
            return 5
    effect = {"kind": "effect", "expected": False, "observed": True}
    identity = {"identity_state": "absent", "declared_root": "/tmp/a33", "path_state": "absent", "canonical_root": None, "git_toplevel": None, "git_private_dir": None, "git_common_dir": None, "git_head": None, "git_branch": None, "detached_head": None, "worktree_membership": "absent", "dirty_state": None, "tracked_files": None, "untracked_files": None, "ignored_files": None, "artifact_files": None, "unknown_files": None}
    bad_identity = dict(identity); bad_identity["git_head"] = "mutated"
    if validate_a33_semantic_mutation(effect) != 5 or validate_a33_semantic_mutation({"kind": "identity", "expected": identity, "observed": bad_identity}) != 5:
        return 5
    successful = [index for index, attempt in enumerate(state["attempts"]) if attempt["result"]["status"] == "pass"]
    successful_attempts = [state["attempts"][index] for index in successful]
    successful_removes = [attempt for attempt in successful_attempts if attempt["operation_kind"] == "remove"]
    successful_adds = [attempt for attempt in successful_attempts if attempt["operation_kind"] == "add"]
    if successful_removes and successful_adds and replay_a33_attempt_sequence([*successful_removes, *successful_adds], state["operations"])[0] != 5:
        return 5
    if len(successful) >= 2:
        approval = copy.deepcopy(state)
        first, second = successful[:2]
        approval["attempts"][second]["result"]["approval"]["approval_id"] = approval["attempts"][first]["result"]["approval"]["approval_id"]
        if validate_a33_runtime_semantics(approval, runtime, config, run_oracles=False)[0] != 5:
            return 5
    counters = copy.deepcopy(state)
    counters["worktree_effects"]["adds"] += 1
    if validate_a33_runtime_semantics(counters, runtime, config, run_oracles=False)[0] != 5:
        return 5
    registration = copy.deepcopy(state)
    registration["registered"] = [registration["operations"][0]["destination"]] if not registration["registered"] else []
    if validate_a33_runtime_semantics(registration, runtime, config, run_oracles=False)[0] != 5:
        return 5
    inventory_attempt = next((index for index, attempt in enumerate(state["attempts"]) if "inventory" in attempt and attempt.get("raw_inventory_observation", {}).get("target_present") is True), None)
    if inventory_attempt is not None:
        inventory = copy.deepcopy(state)
        inventory["attempts"][inventory_attempt]["inventory"]["classes"].append("unknown")
        if validate_a33_runtime_semantics(inventory, runtime, config, run_oracles=False)[0] != 5:
            return 5
        for field, value in [
            ("status_porcelain_v2", "malformed"),
            ("artifact_files", [state["attempts"][inventory_attempt]["raw_inventory_observation"]["tracked_files"][0]] if state["attempts"][inventory_attempt]["raw_inventory_observation"]["tracked_files"] else ["fixture.txt"]),
            ("observed_source", "/mutated/source"), ("observed_path", "/mutated/path"),
            ("observed_membership", "main"),
        ]:
            raw_inventory = copy.deepcopy(state)
            raw_inventory["attempts"][inventory_attempt]["raw_inventory_observation"][field] = value
            if validate_a33_runtime_semantics(raw_inventory, runtime, config, run_oracles=False)[0] != 5:
                return 5
        locked = copy.deepcopy(state)
        destination = locked["attempts"][inventory_attempt]["result"]["operation"]["destination"]
        worktree_raw = locked["attempts"][inventory_attempt]["raw_inventory_observation"]["worktree_porcelain"]
        destination_index = worktree_raw.index(f"worktree {destination}")
        worktree_raw.insert(destination_index + 1, "locked")
        if validate_a33_runtime_semantics(locked, runtime, config, run_oracles=False)[0] != 5:
            return 5
    delta_attempt = next((index for index, attempt in enumerate(state["attempts"]) if attempt["result"]["status"] == "pass"), None)
    if delta_attempt is not None:
        delta = copy.deepcopy(state)
        delta["attempts"][delta_attempt]["result"]["observed_delta"]["common_dir_identity"]["after"] = "mutated"
        if validate_a33_runtime_semantics(delta, runtime, config, run_oracles=False)[0] != 5:
            return 5
        expected_delta = state["attempts"][delta_attempt]["result"]["expected_delta"]
        for kind, field in [("ref", "branch_ref"), ("reflog", "branch_reflog")]:
            observed_delta = copy.deepcopy(expected_delta)
            observed_delta[field]["after"] = {"mutated": kind}
            observed_delta[field]["change"] = "created"
            if validate_a33_semantic_mutation({"kind": kind, "expected": expected_delta, "observed": observed_delta}) != 5:
                return 5
        raw_admin = copy.deepcopy(state)
        raw_admin["attempts"][delta_attempt]["raw_admin_after"]["config"] += "\nmutated"
        if validate_a33_runtime_semantics(raw_admin, runtime, config, run_oracles=False)[0] != 5:
            return 5
    cleanup = copy.deepcopy(runtime)
    cleanup["cleanup"]["eligible"] = not cleanup["cleanup"]["eligible"]
    if validate_a33_runtime_semantics(state, cleanup, config, run_oracles=False)[0] != 5:
        return 5
    category_attempt = next((index for index, attempt in enumerate(state["attempts"]) if attempt["category"] != "valid"), None)
    if category_attempt is not None:
        category = copy.deepcopy(state)
        category["attempts"][category_attempt]["category"] = "valid"
        if validate_a33_runtime_semantics(category, runtime, config, run_oracles=False)[0] != 5:
            return 5
        wrong_bound = copy.deepcopy(state)
        wrong_bound["attempts"][category_attempt]["result"]["approval"]["source"] = "/wrong/source"
        if validate_a33_runtime_semantics(wrong_bound, runtime, config, run_oracles=False)[0] != 5:
            return 5
    key_record = next((record for record in state["join_evidence_records"] if record.get("scenario_id") == "a33-runtime-key-mismatch-zero-effect"), None)
    if key_record is not None:
        for mutation in ["delete", "duplicate", "swap"]:
            key_matrix = copy.deepcopy(state)
            target = next(record for record in key_matrix["join_evidence_records"] if record.get("scenario_id") == "a33-runtime-key-mismatch-zero-effect")
            if mutation == "delete":
                target["operation_bindings"].pop()
            elif mutation == "duplicate":
                target["operation_bindings"].append(copy.deepcopy(target["operation_bindings"][0]))
            else:
                target["operation_bindings"][0]["operation_kind"] = "remove" if target["operation_bindings"][0]["operation_kind"] == "add" else "add"
            if validate_a33_runtime_semantics(key_matrix, runtime, config, run_oracles=False)[0] != 5:
                return 5
    managed_record = next((record for record in state.get("collector_records", []) if record.get("scenario_id") == "a33-runtime-effective-profile-observed" and record.get("status") == "pass"), None)
    if managed_record is not None:
        mutations = [
            lambda value: value["installed_agent_names"].pop(),
            lambda value: value["installed_agent_names"].append("unexpected"),
            lambda value: value["agents"][0].__setitem__("name", "renamed-agent"),
            lambda value: value["canonical_agent_paths"].__setitem__(0, "agents/substituted.md"),
            lambda value: value["manifest_agent_paths"].__setitem__(0, "agents/substituted.md"),
            lambda value: value.__setitem__("manifest_path", "/substituted/rose-aili.components.json"),
            lambda value: value.__setitem__("manifest_regular_nonsymlink", False),
            lambda value: value["environment_controls"].pop("OPENCODE_ALLOW_CUSTOM_HOME"),
            lambda value: value["environment_controls"].__setitem__("AILI_ALLOW_CROSS_ENV", "no"),
            lambda value: value["agents"][0].__setitem__("exact_byte_equality", False),
            lambda value: value["agents"][0].__setitem__("installed_path", "/ambient/agent.md"),
            lambda value: value["agents"][0].__setitem__("canonical_path", "/substituted/agent.md"),
            lambda value: value["agents"][0]["permissions"][0].__setitem__("value", "malformed"),
            lambda value: value["agents"][0]["permissions"].append({"path": "permission.unexpected", "value": "allow"}),
            lambda value: value["agents"][0]["permissions"].append({"path": "permission.unexpected", "value": "ask"}),
            lambda value: value["agents"][0]["provenance"].__setitem__(0, "canonical:/substituted"),
            lambda value: value["isolated_config_entries"].append("opencode.json"),
        ]
        subagent_index = next((index for index, agent in enumerate(managed_record["before_state"]["agents"]) if agent["name"] != "rose"), None)
        if subagent_index is None:
            return 5
        for permission in ["permission.external_directory", "permission.task"]:
            mutations.append(lambda value, name=permission, index=subagent_index: next(entry for entry in value["agents"][index]["permissions"] if entry["path"] == name).__setitem__("value", "allow"))
        for mutate in mutations:
            changed = copy.deepcopy(state)
            target = next(record for record in changed["collector_records"] if record.get("scenario_id") == "a33-runtime-effective-profile-observed")
            mutate(target["before_state"])
            if validate_a33_runtime_semantics(changed, runtime, config, run_oracles=False)[0] != 5:
                return 5
        collector_path = copy.deepcopy(state)
        collector_path["collector_install_paths"].append(str(Path(state["run_root"]) / "unexpected-install-path"))
        if validate_a33_runtime_semantics(collector_path, runtime, config, run_oracles=False)[0] != 5:
            return 5
        for control in ["OPENCODE_ALLOW_CUSTOM_HOME", "AILI_ALLOW_CROSS_ENV"]:
            for mutation in ["missing", "wrong"]:
                environment = copy.deepcopy(state)
                if mutation == "missing":
                    environment["managed_install_attempt"]["environment_controls"].pop(control)
                else:
                    environment["managed_install_attempt"]["environment_controls"][control] = "no"
                if validate_a33_runtime_semantics(environment, runtime, config, run_oracles=False)[0] != 5:
                    return 5
            reconstructed = copy.deepcopy(state)
            reconstructed["git_environment"][control] = "no"
            if validate_a33_runtime_semantics(reconstructed, runtime, config, run_oracles=False)[0] != 5:
                return 5
    stale_attempt = next((attempt for attempt in state["attempts"] if attempt.get("category") == "stale_snapshot_mismatch"), None)
    if stale_attempt is not None:
        stale = copy.deepcopy(state)
        stale["approval_snapshots"].pop(stale_attempt["result"]["approval"]["approval_id"], None)
        if validate_a33_runtime_semantics(stale, runtime, config, run_oracles=False)[0] != 5:
            return 5
    if state.get("consumed_approvals"):
        forged = copy.deepcopy(state)
        consumed_id = next(iter(forged["consumed_approvals"]))
        forged["consumed_approvals"][consumed_id]["approval"]["decision_ref"] = "forged"
        if validate_a33_runtime_semantics(forged, runtime, config, run_oracles=False)[0] != 5:
            return 5
    cross_kind = next((attempt for attempt in state["attempts"] if attempt.get("category") == "reused" and attempt.get("operation_kind") == "remove" and attempt.get("result", {}).get("approval", {}).get("kind") == "add"), None)
    if cross_kind is not None:
        forged_reuse = copy.deepcopy(state)
        forged_reuse["consumed_approvals"].pop(cross_kind["result"]["approval"]["approval_id"], None)
        if validate_a33_runtime_semantics(forged_reuse, runtime, config, run_oracles=False)[0] != 5:
            return 5
    transition_attempt = next((attempt for attempt in state["attempts"] if attempt["result"]["status"] == "pass" and attempt["raw_admin_before"]["branch_ref"]["value"] is not None), None)
    if transition_attempt is not None:
        non_null_transition = copy.deepcopy(state)
        index = state["attempts"].index(transition_attempt)
        non_null_transition["attempts"][index]["raw_admin_after"]["branch_ref"]["value"] = "f" * 40
        if validate_a33_runtime_semantics(non_null_transition, runtime, config, run_oracles=False)[0] != 5:
            return 5
    if any(validate_join_cases(value, ["one"]) != 5 for value in [[None], [[]], ["scalar"], [{}]]):
        return 5
    run_root = Path(state["run_root"])
    security_exit, root_identity, _ = capture_a33_cleanup_security(state, run_root)
    expected_entries = _a33_expected_top_level(state)
    marker = {"schema_version": A33_INTERNAL_EVIDENCE_VERSION, "run_root": str(run_root), "run_id": run_root.name, "cleanup_nonce": state["cleanup_nonce"]}
    if security_exit != 0 or root_identity is None or expected_entries is None:
        return 5
    marker_nonce = dict(marker); marker_nonce["cleanup_nonce"] = "0" * 64
    marker_schema = dict(marker); marker_schema["schema_version"] = "mutated"
    unsafe_mode = dict(root_identity); unsafe_mode["mode"] = 0o770
    wrong_owner = dict(root_identity); wrong_owner["uid"] = root_identity["uid"] + 1
    changed_inode = dict(root_identity); changed_inode["st_ino"] = root_identity["st_ino"] + 1
    changed_device = dict(root_identity); changed_device["st_dev"] = root_identity["st_dev"] + 1
    entries = sorted(expected_entries)
    if validate_a33_cleanup_security_record(state, run_root, marker_nonce, root_identity, entries, []) != 5 \
            or validate_a33_cleanup_security_record(state, run_root, marker_schema, root_identity, entries, []) != 5 \
            or validate_a33_cleanup_security_record(state, run_root.parent / "wrong-prefix", marker, root_identity, entries, []) != 5 \
            or validate_a33_cleanup_security_record(state, run_root, marker, unsafe_mode, entries, []) != 5 \
            or validate_a33_cleanup_security_record(state, run_root, marker, wrong_owner, entries, [], current_uid=root_identity["uid"]) != 5 \
            or validate_a33_cleanup_security_record(state, run_root, marker, root_identity, [*entries, "sentinel"], []) != 5 \
            or same_a33_root_identity(root_identity, changed_inode) or same_a33_root_identity(root_identity, changed_device):
        return 5
    destinations = sorted({operation["destination"] for operation in state["operations"]})
    if validate_a33_live_cleanup_records(destinations, {state["operations"][0]["source"]: [f"worktree {destinations[0]}"]}) != 5:
        return 5
    if validate_a33_live_cleanup_records(destinations, {state["operations"][0]["source"]: []}, [destinations[0]]) != 5:
        return 5
    if records is None:
        return 5
    return 0


def valid_runtime_case(row: Any) -> bool:
    if not exact_keys(row, A33_RUNTIME_CASE_FIELDS) or not isinstance(row["run_id"], str) or not row["run_id"]:
        return False
    joined = {name: row[name] for name in A33_CASE_FIELDS}
    return valid_case(joined, "runtime")


def validate_case_list(cases: Any, mandatory: list[str], subset: str) -> int:
    if not isinstance(cases, list) or len(mandatory) != len(set(mandatory)):
        return 5
    if [row.get("id") for row in cases if isinstance(row, dict)] != mandatory:
        return 5
    return 0 if all(valid_case(row, subset) for row in cases) else 5


def validate_static_result(result: Any, config: dict[str, Any]) -> int:
    mandatory = config["static_mandatory_case_ids"]
    if not exact_keys(result, config["static_result_fields"]):
        return 5
    if result["schema_version"] != A33_SCHEMA or result["command"] != "a33-static" or result["mode"] != "static":
        return 5
    if result["exit_code"] not in {0, 3, 5} or result["status"] not in {"pass", "Unverified", "fail"}:
        return 5
    if result["mandatory_case_ids"] != mandatory or result["observed_case_ids"] != mandatory or result["case_set_equal"] is not True:
        return 5
    if validate_case_list(result["cases"], mandatory, "static") != 0:
        return 5
    mutation_fields = ["id", "mutation", "expected_validator_exit", "observed_validator_exit", "status", "evidence_refs"]
    mutations = result["contract_mutations"]
    if [row.get("id") for row in mutations] != config["contract_mutation_ids"]:
        return 5
    if any(not exact_keys(row, mutation_fields) or row["expected_validator_exit"] != 5 or row["observed_validator_exit"] != 5 or row["status"] != "pass" or not row["evidence_refs"] for row in mutations):
        return 5
    if not isinstance(result["summary"], dict) or not isinstance(result["unverified"], list) or not isinstance(result["ephemeral_result"], str) or not result["ephemeral_result"]:
        return 5
    if result["exit_code"] == 0 and any(row["status"] != "pass" for row in result["cases"]):
        return 5
    return result["exit_code"]


def validate_runtime_result(result: Any, config: dict[str, Any]) -> int:
    mandatory = config["runtime_mandatory_case_ids"]
    if not exact_keys(result, config["runtime_join_fields"]):
        return 5
    if result["schema_version"] != A33_SCHEMA or result["command"] != "a33-runtime-join" or result["mode"] != "runtime":
        return 5
    if result["exit_code"] not in {0, 3, 5} or result["status"] not in {"pass", "Unverified", "fail"}:
        return 5
    if result["mandatory_case_ids"] != mandatory or result["observed_case_ids"] != mandatory or result["case_set_equal"] is not True:
        return 5
    if not isinstance(result["cases"], list) or any(not isinstance(row, dict) for row in result["cases"]):
        return 5
    if [row.get("id") for row in result["cases"]] != mandatory or not all(valid_runtime_case(row) for row in result["cases"]):
        return 5
    cleanup = result["cleanup"]
    if not exact_keys(cleanup, ["eligible", "attempted", "status", "retained_paths", "errors"]):
        return 5
    if not isinstance(cleanup["eligible"], bool) or cleanup["attempted"] is not False or cleanup["status"] not in {"eligible_for_global_join", "retained_registered", "blocked"}:
        return 5
    if not isinstance(cleanup["retained_paths"], list) or not isinstance(cleanup["errors"], list) or not isinstance(result["operations"], list):
        return 5
    if not isinstance(result["summary"], dict) or not isinstance(result["unverified"], list) or not isinstance(result["ephemeral_result"], str) or not result["ephemeral_result"]:
        return 5
    if result["exit_code"] == 0 and (not cleanup["eligible"] or any(row["status"] != "pass" for row in result["cases"])):
        return 5
    return result["exit_code"]


def static_source_failures(project: Path) -> list[str]:
    failures = p6_permission_failures()
    required = {
        ".agents/skills/aili-delivery-flow/references/protocols/worktree-context.md": ["a30-a31-external-read", "a33-attached-shared-trust-domain", "<session-root>/.worktrees/<repo_key>/<worktree_key>", "A33Identity", "No identity hash/digest field or string sentinel is valid", "ambient network", "one declared repository/cwd"],
        ".agents/skills/aili-delivery-flow/references/protocols/subagent-task-packet.md": ["WT-001 context ref", "owning target repository"],
        ".agents/skills/aili-delivery-flow/references/protocols/subagent-result.md": ["WT-001 context ref", "never duplicates or rebinds"],
        ".agents/skills/aili-delivery-flow/references/protocols/implementation-package.md": ["required-satisfied | not-triggered | blocked", "BUILD_MATERIAL_DISCOVERY", "never creates automatic review"],
        ".agents/skills/parallel-subagent-dispatch/SKILL.md": ["Default to at most two", "Do not automatically add review", "one compact `WT-001` reference"],
        ".agents/skills/git-workflow-and-versioning/SKILL.md": ["A33 session-root attached repositories", "reflog_policy:enabled|disabled", "no sandbox, DLP, network isolation"],
        ".agents/skills/aili-delivery-flow/references/backend-routing.md": ["PREPARE has zero add/remove effect", "default concurrency is at most two"],
        "tests/opencode-permission-probe.test.mjs": ["A33 agent installs preserve whole-file equality in copy and selective modes", "a33-runtime-key-mismatch-zero-effect", "delete_each"],
    }
    for relative_path, markers in required.items():
        path = project / relative_path
        if not path.is_file():
            failures.append(f"missing A33 owner: {relative_path}")
            continue
        text = path.read_text(encoding="utf-8")
        failures.extend(f"missing A33 marker: {relative_path}: {marker}" for marker in markers if marker not in text)
    try:
        manifest = json.loads((project / "manifests/rose-aili.components.json").read_text(encoding="utf-8"))
        manifest_agents = {entry["path"] for entry in manifest["components"]["agents"]}
        if manifest_agents != set(P6_AGENT_FILES) or len(manifest_agents) != 20:
            failures.append("manifest Agent inventory is not exact ROSE+19")
    except (OSError, KeyError, TypeError, json.JSONDecodeError):
        failures.append("manifest Agent inventory unavailable")
    return failures


def static_case(id_: str, status: str, evidence: list[str]) -> dict[str, Any]:
    return {"id": id_, "subset": "static", "status": status, "exit_code": 0 if status == "pass" else 5, "operation_id": None, "approval_ref": None, "host_identity": None, "source_identity": None, "target_identity": None, "expected_delta": None, "observed_delta": None, "evidence_refs": evidence, "unverified": [], "cleanup_state": None}


def build_contract_mutations(cases: list[dict[str, Any]], mandatory: list[str], ids: list[str]) -> list[dict[str, Any]]:
    extra = dict(cases[-1]); extra["id"] = "a33-unexpected-extra"
    skipped = [dict(row) for row in cases]; skipped[0]["status"] = "skipped"
    empty = [dict(row) for row in cases]; empty[0]["evidence_refs"] = []
    malformed = [dict(row) for row in cases]; malformed[0].pop("operation_id")
    variants = [
        ("delete one mandatory case", cases[1:], ["delete:first-mandatory-id"]),
        ("duplicate one mandatory case", cases + [dict(cases[0])], ["duplicate:first-mandatory-id"]),
        ("append an extra case", cases + [extra], ["extra:a33-unexpected-extra"]),
        ("mark one case skipped", skipped, ["status:skipped"]),
        ("remove case evidence", empty, ["evidence_refs:empty"]),
        ("schema/key/identity/null mutation variants", malformed, ["case-field-omission", "operation-or-approval-key-omission-wrong-type-reuse", "identity-field-type-sentinel-nullability-detached-array-dirty", "unexpected-identity-hash-or-digest"]),
    ]
    rows = []
    for id_, (description, mutated, evidence) in zip(ids, variants, strict=True):
        observed = validate_case_list(mutated, mandatory, "static")
        rows.append({"id": id_, "mutation": description, "expected_validator_exit": 5, "observed_validator_exit": observed, "status": "pass" if observed == 5 else "fail", "evidence_refs": evidence})
    return rows


def external_ephemeral(path_text: str, project: Path, must_exist: bool) -> Path:
    path = Path(path_text)
    path = path.resolve(strict=must_exist)
    if not path.is_absolute() or path == project or project in path.parents:
        raise ValueError("A33 evidence must use an external driver-owned ephemeral path")
    if not must_exist and not path.parent.is_dir():
        raise ValueError("ephemeral parent does not exist")
    return path


def run_a33_static(args: argparse.Namespace) -> tuple[int, dict[str, Any]]:
    project = Path(args.project).resolve(strict=True)
    fixture_path, config = load_a33_fixture(project, args.fixture)
    output_path = external_ephemeral(args.ephemeral_result, project, False)
    failures = static_source_failures(project)
    status = "pass" if not failures else "fail"
    evidence = [str(fixture_path), ".agents/skills/aili-delivery-flow/references/protocols/worktree-context.md", "agents/*.md"]
    cases = [static_case(id_, status, evidence) for id_ in config["static_mandatory_case_ids"]]
    result = {
        "schema_version": A33_SCHEMA, "command": "a33-static", "mode": "static", "status": status,
        "exit_code": 0 if not failures else 5, "mandatory_case_ids": config["static_mandatory_case_ids"],
        "observed_case_ids": config["static_mandatory_case_ids"], "case_set_equal": True, "cases": cases,
        "contract_mutations": build_contract_mutations(cases, config["static_mandatory_case_ids"], config["contract_mutation_ids"]),
        "summary": {"mandatory": len(cases), "passed": len(cases) if not failures else 0, "failed": len(cases) if failures else 0},
        "unverified": failures, "ephemeral_result": str(output_path),
    }
    if validate_static_result(result, config) == 5 and not failures:
        result["status"] = "fail"; result["exit_code"] = 5; result["unverified"].append("internal static schema validation failed")
    output_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result["exit_code"], result


def load_result(path_text: str, project: Path) -> tuple[Path, dict[str, Any]]:
    path = external_ephemeral(path_text, project, False)
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        value = {}
    return path, value if isinstance(value, dict) else {}


def validate_join_cases(cases: Any, mandatory: list[str]) -> int:
    if not isinstance(cases, list) or any(not isinstance(row, dict) for row in cases) or len(mandatory) != len(set(mandatory)):
        return 5
    if [row.get("id") for row in cases] != mandatory:
        return 5
    return 0 if all(valid_case(row, row.get("subset")) for row in cases) else 5


def validate_a33_live_cleanup_records(destinations: list[str], records_by_source: dict[str, Any], present_destinations: Any = None) -> int:
    if not isinstance(destinations, list) or len(destinations) != len(set(destinations)) or not isinstance(records_by_source, dict):
        return 5
    if present_destinations is None:
        present_destinations = []
    if not isinstance(present_destinations, list) or any(value in destinations for value in present_destinations):
        return 5
    destination_paths = {Path(value) for value in destinations if isinstance(value, str) and value}
    if len(destination_paths) != len(destinations):
        return 5
    for records in records_by_source.values():
        parsed = parse_a33_worktree_porcelain(records)
        if parsed is None:
            return 5
        if any(Path(record["path"]) in destination_paths for record in parsed):
            return 5
    return 0


def _path_chain_without_symlink(path: Path, root: Path) -> bool:
    try:
        relative_path = path.relative_to(root)
    except ValueError:
        return False
    current = root
    if current.is_symlink():
        return False
    for part in relative_path.parts:
        current = current / part
        if current.is_symlink():
            return False
        if not current.exists():
            break
    return True


def _a33_root_identity(run_root: Path) -> dict[str, Any] | None:
    try:
        observed = run_root.lstat()
    except OSError:
        return None
    return {"st_dev": observed.st_dev, "st_ino": observed.st_ino, "uid": observed.st_uid, "mode": stat.S_IMODE(observed.st_mode), "is_dir": stat.S_ISDIR(observed.st_mode)}


def _a33_expected_top_level(state: dict[str, Any]) -> set[str] | None:
    operations = state.get("operations")
    if not isinstance(operations, list):
        return None
    sources = {Path(operation.get("source", "")).name for operation in operations if isinstance(operation, dict)}
    expected_sources = {f"source-{index}" for index in range(1, len(sources) + 1)}
    if sources != expected_sources:
        return None
    run_root = Path(state.get("run_root", ""))
    install_candidates = [run_root / "opencode-home", run_root / "home" / ".agents" / "skills"]
    expected_install_paths = [str(path) for path in install_candidates if path.exists() or path.is_symlink()]
    if state.get("collector_install_paths") != expected_install_paths:
        return None
    install_top = {"opencode-home"} if str(run_root / "opencode-home") in expected_install_paths else set()
    return {".aili-a33-driver-owned", "state.json", "runtime-result.json", "home", "tmp", "empty-hooks", "host", *sources, *install_top}


def validate_a33_cleanup_security_record(state: dict[str, Any], run_root: Path, marker: Any,
                                         root_identity: Any, entries: Any, symlinks: Any,
                                         current_uid: int | None = None) -> int:
    uid = os.getuid() if current_uid is None else current_uid
    temp_root = Path(tempfile.gettempdir()).resolve()
    expected_entries = _a33_expected_top_level(state)
    expected_marker = {"schema_version": A33_INTERNAL_EVIDENCE_VERSION, "run_root": str(run_root), "run_id": run_root.name, "cleanup_nonce": state.get("cleanup_nonce")}
    if run_root.parent != temp_root or re.fullmatch(r"aili-a33-runtime-[A-Za-z0-9]{6}", run_root.name) is None:
        return 5
    if state.get("run_root") != str(run_root) or state.get("run_id") != run_root.name or state.get("schema_version") != A33_SCHEMA:
        return 5
    if not isinstance(state.get("cleanup_nonce"), str) or re.fullmatch(r"[0-9a-f]{64}", state["cleanup_nonce"]) is None:
        return 5
    if not exact_keys(marker, A33_MARKER_FIELDS) or marker != expected_marker:
        return 5
    if not exact_keys(root_identity, ["st_dev", "st_ino", "uid", "mode", "is_dir"]) or root_identity["uid"] != uid \
            or root_identity["mode"] & 0o077 or root_identity["is_dir"] is not True:
        return 5
    if expected_entries is None or not isinstance(entries, list) or set(entries) != expected_entries or len(entries) != len(expected_entries):
        return 5
    if not isinstance(symlinks, list) or symlinks:
        return 5
    return 0


def same_a33_root_identity(before: Any, after: Any) -> bool:
    return exact_keys(before, ["st_dev", "st_ino", "uid", "mode", "is_dir"]) and before == after


def capture_a33_cleanup_security(state: dict[str, Any], run_root: Path) -> tuple[int, dict[str, Any] | None, list[str]]:
    marker_path = run_root / ".aili-a33-driver-owned"
    try:
        root_identity = _a33_root_identity(run_root)
        entries = sorted(entry.name for entry in run_root.iterdir())
        symlinks = [name for name in entries if stat.S_ISLNK((run_root / name).lstat().st_mode)]
        marker = json.loads(marker_path.read_text(encoding="utf-8"))
        expected = _a33_expected_top_level(state)
        if expected is not None:
            for name in expected:
                mode = (run_root / name).lstat().st_mode
                if name in {".aili-a33-driver-owned", "state.json", "runtime-result.json"}:
                    if not stat.S_ISREG(mode):
                        return 5, root_identity, [f"cleanup top-level file type mismatch: {name}"]
                elif not stat.S_ISDIR(mode):
                    return 5, root_identity, [f"cleanup top-level directory type mismatch: {name}"]
        for value in state.get("collector_install_paths", []):
            path = Path(value)
            if not _inside(path, run_root) or path.is_symlink() or not path.is_dir() or not _path_chain_without_symlink(path, run_root):
                return 5, root_identity, [f"cleanup collector path mismatch: {value}"]
    except (OSError, json.JSONDecodeError) as exc:
        return 5, None, [f"cleanup ownership evidence unavailable or malformed: {exc}"]
    result = validate_a33_cleanup_security_record(state, run_root, marker, root_identity, entries, symlinks)
    return result, root_identity, [] if result == 0 else ["cleanup ownership, prefix, nonce, mode, or inventory mismatch"]


def verify_a33_live_cleanup(state: dict[str, Any], run_root: Path) -> tuple[int, dict[str, Any] | None, list[str]]:
    errors: list[str] = []
    if not getattr(shutil.rmtree, "avoids_symlink_attacks", False):
        return 3, None, ["platform shutil.rmtree does not provide symlink-attack-resistant deletion"]
    security_exit, root_identity, security_errors = capture_a33_cleanup_security(state, run_root)
    if security_exit != 0:
        return security_exit, root_identity, security_errors
    destinations = sorted({operation["destination"] for operation in state["operations"]})
    sources = sorted({operation["source"] for operation in state["operations"]})
    for value in destinations:
        destination = Path(value)
        if not _inside(destination, run_root) or destination.exists() or destination.is_symlink() or not _path_chain_without_symlink(destination.parent, run_root):
            errors.append(f"cleanup destination is present, substituted, or outside run root: {value}")
    for value in sources:
        source = Path(value)
        try:
            if not _inside(source, run_root) or source.resolve(strict=True) != source or not source.is_dir() or not _path_chain_without_symlink(source, run_root):
                errors.append(f"cleanup source is substituted or outside run root: {value}")
        except OSError:
            errors.append(f"cleanup source unavailable: {value}")
    if errors:
        return 5, root_identity, errors
    records_by_source: dict[str, list[str]] = {}
    for source in sources:
        try:
            observed = subprocess.run(
                ["git", "-C", source, "worktree", "list", "--porcelain", "-z"], cwd=source,
                env=state["git_environment"], capture_output=True, check=False, timeout=10,
            )
        except (FileNotFoundError, subprocess.TimeoutExpired, OSError) as exc:
            return 3, root_identity, [f"live cleanup worktree evidence unavailable: {exc}"]
        if observed.returncode != 0:
            return 3, root_identity, [f"live cleanup worktree evidence unavailable for {source}"]
        try:
            records_by_source[source] = [value for value in observed.stdout.decode("utf-8", errors="strict").split("\0") if value]
        except UnicodeDecodeError:
            return 5, root_identity, [f"live cleanup worktree evidence malformed for {source}"]
    present_destinations = [
        value for value in destinations
        if Path(value).exists() or Path(value).is_symlink()
        or not _path_chain_without_symlink(Path(value).parent, run_root)
    ]
    result = validate_a33_live_cleanup_records(destinations, records_by_source, present_destinations)
    return (result, root_identity, [] if result == 0 else ["live cleanup worktree residue or malformed evidence detected"])


def run_a33_join(args: argparse.Namespace) -> tuple[int, dict[str, Any]]:
    project = Path(args.project).resolve(strict=True)
    fixture_path, config = load_a33_fixture(project, args.fixture)
    static_path, static = load_result(args.static_result, project)
    runtime_path, runtime = load_result(args.runtime_result, project)
    try:
        static_exit = validate_static_result(static, config)
    except (KeyError, TypeError, ValueError, IndexError, AttributeError):
        static_exit = 5
    try:
        runtime_exit = validate_runtime_result(runtime, config)
    except (KeyError, TypeError, ValueError, IndexError, AttributeError):
        runtime_exit = 5
    try:
        state, state_errors = load_a33_runtime_state(runtime_path, runtime, project, fixture_path)
    except (KeyError, TypeError, ValueError, IndexError, AttributeError):
        state, state_errors = None, ["malformed runtime state evidence"]
    semantic_exit = 5
    semantic_rows: list[dict[str, Any]] = []
    if state is not None and not state_errors:
        try:
            semantic_exit, semantic_rows, semantic_errors = validate_a33_runtime_semantics(state, runtime, config)
            state_errors.extend(semantic_errors)
        except (KeyError, TypeError, ValueError, IndexError, AttributeError):
            semantic_exit = 5
            state_errors.append("malformed runtime semantic evidence")
    mandatory = config["static_mandatory_case_ids"] + config["runtime_mandatory_case_ids"]
    raw_runtime_cases = runtime.get("cases") if isinstance(runtime.get("cases"), list) else []
    runtime_cases = [{name: row.get(name) for name in A33_CASE_FIELDS} for row in raw_runtime_cases if isinstance(row, dict)]
    static_cases = static.get("cases") if isinstance(static.get("cases"), list) else []
    cases = static_cases + runtime_cases
    case_exit = validate_join_cases(cases, mandatory)
    delete_each = []
    for index, id_ in enumerate(mandatory):
        observed = validate_join_cases(cases[:index] + cases[index + 1:], mandatory)
        delete_each.append({"deleted_id": id_, "expected_validator_exit": 5, "observed_validator_exit": observed, "status": "pass" if observed == 5 else "fail", "evidence_refs": [f"delete:{id_}"]})
    runtime_cleanup = runtime.get("cleanup", {})
    eligible = static_exit == runtime_exit == semantic_exit == case_exit == 0 and not state_errors and runtime_cleanup.get("eligible") is True
    run_root = runtime_path.parent.resolve()
    cleanup = {"eligible": eligible, "attempted": False, "status": "retained_registered", "retained_paths": [str(run_root)], "errors": []}
    live_cleanup_exit = 0
    root_identity_before: dict[str, Any] | None = None
    exact_cleanup_identity = eligible and state is not None and state.get("run_root") == str(run_root) and state.get("run_id") == run_root.name \
        and runtime.get("run_id") == run_root.name and runtime.get("ephemeral_result") == str(runtime_path) \
        and run_root.parent == Path(tempfile.gettempdir()).resolve() and re.fullmatch(r"aili-a33-runtime-[A-Za-z0-9]{6}", run_root.name) is not None
    if eligible and not exact_cleanup_identity:
        live_cleanup_exit = 5
        cleanup["eligible"] = False
        cleanup["errors"].append("cleanup identity changed before live verification")
    if eligible and exact_cleanup_identity:
        live_cleanup_exit, root_identity_before, live_cleanup_errors = verify_a33_live_cleanup(state, run_root)
        if live_cleanup_exit != 0:
            cleanup["eligible"] = False
            cleanup["errors"].extend(live_cleanup_errors)
    if eligible and exact_cleanup_identity and live_cleanup_exit == 0:
        security_exit, root_identity_after, security_errors = capture_a33_cleanup_security(state, run_root)
        exact_cleanup_identity = security_exit == 0 and same_a33_root_identity(root_identity_before, root_identity_after)
        if not exact_cleanup_identity:
            live_cleanup_exit = 5
            cleanup["eligible"] = False
            cleanup["errors"].extend(security_errors or ["cleanup device/inode/owner/mode identity changed after live verification"])
        else:
            cleanup["attempted"] = True
            try:
                shutil.rmtree(run_root)
                cleanup["status"] = "succeeded" if not run_root.exists() else "failed"
                cleanup["retained_paths"] = [] if cleanup["status"] == "succeeded" else [str(run_root)]
            except OSError as exc:
                cleanup["status"] = "failed"; cleanup["errors"].append(str(exc))
    violation = state_errors or 5 in {static_exit, runtime_exit, semantic_exit, case_exit, live_cleanup_exit} or any(row["observed_validator_exit"] != 5 for row in delete_each) or cleanup["status"] == "failed"
    unavailable = 3 in {static_exit, runtime_exit, semantic_exit, live_cleanup_exit}
    exit_code = 5 if violation else 3 if unavailable or not eligible else 0
    missing_contract = [row["id"] for row in semantic_rows if row["status"] == "Unverified"]
    join_unverified = [] if exit_code == 0 else state_errors if exit_code == 5 and state_errors else missing_contract or ["mandatory A33 join evidence unavailable"]
    result = {
        "schema_version": A33_SCHEMA, "command": "a33-join", "mode": "joined", "status": "pass" if exit_code == 0 else "Unverified" if exit_code == 3 else "fail", "exit_code": exit_code,
        "static_result_ref": str(static_path), "runtime_result_ref": str(runtime_path),
        "static_mandatory_case_ids": config["static_mandatory_case_ids"], "runtime_mandatory_case_ids": config["runtime_mandatory_case_ids"],
        "mandatory_case_ids": mandatory, "observed_case_ids": [row.get("id") if isinstance(row, dict) else None for row in cases], "case_set_equal": case_exit == 0, "cases": cases,
        "mutation_summary": {"contract_mutations": static.get("contract_mutations", []), "delete_each": delete_each}, "cleanup": cleanup,
        "summary": {"mandatory": len(mandatory), "observed": len(cases), "static_exit": static_exit, "runtime_exit": runtime_exit},
        "unverified": join_unverified,
    }
    if not exact_keys(result, config["join_result_fields"]):
        result["status"] = "fail"; result["exit_code"] = 5
    return result["exit_code"], result


def a33_main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--project", required=True); parser.add_argument("--fixture", required=True)
    parser.add_argument("--mode", choices=["a33-static", "a33-join"], required=True)
    parser.add_argument("--ephemeral-result"); parser.add_argument("--static-result"); parser.add_argument("--runtime-result")
    parser.add_argument("--json", action="store_true")
    args: argparse.Namespace | None = None
    try:
        args = parser.parse_args(argv)
        if not args.json:
            raise ValueError("--json is required")
        if args.mode == "a33-static":
            if not args.ephemeral_result or args.static_result or args.runtime_result:
                raise ValueError("invalid static arguments")
            code, result = run_a33_static(args)
        else:
            if args.ephemeral_result or not args.static_result or not args.runtime_result:
                raise ValueError("invalid join arguments")
            code, result = run_a33_join(args)
        print(json.dumps(result, indent=2))
        return code
    except SystemExit:
        return 2
    except (AttributeError, IndexError) as exc:
        if args is not None and args.mode == "a33-join":
            print(json.dumps({"schema_version": A33_SCHEMA, "command": "a33-join", "status": "fail", "exit_code": 5, "errors": [f"malformed semantic evidence: {exc}"]}))
            return 5
        print(json.dumps({"schema_version": A33_SCHEMA, "status": "usage_error", "exit_code": 2, "errors": [str(exc)]}))
        return 2
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print(json.dumps({"schema_version": A33_SCHEMA, "status": "usage_error", "exit_code": 2, "errors": [str(exc)]}))
        return 2


def main() -> int:
    if "--mode" in sys.argv:
        return a33_main(sys.argv[1:])
    failures: list[str] = []
    permissions_only = "--profile" in sys.argv and "permissions" in sys.argv

    required_files = (
        [
            ".agents/skills/aili-delivery-flow/references/protocols/worktree-context.md",
            ".agents/skills/aili-delivery-flow/references/protocols/subagent-task-packet.md",
            ".agents/skills/aili-delivery-flow/references/protocols/subagent-result.md",
            ".agents/skills/aili-delivery-flow/references/protocols/implementation-package.md",
            ".agents/skills/aili-delivery-flow/references/backend-routing.md",
            ".agents/skills/parallel-subagent-dispatch/SKILL.md",
            "scripts/opencode_permission_probe.mjs",
            "docs/harness/fixtures/cross-worktree-permission-fixtures.yaml",
            "tests/opencode-permission-probe.test.mjs",
        ]
        if permissions_only
        else REQUIRED_FILES
    )

    for relative_path in required_files:
        path = ROOT / relative_path
        if not path.is_file():
            failures.append(f"MISSING FILE: {relative_path}")
            continue

        text = path.read_text(encoding="utf-8")
        for needle in CONTENT_CHECKS.get(relative_path, []):
            if needle not in text:
                failures.append(f"MISSING CONTENT: {relative_path} :: {needle}")

    active_neutral_build_files = [
        "commands/build.md",
        ".agents/skills/aili-delivery-flow/SKILL.md",
        ".agents/skills/aili-delivery-flow/references/build-execution-loop.md",
        ".agents/skills/aili-delivery-flow/references/implementation-packages.md",
        ".agents/skills/aili-delivery-flow/references/lifecycle.md",
        ".agents/skills/aili-delivery-flow/references/backend-routing.md",
        ".agents/skills/aili-delivery-flow/references/artifact-contracts.md",
        ".agents/skills/aili-delivery-flow/references/review-repair-loop.md",
        "docs/harness/aili-harness-contract.md",
        "docs/harness/command-lifecycle.md",
    ]
    forbidden_active_pseudo_goal = [
        "goal_id", "goal-style", "scoped goal marker",
        "scoped BUILD goal", "BUILD Goal Mode", "autonomous goal mode",
    ]
    for relative_path in active_neutral_build_files:
        path = ROOT / relative_path
        if not path.is_file():
            continue
        lowered = path.read_text(encoding="utf-8").lower()
        for marker in forbidden_active_pseudo_goal:
            if marker.lower() in lowered:
                failures.append(f"ACTIVE PSEUDO-GOAL AUTHORITY: {relative_path} :: {marker}")

    p5_required_markers = {
        "commands/build.md": ["IMPLEMENTED_TARGETED_VERIFIED", "Do not infer package"],
        ".agents/skills/aili-delivery-flow/SKILL.md": ["derive the queue from the active contract", "fresh exact key/class-bound approval", "CI failure reports"],
        ".agents/skills/aili-delivery-flow/references/build-execution-loop.md": ["A33 admission and operation gates", "through root `/.worktrees/`", "explicitly scoped product/repository CI", "progress-ledger savepoint"],
        ".agents/skills/aili-delivery-flow/references/backend-routing.md": ["synthesize a queue from the active accepted contract", "PREPARE has zero add/remove effect", "IMPLEMENTED_TARGETED_VERIFIED"],
        ".agents/skills/aili-delivery-flow/references/artifact-contracts.md": ["evidence_state", "one minimal direct changed-scope", "optional matrix evidence is not a broad BUILD or release gate"],
        ".agents/skills/aili-delivery-flow/references/lifecycle.md": ["An attachment is admitted only", "Admission is not operation authority", "build-readiness status: `READY` or `BLOCKED`"],
        ".agents/skills/aili-delivery-flow/references/test-document-policy.md": ["BUILD readiness is only `READY` or `BLOCKED`", "fresh explicit intent", "CI failure returns to the user"],
        "docs/harness/aili-harness-contract.md": ["A33 Static Admission and Approval Gates", "Active-contract completion package", "explicit product/repository CI"],
        "docs/harness/command-lifecycle.md": ["A33 Admission Boundary", "fresh explicit intent", "Explicitly scoped product/repository CI"],
    }
    for relative_path, markers in p5_required_markers.items():
        path = ROOT / relative_path
        if not path.is_file():
            failures.append(f"MISSING P5 SOURCE: {relative_path}")
            continue
        text = path.read_text(encoding="utf-8")
        for marker in markers:
            if marker not in text:
                failures.append(f"MISSING P5 CONTENT: {relative_path} :: {marker}")

    forbidden_p5_residuals = {
        ".agents/skills/aili-delivery-flow/references/build-execution-loop.md": [
            "For each Package 1–11:",
            "Any pure or mixed request to install, register, run, modify",
        ],
        ".agents/skills/aili-delivery-flow/references/artifact-contracts.md": [
            "Package 12 alone owns mandatory convergence",
            "Package 12 review/test/security evidence",
            "- `WAIVED`: the user explicitly waived a gate",
            "- `UNVERIFIED`: the gate state is known to be unverified and the user explicitly accepts proceeding",
        ],
        "docs/harness/aili-harness-contract.md": [
            "Package 12 as the single comprehensive quality gate",
            "before the Package 12 matrix and joined fresh evidence",
            "Pure automation modification and mixed modification-plus-documentation requests reject",
        ],
        "docs/harness/command-lifecycle.md": [
            "Pure or mixed requests to install, register, run, modify",
        ],
    }
    for relative_path, markers in forbidden_p5_residuals.items():
        path = ROOT / relative_path
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        for marker in markers:
            if marker in text:
                failures.append(f"STALE P5 AUTHORITY: {relative_path} :: {marker}")

    failures.extend(p6_permission_failures())

    if not permissions_only:
        code_scout_text = (ROOT / "agents/code-scout.md").read_text(encoding="utf-8")
        for forbidden in FORBIDDEN_CODE_SCOUT_BASH:
            if forbidden in code_scout_text:
                failures.append(f"UNSAFE CODE-SCOUT BASH PERMISSION: {forbidden}")

    top_level_protocols = ROOT / "protocols"
    if not permissions_only and top_level_protocols.exists():
        for protocol_file in top_level_protocols.rglob("*.md"):
            protocol_text = protocol_file.read_text(encoding="utf-8")
            relative_protocol = protocol_file.relative_to(ROOT)
            if CANONICAL_PROTOCOL_PATH not in protocol_text:
                failures.append(
                    f"TOP-LEVEL PROTOCOL LACKS CANONICAL POINTER: {relative_protocol}"
                )
            if "OBSERVED FACTS" in protocol_text or "Subagent task packet:" in protocol_text:
                failures.append(
                    f"TOP-LEVEL PROTOCOL LOOKS LIKE INDEPENDENT AUTHORITY: {relative_protocol}"
                )

    if failures:
        print("FAIL delegation protocol checks")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("PASS delegation protocol checks")
    print(f"Checked {len(required_files)} protocol files and {len(P6_AGENT_FILES)} lean Agent profiles")
    return 0


if __name__ == "__main__":
    sys.exit(main())
