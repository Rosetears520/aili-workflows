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
            "## Evidence-driven claim hygiene",
            "Conversation may use localized `KNOWN`, `COMPUTED`, `INFERRED`, `UNVERIFIED`, and `OPEN QUESTION` labels",
            "Do not mark every sentence.",
            "Agent-internal packets keep `claim_status`, `source_kind`, `source_ref`, `decision_status`, `authorization_status`, `verification_status`, and confidence distinct.",
            "Human-facing artifacts use ordinary prose rather than opaque runtime metadata.",
            "Acceptance of a specification or test plan is not BUILD authorization.",
            "A command result is not acceptance.",
            "an accepted test plan is not BUILD authorization; passing a command is not user acceptance",
        )
        for marker in required:
            with self.subTest(marker=marker):
                self.assertIn(marker, contract)

        forbidden = (
            "TAG every claim",
            "`verification_status: not-run | partial | passed | failed | stale`",
            "final test-plan acceptance does not itself start BUILD",
            "a passing command or test does not establish user acceptance",
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
        local_review_command = read("commands/local-review.md")
        human_report_skills = (
            ".agents/skills/academic-paper-review/SKILL.md",
            ".agents/skills/systematic-literature-review/SKILL.md",
            ".agents/skills/consulting-analysis/SKILL.md",
            ".agents/skills/data-analysis/SKILL.md",
        )

        self.assertNotIn("tag every claim in stress-test conclusions", stress)
        self.assertIn("Persisted human-facing reports use ordinary prose", stress)
        self.assertNotIn("CONFIDENCE:", local_review_command)
        self.assertNotIn("confidence are recorded", local_review_command)
        self.assertIn("evidence limits recorded", local_review_command)
        for relative in human_report_skills:
            with self.subTest(relative=relative):
                text = read(relative)
                self.assertNotIn("CONFIDENCE:", text)
                self.assertIn("EVIDENCE LIMITS:", text)

    def test_contract_keeps_acceptance_and_authorization_independent(self) -> None:
        contract = read("templates/opencode-global-AGENTS.md")
        self.assertIn(
            "Acceptance of a specification or test plan is not BUILD authorization.",
            contract,
        )
        self.assertIn(
            "an Agent judgment does not replace required user confirmation",
            contract,
        )

    def test_global_contract_owns_action_first_and_state_anchoring(self) -> None:
        contract = read("templates/opencode-global-AGENTS.md")
        normalized_contract = " ".join(contract.split())

        required = (
            "## Communication and state anchoring",
            "Lead with the answer, decision, blocker, path, command, or next action.",
            "For multi-step work, use the smallest numbered sequence with one bounded action per item.",
            "End an incomplete result with one concrete next action.",
            "Use estimates only when requested and defensible.",
            "Make errors matter-of-fact",
            "keep the first action obvious",
            "failure, cause, fix, and verification",
            "### 3. Simplicity First",
            "Use the simplest viable design.",
            "### 4. Task-Scoped Changes",
            "Touch only lines traceable to the active request",
            "### 5. Goal-Driven Verification",
            "Prefer observable behavior, contract, type, schema, and public-output checks",
        )
        for marker in required:
            with self.subTest(marker=marker):
                self.assertIn(marker, normalized_contract)

        forbidden = (
            "disable-model-invocation",
            "### Communication and State Anchoring",
            "The reader has ADHD. Output is not just brief.",
            "Forbidden openers include \"Great question,\"",
            "Ship minimal production code that fixes the owning boundary",
            "Do not run bundle or build",
            "Skip shims and backward compatibility unless",
        )
        for marker in forbidden:
            with self.subTest(marker=marker):
                self.assertNotIn(marker, normalized_contract)


if __name__ == "__main__":
    unittest.main()
