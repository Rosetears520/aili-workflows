"""Header-free project templates retain section and managed-block checks."""

import argparse
import contextlib
import importlib.util
import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("agents_md", ROOT / "scripts/agents_md.py")
agents_md = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(agents_md)


class AgentsMdTests(unittest.TestCase):
    def test_init_and_check_without_provenance_headers(self):
        with tempfile.TemporaryDirectory() as directory:
            args = argparse.Namespace(project=directory, strategy="abort", allow_placeholders=True)
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(agents_md.command_init(args), 0)
                target = Path(directory) / "AGENTS.md"
                text = target.read_text(encoding="utf-8")
                self.assertTrue(text.startswith("# AGENTS.md\n"))
                self.assertNotIn("AILI_AGENTS_TEMPLATE_", text)
                self.assertIn("<!-- Fill", text)
                self.assertEqual(agents_md.command_check(args), 0)
                args.allow_placeholders = False
                self.assertEqual(agents_md.command_check(args), 1)
                args.allow_placeholders = True
                for section in agents_md.REQUIRED_SECTIONS:
                    target.write_text(text.replace(section, "removed section"), encoding="utf-8")
                    self.assertEqual(agents_md.command_check(args), 1, section)

    def test_update_preserves_local_text_and_managed_block_validation(self):
        old = "<!-- AILI_MANAGED_BLOCK_BEGIN: rules -->\nold\n<!-- AILI_MANAGED_BLOCK_END: rules -->"
        new = old.replace("\nold\n", "\nnew\n")
        base = "\n\n".join(agents_md.REQUIRED_SECTIONS) + "\n"
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "AGENTS.md"
            template = Path(directory) / "template.md"
            template.write_text(base + new, encoding="utf-8")
            local = base + "Local facts remain.\n" + old
            target.write_text(local, encoding="utf-8")
            args = argparse.Namespace(project=directory, allow_placeholders=False)
            with patch.object(agents_md, "template_path", return_value=template), contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(agents_md.command_check(args), 1)
                self.assertEqual(agents_md.command_update(args), 0)
                self.assertEqual(target.read_text(encoding="utf-8"), local.replace(old, new))
                self.assertEqual(agents_md.command_check(args), 0)
                backups = list(Path(directory).glob("AGENTS.md.backup.*"))
                self.assertEqual(len(backups), 1)
                self.assertEqual(backups[0].read_text(encoding="utf-8"), local)
                target.write_text(base, encoding="utf-8")
                self.assertEqual(agents_md.command_check(args), 1)
                with self.assertRaises(SystemExit):
                    agents_md.command_update(args)
                target.write_text(base + new + "\n" + new.replace("rules", "retired"), encoding="utf-8")
                self.assertEqual(agents_md.command_check(args), 1)


if __name__ == "__main__":
    unittest.main()
