from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class HandoffCommandContractTests(unittest.TestCase):
    def test_canonical_handoff_command_keeps_explicit_non_authoritative_boundary(self) -> None:
        command = (ROOT / "core" / "commands" / "handoff.md").read_text(encoding="utf-8")

        for marker in (
            "Create, list, or resume an explicit repository-local handoff",
            "Act only for an explicit CREATE, LIST, or RESUME request",
            "openspec/changes/<change-id>/handoffs/",
            "Preserve a redacted, immutable, reference-first snapshot.",
            "RESUME must revalidate the current root, worktree, contract, permissions, and affected evidence",
            "Do not create a handoff because of context pressure",
            "Do not treat a handoff as acceptance, authorization, Git truth, verification, completion evidence",
            "Do not archive, prune, migrate, rotate, or modify an existing finalized handoff",
            "handoff is non-authoritative and does not change lifecycle state.",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, command)

    def test_generated_handoff_command_projects_the_canonical_contract(self) -> None:
        canonical = (ROOT / "core" / "commands" / "handoff.md").read_text(encoding="utf-8")
        generated = (ROOT / "commands" / "handoff.md").read_text(encoding="utf-8")

        self.assertIn("# /handoff", generated)
        self.assertIn(canonical, generated)


if __name__ == "__main__":
    unittest.main()
