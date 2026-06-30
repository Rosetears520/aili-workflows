#!/usr/bin/env python3
"""Static smoke validation for AILI harness fixtures.

Uses JSON syntax in .yaml files so validation stays Python-stdlib only.
"""

from __future__ import annotations

import json
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
            "code-scout",
            "implementer",
            "code-reviewer",
            "test-engineer",
            "security-auditor",
            "goal-mode",
            "package-queue",
            "external-repo-root",
            "release-readiness",
            "release-blocker-audit",
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

    ideate_case = find_trigger_case(cases, "IDEATE")
    if ideate_case is None:
        errors.append(f"{name}: missing trigger case for IDEATE")
    else:
        if ideate_case.get("expected_scope") != "evidence-scouting":
            errors.append(f"{name}: IDEATE expected_scope must be 'evidence-scouting'")
        errors.extend(require_checks(ideate_case, "expected_delegation", ["code-scout"], name, "IDEATE"))

    build_case = find_trigger_case(cases, "BUILD")
    if build_case is None:
        errors.append(f"{name}: missing trigger case for BUILD")
    else:
        if build_case.get("expected_scope") != "implementation-quality":
            errors.append(f"{name}: BUILD expected_scope must be 'implementation-quality'")
        errors.extend(require_checks(build_case, "expected_checks", ["code-reviewer", "test-engineer"], name, "BUILD"))
        errors.extend(require_checks(build_case, "expected_conditional_checks", ["security-auditor"], name, "BUILD"))
        build_checks = build_case.get("expected_checks", []) + build_case.get("expected_conditional_checks", [])
        if "release-readiness" in build_checks:
            errors.append(f"{name}: BUILD must not include release-readiness in any expected check list")
        goal_cases = [
            case
            for case in cases
            if isinstance(case, dict)
            and case.get("expected_mode") == "BUILD"
            and case.get("trigger") is True
            and case.get("expected_execution") == "goal-mode"
        ]
        if not goal_cases:
            errors.append(f"{name}: missing BUILD goal-mode trigger case")
        else:
            goal_case = goal_cases[0]
            if goal_case.get("expected_package_source") != "package-queue":
                errors.append(f"{name}: BUILD goal-mode expected_package_source must be 'package-queue'")
            if goal_case.get("target_repo_root") != "infer-canonical-from-backend-context":
                errors.append(f"{name}: BUILD goal-mode target_repo_root must infer canonical root from backend context")
            if goal_case.get("cwd_authority") is not False:
                errors.append(f"{name}: BUILD goal-mode cwd_authority must be false")
            errors.extend(require_checks(goal_case, "queue_inputs", ["tasks.md", "specs", "design", "test-plan.md", "repository-evidence"], name, "BUILD goal-mode"))
            errors.extend(require_checks(goal_case, "expected_delegation", ["implementer"], name, "BUILD goal-mode"))
            errors.extend(require_checks(goal_case, "expected_checks", ["code-reviewer", "test-engineer"], name, "BUILD goal-mode"))
            errors.extend(require_checks(goal_case, "expected_conditional_checks", ["security-auditor"], name, "BUILD goal-mode"))
            errors.extend(
                require_checks(
                    goal_case,
                    "parallelism_analysis",
                    [
                        "shared scaffold/source-of-truth work",
                        "safe parallel lanes",
                        "serial dependencies",
                        "concurrent research/review/test/search lanes",
                        "ownership boundaries",
                        "join points",
                        "blockers",
                        "no-parallel reason",
                    ],
                    name,
                    "BUILD goal-mode",
                )
            )
            errors.extend(
                require_checks(
                    goal_case,
                    "lane_preservation_reasons",
                    ["dependency", "ownership", "verification", "safety", "user-scope"],
                    name,
                    "BUILD goal-mode",
                )
            )
            errors.extend(
                require_checks(
                    goal_case,
                    "research_first_gate",
                    [
                        "official/API docs",
                        "prior-art",
                        "fast-changing",
                        "platform/runtime",
                        "security/permissions",
                        "external integrations",
                        "UI/animation/product-form",
                        "model uncertainty",
                        "user-requested research",
                        "industry/GitHub similar projects",
                    ],
                    name,
                    "BUILD goal-mode",
                )
            )
            errors.extend(require_checks(goal_case, "plan_approval_gate", ["evidence-backed 方案", "approval", "waiver", "UNVERIFIED before implementation"], name, "BUILD goal-mode"))
            errors.extend(
                require_checks(
                    goal_case,
                    "packaging_flow",
                    [
                        "confirm target/platform",
                        "test first",
                        "repair failures",
                        "package",
                        "classify package-time failures",
                        "repair/retest/repackage",
                        "artifact path or blocker",
                    ],
                    name,
                    "BUILD goal-mode",
                )
            )
            errors.extend(
                require_checks(
                    goal_case,
                    "high_risk_packaging_stop",
                    [
                        "signing",
                        "notarization",
                        "platform certificates",
                        "dependency or lockfile changes",
                        "external publishing",
                        "destructive cleanup",
                        "secret handling",
                        "unsupported platform assumptions",
                    ],
                    name,
                    "BUILD goal-mode",
                )
            )
            errors.extend(
                require_checks(
                    goal_case,
                    "stop_conditions",
                    [
                        "ambiguous-target",
                        "missing-readiness",
                        "external-repo-root",
                        "high-risk-gate",
                        "scope-expansion",
                        "unverifiable-acceptance",
                        "unavailable-review-lane",
                        "repair-limit",
                    ],
                    name,
                    "BUILD goal-mode",
                )
            )
            errors.extend(require_checks(goal_case, "non_stop_conditions", ["missing-manual-package"], name, "BUILD goal-mode"))
            errors.extend(require_checks(goal_case, "implementation_objective", ["complete, appropriately scoped, verified", "accepted scope", "not artificially tiny"], name, "BUILD goal-mode"))
            errors.extend(require_checks(goal_case, "verification_order", ["most relevant focused verification"], name, "BUILD goal-mode"))
            errors.extend(
                require_checks(
                    goal_case,
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
                    "BUILD goal-mode",
                )
            )

    ordinary_multiunit = [
        case
        for case in cases
        if isinstance(case, dict) and case.get("id") == "ordinary-chat-multiunit-planning"
    ]
    if not ordinary_multiunit:
        errors.append(f"{name}: missing ordinary-chat-multiunit-planning case")
    else:
        if ordinary_multiunit[0].get("trigger") is not True:
            errors.append(f"{name}: ordinary-chat-multiunit-planning must trigger proactive planning")
        errors.extend(
            require_checks(
                ordinary_multiunit[0],
                "expected_parallelism_analysis",
                ["parallelism analysis", "join completeness", "package/lane preservation", "no-parallel reason"],
                name,
                "ordinary-chat-multiunit-planning",
            )
        )

    define_case = find_trigger_case(cases, "DEFINE")
    if define_case is None:
        errors.append(f"{name}: missing trigger case for DEFINE")
    else:
        if define_case.get("expected_scope") != "artifact-fan-out":
            errors.append(f"{name}: DEFINE expected_scope must be 'artifact-fan-out'")
        errors.extend(require_checks(define_case, "expected_artifacts", ["interview.md", "test-plan.md"], name, "DEFINE"))
        errors.extend(require_checks(define_case, "expected_forbidden_artifacts", ["grill.md", "requirements-grilling.md"], name, "DEFINE"))
        errors.extend(
            require_checks(
                define_case,
                "expected_skills",
                ["requirements-grilling", "test-document-generator"],
                name,
                "DEFINE",
            )
        )
        errors.extend(
            require_checks(
                define_case,
                "expected_readiness",
                ["READY", "BLOCKED", "WAIVED", "UNVERIFIED"],
                name,
                "DEFINE",
            )
        )

    ship_case = find_trigger_case(cases, "SHIP")
    if ship_case is None:
        errors.append(f"{name}: missing trigger case for SHIP")
    else:
        if ship_case.get("expected_scope") != "release-readiness":
            errors.append(f"{name}: SHIP expected_scope must be 'release-readiness'")
        errors.extend(
            require_checks(
                ship_case,
                "expected_checks",
                ["code-reviewer", "test-engineer", "release-readiness", "release-blocker-audit"],
                name,
                "SHIP",
            )
        )
        errors.extend(require_checks(ship_case, "expected_conditional_checks", ["security-auditor"], name, "SHIP"))

    for internal_command in ["/research", "/review", "/release-blocker-audit"]:
        matching = [case for case in cases if isinstance(case, dict) and case.get("input", "").startswith(internal_command)]
        if not matching:
            errors.append(f"{name}: missing non-trigger case for {internal_command}")
        elif any(case.get("trigger") is not False for case in matching):
            errors.append(f"{name}: {internal_command} must remain a non-trigger")

    release_blocker_cases = [
        case
        for case in cases
        if isinstance(case, dict) and case.get("expected_mode") == "SHIP" and case.get("trigger") is True
    ]
    if release_blocker_cases:
        ship_case = release_blocker_cases[0]
        errors.extend(require_checks(ship_case, "expected_checks", ["release-blocker-audit"], name, "SHIP release-blocker audit"))

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
    goal_packets = [case for case in cases if isinstance(case, dict) and case.get("id") == "packet-build-goal-mode"]
    if not goal_packets:
        return [f"{name}: missing packet-build-goal-mode case"]

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
            errors.append(f"{name}: packet-build-goal-mode {field} must be {expected!r}")
    errors.extend(require_checks(packet, "forbidden_scope", ["out-of-scope packages", "high-risk gates without approval"], name, "packet-build-goal-mode"))
    errors.extend(require_checks(packet, "parallelism_analysis", ["parallelism analysis", "no-parallel reason", "join completeness", "package/lane preservation"], name, "packet-build-goal-mode"))
    errors.extend(require_checks(packet, "join_contract", ["join points", "blockers", "expected evidence"], name, "packet-build-goal-mode"))
    errors.extend(require_checks(packet, "required_evidence", ["evidence_anchors", "verification", "changed_files", "scope_boundary"], name, "packet-build-goal-mode"))
    errors.extend(require_checks(packet, "implementation_objective", ["complete, appropriately scoped, verified", "complete task-scoped", "not artificially tiny"], name, "packet-build-goal-mode"))
    errors.extend(require_checks(packet, "verification_order", ["most relevant focused verification"], name, "packet-build-goal-mode"))
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
            "packet-build-goal-mode",
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
        if path.name == "rose.md":
            if "\n  skill: allow\n" not in frontmatter and "\n  \"*\": allow\n" not in frontmatter:
                errors.append(f"{path.relative_to(ROOT)}: missing skill allowance via permission.skill or wildcard")
        elif "\n  skill: allow\n" not in frontmatter:
            errors.append(f"{path.relative_to(ROOT)}: missing permission.skill allow")
        if "\n  read:\n" not in frontmatter:
            errors.append(f"{path.relative_to(ROOT)}: missing permission.read block")
        elif "\n    \"*\": allow\n" not in frontmatter:
            errors.append(f"{path.relative_to(ROOT)}: missing permission.read wildcard allow")
    return errors


