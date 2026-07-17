import copy
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("delegation_protocols_check", ROOT / "scripts" / "delegation_protocols_check.py")
CHECKER = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(CHECKER)
FIXTURE = json.loads((ROOT / "docs/harness/fixtures/cross-worktree-permission-fixtures.yaml").read_text(encoding="utf-8"))["a33"]


def operation(kind="add", index=1):
    return {
        "operation_id": f"{kind}-{index}", "kind": kind, "operation_class": "driver_fixture",
        "source": f"/tmp/run/source-{index}", "destination": f"/tmp/run/host/.worktrees/foreign-{index}/existing",
        "repo_key": f"foreign-{index}", "worktree_key": "existing", "branch": "fixture-existing",
        "base_ref": "HEAD", "branch_mode": "existing", "reflog_policy": "enabled",
    }


def state_for(operations=None):
    return {"run_id": "run", "run_root": "/tmp/run", "host": "/tmp/run/host", "operations": operations or [operation()],
            "registered": [], "consumed_approvals": {}, "approval_snapshots": {}}


def approval_for(op, **overrides):
    value = {
        "approval_id": f"approval-{op['operation_id']}", "run_id": "run", "operation_id": op["operation_id"],
        "kind": op["kind"], "operation_class": op["operation_class"], "source": op["source"],
        "destination": op["destination"], "repo_key": op["repo_key"], "worktree_key": op["worktree_key"],
        "branch": op["branch"], "base_ref": op["base_ref"], "branch_mode": op["branch_mode"],
        "reflog_policy": op["reflog_policy"], "expiry": "2999-01-01T00:00:00Z", "decision_ref": "decision",
        "trusted_code_risk": "accepted" if op["kind"] == "add" else "not_applicable", "status": "valid",
    }
    value.update(overrides)
    return value


def populated(root="/tmp/run/host/.worktrees/foreign-1/existing", common="/tmp/run/source-1/.git"):
    return {
        "identity_state": "populated", "declared_root": root, "path_state": "present", "canonical_root": root,
        "git_toplevel": root, "git_private_dir": f"{common}/worktrees/existing", "git_common_dir": common,
        "git_head": "0" * 40, "git_branch": "fixture-existing", "detached_head": False, "worktree_membership": "linked",
        "dirty_state": {"tracked_modified": False, "tracked_deleted": False, "untracked_count": 0, "ignored_count": 0},
        "tracked_files": ["fixture.txt"], "untracked_files": [], "ignored_files": [], "artifact_files": [], "unknown_files": [],
    }


def absent(root="/tmp/run/host/.worktrees/foreign-1/existing"):
    return {name: ("absent" if name in {"identity_state", "path_state", "worktree_membership"} else root if name == "declared_root" else None)
            for name in CHECKER.A33_IDENTITY_FIELDS}


def raw_snapshot(identity, source, op, value=None):
    common = source["git_common_dir"]
    return {
        "target_path": identity["path_state"], "worktree_membership": identity["worktree_membership"],
        "common_dir_identity": common, "common_dir_admin_entry": None,
        "branch_ref": {"path": str(Path(common, "refs", "heads", op["branch"])), "value": value},
        "branch_reflog": {"path": str(Path(common, "logs", "refs", "heads", op["branch"])), "value": value},
        "unrelated_common_dir_entries": [], "unrelated_refs": [], "config": "config", "hooks": [],
        "unrelated_worktree_records": [], "unrelated_prunable_entries": [], "other_files": None,
    }


def raw_inventory(target, source, op):
    return {
        "schema_version": CHECKER.A33_INTERNAL_EVIDENCE_VERSION, "target_present": True,
        "status_porcelain_v2": [], "worktree_porcelain": [f"worktree {op['destination']}", "HEAD abc"],
        "tracked_files": ["fixture.txt"], "artifact_files": [], "unknown_files": [],
        "visible_files": [".git", "fixture.txt"], "allowlisted_ephemeral_artifacts": [".git"],
        "expected_source": source["git_common_dir"], "observed_source": target["git_common_dir"],
        "expected_path": op["destination"], "observed_path": target["declared_root"],
        "expected_membership": "linked", "observed_membership": target["worktree_membership"],
    }


