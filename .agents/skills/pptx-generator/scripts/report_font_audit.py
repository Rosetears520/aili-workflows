#!/usr/bin/env python3
"""Derive a hash-bound font audit from the current font contract evidence."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Sequence

from workspace_core import WorkspaceError, contained_path, load_json, sha256_file, write_json_atomic


def evaluate_font_contract(contract: Any, contract_sha256: str) -> dict[str, Any]:
    if not isinstance(contract, dict):
        raise WorkspaceError("FONT_CONTRACT_INVALID", "Font contract must contain an object")
    fonts = contract.get("fonts")
    environments = contract.get("environments")
    if not isinstance(fonts, list) or not isinstance(environments, dict):
        raise WorkspaceError("FONT_CONTRACT_INVALID", "Font contract needs fonts and environments")
    required: set[str] = set()
    for item in fonts:
        if (
            not isinstance(item, dict)
            or not isinstance(item.get("family"), str)
            or not item["family"]
            or not isinstance(item.get("required"), bool)
        ):
            raise WorkspaceError("FONT_CONTRACT_INVALID", "Every font needs a family and required boolean")
        if item["required"]:
            required.add(item["family"])

    audits: dict[str, dict[str, Any]] = {}
    need_user = False
    any_unverified = False
    for name in ("build", "render", "target"):
        environment = environments.get(name)
        if not isinstance(environment, dict):
            raise WorkspaceError("FONT_CONTRACT_INVALID", f"Font environment {name} must contain an object")
        status = environment.get("status")
        available = environment.get("available_fonts")
        substitutions = environment.get("observed_substitutions", [])
        if (
            status not in {"verified", "unverified"}
            or not isinstance(available, list)
            or not all(isinstance(item, str) for item in available)
            or not isinstance(substitutions, list)
            or not all(isinstance(item, str) for item in substitutions)
        ):
            raise WorkspaceError("FONT_CONTRACT_INVALID", f"Font environment {name} has an invalid evidence shape")
        missing = sorted(required - set(available)) if status == "verified" else sorted(required)
        audits[name] = {
            "status": status,
            "required_missing": missing,
            "observed_substitutions": substitutions,
        }
        if name in {"build", "render"} and required and (status != "verified" or missing):
            need_user = True
        if status != "verified":
            any_unverified = True

    return {
        "schema_version": "1.0",
        "font_contract_sha256": contract_sha256,
        "status": "need-user" if need_user else "unverified" if any_unverified else "passed",
        "environments": audits,
    }


def evaluate_font_audit(workspace_root: Path) -> dict[str, Any]:
    root = workspace_root.resolve()
    workspace = load_json(root / "workspace.json")
    paths = workspace.get("paths", {}) if isinstance(workspace, dict) and isinstance(workspace.get("paths"), dict) else {}
    relative = paths.get("font_contract", "font-contract.json")
    contract_path = contained_path(root, relative, must_exist=True)
    return evaluate_font_contract(load_json(contract_path), sha256_file(contract_path))


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workspace", help="PPTX workspace root")
    parser.add_argument("--output", help="Workspace-relative output (default: build/font-audit.json)")
    args = parser.parse_args(argv)
    root = Path(args.workspace).resolve()
    try:
        workspace = load_json(root / "workspace.json")
        paths = workspace.get("paths", {}) if isinstance(workspace, dict) and isinstance(workspace.get("paths"), dict) else {}
        output = args.output or paths.get("font_audit", "build/font-audit.json")
        result = evaluate_font_audit(root)
        write_json_atomic(contained_path(root, output), result)
        result = {**result, "output_path": output}
        code = 0 if result["status"] in {"passed", "unverified"} else 2
    except (WorkspaceError, OSError, ValueError) as error:
        result = {"status": "blocked", "error": {"code": getattr(error, "code", "FONT_AUDIT_BLOCKED"), "message": str(error)}}
        code = 2
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return code


if __name__ == "__main__":
    sys.exit(main())
