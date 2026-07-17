#!/usr/bin/env python3
"""Check versioned AILI workflow-orchestration contract fixtures."""

from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
from pathlib import PurePosixPath
import re
import stat
import sys
import tempfile
from typing import Any


SCHEMA_VERSION = "1.0"
PROFILES = ("scaffold", "generated-adapter-boundary", "residual")
UMBRELLA_CHANGE = "complete-aili-workflow-orchestration"
UMBRELLA_TASK_IDS = tuple(
    f"{major}.{minor}"
    for major, final_minor in (
        (1, 6),
        (2, 9),
        (3, 6),
        (4, 6),
        (5, 5),
        (6, 5),
        (7, 5),
        (8, 7),
        (9, 8),
        (10, 5),
        (11, 5),
        (12, 7),
    )
    for minor in range(1, final_minor + 1)
)
TASK_ORACLE_CONTRACT = {
    "scope": UMBRELLA_CHANGE,
    "generic_lifecycle_derivation": "active accepted contract and current task rows",
    "task_ids": list(UMBRELLA_TASK_IDS),
    "task_state_source": f"openspec/changes/{UMBRELLA_CHANGE}/tasks.md",
    "task_state_derivation": "checked_task_ids, checked, and unchecked are derived fresh from current checklist marks on every run",
    "current_acceptance": {
        "decision": "A43/DEF-E12-ACCEPT-DYNAMIC-TASK-STATE-ORACLE",
        "item": 44,
        "state": "accepted",
        "checks_implementation_task": False,
    },
    "historical_or_stale": [
        "A41/item-43 accepted with historical 31 checked/43 unchecked snapshot",
        "A32/item-41",
        "pre-A33 completion and task-audit evidence",
        "A33-era 32 checked/42 unchecked",
        "OQ-008/item-42 superseded-unaccepted",
        "A30 runtime evidence for current A33",
    ],
}
SOURCE_CLASSES = {
    "canonical source",
    "generated/installed adapter",
    "upstream reference",
    "historical evidence",
    "out of scope",
}
REQUIRED_CATEGORIES = {
    "dcp",
    "pseudo-goal",
    "classifier-grilling",
    "continuity-memory-handoff",
    "review-convergence",
    "cross-root",
    "codegraph-graphify",
    "upstream-provenance",
    "docs-manifests-fixtures-tests-generated",
}
CANONICAL_PATH_CONTRACT = {
    "source_register": {
        "path": "docs/harness/workflow-orchestration-source-register.md",
        "owner": "P1",
        "state": "present",
    },
    "artifact_contract": {
        "path": ".agents/skills/aili-delivery-flow/references/artifact-contracts.md",
        "owner": "P3/P5",
        "state": "present",
    },
    "finding_result": {
        "path": ".agents/skills/aili-delivery-flow/references/protocols/subagent-result.md",
        "owner": "P6/P7",
        "state": "present",
    },
    "worktree_context": {
        "path": ".agents/skills/aili-delivery-flow/references/protocols/worktree-context.md",
        "owner": "P6",
        "state": "present",
    },
    "role_overlay": {
        "path": ".agents/skills/aili-delivery-flow/references/protocols/subagent-task-packet.md",
        "owner": "P6",
        "state": "present",
    },
    "loop_envelope": {
        "path": ".agents/skills/aili-delivery-flow/references/artifact-contracts.md#shared-loop-envelope",
        "owner": "P3/P5",
        "state": "present",
    },
    "review_arbitration": {
        "path": "openspec/changes/<change-id>/review-arbitration.md",
        "owner": "P7",
        "state": "planned",
    },
    "graphify_reference": {
        "path": ".agents/skills/local-review-gate/references/graphify-local-review.md",
        "owner": "P9",
        "state": "present",
    },
}
REQUIRED_REJECTED_CONCEPTS = {
    "baseline-manifest.json",
    "content digests",
    "revision approval",
    "nonce approval",
    "receipt approval",
    "worktree registry",
    "worktree maintenance",
    "P1-P4 permission profiles",
    "independent target sessions",
}
REQUIRED_CASES = {
    "inventory-required-categories",
    "inventory-source-classification",
    "inventory-exact-ownership",
    "canonical-path-resolution",
    "generated-ignored-boundary",
    "old-graphify-forbidden",
    "rejected-machinery-absent",
    "shared-protocol-fields",
    "repository-evidence-reuse-discipline",
    "active-dcp-goal-allowed-at-scaffold",
    "inventory-exact-task-oracle",
    "inventory-rose-plus-19-managed-agents",
    "a33-scaffold-field-definitions",
    "a33-rejected-expansion",
    "package-worktree-roots-excluded",
    "stale-authority-later-owner-flags",
    "repair-scaffold-blocked-unverified-exit3",
    "repair-ready-profiles-require-semantics",
    "repair-path-normalization",
    "repair-p6-role-and-wave-ownership",
    "repair-generated-agents-split",
    "repair-compact-result-schema",
    "repair-rejected-machinery-semantic-scan",
}
FORBIDDEN_GRAPHIFY_PATH = "openspec/changes/integrate-codegraph-graphify-workflow"
PACKAGE_IDS = {f"P{number}" for number in range(1, 13)}
# Accepted serialization order for deriving shared edit-path package lists.
ACCEPTED_SERIALIZATION_ORDER = (
    "P2",
    "P5",
    "P3",
    "P4",
    "P6",
    "P7",
    "P8",
    "P9",
    "P10",
    "P11",
)
PACKAGE_1_FILES = {
    "scripts/workflow_contract_check.py",
    "docs/harness/fixtures/workflow-orchestration-fixtures.yaml",
    "docs/harness/workflow-orchestration-source-register.md",
}
P6_REQUIRED_ROLE_PATHS = {
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
}
P6_REQUIRED_CROSS_ROOT_PATHS = P6_REQUIRED_ROLE_PATHS | {
    ".agents/skills/git-workflow-and-versioning/SKILL.md",
    ".agents/skills/aili-delivery-flow/references/protocols/worktree-context.md",
    ".agents/skills/aili-delivery-flow/references/protocols/subagent-task-packet.md",
    ".agents/skills/aili-delivery-flow/references/protocols/subagent-result.md",
    ".agents/skills/aili-delivery-flow/references/protocols/implementation-package.md",
    ".agents/skills/aili-delivery-flow/references/backend-routing.md",
    ".agents/skills/parallel-subagent-dispatch/SKILL.md",
    "scripts/delegation_protocols_check.py",
    "scripts/opencode_permission_probe.mjs",
    "docs/harness/fixtures/cross-worktree-permission-fixtures.yaml",
    "tests/opencode-permission-probe.test.mjs",
}
MANAGED_AGENT_PATHS = P6_REQUIRED_ROLE_PATHS - {"agents/rose.md"}
A33_IDENTITY_FIELDS = (
    "identity_state",
    "declared_root",
    "path_state",
    "canonical_root",
    "git_toplevel",
    "git_private_dir",
    "git_common_dir",
    "git_head",
    "git_branch",
    "detached_head",
    "worktree_membership",
    "dirty_state",
    "tracked_files",
    "untracked_files",
    "ignored_files",
    "artifact_files",
    "unknown_files",
)
A33_RESULT_FIELDS = (
    "id",
    "subset",
    "status",
    "exit_code",
    "operation_id",
    "approval_ref",
    "host_identity",
    "source_identity",
    "target_identity",
    "expected_delta",
    "observed_delta",
    "evidence_refs",
    "unverified",
    "cleanup_state",
)
A33_PREPARE_FIELDS = (
    "schema_version",
    "command",
    "status",
    "exit_code",
    "run_id",
    "run_root",
    "pending_operations",
    "worktree_effects",
    "unverified",
)
A33_OPERATION_RESULT_FIELDS = (
    "schema_version",
    "command",
    "status",
    "exit_code",
    "run_id",
    "operation",
    "approval",
    "effect_started",
    "expected_delta",
    "observed_delta",
    "evidence_refs",
    "unverified",
)
A33_STATIC_RESULT_FIELDS = (
    "schema_version",
    "command",
    "mode",
    "status",
    "exit_code",
    "mandatory_case_ids",
    "observed_case_ids",
    "case_set_equal",
    "cases",
    "contract_mutations",
    "summary",
    "unverified",
    "ephemeral_result",
)
A33_RUNTIME_JOIN_FIELDS = (
    "schema_version",
    "command",
    "mode",
    "status",
    "exit_code",
    "run_id",
    "mandatory_case_ids",
    "observed_case_ids",
    "case_set_equal",
    "cases",
    "operations",
    "cleanup",
    "summary",
    "unverified",
    "ephemeral_result",
)
A33_GLOBAL_JOIN_FIELDS = (
    "schema_version",
    "command",
    "mode",
    "status",
    "exit_code",
    "static_result_ref",
    "runtime_result_ref",
    "static_mandatory_case_ids",
    "runtime_mandatory_case_ids",
    "mandatory_case_ids",
    "observed_case_ids",
    "case_set_equal",
    "cases",
    "mutation_summary",
    "cleanup",
    "summary",
    "unverified",
)
A33_OPERATION_FIELDS = (
    "operation_id",
    "kind",
    "operation_class",
    "source",
    "destination",
    "repo_key",
    "worktree_key",
    "branch",
    "base_ref",
    "branch_mode",
    "reflog_policy",
)
A33_APPROVAL_FIELDS = (
    "approval_id",
    "run_id",
    "operation_id",
    "kind",
    "operation_class",
    "source",
    "destination",
    "repo_key",
    "worktree_key",
    "branch",
    "base_ref",
    "branch_mode",
    "reflog_policy",
    "expiry",
    "decision_ref",
    "trusted_code_risk",
    "status",
)
A33_DELTA_FIELDS = (
    "target_path",
    "worktree_membership",
    "common_dir_identity",
    "common_dir_admin_entry",
    "branch_ref",
    "branch_reflog",
    "unrelated_common_dir_entries",
    "unrelated_refs",
    "config",
    "hooks",
    "unrelated_worktree_records",
    "unrelated_prunable_entries",
    "other_files",
)
A33_SCAFFOLD_CONTRACT = {
    "contract": "A33 scaffold definitions only",
    "mode": {
        "field": "mode",
        "historical": "a30-a31-external-read",
        "current": "a33-attached-shared-trust-domain",
        "mixed_fields_or_guarantees": "reject",
    },
    "keys": {
        "fields": ["repo_key", "worktree_key"],
        "pattern": r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$",
        "nonempty": True,
        "required_on": [
            "runtime-prepare.pending_operations[]",
            "add/remove.operation",
            "add/remove.approval",
        ],
        "approval_operation_destination_exact_match": True,
    },
    "identity": {
        "name": "A33Identity",
        "fields": list(A33_IDENTITY_FIELDS),
        "hash_or_digest_fields": [],
        "host_state": "populated",
        "source_state": "populated",
        "add_target_transition": "absent->populated",
        "remove_target_transition": "populated->absent",
        "absent_nonnull_fields": [
            "identity_state",
            "declared_root",
            "path_state",
            "worktree_membership",
        ],
        "absent_other_fields": None,
        "file_arrays": "duplicate-free sorted canonical repository-relative strings",
        "dirty_state": {
            "tracked_modified": "boolean",
            "tracked_deleted": "boolean",
            "untracked_count": "nonnegative_integer",
            "ignored_count": "nonnegative_integer",
        },
    },
    "target_rules_and_artifacts": {
        "target_rules_read_at": ["operation", "dispatch"],
        "target_rules_effect": "narrow-only",
        "same_level_conflict": "block",
        "broad_host_scan": False,
        "lane_repository_count": 1,
        "artifact_destination": "owning target repository",
    },
    "result_records": {
        "runtime_prepare_fields": list(A33_PREPARE_FIELDS),
        "operation_result_fields": list(A33_OPERATION_RESULT_FIELDS),
        "static_result_fields": list(A33_STATIC_RESULT_FIELDS),
        "runtime_join_fields": list(A33_RUNTIME_JOIN_FIELDS),
        "global_join_fields": list(A33_GLOBAL_JOIN_FIELDS),
        "joined_case_fields": list(A33_RESULT_FIELDS),
        "all_fields_present": True,
        "absent_or_inapplicable_value": None,
        "absence_string_sentinel": "forbidden",
        "observed_remove_trusted_code_risk_exception": "not_applicable",
    },
    "operation": {
        "pending_operation_fields": [*A33_OPERATION_FIELDS, "approval_required"],
        "operation_fields": list(A33_OPERATION_FIELDS),
        "approval_fields": list(A33_APPROVAL_FIELDS),
        "classes": ["driver_fixture", "real"],
        "class_must_match_approval": True,
        "add_trusted_code_risk": ["accepted", "declined", "unavailable", None],
        "add_effect_requires": "accepted",
        "observed_remove_trusted_code_risk": "not_applicable",
        "missing_approval_trusted_code_risk": None,
    },
    "branch_and_reflog": {
        "branch_modes": ["existing", "create"],
        "reflog_policies": ["enabled", "disabled"],
        "existing": "no branch ref or reflog creation",
        "create_enabled": "exact branch ref and exact branch reflog created",
        "create_disabled": "exact branch ref created and branch reflog remains absent",
        "remove": "branch ref and branch reflog unchanged",
    },
    "admin_deltas": {
        "fields": list(A33_DELTA_FIELDS),
        "common_dir_identity": "unchanged",
        "add_allowed": "declared admin entry/membership plus bound create-mode ref/reflog transaction",
        "remove_allowed": "declared admin entry/membership deletion only",
        "unrelated_fields": "unchanged",
        "unrelated_prunable_entries": "unchanged",
    },
}
A33_REJECTION_CONTRACT = {
    "generic_lifecycle_counts": "derive from the active accepted contract; 12 packages/74 tasks are this umbrella only",
    "forbidden_new_machinery": [
        "helper",
        "registry",
        "manifest",
        "public command",
        "dependency",
        "daemon",
        "maintenance plane",
        "host selector",
        "cleanup manager",
    ],
    "forbidden_package_entries": [".worktrees", "worktrees", ".tmp/worktrees"],
    "managed_subagents": {
        "count": 19,
        "external_directory": "deny",
        "ask_or_allow": "reject",
        "rose_distinction": "per-operation ask only",
        "builtins_excluded": ["explore", "general"],
    },
    "historical_only": [
        "A30 runtime evidence",
        "A31 external-read routing",
        "A32/item-41 readiness",
        "A41/item-43 acceptance and its 31 checked/43 unchecked snapshot",
        "pre-A33 completion/task-audit evidence",
        "A33-era 32 checked/42 unchecked",
        "OQ-008/item-42 readiness",
    ],
    "hard_isolation_claim": "reject; shared trust domain is a soft boundary",
    "current_readiness": "A43/item-44 accepted; acceptance alone completes no task; mutable task state is derived from current tasks.md",
    "package_12_authority": "minimal changed-scope BUILD completion check; broad integration/release review belongs to fresh SHIP intent",
    "later_owner_flags": {
        "A33 operation and runtime protocols": "P5/P6/P11",
        "managed role and installed equality behavior": "P6/P10/P11",
        "convergence and stale-evidence behavior": "P7/P11",
        "documentation/template/package synchronization": "P10",
        "minimal BUILD completion evidence": "P12",
    },
}
A33_FORBIDDEN_NEW_PATHS = {
    "scripts/opencode_worktree_worker.py",
    "manifests/opencode-worker-runtime.json",
    "tests/test_opencode_worktree_worker.py",
    "baseline-manifest.json",
}
A33_FORBIDDEN_PACKAGE_ROOTS = {".worktrees", "worktrees", ".tmp/worktrees"}
EXPECTED_PUBLIC_COMMANDS = {"build", "define", "ideate", "local-review", "ship"}
WORKFLOW_PROFILE_CONTRACT = {
    "scaffold": {
        "ready": True,
        "owner_package": "P1",
        "contract_state": {"status": "pass", "blocked": [], "unverified": []},
        "json_fields": [
            "schema_version",
            "profile",
            "status",
            "sources",
            "ownership",
            "generated",
            "traceability",
            "task_oracle",
            "agent_inventory",
            "a33_scaffold",
            "a33_rejections",
            "regression_probes",
            "blocked",
            "unverified",
            "errors",
        ],
    },
    "generated-adapter-boundary": {
        "ready": True,
        "owner_package": "P2",
        "fixture": "docs/harness/fixtures/generated-openspec-adapter-fixtures.yaml",
        "json_fields": [
            "schema_version",
            "profile",
            "status",
            "aili_routes",
            "direct_adapter_cases",
            "claim_boundary",
            "cases",
            "blocked",
            "unverified",
            "errors",
        ],
    },
    "residual": {
        "ready": True,
        "owner_packages": ["P4", "P5", "P10", "P11"],
        "contract_state": {"status": "pass", "blocked": [], "unverified": []},
        "json_fields": [
            "schema_version",
            "profile",
            "status",
            "matches",
            "classifications",
            "blocked",
            "unverified",
            "errors",
        ],
    },
}
INSPECTION_ONLY_SOURCE_CONTRACT = {
    "id": "codegraph-generated-boundary-ignore",
    "classification": "canonical source",
    "state": "inspection-only generated-boundary evidence",
    "owner_package": "none",
    "paths": [".gitignore"],
    "non_edit_reason": "accepted tasks inspect the ignored generated boundary but assign no .gitignore edit",
}
NORMATIVE_REQUIREMENT_IDS = {
    *(f"LIFE-{number:03d}" for number in range(1, 10)),
    *(f"INST-{number:03d}" for number in range(1, 6)),
    "INST-REM-001",
    *(f"CI-REM-{number:03d}" for number in range(1, 6)),
    *(f"CG-{number:03d}" for number in range(1, 4)),
    *(f"DELEG-{number:03d}" for number in range(1, 6)),
    *(f"CONT-{number:03d}" for number in range(1, 6)),
    *(f"GF-{number:03d}" for number in range(1, 8)),
    *(f"ROUTE-{number:03d}" for number in range(1, 9)),
    *(f"GRILL-{number:03d}" for number in range(1, 9)),
    *(f"REV-{number:03d}" for number in range(1, 5)),
    *(f"HAND-{number:03d}" for number in range(1, 4)),
    *(f"SKILL-{number:03d}" for number in range(1, 6)),
    *(f"MEM-{number:03d}" for number in range(1, 6)),
    *(f"WT-{number:03d}" for number in range(1, 5)),
}
AUTHORITATIVE_SOURCE_IDS = {
    *(f"PART-I-I.{number}" for number in range(13)),
    *(f"INBOX-P{number}" for number in range(1, 7)),
    "DEF-E1-LOOPS-NL",
    *(f"DEF-E1-LOOPS-NL-FIX{number}" for number in range(1, 6)),
    "DEF-E2-CONSOLIDATED-REVIEW",
    "DEF-E3-TASK-CHECKLIST-AUDIT",
}
TRACEABILITY_COMMANDS = {
    "C-HARNESS": "python scripts/harness_fixture_check.py",
    "C-NODE": "npm run build && node --test tests/*.test.mjs",
    "C-PYTHON": "python -m unittest discover -s tests -p '*.py'",
    "C-SCAFFOLD": "python scripts/workflow_contract_check.py --project . --change complete-aili-workflow-orchestration --profile scaffold --fixture docs/harness/fixtures/workflow-orchestration-fixtures.yaml --json",
    "C-GENERATED-ADAPTER": "python scripts/workflow_contract_check.py --project . --change complete-aili-workflow-orchestration --profile generated-adapter-boundary --fixture docs/harness/fixtures/generated-openspec-adapter-fixtures.yaml --json",
    "C-RESIDUAL": "python scripts/workflow_contract_check.py --project . --change complete-aili-workflow-orchestration --profile residual --fixture docs/harness/fixtures/workflow-orchestration-fixtures.yaml --json",
    "C-OPENCODE": "npm run build && node scripts/opencode_permission_probe.mjs --project . --opencode-version 1.17.18 --fixture docs/harness/fixtures/cross-worktree-permission-fixtures.yaml --json",
    "C-UPSTREAM": "python scripts/upstream_reference_check.py --project . --manifest manifests/upstream-references.json --fixture docs/harness/fixtures/upstream-reference-fixtures.yaml --opencode-version 1.17.18 --verify-installed-catalog --json",
}
CANONICAL_SOURCE_IDS = {
    "dcp-runtime", "dcp-docs-manifest-tests", "goal-delivery-sources",
    "goal-fixture-checker-sources", "classifier-delivery", "grilling-sources",
    "continuity-sources", "continuity-registry-docs", "review-skills", "review-agents",
    "cross-root-protocols", "cross-root-canonical-context", "codegraph-runtime-policy",
    "codegraph-generated-boundary-ignore", "graphify-current-contract",
    "old-graphify-change", "existing-upstream-references", "upstream-provenance-catalogs",
    "docs-manifests-fixtures-tests", "package11-aggregate-tests", "generated-openspec-adapters",
    "generated-project-agents", "agents-template-generator", "generated-runtime-outputs",
    "historical-archive", "rejected-native-machinery",
    "retired-build-authority",
}
RETIRED_BUILD_AUTHORITY = ".agents/skills/aili-delivery-flow/references/build-goal-mode.md"
RESIDUAL_CONTROL_FILES = {
    "scripts/workflow_contract_check.py",
    "tests/workflow-contract-check.test.mjs",
    "docs/harness/fixtures/workflow-orchestration-fixtures.yaml",
    "docs/harness/workflow-orchestration-source-register.md",
}
INDEPENDENT_RESIDUAL_SOURCE_ROOTS = {
    "src",
    "scripts",
    "tests",
    "agents",
    "commands",
    "docs/harness",
    "docs/opencode-setup.md",
    "README.md",
    "templates/AGENTS.md",
    "templates/opencode-global-AGENTS.md",
    "manifests",
    "workflow.components.yaml",
    "package.json",
    ".agents/skills",
}
REQUIRED_COMPONENT_REGISTRY_IDS = {
    "lifecycle", "backend", "harness-triage", "harness-change", "protocol",
    "verification", "memory", "command", "install", "source-boundary",
    "upstream-provenance", "distribution",
}
REQUIRED_PACKAGE_AUTHORITY_ENTRIES = {
    "agents/", ".agents/", "commands/", "manifests/", "templates/AGENTS.md",
    "templates/opencode-global-AGENTS.md", "scripts/agents_md.py", "README.md",
    "docs/opencode-setup.md",
}
WAVE_A_PACKAGES = ("P4", "P6", "P8")
LEGITIMATE_MATCH_CLASSIFICATIONS = {"scanner self-definition", "negative test fixture"}
REJECTED_SEMANTIC_RULES = {
    "baseline-manifest": re.compile(r"\bbaseline[-_ ]manifest(?:\.json)?\b", re.IGNORECASE),
    "digest-nonce-receipt-revision-approval": re.compile(
        r"\b(?:content[-_ ]?digests?|sha(?:256)?[-_ ]?(?:approval|receipt)|"
        r"(?:digest|nonce|receipt|revision)[-_ ]?(?:approval|gate|token)|"
        r"approval[-_ ]?(?:digest|nonce|receipt|revision))\b",
        re.IGNORECASE,
    ),
    "worktree-registry-maintenance": re.compile(
        r"\bworktree[-_ ](?:registry|maintenance)(?:[-_ ](?:cli|plane))?\b",
        re.IGNORECASE,
    ),
    "p1-p4-permission-profiles": re.compile(
        r"(?:\bP[1-4]\b.{0,40}\bpermission[-_ ]profiles?\b|"
        r"\bpermission[-_ ]profiles?\b.{0,40}\bP[1-4]\b)",
        re.IGNORECASE,
    ),
    "independent-target-sessions": re.compile(
        r"\bindependent[-_ ]target[-_ ]sessions?\b", re.IGNORECASE
    ),
}
RESULT_FIELD_ORDER = (
    "result_id",
    "trace_id",
    "lane",
    "owner",
    "status",
    "confidence",
    "worktree_context_ref",
    "declared_repository",
    "cwd",
    "target_rules_ref",
    "artifact_destination",
    "inspected_scope",
    "checks",
    "freshness",
    "skipped_checks",
    "soft_boundary_limitations",
    "blockers",
    "unverified",
    "findings",
    "convergence_links",
    "review_arbitration_ref",
)
RESULT_FIELDS = set(RESULT_FIELD_ORDER)
FINDING_FIELD_ORDER = (
    "finding_id",
    "source",
    "claim",
    "severity",
    "evidence_anchors",
    "affected_requirement",
    "proposed_disposition",
    "required_action",
    "verification",
)
FINDING_FIELDS = set(FINDING_FIELD_ORDER)
GENERATED_ROUTE_MAP = {
    "IDEATE": "commands/ideate.md",
    "DEFINE": "commands/define.md",
    "BUILD": "commands/build.md",
    "SHIP": "commands/ship.md",
}
GENERATED_ADAPTER_ROOTS = (".opencode/commands", ".opencode/skills")
GENERATED_ADAPTER_CASES = {
    "opsx-apply-command": ".opencode/commands/opsx-apply.md",
    "opsx-archive-command": ".opencode/commands/opsx-archive.md",
    "opsx-explore-command": ".opencode/commands/opsx-explore.md",
    "opsx-propose-command": ".opencode/commands/opsx-propose.md",
    "openspec-apply-skill": ".opencode/skills/openspec-apply-change/SKILL.md",
    "openspec-archive-skill": ".opencode/skills/openspec-archive-change/SKILL.md",
    "openspec-explore-skill": ".opencode/skills/openspec-explore/SKILL.md",
    "openspec-propose-skill": ".opencode/skills/openspec-propose/SKILL.md",
}
GENERATED_CASE_CLASSIFICATIONS = {
    "canonical source",
    "generated/installed adapter",
    "upstream reference",
    "outside AILI claim boundary",
}
TASK_AUDIT_FIELD_ORDER = (
    "task_id",
    "accepted requirement/decision/risk",
    "expected behavior",
    "implementation files/artifacts",
    "fresh tests/inspection/review evidence",
    "status",
    "findings",
    "disposition",
    "freshness",
)
TASK_AUDIT_FIELDS = set(TASK_AUDIT_FIELD_ORDER)
RESIDUAL_CLASSIFICATIONS = {
    "active violation",
    "negative documentation",
    "historical evidence",
    "generated/installed adapter",
    "out of scope",
}
REPAIR_CASE_EXPECTATIONS = {
    "repair-scaffold-blocked-unverified-exit3": {
        "probe": "contract-state-blocked-unverified",
        "expected_exits": [3, 3],
        "violation_exit": 5,
    },
    "repair-ready-profiles-require-semantics": {
        "probe": "ready-profile-empty",
        "profiles": ["generated-adapter-boundary", "residual"],
        "expected_exit": 5,
    },
    "repair-path-normalization": {
        "probe": "path-alias-matrix",
        "rejected": [
            "absolute",
            "dot",
            "dotdot",
            "backslash",
            "non-normalized",
            "placeholder",
            "anchor",
        ],
        "expected_exit": 5,
    },
    "repair-p6-role-and-wave-ownership": {
        "probe": "permission-role-ownership",
        "expected_p6_roles": 20,
        "wave_a_disjoint": True,
        "expected_exit": 5,
    },
    "repair-generated-agents-split": {
        "probe": "generated-agents-classification",
        "expected_generated": ["AGENTS.md"],
        "expected_canonical": ["templates/AGENTS.md", "scripts/agents_md.py"],
        "expected_exit": 5,
    },
    "repair-compact-result-schema": {
        "probe": "result-schema-parse",
        "result_fields": list(RESULT_FIELD_ORDER),
        "finding_fields": list(FINDING_FIELD_ORDER),
        "duplicate_reordered_or_ambiguous": "reject",
        "expected_exit": 5,
    },
    "repair-rejected-machinery-semantic-scan": {
        "probe": "active-negative-incomplete-scan",
        "expected_exits": [5, 3],
        "required_classifications": ["active violation", "negative documentation"],
    },
}


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate workflow orchestration scaffold and later contract profiles."
    )
    parser.add_argument("--project", required=True, help="Repository root.")
    parser.add_argument("--change", required=True, help="OpenSpec change id.")
    parser.add_argument("--profile", required=True, choices=PROFILES)
    parser.add_argument("--fixture", required=True, help="JSON-subset YAML fixture path.")
    parser.add_argument("--json", action="store_true", dest="json_output")
    parser.add_argument(
        "--final-closure",
        action="store_true",
        help="Require every canonical task-audit row to contain passing final evidence.",
    )
    parser.add_argument(
        "--task-audit",
        help="Repository-relative path to the separate ROSE-owned final task-audit JSON.",
    )
    return parser.parse_args(argv)


