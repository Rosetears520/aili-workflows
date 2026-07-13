import argparse
import importlib.util
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "upstream_reference_check", ROOT / "scripts" / "upstream_reference_check.py"
)
CHECKER = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(CHECKER)


class CatalogOutputTests(unittest.TestCase):
    def test_accepts_one_complete_catalog_document(self):
        payload = json.dumps(
            [{"name": "idea-refine", "location": "/repo/.agents/skills/idea-refine/SKILL.md"}]
        )
        self.assertEqual(CHECKER.parse_catalog_output(payload)[0]["name"], "idea-refine")

    def test_rejects_concatenated_noisy_truncated_and_malicious_output(self):
        invalid = (
            "[]\n[]",
            "log line\n[]",
            '[{"name":"idea-refine"',
            '[{"name":"idea-refine","location":"/repo/\\u0000bad"}]',
        )
        for payload in invalid:
            with self.subTest(payload=payload):
                with self.assertRaises(ValueError):
                    CHECKER.parse_catalog_output(payload)

    def test_requires_exact_canonical_routes_and_excludes_upstream_routes(self):
        root = Path("/repo")
        closures = [{"id": "addy-idea-refine", "canonical_skill": "idea-refine", "vendor_root": ".agents/skills/idea-refine/references/upstream/vendor/commit"}]
        valid = [{"name": "idea-refine", "location": "/repo/.agents/skills/idea-refine/SKILL.md"}]
        routes = CHECKER.validate_catalog_routes(valid, root, closures)
        self.assertEqual(routes, valid)

        mutations = (
            [],
            valid + [{"name": "upstream", "location": "/repo/.agents/skills/idea-refine/references/upstream/vendor/commit/SKILL.upstream.md"}],
            valid + [{"name": "unrelated", "location": "/repo/.agents/skills/other/references/upstream/SKILL.md"}],
            [{"name": "idea-refine", "location": "/repo/.agents/skills/other/SKILL.md"}],
        )
        for catalog in mutations:
            with self.subTest(catalog=catalog):
                with self.assertRaises(ValueError):
                    CHECKER.validate_catalog_routes(catalog, root, closures)


class CatalogTruncationWorkaroundTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.workspace = Path(self.temp.name)
        self.skill_root = self.workspace / "home" / ".agents" / "skills"
        for name in ("alpha", "beta", "gamma"):
            (self.skill_root / name).mkdir(parents=True)
        self.command = ["npm", "exec", "--", "opencode", "--pure", "debug", "skill"]

    def tearDown(self):
        self.temp.cleanup()

    @staticmethod
    def truncated(command, **kwargs):
        return CHECKER.subprocess.CompletedProcess(command, 0, "[" + " " * 65535, "")

    def test_retries_exact_truncation_in_batches_and_unions_results(self):
        calls = 0

        def run(command, **kwargs):
            nonlocal calls
            calls += 1
            if calls == 1:
                return self.truncated(command)
            visible = sorted(path.name for path in self.skill_root.iterdir())
            payload = [{"name": name, "location": str(self.skill_root / name / "SKILL.md")} for name in visible]
            return CHECKER.subprocess.CompletedProcess(command, 0, json.dumps(payload), "")

        with mock.patch.object(CHECKER.subprocess, "run", side_effect=run):
            catalog = CHECKER.collect_catalog(self.command, Path("/neutral"), {}, self.skill_root, self.workspace, batch_size=2)

        self.assertEqual([item["name"] for item in catalog], ["alpha", "beta", "gamma"])
        self.assertEqual(sorted(path.name for path in self.skill_root.iterdir()), ["alpha", "beta", "gamma"])
        self.assertEqual(calls, 3)

    def test_rejects_incomplete_batch_and_restores_all_directories(self):
        with mock.patch.object(CHECKER.subprocess, "run", side_effect=self.truncated):
            with self.assertRaisesRegex(ValueError, "batch catalog output is incomplete"):
                CHECKER.collect_catalog(self.command, Path("/neutral"), {}, self.skill_root, self.workspace, batch_size=2)
        self.assertEqual(sorted(path.name for path in self.skill_root.iterdir()), ["alpha", "beta", "gamma"])

    def test_restores_directories_when_batch_command_raises(self):
        responses = [self.truncated(self.command), CHECKER.subprocess.TimeoutExpired(self.command, 120)]
        with mock.patch.object(CHECKER.subprocess, "run", side_effect=responses):
            with self.assertRaises(CHECKER.subprocess.TimeoutExpired):
                CHECKER.collect_catalog(self.command, Path("/neutral"), {}, self.skill_root, self.workspace, batch_size=2)
        self.assertEqual(sorted(path.name for path in self.skill_root.iterdir()), ["alpha", "beta", "gamma"])

    def test_restoration_failure_blocks_even_after_successful_batches(self):
        calls = 0
        real_move = CHECKER.shutil.move

        def run(command, **kwargs):
            nonlocal calls
            calls += 1
            if calls == 1:
                return self.truncated(command)
            return CHECKER.subprocess.CompletedProcess(command, 0, "[]", "")

        def move(source, destination):
            if Path(source).parent.name == "catalog-hidden" and Path(source).name == "alpha":
                raise OSError("restore denied")
            return real_move(source, destination)

        with mock.patch.object(CHECKER.subprocess, "run", side_effect=run), \
             mock.patch.object(CHECKER.shutil, "move", side_effect=move):
            with self.assertRaisesRegex(ValueError, "catalog skill restoration failed"):
                CHECKER.collect_catalog(self.command, Path("/neutral"), {}, self.skill_root, self.workspace, batch_size=2)

    def test_rejects_conflicting_duplicate_routes(self):
        outputs = [
            self.truncated(self.command),
            CHECKER.subprocess.CompletedProcess(self.command, 0, json.dumps([{"name": "duplicate", "location": "/one"}]), ""),
            CHECKER.subprocess.CompletedProcess(self.command, 0, json.dumps([{"name": "duplicate", "location": "/two"}]), ""),
        ]
        with mock.patch.object(CHECKER.subprocess, "run", side_effect=outputs):
            with self.assertRaisesRegex(ValueError, "duplicate catalog route conflict"):
                CHECKER.collect_catalog(self.command, Path("/neutral"), {}, self.skill_root, self.workspace, batch_size=2)

    def test_rejects_upstream_route_found_only_in_a_late_batch(self):
        canonical = str(self.skill_root / "alpha" / "SKILL.md")
        outputs = [
            self.truncated(self.command),
            CHECKER.subprocess.CompletedProcess(self.command, 0, json.dumps([{"name": "alpha", "location": canonical}]), ""),
            CHECKER.subprocess.CompletedProcess(self.command, 0, json.dumps([{
                "name": "late-upstream",
                "location": str(self.skill_root / "gamma" / "references" / "upstream" / "SKILL.md"),
            }]), ""),
        ]
        with mock.patch.object(CHECKER.subprocess, "run", side_effect=outputs):
            catalog = CHECKER.collect_catalog(self.command, Path("/neutral"), {}, self.skill_root, self.workspace, batch_size=2)
        with self.assertRaisesRegex(ValueError, "excluded references/upstream"):
            CHECKER.validate_catalog_routes(
                catalog, Path("/repo"), [{"id": "upstream", "canonical_skill": "alpha"}], self.skill_root
            )


