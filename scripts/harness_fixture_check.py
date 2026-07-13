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

REQUIRED = {
    "command-routing-fixtures.yaml": {
        "markers": [
            "/ideate",
            "/define",
            "/build",
            "/ship",
            "/local-review",
            "code-scout",
            "implementer",
            "code-reviewer",
            "test-engineer",
            "security-auditor",
            "neutral-build",
            "package-queue",
            "external-repo-root",
            "release-readiness",
            "release-blocker-audit",
            "local-review-gate",
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
            "ecc-code-review-adaptation.md",
            "review-repair-lane-adaptation.md",
            "orchestration-adaptation.md",
            "addyosmani-code-review-rubric.md",
            "codex-github-compatibility.md",
            "five axes",
            "Critical/Important/Suggestion",
            "spec/task-first",
            "concrete fixes",
            "uncertainty/proof gates",
            "Codex behavior-only",
            "no official docs text copied",
            "parallelism analysis",
            "no-parallel reason",
            "package/lane preservation",
            "join completeness",
            "official/API docs",
            "evidence-backed 方案",
            "UNVERIFIED before implementation",
            "test first",
            "complete, appropriately scoped, verified",
            "not artificially tiny",
            "most relevant focused verification",
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
        "markers": ["aili-delivery-flow", "harness-issue-triage", "harness-evolution", "mature-project-pattern-research", "source-driven-development", "git-workflow-and-versioning", "official/API docs", "cleanup package", "approval-gated cleanup", "trigger", "non-trigger"],
        "case_key": "cases",
        "min_cases": 6,
    },
    "subagent-dispatch-fixtures.yaml": {
        "markers": ["trace_id", "work_package_type", "artifact_target", "coverage_expectation", "known_exclusions", "evidence_anchors", "package-queue", "implementer", "allowed_scope", "forbidden_scope", "edit_permission", "commit_allowance", "complete, appropriately scoped, verified", "not artificially tiny", "most relevant focused verification", "classify dirty paths", "approval-gated cleanup", "cleanup package", "parallelism analysis", "join completeness", "package/lane preservation", "no-parallel reason"],
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
        "markers": ["memory-explicit-facts", "memory-candidate", "handoff-trigger", "handoff-no-threshold-trigger", "resume-hydration", "artifact-integrity-documentation-only"],
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
        "markers": ["aili.cross-worktree-permission-fixtures.v2", "effective-merged-tool-inventory", "direct-invocation-excluded", "seeded-parent-edit-allow-blocks", "external-always-read-broadens", "no-real-user-state"],
        "case_key": "cases",
        "min_cases": 21,
        "package": "P6",
        "format": "text-yaml",
    },
    "review-convergence-fixtures.yaml": {
        "markers": ["all-task-one-row", "task-audit-na-accepted-source-pass", "subagent-nesting-forbidden", "diverse-lane-join", "no-majority-vote"],
        "case_key": "cases",
        "min_cases": 25,
        "package": "P7",
    },
    "upstream-reference-fixtures.yaml": {
        "markers": ["matt-handoff", "addy-idea-refine", "positive", "near-miss", "negative", "upstream_runnable"],
        "case_key": "cases",
        "min_cases": 15,
        "package": "P8",
    },
    "graphify-local-review-fixtures.yaml": {
        "markers": ["strict-local", "no-install", "network-denial-required", "false-run-claim", "argv-newline"],
        "case_key": "cases",
        "min_cases": 27,
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
        errors.extend(validate_subagent_dispatch(cases, name))
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
            "handoff-trigger", "handoff-no-threshold-trigger", "resume-hydration", "handoff-resume",
            "memory-stage1-boundary", "artifact-authority-boundaries", "artifact-integrity-documentation-only",
        },
        "cross-worktree-permission-fixtures.yaml": {
            "effective-merged-tool-inventory", "unexpected-tool-denied", "direct-invocation-excluded",
            "seeded-parent-edit-allow-blocks", "seeded-parent-bash-allow-blocks",
            "seeded-parent-task-allow-blocks", "external-always-read-broadens",
            "auto-read-privacy-caveat", "mutation-capable-effective-rule-blocks",
            "clean-external-read-positive", "clean-path-ask", "edit-denied", "bash-denied",
            "task-denied", "commit-denied", "merge-denied", "apply-denied", "parent-unchanged",
            "target-unchanged", "common-dir-unchanged", "no-real-user-state",
        },
        "review-convergence-fixtures.yaml": {
            "all-task-one-row", "task-row-missing", "task-row-duplicate", "task-row-undefined",
            "task-audit-all-five-statuses", "task-audit-na-accepted-source-pass", "pseudo-complete",
            "task-status-invalid", "unchecked-task", "stale-evidence", "task-file-mismatch",
            "task-test-mismatch", "na-without-accepted-source", "drift-unrequested",
            "subagent-nesting-forbidden", "diverse-lane-join", "no-majority-vote",
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
        exact_cases = [
            ("effective-merged-tool-inventory", "exact-final-merged-profile"),
            ("unexpected-tool-denied", "deny"),
            ("direct-invocation-excluded", "outside-guarantees"),
            ("seeded-parent-edit-allow-blocks", "block-effective-override"),
            ("seeded-parent-bash-allow-blocks", "block-effective-override"),
            ("seeded-parent-task-allow-blocks", "block-effective-override"),
            ("external-always-read-broadens", "disclose-read-privacy"),
            ("auto-read-privacy-caveat", "disclose-or-unverified"),
            ("mutation-capable-effective-rule-blocks", "block"),
            ("clean-external-read-positive", "pass-through-rose-task"),
            ("clean-path-ask", "exact-path-ask"),
            ("edit-denied", "no-effect"), ("bash-denied", "no-effect"),
            ("task-denied", "no-effect"), ("commit-denied", "no-effect"),
            ("merge-denied", "no-effect"), ("apply-denied", "no-effect"),
            ("parent-unchanged", "equal"), ("target-unchanged", "equal"),
            ("common-dir-unchanged", "equal"), ("no-real-user-state", "temporary-only"),
        ]
        observed_cases = [
            (case.get("id"), case.get("expected")) for case in cases if isinstance(case, dict)
        ]
        if observed_cases != exact_cases:
            errors.append(f"{name}: cases must equal the exact canonical id/expected matrix")
        text = data.get("text", "")
        runtime_modes = re.findall(r"^runtime_mode:\s*(\S+)\s*$", text, re.MULTILINE)
        if runtime_modes != ["real"] or "mode: a30-same-instance-readonly" not in text or "provider: local-mock" not in text:
            errors.append(f"{name}: runtime mode/provider must be exact A30 real declarations")
        fields_block = re.search(
            r"^required_report_fields:\s*\n((?:\s+-\s+[^\n]+\n?)+)", text, re.MULTILINE
        )
        observed_fields = re.findall(r"^\s+-\s+([^\s#]+)\s*$", fields_block.group(1), re.MULTILINE) if fields_block else []
        expected_fields = [
            "schema_version", "mode", "status", "roles", "fixture_identity", "effective_permissions",
            "cases", "parent_before", "parent_after", "target_before", "target_after",
            "common_dir_before", "common_dir_after", "clean_ask", "seeded_always",
            "override_observability", "blocked", "unverified", "errors", "cleanup",
        ]
        if observed_fields != expected_fields:
            errors.append(f"{name}: required_report_fields differs from the exact operational schema")
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
        task_path = ROOT / "openspec/changes/complete-aili-workflow-orchestration/tasks.md"
        canonical_ids = set(re.findall(r"^- \[[ xX]\] (\d+\.\d+)\b", task_path.read_text(encoding="utf-8"), re.MULTILINE))
        fixture_task_ids = data.get("task_ids")
        if len(canonical_ids) != 74 or not isinstance(fixture_task_ids, list) or set(fixture_task_ids) != canonical_ids or len(fixture_task_ids) != len(set(fixture_task_ids)):
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
        if routing_case.get("expected") != {"ai_surface": "ai-regression-scout", "ordinary_test_surface": "test-engineer", "overlap": "dispatch both with distinct evidence questions"}:
            errors.append(f"{name}: AI-regression-scout vs test-engineer routing must remain explicit")
        runtime_enforcement = data.get("runtime_enforcement", {})
        if runtime_enforcement.get("id") != "UV-001" or runtime_enforcement.get("status") != "Unverified" or "do not prove" not in runtime_enforcement.get("reason", ""):
            errors.append(f"{name}: final read-only overlay runtime enforcement must remain UV-001 Unverified")
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
    return errors


def validate_skill_routing(cases: list, name: str) -> list[str]:
    errors: list[str] = []
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
        if case.get("final_gate") != "package-12-final-gate":
            errors.append(f"{name}: neutral BUILD final gate must be Package 12")
        if case.get("target_repo_root") != "infer-canonical-from-backend-context" or case.get("cwd_authority") is not False:
            errors.append(f"{name}: neutral BUILD must infer canonical root and reject cwd authority")
        errors.extend(require_checks(case, "queue_inputs", ["tasks.md", "specs", "design", "test-plan.md", "repository-evidence"], name, "neutral BUILD"))

    for case in cases:
        if isinstance(case, dict) and case.get("expected_mode") == "BUILD":
            if case.get("expected_checks") or case.get("expected_conditional_checks"):
                errors.append(f"{name}: {case.get('id')} encodes a forbidden per-package mandatory quality gate")

    local_modes = {case.get("target_mode") for case in cases if isinstance(case, dict) and case.get("expected_mode") == "LOCAL_REVIEW" and case.get("trigger") is True}
    for target_mode in ["default-local-changes", "base-branch", "commit", "pr", "OpenSpec change", "focus-adversarial", "repair"]:
        if target_mode not in local_modes:
            errors.append(f"{name}: missing /local-review target mode {target_mode!r}")

    for internal_command in ["/research", "/review", "/release-blocker-audit"]:
        matching = [case for case in cases if isinstance(case, dict) and str(case.get("input", "")).startswith(internal_command)]
        if not matching or any(case.get("trigger") is not False for case in matching):
            errors.append(f"{name}: {internal_command} must remain a covered non-trigger")
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


def validate_subagent_dispatch(cases: list, name: str) -> list[str]:
    errors: list[str] = []
    goal_packets = [case for case in cases if isinstance(case, dict) and case.get("id") == "packet-build-neutral-package"]
    if not goal_packets:
        return [f"{name}: missing packet-build-neutral-package case"]

    packet = goal_packets[0]
    expected_scalars = {
        "agent": "implementer",
        "artifact_target": "package-queue",
        "allowed_scope": "single synthesized package",
        "edit_permission": "package-scoped",
        "commit_allowance": "active-contract",
    }
    for field, expected in expected_scalars.items():
        if packet.get(field) != expected:
            errors.append(f"{name}: packet-build-neutral-package {field} must be {expected!r}")
    errors.extend(require_checks(packet, "forbidden_scope", ["out-of-scope packages", "high-risk gates without approval", "package-local mandatory quality gate"], name, "packet-build-neutral-package"))
    errors.extend(require_checks(packet, "parallelism_analysis", ["parallelism analysis", "no-parallel reason", "join completeness", "package/lane preservation"], name, "packet-build-neutral-package"))
    errors.extend(require_checks(packet, "join_contract", ["join points", "blockers", "expected evidence"], name, "packet-build-neutral-package"))
    errors.extend(require_checks(packet, "required_evidence", ["evidence_anchors", "changed_files", "scope_boundary", "lightweight savepoint"], name, "packet-build-neutral-package"))
    errors.extend(require_checks(packet, "implementation_objective", ["complete, appropriately scoped, verified", "complete task-scoped", "not artificially tiny"], name, "packet-build-neutral-package"))
    if packet.get("review_repair", "missing") is not None:
        errors.append(f"{name}: packet-build-neutral-package review_repair must be null for Package 1-11")
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

    return errors


def validate_agent_permissions() -> list[str]:
    errors: list[str] = []
    agent_dir = ROOT / "agents"
    a30_selected = {
        "agent-evaluator.md", "ai-regression-scout.md", "code-reviewer.md", "code-scout.md",
        "convergence-reviewer.md", "doc-researcher.md", "opensource-sanitizer.md", "plan-auditor.md",
        "pr-test-analyzer.md", "security-auditor.md", "silent-failure-reviewer.md", "spec-miner.md",
        "test-coverage-reviewer.md", "web-performance-auditor.md", "web-researcher.md",
    }
    for path in sorted(agent_dir.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        if not text.startswith("---\n"):
            errors.append(f"{path.relative_to(ROOT)}: missing frontmatter")
            continue
        parts = text.split("---", 2)
        if len(parts) < 3:
            errors.append(f"{path.relative_to(ROOT)}: unterminated frontmatter")
            continue
        frontmatter = parts[1]
        if "\npermission:\n" not in frontmatter:
            errors.append(f"{path.relative_to(ROOT)}: missing permission block")
        if path.name in a30_selected:
            if '\n  "*": deny\n' not in frontmatter:
                errors.append(f"{path.relative_to(ROOT)}: A30 selected role missing deny-by-default wildcard")
            if "\n  external_directory: ask\n" not in frontmatter:
                errors.append(f"{path.relative_to(ROOT)}: A30 selected role missing external_directory ask")
            for key in ["list", "glob", "grep"]:
                if f"\n  {key}: allow\n" not in frontmatter:
                    errors.append(f"{path.relative_to(ROOT)}: A30 selected role missing {key} allow")
            for key in ["edit", "bash", "task", "lsp", "skill", "webfetch", "websearch"]:
                if f"\n  {key}: deny\n" not in frontmatter:
                    errors.append(f"{path.relative_to(ROOT)}: A30 selected role missing {key} deny")
        elif path.name == "rose.md":
            if "\n  skill: allow\n" not in frontmatter and "\n  \"*\": allow\n" not in frontmatter:
                errors.append(f"{path.relative_to(ROOT)}: missing skill allowance via permission.skill or wildcard")
        elif "\n  skill: allow\n" not in frontmatter:
            errors.append(f"{path.relative_to(ROOT)}: missing permission.skill allow")
        if "\n  read:\n" not in frontmatter:
            errors.append(f"{path.relative_to(ROOT)}: missing permission.read block")
        elif "\n    \"*\": allow\n" not in frontmatter:
            errors.append(f"{path.relative_to(ROOT)}: missing permission.read wildcard allow")
        if path.name != "rose.md" and path.name not in a30_selected and "\n  external_directory: deny\n" not in frontmatter:
            errors.append(f"{path.relative_to(ROOT)}: nonselected subagent must deny external_directory")
        if path.name != "rose.md" and "\n  task: deny\n" not in frontmatter:
            errors.append(f"{path.relative_to(ROOT)}: non-ROSE subagent must deny task")
    return errors


def read_repo_text(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def validate_command_contracts() -> list[str]:
    errors: list[str] = []
    command_dir = ROOT / "commands"
    allowed_delivery_commands = {"ideate.md", "define.md", "build.md", "ship.md"}
    allowed_non_delivery_commands = {"local-review.md"}
    allowed_public_commands = allowed_delivery_commands | allowed_non_delivery_commands
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
        errors.append(f"commands/{name}: unexpected top-level command; only ideate, define, build, ship, and local-review are allowed")

    unexpected_internal = sorted(existing_commands & internal_delivery_commands)
    for name in unexpected_internal:
        errors.append(f"commands/{name}: internal lifecycle stage must not be a top-level delivery command")

    missing = sorted(allowed_delivery_commands - existing_commands)
    for name in missing:
        errors.append(f"commands/{name}: missing public delivery command")

    for name in sorted(allowed_non_delivery_commands - existing_commands):
        errors.append(f"commands/{name}: missing public local audit command")

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
        "local review gate workflow",
        "local-review-gate",
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

    define_text = read_repo_text("commands/define.md") if (command_dir / "define.md").exists() else ""
    for marker in [
        "requirements-grilling",
        "test-document-generator",
        "interview.md",
        "test-plan.md",
        "Artifact Freshness Gate",
        "READY",
        "BLOCKED",
        "WAIVED",
        "UNVERIFIED",
    ]:
        if marker not in define_text:
            errors.append(f"commands/define.md: missing DEFINE contract marker {marker!r}")

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
            "Review lanes remain read-only",
            "separate edit/repair agent or edit/test lane",
            "convergence-reviewer",
            "phase checkpoint",
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
        ".agents/skills/aili-delivery-flow/references/lifecycle.md": [
            "large or harness-sensitive `/local-review --change <id|path>` targets",
            "`NEEDS_FIXES` and `BLOCKED` as BUILD blockers",
            "`PASS_WITH_UNVERIFIED` only after the user accepts each named `Unverified` item",
        ],
        "agents/convergence-reviewer.md": [
            "edit: deny",
            "task: deny",
            "proposal.md",
            "design.md",
            "tasks.md",
            "interview.md",
            "test-plan.md",
            "context.md",
            "progress.txt",
            "drift-log.md",
            "legacy `implementation-notes.html`",
            "missing",
            "partial",
            "contradicts",
            "unrequested",
            "pseudo-complete",
            "unchecked-task",
            "stale-progress",
            "evidence-gap",
            "Merged-output verification evidence",
        ],
        ".agents/skills/review-pipeline/SKILL.md": [
            "convergence-reviewer",
            "formal-change, OpenSpec, multi-phase, or harness-sensitive convergence review",
            "not final PASS authority",
            "pseudo-complete",
            "unchecked-task",
            "stale-progress",
            "evidence-gap",
        ],
        ".agents/skills/parallel-subagent-dispatch/SKILL.md": [
            "phase checkpoint: command, static check, artifact inspection, diff inspection, or skipped reason with risk",
            "merged-output verification",
            "statuses, evidence, conflicts, blockers, skipped checks, and missing evidence",
        ],
        ".agents/skills/aili-delivery-flow/references/protocols/subagent-task-packet.md": [
            "Phase checkpoint: command | static check | artifact inspection | diff inspection | skipped reason with risk",
            "Parallel joins must reconcile every expected lane's status, evidence, skipped checks, conflicts, blockers, and missing evidence",
            "merged-output verification",
            "Review and convergence lanes remain read-only",
        ],
        "agents/rose.md": [
            '"convergence-reviewer": allow',
            "Local review gate: `local-review-gate`",
            "`convergence-reviewer` (`subagent:review`)",
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
        "96cac1d79edca4a9231cbe6af50415b5e4d6cf42",
        "af791188ac87321f749a96f140a85c739303f453",
        "five dimensions",
        "Critical and Important finding",
        "zero findings",
        "file:line, trigger/input/state, bad outcome",
        "Do not add optional praise",
        "If context is insufficient for a material acceptance claim",
        "Secret-path safety",
        "must not run content-emitting git commands",
        "report only the redacted path/type",
    ]:
        if marker not in code_reviewer_text:
            errors.append(f"agents/code-reviewer.md: missing upstream review rubric marker {marker!r}")
    return errors


def validate_define_artifact_contracts() -> list[str]:
    errors: list[str] = []
    required_markers = {
        ".agents/skills/aili-delivery-flow/SKILL.md": [
            "requirements-grilling",
            "test-document-generator",
            "Unverified",
        ],
        ".agents/skills/aili-delivery-flow/references/lifecycle.md": [
            "requirements-grilling",
            "test-document-generator",
            "READY",
            "BLOCKED",
            "WAIVED",
            "UNVERIFIED",
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
            "Artifact Freshness Gate",
            "Conversation context is stale",
            "disk wins",
            "interview.md",
            "requirements-grilling",
        ],
        ".agents/skills/aili-delivery-flow/references/test-document-policy.md": [
            "Artifact Freshness Gate",
            "Conversation context is stale",
            "disk wins",
            "test-plan.md",
            "test-document-generator",
        ],
        ".agents/skills/requirements-grilling/SKILL.md": [
            "change-interviewer",
            "interview packet",
            "interview.md",
            "unresolved readiness follow-up defaults to chat-first interaction with AI write-back",
            "ask unresolved blocking follow-up questions in chat by default",
            "write accepted answers, waivers, or accepted `UNVERIFIED` states back into the same artifact",
            "re-read answers from disk before classification, readiness, or write-back",
            "Do not call the packet `READY` from chat-only content",
            "Round 2+",
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
            "do not create `grill.md`, `grilling.md`, or `requirements-grilling.md`",
        ],
        ".agents/skills/requirements-grilling/references/INTERVIEW-PACKET-FORMAT.md": [
            "# 需求拷问包：<change-name>",
            "资料来源与证据",
            "覆盖矩阵与状态",
            "术语 / 领域模型挑战",
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
            "UNVERIFIED",
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
        "commands/build.md": ["neutral", "implementation package queue", "target repository root", "Package 12", "lightweight savepoint", "Do not ask for manual package approval"],
        ".agents/skills/aili-delivery-flow/SKILL.md": ["references/build-execution-loop.md", "resolved ready target", "synthesize a package queue", "Package 12"],
        ".agents/skills/aili-delivery-flow/references/lifecycle.md": ["neutral bounded package execution", "synthesize an ordered implementation package queue", "allowed external directories"],
        ".agents/skills/aili-delivery-flow/references/backend-routing.md": ["neutral package queue", "canonicalizes the target repository root", "allowed external directories"],
        ".agents/skills/aili-delivery-flow/references/implementation-packages.md": ["synthesize an ordered package queue", "scoped subagent packet", "missing manual package text is not a stop condition", "Package 12"],
        ".agents/skills/aili-delivery-flow/references/build-execution-loop.md": ["Neutral BUILD Execution Loop", "Exactly six inner loops", "Exactly four outer profiles", "Canonical `CONT-005` envelope and budgets", "Protocol-only automation boundary", "Native command non-ownership"],
        "docs/harness/command-lifecycle.md": ["lightweight savepoints", "Package 12", "exactly six inner loops"],
        "docs/harness/aili-harness-contract.md": ["Neutral BUILD execution", "Package 12", "no per-package quality gate"],
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
    required_ids = """loop-six-inner-four-outer loop-turn-executable loop-turn-no-recursion loop-objective-bounded loop-objective-budget-invalid loop-objective-max-attempt-stop loop-objective-exhaustion loop-objective-resume-no-reset loop-review-budget-separate loop-envelope-complete loop-envelope-terminal-writeback budget-representation-objective budget-representation-turn budget-protocol-template-instantiation budget-invalid-iteration-review budget-invalid-time-unit-value budget-invalid-token-unit-value tokens-not-configured-null tokens-requested-accounting-unavailable-prestart tokens-midrun-accounting-loss budget-exhaustion-evidence budget-resume-no-reset lp-budget-valid-instantiation lp-budget-invalid-iteration-zero lp-budget-invalid-iteration-negative lp-budget-invalid-iteration-fractional lp-budget-invalid-iteration-nonnumeric lp-budget-invalid-review-zero lp-budget-invalid-review-negative lp-budget-invalid-review-fractional lp-budget-invalid-review-nonnumeric lp-budget-review-capable-null lp-budget-review-incapable-nonnull budget-iteration-preflight-unit budget-review-preflight-unit budget-time-overshoot-actual budget-token-overshoot-actual budget-resume-preserves-overshoot-accounting loop-interval-protocol-only loop-event-protocol-only loop-automation-no-registration loop-formal-runbook-protocol-only loop-no-background-primitive loop-interval-documentation-ambiguity loop-interval-executable-request-block neutral-build-native-goal-nonownership ordinary-goal-language-preserved native-goal-partii-na def-e2-no-per-package-gate def-e3-final-matrix-compatibility budget-consumed-over-limit-terminal budget-iteration-consumed-over-limit-corruption budget-review-consumed-over-limit-corruption""".split()
    errors = [f"command-routing-fixtures.yaml: missing Package 5 fixture {case_id}" for case_id in required_ids if case_id not in by_id]
    taxonomy = by_id.get("loop-six-inner-four-outer", {})
    if taxonomy.get("inner") != ["question", "delta", "evidence/plan", "neutral BUILD", "review/repair", "convergence"] or taxonomy.get("outer") != ["turn", "objective", "interval", "event"] or taxonomy.get("seventh_loop") is not False:
        errors.append("command-routing-fixtures.yaml: loop taxonomy must be exactly six inner/four outer with no seventh loop")
    unavailable = by_id.get("tokens-requested-accounting-unavailable-prestart", {}).get("tokens", {})
    if unavailable.get("accounting_status") != "unavailable" or unavailable.get("remaining") != unavailable.get("limit"):
        errors.append("command-routing-fixtures.yaml: unavailable token accounting must preserve requested non-null counters")
    lost = by_id.get("tokens-midrun-accounting-loss", {}).get("tokens", {})
    if lost.get("accounting_status") != "lost" or not isinstance(lost.get("consumed"), int):
        errors.append("command-routing-fixtures.yaml: midrun token loss must preserve non-null counters")
    if by_id.get("def-e2-no-per-package-gate", {}).get("mandatory_quality_gate") is not False:
        errors.append("command-routing-fixtures.yaml: DEF-E2 compatibility must forbid per-package mandatory gates")
    final_case = by_id.get("def-e3-final-matrix-compatibility", {})
    if final_case.get("review_repair_limit") != 3 or final_case.get("max_holistic_cycles") != 3 or final_case.get("task_matrix") != "canonical-all-task":
        errors.append("command-routing-fixtures.yaml: DEF-E3 final matrix must be canonical and limited to three cycles")
    over_limit = by_id.get("budget-consumed-over-limit-terminal", {})
    if over_limit.get("counter") != {"limit": 3, "consumed": 4, "remaining": 0} or over_limit.get("stop_reason") != "budget-exhausted" or over_limit.get("outcome") != "budget-exhausted" or over_limit.get("resume") != "blocked":
        errors.append("command-routing-fixtures.yaml: consumed>limit must preserve consumed, clamp remaining, and remain terminal")
    for case_id in ("budget-iteration-consumed-over-limit-corruption", "budget-review-consumed-over-limit-corruption"):
        case = by_id.get(case_id, {})
        if case.get("expected") not in {"corruption-block-no-action", "corruption-block-no-repair"} or case.get("overshoot_allowed") is not False or case.get("resume") != "blocked":
            errors.append(f"command-routing-fixtures.yaml: {case_id} must treat discrete consumed>limit as corruption and block")
    automation = by_id.get("loop-automation-no-registration", {})
    expected_automation = ["install", "register", "run", "modify", "update", "reconfigure", "enable", "reuse"]
    if automation.get("pure_inputs") != expected_automation or automation.get("mixed_documentation") != "block-whole-request" or automation.get("later_documentation_only") != "may-define-or-reuse-lp":
        errors.append("command-routing-fixtures.yaml: automation fixture must block pure/mixed requests with zero mutation/LP and require later documentation-only restatement")
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
            "requirements/decisions/risks traceability matrix is mandatory",
            "task/package",
            "file/artifact",
            "verification/evidence",
            "Open Question",
            "Unverified",
        ],
        ".agents/skills/aili-delivery-flow/references/lifecycle.md": [
            "map each package from source requirement/decision/risk to task/package",
            "changed files/artifacts mapped to requirements/decisions/risks",
            "spec coverage check for formal changes",
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
        ".agents/skills/verification-before-completion/SKILL.md": [
            "spec coverage check mapping requirements/tasks/test-plan items",
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
            "Deliver a complete, appropriately scoped, verified implementation.",
            "Do not sacrifice correctness, completeness, user goals, or long-term maintainability to minimize the diff.",
            "Run the most relevant focused verification first, then broaden only when needed.",
            "Do not stay artificially small when the assigned task is inherently cross-module",
        ],
        "agents/rose.md": [
            "choose a complete, appropriately scoped, verified implementation",
            "do not sacrifice correctness, completeness, user goals, or long-term maintainability to minimize the diff",
            "Stage only task-scoped files",
        ],
        "templates/opencode-global-AGENTS.md": [
            "Implement the complete, appropriately scoped change that satisfies the accepted task.",
            "Run the most relevant focused verification first, then broaden only as needed.",
            "the diff is task-scoped and non-speculative",
        ],
        "commands/build.md": [
            "Implement complete package behavior inside the accepted scope",
            "not artificially tiny or partial patches",
        ],
        ".agents/skills/aili-delivery-flow/references/lifecycle.md": [
            "require complete implementation for accepted scope",
            "not artificially tiny patches",
            "run the most relevant focused verification first",
        ],
        ".agents/skills/aili-delivery-flow/references/build-execution-loop.md": [
            "run the most relevant focused tests/checks first",
            "Run focused verification when useful",
        ],
    }

    for relative, markers in complete_scoped_markers.items():
        errors.extend(require_text_markers(relative, markers, "complete scoped work"))

    if (ROOT / "agents/implementer.md").exists():
        implementer_text = read_repo_text("agents/implementer.md")
        objective = section_between(implementer_text, "## Primary Objective", "## Implementation Discipline")
        if not objective:
            errors.append("agents/implementer.md: missing Primary Objective section")
        else:
            errors.extend(require_absent_in_section("agents/implementer.md", objective, ["smallest", "minimal", "minimum"], "Primary Objective"))
        verification = section_between(implementer_text, "### Goal-Driven Verification", "### Stop Instead")
        if not verification:
            errors.append("agents/implementer.md: missing Goal-Driven Verification section")
        else:
            errors.extend(require_absent_in_section("agents/implementer.md", verification, ["smallest relevant", "minimal verification", "minimum verification"], "verification-order wording"))
        errors.extend(
            require_text_markers(
                "agents/implementer.md",
                [
                    "current task explicitly allows a private unverified `wip:` checkpoint",
                    "use a private `wip:` prefix only when the current task explicitly allows an unverified checkpoint",
                ],
                "implementer wip checkpoint allowance",
            )
        )

    if (ROOT / "templates/opencode-global-AGENTS.md").exists():
        global_text = read_repo_text("templates/opencode-global-AGENTS.md")
        simplicity = section_between(global_text, "### 3. Simplicity First", "### 4. Task-Scoped Changes")
        if not simplicity:
            errors.append("templates/opencode-global-AGENTS.md: missing Simplicity First section")
        else:
            errors.extend(require_absent_in_section("templates/opencode-global-AGENTS.md", simplicity, ["smallest", "minimal", "minimum"], "implementation-objective wording"))
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
    errors.extend(require_text_markers(".agents/skills/agents-md-initialization/references/agents_md.py", agents_checker_markers, "bundled AGENTS checker"))

    agents_template_markers = [
        "## Project-Specific Testing and Artifact Placement",
        "## Local Overrides",
    ]
    errors.extend(require_text_markers("templates/AGENTS.md", agents_template_markers, "project AGENTS template"))
    errors.extend(require_text_markers(".agents/skills/agents-md-initialization/references/agents-template.md", agents_template_markers, "bundled project AGENTS template"))

    git_workflow_markers = [
        "task-scoped savepoint commits only when current task/project rules explicitly allow verified commits",
        "otherwise ask once with the cleanup package",
        "ask explicit approval before push, destructive clean/reset, branch deletion, worktree removal, OpenSpec archive, stashing unrelated changes, or deleting user-visible artifacts",
        "`wip:` checkpoints are allowed only when the current task explicitly approves a private unverified checkpoint",
    ]
    errors.extend(require_text_markers(".agents/skills/git-workflow-and-versioning/SKILL.md", git_workflow_markers, "commit allowance"))

    external_lookup_markers = [
        "Use external web/Context7/public-project lookup only when the current user, task, or project contract allows source lookup",
        "never send secrets or sensitive context",
        "External public-project lookup is allowed only when the current user request, task packet, or project contract allows source lookup",
        "Never send secrets, private data, proprietary code, or sensitive repository context to external search",
    ]
    errors.extend(require_text_markers(".agents/skills/aili-delivery-flow/references/lifecycle.md", external_lookup_markers[:2], "research-first external lookup gate"))
    errors.extend(require_text_markers(".agents/skills/mature-project-pattern-research/SKILL.md", external_lookup_markers[2:], "mature-project external lookup gate"))
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
        "commands/build.md": [
            "inspect target repo branch/status",
            "classify dirty paths as task-scoped, unrelated/pre-existing, generated/ignored, scratch, or unknown",
            "propose cleanup for residue",
            "ask explicit approval before push, destructive clean/reset, branch deletion, worktree removal, OpenSpec archive, stashing unrelated changes, or deleting user-visible artifacts",
            "Savepoint commits may be proactive only when current task/project rules explicitly allow task-scoped verified commits; otherwise ask once with the cleanup package",
        ],
        "commands/ship.md": [
            "inspect target repo branch/status",
            "classify dirty paths as task-scoped, unrelated/pre-existing, generated/ignored, scratch, or unknown",
            "propose cleanup for residue",
            "ask explicit approval before push, destructive clean/reset, branch deletion, worktree removal, OpenSpec archive, stashing unrelated changes, or deleting user-visible artifacts",
            "Savepoint commits may be proactive only when current task/project rules explicitly allow task-scoped verified commits; otherwise ask once with the cleanup package",
        ],
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
    errors.extend(validate_local_review_gate_contracts())
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
