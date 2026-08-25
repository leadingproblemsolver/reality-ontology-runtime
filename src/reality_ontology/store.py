from __future__ import annotations
import contextlib, hashlib, json, sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable
from .ids import new_id
from .models import AttemptStatus, EpistemicType, Evidence, RealityEvent, TruthState
from .truth import ensure_promotion_allowed

SCHEMA = """
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS actors (
  actor_id TEXT PRIMARY KEY, actor_type TEXT NOT NULL, identity TEXT NOT NULL,
  authority_json TEXT NOT NULL DEFAULT '{}', created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS goals (
  goal_id TEXT PRIMARY KEY, target_state TEXT NOT NULL, success_evidence TEXT NOT NULL,
  status TEXT NOT NULL, created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS objects (
  object_id TEXT PRIMARY KEY, object_type TEXT NOT NULL, canonical_identity TEXT NOT NULL UNIQUE,
  created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS evidence (
  evidence_id TEXT PRIMARY KEY, evidence_type TEXT NOT NULL, source_locator TEXT NOT NULL,
  observation TEXT NOT NULL, digest TEXT NOT NULL, captured_at TEXT NOT NULL,
  trust REAL NOT NULL, metadata_json TEXT NOT NULL DEFAULT '{}'
);
CREATE TABLE IF NOT EXISTS events (
  event_id TEXT PRIMARY KEY, occurred_at TEXT NOT NULL, actor_id TEXT NOT NULL,
  object_id TEXT NOT NULL, event_type TEXT NOT NULL, previous_state TEXT,
  resulting_state TEXT, goal_id TEXT, evidence_ids_json TEXT NOT NULL,
  source TEXT NOT NULL, confidence REAL NOT NULL, epistemic_type TEXT NOT NULL,
  metadata_json TEXT NOT NULL DEFAULT '{}',
  FOREIGN KEY(actor_id) REFERENCES actors(actor_id),
  FOREIGN KEY(object_id) REFERENCES objects(object_id),
  FOREIGN KEY(goal_id) REFERENCES goals(goal_id)
);
CREATE INDEX IF NOT EXISTS idx_events_object_time ON events(object_id, occurred_at, event_id);
CREATE TABLE IF NOT EXISTS relations (
  relation_id TEXT PRIMARY KEY, source_id TEXT NOT NULL, relation_type TEXT NOT NULL,
  target_id TEXT NOT NULL, valid_from TEXT NOT NULL, valid_to TEXT,
  evidence_ids_json TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS approvals (
  approval_id TEXT PRIMARY KEY, transition_id TEXT NOT NULL, actor_id TEXT NOT NULL,
  decision TEXT NOT NULL, decided_at TEXT NOT NULL, evidence_id TEXT
);
CREATE TABLE IF NOT EXISTS attempts (
  attempt_id TEXT PRIMARY KEY, transition_id TEXT NOT NULL, attempt_number INTEGER NOT NULL,
  exact_action TEXT NOT NULL, inputs_json TEXT NOT NULL, actor TEXT NOT NULL,
  started_at TEXT NOT NULL, completed_at TEXT, status TEXT NOT NULL,
  result_json TEXT, failure_class TEXT, evidence_ids_json TEXT NOT NULL DEFAULT '[]',
  external_side_effect INTEGER NOT NULL DEFAULT 0, checkpoint TEXT,
  state_mutation_json TEXT
);
CREATE INDEX IF NOT EXISTS idx_attempts_transition ON attempts(transition_id, attempt_number);
CREATE TABLE IF NOT EXISTS settlements (
  settlement_id TEXT PRIMARY KEY, run_id TEXT NOT NULL, prior_state TEXT,
  action_taken TEXT NOT NULL, observed_result TEXT NOT NULL, evidence_ids_json TEXT NOT NULL,
  new_state TEXT, unresolved_json TEXT NOT NULL, waiting_external_json TEXT NOT NULL,
  next_transition TEXT, next_action TEXT, owner TEXT, do_not_repeat_json TEXT NOT NULL,
  context_updated INTEGER NOT NULL, settled_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS assumptions (
  assumption_id TEXT PRIMARY KEY, decision_id TEXT, text TEXT NOT NULL, category TEXT NOT NULL,
  confidence REAL, status TEXT NOT NULL, created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS decisions (
  decision_id TEXT PRIMARY KEY, label TEXT NOT NULL, predicted_outcome TEXT,
  predicted_metric REAL, measurement_window_days INTEGER NOT NULL DEFAULT 30,
  status TEXT NOT NULL, created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS decision_dependencies (
  decision_id TEXT NOT NULL, assumption_id TEXT NOT NULL, strength TEXT NOT NULL,
  PRIMARY KEY(decision_id, assumption_id)
);
CREATE TABLE IF NOT EXISTS reality_signals (
  signal_id TEXT PRIMARY KEY, signal_type TEXT NOT NULL, source TEXT NOT NULL,
  observation TEXT NOT NULL, severity REAL NOT NULL, contradicts_assumption_id TEXT,
  created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS contradictions (
  contradiction_id TEXT PRIMARY KEY, assumption_id TEXT NOT NULL, signal_id TEXT NOT NULL,
  severity REAL NOT NULL, reevaluation_status TEXT NOT NULL, created_at TEXT NOT NULL
);
"""

