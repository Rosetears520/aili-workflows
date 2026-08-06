from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


class OutputSurfaceContractTests(unittest.TestCase):
    def test_global_contract_scopes_labels_by_natural_language_surface(self) -> None:
        contract = read("templates/opencode-global-AGENTS.md")

        required = (
            "`conversation`",
            "`agent-internal`",
            "`human-artifact`",
            "Do not tag every sentence or bullet",
            "Simple answers may use no labels",
            "Source code,\nconfiguration, schemas, manifests, lockfiles, machine-readable JSON/YAML",
            "When a\nnatural-language destination is ambiguous, treat it as `human-artifact`",
            "`claim_status: observed | inferred | unverified`",
            "`source_kind: user-message | repository | command | external`",
            "`decision_status: proposed | conditional | accepted | rejected`",
            "`authorization_status: absent | granted | expired | revoked`",
            "`verification_status: not-run | partial | passed | failed | stale`",
            "final test-plan acceptance does not itself start BUILD",
            "a passing command or test does not establish user acceptance",
        )
        for marker in required:
            with self.subTest(marker=marker):
                self.assertIn(marker, contract)

        forbidden = (
            "TAG every claim",
            "For sourced claims in documents, reports, handoffs, and formal artifacts",
            "User-facing conclusions, recommendations, readiness/completion",
        )
        for marker in forbidden:
            with self.subTest(marker=marker):
                self.assertNotIn(marker, contract)

    def test_human_artifact_owners_do_not_require_display_metadata(self) -> None:
        artifact_contracts = read(
            ".agents/skills/aili-delivery-flow/references/artifact-contracts.md"
        )
        self.assertNotIn("[KNOWN]", artifact_contracts)
        self.assertIn(
            "Persisted natural-language artifacts are human-facing by default",
            artifact_contracts,
        )

        stress = read(".agents/skills/strategy-stress-test/SKILL.md")
        retrospective = read(".agents/skills/evidence-scoped-retrospective/SKILL.md")
        local_review = read(".agents/skills/local-review-gate/SKILL.md")
        local_review_command = read("commands/local-review.md")
        human_report_skills = (
            ".agents/skills/academic-paper-review/SKILL.md",
            ".agents/skills/systematic-literature-review/SKILL.md",
            ".agents/skills/consulting-analysis/SKILL.md",
            ".agents/skills/data-analysis/SKILL.md",
        )

        self.assertNotIn("tag every claim in stress-test conclusions", stress)
        self.assertIn("Persisted human-facing reports use ordinary prose", stress)
        self.assertIn("Persisted human-facing reports state evidence limits", retrospective)
        self.assertNotIn("CONFIDENCE:", local_review)
        self.assertNotIn("confidence are recorded", local_review)
        self.assertIn("evidence limits recorded", local_review_command)
        for relative in human_report_skills:
            with self.subTest(relative=relative):
                text = read(relative)
                self.assertNotIn("CONFIDENCE:", text)
                self.assertIn("EVIDENCE LIMITS:", text)

    def test_contract_keeps_acceptance_and_authorization_independent(self) -> None:
        contract = read("templates/opencode-global-AGENTS.md")
        self.assertIn(
            "decision acceptance does not grant implementation or operation authorization",
            contract,
        )
        self.assertIn(
            "Agent judgment that a condition is met does not replace required user confirmation",
            contract,
        )

    def test_global_contract_owns_action_first_and_state_anchoring(self) -> None:
        contract = read("templates/opencode-global-AGENTS.md")
        normalized_contract = " ".join(contract.split())

        required = (
            "### Communication and State Anchoring",
            "The reader has ADHD. Output is not just brief. It is shaped so an ADHD brain can act on it.",
            "Working memory is small. Anything not on screen is forgotten",
            "Knowing the answer is not doing the answer",
            "Starting is the hardest step",
            "Time estimates feel uniform",
            "Dopamine is scarce. Visible progress matters",
            "Lead with the answer, result, decision, blocker, path, command, or next required action",
            "If the answer is a command, path, or snippet, it goes first",
            "If the work takes more than one step, write a numbered list",
            "If anything is left open, name one concrete next action",
            "The checklist does the restating; do not also narrate the full plan as prose",
            "Make completed work visible",
            "failure, cause, fix, and verification",
            "Forbidden openers include \"Great question,\"",
            "Forbidden closers include \"Let me know if you need anything else,\"",
            "Do not invent duration estimates",
            "Do not cap lists at an arbitrary number",
            "If the last three attempts have been \"still broken,\" stop iterating on code",
            "If a rule fights the task, the task wins and the shape stays",
            "If a rule fights the harness, the system and harness constraints win and the shape stays",
            "Delete the first sentence if it only announces what you are about to do",
            "Remove hedging that adds no information, but keep uncertainty that changes the claim",
            "Choose the simplest implementation that fully meets the current requirements",
            "Grow the system in layers",
            "Do not assume a library lacks a capability without checking its documentation and types",
            "Do not read source files and regex implementation text",
        )
        for marker in required:
            with self.subTest(marker=marker):
                self.assertIn(marker, normalized_contract)

        forbidden = (
            "disable-model-invocation",
            "These rules apply to every response for the rest of the session",
            "Turn them off only when",
            "stop adhd mode",
            "Give specific time estimates",
            "Cap lists at 5 items",
            "@quartz/plugins/transformers",
            "dev.ts",
            "window.addCleanup",
            "Cloudflare Secrets",
            "Use `pnpm`, `oxlint`, `oxfmt`, and `tsgo`",
            "Do not write comments",
            "Ship minimal production code that fixes the owning boundary",
            "Do not run bundle or build",
            "Skip shims and backward compatibility unless aarnphm asks",
        )
        for marker in forbidden:
            with self.subTest(marker=marker):
                self.assertNotIn(marker, normalized_contract)


if __name__ == "__main__":
    unittest.main()
