#!/usr/bin/env python3
"""Plan or execute OfficeCLI validation, inspection, and PNG render evidence."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence

from officecli_adapter import (
    OfficeCLIAdapterError,
    PINNED_VERSION,
    officecli_environment,
    parse_version,
    print_json,
    require_pinned_officecli,
    require_safe_officecli_argv,
)
from workspace_core import (
    WorkspaceError,
    canonical_json_bytes,
    contained_path,
    load_json,
    relative_workspace_path,
    sha256_bytes,
    sha256_file,
    write_json_atomic,
)


def _slides_from_outline(outline: Any) -> list[dict[str, Any]]:
    slides = outline.get("slides") if isinstance(outline, dict) else None
    if not isinstance(slides, list) or not slides:
        raise WorkspaceError("OUTLINE_INVALID", "outline.json must contain at least one slide")
    result: list[dict[str, Any]] = []
    for index, slide in enumerate(slides):
        if not isinstance(slide, dict):
            raise WorkspaceError("OUTLINE_INVALID", f"Slide {index + 1} is not an object")
        slide_id = slide.get("id") or slide.get("slide_id")
        ordinal = slide.get("ordinal", index + 1)
        if not isinstance(slide_id, str) or not slide_id or not isinstance(ordinal, int) or ordinal < 1:
            raise WorkspaceError("OUTLINE_INVALID", f"Slide {index + 1} needs a stable id and positive ordinal")
        result.append({"slide_id": slide_id, "ordinal": ordinal, "title": slide.get("title")})
    return result


def _help_action(binary: str, family: str, *topic: str) -> dict[str, Any]:
    return {"kind": "help", "family": family, "argv": [binary, "help", "pptx", *topic]}


def _command_action(family: str, argv: list[str], **extra: Any) -> dict[str, Any]:
    return {"kind": "command", "family": family, "argv": argv, **extra}


def prepare_render_packet(
    workspace_root: str | os.PathLike[str],
    *,
    pptx: str = "build/final.pptx",
    render_root: str = "renders/final",
    manifest_path: str | None = None,
    slide_ids: Sequence[str] | None = None,
    environ: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    root = Path(workspace_root).resolve()
    workspace = load_json(contained_path(root, "workspace.json", must_exist=True))
    if not isinstance(workspace, dict):
        raise WorkspaceError("WORKSPACE_INVALID", "workspace.json must contain an object")
    paths = workspace.get("paths", {}) if isinstance(workspace.get("paths"), dict) else {}
    outline_relative = paths.get("outline", "outline.json")
    outline_path = contained_path(root, outline_relative, must_exist=True)
    slides = _slides_from_outline(load_json(outline_path))
    if slide_ids is not None:
        requested = list(slide_ids)
        if not requested or len(requested) != len(set(requested)):
            raise WorkspaceError("STYLE_PROOF_SELECTION_INVALID", "Selected slide IDs must be non-empty and unique")
        known = {slide["slide_id"] for slide in slides}
        unknown = [item for item in requested if item not in known]
        if unknown:
            raise WorkspaceError("STYLE_PROOF_SELECTION_INVALID", f"Unknown selected slide IDs: {', '.join(unknown)}")
        requested_set = set(requested)
        slides = [slide for slide in slides if slide["slide_id"] in requested_set]
    pptx_path = contained_path(root, pptx, must_exist=True, code="RENDER_INPUT_OUTSIDE_WORKSPACE")
    output_root = contained_path(root, render_root, code="RENDER_OUTPUT_OUTSIDE_WORKSPACE")
    manifest_relative = manifest_path or (
        paths.get("render_manifest", f"{render_root}/manifest.json")
        if render_root == "renders/final"
        else f"{render_root}/manifest.json"
    )
    manifest_path = contained_path(root, manifest_relative, code="RENDER_OUTPUT_OUTSIDE_WORKSPACE")
    resolution = require_pinned_officecli(environ=environ)
    binary = str(resolution["path"])

    evidence_paths = {
        "validate": "build/package-validation.json",
        "issues": "build/officecli-issues.json",
        "outline": "build/officecli-outline.json",
        "text": "build/officecli-text.json",
        "contact_sheet": f"{render_root}/contact-sheet.png",
    }
    for relative in evidence_paths.values():
        contained_path(root, relative, code="RENDER_OUTPUT_OUTSIDE_WORKSPACE")

    actions: list[dict[str, Any]] = [
        {"kind": "version", "family": "version", "argv": [binary, "--version"]},
        _help_action(binary, "pptx"),
    ]
    command_specs = [
        (
            "validate",
            ("validate",),
            [binary, "pptx", "validate", str(pptx_path), "--json"],
            evidence_paths["validate"],
        ),
        (
            "issues",
            ("view", "issues"),
            [binary, "pptx", "view", "issues", str(pptx_path), "--json"],
            evidence_paths["issues"],
        ),
        (
            "outline",
            ("view", "outline"),
            [binary, "pptx", "view", "outline", str(pptx_path), "--json"],
            evidence_paths["outline"],
        ),
        (
            "text",
            ("view", "text"),
            [binary, "pptx", "view", "text", str(pptx_path), "--json"],
            evidence_paths["text"],
        ),
    ]
    for family, help_topic, argv, capture_path in command_specs:
        actions.append(_help_action(binary, family, *help_topic))
        actions.append(_command_action(family, argv, capture_path=capture_path))

    contact_path = contained_path(root, evidence_paths["contact_sheet"])
    actions.append(_help_action(binary, "contact-sheet", "screenshot"))
    actions.append(
        _command_action(
            "contact-sheet",
            [binary, "pptx", "screenshot", str(pptx_path), "--contact-sheet", "--output", str(contact_path)],
            expected_path=evidence_paths["contact_sheet"],
        )
    )
    artifacts: list[dict[str, Any]] = []
    for slide in slides:
        relative = f"{render_root}/slides/{slide['slide_id']}.png"
        output = contained_path(root, relative, code="RENDER_OUTPUT_OUTSIDE_WORKSPACE")
        actions.append(_help_action(binary, f"slide:{slide['slide_id']}", "screenshot"))
        actions.append(
            _command_action(
                f"slide:{slide['slide_id']}",
                [
                    binary,
                    "pptx",
                    "screenshot",
                    str(pptx_path),
                    "--slide",
                    str(slide["ordinal"]),
                    "--output",
                    str(output),
                ],
                expected_path=relative,
                slide_id=slide["slide_id"],
                page_id=f"slide-{slide['ordinal']:02d}",
            )
        )
        artifacts.append(
            {
                "slide_id": slide["slide_id"],
                "page_id": f"slide-{slide['ordinal']:02d}",
                "path": relative,
            }
        )
    for action in actions:
        require_safe_officecli_argv(action["argv"])

    return {
        "schema_version": 1,
        "status": "planned",
        "workspace_root": str(root),
        "render_root": render_root,
        "shell": False,
        "officecli": {
            "path": binary,
            "path_source": resolution["source"],
            "expected_version": PINNED_VERSION,
            "version": resolution["version"],
            "environment": {"OFFICECLI_SKIP_UPDATE": "1"},
        },
        "pptx": {"path": relative_workspace_path(root, pptx_path), "sha256": sha256_file(pptx_path)},
        "slide_ids": [slide["slide_id"] for slide in slides],
        "artifacts": artifacts,
        "contact_sheet": {"path": evidence_paths["contact_sheet"]},
        "manifest_path": relative_workspace_path(root, manifest_path),
        "actions": actions,
        "watch_included": False,
        "completion_proof": False,
        "host_image_inspection_required": True,
    }


def _run(
    argv: Sequence[str], root: Path, environ: Mapping[str, str], timeout: int
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        list(argv),
        cwd=root,
        env=dict(environ),
        shell=False,
        check=False,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def execute_render_packet(
    packet: Mapping[str, Any],
    *,
    environ: Mapping[str, str] | None = None,
    timeout: int = 120,
) -> dict[str, Any]:
    if packet.get("status") != "planned" or packet.get("shell") is not False:
        raise ValueError("Only a validated argv-based render packet may execute")
    root = Path(str(packet["workspace_root"])).resolve()
    fresh_packet = prepare_render_packet(
        root,
        pptx=packet.get("pptx", {}).get("path", ""),
        render_root=packet.get("render_root", ""),
        manifest_path=packet.get("manifest_path", ""),
        slide_ids=packet.get("slide_ids"),
        environ=environ,
    )
    comparison_keys = ("officecli", "pptx", "slide_ids", "artifacts", "contact_sheet", "manifest_path", "actions")
    if any(packet.get(key) != fresh_packet.get(key) for key in comparison_keys):
        raise ValueError("Render packet is stale, mutated, or not produced by the registered orchestrator")
    packet = fresh_packet
    office_env = officecli_environment(environ)
    version: str | None = None
    results: list[dict[str, Any]] = []
    for action in packet["actions"]:
        argv = action.get("argv")
        if not isinstance(argv, list):
            raise ValueError("Render actions must contain argv lists")
        require_safe_officecli_argv(argv)
        completed = _run(argv, root, office_env, timeout)
        results.append(
            {
                "kind": action["kind"],
                "family": action["family"],
                "argv": argv,
                "returncode": completed.returncode,
            }
        )
        if completed.returncode != 0:
            raise RuntimeError(f"OfficeCLI {action['kind']} {action['family']} failed: {completed.stderr.strip()}")
        if action["kind"] == "version":
            version = parse_version(completed.stdout + "\n" + completed.stderr)
        capture_relative = action.get("capture_path")
        if capture_relative:
            capture_path = contained_path(root, capture_relative)
            try:
                payload: Any = json.loads(completed.stdout) if completed.stdout.strip() else {}
            except json.JSONDecodeError:
                payload = {"stdout": completed.stdout, "stderr": completed.stderr}
            write_json_atomic(capture_path, payload)
        expected_relative = action.get("expected_path")
        if expected_relative:
            expected_path = contained_path(root, expected_relative)
            if not expected_path.is_file():
                raise RuntimeError(f"OfficeCLI render omitted expected output: {expected_relative}")

    if version != PINNED_VERSION:
        raise RuntimeError(f"OfficeCLI version changed during render: expected {PINNED_VERSION}, found {version or 'unparseable'}")

    artifact_records: list[dict[str, Any]] = []
    aggregate: list[dict[str, str]] = []
    for artifact in packet["artifacts"]:
        path = contained_path(root, artifact["path"], must_exist=True)
        record = {
            "slide_id": artifact["slide_id"],
            "page_id": artifact["page_id"],
            "path": artifact["path"],
            "sha256": sha256_file(path),
            "size": path.stat().st_size,
        }
        artifact_records.append(record)
        aggregate.append({"slide_id": record["slide_id"], "path": record["path"], "sha256": record["sha256"]})
    contact_path = contained_path(root, packet["contact_sheet"]["path"], must_exist=True)
    contact = {
        "path": packet["contact_sheet"]["path"],
        "sha256": sha256_file(contact_path),
        "size": contact_path.stat().st_size,
    }
    aggregate.append({"slide_id": "_contact-sheet", "path": contact["path"], "sha256": contact["sha256"]})
    manifest = {
        "schema_version": "1.0",
        "report_kind": "render-manifest",
        "status": "rendered-awaiting-visual-review",
        "pptx_path": packet["pptx"]["path"],
        "pptx_sha256": packet["pptx"]["sha256"],
        "slide_ids": list(packet["slide_ids"]),
        "artifacts": artifact_records,
        "contact_sheet": contact,
        "render_sha256": sha256_bytes(canonical_json_bytes(aggregate)),
        "officecli": {
            "path": packet["officecli"]["path"],
            "version": version,
            "expected_version": PINNED_VERSION,
            "version_drift": version != PINNED_VERSION if version is not None else True,
            "environment": {"OFFICECLI_SKIP_UPDATE": "1"},
            "actions": results,
        },
        "visual_review_passed": False,
        "host_image_inspection_required": True,
        "watch_used_as_proof": False,
    }
    write_json_atomic(contained_path(root, packet["manifest_path"]), manifest)
    return manifest


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workspace", help="PPTX workspace root")
    parser.add_argument("--pptx", default="build/final.pptx")
    parser.add_argument("--render-root", default="renders/final")
    parser.add_argument("--manifest-path", help="Workspace-relative render manifest output")
    parser.add_argument("--slide-id", action="append", dest="slide_ids", help="Render one selected stable slide ID; repeat for Style Proof")
    parser.add_argument("--mode", choices=("plan", "execute"), default="plan")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        packet = prepare_render_packet(
            args.workspace,
            pptx=args.pptx,
            render_root=args.render_root,
            manifest_path=args.manifest_path,
            slide_ids=args.slide_ids,
        )
        if args.mode == "plan":
            print_json(packet)
            return 0
        manifest = execute_render_packet(packet)
        print_json(manifest)
        return 0
    except (WorkspaceError, OfficeCLIAdapterError, OSError, RuntimeError, ValueError) as error:
        print_json({"status": "blocked", "error": {"code": getattr(error, "code", "RENDER_BLOCKED"), "message": str(error)}})
        return 2


if __name__ == "__main__":
    sys.exit(main())