class PackageInspectionTests(unittest.TestCase):
    def test_npm_pack_uses_only_the_isolated_environment_allowlist(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "source"
            environment_root = Path(temp) / "environment"
            root.mkdir()
            completed = CHECKER.subprocess.CompletedProcess(
                ["/stub/npm"], 0,
                json.dumps([{"filename": "fixture.tgz", "files": [{"path": "package.json"}]}]),
                "",
            )
            ambient_secrets = {
                "NODE_AUTH_TOKEN": "must-not-leak",
                "HTTPS_PROXY": "http://credential@example.invalid",
                "AWS_SECRET_ACCESS_KEY": "must-not-leak",
            }
            with mock.patch.dict(os.environ, ambient_secrets), \
                 mock.patch.object(CHECKER.subprocess, "run", return_value=completed) as run:
                CHECKER._npm_pack_listing("/stub/npm", root, [], environment_root)

            environment = run.call_args.kwargs["env"]
            self.assertEqual(set(environment), CHECKER.BASE_ISOLATED_ENV_KEYS)
            self.assertTrue(ambient_secrets.keys().isdisjoint(environment))
            self.assertEqual(environment["HOME"], str(environment_root / "home"))
            self.assertEqual(environment["TMPDIR"], str(environment_root / "tmp"))

    def test_inspects_actual_source_tar_modes_without_normalizing(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "payload").mkdir()
            script = root / "payload" / "reference.sh"
            script.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
            script.chmod(0o755)
            (root / "package.json").write_text(
                json.dumps({"name": "mode-fixture", "version": "1.0.0", "files": ["payload/reference.sh"]}),
                encoding="utf-8",
            )
            result = CHECKER.output("test")
            CHECKER.verify_package(root, {"payload/reference.sh"}, {"payload/reference.sh": "0644"}, result)
            self.assertTrue(any("distribution tar mode mismatch" in item for item in result["errors"]))
            self.assertEqual(result["unverified"], [])
            evidence = next(item for item in result["modes"] if item["path"] == "payload/reference.sh")
            self.assertEqual(evidence["source_mode"], "0755")
            self.assertEqual(evidence["tar_mode"], "0755")
            self.assertTrue(result["temp_cleanup"]["complete"])

    def test_accepts_git_0644_intent_when_drvfs_reports_every_file_executable(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "payload").mkdir()
            script = root / "payload" / "reference.sh"
            script.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
            script.chmod(0o755)
            (root / "package.json").write_text(
                json.dumps({"name": "mode-fixture", "version": "1.0.0", "files": ["payload/reference.sh"]}),
                encoding="utf-8",
            )
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            subprocess.run(["git", "add", "package.json", "payload/reference.sh"], cwd=root, check=True)
            subprocess.run(["git", "update-index", "--chmod=-x", "payload/reference.sh"], cwd=root, check=True)
            result = CHECKER.output("test")
            with mock.patch.object(CHECKER, "filesystem_type", return_value="v9fs"):
                CHECKER.verify_package(root, {"payload/reference.sh"}, {"payload/reference.sh": "0644"}, result)
            self.assertEqual(result["errors"], [])
            evidence = next(item for item in result["modes"] if item["path"] == "payload/reference.sh")
            self.assertEqual(evidence["git_mode"], "100644")
            self.assertEqual(evidence["verification_basis"], "git-index-on-drvfs")
            self.assertFalse(evidence["local_tar_exact"])
            self.assertTrue(evidence["exact_non_executable"])

    def test_package_omission_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "package.json").write_text(
                json.dumps({"name": "missing-fixture", "version": "1.0.0", "files": ["other.txt"]}),
                encoding="utf-8",
            )
            (root / "other.txt").write_text("other", encoding="utf-8")
            result = CHECKER.output("test")
            CHECKER.verify_package(root, {"required.json"}, {}, result)
            self.assertTrue(any("package omits upstream data" in item for item in result["errors"]))

    def test_installs_the_inspected_archive_and_discovers_catalog_from_neutral_project(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "source"
            workspace = Path(temp) / "runtime"
            archive = Path(temp) / "rose-aili.tgz"
            root.mkdir()
            archive.write_bytes(b"controlled archive")
            closures = [{"id": "addy-idea-refine", "canonical_skill": "idea-refine", "vendor_root": ".agents/skills/idea-refine/references/upstream/vendor/commit"}]
            result = CHECKER.output("1.17.18")
            calls = []
            ambient_secrets = {
                "NODE_AUTH_TOKEN": "must-not-leak",
                "NPM_TOKEN": "must-not-leak",
                "HTTPS_PROXY": "http://credential@example.invalid",
                "AWS_SECRET_ACCESS_KEY": "must-not-leak",
                "GITHUB_TOKEN": "must-not-leak",
            }

            def run(command, **kwargs):
                calls.append((command, kwargs))
                if command[0] == "/stub/npm" and command[1] == "install":
                    self.assertEqual(Path(command[-1]), archive.resolve())
                    return CHECKER.subprocess.CompletedProcess(command, 0, "installed", "")
                if command[0].endswith("rose-aili"):
                    skill = workspace / "home" / ".agents" / "skills" / "idea-refine" / "SKILL.md"
                    skill.parent.mkdir(parents=True)
                    skill.write_text("canonical", encoding="utf-8")
                    return CHECKER.subprocess.CompletedProcess(command, 0, "{}", "")
                if command[-1] == "--version":
                    return CHECKER.subprocess.CompletedProcess(command, 0, "1.17.18\n", "")
                skill = workspace / "home" / ".agents" / "skills" / "idea-refine" / "SKILL.md"
                return CHECKER.subprocess.CompletedProcess(command, 0, json.dumps([{"name": "idea-refine", "location": str(skill)}]), "")

            with mock.patch.dict(os.environ, ambient_secrets), \
                 mock.patch.object(CHECKER.shutil, "which", return_value="/stub/npm"), \
                 mock.patch.object(CHECKER.subprocess, "run", side_effect=run):
                CHECKER.verify_catalog(root, archive, "1.17.18", closures, result, workspace)

            self.assertTrue(result["catalog_routes"]["checked"])
            self.assertEqual(result["errors"], [])
            self.assertEqual(result["unverified"], [])
            neutral = workspace / "neutral-project"
            self.assertTrue(all(Path(kwargs["cwd"]) == neutral for _, kwargs in calls))
            for _, kwargs in calls:
                environment = kwargs["env"]
                self.assertEqual(set(environment), CHECKER.CATALOG_ENV_KEYS)
                self.assertEqual(environment["HOME"], str(workspace / "home"))
                self.assertEqual(environment["TMPDIR"], str(workspace / "tmp"))
                self.assertEqual(environment["OPENCODE_HOME"], str(workspace / "config" / "opencode"))
                self.assertTrue(ambient_secrets.keys().isdisjoint(environment))
            self.assertFalse((workspace / "config" / "opencode" / "skills" / "idea-refine").exists())

    def test_catalog_rejects_canonical_route_under_opencode_home(self):
        root = Path("/repo")
        shared = Path("/isolated/home/.agents/skills")
        opencode_skills = Path("/isolated/opencode/skills")
        closures = [{"id": "addy-idea-refine", "canonical_skill": "idea-refine"}]
        catalogs = (
            [{"name": "idea-refine", "location": str(opencode_skills / "idea-refine" / "SKILL.md")}],
            [
                {"name": "idea-refine", "location": str(shared / "idea-refine" / "SKILL.md")},
                {"name": "addy-idea-refine", "location": str(opencode_skills / "addy-idea-refine" / "SKILL.md")},
            ],
        )
        for catalog in catalogs:
            with self.subTest(catalog=catalog):
                with self.assertRaisesRegex(ValueError, "OPENCODE_HOME/skills"):
                    CHECKER.validate_catalog_routes(catalog, root, closures, shared, opencode_skills)

    def test_catalog_install_timeout_is_unverified(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "source"
            workspace = Path(temp) / "runtime"
            archive = Path(temp) / "rose-aili.tgz"
            root.mkdir()
            archive.write_bytes(b"controlled archive")
            result = CHECKER.output("1.17.18")
            with mock.patch.object(CHECKER.shutil, "which", return_value="/stub/npm"), \
                 mock.patch.object(CHECKER.subprocess, "run", side_effect=CHECKER.subprocess.TimeoutExpired("npm", 120)):
                CHECKER.verify_catalog(root, archive, "1.17.18", [], result, workspace)
            self.assertEqual(result["errors"], [])
            self.assertTrue(any("temporary catalog unavailable" in item for item in result["unverified"]))


class MutationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        manifest = json.loads((ROOT / "manifests/upstream-references.json").read_text(encoding="utf-8"))
        paths = {
            "package.json",
            "manifests/upstream-references.json",
            "manifests/rose-aili.components.json",
            "docs/harness/fixtures/upstream-reference-fixtures.yaml",
            "scripts/upstream_reference_check.py",
        }
        for closure in manifest["closures"]:
            paths.add(closure["vendor_root"])
        for relative in paths:
            source = ROOT / relative
            target = self.root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            if source.is_dir():
                shutil.copytree(source, target)
            else:
                shutil.copy2(source, target)
        self.manifest = manifest
        self.remote = {}
        for closure in manifest["closures"]:
            repo = next(item for item in manifest["repositories"] if item["id"] == closure["repository_id"])
            for mapping in closure["mappings"]:
                self.remote[repo["raw_base"] + mapping["source_path"]] = (self.root / mapping["local_path"]).read_bytes()

    def tearDown(self):
        self.temp.cleanup()

    def run_check(self):
        args = argparse.Namespace(
            project=str(self.root), manifest="manifests/upstream-references.json",
            fixture="docs/harness/fixtures/upstream-reference-fixtures.yaml",
            opencode_version="1.17.18", verify_installed_catalog=False,
        )
        with mock.patch.object(CHECKER, "fetch", side_effect=lambda url: self.remote[url]), \
             mock.patch.object(CHECKER, "verify_package"):
            return CHECKER.check(args)

    def test_hash_license_closure_and_nested_skill_mutations_fail(self):
        first = self.manifest["closures"][0]
        mapped = self.root / first["mappings"][0]["local_path"]
        license_path = self.root / first["license_local_path"]
        vendor = self.root / first["vendor_root"]
        mutations = (
            (mapped, lambda path: path.write_bytes(path.read_bytes() + b"mutation")),
            (license_path, lambda path: path.write_text("bad license", encoding="utf-8")),
            (vendor / "extra.txt", lambda path: path.write_text("extra", encoding="utf-8")),
            (vendor / "nested" / "SKILL.md", lambda path: (path.parent.mkdir(parents=True), path.write_text("runnable", encoding="utf-8"))),
        )
        for path, mutate in mutations:
            with self.subTest(path=path):
                original = path.read_bytes() if path.exists() and path.is_file() else None
                original_mode = stat.S_IMODE(path.stat().st_mode) if path.exists() else None
                mutate(path)
                code, result = self.run_check()
                self.assertEqual(code, 5, result)
                if original is None:
                    if path.exists():
                        path.unlink()
                else:
                    path.write_bytes(original)
                    path.chmod(original_mode)

    def test_non_0644_manifest_mode_fails_distribution_policy(self):
        manifest_path = self.root / "manifests/upstream-references.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["closures"][0]["mappings"][0]["mode"] = "0755"
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        args = argparse.Namespace(
            project=str(self.root), manifest="manifests/upstream-references.json",
            fixture="docs/harness/fixtures/upstream-reference-fixtures.yaml",
            opencode_version="1.17.18", verify_installed_catalog=False,
        )
        with mock.patch.object(CHECKER, "fetch", side_effect=lambda url: self.remote[url]):
            code, result = CHECKER.check(args)
        self.assertEqual(code, 5, result)
        self.assertTrue(any("distribution mode policy" in item for item in result["errors"]))


if __name__ == "__main__":
    unittest.main()
