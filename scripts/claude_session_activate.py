"""Optional live GitHub L0 sync, then read-only canonical context for Claude.

Configured sources are explicit allowlisted PR locators. No background scheduler,
no external writes and no state promotion. A failed read is labeled BLOCKED.
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

from claude_session_context import ROOT, compile_context


def activate(root: Path, db: Path, source_list: str) -> str:
    observations: list[str] = []
    raw = [part.strip() for part in source_list.split(";") if part.strip()]
    if not raw:
        observations.append("live_github_sync=NOT_CONFIGURED (prior local evidence may be stale)")
    elif len(raw) > 2:
        observations.append("live_github_sync=BLOCKED (maximum two PR sources at SessionStart)")
    else:
        # Package import works before editable install as well as after it.
        sys.path.insert(0, str(root / "src"))
        from reality_ontology.github_ingest import sync_github_pr
        for part in raw:
            match = re.fullmatch(r"([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)#([1-9][0-9]*)", part)
            if not match:
                observations.append(f"live_github_sync=BLOCKED (invalid target; no source claim)")
                continue
            repo, number = match.group(1), int(match.group(2))
            try:
                result = sync_github_pr(db, repo, number)
                observations.append(
                    f"live_github_sync={result['status']} source={result['source_url']} "
                    f"evidence={result['evidence_id']} ceiling=EXTERNAL_SOURCE_OBSERVED_ONLY"
                )
            except (OSError, RuntimeError, ValueError) as exc:
                observations.append(
                    f"live_github_sync=BLOCKED source={repo}#{number} "
                    f"reason={type(exc).__name__}; prohibit stale-state promotion"
                )
    return "\n".join(observations + [compile_context(root, db)])


def main() -> None:
    raw_db = Path(os.environ.get("RO_DB", ".runtime/reality.db"))
    db = raw_db if raw_db.is_absolute() else ROOT / raw_db
    output = activate(ROOT, db, os.environ.get("RO_GITHUB_PRS", ""))
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "SessionStart",
        "additionalContext": output[:4800],
    }}))


if __name__ == "__main__":
    main()
