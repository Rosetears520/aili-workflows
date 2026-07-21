from __future__ import annotations

from contextlib import redirect_stdout
from datetime import datetime, timedelta, timezone
import importlib.util
import io
import json
import os
from pathlib import Path
import re
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
HELPER_PATH = ROOT / ".agents" / "skills" / "session-handoff" / "scripts" / "session_handoff.py"
SPEC = importlib.util.spec_from_file_location("session_handoff", HELPER_PATH)
assert SPEC and SPEC.loader
HANDOFF = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(HANDOFF)

CREATED = datetime(2026, 7, 21, 12, 0, 0, tzinfo=timezone.utc)
FINALIZED = CREATED + timedelta(minutes=1)


class SessionHandoffTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.repository = Path(self.temp.name).resolve() / "repository"
        self.task = self.repository / "tasks" / "demo"
        self.task.mkdir(parents=True)

    def tearDown(self):
        self.temp.cleanup()

    def snapshot_path(self, result: dict) -> Path:
        return self.repository / result["path"]

    def fill_draft(
        self,
        result: dict,
        *,
        section_values: dict[str, str] | None = None,
        specialist_sections: dict[str, str] | None = None,
    ) -> Path:
        path = self.snapshot_path(result)
        text = path.read_text(encoding="utf-8")
        text = re.sub(r"\[FILL:[^\]]+\]", "None recorded.", text)
        for section, value in (section_values or {}).items():
            pattern = re.compile(rf"(^## {re.escape(section)}\n\n).*?(?=^## |\Z)", re.MULTILINE | re.DOTALL)
            text, count = pattern.subn(lambda match: f"{match.group(1)}{value}\n\n", text, count=1)
            self.assertEqual(count, 1, section)
        for section, value in (specialist_sections or {}).items():
            text = text.rstrip() + f"\n\n## {section}\n\n{value}\n"
        path.write_text(text, encoding="utf-8", newline="\n")
        return path

    def create_finalized(
        self,
        slug: str,
        *,
        created: datetime = CREATED,
        finalized: datetime = FINALIZED,
        language: str = "en",
        continues_from: str | None = None,
        specialist_sections: dict[str, str] | None = None,
    ) -> tuple[dict, dict, Path]:
        draft = HANDOFF.new_snapshot(
            self.repository,
            self.task,
            slug,
            language=language,
            continues_from=continues_from,
            now=created,
        )
        path = self.fill_draft(draft, specialist_sections=specialist_sections)
        finalized_result = HANDOFF.finalize_snapshot(
            self.repository,
            self.task,
            draft["path"],
            now=finalized,
        )
        return draft, finalized_result, path

    def test_new_uses_task_scoped_exclusive_names_and_normalized_slug(self):
        first = HANDOFF.new_snapshot(self.repository, self.task, " Unsafe / Label ", now=CREATED)
        first_path = self.snapshot_path(first)
        first_bytes = first_path.read_bytes()
        second = HANDOFF.new_snapshot(self.repository, self.task, " Unsafe / Label ", now=CREATED)
        fallback = HANDOFF.new_snapshot(self.repository, self.task, "你好", now=CREATED)

        self.assertEqual(first["path"], "tasks/demo/handoffs/20260721T120000Z--unsafe-label.md")
        self.assertEqual(second["path"], "tasks/demo/handoffs/20260721T120000Z--unsafe-label--02.md")
        self.assertEqual(fallback["path"], "tasks/demo/handoffs/20260721T120000Z--handoff.md")
        self.assertEqual(first_path.read_bytes(), first_bytes)
        metadata, body = HANDOFF._parse_document(first_path.read_text(encoding="utf-8"))
        self.assertEqual(metadata["task_root"], "tasks/demo")
        self.assertEqual(metadata["status"], "draft")
        self.assertTrue(all(f"## {section}" in body for section in HANDOFF.CORE_SECTIONS))
        self.assertTrue(all(f"## {section}" not in body for section in HANDOFF.SPECIALIST_SECTIONS))

        for _ in range(97):
            HANDOFF.new_snapshot(self.repository, self.task, " Unsafe / Label ", now=CREATED)
        hundredth = HANDOFF.new_snapshot(self.repository, self.task, " Unsafe / Label ", now=CREATED)
        collision_rows = [
            row for row in HANDOFF.list_history(self.repository, self.task)["snapshots"]
            if "unsafe-label" in row["snapshot_id"]
        ]
        self.assertTrue(hundredth["path"].endswith("--100.md"))
        self.assertEqual(collision_rows[0]["path"], hundredth["path"])

    def test_failed_new_and_list_do_not_create_history_without_a_valid_trigger(self):
        result = HANDOFF.list_history(self.repository, self.task)
        self.assertEqual(result["snapshots"], [])
        self.assertFalse((self.task / "handoffs").exists())
        with self.assertRaisesRegex(HANDOFF.HandoffError, "invalid language"):
            HANDOFF.new_snapshot(self.repository, self.task, "demo", language="not valid", now=CREATED)
        self.assertFalse((self.task / "handoffs").exists())

    def test_containment_traversal_and_symlink_paths_fail_closed(self):
        outside = Path(self.temp.name).resolve() / "outside"
        outside.mkdir()
        task_link = self.repository / "linked-task"
        task_link.symlink_to(outside, target_is_directory=True)
        with self.assertRaisesRegex(HANDOFF.HandoffError, "ambiguous, symlinked"):
            HANDOFF.new_snapshot(self.repository, task_link, "demo", now=CREATED)

        history_link = self.task / "handoffs"
        history_link.symlink_to(outside, target_is_directory=True)
        with self.assertRaisesRegex(HANDOFF.HandoffError, "not a regular directory"):
            HANDOFF.new_snapshot(self.repository, self.task, "demo", now=CREATED)
        history_link.unlink()
        history_link.symlink_to(outside / "missing", target_is_directory=True)
        with self.assertRaisesRegex(HANDOFF.HandoffError, "not a regular directory"):
            HANDOFF.list_history(self.repository, self.task)
        history_link.unlink()

        draft = HANDOFF.new_snapshot(self.repository, self.task, "demo", now=CREATED)
        self.fill_draft(draft)
        with self.assertRaisesRegex(HANDOFF.HandoffError, "not normalized"):
            HANDOFF.finalize_snapshot(self.repository, self.task, "handoffs/../handoffs/" + Path(draft["path"]).name, now=FINALIZED)
        self.assertFalse((self.task / "handoffs" / "LATEST.md").exists())

    def test_finalize_resolve_immutability_and_localized_output(self):
        draft, finalized, path = self.create_finalized("first", language="zh-CN")
        pointer = self.task / "handoffs" / "LATEST.md"
        original = path.read_bytes()

        self.assertTrue(pointer.is_file())
        self.assertFalse(pointer.is_symlink())
        pointer_text = pointer.read_text(encoding="utf-8")
        self.assertIn(f"snapshot_path: `{finalized['task_path']}`", pointer_text)
        self.assertIn(f"snapshot_id: `{finalized['snapshot_id']}`", pointer_text)
        self.assertIn(f"sha256: `{finalized['sha256']}`", pointer_text)
        self.assertEqual(HANDOFF.resolve_snapshot(self.repository, self.task, snapshot=finalized["path"])["path"], finalized["path"])
        self.assertEqual(HANDOFF.resolve_snapshot(self.repository, self.task)["path"], finalized["path"])
        with self.assertRaisesRegex(HANDOFF.HandoffError, "only a draft"):
            HANDOFF.finalize_snapshot(self.repository, self.task, draft["task_path"], now=FINALIZED + timedelta(minutes=1))
        self.assertEqual(path.read_bytes(), original)

        response = HANDOFF.format_create_success(finalized["path"], "zh-CN")
        self.assertEqual(response.count("```text"), 1)
        self.assertEqual(response.count("```"), 2)
        self.assertTrue(response.endswith("```"))
        self.assertIn(finalized["path"], response)
        for marker in ("不是合同", "权限", "branch/HEAD", "dirty", "Unverified", "Next Action"):
            self.assertIn(marker, response)

    def test_correction_chain_preserves_predecessor_and_exact_beats_latest(self):
        _, first, first_path = self.create_finalized("first")
        first_bytes = first_path.read_bytes()
        _, second, _ = self.create_finalized(
            "second",
            created=CREATED + timedelta(minutes=2),
            finalized=FINALIZED + timedelta(minutes=2),
            continues_from=first["path"],
        )

        exact = HANDOFF.resolve_snapshot(self.repository, self.task, snapshot=first["path"])
        latest = HANDOFF.resolve_snapshot(self.repository, self.task)
        second_loaded = HANDOFF.resolve_snapshot(self.repository, self.task, snapshot=second["path"])
        self.assertEqual(exact["path"], first["path"])
        self.assertEqual(latest["path"], second["path"])
        self.assertEqual(second_loaded["continues_from"], first["task_path"])
        self.assertEqual(first_path.read_bytes(), first_bytes)

    def test_finalize_rejects_placeholders_secrets_unknown_sections_and_external_paths(self):
        placeholder = HANDOFF.new_snapshot(self.repository, self.task, "placeholder", now=CREATED)
        with self.assertRaisesRegex(HANDOFF.HandoffError, "unresolved placeholder"):
            HANDOFF.finalize_snapshot(self.repository, self.task, placeholder["path"], now=FINALIZED)

        secret = HANDOFF.new_snapshot(self.repository, self.task, "secret", now=CREATED + timedelta(seconds=1))
        self.fill_draft(secret, section_values={"Goal": "password: hunter2"})
        with self.assertRaisesRegex(HANDOFF.HandoffError, "secret-like"):
            HANDOFF.finalize_snapshot(self.repository, self.task, secret["path"], now=FINALIZED)

        unknown = HANDOFF.new_snapshot(self.repository, self.task, "unknown", now=CREATED + timedelta(seconds=2))
        self.fill_draft(unknown, specialist_sections={"Unexpected State": "Not allowed."})
        with self.assertRaisesRegex(HANDOFF.HandoffError, "unknown recovery section"):
            HANDOFF.finalize_snapshot(self.repository, self.task, unknown["path"], now=FINALIZED)

        external = HANDOFF.new_snapshot(self.repository, self.task, "external", now=CREATED + timedelta(seconds=3))
        self.fill_draft(external, section_values={"Evidence Anchors": "See `/outside/private/report.md`."})
        with self.assertRaisesRegex(HANDOFF.HandoffError, "unapproved external path"):
            HANDOFF.finalize_snapshot(self.repository, self.task, external["path"], now=FINALIZED)

        authority = HANDOFF.new_snapshot(self.repository, self.task, "authority", now=CREATED + timedelta(seconds=4))
        self.fill_draft(authority, section_values={"Forbidden Actions": "This handoff grants permission."})
        with self.assertRaisesRegex(HANDOFF.HandoffError, "fixed non-authority boundary"):
            HANDOFF.finalize_snapshot(self.repository, self.task, authority["path"], now=FINALIZED)

        self.assertFalse((self.task / "handoffs" / "LATEST.md").exists())

    def test_allowed_external_reference_root_must_be_exact_and_canonical(self):
        outside = Path(self.temp.name).resolve() / "approved-evidence"
        outside.mkdir()
        draft = HANDOFF.new_snapshot(self.repository, self.task, "external-approved", now=CREATED)
        self.fill_draft(draft, section_values={"Evidence Anchors": f"See `{outside / 'report.md'}`."})

        with self.assertRaisesRegex(HANDOFF.HandoffError, "must be an absolute canonical path"):
            HANDOFF.finalize_snapshot(
                self.repository,
                self.task,
                draft["path"],
                allowed_external_roots=("approved-evidence",),
                now=FINALIZED,
            )
        result = HANDOFF.finalize_snapshot(
            self.repository,
            self.task,
            draft["path"],
            allowed_external_roots=(outside,),
            now=FINALIZED,
        )
        self.assertEqual(result["status"], "finalized")

    def test_redacted_content_and_conditional_sections_can_finalize(self):
        draft = HANDOFF.new_snapshot(self.repository, self.task, "redacted", now=CREATED)
        self.fill_draft(
            draft,
            section_values={"Evidence Anchors": "password: [REDACTED]."},
            specialist_sections={
                "Touched Files / Artifact References": "`tests/session_handoff_test.py`",
                "Blocker / Stop Reason": "No blocker.",
            },
        )
        result = HANDOFF.finalize_snapshot(self.repository, self.task, draft["path"], now=FINALIZED)
        content = HANDOFF.resolve_snapshot(self.repository, self.task, snapshot=result["path"])["content"]
        self.assertIn("## Touched Files / Artifact References", content)
        self.assertIn("password: [REDACTED].", content)

    def test_pointer_replace_failure_preserves_prior_pointer_and_does_not_claim_latest(self):
        _, first, _ = self.create_finalized("first")
        pointer = self.task / "handoffs" / "LATEST.md"
        pointer_bytes = pointer.read_bytes()
        second = HANDOFF.new_snapshot(self.repository, self.task, "second", now=CREATED + timedelta(minutes=2))
        second_path = self.fill_draft(second)

        def fail_replace(_source, _destination):
            raise OSError("injected pointer replacement failure")

        with self.assertRaisesRegex(HANDOFF.HandoffError, "snapshot finalized but LATEST.md replacement failed"):
            HANDOFF.finalize_snapshot(
                self.repository,
                self.task,
                second["path"],
                replace=fail_replace,
                now=FINALIZED + timedelta(minutes=2),
            )

        self.assertEqual(pointer.read_bytes(), pointer_bytes)
        self.assertEqual(HANDOFF.resolve_snapshot(self.repository, self.task)["path"], first["path"])
        second_metadata, _ = HANDOFF._parse_document(second_path.read_text(encoding="utf-8"))
        self.assertEqual(second_metadata["status"], "finalized")

    def test_list_reads_bounded_frontmatter_reports_anomalies_and_sorts_newest_first(self):
        _, first, _ = self.create_finalized("first")
        _, second, _ = self.create_finalized(
            "second",
            created=CREATED + timedelta(minutes=2),
            finalized=FINALIZED + timedelta(minutes=2),
        )
        body_unreadable = HANDOFF.new_snapshot(self.repository, self.task, "body-unreadable", now=CREATED + timedelta(minutes=3))
        body_path = self.snapshot_path(body_unreadable)
        raw = body_path.read_bytes()
        closing = raw.find(b"\n---\n", 4) + 5
        body_path.write_bytes(raw[:closing] + b"\xff\xfe body is intentionally not UTF-8")
        (self.task / "handoffs" / "notes.txt").write_text("unexpected", encoding="utf-8")
        linked = self.task / "handoffs" / "20260721T120400Z--linked.md"
        linked.symlink_to(self.snapshot_path(first))

        result = HANDOFF.list_history(self.repository, self.task)
        paths = [row["path"] for row in result["snapshots"]]
        self.assertEqual(paths, sorted(paths, reverse=True))
        self.assertIn(body_unreadable["path"], paths)
        self.assertTrue(all("content" not in row for row in result["snapshots"]))
        self.assertEqual({Path(row["path"]).name for row in result["invalid"]}, {"notes.txt", linked.name})
        self.assertIn(first["path"], paths)
        self.assertIn(second["path"], paths)

    def test_corrupt_latest_reports_candidates_without_guessing_and_exact_still_works(self):
        _, finalized, _ = self.create_finalized("first")
        pointer = self.task / "handoffs" / "LATEST.md"
        pointer.write_text("# malformed\n", encoding="utf-8")

        with self.assertRaises(HANDOFF.HandoffResolveError) as raised:
            HANDOFF.resolve_snapshot(self.repository, self.task)
        self.assertEqual(raised.exception.candidates, [finalized["path"]])
        exact = HANDOFF.resolve_snapshot(self.repository, self.task, snapshot=finalized["path"])
        self.assertEqual(exact["resolution"], "exact")

    def test_legacy_is_explicit_read_only_and_versioned_operations_never_prune(self):
        legacy = self.task / "handoff.md"
        legacy.write_text("legacy navigation\n", encoding="utf-8")
        legacy_bytes = legacy.read_bytes()
        _, first, first_path = self.create_finalized("first")
        _, second, second_path = self.create_finalized(
            "second",
            created=CREATED + timedelta(minutes=2),
            finalized=FINALIZED + timedelta(minutes=2),
        )

        resolved = HANDOFF.resolve_snapshot(self.repository, self.task, legacy=True)
        self.assertTrue(resolved["legacy"])
        self.assertEqual(resolved["content"], "legacy navigation\n")
        self.assertEqual(legacy.read_bytes(), legacy_bytes)
        self.assertTrue(first_path.exists())
        self.assertTrue(second_path.exists())
        self.assertEqual(len(HANDOFF.list_history(self.repository, self.task)["snapshots"]), 2)
        with self.assertRaisesRegex(HANDOFF.HandoffError, "mutually exclusive"):
            HANDOFF.resolve_snapshot(self.repository, self.task, snapshot=first["path"], legacy=True)
        self.assertEqual(HANDOFF.resolve_snapshot(self.repository, self.task)["path"], second["path"])

    def test_finalization_time_and_task_root_identity_fail_before_pointer_mutation(self):
        draft = HANDOFF.new_snapshot(self.repository, self.task, "future", now=FINALIZED)
        path = self.fill_draft(draft)
        before = path.read_bytes()
        with self.assertRaisesRegex(HANDOFF.HandoffError, "precedes created_at"):
            HANDOFF.finalize_snapshot(self.repository, self.task, draft["path"], now=CREATED)
        self.assertEqual(path.read_bytes(), before)
        self.assertFalse((self.task / "handoffs" / "LATEST.md").exists())

        text = path.read_text(encoding="utf-8").replace('task_root: "tasks/demo"', 'task_root: "tasks/other"')
        path.write_text(text, encoding="utf-8", newline="\n")
        with self.assertRaisesRegex(HANDOFF.HandoffError, "task_root does not match"):
            HANDOFF.finalize_snapshot(self.repository, self.task, draft["path"], now=FINALIZED + timedelta(minutes=1))

    def test_cli_user_output_ends_with_one_text_fence(self):
        draft = HANDOFF.new_snapshot(
            self.repository,
            self.task,
            "cli",
            language="en",
            now=datetime.now(timezone.utc) - timedelta(minutes=1),
        )
        self.fill_draft(draft)
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            code = HANDOFF.main(
                [
                    "finalize",
                    "--repository-root",
                    os.fspath(self.repository),
                    "--task-root",
                    os.fspath(self.task),
                    "--snapshot",
                    draft["path"],
                    "--user-output",
                ]
            )
        output = stdout.getvalue().rstrip("\n")
        self.assertEqual(code, 0)
        self.assertEqual(output.count("```text"), 1)
        self.assertEqual(output.count("```"), 2)
        self.assertTrue(output.endswith("```"))
        self.assertIn(draft["path"], output)

    def test_cli_resolve_error_is_structured_with_recoverable_candidates(self):
        _, finalized, _ = self.create_finalized("first")
        (self.task / "handoffs" / "LATEST.md").write_text("bad\n", encoding="utf-8")
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            code = HANDOFF.main(
                [
                    "resolve",
                    "--repository-root",
                    os.fspath(self.repository),
                    "--task-root",
                    os.fspath(self.task),
                ]
            )
        result = json.loads(stdout.getvalue())
        self.assertEqual(code, 5)
        self.assertEqual(result["status"], "blocked")
        self.assertEqual(result["recoverable_candidates"], [finalized["path"]])

    def test_skill_lifecycle_fixture_and_distribution_contracts_are_versioned(self):
        skill = (ROOT / ".agents" / "skills" / "session-handoff" / "SKILL.md").read_text(encoding="utf-8")
        artifact_contracts = (
            ROOT / ".agents" / "skills" / "aili-delivery-flow" / "references" / "artifact-contracts.md"
        ).read_text(encoding="utf-8")
        continuity = json.loads(
            (ROOT / "docs" / "harness" / "fixtures" / "continuity-memory-handoff-fixtures.yaml").read_text(encoding="utf-8")
        )
        upstream = json.loads(
            (ROOT / "docs" / "harness" / "fixtures" / "upstream-reference-fixtures.yaml").read_text(encoding="utf-8")
        )
        manifest = json.loads((ROOT / "manifests" / "rose-aili.components.json").read_text(encoding="utf-8"))

        skill.encode("ascii")
        frontmatter = skill.split("---", 2)[1].strip().splitlines()
        self.assertEqual([line.split(":", 1)[0] for line in frontmatter], ["name", "description"])
        for forbidden_tag in ("[KNOWN]", "[FRAME]", "[已知]", "[框架内]"):
            self.assertNotIn(forbidden_tag, skill)
        for marker in ("## CREATE", "## LIST", "## RESUME", "scripts/session_handoff.py", "--user-output"):
            self.assertIn(marker, skill)
        self.assertIn("openspec/changes/<change-id>/handoffs/", skill)
        self.assertIn("OpenSpec uses `openspec/changes/<change-id>/handoffs/`", artifact_contracts)
        self.assertIn("exactly one localized fenced `text` prompt", artifact_contracts)
        cases = {case["id"]: case for case in continuity["cases"]}
        for case_id in (
            "handoff-trigger",
            "handoff-list-bounded-history",
            "handoff-exact-resume",
            "handoff-invalid-latest",
            "handoff-legacy-read-only",
        ):
            self.assertIn(case_id, cases)
        handoff_case = next(case for case in upstream["cases"] if case["id"] == "handoff-positive")
        self.assertIn("immutable snapshot", handoff_case["artifact_target"])
        component = next(item for item in manifest["components"]["skills"] if item["name"] == "session-handoff")
        self.assertEqual(component["path"], ".agents/skills/session-handoff")
        self.assertTrue(HELPER_PATH.is_file())
        self.assertNotIn("prune", HANDOFF._command_parser()._subparsers._group_actions[0].choices)


if __name__ == "__main__":
    unittest.main()
