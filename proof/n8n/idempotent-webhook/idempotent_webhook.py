from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Callable


SCHEMA = """
CREATE TABLE IF NOT EXISTS webhook_events (
    event_key TEXT PRIMARY KEY,
    state TEXT NOT NULL CHECK(state IN ('PROCESSING','COMPLETED','FAILED')),
    attempt_count INTEGER NOT NULL DEFAULT 1,
    receipt TEXT,
    last_error TEXT,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""


@dataclass(frozen=True)
class ClaimResult:
    event_key: str
    decision: str
    state: str
    attempt_count: int
    receipt: str | None = None


class IdempotentWebhookStore:
    """Tiny reference state machine for retry-safe webhook side effects.

    This is a proof artifact, not an n8n integration. It models the database
    contract an n8n workflow can implement with Postgres/SQLite.
    """

    def __init__(self, path: str | Path):
        self.path = str(path)
        self.db = sqlite3.connect(self.path, timeout=5, isolation_level=None)
        self.db.row_factory = sqlite3.Row
        self.db.executescript(SCHEMA)

    def close(self) -> None:
        self.db.close()

    def claim(self, event_key: str) -> ClaimResult:
        """Atomically decide whether this delivery may execute the side effect."""
        event_key = event_key.strip()
        if not event_key:
            raise ValueError("event_key is required")

        self.db.execute("BEGIN IMMEDIATE")
        try:
            row = self.db.execute(
                "SELECT event_key,state,attempt_count,receipt FROM webhook_events WHERE event_key=?",
                (event_key,),
            ).fetchone()

            if row is None:
                self.db.execute(
                    "INSERT INTO webhook_events(event_key,state,attempt_count) VALUES(?, 'PROCESSING', 1)",
                    (event_key,),
                )
                self.db.execute("COMMIT")
                return ClaimResult(event_key, "EXECUTE", "PROCESSING", 1)

            if row["state"] == "COMPLETED":
                self.db.execute("COMMIT")
                return ClaimResult(
                    event_key,
                    "RETURN_EXISTING_RECEIPT",
                    "COMPLETED",
                    int(row["attempt_count"]),
                    row["receipt"],
                )

            if row["state"] == "PROCESSING":
                self.db.execute("COMMIT")
                return ClaimResult(
                    event_key,
                    "SUPPRESS_DUPLICATE_IN_FLIGHT",
                    "PROCESSING",
                    int(row["attempt_count"]),
                    row["receipt"],
                )

            # FAILED is explicitly retryable. The same business event advances
            # the attempt counter but never creates a second event identity.
            next_attempt = int(row["attempt_count"]) + 1
            self.db.execute(
                """
                UPDATE webhook_events
                SET state='PROCESSING', attempt_count=?, last_error=NULL, updated_at=CURRENT_TIMESTAMP
                WHERE event_key=?
                """,
                (next_attempt, event_key),
            )
            self.db.execute("COMMIT")
            return ClaimResult(event_key, "RETRY", "PROCESSING", next_attempt)
        except Exception:
            self.db.execute("ROLLBACK")
            raise

    def complete(self, event_key: str, receipt: str) -> None:
        receipt = receipt.strip()
        if not receipt:
            raise ValueError("receipt is required")
        cur = self.db.execute(
            """
            UPDATE webhook_events
            SET state='COMPLETED', receipt=?, last_error=NULL, updated_at=CURRENT_TIMESTAMP
            WHERE event_key=? AND state='PROCESSING'
            """,
            (receipt, event_key),
        )
        if cur.rowcount != 1:
            raise ValueError("event must be PROCESSING before completion")

    def fail(self, event_key: str, error: str) -> None:
        cur = self.db.execute(
            """
            UPDATE webhook_events
            SET state='FAILED', last_error=?, updated_at=CURRENT_TIMESTAMP
            WHERE event_key=? AND state='PROCESSING'
            """,
            (error, event_key),
        )
        if cur.rowcount != 1:
            raise ValueError("event must be PROCESSING before failure")

    def get(self, event_key: str) -> dict | None:
        row = self.db.execute(
            "SELECT * FROM webhook_events WHERE event_key=?", (event_key,)
        ).fetchone()
        return dict(row) if row else None


def process_delivery(
    store: IdempotentWebhookStore,
    event_key: str,
    side_effect: Callable[[], str],
) -> ClaimResult:
    """Reference orchestration: claim → side effect → durable receipt."""
    claim = store.claim(event_key)
    if claim.decision not in {"EXECUTE", "RETRY"}:
        return claim

    try:
        receipt = side_effect()
    except Exception as exc:
        store.fail(event_key, str(exc))
        raise

    store.complete(event_key, receipt)
    row = store.get(event_key)
    return ClaimResult(
        event_key=event_key,
        decision="COMPLETED",
        state="COMPLETED",
        attempt_count=int(row["attempt_count"]),
        receipt=str(row["receipt"]),
    )
