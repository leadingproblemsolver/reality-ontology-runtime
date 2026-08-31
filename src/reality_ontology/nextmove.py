from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Iterable
from uuid import uuid4


NEXTMOVE_SCHEMA = """
CREATE TABLE IF NOT EXISTS next_missions (
  mission_id TEXT PRIMARY KEY,
  target TEXT NOT NULL,
  observed_state TEXT NOT NULL,
  delta TEXT NOT NULL,
  status TEXT NOT NULL,
  selected_candidate_id TEXT NOT NULL,
  timebox_seconds INTEGER NOT NULL,
  base_urgency INTEGER NOT NULL,
  started_at TEXT NOT NULL,
  settled_at TEXT,
  owner TEXT,
  core_goal_id TEXT,
  core_object_id TEXT
);
CREATE TABLE IF NOT EXISTS next_candidates (
  candidate_id TEXT PRIMARY KEY,
  mission_id TEXT NOT NULL,
  action TEXT NOT NULL,
  expected_postcondition TEXT NOT NULL,
  expected_receipt TEXT NOT NULL,
  external_consequence INTEGER NOT NULL,
  information_gain INTEGER NOT NULL,
  technical_ownership INTEGER NOT NULL,
  warm_access INTEGER NOT NULL,
  compounding_leverage INTEGER NOT NULL,
  internal_preparation INTEGER NOT NULL,
  prerequisites_met INTEGER NOT NULL,
  authority_available INTEGER NOT NULL,
  observable_receipt INTEGER NOT NULL,
  rank_json TEXT NOT NULL,
  selected INTEGER NOT NULL DEFAULT 0,
  eligible INTEGER NOT NULL DEFAULT 0,
  FOREIGN KEY(mission_id) REFERENCES next_missions(mission_id)
);
CREATE INDEX IF NOT EXISTS idx_next_candidates_mission ON next_candidates(mission_id);
CREATE TABLE IF NOT EXISTS next_events (
  event_id TEXT PRIMARY KEY,
  mission_id TEXT NOT NULL,
  event_type TEXT NOT NULL,
  payload_json TEXT NOT NULL,
  created_at TEXT NOT NULL,
  FOREIGN KEY(mission_id) REFERENCES next_missions(mission_id)
);
CREATE INDEX IF NOT EXISTS idx_next_events_mission_time ON next_events(mission_id, created_at);
"""


class SettlementOutcome(str, Enum):
    RECEIPT = "RECEIPT"
    CAPABILITY_GAIN = "CAPABILITY_GAIN"
    FALSIFIED_HYPOTHESIS = "FALSIFIED_HYPOTHESIS"
    EXPLICIT_KILL = "EXPLICIT_KILL"
    BLOCKED = "BLOCKED"


@dataclass(frozen=True)
class Candidate:
    action: str
    expected_postcondition: str
    expected_receipt: str
    external_consequence: int = 0
    information_gain: int = 0
    technical_ownership: int = 0
    warm_access: int = 0
    compounding_leverage: int = 0
    internal_preparation: int = 0
    prerequisites_met: bool = True
    authority_available: bool = True
    observable_receipt: bool = True

    @classmethod
    def from_mapping(cls, raw: dict[str, Any]) -> "Candidate":
        required = ("action", "expected_postcondition", "expected_receipt")
        missing = [key for key in required if not str(raw.get(key, "")).strip()]
        if missing:
            raise ValueError(f"candidate missing required fields: {missing}")

        factors: dict[str, int] = {}
        for key in (
            "external_consequence",
            "information_gain",
            "technical_ownership",
            "warm_access",
            "compounding_leverage",
            "internal_preparation",
        ):
            value = int(raw.get(key, 0))
            if value < 0 or value > 5:
                raise ValueError(f"{key} must be between 0 and 5")
            factors[key] = value

        return cls(
            action=str(raw["action"]).strip(),
            expected_postcondition=str(raw["expected_postcondition"]).strip(),
            expected_receipt=str(raw["expected_receipt"]).strip(),
            prerequisites_met=bool(raw.get("prerequisites_met", True)),
            authority_available=bool(raw.get("authority_available", True)),
            observable_receipt=bool(raw.get("observable_receipt", True)),
            **factors,
        )

    @property
    def eligible(self) -> bool:
        return self.prerequisites_met and self.authority_available and self.observable_receipt

    @property
    def rank(self) -> tuple[int, int, int, int, int, int]:
        # Intentional lexicographic order: earlier dimensions dominate later ones.
        # This mirrors the execution kernel priority instead of hiding it in weights.
        return (
            self.external_consequence,
            self.information_gain,
            self.technical_ownership,
            self.warm_access,
            self.compounding_leverage,
            -self.internal_preparation,
        )