class RegistryAndApprovalTests(unittest.TestCase):
    def test_exact_python_registry_order_metadata_and_mutations(self):
        ids = FIXTURE["runtime_mandatory_case_ids"]
        self.assertEqual(len(ids), 70)
        self.assertEqual(CHECKER.validate_a33_scenario_registry(ids), 0)
        mutations = []
        swapped = copy.deepcopy(CHECKER.A33_RUNTIME_SCENARIO_REGISTRY)
        swapped[0], swapped[1] = swapped[1], swapped[0]
        mutations.extend([swapped, swapped[1:], [*swapped, copy.deepcopy(swapped[0])]])
        duplicate = copy.deepcopy(CHECKER.A33_RUNTIME_SCENARIO_REGISTRY); duplicate[1]["id"] = duplicate[0]["id"]; mutations.append(duplicate)
        metadata = copy.deepcopy(CHECKER.A33_RUNTIME_SCENARIO_REGISTRY); metadata[0]["family"] = "valid-add"; mutations.append(metadata)
        for mutation in mutations:
            with self.subTest(mutation=len(mutation)):
                self.assertEqual(CHECKER.validate_a33_scenario_registry(ids, mutation), 5)

    def test_approval_precedence_snapshot_reuse_and_four_key_cells(self):
        add = operation("add")
        state = state_for([add])
        valid = approval_for(add)
        self.assertEqual(CHECKER.classify_a33_approval(approval_for(add, status="declined", source="/wrong"), state, add, set())[0], "wrong_source")
        stale = approval_for(add, approval_id="stale", status="stale")
        snapshot = CHECKER.build_a33_operation_snapshot(state, add, [], True)
        state["approval_snapshots"] = {"stale": {"approval_binding": CHECKER.a33_approval_binding(stale), "operation_snapshot": snapshot}}
        self.assertEqual(CHECKER.classify_a33_approval(stale, state, add, set(), [], False)[0], "stale_snapshot_mismatch")
        forged = copy.deepcopy(state); forged["approval_snapshots"].pop("stale")
        self.assertEqual(CHECKER.classify_a33_approval(stale, forged, add, set())[0], "schema_omission")
        cells = []
        for kind in ("add", "remove"):
            op = operation(kind)
            for field, expected in (("repo_key", "repo_key_mismatch"), ("worktree_key", "worktree_key_mismatch")):
                mutated = approval_for(op, **{field: "wrong"})
                cells.append((kind, CHECKER.classify_a33_approval(mutated, state_for([op]), op, set())[0]))
        self.assertEqual(sorted(cells), sorted([("add", "repo_key_mismatch"), ("add", "worktree_key_mismatch"), ("remove", "repo_key_mismatch"), ("remove", "worktree_key_mismatch")]))
        reused_state = state_for([add])
        consumed_snapshot = CHECKER.build_a33_operation_snapshot(reused_state, add, [], False)
        reused_state["consumed_approvals"] = {valid["approval_id"]: {
            "approval": copy.deepcopy(valid), "snapshot": copy.deepcopy(consumed_snapshot),
        }}
        remove = operation("remove"); remove.update({name: add[name] for name in ["source", "destination", "repo_key", "worktree_key", "branch", "base_ref", "branch_mode", "reflog_policy"]})
        self.assertEqual(CHECKER.classify_a33_approval(valid, reused_state, remove, {valid["approval_id"]})[:2], ("reused", "reused-add-for-remove"))
        reused_state["consumed_approvals"][valid["approval_id"]]["approval"]["decision_ref"] = "forged"
        self.assertEqual(CHECKER.classify_a33_approval(valid, reused_state, remove, {valid["approval_id"]})[0], "schema_omission")


