import json
import sqlite3
from pathlib import Path

from reality_ontology.nextmove import NextMoveEngine


class StubStore:
    def __init__(self):
        self.db = sqlite3.connect(":memory:")
        self.db.row_factory = sqlite3.Row


def test_logistinfra_mve_gateofai_selects_dependency_correct_transition():
    spec_path = Path(__file__).parents[1] / "examples" / "logistinfra_mve_gateofai.json"
    spec = json.loads(spec_path.read_text(encoding="utf-8"))

    engine = NextMoveEngine(StubStore())
    view = engine.start_mission(
        target=spec["target"],
        observed_state=spec["observed_state"],
        delta=spec["delta"],
        candidates=spec["candidates"],
        timebox_seconds=spec["timebox_seconds"],
        base_urgency=spec["base_urgency"],
        owner=spec["owner"],
    )

    assert view["next_move"] == (
        "Verify the highest-information 10 GateOfAI accounts and compile an "
        "evidence-backed top-5 SEND_QUEUE."
    )
    assert view["expected_receipt"].startswith("Updated canonical batch")
    assert view["status"] == "ACTIVE"
