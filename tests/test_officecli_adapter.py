from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / ".agents" / "skills" / "pptx-generator" / "scripts"
sys.path.insert(0, str(SCRIPTS))

import build_workspace  # noqa: E402
import compile_plan  # noqa: E402
import emit_visual_review_packet  # noqa: E402
import init_workspace  # noqa: E402
import officecli_adapter  # noqa: E402
import render_with_officecli  # noqa: E402
import report_workspace_readiness  # noqa: E402
from workspace_core import WorkspaceError, canonical_json_bytes, sha256_bytes, sha256_file  # noqa: E402


def write_executable(path: Path, source: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(source, encoding="utf-8")
    path.chmod(0o755)
    return path


def read_json_lines(path: Path) -> list[dict[str, object]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def fake_officecli(path: Path, version: str = officecli_adapter.PINNED_VERSION) -> Path:
    return write_executable(
        path,
        f"""#!{sys.executable}
import json
import os
import pathlib
import shutil
import sys
args = sys.argv[1:]
log = os.environ.get("FAKE_OFFICECLI_LOG")
if log:
    with open(log, "a", encoding="utf-8") as stream:
        stream.write(json.dumps({{"argv": args, "skip_update": os.environ.get("OFFICECLI_SKIP_UPDATE")}}) + "\\n")
if args == ["--version"]:
    print("OfficeCLI {version}")
elif args and args[0] == "help":
    print("pptx validate view outline text issues screenshot batch save")
elif len(args) >= 2 and args[:2] == ["pptx", "batch"]:
    source = pathlib.Path(args[args.index("--input") + 1])
    source.write_bytes(source.read_bytes() + b"|patched")
    print("{{}}")
elif len(args) >= 2 and args[:2] == ["pptx", "save"]:
    source = pathlib.Path(args[args.index("--input") + 1])
    output = pathlib.Path(args[args.index("--output") + 1])
    output.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, output)
    print("{{}}")
elif "screenshot" in args:
    output = pathlib.Path(args[args.index("--output") + 1])
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(b"PNG:" + " ".join(args).encode("utf-8"))
    print("{{}}")
else:
    print(json.dumps({{"ok": True, "argv": args}}))
""",
    )


def fake_node(path: Path) -> Path:
    return write_executable(
        path,
        f"""#!{sys.executable}
import pathlib
import sys
args = sys.argv[1:]
output = pathlib.Path(args[args.index("--output") + 1])
output.parent.mkdir(parents=True, exist_ok=True)
output.write_bytes(b"BASE-PPTX")
""",
    )


def make_workspace(root: Path, *, patch: bool = True) -> None:
    if root.exists():
        if any(root.iterdir()):
            raise AssertionError("make_workspace requires an empty target")
        root.rmdir()
    init_workspace.initialize_workspace(root, "template-edit", "adapter-deck", "Adapter Deck")
    source = root / "sources" / "input.pptx"
    source.write_bytes(b"SOURCE-PPTX")
    manifest_path = root / "sources" / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["sources"][0]["path"] = "sources/input.pptx"
    manifest["sources"][0]["sha256"] = sha256_file(source)
    manifest_path.write_bytes(canonical_json_bytes(manifest))
    plan = (
        "# Adapter Deck — Per-Slide Content Plan\n\n"
        "Recommended topic: **Adapter Deck**\n"
        "Recommended slide count: **2**\n"
        "Expected duration: **5 minutes**\n"
        "Overall logic: **opening → decision**\n\n---\n\n"
        "## Slide 01: Opening\n<!-- slide-id: opening -->\n\n### 1. Layout\nCover\n\n### 2. Content\nOpen\n\n---\n\n"
        "## Slide 02: Decision\n<!-- slide-id: decision -->\n\n### 1. Layout\nDecision\n\n### 2. Content\nDecide\n"
    )
    (root / "per-slide-content-plan.md").write_text(plan, encoding="utf-8")
    compiled = compile_plan.compile_plan(root / "per-slide-content-plan.md", root / "outline.json", workspace_root=root)
    if compiled["status"] != "compiled":
        raise AssertionError(compiled)
    if patch:
        batch = {
            "operations": [
                {"id": "first-patch", "action": "set-transition"},
                {"id": "second-patch", "action": "set-metadata"},
            ]
        }
        (root / "patches" / "officecli-postbuild.batch.json").write_text(json.dumps(batch), encoding="utf-8")
    readiness = report_workspace_readiness.evaluate_workspace(root)
    if readiness["status"] != "ready":
        raise AssertionError(readiness)
    (root / "build" / "workspace-readiness.json").write_bytes(canonical_json_bytes(readiness))


class ProbeTests(unittest.TestCase):
    def test_override_then_managed_posix_and_windows_resolution(self):
        with tempfile.TemporaryDirectory() as temp:
            home = Path(temp) / "home"
            target = officecli_adapter.managed_target(home)
            managed = fake_officecli(target / "node_modules" / ".bin" / "officecli")
            override = fake_officecli(Path(temp) / "override" / "officecli")
            resolved = officecli_adapter.resolve_officecli_bin(
                home=home, environ={"OFFICECLI_BIN": str(override)}, platform_name="linux"
            )
            self.assertEqual(resolved["path"], str(override.absolute()))
            self.assertEqual(resolved["source"], "OFFICECLI_BIN")
            resolved = officecli_adapter.resolve_officecli_bin(home=home, environ={}, platform_name="linux")
            self.assertEqual(resolved["path"], str(managed.absolute()))
            windows = target / "node_modules" / ".bin" / "officecli.cmd"
            windows.write_text("@rem fake\n", encoding="utf-8")
            resolved = officecli_adapter.resolve_officecli_bin(home=home, environ={}, platform_name="win32")
            self.assertEqual(resolved["path"], str(windows.absolute()))

    def test_probe_reports_version_drift_and_sets_skip_update(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            binary = fake_officecli(root / "officecli", version="1.0.144")
            log = root / "officecli.log"
            env = {"OFFICECLI_BIN": str(binary), "FAKE_OFFICECLI_LOG": str(log), "PATH": os.environ.get("PATH", "")}
            result = officecli_adapter.probe_officecli(environ=env)
            self.assertTrue(result["present"])
            self.assertEqual(result["version"], "1.0.144")
            self.assertTrue(result["version_drift"])
            self.assertTrue(all(result["capabilities"].values()))
            calls = read_json_lines(log)
            self.assertTrue(all(call["skip_update"] == "1" for call in calls))
            self.assertTrue(all(call["argv"] == ["--version"] or call["argv"][0] == "help" for call in calls))

    def test_missing_and_drift_recovery_belong_to_aili_installer(self):
        with tempfile.TemporaryDirectory() as temp:
            resolution = officecli_adapter.resolve_officecli_bin(home=Path(temp), environ={})
            self.assertIn("rose-aili install or update", resolution["error"]["message"])
            drifted = fake_officecli(Path(temp) / "officecli", version="1.0.144")
            with self.assertRaisesRegex(
                officecli_adapter.OfficeCLIAdapterError,
                "rose-aili install or update without --skip-officecli",
            ):
                officecli_adapter.require_pinned_officecli(environ={"OFFICECLI_BIN": str(drifted)})

    def test_forbidden_skill_mcp_and_install_commands_are_rejected(self):
        for argv in (
            ["/fake/officecli", "install"],
            ["/fake/officecli", "skills", "install"],
            ["/fake/officecli", "mcp"],
            ["/fake/officecli", "load_skill", "pptx"],
        ):
            with self.subTest(argv=argv), self.assertRaises(officecli_adapter.OfficeCLIAdapterError):
                officecli_adapter.require_safe_officecli_argv(argv)


class BuildTests(unittest.TestCase):
    def test_rejects_command_strings_paths_unregistered_renderer_and_missing_readiness(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            make_workspace(root)
            binary = fake_officecli(root / "officecli")
            env = {"OFFICECLI_BIN": str(binary)}
            workspace_path = root / "workspace.json"
            workspace = json.loads(workspace_path.read_text(encoding="utf-8"))

            workspace["renderer"]["command"] = "node src/deck.js; rm -rf /"
            workspace_path.write_text(json.dumps(workspace), encoding="utf-8")
            with self.assertRaisesRegex(WorkspaceError, "forbidden command"):
                build_workspace.prepare_build_plan(root, node_bin="node", environ=env)

            workspace["renderer"] = {"kind": "shell", "entrypoint": "src/deck.js"}
            workspace_path.write_text(json.dumps(workspace), encoding="utf-8")
            with self.assertRaisesRegex(WorkspaceError, "not registered"):
                build_workspace.prepare_build_plan(root, node_bin="node", environ=env)

            workspace["renderer"] = {"kind": "pptxgenjs", "entrypoint": "../deck.js"}
            workspace_path.write_text(json.dumps(workspace), encoding="utf-8")
            with self.assertRaises(WorkspaceError):
                build_workspace.prepare_build_plan(root, node_bin="node", environ=env)

            workspace["renderer"]["entrypoint"] = "src/deck.js"
            workspace_path.write_text(json.dumps(workspace), encoding="utf-8")
            with self.assertRaises(WorkspaceError):
                build_workspace.prepare_build_plan(root, node_bin="node", environ=env, final_output="/tmp/out.pptx")

            (root / "build" / "workspace-readiness.json").unlink()
            with self.assertRaisesRegex(WorkspaceError, "missing"):
                build_workspace.prepare_build_plan(root, node_bin="node", environ=env)

    def test_registered_renderer_replays_batch_in_order_and_writes_current_hashes(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "workspace"
            root.mkdir()
            make_workspace(root)
            node = fake_node(Path(temp) / "bin" / "node")
            officecli = fake_officecli(Path(temp) / "bin" / "officecli")
            log = Path(temp) / "officecli.log"
            env = {
                "OFFICECLI_BIN": str(officecli),
                "FAKE_OFFICECLI_LOG": str(log),
                "PATH": os.environ.get("PATH", ""),
            }
            plan = build_workspace.prepare_build_plan(root, node_bin=str(node), environ=env)
            self.assertEqual(plan["renderer"]["kind"], "pptxgenjs")
            self.assertEqual(plan["postbuild"]["operation_order"], ["first-patch", "second-patch"])
            self.assertFalse(plan["shell"])
            self.assertTrue(all(isinstance(action["argv"], list) for action in plan["actions"]))
            report = build_workspace.execute_build_plan(plan, environ=env)
            self.assertEqual(report["status"], "succeeded")
            self.assertEqual(report["postbuild"]["operation_order"], ["first-patch", "second-patch"])
            self.assertEqual((root / "build" / "final.pptx").read_bytes(), b"BASE-PPTX|patched")
            self.assertEqual(report["final_pptx"]["sha256"], sha256_file(root / "build" / "final.pptx"))
            self.assertEqual(report["final_pptx"]["sha256"], report["validation"]["pptx_sha256"])
            families = [call["argv"][:2] for call in read_json_lines(log) if call["argv"] != ["--version"]]
            self.assertEqual(
                families,
                [
                    ["help", "pptx"],
                    ["pptx", "batch"],
                    ["help", "pptx"],
                    ["pptx", "save"],
                    ["help", "pptx"],
                    ["pptx", "validate"],
                ],
            )
            self.assertTrue(all(call["skip_update"] == "1" for call in read_json_lines(log)))

    def test_saved_readiness_and_officecli_version_drift_fail_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "workspace"
            root.mkdir()
            make_workspace(root)
            node = fake_node(Path(temp) / "bin" / "node")
            officecli = fake_officecli(Path(temp) / "bin" / "officecli")
            env = {"OFFICECLI_BIN": str(officecli), "PATH": os.environ.get("PATH", "")}
            (root / "design-contract.json").write_text("{}", encoding="utf-8")
            with self.assertRaisesRegex(WorkspaceError, "readiness"):
                build_workspace.prepare_build_plan(root, node_bin=str(node), environ=env)

        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "workspace"
            root.mkdir()
            make_workspace(root)
            node = fake_node(Path(temp) / "bin" / "node")
            drifted = fake_officecli(Path(temp) / "bin" / "officecli", version="1.0.144")
            env = {"OFFICECLI_BIN": str(drifted), "PATH": os.environ.get("PATH", "")}
            with self.assertRaisesRegex(officecli_adapter.OfficeCLIAdapterError, "Expected OfficeCLI"):
                build_workspace.prepare_build_plan(root, node_bin=str(node), environ=env)


class RenderAndReviewTests(unittest.TestCase):
    def test_render_packet_is_help_first_and_visual_packet_never_auto_passes(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "workspace"
            root.mkdir()
            make_workspace(root, patch=False)
            final = root / "build" / "final.pptx"
            final.write_bytes(b"FINAL-PPTX")
            officecli = fake_officecli(Path(temp) / "bin" / "officecli")
            log = Path(temp) / "officecli.log"
            env = {
                "OFFICECLI_BIN": str(officecli),
                "FAKE_OFFICECLI_LOG": str(log),
                "PATH": os.environ.get("PATH", ""),
            }
            packet = render_with_officecli.prepare_render_packet(root, environ=env)
            self.assertFalse(packet["completion_proof"])
            self.assertFalse(packet["watch_included"])
            actions = packet["actions"]
            for index, action in enumerate(actions):
                if action["kind"] == "command":
                    self.assertGreater(index, 0)
                    self.assertEqual(actions[index - 1]["kind"], "help")
                    self.assertEqual(actions[index - 1]["family"], action["family"])
                    self.assertIsInstance(action["argv"], list)

            manifest = render_with_officecli.execute_render_packet(packet, environ=env)
            self.assertEqual(manifest["slide_ids"], ["opening", "decision"])
            self.assertEqual(len(manifest["artifacts"]), 2)
            self.assertFalse(manifest["visual_review_passed"])
            self.assertTrue(all(call["skip_update"] == "1" for call in read_json_lines(log)))

            aggregate = [
                {"slide_id": item["slide_id"], "path": item["path"], "sha256": item["sha256"]}
                for item in manifest["artifacts"]
            ]
            aggregate.append(
                {
                    "slide_id": "_contact-sheet",
                    "path": manifest["contact_sheet"]["path"],
                    "sha256": manifest["contact_sheet"]["sha256"],
                }
            )
            self.assertEqual(manifest["render_sha256"], sha256_bytes(canonical_json_bytes(aggregate)))

            review = emit_visual_review_packet.emit_visual_review_packet(root)
            self.assertEqual(review["pptx_sha256"], manifest["pptx_sha256"])
            self.assertEqual(review["render_sha256"], manifest["render_sha256"])
            self.assertEqual(review["slide_ids"], ["opening", "decision"])
            self.assertEqual(review["disposition"], "unreviewed")
            self.assertFalse(review["auto_pass"])
            self.assertIsNone(review["reviewer"])
            self.assertIn("must open and inspect", review["host_action_required"])
            self.assertTrue(all("sha256" in item for item in review["render_files"]))
            stored = json.loads((root / "reviews" / "visual-review-final.json").read_text(encoding="utf-8"))
            self.assertNotEqual(stored.get("disposition"), "pass")

            proof_packet = render_with_officecli.prepare_render_packet(
                root,
                render_root="renders/style-proof",
                manifest_path="renders/style-proof/manifest.json",
                slide_ids=["decision"],
                environ=env,
            )
            self.assertEqual(proof_packet["slide_ids"], ["decision"])
            self.assertEqual(proof_packet["manifest_path"], "renders/style-proof/manifest.json")

    def test_render_paths_are_confined(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "workspace"
            root.mkdir()
            make_workspace(root, patch=False)
            (root / "build" / "final.pptx").write_bytes(b"FINAL")
            binary = fake_officecli(Path(temp) / "officecli")
            env = {"OFFICECLI_BIN": str(binary)}
            with self.assertRaises(WorkspaceError):
                render_with_officecli.prepare_render_packet(root, render_root="../outside", environ=env)
            with self.assertRaises(WorkspaceError):
                render_with_officecli.prepare_render_packet(root, pptx="/tmp/final.pptx", environ=env)


if __name__ == "__main__":
    unittest.main()
