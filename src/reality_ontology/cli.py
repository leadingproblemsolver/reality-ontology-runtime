from __future__ import annotations
import argparse, json
from pathlib import Path
from .executor import ExecutionEngine
from .models import RiskLevel, TransitionContract
from .operators import FileMarkerOperator
from .store import RealityStore


def _demo(db_path: str) -> dict:
    store = RealityStore(db_path)
    actor = store.add_actor("local_operator", actor_id="actor_local")
    goal = store.add_goal("proof-carrying transition settled", "verified marker + settlement", goal_id="goal_demo")
    obj = store.add_object("demo:artifact:reality-ontology", "artifact", object_id="obj_demo")
    if store.current_state(obj) is None:
        ev = store.add_evidence("observation", "local://demo", "demo object exists")
        store.record_event(actor_id=actor, object_id=obj, goal_id=goal, event_type="object_observed", resulting_state="READY", evidence_ids=[ev])

    if store.current_state(obj) == "SETTLED_PROOF":
        packet = store.context_packet(goal)
        store.close()
        fresh = RealityStore(db_path)
        recovered = fresh.current_state(obj)
        fresh.close()
        return {
            "execution": "NOOP_ALREADY_SETTLED",
            "state_before_restart": "SETTLED_PROOF",
            "state_after_restart": recovered,
            "fresh_context_object_count": len(packet["objects"]),
            "acceptance": recovered == "SETTLED_PROOF",
        }

    target = str(Path(db_path).parent / "external_target.txt") if db_path != ":memory:" else "/tmp/ro_external_target.txt"
    contract = TransitionContract(
        transition_id="transition_demo_settle", object_id=obj, goal_id=goal,
        entry_state=store.current_state(obj), desired_state="SETTLED_PROOF",
        operator="filesystem.append_marker", operation="append_verified_marker",
        proof_required="fresh reread contains exact marker", risk=RiskLevel.L1_REVERSIBLE_WRITE,
        verification={"exact_marker": "REALITY_ONTOLOGY_VERIFIED"}
    )
    engine = ExecutionEngine(store, [FileMarkerOperator()])
    result = engine.execute(contract, inputs={"path": target, "marker": "REALITY_ONTOLOGY_VERIFIED"}, actor_id=actor, owner=actor, next_transition="inspect_context", next_action="ro context goal_demo")
    before_close = store.current_state(obj)
    store.close()

    fresh = RealityStore(db_path)
    recovered = fresh.current_state(obj)
    packet = fresh.context_packet(goal)
    fresh.close()
    return {"execution": result, "state_before_restart": before_close, "state_after_restart": recovered, "fresh_context_object_count": len(packet["objects"]), "acceptance": recovered == "SETTLED_PROOF"}


def main(argv=None):
    p = argparse.ArgumentParser(prog="ro")
    p.add_argument("--db", default=".runtime/reality.db")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("init")
    sub.add_parser("demo")
    sub.add_parser("reality")
    tl = sub.add_parser("timeline"); tl.add_argument("object_id")
    cp = sub.add_parser("context"); cp.add_argument("goal_id")
    sub.add_parser("verify-invariants")
    args = p.parse_args(argv)

    if args.cmd == "init":
        s = RealityStore(args.db); s.close(); print(json.dumps({"db": args.db, "initialized": True}, indent=2)); return
    if args.cmd == "demo":
        print(json.dumps(_demo(args.db), indent=2)); return

    with RealityStore(args.db) as s:
        if args.cmd == "reality":
            objs = s.db.execute("SELECT object_id,canonical_identity,object_type FROM objects ORDER BY object_id").fetchall()
            print(json.dumps([dict(r) | {"current_state": s.current_state(r["object_id"])} for r in objs], indent=2)); return
        if args.cmd == "timeline": print(json.dumps(s.timeline(args.object_id), indent=2)); return
        if args.cmd == "context": print(json.dumps(s.context_packet(args.goal_id), indent=2)); return
        if args.cmd == "verify-invariants": print(json.dumps(s.invariant_report(), indent=2)); return

if __name__ == "__main__": main()
