#!/usr/bin/env python3
"""Zero-dependency structure/content check for delegation protocol harness files."""

from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "agents/rose.md",
    "agents/code-scout.md",
    "skills/parallel-subagent-dispatch/SKILL.md",
    "skills/repo-evidence-first/SKILL.md",
    "skills/session-handoff/SKILL.md",
    "skills/aili-delivery-flow/references/direct-vs-delegated-work.md",
    "skills/aili-delivery-flow/references/protocols/subagent-task-packet.md",
    "skills/aili-delivery-flow/references/protocols/subagent-result.md",
]

CONTENT_CHECKS = {
    "agents/rose.md": [
        "Delegation Protocol Router",
        "direct-vs-delegated-work.md",
        "repo-evidence-first",
        "session-handoff",
        "subagent-task-packet.md",
        "subagent-result.md",
    ],
    "agents/code-scout.md": [
        "CODE LOCALITY MAP",
        "Upstream callers/entrypoints",
        "Downstream consumers/outputs",
        "Peer patterns",
        "Freshness",
        "CONCLUSION",
    ],
    "skills/parallel-subagent-dispatch/SKILL.md": [
        "Mandatory Dispatch Rule",
        "3+ relevant files",
        "2+ directories/subsystems",
        "2+ search passes",
        "subagent-task-packet.md",
        "subagent-result.md",
    ],
    "skills/repo-evidence-first/SKILL.md": [
        "REPO EVIDENCE STATUS",
        "Grounded Fact",
        "Hypothesis",
        "Open Question",
        "Unverified",
        "Blocked",
        "code-scout",
        "doc-researcher",
        "web-researcher",
        "test-engineer",
        "security-auditor",
    ],
    "skills/session-handoff/SKILL.md": [
        "只有用户明确要求",
        "openspec/changes/<change-id>/handoff.md",
        "## Goal",
        "## Active Contract",
        "## Lifecycle / Backend",
        "## Scope Boundary",
        "## Touched Files / Artifacts",
        "## Evidence Anchors",
        "## Subagent Activity",
        "## Decisions Made",
        "## Open Questions",
        "## Risks / Unknowns",
        "## Verification State",
        "## Blocker / Stop Reason",
        "## Next Action",
        "## Suggested Next-Session Prompt",
        "MUST NOT",
        "secrets",
        "durable memory",
    ],
    "skills/aili-delivery-flow/references/direct-vs-delegated-work.md": [
        "Direct allowlist",
        "Mandatory delegation triggers",
        "3+ relevant files",
        "2+ directories/subsystems",
        "2+ search passes",
        "context savings",
    ],
    "skills/aili-delivery-flow/references/protocols/subagent-task-packet.md": [
        "- Goal:",
        "- Context:",
        "- Allowed scope:",
        "- Forbidden scope:",
        "- Edit permission:",
        "- Evidence required:",
        "- Expected return format:",
        "- Placement / artifact rules:",
        "- Coverage expectations:",
        "- Known exclusions:",
        "- Stop conditions:",
    ],
    "skills/aili-delivery-flow/references/protocols/subagent-result.md": [
        "CONFIDENCE",
        "INSPECTED SCOPE",
        "OBSERVED FACTS",
        "freshness",
        "INFERENCES",
        "RECOMMENDATIONS",
        "UNKNOWNS / GAPS",
        "MAINAGENT NEXT READS",
        "VERIFICATION EVIDENCE",
        "STOP CONDITIONS HIT",
        "not authority",
    ],
}

FORBIDDEN_CODE_SCOUT_BASH = [
    '"git grep*": allow',
    '"rg*": allow',
    '"grep*": allow',
    '"find*": allow',
    '"ls*": allow',
]

CANONICAL_PROTOCOL_PATH = "skills/aili-delivery-flow/references/protocols/"


def main() -> int:
    failures: list[str] = []

    for relative_path in REQUIRED_FILES:
        path = ROOT / relative_path
        if not path.is_file():
            failures.append(f"MISSING FILE: {relative_path}")
            continue

        text = path.read_text(encoding="utf-8")
        for needle in CONTENT_CHECKS.get(relative_path, []):
            if needle not in text:
                failures.append(f"MISSING CONTENT: {relative_path} :: {needle}")

    code_scout_text = (ROOT / "agents/code-scout.md").read_text(encoding="utf-8")
    for forbidden in FORBIDDEN_CODE_SCOUT_BASH:
        if forbidden in code_scout_text:
            failures.append(f"UNSAFE CODE-SCOUT BASH PERMISSION: {forbidden}")

    top_level_protocols = ROOT / "protocols"
    if top_level_protocols.exists():
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
    print(f"Checked {len(REQUIRED_FILES)} files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
