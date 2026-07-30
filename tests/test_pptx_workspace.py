from __future__ import annotations

import importlib.util
import json
import re
import subprocess
import sys
import tempfile
import unittest
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
COMPILER = load_module("compile_plan")
INIT = load_module("init_workspace")
STYLE_LOCK = load_module("lock_style_proof")
FONT_AUDIT = load_module("report_font_audit")
WORKSPACE_READINESS = load_module("report_workspace_readiness")
DELIVERY_READINESS = load_module("report_delivery_readiness")
LAYOUT_PREFLIGHT = load_module("report_layout_preflight")


def plan_text(slides=None, declared_count=None, *, ids=True):
    slides = slides or [
        ("first-slide", "First conclusion", "Two-column structure", "First body"),
        ("second-slide", "Second conclusion", "Full-width comparison", "Second body"),
    ]
    count = len(slides) if declared_count is None else declared_count
    sections = []
    for ordinal, (slide_id, title, layout, content) in enumerate(slides, 1):
        id_line = f"<!-- slide-id: {slide_id} -->\n\n" if ids else ""
        sections.append(
            f"## Slide {ordinal:02d}: {title}\n"
            f"{id_line}"
            f"### 1. Layout\n{layout}\n\n"
            f"### 2. Content\n{content}"
        )
    return (
        "# Test Deck — Per-Slide Content Plan\n\n"
        "Recommended topic: **Test Topic**\n"
        f"Recommended slide count: **{count}**\n"
        "Expected duration: **10 minutes**\n"
        "Overall logic: **opening → evidence → close**\n\n"
        "---\n\n"
        + "\n\n---\n\n".join(sections)
        + "\n"
    )


