#!/usr/bin/env python3
"""Fail-closed Graphify contract checker and sole optional local launcher."""

from __future__ import annotations

import argparse
import base64
import csv
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import selectors
import shutil
import stat
import subprocess
import sys
import sysconfig
import tempfile
import time
from typing import Any, NamedTuple
import urllib.error
import urllib.request
import zipfile

try:
    import resource
except ImportError:  # pragma: no cover - execution is Linux-only and fails closed below
    resource = None


SCHEMA = "1.0"
BASELINE = {
    "repository": "Graphify-Labs/graphify",
    "version": "0.9.12",
    "commit": "35665a76ba26da0e1bfcab074fede19c94fc5c89",
    "distribution": "graphifyy",
    "executable": "graphify",
    "requires_python": ">=3.10",
    "license": "MIT",
    "artifact": "graphifyy-0.9.12-py3-none-any.whl",
    "artifact_sha256": "94f9d0d7ef68455a2055c7623fb9574c7a781afb1473d26c7936d1abfc14d62c",
}
EXTRACT_TEMPLATE = ["<verified-python-path>", "-I", "-m", "graphify", "extract", "<repo>", "--code-only", "--no-cluster", "--out", "<local-output-root>"]
CLUSTER_TEMPLATE = ["<verified-python-path>", "-I", "-m", "graphify", "cluster-only", "--graph", "<local-output-root>/graphify-out/graph.json", "--no-label", "--no-viz"]
CONTRACT_KEYS = ("schema_version", "status", "mode", "distribution", "executable", "source", "launcher", "controls", "cases", "blocked", "unverified", "errors", "temp_cleanup")
SECURITY_KEYS = ("schema_version", "status", "mode", "official_advisories", "security_policy", "package_metadata", "dependencies", "blocked", "unverified", "errors")
PROJECT_KEYS = ("schema_version", "status", "mode", "launch_attempted", "process_started", "target_root", "output_root", "argv", "environment", "network", "write_inventory", "output_inventory", "blocked", "unverified", "errors", "temp_cleanup")
REQUIRED_CATEGORIES = {"explicit-only", "root-output", "executable", "environment", "query", "network", "write-inventory", "advisory", "dependency", "false-run-claim", "argv-safety"}
SENSITIVE_ENV = re.compile(r"(?:TOKEN|SECRET|PASSWORD|PASSWD|CREDENTIAL|API_KEY|PRIVATE_KEY|COOKIE|AUTH|AWS_|AZURE_|GOOGLE_|GCP_|GITHUB_|GITLAB_|SSH_|GIT_ASKPASS|NETRC|DOCKER_|KUBE|VAULT|OPENAI_|ANTHROPIC_)", re.IGNORECASE)
FORBIDDEN_CONFIG_ENV = re.compile(r"(?:GRAPHIFY_.*(?:URL|BACKEND|CLOUD|INTEGRATION)|HTTP_PROXY|HTTPS_PROXY|ALL_PROXY|NO_PROXY)", re.IGNORECASE)
URLS = {
    "commit": f"https://api.github.com/repos/Graphify-Labs/graphify/commits/{BASELINE['commit']}",
    "pyproject": f"https://raw.githubusercontent.com/Graphify-Labs/graphify/{BASELINE['commit']}/pyproject.toml",
    "pinned_security": f"https://raw.githubusercontent.com/Graphify-Labs/graphify/{BASELINE['commit']}/SECURITY.md",
    "pinned_ci": f"https://raw.githubusercontent.com/Graphify-Labs/graphify/{BASELINE['commit']}/.github/workflows/ci.yml",
    "current_security": "https://raw.githubusercontent.com/Graphify-Labs/graphify/main/SECURITY.md",
    "current_ci": "https://raw.githubusercontent.com/Graphify-Labs/graphify/main/.github/workflows/ci.yml",
    "license": f"https://raw.githubusercontent.com/Graphify-Labs/graphify/{BASELINE['commit']}/LICENSE",
    "advisories": "https://api.github.com/repos/Graphify-Labs/graphify/security-advisories",
    "pypi": f"https://pypi.org/pypi/graphifyy/{BASELINE['version']}/json",
    "osv": "https://api.osv.dev/v1/query",
}
RESOURCE_LIMITS = {
    "cpu_seconds": 900,
    "address_space_bytes": 4 * 1024 * 1024 * 1024,
    "processes": 128,
    "file_bytes": 512 * 1024 * 1024,
    "open_files": 256,
    "captured_output_bytes": 1024 * 1024,
    "writable_bytes": 512 * 1024 * 1024,
    "writable_inodes": 100_000,
}
REFERENCE_CONTEXT_DIGESTS = frozenset("""
0bc2d1ee170b13e6af2985e734fa881d96ef13db0c8cd1c7449d31daae3e8e7a 0c5eef839b4550632eabec1be538589fb21af8deaab9b2576f64c8fc04525b37 0c922d7014a8a45aab9e3d000ae8b626504dea944c182514822e854bcbfa4e70 0e352863a13a8b407a631abed8ca6f5e164c4cd81bbf39a8f029e05e37b53e1c 0f09b8e894d76d78f496daaf1b2d170a11d090634052bf3ebb2873ece137a687 191adc033219773e0c8030f14ab19581cc0f1da57449d7459fe93d563c8d18aa 2741a203fb9ddabf52957085e120aba2be02046257aafc866f8fa10f4db06e4f 27e56626e75bb060117f2907d4ed8b3e18a0d1bc0fab5a69041e4a9347bf0898 3c723a3727ccb4df022d78fd1c3ea5197c3641170aa7fa6001cf523123e2ec7f 46f0bf633a1d8d591ac3c17735e541e6ed0cd395371554a59f62dc4ec688b941 480e28f9d430c7998f9605a4218faf5bc75a812fbba8c4aa70e90e776033e650 492aec1942e51185676ffe5efd47c02171557a0a1ffa2ce70b0e9b46fb3f6e0d 4c3e133ba19fd46c55dd033028006d3555800d3b2699b47f0f5c5b0c9671a9e3 59cc34429543c470be735e0dbe250f0a98c65aa55d48cec760999c10e689f4b0 5b9904e288371426c61c4abd45549b6b3a81adfbf4741b3596653ef987c25919 66f5d8d6f88d52fb6a020bb640d7ece32b41b12951d72c447e5f12d88896f1ca 6deb313078ee3214183fbbb0cc7ad40fdb3b3977518b2a143da2614e3b2e20f3 7208b437b758c039e169f5a3672da59b9eabe7ec1c3cb5782b816ecf074e7799 76614fad5d252522a698dad615bceb704fd56a9d2888f45fc0b1155887cbf979 81ff453c6361c0d713bd762474e5350eedd5cac47235acf4fb616a2543384b33 83a24a8063cd7f7ccaef53b2ae5bafd034aba2fd4d40471643d9c0f07fa01bf2 8433f128764e382900cc73c8615d84d31435d1ead8c398e8bc12783e4b1059dd 8dc85c42a2a9362ed1a177f5e292a0269b56917688c8275d449c7aef4df3c7fe 95c60cf102820059f01608c4e46ac9c3eb21ab79c9f18bc479ebf0644eda9f33 a3a0909875f7eca0001bfa609523da0e8009221d327a0ab56cc5868667f086ef a4cb05925d3cc033c6cbbfe76b7da0768634aa603a16ae7533ce088b7a0f8497 a7ef36ca276a6abc4028a950a873d566a45654c7db9ec14907b2b953925edd60 c608b7296b3773010042f48a05802ebb58ddde1dabea20caf0b796af0ea0c22e c9e43fea34e11b76daa73fd672b6ecebb2156bb1792a2c9185fdf643fefaa090 d199a4715649247c32de7174d147c42d0aa927e6d755ff05da7aec7dfdaa0649 ecf58fbf8315757d9b191307afe24e7b7c466ecd44fc3d4bbe1e3144cb87d148
""".split())
REFERENCE_CONTEXT_DIGESTS = (REFERENCE_CONTEXT_DIGESTS - {"66f5d8d6f88d52fb6a020bb640d7ece32b41b12951d72c447e5f12d88896f1ca", "a3a0909875f7eca0001bfa609523da0e8009221d327a0ab56cc5868667f086ef"}) | {"5553b3530f55e1b84a024b5a66f3d024da37f598c397db5a4d14a41afb63bbe7", "730aa7d89605a1800893f49b37c416139a1319b9892aaa801f962bfa9f153b79"}
CHECKER_OCCURRENCE_COUNT = 82

