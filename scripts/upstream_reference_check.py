#!/usr/bin/env python3
"""Fail-closed validation for pinned, inert upstream skill references."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import stat
import subprocess
import sys
import tarfile
import tempfile
import urllib.error
import urllib.request
from typing import Any

SCHEMA = "1.0"
KINDS = {"positive", "near-miss", "negative"}
OUTPUT_KEYS = ("schema_version", "status", "opencode_version", "repositories", "closures", "mappings", "licenses", "modes", "catalog_routes", "blocked", "unverified", "errors", "temp_cleanup")
BASE_ISOLATED_ENV_KEYS = frozenset({
    "PATH", "LANG", "HOME", "XDG_CONFIG_HOME", "XDG_DATA_HOME", "XDG_CACHE_HOME",
    "XDG_STATE_HOME", "XDG_RUNTIME_DIR", "TMPDIR", "TMP", "TEMP", "npm_config_cache",
    "npm_config_userconfig", "npm_config_globalconfig", "npm_config_audit", "npm_config_fund",
    "npm_config_update_notifier", "NO_UPDATE_NOTIFIER",
})
CATALOG_ENV_KEYS = BASE_ISOLATED_ENV_KEYS | frozenset({
    "OPENCODE_DISABLE_AUTOUPDATE", "OPENCODE_HOME", "OPENCODE_ALLOW_CUSTOM_HOME",
    "AILI_ALLOW_PACKAGE_HOME",
})


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected object")
    return value


def project_path(root: Path, relative: str) -> Path:
    pure = PurePosixPath(relative)
    if pure.is_absolute() or ".." in pure.parts or str(pure) != relative:
        raise ValueError(f"non-canonical path: {relative!r}")
    path = root.joinpath(*pure.parts)
    path.resolve(strict=False).relative_to(root)
    return path


def blob_sha(data: bytes) -> str:
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()


def output(version: str) -> dict[str, Any]:
    return {"schema_version": SCHEMA, "status": "exact", "opencode_version": version, "repositories": [], "closures": [], "mappings": [], "licenses": [], "modes": [], "catalog_routes": {"checked": False, "routes": []}, "blocked": [], "unverified": [], "errors": [], "temp_cleanup": {"created": [], "removed": [], "complete": True}}


def error(result: dict[str, Any], message: str) -> None:
    result["errors"].append(message)
    if message not in result["blocked"]:
        result["blocked"].append(message)


def unverified(result: dict[str, Any], message: str) -> None:
    result["unverified"].append(message)
    if message not in result["blocked"]:
        result["blocked"].append(message)


def isolated_environment(workspace: Path, opencode_home: Path | None = None) -> dict[str, str]:
    roots = {
        "HOME": workspace / "home",
        "XDG_CONFIG_HOME": workspace / "config",
        "XDG_DATA_HOME": workspace / "data",
        "XDG_CACHE_HOME": workspace / "cache",
        "XDG_STATE_HOME": workspace / "state",
        "XDG_RUNTIME_DIR": workspace / "runtime-dir",
        "TMPDIR": workspace / "tmp",
    }
    for path in roots.values():
        path.mkdir(parents=True, exist_ok=True)
    roots["XDG_RUNTIME_DIR"].chmod(0o700)
    npm_cache = workspace / "npm-cache"
    npm_cache.mkdir(parents=True, exist_ok=True)
    npm_userconfig = workspace / "npmrc"
    npm_globalconfig = workspace / "npm-globalrc"
    npm_userconfig.touch()
    npm_globalconfig.touch()
    environment = {
        "PATH": os.environ.get("PATH", os.defpath),
        "LANG": "C.UTF-8",
        **{key: str(value) for key, value in roots.items()},
        "TMP": str(roots["TMPDIR"]),
        "TEMP": str(roots["TMPDIR"]),
        "npm_config_cache": str(npm_cache),
        "npm_config_userconfig": str(npm_userconfig),
        "npm_config_globalconfig": str(npm_globalconfig),
        "npm_config_audit": "false",
        "npm_config_fund": "false",
        "npm_config_update_notifier": "false",
        "NO_UPDATE_NOTIFIER": "1",
    }
    if opencode_home is not None:
        opencode_home.mkdir(parents=True, exist_ok=True)
        environment.update({
            "OPENCODE_DISABLE_AUTOUPDATE": "true",
            "OPENCODE_HOME": str(opencode_home),
            "OPENCODE_ALLOW_CUSTOM_HOME": "yes",
            "AILI_ALLOW_PACKAGE_HOME": "yes",
        })
    expected_keys = CATALOG_ENV_KEYS if opencode_home is not None else BASE_ISOLATED_ENV_KEYS
    if set(environment) != expected_keys:
        raise ValueError("isolated environment differs from strict allowlist")
    return environment


def verify_fixture(data: dict[str, Any], closure_ids: set[str], result: dict[str, Any]) -> None:
    cases = data.get("cases")
    if data.get("schema_version") != SCHEMA or not isinstance(cases, list):
        error(result, "invalid fixture schema/cases")
        return
    if set(data.get("required_mappings", [])) != closure_ids:
        error(result, "fixture mappings differ from manifest closures")
    seen: set[str] = set()
    coverage = {item: set() for item in closure_ids}
    fields = {"id", "mapping", "kind", "input", "expected_skill", "artifact_target", "permission_profile", "stop_condition", "upstream_runnable"}
    for case in cases:
        if not isinstance(case, dict) or not fields.issubset(case):
            error(result, "fixture case missing required fields")
            continue
        if case["id"] in seen:
            error(result, f"duplicate fixture id: {case['id']}")
        seen.add(case["id"])
        if case["mapping"] not in coverage or case["kind"] not in KINDS:
            error(result, f"invalid fixture mapping/kind: {case['id']}")
        else:
            coverage[case["mapping"]].add(case["kind"])
        if case["upstream_runnable"] is not False:
            error(result, f"runnable fixture reference: {case['id']}")
    for mapping, kinds in coverage.items():
        if kinds != KINDS:
            error(result, f"missing positive/near-miss/negative cases: {mapping}")


def fetch(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "rose-aili-upstream-reference-check/1"})
    with urllib.request.urlopen(request, timeout=20) as response:
        return response.read()


def parse_catalog_output(text: str) -> list[dict[str, str]]:
    if not text or len(text.encode("utf-8")) > 1024 * 1024:
        raise ValueError("catalog output is empty or too large")
    try:
        value = json.loads(text)
    except (json.JSONDecodeError, RecursionError) as exc:
        raise ValueError(f"catalog is not one complete JSON document: {exc}") from exc
    if not isinstance(value, list) or len(value) > 10_000:
        raise ValueError("catalog must be a bounded list")
    routes: list[dict[str, str]] = []
    for index, item in enumerate(value):
        if not isinstance(item, dict):
            raise ValueError(f"catalog item {index} is not an object")
        name, location = item.get("name"), item.get("location")
        if not isinstance(name, str) or not name or not isinstance(location, str) or not location:
            raise ValueError(f"catalog item {index} has invalid name/location")
        if any(ord(char) < 32 for char in name + location):
            raise ValueError(f"catalog item {index} contains control characters")
        routes.append({"name": name, "location": location})
    return routes


def collect_catalog(command: list[str], cwd: Path, env: dict[str, str], skill_root: Path, workspace: Path, batch_size: int = 1) -> list[dict[str, str]]:
    def invoke() -> tuple[list[dict[str, str]] | None, bool]:
        proc = subprocess.run(command, cwd=cwd, env=env, text=True, capture_output=True, timeout=120, check=False)
        if proc.returncode != 0:
            raise ValueError(f"catalog command unavailable: {proc.stderr.strip()[-300:] or f'exited {proc.returncode}'}")
        try:
            return parse_catalog_output(proc.stdout), False
        except ValueError:
            if len(proc.stdout.encode("utf-8")) == 65536:
                return None, True
            raise

    catalog, truncated = invoke()
    if not truncated:
        assert catalog is not None
        return catalog

    directories = sorted((path for path in skill_root.iterdir() if path.is_dir()), key=lambda path: path.name)
    if not directories or batch_size < 1:
        raise ValueError("exact 65536-byte catalog output is incomplete and cannot be partitioned")
    hidden_root = workspace / "catalog-hidden"
    hidden_root.mkdir()
    restoration_errors: list[str] = []
    collected: list[dict[str, str]] = []
    try:
        for path in directories:
            shutil.move(str(path), str(hidden_root / path.name))
        for start in range(0, len(directories), batch_size):
            batch = directories[start:start + batch_size]
            try:
                for path in batch:
                    shutil.move(str(hidden_root / path.name), str(path))
                batch_catalog, batch_truncated = invoke()
                if batch_truncated:
                    raise ValueError(f"batch catalog output is incomplete at exact 65536 bytes: {[path.name for path in batch]}")
                assert batch_catalog is not None
                collected.extend(batch_catalog)
            finally:
                for path in batch:
                    if path.exists() and not (hidden_root / path.name).exists():
                        shutil.move(str(path), str(hidden_root / path.name))
    finally:
        for path in directories:
            hidden = hidden_root / path.name
            try:
                if path.exists() and hidden.exists():
                    raise ValueError("both installed and hidden copies exist")
                if hidden.exists():
                    shutil.move(str(hidden), str(path))
                elif not path.exists():
                    raise ValueError("directory is missing")
            except (OSError, ValueError) as exc:
                restoration_errors.append(f"{path.name}: {exc}")
        if restoration_errors:
            raise ValueError(f"catalog skill restoration failed: {restoration_errors}")

    by_name: dict[str, str] = {}
    deduplicated: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for route in collected:
        pair = (route["name"], route["location"])
        previous = by_name.setdefault(route["name"], route["location"])
        if previous != route["location"]:
            raise ValueError(f"duplicate catalog route conflict for {route['name']}: {previous!r} != {route['location']!r}")
        if pair not in seen:
            seen.add(pair)
            deduplicated.append(route)
    return deduplicated


def validate_catalog_routes(catalog: list[dict[str, str]], root: Path, closures: list[dict[str, Any]], skill_root: Path | None = None, forbidden_skill_root: Path | None = None) -> list[dict[str, str]]:
    normalized = [(item["name"], Path(item["location"]).resolve(strict=False)) for item in catalog]
    leaked = [str(location) for _, location in normalized if "references/upstream" in location.as_posix()]
    if leaked:
        raise ValueError(f"excluded references/upstream route discovered: {leaked}")
    canonical_root = skill_root if skill_root is not None else root / ".agents" / "skills"
    canonical_names = {str(closure.get("canonical_skill")) for closure in closures}
    upstream_names = {str(closure.get("id")) for closure in closures}
    if forbidden_skill_root is not None:
        forbidden = forbidden_skill_root.resolve(strict=False)
        forbidden_routes = [
            str(location) for name, location in normalized
            if location.is_relative_to(forbidden)
            and (name in canonical_names or name in upstream_names or "upstream" in location.as_posix())
        ]
        if forbidden_routes:
            raise ValueError(f"canonical/upstream route discovered under OPENCODE_HOME/skills: {forbidden_routes}")
    for closure in closures:
        canonical = closure.get("canonical_skill")
        expected = (canonical_root / str(canonical) / "SKILL.md").resolve(strict=False)
        matches = [location for name, location in normalized if name == canonical]
        if matches != [expected]:
            raise ValueError(f"canonical catalog route mismatch for {canonical}: {matches}")
    return catalog


def _npm_pack_listing(npm: str, root: Path, extra: list[str], environment_root: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    proc = subprocess.run(
        [npm, "pack", "--json", "--ignore-scripts", *extra], cwd=root, text=True,
        capture_output=True, timeout=90, check=False,
        env=isolated_environment(environment_root),
    )
    if proc.returncode != 0:
        raise ValueError(proc.stderr.strip()[-500:] or f"npm pack exited {proc.returncode}")
    payload = json.loads(proc.stdout)
    if not isinstance(payload, list) or len(payload) != 1 or not isinstance(payload[0], dict):
        raise ValueError("npm pack JSON has unexpected shape")
    files = payload[0].get("files")
    if not isinstance(files, list) or any(not isinstance(item, dict) or not isinstance(item.get("path"), str) for item in files):
        raise ValueError("npm pack file list has unexpected shape")
    return files, payload[0]


def filesystem_type(root: Path) -> str | None:
    try:
        proc = subprocess.run(
            ["stat", "-f", "-c", "%T", str(root)], text=True, capture_output=True,
            timeout=10, check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    return proc.stdout.strip().lower() if proc.returncode == 0 else None


def git_index_mode(root: Path, relative: str) -> str | None:
    try:
        proc = subprocess.run(
            ["git", "ls-files", "--stage", "--", relative], cwd=root, text=True,
            capture_output=True, timeout=10, check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if proc.returncode != 0 or not proc.stdout.strip():
        return None
    fields = proc.stdout.split(maxsplit=1)
    return fields[0] if fields and fields[0] in {"100644", "100755"} else None


def verify_package(root: Path, expected: set[str], expected_modes: dict[str, str], result: dict[str, Any], catalog_version: str | None = None, closures: list[dict[str, Any]] | None = None) -> None:
    npm = shutil.which("npm")
    if not npm:
        unverified(result, "npm unavailable; package contents unverified")
        return
    temp_name: str | None = None
    try:
        with tempfile.TemporaryDirectory(prefix="rose-aili-pack-") as temp:
            temp_name = temp
            result["temp_cleanup"]["created"].append(temp)
            packed = Path(temp) / "packed"
            packed.mkdir()
            tar_entries, pack_data = _npm_pack_listing(npm, root, ["--pack-destination", str(packed)], Path(temp) / "environment")
            tar_files = {item["path"] for item in tar_entries}
            missing = sorted(expected - tar_files)
            if missing:
                error(result, f"package omits upstream data: {missing}")
                return
            filename = pack_data.get("filename")
            if not isinstance(filename, str):
                raise ValueError("npm pack did not report a tar filename")
            archive = packed / filename
            with tarfile.open(archive, "r:gz") as tar:
                members = {member.name.removeprefix("package/"): member for member in tar.getmembers() if member.isfile()}
            if set(members) != tar_files:
                error(result, "actual npm tar entries differ from npm pack JSON")
                return
            fs_type = filesystem_type(root)
            drvfs_mode_emulation = fs_type in {"9p", "drvfs", "v9fs"}
            for relative, expected_mode in expected_modes.items():
                tar_mode = stat.S_IMODE(members[relative].mode)
                source_mode = stat.S_IMODE(project_path(root, relative).stat().st_mode)
                index_mode = git_index_mode(root, relative)
                expected_value = int(expected_mode, 8)
                if expected_value != 0o644 or expected_value & 0o111:
                    error(result, f"distribution mode policy must be 0644/non-executable: {relative} ({expected_mode})")
                    return
                local_tar_exact = tar_mode == expected_value and not tar_mode & 0o111
                git_archive_exact = drvfs_mode_emulation and index_mode == "100644"
                exact = local_tar_exact or git_archive_exact
                basis = "packed-tar" if local_tar_exact else "git-index-on-drvfs" if git_archive_exact else "mismatch"
                result["modes"].append({"path": relative, "source_mode": f"{source_mode:04o}", "tar_mode": f"{tar_mode:04o}", "git_mode": index_mode, "filesystem_type": fs_type, "expected": expected_mode, "verification_basis": basis, "local_tar_exact": local_tar_exact, "exact_non_executable": exact})
                if not exact:
                    error(result, f"distribution tar mode mismatch: {relative} (source={source_mode:04o}, tar={tar_mode:04o}, git={index_mode}, fs={fs_type}, expected={expected_mode})")
            if catalog_version is not None and closures is not None:
                verify_catalog(root, archive, catalog_version, closures, result, Path(temp) / "runtime")
    except (OSError, subprocess.TimeoutExpired, json.JSONDecodeError, KeyError, TypeError, ValueError, tarfile.TarError) as exc:
        unverified(result, f"npm package contents unavailable: {exc}")
    finally:
        if temp_name:
            if Path(temp_name).exists():
                result["temp_cleanup"]["complete"] = False
                error(result, f"temporary path remains: {temp_name}")
            else:
                result["temp_cleanup"]["removed"].append(temp_name)


def verify_catalog(root: Path, archive: Path, version: str, closures: list[dict[str, Any]], result: dict[str, Any], workspace: Path) -> None:
    npm = shutil.which("npm")
    if not npm:
        unverified(result, "UV-005: npm unavailable; installed catalog unverified")
        return
    try:
        prefix = workspace / "prefix"
        neutral = workspace / "neutral-project"
        opencode_home = workspace / "config" / "opencode"
        for path in (prefix, neutral, opencode_home):
            path.mkdir(parents=True, exist_ok=True)
        env = isolated_environment(workspace, opencode_home)
        installed = subprocess.run([npm, "install", "--prefix", str(prefix), "--ignore-scripts", "--no-audit", "--no-fund", str(archive.resolve())], cwd=neutral, env=env, text=True, capture_output=True, timeout=120, check=False)
        if installed.returncode != 0:
            unverified(result, f"UV-005: exact archive install unavailable: {installed.stderr.strip()[-300:]}")
            return
        cli = prefix / "node_modules" / ".bin" / "rose-aili"
        invoked = subprocess.run([str(cli), "install", "--opencode", "--opencode-home", str(opencode_home), "--yes", "--skip-opencode-config", "--skip-playwright", "--skip-codegraph", "--skip-openspec", "--json"], cwd=neutral, env=env, text=True, capture_output=True, timeout=120, check=False)
        if invoked.returncode != 0:
            error(result, f"installed publish candidate failed: {invoked.stderr.strip()[-300:]}")
            return
        shared_skill_root = Path(env["HOME"]) / ".agents" / "skills"
        canonical_names = {str(closure.get("canonical_skill")) for closure in closures}
        missing_canonical = sorted(
            name for name in canonical_names if not (shared_skill_root / name / "SKILL.md").is_file()
        )
        if missing_canonical:
            error(result, f"installed canonical skills missing from isolated HOME/.agents/skills: {missing_canonical}")
            return
        misplaced_canonical = sorted(
            name for name in canonical_names if (opencode_home / "skills" / name).exists()
        )
        if misplaced_canonical:
            error(result, f"canonical skills installed under OPENCODE_HOME/skills: {misplaced_canonical}")
            return
        command = [npm, "exec", "--yes", f"--package=opencode-ai@{version}", "--", "opencode"]
        found = subprocess.run(command + ["--version"], cwd=neutral, env=env, text=True, capture_output=True, timeout=120, check=False)
        if found.returncode != 0 or found.stdout.strip() != version:
            unverified(result, f"UV-005: OpenCode {version} unavailable: {found.stderr.strip()[-300:]}")
            return
        try:
            catalog = collect_catalog(
                command + ["--pure", "debug", "skill"], neutral, env,
                shared_skill_root, workspace,
            )
        except ValueError as exc:
            unverified(result, f"UV-005: installed catalog output unavailable: {exc}")
            return
        try:
            routes = validate_catalog_routes(catalog, root, closures, shared_skill_root, opencode_home / "skills")
        except ValueError as exc:
            error(result, f"installed catalog mismatch: {exc}")
            return
        result["catalog_routes"] = {"checked": True, "routes": routes}
    except (OSError, subprocess.TimeoutExpired) as exc:
        unverified(result, f"UV-005: temporary catalog unavailable: {exc}")


def check(args: argparse.Namespace) -> tuple[int, dict[str, Any]]:
    root = Path(args.project).resolve()
    result = output(args.opencode_version)
    try:
        manifest = load(project_path(root, args.manifest))
        fixture = load(project_path(root, args.fixture))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        error(result, str(exc))
        return 5, result
    if manifest.get("schema_version") != SCHEMA or "Provenance data only" not in str(manifest.get("authority")):
        error(result, "invalid manifest schema/non-authority declaration")
    repos, closures = manifest.get("repositories"), manifest.get("closures")
    if not isinstance(repos, list) or not isinstance(closures, list):
        error(result, "manifest repositories/closures must be lists")
        return 5, result
    repo_map = {repo.get("id"): repo for repo in repos if isinstance(repo, dict)}
    if len(repo_map) != len(repos):
        error(result, "repository IDs are missing/duplicate")
    closure_ids = {item.get("id") for item in closures if isinstance(item, dict)}
    verify_fixture(fixture, closure_ids, result)
    referenced_assets = {manifest.get("checker"), manifest.get("fixture"), manifest.get("component_manifest"), manifest.get("package_manifest")}
    if None in referenced_assets or manifest.get("fixture") != args.fixture:
        error(result, "manifest validation asset references are missing or differ from requested fixture")
    package_files = {args.manifest, *(str(item) for item in referenced_assets if isinstance(item, str))}
    expected_modes: dict[str, str] = {}
    local_paths: set[str] = set()
    for closure in closures:
        cid = closure.get("id", "<missing>")
        repo = repo_map.get(closure.get("repository_id"))
        if repo is None:
            error(result, f"{cid}: unknown repository")
            continue
        if closure.get("catalog_excluded") is not True:
            error(result, f"{cid}: catalog exclusion not asserted")
        try:
            vendor = project_path(root, closure["vendor_root"])
            license_path = project_path(root, closure["license_local_path"])
            notice_path = project_path(root, closure["notice_local_path"])
        except (KeyError, ValueError) as exc:
            error(result, f"{cid}: {exc}")
            continue
        package_files.update((closure["license_local_path"], closure["notice_local_path"]))
        expected_modes[closure["license_local_path"]] = "0644"
        expected_modes[closure["notice_local_path"]] = "0644"
        expected = {str(license_path.relative_to(vendor)).replace(os.sep, "/"), str(notice_path.relative_to(vendor)).replace(os.sep, "/")}
        if not license_path.is_file() or not notice_path.is_file():
            error(result, f"{cid}: missing LICENSE/NOTICE")
        if license_path.is_file():
            data = license_path.read_bytes()
            exact = hashlib.sha256(data).hexdigest() == repo.get("license_sha256") and blob_sha(data) == repo.get("license_git_blob_sha1") and repo.get("copyright") in data.decode(errors="replace")
            result["licenses"].append({"closure": cid, "path": closure["license_local_path"], "exact": exact})
            if not exact:
                error(result, f"{cid}: license mismatch")
        if notice_path.is_file():
            notice = notice_path.read_text(encoding="utf-8")
            for marker in (repo.get("repository"), repo.get("commit"), repo.get("copyright"), "inert"):
                if marker not in notice:
                    error(result, f"{cid}: NOTICE missing {marker!r}")
        for mapping in closure.get("mappings", []):
            source, local = mapping.get("source_path"), mapping.get("local_path")
            try:
                path = project_path(root, local)
            except (TypeError, ValueError) as exc:
                error(result, f"{cid}: {exc}")
                continue
            if local in local_paths:
                error(result, f"duplicate local mapping: {local}")
            local_paths.add(local)
            package_files.add(local)
            expected_modes[local] = str(mapping.get("mode"))
            expected.add(str(path.relative_to(vendor)).replace(os.sep, "/"))
            if source.endswith("SKILL.md") and path.name != "SKILL.upstream.md":
                error(result, f"{cid}: SKILL.md not inertly renamed")
            if not path.is_file():
                error(result, f"{cid}: missing {local}")
                continue
            data = path.read_bytes()
            sha256, blob = hashlib.sha256(data).hexdigest(), blob_sha(data)
            exact = sha256 == mapping.get("sha256") and blob == mapping.get("git_blob_sha1")
            result["mappings"].append({"closure": cid, "source": source, "local": local, "sha256": sha256, "git_blob_sha1": blob, "exact": exact})
            if not exact:
                error(result, f"{cid}: local hash mismatch: {local}")
            try:
                remote = fetch(repo["raw_base"] + source)
            except (urllib.error.URLError, TimeoutError, OSError) as exc:
                unverified(result, f"source unavailable {cid}:{source}: {exc}")
            else:
                if remote != data:
                    error(result, f"{cid}: pinned source/local bytes differ: {source}")
        if vendor.is_dir():
            actual = {str(path.relative_to(vendor)).replace(os.sep, "/") for path in vendor.rglob("*") if path.is_file()}
            extra, missing = sorted(actual - expected), sorted(expected - actual)
            result["closures"].append({"id": cid, "exact": not extra and not missing, "extra": extra, "missing": missing})
            if extra or missing:
                error(result, f"{cid}: closure mismatch extra={extra} missing={missing}")
    result["repositories"] = [{key: repo.get(key) for key in ("id", "repository", "commit", "license")} for repo in repos]
    for upstream in root.glob(".agents/skills/*/references/upstream"):
        for nested in upstream.rglob("SKILL.md"):
            error(result, f"nested runnable SKILL.md: {nested.relative_to(root)}")
    try:
        component_data = load(project_path(root, manifest["component_manifest"]))
        component = json.dumps(component_data, sort_keys=True)
        if "references/upstream" in component or "SKILL.upstream.md" in component:
            error(result, "component manifest registers upstream data")
        components = component_data.get("components", {})
        skills = components.get("skills", [])
        commands = components.get("commands", [])
        skill_names = [item.get("name") for item in skills if isinstance(item, dict)]
        command_names = [item.get("name") for item in commands if isinstance(item, dict)]
        for closure in closures:
            canonical = closure.get("canonical_skill")
            if skill_names.count(canonical) != 1:
                error(result, f"canonical skill must be registered exactly once: {canonical}")
            if closure.get("id") in skill_names:
                error(result, f"upstream closure registered as skill: {closure.get('id')}")
        if len(command_names) != len(set(command_names)):
            error(result, "duplicate public command registration")
        forbidden_commands = fixture.get("forbidden", {}).get("duplicate_public_commands", [])
        discovered_forbidden = sorted(name for name in forbidden_commands if name.lstrip("/") in command_names)
        if discovered_forbidden:
            error(result, f"upstream public commands registered: {discovered_forbidden}")
    except (OSError, KeyError, ValueError, json.JSONDecodeError) as exc:
        error(result, f"component manifest check failed: {exc}")
    verify_package(
        root,
        package_files,
        expected_modes,
        result,
        args.opencode_version if args.verify_installed_catalog else None,
        closures if args.verify_installed_catalog else None,
    )
    if not args.verify_installed_catalog:
        unverified(result, "UV-005: installed catalog check not requested")
    if result["errors"]:
        result["status"] = "mismatch-or-runnable"
        return 5, result
    if result["unverified"]:
        result["status"] = "unverified"
        return 3, result
    return 0, result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", default=".")
    parser.add_argument("--manifest", default="manifests/upstream-references.json")
    parser.add_argument("--fixture", default="docs/harness/fixtures/upstream-reference-fixtures.yaml")
    parser.add_argument("--opencode-version", default="1.17.18")
    parser.add_argument("--verify-installed-catalog", action="store_true")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()
    code, result = check(args)
    if args.as_json:
        print(json.dumps({key: result[key] for key in OUTPUT_KEYS}, ensure_ascii=False, indent=2))
    else:
        print(f"upstream references: {result['status']}")
        for message in result["errors"] + result["unverified"]:
            print(f"- {message}", file=sys.stderr)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
