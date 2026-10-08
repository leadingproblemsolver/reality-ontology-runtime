import json
from pathlib import Path

import pytest

from reality_ontology.nextmove import NextMoveEngine
from reality_ontology.pminus1 import compile_block, resume_view
from reality_ontology.store import RealityStore


BASE = {
    "action": "verify ten accounts and produce the top-five send queue",
    "expected_postcondition": "ten accounts are settled and five are send-ready",
    "expected_receipt": "updated batch plus send queue",
    "external_consequence": 2,
    "information_gain": 5,
    "technical_ownership": 3,
    "warm_access": 3,
    "compounding_leverage": 5,
    "internal_preparation": 2,
    "prerequisites_met": True,
    "authority_available": True,
    "observable_receipt": True,
}


def test_resume_recovers_active_transition_without_chat_history(tmp_path):
    db = tmp_path / "reality.db"
    with RealityStore(db) as store:
        engine = NextMoveEngine(store)
        mission = engine.start_mission(
            target="produce evidence-backed send queue",
            observed_state="batch exists; live verification incomplete",
            delta="no verified send queue",
            candidates=[BASE],
            owner="Taha",
        )
        view = resume_view(store)

    assert view["mission_id"] == mission["mission_id"]
    assert view["status"] == "ACTIVE"
    assert view["selected_transition"] == BASE["action"]
    assert view["expected_receipt"] == BASE["expected_receipt"]
    assert "chat history" not in view["restart_instruction"].lower()


def test_block_compiler_embeds_preproof_and_bounded_phases(tmp_path):
    db = tmp_path / "reality.db"
    with RealityStore(db) as store:
        NextMoveEngine(store).start_mission(
            target="produce evidence-backed send queue",
            observed_state="batch exists",
            delta="send queue missing",
            candidates=[BASE],
        )
        block = compile_block(store, minutes=10)

    assert block["timebox_minutes"] == 10
    assert block["exact_action"] == BASE["action"]
    assert block["phases"][0]["phase"] == "SYNC"
    assert block["phases"][-1]["phase"] == "RESTART_CUE"
    assert block["preproof"]["required_receipt"] == BASE["expected_receipt"]
    assert "receipt" in block["preproof"]["proof_surface"]


def test_block_refuses_settled_mission(tmp_path):
    db = tmp_path / "reality.db"
    with RealityStore(db) as store:
        engine = NextMoveEngine(store)
        mission = engine.start_mission(
            target="ship",
            observed_state="ready",
            delta="unshipped",
            candidates=[BASE],
        )
        engine.settle(
            mission["mission_id"],
            outcome="RECEIPT",
            observation="receipt exists",
            receipt_locator="https://example.test/receipt",
        )
        with pytest.raises(ValueError, match="cannot compile block"):
            compile_block(store)
