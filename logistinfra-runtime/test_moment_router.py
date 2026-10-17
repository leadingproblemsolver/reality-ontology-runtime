import copy
import json
from pathlib import Path

from moment_router import route

BASE = json.loads(Path(__file__).with_name("reality.example.json").read_text())


def test_selects_bounded_external_proof_task():
    decision = route(copy.deepcopy(BASE), available_minutes=45)
    assert decision.primary is not None
    assert decision.primary["project"] == "Browser Use contribution"
    assert all(x["item"] != decision.primary["action"] for x in decision.waiting)


def test_waiting_external_is_suppressed():
    decision = route(copy.deepcopy(BASE), available_minutes=45)
    assert any("Follow up with employer contact" == x["item"] for x in decision.waiting)
    assert decision.primary["action"] != "Follow up with employer contact"


def test_urgent_external_actor_preempts_score():
    reality = copy.deepcopy(BASE)
    reality["candidates"].append({
        "goal": "advance live external conversation",
        "project": "Inbound founder reply",
        "action": "Answer founder's blocking question",
        "why_now": "external actor is waiting on us",
        "operator": "message_triage",
        "chat_reference": "Message Triage Process",
        "context_refs": ["inbound reply", "previous outbound"],
        "first_physical_action": "Read reply and answer the exact blocking question",
        "stop_condition": "response sent and receipt stored",
        "receipt_required": "sent-message receipt",
        "timebox_minutes": 10,
        "status": "active",
        "hard_gate": "external_actor_waiting",
        "scores": {"external_consequence": 1}
    })
    decision = route(reality, available_minutes=45)
    assert decision.primary["project"] == "Inbound founder reply"
