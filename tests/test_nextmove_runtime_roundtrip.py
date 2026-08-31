from datetime import datetime, timezone

from reality_ontology.nextmove import NextMoveEngine
from reality_ontology.store import RealityStore


def test_nextmove_round_trip_with_real_reality_store(tmp_path):
    db_path = tmp_path / "reality.db"
    fixed_now = datetime(2026, 8, 31, 18, 30, tzinfo=timezone.utc)

    with RealityStore(db_path) as store:
        engine = NextMoveEngine(store, clock=lambda: fixed_now)
        view = engine.start_mission(
            target="obtain external receipt",
            observed_state="artifact ready but not exposed",
            delta="external actor has not received it",
            candidates=[{
                "action": "submit artifact to external actor",
                "expected_postcondition": "external actor can inspect artifact",
                "expected_receipt": "submission confirmation",
                "external_consequence": 5,
                "information_gain": 4,
                "prerequisites_met": True,
                "authority_available": True,
                "observable_receipt": True,
            }],
            owner="runtime_test_operator",
        )
        mission_id = view["mission_id"]
        assert view["core_goal_id"] is not None
        assert view["core_object_id"] is not None
        assert store.current_state(view["core_object_id"]) == "ACTIVE"

        settled = engine.settle(
            mission_id,
            outcome="RECEIPT",
            observation="submission accepted and inspectable",
            receipt_locator="test://receipt/submission-1",
        )
        assert settled["status"] == "SETTLED"
        assert settled["settlement"]["evidence_ids"]
        settlement_count = store.db.execute(
            "SELECT COUNT(*) FROM settlements WHERE run_id=?", (mission_id,)
        ).fetchone()[0]
        assert settlement_count == 1

    with RealityStore(db_path) as fresh_store:
        fresh_engine = NextMoveEngine(fresh_store, clock=lambda: fixed_now)
        recovered = fresh_engine.current(mission_id)
        assert recovered["status"] == "SETTLED"
        assert [event["event_type"] for event in fresh_engine.events(mission_id)] == [
            "MISSION_STARTED",
            "CANDIDATE_SELECTED",
            "MISSION_SETTLED",
        ]
