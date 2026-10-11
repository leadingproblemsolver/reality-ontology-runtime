import json
import subprocess

import pytest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = json.loads((ROOT / "logistinfra-runtime/bootstrap/migration_manifest.v1.json").read_text(encoding="utf-8"))


def test_statuses_come_from_declared_vocabulary():
    allowed = set(MANIFEST["status_vocabulary"])
    assert {p["state"] for p in MANIFEST["pipelines"]} <= allowed


def test_verified_and_observed_entries_cite_evidence():
    for p in MANIFEST["pipelines"]:
        if p["state"] in {"VERIFIED", "OBSERVED"}:
            assert p.get("evidence"), p["id"]


def test_blocked_entries_name_blocker_and_exact_next_action():
    for p in MANIFEST["pipelines"]:
        if p["state"] == "BLOCKED":
            assert p.get("blocker") and p.get("next_action"), p["id"]


def test_every_implementation_path_exists():
    for p in MANIFEST["pipelines"]:
        for rel in p["implementation"]:
            if rel.startswith("0") and not rel.startswith("logistinfra"):
                rel = "logistinfra-runtime/immediatelyusable/" + rel
            if rel.endswith("/"):
                assert (ROOT / rel).is_dir(), (p["id"], rel)
            elif rel.startswith(("02_", "05_", "06_")):
                assert (ROOT / "logistinfra-runtime/immediatelyusable" / rel).is_file(), (p["id"], rel)
            else:
                assert (ROOT / rel).exists(), (p["id"], rel)


def test_cited_commits_exist_in_history():
    shallow = subprocess.run(["git", "rev-parse", "--is-shallow-repository"], cwd=ROOT, capture_output=True, text=True)
    if shallow.returncode != 0 or shallow.stdout.strip() != "false":
        pytest.skip("history not fully available (shallow clone)")
    shas = [MANIFEST["base_commit"]] + [p["origin"]["commit"] for p in MANIFEST["pipelines"] if "origin" in p]
    for sha in shas:
        result = subprocess.run(["git", "cat-file", "-e", sha + "^{commit}"], cwd=ROOT, capture_output=True)
        assert result.returncode == 0, sha


def test_excluded_sources_are_declared_and_seeds_are_stale():
    assert len(MANIFEST["provenance"]["excluded_sources"]) >= 3
    assert "stale" in MANIFEST["provenance"]["seed_policy"]
