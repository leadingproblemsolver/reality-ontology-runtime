from datetime import datetime, timedelta, timezone
import sqlite3

import pytest

from reality_ontology.nextmove import NextMoveEngine


class StubStore:
    def __init__(self):
        self.db = sqlite3.connect(":memory:")
        self.db.row_factory = sqlite3.Row


BASE = {
    "expected_postcondition": "buyer can inspect the submitted artifact",
    "expected_receipt": "submission confirmation",
    "prerequisites_met": True,
    "authority_available": True,
    "observable_receipt": True,
}


def test_strict_priority_and_gating_selects_external_transition():
    store = StubStore()
    engine = NextMoveEngine(store)
    view = engine.start_mission(
        target="obtain external buyer receipt",
        observed_state="artifact is ready but unsent",
        delta="buyer has not received it",
        candidates=[
            dict(BASE, action="polish internal docs", external_consequence=0, information_gain=5, technical_ownership=5, internal_preparation=5),
            dict(BASE, action="submit to live buyer", external_consequence=5, information_gain=3, technical_ownership=1),
            dict(BASE, action="send without authority", external_consequence=5, information_gain=5, authority_available=False),
        ],
    )
    assert view["next_move"] == "submit to live buyer"
    assert view["rank"][0] == 5
    events = engine.events(view["mission_id"])
    assert [e["event_type"] for e in events] == ["MISSION_STARTED", "CANDIDATE_SELECTED"]


def test_receipt_outcome_requires_inspectable_locator():
    store = StubStore()
    engine = NextMoveEngine(store)
    view = engine.start_mission(
        target="ship",
        observed_state="ready",
        delta="not shipped",
        candidates=[dict(BASE, action="submit")],
    )
    with pytest.raises(ValueError, match="receipt_locator"):
        engine.settle(view["mission_id"], outcome="RECEIPT", observation="submitted")


def test_timer_expiry_forces_settlement_nudge():
    t0 = datetime(2026, 8, 31, 18, 0, tzinfo=timezone.utc)
    clock = {"now": t0}
    store = StubStore()
    engine = NextMoveEngine(store, clock=lambda: clock["now"])
    view = engine.start_mission(
        target="external consequence",
        observed_state="ready",
        delta="unsent",
        timebox_seconds=60,
        candidates=[dict(BASE, action="send now")],
    )
    clock["now"] = t0 + timedelta(seconds=61)
    expired = engine.current(view["mission_id"])
    assert expired["status"] == "EXPIRED_NEEDS_SETTLEMENT"
    assert expired["timer"]["remaining_seconds"] == 0
    assert "SETTLE REQUIRED" in expired["nudge"]


def test_settlement_is_terminal_and_append_only():
    store = StubStore()
    engine = NextMoveEngine(store)
    view = engine.start_mission(
        target="external consequence",
        observed_state="ready",
        delta="unsent",
        candidates=[dict(BASE, action="send now")],
    )
    settled = engine.settle(
        view["mission_id"],
        outcome="RECEIPT",
        observation="submission accepted",
        receipt_locator="https://example.test/receipt/123",
    )
    assert settled["status"] == "SETTLED"
    assert settled["settlement"]["outcome"] == "RECEIPT"
    assert [e["event_type"] for e in engine.events(view["mission_id"])] == [
        "MISSION_STARTED",
        "CANDIDATE_SELECTED",
        "MISSION_SETTLED",
    ]
    with pytest.raises(ValueError, match="already settled"):
        engine.settle(view["mission_id"], outcome="EXPLICIT_KILL", observation="duplicate")


def test_only_one_active_mission_can_exist():
    store = StubStore()
    engine = NextMoveEngine(store)
    engine.start_mission(
        target="one",
        observed_state="ready",
        delta="unsent",
        candidates=[dict(BASE, action="send")],
    )
    with pytest.raises(ValueError, match="active mission exists"):
        engine.start_mission(
            target="two",
            observed_state="ready",
            delta="unsent",
            candidates=[dict(BASE, action="another")],
        )
