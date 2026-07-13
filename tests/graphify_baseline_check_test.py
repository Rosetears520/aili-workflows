from __future__ import annotations

import copy
import base64
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import types
import unittest
from unittest import mock
import zipfile


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "graphify_baseline_check.py"
FIXTURE = ROOT / "docs" / "harness" / "fixtures" / "graphify-local-review-fixtures.yaml"

SPEC = importlib.util.spec_from_file_location("graphify_baseline_check", SCRIPT)
assert SPEC and SPEC.loader
CHECKER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECKER)


class GraphifyBaselineCheckTests(unittest.TestCase):
    def fixture(self):
        return json.loads(FIXTURE.read_text(encoding="utf-8"))

    def result(self):
        return CHECKER.base_contract_result("contract")

    def test_contract_accepts_fixture_and_repository_scan(self):
        args = CHECKER.argparse.Namespace(
            version=CHECKER.BASELINE["version"],
            commit=CHECKER.BASELINE["commit"],
            profile="strict-local",
        )
        code, result = CHECKER.contract_mode(ROOT, FIXTURE, args)
        self.assertEqual(code, 0, result)
        self.assertTrue(result["controls"]["repository_surface_scan"]["complete"])
        self.assertEqual(result["controls"]["repository_surface_scan"]["forbidden"], [])

    def test_every_fixture_expected_or_control_mutation_fails_closed(self):
        original = self.fixture()
        for index, case in enumerate(original["cases"]):
            mutated = copy.deepcopy(original)
            mutated["cases"][index]["expected"] += "-mutated"
            result = self.result()
            CHECKER.verify_fixture(mutated, result)
            self.assertTrue(result["errors"], case["id"])

        for control in original["forbidden"]:
            mutated = copy.deepcopy(original)
            mutated["forbidden"][control] = False
            result = self.result()
            CHECKER.verify_fixture(mutated, result)
            self.assertTrue(result["errors"], control)
        for mutate in (
            lambda value: value["baseline"].__setitem__("artifact_sha256", "0" * 64),
            lambda value: value["exact_argv"]["extract"].append("--mutated"),
        ):
            mutated = copy.deepcopy(original)
            mutate(mutated)
            result = self.result()
            CHECKER.verify_fixture(mutated, result)
            self.assertTrue(result["errors"])

    def test_record_hashes_are_checked_and_missing_hash_fails(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            package = root / "pkg" / "module.py"
            package.parent.mkdir()
            package.write_text("value = 1\n", encoding="utf-8")
            digest = base64.urlsafe_b64encode(hashlib.sha256(package.read_bytes()).digest()).rstrip(b"=").decode()
            item = CHECKER.importlib.metadata.PackagePath("pkg/module.py")
            item.hash = CHECKER.importlib.metadata.FileHash(f"sha256={digest}")
            record = CHECKER.importlib.metadata.PackagePath("pkg-1.dist-info/RECORD")
            record.hash = None
            record_path = root / record
            record_path.parent.mkdir()
            record_path.write_text("record", encoding="utf-8")

            class Dist:
                files = [item, record]
                def locate_file(self, relative):
                    return root / relative

            self.assertTrue(CHECKER.verify_record(Dist())["complete"])
            item.hash = None
            self.assertFalse(CHECKER.verify_record(Dist())["complete"])

    def test_trusted_wheel_binds_installed_bytes_and_rejects_substitution_or_extra(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            package_bytes = b"value = 1\n"
            package_digest = base64.urlsafe_b64encode(hashlib.sha256(package_bytes).digest()).rstrip(b"=").decode()
            record_name = "graphifyy-0.9.12.dist-info/RECORD"
            record = f"graphify/module.py,sha256={package_digest},{len(package_bytes)}\n{record_name},,\n"
            wheel_path = root / "trusted.whl"
            with zipfile.ZipFile(wheel_path, "w") as archive:
                archive.writestr("graphify/module.py", package_bytes)
                archive.writestr(record_name, record)
            wheel = wheel_path.read_bytes()
            with mock.patch.dict(CHECKER.BASELINE, {"artifact_sha256": hashlib.sha256(wheel).hexdigest()}):
                trusted = CHECKER.parse_trusted_wheel(wheel)
                substituted = bytearray(wheel)
                substituted[-1] ^= 1
                with self.assertRaises(ValueError):
                    CHECKER.parse_trusted_wheel(bytes(substituted))

            for relative, content, digest in (("graphify/module.py", package_bytes, package_digest), (record_name, record.encode(), None)):
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(content)
            items = []
            for relative, digest in (("graphify/module.py", package_digest), (record_name, None)):
                item = CHECKER.importlib.metadata.PackagePath(relative)
                item.hash = CHECKER.importlib.metadata.FileHash(f"sha256={digest}") if digest else None
                items.append(item)

            class Dist:
                files = items
                def locate_file(self, relative):
                    return root / relative

            self.assertTrue(CHECKER.compare_installed_to_wheel(Dist(), trusted)["complete"])
            extra = CHECKER.importlib.metadata.PackagePath("graphify/autorun.py")
            extra.hash = None
            Dist.files = [*items, extra]
            self.assertFalse(CHECKER.compare_installed_to_wheel(Dist(), trusted)["complete"])

    def test_repository_scan_rejects_mutations_in_exact_and_ignored_active_surfaces(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            (root / "package.json").write_text(json.dumps({"files": ["scripts/graphify_baseline_check.py", "docs/harness/fixtures/graphify-local-review-fixtures.yaml"], "scripts": {}}), encoding="utf-8")
            skill = root / ".agents/skills/local-review-gate/SKILL.md"
            skill.parent.mkdir(parents=True)
            skill.write_text("- `references/graphify-local-review.md`: explicit-operation-only Graphify adapter, pinned provenance/security concerns, sole guarded launcher, exact argv/network/environment/output controls, local-uncommitted output, and advisory-only findings. It adds no install, registration, hook/plugin, scheduler, lifecycle gate, or completion authority.\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(root), "add", "package.json", str(skill.relative_to(root))], check=True)
            result = self.result()
            self.assertTrue(CHECKER.repository_surface_scan(root, result)["complete"])

            package = json.loads((root / "package.json").read_text(encoding="utf-8"))
            package["scripts"]["graphify:autorun"] = "graphify install --platform opencode"
            (root / "package.json").write_text(json.dumps(package), encoding="utf-8")
            result = self.result()
            self.assertIn("package.json", CHECKER.repository_surface_scan(root, result)["forbidden"])

            skill.write_text(skill.read_text(encoding="utf-8") + "Graphify autorun hook\n", encoding="utf-8")
            result = self.result()
            self.assertIn(".agents/skills/local-review-gate/SKILL.md", CHECKER.repository_surface_scan(root, result)["forbidden"])

            (root / ".gitignore").write_text("plugins/\n", encoding="utf-8")
            plugin = root / "plugins/graphify-hook.json"
            plugin.parent.mkdir()
            plugin.write_text('{"hook":"graphify autorun"}', encoding="utf-8")
            result = self.result()
            scan = CHECKER.repository_surface_scan(root, result)
            self.assertIn("plugins/graphify-hook.json", scan["forbidden"])
            unreadable = root / "commands/binary.md"
            unreadable.parent.mkdir()
            unreadable.write_bytes(b"\xff\xfe")
            result = self.result()
            scan = CHECKER.repository_surface_scan(root, result)
            self.assertFalse(scan["complete"])
            self.assertIn("commands/binary.md", scan["unreadable"])

            checker = root / "scripts/graphify_baseline_check.py"
            checker.parent.mkdir(exist_ok=True)
            checker.write_text("# Graphify hook mutation\n", encoding="utf-8")
            result = self.result()
            self.assertIn("scripts/graphify_baseline_check.py", CHECKER.repository_surface_scan(root, result)["forbidden"])

            reference = root / ".agents/skills/local-review-gate/references/graphify-local-review.md"
            reference.parent.mkdir(parents=True, exist_ok=True)
            reference.write_text("Graphify hook mutation\n", encoding="utf-8")
            result = self.result()
            self.assertIn(str(reference.relative_to(root)), CHECKER.repository_surface_scan(root, result)["forbidden"])

            arbitrary = root / "scripts/arbitrary.py"
            arbitrary.write_bytes(b"\xff\xfe")
            result = self.result()
            scan = CHECKER.repository_surface_scan(root, result)
            self.assertFalse(scan["complete"])
            self.assertIn("scripts/arbitrary.py", scan["unreadable"])

            arbitrary.write_text("# do not graphify install --platform opencode\n", encoding="utf-8")
            result = self.result()
            self.assertIn("scripts/arbitrary.py", CHECKER.repository_surface_scan(root, result)["forbidden"])

    def test_recursive_marker_closure_queries_root_and_active_dependency(self):
        class Entry:
            group, name, value = "console_scripts", "graphify", "graphify.__main__:main"

        class Dist:
            files = []
            entry_points = [Entry()]
            def __init__(self, name, version, requires):
                self.metadata, self.version, self.requires = {"Name": name}, version, requires

        root = Dist("graphifyy", "0.9.12", ["active-dep>=1; python_version >= '3.10'", "inactive-dep; extra == 'cloud'"])
        dep = Dist("active-dep", "1.2.3", [])
        queries = []

        def fake_fetch(url, payload=None):
            queries.append(payload["package"]["name"])
            return {"vulns": []}, {"url": url}

        class Marker:
            def __init__(self, active):
                self.active = active
            def evaluate(self, environment):
                return self.active

        class Requirement:
            def __init__(self, raw):
                self.raw = raw
                self.name = raw.split(";", 1)[0].split(">", 1)[0].strip()
                self.marker = Marker("extra ==" not in raw) if ";" in raw else None
            def __str__(self):
                return self.raw

        packaging = types.ModuleType("packaging")
        markers = types.ModuleType("packaging.markers")
        markers.default_environment = lambda: {"python_version": "3.12"}
        requirements = types.ModuleType("packaging.requirements")
        requirements.Requirement = Requirement

        with tempfile.TemporaryDirectory() as temp:
            executable = Path(temp) / "graphify"
            executable.write_text("stub", encoding="utf-8")
            with mock.patch.dict(CHECKER.sys.modules, {"packaging": packaging, "packaging.markers": markers, "packaging.requirements": requirements}), \
                 mock.patch.object(CHECKER.shutil, "which", return_value=str(executable)), \
                 mock.patch.object(CHECKER.importlib.metadata, "distributions", return_value=[root]), \
                 mock.patch.object(CHECKER.importlib.metadata, "distribution", side_effect=lambda name: dep if name == "active-dep" else (_ for _ in ()).throw(CHECKER.importlib.metadata.PackageNotFoundError(name))), \
                 mock.patch.object(CHECKER, "fetch", side_effect=fake_fetch):
                _, report, _, _ = CHECKER.installed_closure_evidence()
        self.assertEqual([row["name"] for row in report["closure"]], ["graphifyy", "active-dep"])
        self.assertEqual(queries, ["graphifyy", "active-dep"])

    def test_sandbox_has_only_explicit_mounts_and_full_namespace_isolation(self):
        runtime = CHECKER.RuntimeMounts(
            readonly=(Path("/runtime/python"), Path("/runtime/graphify"), Path("/runtime/lib.so")),
            masked=(Path("/runtime/site-packages"),),
        )
        command = CHECKER.sandbox_command(
            Path("/runtime/bwrap"),
            Path("/target weird;$(literal)\nΔ"),
            Path("/output weird"),
            [Path("/private/home")],
            ["/runtime/graphify", "extract", "/target weird;$(literal)\nΔ"],
            runtime,
        )
        self.assertNotIn(["--ro-bind", "/", "/"], [command[i : i + 3] for i in range(len(command) - 2)])
        for flag in ("--unshare-user", "--unshare-pid", "--unshare-ipc", "--unshare-uts", "--unshare-net", "--proc", "--dev"):
            self.assertIn(flag, command)
        self.assertEqual(command[-3:], ["/runtime/graphify", "extract", "/target weird;$(literal)\nΔ"])

    def test_security_mode_separates_pinned_provenance_from_current_evidence(self):
        evidence = CHECKER.security_result()
        with mock.patch.object(CHECKER, "collect_pinned_provenance", return_value={"exact": True}), \
             mock.patch.object(CHECKER, "collect_current_security", return_value={"complete": False, "blocked": ["stale"]}), \
             mock.patch.object(CHECKER, "installed_closure_evidence", return_value=(None, {"complete": False}, ["missing install"], [])):
            code, result = CHECKER.security_evidence(CHECKER.argparse.Namespace(
                version=CHECKER.BASELINE["version"], commit=CHECKER.BASELINE["commit"], profile="strict-local"
            ))
        self.assertEqual(code, 3)
        self.assertTrue(result["package_metadata"]["pinned_provenance"]["exact"])
        self.assertIn("stale", " ".join(result["blocked"]))
        self.assertIn("missing install", " ".join(result["blocked"]))

    def test_current_security_requires_explicit_baseline_support(self):
        def fake_fetch(url, payload=None):
            if url == CHECKER.URLS["current_security"]:
                return "| 0.1.x | Yes |", {"url": url}
            if url == CHECKER.URLS["current_ci"]:
                return "security-scan:\n  pip-audit\n  bandit", {"url": url}
            return [], {"url": url}

        with mock.patch.object(CHECKER, "fetch", side_effect=fake_fetch):
            current = CHECKER.collect_current_security()
        self.assertFalse(current["support"]["baseline_supported_explicitly"])
        self.assertFalse(current["complete"])
        self.assertIn("does not explicitly support", " ".join(current["blocked"]))

    def test_execute_modes_use_literal_argv_strict_env_output_and_verified_cleanup(self):
        fixture_args = dict(
            version=CHECKER.BASELINE["version"], commit=CHECKER.BASELINE["commit"], profile="strict-local",
            require_operation_permission=True, network_deny="required",
        )
        calls = []

        def fake_supervised(command, env, limiter, writable):
            calls.append((command, {"env": env, "limiter": limiter}))
            graph_index = command.index("--") + 1
            graph_argv = command[graph_index:]
            if graph_argv[4] == "cluster-only":
                Path(graph_argv[graph_argv.index("--graph") + 1]).parent.mkdir(parents=True, exist_ok=True)
                Path(graph_argv[graph_argv.index("--graph") + 1]).write_text("{}", encoding="utf-8")
            return {"returncode": 0, "stdout": b"ok", "stderr": b"", "captured_bytes": 2, "usage": CHECKER.writable_usage(writable), "violation": None}

        exact_security = (0, {"errors": [], "unverified": [], "dependencies": {"installed_closure": {"trusted_wheel_binding": {"complete": True}}}})
        runtime = CHECKER.RuntimeMounts(readonly=(Path("/runtime/graphify"), Path("/runtime/python")), masked=())
        common = (
            mock.patch.object(CHECKER, "contract_mode", return_value=(0, {"errors": [], "unverified": []})),
            mock.patch.object(CHECKER, "security_evidence", return_value=exact_security),
            mock.patch.object(CHECKER, "executable_preflight", return_value=(Path("/runtime/graphify"), {"exact": True}, None)),
            mock.patch.object(CHECKER, "bwrap_preflight", return_value=(Path("/runtime/bwrap"), {"canary": True})),
            mock.patch.object(CHECKER, "construct_runtime_mounts", return_value=(runtime, None)),
            mock.patch.object(CHECKER, "git_output_safety", side_effect=lambda target, output, result: {"checked": True, "source_repository_root": str(target), "tracked": False, "staged": False}),
            mock.patch.object(CHECKER, "run_supervised", side_effect=fake_supervised),
        )
        with common[0], common[1], common[2], common[3], common[4], common[5], common[6]:
            synthetic_args = CHECKER.argparse.Namespace(mode="execute-synthetic", target_root=None, output_root=None, **fixture_args)
            code, synthetic = CHECKER.execute_mode(synthetic_args, ROOT, FIXTURE)
            self.assertEqual(code, 0, synthetic)
            self.assertTrue(synthetic["process_started"])
            self.assertTrue(synthetic["temp_cleanup"]["complete"])
            self.assertEqual(synthetic["temp_cleanup"]["created"], synthetic["temp_cleanup"]["removed"])
            self.assertIn("$(literal)", synthetic["argv"][0][5])
            self.assertEqual(synthetic["argv"][0][1:4], ["-I", "-m", "graphify"])
            self.assertEqual(calls[-1][1]["env"]["GRAPHIFY_QUERY_LOG_DISABLE"], "1")
            self.assertIsNotNone(calls[-1][1]["limiter"])
            self.assertTrue(synthetic["launch_attempted"])

        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp, "repo weird;$(literal)\n图谱")
            target.mkdir()
            output = Path(temp, "private output")
            calls.clear()
            patches = (
                mock.patch.object(CHECKER, "contract_mode", return_value=(0, {"errors": [], "unverified": []})),
                mock.patch.object(CHECKER, "security_evidence", return_value=exact_security),
                mock.patch.object(CHECKER, "executable_preflight", return_value=(Path("/runtime/graphify"), {"exact": True}, None)),
                mock.patch.object(CHECKER, "bwrap_preflight", return_value=(Path("/runtime/bwrap"), {"canary": True})),
                mock.patch.object(CHECKER, "construct_runtime_mounts", return_value=(runtime, None)),
                mock.patch.object(CHECKER, "git_output_safety", return_value={"checked": True, "source_repository_root": str(target), "tracked": False, "staged": False}),
                mock.patch.object(CHECKER, "run_supervised", side_effect=fake_supervised),
            )
            with patches[0], patches[1], patches[2], patches[3], patches[4], patches[5], patches[6]:
                project_args = CHECKER.argparse.Namespace(mode="execute-project", target_root=str(target), output_root=str(output), **fixture_args)
                code, project = CHECKER.execute_mode(project_args, ROOT, FIXTURE)
            self.assertEqual(code, 0, project)
            self.assertEqual(project["argv"][0][5], str(target))
            self.assertTrue(output.exists())
            self.assertFalse(any(Path(item).exists() for item in project["temp_cleanup"]["removed"]))

    def test_launch_failure_does_not_claim_graphify_started_and_still_cleans(self):
        args = CHECKER.argparse.Namespace(
            mode="execute-synthetic", target_root=None, output_root=None,
            version=CHECKER.BASELINE["version"], commit=CHECKER.BASELINE["commit"], profile="strict-local",
            require_operation_permission=True, network_deny="required",
        )
        runtime = CHECKER.RuntimeMounts(readonly=(Path("/runtime/graphify"),), masked=())
        with mock.patch.object(CHECKER, "contract_mode", return_value=(0, {"errors": [], "unverified": []})), \
             mock.patch.object(CHECKER, "security_evidence", return_value=(0, {"errors": [], "unverified": []})), \
             mock.patch.object(CHECKER, "executable_preflight", return_value=(Path("/runtime/graphify"), {"exact": True}, None)), \
             mock.patch.object(CHECKER, "bwrap_preflight", return_value=(Path("/runtime/bwrap"), {"canary": True})), \
             mock.patch.object(CHECKER, "construct_runtime_mounts", return_value=(runtime, None)), \
             mock.patch.object(CHECKER, "git_output_safety", return_value={"checked": True, "source_repository_root": None, "tracked": False, "staged": False}), \
             mock.patch.object(CHECKER, "run_supervised", side_effect=OSError("stub launch failure")):
            code, result = CHECKER.execute_mode(args, ROOT, FIXTURE)
        self.assertEqual(code, 5)
        self.assertFalse(result["process_started"])
        self.assertTrue(result["temp_cleanup"]["complete"])
        self.assertFalse(any(Path(item).exists() for item in result["temp_cleanup"]["removed"]))

    def test_timeout_records_attempt_and_unknown_start_state(self):
        args = CHECKER.argparse.Namespace(
            mode="execute-synthetic", target_root=None, output_root=None,
            version=CHECKER.BASELINE["version"], commit=CHECKER.BASELINE["commit"], profile="strict-local",
            require_operation_permission=True, network_deny="required",
        )
        runtime = CHECKER.RuntimeMounts(readonly=(Path("/runtime/graphify"),), masked=())
        with mock.patch.object(CHECKER, "contract_mode", return_value=(0, {"errors": [], "unverified": []})), \
             mock.patch.object(CHECKER, "security_evidence", return_value=(0, {"errors": [], "unverified": []})), \
             mock.patch.object(CHECKER, "executable_preflight", return_value=(Path("/runtime/graphify"), {"exact": True}, None)), \
             mock.patch.object(CHECKER, "bwrap_preflight", return_value=(Path("/runtime/bwrap"), {"canary": True})), \
             mock.patch.object(CHECKER, "construct_runtime_mounts", return_value=(runtime, None)), \
             mock.patch.object(CHECKER, "git_output_safety", return_value={"checked": True, "source_repository_root": None, "tracked": False, "staged": False}), \
             mock.patch.object(CHECKER, "run_supervised", side_effect=subprocess.TimeoutExpired(["bwrap"], 930)):
            code, result = CHECKER.execute_mode(args, ROOT, FIXTURE)
        self.assertEqual(code, 5)
        self.assertTrue(result["launch_attempted"])
        self.assertIsNone(result["process_started"])
        self.assertTrue(result["temp_cleanup"]["complete"])

    def test_generated_launcher_is_never_in_executed_argv(self):
        class Entry:
            group, name, value = "console_scripts", "graphify", "graphify.__main__:main"

        class Dist:
            version = CHECKER.BASELINE["version"]
            metadata = {"Name": CHECKER.BASELINE["distribution"]}
            entry_points = [Entry()]

        with tempfile.TemporaryDirectory() as temp:
            interpreter = Path(temp) / "python"
            generated_launcher = Path(temp) / "graphify"
            interpreter.write_text("verified interpreter", encoding="utf-8")
            generated_launcher.write_text("untrusted generated launcher", encoding="utf-8")
            with mock.patch.object(CHECKER.shutil, "which", return_value=str(generated_launcher)), \
                 mock.patch.object(CHECKER.sys, "executable", str(interpreter)), \
                 mock.patch.object(CHECKER.importlib.metadata, "distributions", return_value=[Dist()]), \
                 mock.patch.object(CHECKER, "verify_record", return_value={"complete": True}):
                selected, report, error = CHECKER.executable_preflight(CHECKER.BASELINE["version"], True)
            self.assertIsNone(error)
            self.assertEqual(selected, interpreter)
            self.assertNotEqual(selected, generated_launcher)
        self.assertFalse(report["launcher_executed"])
        self.assertEqual(CHECKER.EXTRACT_TEMPLATE[:4], ["<verified-python-path>", "-I", "-m", "graphify"])
        self.assertNotIn("<graphify-realpath>", CHECKER.EXTRACT_TEMPLATE)

    def test_stream_and_cumulative_writable_quotas_fail_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            with mock.patch.dict(CHECKER.RESOURCE_LIMITS, {"captured_output_bytes": 1024}):
                supervised = CHECKER.run_supervised(
                    [sys.executable, "-c", "import sys; sys.stdout.write('x' * 4096)"],
                    {}, None, [root],
                )
            self.assertIn("stdout/stderr", supervised["violation"])
            payload = root / "payload"
            payload.write_bytes(b"12345")
            with mock.patch.dict(CHECKER.RESOURCE_LIMITS, {"writable_bytes": 4}):
                usage = CHECKER.writable_usage([root])
            self.assertFalse(usage["within_quota"])
            self.assertEqual(usage["byte_limit"], 4)


if __name__ == "__main__":
    unittest.main()
