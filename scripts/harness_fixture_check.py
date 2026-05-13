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
            "code-reviewer",
            "test-engineer",
            "security-auditor",
            "release-readiness",
            "non-trigger",
        ],
        "case_key": "cases",
        "min_cases": 6,
    },
    "skill-routing-fixtures.yaml": {
        "markers": ["aili-delivery-flow", "harness-issue-triage", "harness-evolution", "trigger", "non-trigger"],
        "case_key": "cases",
        "min_cases": 6,
    },
    "subagent-dispatch-fixtures.yaml": {
        "markers": ["trace_id", "work_package_type", "artifact_target", "coverage_expectation", "known_exclusions", "evidence_anchors"],
        "case_key": "packet_cases",
        "min_cases": 1,
    },
    "verification-claim-fixtures.yaml": {
        "markers": ["sufficient-evidence", "insufficient-evidence", "Unverified"],
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
                ["code-reviewer", "test-engineer", "release-readiness"],
                name,
                "SHIP",
            )
        )
        errors.extend(require_checks(ship_case, "expected_conditional_checks", ["security-auditor"], name, "SHIP"))

    for internal_command in ["/research", "/review"]:
        matching = [case for case in cases if isinstance(case, dict) and case.get("input", "").startswith(internal_command)]
        if not matching:
            errors.append(f"{name}: missing non-trigger case for {internal_command}")
        elif any(case.get("trigger") is not False for case in matching):
            errors.append(f"{name}: {internal_command} must remain a non-trigger")

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


def main() -> int:
    errors: list[str] = []
    for name, spec in REQUIRED.items():
        errors.extend(validate_fixture(name, spec))
    errors.extend(validate_agent_permissions())

    if errors:
        print("harness fixture check: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"harness fixture check: PASS ({len(REQUIRED)} fixture files)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
