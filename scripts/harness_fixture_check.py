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
            "non-trigger",
        ],
        "case_key": "cases",
        "min_cases": 6,
    },
    "skill-routing-fixtures.yaml": {
        "markers": ["aili-delivery-flow", "harness-issue-triage", "harness-evolution", "mature-project-pattern-research", "trigger", "non-trigger"],
        "case_key": "cases",
        "min_cases": 6,
    },
    "subagent-dispatch-fixtures.yaml": {
        "markers": ["trace_id", "work_package_type", "artifact_target", "coverage_expectation", "known_exclusions", "evidence_anchors", "package-queue", "implementer", "allowed_scope", "forbidden_scope", "edit_permission", "commit_allowance"],
        "case_key": "packet_cases",
        "min_cases": 2,
    },
    "verification-claim-fixtures.yaml": {
        "markers": ["sufficient-evidence", "insufficient-evidence", "Unverified", "release-blocking"],
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

    define_case = find_trigger_case(cases, "DEFINE")
    if define_case is None:
        errors.append(f"{name}: missing trigger case for DEFINE")
    else:
        if define_case.get("expected_scope") != "artifact-fan-out":
            errors.append(f"{name}: DEFINE expected_scope must be 'artifact-fan-out'")
        errors.extend(require_checks(define_case, "expected_artifacts", ["interview.md", "test-plan.md"], name, "DEFINE"))
        errors.extend(
            require_checks(
                define_case,
                "expected_skills",
                ["change-interviewer", "test-document-generator"],
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
    errors.extend(require_checks(packet, "required_evidence", ["evidence_anchors", "verification", "changed_files", "scope_boundary"], name, "packet-build-goal-mode"))

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
        "change-interviewer",
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
        "skills/aili-delivery-flow/SKILL.md": [
            "change-interviewer",
            "test-document-generator",
            "Unverified",
        ],
        "skills/aili-delivery-flow/references/lifecycle.md": [
            "change-interviewer",
            "test-document-generator",
            "READY",
            "BLOCKED",
            "WAIVED",
            "UNVERIFIED",
            "Change Revision Decision",
        ],
        "skills/aili-delivery-flow/references/backend-routing.md": [
            "interview.md",
            "test-plan.md",
            "change-interviewer",
            "test-document-generator",
            "asks once",
        ],
        "skills/aili-delivery-flow/references/artifact-contracts.md": [
            "interview.md",
            "test-plan.md",
            "change-interviewer",
            "test-document-generator",
            "BUILD Readiness",
        ],
        "skills/aili-delivery-flow/references/questionnaire-policy.md": [
            "Artifact Freshness Gate",
            "Conversation context is stale",
            "disk wins",
            "interview.md",
            "change-interviewer",
        ],
        "skills/aili-delivery-flow/references/test-document-policy.md": [
            "Artifact Freshness Gate",
            "Conversation context is stale",
            "disk wins",
            "test-plan.md",
            "test-document-generator",
        ],
        "docs/harness/backend-adapters.md": [
            "change-interviewer",
            "test-document-generator",
            "interview.md",
            "test-plan.md",
            "UNVERIFIED",
        ],
        "docs/harness/command-lifecycle.md": [
            "change-interviewer",
            "test-document-generator",
            "required behavior",
            "output contract",
        ],
        "docs/harness/aili-harness-contract.md": [
            "change-interviewer",
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
        "skills/aili-delivery-flow/SKILL.md": [
            "references/build-goal-mode.md",
            "resolved ready target",
            "synthesize a package queue",
        ],
        "skills/aili-delivery-flow/references/lifecycle.md": [
            "autonomous goal mode",
            "synthesize an ordered implementation package queue",
            "current active contract",
            "allowed external directories",
        ],
        "skills/aili-delivery-flow/references/backend-routing.md": [
            "autonomous package queue synthesis",
            "canonicalizes the target repository root",
            "allowed external directories",
        ],
        "skills/aili-delivery-flow/references/implementation-packages.md": [
            "synthesize an ordered package queue",
            "scoped subagent packet",
            "missing manual package text is not a stop condition",
        ],
        "skills/aili-delivery-flow/references/build-goal-mode.md": [
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


def main() -> int:
    errors: list[str] = []
    for name, spec in REQUIRED.items():
        errors.extend(validate_fixture(name, spec))
    errors.extend(validate_agent_permissions())
    errors.extend(validate_command_contracts())
    errors.extend(validate_define_artifact_contracts())
    errors.extend(validate_build_goal_mode_contracts())

    if errors:
        print("harness fixture check: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"harness fixture check: PASS ({len(REQUIRED)} fixture files + command contracts)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