def run_script(name: str, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPTS / name), *map(str, args)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def json_write(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(CORE.canonical_json_bytes(value))


class CompilerTests(unittest.TestCase):
    def test_deterministic_compile_and_raw_fields(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            plan = root / "test-per-slide-content-plan.md"
            outline = root / "outline.json"
            plan.write_text(plan_text(), encoding="utf-8")

            first = COMPILER.compile_plan(plan, outline)
            first_bytes = outline.read_bytes()
            second = COMPILER.compile_plan(plan, outline)
            self.assertEqual(first["status"], "compiled")
            self.assertEqual(second["status"], "compiled")
            self.assertEqual(first_bytes, outline.read_bytes())
            value = json.loads(first_bytes)
            self.assertNotIn("timestamp", value)
            self.assertEqual(value["generator_version"], CORE.GENERATOR_VERSION)
            self.assertEqual(value["deck"]["declared_slide_count"], 2)
            self.assertEqual(value["slides"][0]["layout"], "Two-column structure")
            self.assertEqual(value["slides"][0]["content"], "First body")

    def test_bom_and_crlf_are_normalized_for_hash_and_output(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            plan = root / "plan.md"
            outline = root / "outline.json"
            normalized = plan_text().encode("utf-8")
            plan.write_bytes(b"\xef\xbb\xbf" + normalized.replace(b"\n", b"\r\n"))
            result = COMPILER.compile_plan(plan, outline)
            value = json.loads(outline.read_text(encoding="utf-8"))
            self.assertEqual(result["status"], "compiled")
            self.assertEqual(value["source_plan_sha256"], CORE.sha256_bytes(normalized))
            self.assertNotIn("\r", value["slides"][0]["content"])

    def test_reorder_preserves_stable_ids(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            plan = root / "plan.md"
            outline = root / "outline.json"
            plan.write_text(plan_text(), encoding="utf-8")
            COMPILER.compile_plan(plan, outline)
            reordered = [
                ("second-slide", "Second conclusion", "Full-width comparison", "Second body"),
                ("first-slide", "First conclusion", "Two-column structure", "First body"),
            ]
            plan.write_text(plan_text(reordered), encoding="utf-8")
            COMPILER.compile_plan(plan, outline)
            value = json.loads(outline.read_text(encoding="utf-8"))
            self.assertEqual([slide["id"] for slide in value["slides"]], ["second-slide", "first-slide"])
            self.assertEqual([slide["ordinal"] for slide in value["slides"]], [1, 2])

    def test_missing_duplicate_and_invalid_ids_fail_without_clobber(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            plan = root / "plan.md"
            outline = root / "outline.json"
            valid = plan_text()
            plan.write_text(valid, encoding="utf-8")
            COMPILER.compile_plan(plan, outline)
            last_good = outline.read_bytes()
            mutations = {
                "NEEDS_STABLE_IDS": valid.replace("<!-- slide-id: first-slide -->\n", "", 1),
                "DUPLICATE_SLIDE_ID": valid.replace("second-slide", "first-slide", 1),
                "INVALID_SLIDE_ID": valid.replace("first-slide", "First_Slide", 1),
            }
            for expected, mutation in mutations.items():
                with self.subTest(expected=expected):
                    plan.write_text(mutation, encoding="utf-8")
                    result = COMPILER.compile_plan(plan, outline)
                    self.assertEqual(result["status"], "invalid")
                    self.assertIn(expected, {item["code"] for item in result["diagnostics"]})
                    self.assertEqual(outline.read_bytes(), last_good)

    def test_initialize_ids_inserts_only_comments_and_preserves_bom_crlf_semantics(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            plan = root / "plan.md"
            outline = root / "outline.json"
            original = b"\xef\xbb\xbf" + plan_text(ids=False).encode("utf-8").replace(b"\n", b"\r\n")
            plan.write_bytes(original)
            result = run_script("compile_plan.py", "--plan", str(plan), "--output", str(outline), "--initialize-ids")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            updated = plan.read_bytes()
            self.assertTrue(updated.startswith(b"\xef\xbb\xbf"))
            self.assertIn(b"\r\n", updated)
            without_ids = re.sub(rb"<!-- slide-id: [a-z0-9-]+ -->\r\n", b"", updated)
            self.assertEqual(without_ids, original)
            self.assertEqual([slide["id"] for slide in json.loads(outline.read_text())["slides"]], ["slide-01", "slide-02"])

    def test_shape_failures_do_not_clobber_last_valid_outline(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            plan = root / "plan.md"
            outline = root / "outline.json"
            valid = plan_text()
            plan.write_text(valid, encoding="utf-8")
            COMPILER.compile_plan(plan, outline)
            last_good = outline.read_bytes()
            mutations = {
                "SLIDE_COUNT_MISMATCH": plan_text(declared_count=3),
                "SLIDE_ORDINALS_INVALID": valid.replace("## Slide 02:", "## Slide 03:"),
                "LAYOUT_SECTION_INVALID": valid.replace("### 1. Layout\nTwo-column structure", "Two-column structure", 1),
                "CONTENT_SECTION_INVALID": valid.replace("### 2. Content\nFirst body", "First body", 1),
                "duplicate-layout": valid.replace("### 2. Content\nFirst body", "### 1. Layout\nExtra\n\n### 2. Content\nFirst body", 1),
            }
            for expected, mutation in mutations.items():
                with self.subTest(expected=expected):
                    plan.write_text(mutation, encoding="utf-8")
                    result = COMPILER.compile_plan(plan, outline)
                    codes = {item["code"] for item in result["diagnostics"]}
                    self.assertEqual(result["status"], "invalid")
                    self.assertIn("LAYOUT_SECTION_INVALID" if expected == "duplicate-layout" else expected, codes)
                    self.assertEqual(outline.read_bytes(), last_good)


class WorkspaceTests(unittest.TestCase):
    def initialize(self, root: Path, profile="from-scratch") -> Path:
        workspace = root / profile
        result = INIT.initialize_workspace(workspace, profile, f"{profile}-deck", "Profile Deck")
        self.assertEqual(result["status"], "initialized")
        return workspace

    def compile_workspace(self, workspace: Path):
        result = COMPILER.compile_plan(
            workspace / "per-slide-content-plan.md",
            workspace / "outline.json",
            workspace_root=workspace,
        )
        self.assertEqual(result["status"], "compiled", result)

    def test_profile_initialization_and_existing_target_guard(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            full_required = {
                "workspace.json", "intake.json", "per-slide-content-plan.md", "design-brief.json",
                "design-contract.json", "font-contract.json", "font-environment.json", "evidence-plan.json", "asset-plan.json",
                "notes.md", "sources/manifest.json", "src/deck.js", "src/theme.js",
                "assets/manifest.json", "assets/attribution.csv", "patches/.gitkeep",
            }
            for profile in ("from-scratch", "template-edit"):
                workspace = self.initialize(root, profile)
                inventory = {path.relative_to(workspace).as_posix() for path in workspace.rglob("*") if path.is_file()}
                self.assertTrue(full_required.issubset(inventory))
                if profile == "template-edit":
                    self.assertIn("template-profile.json", inventory)
                self.assertIn("<!-- slide-id: slide-01 -->", (workspace / "per-slide-content-plan.md").read_text())
                self.assertEqual(json.loads((workspace / "workspace.json").read_text())["profile"], profile)
                with self.assertRaises(CORE.WorkspaceError):
                    INIT.initialize_workspace(workspace, profile, f"{profile}-deck", "Profile Deck")

            inspect = self.initialize(root, "inspect")
            self.assertTrue((inspect / "sources/manifest.json").is_file())
            self.assertFalse((inspect / "per-slide-content-plan.md").exists())
            self.assertFalse((inspect / "src").exists())
            report = WORKSPACE_READINESS.evaluate_workspace(inspect)
            self.assertEqual(report["status"], "blocked")
            self.assertIn("REQUIRED_SOURCE_MISSING", {item["code"] for item in report["blockers"]})

    def test_inspect_source_file_is_part_of_fingerprint(self):
        with tempfile.TemporaryDirectory() as temporary:
            workspace = self.initialize(Path(temporary), "inspect")
            source = workspace / "input.pptx"
            source.write_bytes(b"first-package")
            manifest_path = workspace / "sources/manifest.json"
            manifest = json.loads(manifest_path.read_text())
            manifest["sources"][0]["path"] = "input.pptx"
            manifest["sources"][0]["sha256"] = None
            json_write(manifest_path, manifest)
            first = WORKSPACE_READINESS.evaluate_workspace(workspace)
            self.assertEqual(first["status"], "ready")
            source.write_bytes(b"changed-package")
            second = WORKSPACE_READINESS.evaluate_workspace(workspace)
            self.assertNotEqual(first["source_fingerprint"], second["source_fingerprint"])

    def test_outline_mutation_and_plan_staleness_are_blocked(self):
        with tempfile.TemporaryDirectory() as temporary:
            workspace = self.initialize(Path(temporary))
            self.compile_workspace(workspace)
            self.assertEqual(WORKSPACE_READINESS.evaluate_workspace(workspace)["status"], "ready")

            outline_path = workspace / "outline.json"
            outline = json.loads(outline_path.read_text())
            outline["slides"][0]["title"] = "Mutated generated title"
            json_write(outline_path, outline)
            mutated = WORKSPACE_READINESS.evaluate_workspace(workspace)
            self.assertEqual(mutated["status"], "blocked")
            self.assertIn("STALE_OR_MUTATED_OUTLINE", {item["code"] for item in mutated["blockers"]})

            self.compile_workspace(workspace)
            plan = workspace / "per-slide-content-plan.md"
            plan.write_text(plan.read_text().replace("Profile Deck\n<!--", "Updated Profile Deck\n<!--", 1))
            stale = WORKSPACE_READINESS.evaluate_workspace(workspace)
            self.assertIn("STALE_OR_MUTATED_OUTLINE", {item["code"] for item in stale["blockers"]})

    def test_renderer_and_source_paths_are_confined(self):
        mutations = [
            {"kind": "shell", "entrypoint": "src/deck.js"},
            {"kind": "pptxgenjs", "entrypoint": "../outside.js"},
            {"kind": "pptxgenjs", "entrypoint": "/tmp/outside.js"},
            {"kind": "pptxgenjs", "entrypoint": "C:\\outside.js"},
            {"kind": "pptxgenjs", "entrypoint": "src/missing.js"},
            {"kind": "pptxgenjs", "entrypoint": "src/deck.js", "command": "node src/deck.js"},
        ]
        for renderer in mutations:
            with self.subTest(renderer=renderer), tempfile.TemporaryDirectory() as temporary:
                workspace = self.initialize(Path(temporary))
                self.compile_workspace(workspace)
                config_path = workspace / "workspace.json"
                config = json.loads(config_path.read_text())
                config["renderer"] = renderer
                json_write(config_path, config)
                report = WORKSPACE_READINESS.evaluate_workspace(workspace)
                self.assertEqual(report["status"], "blocked")
                self.assertTrue(any(item["code"].startswith("RENDERER_") for item in report["blockers"]))

        with tempfile.TemporaryDirectory() as temporary:
            workspace = self.initialize(Path(temporary), "template-edit")
            self.compile_workspace(workspace)
            manifest_path = workspace / "sources/manifest.json"
            manifest = json.loads(manifest_path.read_text())
            manifest["sources"][0]["path"] = "../outside.pptx"
            json_write(manifest_path, manifest)
            report = WORKSPACE_READINESS.evaluate_workspace(workspace)
            self.assertIn("PATH_OUTSIDE_WORKSPACE", {item["code"] for item in report["blockers"]})

        with tempfile.TemporaryDirectory() as temporary:
            workspace = self.initialize(Path(temporary))
            self.compile_workspace(workspace)
            config_path = workspace / "workspace.json"
            config = json.loads(config_path.read_text())
            config["paths"]["build_report"] = "../escaped-build.json"
            json_write(config_path, config)
            report = WORKSPACE_READINESS.evaluate_workspace(workspace)
            self.assertIn("PATH_OUTSIDE_WORKSPACE", {item["code"] for item in report["blockers"]})

    def test_font_build_render_and_target_behaviors(self):
        with tempfile.TemporaryDirectory() as temporary:
            workspace = self.initialize(Path(temporary))
            self.compile_workspace(workspace)
            font_path = workspace / "font-contract.json"
            contract = json.loads(font_path.read_text())
            contract["fonts"] = [{"role": "body", "family": "Brand Sans", "required": True, "fallback_allowed": False, "source": "user"}]
            json_write(font_path, contract)
            environment_path = workspace / "font-environment.json"
            environment = json.loads(environment_path.read_text())
            environment["status"] = "ready"
            environment["environments"]["build"].update({"status": "verified", "renderer": "test-build", "visible_fonts": []})
            environment["environments"]["render"].update({"status": "verified", "renderer": "test-render", "visible_fonts": ["Brand Sans"]})
            json_write(environment_path, environment)
            missing = WORKSPACE_READINESS.evaluate_workspace(workspace)
            self.assertEqual(missing["status"], "blocked")
            blocker_item = next(item for item in missing["blockers"] if item["code"] == "REQUIRED_FONT_UNAVAILABLE")
            self.assertEqual(blocker_item["next_action"], "need-user")

            environment["environments"]["build"]["visible_fonts"] = ["Brand Sans"]
            json_write(environment_path, environment)
            target_unknown = WORKSPACE_READINESS.evaluate_workspace(workspace)
            self.assertEqual(target_unknown["status"], "ready")
            self.assertIn("TARGET_FONT_UNVERIFIED", {item["code"] for item in target_unknown["unverified"]})
            audit = FONT_AUDIT.evaluate_font_audit(workspace)
            self.assertEqual(audit["status"], "unverified")
            self.assertEqual(audit["environments"]["build"]["required_missing"], [])

    def test_style_lock_binds_current_sources_proof_render_and_review(self):
        with tempfile.TemporaryDirectory() as temporary:
            workspace = self.initialize(Path(temporary))
            self.compile_workspace(workspace)
            readiness = WORKSPACE_READINESS.evaluate_workspace(workspace)
            self.assertEqual(readiness["status"], "ready", readiness)

            proof = workspace / "build/style-proof.pptx"
            proof.write_bytes(b"STYLE-PROOF")
            build_report = {
                "schema_version": "1.0",
                "report_kind": "build-report",
                "status": "succeeded",
                "build_kind": "style-proof",
                "source_fingerprint": readiness["source_fingerprint"],
                "renderer_source_sha256": readiness["renderer_source_sha256"],
                "outline_sha256": CORE.sha256_file(workspace / "outline.json"),
                "final_pptx": {"path": "build/style-proof.pptx", "sha256": CORE.sha256_file(proof)},
            }
            json_write(workspace / "build/style-proof-build-report.json", build_report)

            slide = workspace / "renders/style-proof/slides/slide-01.png"
            contact = workspace / "renders/style-proof/contact-sheet.png"
            slide.parent.mkdir(parents=True, exist_ok=True)
            slide.write_bytes(b"PROOF-SLIDE")
            contact.write_bytes(b"PROOF-CONTACT")
            aggregate = [
                {"slide_id": "slide-01", "path": "renders/style-proof/slides/slide-01.png", "sha256": CORE.sha256_file(slide)},
                {"slide_id": "_contact-sheet", "path": "renders/style-proof/contact-sheet.png", "sha256": CORE.sha256_file(contact)},
            ]
            render = {
                "schema_version": "1.0",
                "pptx_sha256": CORE.sha256_file(proof),
                "slide_ids": ["slide-01"],
                "artifacts": [aggregate[0]],
                "contact_sheet": {"path": aggregate[1]["path"], "sha256": aggregate[1]["sha256"]},
                "render_sha256": CORE.sha256_bytes(CORE.canonical_json_bytes(aggregate)),
            }
            json_write(workspace / "renders/style-proof/manifest.json", render)
            review = {
                "schema_version": "1.0",
                "report_kind": "visual-review",
                "review_scope": "style-proof",
                "reviewer": "image-capable-reviewer",
                "pptx_sha256": render["pptx_sha256"],
                "render_sha256": render["render_sha256"],
                "slide_ids": ["slide-01"],
                "pages": [{
                    "slide_id": "slide-01", "inspection_status": "inspected",
                    "checks": {"alignment": "pass", "spacing": "pass", "text_wrap": "pass", "overflow": "pass", "image_aspect": "not-applicable", "font_rendering": "pass", "reference_fidelity": "not-applicable"},
                    "observations": ["Style proof page was inspected."],
                }],
                "findings": [],
                "disposition": "pass",
            }
            json_write(workspace / "reviews/style-proof-review.json", review)

            result = STYLE_LOCK.create_style_lock(workspace)
            self.assertEqual(result["status"], "locked")
            current = CORE.validate_style_lock(workspace)
            self.assertEqual(current["lock"]["disposition"], "locked")

            design_path = workspace / "design-contract.json"
            design = json.loads(design_path.read_text(encoding="utf-8"))
            design["palette_roles"] = {"accent": "#123456"}
            json_write(design_path, design)
            with self.assertRaises(CORE.WorkspaceError) as raised:
                CORE.validate_style_lock(workspace)
            self.assertEqual(raised.exception.code, "STYLE_LOCK_STALE")


class DeliveryTests(unittest.TestCase):
    def initialize_ready_workspace(self, root: Path) -> Path:
        workspace = root / "workspace"
        INIT.initialize_workspace(workspace, "from-scratch", "delivery-deck", "Delivery Deck")
        result = COMPILER.compile_plan(
            workspace / "per-slide-content-plan.md",
            workspace / "outline.json",
            workspace_root=workspace,
        )
        self.assertEqual(result["status"], "compiled")
        return workspace

    def create_current_chain(self, workspace: Path):
        readiness = WORKSPACE_READINESS.evaluate_workspace(workspace)
        self.assertEqual(readiness["status"], "ready", readiness)
        final_pptx = workspace / "build/final.pptx"
        final_pptx.write_bytes(b"current-pptx-package")
        validation_report = workspace / "build/package-validation.json"
        validation_report.write_bytes(CORE.canonical_json_bytes({"status": "passed"}))
        pptx_sha = CORE.sha256_file(final_pptx)
        outline_sha = CORE.sha256_file(workspace / "outline.json")
        build = {
            "schema_version": "1.0",
            "status": "succeeded",
            "source_plan_sha256": readiness["source_plan_sha256"],
            "outline_sha256": outline_sha,
            "source_fingerprint": readiness["source_fingerprint"],
            "renderer_source_sha256": readiness["renderer_source_sha256"],
            "final_pptx": {"path": "build/final.pptx", "sha256": pptx_sha},
            "validation": {
                "status": "passed",
                "path": "build/package-validation.json",
                "report_sha256": CORE.sha256_file(validation_report),
                "pptx_sha256": pptx_sha,
            },
        }
        json_write(workspace / "build/build-report.json", build)

        autofit_evidence = {
            "schema_version": "1.0", "report_kind": "autofit-evidence", "status": "verified",
            "source_pptx_sha256": pptx_sha, "output_pptx_sha256": pptx_sha,
            "text_fit_policy": "shape-to-fit-text", "shapes": [], "blockers": [],
        }
        json_write(workspace / "build/autofit-evidence.json", autofit_evidence)
        build["autofit"] = {
            "status": "verified",
            "evidence_path": "build/autofit-evidence.json",
            "evidence_sha256": CORE.sha256_file(workspace / "build/autofit-evidence.json"),
            "pptx_sha256": pptx_sha,
        }
        json_write(workspace / "build/build-report.json", build)

        slide_image = workspace / "renders/final/slide-01.png"
        contact = workspace / "renders/final/contact-sheet.png"
        slide_image.write_bytes(b"rendered-slide")
        contact.write_bytes(b"contact-sheet")
        artifacts = [{
            "slide_id": "slide-01",
            "path": "renders/final/slide-01.png",
            "sha256": CORE.sha256_file(slide_image),
        }]
        contact_record = {"path": "renders/final/contact-sheet.png", "sha256": CORE.sha256_file(contact)}
        aggregate = artifacts + [{"slide_id": "_contact-sheet", **contact_record}]
        render_sha = CORE.sha256_bytes(CORE.canonical_json_bytes(aggregate))
        render = {
            "schema_version": "1.0",
            "pptx_sha256": pptx_sha,
            "render_sha256": render_sha,
            "slide_ids": ["slide-01"],
            "artifacts": artifacts,
            "contact_sheet": contact_record,
        }
        issues = {
            "schema_version": "1.0", "report_kind": "officecli-issues", "officecli_path": "/fake/officecli",
            "officecli_version": "1.0.143", "argv": ["/fake/officecli", "view", "build/final.pptx", "issues", "--json"],
            "pptx_sha256": pptx_sha, "count": 0, "issues": [],
        }
        json_write(workspace / "build/officecli-issues.json", issues)
        render["issue_scan"] = {
            "path": "build/officecli-issues.json",
            "sha256": CORE.sha256_file(workspace / "build/officecli-issues.json"),
            "pptx_sha256": pptx_sha,
        }
        json_write(workspace / "renders/final/manifest.json", render)
        json_write(workspace / "build/font-audit.json", readiness["font_audit"])
        layout_evidence = {
            "schema_version": "1.0", "report_kind": "layout-evidence", "pptx_sha256": pptx_sha,
            "slide_size": {"w": 100, "h": 100}, "shapes": [], "alignment_groups": [], "issue_dispositions": {},
        }
        json_write(workspace / "build/layout-evidence.json", layout_evidence)
        preflight = LAYOUT_PREFLIGHT.evaluate_layout_preflight(
            final_pptx_sha256=pptx_sha,
            template_profile_sha256=None,
            font_audit_sha256=CORE.sha256_file(workspace / "build/font-audit.json"),
            issues_sha256=CORE.sha256_file(workspace / "build/officecli-issues.json"),
            layout_evidence_sha256=CORE.sha256_file(workspace / "build/layout-evidence.json"),
            layout_evidence=layout_evidence,
            issues=issues,
            render_sha256=render_sha,
        )
        json_write(workspace / "build/layout-preflight.json", preflight)
        passing_checks = {
            "alignment": "pass", "spacing": "pass", "text_wrap": "pass", "overflow": "pass",
            "image_aspect": "not-applicable", "font_rendering": "pass", "reference_fidelity": "not-applicable",
        }
        review = {
            "schema_version": "1.0",
            "review_scope": "final",
            "reviewer": "image-capable-reviewer",
            "pptx_sha256": pptx_sha,
            "render_sha256": render_sha,
            "slide_ids": ["slide-01"],
            "pages": [{
                "slide_id": "slide-01", "page_id": "slide-01", "render_path": "renders/final/slide-01.png",
                "render_sha256": artifacts[0]["sha256"], "inspection_status": "inspected", "checks": passing_checks,
                "observations": ["No clipping, wrapping, or alignment drift is visible in the bound render."],
            }],
            "findings": [],
            "disposition": "pass",
        }
        json_write(workspace / "reviews/visual-review-final.json", review)
        return readiness

    def test_visual_review_requires_current_complete_hash_chain(self):
        with tempfile.TemporaryDirectory() as temporary:
            workspace = self.initialize_ready_workspace(Path(temporary))
            self.create_current_chain(workspace)
            ready = DELIVERY_READINESS.evaluate_delivery(workspace)
            self.assertEqual(ready["status"], "ready", ready)

            (workspace / "renders/final/slide-01.png").write_bytes(b"mutated-render")
            stale = DELIVERY_READINESS.evaluate_delivery(workspace)
            self.assertEqual(stale["status"], "blocked")
            self.assertIn("STALE_RENDER", {item["code"] for item in stale["blockers"]})

        with tempfile.TemporaryDirectory() as temporary:
            workspace = self.initialize_ready_workspace(Path(temporary))
            self.create_current_chain(workspace)
            review_path = workspace / "reviews/visual-review-final.json"
            review = json.loads(review_path.read_text())
            review["reviewer"] = ""
            json_write(review_path, review)
            blocked = DELIVERY_READINESS.evaluate_delivery(workspace)
            self.assertIn("STALE_VISUAL_REVIEW", {item["code"] for item in blocked["blockers"]})

        with tempfile.TemporaryDirectory() as temporary:
            workspace = self.initialize_ready_workspace(Path(temporary))
            self.create_current_chain(workspace)
            review_path = workspace / "reviews/visual-review-final.json"
            review = json.loads(review_path.read_text())
            review["pages"] = []
            json_write(review_path, review)
            blocked = DELIVERY_READINESS.evaluate_delivery(workspace)
            self.assertIn("STALE_VISUAL_REVIEW", {item["code"] for item in blocked["blockers"]})

    def test_source_and_renderer_changes_invalidate_build(self):
        with tempfile.TemporaryDirectory() as temporary:
            workspace = self.initialize_ready_workspace(Path(temporary))
            self.create_current_chain(workspace)
            design_path = workspace / "design-contract.json"
            design = json.loads(design_path.read_text())
            design["palette_roles"] = {"accent": "123456"}
            json_write(design_path, design)
            stale = DELIVERY_READINESS.evaluate_delivery(workspace)
            self.assertEqual(stale["status"], "blocked")
            self.assertIn("STALE_BUILD", {item["code"] for item in stale["blockers"]})

        with tempfile.TemporaryDirectory() as temporary:
            workspace = self.initialize_ready_workspace(Path(temporary))
            self.create_current_chain(workspace)
            renderer = workspace / "src/deck.js"
            renderer.write_text(renderer.read_text() + "\n// accepted layout implementation change\n")
            stale = DELIVERY_READINESS.evaluate_delivery(workspace)
            self.assertIn("STALE_BUILD", {item["code"] for item in stale["blockers"]})


if __name__ == "__main__":
    unittest.main()
