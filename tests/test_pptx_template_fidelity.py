from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / ".agents" / "skills" / "pptx-generator" / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))


def load_module(name: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


CORE = load_module("workspace_core")
INIT = load_module("init_workspace")
PROFILE = load_module("profile_template")
FONTS = load_module("inventory_fonts")
FONT_AUDIT = load_module("report_font_audit")
AUTOFIT = load_module("apply_text_autofit")
PREFLIGHT = load_module("report_layout_preflight")
READINESS = load_module("report_workspace_readiness")


def json_write(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(CORE.canonical_json_bytes(value))


def sample_pptx(path: Path) -> Path:
    presentation = '<p:presentation xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"><p:sldSz cx="9144000" cy="5143500" type="screen16x9"/></p:presentation>'
    theme = '<a:theme xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" name="Sample"><a:themeElements><a:clrScheme name="Sample"><a:accent1><a:srgbClr val="123456"/></a:accent1></a:clrScheme><a:fontScheme name="Sample"><a:majorFont><a:latin typeface="Major Sans"/><a:ea typeface=""/></a:majorFont><a:minorFont><a:latin typeface="Minor Sans"/><a:ea typeface=""/></a:minorFont></a:fontScheme><a:fmtScheme name="Sample"/></a:themeElements></a:theme>'
    slide = '''<p:sld xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"><p:cSld><p:spTree>
    <p:sp><p:nvSpPr><p:cNvPr id="2" name="Mixed runs"/><p:cNvSpPr/><p:nvPr><p:ph type="body"/></p:nvPr></p:nvSpPr><p:spPr><a:xfrm><a:off x="100" y="200"/><a:ext cx="2000" cy="1000"/></a:xfrm><a:prstGeom prst="rect"/></p:spPr><p:txBody><a:bodyPr/><a:lstStyle/><a:p><a:pPr algn="ctr"><a:defRPr sz="1800"><a:latin typeface="+mn-lt"/></a:defRPr></a:pPr><a:r><a:rPr sz="2400" b="1"><a:latin typeface="Direct Sans"/><a:solidFill><a:srgbClr val="FF0000"/></a:solidFill></a:rPr><a:t>First</a:t></a:r><a:r><a:rPr i="1"/><a:t>Second</a:t></a:r></a:p></p:txBody></p:sp>
    <p:pic><p:nvPicPr><p:cNvPr id="3" name="Picture"/><p:cNvPicPr/><p:nvPr/></p:nvPicPr><p:blipFill/><p:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="1600" cy="900"/></a:xfrm></p:spPr></p:pic>
    </p:spTree></p:cSld></p:sld>'''
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("ppt/presentation.xml", presentation)
        archive.writestr("ppt/theme/theme1.xml", theme)
        archive.writestr("ppt/slides/slide1.xml", slide)
        archive.writestr("ppt/slideMasters/slideMaster1.xml", '<p:sldMaster xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"/>')
        archive.writestr("ppt/slideLayouts/slideLayout1.xml", '<p:sldLayout xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"/>')
    return path


class TemplateProfileTests(unittest.TestCase):
    def test_contract_schemas_and_templates_expose_fidelity_gates(self):
        schemas = ROOT / ".agents" / "skills" / "pptx-generator" / "schemas"
        values = {path.name: json.loads(path.read_text(encoding="utf-8")) for path in schemas.glob("*.json")}
        self.assertIn("template-profile.schema.json", values)
        self.assertIn("font-environment.schema.json", values)
        self.assertIn("layout-preflight.schema.json", values)
        self.assertIn("template-style-confirmation.schema.json", values)
        review_required = set(values["visual-review.schema.json"]["required"])
        self.assertIn("pages", review_required)
        workspace = json.loads((ROOT / ".agents" / "skills" / "pptx-generator" / "templates" / "workspace" / "template-edit" / "workspace.json").read_text(encoding="utf-8"))
        self.assertEqual(workspace["text_fit_policy"], "shape-to-fit-text")
        for name in ("template_profile", "font_environment", "layout_preflight", "template_style_confirmation"):
            self.assertIn(name, workspace["paths"])

    def test_profile_is_deterministic_and_keeps_run_level_differences(self):
        with tempfile.TemporaryDirectory() as temporary:
            source = sample_pptx(Path(temporary) / "template.pptx")
            first = PROFILE.profile_template(source)
            second = PROFILE.profile_template(source)
            self.assertEqual(CORE.canonical_json_bytes(first), CORE.canonical_json_bytes(second))
            runs = first["slides"][0]["shapes"][0]["paragraphs"][0]["runs"]
            self.assertEqual(runs[0]["effective"]["font_family"], "Direct Sans")
            self.assertEqual(runs[0]["effective"]["font_size_pt"], 24)
            self.assertTrue(runs[0]["effective"]["bold"])
            self.assertEqual(runs[1]["effective"]["font_family"], "Minor Sans")
            self.assertEqual(runs[1]["effective"]["font_size_pt"], 18)
            self.assertTrue(runs[1]["effective"]["italic"])
            self.assertFalse(first["typography_summary"]["summary_overrides_run_formatting"])

    def test_template_readiness_requires_confirmed_current_reference_and_profile(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "workspace"
            INIT.initialize_workspace(root, "template-edit", "template-test", "Template Test")
            blocked = READINESS.evaluate_workspace(root)
            codes = {item["code"] for item in blocked["blockers"]}
            self.assertIn("REFERENCE_PERMISSION_UNRESOLVED", codes)
            self.assertIn("REQUIRED_SOURCE_MISSING", codes)


class FontInventoryTests(unittest.TestCase):
    def test_wsl_mounted_files_do_not_prove_renderer_visibility(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            workspace = base / "workspace"
            workspace.mkdir()
            mounted = base / "external-fonts"
            mounted.mkdir()
            (mounted / "BrandSans.ttf").write_bytes(b"font")
            blocked = FONTS.inventory_font_environment(
                workspace,
                platform_name="linux",
                wsl=True,
                renderers={"build": "node", "render": "officecli", "target": "powerpoint"},
                observations=[{"kind": "mounted-files", "environment": "build", "path": str(mounted)}],
            )
            self.assertEqual(blocked["status"], "need-user")
            approved = FONTS.inventory_font_environment(
                workspace,
                platform_name="linux",
                wsl=True,
                renderers={"build": "node", "render": "officecli", "target": "powerpoint"},
                observations=[{"kind": "mounted-files", "environment": "build", "path": str(mounted)}],
                approved_paths=[str(mounted)],
            )
            self.assertEqual(approved["environments"]["build"]["status"], "unverified")
            self.assertEqual(approved["environments"]["build"]["visible_fonts"], [])
            visible = workspace / "fontconfig.txt"
            visible.write_text("Brand Sans\n", encoding="utf-8")
            verified = FONTS.inventory_font_environment(
                workspace,
                platform_name="linux",
                wsl=True,
                renderers={"build": "node", "render": "officecli", "target": "powerpoint"},
                observations=[{"kind": "fontconfig", "environment": "build", "path": str(visible)}],
            )
            self.assertEqual(verified["environments"]["build"]["visible_fonts"], ["Brand Sans"])

    def test_unapproved_substitution_blocks_font_audit(self):
        contract = {
            "schema_version": "1.0", "selection_basis": "user", "template_profile_sha256": None,
            "fonts": [{"role": "body", "family": "Brand Sans", "required": True, "fallback_allowed": False, "source": "user"}],
        }
        environment = {
            "environments": {
                name: {"status": "verified" if name != "target" else "unverified", "renderer": name, "visible_fonts": ["Brand Sans"], "observed_substitutions": ["Brand Sans->Arial"] if name == "render" else []}
                for name in ("build", "render", "target")
            }
        }
        audit = FONT_AUDIT.evaluate_font_contract(contract, "a" * 64, environment, "b" * 64, None)
        self.assertEqual(audit["status"], "need-user")
        self.assertEqual(audit["environments"]["render"]["unapproved_substitutions"], ["Brand Sans->Arial"])


class AutoFitAndPreflightTests(unittest.TestCase):
    def test_autofit_applies_to_every_editable_text_shape(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = sample_pptx(root / "source.pptx")
            output = root / "output.pptx"
            result = AUTOFIT.apply_shape_to_fit_text(source, output)
            self.assertEqual(result["status"], "applied-awaiting-geometry-recalculation")
            self.assertEqual(len(result["shapes"]), 1)
            self.assertEqual(result["shapes"][0]["after_mode"], "shape-to-fit-text")
            with zipfile.ZipFile(output) as archive:
                self.assertIn(b"spAutoFit", archive.read("ppt/slides/slide1.xml"))

    def test_user_reported_layout_failures_and_undispositioned_issues_block(self):
        shapes = [
            {"slide_id": "slide-06", "shape_id": "20", "editable": True, "supported": True, "after_mode": "shape-to-fit-text", "geometry_recalculated": True, "text": "结构赛道", "expected_single_line": True, "line_count": 2, "bounds": {"x": 0, "y": 0, "w": 20, "h": 10}},
            {"slide_id": "slide-07", "shape_id": "117", "editable": True, "supported": True, "after_mode": "shape-to-fit-text", "geometry_recalculated": True, "text": "+42.5%", "expected_single_line": True, "line_count": 2, "bounds": {"x": 0, "y": 10, "w": 20, "h": 10}},
            {"slide_id": "slide-03", "shape_id": "image", "editable": False, "bounds": {"x": 95, "y": 0, "w": 20, "h": 10}, "image": {"source_aspect_ratio": 1.7778, "frame_aspect_ratio": 2.169, "fit": "stretch"}, "overlaps": [{"with": "caption", "severity": "severe"}]},
        ]
        issues = {"issues": [{"id": f"i-{index:02d}", "type": "overflow"} for index in range(19)]}
        result = PREFLIGHT.evaluate_layout_preflight(
            final_pptx_sha256="a" * 64,
            template_profile_sha256="b" * 64,
            font_audit_sha256="c" * 64,
            issues_sha256="d" * 64,
            layout_evidence_sha256="e" * 64,
            layout_evidence={"slide_size": {"w": 100, "h": 100}, "shapes": shapes, "alignment_groups": [], "issue_dispositions": {}},
            issues=issues,
            render_sha256="f" * 64,
        )
        codes = {item["code"] for item in result["findings"]}
        self.assertEqual(result["status"], "blocked")
        self.assertIn("SINGLE_LINE_OVERFLOW", codes)
        self.assertIn("IMAGE_ASPECT_RATIO_DRIFT", codes)
        self.assertIn("SHAPE_OFF_SLIDE", codes)
        self.assertIn("SEVERE_OVERLAP", codes)
        self.assertEqual(sum(item["code"] == "STATIC_ISSUE_UNDISPOSITIONED" for item in result["findings"]), 19)

    def test_recalculated_geometry_and_zero_issues_pass(self):
        shape = {"slide_id": "slide-01", "shape_id": "title", "editable": True, "supported": True, "after_mode": "shape-to-fit-text", "geometry_recalculated": True, "text": "One line", "expected_single_line": True, "line_count": 1, "font_size_pt": 20, "minimum_font_size_pt": 12, "bounds": {"x": 0, "y": 0, "w": 50, "h": 10}}
        result = PREFLIGHT.evaluate_layout_preflight(
            final_pptx_sha256="a" * 64,
            template_profile_sha256=None,
            font_audit_sha256="c" * 64,
            issues_sha256="d" * 64,
            layout_evidence_sha256="e" * 64,
            layout_evidence={"slide_size": {"w": 100, "h": 100}, "shapes": [shape], "alignment_groups": [], "issue_dispositions": {}},
            issues={"issues": []},
        )
        self.assertEqual(result["status"], "ready")

    def test_unknown_issue_cannot_be_waived_as_non_blocking(self):
        issue = {"id": "mystery", "type": "new-unknown-kind"}
        result = PREFLIGHT.evaluate_layout_preflight(
            final_pptx_sha256="a" * 64,
            template_profile_sha256=None,
            font_audit_sha256="c" * 64,
            issues_sha256="d" * 64,
            layout_evidence_sha256="e" * 64,
            layout_evidence={"shapes": [], "alignment_groups": [], "issue_dispositions": {"mystery": {"classification": "non-blocking", "reason": "looks fine", "render_observation": "checked"}}},
            issues={"issues": [issue]},
        )
        self.assertEqual(result["status"], "blocked")
        self.assertIn("STATIC_ISSUE_BLOCKING", {item["code"] for item in result["findings"]})


if __name__ == "__main__":
    unittest.main()
