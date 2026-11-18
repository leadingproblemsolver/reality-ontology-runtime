import importlib.util
from pathlib import Path
import pytest

spec = importlib.util.spec_from_file_location("gate", Path(__file__).parents[1] / "tools" / "prototype_gate.py")
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)

def test_empty_is_not_verified(tmp_path):
    result = gate.audit(tmp_path)
    assert len(result["findings"]) == 10
    assert all(r["state"] == "NOT_DETECTED" for r in result["findings"])

def test_file_clues_never_equal_working(tmp_path):
    (tmp_path / "index.html").write_text("BROKEN")
    (tmp_path / "server.py").write_text("BROKEN")
    states = {r["area"]:r["state"] for r in gate.audit(tmp_path)["findings"]}
    assert states["frontend"] == "CANDIDATE_UNVERIFIED"
    assert states["backend"] == "CANDIDATE_UNVERIFIED"
    assert "STATIC CLUES ONLY" in gate.audit(tmp_path)["claim_boundary"]

def test_dependency_and_symlink_excluded(tmp_path):
    d = tmp_path / "node_modules"
    d.mkdir()
    (d/"server.py").write_text("x")
    (tmp_path/"server.py").symlink_to(d/"server.py")
    assert gate.audit(tmp_path)["files_scanned"] == 0

def test_bad_path_rejected(tmp_path):
    with pytest.raises(ValueError):
        gate.audit(tmp_path/"absent")
