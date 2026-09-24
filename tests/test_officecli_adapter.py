from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest import mock
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / ".agents" / "skills" / "pptx-generator" / "scripts"
sys.path.insert(0, str(SCRIPTS))

import build_workspace  # noqa: E402
import compile_plan  # noqa: E402
import emit_visual_review_packet  # noqa: E402
import init_workspace  # noqa: E402
import officecli_adapter  # noqa: E402
import profile_template  # noqa: E402
import report_layout_preflight  # noqa: E402
import render_with_officecli  # noqa: E402
import report_workspace_readiness  # noqa: E402
from workspace_core import WorkspaceError, canonical_json_bytes, current_template_style_bindings, sha256_bytes, sha256_file  # noqa: E402


def write_executable(path: Path, source: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(source, encoding="utf-8")
    path.chmod(0o755)
    return path


def read_json_lines(path: Path) -> list[dict[str, object]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def write_minimal_pptx(path: Path, text: str = "Editable text", slide_count: int = 1) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    slide_ids = ''.join(f'<p:sldId id="{256 + i}"/>' for i in range(slide_count))
    presentation = f'<p:presentation xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"><p:sldIdLst>{slide_ids}</p:sldIdLst><p:sldSz cx="9144000" cy="5143500" type="screen16x9"/></p:presentation>'
    slide = f'''<p:sld xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"><p:cSld><p:spTree><p:sp><p:nvSpPr><p:cNvPr id="2" name="Text 1"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr><p:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="1000000" cy="500000"/></a:xfrm><a:prstGeom prst="rect"/></p:spPr><p:txBody><a:bodyPr/><a:lstStyle/><a:p><a:r><a:rPr sz="2000"><a:latin typeface="Test Sans"/></a:rPr><a:t>{text}</a:t></a:r></a:p></p:txBody></p:sp></p:spTree></p:cSld></p:sld>'''
    theme = '<a:theme xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" name="Test"><a:themeElements><a:clrScheme name="Test"><a:accent1><a:srgbClr val="112233"/></a:accent1></a:clrScheme><a:fontScheme name="Test"><a:majorFont><a:latin typeface="Test Sans"/><a:ea typeface=""/></a:majorFont><a:minorFont><a:latin typeface="Test Sans"/><a:ea typeface=""/></a:minorFont></a:fontScheme><a:fmtScheme name="Test"/></a:themeElements></a:theme>'
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("ppt/presentation.xml", presentation)
        for index in range(1, slide_count + 1):
            archive.writestr(f"ppt/slides/slide{index}.xml", slide)
        archive.writestr("ppt/theme/theme1.xml", theme)
    return path


SCREENSHOT_HELP = "officecli view <file> screenshot --page <page> --out <path> --grid N --screenshot-width W --screenshot-height H"


def fake_officecli(
    path: Path,
    version: str = officecli_adapter.PINNED_VERSION,
    view_help: str = SCREENSHOT_HELP,
) -> Path:
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
elif args and (args[0] == "screenshot" or any(flag in args for flag in ("--slide", "--output", "--contact-sheet"))):
    sys.exit(2)
elif args == ["view", "--help"]:
    print({view_help!r})
elif args in (["validate", "--help"], ["batch", "--help"]):
    print("validate batch")
elif args and args[0] == "batch":
    source = pathlib.Path(args[1])
    source.write_bytes(source.read_bytes() + b"|patched")
    print("{{}}")
elif len(args) >= 3 and args[0] == "view" and args[2] == "screenshot":
    if args[3] == "--page":
        if len(args) != 7 or args[5] != "--out" or not args[4].isdigit() or int(args[4]) < 1:
            sys.exit(2)
    elif args[3] == "--grid":
        if len(args) != 11 or args[5] != "--screenshot-width" or args[7] != "--screenshot-height" or args[9] != "--out":
            sys.exit(2)
        if any(not args[i].isdigit() or int(args[i]) < 1 for i in (4, 6, 8)):
            sys.exit(2)
    else:
        sys.exit(2)
    output = pathlib.Path(args[-1])
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(b"PNG:" + " ".join(args).encode("utf-8"))
    print("{{}}")
else:
    print(json.dumps({{"ok": True, "argv": args}}))
""",
    )


def fake_node(path: Path, presentation: str | None = None, content_types: str | None = None, slide: str | None = None) -> Path:
    return write_executable(
        path,
        f"""#!{sys.executable}
import pathlib
import sys
import zipfile
args = sys.argv[1:]
output = pathlib.Path(args[args.index("--output") + 1])
output.parent.mkdir(parents=True, exist_ok=True)
slide = {slide!r} or '<p:sld xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"><p:cSld><p:spTree><p:sp><p:nvSpPr><p:cNvPr id="2" name="Text"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr><p:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="1000000" cy="500000"/></a:xfrm></p:spPr><p:txBody><a:bodyPr/><a:lstStyle/><a:p><a:r><a:t>Text</a:t></a:r></a:p></p:txBody></p:sp></p:spTree></p:cSld></p:sld>'
with zipfile.ZipFile(output, "w") as archive:
    archive.writestr("ppt/slides/slide1.xml", slide)
    if {presentation!r} is not None:
        archive.writestr("ppt/presentation.xml", {presentation!r})
    if {content_types!r} is not None:
        archive.writestr("[Content_Types].xml", {content_types!r})
""",
    )


def make_workspace(root: Path, *, patch: bool = True) -> None:
    if root.exists():
        if any(root.iterdir()):
            raise AssertionError("make_workspace requires an empty target")
        root.rmdir()
    init_workspace.initialize_workspace(root, "template-edit", "adapter-deck", "Adapter Deck")
    source = root / "sources" / "input.pptx"
    write_minimal_pptx(source)
    manifest_path = root / "sources" / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["sources"][0]["path"] = "sources/input.pptx"
    manifest["sources"][0]["sha256"] = sha256_file(source)
    manifest["sources"][0]["user_decision"] = "confirmed"
    manifest_path.write_bytes(canonical_json_bytes(manifest))
    intake_path = root / "intake.json"
    intake = json.loads(intake_path.read_text(encoding="utf-8"))
    intake["visual_references"][0].update({"path": "sources/input.pptx", "sha256": sha256_file(source), "user_decision": "confirmed"})
    intake_path.write_bytes(canonical_json_bytes(intake))
    profile = profile_template.profile_template(source)
    profile["source"]["path"] = "sources/input.pptx"
    (root / "template-profile.json").write_bytes(canonical_json_bytes(profile))
    font_contract_path = root / "font-contract.json"
    font_contract = json.loads(font_contract_path.read_text(encoding="utf-8"))
    font_contract["template_profile_sha256"] = sha256_file(root / "template-profile.json")
    font_contract["fonts"] = [{"role": "template-run", "family": "Test Sans", "required": True, "fallback_allowed": False, "source": "controlling-template", "template_run_ids": ["slide-01/2/p1/r1"]}]
    font_contract_path.write_bytes(canonical_json_bytes(font_contract))
    font_environment_path = root / "font-environment.json"
    font_environment = json.loads(font_environment_path.read_text(encoding="utf-8"))
    font_environment["status"] = "ready"
    font_environment["external_reads"] = {"approval_state": "not-required", "requested_paths": [], "observed_paths": []}
    for name in ("build", "render"):
        font_environment["environments"][name].update({"status": "verified", "renderer": f"test-{name}", "visible_fonts": ["Test Sans"]})
    font_environment_path.write_bytes(canonical_json_bytes(font_environment))
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
    (root / "build" / "font-audit.json").write_bytes(canonical_json_bytes(readiness["font_audit"]))
    proof = write_minimal_pptx(root / "build" / "style-proof.pptx", "Proof")
    proof_slide = root / "renders" / "style-proof" / "slides" / "opening.png"
    proof_slide.parent.mkdir(parents=True, exist_ok=True)
    proof_slide.write_bytes(b"PROOF")
    proof_contact = root / "renders" / "style-proof" / "contact-sheet.png"
    proof_contact.write_bytes(b"CONTACT")
    aggregate = [
        {"slide_id": "opening", "path": "renders/style-proof/slides/opening.png", "sha256": sha256_file(proof_slide)},
        {"slide_id": "_contact-sheet", "path": "renders/style-proof/contact-sheet.png", "sha256": sha256_file(proof_contact)},
    ]
    render = {
        "pptx_sha256": sha256_file(proof), "slide_ids": ["opening"], "artifacts": [aggregate[0]],
        "contact_sheet": {"path": aggregate[1]["path"], "sha256": aggregate[1]["sha256"]},
        "render_sha256": sha256_bytes(canonical_json_bytes(aggregate)),
    }
    (root / "renders" / "style-proof" / "manifest.json").write_bytes(canonical_json_bytes(render))
    baseline_slide = root / "renders" / "style-proof" / "baseline" / "slides" / "opening.png"
    baseline_slide.parent.mkdir(parents=True, exist_ok=True)
    baseline_slide.write_bytes(b"BASELINE-PROOF")
    baseline_contact = root / "renders" / "style-proof" / "baseline" / "contact-sheet.png"
    baseline_contact.write_bytes(b"BASELINE-CONTACT")
    baseline_aggregate = [
        {"slide_id": "opening", "path": "renders/style-proof/baseline/slides/opening.png", "sha256": sha256_file(baseline_slide)},
        {"slide_id": "_contact-sheet", "path": "renders/style-proof/baseline/contact-sheet.png", "sha256": sha256_file(baseline_contact)},
    ]
    baseline_render = {
        "pptx_sha256": sha256_file(source), "slide_ids": ["opening"], "artifacts": [baseline_aggregate[0]],
        "contact_sheet": {"path": baseline_aggregate[1]["path"], "sha256": baseline_aggregate[1]["sha256"]},
        "render_sha256": sha256_bytes(canonical_json_bytes(baseline_aggregate)),
    }
    (root / "renders" / "style-proof" / "baseline" / "manifest.json").write_bytes(canonical_json_bytes(baseline_render))
    style_issues = {"schema_version": "1.0", "report_kind": "officecli-issues", "pptx_sha256": sha256_file(proof), "count": 0, "issues": []}
    style_layout = {"schema_version": "1.0", "report_kind": "layout-evidence", "pptx_sha256": sha256_file(proof), "slide_size": {}, "shapes": [], "alignment_groups": [], "issue_dispositions": {}}
    (root / "build" / "style-proof-officecli-issues.json").write_bytes(canonical_json_bytes(style_issues))
    (root / "build" / "style-proof-layout-evidence.json").write_bytes(canonical_json_bytes(style_layout))
    style_preflight = report_layout_preflight.evaluate_layout_preflight(
        final_pptx_sha256=sha256_file(proof),
        template_profile_sha256=sha256_file(root / "template-profile.json"),
        font_audit_sha256=sha256_file(root / "build" / "font-audit.json"),
        issues_sha256=sha256_file(root / "build" / "style-proof-officecli-issues.json"),
        layout_evidence_sha256=sha256_file(root / "build" / "style-proof-layout-evidence.json"),
        layout_evidence=style_layout,
        issues=style_issues,
        render_sha256=render["render_sha256"],
    )
    (root / "build" / "style-proof-layout-preflight.json").write_bytes(canonical_json_bytes(style_preflight))
    checks = {"alignment": "pass", "spacing": "pass", "text_wrap": "pass", "overflow": "pass", "image_aspect": "not-applicable", "font_rendering": "pass", "reference_fidelity": "pass"}
    review = {
        "review_scope": "style-proof", "reviewer": "fixture-reviewer", "disposition": "pass",
        "pptx_sha256": sha256_file(proof), "render_sha256": render["render_sha256"], "slide_ids": ["opening"], "findings": [],
        "pages": [{"slide_id": "opening", "inspection_status": "inspected", "checks": checks, "observations": ["Fixture proof reviewed."]}],
    }
    (root / "reviews" / "style-proof-review.json").write_bytes(canonical_json_bytes(review))
    bindings = current_template_style_bindings(root)
    confirmation = {
        "schema_version": "1.0", "report_kind": "template-style-confirmation", "status": "confirmed", "confirmed_by": "fixture-user",
        "proof_hash": sha256_bytes(canonical_json_bytes(bindings)),
        "role_coverage": {"image-or-chart": "opening", "longest-text": "opening", "densest-numeric": "opening"},
        "bindings": bindings,
    }
    (root / "reviews" / "template-style-confirmation.json").write_bytes(canonical_json_bytes(confirmation))


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
            self.assertTrue(all(result["capabilities"][name] for name in ("read", "validate", "render", "batch")))
            self.assertFalse(result["capabilities"]["save"])
            calls = read_json_lines(log)
            self.assertTrue(all(call["skip_update"] == "1" for call in calls))
            self.assertTrue(all(call["argv"] == ["--version"] or call["argv"][-1] == "--help" for call in calls))

    def test_screenshot_argv_and_help_use_view(self):
        self.assertEqual(
            officecli_adapter.officecli_help_argv("officecli", "screenshot"),
            ["officecli", "view", "--help"],
        )
        with tempfile.TemporaryDirectory() as temp:
            document = str(write_minimal_pptx(Path(temp) / "deck with spaces.pptx", slide_count=2))
            for kwargs, flags in (
                ({"slide": 2}, ["--page", "2"]),
                ({"contact_sheet": True}, ["--grid", "2", "--screenshot-width", "1600", "--screenshot-height", "1200"]),
            ):
                with self.subTest(kwargs=kwargs):
                    self.assertEqual(
                        officecli_adapter.officecli_command_argv(
                            "officecli", "screenshot", document, output="render.png", **kwargs
                        ),
                        ["officecli", "view", document, "screenshot", *flags, "--out", "render.png"],
                    )

    def test_probe_requires_screenshot_and_required_flags_in_view_help(self):
        help_texts = ["view outline text issues"] + [
            SCREENSHOT_HELP.replace(token, "unsupported")
            for token in ("screenshot", "--page", "--out", "--grid", "--screenshot-width", "--screenshot-height")
        ] + [SCREENSHOT_HELP.replace("--out", "--output")]
        with tempfile.TemporaryDirectory() as temp:
            for help_text in help_texts:
                with self.subTest(help_text=help_text):
                    binary = fake_officecli(Path(temp) / "officecli", view_help=help_text)
                    result = officecli_adapter.probe_officecli(environ={"OFFICECLI_BIN": str(binary)})
                    self.assertTrue(result["capabilities"]["read"])
                    self.assertFalse(result["capabilities"]["render"])
                    query = next(item for item in result["queries"] if item["name"] == "help:screenshot")
                    self.assertEqual(query["argv"], [str(binary), "view", "--help"])
                    self.assertEqual(query["returncode"], 0)

    def test_fake_cli_rejects_obsolete_screenshot_syntax(self):
        with tempfile.TemporaryDirectory() as temp:
            binary = fake_officecli(Path(temp) / "officecli")
            for args in (
                ["screenshot", "--help"],
                ["screenshot", "deck.pptx", "--output", "render.png"],
                ["view", "deck.pptx", "screenshot", "--slide", "1", "--out", "render.png"],
                ["view", "deck.pptx", "screenshot", "--contact-sheet", "--out", "render.png"],
                ["view", "deck.pptx", "screenshot", "--page", "1", "--output", "render.png"],
            ):
                with self.subTest(args=args):
                    self.assertNotEqual(officecli_adapter.run_officecli([str(binary), *args]).returncode, 0)

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


class OrphanSlideMasterOverrideTests(unittest.TestCase):
    NS = "http://schemas.openxmlformats.org/package/2006/content-types"
    TYPE = "application/vnd.openxmlformats-officedocument.presentationml.slideMaster+xml"

    @classmethod
    def content_types(cls):
        declarations = [
            ("/ppt/slideMasters/slideMaster1.xml", cls.TYPE),
            ("/ppt/slideMasters/slideMaster2.xml", cls.TYPE),
            ("/ppt/slideMasters/slideMaster3.xml", cls.TYPE),
            ("/ppt/slides/slide99.xml", "application/vnd.openxmlformats-officedocument.presentationml.slide+xml"),
            ("/ppt/slideMasters/slideMaster4.xml", "different-content-type"),
            ("/ppt/slideMasters/custom.xml", cls.TYPE),
        ]
        return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                f'<Types xmlns="{cls.NS}"><!--keep--><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
                + ''.join(f'<Override PartName="{name}" ContentType="{kind}"/>' for name, kind in declarations)
                + '</Types>')

    def test_only_orphan_numbered_master_overrides_removed_and_members_preserved(self):
        with tempfile.TemporaryDirectory() as temp:
            package = Path(temp) / "deck.pptx"
            members = {
                "[Content_Types].xml": self.content_types().encode(),
                "ppt/slideMasters/slideMaster1.xml": b"existing master",
                "ppt/slides/slide1.xml": b"unchanged text and geometry",
                "ppt/media/image.png": bytes(range(256)),
                "ppt/_rels/presentation.xml.rels": b'<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="master" Target="slideMasters/slideMaster1.xml"/><Relationship Id="rId2" Type="external" Target="slideMasters/slideMaster2.xml" TargetMode="External"/></Relationships>',
            }
            with zipfile.ZipFile(package, "w") as archive:
                archive.comment = b"archive comment"
                for name, payload in members.items():
                    info = zipfile.ZipInfo(name, (2024, 1, 2, 3, 4, 6))
                    info.compress_type = zipfile.ZIP_DEFLATED
                    info.comment = b"member comment"
                    info.external_attr = 0o100644 << 16
                    archive.writestr(info, payload)
            self.assertTrue(build_workspace.normalize_orphan_slide_master_overrides(package))
            with zipfile.ZipFile(package) as archive:
                self.assertEqual(archive.namelist(), list(members))
                self.assertEqual(archive.comment, b"archive comment")
                for info in archive.infolist():
                    self.assertEqual(info.date_time, (2024, 1, 2, 3, 4, 6))
                    self.assertEqual(info.compress_type, zipfile.ZIP_DEFLATED)
                    self.assertEqual(info.comment, b"member comment")
                    self.assertEqual(info.external_attr, 0o100644 << 16)
                    if info.filename != "[Content_Types].xml":
                        self.assertEqual(archive.read(info), members[info.filename])
                changed = archive.read("[Content_Types].xml")
            original = ET.fromstring(members["[Content_Types].xml"])
            expected = [ET.tostring(node) for node in original
                        if node.get("PartName") not in {"/ppt/slideMasters/slideMaster2.xml", "/ppt/slideMasters/slideMaster3.xml"}]
            self.assertEqual([ET.tostring(node) for node in ET.fromstring(changed)], expected)
            self.assertIn(b"<!--keep-->", changed)
            normalized = package.read_bytes()
            self.assertFalse(build_workspace.normalize_orphan_slide_master_overrides(package))
            self.assertEqual(package.read_bytes(), normalized)

    def test_referenced_missing_masters_remain_declared_byte_identical(self):
        cases = [
            ("ppt/_rels/presentation.xml.rels", "slideMasters/slideMaster2.xml"),
            ("ppt/slideLayouts/_rels/slideLayout1.xml.rels", "../slideMasters/slideMaster2.xml"),
            ("_rels/.rels", "/ppt/slideMasters/slideMaster2.xml"),
            ("ppt/_rels/presentation.xml.rels", "slideMasters/%73lideMaster2.xml#fragment"),
        ]
        for relationship_part, target in cases:
            with self.subTest(target=target), tempfile.TemporaryDirectory() as temp:
                package = Path(temp) / "deck.pptx"
                with zipfile.ZipFile(package, "w") as archive:
                    archive.writestr("[Content_Types].xml", f'<Types xmlns="{self.NS}"><Override PartName="/ppt/slideMasters/slideMaster2.xml" ContentType="{self.TYPE}"/></Types>')
                    archive.writestr(relationship_part, f'<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="master" Target="{target}"/></Relationships>')
                original = package.read_bytes()
                self.assertFalse(build_workspace.normalize_orphan_slide_master_overrides(package))
                self.assertEqual(package.read_bytes(), original)

    def test_existing_master_and_absent_content_types_are_byte_identical_noops(self):
        for declared in (False, True):
            with self.subTest(declared=declared), tempfile.TemporaryDirectory() as temp:
                package = Path(temp) / "deck.pptx"
                with zipfile.ZipFile(package, "w") as archive:
                    archive.writestr("ppt/slideMasters/slideMaster2.xml", b"master")
                    if declared:
                        archive.writestr("[Content_Types].xml", f'<Types xmlns="{self.NS}"><Override PartName="/ppt/slideMasters/slideMaster2.xml" ContentType="{self.TYPE}"/></Types>')
                original = package.read_bytes()
                self.assertFalse(build_workspace.normalize_orphan_slide_master_overrides(package))
                self.assertEqual(package.read_bytes(), original)


class SlideOoxmlCompletionTests(unittest.TestCase):
    P = "http://schemas.openxmlformats.org/presentationml/2006/main"
    A = "http://schemas.openxmlformats.org/drawingml/2006/main"
    R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
    NS = {"p": P, "a": A}

    @classmethod
    def incomplete_slide(cls):
        return (f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                f'<p:sld xmlns:p="{cls.P}" xmlns:d="{cls.A}" xmlns:r="{cls.R}">'
                '<p:cSld><p:bg><p:bgPr shadeToTitle="1"><d:solidFill><d:srgbClr val="AABBCC"/></d:solidFill>'
                '<d:extLst><d:ext uri="keep"/></d:extLst></p:bgPr></p:bg>'
                '<p:spTree><!--keep slide comment-->'
                '<p:sp><p:nvSpPr><p:cNvPr id="2" name="Empty"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
                '<p:spPr><d:xfrm><d:off x="123" y="456"/><d:ext cx="1000000" cy="500000"/></d:xfrm>'
                '<d:prstGeom prst="rect"/></p:spPr><p:style><d:lnRef idx="0"/></p:style>'
                '<p:extLst><p:ext uri="keep" r:id="rId1"/></p:extLst></p:sp>'
                '<p:sp><p:nvSpPr><p:cNvPr id="3" name="Existing"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
                '<p:spPr/><p:txBody><d:bodyPr/><d:lstStyle/><d:p><d:r><d:t>Keep exact text</d:t>'
                '</d:r></d:p></p:txBody></p:sp>'
                '</p:spTree></p:cSld><p:clrMapOvr><d:masterClrMapping/></p:clrMapOvr></p:sld>')

    @classmethod
    def complete_slide(cls):
        return (f'<p:sld xmlns:p="{cls.P}" xmlns:d="{cls.A}"><p:cSld><p:bg><p:bgPr>'
                '<d:solidFill><d:srgbClr val="112233"/></d:solidFill><d:effectLst/></p:bgPr></p:bg>'
                '<p:spTree><p:sp><p:spPr/><p:txBody><d:bodyPr/><d:lstStyle/><d:p/></p:txBody></p:sp>'
                '</p:spTree></p:cSld></p:sld>')

    def assert_completed(self, package):
        with zipfile.ZipFile(package) as archive:
            slide = ET.fromstring(archive.read("ppt/slides/slide1.xml"))
        shapes = slide.findall(".//p:sp", self.NS)
        self.assertEqual(len(shapes), 2)
        body = shapes[0].find("p:txBody", self.NS)
        self.assertIsNotNone(body)
        self.assertEqual([child.tag for child in body], [f"{{{self.A}}}{name}" for name in ("bodyPr", "lstStyle", "p")])
        self.assertEqual(body.find("a:p/a:endParaRPr", self.NS).get("lang"), "en-US")
        self.assertEqual([child.tag.rsplit("}", 1)[-1] for child in shapes[0]], ["nvSpPr", "spPr", "style", "txBody", "extLst"])
        self.assertEqual(shapes[0].find("p:extLst/p:ext", self.NS).get(f"{{{self.R}}}id"), "rId1")
        self.assertEqual(shapes[1].find("p:txBody/a:p/a:r/a:t", self.NS).text, "Keep exact text")
        background = slide.find("p:cSld/p:bg/p:bgPr", self.NS)
        self.assertEqual([child.tag.rsplit("}", 1)[-1] for child in background], ["solidFill", "effectLst", "extLst"])
        self.assertEqual(len(background.find("a:effectLst", self.NS)), 0)
        self.assertEqual(background.find("a:solidFill/a:srgbClr", self.NS).get("val"), "AABBCC")

    def test_completes_only_missing_slide_nodes_preserving_content_and_zip_members(self):
        with tempfile.TemporaryDirectory() as temp:
            package = Path(temp) / "derived.pptx"
            members = {
                "ppt/slides/slide1.xml": self.incomplete_slide().encode(),
                "ppt/slides/slide2.xml": self.complete_slide().encode(),
                "ppt/slides/_rels/slide1.xml.rels": b'<Relationships><Relationship Id="rId1" Target="../media/image.png"/></Relationships>',
                "ppt/notesSlides/notesSlide1.xml": self.incomplete_slide().encode(),
                "ppt/media/image.png": bytes(range(256)),
            }
            with zipfile.ZipFile(package, "w") as archive:
                archive.comment = b"package comment"
                for name, payload in members.items():
                    info = zipfile.ZipInfo(name, (2024, 1, 2, 3, 4, 6))
                    info.compress_type = zipfile.ZIP_DEFLATED
                    info.comment = b"member comment"
                    info.external_attr = 0o100644 << 16
                    archive.writestr(info, payload)
            self.assertTrue(build_workspace.normalize_slide_shape_and_background_xml(package))
            self.assert_completed(package)
            with zipfile.ZipFile(package) as archive:
                self.assertEqual(archive.namelist(), list(members))
                self.assertEqual(archive.comment, b"package comment")
                for info in archive.infolist():
                    self.assertEqual(info.date_time, (2024, 1, 2, 3, 4, 6))
                    self.assertEqual(info.compress_type, zipfile.ZIP_DEFLATED)
                    self.assertEqual(info.comment, b"member comment")
                    self.assertEqual(info.external_attr, 0o100644 << 16)
                    if info.filename != "ppt/slides/slide1.xml":
                        self.assertEqual(archive.read(info), members[info.filename])
                changed = archive.read("ppt/slides/slide1.xml")
            self.assertIn(b"<!--keep slide comment-->", changed)
            before = ET.fromstring(members["ppt/slides/slide1.xml"])
            after = ET.fromstring(changed)
            self.assertEqual(before.attrib, after.attrib)
            self.assertEqual(ET.tostring(before.find(".//p:sp/p:spPr", self.NS)),
                             ET.tostring(after.find(".//p:sp/p:spPr", self.NS)))
            self.assertEqual(ET.tostring(before.find(".//p:sp/p:style", self.NS)),
                             ET.tostring(after.find(".//p:sp/p:style", self.NS)))
            self.assertEqual(ET.tostring(before.findall(".//p:sp", self.NS)[1]),
                             ET.tostring(after.findall(".//p:sp", self.NS)[1]))
            self.assertEqual(ET.tostring(before.find(".//p:bgPr/a:solidFill", self.NS)),
                             ET.tostring(after.find(".//p:bgPr/a:solidFill", self.NS)))
            normalized = package.read_bytes()
            self.assertFalse(build_workspace.normalize_slide_shape_and_background_xml(package))
            self.assertEqual(package.read_bytes(), normalized)

    def test_absent_non_solid_existing_and_non_slide_xml_are_byte_identical_noops(self):
        cases = [self.complete_slide(),
                 f'<p:sld xmlns:p="{self.P}" xmlns:d="{self.A}"><p:cSld><p:bg><p:bgPr><d:gradFill/></p:bgPr></p:bg><p:spTree/></p:cSld></p:sld>',
                 f'<p:sld xmlns:p="{self.P}" xmlns:d="{self.A}"><p:cSld><p:bg><p:bgPr><d:solidFill/><d:effectDag/></p:bgPr></p:bg><p:spTree/></p:cSld></p:sld>',
                 '<fixture><sp/><bgPr/></fixture>', None]
        for slide in cases:
            with self.subTest(slide=slide), tempfile.TemporaryDirectory() as temp:
                package = Path(temp) / "derived.pptx"
                with zipfile.ZipFile(package, "w") as archive:
                    archive.writestr("fixture.bin", b"no changes")
                    if slide is not None:
                        archive.writestr("ppt/slides/slide1.xml", slide)
                    archive.writestr("ppt/slides/slide1.xml.rels", b"keep rels")
                original = package.read_bytes()
                self.assertFalse(build_workspace.normalize_slide_shape_and_background_xml(package))
                self.assertEqual(package.read_bytes(), original)

    def test_build_completes_derived_package_before_batch_autofit_and_validate(self):
        for kind, patch in (("full", True), ("style-proof", False)):
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as temp:
                root = Path(temp) / "workspace"
                make_workspace(root, patch=patch)
                node = fake_node(Path(temp) / "bin" / "node", slide=self.incomplete_slide())
                binary = fake_officecli(Path(temp) / "bin" / "officecli")
                env = {"OFFICECLI_BIN": str(binary), "PATH": os.environ.get("PATH", "")}
                plan = build_workspace.prepare_build_plan(root, build_kind=kind, node_bin=str(node), environ=env)
                real_run = build_workspace._run_argv
                real_autofit = build_workspace.apply_shape_to_fit_text
                observed = []

                def checked_run(argv, **kwargs):
                    if len(argv) > 2 and argv[1] in {"batch", "validate"} and argv[2] != "--help":
                        self.assert_completed(Path(argv[2]))
                        observed.append(argv[1])
                    return real_run(argv, **kwargs)

                def checked_autofit(source, output):
                    self.assert_completed(source)
                    observed.append("autofit")
                    return real_autofit(source, output)

                with mock.patch.object(build_workspace, "_run_argv", side_effect=checked_run), \
                     mock.patch.object(build_workspace, "apply_shape_to_fit_text", side_effect=checked_autofit):
                    build_workspace.execute_build_plan(plan, environ=env)
                self.assertEqual(observed, (["batch"] if patch else []) + ["autofit", "validate"])
                with zipfile.ZipFile(root / plan["paths"]["base"]) as archive:
                    raw = archive.read("ppt/slides/slide1.xml")
                self.assertEqual(raw, self.incomplete_slide().encode())
                self.assert_completed(root / plan["paths"]["final"])


class NotesMasterOrderTests(unittest.TestCase):
    WRONG = ["sldMasterIdLst", "sldIdLst", "notesMasterIdLst", "sldSz", "notesSz", "defaultTextStyle"]
    CORRECT = ["sldMasterIdLst", "notesMasterIdLst", "sldIdLst", "sldSz", "notesSz", "defaultTextStyle"]

    @staticmethod
    def presentation(order):
        parts = {
            "sldMasterIdLst": '<p:sldMasterIdLst><p:sldMasterId id="2147483648" r:id="rId1"/></p:sldMasterIdLst>',
            "notesMasterIdLst": '<p:notesMasterIdLst><!--keep notes--><p:notesMasterId r:id="rId3"/></p:notesMasterIdLst>',
            "handoutMasterIdLst": '<p:handoutMasterIdLst><p:handoutMasterId r:id="rId4"/></p:handoutMasterIdLst>',
            "sldIdLst": '<p:sldIdLst><p:sldId id="256" r:id="rId2"/></p:sldIdLst>',
            "sldSz": '<p:sldSz cx="9144000" cy="5143500"/>',
            "notesSz": '<p:notesSz cx="6858000" cy="9144000"/>',
            "defaultTextStyle": '<p:defaultTextStyle><a:defPPr><a:defRPr lang="en-US"/></a:defPPr></p:defaultTextStyle>',
        }
        return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                '<p:presentation xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" '
                'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
                'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" saveSubsetFonts="1">'
                + ''.join(parts[name] for name in order) + '</p:presentation>')

    def assert_order(self, package, expected):
        with zipfile.ZipFile(package) as archive:
            root = ET.fromstring(archive.read("ppt/presentation.xml"))
        self.assertEqual([node.tag.rsplit("}", 1)[-1] for node in root], expected)

    def test_zip_repair_preserves_nodes_relationships_members_and_is_idempotent(self):
        with tempfile.TemporaryDirectory() as temp:
            package = Path(temp) / "deck.pptx"
            original = self.presentation(self.WRONG).encode()
            members = {
                "ppt/presentation.xml": original,
                "ppt/_rels/presentation.xml.rels": b'<Relationships><Relationship Id="rId3" Target="notesMasters/notesMaster1.xml"/></Relationships>',
                "ppt/notesMasters/notesMaster1.xml": b"notes master content",
                "ppt/media/image1.png": bytes(range(256)),
                "[Content_Types].xml": b"types unchanged",
            }
            with zipfile.ZipFile(package, "w") as archive:
                archive.comment = b"preserve archive comment"
                for name, payload in members.items():
                    info = zipfile.ZipInfo(name, (2024, 1, 2, 3, 4, 6))
                    info.compress_type = zipfile.ZIP_DEFLATED
                    info.comment = b"member comment"
                    info.external_attr = 0o100644 << 16
                    archive.writestr(info, payload)
            self.assertTrue(build_workspace.normalize_notes_master_order(package))
            self.assert_order(package, self.CORRECT)
            with zipfile.ZipFile(package) as archive:
                self.assertEqual(archive.namelist(), list(members))
                self.assertEqual(archive.comment, b"preserve archive comment")
                for info in archive.infolist():
                    self.assertEqual(info.date_time, (2024, 1, 2, 3, 4, 6))
                    self.assertEqual(info.compress_type, zipfile.ZIP_DEFLATED)
                    self.assertEqual(info.comment, b"member comment")
                    self.assertEqual(info.external_attr, 0o100644 << 16)
                    if info.filename != "ppt/presentation.xml":
                        self.assertEqual(archive.read(info), members[info.filename])
                changed = archive.read("ppt/presentation.xml")
            before, after = ET.fromstring(original), ET.fromstring(changed)
            self.assertEqual(before.attrib, after.attrib)
            self.assertEqual({node.tag: ET.tostring(node) for node in before},
                             {node.tag: ET.tostring(node) for node in after})
            self.assertIn(b"<!--keep notes-->", changed)
            normalized = package.read_bytes()
            self.assertFalse(build_workspace.normalize_notes_master_order(package))
            self.assertEqual(package.read_bytes(), normalized)

    def test_correct_absent_and_minimal_fixtures_are_byte_identical_noops(self):
        cases = [self.presentation(self.CORRECT), self.presentation(["sldSz", "notesSz"]),
                 '<fixture/>', None]
        with tempfile.TemporaryDirectory() as temp:
            for presentation in cases:
                with self.subTest(presentation=presentation):
                    package = Path(temp) / "deck.pptx"
                    with zipfile.ZipFile(package, "w") as archive:
                        archive.writestr("fixture", b"not a validation proof")
                        if presentation is not None:
                            archive.writestr("ppt/presentation.xml", presentation)
                    original = package.read_bytes()
                    self.assertFalse(build_workspace.normalize_notes_master_order(package))
                    self.assertEqual(package.read_bytes(), original)

    def test_notes_precede_handout_and_work_without_slide_master(self):
        for wrong, correct in (
            (["sldMasterIdLst", "handoutMasterIdLst", "sldIdLst", "notesMasterIdLst", "notesSz"],
             ["sldMasterIdLst", "notesMasterIdLst", "handoutMasterIdLst", "sldIdLst", "notesSz"]),
            (["sldIdLst", "notesMasterIdLst", "notesSz"], ["notesMasterIdLst", "sldIdLst", "notesSz"]),
        ):
            with self.subTest(wrong=wrong), tempfile.TemporaryDirectory() as temp:
                package = Path(temp) / "deck.pptx"
                with zipfile.ZipFile(package, "w") as archive:
                    archive.writestr("ppt/presentation.xml", self.presentation(wrong))
                self.assertTrue(build_workspace.normalize_notes_master_order(package))
                self.assert_order(package, correct)

    def test_build_preserves_raw_base_and_normalizes_before_batch_autofit_validate(self):
        for kind, patch in (("style-proof", False), ("full", False), ("full", True)):
            with self.subTest(kind=kind, patch=patch), tempfile.TemporaryDirectory() as temp:
                root = Path(temp) / "workspace"
                make_workspace(root, patch=patch)
                types = OrphanSlideMasterOverrideTests.content_types()
                node = fake_node(Path(temp) / "bin" / "node", self.presentation(self.WRONG), types)
                binary = fake_officecli(Path(temp) / "bin" / "officecli")
                env = {"OFFICECLI_BIN": str(binary), "PATH": os.environ.get("PATH", "")}
                plan = build_workspace.prepare_build_plan(root, build_kind=kind, node_bin=str(node), environ=env)
                real_run = build_workspace._run_argv
                real_autofit = build_workspace.apply_shape_to_fit_text
                observed = []

                def assert_clean_types(package):
                    with zipfile.ZipFile(package) as archive:
                        names = {node.get("PartName") for node in ET.fromstring(archive.read("[Content_Types].xml"))}
                    self.assertNotIn("/ppt/slideMasters/slideMaster2.xml", names)
                    self.assertNotIn("/ppt/slideMasters/slideMaster3.xml", names)
                    self.assertIn("/ppt/slides/slide99.xml", names)

                def checked_run(argv, **kwargs):
                    if len(argv) > 2 and argv[1] in {"batch", "validate"} and argv[2] != "--help":
                        self.assert_order(Path(argv[2]), self.CORRECT)
                        assert_clean_types(Path(argv[2]))
                        observed.append(argv[1])
                    return real_run(argv, **kwargs)

                def checked_autofit(source, output):
                    self.assert_order(source, self.CORRECT)
                    assert_clean_types(source)
                    observed.append("autofit")
                    return real_autofit(source, output)

                with mock.patch.object(build_workspace, "_run_argv", side_effect=checked_run), \
                     mock.patch.object(build_workspace, "apply_shape_to_fit_text", side_effect=checked_autofit):
                    report = build_workspace.execute_build_plan(plan, environ=env)
                self.assertEqual(observed, (["batch"] if patch else []) + ["autofit", "validate"])
                self.assert_order(root / plan["paths"]["base"], self.WRONG)
                with zipfile.ZipFile(root / plan["paths"]["base"]) as archive:
                    self.assertEqual(archive.read("[Content_Types].xml"), types.encode())
                self.assert_order(root / plan["paths"]["final"], self.CORRECT)
                assert_clean_types(root / plan["paths"]["final"])
                self.assertEqual(report["base_pptx"]["sha256"], sha256_file(root / plan["paths"]["base"]))


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
            self.assertTrue(zipfile.is_zipfile(root / "build" / "final.pptx"))
            self.assertEqual(report["final_pptx"]["sha256"], sha256_file(root / "build" / "final.pptx"))
            self.assertEqual(report["final_pptx"]["sha256"], report["validation"]["pptx_sha256"])
            families = [call["argv"][:2] for call in read_json_lines(log) if call["argv"] != ["--version"]]
            self.assertEqual(
                families,
                [
                    ["batch", "--help"],
                    ["batch", str(root / "build" / "draft.pptx")],
                    ["validate", "--help"],
                    ["validate", str(root / "build" / "final.pptx")],
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
            write_minimal_pptx(final, slide_count=2)
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

            screenshots = [action for action in actions if action.get("expected_path")]
            self.assertEqual(
                [action["argv"] for action in screenshots],
                [
                    [str(officecli), "view", str(final), "screenshot", "--grid", "2", "--screenshot-width", "1600", "--screenshot-height", "1200", "--out", str(root / "renders/final/contact-sheet.png")],
                    [str(officecli), "view", str(final), "screenshot", "--page", "1", "--out", str(root / "renders/final/slides/opening.png")],
                    [str(officecli), "view", str(final), "screenshot", "--page", "2", "--out", str(root / "renders/final/slides/decision.png")],
                ],
            )
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