def resolve_inside(project: Path, value: str, label: str) -> Path:
    candidate = Path(value)
    resolved = candidate.resolve() if candidate.is_absolute() else (project / candidate).resolve()
    if resolved != project and project not in resolved.parents:
        raise ValueError(f"{label} must remain inside project: {value}")
    return resolved


def validate_repo_path(
    value: Any,
    label: str,
    *,
    allow_change_placeholder: bool = False,
    expected_anchor: str | None = None,
) -> str | None:
    if not isinstance(value, str) or not value:
        return f"{label} must be a non-empty repository-relative POSIX path"
    if value != value.strip() or any(ord(character) < 32 for character in value):
        return f"{label} contains whitespace/control aliases: {value!r}"
    if "\\" in value:
        return f"{label} must use POSIX separators: {value!r}"
    if value.count("#") > 1:
        return f"{label} contains more than one anchor: {value!r}"
    if "#" in value:
        base, anchor = value.split("#", 1)
        if expected_anchor is None or anchor != expected_anchor:
            return f"{label} has an unapproved anchor: {value!r}"
    else:
        base = value
        if expected_anchor is not None:
            return f"{label} must use anchor #{expected_anchor}"
    path = PurePosixPath(base)
    parts = path.parts
    if path.is_absolute() or base.startswith("/") or base.startswith("~"):
        return f"{label} must be repository-relative: {value!r}"
    if not parts or any(part in {"", ".", ".."} for part in parts) or "//" in base:
        return f"{label} is not normalized: {value!r}"
    if path.as_posix() != base or (parts and parts[0].endswith(":")):
        return f"{label} is not normalized repository-relative POSIX syntax: {value!r}"
    placeholder_parts = [part for part in parts if "<" in part or ">" in part]
    if placeholder_parts:
        if not allow_change_placeholder or placeholder_parts != ["<change-id>"]:
            return f"{label} contains an unapproved placeholder: {value!r}"
    return None


def resolve_repo_field_target(
    project: Path,
    value: str,
    label: str,
    *,
    allow_missing: bool,
) -> tuple[Path | None, str | None]:
    base = path_without_anchor(value)
    if "<change-id>" in base:
        return None, None
    candidate = project.joinpath(*PurePosixPath(base).parts)
    try:
        resolved = candidate.resolve(strict=False)
    except (OSError, RuntimeError) as exc:
        return None, f"{label} cannot be resolved safely: {exc}"
    if resolved != project and project not in resolved.parents:
        return None, f"{label} resolves outside project: {value} -> {resolved}"
    if not allow_missing and not resolved.exists():
        return None, f"{label} does not exist: {value}"
    return resolved, None


def expand_owner_packages(value: str) -> set[str] | None:
    if value == "none":
        return set()
    packages: set[str] = set()
    for token in value.split("/"):
        if re.fullmatch(r"P\d+-P\d+", token):
            start_text, end_text = token.split("-", 1)
            start = int(start_text[1:])
            end = int(end_text[1:])
            if start > end:
                return None
            packages.update(f"P{number}" for number in range(start, end + 1))
        elif token in PACKAGE_IDS:
            packages.add(token)
        else:
            return None
    return packages


def source_path_owned_by(source_path: str, owned_paths: set[str], project: Path) -> bool:
    if source_path in owned_paths:
        return True
    target, error = resolve_repo_field_target(
        project, source_path, "source ownership path", allow_missing=True
    )
    if error or target is None or not target.is_dir():
        return False
    prefix = source_path.rstrip("/") + "/"
    return any(path.startswith(prefix) for path in owned_paths)