def read_repo_text(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def validate_command_contracts() -> list[str]:
    errors: list[str] = []
    command_dir = ROOT / "commands"
    allowed_delivery_commands = {"ideate.md", "define.md", "build.md", "ship.md"}
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
    unexpected_commands = sorted(existing_commands - allowed_delivery_commands)
    for name in unexpected_commands:
        errors.append(f"commands/{name}: unexpected top-level delivery command; only ideate, define, build, and ship are allowed")

    unexpected_internal = sorted(existing_commands & internal_delivery_commands)
    for name in unexpected_internal:
        errors.append(f"commands/{name}: internal lifecycle stage must not be a top-level delivery command")

    missing = sorted(allowed_delivery_commands - existing_commands)
    for name in missing:
        errors.append(f"commands/{name}: missing public delivery command")

    for name in sorted(allowed_delivery_commands & existing_commands):
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
        for marker in ["User input:", "Required behavior:", "Hard stops:", "Output contract:", "aili-delivery-flow"]:
            if marker not in text:
                errors.append(f"{relative}: missing command contract marker {marker!r}")

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


def validate_build_goal_mode_contracts() -> list[str]:
    errors: list[str] = []
    required_markers = {
        "commands/build.md": [
            "autonomous goal mode",
            "implementation package queue",
            "target repository root",
            "allowed external directories",
            "Do not ask for manual package approval",
        ],
        ".agents/skills/aili-delivery-flow/SKILL.md": [
            "references/build-goal-mode.md",
            "resolved ready target",
            "synthesize a package queue",
        ],
        ".agents/skills/aili-delivery-flow/references/lifecycle.md": [
            "autonomous goal mode",
            "synthesize an ordered implementation package queue",
            "current active contract",
            "allowed external directories",
        ],
        ".agents/skills/aili-delivery-flow/references/backend-routing.md": [
            "autonomous package queue synthesis",
            "canonicalizes the target repository root",
            "allowed external directories",
        ],
        ".agents/skills/aili-delivery-flow/references/implementation-packages.md": [
            "synthesize an ordered package queue",
            "scoped subagent packet",
            "missing manual package text is not a stop condition",
        ],
        ".agents/skills/aili-delivery-flow/references/build-goal-mode.md": [
            "BUILD goal mode",
            "Target and Repository Root Resolution",
            "Package Queue Synthesis",
            "Execution Loop",
            "Stop Conditions",
            "allowed external directories",
        ],
        "docs/harness/command-lifecycle.md": ["goal mode", "package queue"],
        "docs/harness/aili-harness-contract.md": ["BUILD goal mode", "package queue"],
    }

    for relative, markers in required_markers.items():
        path = ROOT / relative
        if not path.exists():
            errors.append(f"{relative}: missing BUILD goal-mode contract file")
            continue
        text = path.read_text(encoding="utf-8")
        for marker in markers:
            if marker not in text:
                errors.append(f"{relative}: missing BUILD goal-mode marker {marker!r}")

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
        ".agents/skills/aili-delivery-flow/references/build-goal-mode.md": [
            "run the most relevant focused tests/checks first",
            "Run focused verification.",
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

    build_goal_text = read_repo_text(".agents/skills/aili-delivery-flow/references/build-goal-mode.md") if (ROOT / ".agents/skills/aili-delivery-flow/references/build-goal-mode.md").exists() else ""
    if "run the smallest relevant tests/checks first" in build_goal_text:
        errors.append(".agents/skills/aili-delivery-flow/references/build-goal-mode.md: packaging flow must use most relevant focused tests/checks wording")

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
        ".agents/skills/aili-delivery-flow/references/build-goal-mode.md": [
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
    errors.extend(validate_build_goal_mode_contracts())
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
