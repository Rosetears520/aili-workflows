from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "docs" / "harness" / "fixtures" / "graphify-local-review-fixtures.yaml"
LEGACY_LAUNCHER = ROOT / "scripts" / "graphify_baseline_check.py"

EXPECTED_CONTRACT = {
    "cli_install": "uv tool install graphifyy",
    "global_skill_registration": "graphify install --platform agents",
    "global_skill_path": "~/.agents/skills/graphify/SKILL.md",
    "local_review_launches_graphify": False,
    "project_execution_requires_separate_approval": True,
}
EXPECTED_CASES = {
    "architecture-existing-graph": "one-scoped-official-graphify-result",
    "architecture-no-graph": "skip-graphify-use-current-evidence",
    "exact-current-symbol": "codegraph-or-current-files",
    "no-auto-install": "no-uv-or-graphify-command",
    "no-auto-register": "registration-remains-separately-approved",
    "no-auto-run": "no-project-graph-command",
    "project-operation-separate": "fresh-exact-target-effect-approval",
    "non-authoritative": "reconcile-current-source-tests-contract",
    "current-conflict": "current-files-win-graphify-unverified",
    "no-duplicate-discovery": "no-graphify-codegraph-broad-grep-duplication",
    "local-review-existing-output-only": "consume-bounded-result-with-current-evidence",
    "local-review-no-output": "continue-without-launching-graphify",
}
EXPECTED_CATEGORIES = {
    "architecture-routing",
    "exact-locality",
    "operation-boundary",
    "evidence-authority",
    "review-consumption",
}
EXPECTED_FORBIDDEN = {
    "custom_runtime_or_launcher",
    "automatic_install_register_or_run",
    "project_opencode_plugin",
    "authoritative_graph_claim",
    "duplicate_broad_discovery",
    "local_review_graphify_launch",
}


def validate_fixture(data: object) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["fixture must be an object"]
    if data.get("schema_version") != "2.0" or data.get("profile") != "official-upstream-navigation":
        errors.append("schema/profile mismatch")
    if data.get("contract") != EXPECTED_CONTRACT:
        errors.append("official command/ownership contract mismatch")
    cases = data.get("cases")
    if not isinstance(cases, list):
        return [*errors, "cases must be an array"]
    ids = [case.get("id") for case in cases if isinstance(case, dict)]
    if len(ids) != len(cases) or len(ids) != len(set(ids)):
        errors.append("case ids must be complete and unique")
    categories = {case.get("category") for case in cases if isinstance(case, dict)}
    if categories != EXPECTED_CATEGORIES or set(data.get("required_categories", [])) != EXPECTED_CATEGORIES:
        errors.append("category coverage mismatch")
    by_id = {case.get("id"): case for case in cases if isinstance(case, dict)}
    for case_id, expected in EXPECTED_CASES.items():
        if by_id.get(case_id, {}).get("expected") != expected:
            errors.append(f"{case_id} expected mismatch")
    forbidden = data.get("forbidden")
    if not isinstance(forbidden, dict) or set(forbidden) != EXPECTED_FORBIDDEN or any(value is not True for value in forbidden.values()):
        errors.append("forbidden ownership/integration contract mismatch")
    return errors


class GraphifyOfficialIntegrationTests(unittest.TestCase):
    def fixture(self) -> dict:
        return json.loads(FIXTURE.read_text(encoding="utf-8"))

    def test_official_routing_fixture_is_complete(self):
        self.assertEqual(validate_fixture(self.fixture()), [])

    def test_fixture_mutations_fail_closed(self):
        original = self.fixture()
        mutations = []
        changed_command = copy.deepcopy(original)
        changed_command["contract"]["global_skill_registration"] = "graphify install --platform opencode"
        mutations.append(changed_command)
        removed_case = copy.deepcopy(original)
        removed_case["cases"] = [case for case in removed_case["cases"] if case["id"] != "no-auto-run"]
        mutations.append(removed_case)
        weakened_forbidden = copy.deepcopy(original)
        weakened_forbidden["forbidden"]["local_review_graphify_launch"] = False
        mutations.append(weakened_forbidden)
        for mutation in mutations:
            with self.subTest(mutation=mutation):
                self.assertTrue(validate_fixture(mutation))

    def test_legacy_launcher_and_distribution_entry_are_retired(self):
        package = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))
        self.assertFalse(LEGACY_LAUNCHER.exists())
        self.assertNotIn("scripts/graphify_baseline_check.py", package["files"])
        self.assertIn("docs/harness/fixtures/graphify-local-review-fixtures.yaml", package["files"])
        self.assertFalse(any("graphify" in f"{name} {command}".lower() for name, command in package.get("scripts", {}).items()))

    def test_local_review_consumes_existing_output_without_launch_ownership(self):
        command = (ROOT / "core" / "commands" / "local-review.md").read_text(encoding="utf-8")
        fixture = FIXTURE.read_text(encoding="utf-8")
        self.assertIn("standalone non-delivery audit", command)
        self.assertIn("not lifecycle acceptance or SHIP", command)
        self.assertNotIn("Graphify", command)
        self.assertIn("local-review-existing-output-only", fixture)
        self.assertIn("local-review-no-output", fixture)

    def test_global_routing_separates_architecture_from_exact_locality(self):
        surfaces = [
            ROOT / "agents" / "rose.md",
            ROOT / "templates" / "opencode-global-AGENTS.md",
            ROOT / ".agents" / "skills" / "aili-delivery-flow" / "SKILL.md",
        ]
        text = "\n".join(path.read_text(encoding="utf-8") for path in surfaces)
        self.assertIn("architecture-orientation", text)
        self.assertIn("CodeGraph or current files", text)
        self.assertIn("no lifecycle phase installs, registers, or runs Graphify automatically", text)

    def test_runtime_source_uses_only_official_install_and_registration_commands(self):
        source = (ROOT / "src" / "graphify.ts").read_text(encoding="utf-8")
        self.assertIn('["uv", "tool", "install", "graphifyy"]', source)
        self.assertIn('["graphify", "install", "--platform", "agents"]', source)
        self.assertNotIn("--platform\", \"opencode", source)
        self.assertNotIn("graphify-out", source)
        self.assertFalse((ROOT / ".agents" / "skills" / "graphify-project-map").exists())
        self.assertFalse((ROOT / ".agents" / "skills" / "graphify-index").exists())

    def test_readme_and_setup_document_the_official_separate_flow(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        setup = (ROOT / "docs" / "opencode-setup.md").read_text(encoding="utf-8")
        combined = readme + "\n" + setup
        for marker in (
            "uv tool install graphifyy",
            "graphify install --platform agents",
            "--enable-graphify",
            "--register-graphify-skill",
            "--skip-graphify",
            "uv` must already exist",
            "$HOME/.agents/skills/graphify/",
            "current-project `.opencode`",
            "upstream-owned",
            "architecture-orientation",
            "project graph operation",
        ):
            self.assertIn(marker, combined)
        self.assertNotIn("Graphify guarded launcher", combined)
        self.assertNotIn("graphify_baseline_check.py", combined)


if __name__ == "__main__":
    unittest.main()