class ReplayAndDeltaTests(unittest.TestCase):
    def successful_attempt(self, op):
        return {"operation_id": op["operation_id"], "result": {"status": "pass", "exit_code": 0, "operation": op}}

    def test_attempt_replay_rejects_order_duplicates_counters_and_registration(self):
        add, remove = operation("add"), operation("remove")
        remove.update({name: add[name] for name in ["source", "destination", "repo_key", "worktree_key", "branch", "base_ref", "branch_mode", "reflog_policy"]})
        good = [self.successful_attempt(add), self.successful_attempt(remove)]
        self.assertEqual(CHECKER.replay_a33_attempt_sequence(good, [add, remove]), (0, [], {"adds": 1, "removes": 1}))
        for attempts in ([good[1], good[0]], [good[0], good[0]], [good[0], good[1], good[1]]):
            self.assertEqual(CHECKER.replay_a33_attempt_sequence(attempts, [add, remove])[0], 5)
        exit_code, registered, counters = CHECKER.replay_a33_attempt_sequence([good[0]], [add, remove])
        self.assertEqual((exit_code, registered, counters), (0, [add["destination"]], {"adds": 1, "removes": 0}))
        self.assertNotEqual(registered, [])
        self.assertNotEqual(counters, {"adds": 0, "removes": 0})

    def test_raw_delta_derivation_and_non_null_modification(self):
        before = {name: None for name in CHECKER.A33_DELTA_FIELDS}
        after = copy.deepcopy(before); after["target_path"] = "present"
        before["branch_ref"] = {"path": "/ref", "value": None}; after["branch_ref"] = {"path": "/ref", "value": "abc"}
        before["branch_reflog"] = {"path": "/log", "value": "same"}; after["branch_reflog"] = {"path": "/log", "value": "same"}
        delta = CHECKER.derive_a33_delta(before, after)
        self.assertEqual(delta["target_path"]["change"], "created")
        self.assertEqual(delta["branch_ref"]["change"], "created")
        self.assertEqual(delta["branch_reflog"]["change"], "unchanged")
        deleted = copy.deepcopy(after); deleted["target_path"] = None; deleted["branch_ref"]["value"] = None
        self.assertEqual(CHECKER.derive_a33_delta(after, deleted)["target_path"]["change"], "deleted")
        modified = copy.deepcopy(after); modified["config"] = "changed"
        after["config"] = "original"
        self.assertIsNone(CHECKER.derive_a33_delta(after, modified))


class InventoryAndMalformedRowTests(unittest.TestCase):
    def setUp(self):
        self.op = operation("remove")
        self.source = populated("/tmp/run/source-1", "/tmp/run/source-1/.git")
        self.target = populated(self.op["destination"], self.source["git_common_dir"])
        self.attempt = {"target_before": self.target, "source_identity": self.source}
        self.raw = raw_inventory(self.target, self.source, self.op)

    def test_raw_inventory_mutations_fail_without_exception(self):
        good = CHECKER.derive_a33_removal_inventory(self.raw, self.attempt, self.op)
        self.assertTrue(good["clean"])
        mutations = [None, "scalar", [], {**self.raw, "tracked_files": "fixture.txt"}]
        duplicate = copy.deepcopy(self.raw); duplicate["artifact_files"] = ["fixture.txt"]; mutations.append(duplicate)
        for field, value in (("observed_source", "/wrong"), ("observed_path", "/wrong"), ("observed_membership", "main")):
            mutation = copy.deepcopy(self.raw); mutation[field] = value; mutations.append(mutation)
        for mutation in mutations:
            with self.subTest(mutation=repr(mutation)[:40]):
                try:
                    derived = CHECKER.derive_a33_removal_inventory(mutation, self.attempt, self.op)
                except Exception as exc:  # fail with useful assertion rather than traceback from the checker
                    self.fail(f"raw inventory raised {exc!r}")
                self.assertIsNone(derived)
        locked = copy.deepcopy(self.raw); locked["worktree_porcelain"].insert(1, "locked")
        forged_inventory = {"clean": True, "classes": [], "primary_class": "clean", "evidence_by_class": good["evidence_by_class"], "contradiction": False}
        locked_attempt = {**self.attempt, "raw_inventory_observation": locked}
        self.assertFalse(CHECKER.validate_a33_removal_inventory(forged_inventory, locked_attempt, self.op))

    def test_malformed_static_runtime_and_join_rows_fail_semantically_without_traceback(self):
        ids = ["one"]
        malformed = [None, "scalar", [], [None], [["nested"]], [{}]]
        for value in malformed:
            with self.subTest(value=value):
                self.assertEqual(CHECKER.validate_join_cases(value, ids), 5)
                self.assertEqual(CHECKER.validate_case_list(value, ids, "static"), 5)
        runtime = {name: None for name in FIXTURE["runtime_join_fields"]}
        for cases in (None, "scalar", [None], [[]], [{}]):
            candidate = copy.deepcopy(runtime); candidate["cases"] = cases
            try:
                self.assertEqual(CHECKER.validate_runtime_result(candidate, FIXTURE), 5)
            except Exception as exc:
                self.fail(f"runtime validator raised {exc!r}")


