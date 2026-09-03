from __future__ import annotations
import argparse, json
from datetime import date
from pathlib import Path
from .executor import ExecutionEngine
from .models import RiskLevel, TransitionContract
from .nextmove import NextMoveEngine, SettlementOutcome
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


def _load_spec(path: str) -> dict:
    value = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("mission spec must be a JSON object")
    return value


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

    construction = sub.add_parser(
        "construction-lookahead",
        help="project source-linked construction readiness from schedule exports",
    )
    construction.add_argument("--activities", required=True)
    construction.add_argument("--relationships", required=True)
    construction.add_argument("--requirements", required=True)
    construction.add_argument("--previous-activities")
    construction.add_argument("--as-of", required=True, help="YYYY-MM-DD")
    construction.add_argument("--days", type=int, default=90)
    construction.add_argument("--output-dir", default="artifacts/construction")

    ns = sub.add_parser("next-start", help="select and start exactly one executable NextMove mission")
    ns.add_argument("--spec", required=True, help="path to a mission JSON spec")
    nv = sub.add_parser("next", help="show the current NextMove mission")
    nv.add_argument("mission_id", nargs="?")
    ne = sub.add_parser("next-events", help="show append-only NextMove mission events")
    ne.add_argument("mission_id")
    nset = sub.add_parser("next-settle", help="settle the current transition before doing more work")
    nset.add_argument("outcome", choices=[value.value for value in SettlementOutcome])
    nset.add_argument("--mission-id")
    nset.add_argument("--observation", required=True)
    nset.add_argument("--receipt")
    nset.add_argument("--next-action")
    srv = sub.add_parser("serve", help="serve the minimal Logistinfra /next operator surface")
    srv.add_argument("--host", default="127.0.0.1")
    srv.add_argument("--port", default=8787, type=int)

    args = p.parse_args(argv)

    if args.cmd == "init":
        s = RealityStore(args.db); s.close(); print(json.dumps({"db": args.db, "initialized": True}, indent=2)); return
    if args.cmd == "demo":
        print(json.dumps(_demo(args.db), indent=2)); return
    if args.cmd == "serve":
        from .web import serve
        serve(args.db, host=args.host, port=args.port); return
    if args.cmd == "construction-lookahead":
        from .domains.construction_planning import run_lookahead
        try:
            as_of = date.fromisoformat(args.as_of)
        except ValueError as exc:
            p.error(f"--as-of must be YYYY-MM-DD: {exc}")
        result = run_lookahead(
            activities_path=args.activities,
            relationships_path=args.relationships,
            requirements_path=args.requirements,
            previous_activities_path=args.previous_activities,
            as_of=as_of,
            days=args.days,
            output_dir=args.output_dir,
        )
        print(json.dumps(result, indent=2))
        return

    with RealityStore(args.db) as s:
        if args.cmd == "reality":
            objs = s.db.execute("SELECT object_id,canonical_identity,object_type FROM objects ORDER BY object_id").fetchall()
            print(json.dumps([dict(r) | {"current_state": s.current_state(r["object_id"])} for r in objs], indent=2)); return
        if args.cmd == "timeline": print(json.dumps(s.timeline(args.object_id), indent=2)); return
        if args.cmd == "context": print(json.dumps(s.context_packet(args.goal_id), indent=2)); return
        if args.cmd == "verify-invariants": print(json.dumps(s.invariant_report(), indent=2)); return

        engine = NextMoveEngine(s)
        if args.cmd == "next-start":
            spec = _load_spec(args.spec)
            result = engine.start_mission(
                target=str(spec.get("target", "")),
                observed_state=str(spec.get("observed_state", "")),
                delta=str(spec.get("delta", "")),
                candidates=spec.get("candidates", []),
                timebox_seconds=int(spec.get("timebox_seconds", 900)),
                base_urgency=int(spec.get("base_urgency", 50)),
                owner=spec.get("owner"),
            )
            print(json.dumps(result, indent=2)); return
        if args.cmd == "next":
            print(json.dumps(engine.current(args.mission_id), indent=2)); return
        if args.cmd == "next-events":
            print(json.dumps(engine.events(args.mission_id), indent=2)); return
        if args.cmd == "next-settle":
            mission_id = args.mission_id or engine.current()["mission_id"]
            print(json.dumps(engine.settle(
                mission_id,
                outcome=args.outcome,
                observation=args.observation,
                receipt_locator=args.receipt,
                next_action=args.next_action,
            ), indent=2)); return

if __name__ == "__main__": main()