class NextMoveEngine:
    def __init__(self, store: Any, *, clock: Callable[[], datetime] | None = None):
        self.store = store
        self.db = store.db
        self.clock = clock or (lambda: datetime.now(timezone.utc))
        self.db.executescript(NEXTMOVE_SCHEMA)
        self.db.commit()

    def _now(self) -> datetime:
        now = self.clock()
        return now if now.tzinfo else now.replace(tzinfo=timezone.utc)

    def _iso_now(self) -> str:
        return self._now().isoformat()

    @staticmethod
    def _new_id(prefix: str) -> str:
        return f"{prefix}_{uuid4().hex[:16]}"

    def _append_event(self, mission_id: str, event_type: str, payload: dict[str, Any]) -> str:
        event_id = self._new_id("nextevt")
        self.db.execute(
            "INSERT INTO next_events VALUES (?,?,?,?,?)",
            (event_id, mission_id, event_type, json.dumps(payload, sort_keys=True), self._iso_now()),
        )
        self.db.commit()
        return event_id

    def _bridge_core_start(self, *, mission_id: str, target: str, observed_state: str, owner: str | None) -> tuple[str | None, str | None]:
        """Best-effort bridge into the canonical RealityStore without making NextMove depend on internals."""
        needed = ("add_actor", "add_goal", "add_object", "add_evidence", "record_event")
        if not all(hasattr(self.store, name) for name in needed):
            return None, None
        try:
            actor_id = self.store.add_actor(owner or "nextmove_operator")
            goal_id = self.store.add_goal(target, "NextMove settlement evidence")
            object_id = self.store.add_object(f"nextmove:{mission_id}", "execution_mission")
            evidence_id = self.store.add_evidence(
                "observation",
                f"nextmove://{mission_id}/start",
                observed_state,
                metadata={"mission_id": mission_id},
            )
            self.store.record_event(
                actor_id=actor_id,
                object_id=object_id,
                goal_id=goal_id,
                event_type="nextmove_started",
                resulting_state="ACTIVE",
                evidence_ids=[evidence_id],
                source="nextmove",
                metadata={"mission_id": mission_id},
            )
            return goal_id, object_id
        except Exception:
            # The overlay must not corrupt/override the canonical runtime if a bridge assumption fails.
            return None, None

    def start_mission(
        self,
        *,
        target: str,
        observed_state: str,
        delta: str,
        candidates: Iterable[dict[str, Any] | Candidate],
        timebox_seconds: int = 900,
        base_urgency: int = 50,
        owner: str | None = None,
    ) -> dict[str, Any]:
        active = self.db.execute("SELECT mission_id FROM next_missions WHERE status='ACTIVE' LIMIT 1").fetchone()
        if active:
            raise ValueError(f"active mission exists: {active[0]}; settle or kill it before starting another")

        target = target.strip()
        observed_state = observed_state.strip()
        delta = delta.strip()
        if not all((target, observed_state, delta)):
            raise ValueError("target, observed_state, and delta are required")
        if timebox_seconds < 60 or timebox_seconds > 86400:
            raise ValueError("timebox_seconds must be between 60 and 86400")
        if base_urgency < 0 or base_urgency > 100:
            raise ValueError("base_urgency must be between 0 and 100")

        parsed = [c if isinstance(c, Candidate) else Candidate.from_mapping(c) for c in candidates]
        if not parsed:
            raise ValueError("at least one candidate is required")
        if len(parsed) > 25:
            raise ValueError("at most 25 candidates are supported in v1")
        eligible = [(idx, c) for idx, c in enumerate(parsed) if c.eligible]
        if not eligible:
            raise ValueError("no executable candidate: prerequisites, authority, and observable receipt are required")

        # Stable tie-break: preserve caller order only after the strict kernel rank ties.
        selected_idx, selected = max(eligible, key=lambda pair: (pair[1].rank, -pair[0]))
        mission_id = self._new_id("mission")
        candidate_ids = [self._new_id("candidate") for _ in parsed]
        selected_candidate_id = candidate_ids[selected_idx]
        core_goal_id, core_object_id = self._bridge_core_start(
            mission_id=mission_id, target=target, observed_state=observed_state, owner=owner
        )

        self.db.execute(
            "INSERT INTO next_missions VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (
                mission_id,
                target,
                observed_state,
                delta,
                "ACTIVE",
                selected_candidate_id,
                timebox_seconds,
                base_urgency,
                self._iso_now(),
                None,
                owner,
                core_goal_id,
                core_object_id,
            ),
        )
        for idx, candidate in enumerate(parsed):
            self.db.execute(
                "INSERT INTO next_candidates VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (
                    candidate_ids[idx],
                    mission_id,
                    candidate.action,
                    candidate.expected_postcondition,
                    candidate.expected_receipt,
                    candidate.external_consequence,
                    candidate.information_gain,
                    candidate.technical_ownership,
                    candidate.warm_access,
                    candidate.compounding_leverage,
                    candidate.internal_preparation,
                    int(candidate.prerequisites_met),
                    int(candidate.authority_available),
                    int(candidate.observable_receipt),
                    json.dumps(candidate.rank),
                    int(idx == selected_idx),
                    int(candidate.eligible),
                ),
            )
        self.db.commit()

        self._append_event(
            mission_id,
            "MISSION_STARTED",
            {
                "target": target,
                "observed_state": observed_state,
                "delta": delta,
                "timebox_seconds": timebox_seconds,
                "candidate_count": len(parsed),
                "eligible_count": len(eligible),
            },
        )
        self._append_event(
            mission_id,
            "CANDIDATE_SELECTED",
            {
                "candidate_id": selected_candidate_id,
                "action": selected.action,
                "rank": selected.rank,
                "expected_receipt": selected.expected_receipt,
            },
        )
        return self.current(mission_id)

    def _mission_row(self, mission_id: str | None = None):
        if mission_id:
            row = self.db.execute("SELECT * FROM next_missions WHERE mission_id=?", (mission_id,)).fetchone()
        else:
            row = self.db.execute(
                "SELECT * FROM next_missions ORDER BY CASE status WHEN 'ACTIVE' THEN 0 ELSE 1 END, started_at DESC LIMIT 1"
            ).fetchone()
        if not row:
            raise KeyError(mission_id or "no mission")
        return row

    def current(self, mission_id: str | None = None) -> dict[str, Any]:
        row = self._mission_row(mission_id)
        candidate = self.db.execute(
            "SELECT * FROM next_candidates WHERE candidate_id=?", (row["selected_candidate_id"],)
        ).fetchone()
        started = datetime.fromisoformat(row["started_at"])
        elapsed = max(0, int((self._now() - started).total_seconds()))
        remaining = max(0, int(row["timebox_seconds"]) - elapsed)
        ratio = min(1.0, elapsed / max(1, int(row["timebox_seconds"])))
        urgency = min(100, int(row["base_urgency"]) + round((100 - int(row["base_urgency"])) * ratio))
        display_status = row["status"]
        if display_status == "ACTIVE" and remaining == 0:
            display_status = "EXPIRED_NEEDS_SETTLEMENT"

        if row["status"] != "ACTIVE":
            nudge = "Mission settled. Select the next dependency-correct transition."
        elif remaining == 0:
            nudge = "SETTLE REQUIRED — do not continue invisibly. Capture receipt, falsification, block, or kill."
        elif ratio >= 0.75:
            nudge = "Receipt window closing — finish the selected transition or settle it explicitly."
        else:
            nudge = "Execute exactly this transition. Do not open a lower-value preparation loop."

        return {
            "mission_id": row["mission_id"],
            "target": row["target"],
            "now": row["observed_state"],
            "delta": row["delta"],
            "status": display_status,
            "next_move": candidate["action"],
            "expected_postcondition": candidate["expected_postcondition"],
            "expected_receipt": candidate["expected_receipt"],
            "rank": json.loads(candidate["rank_json"]),
            "timer": {
                "timebox_seconds": int(row["timebox_seconds"]),
                "elapsed_seconds": elapsed,
                "remaining_seconds": remaining,
            },
            "urgency": urgency,
            "nudge": nudge,
            "owner": row["owner"],
            "core_goal_id": row["core_goal_id"],
            "core_object_id": row["core_object_id"],
        }

    def settle(
        self,
        mission_id: str,
        *,
        outcome: SettlementOutcome | str,
        observation: str,
        receipt_locator: str | None = None,
        next_action: str | None = None,
    ) -> dict[str, Any]:
        row = self._mission_row(mission_id)
        if row["status"] != "ACTIVE":
            raise ValueError("mission is already settled")
        outcome = outcome if isinstance(outcome, SettlementOutcome) else SettlementOutcome(outcome)
        observation = observation.strip()
        receipt_locator = receipt_locator.strip() if receipt_locator else None
        next_action = next_action.strip() if next_action else None
        if not observation:
            raise ValueError("observation is required")
        if outcome in {SettlementOutcome.RECEIPT, SettlementOutcome.CAPABILITY_GAIN, SettlementOutcome.FALSIFIED_HYPOTHESIS} and not receipt_locator:
            raise ValueError(f"{outcome.value} requires an inspectable receipt_locator")

        evidence_ids: list[str] = []
        if receipt_locator and hasattr(self.store, "add_evidence"):
            evidence_type = {
                SettlementOutcome.RECEIPT: "external_receipt",
                SettlementOutcome.CAPABILITY_GAIN: "test_result",
                SettlementOutcome.FALSIFIED_HYPOTHESIS: "contradiction_evidence",
            }.get(outcome, "observation")
            try:
                evidence_ids.append(
                    self.store.add_evidence(
                        evidence_type,
                        receipt_locator,
                        observation,
                        metadata={"mission_id": mission_id, "settlement_outcome": outcome.value},
                    )
                )
            except Exception:
                evidence_ids = []

        self.db.execute(
            "UPDATE next_missions SET status='SETTLED', settled_at=? WHERE mission_id=?",
            (self._iso_now(), mission_id),
        )
        self.db.commit()
        self._append_event(
            mission_id,
            "MISSION_SETTLED",
            {
                "outcome": outcome.value,
                "observation": observation,
                "receipt_locator": receipt_locator,
                "next_action": next_action,
                "evidence_ids": evidence_ids,
            },
        )

        # Preserve the runtime's settlement contract when available.
        if hasattr(self.store, "settle"):
            try:
                self.store.settle(
                    run_id=mission_id,
                    prior_state="ACTIVE",
                    action_taken=self.current(mission_id)["next_move"],
                    observed_result=observation,
                    evidence_ids=evidence_ids,
                    new_state=f"SETTLED_{outcome.value}",
                    next_transition=next_action,
                    next_action=next_action,
                    owner=row["owner"],
                    unresolved=[observation] if outcome == SettlementOutcome.BLOCKED else [],
                    do_not_repeat=[] if outcome != SettlementOutcome.FALSIFIED_HYPOTHESIS else [self.current(mission_id)["next_move"]],
                    context_updated=True,
                )
            except Exception:
                # NextMove's append-only settlement remains authoritative for this overlay even if an
                # older RealityStore settlement signature/schema differs.
                pass

        view = self.current(mission_id)
        view["settlement"] = {
            "outcome": outcome.value,
            "observation": observation,
            "receipt_locator": receipt_locator,
            "next_action": next_action,
            "evidence_ids": evidence_ids,
        }
        return view

    def events(self, mission_id: str) -> list[dict[str, Any]]:
        rows = self.db.execute(
            "SELECT event_id,event_type,payload_json,created_at FROM next_events WHERE mission_id=? ORDER BY created_at, rowid",
            (mission_id,),
        ).fetchall()
        return [
            {
                "event_id": row["event_id"],
                "event_type": row["event_type"],
                "payload": json.loads(row["payload_json"]),
                "created_at": row["created_at"],
            }
            for row in rows
        ]