def derive_independent_residual_roots(project: Path) -> tuple[list[str], list[str]]:
    """Build residual roots without consulting the mutable workflow fixture inventories."""
    errors: list[str] = []
    roots = {
        relative
        for relative in INDEPENDENT_RESIDUAL_SOURCE_ROOTS
        if (project / relative).exists()
    }

    def allowlisted(value: str) -> bool:
        return any(
            value == root or value.startswith(f"{root}/") or root.startswith(f"{value}/")
            for root in INDEPENDENT_RESIDUAL_SOURCE_ROOTS
        )

    registry_data: dict[str, Any] = {}
    for relative in ("workflow.components.yaml", "manifests/rose-aili.components.json", "package.json"):
        try:
            data = json.loads((project / relative).read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            errors.append(f"independent residual registry/manifest is unreadable: {relative}: {exc}")
            continue
        registry_data[relative] = data

        def visit(value: Any, key: str | None = None) -> None:
            if isinstance(value, dict):
                for child_key, child in value.items():
                    visit(child, child_key)
            elif isinstance(value, list):
                for child in value:
                    visit(child, key)
            elif isinstance(value, str) and key in {"path", "authority", "fallback"}:
                candidate = value.rstrip("/")
                if allowlisted(candidate) and (project / candidate).exists():
                    roots.add(candidate)

        visit(data)

    component_registry = registry_data.get("workflow.components.yaml")
    component_rows = component_registry.get("components") if isinstance(component_registry, dict) else None
    if not isinstance(component_rows, list):
        errors.append("independent component registry must contain a components array")
    else:
        component_ids = [row.get("id") for row in component_rows if isinstance(row, dict)]
        if len(component_ids) != len(set(component_ids)) or set(component_ids) != REQUIRED_COMPONENT_REGISTRY_IDS:
            errors.append("independent component registry ids differ from the canonical active authority set")
        for index, row in enumerate(component_rows):
            if not isinstance(row, dict) or set(row) not in ({"id", "authority"}, {"id", "authority", "fallback"}):
                errors.append(f"independent component registry row {index} has invalid fields")
                continue
            for field in ("authority", "fallback"):
                if field not in row:
                    continue
                value = row[field].rstrip("/")
                path_error = validate_repo_path(value, f"workflow.components[{index}].{field}")
                if path_error:
                    errors.append(path_error)
                elif not (project / value).exists():
                    errors.append(f"independent component registry authority is missing: {value}")
                elif allowlisted(value):
                    roots.add(value)

    component_manifest = registry_data.get("manifests/rose-aili.components.json")
    manifest_components = component_manifest.get("components") if isinstance(component_manifest, dict) else None
    if not isinstance(manifest_components, dict):
        errors.append("independent component manifest lacks components")
    else:
        disk_names = {
            "agents": {path.stem for path in (project / "agents").glob("*.md")},
            "commands": {path.stem for path in (project / "commands").glob("*.md")},
            "skills": {path.parent.name for path in (project / ".agents/skills").glob("*/SKILL.md")},
        }
        for kind, names in disk_names.items():
            rows = manifest_components.get(kind)
            if not isinstance(rows, list):
                errors.append(f"independent component manifest {kind} must be an array")
                continue
            manifest_names = [row.get("name") for row in rows if isinstance(row, dict)]
            if len(manifest_names) != len(set(manifest_names)) or set(manifest_names) != names:
                errors.append(
                    f"independent component manifest {kind} differs from named source tree; "
                    f"missing={sorted(names - set(manifest_names))}, extra={sorted(set(manifest_names) - names)}"
                )
            for row in rows:
                if not isinstance(row, dict) or not isinstance(row.get("path"), str):
                    continue
                value = row["path"].rstrip("/")
                if not (project / value).exists():
                    errors.append(f"independent component manifest path is missing: {value}")
                elif allowlisted(value):
                    roots.add(value)

    package_registry = registry_data.get("package.json")
    package_files = package_registry.get("files") if isinstance(package_registry, dict) else None
    if not isinstance(package_files, list) or not REQUIRED_PACKAGE_AUTHORITY_ENTRIES.issubset(set(package_files)):
        missing = sorted(REQUIRED_PACKAGE_AUTHORITY_ENTRIES - set(package_files or []))
        errors.append(f"independent package registry omits active authority entries: {missing}")

    register = project / "docs/harness/workflow-orchestration-source-register.md"
    try:
        register_text = register.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        errors.append(f"independent residual source register is unreadable: {exc}")
    else:
        if "checked-in registry/manifests/source-tree/package allowlist" not in register_text:
            errors.append("independent residual source register lacks the canonical root authority marker")

    source_rows = None
    try:
        workflow_fixture = load_fixture(project / "docs/harness/fixtures/workflow-orchestration-fixtures.yaml")
        source_rows = workflow_fixture.get("sources")
    except ValueError as exc:
        errors.append(f"independent source registry is unreadable: {exc}")
    if not isinstance(source_rows, list):
        errors.append("independent source registry must contain source rows")
    else:
        source_paths = {
            path.rstrip("/")
            for row in source_rows if isinstance(row, dict)
            for path in row.get("paths", []) if isinstance(path, str)
        }
        missing_roots = sorted(
            root for root in INDEPENDENT_RESIDUAL_SOURCE_ROOTS
            if not any(path == root or path.startswith(f"{root}/") or root.startswith(f"{path}/") for path in source_paths)
        )
        if missing_roots:
            errors.append(f"independent source registry omits active authority roots: {missing_roots}")

    missing_allowlist = sorted(
        relative for relative in INDEPENDENT_RESIDUAL_SOURCE_ROOTS if not (project / relative).exists()
    )
    if missing_allowlist:
        errors.append(f"independent residual package allowlist paths are missing: {missing_allowlist}")
    return sorted(roots - RESIDUAL_CONTROL_FILES), errors


def load_fixture(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot load JSON-subset fixture {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError("fixture top level must be an object")
    return data


def collect_test_case_catalog(
    project: Path, section: dict[str, Any], errors: list[str]
) -> dict[str, set[str]]:
    """Derive evidence IDs from checked fixtures/tests, then validate aliases against them."""
    catalog: dict[str, set[str]] = {}
    concrete: dict[tuple[str, str], set[str]] = {}
    fixture_commands = {
        "workflow-orchestration-fixtures.yaml": "C-SCAFFOLD",
        "generated-openspec-adapter-fixtures.yaml": "C-GENERATED-ADAPTER",
        "cross-worktree-permission-fixtures.yaml": "C-OPENCODE",
        "upstream-reference-fixtures.yaml": "C-UPSTREAM",
    }

    def add(case_id: str, command_id: str, source_path: str) -> None:
        catalog.setdefault(case_id, set()).add(command_id)
        concrete.setdefault((source_path, case_id), set()).add(command_id)

    def visit(value: Any, command_id: str, source_path: str) -> None:
        if isinstance(value, dict):
            case_id = value.get("id")
            if isinstance(case_id, str) and case_id:
                add(case_id, command_id, source_path)
            for child in value.values():
                visit(child, command_id, source_path)
        elif isinstance(value, list):
            for child in value:
                visit(child, command_id, source_path)

    fixture_root = project / "docs" / "harness" / "fixtures"
    for path in sorted(fixture_root.glob("*.yaml")):
        try:
            value = load_fixture(path)
        except ValueError as exc:
            if path.name == "cross-worktree-permission-fixtures.yaml":
                continue
            errors.append(f"cannot derive test/case catalog from {path.relative_to(project)}: {exc}")
            continue
        if path.name == "workflow-orchestration-fixtures.yaml":
            value = {key: child for key, child in value.items() if key != "aggregate_traceability"}
        visit(value, fixture_commands.get(path.name, "C-HARNESS"), path.relative_to(project).as_posix())

    cross_path = fixture_root / "cross-worktree-permission-fixtures.yaml"
    try:
        cross_fixture = load_fixture(cross_path)
    except ValueError as exc:
        errors.append(f"cannot derive cross-worktree case catalog: {exc}")
    else:
        relative = cross_path.relative_to(project).as_posix()
        case_arrays = (
            ("historical_a30", "case_ids"),
            ("a33", "static_mandatory_case_ids"),
            ("a33", "runtime_mandatory_case_ids"),
            ("a33", "contract_mutation_ids"),
        )
        for section_name, field_name in case_arrays:
            section_value = cross_fixture.get(section_name)
            case_ids = section_value.get(field_name) if isinstance(section_value, dict) else None
            if not isinstance(case_ids, list) or any(
                not isinstance(case_id, str) or not case_id for case_id in case_ids
            ):
                errors.append(
                    f"cannot derive cross-worktree case catalog: {section_name}.{field_name} "
                    "must be an array of non-empty strings"
                )
                continue
            for case_id in case_ids:
                add(case_id, "C-OPENCODE", relative)

    test_pattern = re.compile(r"\b(?:test|it)\(\s*[\"'`]([^\"'`]+)")
    for path in sorted((project / "tests").glob("*.test.mjs")):
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            errors.append(f"cannot derive executable test catalog from {path.relative_to(project)}: {exc}")
            continue
        for case_id in test_pattern.findall(text):
            add(case_id, "C-NODE", path.relative_to(project).as_posix())

    for path in sorted((project / "tests").glob("*.py")):
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            errors.append(f"cannot derive Python unittest catalog from {path.relative_to(project)}: {exc}")
            continue
        for test_id in re.findall(r"^\s*def\s+(test_[A-Za-z0-9_]+)\s*\(", text, re.MULTILINE):
            add(test_id, "C-PYTHON", path.relative_to(project).as_posix())

    aliases = section.get("test_evidence_aliases")
    if not isinstance(aliases, list) or not aliases:
        errors.append("aggregate_traceability.test_evidence_aliases must be a non-empty fixture catalog")
    else:
        alias_ids: list[str] = []
        for index, row in enumerate(aliases):
            label = f"aggregate_traceability.test_evidence_aliases[{index}]"
            if not isinstance(row, dict) or set(row) != {"aliases", "source_path", "actual_id", "command_ids"}:
                errors.append(f"{label} must define aliases, source_path, actual_id, and command_ids")
                continue
            case_ids = row.get("aliases")
            command_ids = row.get("command_ids")
            source_path = row.get("source_path")
            actual_id = row.get("actual_id")
            if (
                not isinstance(command_ids, list)
                or not command_ids
                or any(command_id not in TRACEABILITY_COMMANDS for command_id in command_ids)
                or not isinstance(case_ids, list)
                or not case_ids
                or any(not isinstance(case_id, str) or not case_id for case_id in case_ids)
                or not isinstance(source_path, str)
                or not isinstance(actual_id, str)
                or not actual_id
            ):
                errors.append(f"invalid test evidence alias group: {label}")
                continue
            observed_commands = concrete.get((source_path, actual_id))
            if observed_commands is None:
                errors.append(
                    f"{label}: alias source does not contain actual fixture case/executable test id "
                    f"{source_path!r} / {actual_id!r}"
                )
                continue
            if not set(command_ids).issubset(observed_commands):
                errors.append(
                    f"{label}: alias source command mismatch for {source_path!r} / {actual_id!r}; "
                    f"declared={sorted(command_ids)}, observed={sorted(observed_commands)}"
                )
                continue
            alias_ids.extend(case_ids)
            for case_id in case_ids:
                for command_id in command_ids:
                    catalog.setdefault(case_id, set()).add(command_id)
        duplicates = sorted(item for item, count in Counter(alias_ids).items() if count > 1)
        if duplicates:
            errors.append(f"duplicate test evidence aliases: {duplicates}")
    return catalog


def path_without_anchor(value: str) -> str:
    return value.split("#", 1)[0]


def emit(payload: dict[str, Any], json_output: bool) -> None:
    if json_output:
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
        return
    print(f"{payload['profile']}: {payload['status']}")
    for key in ("blocked", "unverified", "errors"):
        for item in payload.get(key, []):
            print(f"- {key}: {item}")


def base_payload(profile: str) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "profile": profile,
        "status": "violation",
        "blocked": [],
        "unverified": [],
        "errors": [],
    }


def profile_payload(profile: str) -> dict[str, Any]:
    payload = base_payload(profile)
    if profile == "generated-adapter-boundary":
        payload.update(
            {
                "aili_routes": [],
                "direct_adapter_cases": [],
                "claim_boundary": {},
                "cases": [],
            }
        )
    elif profile == "residual":
        payload.update({"matches": [], "classifications": []})
    return payload


def apply_contract_state(
    payload: dict[str, Any], state: Any, label: str, errors: list[str]
) -> None:
    if not isinstance(state, dict):
        errors.append(f"{label}.contract_state must be an object")
        return
    status = state.get("status")
    blocked = state.get("blocked")
    unverified = state.get("unverified")
    if status not in {"pass", "blocked", "Unverified"}:
        errors.append(f"{label}.contract_state.status must be pass, blocked, or Unverified")
        return
    if not isinstance(blocked, list) or any(not isinstance(item, str) or not item for item in blocked):
        errors.append(f"{label}.contract_state.blocked must be an array of non-empty strings")
        return
    if not isinstance(unverified, list) or any(
        not isinstance(item, str) or not item for item in unverified
    ):
        errors.append(f"{label}.contract_state.unverified must be an array of non-empty strings")
        return
    if status == "pass" and (blocked or unverified):
        errors.append(f"{label}.contract_state pass must have empty blocked/unverified")
        return
    if status == "blocked" and not blocked:
        errors.append(f"{label}.contract_state blocked requires blocked reasons")
        return
    if status == "Unverified" and not unverified:
        errors.append(f"{label}.contract_state Unverified requires unverified reasons")
        return
    payload["blocked"].extend(blocked)
    payload["unverified"].extend(unverified)


def validate_task_oracle(
    project: Path, fixture: dict[str, Any], errors: list[str]
) -> dict[str, Any]:
    declared = fixture.get("task_oracle")
    if declared != TASK_ORACLE_CONTRACT:
        errors.append("task_oracle must equal the change-specific ordered-ID and current-tasks-derived-state contract")
    tasks_path = project / "openspec/changes" / UMBRELLA_CHANGE / "tasks.md"
    try:
        task_text = tasks_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        errors.append(f"cannot read current umbrella task oracle: {exc}")
        return {
            "scope": UMBRELLA_CHANGE,
            "task_ids": [],
            "checked_task_ids": [],
            "checked": 0,
            "unchecked": 0,
        }
    matches = re.findall(r"^- \[([^\]]*)\] (\d+\.\d+)\s+", task_text, re.MULTILINE)
    invalid_marks = [
        {"task_id": task_id, "mark": mark}
        for mark, task_id in matches
        if mark not in {" ", "x", "X"}
    ]
    if invalid_marks:
        errors.append(f"current umbrella tasks contain invalid checklist marks: {invalid_marks}")
    observed_ids = [task_id for _, task_id in matches]
    observed_checked = [task_id for mark, task_id in matches if mark.lower() == "x"]
    observed_unchecked = [task_id for mark, task_id in matches if mark == " "]
    duplicate_ids = sorted(
        task_id for task_id, count in Counter(observed_ids).items() if count > 1
    )
    if duplicate_ids:
        errors.append(f"current umbrella tasks contain duplicate checklist IDs: {duplicate_ids}")
    if observed_ids != list(UMBRELLA_TASK_IDS):
        errors.append("current umbrella task IDs or ordering differ from the exact tracked 74-ID oracle")
    return {
        "scope": UMBRELLA_CHANGE,
        "task_ids": observed_ids,
        "checked_task_ids": observed_checked,
        "checked": len(observed_checked),
        "unchecked": len(observed_unchecked),
        "generic_lifecycle_derivation": TASK_ORACLE_CONTRACT["generic_lifecycle_derivation"],
        "task_state_source": TASK_ORACLE_CONTRACT["task_state_source"],
        "task_state_derivation": TASK_ORACLE_CONTRACT["task_state_derivation"],
        "current_acceptance": TASK_ORACLE_CONTRACT["current_acceptance"],
        "historical_or_stale": TASK_ORACLE_CONTRACT["historical_or_stale"],
    }


def inspect_agent_inventory(project: Path, errors: list[str]) -> dict[str, Any]:
    disk_paths = sorted(path.relative_to(project).as_posix() for path in (project / "agents").glob("*.md"))
    expected_paths = sorted(P6_REQUIRED_ROLE_PATHS)
    if disk_paths != expected_paths:
        errors.append(
            "canonical Agent inventory must be exactly ROSE plus 19 managed subagents; "
            f"missing={sorted(set(expected_paths) - set(disk_paths))}, "
            f"extra={sorted(set(disk_paths) - set(expected_paths))}"
        )

    observed_modes: dict[str, str | None] = {}
    observed_external: dict[str, str | None] = {}
    for relative in expected_paths:
        path = project / relative
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            errors.append(f"cannot inspect canonical Agent {relative}: {exc}")
            continue
        observed_modes[relative] = re.search(r"^mode:\s*(\S+)\s*$", text, re.MULTILINE).group(1) if re.search(r"^mode:\s*(\S+)\s*$", text, re.MULTILINE) else None
        external_match = re.search(r"^  external_directory:\s*(\S+)\s*$", text, re.MULTILINE)
        observed_external[relative] = external_match.group(1) if external_match else None

    if observed_modes.get("agents/rose.md") != "primary":
        errors.append("agents/rose.md must remain the one primary Agent")
    if observed_external.get("agents/rose.md") != "ask":
        errors.append("ROSE must remain distinct with per-operation external_directory ask")
    invalid_managed = sorted(
        relative
        for relative in MANAGED_AGENT_PATHS
        if observed_modes.get(relative) != "subagent" or observed_external.get(relative) != "deny"
    )
    if invalid_managed:
        errors.append(f"all 19 managed subagents must be subagent/external_directory deny: {invalid_managed}")

    manifest_path = project / "manifests/rose-aili.components.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        errors.append(f"cannot inspect Agent component manifest: {exc}")
        manifest_paths: list[str] = []
    else:
        rows = manifest.get("components", {}).get("agents", [])
        manifest_paths = sorted(
            row.get("path") for row in rows if isinstance(row, dict) and isinstance(row.get("path"), str)
        )
        if manifest_paths != expected_paths:
            errors.append("Agent component manifest differs from the exact ROSE-plus-19 source inventory")

    web_path = project / "agents/web-researcher.md"
    try:
        web_text = web_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        web_text = ""
    web_markers = {
        '  "*": deny',
        "  external_directory: deny",
        "  webfetch: ask",
        "  websearch: ask",
        "  task: deny",
    }
    if not web_markers.issubset(set(web_text.splitlines())):
        errors.append("web-researcher must preserve the inspected A31 web-only deny-by-default markers")
    if (project / "agents/debug-investigator.md").exists():
        errors.append("historical agents/debug-investigator.md must remain deleted")

    return {
        "primary": "agents/rose.md",
        "managed": sorted(MANAGED_AGENT_PATHS),
        "managed_count": len(MANAGED_AGENT_PATHS),
        "canonical_count": len(expected_paths),
        "all_managed_external_directory": "deny",
        "rose_external_directory": "ask-per-operation",
        "web_profile": "deny-by-default; webfetch/websearch ask; local/external/mutation/delegation deny",
        "builtins_excluded": ["explore", "general"],
        "historical_removed": ["agents/debug-investigator.md"],
        "manifest_paths": manifest_paths,
    }


def validate_a33_scaffold_and_rejections(
    project: Path, fixture: dict[str, Any], errors: list[str]
) -> tuple[dict[str, Any], dict[str, Any]]:
    scaffold_contract = fixture.get("a33_scaffold")
    rejection_contract = fixture.get("a33_rejections")
    if scaffold_contract != A33_SCAFFOLD_CONTRACT:
        errors.append("a33_scaffold differs from the exact current A33 definition-only contract")
    if rejection_contract != A33_REJECTION_CONTRACT:
        errors.append("a33_rejections differs from the exact Package-1 rejection/later-owner contract")

    for relative in sorted(A33_FORBIDDEN_NEW_PATHS):
        if (project / relative).exists():
            errors.append(f"forbidden A33 parallel machinery exists: {relative}")

    package_path = project / "package.json"
    manifest_path = project / "manifests/rose-aili.components.json"
    try:
        package = json.loads(package_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        errors.append(f"cannot inspect package boundary: {exc}")
        package_files: list[str] = []
        package_dependencies: list[str] = []
    else:
        package_files = package.get("files", []) if isinstance(package.get("files"), list) else []
        package_dependencies = sorted(package.get("dependencies", {})) if isinstance(package.get("dependencies"), dict) else []
        normalized_package_entries = {str(value).rstrip("/") for value in package_files}
        included_forbidden = sorted(A33_FORBIDDEN_PACKAGE_ROOTS & normalized_package_entries)
        if included_forbidden:
            errors.append(f"package includes forbidden worktree roots: {included_forbidden}")
        if set(package.get("bin", {})) != {"rose-aili"}:
            errors.append("package bin registry must not add an A33 public command")
        if package_dependencies != ["jsonc-parser"]:
            errors.append("Package-1 dependency inventory changed; A33 adds no dependency")

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        errors.append(f"cannot inspect public command manifest boundary: {exc}")
        command_names: list[str] = []
    else:
        command_rows = manifest.get("components", {}).get("commands", [])
        command_names = sorted(
            row.get("name") for row in command_rows if isinstance(row, dict) and isinstance(row.get("name"), str)
        )
        if set(command_names) != EXPECTED_PUBLIC_COMMANDS:
            errors.append("public command inventory differs from four delivery commands plus standalone local-review")

    observed_rejections = dict(rejection_contract) if isinstance(rejection_contract, dict) else {}
    observed_rejections["repository_inspection"] = {
        "forbidden_new_paths_present": sorted(
            relative for relative in A33_FORBIDDEN_NEW_PATHS if (project / relative).exists()
        ),
        "package_files": package_files,
        "production_dependencies": package_dependencies,
        "public_commands": command_names,
    }
    return (
        dict(scaffold_contract) if isinstance(scaffold_contract, dict) else {},
        observed_rejections,
    )


def parse_canonical_result_block(
    text: str,
) -> tuple[tuple[str, ...], tuple[str, ...]] | None:
    result_matches = list(
        re.finditer(r"```text\nCANONICAL RESULT:\n(?P<body>[\s\S]*?)\n```", text)
    )
    finding_matches = list(
        re.finditer(r"Each finding has exactly:\s*\n```text\n(?P<body>[\s\S]*?)\n```", text)
    )
    if len(result_matches) != 1 or len(finding_matches) != 1:
        return None
    result_fields = tuple(
        re.findall(r"^([a-z_]+):", result_matches[0].group("body"), re.MULTILINE)
    )
    finding_fields = tuple(
        re.findall(r"^([a-z_]+):", finding_matches[0].group("body"), re.MULTILINE)
    )
    if (
        len(result_fields) != len(set(result_fields))
        or result_fields != RESULT_FIELD_ORDER
        or len(finding_fields) != len(set(finding_fields))
        or finding_fields != FINDING_FIELD_ORDER
    ):
        return None
    return result_fields, finding_fields


def scan_rejected_machinery(
    project: Path,
    fixture: dict[str, Any],
    package_ownership: dict[str, dict[str, Any]],
    errors: list[str],
    blocked: list[str],
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "scope": "",
        "scanned_files": [],
        "legitimate_matches": [],
        "active_violations": [],
    }
    config = fixture.get("rejected_machinery_scan")
    if not isinstance(config, dict):
        blocked.append("rejected machinery proof is incomplete: scan contract is missing")
        return result
    result["scope"] = config.get("scope", "")
    rule_ids = config.get("rule_ids")
    legitimate_rows = config.get("legitimate_matches")
    if result["scope"] != "all existing P2-P11 package-owned authority files with exact legitimate-match allowlist":
        blocked.append("rejected machinery proof is incomplete: scan scope is not canonical")
    if not isinstance(rule_ids, list) or set(rule_ids) != set(REJECTED_SEMANTIC_RULES):
        blocked.append("rejected machinery proof is incomplete: semantic rule set differs")
    allowances: dict[tuple[str, str], dict[str, Any]] = {}
    if not isinstance(legitimate_rows, list) or not legitimate_rows:
        blocked.append("rejected machinery proof is incomplete: exact legitimate-match allowlist missing")
        legitimate_rows = []
    for index, row in enumerate(legitimate_rows):
        label = f"rejected_machinery_scan.legitimate_matches[{index}]"
        if not isinstance(row, dict):
            errors.append(f"{label} must be an object")
            continue
        path = row.get("path")
        row_rule_ids = row.get("rule_ids")
        classification = row.get("classification")
        reason = row.get("reason")
        expected_occurrences = row.get("expected_occurrences")
        expected_contexts = row.get("expected_contexts")
        path_error = validate_repo_path(path, f"{label}.path")
        if path_error:
            errors.append(path_error)
            continue
        resolved, resolution_error = resolve_repo_field_target(
            project, path, f"{label}.path", allow_missing=False
        )
        if resolution_error:
            errors.append(resolution_error)
            continue
        if (
            not isinstance(row_rule_ids, list)
            or not row_rule_ids
            or len(row_rule_ids) != len(set(row_rule_ids))
            or any(rule_id not in REJECTED_SEMANTIC_RULES for rule_id in row_rule_ids)
        ):
            errors.append(f"{label}.rule_ids must be a non-empty unique semantic-rule subset")
            continue
        if classification not in LEGITIMATE_MATCH_CLASSIFICATIONS:
            errors.append(f"{label}.classification is not allowed")
            continue
        if not isinstance(reason, str) or not reason.strip():
            errors.append(f"{label}.reason must be non-empty")
            continue
        if not isinstance(expected_occurrences, int) or expected_occurrences < 1:
            errors.append(f"{label}.expected_occurrences must be a positive integer")
            continue
        if (
            not isinstance(expected_contexts, list)
            or len(expected_contexts) != expected_occurrences
            or any(not isinstance(context, str) or not context for context in expected_contexts)
        ):
            errors.append(f"{label}.expected_contexts must list every exact allowed line occurrence")
            continue
        assert resolved is not None
        for rule_id in row_rule_ids:
            key = (path, rule_id)
            if key in allowances:
                errors.append(f"duplicate legitimate match allowance: {path} / {rule_id}")
            allowances[key] = {
                "classification": classification,
                "reason": reason,
                "expected_occurrences": expected_occurrences,
                "expected_contexts": Counter(expected_contexts),
            }
    if blocked or errors:
        return result

    active_paths: dict[str, Path] = {}
    for package_number in range(2, 12):
        package = f"P{package_number}"
        for path in package_ownership.get(package, {}).get("files", []):
            target, resolution_error = resolve_repo_field_target(
                project, path, f"{package}.files", allow_missing=True
            )
            if resolution_error:
                errors.append(resolution_error)
                continue
            if target is not None and target.exists() and path not in RESIDUAL_CONTROL_FILES:
                active_paths[path] = target

    allowance_hits: Counter[tuple[str, str]] = Counter()
    for relative, target in sorted(active_paths.items()):
        if not target.is_file():
            blocked.append(
                f"rejected machinery proof is incomplete: active owned path is not a file: {relative}"
            )
            continue
        try:
            lines = target.read_text(encoding="utf-8").splitlines()
        except (OSError, UnicodeError) as exc:
            blocked.append(
                f"rejected machinery proof is incomplete: cannot read {relative}: {exc}"
            )
            continue
        result["scanned_files"].append(relative)
        for line_number, line in enumerate(lines, start=1):
            for rule_id, pattern in REJECTED_SEMANTIC_RULES.items():
                for occurrence in pattern.finditer(line):
                    record = {
                        "rule_id": rule_id,
                        "path": relative,
                        "line": line_number,
                        "column": occurrence.start() + 1,
                    }
                    key = (relative, rule_id)
                    allowance = allowances.get(key)
                    context_hits = sum(
                        1
                        for item in result["legitimate_matches"]
                        if item["path"] == relative and item["rule_id"] == rule_id and item.get("context") == line
                    )
                    if allowance and context_hits < allowance["expected_contexts"].get(line, 0):
                        allowance_hits[key] += 1
                        result["legitimate_matches"].append(
                            {
                                **record,
                                "classification": allowance["classification"],
                                "reason": allowance["reason"],
                                "context": line,
                            }
                        )
                    else:
                        result["active_violations"].append(record)
                        errors.append(
                            f"active rejected machinery semantic: {rule_id} at {relative}:{line_number}:{occurrence.start() + 1}"
                        )
    unused_allowances = sorted(
        key
        for key, allowance in allowances.items()
        if allowance_hits[key] != allowance["expected_occurrences"]
    )
    if unused_allowances:
        errors.append(
            f"legitimate-match allowance occurrence counts differ from observations: {unused_allowances}"
        )
    return result


def validate_aggregate_traceability(
    project: Path,
    fixture: dict[str, Any],
    package_ownership: dict[str, dict[str, Any]],
    errors: list[str],
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "requirements": 0,
        "authoritative_sources": 0,
        "task_ids": [],
        "commands": {},
        "test_case_catalog_size": 0,
        "task_matrix": [],
    }
    section = fixture.get("aggregate_traceability")
    if not isinstance(section, dict):
        errors.append("aggregate_traceability must be an object")
        return result
    if section.get("schema_version") != SCHEMA_VERSION:
        errors.append("aggregate_traceability.schema_version must match checker version")
    if section.get("aggregate_owner") != "P11" or section.get("final_gate_owner") != "P12":
        errors.append("aggregate traceability owners must be P11 aggregate and P12 final gate")
    if section.get("commands") != TRACEABILITY_COMMANDS:
        errors.append("aggregate traceability commands must equal the exact command registry subset")
    result["commands"] = section.get("commands", {})

    tasks_path = project / "openspec/changes" / UMBRELLA_CHANGE / "tasks.md"
    canonical_task_text: dict[str, str] = {}
    task_id_values: list[str] = []
    try:
        task_text = tasks_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        errors.append(f"cannot read canonical tasks for aggregate traceability: {exc}")
        canonical_task_ids: set[str] = set()
    else:
        task_matches = re.findall(
            r"^- \[[ xX]\] (\d+\.\d+)\s+(.+)$", task_text, re.MULTILINE
        )
        task_id_values = [task_id for task_id, _ in task_matches]
        duplicate_task_ids = sorted(
            task_id for task_id, count in Counter(task_id_values).items() if count > 1
        )
        if duplicate_task_ids:
            errors.append(f"canonical tasks contain duplicate checklist ids: {duplicate_task_ids}")
        canonical_task_ids = set(task_id_values)
        canonical_task_text = dict(task_matches)
    if task_id_values != list(UMBRELLA_TASK_IDS):
        errors.append("canonical task inventory must equal this umbrella's exact ordered 74-ID oracle")
    result["task_ids"] = sorted(canonical_task_ids)
    test_case_catalog = collect_test_case_catalog(project, section, errors)
    result["test_case_catalog_size"] = len(test_case_catalog)
    task_evidence: dict[str, dict[str, set[str]]] = {
        task_id: {"files": set(), "tests": set(), "commands": set()}
        for task_id in canonical_task_ids
    }

    def validate_rows(field: str, expected_ids: set[str]) -> list[dict[str, Any]]:
        rows = section.get(field)
        if not isinstance(rows, list):
            errors.append(f"aggregate_traceability.{field} must be an array")
            return []
        ids = [row.get("id") for row in rows if isinstance(row, dict)]
        duplicates = sorted(item for item, count in Counter(ids).items() if count > 1)
        if duplicates:
            errors.append(f"aggregate_traceability.{field} duplicate ids: {duplicates}")
        if set(ids) != expected_ids:
            errors.append(
                f"aggregate_traceability.{field} ids differ; missing={sorted(expected_ids - set(ids))}, undefined={sorted(set(ids) - expected_ids)}"
            )
        for index, row in enumerate(rows):
            label = f"aggregate_traceability.{field}[{index}]"
            if not isinstance(row, dict):
                errors.append(f"{label} must be an object")
                continue
            task_ids = row.get("task_ids")
            surfaces = row.get("owned_surfaces")
            tests = row.get("tests")
            first_owner = row.get("first_owner")
            aggregate_owner = row.get("aggregate_owner")
            command_ids = row.get("command_ids")
            if (
                not isinstance(task_ids, list)
                or not task_ids
                or len(task_ids) != len(set(task_ids))
                or any(task_id not in canonical_task_ids for task_id in task_ids)
            ):
                errors.append(f"{label}.task_ids must be a non-empty unique canonical task subset")
            if not isinstance(surfaces, list) or not surfaces:
                errors.append(f"{label}.owned_surfaces must be non-empty")
            else:
                for surface in surfaces:
                    path_error = validate_repo_path(surface, f"{label}.owned_surfaces")
                    if path_error:
                        errors.append(path_error)
            if not isinstance(first_owner, str) or expand_owner_packages(first_owner) is None:
                errors.append(f"{label}.first_owner must be a valid package expression")
                owners: set[str] = set()
            else:
                owners = expand_owner_packages(first_owner) or set()
            if aggregate_owner != "P11":
                errors.append(f"{label}.aggregate_owner must be P11")
            if isinstance(surfaces, list) and owners:
                for surface in surfaces:
                    if not any(
                        source_path_owned_by(
                            surface,
                            set(package_ownership.get(owner, {}).get("files", [])),
                            project,
                        )
                        for owner in owners
                    ):
                        errors.append(f"{label}: ownership drift for {surface} / {first_owner}")
            if not isinstance(tests, dict) or set(tests) != {"positive", "negative", "recovery"}:
                errors.append(f"{label}.tests must define positive, negative, and recovery")
            elif any(not isinstance(tests[kind], list) or not tests[kind] for kind in tests):
                errors.append(f"{label}.tests entries must be non-empty arrays")
            if (
                not isinstance(command_ids, list)
                or not command_ids
                or len(command_ids) != len(set(command_ids))
                or any(command_id not in TRACEABILITY_COMMANDS for command_id in command_ids)
            ):
                errors.append(f"{label}.command_ids must be a non-empty exact-command subset")
            if isinstance(task_ids, list) and isinstance(surfaces, list) and isinstance(tests, dict) and isinstance(command_ids, list):
                referenced_tests = [
                    case_id
                    for kind in ("positive", "negative", "recovery")
                    for case_id in tests.get(kind, [])
                    if isinstance(case_id, str)
                ]
                for case_id in referenced_tests:
                    if case_id not in test_case_catalog:
                        errors.append(f"{label}: unknown test/case id {case_id!r}")
                    elif not (set(command_ids) & test_case_catalog[case_id]):
                        errors.append(
                            f"{label}: wrong command for test/case {case_id!r}; "
                            f"row={sorted(command_ids)}, catalog={sorted(test_case_catalog[case_id])}"
                        )
                for task_id in task_ids:
                    if task_id in task_evidence:
                        task_evidence[task_id]["files"].update(
                            surface for surface in surfaces if isinstance(surface, str)
                        )
                        task_evidence[task_id]["tests"].update(referenced_tests)
                        task_evidence[task_id]["commands"].update(
                            command_id for command_id in command_ids if isinstance(command_id, str)
                        )
        return [row for row in rows if isinstance(row, dict)]

    requirement_rows = validate_rows("requirements", NORMATIVE_REQUIREMENT_IDS)
    source_rows = validate_rows("authoritative_sources", AUTHORITATIVE_SOURCE_IDS)
    result["requirements"] = len(requirement_rows)
    result["authoritative_sources"] = len(source_rows)
    covered_task_ids = {
        task_id
        for task_id, evidence in task_evidence.items()
        if evidence["files"] and evidence["tests"] and evidence["commands"]
    }
    if covered_task_ids != canonical_task_ids:
        errors.append(
            "aggregate task coverage differs; "
            f"missing={sorted(canonical_task_ids - covered_task_ids)}, "
            f"undefined={sorted(covered_task_ids - canonical_task_ids)}"
        )

    catalog_rows = section.get("task_evidence_catalog")
    if not isinstance(catalog_rows, list):
        errors.append("aggregate task evidence catalog must be an array")
        catalog_rows = []
    catalog_ids = [
        row.get("task_id") for row in catalog_rows if isinstance(row, dict)
    ]
    catalog_duplicates = sorted(
        task_id for task_id, count in Counter(catalog_ids).items() if count > 1
    )
    if catalog_duplicates:
        errors.append(f"aggregate task evidence duplicate ids: {catalog_duplicates}")
    if set(catalog_ids) != canonical_task_ids:
        errors.append(
            "aggregate task evidence ids differ; "
            f"missing={sorted(canonical_task_ids - set(catalog_ids))}, "
            f"undefined={sorted(set(catalog_ids) - canonical_task_ids)}"
        )
    for index, row in enumerate(catalog_rows):
        if not isinstance(row, dict) or set(row) != {"task_id"}:
            errors.append(
                f"aggregate_traceability.task_evidence_catalog[{index}] must contain only task_id; "
                "files/tests/commands are repository-derived"
            )

    def task_sort_key(task_id: str) -> tuple[int, int]:
        major, minor = task_id.split(".", 1)
        return int(major), int(minor)

    result["task_matrix"] = [
        {
            "task_id": task_id,
            "accepted requirement/decision/risk": canonical_task_text.get(task_id, ""),
            "expected behavior": canonical_task_text.get(task_id, ""),
            "implementation files/artifacts": sorted(task_evidence[task_id]["files"]),
            "fresh tests/inspection/review evidence": {
                "test_case_ids": sorted(task_evidence[task_id]["tests"]),
                "command_ids": sorted(task_evidence[task_id]["commands"]),
                "claim": "catalog references only; Package 12 must replace with fresh results",
            },
            "status": "Partial",
            "findings": ["P11 generated traceability only; final task evidence has not been adjudicated"],
            "disposition": "ROSE-owned: unresolved",
            "freshness": "not final evidence",
        }
        for task_id in sorted(canonical_task_ids, key=task_sort_key)
    ]
    if section.get("loop_protocol_ids") != ["LP-INTERVAL-001", "LP-EVENT-001"]:
        errors.append("aggregate traceability must include the two canonical LP ids")
    required_fixture_ids = {
        "tokens-not-configured-null",
        "tokens-requested-accounting-unavailable-prestart",
        "tokens-midrun-accounting-loss",
        "lp-identity-natural-decomposed-normalizes-reuse",
        "lp-identity-reject-decomposed-nfc",
        "automation-modify-reject",
        "automation-mixed-documentation-block",
        "lp-allocation-race-recompute-once",
        "lp-allocation-second-race-block",
        "lp-duplicate-identity-key-hard-block",
        "task-audit-na-accepted-source-pass",
        "task-row-missing",
        "task-row-duplicate",
        "task-row-undefined",
        "pseudo-complete",
        "unchecked-task",
        "stale-evidence",
        "task-file-mismatch",
        "task-test-mismatch",
        "na-without-accepted-source",
        "subagent-nesting-forbidden",
        "optional-specialist-join",
        "no-majority-vote",
        "routing-bare-aili-direct-command-collision",
        "routing-bare-aili-direct-skill-collision",
        "routing-bare-continue-implementation-change",
        "routing-bare-implement-accepted-openspec-change",
        "routing-interval-executable-block",
        "budget-iteration-consumed-over-limit-corruption",
        "budget-review-consumed-over-limit-corruption",
        "review-ai-regression-vs-test-engineer-routing",
    }
    fixture_ids = section.get("required_fixture_ids")
    if not isinstance(fixture_ids, list) or set(fixture_ids) != required_fixture_ids:
        errors.append("aggregate traceability required_fixture_ids differs from DEF-E3/FIX4/FIX5 set")
    return result


def validate_final_task_audit(
    project: Path,
    change: str,
    audit_path: Path,
    partial_matrix: list[dict[str, Any]],
    errors: list[str],
) -> dict[str, Any]:
    summary = {"path": audit_path.relative_to(project).as_posix(), "owner": None, "rows": 0}
    try:
        audit = load_fixture(audit_path)
    except ValueError as exc:
        errors.append(f"cannot read separate ROSE-owned task-audit JSON: {exc}")
        return summary

    expected_top_fields = {
        "schema_version", "owner", "change", "unresolved", "runtime_enforcement", "rows"
    }
    if set(audit) != expected_top_fields:
        errors.append("final task-audit top level must contain only the canonical ROSE audit fields")
    if audit.get("schema_version") != SCHEMA_VERSION:
        errors.append("final task-audit schema_version must match checker version")
    if audit.get("owner") != "ROSE":
        errors.append("final task-audit must be ROSE-owned")
    if audit.get("change") != change:
        errors.append("final task-audit change differs from the requested change")
    summary["owner"] = audit.get("owner")
    if audit.get("unresolved") != []:
        errors.append("final task-audit has unresolved top-level findings or gaps")

    runtime = audit.get("runtime_enforcement")
    expected_runtime_fields = {"uv_id", "read_only_edit", "nested_task", "evidence"}
    if not isinstance(runtime, dict) or set(runtime) != expected_runtime_fields:
        errors.append("final task-audit must contain exact UV-001 read-only runtime enforcement evidence")
    elif (
        runtime.get("uv_id") != "UV-001"
        or runtime.get("read_only_edit") != "verified"
        or runtime.get("nested_task") != "verified"
        or not isinstance(runtime.get("evidence"), list)
        or not runtime["evidence"]
        or any(not isinstance(item, str) or not item.strip() for item in runtime["evidence"])
    ):
        errors.append("UV-001 read-only runtime enforcement remains unresolved")

    expected_by_id = {
        row.get("task_id"): row for row in partial_matrix if isinstance(row, dict)
    }
    rows = audit.get("rows")
    if not isinstance(rows, list):
        errors.append("final task-audit rows must be an array")
        return summary
    summary["rows"] = len(rows)
    ids = [row.get("task_id") for row in rows if isinstance(row, dict)]
    duplicate_ids = sorted(task_id for task_id, count in Counter(ids).items() if count > 1)
    if duplicate_ids:
        errors.append(f"final task-audit duplicate task ids: {duplicate_ids}")
    expected_ids = set(expected_by_id)
    if len(rows) != len(UMBRELLA_TASK_IDS) or set(ids) != expected_ids:
        errors.append(
            "this umbrella's final task-audit must contain its exact 74 canonical rows once; "
            f"rows={len(rows)}, missing={sorted(expected_ids - set(ids))}, "
            f"undefined={sorted(set(ids) - expected_ids)}"
        )

    accepted_source_root = f"openspec/changes/{change}/"
    accepted_source_names = {"proposal.md", "design.md", "interview.md", "tasks.md"}
    for index, row in enumerate(rows):
        label = f"final task-audit rows[{index}]"
        if not isinstance(row, dict):
            errors.append(f"{label} must be an object")
            continue
        if set(row) != TASK_AUDIT_FIELDS:
            errors.append(f"{label} must contain the exact nine task-audit fields")
            continue
        task_id = row.get("task_id")
        expected = expected_by_id.get(task_id)
        if expected is None:
            continue
        for field in ("accepted requirement/decision/risk", "expected behavior"):
            if row.get(field) != expected.get(field):
                errors.append(f"{label}.{field} differs from the canonical task")

        status = row.get("status")
        if status not in {"Done", "N/A"}:
            errors.append(f"{label}.status must be Done or resolved N/A for final closure")
        if row.get("freshness") != "final":
            errors.append(f"{label} lacks final freshness")
        if row.get("findings") != []:
            errors.append(f"{label} has unresolved findings")

        files = row.get("implementation files/artifacts")
        evidence = row.get("fresh tests/inspection/review evidence")
        if not isinstance(evidence, dict) or evidence.get("task_id") != task_id:
            errors.append(f"{label} lacks task-specific fresh evidence")
            continue
        if status == "Done":
            if row.get("disposition") != "ROSE-resolved: pass":
                errors.append(f"{label} Done row lacks a resolved disposition")
            if (
                not isinstance(files, list)
                or not files
                or any(not isinstance(item, str) or not item for item in files)
            ):
                errors.append(f"{label} Done row lacks task-specific implementation files")
            else:
                expected_files = set(expected.get("implementation files/artifacts", []))
                if not expected_files.intersection(files):
                    errors.append(f"{label} Done row files do not match task-specific aggregate evidence")
                for file_index, relative in enumerate(files):
                    path_error = validate_repo_path(relative, f"{label}.implementation files/artifacts[{file_index}]")
                    if path_error:
                        errors.append(path_error)
                        continue
                    _, resolution_error = resolve_repo_field_target(
                        project, relative, f"{label}.implementation files/artifacts[{file_index}]", allow_missing=False
                    )
                    if resolution_error:
                        errors.append(resolution_error)
            results = evidence.get("results")
            if not isinstance(results, list) or not results:
                errors.append(f"{label} Done row lacks fresh evidence results")
            else:
                for result_index, result in enumerate(results):
                    if (
                        not isinstance(result, dict)
                        or result.get("command_id") not in TRACEABILITY_COMMANDS
                        or result.get("status") != "pass"
                        or not isinstance(result.get("scope"), str)
                        or task_id not in result.get("scope", "")
                    ):
                        errors.append(f"{label} has invalid task-specific fresh evidence result {result_index}")
        elif status == "N/A":
            if row.get("disposition") != "ROSE-resolved: accepted N/A":
                errors.append(f"{label} N/A row lacks a resolved disposition")
            if files != []:
                errors.append(f"{label} N/A row implementation files must be empty")
            source = evidence.get("accepted_scope_source")
            rationale = evidence.get("rationale")
            confirmed_by = evidence.get("confirmed_by")
            if (
                not isinstance(source, str)
                or not source.startswith(accepted_source_root)
                or PurePosixPath(source).name not in accepted_source_names
                or not isinstance(rationale, str)
                or not rationale.strip()
                or not isinstance(confirmed_by, list)
                or any(not isinstance(item, str) for item in confirmed_by)
                or not {"convergence-reviewer", "ROSE"}.issubset(set(confirmed_by))
            ):
                errors.append(f"{label} N/A requires accepted scope source, rationale, and convergence-reviewer/ROSE confirmation")
            elif validate_repo_path(source, f"{label}.accepted_scope_source"):
                errors.append(validate_repo_path(source, f"{label}.accepted_scope_source") or "")
            else:
                _, resolution_error = resolve_repo_field_target(
                    project, source, f"{label}.accepted_scope_source", allow_missing=False
                )
                if resolution_error:
                    errors.append(resolution_error)
    return summary


def inspect_generated_adapter_repository(
    project: Path,
) -> tuple[dict[str, Any], list[str], list[str]]:
    inspection: dict[str, Any] = {
        "route_map": dict(GENERATED_ROUTE_MAP),
        "adapter_roots": list(GENERATED_ADAPTER_ROOTS),
        "adapter_cases": dict(GENERATED_ADAPTER_CASES),
        "inspected_files": [],
        "non_routing": False,
        "direct_output_no_evidence": False,
        "aili_gate_evidence": {},
    }
    errors: list[str] = []
    unverified: list[str] = []
    route_texts: list[str] = []
    for route, relative in GENERATED_ROUTE_MAP.items():
        target, resolution_error = resolve_repo_field_target(
            project, relative, f"generated route {route}", allow_missing=False
        )
        if resolution_error:
            errors.append(resolution_error)
            continue
        assert target is not None
        try:
            target_mode = target.lstat().st_mode
        except OSError as exc:
            errors.append(f"generated adapter is not a readable regular in-repository file: {relative}: {exc}")
            continue
        if target.is_symlink() or not stat.S_ISREG(target_mode):
            errors.append(f"generated adapter must be a regular in-repository file: {relative}")
            continue
        try:
            text = target.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            unverified.append(f"cannot inspect generated route source {relative}: {exc}")
            continue
        if not text.strip():
            errors.append(f"generated route source is empty: {relative}")
        required_gate_markers = {
            "aili-delivery-flow",
            "Required behavior:",
            "Hard stops:",
            "Output contract:",
        }
        observed_gate_markers = sorted(
            marker for marker in required_gate_markers if marker in text
        )
        inspection["aili_gate_evidence"][route] = {
            "source": relative,
            "required_markers": sorted(required_gate_markers),
            "observed_markers": observed_gate_markers,
            "gates_apply": len(observed_gate_markers) == len(required_gate_markers),
        }
        if len(observed_gate_markers) != len(required_gate_markers):
            errors.append(
                f"canonical AILI route lacks required gate evidence: {relative}: missing {sorted(required_gate_markers - set(observed_gate_markers))}"
            )
        route_texts.append(text)
        inspection["inspected_files"].append(relative)

    actual_cases: set[str] = set()
    for root_relative in GENERATED_ADAPTER_ROOTS:
        root_target, resolution_error = resolve_repo_field_target(
            project, root_relative, "generated adapter root", allow_missing=False
        )
        if resolution_error:
            errors.append(resolution_error)
            continue
        assert root_target is not None
        if not root_target.is_dir():
            errors.append(f"generated adapter root is not a directory: {root_relative}")
            continue
        if root_relative.endswith("commands"):
            candidates = sorted(root_target.glob("*.md"))
        else:
            candidates = sorted(root_target.glob("*/SKILL.md"))
        for candidate in candidates:
            try:
                resolved = candidate.resolve(strict=False)
            except (OSError, RuntimeError) as exc:
                unverified.append(f"cannot resolve generated adapter candidate {candidate}: {exc}")
                continue
            if resolved != project and project not in resolved.parents:
                errors.append(f"generated adapter candidate escapes project: {candidate}")
                continue
            actual_cases.add(resolved.relative_to(project).as_posix())
    expected_case_paths = set(GENERATED_ADAPTER_CASES.values())
    if actual_cases != expected_case_paths:
        errors.append(
            f"generated adapter repository set mismatch: expected {sorted(expected_case_paths)}, observed {sorted(actual_cases)}"
        )

    for case_id, relative in GENERATED_ADAPTER_CASES.items():
        lexical_target = project.joinpath(*PurePosixPath(relative).parts)
        try:
            lexical_mode = lexical_target.lstat().st_mode
        except OSError as exc:
            errors.append(f"generated adapter is not a readable regular in-repository file: {relative}: {exc}")
            continue
        if lexical_target.is_symlink() or not stat.S_ISREG(lexical_mode):
            errors.append(f"generated adapter must be a regular in-repository file: {relative}")
            continue
        target, resolution_error = resolve_repo_field_target(
            project, relative, f"generated adapter {case_id}", allow_missing=False
        )
        if resolution_error:
            errors.append(resolution_error)
            continue
        try:
            assert target is not None
            text = target.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            unverified.append(f"cannot inspect generated adapter {relative}: {exc}")
            continue
        if not text.strip():
            errors.append(f"generated adapter is empty: {relative}")
        if relative.startswith(".opencode/commands/"):
            if "openspec" not in text.lower() or "/opsx-" not in text:
                errors.append(f"generated command lacks current OpenSpec adapter markers: {relative}")
        elif "generatedBy:" not in text or "openspec" not in text.lower():
            errors.append(f"generated skill lacks current generated OpenSpec markers: {relative}")
        inspection["inspected_files"].append(relative)

    gitignore_target, gitignore_error = resolve_repo_field_target(
        project, ".gitignore", "generated adapter ignore source", allow_missing=False
    )
    if gitignore_error:
        errors.append(gitignore_error)
    else:
        try:
            assert gitignore_target is not None
            ignored = gitignore_target.read_text(encoding="utf-8").splitlines()
        except (OSError, UnicodeError) as exc:
            unverified.append(f"cannot inspect .gitignore generated boundary: {exc}")
        else:
            if ".opencode/" not in {line.strip() for line in ignored}:
                errors.append(".opencode generated adapter root is not ignored")
            inspection["inspected_files"].append(".gitignore")

    forbidden_route_pattern = re.compile(
        r"(?:/opsx-(?:apply|archive|explore|propose)|openspec-(?:apply-change|archive-change|explore|propose))"
    )
    if any(forbidden_route_pattern.search(text) for text in route_texts):
        errors.append("AILI route source routes to or recommends a direct generated adapter")
    else:
        inspection["non_routing"] = len(route_texts) == len(GENERATED_ROUTE_MAP)

    register_relative = "docs/harness/workflow-orchestration-source-register.md"
    register_target, register_error = resolve_repo_field_target(
        project, register_relative, "generated claim boundary source", allow_missing=False
    )
    if register_error:
        errors.append(register_error)
    else:
        try:
            assert register_target is not None
            register_text = register_target.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            unverified.append(f"cannot inspect direct-output evidence boundary: {exc}")
        else:
            boundary_pattern = re.compile(
                r"\bdoes not\b[^\n]{0,160}\btreat their direct output as AILI evidence\b",
                re.IGNORECASE,
            )
            if not boundary_pattern.search(register_text):
                errors.append("direct generated output no-evidence boundary is missing")
            else:
                inspection["direct_output_no_evidence"] = True
            inspection["inspected_files"].append(register_relative)
    inspection["inspected_files"] = sorted(set(inspection["inspected_files"]))
    return inspection, errors, unverified


def derive_residual_scan(
    project: Path, fixture: dict[str, Any], section: dict[str, Any]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[str], list[str]]:
    errors: list[str] = []
    unverified: list[str] = []
    allowances: dict[tuple[str, str, int, int, str], dict[str, str]] = {}
    allowance_hits: set[tuple[str, str, int, int, str]] = set()
    rows = section.get("legitimate_matches")
    if not isinstance(rows, list) or not rows:
        return [], [], ["residual.legitimate_matches must be a non-empty exact path/rule allowlist"], []
    for index, row in enumerate(rows):
        label = f"residual.legitimate_matches[{index}]"
        if not isinstance(row, dict):
            errors.append(f"{label} must be an object")
            continue
        path = row.get("path")
        rule_ids = row.get("rule_ids")
        classification = row.get("classification")
        reason = row.get("reason")
        occurrences = row.get("occurrences")
        path_error = validate_repo_path(path, f"{label}.path")
        if path_error:
            errors.append(path_error)
            continue
        target, resolution_error = resolve_repo_field_target(
            project, path, f"{label}.path", allow_missing=False
        )
        if resolution_error:
            errors.append(resolution_error)
            continue
        if not isinstance(rule_ids, list) or not rule_ids or len(rule_ids) != len(set(rule_ids)):
            errors.append(f"{label}.rule_ids must be a non-empty unique array")
            continue
        if any(rule_id not in REJECTED_SEMANTIC_RULES for rule_id in rule_ids):
            errors.append(f"{label}.rule_ids contains an undeclared semantic rule")
            continue
        if classification not in RESIDUAL_CLASSIFICATIONS - {"active violation"}:
            errors.append(f"{label}.classification must be a clean residual classification")
            continue
        if not isinstance(reason, str) or not reason.strip():
            errors.append(f"{label}.reason must be non-empty")
            continue
        if not isinstance(occurrences, list) or not occurrences:
            errors.append(f"{label}.occurrences must be a non-empty exact occurrence allowlist")
            continue
        assert target is not None
        for rule_id in rule_ids:
            rule_occurrences = [
                occurrence
                for occurrence in occurrences
                if isinstance(occurrence, dict) and occurrence.get("rule_id") == rule_id
            ]
            if not rule_occurrences:
                errors.append(f"{label}: no exact occurrence is declared for {rule_id}")
            for occurrence in rule_occurrences:
                line = occurrence.get("line")
                column = occurrence.get("column")
                evidence = occurrence.get("evidence")
                context = occurrence.get("context")
                if (
                    not isinstance(line, int) or line < 1
                    or not isinstance(column, int) or column < 1
                    or not isinstance(evidence, str) or not evidence
                    or not isinstance(context, str) or not context
                ):
                    errors.append(f"{label}: invalid exact residual occurrence")
                    continue
                key = (path, rule_id, line, column, evidence)
                if key in allowances:
                    errors.append(f"duplicate exact residual allowance: {key}")
                allowances[key] = {
                    "classification": classification,
                    "reason": reason,
                    "context": context,
                }

    files: dict[str, Path] = {}
    source_rows = fixture.get("sources")
    source_ids = {
        row.get("id") for row in source_rows if isinstance(row, dict)
    } if isinstance(source_rows, list) else set()
    if source_ids != CANONICAL_SOURCE_IDS:
        errors.append(
            "residual requires canonical residual source authority; "
            f"missing={sorted(CANONICAL_SOURCE_IDS - source_ids)}, "
            f"undefined={sorted(source_ids - CANONICAL_SOURCE_IDS)}"
        )
    roots, root_errors = derive_independent_residual_roots(project)
    errors.extend(root_errors)
    if not roots:
        errors.append("independent residual source inventory is empty")
        return [], [], errors, unverified
    if "scan_roots" in section and section.get("scan_roots") != roots:
        errors.append("residual.scan_roots, when present, must equal independent registry/manifest/source-tree/package allowlist")
    for index, relative in enumerate(roots):
        path_error = validate_repo_path(relative, f"residual.scan_roots[{index}]")
        if path_error:
            errors.append(path_error)
            continue
        target, resolution_error = resolve_repo_field_target(
            project, relative, f"residual.scan_roots[{index}]", allow_missing=False
        )
        if resolution_error:
            errors.append(resolution_error)
            continue
        assert target is not None
        candidates = [target] if target.is_file() else sorted(target.rglob("*"))
        for candidate in candidates:
            if not candidate.is_file():
                continue
            if candidate.suffix.lower() not in {
                "", ".json", ".jsonc", ".md", ".yaml", ".yml", ".toml",
                ".py", ".js", ".mjs", ".cjs", ".ts", ".tsx", ".sh",
            }:
                continue
            try:
                resolved = candidate.resolve(strict=True)
            except (OSError, RuntimeError) as exc:
                unverified.append(f"cannot resolve residual candidate {candidate}: {exc}")
                continue
            if resolved != project and project not in resolved.parents:
                errors.append(f"residual candidate resolves outside project: {candidate} -> {resolved}")
                continue
            relative_candidate = resolved.relative_to(project).as_posix()
            if relative_candidate in RESIDUAL_CONTROL_FILES:
                continue
            files[relative_candidate] = resolved

    matches: list[dict[str, Any]] = []
    classifications: list[dict[str, Any]] = []
    for relative, target in sorted(files.items()):
        try:
            text = target.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            unverified.append(f"cannot inspect residual source {relative}: {exc}")
            continue
        for line_number, line in enumerate(text.splitlines(), 1):
            for rule_id, pattern in sorted(REJECTED_SEMANTIC_RULES.items()):
                for occurrence in pattern.finditer(line):
                    column = occurrence.start() + 1
                    evidence = occurrence.group(0)
                    key = (relative, rule_id, line_number, column, evidence)
                    allowance = allowances.get(key)
                    if allowance and allowance["context"] == line:
                        classification = allowance["classification"]
                    else:
                        classification = "active violation"
                    if allowance and allowance["context"] == line:
                        allowance_hits.add(key)
                    observation_id = f"{rule_id}:{relative}:{line_number}:{column}"
                    matches.append(
                        {
                            "id": observation_id,
                            "path": relative,
                            "line": line_number,
                            "column": column,
                            "semantic_rule": rule_id,
                            "evidence": evidence,
                        }
                    )
                    classifications.append(
                        {
                            "id": observation_id,
                            "path": relative,
                            "semantic_rule": rule_id,
                            "classification": classification,
                            "evidence": allowance["reason"] if allowance and allowance["context"] == line else evidence,
                        }
                    )
    unused = sorted(set(allowances) - allowance_hits)
    if unused:
        errors.append(f"exact residual allowances have no derived occurrence: {unused}")
    return matches, classifications, errors, unverified


def run_internal_regression_probes(
    project: Path, fixture: dict[str, Any]
) -> tuple[list[dict[str, str]], list[str]]:
    results: list[dict[str, str]] = []
    failures: list[str] = []

    def record(probe_id: str, passed: bool, detail: str) -> None:
        results.append(
            {"id": probe_id, "status": "pass" if passed else "violation", "detail": detail}
        )
        if not passed:
            failures.append(f"internal regression probe failed: {probe_id}: {detail}")

    state_exits: list[int] = []
    for state in (
        {"status": "blocked", "blocked": ["probe"], "unverified": []},
        {"status": "Unverified", "blocked": [], "unverified": ["probe"]},
    ):
        state_payload = base_payload("scaffold")
        state_errors: list[str] = state_payload["errors"]
        apply_contract_state(state_payload, state, "probe", state_errors)
        state_exits.append(exit_code(state_payload))
    record(
        "contract-state-blocked-unverified",
        state_exits == [3, 3],
        f"observed exits {state_exits}",
    )

    empty_generated = {
        "schema_version": SCHEMA_VERSION,
        "fixture": "generated-openspec-adapter",
        "change": fixture.get("change"),
        "profiles": {
            "generated-adapter-boundary": {
                "ready": True,
                "contract_state": {"status": "pass", "blocked": [], "unverified": []},
            }
        },
        "generated_adapter_boundary": {"schema_version": SCHEMA_VERSION},
    }
    empty_residual = {
        "schema_version": SCHEMA_VERSION,
        "fixture": "workflow-orchestration",
        "change": fixture.get("change"),
        "profiles": {
            "residual": {
                "ready": True,
                "contract_state": {"status": "pass", "blocked": [], "unverified": []},
            }
        },
        "residual": {"schema_version": SCHEMA_VERSION},
    }
    empty_exits = [
        exit_code(generated_adapter_boundary(project, fixture.get("change"), empty_generated)),
        exit_code(residual(project, fixture.get("change"), empty_residual)),
    ]
    record("ready-profile-empty", empty_exits == [5, 5], f"observed exits {empty_exits}")

    path_matrix = {
        "absolute": "/tmp/x",
        "dot": "./x",
        "dotdot": "a/../x",
        "backslash": "a\\x",
        "non-normalized": "a//x",
        "placeholder": "a/<id>/x",
        "anchor": "a/x#section",
    }
    path_results = {
        name: validate_repo_path(value, f"probe.{name}") is not None
        for name, value in path_matrix.items()
    }
    record(
        "path-alias-matrix",
        all(path_results.values()),
        f"rejected aliases {sorted(name for name, rejected in path_results.items() if rejected)}",
    )

    package_rows = fixture.get("package_file_ownership", [])
    package_map = {
        row.get("package"): set(row.get("files", []))
        for row in package_rows
        if isinstance(row, dict) and isinstance(row.get("files"), list)
    }
    p6_complete = P6_REQUIRED_ROLE_PATHS.issubset(package_map.get("P6", set()))
    wave_disjoint = all(
        not (package_map.get(left, set()) & package_map.get(right, set()))
        for index, left in enumerate(WAVE_A_PACKAGES)
        for right in WAVE_A_PACKAGES[index + 1 :]
    )
    missing_role_detected = bool(P6_REQUIRED_ROLE_PATHS - (package_map.get("P6", set()) - {"agents/rose.md"}))
    overlap_detected = bool((package_map.get("P4", set()) | {"probe/shared"}) & (package_map.get("P6", set()) | {"probe/shared"}))
    record(
        "permission-role-ownership",
        p6_complete and wave_disjoint and missing_role_detected and overlap_detected,
        f"roles={len(P6_REQUIRED_ROLE_PATHS & package_map.get('P6', set()))}, wave_disjoint={wave_disjoint}",
    )

    source_by_id = {
        row.get("id"): row for row in fixture.get("sources", []) if isinstance(row, dict)
    }
    generated_agents = source_by_id.get("generated-project-agents", {})
    template_agents = source_by_id.get("agents-template-generator", {})
    split_valid = (
        generated_agents.get("classification") == "generated/installed adapter"
        and generated_agents.get("paths") == ["AGENTS.md"]
        and template_agents.get("classification") == "canonical source"
        and set(template_agents.get("paths", []))
        == {"templates/AGENTS.md", "scripts/agents_md.py"}
    )
    split_mutation_detected = generated_agents.get("paths") != [
        "AGENTS.md",
        "templates/AGENTS.md",
    ]
    record(
        "generated-agents-classification",
        split_valid and split_mutation_detected,
        "generated root and canonical template/generator are distinct",
    )

    result_path, result_path_error = resolve_repo_field_target(
        project,
        ".agents/skills/aili-delivery-flow/references/protocols/subagent-result.md",
        "result-schema probe",
        allow_missing=False,
    )
    if result_path_error:
        record("result-schema-parse", False, result_path_error)
    else:
        try:
            assert result_path is not None
            canonical_text = result_path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            record("result-schema-parse", False, f"cannot read canonical result protocol: {exc}")
            canonical_text = ""
        if canonical_text:
            duplicate = canonical_text.replace("result_id:\n", "result_id:\nresult_id:\n", 1)
            reordered = canonical_text.replace(
                "result_id:\ntrace_id:\n", "trace_id:\nresult_id:\n", 1
            )
            finding_duplicate = canonical_text.replace(
                "finding_id:\n", "finding_id:\nfinding_id:\n", 1
            )
            finding_reordered = canonical_text.replace(
                "finding_id:\nsource:\n", "source:\nfinding_id:\n", 1
            )
            ambiguous = canonical_text + "\n" + canonical_text[canonical_text.index("```text\nCANONICAL RESULT:"):canonical_text.index("```", canonical_text.index("```text\nCANONICAL RESULT:") + 3) + 3]
            parser_valid = parse_canonical_result_block(canonical_text) == (
                RESULT_FIELD_ORDER,
                FINDING_FIELD_ORDER,
            )
            parser_rejects = all(
                parse_canonical_result_block(value) is None
                for value in (
                    duplicate,
                    reordered,
                    finding_duplicate,
                    finding_reordered,
                    ambiguous,
                )
            )
            record(
                "result-schema-parse",
                parser_valid and parser_rejects,
                "ordered schema accepted; duplicate, reordered, and ambiguous forms rejected",
            )

    with tempfile.TemporaryDirectory(prefix="workflow-contract-probe-") as temp_name:
        temp_root = Path(temp_name).resolve()
        (temp_root / "active.md").write_text("baseline-manifest.json\n", encoding="utf-8")
        (temp_root / "negative.md").write_text("baseline-manifest.json is rejected\n", encoding="utf-8")
        scan_fixture = {
            "rejected_machinery_scan": {
                "scope": "all existing P2-P11 package-owned authority files with exact legitimate-match allowlist",
                "rule_ids": list(REJECTED_SEMANTIC_RULES),
                "legitimate_matches": [
                    {
                        "path": "negative.md",
                        "rule_ids": ["baseline-manifest"],
                        "classification": "negative test fixture",
                        "reason": "probe",
                        "expected_occurrences": 1,
                        "expected_contexts": ["baseline-manifest.json is rejected"],
                    }
                ],
            }
        }
        scan_errors: list[str] = []
        scan_blocked: list[str] = []
        scan_result = scan_rejected_machinery(
            temp_root,
            scan_fixture,
            {"P2": {"files": ["active.md", "negative.md"]}},
            scan_errors,
            scan_blocked,
        )
        incomplete_errors: list[str] = []
        incomplete_blocked: list[str] = []
        scan_rejected_machinery(
            temp_root,
            {},
            {"P2": {"files": ["active.md"]}},
            incomplete_errors,
            incomplete_blocked,
        )
        semantic_valid = (
            bool(scan_result["active_violations"])
            and bool(scan_result["legitimate_matches"])
            and exit_code({"errors": scan_errors, "blocked": scan_blocked, "unverified": []}) == 5
            and exit_code(
                {"errors": incomplete_errors, "blocked": incomplete_blocked, "unverified": []}
            )
            == 3
        )
        record(
            "active-negative-incomplete-scan",
            semantic_valid,
            "active violation exits 5; exact negative allowance is classified; incomplete scan exits 3",
        )
    return results, failures


def scaffold(project: Path, change: str, fixture: dict[str, Any]) -> dict[str, Any]:
    payload = base_payload("scaffold")
    errors: list[str] = payload["errors"]

    if fixture.get("schema_version") != SCHEMA_VERSION:
        errors.append(
            f"schema_version must be {SCHEMA_VERSION!r}, got {fixture.get('schema_version')!r}"
        )
    if fixture.get("fixture") != "workflow-orchestration":
        errors.append("fixture must be 'workflow-orchestration'")
    if fixture.get("change") != change:
        errors.append(f"fixture change must equal requested change {change!r}")
    if change != UMBRELLA_CHANGE:
        errors.append(f"scaffold profile is change-specific and requires {UMBRELLA_CHANGE!r}")

    profiles = fixture.get("profiles")
    if profiles != WORKFLOW_PROFILE_CONTRACT:
        errors.append("profiles must equal the three existing owner/readiness/JSON-field contracts")
    else:
        scaffold_profile = profiles.get("scaffold")
        apply_contract_state(
            payload, scaffold_profile.get("contract_state"), "profiles.scaffold", errors
        )

    sources = fixture.get("sources")
    source_rows = sources if isinstance(sources, list) else []
    if not isinstance(sources, list) or not sources:
        errors.append("sources must be a non-empty array")

    ids: list[str] = []
    categories: list[str] = []
    classifications: list[str] = []
    ownership: dict[str, dict[str, Any]] = {}
    checked_paths = 0
    optional_missing: list[str] = []

    for index, row in enumerate(source_rows):
        label = f"sources[{index}]"
        if not isinstance(row, dict):
            errors.append(f"{label} must be an object")
            continue
        source_id = row.get("id")
        category = row.get("category")
        classification = row.get("classification")
        owner = row.get("owner_package")
        paths = row.get("paths")
        if not isinstance(source_id, str) or not source_id:
            errors.append(f"{label}.id must be a non-empty string")
            continue
        ids.append(source_id)
        if category not in REQUIRED_CATEGORIES:
            errors.append(f"{source_id}: unsupported category {category!r}")
        else:
            categories.append(category)
        if classification not in SOURCE_CLASSES:
            errors.append(f"{source_id}: unsupported classification {classification!r}")
        else:
            classifications.append(classification)
        if not isinstance(owner, str) or not owner:
            errors.append(f"{source_id}: owner_package must be explicit")
        if not isinstance(paths, list) or any(not isinstance(item, str) for item in paths):
            errors.append(f"{source_id}: paths must be an array of strings")
            continue
        if len(paths) != len(set(paths)):
            errors.append(f"{source_id}: paths must not contain duplicates")
        if not paths and classification != "out of scope":
            errors.append(f"{source_id}: only out-of-scope entries may have no paths")
        ownership[source_id] = {"owner_package": owner, "paths": paths}
        for relative in paths:
            path_error = validate_repo_path(relative, f"{source_id}.paths")
            if path_error:
                errors.append(path_error)
                continue
            target, resolution_error = resolve_repo_field_target(
                project,
                relative,
                f"{source_id}.paths",
                allow_missing=classification == "generated/installed adapter",
            )
            if resolution_error:
                errors.append(resolution_error)
                continue
            checked_paths += 1
            if target is not None and target.exists():
                continue
            if classification == "generated/installed adapter":
                optional_missing.append(relative)
            else:
                errors.append(f"{source_id}: inventoried path does not exist: {relative}")

    duplicates = sorted(item for item, count in Counter(ids).items() if count > 1)
    if duplicates:
        errors.append(f"duplicate source ids: {duplicates}")
    missing_categories = sorted(REQUIRED_CATEGORIES - set(categories))
    if missing_categories:
        errors.append(f"missing source categories: {missing_categories}")
    missing_classes = sorted(SOURCE_CLASSES - set(classifications))
    if missing_classes:
        errors.append(f"missing source classifications: {missing_classes}")

    canonical_paths = fixture.get("canonical_paths")
    canonical = canonical_paths if isinstance(canonical_paths, dict) else {}
    if canonical != CANONICAL_PATH_CONTRACT:
        errors.append("canonical_paths must exactly equal the accepted path/owner/state contract")
    for name, decision in canonical.items():
        if not isinstance(decision, dict):
            errors.append(f"canonical_paths.{name} must be an object")
            continue
        path = decision.get("path")
        owner = decision.get("owner")
        state = decision.get("state")
        if not isinstance(path, str) or not path or not isinstance(owner, str) or not owner:
            errors.append(f"canonical_paths.{name} requires path and owner")
            continue
        path_error = validate_repo_path(
            path,
            f"canonical_paths.{name}.path",
            allow_change_placeholder=name == "review_arbitration",
            expected_anchor="shared-loop-envelope" if name == "loop_envelope" else None,
        )
        if path_error:
            errors.append(path_error)
            continue
        if state not in {"present", "planned"}:
            errors.append(f"canonical_paths.{name}.state must be present or planned")
            continue
        if state == "present":
            target, resolution_error = resolve_repo_field_target(
                project, path, f"canonical_paths.{name}", allow_missing=False
            )
            if resolution_error:
                errors.append(resolution_error)

    package_rows = fixture.get("package_file_ownership")
    package_ownership: dict[str, dict[str, Any]] = {}
    if not isinstance(package_rows, list):
        errors.append("package_file_ownership must be an array")
    else:
        for index, row in enumerate(package_rows):
            label = f"package_file_ownership[{index}]"
            if not isinstance(row, dict):
                errors.append(f"{label} must be an object")
                continue
            package = row.get("package")
            mode = row.get("mode")
            files = row.get("files")
            if package not in PACKAGE_IDS:
                errors.append(f"{label}.package must be P1 through P12")
                continue
            if package in package_ownership:
                errors.append(f"duplicate package ownership entry: {package}")
                continue
            if mode not in {"edit", "verification-only"}:
                errors.append(f"{package}: mode must be edit or verification-only")
            if not isinstance(files, list) or any(not isinstance(item, str) for item in files):
                errors.append(f"{package}: files must be an array of exact paths")
                files = []
            if len(files) != len(set(files)):
                errors.append(f"{package}: files must not contain duplicates")
            for relative in files:
                path_error = validate_repo_path(relative, f"{package}.files")
                if path_error:
                    errors.append(path_error)
                if relative == FORBIDDEN_GRAPHIFY_PATH or relative.startswith(
                    f"{FORBIDDEN_GRAPHIFY_PATH}/"
                ):
                    errors.append(f"{package}: old Graphify change cannot be an owned edit path")
                if not path_error:
                    _, resolution_error = resolve_repo_field_target(
                        project, relative, f"{package}.files", allow_missing=True
                    )
                    if resolution_error:
                        errors.append(resolution_error)
            if mode == "verification-only" and files:
                errors.append(f"{package}: verification-only ownership must not list edit files")
            if mode == "edit" and not files:
                errors.append(f"{package}: edit ownership must list files")
            package_ownership[package] = {"mode": mode, "files": files}
        missing_packages = sorted(PACKAGE_IDS - set(package_ownership))
        if missing_packages:
            errors.append(f"missing package ownership entries: {missing_packages}")
        if set(package_ownership.get("P1", {}).get("files", [])) != PACKAGE_1_FILES:
            errors.append("P1 ownership must match the accepted Package-1 edit surface exactly")
        if package_ownership.get("P12", {}).get("mode") != "verification-only":
            errors.append("P12 must remain verification-only")
        for package_number in range(2, 12):
            package = f"P{package_number}"
            entry = package_ownership.get(package, {})
            if entry.get("mode") != "edit" or not entry.get("files"):
                errors.append(f"{package} must have a non-empty exact edit ownership row")
        p6_paths = set(package_ownership.get("P6", {}).get("files", []))
        missing_p6_paths = sorted(P6_REQUIRED_CROSS_ROOT_PATHS - p6_paths)
        if missing_p6_paths:
            errors.append(f"P6 is missing canonical cross-root inventory: {missing_p6_paths}")
        for index, left in enumerate(WAVE_A_PACKAGES):
            for right in WAVE_A_PACKAGES[index + 1 :]:
                overlap = sorted(
                    set(package_ownership.get(left, {}).get("files", []))
                    & set(package_ownership.get(right, {}).get("files", []))
                )
                if overlap:
                    errors.append(f"Wave A ownership overlap {left}/{right}: {overlap}")

    derived_overlaps: dict[str, list[str]] = {}
    for package in ACCEPTED_SERIALIZATION_ORDER:
        for path in package_ownership.get(package, {}).get("files", []):
            derived_overlaps.setdefault(path, []).append(package)
    derived_overlaps = {
        path: packages for path, packages in derived_overlaps.items() if len(packages) > 1
    }
    declared_overlaps: dict[str, list[str]] = {}
    overlap_rows = fixture.get("serial_overlaps")
    if not isinstance(overlap_rows, list):
        errors.append("serial_overlaps must be an array")
    else:
        for index, row in enumerate(overlap_rows):
            label = f"serial_overlaps[{index}]"
            if not isinstance(row, dict):
                errors.append(f"{label} must be an object")
                continue
            path = row.get("path")
            packages = row.get("packages")
            reason = row.get("reason")
            path_error = validate_repo_path(path, f"{label}.path")
            if path_error:
                errors.append(path_error)
                continue
            if path in declared_overlaps:
                errors.append(f"duplicate serial overlap declaration: {path}")
                continue
            if (
                not isinstance(packages, list)
                or len(packages) < 2
                or any(not isinstance(package, str) for package in packages)
                or any(package not in PACKAGE_IDS for package in packages)
                or len(packages) != len(set(packages))
            ):
                errors.append(f"{label}.packages must be unique P1-P12 ids")
                continue
            if not isinstance(reason, str) or not reason.strip():
                errors.append(f"{label}.reason must be non-empty")
            declared_overlaps[path] = packages
    if declared_overlaps != derived_overlaps:
        errors.append("serial_overlaps must exactly match every P2-P11 shared edit path")

    active_authority_paths = {
        path
        for package_number in range(2, 12)
        for path in package_ownership.get(f"P{package_number}", {}).get("files", [])
        if path not in RESIDUAL_CONTROL_FILES
    }
    for relative in sorted(active_authority_paths):
        target, resolution_error = resolve_repo_field_target(
            project, relative, "active BUILD authority scan", allow_missing=True
        )
        if resolution_error or target is None or not target.is_file():
            continue
        try:
            text = target.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            continue
        if Path(RETIRED_BUILD_AUTHORITY).name in text:
            errors.append(f"retired BUILD authority path appears in active authority: {relative}")

    source_owner_crosscheck: list[dict[str, Any]] = []
    owned_by_package = {
        package: set(entry.get("files", [])) for package, entry in package_ownership.items()
    }
    for row in source_rows:
        if not isinstance(row, dict) or not isinstance(row.get("id"), str):
            continue
        source_id = row["id"]
        owner_value = row.get("owner_package")
        owners = expand_owner_packages(owner_value) if isinstance(owner_value, str) else None
        if owners is None:
            errors.append(f"{source_id}: owner_package expression is invalid")
            continue
        paths = row.get("paths", []) if isinstance(row.get("paths"), list) else []
        if not owners:
            classification = row.get("classification")
            state = row.get("state")
            non_edit_reason = row.get("non_edit_reason")
            non_edit_classification = classification in {
                "generated/installed adapter",
                "historical evidence",
                "out of scope",
            }
            accepted_non_edit_contract = classification == "canonical source" and state == "accepted contract"
            inspection_only = all(
                row.get(key) == value
                for key, value in INSPECTION_ONLY_SOURCE_CONTRACT.items()
            )
            if not (non_edit_classification or accepted_non_edit_contract or inspection_only):
                errors.append(
                    f"{source_id}: canonical active source requires edit ownership or justified inspection-only state"
                )
            source_owner_crosscheck.append(
                {
                    "source_id": source_id,
                    "owners": [],
                    "status": "inspection-only" if inspection_only else "non-edit authority",
                }
            )
            continue
        uncovered_paths = [
            path
            for path in paths
            if not any(
                source_path_owned_by(path, owned_by_package.get(package, set()), project)
                for package in owners
            )
        ]
        owner_without_surface = [
            package
            for package in sorted(owners)
            if not any(
                source_path_owned_by(path, owned_by_package.get(package, set()), project)
                for path in paths
            )
        ]
        if uncovered_paths:
            errors.append(f"{source_id}: source paths lack declared package ownership: {uncovered_paths}")
        if owner_without_surface:
            errors.append(
                f"{source_id}: declared owners have no source surface: {owner_without_surface}"
            )
        source_owner_crosscheck.append(
            {
                "source_id": source_id,
                "owners": sorted(owners),
                "status": "covered" if not uncovered_paths and not owner_without_surface else "violation",
            }
        )

    source_register = fixture.get("source_register")
    if not isinstance(source_register, str):
        errors.append("source_register must be a repository-relative path")
        register_text = ""
    else:
        path_error = validate_repo_path(source_register, "source_register")
        if path_error:
            errors.append(path_error)
        register_path, resolution_error = resolve_repo_field_target(
            project, source_register, "source_register", allow_missing=False
        )
        try:
            register_text = (
                register_path.read_text(encoding="utf-8")
                if register_path is not None and resolution_error is None
                else ""
            )
        except (OSError, UnicodeError) as exc:
            errors.append(f"cannot read source register: {exc}")
            register_text = ""
        if resolution_error:
            errors.append(resolution_error)
    for marker in (
        "aili.workflow-orchestration-sources.v1",
        "canonical source",
        "generated/installed adapter",
        "upstream reference",
        "historical evidence",
        "out of scope",
        FORBIDDEN_GRAPHIFY_PATH,
        "no Git-status/diff unchanged proof",
    ):
        if marker not in register_text:
            errors.append(f"source register missing marker: {marker}")

    protocol_markers = fixture.get("protocol_markers")
    if not isinstance(protocol_markers, dict) or not protocol_markers:
        errors.append("protocol_markers must be a non-empty object")
    else:
        for relative, markers in protocol_markers.items():
            if not isinstance(relative, str) or not isinstance(markers, list):
                errors.append("protocol_markers entries require a path and marker array")
                continue
            path_error = validate_repo_path(relative, "protocol_markers path")
            if path_error:
                errors.append(path_error)
                continue
            protocol_path, resolution_error = resolve_repo_field_target(
                project, relative, "protocol marker path", allow_missing=False
            )
            try:
                text = (
                    protocol_path.read_text(encoding="utf-8")
                    if protocol_path is not None and resolution_error is None
                    else ""
                )
            except (OSError, UnicodeError) as exc:
                errors.append(f"cannot read protocol marker path {relative}: {exc}")
                continue
            if resolution_error:
                errors.append(resolution_error)
                continue
            for marker in markers:
                if not isinstance(marker, str) or marker not in text:
                    errors.append(f"{relative}: missing protocol marker {marker!r}")

    protocol_contracts = fixture.get("protocol_contracts")
    result_contract = protocol_contracts.get("result") if isinstance(protocol_contracts, dict) else None
    if not isinstance(result_contract, dict):
        errors.append("protocol_contracts.result must be an object")
    else:
        result_path = result_contract.get("path")
        path_error = validate_repo_path(result_path, "protocol_contracts.result.path")
        if path_error:
            errors.append(path_error)
        result_values = result_contract.get("result_fields")
        finding_values = result_contract.get("finding_fields")
        declared_result_fields = (
            tuple(result_values)
            if isinstance(result_values, list) and all(isinstance(item, str) for item in result_values)
            else ()
        )
        declared_finding_fields = (
            tuple(finding_values)
            if isinstance(finding_values, list) and all(isinstance(item, str) for item in finding_values)
            else ()
        )
        if declared_result_fields != RESULT_FIELD_ORDER:
            errors.append("protocol_contracts.result.result_fields differs from canonical schema")
        if declared_finding_fields != FINDING_FIELD_ORDER:
            errors.append("protocol_contracts.result.finding_fields differs from canonical schema")
        if not path_error:
            result_target, resolution_error = resolve_repo_field_target(
                project, result_path, "result protocol", allow_missing=False
            )
            try:
                result_text = (
                    result_target.read_text(encoding="utf-8")
                    if result_target is not None and resolution_error is None
                    else ""
                )
            except (OSError, UnicodeError) as exc:
                errors.append(f"cannot read result protocol: {exc}")
            else:
                if resolution_error:
                    errors.append(resolution_error)
                parsed = parse_canonical_result_block(result_text)
                if parsed is None:
                    errors.append("result protocol lacks parseable canonical result/finding blocks")
                else:
                    actual_result, actual_finding = parsed
                    if actual_result != RESULT_FIELD_ORDER:
                        errors.append("CANONICAL RESULT top-level fields differ from schema")
                    if actual_finding != FINDING_FIELD_ORDER:
                        errors.append("CANONICAL RESULT finding fields differ from schema")

    forbidden = fixture.get("forbidden_scopes")
    old_graphify = []
    if isinstance(forbidden, list):
        old_graphify = [
            item
            for item in forbidden
            if isinstance(item, dict) and item.get("path") == FORBIDDEN_GRAPHIFY_PATH
        ]
    if len(old_graphify) != 1:
        errors.append("old Graphify change must have exactly one forbidden-scope entry")
    else:
        actions = old_graphify[0].get("actions")
        if actions != ["edit", "archive", "apply"]:
            errors.append("old Graphify forbidden actions must be edit/archive/apply")
        if old_graphify[0].get("byte_claim") != "no Git-status/diff unchanged proof":
            errors.append("old Graphify entry must reject Git-status/diff byte proof")

    rejected = fixture.get("rejected_concepts")
    rejected_set = (
        set(rejected)
        if isinstance(rejected, list) and all(isinstance(item, str) for item in rejected)
        else set()
    )
    if rejected_set != REQUIRED_REJECTED_CONCEPTS:
        errors.append(
            "rejected_concepts must match the Package-1 rejected machinery set exactly"
        )

    generated = fixture.get("generated")
    generated_data = generated if isinstance(generated, dict) else {}
    ignored_roots = generated_data.get("ignored_roots", [])
    gitignore_target, gitignore_resolution_error = resolve_repo_field_target(
        project, ".gitignore", "generated ignore boundary", allow_missing=False
    )
    if gitignore_resolution_error:
        errors.append(gitignore_resolution_error)
        gitignore = []
    else:
        try:
            assert gitignore_target is not None
            gitignore = gitignore_target.read_text(encoding="utf-8").splitlines()
        except (OSError, UnicodeError) as exc:
            errors.append(f"cannot read .gitignore: {exc}")
            gitignore = []
    ignored_normalized = {line.strip().rstrip("/") for line in gitignore if line.strip()}
    if not isinstance(ignored_roots, list):
        errors.append("generated.ignored_roots must be an array")
    else:
        for root in ignored_roots:
            if not isinstance(root, str) or root.rstrip("/") not in ignored_normalized:
                errors.append(f"generated root is not explicitly ignored: {root!r}")
    boundaries = generated_data.get("boundaries", [])
    if not isinstance(boundaries, list):
        errors.append("generated.boundaries must be an array")
        boundaries = []
    for marker in (
        "do not hand-edit generated adapters",
        "do not route or recommend direct adapters",
        "do not treat direct adapter output as AILI evidence",
        "return to canonical source or generator",
    ):
        if marker not in boundaries:
            errors.append(f"generated boundary missing: {marker}")

    source_by_id = {
        row.get("id"): row for row in source_rows if isinstance(row, dict) and isinstance(row.get("id"), str)
    }
    generated_agents = source_by_id.get("generated-project-agents")
    template_generator = source_by_id.get("agents-template-generator")
    if not isinstance(generated_agents, dict) or (
        generated_agents.get("classification") != "generated/installed adapter"
        or generated_agents.get("paths") != ["AGENTS.md"]
    ):
        errors.append("generated-project-agents must classify only root AGENTS.md as generated")
    if not isinstance(template_generator, dict) or (
        template_generator.get("classification") != "canonical source"
        or set(template_generator.get("paths", [])) != {"templates/AGENTS.md", "scripts/agents_md.py"}
    ):
        errors.append("templates/AGENTS.md and scripts/agents_md.py must be canonical source/generator")

    cross_root_inventory = {
        path
        for row in source_rows
        if isinstance(row, dict) and row.get("category") == "cross-root"
        for path in row.get("paths", [])
        if isinstance(path, str)
    }
    if cross_root_inventory != P6_REQUIRED_CROSS_ROOT_PATHS:
        errors.append("cross-root-protocols source inventory must equal the canonical P6 inventory")

    rejected_scan = scan_rejected_machinery(
        project, fixture, package_ownership, errors, payload["blocked"]
    )
    task_oracle = validate_task_oracle(project, fixture, errors)
    agent_inventory = inspect_agent_inventory(project, errors)
    a33_scaffold, a33_rejections = validate_a33_scaffold_and_rejections(
        project, fixture, errors
    )
    aggregate_traceability = validate_aggregate_traceability(
        project, fixture, package_ownership, errors
    )

    cases = fixture.get("cases")
    case_rows = cases if isinstance(cases, list) else []
    case_ids = {
        item.get("id")
        for item in case_rows
        if isinstance(item, dict) and item.get("expected") == "pass"
    }
    if case_ids != REQUIRED_CASES:
        errors.append("scaffold cases must match the required Package-1 case set exactly")
    case_by_id = {
        item.get("id"): item for item in case_rows if isinstance(item, dict)
    }
    for case_id, expected_fields in REPAIR_CASE_EXPECTATIONS.items():
        case = case_by_id.get(case_id)
        if not isinstance(case, dict):
            continue
        actual_fields = {key: value for key, value in case.items() if key not in {"id", "expected"}}
        if actual_fields != expected_fields:
            errors.append(f"{case_id}: regression probe contract differs from expected semantics")

    regression_probes, probe_failures = run_internal_regression_probes(project, fixture)
    errors.extend(probe_failures)

    payload["sources"] = {
        "count": len(source_rows),
        "checked_paths": checked_paths,
        "categories": sorted(set(categories)),
        "classifications": sorted(set(classifications)),
        "ids": sorted(ids),
        "optional_generated_paths_not_present": sorted(optional_missing),
        "rejected_machinery_scan": rejected_scan,
    }
    payload["ownership"] = {
        "canonical_paths": canonical,
        "package_file_ownership": package_ownership,
        "source_owners": ownership,
        "source_owner_crosscheck": source_owner_crosscheck,
    }
    payload["generated"] = generated_data
    payload["traceability"] = aggregate_traceability
    payload["task_oracle"] = task_oracle
    payload["agent_inventory"] = agent_inventory
    payload["a33_scaffold"] = a33_scaffold
    payload["a33_rejections"] = a33_rejections
    payload["regression_probes"] = regression_probes
    if errors:
        payload["status"] = "violation"
    elif payload["blocked"]:
        payload["status"] = "blocked"
    elif payload["unverified"]:
        payload["status"] = "Unverified"
    else:
        payload["status"] = "pass"
    return payload


def generated_adapter_boundary(
    project: Path, change: str, fixture: dict[str, Any]
) -> dict[str, Any]:
    payload = profile_payload("generated-adapter-boundary")
    errors: list[str] = payload["errors"]
    if fixture.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must be {SCHEMA_VERSION!r}")
    if fixture.get("change") != change:
        errors.append(f"fixture change must equal requested change {change!r}")
    profiles = fixture.get("profiles")
    profile = profiles.get("generated-adapter-boundary") if isinstance(profiles, dict) else None
    section = fixture.get("generated_adapter_boundary")
    if not isinstance(profile, dict) or not isinstance(profile.get("ready"), bool):
        errors.append("generated-adapter-boundary profile requires boolean ready")
        payload["status"] = "violation"
        return payload
    if profile.get("ready") is not True:
        if errors:
            payload["status"] = "violation"
            return payload
        payload["blocked"].append(
            "generated-adapter-boundary is owned by Package 2 and is not executable from the Package-1 scaffold"
        )
        payload["status"] = "blocked"
        return payload
    if fixture.get("fixture") != "generated-openspec-adapter":
        errors.append("generated profile fixture must be 'generated-openspec-adapter'")
    apply_contract_state(payload, profile.get("contract_state"), "generated-adapter-boundary", errors)
    workflow_fixture_path = project / "docs/harness/fixtures/workflow-orchestration-fixtures.yaml"
    try:
        workflow_fixture = load_fixture(workflow_fixture_path)
    except ValueError as exc:
        errors.append(f"cannot validate generated cross-fixture ready state: {exc}")
    else:
        workflow_profile = workflow_fixture.get("profiles", {}).get("generated-adapter-boundary")
        if not isinstance(workflow_profile, dict) or workflow_profile.get("ready") is not True:
            errors.append("generated cross-fixture ready state must be true in both fixtures")
        if workflow_profile.get("fixture") != "docs/harness/fixtures/generated-openspec-adapter-fixtures.yaml":
            errors.append("generated cross-fixture fixture path differs from canonical adapter fixture")
    if not isinstance(section, dict):
        errors.append("generated_adapter_boundary must be an object")
        return payload
    if section.get("schema_version") != SCHEMA_VERSION:
        errors.append("generated_adapter_boundary.schema_version must match checker version")

    routes = section.get("aili_routes")
    route_map: dict[str, str] = {}
    if not isinstance(routes, list) or not routes:
        errors.append("generated_adapter_boundary.aili_routes must be non-empty")
        routes = []
    for index, route in enumerate(routes):
        if not isinstance(route, dict):
            errors.append(f"aili_routes[{index}] must be an object")
            continue
        route_id = route.get("route")
        source = route.get("canonical_source")
        if route_id not in GENERATED_ROUTE_MAP:
            errors.append(f"aili_routes[{index}].route is invalid")
        else:
            if route_id in route_map:
                errors.append(f"aili_routes[{index}].route is duplicated")
            route_map[route_id] = source
        path_error = validate_repo_path(source, f"aili_routes[{index}].canonical_source")
        if path_error:
            errors.append(path_error)
        else:
            target, resolution_error = resolve_repo_field_target(
                project, source, "generated route source", allow_missing=False
            )
            if resolution_error:
                errors.append(resolution_error)
            elif target is None or not target.is_file():
                errors.append(f"aili_routes[{index}].canonical_source is not a file: {source}")
        if not isinstance(route.get("aili_gates_apply"), bool):
            errors.append(f"aili_routes[{index}].aili_gates_apply must be boolean metadata")
        if route.get("classification") != "canonical source":
            errors.append(f"aili_routes[{index}].classification must be canonical source")
    if route_map != GENERATED_ROUTE_MAP:
        errors.append("aili_routes must equal the accepted route-to-command map exactly")

    adapter_roots = section.get("adapter_roots")
    if adapter_roots != list(GENERATED_ADAPTER_ROOTS):
        errors.append("generated_adapter_boundary.adapter_roots must equal the exact generated roots")

    direct_cases = section.get("direct_adapter_cases")
    if not isinstance(direct_cases, list) or not direct_cases:
        errors.append("generated_adapter_boundary.direct_adapter_cases must be non-empty")
        direct_cases = []
    direct_map: dict[str, str] = {}
    for index, case in enumerate(direct_cases):
        if not isinstance(case, dict):
            errors.append(f"direct_adapter_cases[{index}] must be an object")
            continue
        case_id = case.get("id")
        if not isinstance(case_id, str) or not case_id or case_id in direct_map:
            errors.append(f"direct_adapter_cases[{index}].id must be unique and non-empty")
        else:
            direct_map[case_id] = case.get("adapter_path")
        path_error = validate_repo_path(
            case.get("adapter_path"), f"direct_adapter_cases[{index}].adapter_path"
        )
        if path_error:
            errors.append(path_error)
        else:
            target, resolution_error = resolve_repo_field_target(
                project,
                case.get("adapter_path"),
                "direct adapter path",
                allow_missing=False,
            )
            if resolution_error:
                errors.append(resolution_error)
            elif target is None or not target.is_file():
                errors.append(
                    f"direct_adapter_cases[{index}].adapter_path is not a file: {case.get('adapter_path')}"
                )
        if case.get("classification") != "generated/installed adapter":
            errors.append(
                f"direct_adapter_cases[{index}].classification must be generated/installed adapter"
            )
        if not isinstance(case.get("input_semantics"), str) or not case.get(
            "input_semantics"
        ).strip():
            errors.append(f"direct_adapter_cases[{index}].input_semantics must be non-empty")
    if direct_map != GENERATED_ADAPTER_CASES:
        errors.append("direct_adapter_cases must equal exact current generated adapter case IDs/paths")

    claim_boundary = section.get("claim_boundary")
    expected_boundary = {
        "direct_use_outside_aili": True,
        "aili_routes_to_direct_adapters": False,
        "aili_recommends_direct_adapters": False,
        "direct_output_is_aili_evidence": False,
    }
    if claim_boundary != expected_boundary:
        errors.append("generated_adapter_boundary.claim_boundary differs from canonical boundary")

    cases = section.get("cases")
    if not isinstance(cases, list) or not cases:
        errors.append("generated_adapter_boundary.cases must be non-empty")
        cases = []
    case_ids: set[str] = set()
    case_classifications: set[str] = set()
    for index, case in enumerate(cases):
        if not isinstance(case, dict):
            errors.append(f"generated adapter cases[{index}] must be an object")
            continue
        case_id = case.get("id")
        classification = case.get("expected_classification")
        if not isinstance(case_id, str) or not case_id or case_id in case_ids:
            errors.append(f"generated adapter cases[{index}].id must be unique and non-empty")
        else:
            case_ids.add(case_id)
        if classification not in GENERATED_CASE_CLASSIFICATIONS:
            errors.append(f"generated adapter cases[{index}] has invalid expected_classification")
        else:
            case_classifications.add(classification)
        if not isinstance(case.get("input_semantics"), str) or not case.get(
            "input_semantics"
        ).strip():
            errors.append(f"generated adapter cases[{index}].input_semantics must be non-empty")
        if not isinstance(case.get("expected_aili_gate_evaluated"), bool):
            errors.append(
                f"generated adapter cases[{index}].expected_aili_gate_evaluated must be boolean"
            )
    if case_classifications != GENERATED_CASE_CLASSIFICATIONS:
        errors.append("generated adapter cases must cover every expected classification")

    repository_inspection, repository_errors, repository_unverified = (
        inspect_generated_adapter_repository(project)
    )
    errors.extend(repository_errors)
    payload["unverified"].extend(repository_unverified)

    payload["aili_routes"] = routes
    payload["direct_adapter_cases"] = direct_cases
    payload["claim_boundary"] = claim_boundary if isinstance(claim_boundary, dict) else {}
    payload["cases"] = cases
    payload["repository_inspection"] = repository_inspection
    if any(
        route.get("aili_gates_apply")
        != repository_inspection.get("aili_gate_evidence", {}).get(route.get("route"), {}).get(
            "gates_apply"
        )
        for route in routes
        if isinstance(route, dict)
    ):
        errors.append(
            "fixture AILI gate booleans must match canonical-source-derived gate evidence"
        )
    if errors:
        payload["status"] = "violation"
    elif payload["blocked"]:
        payload["status"] = "blocked"
    elif payload["unverified"]:
        payload["status"] = "Unverified"
    else:
        payload["status"] = "pass"
    return payload


def residual(project: Path, change: str, fixture: dict[str, Any]) -> dict[str, Any]:
    payload = profile_payload("residual")
    errors: list[str] = payload["errors"]
    if fixture.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must be {SCHEMA_VERSION!r}")
    if fixture.get("change") != change:
        errors.append(f"fixture change must equal requested change {change!r}")
    if change != UMBRELLA_CHANGE:
        errors.append(f"residual profile is change-specific and requires {UMBRELLA_CHANGE!r}")
    profiles = fixture.get("profiles")
    profile = profiles.get("residual") if isinstance(profiles, dict) else None
    section = fixture.get("residual")
    if not isinstance(profile, dict) or not isinstance(profile.get("ready"), bool):
        errors.append("residual profile requires boolean ready")
        payload["status"] = "violation"
        return payload
    if profile.get("ready") is not True:
        if errors:
            payload["status"] = "violation"
            return payload
        payload["blocked"].append(
            "residual is owned by Packages 4-11 and is not executable as a clean final scan from Package 1"
        )
        payload["status"] = "blocked"
        return payload
    if fixture.get("fixture") != "workflow-orchestration":
        errors.append("residual profile fixture must be 'workflow-orchestration'")
    apply_contract_state(payload, profile.get("contract_state"), "residual", errors)
    if not isinstance(section, dict):
        errors.append("residual must be an object")
        return payload
    if section.get("schema_version") != SCHEMA_VERSION:
        errors.append("residual.schema_version must match checker version")
    if section.get("proof_scope") != "complete-active-source-scan-with-explicit-exclusions":
        errors.append("residual.proof_scope is incomplete")

    validate_task_oracle(project, fixture, errors)
    inspect_agent_inventory(project, errors)
    validate_a33_scaffold_and_rejections(project, fixture, errors)

    semantic_rules = section.get("semantic_rules")
    if semantic_rules is not None and semantic_rules != sorted(REJECTED_SEMANTIC_RULES):
        errors.append("residual.semantic_rules, when present, must equal the deterministic rule set exactly")
    semantic_patterns = section.get("semantic_patterns")
    expected_patterns = {
        rule_id: pattern.pattern for rule_id, pattern in sorted(REJECTED_SEMANTIC_RULES.items())
    }
    if semantic_patterns is not None and semantic_patterns != expected_patterns:
        errors.append("residual.semantic_patterns, when present, must equal the checker patterns exactly")

    supplied_matches = section.get("matches")
    supplied_classifications = section.get("classifications")

    derived_matches, derived_classifications, scan_errors, scan_unverified = derive_residual_scan(
        project, fixture, section
    )
    errors.extend(scan_errors)
    payload["unverified"].extend(scan_unverified)
    if supplied_matches is not None and supplied_matches != derived_matches:
        errors.append("residual.matches must exactly equal repository-derived observations")
    if supplied_classifications is not None and supplied_classifications != derived_classifications:
        errors.append("residual.classifications must exactly classify every derived match once")
    if any(
        item.get("classification") == "active violation"
        for item in derived_classifications
    ):
        errors.append("repository-derived residual scan reports an active violation")

    cases = section.get("cases")
    if not isinstance(cases, list) or not cases:
        errors.append("residual.cases must be non-empty")
        cases = []
    case_ids: set[str] = set()
    expected_classes: set[str] = set()
    for index, case in enumerate(cases):
        if not isinstance(case, dict):
            errors.append(f"residual.cases[{index}] must be an object")
            continue
        case_id = case.get("id")
        expected = case.get("expected_classification")
        if not isinstance(case_id, str) or not case_id or case_id in case_ids:
            errors.append(f"residual.cases[{index}].id must be unique and non-empty")
        else:
            case_ids.add(case_id)
        if expected not in RESIDUAL_CLASSIFICATIONS:
            errors.append(f"residual.cases[{index}] has invalid expected_classification")
        else:
            expected_classes.add(expected)
        if not isinstance(case.get("input_semantics"), str) or not case.get(
            "input_semantics"
        ).strip():
            errors.append(f"residual.cases[{index}].input_semantics must be non-empty")
        if not isinstance(case.get("expected_active_authority"), bool):
            errors.append(
                f"residual.cases[{index}].expected_active_authority must be boolean"
            )
    if expected_classes != RESIDUAL_CLASSIFICATIONS:
        errors.append("residual.cases must cover every expected classification")

    payload["matches"] = derived_matches
    payload["classifications"] = derived_classifications
    if errors:
        payload["status"] = "violation"
    elif payload["blocked"]:
        payload["status"] = "blocked"
    elif payload["unverified"]:
        payload["status"] = "Unverified"
    else:
        payload["status"] = "pass"
    return payload


def exit_code(payload: dict[str, Any]) -> int:
    if payload.get("errors"):
        return 5
    if payload.get("blocked") or payload.get("unverified"):
        return 3
    return 0


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    project = Path(args.project).resolve()
    if not project.is_dir():
        print(f"workflow-contract-check: project is not a directory: {project}", file=sys.stderr)
        return 2
    try:
        fixture_path = resolve_inside(project, args.fixture, "fixture")
    except ValueError as exc:
        print(f"workflow-contract-check: {exc}", file=sys.stderr)
        return 2
    if not fixture_path.is_file():
        print(f"workflow-contract-check: fixture does not exist: {fixture_path}", file=sys.stderr)
        return 2
    try:
        fixture = load_fixture(fixture_path)
    except ValueError as exc:
        payload = profile_payload(args.profile)
        payload["errors"].append(str(exc))
        emit(payload, args.json_output)
        return 5

    if args.profile == "scaffold":
        payload = scaffold(project, args.change, fixture)
    elif args.profile == "generated-adapter-boundary":
        payload = generated_adapter_boundary(project, args.change, fixture)
    else:
        payload = residual(project, args.change, fixture)
    if args.task_audit and not args.final_closure:
        payload["errors"].append("--task-audit is valid only with --final-closure")
    if args.final_closure:
        if args.profile != "scaffold":
            payload["errors"].append("final closure mode is valid only with the scaffold profile")
        elif not args.task_audit:
            payload["errors"].append("final closure requires a separate ROSE-owned task-audit JSON path")
        else:
            try:
                task_audit_path = resolve_inside(project, args.task_audit, "task audit")
            except ValueError as exc:
                payload["errors"].append(str(exc))
            else:
                if task_audit_path == fixture_path:
                    payload["errors"].append(
                        "final closure requires a separate ROSE-owned task-audit path that must differ from generated Partial traceability"
                    )
                elif not task_audit_path.is_file():
                    payload["errors"].append(f"task audit does not exist: {task_audit_path}")
                else:
                    payload["final_task_audit"] = validate_final_task_audit(
                        project,
                        args.change,
                        task_audit_path,
                        payload.get("traceability", {}).get("task_matrix", []),
                        payload["errors"],
                    )
    if payload["errors"]:
        payload["status"] = "violation"
    emit(payload, args.json_output)
    return exit_code(payload)


if __name__ == "__main__":
    sys.exit(main())
