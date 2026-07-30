from __future__ import annotations

import importlib.util
import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIXTURE_CHECK_SPEC = importlib.util.spec_from_file_location(
    "harness_fixture_check",
    ROOT / "scripts" / "harness_fixture_check.py",
)
assert FIXTURE_CHECK_SPEC and FIXTURE_CHECK_SPEC.loader
FIXTURE_CHECK = importlib.util.module_from_spec(FIXTURE_CHECK_SPEC)
FIXTURE_CHECK_SPEC.loader.exec_module(FIXTURE_CHECK)


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


class OfficeArtifactSkillContractTests(unittest.TestCase):
    def assert_markers(self, relative: str, markers: tuple[str, ...]) -> None:
        text = read(relative)
        for marker in markers:
            with self.subTest(path=relative, marker=marker):
                self.assertIn(marker, text)

    def test_docx_is_officecli_first_with_openxml_fallback_and_preservation(self) -> None:
        self.assert_markers(
            ".agents/skills/minimax-docx/SKILL.md",
            (
                "sole DOCX artifact owner",
                "OfficeCLI-First Selection",
                "Installed-version help is the authority",
                "Preserve every input original",
                "OpenXML Fallback Setup",
                "setup.sh",
                "env_check.sh",
                "claim-matched evidence",
                "OfficeCLI Skill",
                "OfficeCLI MCP",
                "rose-aili install",
                "rose-aili update",
            ),
        )

    def test_xlsx_is_officecli_first_with_pandas_and_xml_preservation_fallbacks(self) -> None:
        self.assert_markers(
            ".agents/skills/minimax-xlsx/SKILL.md",
            (
                "sole spreadsheet artifact owner",
                "OfficeCLI-First Selection",
                "Installed-version help is the authority",
                "Preserve every input original",
                "Use pandas for CSV/TSV analysis",
                ".xlsm",
                "VBA",
                "direct XML path",
                "formula/readback/recalculation",
                "OfficeCLI Skill",
                "OfficeCLI MCP",
                "Cross-viewer fidelity remains `Unverified`",
            ),
        )

    def test_ppt_keeps_adapter_but_has_no_skill_local_install_owner(self) -> None:
        skill_root = ROOT / ".agents" / "skills" / "pptx-generator"
        self.assertFalse((skill_root / "scripts" / "setup_officecli.py").exists())
        self.assertFalse((skill_root / "references" / "officecli-release.json").exists())
        self.assertTrue((skill_root / "scripts" / "probe_officecli.py").is_file())
        self.assertTrue((skill_root / "scripts" / "build_workspace.py").is_file())
        self.assertTrue((skill_root / "scripts" / "render_with_officecli.py").is_file())
        self.assert_markers(
            ".agents/skills/pptx-generator/references/officecli-adapter.md",
            (
                "managed installation is owned by the AILI installer",
                "manifests/officecli-tool.json",
                "rose-aili install",
                "rose-aili update",
                "This Skill has no OfficeCLI setup or npm execution path",
            ),
        )
        manifest = json.loads(read("manifests/officecli-tool.json"))
        adapter = read(".agents/skills/pptx-generator/scripts/officecli_adapter.py")
        mirrored_version = re.search(r'^PINNED_VERSION = "([^"]+)"$', adapter, re.MULTILINE)
        self.assertIsNotNone(mirrored_version)
        self.assertEqual(mirrored_version.group(1), manifest["version"])
        self.assertEqual(manifest["packageSpec"], f'{manifest["package"]}@{manifest["version"]}')

    def test_docs_and_routing_keep_officecli_non_routable_and_default_skippable(self) -> None:
        for relative in ("README.md", "docs/opencode-setup.md"):
            self.assert_markers(
                relative,
                (
                    "--skip-officecli",
                    "$HOME/.agents/tools/officecli",
                    "manifests/officecli-tool.json",
                    "non-routable",
                    "Unverified",
                ),
            )

        fixture = json.loads(read("docs/harness/fixtures/skill-routing-fixtures.yaml"))
        by_id = {case["id"]: case for case in fixture["cases"]}
        self.assertEqual(by_id["docx-officecli-simple"]["skill"], "minimax-docx")
        self.assertEqual(by_id["xlsx-officecli-simple"]["skill"], "minimax-xlsx")
        self.assertEqual(by_id["pptx-officecli-internal-adapter"]["skill"], "pptx-generator")
        self.assertNotIn("officecli", {case["skill"] for case in fixture["cases"]})
        fixture_errors = FIXTURE_CHECK.validate_fixture(
            "skill-routing-fixtures.yaml",
            FIXTURE_CHECK.REQUIRED["skill-routing-fixtures.yaml"],
        )
        self.assertEqual(fixture_errors, [])


if __name__ == "__main__":
    unittest.main()