EXPECTED_CASE_OUTCOMES = {
    "no-install": "forbidden-no-process", "no-opencode-install": "forbidden-no-process",
    "no-register-hook": "forbidden-no-mutation", "no-auto-run": "skip-no-process",
    "wrong-target-root": "exit-3-process-false", "unsafe-output": "exit-5-process-false",
    "tracked-staged-output": "exit-5-process-false", "executable-mismatch": "exit-3-process-false",
    "sanitized-isolated-env": "remove-and-isolate", "workspace-integration-unset": "exit-3-process-false",
    "query-log-disabled": "GRAPHIFY_QUERY_LOG_DISABLE=1", "network-denial-required": "exit-3-process-false",
    "complete-write-inventory": "complete-pre-post-inventory", "unexpected-write": "exit-5",
    "stale-security-policy": "exit-3-unverified", "nonblocking-security-ci": "exit-3-unverified",
    "advisory-unavailable": "exit-3-unverified", "dependency-evidence": "exit-3-unverified",
    "known-unacceptable-risk": "exit-5-unsafe", "false-run-claim": "process_started=false-and-no-run-claim",
    "argv-space": "single-literal-argv", "argv-command-substitution": "single-literal-argv",
    "argv-semicolon": "single-literal-argv", "argv-quotes": "single-literal-argv",
    "argv-leading-dash": "single-literal-argv", "argv-unicode": "single-literal-argv",
    "argv-newline": "single-literal-argv",
    "minimal-runtime-mounts": "explicit-runtime-target-only", "full-namespace-isolation": "all-namespaces-private",
    "artifact-digest": "pinned-wheel-sha256-exact", "record-verification": "all-installed-files-sha256",
    "invalid-install-shape": "exit-3-process-false", "recursive-marker-closure": "active-installed-closure-complete",
    "root-advisory-query": "graphifyy-and-closure-osv", "fresh-evidence-separation": "pinned-exact-current-blocks",
    "repository-surface-scan": "derived-no-active-integration", "verified-cleanup": "removed-only-after-nonexistence",
    "graphify-process-semantics": "sandbox-preflight-is-not-graphify-start",
    "wheel-substitution": "exit-3-process-false", "exact-occurrence-allowlist": "path-and-context-exact",
    "timeout-start-state": "launch-attempted-start-unknown", "resource-enforcement": "rlimits-or-exit-3",
}


class RuntimeMounts(NamedTuple):
    readonly: tuple[Path, ...]
    masked: tuple[Path, ...]


def ordered(keys: tuple[str, ...], **values: Any) -> dict[str, Any]:
    return {key: values[key] for key in keys}


def project_path(root: Path, relative: str) -> Path:
    pure = PurePosixPath(relative)
    if pure.is_absolute() or ".." in pure.parts or str(pure) != relative:
        raise ValueError(f"non-canonical project path: {relative!r}")
    path = root.joinpath(*pure.parts)
    path.resolve(strict=False).relative_to(root)
    return path


def load_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected object")
    return value


def add_once(result: dict[str, Any], key: str, message: str) -> None:
    if message not in result[key]:
        result[key].append(message)


def block(result: dict[str, Any], message: str) -> None:
    add_once(result, "blocked", message)


def unverified(result: dict[str, Any], message: str) -> None:
    add_once(result, "unverified", message)
    block(result, message)


def unsafe(result: dict[str, Any], message: str) -> None:
    add_once(result, "errors", message)
    block(result, message)


def finish(result: dict[str, Any]) -> tuple[int, dict[str, Any]]:
    if result["errors"]:
        result["status"] = "unsafe"
        return 5, result
    if result["blocked"] or result["unverified"]:
        result["status"] = "unverified"
        return 3, result
    result["status"] = "exact"
    return 0, result


