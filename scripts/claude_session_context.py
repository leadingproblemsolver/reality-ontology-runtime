"""Read-only Claude Code SessionStart context from the existing Reality Ontology DB.

This is a context projection, never an authority for settlements or writes.
Python stdlib only so it can run before project dependencies are installed.
"""
from __future__ import annotations

import json
import os
import sqlite3
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def compile_context(root: Path, db: Path) -> str:
    """Return a bounded factual context, without creating or modifying a DB."""
    lines = [
        "CLAUDE OPERATING CONTEXT (read-only; not a live source sync)",
        f"repository={root}",
        "canonical_authority=src/reality_ontology/store.py + ontology/",
        "rule=No model or tool output becomes a verified receipt without fresh independent evidence.",
    ]
    for label, rel in (
        ("operational_contract", "logistinfra-runtime/operational-reality/OPERATIONAL_REALITY_CONTRACT.md"),
        ("existing_surface_registry", "logistinfra-runtime/bootstrap/surfaces.v0.json"),
        ("existing_workstream_seed", "logistinfra-runtime/bootstrap/continuity.live.v0.json"),
        ("runtime_pipeline", "logistinfra-runtime/src/pipelines/github_opportunity/pipeline.ts"),
    ):
        lines.append(f"{label}={'PRESENT' if (root / rel).is_file() else 'MISSING'}:{rel}")

    if not db.is_file():
        lines.extend([
            "canonical_db=UNINITIALIZED (no live mission state available)",
            "first_action=Run local install and 'ro --db .runtime/reality.db init'; then ingest VERIFIED observations.",
        ])
        return "\n".join(lines)

    connection = None
    try:
        # SQLite URI mode=ro prevents accidental schema creation or mutation.
        connection = sqlite3.connect(db.resolve().as_uri() + "?mode=ro", uri=True, timeout=1.0)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA query_only = ON")
        tables = {row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        lines.append("canonical_db=PRESENT (local SQLite; NOT proof of live external sync)")
        lines.append(f"canonical_table_count={len(tables)}")
        if "next_missions" in tables:
            mission = connection.execute(
                "SELECT mission_id,target,status FROM next_missions "
                "ORDER BY CASE WHEN status='ACTIVE' THEN 0 ELSE 1 END, started_at DESC LIMIT 1"
            ).fetchone()
            if mission:
                lines.append(f"next_mission={mission['mission_id']} status={mission['status']} target={mission['target'][:160]}")
            else:
                lines.append("next_mission=NONE")
        else:
            lines.append("next_mission=UNINITIALIZED (next-start requires an evidence-backed mission spec)")
    except (sqlite3.DatabaseError, OSError) as exc:
        lines.append(f"canonical_db=UNREADABLE ({type(exc).__name__}); fail closed; do not settle")
    finally:
        if connection is not None:
            connection.close()
    lines.append("next_action=Inspect /operate and current verified DB state; do not infer external receipts from seed JSON.")
    return "\n".join(lines)


def main() -> None:
    raw = Path(os.environ.get("RO_DB", ".runtime/reality.db"))
    db = raw if raw.is_absolute() else ROOT / raw
    context = compile_context(ROOT, db)
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "SessionStart",
        "additionalContext": context[:4800],
    }}))


if __name__ == "__main__":
    main()
