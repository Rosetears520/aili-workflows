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

    def test_i_have_adhd_is_current_response_only_and_safety_first(self) -> None:
        skill = read(".agents/skills/i-have-adhd/SKILL.md")
        normalized_skill = " ".join(skill.split())

        required = (
            "Positive trigger",
            "Near misses",
            "shape only the current response",
            "failure → cause → fix → verification",
            "Correctness, complete required findings, evidence, uncertainty, safety gates",
            "Do not invent duration estimates",
            "Do not omit required blockers, safety findings, or requested items",
            "no flag file, Hook, plugin, service, global-rule projection, or",
            "does not claim survival across later turns",
        )
        for marker in required:
            with self.subTest(marker=marker):
                self.assertIn(marker, normalized_skill)

        forbidden = (
            "disable-model-invocation",
            "These rules apply to every response for the rest of the session",
            "Turn them off only when",
            "Give specific time estimates",
            "Cap lists at 5 items",
        )
        for marker in forbidden:
            with self.subTest(marker=marker):
                self.assertNotIn(marker, normalized_skill)


if __name__ == "__main__":
    unittest.main()
