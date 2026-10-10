"""Read-only and fail-closed Claude Code SessionStart activation."""
import importlib.util
import json
import sqlite3
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
module_path = ROOT / "scripts" / "claude_session_context.py"
spec = importlib.util.spec_from_file_location("claude_session_context", module_path)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_missing_db_does_not_create_db(tmp_path):
    db = tmp_path / "missing.sqlite"
    result = module.compile_context(tmp_path, db)
    assert "canonical_db=UNINITIALIZED" in result
    assert not db.exists()


def test_read_existing_active_mission(tmp_path):
    db = tmp_path / "state.sqlite"
    connection = sqlite3.connect(db)
    connection.execute("CREATE TABLE next_missions (mission_id TEXT, target TEXT, status TEXT, started_at TEXT)")
    connection.execute(
        "INSERT INTO next_missions VALUES (?, ?, ?, ?)",
        ("mission_verified", "real pilot", "ACTIVE", "2026-10-10T00:00:00Z"),
    )
    connection.commit()
    connection.close()
    result = module.compile_context(tmp_path, db)
    assert "next_mission=mission_verified status=ACTIVE target=real pilot" in result
    with sqlite3.connect(db) as check:
        assert check.execute("SELECT COUNT(*) FROM next_missions").fetchone()[0] == 1


def test_corrupt_db_fails_closed(tmp_path):
    db = tmp_path / "corrupt.sqlite"
    db.write_bytes(b"not SQLite")
    result = module.compile_context(tmp_path, db)
    assert "canonical_db=UNREADABLE" in result
    assert "do not settle" in result


def test_sessionstart_hook_points_at_read_only_script():
    settings = json.loads((ROOT / ".claude" / "settings.json").read_text(encoding="utf-8"))
    hook = settings["hooks"]["SessionStart"][0]["hooks"][0]
    assert hook["type"] == "command"
    assert hook["command"] == "python"
    assert hook["args"] == ["${CLAUDE_PROJECT_DIR}/scripts/claude_session_context.py"]