def fetch(url: str, payload: dict[str, Any] | None = None) -> tuple[Any, dict[str, Any]]:
    data = None if payload is None else json.dumps(payload, separators=(",", ":")).encode()
    request = urllib.request.Request(
        url,
        data=data,
        headers={"Accept": "application/vnd.github+json, application/json", "Content-Type": "application/json", "User-Agent": "rose-aili-graphify-baseline-check/1"},
        method="GET" if data is None else "POST",
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        body = response.read()
        content_type = response.headers.get_content_type()
    value: Any = json.loads(body) if "json" in content_type else body.decode("utf-8")
    return value, {"url": url, "fetched_at": datetime.now(timezone.utc).isoformat(), "network": "public-read"}


def fetch_bytes(url: str) -> tuple[bytes, dict[str, Any]]:
    request = urllib.request.Request(url, headers={"Accept": "application/octet-stream", "User-Agent": "rose-aili-graphify-baseline-check/1"})
    with urllib.request.urlopen(request, timeout=20) as response:
        body = response.read(100 * 1024 * 1024 + 1)
    if len(body) > 100 * 1024 * 1024:
        raise ValueError("approved wheel exceeds bounded download size")
    return body, {"url": url, "fetched_at": datetime.now(timezone.utc).isoformat(), "network": "public-read"}


def base_contract_result(mode: str) -> dict[str, Any]:
    return ordered(
        CONTRACT_KEYS,
        schema_version=SCHEMA,
        status="exact",
        mode=mode,
        distribution={"name": BASELINE["distribution"], "version": BASELINE["version"], "requires_python": BASELINE["requires_python"], "license": BASELINE["license"]},
        executable={"name": BASELINE["executable"], "required_realpath": True, "installed": None},
        source={"repository": BASELINE["repository"], "commit": BASELINE["commit"], "official_urls": URLS},
        launcher={"path": "scripts/graphify_baseline_check.py", "sole_launcher": True, "modes": ["contract", "security-evidence", "execute-synthetic", "execute-project"], "shell": False, "extract_argv": EXTRACT_TEMPLATE, "cluster_argv": CLUSTER_TEMPLATE},
        controls={},
        cases=[],
        blocked=[],
        unverified=[],
        errors=[],
        temp_cleanup={"created": [], "removed": [], "complete": True},
    )


def verify_fixture(fixture: dict[str, Any], result: dict[str, Any]) -> None:
    if fixture.get("schema_version") != SCHEMA or fixture.get("profile") != "strict-local":
        unsafe(result, "fixture schema/profile mismatch")
    if fixture.get("baseline") != BASELINE:
        unsafe(result, "fixture baseline mismatch")
    exact = fixture.get("exact_argv")
    if exact != {"extract": EXTRACT_TEMPLATE, "cluster": CLUSTER_TEMPLATE}:
        unsafe(result, "fixture exact argv mismatch")
    cases = fixture.get("cases")
    if not isinstance(cases, list):
        unsafe(result, "fixture cases must be a list")
        return
    seen: set[str] = set()
    categories: set[str] = set()
    for case in cases:
        if not isinstance(case, dict) or not {"id", "category", "mode", "input", "expected"}.issubset(case):
            unsafe(result, "fixture case missing required fields")
            continue
        if case["id"] in seen:
            unsafe(result, f"duplicate fixture id: {case['id']}")
        seen.add(case["id"])
        categories.add(case["category"])
        if EXPECTED_CASE_OUTCOMES.get(case["id"]) != case.get("expected"):
            unsafe(result, f"fixture expected outcome mismatch: {case['id']}")
        if case["mode"] not in {"contract", "security-evidence", "execute-synthetic", "execute-project"}:
            unsafe(result, f"invalid fixture mode: {case['id']}")
    if set(fixture.get("required_categories", [])) != REQUIRED_CATEGORIES or not REQUIRED_CATEGORIES.issubset(categories):
        unsafe(result, "fixture category coverage mismatch")
    required_ids = {"no-install", "no-opencode-install", "no-register-hook", "no-auto-run", "wrong-target-root", "unsafe-output", "tracked-staged-output", "executable-mismatch", "sanitized-isolated-env", "workspace-integration-unset", "query-log-disabled", "network-denial-required", "complete-write-inventory", "unexpected-write", "stale-security-policy", "nonblocking-security-ci", "advisory-unavailable", "dependency-evidence", "known-unacceptable-risk", "false-run-claim", "argv-space", "argv-command-substitution", "argv-semicolon", "argv-quotes", "argv-leading-dash", "argv-unicode", "argv-newline"}
    missing = sorted(required_ids - seen)
    if missing:
        unsafe(result, f"fixture cases missing: {missing}")
    forbidden = fixture.get("forbidden", {})
    if not isinstance(forbidden, dict) or not all(forbidden.get(item) is True for item in ("install", "register", "auto_run", "hook_plugin", "shell_form", "network_fallback", "output_overwrite", "tracked_output", "automatic_writeback")):
        unsafe(result, "fixture forbidden controls incomplete")
    result["cases"] = [{"id": item.get("id"), "category": item.get("category"), "covered": item.get("id") in seen} for item in cases if isinstance(item, dict)]


def repository_surface_scan(root: Path, result: dict[str, Any]) -> dict[str, Any]:
    """Scan tracked, untracked, and ignored registration surfaces fail-closed."""
    git = shutil.which("git")
    report: dict[str, Any] = {"complete": False, "files_scanned": 0, "candidates": [], "forbidden": [], "unreadable": [], "roots": []}
    if not git:
        unverified(result, "repository Graphify integration scan requires Git")
        return report
    try:
        proc = subprocess.run(
            [git, "-C", str(root), "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
            shell=False, capture_output=True, timeout=20, check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        unverified(result, f"repository Graphify integration scan unavailable: {exc}")
        return report
    if proc.returncode != 0:
        unverified(result, "repository Graphify integration scan failed")
        return report
    try:
        staged = subprocess.run(
            [git, "-C", str(root), "ls-files", "--stage", "-z"],
            shell=False, capture_output=True, timeout=20, check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        unverified(result, f"tracked executable-root enumeration unavailable: {exc}")
        return report
    if staged.returncode != 0:
        unverified(result, "tracked executable-root enumeration failed")
        return report
    tracked_names: set[str] = set()
    executable_tracked: set[str] = set()
    for raw in staged.stdout.split(b"\0"):
        if not raw:
            continue
        try:
            metadata, encoded_path = raw.split(b"\t", 1)
            tracked_names.add(os.fsdecode(encoded_path))
            if metadata.split(b" ", 1)[0] == b"100755":
                executable_tracked.add(os.fsdecode(encoded_path))
        except ValueError:
            unverified(result, "tracked executable-root enumeration was malformed")
            return report
    try:
        ignored = subprocess.run(
            [git, "-C", str(root), "ls-files", "--others", "--ignored", "--exclude-standard", "-z", "--", "package.json", ".agents/skills", "scripts", "commands", "agents", "manifests", ".opencode", "plugins", ".github/workflows", "workflow.components.yaml", "opencode.json", "opencode.jsonc"],
            shell=False, capture_output=True, timeout=20, check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        unverified(result, f"ignored Graphify registration-root scan unavailable: {exc}")
        return report
    if ignored.returncode != 0:
        unverified(result, "ignored Graphify registration-root scan failed")
        return report
    approved = {
        "scripts/graphify_baseline_check.py",
        "docs/harness/fixtures/graphify-local-review-fixtures.yaml",
        ".agents/skills/local-review-gate/references/graphify-local-review.md",
        ".agents/skills/local-review-gate/SKILL.md",
        "tests/graphify_baseline_check_test.py",
        "package.json",
    }
    active_prefixes = ("scripts/", "commands/", "agents/", "manifests/", ".agents/skills/", ".opencode/", "plugins/", ".github/workflows/")
    active_names = {"workflow.components.yaml", "opencode.json", "opencode.jsonc"}
    explicit_paths = {"package.json", ".agents/skills/local-review-gate/SKILL.md"}
    report["roots"] = sorted([*active_prefixes, *active_names, *explicit_paths])
    allowed_skill_lines = {
        ".agents/skills/local-review-gate/SKILL.md": "- `references/graphify-local-review.md`: explicit-operation-only Graphify adapter, pinned provenance/security concerns, sole guarded launcher, exact argv/network/environment/output controls, local-uncommitted output, and advisory-only findings. It adds no install, registration, hook/plugin, scheduler, lifecycle gate, or completion authority.",
        ".agents/skills/using-agent-skills/SKILL.md": "These are exactly four delivery shortcuts, not separate capabilities from natural language. Do not create or route to `/loop`, `/schedule`, `/goal`, `/proactive`, `/cycle`, `/watch`, `/objective`, worktree-maintenance, or Graphify commands, and do not turn interval/event protocol descriptions into schedulers, watchers, hooks, queues, or other background runtime.",
        ".agents/skills/aili-delivery-flow/references/artifact-contracts.md": "[KNOWN] Each convergence claim uses one link with `requirement_or_decision`, `task_or_package`, `file_or_artifact`, `fresh_verification`, `review_or_security_disposition`, `freshness`, and `status`. Status is `linked`, `missing`, `stale`, `conflicting`, `blocked`, or `Unverified`. A checked task, generated summary, CodeGraph result, or Graphify result is not a substitute for the link.",
        ".agents/skills/aili-delivery-flow/references/build-execution-loop.md": "Pre-action gates remain mandatory for destructive/high-risk operations, external roots, dependencies/lockfiles, secrets, Graphify execution, and unsafe runtime behavior. Before non-trivial closeout, inspect `git status --short --branch` and classify dirty paths as task-scoped, unrelated/pre-existing, generated/ignored, scratch, or unknown. Propose cleanup for remaining residue; ask explicit approval before push, destructive clean/reset, branch deletion, worktree removal, OpenSpec archive, stashing unrelated changes, or deleting user-visible artifacts. Savepoint commits may be proactive only when current task/project rules explicitly allow task-scoped verified commits; otherwise ask once with the cleanup package.",
    }
    names = {os.fsdecode(raw) for raw in (proc.stdout + ignored.stdout).split(b"\0") if raw}
    for relative in sorted(names, key=os.fsencode):
        source_like = "node_modules" not in PurePosixPath(relative).parts and Path(relative).suffix.lower() in {"", ".json", ".jsonc", ".md", ".yaml", ".yml", ".toml", ".py", ".js", ".mjs", ".cjs", ".ts", ".tsx", ".sh"}
        registration_surface = source_like and (relative.startswith(active_prefixes) or relative in active_names or relative in explicit_paths)
        active_surface = registration_surface
        if not source_like:
            continue
        try:
            path = project_path(root, relative)
            if not path.is_file():
                continue
            executable_kind = Path(relative).suffix.lower() in {"", ".py", ".js", ".mjs", ".cjs", ".ts", ".tsx", ".sh"}
            executable_surface = executable_kind and (relative in executable_tracked or (relative not in tracked_names and bool(path.stat().st_mode & 0o111)))
            active_surface = active_surface or executable_surface
            if path.stat().st_size > 2_000_000:
                if active_surface:
                    report["unreadable"].append(relative)
                continue
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError, ValueError):
            if active_surface:
                report["unreadable"].append(relative)
            continue
        report["files_scanned"] += 1
        if "graphify" not in text.lower() and "graphify" not in relative.lower():
            continue
        report["candidates"].append(relative)
        occurrence_lines = [line.strip() for line in text.splitlines() if "graphify" in line.lower()]
        forbidden_context = False
        if relative == "package.json":
            try:
                package = json.loads(text)
                graphify_values = [item for item in package.get("files", []) if "graphify" in str(item).lower()]
                package_exact = graphify_values == ["scripts/graphify_baseline_check.py", "docs/harness/fixtures/graphify-local-review-fixtures.yaml"] and occurrence_lines == ['"scripts/graphify_baseline_check.py",', '"docs/harness/fixtures/graphify-local-review-fixtures.yaml",'] and not any("graphify" in f"{key} {value}".lower() for key, value in package.get("scripts", {}).items())
            except (TypeError, ValueError, json.JSONDecodeError):
                package_exact = False
            forbidden_context = forbidden_context or not package_exact
        elif relative == ".agents/skills/local-review-gate/references/graphify-local-review.md":
            digests = [hashlib.sha256(line.encode()).hexdigest() for line in occurrence_lines]
            forbidden_context = len(digests) != len(REFERENCE_CONTEXT_DIGESTS) or set(digests) != REFERENCE_CONTEXT_DIGESTS
        elif relative in allowed_skill_lines:
            forbidden_context = occurrence_lines != [allowed_skill_lines[relative]]
        elif relative.startswith(".agents/skills/"):
            forbidden_context = bool(occurrence_lines)
        elif relative == "scripts/graphify_baseline_check.py":
            # The checker may name the guarded tool in executable Python, but a
            # free-form comment or newly added integration instruction is never allowed.
            forbidden_context = len(occurrence_lines) != CHECKER_OCCURRENCE_COUNT or any(line.startswith("#") for line in occurrence_lines)
        elif relative in {"scripts/harness_fixture_check.py", "scripts/workflow_contract_check.py"}:
            forbidden_context = False
        elif relative == "tests/graphify_baseline_check_test.py":
            forbidden_context = False
        elif relative.startswith("scripts/"):
            forbidden_context = bool(re.search(r"(?is)(?:subprocess|os\.system|exec|spawn|run).{0,200}\bgraphify\b|\bgraphify\b.{0,120}\b(?:install|extract|cluster-only|opencode)\b", text))
        elif registration_surface and relative not in approved:
            forbidden_context = bool(occurrence_lines)
        elif executable_surface:
            forbidden_context = bool(re.search(r"(?is)(?:subprocess|os\.system|exec|spawn|run).{0,200}\bgraphify\b|\bgraphify\b.{0,120}\b(?:install|extract|cluster-only|opencode|hook|plugin|autorun|auto-run)\b", text))
        if active_surface and forbidden_context:
            report["forbidden"].append(relative)
    report["candidates"].sort()
    report["forbidden"].sort()
    report["complete"] = not report["unreadable"]
    if report["unreadable"]:
        unverified(result, f"repository Graphify registration scan unreadable/incomplete: {report['unreadable']}")
    if report["forbidden"]:
        unsafe(result, f"repository Graphify install/register/hook/auto-run surfaces found: {report['forbidden']}")
    return report


def contract_mode(root: Path, fixture_path: Path, args: argparse.Namespace) -> tuple[int, dict[str, Any]]:
    result = base_contract_result("contract")
    if args.version != BASELINE["version"] or args.commit != BASELINE["commit"] or args.profile != "strict-local":
        unsafe(result, "requested baseline/profile differs from the pinned contract")
    try:
        fixture = load_object(fixture_path)
        verify_fixture(fixture, result)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        unsafe(result, f"fixture unavailable: {exc}")
    required_surfaces = {
        ".agents/skills/local-review-gate/references/graphify-local-review.md": ("sole guarded launcher", "graphify install --platform opencode", "subprocess.run([...], shell=False)"),
        "agents/rose.md": ("CodeGraph", "exact current repository root"),
        "agents/code-scout.md": ("CodeGraph", "exact current repository root"),
        ".agents/skills/repo-evidence-first/SKILL.md": ("CodeGraph", "exact current repository root"),
        ".agents/skills/agents-md-initialization/SKILL.md": ("CodeGraph", "exact current repository root"),
        ".agents/skills/context-engineering/SKILL.md": ("CodeGraph", "exact current repository root"),
        ".agents/skills/review-pipeline/SKILL.md": ("CodeGraph", "exact current repository root"),
        ".agents/skills/parallel-subagent-dispatch/SKILL.md": ("CodeGraph", "exact current repository root"),
        "templates/opencode-global-AGENTS.md": ("CodeGraph", "exact current repository root"),
    }
    for relative, markers in required_surfaces.items():
        try:
            text = project_path(root, relative).read_text(encoding="utf-8")
        except (OSError, ValueError) as exc:
            unsafe(result, f"required policy unavailable: {relative}: {exc}")
            continue
        lowered = text.lower()
        missing = [marker for marker in markers if marker.lower() not in lowered]
        if missing:
            unsafe(result, f"policy markers missing from {relative}: {missing}")
    source = Path(__file__).read_text(encoding="utf-8")
    source_markers = ("subprocess.Popen(", '"-I", "-m", "graphify"', "run_supervised", "EXTRACT_TEMPLATE", "CLUSTER_TEMPLATE", "execute-synthetic", "execute-project")
    if any(marker not in source for marker in source_markers):
        unsafe(result, "sole launcher source lacks required argv/shell=False contract")
    scan = repository_surface_scan(root, result)
    result["controls"] = {
        "explicit_operation_permission": True,
        "no_install_register_hook_auto_run": True,
        "exact_argv_shell_false": True,
        "canonical_executable_distribution": True,
        "current_security_dependency_evidence": True,
        "network_denial_required": True,
        "isolated_sanitized_environment": True,
        "private_new_output": True,
        "complete_write_inventory": True,
        "advisory_only_no_writeback": True,
        "execution_not_performed": True,
        "repository_surface_scan": scan,
    }
    return finish(result)


def security_result() -> dict[str, Any]:
    return ordered(SECURITY_KEYS, schema_version=SCHEMA, status="exact", mode="security-evidence", official_advisories={}, security_policy={}, package_metadata={}, dependencies={}, blocked=[], unverified=[], errors=[])


def normalized_name(value: str) -> str:
    return re.sub(r"[-_.]+", "-", value).lower()


def parse_trusted_wheel(wheel: bytes) -> dict[str, Any]:
    if hashlib.sha256(wheel).hexdigest() != BASELINE["artifact_sha256"]:
        raise ValueError("downloaded wheel SHA-256 differs from approved digest")
    with zipfile.ZipFile(io.BytesIO(wheel)) as archive:
        names = archive.namelist()
        record_names = [name for name in names if name.endswith(".dist-info/RECORD")]
        if len(record_names) != 1 or len(names) != len(set(names)):
            raise ValueError("wheel has missing/duplicate RECORD or duplicate paths")
        manifest: dict[str, str | None] = {}
        for row in csv.reader(io.StringIO(archive.read(record_names[0]).decode("utf-8"))):
            pure = PurePosixPath(row[0]) if row else PurePosixPath()
            if len(row) != 3 or not row[0] or row[0] in manifest or pure.is_absolute() or ".." in pure.parts:
                raise ValueError("wheel RECORD contains an invalid path/row")
            if row[0] == record_names[0]:
                if row[1] or row[2]:
                    raise ValueError("wheel RECORD self-entry must be unhashed")
                manifest[row[0]] = None
                continue
            if not row[1].startswith("sha256=") or not row[2].isdigit():
                raise ValueError("wheel RECORD entry lacks SHA-256/size")
            content = archive.read(row[0])
            digest = base64.urlsafe_b64encode(hashlib.sha256(content).digest()).rstrip(b"=").decode()
            if digest != row[1][7:] or len(content) != int(row[2]):
                raise ValueError("wheel bytes differ from wheel RECORD")
            manifest[row[0]] = digest
        if set(manifest) != set(names):
            raise ValueError("wheel has files absent from RECORD")
    return {"files": manifest, "record": record_names[0]}


def compare_installed_to_wheel(dist: importlib.metadata.Distribution, trusted: dict[str, Any]) -> dict[str, Any]:
    installed = {str(item): item for item in (dist.files or [])}
    expected: dict[str, str | None] = trusted["files"]
    missing = sorted(set(expected) - set(installed))
    allowed_script = f"../../../bin/{BASELINE['executable']}"
    extra = sorted(set(installed) - set(expected) - {allowed_script})
    mismatched: list[str] = []
    for relative, digest in expected.items():
        item = installed.get(relative)
        if item is None:
            continue
        path = Path(dist.locate_file(item))
        if not path.is_file():
            missing.append(relative)
        elif digest is not None:
            actual = base64.urlsafe_b64encode(hashlib.sha256(path.read_bytes()).digest()).rstrip(b"=").decode()
            if actual != digest or item.hash is None or item.hash.mode != "sha256" or item.hash.value != digest:
                mismatched.append(relative)
    return {"complete": not missing and not extra and not mismatched, "missing": sorted(set(missing)), "extra": extra, "mismatched": mismatched, "approved_generated_scripts": [allowed_script] if allowed_script in installed else []}


def verify_record(dist: importlib.metadata.Distribution) -> dict[str, Any]:
    files = list(dist.files or [])
    direct_url = next((item for item in files if str(item).endswith("direct_url.json")), None)
    editable = False
    if direct_url is not None:
        try:
            editable = bool(json.loads(Path(dist.locate_file(direct_url)).read_text(encoding="utf-8")).get("dir_info", {}).get("editable"))
        except (OSError, ValueError, json.JSONDecodeError):
            editable = True
    missing: list[str] = []
    unhashed: list[str] = []
    mismatched: list[str] = []
    for item in files:
        relative = str(item)
        path = Path(dist.locate_file(item))
        if not path.is_file():
            missing.append(relative)
        elif item.hash is None:
            if not relative.endswith(".dist-info/RECORD"):
                unhashed.append(relative)
        elif item.hash.mode != "sha256":
            mismatched.append(relative)
        else:
            actual = base64.urlsafe_b64encode(hashlib.sha256(path.read_bytes()).digest()).rstrip(b"=").decode()
            if actual != item.hash.value:
                mismatched.append(relative)
    return {"complete": bool(files) and not missing and not unhashed and not mismatched and not editable, "files": len(files), "missing": missing, "unhashed": unhashed, "mismatched": mismatched, "editable": editable}


def collect_pinned_provenance() -> dict[str, Any]:
    evidence: dict[str, tuple[Any, dict[str, Any]]] = {}
    blocked: list[str] = []
    for name in ("commit", "pyproject", "license", "pypi"):
        try:
            evidence[name] = fetch(URLS[name])
        except (OSError, ValueError, json.JSONDecodeError, urllib.error.URLError) as exc:
            blocked.append(f"UV-003: pinned official {name} evidence unavailable: {exc}")
    commit, pyproject = evidence.get("commit", ({}, {}))[0], evidence.get("pyproject", ("", {}))[0]
    license_text, pypi = evidence.get("license", ("", {}))[0], evidence.get("pypi", ({}, {}))[0]
    artifacts = pypi.get("urls", []) if isinstance(pypi, dict) else []
    artifact = next((item for item in artifacts if item.get("filename") == BASELINE["artifact"]), None)
    artifact_exact = bool(artifact and artifact.get("digests", {}).get("sha256") == BASELINE["artifact_sha256"] and not artifact.get("yanked"))
    wheel_manifest = None
    wheel_source: dict[str, Any] = {}
    if artifact_exact:
        try:
            wheel, wheel_source = fetch_bytes(artifact["url"])
            wheel_manifest = parse_trusted_wheel(wheel)
        except (KeyError, OSError, ValueError, zipfile.BadZipFile, UnicodeError, urllib.error.URLError) as exc:
            blocked.append(f"UV-003: approved wheel bytes/RECORD unavailable or invalid: {exc}")
    exact = not blocked and isinstance(commit, dict) and commit.get("sha") == BASELINE["commit"] and isinstance(pyproject, str) \
        and 'name = "graphifyy"' in pyproject and 'version = "0.9.12"' in pyproject and 'requires-python = ">=3.10"' in pyproject \
        and 'graphify = "graphify.__main__:main"' in pyproject and isinstance(license_text, str) and license_text.startswith("MIT License") and artifact_exact and wheel_manifest is not None
    return {"exact": exact, "artifact": {"filename": BASELINE["artifact"], "sha256": BASELINE["artifact_sha256"], "verified": artifact_exact and wheel_manifest is not None, "record_files": len(wheel_manifest["files"]) if wheel_manifest else 0, "source": wheel_source}, "sources": [meta for _, meta in evidence.values()], "blocked": blocked, "errors": ([] if blocked or exact else ["official pinned source/package/artifact baseline mismatch"]), "_wheel_manifest": wheel_manifest}


def collect_current_security() -> dict[str, Any]:
    evidence: dict[str, tuple[Any, dict[str, Any]]] = {}
    blocked: list[str] = []
    for name in ("current_security", "current_ci", "advisories"):
        try:
            evidence[name] = fetch(URLS[name])
        except (OSError, ValueError, json.JSONDecodeError, urllib.error.URLError) as exc:
            blocked.append(f"UV-003: fresh current {name} evidence unavailable: {exc}")
    security, ci, advisories = evidence.get("current_security", (None, {}))[0], evidence.get("current_ci", (None, {}))[0], evidence.get("advisories", (None, {}))[0]
    supported = bool(isinstance(security, str) and re.search(r"\|\s*0\.9(?:\.12|\.x)?\s*\|\s*(?:yes|✅)", security, re.IGNORECASE))
    nonblocking = isinstance(ci, str) and "security-scan:" in ci and ci.count("continue-on-error: true") >= 2 and "pip-audit" in ci and "bandit" in ci
    if isinstance(security, str) and not supported:
        blocked.append("UV-003: current official SECURITY.md does not explicitly support baseline 0.9.12")
    if nonblocking:
        blocked.append("UV-003: current official Bandit and pip-audit CI checks are non-blocking")
    if not isinstance(advisories, list):
        blocked.append("UV-003: current repository advisory response is not a list")
    return {"complete": not blocked, "support": {"source": evidence.get("current_security", (None, {}))[1], "baseline_supported_explicitly": supported if isinstance(security, str) else None}, "ci": {"source": evidence.get("current_ci", (None, {}))[1], "security_ci_nonblocking": nonblocking if isinstance(ci, str) else None}, "advisories": {"source": evidence.get("advisories", (None, {}))[1], "repository_advisory_count": len(advisories) if isinstance(advisories, list) else None, "empty_is_not_safety_proof": True}, "blocked": blocked}


def installed_closure_evidence(trusted_wheel: dict[str, Any] | None = None) -> tuple[importlib.metadata.Distribution | None, dict[str, Any], list[str], list[str]]:
    blocked: list[str] = []
    errors: list[str] = []
    executable = shutil.which(BASELINE["executable"])
    if not executable:
        return None, {"complete": False}, ["UV-003: graphify executable is not installed; provenance and dependency closure unavailable"], []
    realpath = Path(executable).resolve(strict=True)
    try:
        from packaging.markers import default_environment
        from packaging.requirements import Requirement
    except ImportError:
        return None, {"complete": False}, ["UV-003: marker-aware requirement parser unavailable"], []
    matches = [item for item in importlib.metadata.distributions() if normalized_name(item.metadata.get("Name", "")) == normalized_name(BASELINE["distribution"])]
    if len(matches) != 1:
        return None, {"complete": False, "matching_distributions": len(matches)}, ["UV-003: graphifyy install is missing or duplicated"], []
    root_dist = matches[0]
    entrypoint = any(item.group == "console_scripts" and item.name == BASELINE["executable"] and item.value == "graphify.__main__:main" for item in root_dist.entry_points)
    root_record = verify_record(root_dist)
    wheel_binding = compare_installed_to_wheel(root_dist, trusted_wheel) if trusted_wheel is not None else {"complete": False, "reason": "trusted wheel unavailable"}
    root_exact = root_dist.version == BASELINE["version"] and entrypoint and realpath.parent == Path(sys.executable).resolve().parent and root_record["complete"] and wheel_binding["complete"]
    if not root_exact:
        blocked.append("UV-003: executable/distribution/RECORD provenance is not exact, non-editable, unique graphifyy==0.9.12")
    environment = default_environment()
    environment["extra"] = ""
    queue, seen, closure, unacceptable = [root_dist], set(), [], []
    while queue:
        current = queue.pop(0)
        name = current.metadata.get("Name", "")
        if normalized_name(name) in seen:
            continue
        seen.add(normalized_name(name))
        record = verify_record(current)
        item: dict[str, Any] = {"name": name, "version": current.version, "record": record, "active_requirements": [], "osv": []}
        if not record["complete"]:
            blocked.append(f"UV-003: installed RECORD verification incomplete for {name}=={current.version}")
        try:
            osv, source = fetch(URLS["osv"], {"package": {"name": name, "ecosystem": "PyPI"}, "version": current.version})
            item["osv_source"], item["osv"] = source, osv.get("vulns", []) if isinstance(osv, dict) else []
            if not isinstance(osv, dict):
                blocked.append(f"UV-003: OSV response invalid for {name}=={current.version}")
            unacceptable.extend({"dependency": name, "version": current.version, "id": vuln.get("id"), "severity": vuln.get("severity", [])} for vuln in item["osv"])
        except (OSError, ValueError, json.JSONDecodeError, urllib.error.URLError) as exc:
            blocked.append(f"UV-003: advisory evidence unavailable for {name}=={current.version}: {exc}")
        for raw in current.requires or []:
            try:
                requirement = Requirement(raw)
                if requirement.marker is not None and not requirement.marker.evaluate(environment=environment):
                    continue
                queue.append(importlib.metadata.distribution(requirement.name))
                item["active_requirements"].append(str(requirement))
            except (ValueError, importlib.metadata.PackageNotFoundError) as exc:
                blocked.append(f"UV-003: installed dependency closure unresolved from {name}: {raw}: {exc}")
        item["active_requirements"].sort()
        closure.append(item)
    if unacceptable:
        errors.append(f"applicable installed root/dependency advisories require resolution: {unacceptable}")
    return root_dist, {"complete": not blocked and not errors, "executable_realpath": str(realpath), "root_exact": root_exact, "trusted_wheel_binding": wheel_binding, "marker_environment": environment, "closure": closure, "unacceptable": unacceptable}, blocked, errors


def security_evidence(args: argparse.Namespace) -> tuple[int, dict[str, Any]]:
    result = security_result()
    if args.version != BASELINE["version"] or args.commit != BASELINE["commit"] or args.profile != "strict-local":
        unsafe(result, "requested baseline/profile differs from the pinned contract")
        return finish(result)
    pinned = collect_pinned_provenance()
    trusted_wheel = pinned.pop("_wheel_manifest", None)
    result["package_metadata"]["pinned_provenance"] = pinned
    current = collect_current_security()
    result["security_policy"]["current"] = current
    result["official_advisories"] = current.get("advisories", {})
    _, closure, closure_blocked, closure_errors = installed_closure_evidence(trusted_wheel)
    result["dependencies"]["installed_closure"] = closure
    for message in [*pinned.get("blocked", []), *current.get("blocked", []), *closure_blocked]:
        unverified(result, message)
    for message in [*pinned.get("errors", []), *closure_errors]:
        unsafe(result, message)
    return finish(result)


def has_symlink_component(path: Path, include_leaf: bool = True) -> bool:
    candidate = path if include_leaf else path.parent
    parts = candidate.parts
    current = Path(parts[0]) if candidate.is_absolute() else Path()
    for part in parts[1:] if candidate.is_absolute() else parts:
        current /= part
        if current.exists() or current.is_symlink():
            if stat.S_ISLNK(current.lstat().st_mode):
                return True
    return False


def is_within(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def snapshot(roots: list[Path]) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for root in roots:
        if not root.exists():
            continue
        for path in sorted([root, *root.rglob("*")], key=lambda item: os.fsencode(str(item))):
            info = path.lstat()
            entries.append({"root": str(root), "path": str(path.relative_to(root)) or ".", "type": "symlink" if path.is_symlink() else "directory" if path.is_dir() else "file", "mode": f"{stat.S_IMODE(info.st_mode):04o}", "size": info.st_size})
    return entries


def sanitized_environment(home: Path, config: Path, cache: Path, data: Path, temp: Path) -> tuple[dict[str, str], dict[str, Any]]:
    kept = {key: value for key, value in os.environ.items() if key in {"LANG", "LC_ALL", "LC_CTYPE", "TZ"} and not SENSITIVE_ENV.search(key) and not FORBIDDEN_CONFIG_ENV.search(key)}
    kept.update({"HOME": str(home), "XDG_CONFIG_HOME": str(config), "XDG_CACHE_HOME": str(cache), "XDG_DATA_HOME": str(data), "TMPDIR": str(temp), "GRAPHIFY_QUERY_LOG_DISABLE": "1", "PYTHONNOUSERSITE": "1"})
    kept.pop("GRAPHIFY_GOOGLE_WORKSPACE", None)
    report = {"isolated": True, "allowlisted_ambient": sorted(key for key in kept if key in {"LANG", "LC_ALL", "LC_CTYPE", "TZ"}), "path_unset": "PATH" not in kept, "credential_variables_removed": sorted(key for key in os.environ if SENSITIVE_ENV.search(key)), "proxy_integration_variables_removed": sorted(key for key in os.environ if FORBIDDEN_CONFIG_ENV.search(key)), "workspace_integration_unset": "GRAPHIFY_GOOGLE_WORKSPACE" not in kept, "query_logging_disabled": kept.get("GRAPHIFY_QUERY_LOG_DISABLE") == "1", "paths": {key: kept[key] for key in ("HOME", "XDG_CONFIG_HOME", "XDG_CACHE_HOME", "XDG_DATA_HOME", "TMPDIR")}}
    return kept, report


def executable_preflight(expected_version: str, trusted_wheel_binding: bool = False) -> tuple[Path | None, dict[str, Any], str | None]:
    executable = shutil.which(BASELINE["executable"])
    if not executable:
        return None, {}, "graphify executable unavailable"
    realpath = Path(executable).resolve(strict=True)
    matches = [item for item in importlib.metadata.distributions() if normalized_name(item.metadata.get("Name", "")) == normalized_name(BASELINE["distribution"])]
    if len(matches) != 1:
        return None, {"realpath": str(realpath)}, "graphifyy distribution unavailable in checker environment"
    dist = matches[0]
    exact_entry = any(entry.group == "console_scripts" and entry.name == "graphify" and entry.value == "graphify.__main__:main" for entry in dist.entry_points)
    record = verify_record(dist)
    interpreter = Path(sys.executable).absolute()
    interpreter_realpath = interpreter.resolve(strict=True)
    same_environment = Path(executable).absolute().parent == interpreter.parent
    exact = dist.version == expected_version and exact_entry and same_environment and record["complete"] and trusted_wheel_binding
    report = {"generated_launcher_realpath": str(realpath), "launcher_executed": False, "verified_interpreter_path": str(interpreter), "verified_interpreter_realpath": str(interpreter_realpath), "module": "graphify", "distribution": dist.metadata.get("Name"), "version": dist.version, "entrypoint_exact": exact_entry, "checker_environment": same_environment, "record": record, "trusted_wheel_binding": trusted_wheel_binding, "unique_distribution": len(matches) == 1, "exact": exact}
    return (interpreter if exact else None), report, (None if exact else "canonical module/interpreter/wheel provenance mismatch")


def dynamic_libraries(paths: list[Path]) -> tuple[set[Path], str | None]:
    ldd = shutil.which("ldd")
    if not ldd:
        return set(), "ldd unavailable"
    libraries: set[Path] = set()
    for path in paths:
        try:
            proc = subprocess.run([ldd, str(path)], shell=False, text=True, capture_output=True, timeout=20, check=False)
        except (OSError, subprocess.TimeoutExpired) as exc:
            return set(), f"runtime library resolution failed for {path}: {exc}"
        if proc.returncode != 0:
            return set(), f"runtime library resolution failed for {path}"
        for line in proc.stdout.splitlines():
            match = re.search(r"(?:=>\s+)?(/[^\s(]+)", line)
            if match:
                candidate = Path(match.group(1)).resolve(strict=True)
                if not candidate.is_file():
                    return set(), f"runtime library is not a file: {candidate}"
                libraries.add(candidate)
    return libraries, None


def installed_runtime_distributions() -> tuple[list[importlib.metadata.Distribution], str | None]:
    try:
        from packaging.markers import default_environment
        from packaging.requirements import Requirement
    except ImportError:
        return [], "marker-aware requirement parser unavailable"
    try:
        root = importlib.metadata.distribution(BASELINE["distribution"])
    except importlib.metadata.PackageNotFoundError:
        return [], "graphifyy distribution unavailable"
    environment = default_environment()
    environment["extra"] = ""
    queue, seen, result = [root], set(), []
    while queue:
        current = queue.pop(0)
        name = normalized_name(current.metadata.get("Name", ""))
        if name in seen:
            continue
        seen.add(name)
        result.append(current)
        for raw in current.requires or []:
            try:
                requirement = Requirement(raw)
                if requirement.marker is None or requirement.marker.evaluate(environment=environment):
                    queue.append(importlib.metadata.distribution(requirement.name))
            except (ValueError, importlib.metadata.PackageNotFoundError) as exc:
                return [], f"runtime dependency closure unresolved: {raw}: {exc}"
    return result, None


def construct_runtime_mounts(interpreter: Path) -> tuple[RuntimeMounts | None, str | None]:
    """Build an explicit Python/Graphify runtime while omitting neighboring installs."""
    distributions, error = installed_runtime_distributions()
    if error:
        return None, error
    interpreter_path = Path(sys.executable)
    if interpreter.resolve(strict=True) != interpreter_path.resolve(strict=True):
        return None, "verified interpreter differs from checker interpreter"
    stdlib = Path(sysconfig.get_path("stdlib")).resolve(strict=True)
    site_roots = {Path(value).resolve(strict=True) for key in ("purelib", "platlib") if (value := sysconfig.get_path(key))}
    readonly: set[Path] = {interpreter_path, interpreter.resolve(strict=True)}
    pyvenv = interpreter_path.parent.parent / "pyvenv.cfg"
    if pyvenv.is_file():
        readonly.add(pyvenv.resolve(strict=True))
    # Mount stdlib one direct child at a time so nested site-packages is never exposed.
    for child in stdlib.iterdir():
        resolved = child.resolve(strict=True)
        if any(resolved == site or is_within(resolved, site) or is_within(site, resolved) for site in site_roots):
            continue
        readonly.add(resolved)
    native_files = [interpreter]
    for dist in distributions:
        if not verify_record(dist)["complete"]:
            return None, f"runtime distribution RECORD is not exact: {dist.metadata.get('Name')}"
        for item in dist.files or []:
            installed_path = Path(dist.locate_file(item))
            if has_symlink_component(installed_path):
                return None, f"runtime distribution file has a symlink component: {installed_path}"
            path = installed_path.resolve(strict=True)
            containing = next((site for site in site_roots if is_within(path, site)), None)
            if containing is None:
                continue
            readonly.add(path)
            if path.suffix == ".so":
                native_files.append(path)
    libraries, library_error = dynamic_libraries(native_files)
    if library_error:
        return None, library_error
    readonly.update(libraries)
    cache = Path("/etc/ld.so.cache")
    if cache.is_file():
        readonly.add(cache)
    if not readonly or any(path == Path("/") for path in readonly):
        return None, "minimal runtime mount set is invalid"
    return RuntimeMounts(tuple(sorted(readonly, key=lambda item: os.fsencode(str(item)))), tuple(sorted(site_roots, key=lambda item: os.fsencode(str(item))))), None


def mount_parent_dirs(paths: list[Path]) -> list[Path]:
    parents: set[Path] = set()
    for path in paths:
        current = path.parent
        while current != Path("/"):
            parents.add(current)
            current = current.parent
    return sorted(parents, key=lambda item: (len(item.parts), os.fsencode(str(item))))


def bwrap_preflight() -> tuple[Path | None, dict[str, Any]]:
    found = shutil.which("bwrap")
    if not found:
        return None, {"required": True, "enforcer": "bubblewrap", "available": False, "canary": False}
    realpath = Path(found).resolve(strict=True)
    true = Path(shutil.which("true") or "").resolve(strict=True) if shutil.which("true") else None
    if true is None:
        return None, {"required": True, "enforcer": "bubblewrap", "available": True, "canary": False, "reason": "true unavailable"}
    libraries, error = dynamic_libraries([true])
    if error:
        return None, {"required": True, "enforcer": "bubblewrap", "available": True, "canary": False, "reason": error}
    runtime = RuntimeMounts(tuple(sorted({true, *libraries}, key=lambda item: os.fsencode(str(item)))), ())
    try:
        proc = subprocess.run(sandbox_command(realpath, Path("/"), Path("/tmp"), [], [str(true)], runtime, canary=True), shell=False, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True, timeout=15, check=False)
        ok = proc.returncode == 0
    except (OSError, subprocess.TimeoutExpired):
        ok = False
    return (realpath if ok else None), {"required": True, "enforcer": "bubblewrap", "realpath": str(realpath), "available": True, "canary": ok, "exact_process_wrapped": ok, "fallback": False}


def validate_target_output(target_arg: str, output_arg: str, result: dict[str, Any]) -> tuple[Path | None, Path | None]:
    target_lexical, output_lexical = Path(target_arg), Path(output_arg)
    if not target_lexical.is_absolute() or not output_lexical.is_absolute():
        unverified(result, "target and output roots require exact canonical absolute paths")
        return None, None
    try:
        target = target_lexical.resolve(strict=True)
        output_parent = output_lexical.parent.resolve(strict=True)
    except OSError as exc:
        unverified(result, f"target/output parent unavailable: {exc}")
        return None, None
    output = output_parent / output_lexical.name
    if str(target) != str(target_lexical) or str(output) != str(output_lexical) or not target.is_dir():
        unverified(result, "target/output paths are not exact canonical directories")
        return None, None
    if has_symlink_component(target) or has_symlink_component(output, include_leaf=False):
        unsafe(result, "target/output path has a symlink component")
    if output.exists() or output.is_symlink():
        unsafe(result, "output root already exists; overwrite/reuse is forbidden")
    if is_within(output, target) or is_within(target, output):
        unsafe(result, "source/output overlap is forbidden")
    return target, output


def git_output_safety(target: Path, output: Path, result: dict[str, Any]) -> dict[str, Any]:
    git = shutil.which("git")
    report = {"checked": False, "inside_target": is_within(output, target), "tracked": False, "staged": False, "output_repository_root": None}
    if report["inside_target"]:
        unsafe(result, "output root is inside source and may be tracked/staged")
        return report
    if not git:
        unverified(result, "Git unavailable; local/uncommitted output status cannot be checked")
        return report
    try:
        source_proc = subprocess.run([git, "-C", str(target), "rev-parse", "--show-toplevel"], shell=False, text=True, capture_output=True, timeout=10, check=False)
        report["source_repository_root"] = source_proc.stdout.strip() if source_proc.returncode == 0 else None
        output_proc = subprocess.run([git, "-C", str(output.parent), "rev-parse", "--show-toplevel"], shell=False, text=True, capture_output=True, timeout=10, check=False)
        if output_proc.returncode == 0:
            output_repo = Path(output_proc.stdout.strip()).resolve(strict=True)
            report["output_repository_root"] = str(output_repo)
            relative = output.relative_to(output_repo)
            tracked = subprocess.run([git, "-C", str(output_repo), "ls-files", "--stage", "--", str(relative)], shell=False, text=True, capture_output=True, timeout=10, check=False)
            staged = subprocess.run([git, "-C", str(output_repo), "diff", "--cached", "--name-only", "--", str(relative)], shell=False, text=True, capture_output=True, timeout=10, check=False)
            report["tracked"] = bool(tracked.stdout.strip())
            report["staged"] = bool(staged.stdout.strip())
            if report["tracked"] or report["staged"]:
                unsafe(result, "output root is tracked or staged")
        report["checked"] = True
    except (OSError, subprocess.TimeoutExpired) as exc:
        unverified(result, f"Git output safety check unavailable: {exc}")
    return report


def execution_result(mode: str, target_arg: str | None, output_arg: str | None) -> dict[str, Any]:
    if mode == "execute-project":
        return ordered(PROJECT_KEYS, schema_version=SCHEMA, status="exact", mode=mode, launch_attempted=False, process_started=False, target_root=target_arg, output_root=output_arg, argv=[], environment={}, network={}, write_inventory={}, output_inventory=[], blocked=[], unverified=[], errors=[], temp_cleanup={"created": [], "removed": [], "complete": True})
    result = base_contract_result(mode)
    result.update({"launch_attempted": False, "process_started": False, "target_root": target_arg, "output_root": output_arg, "argv": [], "environment": {}, "network": {}, "write_inventory": {}, "output_inventory": []})
    return result


def sandbox_command(bwrap: Path, target: Path, output: Path, writable: list[Path], argv: list[str], runtime: RuntimeMounts, canary: bool = False) -> list[str]:
    mount_paths = list(runtime.readonly) + ([] if canary else [target, output, *writable]) + [Path("/proc"), Path("/dev")]
    command = [str(bwrap), "--die-with-parent", "--new-session", "--unshare-user", "--unshare-pid", "--unshare-ipc", "--unshare-uts", "--unshare-net"]
    for parent in mount_parent_dirs(mount_paths):
        command.extend(["--dir", str(parent)])
    command.extend(["--proc", "/proc", "--dev", "/dev"])
    for path in runtime.readonly:
        command.extend(["--ro-bind", str(path), str(path)])
    if not canary:
        command.extend(["--ro-bind", str(target), str(target), "--bind", str(output), str(output)])
    for path in writable:
        command.extend(["--bind", str(path), str(path)])
    command.extend(["--chdir", str(target if not canary else Path("/")), "--", *argv])
    return command


def resource_limiter() -> Any:
    if resource is None or not all(hasattr(resource, name) for name in ("RLIMIT_CPU", "RLIMIT_AS", "RLIMIT_NPROC", "RLIMIT_FSIZE", "RLIMIT_NOFILE")):
        return None

    def apply() -> None:
        for name, value in (("RLIMIT_CPU", RESOURCE_LIMITS["cpu_seconds"]), ("RLIMIT_AS", RESOURCE_LIMITS["address_space_bytes"]), ("RLIMIT_NPROC", RESOURCE_LIMITS["processes"]), ("RLIMIT_FSIZE", RESOURCE_LIMITS["file_bytes"]), ("RLIMIT_NOFILE", RESOURCE_LIMITS["open_files"])):
            current_hard = resource.getrlimit(getattr(resource, name))[1]
            hard = value if current_hard == resource.RLIM_INFINITY else min(value, current_hard)
            resource.setrlimit(getattr(resource, name), (min(value, hard), hard))

    return apply


def writable_usage(roots: list[Path]) -> dict[str, Any]:
    """Measure cumulative regular-file bytes and directory entries fail-closed."""
    total_bytes = 0
    total_inodes = 0
    errors: list[str] = []
    for root in roots:
        try:
            paths = [root] if root.exists() else []
            while paths:
                path = paths.pop()
                info = path.lstat()
                total_inodes += 1
                if stat.S_ISREG(info.st_mode):
                    total_bytes += info.st_size
                elif stat.S_ISDIR(info.st_mode):
                    with os.scandir(path) as entries:
                        for entry in entries:
                            paths.append(Path(entry.path))
                            if total_inodes + len(paths) > RESOURCE_LIMITS["writable_inodes"]:
                                total_inodes = RESOURCE_LIMITS["writable_inodes"] + 1
                                paths.clear()
                                break
                if total_bytes > RESOURCE_LIMITS["writable_bytes"] or total_inodes > RESOURCE_LIMITS["writable_inodes"]:
                    break
        except (OSError, ValueError) as exc:
            errors.append(f"{root}: {exc}")
        if total_bytes > RESOURCE_LIMITS["writable_bytes"] or total_inodes > RESOURCE_LIMITS["writable_inodes"]:
            break
    return {
        "bytes": total_bytes,
        "inodes": total_inodes,
        "byte_limit": RESOURCE_LIMITS["writable_bytes"],
        "inode_limit": RESOURCE_LIMITS["writable_inodes"],
        "within_quota": not errors and total_bytes <= RESOURCE_LIMITS["writable_bytes"] and total_inodes <= RESOURCE_LIMITS["writable_inodes"],
        "errors": errors,
    }


def run_supervised(command: list[str], env: dict[str, str], limiter: Any, writable: list[Path]) -> dict[str, Any]:
    """Run one sandboxed command with active stream and writable-tree quotas."""
    proc = subprocess.Popen(
        command, shell=False, env=env, stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, preexec_fn=limiter,
    )
    if proc.stdout is None or proc.stderr is None:  # pragma: no cover - PIPE contract
        proc.kill()
        proc.wait()
        raise OSError("bounded output pipes unavailable")
    selector = selectors.DefaultSelector()
    selector.register(proc.stdout, selectors.EVENT_READ, "stdout")
    selector.register(proc.stderr, selectors.EVENT_READ, "stderr")
    captured = {"stdout": bytearray(), "stderr": bytearray()}
    total_captured = 0
    deadline = time.monotonic() + RESOURCE_LIMITS["cpu_seconds"] + 30
    violation: str | None = None
    usage = writable_usage(writable)
    try:
        while selector.get_map() or proc.poll() is None:
            if time.monotonic() >= deadline:
                proc.kill()
                proc.wait()
                raise subprocess.TimeoutExpired(command, RESOURCE_LIMITS["cpu_seconds"] + 30)
            for key, _ in selector.select(timeout=0.05):
                chunk = os.read(key.fileobj.fileno(), 65536)
                if not chunk:
                    selector.unregister(key.fileobj)
                    continue
                total_captured += len(chunk)
                remaining = max(0, RESOURCE_LIMITS["captured_output_bytes"] - len(captured[key.data]))
                captured[key.data].extend(chunk[:remaining])
                if total_captured > RESOURCE_LIMITS["captured_output_bytes"]:
                    violation = "combined stdout/stderr exceeded 1 MiB"
            usage = writable_usage(writable)
            if not usage["within_quota"]:
                violation = "cumulative writable byte/inode quota exceeded or became unreadable"
            if violation:
                proc.kill()
                proc.wait()
                break
        return {"returncode": proc.wait(), "stdout": bytes(captured["stdout"]), "stderr": bytes(captured["stderr"]), "captured_bytes": total_captured, "usage": usage, "violation": violation}
    finally:
        selector.close()
        proc.stdout.close()
        proc.stderr.close()


def execute_mode(args: argparse.Namespace, root: Path, fixture_path: Path) -> tuple[int, dict[str, Any]]:
    result = execution_result(args.mode, args.target_root, args.output_root)
    if not args.require_operation_permission:
        unverified(result, "exact Graphify operation permission is absent; no process started")
        return finish(result)
    if args.network_deny != "required":
        unverified(result, "enforceable network denial was not required; no process started")
        return finish(result)
    contract_code, contract = contract_mode(root, fixture_path, args)
    if contract_code != 0:
        for item in contract["errors"]:
            unsafe(result, item)
        for item in contract["unverified"]:
            unverified(result, item)
        return finish(result)
    security_code, security = security_evidence(args)
    if security_code != 0:
        for item in security["errors"]:
            unsafe(result, item)
        for item in security["unverified"]:
            unverified(result, item)
        block(result, "security-evidence did not exit 0; no Graphify process started")
        return finish(result)
    wheel_binding = bool(security.get("dependencies", {}).get("installed_closure", {}).get("trusted_wheel_binding", {}).get("complete"))
    executable, executable_report, executable_error = executable_preflight(args.version, wheel_binding)
    result["environment"]["executable"] = executable_report
    if executable_error:
        unverified(result, f"{executable_error}; no Graphify process started")
    bwrap, network_report = bwrap_preflight()
    result["network"] = network_report
    if not bwrap:
        unverified(result, "enforceable exact-process network denial unavailable; no Graphify process started")
    if executable is None or bwrap is None:
        return finish(result)
    runtime, runtime_error = construct_runtime_mounts(executable)
    if runtime_error or runtime is None:
        unverified(result, f"minimal explicit Graphify runtime unavailable: {runtime_error}; no Graphify process started")
        return finish(result)
    result["environment"]["runtime_mounts"] = {"readonly": [str(path) for path in runtime.readonly], "omitted_neighbor_roots": [str(path) for path in runtime.masked], "root_mounted": False}
    limiter = resource_limiter()
    if limiter is None:
        unverified(result, "CPU/memory/process/file/output resource enforcement unavailable; no Graphify process started")
        return finish(result)
    result["environment"]["resource_limits"] = dict(RESOURCE_LIMITS)
    result["environment"]["quota_supervisor"] = {"active": True, "stream_limit_bytes": RESOURCE_LIMITS["captured_output_bytes"], "writable_byte_limit": RESOURCE_LIMITS["writable_bytes"], "writable_inode_limit": RESOURCE_LIMITS["writable_inodes"], "fail_closed": True}
    temp_context = tempfile.TemporaryDirectory(prefix="rose-aili-graphify-")
    temp_root = Path(temp_context.name).resolve()
    result["temp_cleanup"]["created"].append(str(temp_root))
    class StopExecution(Exception):
        pass
    try:
        if args.mode == "execute-synthetic":
            synthetic_target = temp_root / "synthetic repo $(literal); '引号'\nline"
            synthetic_target.mkdir(mode=0o700)
            (synthetic_target / "sample.py").write_text("def answer():\n    return 42\n", encoding="utf-8")
            target_arg, output_arg = str(synthetic_target), str(temp_root / "private output -literal Δ")
            result["target_root"], result["output_root"] = target_arg, output_arg
        else:
            target_arg, output_arg = args.target_root, args.output_root
        assert target_arg is not None and output_arg is not None
        target, output = validate_target_output(target_arg, output_arg, result)
        if target is None or output is None or result["errors"]:
            raise StopExecution
        output_safety = git_output_safety(target, output, result)
        if args.mode == "execute-project" and output_safety.get("source_repository_root") != str(target):
            unverified(result, "execute-project target is not the exact approved Git repository root")
        if result["blocked"]:
            raise StopExecution
        old_umask = os.umask(0o077)
        try:
            output.mkdir(mode=0o700)
            isolation = temp_root / "isolation"
            home, config, cache, data, temp = (isolation / name for name in ("home", "config", "cache", "data", "tmp"))
            for path in (home, config, cache, data, temp):
                path.mkdir(parents=True, mode=0o700)
        finally:
            os.umask(old_umask)
        if stat.S_IMODE(output.stat().st_mode) != 0o700 or has_symlink_component(output):
            unsafe(result, "new output root is not private/non-symlink")
        env, env_report = sanitized_environment(home, config, cache, data, temp)
        env_report["output_safety"] = output_safety
        result["environment"].update(env_report)
        writable = [home, config, cache, data, temp]
        inventory_roots = [output, *writable]
        before = snapshot(inventory_roots)
        extract_argv = [str(executable), "-I", "-m", "graphify", "extract", str(target), "--code-only", "--no-cluster", "--out", str(output)]
        graph = output / "graphify-out" / "graph.json"
        cluster_argv = [str(executable), "-I", "-m", "graphify", "cluster-only", "--graph", str(graph), "--no-label", "--no-viz"]
        result["argv"] = [extract_argv, cluster_argv]
        returncodes: list[int] = []
        try:
            for graphify_argv in (extract_argv, cluster_argv):
                command = sandbox_command(bwrap, target, output, writable, graphify_argv, runtime)
                result["launch_attempted"] = True
                supervised = run_supervised(command, env, limiter, inventory_roots)
                result["write_inventory"]["active_quota"] = supervised["usage"]
                result["write_inventory"]["captured_output_bytes"] = supervised["captured_bytes"]
                if supervised["violation"]:
                    unsafe(result, f"Graphify supervisor stopped execution: {supervised['violation']}")
                    break
                graphify_started = supervised["returncode"] not in {126, 127} and not supervised["stderr"].lstrip().startswith(b"bwrap:")
                result["process_started"] = result["process_started"] or graphify_started
                returncodes.append(supervised["returncode"])
                if supervised["returncode"] != 0:
                    unsafe(result, f"Graphify exact command failed with exit {supervised['returncode']}")
                    break
        except subprocess.TimeoutExpired as exc:
            result["process_started"] = None
            unsafe(result, f"Graphify exact command timed out after launch; child start is unknown: {exc}")
        except (OSError, subprocess.SubprocessError) as exc:
            unsafe(result, f"Graphify exact command failed: {exc}")
        after = snapshot(inventory_roots)
        quota = writable_usage(inventory_roots)
        if not quota["within_quota"]:
            unsafe(result, "final cumulative writable byte/inode quota is exceeded or incomplete")
        result["write_inventory"].update({"roots": [str(path) for path in inventory_roots], "sandbox_denies_other_writes": True, "before": before, "after": after, "quota": quota, "complete": quota["within_quota"]})
        result["output_inventory"] = snapshot([output])
        if len(returncodes) == 2 and returncodes == [0, 0] and not graph.is_file():
            unsafe(result, "both commands exited 0 but expected graph output is absent")
    except StopExecution:
        pass
    finally:
        temp_context.cleanup()
        if temp_root.exists():
            result["temp_cleanup"]["complete"] = False
            unsafe(result, "temporary isolation root remains after cleanup")
        else:
            result["temp_cleanup"]["removed"].append(str(temp_root))
    return finish(result)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True)
    parser.add_argument("--fixture", required=True)
    parser.add_argument("--version", required=True)
    parser.add_argument("--commit", required=True)
    parser.add_argument("--profile", required=True)
    parser.add_argument("--mode", required=True, choices=("contract", "security-evidence", "execute-synthetic", "execute-project"))
    parser.add_argument("--target-root")
    parser.add_argument("--output-root")
    parser.add_argument("--require-operation-permission", action="store_true")
    parser.add_argument("--network-deny", choices=("required",))
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(args.project).resolve(strict=True)
    try:
        fixture_path = project_path(root, args.fixture)
    except ValueError as exc:
        result = base_contract_result(args.mode)
        unsafe(result, str(exc))
        code, result = finish(result)
        print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
        return code
    execution_args = any((args.target_root, args.output_root, args.require_operation_permission, args.network_deny))
    if args.mode in {"contract", "security-evidence"} and execution_args:
        result = base_contract_result(args.mode) if args.mode == "contract" else security_result()
        unsafe(result, "execution-only arguments supplied to non-execution mode")
        code, result = finish(result)
    elif args.mode == "execute-project" and (args.target_root is None or args.output_root is None):
        result = execution_result(args.mode, args.target_root, args.output_root)
        unverified(result, "execute-project requires exact --target-root and --output-root")
        code, result = finish(result)
    elif args.mode == "execute-synthetic" and (args.target_root is not None or args.output_root is not None):
        result = execution_result(args.mode, args.target_root, args.output_root)
        unsafe(result, "execute-synthetic creates its own target/output and rejects project paths")
        code, result = finish(result)
    elif args.mode == "contract":
        code, result = contract_mode(root, fixture_path, args)
    elif args.mode == "security-evidence":
        code, result = security_evidence(args)
    else:
        code, result = execute_mode(args, root, fixture_path)
    print(json.dumps(result, ensure_ascii=False, separators=(",", ":")) if args.json else json.dumps(result, ensure_ascii=False, indent=2))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
