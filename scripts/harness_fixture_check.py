#!/usr/bin/env python3
"""Static smoke validation for AILI harness fixtures.

Uses JSON syntax in .yaml files so validation stays Python-stdlib only.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIXTURE_DIR = ROOT / "docs" / "harness" / "fixtures"
DELIVERY_COMMANDS = {"ideate.md", "define.md", "build.md", "ship.md"}
UTILITY_COMMANDS = {
    "local-review.md",
    "handoff.md",
    "agents-md.md",
    "harness-audit.md",
    "retro.md",
    "security-review.md",
}
PUBLIC_COMMANDS = DELIVERY_COMMANDS | UTILITY_COMMANDS
RETIRED_SKILLS = {
    "agents-md-initialization",
    "evidence-scoped-retrospective",
    "harness-optimization-audit",
    "local-review-gate",
    "rose-memory",
    "session-handoff",
}

REQUIRED = {
    "command-routing-fixtures.yaml": {
        "markers": [
            "/ideate",
            "/define",
            "/build",
            "/ship",
            "/local-review",
            "natural-language-first-class",
            "slash-not-required",
            "same-canonical-loop",
            "ambiguous-mode-one-question",
            "code-scout",
            "implementer",
            "neutral-build",
            "active-contract-queue",
            "IMPLEMENTED_TARGETED_VERIFIED",
            "release-readiness",
            "release-blocker-audit",
            "/handoff",
            "/agents-md",
            "/harness-audit",
            "/retro",
            "/security-review",
            "OpenCode-owned /review",
            "categorized report",
            "PASS_WITH_UNVERIFIED",
            "gh api",
            "redacted path:line/type evidence",
            "user accepts each named Unverified item",
            "report before repair",
            "separate repair ownership",
            "re-review after fixes",
            "convergence-reviewer",
            "provenance boundaries",
            "five axes",
            "Critical/Important/Suggestion",
            "spec/task-first",
            "concrete fixes",
            "uncertainty/proof gates",
            "parallelism analysis",
            "no-parallel reason",
            "package/lane preservation",
            "join completeness",
            "official/API docs",
            "evidence-backed 方案",
            "UNVERIFIED before implementation",
            "complete, appropriately scoped, verified",
            "not artificially tiny",
            "risk-or-need-triggered-feedback",
            "one minimal completion check",
            "classify dirty paths",
            "approval-gated cleanup",
            "cleanup package",
            "deleting user-visible artifacts",
            "high-risk packaging stop",
            "non-trigger",
        ],
        "case_key": "cases",
        "min_cases": 6,
    },
    "skill-routing-fixtures.yaml": {
        "markers": ["aili-delivery-flow", "harness-issue-triage", "harness-evolution", "mature-project-pattern-research", "source-driven-development", "git-workflow-and-versioning", "ci-cd-and-automation", "parallel-subagent-dispatch", "spec-driven-development", "planning-and-task-breakdown", "browser-testing-with-devtools", "official/API docs", "cleanup package", "approval-gated cleanup", "trigger", "non-trigger"],
        "case_key": "cases",
        "min_cases": 6,
    },
    "subagent-dispatch-fixtures.yaml": {
        "markers": ["trace_id", "work_package_type", "artifact_target", "coverage_expectation", "known_exclusions", "evidence_anchors", "active-contract-queue", "implementer", "allowed_scope", "forbidden_scope", "edit_permission", "commit_allowance", "complete, appropriately scoped, verified", "not artificially tiny", "progress-ledger savepoint", "evidence_state", "classify dirty paths", "approval-gated cleanup", "cleanup package", "parallelism analysis", "join completeness", "package/lane preservation", "no-parallel reason", "proactive-delegation-scan", "dispatch-when-specialist-preferred", "default-two-not-hard-cap", "model-selected-bounded-fan-out", "same-message-parallel", "join-plan"],
        "case_key": "packet_cases",
        "min_cases": 3,
    },
    "verification-claim-fixtures.yaml": {
        "markers": ["sufficient-evidence", "insufficient-evidence", "Unverified", "release-blocking", "spec coverage check", "Open Question"],
        "case_key": "cases",
        "min_cases": 3,
    },
    "agents-template-fixtures.yaml": {
        "markers": ["AGENTS.md", "templates/AGENTS.md", "test-plan.md", "placement decision", "smoke"],
        "case_key": "cases",
        "min_cases": 2,
    },
    "continuity-memory-handoff-fixtures.yaml": {
        "markers": ["memory-explicit-facts", "memory-candidate", "handoff-trigger", "handoff-no-threshold-trigger", "handoff-list-bounded-history", "handoff-exact-resume", "handoff-invalid-latest", "handoff-legacy-read-only", "LATEST.md", "exactly one fenced text prompt", "resume-hydration", "artifact-integrity-documentation-only"],
        "case_key": "cases",
        "min_cases": 12,
        "package": "P3",
    },
    "dcp-removal-fixtures.yaml": {
        "markers": ["INST-005", "malformed-jsonc", "symlink-jsonc", "forbidden_interactions", "@playwright/mcp@0.0.75"],
        "case_key": "state_cases",
        "min_cases": 5,
        "package": "P4",
    },
    "cross-worktree-permission-fixtures.yaml": {
        "markers": ["aili.cross-worktree-permission-fixtures.v3", "historical_a30", "static_mandatory_case_ids", "runtime_mandatory_case_ids", "contract_mutation_ids", "attachments"],
        "case_key": None,
        "package": "P6",
    },
    "review-convergence-fixtures.yaml": {
        "markers": ["all-task-one-row", "task-audit-na-accepted-source-pass", "subagent-nesting-forbidden", "optional-specialist-join", "no-majority-vote"],
        "case_key": "cases",
        "min_cases": 25,
        "package": "P7",
    },
    "upstream-reference-fixtures.yaml": {
        "markers": ["addy-idea-refine", "positive", "near-miss", "negative", "upstream_runnable"],
        "case_key": "cases",
        "min_cases": 15,
        "package": "P8",
    },
    "graphify-local-review-fixtures.yaml": {
        "markers": ["official-upstream-navigation", "architecture-existing-graph", "exact-current-symbol", "local-review-existing-output-only", "no-auto-run", "non-authoritative"],
        "case_key": "cases",
        "min_cases": 12,
        "package": "P9",
    },
    "generated-openspec-adapter-fixtures.yaml": {
        "markers": ["canonical-four-routes-own-gates", "direct-output-no-aili-claim", "lp-identity-natural-decomposed-normalizes-reuse", "automation-modify-documentation-mixed-block"],
        "case_key": "package_2_cases",
        "min_cases": 80,
        "package": "P2",
    },
    "workflow-orchestration-fixtures.yaml": {
        "markers": ["aggregate_traceability", "DEF-E3-TASK-CHECKLIST-AUDIT", "required_fixture_ids", "tests/opencode-permission-probe.test.mjs"],
        "case_key": "cases",
        "min_cases": 17,
        "package": "P11",
    },
}


def load_fixture(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"{path}: not parseable by stdlib JSON subset: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"{path}: top-level value must be an object")
    return data


def contains_marker(data: object, marker: str) -> bool:
    if isinstance(data, str):
        return marker in data
    if isinstance(data, list):
        return any(contains_marker(item, marker) for item in data)
    if isinstance(data, dict):
        return any(marker in str(key) or contains_marker(value, marker) for key, value in data.items())
    return False


def validate_fixture(name: str, spec: dict) -> list[str]:
    errors: list[str] = []
    path = FIXTURE_DIR / name
    if not path.exists():
        return [f"missing fixture: {path}"]

    if spec.get("format") == "text-yaml":
        text = path.read_text(encoding="utf-8")
        fixture_cases = re.findall(
            r"^\s*- id:\s*(\S+)\s*\n\s+expected:\s*([^\n]+)\s*$",
            text,
            re.MULTILINE,
        )
        data = {
            "cases": [{"id": case_id, "expected": expected.strip()} for case_id, expected in fixture_cases],
            "text": text,
        }
    else:
        try:
            data = load_fixture(path)
        except ValueError as exc:
            return [str(exc)]

    if name == "cross-worktree-permission-fixtures.yaml":
        a33 = data.get("a33", {})
        static_ids = a33.get("static_mandatory_case_ids", []) if isinstance(a33, dict) else []
        runtime_ids = a33.get("runtime_mandatory_case_ids", []) if isinstance(a33, dict) else []
        cases = [
            {"id": case_id}
            for case_id in [*static_ids, *runtime_ids]
            if isinstance(case_id, str)
        ]
    else:
        cases = data.get(spec["case_key"])
        if not isinstance(cases, list) or len(cases) < spec["min_cases"]:
            errors.append(f"{name}: expected at least {spec['min_cases']} cases in {spec['case_key']}")

    marker_data = {key: value for key, value in data.items() if key != "required_markers"}
    for marker in spec["markers"]:
        if not contains_marker(marker_data, marker):
            errors.append(f"{name}: missing required marker {marker!r}")

    if name == "command-routing-fixtures.yaml" and isinstance(cases, list):
        errors.extend(validate_command_routing(cases, name))
    if name == "skill-routing-fixtures.yaml" and isinstance(cases, list):
        errors.extend(validate_skill_routing(cases, name))
    if name == "verification-claim-fixtures.yaml" and isinstance(cases, list):
        errors.extend(validate_verification_claims(cases, name))
    if name == "subagent-dispatch-fixtures.yaml" and isinstance(cases, list):
        errors.extend(validate_subagent_dispatch(cases, name, data))
    if name in {
        "continuity-memory-handoff-fixtures.yaml",
        "dcp-removal-fixtures.yaml",
        "cross-worktree-permission-fixtures.yaml",
        "review-convergence-fixtures.yaml",
        "upstream-reference-fixtures.yaml",
        "graphify-local-review-fixtures.yaml",
        "generated-openspec-adapter-fixtures.yaml",
    }:
        errors.extend(validate_package_fixture(name, data, cases))

    return errors


def find_trigger_case(cases: list, expected_mode: str) -> dict | None:
    for case in cases:
        if isinstance(case, dict) and case.get("expected_mode") == expected_mode and case.get("trigger") is True:
            return case
    return None


def require_checks(case: dict, field: str, required: list[str], name: str, case_id: str) -> list[str]:
    errors: list[str] = []
    checks = case.get(field)
    if not isinstance(checks, list):
        return [f"{name}: {case_id} missing list field {field}"]
    for required_check in required:
        if required_check not in checks:
            errors.append(f"{name}: {case_id} {field} missing {required_check!r}")
    return errors


def require_exact_checks(case: dict, field: str, expected: list[str], name: str, case_id: str) -> list[str]:
    checks = case.get(field)
    if not isinstance(checks, list):
        return [f"{name}: {case_id} missing list field {field}"]
    if checks != expected:
        return [f"{name}: {case_id} {field} must be exactly {expected!r}"]
    return []


def section_between(text: str, start_marker: str, end_marker: str) -> str:
    start = text.find(start_marker)
    if start == -1:
        return ""
    end = text.find(end_marker, start + len(start_marker))
    if end == -1:
        return text[start:]
    return text[start:end]


def require_text_markers(relative_path: str, markers: list[str], label: str | None = None) -> list[str]:
    errors: list[str] = []
    path = ROOT / relative_path
    if not path.exists():
        return [f"{relative_path}: missing {label or 'contract'} file"]
    text = path.read_text(encoding="utf-8")
    for marker in markers:
        if marker not in text:
            errors.append(f"{relative_path}: missing {label or 'contract'} marker {marker!r}")
    return errors


def require_absent_in_section(relative_path: str, section: str, forbidden: list[str], label: str) -> list[str]:
    errors: list[str] = []
    lowered = section.lower()
    for marker in forbidden:
        if marker.lower() in lowered:
            errors.append(f"{relative_path}: {label} must not contain {marker!r}")
    return errors


def canonical_task_ids() -> tuple[list[str], list[str]]:
    errors: list[str] = []
    catalog_path = FIXTURE_DIR / "workflow-orchestration-fixtures.yaml"
    try:
        catalog = load_fixture(catalog_path).get("aggregate_traceability", {}).get("task_evidence_catalog")
    except ValueError as exc:
        return [], [str(exc)]
    if not isinstance(catalog, list):
        return [], [f"{catalog_path.name}: task_evidence_catalog must be a list"]

    catalog_ids = [row.get("task_id") if isinstance(row, dict) else None for row in catalog]
    catalog_format_valid = all(
        isinstance(task_id, str) and re.fullmatch(r"\d+\.\d+", task_id) is not None
        for task_id in catalog_ids
    )
    if (
        len(catalog_ids) != 74
        or not catalog_format_valid
        or len(catalog_ids) != len(set(catalog_ids))
    ):
        errors.append(
            f"{catalog_path.name}: task_evidence_catalog must contain exactly 74 unique task ids in N.N format"
        )

    task_path = ROOT / "openspec/changes/complete-aili-workflow-orchestration/tasks.md"
    if task_path.exists():
        task_ids = re.findall(r"^- \[[ xX]\] (\d+\.\d+)\b", task_path.read_text(encoding="utf-8"), re.MULTILINE)
        if len(task_ids) != 74 or len(task_ids) != len(set(task_ids)) or set(task_ids) != set(catalog_ids):
            errors.append(
                f"{task_path}: checklist ids must equal the tracked 74-task evidence catalog exactly once"
            )
        return task_ids, errors
    return catalog_ids, errors


def validate_package_fixture(name: str, data: dict, cases: list) -> list[str]:
    errors: list[str] = []
    ids = [case.get("id") for case in cases if isinstance(case, dict)]
    duplicate_ids = sorted({case_id for case_id in ids if ids.count(case_id) > 1})
    if duplicate_ids:
        errors.append(f"{name}: duplicate case ids {duplicate_ids}")

    required_by_name = {
        "continuity-memory-handoff-fixtures.yaml": {
            "memory-explicit-facts", "memory-candidate", "memory-ambiguous-scope",
            "handoff-content-security", "ideate-define-writeback", "define-ambiguous-change-identity",
            "handoff-trigger", "handoff-no-threshold-trigger", "handoff-list-bounded-history",
            "handoff-exact-resume", "handoff-invalid-latest", "handoff-legacy-read-only",
            "resume-hydration", "handoff-resume",
            "memory-stage1-boundary", "artifact-authority-boundaries", "artifact-integrity-documentation-only",
        },
        "review-convergence-fixtures.yaml": {
            "all-task-one-row", "task-row-missing", "task-row-duplicate", "task-row-undefined",
            "task-audit-all-five-statuses", "task-audit-na-accepted-source-pass", "pseudo-complete",
            "task-status-invalid", "unchecked-task", "stale-evidence", "task-file-mismatch",
            "task-test-mismatch", "na-without-accepted-source", "drift-unrequested",
            "subagent-nesting-forbidden", "optional-specialist-join", "no-majority-vote",
            "final-overlay-edit-attempt-denied", "review-ai-vs-product-routing",
            "review-ai-regression-vs-test-engineer-routing",
        },
        "generated-openspec-adapter-fixtures.yaml": {
            "lp-identity-natural-decomposed-normalizes-reuse", "lp-identity-reject-decomposed-nfc",
            "lp-identity-unicode-byte-oracle", "automation-modify-reject",
            "automation-mixed-documentation-block", "lp-allocation-race-recompute-once",
            "lp-allocation-second-race-block", "lp-duplicate-identity-key-hard-block",
            "routing-natural-aili-vs-direct-adapter", "routing-maximal-compound-no-write",
            "routing-bare-aili-direct-command-collision", "routing-bare-aili-direct-skill-collision",
            "routing-interval-objective-ambiguity", "routing-interval-executable-block", "lp-nfc-same-key-race",
        },
    }
    missing = sorted(required_by_name.get(name, set()) - set(ids))
    if missing:
        errors.append(f"{name}: missing required package cases {missing}")

    if name == "cross-worktree-permission-fixtures.yaml":
        historical_case_ids = [
            "effective-merged-tool-inventory", "unexpected-tool-denied", "direct-invocation-excluded",
            "seeded-parent-edit-allow-blocks", "seeded-parent-bash-allow-blocks", "seeded-parent-task-allow-blocks",
            "external-always-read-broadens", "auto-read-privacy-caveat", "mutation-capable-effective-rule-blocks",
            "clean-external-read-positive", "clean-path-ask", "edit-denied", "bash-denied", "task-denied",
            "commit-denied", "merge-denied", "apply-denied", "parent-unchanged", "target-unchanged",
            "common-dir-unchanged", "no-real-user-state",
        ]
        static_mandatory = [
            "a33-host-non-git-block", "a33-host-no-ranking", "a33-ignore-missing-block", "a33-ignore-reinclude-block", "a33-destination-tracked-block", "a33-key-valid", "a33-key-invalid-block", "a33-collision-no-guess-block", "a33-shared-trust-disclosure", "a33-hard-isolation-claim-reject", "a33-managed-20-external-deny", "a33-managed-external-ask-reject", "a33-builtins-excluded", "a33-web-profile-unchanged", "a33-install-equality", "a33-rules-narrow", "a33-rules-broaden-block", "a33-rules-conflict-block", "a33-lane-one-repository", "a33-no-recursive-host-scan", "a33-artifact-owning-repository", "a33-topology-submodule-block", "a33-path-ambiguity-block", "a33-result-null-representation", "a33-result-null-field-omission-rejected", "a33-result-not-applicable-string-misuse-rejected", "a33-result-null-wrong-type-rejected", "a33-join-static-row-null-shape", "a33-join-runtime-nonoperation-null-shape", "a33-join-runtime-operation-populated-shape", "a33-forbidden-git-block", "a33-rollback-preserves", "a33-codegraph-per-target", "a33-no-new-machinery", "a33-package-excludes-worktrees", "a33-acceptance-item43-only",
            "a33-operation-key-omission-rejected", "a33-operation-key-wrong-type-rejected", "a33-approval-key-omission-rejected", "a33-approval-key-wrong-type-rejected", "a33-identity-field-omission-rejected", "a33-identity-field-wrong-type-rejected", "a33-identity-string-sentinel-rejected", "a33-identity-populated-required-null-rejected", "a33-identity-absent-forbidden-nonnull-rejected", "a33-identity-detached-branch-mismatch-rejected", "a33-identity-file-array-invalid-rejected", "a33-identity-dirty-count-invalid-rejected",
        ]
        runtime_mandatory = [
            "a33-host-git-positive", "a33-ignore-positive", "a33-multiple-attachments", "a33-runtime-prepare-no-worktree-effect", "a33-runtime-effective-profile-observed", "a33-runtime-install-observed", "a33-runtime-nested-repository-observed", "a33-runtime-approval-positive", "a33-runtime-each-attachment-add-separate-approval", "a33-runtime-each-attachment-remove-separate-approval", "a33-runtime-add-approval-wrong-zero-effect", "a33-runtime-add-approval-reused-zero-effect", "a33-runtime-remove-approval-wrong-zero-effect", "a33-runtime-remove-approval-reused-zero-effect", "a33-runtime-fixture-add-real-approval-zero-effect", "a33-runtime-fixture-remove-real-approval-zero-effect", "a33-runtime-operation-class-mismatch-zero-effect", "a33-runtime-approval-missing-zero-effect", "a33-runtime-missing-approval-null-fields", "a33-runtime-approval-stale-zero-effect", "a33-runtime-approval-mismatched-zero-effect", "a33-runtime-approval-expired-zero-effect", "a33-runtime-approval-wrong-source-zero-effect", "a33-runtime-approval-wrong-destination-zero-effect", "a33-runtime-approval-wrong-branch-zero-effect", "a33-runtime-approval-wrong-ref-zero-effect", "a33-runtime-add-approval-reused-real-remove-zero-effect", "a33-runtime-approval-other-operation-zero-effect", "a33-runtime-approval-declined-unavailable", "a33-runtime-add-trusted-code-risk-accepted", "a33-runtime-add-trusted-code-risk-declined-zero-effect", "a33-runtime-add-trusted-code-risk-unavailable-zero-effect", "a33-runtime-remove-trusted-code-risk-not-applicable", "a33-pre-add-target-absent", "a33-add-delta-exact", "a33-add-common-dir-exact-allowed-delta", "a33-add-common-dir-identity-preserved", "a33-add-existing-branch-no-ref-reflog-creation", "a33-add-new-branch-reflog-enabled-created", "a33-add-new-branch-reflog-disabled-absent", "a33-unrelated-common-dir-preserved", "a33-add-unrelated-preserved", "a33-pre-remove-target-populated", "a33-remove-delta-exact", "a33-remove-common-dir-exact-allowed-delta", "a33-remove-common-dir-identity-preserved", "a33-remove-dirty-block", "a33-remove-unknown-block", "a33-remove-user-visible-block", "a33-remove-ignored-block", "a33-remove-untracked-block", "a33-remove-artifact-block", "a33-remove-locked-block", "a33-remove-wrong-source-block", "a33-remove-wrong-path-block", "a33-remove-missing-target-block", "a33-runtime-cleanup-after-approved-removes", "a33-runtime-cleanup-retain-registered", "a33-residual-nongoal-exit0", "a33-material-missing-exit3", "a33-contract-violation-exit5",
            "a33-common-dir-identity-change-block", "a33-add-common-dir-unrelated-mutation-block", "a33-remove-common-dir-unrelated-mutation-block", "a33-add-new-branch-reflog-enabled-missing-block", "a33-add-new-branch-reflog-disabled-unexpected-block", "a33-remove-branch-deletion-block", "a33-remove-branch-reflog-mutation-block", "a33-runtime-key-mismatch-zero-effect", "a33-runtime-identity-transition-schema",
        ]
        expected_fields = {
            "identity_fields": ["identity_state", "declared_root", "path_state", "canonical_root", "git_toplevel", "git_private_dir", "git_common_dir", "git_head", "git_branch", "detached_head", "worktree_membership", "dirty_state", "tracked_files", "untracked_files", "ignored_files", "artifact_files", "unknown_files"],
            "dirty_state_fields": ["tracked_modified", "tracked_deleted", "untracked_count", "ignored_count"],
            "delta_fields": ["target_path", "worktree_membership", "common_dir_identity", "common_dir_admin_entry", "branch_ref", "branch_reflog", "unrelated_common_dir_entries", "unrelated_refs", "config", "hooks", "unrelated_worktree_records", "unrelated_prunable_entries", "other_files"],
            "pending_operation_fields": ["operation_id", "kind", "operation_class", "source", "destination", "repo_key", "worktree_key", "branch", "base_ref", "branch_mode", "reflog_policy", "approval_required"],
            "operation_fields": ["operation_id", "kind", "operation_class", "source", "destination", "repo_key", "worktree_key", "branch", "base_ref", "branch_mode", "reflog_policy"],
            "approval_fields": ["approval_id", "run_id", "operation_id", "kind", "operation_class", "source", "destination", "repo_key", "worktree_key", "branch", "base_ref", "branch_mode", "reflog_policy", "expiry", "decision_ref", "trusted_code_risk", "status"],
            "prepare_result_fields": ["schema_version", "command", "status", "exit_code", "run_id", "run_root", "pending_operations", "worktree_effects", "unverified"],
            "operation_result_fields": ["schema_version", "command", "status", "exit_code", "run_id", "operation", "approval", "effect_started", "expected_delta", "observed_delta", "evidence_refs", "unverified"],
            "static_result_fields": ["schema_version", "command", "mode", "status", "exit_code", "mandatory_case_ids", "observed_case_ids", "case_set_equal", "cases", "contract_mutations", "summary", "unverified", "ephemeral_result"],
            "runtime_join_fields": ["schema_version", "command", "mode", "status", "exit_code", "run_id", "mandatory_case_ids", "observed_case_ids", "case_set_equal", "cases", "operations", "cleanup", "summary", "unverified", "ephemeral_result"],
            "runtime_case_fields": ["id", "subset", "status", "exit_code", "run_id", "operation_id", "approval_ref", "host_identity", "source_identity", "target_identity", "expected_delta", "observed_delta", "evidence_refs", "unverified", "cleanup_state"],
            "joined_case_fields": ["id", "subset", "status", "exit_code", "operation_id", "approval_ref", "host_identity", "source_identity", "target_identity", "expected_delta", "observed_delta", "evidence_refs", "unverified", "cleanup_state"],
            "join_result_fields": ["schema_version", "command", "mode", "status", "exit_code", "static_result_ref", "runtime_result_ref", "static_mandatory_case_ids", "runtime_mandatory_case_ids", "mandatory_case_ids", "observed_case_ids", "case_set_equal", "cases", "mutation_summary", "cleanup", "summary", "unverified"],
        }
        expected_mutations = ["a33-contract-missing-case-rejected", "a33-contract-duplicate-case-rejected", "a33-contract-extra-case-rejected", "a33-contract-skipped-case-rejected", "a33-contract-evidence-empty-case-rejected", "a33-contract-schema-mismatch-rejected"]
        expected_attachments = [
            {"repo_key": "foreign-a", "worktree_key": "existing", "branch": "fixture-existing", "base_ref": "HEAD", "branch_mode": "existing", "reflog_policy": "enabled"},
            {"repo_key": "foreign-b", "worktree_key": "create-enabled", "branch": "fixture-create-enabled", "base_ref": "HEAD", "branch_mode": "create", "reflog_policy": "enabled"},
            {"repo_key": "foreign-c", "worktree_key": "create-disabled", "branch": "fixture-create-disabled", "base_ref": "HEAD", "branch_mode": "create", "reflog_policy": "disabled"},
        ]
        historical_a30 = data.get("historical_a30", {})
        if not isinstance(historical_a30, dict):
            historical_a30 = {}
        a33 = data.get("a33", {})
        if not isinstance(a33, dict):
            a33 = {}
        expected_top_level_keys = ["schema", "version", "exit_codes", "historical_a30", "a33"]
        expected_a33_keys = [
            "mode", "provider", "destination_template", "key_pattern", "reserved_keys",
            *expected_fields,
            "contract_mutation_ids", "static_mandatory_case_ids", "runtime_mandatory_case_ids",
            "attachments", "null_semantics", "soft_boundary", "operation_scope",
        ]
        if list(data) != expected_top_level_keys:
            errors.append(f"{name}: top-level keys differ from the exact ordered v3 schema")
        if list(a33) != expected_a33_keys:
            errors.append(f"{name}: a33 keys differ from the exact ordered v3 schema")
        if data.get("schema") != "aili.cross-worktree-permission-fixtures.v3" or data.get("version") != "3.0":
            errors.append(f"{name}: schema/version must be exact v3")
        if data.get("exit_codes") != {"safe_observed": 0, "usage_or_fixture_error": 2, "blocked_or_unverified": 3, "unsafe": 5}:
            errors.append(f"{name}: exit_codes must equal the exact v3 map")
        if historical_a30.get("case_ids") != historical_case_ids:
            errors.append(f"{name}: historical_a30.case_ids must preserve the exact ordered 21-case history")
        for field, expected in expected_fields.items():
            if a33.get(field) != expected:
                errors.append(f"{name}: a33.{field} differs from the exact ordered v3 schema")
        if a33.get("static_mandatory_case_ids") != static_mandatory:
            errors.append(f"{name}: static_mandatory_case_ids differs from the exact ordered v3 set")
        if a33.get("runtime_mandatory_case_ids") != runtime_mandatory:
            errors.append(f"{name}: runtime_mandatory_case_ids differs from the exact ordered v3 set")
        observed_static = a33.get("static_mandatory_case_ids", [])
        observed_runtime = a33.get("runtime_mandatory_case_ids", [])
        observed_sets_valid = (
            isinstance(observed_static, list)
            and isinstance(observed_runtime, list)
            and all(isinstance(case_id, str) for case_id in [*observed_static, *observed_runtime])
        )
        if not observed_sets_valid or not set(observed_static).isdisjoint(observed_runtime):
            errors.append(f"{name}: observed static/runtime mandatory sets must be disjoint")
        if a33.get("contract_mutation_ids") != expected_mutations:
            errors.append(f"{name}: contract_mutation_ids must equal the exact six-mutation sequence")
        if a33.get("attachments") != expected_attachments:
            errors.append(f"{name}: attachments must equal the exact existing/create-enabled/create-disabled variants")
    elif name == "dcp-removal-fixtures.yaml":
        if data.get("owner_package") != "P4":
            errors.append(f"{name}: owner_package must be P4")
        parser_ids = {
            row.get("id") for row in data.get("parser_cases", []) if isinstance(row, dict)
        }
        expected_parser = {
            "supported-command-option", "unknown-command-option-precedence", "bare-removed-flag",
            "command-help-invalid-option", "top-level-help-precedence",
        }
        if parser_ids != expected_parser:
            errors.append(f"{name}: parser case ids differ from the exact removed-flag matrix")
    elif name == "review-convergence-fixtures.yaml":
        canonical_ids, canonical_errors = canonical_task_ids()
        errors.extend(canonical_errors)
        fixture_task_ids = data.get("task_ids")
        fixture_ids_valid = isinstance(fixture_task_ids, list) and all(
            isinstance(task_id, str) and re.fullmatch(r"\d+\.\d+", task_id) is not None
            for task_id in fixture_task_ids
        )
        if not fixture_ids_valid or set(fixture_task_ids) != set(canonical_ids) or len(fixture_task_ids) != len(set(fixture_task_ids)):
            errors.append(f"{name}: task_ids must equal all 74 canonical task checklist rows exactly once")
        expected_fields = [
            "task_id", "accepted requirement/decision/risk", "expected behavior",
            "implementation files/artifacts", "fresh tests/inspection/review evidence",
            "status", "findings", "disposition", "freshness",
        ]
        if data.get("matrix_fields") != expected_fields:
            errors.append(f"{name}: matrix_fields differs from DEF-E3 canonical order")
        if data.get("statuses") != ["Done", "Partial", "Missing", "Blocked", "N/A"]:
            errors.append(f"{name}: status vocabulary differs from DEF-E3")
        expected_overlay_agents = {
            "agents/agent-evaluator.md", "agents/ai-regression-scout.md", "agents/code-reviewer.md",
            "agents/code-scout.md", "agents/convergence-reviewer.md", "agents/doc-researcher.md",
            "agents/opensource-sanitizer.md", "agents/plan-auditor.md", "agents/pr-test-analyzer.md",
            "agents/security-auditor.md", "agents/silent-failure-reviewer.md", "agents/spec-miner.md",
            "agents/test-coverage-reviewer.md", "agents/test-engineer.md",
            "agents/web-performance-auditor.md", "agents/web-researcher.md",
        }
        overlays = data.get("final_review_overlays")
        overlay_map = {
            row.get("agent"): row for row in overlays if isinstance(row, dict)
        } if isinstance(overlays, list) else {}
        if set(overlay_map) != expected_overlay_agents or len(overlay_map) != len(overlays or []):
            errors.append(f"{name}: final review overlays must cover every read-only lane exactly once")
        for agent in sorted(expected_overlay_agents):
            row = overlay_map.get(agent, {})
            if row.get("edit") != "deny":
                errors.append(f"{name}: {agent} final overlay edit must deny")
            if row.get("task") != "deny":
                errors.append(f"{name}: {agent} final overlay task must deny")
        edit_case = next((case for case in cases if isinstance(case, dict) and case.get("id") == "final-overlay-edit-attempt-denied"), {})
        if edit_case.get("input", {}).get("overlay_edit") != "deny" or edit_case.get("expected") != "deny-before-mutation":
            errors.append(f"{name}: executable final overlay edit attempt must be denied before mutation")
        reviewer_case = next((case for case in cases if isinstance(case, dict) and case.get("id") == "review-ai-vs-product-routing"), {})
        if reviewer_case.get("input", {}).get("candidate_lanes") != ["AI-regression", "code-review", "product decision"] or "ROSE/user" not in reviewer_case.get("expected", ""):
            errors.append(f"{name}: AI-vs-product reviewer routing collision differs from the exact contract")
        routing_case = next((case for case in cases if isinstance(case, dict) and case.get("id") == "review-ai-regression-vs-test-engineer-routing"), {})
        if routing_case.get("expected") != {"ai_surface": "ai-regression-scout when a specialist is needed", "ordinary_test_surface": "test-engineer when a specialist is needed", "overlap": "ROSE selects only concrete missing capabilities; default concurrency two is not a hard cap and larger fan-out requires independent scopes, suitable owners, concrete benefit, and a join plan"}:
            errors.append(f"{name}: optional AI-regression-scout vs test-engineer routing differs from the lean contract")
        runtime_enforcement = data.get("runtime_enforcement", {})
        expected_policy = "an optional Package 12 or SHIP specialist uses a read-only edit-deny/task-deny overlay only when a concrete gap selects it"
        if runtime_enforcement.get("id") != "UV-007" or runtime_enforcement.get("policy") != expected_policy or runtime_enforcement.get("status") != "Unverified" or "do not prove current A33 runtime overlay" not in runtime_enforcement.get("reason", ""):
            errors.append(f"{name}: runtime enforcement must remain UV-007 Unverified under the exact concrete-gap policy")
    elif name == "generated-openspec-adapter-fixtures.yaml":
        by_id = {case.get("id"): case for case in cases if isinstance(case, dict)}
        exact_collisions = {
            "routing-natural-aili-vs-direct-adapter": "natural AILI BUILD route wins; direct adapter remains outside AILI and is not invoked",
            "routing-bare-aili-direct-command-collision": "ask one AILI-versus-direct-route question; zero write and execution",
            "routing-bare-aili-direct-skill-collision": "ask one AILI-versus-direct-route question; zero write and execution",
            "routing-maximal-compound-no-write": "no-write wins; zero persistence/execution; BUILD and SHIP remain unauthorized",
            "routing-interval-objective-ambiguity": "ask one documentation-protocol question; zero write and execution",
            "routing-interval-executable-block": "block executable interval request; zero mutation and LP",
            "lp-nfc-same-key-race": "one allocation may win; one re-read reuses the same key; no duplicate ID/body",
        }
        for case_id, expected in exact_collisions.items():
            if by_id.get(case_id, {}).get("expected") != expected:
                errors.append(f"{name}: exact routing collision {case_id} differs")
    elif name == "upstream-reference-fixtures.yaml":
        mappings = data.get("required_mappings", [])
        for mapping in mappings:
            kinds = {
                case.get("kind") for case in cases if isinstance(case, dict) and case.get("mapping") == mapping
            }
            if kinds != {"positive", "near-miss", "negative"}:
                errors.append(f"{name}: {mapping} must have positive/near-miss/negative cases")
        if any(case.get("upstream_runnable") is not False for case in cases if isinstance(case, dict)):
            errors.append(f"{name}: every upstream reference case must remain non-runnable")
    elif name == "graphify-local-review-fixtures.yaml":
        categories = {case.get("category") for case in cases if isinstance(case, dict)}
        if categories != set(data.get("required_categories", [])):
            errors.append(f"{name}: cases must cover every required category exactly as declared")
        contract = data.get("contract", {})
        expected_contract = {
            "cli_install": "uv tool install graphifyy",
            "global_skill_registration": "graphify install --platform agents",
            "global_skill_path": "~/.agents/skills/graphify/SKILL.md",
            "local_review_launches_graphify": False,
            "project_execution_requires_separate_approval": True,
        }
        if contract != expected_contract:
            errors.append(f"{name}: official upstream Graphify contract differs")
        by_id = {case.get("id"): case for case in cases if isinstance(case, dict)}
        expected_cases = {
            "architecture-existing-graph": "one-scoped-official-graphify-result",
            "exact-current-symbol": "codegraph-or-current-files",
            "no-auto-install": "no-uv-or-graphify-command",
            "no-auto-register": "registration-remains-separately-approved",
            "no-auto-run": "no-project-graph-command",
            "project-operation-separate": "fresh-exact-target-effect-approval",
            "official-command-packets": "literal-uv-install-and-agents-registration-packets",
            "combined-stage-approval": "reject-combined-approval",
            "separate-stage-invocations": "registration-pending-separate-invocation",
            "no-fallback-core-independent": "no-fallback-core-install-remains-independent",
            "non-authoritative": "reconcile-current-source-tests-contract",
            "current-conflict": "current-files-win-graphify-unverified",
            "no-duplicate-discovery": "no-graphify-codegraph-broad-grep-duplication",
            "upstream-owned-status": "observed-version-path-upstream-owned-only",
            "ownership-conflict": "conflict-no-reinstall-or-registration",
            "local-review-existing-output-only": "consume-bounded-result-with-current-evidence",
            "local-review-no-output": "continue-without-launching-graphify",
        }
        for case_id, expected in expected_cases.items():
            if by_id.get(case_id, {}).get("expected") != expected:
                errors.append(f"{name}: {case_id} expected must be {expected!r}")
    return errors


def validate_skill_routing(cases: list, name: str) -> list[str]:
    errors: list[str] = []
    expected_residual_cases = {
        "ci-cd-explicit-pipeline": ("ci-cd-and-automation", "trigger", "concrete CI pipeline job", None),
        "ci-cd-existing-failure": ("ci-cd-and-automation", "non-trigger", "existing failing CI typecheck gate", None),
        "parallel-dispatch-two-independent": ("parallel-subagent-dispatch", "trigger", "two fresh independent read-only subagents", None),
        "parallel-dispatch-old-task-handoff": ("parallel-subagent-dispatch", "trigger", "reuse the same old task_id", "ROSE re-evaluates fresh Task benefit; never reuse old task_id"),
        "spec-formal-contract": ("spec-driven-development", "trigger", "durable specification", None),
        "spec-ordinary-bounded-edit": ("spec-driven-development", "non-trigger", "ordinary bounded typo", None),
        "planning-explicit-packages": ("planning-and-task-breakdown", "trigger", "dependency-ordered implementation packages", None),
        "planning-clear-eight-file-edit": ("planning-and-task-breakdown", "non-trigger", "eight files", None),
        "browser-direct-evidence": ("browser-testing-with-devtools", "trigger", "direct Playwright console and POST evidence", None),
        "browser-source-fix-handoff": ("browser-testing-with-devtools", "trigger", "browser evidence identifies a source fix", "return source fix and durable test-plan needs to ROSE"),
    }
    for case_id, (skill, expected, input_marker, handoff) in expected_residual_cases.items():
        matches = [case for case in cases if isinstance(case, dict) and case.get("id") == case_id]
        if len(matches) != 1:
            errors.append(f"{name}: expected exactly one {case_id} case")
            continue
        case = matches[0]
        if case.get("skill") != skill:
            errors.append(f"{name}: {case_id} skill must be {skill!r}")
        if case.get("expected") != expected:
            errors.append(f"{name}: {case_id} expected must be {expected!r}")
        if input_marker not in str(case.get("input", "")):
            errors.append(f"{name}: {case_id} input must contain {input_marker!r}")
        if handoff is not None and case.get("expected_handoff") != handoff:
            errors.append(f"{name}: {case_id} expected_handoff must be {handoff!r}")

    mature_cases = {
        case.get("id"): case
        for case in cases
        if isinstance(case, dict) and case.get("skill") == "mature-project-pattern-research"
    }
    expected_cases = {
        "mature-project-prior-art": ("trigger", "mature public project patterns"),
        "mature-project-chinese-others": ("trigger", "看看别人怎么做"),
        "mature-project-github-others": ("trigger", "GitHub 上别人怎么做"),
        "mature-project-look-others": ("trigger", "look at how others do it"),
        "mature-project-reference-projects": ("trigger", "reference mature projects"),
        "mature-project-local-review": ("non-trigger", "local code implementation"),
        "mature-project-github-issue-pr-triage": ("non-trigger", "GitHub issue and PR"),
    }
    for case_id, (expected, input_marker) in expected_cases.items():
        case = mature_cases.get(case_id)
        if case is None:
            errors.append(f"{name}: missing {case_id} case for mature-project-pattern-research")
        elif case.get("expected") != expected:
            errors.append(f"{name}: {case_id} expected must be {expected!r}")
        elif input_marker not in str(case.get("input", "")):
            errors.append(f"{name}: {case_id} input must contain {input_marker!r}")

    source_cases = {
        case.get("id"): case
        for case in cases
        if isinstance(case, dict) and case.get("skill") == "source-driven-development"
    }
    expected_source_cases = {
        "source-driven-official-api-docs": "official/API docs",
        "source-driven-deepseek-fast-changing": "DeepSeek API docs",
        "source-driven-model-uncertainty": "uncertain",
    }
    for case_id, input_marker in expected_source_cases.items():
        case = source_cases.get(case_id)
        if case is None:
            errors.append(f"{name}: missing {case_id} case for source-driven-development")
        elif case.get("expected") != "trigger":
            errors.append(f"{name}: {case_id} expected must be 'trigger'")
        elif input_marker not in str(case.get("input", "")):
            errors.append(f"{name}: {case_id} input must contain {input_marker!r}")

    git_cases = {
        case.get("id"): case
        for case in cases
        if isinstance(case, dict) and case.get("skill") == "git-workflow-and-versioning"
    }
    cleanup_case = git_cases.get("git-workflow-cleanup-gate")
    if cleanup_case is None:
        errors.append(f"{name}: missing git-workflow-cleanup-gate case for git-workflow-and-versioning")
    elif cleanup_case.get("expected") != "trigger":
        errors.append(f"{name}: git-workflow-cleanup-gate expected must be 'trigger'")
    else:
        cleanup_input = str(cleanup_case.get("input", ""))
        for marker in ["branch/status", "classify dirty paths", "cleanup package", "approval-gated cleanup"]:
            if marker not in cleanup_input:
                errors.append(f"{name}: git-workflow-cleanup-gate input must contain {marker!r}")

    return errors


def validate_command_routing(cases: list, name: str) -> list[str]:
    errors: list[str] = []
    for mode, scope in [("IDEATE", "evidence-scouting"), ("DEFINE", "artifact-fan-out"), ("BUILD", "implementation-quality"), ("SHIP", "release-readiness")]:
        case = find_trigger_case(cases, mode)
        if case is None:
            errors.append(f"{name}: missing trigger case for {mode}")
        elif case.get("expected_scope") != scope:
            errors.append(f"{name}: {mode} expected_scope must be {scope!r}")

    neutral = [case for case in cases if isinstance(case, dict) and case.get("id") == "cmd-build-neutral-queue"]
    if not neutral:
        errors.append(f"{name}: missing cmd-build-neutral-queue")
    else:
        case = neutral[0]
        if case.get("expected_execution") != "neutral-build" or case.get("package_gate") != "no-per-package-gate":
            errors.append(f"{name}: neutral BUILD must use no per-package gate")
        if case.get("expected_package_source") != "active-contract-queue" or case.get("final_gate") != "minimal-changed-scope-completion-check" or case.get("success_state") != "IMPLEMENTED_TARGETED_VERIFIED":
            errors.append(f"{name}: neutral BUILD must derive the active-contract queue and stop at the minimal completion check")
        if case.get("target_repo_root") != "user-selected-git-startup-root" or case.get("cwd_authority") != "startup-git-host-only":
            errors.append(f"{name}: neutral BUILD must preserve the user-selected Git startup host")
        if case.get("build_to_ship") != "fresh-intent-required":
            errors.append(f"{name}: neutral BUILD must not preauthorize SHIP")
        errors.extend(require_checks(case, "queue_inputs", ["tasks.md", "specs", "design", "test-plan.md", "repository-evidence"], name, "neutral BUILD"))

    for case in cases:
        if isinstance(case, dict) and case.get("expected_mode") == "BUILD":
            if case.get("expected_checks") or case.get("expected_conditional_checks"):
                errors.append(f"{name}: {case.get('id')} encodes a forbidden per-package mandatory quality gate")

    define = find_trigger_case(cases, "DEFINE")
    if define is not None and define.get("expected_readiness") != ["READY", "BLOCKED"]:
        errors.append(f"{name}: DEFINE readiness must be exactly READY or BLOCKED")
    ship = find_trigger_case(cases, "SHIP")
    if ship is not None and (ship.get("fresh_intent") is not True or ship.get("automatic_full_matrix") is not False):
        errors.append(f"{name}: SHIP must require fresh intent without an automatic full matrix")

    local_modes = {case.get("target_mode") for case in cases if isinstance(case, dict) and case.get("expected_mode") == "LOCAL_REVIEW" and case.get("trigger") is True}
    for target_mode in ["default-local-changes", "base-branch", "commit", "pr", "OpenSpec change", "focus-adversarial", "repair"]:
        if target_mode not in local_modes:
            errors.append(f"{name}: missing /local-review target mode {target_mode!r}")

    utility_cases = {
        "handoff": "explicit-repository-handoff",
        "agents-md": "project-agents-template",
        "harness-audit": "report-first-harness-audit",
        "retro": "approved-evidence-retrospective",
        "security-review": "preview-first-security-review",
    }
    by_id = {case.get("id"): case for case in cases if isinstance(case, dict)}
    for command, expected_scope in utility_cases.items():
        case = by_id.get(f"cmd-{command}")
        if case is None:
            errors.append(f"{name}: missing /{command} Utility Command case")
        elif case.get("expected_mode") != "UTILITY" or case.get("expected_scope") != expected_scope or case.get("trigger") is not True:
            errors.append(f"{name}: /{command} must be a triggered non-lifecycle Utility Command")

    for command in ["/aili-doctor", "/simplify"]:
        matching = [case for case in cases if isinstance(case, dict) and str(case.get("input", "")).startswith(command)]
        if not matching or any(case.get("trigger") is not False for case in matching):
            errors.append(f"{name}: {command} must be a covered non-trigger")

    for internal_command in ["/research", "/review", "/release-blocker-audit"]:
        matching = [case for case in cases if isinstance(case, dict) and str(case.get("input", "")).startswith(internal_command)]
        if not matching or any(case.get("trigger") is not False for case in matching):
            errors.append(f"{name}: {internal_command} must remain a covered non-trigger")

    natural_routes = {
        "natural-ideate-zh": ("IDEATE", "/ideate", "先帮我想几种方案，暂时不要实现"),
        "natural-define-zh": ("DEFINE", "/define", "把这个需求定义成可实施方案和测试计划，先不要实现"),
        "natural-build-zh": ("BUILD", "/build", "按已经接受的方案和测试计划开始实现"),
        "natural-ship-zh": ("SHIP", "/ship", "把已实现的改动收尾并准备交付"),
        "natural-ideate-en": ("IDEATE", "/ideate", "Explore a few options before we implement anything"),
        "natural-define-en": ("DEFINE", "/define", "Turn this requirement into an implementation-ready contract and test plan without implementing it"),
        "natural-build-en": ("BUILD", "/build", "Implement the accepted change and test plan"),
        "natural-ship-en": ("SHIP", "/ship", "Close out the implemented change for delivery"),
    }
    for case_id, (mode, shortcut, exact_input) in natural_routes.items():
        case = by_id.get(case_id, {})
        if case.get("entrypoint") != "natural-language" or case.get("expected_mode") != mode or case.get("trigger") is not True:
            errors.append(f"{name}: {case_id} must be a positive natural-language {mode} route")
        if case.get("same_contract_as") != shortcut or case.get("slash_required") is not False:
            errors.append(f"{name}: {case_id} must enter the same {shortcut} contract without slash syntax")
        if case.get("input") != exact_input or exact_input.lstrip().startswith("/"):
            errors.append(f"{name}: {case_id} must preserve its exact non-slash semantic input")
    near_misses = {
        "natural-explanation-near-miss": "解释 IDEATE 和 DEFINE 的区别",
        "natural-status-near-miss": "现在 BUILD 到哪一步了",
        "natural-translation-near-miss": "把 SHIP 翻译成中文",
    }
    for case_id, exact_input in near_misses.items():
        near_miss = by_id.get(case_id, {})
        if near_miss.get("input") != exact_input or near_miss.get("expected_mode") != "ordinary-chat" or near_miss.get("trigger") is not False or near_miss.get("expected") != "non-trigger":
            errors.append(f"{name}: {case_id} must remain an exact ordinary natural-language near miss")
    ambiguous = by_id.get("natural-ambiguous-lifecycle", {})
    if ambiguous.get("input") != "继续这个改动" or ambiguous.get("expected") != "ambiguous-mode-one-question" or ambiguous.get("trigger") is not False or ambiguous.get("question_count") != 1 or ambiguous.get("mutation") is not False or ambiguous.get("persistence") is not False:
        errors.append(f"{name}: ambiguous natural-language lifecycle intent must ask exactly one question with zero mutation/persistence")
    baseline_no_trigger_ids = [
        "cmd-ideate", "cmd-define", "cmd-build", "cmd-ship",
        "natural-ideate-zh", "natural-define-zh", "natural-build-zh", "natural-ship-zh",
        "natural-ideate-en", "natural-define-en", "natural-build-en", "natural-ship-en",
    ]
    for case_id in baseline_no_trigger_ids:
        case = by_id.get(case_id, {})
        if case.get("delegation_scan") != "required" or case.get("task_trigger_evidence") != [] or case.get("expected_delegation") != []:
            errors.append(f"{name}: {case_id} must scan and remain direct when no Task trigger exists")
    neutral_build = by_id.get("cmd-build-neutral-queue", {})
    if neutral_build.get("delegation_scan") != "required" or not isinstance(neutral_build.get("task_trigger_evidence"), list):
        errors.append(f"{name}: cmd-build-neutral-queue must run a delegation scan and record conditional lane evidence")
    for case in cases:
        if not isinstance(case, dict):
            continue
        expected = case.get("expected_delegation")
        evidence = case.get("task_trigger_evidence")
        if isinstance(expected, list) and expected and (not isinstance(evidence, list) or not evidence):
            errors.append(f"{name}: {case.get('id')} must not expect delegation without Task-trigger evidence")
    if neutral_build.get("expected_delegation") != "eligible-lanes-only":
        errors.append(f"{name}: neutral BUILD delegation must remain conditional on eligible lanes")
    explicit = by_id.get("natural-build-explicit-subagents", {})
    if explicit.get("input") != "Use subagents to implement two independent accepted packages" or explicit.get("expected_mode") != "BUILD" or explicit.get("same_contract_as") != "/build" or explicit.get("task_trigger_evidence") != ["explicit-user-request", "two-independent-units"] or explicit.get("expected_delegation") != ["implementer", "implementer"] or explicit.get("join_plan") != "required":
        errors.append(f"{name}: explicit natural-language BUILD subagent request must dispatch two eligible implementer lanes with a join plan")
    for relative in ["agents/rose.md", "templates/opencode-global-AGENTS.md", ".agents/skills/aili-delivery-flow/SKILL.md"]:
        errors.extend(require_text_markers(relative, ["first-class lifecycle entr", "do not ask the user to restate"], "natural-language routing"))
    return errors


def validate_verification_claims(cases: list, name: str) -> list[str]:
    errors: list[str] = []
    release_blocker_cases = [
        case
        for case in cases
        if isinstance(case, dict) and case.get("id") == "release-blocking-unresolved"
    ]
    if not release_blocker_cases:
        return [f"{name}: missing release-blocking-unresolved case"]

    case = release_blocker_cases[0]
    if case.get("expected") != "reject":
        errors.append(f"{name}: release-blocking-unresolved expected must be 'reject'")
    evidence = case.get("evidence")
    if not isinstance(evidence, list) or not contains_marker(evidence, "release-blocking"):
        errors.append(f"{name}: release-blocking-unresolved evidence must mention 'release-blocking'")
    if "ready" not in str(case.get("claim", "")):
        errors.append(f"{name}: release-blocking-unresolved claim should exercise a ready claim")

    coverage_cases = [
        case
        for case in cases
        if isinstance(case, dict) and case.get("id") == "spec-coverage-uncovered"
    ]
    if not coverage_cases:
        errors.append(f"{name}: missing spec-coverage-uncovered case")
    else:
        coverage_case = coverage_cases[0]
        if coverage_case.get("expected") != "reject":
            errors.append(f"{name}: spec-coverage-uncovered expected must be 'reject'")
        coverage_evidence = coverage_case.get("evidence")
        if not isinstance(coverage_evidence, list) or not contains_marker(coverage_evidence, "spec coverage check"):
            errors.append(f"{name}: spec-coverage-uncovered evidence must mention 'spec coverage check'")
        if not contains_marker(coverage_evidence, "Open Question") or not contains_marker(coverage_evidence, "Unverified"):
            errors.append(f"{name}: spec-coverage-uncovered evidence must label uncovered items Open Question and Unverified")

    return errors


def validate_subagent_dispatch(cases: list, name: str, data: dict) -> list[str]:
    errors: list[str] = []
    case_ids = [case.get("id") for case in cases if isinstance(case, dict)]
    trace_ids = [case.get("trace_id") for case in cases if isinstance(case, dict)]
    if len(case_ids) != len(cases) or len(case_ids) != len(set(case_ids)):
        errors.append(f"{name}: packet cases must be objects with unique ids")
    if any(not isinstance(trace_id, str) or not trace_id for trace_id in trace_ids) or len(trace_ids) != len(set(trace_ids)):
        errors.append(f"{name}: packet trace_ids must be present and unique")
    goal_packets = [case for case in cases if isinstance(case, dict) and case.get("id") == "packet-build-neutral-package"]
    if not goal_packets:
        return [f"{name}: missing packet-build-neutral-package case"]

    packet = goal_packets[0]
    expected_scalars = {
        "agent": "implementer",
        "artifact_target": "active-contract-queue",
        "allowed_scope": "one active-contract package",
        "edit_permission": "package-scoped",
        "commit_allowance": "none-without-exact-approval",
    }
    for field, expected in expected_scalars.items():
        if packet.get(field) != expected:
            errors.append(f"{name}: packet-build-neutral-package {field} must be {expected!r}")
    errors.extend(require_checks(packet, "forbidden_scope", ["out-of-scope packages", "high-risk gates without approval", "package-local mandatory quality gate", "automatic test", "automatic commit", "package approval"], name, "packet-build-neutral-package"))
    errors.extend(require_checks(packet, "parallelism_analysis", ["parallelism analysis", "no-parallel reason", "join completeness", "package/lane preservation"], name, "packet-build-neutral-package"))
    errors.extend(require_checks(packet, "join_contract", ["join points", "blockers", "expected evidence"], name, "packet-build-neutral-package"))
    errors.extend(require_checks(packet, "required_evidence", ["evidence_anchors", "changed_files", "scope_boundary", "progress-ledger savepoint"], name, "packet-build-neutral-package"))
    errors.extend(require_checks(packet, "savepoint_fields", ["scope", "files_changed", "unresolved_items", "evidence_state", "next_package"], name, "packet-build-neutral-package"))
    errors.extend(require_checks(packet, "implementation_objective", ["complete, appropriately scoped, verified", "complete task-scoped", "not artificially tiny"], name, "packet-build-neutral-package"))
    if packet.get("review_repair", "missing") is not None:
        errors.append(f"{name}: packet-build-neutral-package review_repair must be null for implementation-only packages")
    errors.extend(
        require_checks(
            packet,
            "cleanup_gate",
            [
                "branch/status",
                "classify dirty paths",
                "task-scoped",
                "unrelated/pre-existing",
                "generated/ignored",
                "scratch",
                "unknown",
                "cleanup proposal",
                "approval-gated cleanup",
                "push",
                "destructive clean/reset",
                "branch deletion",
                "worktree removal",
                "OpenSpec archive",
                "stashing unrelated changes",
                "deleting user-visible artifacts",
                "task-scoped verified commits",
                "cleanup package",
            ],
            name,
            "packet-build-neutral-package",
        )
    )

    conflict_packets = [case for case in cases if isinstance(case, dict) and case.get("id") == "packet-shared-edit-conflict"]
    if not conflict_packets:
        errors.append(f"{name}: missing packet-shared-edit-conflict case")
    else:
        conflict = conflict_packets[0]
        errors.extend(require_checks(conflict, "parallelism_analysis", ["shared scaffold/source-of-truth work", "no-parallel reason", "shared mutable state", "later fan-out after join"], name, "packet-shared-edit-conflict"))
        errors.extend(require_checks(conflict, "forbidden_scope", ["parallel edits to same file"], name, "packet-shared-edit-conflict"))
        if conflict.get("expected") != "reject-parallel-shared-edit":
            errors.append(f"{name}: shared-edit conflict must reject parallel execution")

    by_id = {case.get("id"): case for case in cases if isinstance(case, dict)}
    proactive = by_id.get("packet-proactive-eligible", {})
    if proactive.get("scan") != "proactive-delegation-scan" or proactive.get("expected") != "dispatch-when-specialist-preferred" or proactive.get("timing") != "before duplicate direct work":
        errors.append(f"{name}: specialist-preferred work must dispatch from the proactive scan before duplicate direct work")
    preferred = by_id.get("packet-proactive-eligible", {})
    if (
        preferred.get("clear_bounded_package") is not True
        or preferred.get("non_trivial") is not True
        or preferred.get("matching_specialist") != "code-scout"
        or preferred.get("effective_capabilities") is not True
        or preferred.get("effective_permissions") is not True
        or preferred.get("ownership_overlap") is not False
        or preferred.get("expected") != "dispatch-when-specialist-preferred"
    ):
        errors.append(f"{name}: packet-proactive-eligible must cover every specialist-preferred dispatch condition")
    direct_exceptions = {
        "packet-direct-trivial": "trivial",
        "packet-direct-clarification": "contract-clarification-or-splitting",
        "packet-direct-no-specialist": "no-matching-specialist",
        "packet-direct-capability": "permission-or-capability-failure",
        "packet-direct-overlap": "overlapping-ownership",
        "packet-direct-negative-benefit": "concrete-negative-benefit",
    }
    for case_id, exception in direct_exceptions.items():
        case = by_id.get(case_id, {})
        if case.get("direct_exception") != exception or case.get("expected") != "ROSE-direct-with-named-exception":
            errors.append(f"{name}: {case_id} must preserve the {exception} direct-work exception")
    solution_architect = by_id.get("packet-solution-architect", {})
    if (
        solution_architect.get("agent") != "solution-architect"
        or solution_architect.get("expected") != "proposal-evidence-returned-to-ROSE"
        or not isinstance(solution_architect.get("forbidden_scope"), list)
        or any(item not in solution_architect["forbidden_scope"] for item in ["implementation", "nested delegation", "architecture acceptance", "product decision", "ADR approval", "final verdict"])
    ):
        errors.append(f"{name}: solution-architect must remain a bounded non-implementing, non-delegating proposal Worker")
    fanout = by_id.get("packet-model-selected-fanout", {})
    if fanout.get("default_policy") != "default-two-not-hard-cap" or fanout.get("hard_cap", "missing") is not None:
        errors.append(f"{name}: concurrency must default to two without a hard cap")
    allowed_owners = {path.stem for path in (ROOT / "agents").glob("*.md")} - {"rose"}
    allowed_owners.update({"explore", "general"})

    def scope_parts(value: object) -> tuple[str, ...] | None:
        if not isinstance(value, str) or not value:
            return None
        path = Path(value)
        if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
            return None
        return path.parts

    def scopes_overlap(values: list[str]) -> bool:
        parts = [scope_parts(value) for value in values]
        if any(value is None for value in parts):
            return True
        concrete = [value for value in parts if value is not None]
        return any(
            left == right[:len(left)] or right == left[:len(right)]
            for index, left in enumerate(concrete)
            for right in concrete[index + 1:]
        )

    units = fanout.get("eligible_units")
    valid_units = isinstance(units, list) and len(units) > 2 and all(
        isinstance(unit, dict)
        and list(unit) == ["id", "scope", "owner"]
        and all(isinstance(unit.get(field), str) and unit.get(field) for field in ("id", "scope", "owner"))
        and unit.get("owner") in allowed_owners
        and scope_parts(unit.get("scope")) is not None
        for unit in units
    )
    unit_ids = [unit["id"] for unit in units] if valid_units else []
    unit_scopes = [unit["scope"] for unit in units] if valid_units else []
    if not valid_units or len(unit_ids) != len(set(unit_ids)) or len(unit_scopes) != len(set(unit_scopes)) or scopes_overlap(unit_scopes):
        errors.append(f"{name}: larger fan-out units must have unique non-overlapping scopes and available owners")
    if fanout.get("selected_concurrency") != len(unit_ids) or any(fanout.get(field) is not True for field in ("independent", "non_overlapping", "clear_benefit", "owners_available")):
        errors.append(f"{name}: selected fan-out must equal eligible independent non-overlapping beneficial owned units")
    join_plan = fanout.get("join_plan")
    valid_join = isinstance(join_plan, dict) and list(join_plan) == ["id", "owner", "inputs", "expected"] and join_plan.get("id") == "join-plan" and join_plan.get("owner") == "ROSE" and join_plan.get("inputs") == unit_ids and join_plan.get("expected") == "integrated evidence"
    if fanout.get("selection") != "model-selected-bounded-fan-out" or fanout.get("dispatch_shape") != "same-message-parallel" or not valid_join:
        errors.append(f"{name}: larger fan-out must be model-selected, same-message, and join-planned")
    overlap_case = by_id.get("packet-overlap-rejected", {})
    overlap_units = overlap_case.get("eligible_units")
    overlap_scopes = [unit.get("scope") for unit in overlap_units if isinstance(unit, dict)] if isinstance(overlap_units, list) else []
    if overlap_case.get("expected") != "reject-overlapping-scopes" or not scopes_overlap(overlap_scopes):
        errors.append(f"{name}: ancestor/descendant scope overlap must have an executable rejection case")
    owner_case = by_id.get("packet-unavailable-owner-rejected", {})
    owner_units = owner_case.get("eligible_units")
    unavailable = [unit.get("owner") for unit in owner_units if isinstance(unit, dict) and unit.get("owner") not in allowed_owners] if isinstance(owner_units, list) else []
    if owner_case.get("expected") != "reject-unavailable-owner" or not unavailable:
        errors.append(f"{name}: unavailable owner must have an executable rejection case")
    reevaluation = by_id.get("packet-stage-reevaluation", {})
    if reevaluation.get("expected") != "rerun-proactive-delegation-scan" or reevaluation.get("old_task_id_reused") is not False:
        errors.append(f"{name}: changed evidence must rerun the scan without task_id reuse")
    preference = by_id.get("packet-user-aggressive-preference", {})
    if preference.get("expected") != "re-evaluate-and-dispatch-each-eligible-stage" or preference.get("permission_gates_preserved") is not True:
        errors.append(f"{name}: aggressive user preference must increase eligible dispatch without weakening permission gates")
    direct = by_id.get("packet-ineligible-direct", {})
    if direct.get("eligible_trigger") is not False or direct.get("reason_required") is not True or direct.get("reason") not in {"trivial", "contract-clarification-or-splitting", "no-matching-specialist", "permission-or-capability-failure", "overlapping-ownership", "concrete-negative-benefit"}:
        errors.append(f"{name}: ineligible direct work must retain a concrete no-dispatch reason")
    for relative in ["agents/rose.md", ".agents/skills/aili-delivery-flow/references/direct-vs-delegated-work.md", ".agents/skills/parallel-subagent-dispatch/SKILL.md"]:
        errors.extend(require_text_markers(relative, ["proactive delegation scan", "not a hard cap", "join plan"], "proactive delegation"))

    result_cases = data.get("result_cases")
    if not isinstance(result_cases, list):
        return [*errors, f"{name}: result_cases must be a list"]
    result_ids = [case.get("id") for case in result_cases if isinstance(case, dict)]
    required_result_ids = {
        "result-pass", "final-review-subagent-non-nesting", "final-review-test-engineer-edit-denied",
        "result-old-task-followup-rejected", "result-partial-no-auto-retry", "result-subagent-final-verdict-rejected",
    }
    if len(result_ids) != len(result_cases) or set(result_ids) != required_result_ids or len(result_ids) != len(set(result_ids)):
        errors.append(f"{name}: result cases must equal the six required unique safety cases")
    results = {case.get("id"): case for case in result_cases if isinstance(case, dict)}
    statuses = {"completed", "partial", "blocked", "unverified"}
    confidences = {"HIGH", "MED", "LOW", "VERY LOW", "UNKNOWN"}
    for result_id, result in results.items():
        if result.get("status") not in statuses or result.get("confidence") not in confidences:
            errors.append(f"{name}: {result_id} must use canonical status and confidence enums")
    valid_result = results.get("result-pass", {})
    if valid_result.get("status") != "completed" or valid_result.get("confidence") != "HIGH" or not valid_result.get("evidence_anchors") or not valid_result.get("inspected_scope") or not valid_result.get("checks") or valid_result.get("freshness") != "fresh" or valid_result.get("skipped_checks") != [] or valid_result.get("blockers") != [] or valid_result.get("unverified") != [] or valid_result.get("findings") != [] or "final_verdict" not in valid_result or valid_result.get("final_verdict") is not None:
        errors.append(f"{name}: valid result must use canonical completed/HIGH evidence fields without a final verdict")
    non_nesting = results.get("final-review-subagent-non-nesting", {})
    if non_nesting.get("subagent_calls") != 0 or non_nesting.get("returns_to") != "ROSE" or non_nesting.get("majority_vote") is not False or non_nesting.get("overlay") != {"edit": "deny", "task": "deny"}:
        errors.append(f"{name}: final-review result must remain non-nesting and return to ROSE")
    denied_edit = results.get("final-review-test-engineer-edit-denied", {})
    if denied_edit.get("status") != "blocked" or denied_edit.get("overlay") != {"edit": "deny", "task": "deny"}:
        errors.append(f"{name}: read-only test lane mutation must be denied")
    old_task = results.get("result-old-task-followup-rejected", {})
    if old_task.get("old_task_id_supplied") is not True or old_task.get("expected") != "reject-old-task-id":
        errors.append(f"{name}: old task_id follow-up must be rejected")
    partial = results.get("result-partial-no-auto-retry", {})
    if partial.get("status") != "partial" or partial.get("automatic_fresh_retry") is not False or partial.get("expected") != "return-gap-to-ROSE":
        errors.append(f"{name}: partial result must not trigger an automatic fresh retry")
    final_verdict = results.get("result-subagent-final-verdict-rejected", {})
    if final_verdict.get("status") != "blocked" or final_verdict.get("attempted_verdict") != "PASS" or final_verdict.get("expected") != "return-to-ROSE-no-final-verdict":
        errors.append(f"{name}: subagent final verdict attempts must return to ROSE")

    return errors


def validate_agent_permissions() -> list[str]:
    errors: list[str] = []
    paths = sorted((ROOT / "agents").glob("*.md"))
    if len(paths) != 21:
        errors.append(f"agent inventory: expected 21 files, found {len(paths)}")
    headings = ["## Role", "## Goal", "## Success criteria", "## Constraints", "## Tools", "## Output", "## Stop"]
    for path in paths:
        text = path.read_text(encoding="utf-8")
        if not text.startswith("---\n") or "\n---\n" not in text[4:]:
            errors.append(f"{path.relative_to(ROOT)}: invalid frontmatter")
            continue
        frontmatter = text.split("---", 2)[1]
        for heading in headings:
            if heading not in text:
                errors.append(f"{path.relative_to(ROOT)}: missing {heading}")
        if path.name == "rose.md":
            if "\n  external_directory: ask\n" not in frontmatter:
                errors.append("agents/rose.md: expected external_directory ask")
            if "debug-investigator" in text:
                errors.append("agents/rose.md: removed debug-investigator route remains")
            continue
        if "\n  external_directory: deny\n" not in frontmatter:
            errors.append(f"{path.relative_to(ROOT)}: managed agent must deny external_directory")
        if "\n  task: deny\n" not in frontmatter:
            errors.append(f"{path.relative_to(ROOT)}: managed agent must deny task")
    web = (ROOT / "agents/web-researcher.md").read_text(encoding="utf-8")
    for marker in ["\n  read: deny\n", "\n  list: deny\n", "\n  glob: deny\n", "\n  grep: deny\n", "\n  webfetch: ask\n", "\n  websearch: ask\n"]:
        if marker not in web:
            errors.append(f"agents/web-researcher.md: missing web-only marker {marker.strip()}")
    if (ROOT / "agents/debug-investigator.md").exists():
        errors.append("agents/debug-investigator.md: removed Agent still present")
    if (ROOT / ".agents/skills/debugging-and-error-recovery").exists():
        errors.append("debugging-and-error-recovery: removed skill still present")
    return errors


def read_repo_text(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def validate_command_contracts() -> list[str]:
    errors: list[str] = []
    command_dir = ROOT / "commands"
    allowed_delivery_commands = DELIVERY_COMMANDS
    allowed_non_delivery_commands = UTILITY_COMMANDS
    allowed_public_commands = PUBLIC_COMMANDS
    internal_delivery_commands = {
        "questionnaire.md",
        "test-plan.md",
        "research.md",
        "implement.md",
        "fix.md",
        "debug.md",
        "review.md",
        "evolve.md",
    }

    existing_commands = {path.name for path in command_dir.glob("*.md")}
    unexpected_commands = sorted(existing_commands - allowed_public_commands)
    for name in unexpected_commands:
        errors.append(f"commands/{name}: unexpected top-level command; the ten canonical delivery and Utility Commands are the only public commands")

    unexpected_internal = sorted(existing_commands & internal_delivery_commands)
    for name in unexpected_internal:
        errors.append(f"commands/{name}: internal lifecycle stage must not be a top-level delivery command")

    missing = sorted(allowed_delivery_commands - existing_commands)
    for name in missing:
        errors.append(f"commands/{name}: missing public Delivery Command")

    for name in sorted(allowed_non_delivery_commands - existing_commands):
        errors.append(f"commands/{name}: missing public Utility Command")

    for name in sorted(allowed_public_commands & existing_commands):
        relative = f"commands/{name}"
        text = read_repo_text(relative)
        if not text.startswith("---\n"):
            errors.append(f"{relative}: missing frontmatter")
        else:
            parts = text.split("---", 2)
            if len(parts) < 3:
                errors.append(f"{relative}: unterminated frontmatter")
                frontmatter = ""
            else:
                frontmatter = parts[1]
            if "\nagent: rose\n" not in frontmatter:
                errors.append(f"{relative}: frontmatter missing agent: rose")
            if "\nsubtask: false\n" not in frontmatter:
                errors.append(f"{relative}: frontmatter missing subtask: false")
        if f"# /{name.removesuffix('.md')}" not in text:
            errors.append(f"{relative}: missing command heading")
        for marker in ["User input:", "Required behavior:", "Hard stops:", "Output contract:"]:
            if marker not in text:
                errors.append(f"{relative}: missing command contract marker {marker!r}")
        if name in allowed_delivery_commands and "aili-delivery-flow" not in text:
            errors.append(f"{relative}: missing delivery routing marker 'aili-delivery-flow'")

    local_review_text = read_repo_text("commands/local-review.md") if (command_dir / "local-review.md").exists() else ""
    for marker in [
        "canonical report-first local-review utility",
        "standalone non-delivery audit",
        "--base <branch>",
        "--commit <sha>",
        "--pr <url|number>",
        "--change <id|path>",
        "--focus <text>",
        "--repair",
        "categorized report",
        "OpenCode's built-in `/review`",
        "Do not replace `/ship`",
        "mutate remote state",
        "PASS_WITH_UNVERIFIED",
        "Unverified",
        "exact read-only GitHub CLI allowlist `gh pr view`, `gh pr diff`, and `gh pr list --head`",
        "Do not run `gh api`, `gh pr checkout`, `gh pr comment`, `gh pr review`, `gh pr merge`, `gh pr create`, `gh repo clone`",
        "Do not store or print secrets, tokens, private keys, cookies, raw logs, full transcripts, full file dumps, or private data in reports; use redacted path:line/type evidence instead.",
        "read the conventional OpenSpec artifact paths directly",
        "local OpenSpec artifacts may be git-ignored or absent from snapshot-style search indexes",
        "`NEEDS_FIXES` and `BLOCKED` block BUILD continuation",
        "`PASS_WITH_UNVERIFIED` permits continuation only after the user accepts each named `Unverified` item",
    ]:
        if marker not in local_review_text:
            errors.append(f"commands/local-review.md: missing local-review contract marker {marker!r}")

    canonical_dir = ROOT / "core" / "commands"
    canonical_commands = {path.name for path in canonical_dir.glob("*.md")}
    if canonical_commands != allowed_public_commands:
        errors.append(
            "core/commands: canonical command inventory differs from the exact four Delivery Commands and six Utility Commands"
        )
    canonical_utility_markers = {
        "handoff.md": ["Required behavior:", "Hard stops:", "Output contract:", "explicit CREATE, LIST, or RESUME", "repository-local handoff"],
        "agents-md.md": ["Required behavior:", "Hard stops:", "Output contract:", "scripts/agents_md.py", "managed-block or backup-overwrite strategy"],
        "harness-audit.md": ["Required behavior:", "Hard stops:", "Output contract:", "report-first audit", "Do not edit harness controls"],
        "retro.md": ["Required behavior:", "Hard stops:", "Output contract:", "explicitly supplied or approved sanitized evidence", "Do not claim access to global history"],
        "security-review.md": ["Required behavior:", "Hard stops:", "Output contract:", "independent `security-auditor` role", "exact approval before an external backend receives source"],
    }
    for name, markers in canonical_utility_markers.items():
        relative = f"core/commands/{name}"
        if not (canonical_dir / name).exists():
            errors.append(f"{relative}: missing canonical Utility Command")
            continue
        errors.extend(require_text_markers(relative, markers, "canonical Utility Command"))

    try:
        manifest = json.loads(read_repo_text("manifests/rose-aili.components.json"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"manifests/rose-aili.components.json: unreadable command/Skill inventory: {exc}")
    else:
        components = manifest.get("components", {}) if isinstance(manifest, dict) else {}
        command_rows = components.get("commands", []) if isinstance(components, dict) else []
        skill_rows = components.get("skills", []) if isinstance(components, dict) else []
        command_names = {row.get("name") for row in command_rows if isinstance(row, dict)}
        skill_names = {row.get("name") for row in skill_rows if isinstance(row, dict)}
        retired_names = {row.get("name") for row in manifest.get("retiredSkills", []) if isinstance(row, dict)} if isinstance(manifest, dict) else set()
        if command_names != {name.removesuffix(".md") for name in allowed_public_commands}:
            errors.append("component manifest must expose exactly ten Commands")
        if len(skill_names) != 58:
            errors.append(f"component manifest must expose exactly 58 retained Skills; found {len(skill_names)}")
        if retired_names != RETIRED_SKILLS:
            errors.append("component manifest retired Skill inventory is incomplete or unexpected")
        if skill_names & RETIRED_SKILLS:
            errors.append("component manifest must not package a retired Skill")

    for skill in RETIRED_SKILLS:
        if (ROOT / ".agents" / "skills" / skill / "SKILL.md").exists():
            errors.append(f".agents/skills/{skill}/SKILL.md: retired Skill remains runnable")

    thin_commands = {
        "commands/define.md": {
            "required": [
                "Invoke `aili-delivery-flow` in DEFINE mode.",
                "Produce or align the complete implementation-readiness contract before BUILD.",
                "Do not implement; unresolved material decisions or decision-shaping research, invalid/incoherent artifacts, or missing explicit final `test-plan.md` acceptance block BUILD readiness.",
                "readiness exactly `READY | BLOCKED`, named `Unverified` residuals separately",
            ],
            "forbidden": ["requirements-grilling", "test-document-generator", "interview.md", "Artifact Freshness Gate"],
        },
        "commands/ship.md": {
            "required": [
                "Invoke `aili-delivery-flow` in SHIP mode.",
                "Reconcile the implemented target directly and select only the evidence, review, repair, packaging, or release check required by the exact closeout claim.",
                "Do not start a review swarm, broad matrix, or repair cycle merely because SHIP was requested. Fresh SHIP intent and current implementation evidence are required; exact high-risk/Git/release operations retain separate approval.",
                "Mode/target, closeout path when applicable, verdict, blocking or `Unverified` evidence, approvals needed, and next action.",
            ],
            "forbidden": ["git status --short --branch", "classify dirty paths", "propose cleanup for residue", "Savepoint commits"],
        },
    }
    for relative, contract in thin_commands.items():
        text = read_repo_text(relative)
        errors.extend(require_text_markers(relative, contract["required"], "thin command"))
        for marker in contract["forbidden"]:
            if marker in text:
                errors.append(f"{relative}: duplicates canonical detailed policy marker {marker!r}")

    return errors


def validate_local_review_gate_contracts() -> list[str]:
    errors: list[str] = []
    required_markers = {
        ".agents/skills/local-review-gate/SKILL.md": [
            "name: local-review-gate",
            "OpenCode's built-in `/review`",
            "--base <branch>",
            "--commit <sha>",
            "--pr <url\\|number>",
            "--change <id\\|path>",
            "--focus <text>",
            "--repair",
            "categorized report",
            "openspec/changes/<change-id>/review-report.md",
            "BLOCKED",
            "NEEDS_FIXES",
            "NEEDS_REVIEW",
            "PASS_WITH_UNVERIFIED",
            "REREVIEW_REQUIRED",
            "Any delegated review context remains read-only and terminal",
            "ROSE may repair directly or use one independently justified fresh edit assignment",
            "convergence-reviewer",
            "A local-review report neither triggers nor satisfies lifecycle completion",
            "skipped reason with risk",
            "remote state",
            "exact GitHub CLI allowlist `gh pr view`, `gh pr diff`, and `gh pr list --head`",
            "do not run `gh api`, `gh pr checkout`, `gh pr comment`, `gh pr review`, `gh pr merge`, `gh pr create`, `gh repo clone`",
            "Do not store or print secrets, tokens, private keys, cookies, raw logs, full transcripts, full file dumps, or private data in reports; use redacted path:line/type evidence instead.",
            "resolve the conventional artifact paths directly instead of relying only on broad glob/search output",
            "omitted from snapshot-style indexes",
            "`NEEDS_FIXES` and `BLOCKED` block BUILD continuation",
            "`PASS_WITH_UNVERIFIED` may continue only after the user accepts each named `Unverified` item",
        ],
        ".agents/skills/local-review-gate/references/upstream-provenance.md": [
            "provenance, trigger-fit, and OpenCode compatibility checks",
            "active-reference",
            "deferred",
            "Do not copy/adapt ECC agents, ECC skills, orchestration commands, or addyosmani rubrics wholesale",
            "5A.2",
            "5A.8",
            "active/completed",
        ],
        ".agents/skills/local-review-gate/references/ecc-code-review-adaptation.md": [
            "## Provenance",
            "Copy/adapt scope",
            "MIT License, Copyright 2026 Affaan Mustafa",
            "commands/code-review.md",
            "2382c59968231c205f9cf9cffa9013f480899a9c",
            "Activated AILI behavior",
            "full-file",
            "Do not activate `.claude` paths",
            "Do not activate remote mutation defaults",
        ],
        ".agents/skills/local-review-gate/references/review-repair-lane-adaptation.md": [
            "## Provenance",
            "Copy/adapt scope",
            "MIT License, Copyright 2026 Affaan Mustafa",
            "agents/security-reviewer.md",
            "agents/pr-test-analyzer.md",
            "agents/build-error-resolver.md",
            "commands/build-fix.md",
            "Review lanes remain read-only",
            "detect the build system",
            "one error class at a time",
        ],
        ".agents/skills/local-review-gate/references/orchestration-adaptation.md": [
            "## Provenance",
            "Copy/adapt scope",
            "commands/orch-review.md",
            "commands/multi-plan.md",
            "5216c7df157a9099214c122bc096e9693730ac77",
            "b50912b1f0900ed34935228d973dd92902b97342",
            "fail-closed",
            "blocking and advisory",
            "adversarial verification",
            "Do not add public `multi-*` commands",
        ],
        ".agents/skills/local-review-gate/references/addyosmani-code-review-rubric.md": [
            "## Provenance",
            "Copy/adapt scope",
            "MIT License, Copyright 2025 Addy Osmani",
            "96cac1d79edca4a9231cbe6af50415b5e4d6cf42",
            "5efda7afb5d0e4a5393c5a7da84e15b197f7b5b6",
            "five axes: correctness, readability, architecture, security, and performance",
            "Critical`, `Important`, and `Suggestion`",
            "spec/task-first",
            "concrete fix",
            "uncertainty/proof gates",
        ],
        ".agents/skills/local-review-gate/references/codex-github-compatibility.md": [
            "## Provenance",
            "behavior-only guidance",
            "No official documentation prose is copied",
            "AGENTS.md",
            "PR-style focus instructions",
            "high-priority",
            "review/fix parity",
            "exact GitHub CLI allowlist `gh pr view`, `gh pr diff`, and `gh pr list --head`",
        ],
        "agents/convergence-reviewer.md": [
            "external_directory: deny",
            "task: deny",
            "Compare formal artifacts",
            "partial, missing, stale, contradictory, or pseudo-complete",
            "ROSE owns the verdict",
        ],
        ".agents/skills/review-pipeline/SKILL.md": [
            "proactive delegation scan",
            "Choose at most one auxiliary specialist capability",
            "Default concurrency is at most two but is not a hard cap",
            "suitable owners",
            "explicit join plan",
            "one targeted recheck",
            "Never creates an automatic review swarm",
        ],
        ".agents/skills/parallel-subagent-dispatch/SKILL.md": [
            "proactive delegation scan",
            "Default to at most two concurrent subagents",
            "not a hard cap",
            "## Canonical packet protocol",
            ".agents/skills/aili-delivery-flow/references/protocols/subagent-task-packet.md",
            "## Canonical result protocol",
            ".agents/skills/aili-delivery-flow/references/protocols/subagent-result.md",
        ],
        ".agents/skills/aili-delivery-flow/references/protocols/subagent-task-packet.md": [
            "Package ID:",
            "Role ID:",
            "Assignment:",
            "Scope:",
            "Forbidden scope:",
            "Allowed actions:",
            "Expected result:",
            "Expected evidence:",
            "Execution: sync | async",
            "Continuation: same-package | new-package",
            "Stop when:",
        ],
        "agents/rose.md": [
            '"convergence-reviewer": allow',
            "Run a proactive delegation scan",
            "Default concurrency is at most two",
            "not a hard cap",
        ],
        ".agents/skills/aili-delivery-flow/SKILL.md": [
            "Only four top-level delivery commands are valid",
            "`/local-review` is a standalone non-delivery local audit command owned by `local-review-gate`",
            "do not route it through this delivery lifecycle skill as a fifth lifecycle mode",
        ],
    }

    for relative, markers in required_markers.items():
        errors.extend(require_text_markers(relative, markers, "local-review gate"))

    active_reference_sections = {
        ".agents/skills/local-review-gate/references/ecc-code-review-adaptation.md": section_between(read_repo_text(".agents/skills/local-review-gate/references/ecc-code-review-adaptation.md"), "## Activated AILI behavior", "## Rejected upstream behavior"),
        ".agents/skills/local-review-gate/references/review-repair-lane-adaptation.md": section_between(read_repo_text(".agents/skills/local-review-gate/references/review-repair-lane-adaptation.md"), "## Activated AILI behavior", "## Deferred or rejected ECC lane candidates"),
        ".agents/skills/local-review-gate/references/orchestration-adaptation.md": section_between(read_repo_text(".agents/skills/local-review-gate/references/orchestration-adaptation.md"), "## Activated AILI behavior", "## Rejected upstream behavior"),
        ".agents/skills/local-review-gate/references/codex-github-compatibility.md": section_between(read_repo_text(".agents/skills/local-review-gate/references/codex-github-compatibility.md"), "## Activated AILI behavior", ""),
    }
    forbidden_active_markers = [".claude/", "Claude-only", "ccg-workflow", "Codex/Gemini runtime", "gh api", "gh pr comment", "gh pr review", "gh pr merge", "gh pr create", "gh repo clone"]
    for relative, section in active_reference_sections.items():
        if not section:
            errors.append(f"{relative}: missing active AILI behavior section for upstream adaptation")
        else:
            errors.extend(require_absent_in_section(relative, section, forbidden_active_markers, "active upstream adaptation"))

    local_review_text = read_repo_text("commands/local-review.md") if (ROOT / "commands/local-review.md").exists() else ""
    for marker in [
        "five axes — correctness, readability, architecture, security, and performance",
        "Critical/Important findings",
        "concrete fixes",
        "zero findings is valid",
        "fail-closed orchestration",
    ]:
        if marker not in local_review_text:
            errors.append(f"commands/local-review.md: missing upstream review adaptation marker {marker!r}")

    code_reviewer_text = read_repo_text("agents/code-reviewer.md") if (ROOT / "agents/code-reviewer.md").exists() else ""
    for marker in [
        "Review a supplied change",
        "path and line evidence",
        "Do not edit",
        "STATUS",
    ]:
        if marker not in code_reviewer_text:
            errors.append(f"agents/code-reviewer.md: missing lean review marker {marker!r}")
    return errors


def validate_define_artifact_contracts() -> list[str]:
    errors: list[str] = []
    required_markers = {
        ".agents/skills/aili-delivery-flow/SKILL.md": [
            "requirements-grilling",
            "test-document-generator",
            "explicitly user-invoked Frontier Batch Mode",
            "never infer batch mode from blocker count",
            "Unverified",
        ],
        ".agents/skills/aili-delivery-flow/references/lifecycle.md": [
            "requirements-grilling",
            "test-document-generator",
            "READY",
            "BLOCKED",
            "not a readiness alternative",
            "Change Revision Decision",
        ],
        ".agents/skills/aili-delivery-flow/references/backend-routing.md": [
            "interview.md",
            "test-plan.md",
            "requirements-grilling",
            "test-document-generator",
            "asks once",
        ],
        ".agents/skills/aili-delivery-flow/references/artifact-contracts.md": [
            "interview.md",
            "test-plan.md",
            "requirements-grilling",
            "test-document-generator",
            "BUILD Readiness",
        ],
        ".agents/skills/aili-delivery-flow/references/questionnaire-policy.md": [
            "Artifact Freshness",
            "Disk wins",
            "freshness is event-directed",
            "interview.md",
            "requirements-grilling",
            "Explicit Frontier Batch Mode",
            "never infer it from blocker count",
            "fresh single-use Task",
            "no batch answer grants or implies authority",
        ],
        ".agents/skills/aili-delivery-flow/references/test-document-policy.md": [
            "Artifact Freshness",
            "Disk wins",
            "freshness is event-directed",
            "test-plan.md",
            "test-document-generator",
        ],
        ".agents/skills/requirements-grilling/SKILL.md": [
            "change-interviewer",
            "interview packet",
            "interview.md",
            "focused unresolved-answer follow-up defaults to chat-first interaction with AI write-back",
            "ask one decision-changing blocking question in chat",
            "write the user's accepted answer, accepted default, explicit waiver, or named `UNVERIFIED` state into `interview.md`",
            "re-read once before classification, readiness, or write-back",
            "Do not call the packet `READY` from chat-only content",
            "Default to one focused follow-up",
            "Re-read the filled packet from disk",
            "ambiguous",
            "BLOCKED",
            "evidence-backed recommended answer",
            "Domain-Modeling Discipline",
            "CONTEXT-FORMAT.md",
            "ADR-FORMAT.md",
            "INTERVIEW-PACKET-FORMAT.md",
            "MIT-LICENSE-MATT-POCOCK.md",
            "Status: Proposed",
            "do not add `/grill`, `/grill-me`, or `/interview`",
            "Do not register `batch-grill-me` as a second skill",
            "do not create `grill.md`, `grilling.md`, or `requirements-grilling.md`",
            "Frontier Batch Mode is an explicit user interaction mode",
            "complete set of material user decisions",
            "never resumes an old `task_id`",
            "A batch answer never grants or implies authority",
            "## Decision-state contract",
            "direction-recorded",
            "awaiting-confirmation",
            "implementation_authorization: absent | granted | expired | revoked",
        ],
        ".agents/skills/test-document-generator/SKILL.md": [
            "marking a test plan final never marks user acceptance",
            "never grants BUILD authorization",
            "implementation_authorization: granted",
        ],
        ".agents/skills/strategy-stress-test/SKILL.md": [
            "report-style stress test",
            "explicitly requested frontier batch",
            "Do not register or invoke a second `batch-grill-me` skill",
        ],
        "agents/rose.md": [
            "explicitly user-invoked `requirements-grilling` Frontier Batch Mode",
            "never infer batch mode from blocker count",
            "a batch never grants or implies authority",
        ],
        "templates/opencode-global-AGENTS.md": [
            "explicitly user-invoked `requirements-grilling` Frontier Batch Mode",
            "never infer batch mode from blocker count",
            "a batch never grants or implies authority",
        ],
        ".agents/skills/requirements-grilling/references/INTERVIEW-PACKET-FORMAT.md": [
            "# 需求拷问包：<change-name>",
            "资料来源与证据",
            "材料性决策与状态",
            "术语或领域边界问题",
            "答案吸收记录",
        ],
        ".agents/skills/requirements-grilling/references/CONTEXT-FORMAT.md": [
            "## Language",
            "_Avoid_",
            "project-specific terms only",
            "implementation decisions",
            "context.md` remains beside `interview.md`",
        ],
        ".agents/skills/requirements-grilling/references/ADR-FORMAT.md": [
            "Status: Proposed",
            "hard to reverse",
            "surprising without context",
            "real trade-off",
            "beside `interview.md`",
        ],
        ".agents/skills/requirements-grilling/references/MIT-LICENSE-MATT-POCOCK.md": [
            "MIT License",
            "Copyright (c) 2026 Matt Pocock",
            "substantial portions of the Software",
        ],
        "docs/harness/backend-adapters.md": [
            "requirements-grilling",
            "test-document-generator",
            "interview.md",
            "test-plan.md",
            "Unverified",
        ],
        "docs/harness/command-lifecycle.md": [
            "requirements-grilling",
            "test-document-generator",
            "required behavior",
            "output contract",
        ],
        "docs/harness/aili-harness-contract.md": [
            "requirements-grilling",
            "test-document-generator",
            "Unverified",
        ],
    }

    for relative, markers in required_markers.items():
        path = ROOT / relative
        if not path.exists():
            errors.append(f"{relative}: missing DEFINE artifact contract file")
            continue
        text = path.read_text(encoding="utf-8")
        for marker in markers:
            if marker not in text:
                errors.append(f"{relative}: missing DEFINE artifact marker {marker!r}")

    return errors


def validate_neutral_build_contracts() -> list[str]:
    errors: list[str] = []
    required_markers = {
        "commands/build.md": ["neutral", "accepted scoped queue", "progress-ledger savepoints", "IMPLEMENTED_TARGETED_VERIFIED", "Do not infer package"],
        ".agents/skills/aili-delivery-flow/SKILL.md": ["references/build-execution-loop.md", "current acceptance, target, package, permission, and claim-verification path", "Derive a dependency-ordered queue from the accepted contract", "smallest fresh check supporting the exact claim"],
        ".agents/skills/parallel-subagent-dispatch/references/agent-selection-matrix.md": ["Protocol: `aili-agent-selection/v1`", "Role namespace: `canonical`", "Selector mapping: `adapter-owned`", "Phase affinity is advisory", "`general` is not a canonical specialist role"],
        ".agents/skills/aili-delivery-flow/references/formal-task-board.md": ["Protocol: `aili-task-board/v1`", "Package kind: `evidence | task-execution`", "Every accepted task ID belongs to exactly one current task-execution package", "returned → done", "waiver is recorded before execution", "Every async package declares a stable join ID"],
        ".agents/skills/aili-delivery-flow/references/lifecycle.md": ["neutral bounded package execution", "synthesize the ordered queue from the accepted contract", "IMPLEMENTED_TARGETED_VERIFIED"],
        ".agents/skills/aili-delivery-flow/references/backend-routing.md": ["synthesize a queue from the active accepted contract", "user selects the A33 host", "IMPLEMENTED_TARGETED_VERIFIED"],
        ".agents/skills/aili-delivery-flow/references/implementation-packages.md": ["synthesize an ordered package queue", "compact packet contract", "missing manual package text is not a stop condition", "Package 1–12 naming is historical", "Every accepted task ID belongs to exactly one current task-execution package", "One-shot and persistent adapters"],
        ".agents/skills/aili-delivery-flow/references/build-execution-loop.md": ["Neutral BUILD Execution Loop", "active accepted contract", "bounded loop vocabulary, not an automatic sequence", "One current intent selects one primary loop", "Canonical `CONT-005` envelope and budgets", "Protocol-only automation boundary", "A33 admission and operation gates", "IMPLEMENTED_TARGETED_VERIFIED"],
        ".agents/skills/aili-delivery-flow/references/artifact-contracts.md": ["evidence_state", "ROSE directly inspects the changed scope/affected links", "selected only for a concrete gap or affected SHIP claim", "neither a waiver nor accepted-`Unverified` wording is a BUILD-readiness alternative"],
        ".agents/skills/aili-delivery-flow/references/test-document-policy.md": ["BUILD readiness is only `READY` or `BLOCKED`", "IMPLEMENTED_TARGETED_VERIFIED", "fresh explicit intent", "exact commit/push/merge/release approvals"],
        "docs/harness/command-lifecycle.md": ["progress-ledger savepoints", "IMPLEMENTED_TARGETED_VERIFIED", "bounded loop vocabulary, not an automatic sequence"],
        "docs/harness/aili-harness-contract.md": ["Neutral BUILD execution", "IMPLEMENTED_TARGETED_VERIFIED", "Active-contract completion package"],
    }
    for relative, markers in required_markers.items():
        errors.extend(require_text_markers(relative, markers, "neutral BUILD"))

    active_files = list(required_markers) + [
        ".agents/skills/aili-delivery-flow/references/artifact-contracts.md",
        ".agents/skills/aili-delivery-flow/references/review-repair-loop.md",
    ]
    forbidden = ["goal_id", "goal-style", "scoped goal marker", "scoped BUILD goal", "BUILD Goal Mode", "autonomous goal mode"]
    for relative in active_files:
        text = read_repo_text(relative).lower()
        for marker in forbidden:
            if marker.lower() in text:
                errors.append(f"{relative}: forbidden active pseudo-goal semantic {marker!r}")
    return errors


def validate_package5_loop_fixtures() -> list[str]:
    data = load_fixture(FIXTURE_DIR / "command-routing-fixtures.yaml")
    cases = data.get("cases", [])
    by_id = {case.get("id"): case for case in cases if isinstance(case, dict)}
    case_ids = [case.get("id") for case in cases if isinstance(case, dict)]
    duplicate_ids = sorted({case_id for case_id in case_ids if case_ids.count(case_id) > 1})
    required_ids = """loop-six-inner-four-outer loop-turn-executable loop-turn-no-recursion loop-objective-bounded loop-objective-budget-invalid loop-objective-max-attempt-stop loop-objective-exhaustion loop-objective-resume-no-reset loop-review-budget-separate loop-envelope-complete loop-envelope-terminal-writeback budget-representation-objective budget-representation-turn budget-protocol-template-instantiation budget-invalid-iteration-review budget-invalid-time-unit-value budget-invalid-token-unit-value tokens-not-configured-null tokens-requested-accounting-unavailable-prestart tokens-midrun-accounting-loss budget-exhaustion-evidence budget-resume-no-reset lp-budget-valid-instantiation lp-budget-invalid-iteration-zero lp-budget-invalid-iteration-negative lp-budget-invalid-iteration-fractional lp-budget-invalid-iteration-nonnumeric lp-budget-invalid-review-zero lp-budget-invalid-review-negative lp-budget-invalid-review-fractional lp-budget-invalid-review-nonnumeric lp-budget-review-capable-null lp-budget-review-incapable-nonnull budget-iteration-preflight-unit budget-review-preflight-unit budget-time-overshoot-actual budget-token-overshoot-actual budget-resume-preserves-overshoot-accounting loop-interval-protocol-only loop-event-protocol-only loop-automation-no-registration loop-formal-runbook-protocol-only loop-no-background-primitive loop-interval-documentation-ambiguity loop-interval-executable-request-block neutral-build-native-goal-nonownership ordinary-goal-language-preserved native-goal-partii-na def-e2-no-per-package-gate def-e9-lean-final-inspection budget-consumed-over-limit-terminal budget-iteration-consumed-over-limit-corruption budget-review-consumed-over-limit-corruption""".split()
    required_ids += """automation-hidden-aili-block automation-product-ci-formal-allowed automation-product-cron-formal-allowed automation-product-webhook-listener-formal-allowed automation-product-queue-daemon-hook-retry-formal-allowed automation-vocabulary-only-ordinary automation-required-risk-gates automation-aili-protocol-doc-only automation-hidden-plus-protocol-no-lp T-BUILD-NO-AUTO-SAVEPOINT-ACTIONS T-BUILD-MINIMUM-COMPLETION T-BUILD-COMPLETION-STOP T-SHIP-EVIDENCE-REUSE T-EVIDENCE-NONINVALIDATING-GIT T-EVIDENCE-INVALIDATION-EVENTS T-MERGE-EVIDENCE-SCOPE T-CI-FAILURE-USER-STOP T-USER-CONTROL-POINTS T-NO-FIFTH-COMMAND""".split()
    required_ids += """a33-host-git-positive a33-host-non-git-block a33-host-no-ranking a33-ignore-positive a33-ignore-missing-block a33-ignore-reinclude-block a33-destination-tracked-block a33-key-valid a33-key-invalid-block a33-operation-key-omission-rejected a33-operation-key-wrong-type-rejected a33-approval-key-omission-rejected a33-approval-key-wrong-type-rejected a33-collision-no-guess-block a33-multiple-attachments a33-rules-narrow a33-rules-broaden-block a33-rules-conflict-block a33-topology-submodule-block a33-path-ambiguity-block a33-identity-field-omission-rejected a33-identity-field-wrong-type-rejected a33-identity-string-sentinel-rejected a33-identity-populated-required-null-rejected a33-identity-absent-forbidden-nonnull-rejected a33-identity-detached-branch-mismatch-rejected a33-identity-file-array-invalid-rejected a33-identity-dirty-count-invalid-rejected a33-runtime-identity-transition-schema""".split()
    required_ids += """a33-runtime-prepare-no-worktree-effect a33-runtime-approval-positive a33-runtime-each-attachment-add-separate-approval a33-runtime-each-attachment-remove-separate-approval a33-runtime-add-approval-wrong-zero-effect a33-runtime-add-approval-reused-zero-effect a33-runtime-remove-approval-wrong-zero-effect a33-runtime-remove-approval-reused-zero-effect a33-runtime-fixture-add-real-approval-zero-effect a33-runtime-fixture-remove-real-approval-zero-effect a33-runtime-operation-class-mismatch-zero-effect a33-runtime-key-mismatch-zero-effect a33-runtime-approval-missing-zero-effect a33-runtime-missing-approval-null-fields a33-runtime-approval-stale-zero-effect a33-runtime-approval-mismatched-zero-effect a33-runtime-approval-expired-zero-effect a33-runtime-approval-wrong-source-zero-effect a33-runtime-approval-wrong-destination-zero-effect a33-runtime-approval-wrong-branch-zero-effect a33-runtime-approval-wrong-ref-zero-effect a33-runtime-add-approval-reused-real-remove-zero-effect a33-runtime-approval-other-operation-zero-effect a33-runtime-approval-declined-unavailable a33-runtime-add-trusted-code-risk-accepted a33-runtime-add-trusted-code-risk-declined-zero-effect a33-runtime-add-trusted-code-risk-unavailable-zero-effect a33-runtime-remove-trusted-code-risk-not-applicable""".split()
    required_ids += """a33-pre-add-target-absent a33-add-delta-exact a33-add-common-dir-exact-allowed-delta a33-add-common-dir-identity-preserved a33-add-existing-branch-no-ref-reflog-creation a33-add-new-branch-reflog-enabled-created a33-add-new-branch-reflog-disabled-absent a33-add-new-branch-reflog-enabled-missing-block a33-add-new-branch-reflog-disabled-unexpected-block a33-unrelated-common-dir-preserved a33-add-unrelated-preserved a33-pre-remove-target-populated a33-remove-delta-exact a33-remove-common-dir-exact-allowed-delta a33-remove-common-dir-identity-preserved a33-common-dir-identity-change-block a33-add-common-dir-unrelated-mutation-block a33-remove-common-dir-unrelated-mutation-block a33-remove-branch-deletion-block a33-remove-branch-reflog-mutation-block a33-remove-dirty-block a33-remove-unknown-block a33-remove-user-visible-block a33-remove-ignored-block a33-remove-untracked-block a33-remove-artifact-block a33-remove-locked-block a33-remove-wrong-source-block a33-remove-wrong-path-block a33-remove-missing-target-block a33-forbidden-git-block a33-rollback-preserves""".split()
    errors = [f"command-routing-fixtures.yaml: missing Package 5 fixture {case_id}" for case_id in required_ids if case_id not in by_id]
    if duplicate_ids:
        errors.append(f"command-routing-fixtures.yaml: duplicate Package 5 fixture ids {duplicate_ids}")
    taxonomy = by_id.get("loop-six-inner-four-outer", {})
    if taxonomy.get("inner") != ["question", "delta", "evidence/plan", "neutral BUILD", "review/repair", "convergence"] or taxonomy.get("outer") != ["turn", "objective", "interval", "event"] or taxonomy.get("seventh_loop") is not False:
        errors.append("command-routing-fixtures.yaml: loop taxonomy must be exactly six inner/four outer with no seventh loop")
    unavailable = by_id.get("tokens-requested-accounting-unavailable-prestart", {}).get("tokens", {})
    if unavailable.get("accounting_status") != "unavailable" or unavailable.get("remaining") != unavailable.get("limit"):
        errors.append("command-routing-fixtures.yaml: unavailable token accounting must preserve requested non-null counters")
    lost = by_id.get("tokens-midrun-accounting-loss", {}).get("tokens", {})
    if lost.get("accounting_status") != "lost" or not isinstance(lost.get("consumed"), int):
        errors.append("command-routing-fixtures.yaml: midrun token loss must preserve non-null counters")
    package_gate_case = by_id.get("def-e2-no-per-package-gate", {})
    if package_gate_case.get("mandatory_quality_gate") is not False or package_gate_case.get("generic_template") is not False or package_gate_case.get("change") != "complete-aili-workflow-orchestration":
        errors.append("command-routing-fixtures.yaml: DEF-E2 compatibility must forbid per-package mandatory gates")
    final_case = by_id.get("def-e9-lean-final-inspection", {})
    expected_fanout_requirements = ["independent non-overlapping units", "concrete benefit", "suitable owners", "explicit join plan"]
    if final_case.get("change") != "complete-aili-workflow-orchestration" or final_case.get("generic_template") is not False or final_case.get("task_coverage") != "applicable-current-scope" or final_case.get("automatic_review_swarm") is not False or final_case.get("default_concurrency") != 2 or final_case.get("hard_cap", "missing") is not None or final_case.get("larger_fanout_requires") != expected_fanout_requirements or "specialist_limit" in final_case or final_case.get("targeted_recheck_limit") != 1:
        errors.append("command-routing-fixtures.yaml: DEF-E9 final inspection must use default-two uncapped eligible fan-out without an automatic swarm and retain one targeted recheck")
    over_limit = by_id.get("budget-consumed-over-limit-terminal", {})
    if over_limit.get("counter") != {"limit": 3, "consumed": 4, "remaining": 0} or over_limit.get("stop_reason") != "budget-exhausted" or over_limit.get("outcome") != "budget-exhausted" or over_limit.get("resume") != "blocked":
        errors.append("command-routing-fixtures.yaml: consumed>limit must preserve consumed, clamp remaining, and remain terminal")
    for case_id in ("budget-iteration-consumed-over-limit-corruption", "budget-review-consumed-over-limit-corruption"):
        case = by_id.get(case_id, {})
        if case.get("expected") not in {"corruption-block-no-action", "corruption-block-no-repair"} or case.get("overshoot_allowed") is not False or case.get("resume") != "blocked":
            errors.append(f"command-routing-fixtures.yaml: {case_id} must treat discrete consumed>limit as corruption and block")
    automation = by_id.get("loop-automation-no-registration", {})
    if automation != {
        "id": "loop-automation-no-registration",
        "expected": "hidden-aili-block-product-gated",
        "hidden_aili": "block-zero-mutation-zero-lp",
        "explicit_product": "formal-high-risk-gates",
        "vocabulary_only": "ordinary",
        "protocol_only": "no-runtime-no-lifecycle-permission",
    }:
        errors.append("command-routing-fixtures.yaml: automation boundary must block hidden AILI runtime while allowing gated product automation")

    product_cases = [
        "automation-product-ci-formal-allowed",
        "automation-product-cron-formal-allowed",
        "automation-product-webhook-listener-formal-allowed",
        "automation-product-queue-daemon-hook-retry-formal-allowed",
    ]
    if any(by_id.get(case_id, {}).get("expected") != "eligible-through-formal-high-risk-gates" for case_id in product_cases):
        errors.append("command-routing-fixtures.yaml: explicit product automation must remain eligible through formal/high-risk gates")
    if by_id.get("automation-hidden-aili-block", {}).get("expected") != "block-zero-mutation-zero-lp" or by_id.get("automation-hidden-plus-protocol-no-lp", {}).get("expected") != "block-zero-mutation-zero-lp":
        errors.append("command-routing-fixtures.yaml: hidden AILI automation must block with zero mutation and zero LP")
    if by_id.get("automation-vocabulary-only-ordinary", {}).get("expected") != "ordinary":
        errors.append("command-routing-fixtures.yaml: automation vocabulary alone must remain ordinary")
    risk_gates = by_id.get("automation-required-risk-gates", {}).get("gates", [])
    for gate in ["permission", "external-write", "credential", "persistent-service", "dependency-lockfile", "destructive", "exact-operation"]:
        if gate not in risk_gates:
            errors.append(f"command-routing-fixtures.yaml: automation risk gates missing {gate!r}")

    savepoint = by_id.get("T-BUILD-NO-AUTO-SAVEPOINT-ACTIONS", {})
    if savepoint.get("savepoint_fields") != ["scope", "files_changed", "unresolved_items", "evidence_state", "next_package"] or any(savepoint.get(field) is not False for field in ("automatic_tests", "automatic_commit", "package_approval")):
        errors.append("command-routing-fixtures.yaml: BUILD savepoint must use exact fields and trigger no test/commit/approval")
    completion = by_id.get("T-BUILD-MINIMUM-COMPLETION", {})
    if completion.get("expected") != "one-minimal-changed-scope-check" or completion.get("automatic_full_matrix") is not False or completion.get("automatic_review_test_security") is not False or completion.get("targeted_recheck_limit") != 1:
        errors.append("command-routing-fixtures.yaml: BUILD completion must be one minimal changed-scope check")
    if by_id.get("T-BUILD-COMPLETION-STOP", {}).get("expected") != "IMPLEMENTED_TARGETED_VERIFIED" or by_id.get("T-BUILD-COMPLETION-STOP", {}).get("enters_ship") is not False:
        errors.append("command-routing-fixtures.yaml: BUILD must stop at IMPLEMENTED_TARGETED_VERIFIED")
    ship_reuse = by_id.get("T-SHIP-EVIDENCE-REUSE", {})
    if ship_reuse.get("fresh_intent") is not True or ship_reuse.get("reuse_event_fresh_build_evidence") is not True or ship_reuse.get("checks") != "stale-affected-risk-integration-packaging-release-merge-target-only":
        errors.append("command-routing-fixtures.yaml: SHIP must require fresh intent and reuse event-fresh evidence")
    if by_id.get("T-EVIDENCE-NONINVALIDATING-GIT", {}).get("stales_evidence") is not False or by_id.get("T-EVIDENCE-INVALIDATION-EVENTS", {}).get("invalidation") != "affected-only":
        errors.append("command-routing-fixtures.yaml: evidence freshness must be event-based and affected-only")
    merge_scope = by_id.get("T-MERGE-EVIDENCE-SCOPE", {})
    if merge_scope.get("exact_verified_fast_forward") != "no-full-rerun" or merge_scope.get("changed_merge") != "affected-integration-checks":
        errors.append("command-routing-fixtures.yaml: fast-forward/changed-merge evidence scope drift")
    controls = by_id.get("T-USER-CONTROL-POINTS", {})
    if controls.get("package_approval") is not False or controls.get("controls") != ["material-define-decisions", "one-final-test-plan-acceptance", "fresh-ship-intent", "exact-commit-approval", "exact-push-approval", "exact-merge-approval", "exact-release-approval", "ci-failure-user-return"]:
        errors.append("command-routing-fixtures.yaml: DEF-E11 user control points must remain exact and package approval absent")
    ci_stop = by_id.get("T-CI-FAILURE-USER-STOP", {})
    if ci_stop.get("expected") != "need-user" or ci_stop.get("automatic_actions") != []:
        errors.append("command-routing-fixtures.yaml: CI failure must return to the user without automatic actions")
    commands = by_id.get("T-NO-FIFTH-COMMAND", {})
    if commands.get("delivery_commands") != ["/ideate", "/define", "/build", "/ship"] or commands.get("local_review") != "standalone-non-delivery-no-lifecycle-or-ship-authority":
        errors.append("command-routing-fixtures.yaml: four delivery commands and standalone /local-review boundary drift")

    key_case = by_id.get("a33-key-valid", {})
    if key_case.get("regex") != "^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$" or key_case.get("worktree_key") != "explicit":
        errors.append("command-routing-fixtures.yaml: A33 key grammar/explicit worktree key drift")
    collision = by_id.get("a33-collision-no-guess-block", {}).get("forbidden_recovery", [])
    for value in ["suffix", "force", "-B", "orphan", "remote-guess", "implicit-base-ref"]:
        if value not in collision:
            errors.append(f"command-routing-fixtures.yaml: A33 collision recovery must forbid {value!r}")
    ignore = by_id.get("a33-ignore-positive", {})
    if ignore.get("ignore_rule") != "/.worktrees/" or ignore.get("reinclude") is not False or ignore.get("tracked_destination") is not False:
        errors.append("command-routing-fixtures.yaml: A33 exact ignore must reject re-inclusion and tracked destination")
    if by_id.get("a33-host-git-positive", {}).get("expected") != "admit-static-only" or by_id.get("a33-host-non-git-block", {}).get("operation_authority") is not False:
        errors.append("command-routing-fixtures.yaml: A33 host admission is static-only and non-Git blocks")
    if by_id.get("a33-rules-narrow", {}).get("reread_at") != "operation-dispatch-boundary" or by_id.get("a33-rules-broaden-block", {}).get("expected") != "block" or by_id.get("a33-rules-conflict-block", {}).get("expected") != "block-same-level-conflict":
        errors.append("command-routing-fixtures.yaml: A33 target rules must be re-read, narrow-only, and conflict-blocking")
    prepare = by_id.get("a33-runtime-prepare-no-worktree-effect", {})
    if prepare.get("expected") != "zero-effect" or prepare.get("adds") != 0 or prepare.get("removes") != 0 or prepare.get("descriptor_authority") is not False:
        errors.append("command-routing-fixtures.yaml: A33 PREPARE must have zero worktree effect and no authority")
    approval_positive = by_id.get("a33-runtime-approval-positive", {})
    if approval_positive.get("operation_classes") != ["driver_fixture", "real"] or approval_positive.get("bound_fields") != ["repo_key", "worktree_key", "source", "destination", "branch", "base_ref", "branch_mode", "reflog_policy", "operation_class", "expiry", "operation"] or approval_positive.get("aggregate_authority") is not False:
        errors.append("command-routing-fixtures.yaml: A33 approval must bind one exact real/fixture operation, keys, branch/base-ref, and reflog policy")
    key_mismatch = by_id.get("a33-runtime-key-mismatch-zero-effect", {})
    if key_mismatch.get("expected") != "block-zero-effect" or key_mismatch.get("parameters") != {"keys": ["repo_key", "worktree_key"], "operations": ["ADD", "REMOVE"]}:
        errors.append("command-routing-fixtures.yaml: A33 key mismatch must cover both keys and operations with zero effect")
    remove_risk = by_id.get("a33-runtime-remove-trusted-code-risk-not-applicable", {})
    if remove_risk.get("expected") != "observed-approval-not_applicable" or remove_risk.get("separate_deletion_risk_gate") is not True:
        errors.append("command-routing-fixtures.yaml: observed REMOVE must use not_applicable trusted-code risk under a separate deletion gate")
    missing_approval = by_id.get("a33-runtime-missing-approval-null-fields", {})
    if missing_approval.get("expected") != "requested-fields-populated-approval-id-decision-expiry-risk-null" or missing_approval.get("effect_started") is not False:
        errors.append("command-routing-fixtures.yaml: missing A33 approval must preserve requested fields, null approval evidence, and start no effect")
    remove_delta = by_id.get("a33-remove-delta-exact", {})
    if remove_delta.get("force") is not False or remove_delta.get("branch_ref_reflog") != "retained":
        errors.append("command-routing-fixtures.yaml: A33 REMOVE must be non-force and retain branch ref/reflog")
    identity = by_id.get("a33-runtime-identity-transition-schema", {})
    if identity.get("expected") != "host-source-populated-target-absent-populated-absent" or identity.get("identity_hash_digest") is not False:
        errors.append("command-routing-fixtures.yaml: A33 identities must stay separate with exact target transitions and no digest authority")
    if by_id.get("a33-add-existing-branch-no-ref-reflog-creation", {}).get("expected") != "unchanged-ref-reflog" or by_id.get("a33-add-new-branch-reflog-enabled-created", {}).get("expected") != "exact-ref-and-reflog-created" or by_id.get("a33-add-new-branch-reflog-disabled-absent", {}).get("expected") != "exact-ref-created-reflog-absent":
        errors.append("command-routing-fixtures.yaml: A33 branch-mode/source-reflog outcomes must remain exact")
    if by_id.get("a33-unrelated-common-dir-preserved", {}).get("parameters") != ["ADD", "REMOVE"] or by_id.get("a33-rollback-preserves", {}).get("automatic_remove") is not False:
        errors.append("command-routing-fixtures.yaml: A33 unrelated state and rollback worktrees/evidence must be preserved")
    return errors


def validate_traceability_contracts() -> list[str]:
    errors: list[str] = []

    traceability_markers = {
        ".agents/skills/aili-delivery-flow/references/implementation-packages.md": [
            "traceability mapping from source requirement, decision, or risk to task/package",
            "target files or artifacts",
            "verification command or inspection",
            "Open Question",
            "Unverified",
        ],
        ".agents/skills/aili-delivery-flow/references/protocols/implementation-package.md": [
            "Source requirement/decision/risk:",
            "Target files/artifacts:",
            "Traceability mapping:",
            "coverage status: covered | Open Question | Unverified",
        ],
        ".agents/skills/aili-delivery-flow/references/test-document-policy.md": [
            "traceability matrix for formal changes",
            "task/package",
            "file/artifact",
            "verification command or inspection",
            "Open Question",
            "Unverified",
        ],
        ".agents/skills/test-document-generator/SKILL.md": [
            "formal changes include a traceability matrix from requirement/decision/risk",
            "task/package",
            "file/artifact",
            "verification command or inspection, evidence",
            "Open Question",
            "Unverified",
        ],
        ".agents/skills/aili-delivery-flow/references/lifecycle.md": [
            "active-contract package queue",
            "changed files/artifacts mapped to requirements/decisions/risks",
            "final changed scope and affected links",
            "only for a concrete gap",
            "Open Question",
            "Unverified",
        ],
        ".agents/skills/aili-delivery-flow/references/review-repair-loop.md": [
            "Run a spec coverage check for formal changes",
            "requirements/tasks/test-plan items",
            "implementation, verification, review, and security evidence",
            "Open Question",
            "Unverified",
        ],
    }

    for relative, markers in traceability_markers.items():
        errors.extend(require_text_markers(relative, markers, "traceability contract"))

    return errors


def validate_complete_scoped_work_contracts() -> list[str]:
    errors: list[str] = []

    complete_scoped_markers = {
        "agents/implementer.md": [
            "Implement one complete, scoped code-change assignment.",
            "Change only task-owned files",
            "Run the smallest relevant check",
        ],
        "agents/rose.md": [
            "Deliver the complete accepted scope",
            "Run a proactive delegation scan",
            "run the smallest fresh check that supports the exact claim",
        ],
        "templates/opencode-global-AGENTS.md": [
            "Implement the complete, appropriately scoped change that satisfies the accepted task.",
            "Run the selected focused verification first, then broaden only when the claim still lacks evidence.",
            "the diff is task-scoped and non-speculative",
        ],
        "commands/build.md": [
            "complete accepted scoped queue",
            "progress-ledger savepoints",
            "one minimal changed-scope completion check",
        ],
        ".agents/skills/aili-delivery-flow/references/lifecycle.md": [
            "implement complete scoped packages in dependency order",
            "selects the smallest completion check",
            "one permitted targeted repair/recheck",
        ],
        ".agents/skills/aili-delivery-flow/references/build-execution-loop.md": [
            "Implement its complete accepted behavior",
            "Run a focused test/check only when the changed behavior, risk, package need, or bounded failure diagnosis triggers it",
        ],
    }

    for relative, markers in complete_scoped_markers.items():
        errors.extend(require_text_markers(relative, markers, "complete scoped work"))

    if (ROOT / "templates/opencode-global-AGENTS.md").exists():
        global_text = read_repo_text("templates/opencode-global-AGENTS.md")
        simplicity = section_between(global_text, "### 3. Simplicity First", "### 4. Task-Scoped Changes")
        if not simplicity:
            errors.append("templates/opencode-global-AGENTS.md: missing Simplicity First section")
        else:
            errors.extend(require_absent_in_section("templates/opencode-global-AGENTS.md", simplicity, ["Ship minimal production code", "smallest possible implementation", "minimum viable change"], "implementation-objective wording"))
        verification = section_between(global_text, "### 5. Goal-Driven Verification", "### 6. Task Continuity")
        if not verification:
            errors.append("templates/opencode-global-AGENTS.md: missing Goal-Driven Verification section")
        else:
            errors.extend(require_absent_in_section("templates/opencode-global-AGENTS.md", verification, ["smallest relevant", "minimal verification", "minimum verification"], "verification-order wording"))

    build_goal_text = read_repo_text(".agents/skills/aili-delivery-flow/references/build-execution-loop.md") if (ROOT / ".agents/skills/aili-delivery-flow/references/build-execution-loop.md").exists() else ""
    if "run the smallest relevant tests/checks first" in build_goal_text:
        errors.append(".agents/skills/aili-delivery-flow/references/build-execution-loop.md: packaging flow must use most relevant focused tests/checks wording")

    active_agents_markers = [
        "<!-- AILI_AGENTS_TEMPLATE_VERSION: 2 -->",
        "It contains project facts, local commands, local artifact placement, and repository-specific exceptions.",
        "## Project-Specific Testing and Artifact Placement",
        "CLI tests: use repository scripts under `scripts/` and harness fixtures under `docs/harness/fixtures/`.",
        "Temporary test output: OS temp is allowed only for ephemeral scratch/cache data that users do not need to open, review, or reference.",
        "## Local Overrides",
    ]
    errors.extend(require_text_markers("AGENTS.md", active_agents_markers, "v2 local AGENTS"))
    if (ROOT / "AGENTS.md").exists():
        active_agents_text = read_repo_text("AGENTS.md")
        for marker in [
            "AILI_MANAGED_BLOCK_BEGIN",
            "## Agent Operating Discipline",
            "## Coding Conventions",
            "## Testing and Verification",
            "## Security Rules",
            "## Git Rules",
        ]:
            if marker in active_agents_text:
                errors.append(f"AGENTS.md: v2 local AGENTS must not retain global rule section {marker!r}")

    agents_checker_markers = [
        "template version mismatch",
        "stale managed block not present in template",
        "## Project-Specific Testing and Artifact Placement",
        "## Local Overrides",
    ]
    errors.extend(require_text_markers("scripts/agents_md.py", agents_checker_markers, "AGENTS checker"))

    agents_template_markers = [
        "## Project-Specific Testing and Artifact Placement",
        "## Local Overrides",
    ]
    errors.extend(require_text_markers("templates/AGENTS.md", agents_template_markers, "project AGENTS template"))

    git_workflow_markers = [
        "task-scoped savepoint commits only when current task/project rules explicitly allow verified commits",
        "otherwise ask once with the cleanup package",
        "ask explicit approval before push, destructive clean/reset, branch deletion, worktree removal, OpenSpec archive, stashing unrelated changes, or deleting user-visible artifacts",
        "`wip:` checkpoints are allowed only when the current task explicitly approves a private unverified checkpoint",
    ]
    errors.extend(require_text_markers(".agents/skills/git-workflow-and-versioning/SKILL.md", git_workflow_markers, "commit allowance"))

    external_lookup_markers = [
        "External public-project lookup is allowed only when the current user request, task packet, or project contract allows source lookup",
        "Never send secrets, private data, proprietary code, or sensitive repository context to external search",
    ]
    errors.extend(require_text_markers(".agents/skills/mature-project-pattern-research/SKILL.md", external_lookup_markers, "mature-project external lookup gate"))
    if (ROOT / ".agents/skills/git-workflow-and-versioning/SKILL.md").exists():
        git_workflow_text = read_repo_text(".agents/skills/git-workflow-and-versioning/SKILL.md")
        commit_matrix = section_between(git_workflow_text, "Decision matrix:", "## Core Principles")
        if not commit_matrix:
            errors.append(".agents/skills/git-workflow-and-versioning/SKILL.md: missing decision matrix section")
        else:
            errors.extend(
                require_absent_in_section(
                    ".agents/skills/git-workflow-and-versioning/SKILL.md",
                    commit_matrix,
                    ["After completion", "After fix and verification", "Each vertical slice", "Each verified phase"],
                    "commit matrix allowance wording",
                )
            )
        savepoint_principle = section_between(git_workflow_text, "### 1. Use Savepoints When Allowed", "### 2. Atomic Commits")
        if not savepoint_principle:
            errors.append(".agents/skills/git-workflow-and-versioning/SKILL.md: missing qualified savepoint principle section")
        else:
            errors.extend(
                require_absent_in_section(
                    ".agents/skills/git-workflow-and-versioning/SKILL.md",
                    savepoint_principle,
                    ["Each successful increment gets its own commit", "Commit → Continue"],
                    "savepoint principle allowance wording",
                )
            )

    implementation_package_markers = [
        "Task-end branch/worktree hygiene:",
        "branch/status inspection:",
        "dirty path classification:",
        "classify dirty paths as task-scoped, unrelated/pre-existing, generated/ignored, scratch, or unknown",
        "safe scratch cleanup:",
        "cleanup proposal:",
        "approval-gated operations:",
        "ask explicit approval before push, destructive clean/reset, branch deletion, worktree removal, OpenSpec archive, stashing unrelated changes, or deleting user-visible artifacts",
        "commit allowance:",
        "savepoint commits may be proactive only when current task/project rules explicitly allow task-scoped verified commits; otherwise ask once with the cleanup package",
    ]
    errors.extend(require_text_markers(".agents/skills/aili-delivery-flow/references/protocols/implementation-package.md", implementation_package_markers, "task-end hygiene"))

    cleanup_gate_markers = {
        ".agents/skills/aili-delivery-flow/references/lifecycle.md": [
            "inspect `git status --short --branch`",
            "classify dirty paths as task-scoped, unrelated/pre-existing, generated/ignored, scratch, or unknown",
            "Propose cleanup for remaining residue",
            "ask explicit approval before push, destructive clean/reset, branch deletion, worktree removal, OpenSpec archive, stashing unrelated changes, or deleting user-visible artifacts",
            "Savepoint commits may be proactive only when current task/project rules explicitly allow task-scoped verified commits; otherwise ask once with the cleanup package",
        ],
        ".agents/skills/aili-delivery-flow/references/build-execution-loop.md": [
            "inspect `git status --short --branch`",
            "classify dirty paths as task-scoped, unrelated/pre-existing, generated/ignored, scratch, or unknown",
            "Propose cleanup for remaining residue",
            "ask explicit approval before push, destructive clean/reset, branch deletion, worktree removal, OpenSpec archive, stashing unrelated changes, or deleting user-visible artifacts",
            "Savepoint commits may be proactive only when current task/project rules explicitly allow task-scoped verified commits; otherwise ask once with the cleanup package",
        ],
    }
    for relative, markers in cleanup_gate_markers.items():
        errors.extend(require_text_markers(relative, markers, "cleanup gate"))

    return errors


def main() -> int:
    errors: list[str] = []
    for name, spec in REQUIRED.items():
        errors.extend(validate_fixture(name, spec))
    errors.extend(validate_agent_permissions())
    errors.extend(validate_command_contracts())
    errors.extend(validate_define_artifact_contracts())
    errors.extend(validate_neutral_build_contracts())
    errors.extend(validate_package5_loop_fixtures())
    errors.extend(validate_traceability_contracts())
    errors.extend(validate_complete_scoped_work_contracts())

    if errors:
        print("harness fixture check: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"harness fixture check: PASS ({len(REQUIRED)} fixture files + command contracts)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