class CleanupAndSemanticOracleTests(unittest.TestCase):
    def cleanup_values(self):
        run_root = Path(tempfile.gettempdir()).resolve() / "aili-a33-runtime-Ab12Cd"
        state = {"schema_version": CHECKER.A33_SCHEMA, "run_id": run_root.name, "run_root": str(run_root), "cleanup_nonce": "a" * 64,
                 "operations": [operation("add", 1)], "collector_install_paths": []}
        state["operations"][0]["source"] = str(run_root / "source-1")
        marker = {"schema_version": CHECKER.A33_INTERNAL_EVIDENCE_VERSION, "run_root": str(run_root), "run_id": run_root.name, "cleanup_nonce": state["cleanup_nonce"]}
        identity = {"st_dev": 1, "st_ino": 2, "uid": os.getuid(), "mode": 0o700, "is_dir": True}
        entries = sorted(CHECKER._a33_expected_top_level(state))
        return run_root, state, marker, identity, entries

    def test_cleanup_ownership_and_live_residue_guards_never_delete(self):
        run_root, state, marker, identity, entries = self.cleanup_values()
        self.assertEqual(CHECKER.validate_a33_cleanup_security_record(state, run_root, marker, identity, entries, []), 0)
        variants = []
        bad = dict(marker); bad["cleanup_nonce"] = "b" * 64; variants.append((run_root, bad, identity, entries, []))
        bad = dict(marker); bad["schema_version"] = "bad"; variants.append((run_root, bad, identity, entries, []))
        variants.append((run_root.parent / "wrong-prefix", marker, identity, entries, []))
        unsafe = dict(identity); unsafe["mode"] = 0o770; variants.append((run_root, marker, unsafe, entries, []))
        variants.append((run_root, marker, identity, [*entries, "unexpected"], []))
        variants.append((run_root, marker, identity, entries, ["source-1"]))
        for values in variants:
            self.assertEqual(CHECKER.validate_a33_cleanup_security_record(state, *values), 5)
        changed_dev = dict(identity); changed_dev["st_dev"] += 1
        changed_ino = dict(identity); changed_ino["st_ino"] += 1
        self.assertFalse(CHECKER.same_a33_root_identity(identity, changed_dev))
        self.assertFalse(CHECKER.same_a33_root_identity(identity, changed_ino))
        destination = state["operations"][0]["destination"]
        self.assertEqual(CHECKER.validate_a33_live_cleanup_records([destination], {state["operations"][0]["source"]: [f"worktree {destination}"]}), 5)
        self.assertEqual(CHECKER.validate_a33_live_cleanup_records([destination], {state["operations"][0]["source"]: []}, [destination]), 5)

    def test_internal_semantic_mutation_kinds_reject(self):
        unchanged = {name: {"before": None, "after": None, "change": "unchanged"} for name in CHECKER.A33_DELTA_FIELDS}
        changed = copy.deepcopy(unchanged); changed["target_path"] = {"before": None, "after": "present", "change": "created"}
        for kind in ("delta", "ref", "reflog"):
            self.assertEqual(CHECKER.validate_a33_semantic_mutation({"kind": kind, "expected": unchanged, "observed": changed}), 5)
        for kind in ("effect", "inventory", "cleanup"):
            self.assertEqual(CHECKER.validate_a33_semantic_mutation({"kind": kind, "expected": False, "observed": True}), 5)
        identity = absent(); changed_identity = copy.deepcopy(identity); changed_identity["git_head"] = "mutated"
        self.assertEqual(CHECKER.validate_a33_semantic_mutation({"kind": "identity", "expected": identity, "observed": changed_identity}), 5)
        for malformed in (None, "scalar", [], {}, {"kind": "delta"}):
            self.assertEqual(CHECKER.validate_a33_semantic_mutation(malformed), 5)


if __name__ == "__main__":
    unittest.main()
