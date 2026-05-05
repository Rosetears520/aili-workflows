import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "memory_cli.py"


class MemoryCliTests(unittest.TestCase):
    def run_cli(self, *args, cwd=None, check=True):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            cwd=cwd or ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        if check and result.returncode != 0:
            self.fail(f"command failed: {result.stderr}\nstdout: {result.stdout}")
        return result.returncode, json.loads(result.stdout)

    def init_db(self, tmpdir, project="aili-workflow", agent="rose"):
        db = str(Path(tmpdir) / "memory.db")
        _, output = self.run_cli("init", "--db", db, "--project", project, "--agent", agent)
        self.assertTrue(output["ok"])
        return db

    def test_init_and_doctor_create_valid_schema(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db = self.init_db(tmpdir)
            _, output = self.run_cli("doctor", "--db", db)
            self.assertTrue(output["ok"])
            self.assertEqual(output["result"]["status"], "ok")
            self.assertEqual(output["result"]["missing_tables"], [])

    def test_search_is_scoped_by_project_and_agent(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db = self.init_db(tmpdir)
            self.run_cli("session", "start", "--db", db, "--session-key", "s1", "--project", "p1", "--agent", "rose")
            self.run_cli("session", "start", "--db", db, "--session-key", "s2", "--project", "p2", "--agent", "other")
            self.run_cli(
                "finding",
                "add",
                "--db",
                db,
                "--session-key",
                "s1",
                "--project",
                "p1",
                "--agent",
                "rose",
                "--kind",
                "correction",
                "--category",
                "scope_control",
                "--severity",
                "high",
                "--summary",
                "Scoped memory result.",
            )
            self.run_cli(
                "finding",
                "add",
                "--db",
                db,
                "--session-key",
                "s2",
                "--project",
                "p2",
                "--agent",
                "other",
                "--kind",
                "correction",
                "--category",
                "scope_control",
                "--severity",
                "high",
                "--summary",
                "Other project memory result.",
            )
            _, output = self.run_cli("search", "scope", "--db", db, "--project", "p1", "--agent", "rose")
            summaries = [item["summary"] for item in output["result"]["items"]]
            self.assertTrue(summaries)
            self.assertTrue(all("Other project" not in summary for summary in summaries))

    def test_sensitive_fact_update_removes_search_result(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db = self.init_db(tmpdir)
            self.run_cli("session", "start", "--db", db, "--session-key", "s1")
            self.run_cli(
                "fact",
                "add",
                "--db",
                db,
                "--session-key",
                "s1",
                "--fact-key",
                "token_note",
                "--fact-text",
                "temporary searchable token note",
                "--category",
                "test",
            )
            _, before = self.run_cli("search", "token", "--db", db)
            self.assertTrue(before["result"]["items"])
            self.run_cli(
                "fact",
                "add",
                "--db",
                db,
                "--session-key",
                "s1",
                "--fact-key",
                "token_note",
                "--fact-text",
                "temporary searchable token note",
                "--category",
                "test",
                "--sensitive",
            )
            _, after = self.run_cli("search", "token", "--db", db)
            self.assertEqual(after["result"]["items"], [])

    def test_rule_approve_requires_exact_patch_hash(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db = self.init_db(tmpdir)
            self.run_cli("session", "start", "--db", db, "--session-key", "s1")
            _, finding = self.run_cli(
                "finding",
                "add",
                "--db",
                db,
                "--session-key",
                "s1",
                "--kind",
                "risk",
                "--category",
                "safety",
                "--severity",
                "high",
                "--summary",
                "Patch approval test.",
            )
            evidence_id = str(finding["result"]["evidence_id"])
            _, observed = self.run_cli(
                "rule",
                "observe",
                "--db",
                db,
                "--evidence-id",
                evidence_id,
                "--rule-key",
                "patch_hash_approval_test",
                "--rule-text",
                "Require exact patch hash approval.",
                "--category",
                "safety",
                "--severity",
                "high",
                "--signal-type",
                "risk_signal",
            )
            _, proposed = self.run_cli("rule", "propose", "--db", db, "--rule-id", str(observed["result"]["rule_id"]), cwd=tmpdir)
            patch_id = str(proposed["result"]["patch_id"])
            code, failed = self.run_cli(
                "rule",
                "approve",
                "--db",
                db,
                "--patch-id",
                patch_id,
                "--patch-hash",
                "bad-hash",
                "--actor",
                "user",
                cwd=tmpdir,
                check=False,
            )
            self.assertNotEqual(code, 0)
            self.assertEqual(failed["error_code"], "PATCH_HASH_MISMATCH")
            _, approved = self.run_cli(
                "rule",
                "approve",
                "--db",
                db,
                "--patch-id",
                patch_id,
                "--patch-hash",
                proposed["result"]["patch_hash"],
                "--actor",
                "user",
                cwd=tmpdir,
            )
            self.assertTrue(approved["ok"])

    def test_complete_requires_evidence_or_no_durable_marker(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db = self.init_db(tmpdir)
            self.run_cli("session", "start", "--db", db, "--session-key", "s1")
            code, failed = self.run_cli("complete", "--db", db, "--session-key", "s1", check=False)
            self.assertNotEqual(code, 0)
            self.assertEqual(failed["error_code"], "COMPLETION_EVIDENCE_REQUIRED")
            _, output = self.run_cli("complete", "--db", db, "--session-key", "s1", "--no-durable-memory-promoted")
            self.assertTrue(output["ok"])


if __name__ == "__main__":
    unittest.main()
