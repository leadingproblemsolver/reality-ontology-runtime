from reality_ontology.executor import ExecutionEngine
from reality_ontology.models import RiskLevel, TransitionContract
from reality_ontology.operators import FileMarkerOperator
from reality_ontology.store import RealityStore


def test_execute_verify_settle_and_restart(tmp_path):
    db = tmp_path / "reality.db"
    target = tmp_path / "external.txt"
    with RealityStore(db) as s:
        actor = s.add_actor("operator")
        goal = s.add_goal("verified", "reread receipt")
        obj = s.add_object("artifact:demo", "artifact")
        ev = s.add_evidence("observation", "local://seed", "ready")
        s.record_event(actor_id=actor, object_id=obj, goal_id=goal, event_type="seed", resulting_state="READY", evidence_ids=[ev])
        c = TransitionContract("t1", obj, goal, "READY", "VERIFIED_LOCAL", "filesystem.append_marker", "append", "reread marker", RiskLevel.L1_REVERSIBLE_WRITE)
        result = ExecutionEngine(s, [FileMarkerOperator()]).execute(c, inputs={"path": str(target), "marker": "OK"}, actor_id=actor)
        assert s.current_state(obj) == "VERIFIED_LOCAL"
        assert s.attempt(result["attempt_id"])["status"] == "SETTLED"

    with RealityStore(db) as fresh:
        assert fresh.current_state(obj) == "VERIFIED_LOCAL"
        packet = fresh.context_packet(goal)
        assert packet["objects"][0]["current_state"] == "VERIFIED_LOCAL"