def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()

def digest_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

class RealityStore:
    def __init__(self, path: str | Path = ":memory:"):
        self.path = str(path)
        if self.path != ":memory:":
            Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(self.path)
        self.db.row_factory = sqlite3.Row
        self.db.executescript(SCHEMA)
        self.db.commit()

    def close(self): self.db.close()
    def __enter__(self): return self
    def __exit__(self, *args): self.close()

    def add_actor(self, identity: str, actor_type: str = "human", authority: dict[str, Any] | None = None, actor_id: str | None = None) -> str:
        actor_id = actor_id or new_id("actor")
        self.db.execute("INSERT OR IGNORE INTO actors VALUES (?,?,?,?,?)", (actor_id, actor_type, identity, json.dumps(authority or {}), utcnow()))
        self.db.commit(); return actor_id

    def add_goal(self, target_state: str, success_evidence: str, status: str = "ACTIVE", goal_id: str | None = None) -> str:
        goal_id = goal_id or new_id("goal")
        self.db.execute("INSERT OR IGNORE INTO goals VALUES (?,?,?,?,?)", (goal_id, target_state, success_evidence, status, utcnow()))
        self.db.commit(); return goal_id

    def add_object(self, canonical_identity: str, object_type: str, object_id: str | None = None) -> str:
        row = self.db.execute("SELECT object_id FROM objects WHERE canonical_identity=?", (canonical_identity,)).fetchone()
        if row: return row[0]
        object_id = object_id or new_id("obj")
        self.db.execute("INSERT INTO objects VALUES (?,?,?,?)", (object_id, object_type, canonical_identity, utcnow()))
        self.db.commit(); return object_id

    def add_evidence(self, evidence_type: str, source_locator: str, observation: str, trust: float = 1.0, metadata: dict[str, Any] | None = None, evidence_id: str | None = None) -> str:
        evidence_id = evidence_id or new_id("ev")
        payload = f"{evidence_type}\0{source_locator}\0{observation}"
        self.db.execute("INSERT INTO evidence VALUES (?,?,?,?,?,?,?,?)", (evidence_id, evidence_type, source_locator, observation, digest_text(payload), utcnow(), trust, json.dumps(metadata or {})))
        self.db.commit(); return evidence_id

    def evidence_types(self, evidence_ids: Iterable[str]) -> set[str]:
        ids = list(evidence_ids)
        if not ids: return set()
        q = ",".join("?" for _ in ids)
        return {r[0] for r in self.db.execute(f"SELECT evidence_type FROM evidence WHERE evidence_id IN ({q})", ids)}

    def current_state(self, object_id: str) -> str | None:
        row = self.db.execute("SELECT resulting_state FROM events WHERE object_id=? AND resulting_state IS NOT NULL ORDER BY occurred_at DESC, rowid DESC LIMIT 1", (object_id,)).fetchone()
        return row[0] if row else None

    def record_event(self, *, actor_id: str, object_id: str, event_type: str, resulting_state: str | None, evidence_ids: list[str], goal_id: str | None = None, source: str = "runtime", confidence: float = 1.0, epistemic_type: EpistemicType = EpistemicType.OBSERVATION, metadata: dict[str, Any] | None = None, event_id: str | None = None) -> str:
        previous = self.current_state(object_id)
        missing = [eid for eid in evidence_ids if not self.db.execute("SELECT 1 FROM evidence WHERE evidence_id=?", (eid,)).fetchone()]
        if missing: raise ValueError(f"event references missing evidence: {missing}")
        if resulting_state:
            ensure_promotion_allowed(previous, resulting_state, self.evidence_types(evidence_ids))
        event_id = event_id or new_id("evt")
        self.db.execute("INSERT INTO events VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)", (
            event_id, utcnow(), actor_id, object_id, event_type, previous, resulting_state, goal_id,
            json.dumps(evidence_ids), source, confidence, epistemic_type.value, json.dumps(metadata or {})
        ))
        self.db.commit(); return event_id

    def timeline(self, object_id: str) -> list[dict[str, Any]]:
        rows = self.db.execute("SELECT * FROM events WHERE object_id=? ORDER BY occurred_at, rowid", (object_id,)).fetchall()
        return [dict(r) | {"evidence_ids": json.loads(r["evidence_ids_json"]), "metadata": json.loads(r["metadata_json"])} for r in rows]

    def relate(self, source_id: str, relation_type: str, target_id: str, evidence_ids: list[str], valid_to: str | None = None) -> str:
        if not evidence_ids: raise ValueError("canonical relation requires evidence provenance")
        rid = new_id("rel")
        self.db.execute("INSERT INTO relations VALUES (?,?,?,?,?,?,?)", (rid, source_id, relation_type, target_id, utcnow(), valid_to, json.dumps(evidence_ids)))
        self.db.commit(); return rid

    def approve(self, transition_id: str, actor_id: str, decision: str = "APPROVE", evidence_id: str | None = None) -> str:
        aid = new_id("approval")
        self.db.execute("INSERT INTO approvals VALUES (?,?,?,?,?,?)", (aid, transition_id, actor_id, decision, utcnow(), evidence_id))
        self.db.commit(); return aid

    def is_approved(self, transition_id: str) -> bool:
        row = self.db.execute("SELECT decision FROM approvals WHERE transition_id=? ORDER BY decided_at DESC LIMIT 1", (transition_id,)).fetchone()
        return bool(row and row[0] == "APPROVE")

    def begin_attempt(self, transition_id: str, exact_action: str, inputs: dict[str, Any], actor: str) -> str:
        n = self.db.execute("SELECT COALESCE(MAX(attempt_number),0)+1 FROM attempts WHERE transition_id=?", (transition_id,)).fetchone()[0]
        aid = new_id("attempt")
        self.db.execute("INSERT INTO attempts (attempt_id,transition_id,attempt_number,exact_action,inputs_json,actor,started_at,status) VALUES (?,?,?,?,?,?,?,?)", (aid, transition_id, n, exact_action, json.dumps(inputs), actor, utcnow(), AttemptStatus.RUNNING.value))
        self.db.commit(); return aid

    def update_attempt(self, attempt_id: str, status: AttemptStatus, *, result: dict[str, Any] | None = None, failure_class: str | None = None, evidence_ids: list[str] | None = None, external_side_effect: bool | None = None, checkpoint: str | None = None, state_mutation: dict[str, Any] | None = None) -> None:
        row = self.db.execute("SELECT * FROM attempts WHERE attempt_id=?", (attempt_id,)).fetchone()
        if not row: raise KeyError(attempt_id)
        self.db.execute("UPDATE attempts SET completed_at=?, status=?, result_json=?, failure_class=?, evidence_ids_json=?, external_side_effect=?, checkpoint=?, state_mutation_json=? WHERE attempt_id=?", (
            utcnow() if status not in {AttemptStatus.RUNNING, AttemptStatus.WAITING_EXTERNAL} else row["completed_at"], status.value,
            json.dumps(result) if result is not None else row["result_json"], failure_class,
            json.dumps(evidence_ids if evidence_ids is not None else json.loads(row["evidence_ids_json"])),
            int(external_side_effect if external_side_effect is not None else row["external_side_effect"]), checkpoint,
            json.dumps(state_mutation) if state_mutation is not None else row["state_mutation_json"], attempt_id
        )); self.db.commit()

    def attempt(self, attempt_id: str) -> dict[str, Any]:
        r = self.db.execute("SELECT * FROM attempts WHERE attempt_id=?", (attempt_id,)).fetchone()
        if not r: raise KeyError(attempt_id)
        d = dict(r)
        for k in ("inputs_json","result_json","evidence_ids_json","state_mutation_json"):
            if d[k] is not None: d[k[:-5] if k.endswith('_json') else k] = json.loads(d[k])
        return d

    def settle(self, *, run_id: str, prior_state: str | None, action_taken: str, observed_result: str, evidence_ids: list[str], new_state: str | None, next_transition: str | None, next_action: str | None, owner: str | None, unresolved: list[str] | None = None, waiting_external: list[str] | None = None, do_not_repeat: list[str] | None = None, context_updated: bool = True) -> str:
        if not context_updated: raise ValueError("context_updated=false => run is not settled")
        sid = new_id("settlement")
        self.db.execute("INSERT INTO settlements VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (
            sid, run_id, prior_state, action_taken, observed_result, json.dumps(evidence_ids), new_state,
            json.dumps(unresolved or []), json.dumps(waiting_external or []), next_transition, next_action, owner,
            json.dumps(do_not_repeat or []), 1, utcnow()
        )); self.db.commit(); return sid

    def context_packet(self, goal_id: str) -> dict[str, Any]:
        goal = self.db.execute("SELECT * FROM goals WHERE goal_id=?", (goal_id,)).fetchone()
        if not goal: raise KeyError(goal_id)
        rows = self.db.execute("SELECT DISTINCT object_id FROM events WHERE goal_id=?", (goal_id,)).fetchall()
        objects = [{"object_id": r[0], "current_state": self.current_state(r[0]), "timeline": self.timeline(r[0])[-5:]} for r in rows]
        invalid = self.invalidated_decision_ids()
        decisions = [dict(r) for r in self.db.execute("SELECT * FROM decisions WHERE decision_id NOT IN (SELECT d.decision_id FROM decision_dependencies d JOIN assumptions a ON d.assumption_id=a.assumption_id WHERE a.status='invalidated') ORDER BY created_at")]
        return {"goal": dict(goal), "objects": objects, "active_decisions": decisions, "excluded_invalid_decision_ids": sorted(invalid)}

    def add_decision(self, label: str, predicted_outcome: str | None = None, predicted_metric: float | None = None, decision_id: str | None = None) -> str:
        decision_id = decision_id or new_id("decision")
        self.db.execute("INSERT INTO decisions VALUES (?,?,?,?,?,?,?)", (decision_id, label, predicted_outcome, predicted_metric, 30, "active", utcnow()))
        self.db.commit(); return decision_id

    def add_assumption(self, text: str, category: str, confidence: float | None = None, decision_id: str | None = None, assumption_id: str | None = None) -> str:
        assumption_id = assumption_id or new_id("assumption")
        self.db.execute("INSERT INTO assumptions VALUES (?,?,?,?,?,?,?)", (assumption_id, decision_id, text, category, confidence, "active", utcnow()))
        if decision_id:
            self.db.execute("INSERT OR IGNORE INTO decision_dependencies VALUES (?,?,?)", (decision_id, assumption_id, "critical"))
        self.db.commit(); return assumption_id

    def add_signal(self, signal_type: str, source: str, observation: str, severity: float, contradicts_assumption_id: str | None = None) -> str:
        sid = new_id("signal")
        self.db.execute("INSERT INTO reality_signals VALUES (?,?,?,?,?,?,?)", (sid, signal_type, source, observation, severity, contradicts_assumption_id, utcnow()))
        if contradicts_assumption_id and severity <= -0.70:
            self.db.execute("UPDATE assumptions SET status='invalidated' WHERE assumption_id=?", (contradicts_assumption_id,))
            cid = new_id("contradiction")
            self.db.execute("INSERT INTO contradictions VALUES (?,?,?,?,?,?)", (cid, contradicts_assumption_id, sid, severity, "pending", utcnow()))
        self.db.commit(); return sid

    def invalidated_decision_ids(self) -> set[str]:
        return {r[0] for r in self.db.execute("SELECT DISTINCT d.decision_id FROM decision_dependencies d JOIN assumptions a ON a.assumption_id=d.assumption_id WHERE a.status='invalidated'")}

    def invariant_report(self) -> dict[str, Any]:
        orphan_events = self.db.execute("SELECT COUNT(*) FROM events e WHERE NOT EXISTS (SELECT 1 FROM evidence v WHERE instr(e.evidence_ids_json, v.evidence_id)>0) AND e.evidence_ids_json != '[]'").fetchone()[0]
        unsettled_verified = self.db.execute("SELECT COUNT(*) FROM attempts WHERE status='VERIFIED'").fetchone()[0]
        return {
            "event_evidence_references_checked": True,
            "orphan_event_warning_count": orphan_events,
            "verified_but_unsettled_attempts": unsettled_verified,
            "invalidated_decisions": sorted(self.invalidated_decision_ids()),
        }
