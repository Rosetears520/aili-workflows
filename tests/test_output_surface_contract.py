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
            "Match the label language to the response:",
            "`[KNOWN]` / `[已知]` for information already established",
            "`[VERIFIED]` / `[查证]` for information checked in the current task by reading files, searching, querying, or inspecting evidence",
            "`[INFERRED]` / `[推断]`",
            "`[UNVERIFIED]` / `[未验证]`",
            "`[OPEN QUESTION]` / `[待确认]`",
            "does not by itself prove runtime behavior or overall completion",
            "Do not mark every sentence.",
            "Agent-internal packets keep `claim_status`, `source_kind`, `source_ref`, `decision_status`, `authorization_status`, `verification_status`, and confidence distinct.",
            "Human-facing artifacts use ordinary prose rather than opaque runtime metadata.",
            "Acceptance of a specification or test plan is not BUILD authorization",
            "A command result is not acceptance.",
            "an accepted test plan is not BUILD authorization; passing a command is not user acceptance",
        )
        for marker in required:
            with self.subTest(marker=marker):
                self.assertIn(marker, contract)

        forbidden = (
            "TAG every claim",
            "COMPUTED",
            "计算结果",
            "计算所得",
            "`verification_status: not-run | partial | passed | failed | stale`",
            "final test-plan acceptance does not itself start BUILD",
            "a passing command or test does not establish user acceptance",
        )
        for marker in forbidden:
            with self.subTest(marker=marker):
                self.assertNotIn(marker, contract)

    def test_global_rules_are_self_contained_and_use_general_roles(self) -> None:
        for relative in (
            "generated/pi/AGENTS.md",
            "generated/opencode/AGENTS.md",
            "templates/opencode-global-AGENTS.md",
        ):
            contract = read(relative)
            with self.subTest(relative=relative):
                for marker in (
                    "The main agent understands the request",
                    "Decisions reserved for the user remain with the user.",
                    "A subagent performs its assigned task",
                    "Clear natural-language requests are valid",
                    "Invoking a command does not expand permissions",
                    "without a fixed default count",
                    "The main agent checks each subagent's result",
                    "The main agent reads and checks the report",
                    "If required file delivery is unavailable, report the blocker.",
                    "A subagent writing an authorized report rereads it",
                    "First resolve questions from available code, files, and documentation.",
                    "Group related questions the user can answer now",
                    "they do not authorize unrelated operations",
                ):
                    self.assertIn(marker, contract)
                for marker in (
                    "ROSE", "Worker", "`/ideate`", "`/eli5`",
                    "requirements-grilling", "Frontier Batch Mode",
                    "core/protocols/README.md",
                    "aili-delivery-flow/references/formal-task-board.md",
                    "Default concurrent specialist work is at most two",
                ):
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
        self.assertRegex(
            contract,
            r"Acceptance of a specification or test plan is not BUILD authorization[.;]",
        )
        self.assertIn(
            "an Agent judgment does not replace required user confirmation",
            contract,
        )

    def test_temporary_files_and_long_commands_have_separate_rules(self) -> None:
        for relative in (
            "core/governance/operating-discipline.md",
            "generated/pi/AGENTS.md",
            "generated/opencode/AGENTS.md",
            "templates/opencode-global-AGENTS.md",
        ):
            with self.subTest(relative=relative):
                text = read(relative)
                practical = text.split("## Practical engineering behavior\n", 1)[1].split("\n## ", 1)[0]
                temporary = text.split("## Temporary files\n", 1)[1].split("\n## ", 1)[0]
                self.assertIn("Write long commands or logically complex Bash or Python scripts", practical)
                self.assertIn("a script file in `.tmp/<task-name>/` before executing the file", practical)
                self.assertIn("If the runtime mandates a different temporary directory", practical)
                for marker in (
                    "debugging output, downloaded intermediate files, format-conversion files, and experimental data",
                    "`.tmp/<task-name>/`",
                    "artifacts the user needs to inspect or retain",
                    "production code and tests",
                    "secrets or credentials",
                    "system `/tmp/`, the user's home directory, `.agent/`, or `.agents/`",
                    "`scratch/` or `temp/`",
                    "If the runtime mandates a temporary directory",
                    "tool-managed cache, build, and dependency locations",
                    "`node_modules/` and `dist/`",
                    "Inspect existing `.tmp/` contents before writing",
                    "identify any temporary files retained and explain why",
                    "only files created by this task whose deletion is permitted",
                    "Do not automatically change `.gitignore`",
                ):
                    self.assertIn(marker, temporary)
                self.assertNotIn("Use the permitted task or scratch location", text)

    def test_global_contract_owns_action_first_and_state_anchoring(self) -> None:
        contract = read("templates/opencode-global-AGENTS.md")
        normalized_contract = " ".join(contract.split())

        required = (
            "## About the user",
            "The user has ADHD and no technical background.",
            "Lead with the next action",
            "Each step is one bounded action.",
            "End with one concrete next action",
            "Use estimates only when requested and defensible.",
            "Matter-of-fact tone for errors",
            "Restate state every turn",
            "Include verification evidence when reporting a failure or fix.",
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
