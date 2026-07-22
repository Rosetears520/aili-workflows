#!/usr/bin/env python3
"""Validate that capability assignments cover the installed Skill manifest exactly once."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COMPONENTS = ROOT / "manifests" / "rose-aili.components.json"
CAPABILITIES = ROOT / "manifests" / "skill-capabilities.json"


def main() -> int:
    components = json.loads(COMPONENTS.read_text(encoding="utf-8"))
    capabilities = json.loads(CAPABILITIES.read_text(encoding="utf-8"))
    expected = {item["name"] for item in components["components"]["skills"]}
    profiles = capabilities.get("profiles", {})
    assigned: list[str] = []

    if capabilities.get("canonicalSkillRoot") != ".agents/skills":
        raise SystemExit("FAIL: canonicalSkillRoot must be .agents/skills")
    for profile_name, profile in profiles.items():
        if not isinstance(profile, dict) or not all(
            key in profile for key in ("requiredCapabilities", "optionalCapabilities", "sideEffectClass", "missingBehavior")
        ):
            raise SystemExit(f"FAIL: incomplete capability profile: {profile_name}")

    for assignment in capabilities.get("assignments", []):
        profile = assignment.get("profile")
        if profile not in profiles:
            raise SystemExit(f"FAIL: unknown capability profile: {profile}")
        skills = assignment.get("skills")
        if not isinstance(skills, list) or not all(isinstance(skill, str) for skill in skills):
            raise SystemExit(f"FAIL: invalid skills list for profile: {profile}")
        assigned.extend(skills)

    duplicates = sorted({name for name in assigned if assigned.count(name) > 1})
    missing = sorted(expected - set(assigned))
    unknown = sorted(set(assigned) - expected)
    missing_paths = sorted(
        item["path"] for item in components["components"]["skills"]
        if not (ROOT / item["path"] / "SKILL.md").is_file()
    )
    legacy_compatibility = sorted(
        str(ROOT / item["path"] / "SKILL.md")
        for item in components["components"]["skills"]
        if (ROOT / item["path"] / "SKILL.md").is_file()
        and "compatibility: opencode" in (ROOT / item["path"] / "SKILL.md").read_text(encoding="utf-8")
    )
    if duplicates or missing or unknown or missing_paths or legacy_compatibility:
        for label, values in (
            ("duplicate", duplicates),
            ("missing", missing),
            ("unknown", unknown),
            ("missing SKILL.md", missing_paths),
            ("legacy OpenCode-only compatibility metadata", legacy_compatibility),
        ):
            if values:
                print(f"FAIL: {label}: {', '.join(values)}")
        return 1

    print(f"PASS: {len(expected)} installed skills have exactly one capability profile")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
